from __future__ import annotations

import json
import os
import threading
from pathlib import Path
from typing import Any

from runner.config import BenchmarkConfig, validate_document
from runner.errors import BenchmarkError

_JSONL_APPEND_LOCK = threading.Lock()


class ResultStore:
    def __init__(self, config: BenchmarkConfig, run_id: str) -> None:
        self.config = config
        self.run_id = run_id
        self.raw_root = config.repository_path("results") / "raw"
        self.run_directory = self.raw_root / run_id

    def create(self) -> None:
        self.run_directory.mkdir(parents=True, exist_ok=False)

    def relative(self, path: Path) -> str:
        return path.relative_to(self.config.root).as_posix()

    def write_artifact(self, filename: str, content: str) -> str:
        if Path(filename).name != filename:
            raise BenchmarkError(f"Artifact filename must not contain directories: {filename}")
        path = self.run_directory / filename
        path.write_text(content, encoding="utf-8", newline="")
        return self.relative(path)

    def save_result(self, result: dict[str, Any]) -> Path:
        result_path = self.run_directory / "result.json"
        result["artifacts"]["result"] = self.relative(result_path)
        validate_document(result, self.config.schema_dir / "run-result.schema.json", result_path)
        serialized = json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
        with result_path.open("x", encoding="utf-8", newline="") as stream:
            stream.write(serialized)
        if self.config.data["runner"]["append_jsonl"]:
            self._append_jsonl(json.dumps(result, ensure_ascii=False, sort_keys=True) + "\n")
        return result_path

    def _append_jsonl(self, line: str) -> None:
        self.raw_root.mkdir(parents=True, exist_ok=True)
        path = self.raw_root / "runs.jsonl"
        with _JSONL_APPEND_LOCK:
            descriptor = os.open(path, os.O_APPEND | os.O_CREAT | os.O_WRONLY, 0o644)
            try:
                os.write(descriptor, line.encode("utf-8"))
            finally:
                os.close(descriptor)
