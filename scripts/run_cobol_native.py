"""Compile and optionally run a COBOL source when GnuCOBOL is installed."""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
from pathlib import Path


def main(arguments: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--run", action="store_true")
    options = parser.parse_args(arguments)
    compiler = shutil.which("cobc")
    if compiler is None:
        print(
            json.dumps(
                {"status": "skipped", "reason": "cobc not found", "source": str(options.source)},
                ensure_ascii=False,
            )
        )
        return 0
    options.output_dir.mkdir(parents=True, exist_ok=True)
    executable = options.output_dir / options.source.stem
    command = [compiler, "-x", "-o", str(executable), str(options.source)]
    completed = subprocess.run(
        command,
        capture_output=True,
        text=True,
        timeout=120,
        check=False,
    )
    result = {
        "status": "compiled" if completed.returncode == 0 else "failed",
        "compiler": compiler,
        "command": command,
        "return_code": completed.returncode,
        "stdout": completed.stdout,
        "stderr": completed.stderr,
    }
    if completed.returncode == 0 and options.run:
        execution = subprocess.run(
            [str(executable)],
            capture_output=True,
            text=True,
            timeout=120,
            check=False,
        )
        result["run_return_code"] = execution.returncode
        result["run_stdout"] = execution.stdout
        result["run_stderr"] = execution.stderr
        result["status"] = "passed" if execution.returncode == 0 else "run_failed"
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["status"] in {"compiled", "passed"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
