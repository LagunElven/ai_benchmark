from __future__ import annotations

import shutil
from pathlib import Path
from typing import Any

import yaml

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]


def write_yaml(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump(value, sort_keys=False), encoding="utf-8")


def create_repository(root: Path, *, hidden_validation: bool = False) -> Path:
    shutil.copytree(REPOSITORY_ROOT / "schemas", root / "schemas")
    (root / "tasks" / "java" / "JAVA-99" / "workspace").mkdir(parents=True)
    (root / "tasks" / "java" / "JAVA-99" / "public-tests").mkdir(parents=True)
    (root / "private-tests" / "JAVA-99").mkdir(parents=True)
    (root / "tasks" / "java" / "JAVA-99" / "prompt.md").write_text(
        "Change VALUE from 1 to 2.", encoding="utf-8"
    )
    (root / "tasks" / "java" / "JAVA-99" / "workspace" / "app.py").write_text(
        "VALUE = 1\n", encoding="utf-8"
    )
    (root / "tasks" / "java" / "JAVA-99" / "public-tests" / "README.txt").write_text(
        "Visible public test notes.", encoding="utf-8"
    )
    (root / "private-tests" / "JAVA-99" / "answer.txt").write_text("secret", encoding="utf-8")
    task = {
        "id": "JAVA-99",
        "revision": 1,
        "name": "Runner fixture",
        "category": "java",
        "difficulty": "easy",
        "suites": ["smoke", "core", "full"],
        "tags": ["java", "fixture"],
        "modes": ["one-shot", "repair"],
        "toolchain": {"language": "python", "version": None, "requirements": []},
        "runtime": {
            "internet": False,
            "max_iterations": 3,
            "timeout_seconds": 10,
            "max_output_tokens": 1000,
        },
        "workspace": {
            "source": "workspace",
            "include": [{"source": "public-tests", "target": "public-tests"}],
            "expected_modified_files": ["app.py"],
        },
        "validation": {
            "public": [
                {
                    "name": "value check",
                    "command": [
                        "python",
                        "-c",
                        "from app import VALUE; assert VALUE == 2",
                    ],
                }
            ],
            "hidden": ([{"command": ["python", "hidden.py"]}] if hidden_validation else []),
        },
        "metrics": ["pass_at_1", "files_modified"],
        "metric_extractors": [],
    }
    write_yaml(root / "tasks" / "java" / "JAVA-99" / "task.yaml", task)

    config = {
        "benchmark": {"name": "test-benchmark", "version": "0.1.0-test"},
        "paths": {
            "tasks": "tasks",
            "private_tests": "private-tests",
            "results": "results",
            "work": ".benchmark-work",
        },
        "model": {
            "provider": "fake",
            "name": "deterministic-test-adapter",
            "revision": "fixture-1",
            "tokenizer_revision": None,
            "quantization": None,
            "dtype": None,
            "request_timeout_seconds": 10,
            "fake_response_file": "fake-response.json",
            "generation": {
                "temperature": 0.0,
                "top_p": 1.0,
                "top_k": None,
                "max_output_tokens": 1000,
                "seed": 1,
            },
        },
        "hardware": {
            "accelerator_model": None,
            "gpu_count": None,
            "gpu_memory_gb": None,
            "driver_version": None,
            "cuda_version": None,
            "cpu_model": None,
            "host_memory_gb": None,
        },
        "serving": {
            "engine": None,
            "engine_version": None,
            "launch_command": None,
            "tensor_parallel_size": None,
            "pipeline_parallel_size": None,
            "max_model_length": None,
            "prefix_caching": None,
            "batch_size": None,
            "concurrency": None,
        },
        "runner": {
            "response_protocol": "file_changes_v1",
            "max_context_bytes": 100000,
            "keep_workspaces": False,
            "append_jsonl": True,
        },
    }
    write_yaml(root / "benchmark.yaml", config)
    (root / "fake-response.json").write_text(
        '{"changes":[{"path":"app.py","content":"VALUE = 2\\n"}]}', encoding="utf-8"
    )
    return root / "benchmark.yaml"
