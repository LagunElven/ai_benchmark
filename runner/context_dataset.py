"""Generation and measurement helpers for controlled long-context variants."""

from __future__ import annotations

import hashlib
import json
import re
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Protocol


class Tokenizer(Protocol):
    def encode(self, text: str) -> list[int]: ...


@dataclass(frozen=True)
class TokenCount:
    tokens: int
    method: str
    tokenizer: str | None


def load_optional_tokenizer(name: str | None = None) -> tuple[Tokenizer | None, str]:
    """Load an optional tokenizer without making it a hard benchmark dependency."""
    if name:
        try:
            import tiktoken

            return tiktoken.get_encoding(name), f"tiktoken:{name}"
        except (ImportError, LookupError):
            return None, f"fallback:no-tokenizer({name})"
    try:
        import tiktoken

        return tiktoken.get_encoding("cl100k_base"), "tiktoken:cl100k_base"
    except (ImportError, LookupError):
        return None, "fallback:regex"


def count_tokens(
    text: str, tokenizer: Tokenizer | None = None, method: str | None = None
) -> TokenCount:
    if tokenizer is not None:
        return TokenCount(len(tokenizer.encode(text)), method or "custom", method)
    return TokenCount(
        len(re.findall(r"\w+|[^\w\s]", text, flags=re.UNICODE)),
        method or "fallback:regex",
        None,
    )


def count_workspace_tokens(
    workspace: str | Path, *, tokenizer: Tokenizer | None = None, method: str | None = None
) -> TokenCount:
    root = Path(workspace)
    total = 0
    selected_method = method or "fallback:regex"
    tokenizer_name = method
    for path in sorted(root.rglob("*")):
        if not path.is_file() or path.is_symlink():
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        count = count_tokens(text, tokenizer, method)
        total += count.tokens
        selected_method = count.method
        tokenizer_name = count.tokenizer
    return TokenCount(total, selected_method, tokenizer_name)


def _distractor_text(index: int, seed: int) -> str:
    rows = [
        f"historical module {index} seed {seed}: this entry is unrelated to billing.",
        "The service records an immutable correlation id and validates tenant boundaries.",
        "A replay must be idempotent and preserve event ordering across projections.",
        "Operational dashboards retain p50 p95 p99 latency and bounded failure counts.",
        "Configuration changes require an owner, an expiry date and a migration note.",
        "These words are deterministic context noise used to measure file retrieval.",
    ]
    return "\n".join(rows * 24) + "\n"


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    digest.update(path.read_bytes())
    return digest.hexdigest()


def _copy_source(source: Path, destination: Path) -> None:
    if not source.is_dir():
        raise ValueError(f"Context source is not a directory: {source}")
    for path in source.rglob("*"):
        if path.is_symlink():
            raise ValueError(f"Context source contains a symlink: {path}")
    shutil.copytree(source, destination)


def generate_context_variants(
    source: str | Path,
    output: str | Path,
    sizes: list[int],
    *,
    relevant_files: list[str] | None = None,
    tokenizer_name: str | None = None,
    seed: int = 20260915,
) -> list[Path]:
    """Create fresh variants with monotonically increasing deterministic distractors."""
    if not sizes or any(size <= 0 for size in sizes):
        raise ValueError("sizes must contain positive token targets")
    if sizes != sorted(set(sizes)):
        raise ValueError("sizes must be sorted and unique")
    source_path = Path(source)
    destination = Path(output)
    if destination.exists() and any(destination.iterdir()):
        raise ValueError(f"Output directory is not empty: {destination}")
    destination.mkdir(parents=True, exist_ok=True)
    tokenizer, tokenizer_method = load_optional_tokenizer(tokenizer_name)
    base_count = count_workspace_tokens(
        source_path, tokenizer=tokenizer, method=tokenizer_method
    )
    expected_files = sorted(relevant_files or [])
    source_files = {
        path.relative_to(source_path).as_posix()
        for path in source_path.rglob("*")
        if path.is_file()
    }
    missing_relevant = sorted(set(expected_files) - source_files)
    if missing_relevant:
        raise ValueError(f"Relevant files are missing from context source: {missing_relevant}")
    variants: list[Path] = []
    for size in sizes:
        variant_name = f"ctx-{size // 1000}k" if size % 1000 == 0 else f"ctx-{size}tokens"
        variant = destination / variant_name
        _copy_source(source_path, variant)
        generated = variant / "generated-distractors"
        if generated.exists():
            raise ValueError(f"Context source already contains {generated.name}")
        generated.mkdir()
        current = base_count.tokens
        index = 1
        while current < size:
            content = _distractor_text(index, seed)
            path = generated / f"distractor-{index:04d}.md"
            path.write_text(content, encoding="utf-8", newline="")
            current += count_tokens(content, tokenizer, tokenizer_method).tokens
            index += 1
            if index > 10000:
                raise ValueError(f"Could not reach target context size {size}")
        actual = count_workspace_tokens(
            variant, tokenizer=tokenizer, method=tokenizer_method
        )
        files = [
            {
                "path": path.relative_to(variant).as_posix(),
                "sha256": _sha256(path),
                "generated": path.is_relative_to(generated),
            }
            for path in sorted(variant.rglob("*"))
            if path.is_file()
        ]
        manifest = {
            "schema_version": "1.0",
            "variant": variant.name,
            "target_tokens": size,
            "actual_tokens": actual.tokens,
            "token_count_method": actual.method,
            "tokenizer": actual.tokenizer,
            "seed": seed,
            "source": source_path.as_posix(),
            "relevant_files": expected_files,
            "distractor_directory": "generated-distractors",
            "files": files,
        }
        # Keep scoring metadata outside the model-visible variant directory.
        # In particular, relevant_files is ground truth and must never enter
        # the workspace that the evaluated model receives.
        manifest_path = destination / f"{variant.name}.context-manifest.json"
        manifest_path.write_text(
            json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
            newline="",
        )
        variants.append(variant)
    (destination / "manifest.json").write_text(
        json.dumps(
            {
                "schema_version": "1.0",
                "source": source_path.as_posix(),
                "token_count_method": tokenizer_method,
                "tokenizer": tokenizer_method if tokenizer is not None else tokenizer_name,
                "seed": seed,
                "variants": [
                    str(path.relative_to(destination)).replace("\\", "/") for path in variants
                ],
            },
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
        newline="",
    )
    return variants


def score_relevant_files(
    expected_files: list[str], modified_files: list[str]
) -> dict[str, Any]:
    expected = set(expected_files)
    modified = set(modified_files)
    unnecessary = sorted(modified - expected)
    return {
        "files_modified": sorted(modified),
        "expected_files_modified": sorted(modified & expected),
        "unnecessary_files_modified": unnecessary,
        "relevant_file_precision": len(modified & expected) / len(modified) if modified else 0.0,
        "relevant_file_recall": len(modified & expected) / len(expected) if expected else 1.0,
    }
