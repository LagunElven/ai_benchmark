from __future__ import annotations

import json
import threading
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from serving.client import OpenAICompatibleServingClient


class _StreamingHandler(BaseHTTPRequestHandler):
    request_payload: dict[str, object] | None = None

    def do_POST(self) -> None:  # noqa: N802
        length = int(self.headers["Content-Length"])
        self.__class__.request_payload = json.loads(self.rfile.read(length))
        self.send_response(200)
        self.send_header("Content-Type", "text/event-stream")
        self.send_header("Connection", "close")
        self.send_header("X-KV-Cache-Hit-Tokens", "12")
        self.end_headers()
        chunks = [
            {"choices": [{"delta": {"role": "assistant"}}]},
            {"choices": [{"delta": {"content": "ok"}}]},
            {"choices": [], "usage": {"prompt_tokens": 20, "completion_tokens": 2}},
        ]
        for chunk in chunks:
            self.wfile.write(f"data: {json.dumps(chunk)}\n\n".encode())
            self.wfile.flush()
        self.wfile.write(b"data: [DONE]\n\n")
        self.wfile.flush()
        self.close_connection = True

    def log_message(self, format: str, *args: object) -> None:
        del format, args


class _OutOfMemoryHandler(BaseHTTPRequestHandler):
    def do_POST(self) -> None:  # noqa: N802
        self.send_response(507)
        self.send_header("Content-Type", "text/plain")
        self.send_header("Content-Length", "18")
        self.end_headers()
        self.wfile.write(b"CUDA out of memory")

    def log_message(self, format: str, *args: object) -> None:
        del format, args


class _NonStreamingHandler(BaseHTTPRequestHandler):
    def do_POST(self) -> None:  # noqa: N802
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        body = json.dumps({"choices": [{"message": {"content": "hello world"}}]}).encode()
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format: str, *args: object) -> None:
        del format, args


class _TruncatedStreamHandler(BaseHTTPRequestHandler):
    def do_POST(self) -> None:  # noqa: N802
        self.send_response(200)
        self.send_header("Content-Type", "text/event-stream")
        self.send_header("Connection", "close")
        self.end_headers()
        chunk = {"choices": [{"delta": {"content": "partial"}}]}
        self.wfile.write(f"data: {json.dumps(chunk)}\n\n".encode())
        self.wfile.flush()
        self.close_connection = True

    def log_message(self, format: str, *args: object) -> None:
        del format, args


class ServingClientTests(unittest.TestCase):
    def test_streaming_response_captures_ttft_usage_and_server_metrics(self) -> None:
        server = ThreadingHTTPServer(("127.0.0.1", 0), _StreamingHandler)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            client = OpenAICompatibleServingClient(
                f"http://127.0.0.1:{server.server_port}/v1",
                "test-model",
                timeout_seconds=5,
            )
            measurement = client.complete_stream(
                [{"role": "user", "content": "hello"}],
                max_output_tokens=8,
                temperature=0.0,
                top_p=1.0,
                seed=42,
                request_id="test-request",
            )
        finally:
            server.shutdown()
            thread.join(timeout=5)
            server.server_close()
        self.assertEqual(measurement.status, "completed")
        self.assertEqual(measurement.input_tokens, 20)
        self.assertEqual(measurement.output_tokens, 2)
        self.assertEqual(measurement.output_tokens_method, "provider_usage")
        self.assertIsNotNone(measurement.ttft_seconds)
        self.assertIsNotNone(measurement.tpot_seconds)
        self.assertEqual(measurement.server_metrics["kv_cache_hit_tokens"], 12)
        self.assertEqual(_StreamingHandler.request_payload["stream"], True)
        self.assertEqual(_StreamingHandler.request_payload["model"], "test-model")

    def test_http_out_of_memory_is_recorded_as_oom(self) -> None:
        server = ThreadingHTTPServer(("127.0.0.1", 0), _OutOfMemoryHandler)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            client = OpenAICompatibleServingClient(
                f"http://127.0.0.1:{server.server_port}/v1",
                "test-model",
                timeout_seconds=5,
            )
            measurement = client.complete_stream(
                [{"role": "user", "content": "hello"}],
                max_output_tokens=8,
                temperature=0.0,
                top_p=1.0,
                seed=None,
                request_id="oom-request",
            )
        finally:
            server.shutdown()
            thread.join(timeout=5)
            server.server_close()
        self.assertEqual(measurement.status, "oom")
        self.assertEqual(measurement.error_type, "oom")

    def test_non_streaming_response_does_not_fabricate_ttft(self) -> None:
        server = ThreadingHTTPServer(("127.0.0.1", 0), _NonStreamingHandler)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            client = OpenAICompatibleServingClient(
                f"http://127.0.0.1:{server.server_port}/v1",
                "test-model",
                timeout_seconds=5,
            )
            measurement = client.complete_stream(
                [{"role": "user", "content": "hello"}],
                max_output_tokens=8,
                temperature=0.0,
                top_p=1.0,
                seed=None,
                request_id="json-request",
            )
        finally:
            server.shutdown()
            thread.join(timeout=5)
            server.server_close()
        self.assertEqual(measurement.status, "completed")
        self.assertIsNone(measurement.ttft_seconds)
        self.assertEqual(measurement.output_tokens_method, "fallback:regex")

    def test_eof_without_sse_terminal_event_is_incomplete(self) -> None:
        server = ThreadingHTTPServer(("127.0.0.1", 0), _TruncatedStreamHandler)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            client = OpenAICompatibleServingClient(
                f"http://127.0.0.1:{server.server_port}/v1",
                "test-model",
                timeout_seconds=5,
            )
            measurement = client.complete_stream(
                [{"role": "user", "content": "hello"}],
                max_output_tokens=8,
                temperature=0.0,
                top_p=1.0,
                seed=None,
                request_id="truncated-request",
            )
        finally:
            server.shutdown()
            thread.join(timeout=5)
            server.server_close()
        self.assertEqual(measurement.status, "incomplete")
        self.assertEqual(measurement.error_type, "incomplete_stream")


if __name__ == "__main__":
    unittest.main()
