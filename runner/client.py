from __future__ import annotations

import json
import os
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Any, Protocol

from runner.config import BenchmarkConfig
from runner.errors import ConfigurationError, ModelClientError


@dataclass(frozen=True)
class ModelResponse:
    content: str
    raw: dict[str, Any]
    usage: dict[str, int | None]
    generation_seconds: float
    ttft_seconds: float | None = None


class ModelClient(Protocol):
    def complete(
        self, messages: list[dict[str, str]], *, max_output_tokens: int
    ) -> ModelResponse: ...


def _message_text(value: Any) -> str:
    if isinstance(value, str):
        return value
    if isinstance(value, list):
        parts = [part.get("text", "") for part in value if isinstance(part, dict)]
        return "".join(parts)
    raise ModelClientError("Model response message content is not text")


class OpenAICompatibleClient:
    def __init__(self, config: BenchmarkConfig) -> None:
        self.model = config.data["model"]

    def complete(self, messages: list[dict[str, str]], *, max_output_tokens: int) -> ModelResponse:
        base_url = self.model.get("base_url")
        if not base_url:
            raise ConfigurationError("model.base_url is required for openai_compatible")
        generation = self.model["generation"]
        payload: dict[str, Any] = {
            "model": self.model["name"],
            "messages": messages,
            "temperature": generation["temperature"],
            "top_p": generation["top_p"],
            "max_tokens": min(generation["max_output_tokens"], max_output_tokens),
            "stream": False,
        }
        if generation.get("top_k") is not None:
            payload["top_k"] = generation["top_k"]
        if generation.get("seed") is not None:
            payload["seed"] = generation["seed"]
        if generation.get("chat_template_kwargs") is not None:
            payload["chat_template_kwargs"] = generation["chat_template_kwargs"]

        headers = {"Content-Type": "application/json"}
        api_key_env = self.model.get("api_key_env")
        if api_key_env and os.environ.get(api_key_env):
            headers["Authorization"] = f"Bearer {os.environ[api_key_env]}"
        request = urllib.request.Request(
            f"{base_url.rstrip('/')}/chat/completions",
            data=json.dumps(payload).encode("utf-8"),
            headers=headers,
            method="POST",
        )
        started = time.monotonic()
        try:
            with urllib.request.urlopen(
                request, timeout=self.model["request_timeout_seconds"]
            ) as response:
                raw = json.loads(response.read().decode("utf-8"))
        except (OSError, urllib.error.URLError, json.JSONDecodeError) as exc:
            raise ModelClientError(f"OpenAI-compatible request failed: {exc}") from exc
        duration = time.monotonic() - started
        try:
            content = _message_text(raw["choices"][0]["message"]["content"])
        except (KeyError, IndexError, TypeError) as exc:
            raise ModelClientError("Response does not contain choices[0].message.content") from exc

        usage = raw.get("usage") or {}
        prompt_details = usage.get("prompt_tokens_details") or {}
        completion_details = usage.get("completion_tokens_details") or {}
        return ModelResponse(
            content=content,
            raw=raw,
            generation_seconds=duration,
            usage={
                "input_tokens": usage.get("prompt_tokens"),
                "cached_input_tokens": prompt_details.get("cached_tokens"),
                "output_tokens": usage.get("completion_tokens"),
                "reasoning_tokens": completion_details.get("reasoning_tokens"),
            },
        )


class FakeModelClient:
    def __init__(self, response_content: str) -> None:
        self.response_content = response_content

    def complete(self, messages: list[dict[str, str]], *, max_output_tokens: int) -> ModelResponse:
        del max_output_tokens
        input_tokens = sum(len(item["content"].split()) for item in messages)
        output_tokens = len(self.response_content.split())
        raw = {
            "id": "fake-completion",
            "choices": [{"message": {"role": "assistant", "content": self.response_content}}],
            "usage": {"prompt_tokens": input_tokens, "completion_tokens": output_tokens},
        }
        return ModelResponse(
            content=self.response_content,
            raw=raw,
            generation_seconds=0.0,
            usage={
                "input_tokens": input_tokens,
                "cached_input_tokens": None,
                "output_tokens": output_tokens,
                "reasoning_tokens": None,
            },
        )


def create_client(config: BenchmarkConfig) -> ModelClient:
    provider = config.data["model"]["provider"]
    if provider == "openai_compatible":
        return OpenAICompatibleClient(config)
    if provider == "fake":
        relative = config.data["model"].get("fake_response_file")
        if not relative:
            raise ConfigurationError("model.fake_response_file is required for provider=fake")
        response_path = (config.root / relative).resolve()
        try:
            response_path.relative_to(config.root)
        except ValueError as exc:
            raise ConfigurationError(
                "model.fake_response_file must remain in the repository"
            ) from exc
        return FakeModelClient(response_path.read_text(encoding="utf-8"))
    raise ConfigurationError(f"Unsupported model provider: {provider}")
