"""Model-local tokenizer preflight for fully serialized quality prompts."""

from __future__ import annotations

from functools import lru_cache
from typing import Any

from runner.context_dataset import count_tokens


@lru_cache(maxsize=8)
def _load_huggingface_tokenizer(repository: str, revision: str | None) -> Any | None:
    try:
        from transformers import AutoTokenizer

        return AutoTokenizer.from_pretrained(
            repository,
            revision=revision,
            local_files_only=True,
        )
    except (ImportError, OSError, ValueError):
        return None


def load_context_tokenizer(model: dict[str, Any]) -> tuple[Any | None, str]:
    repository = (
        model.get("tokenizer_repository") or model.get("source_repository") or model.get("name")
    )
    revision = model.get("tokenizer_revision")
    if not repository:
        return None, "unavailable:not-configured"
    tokenizer = _load_huggingface_tokenizer(repository, revision)
    if tokenizer is None:
        return None, "unavailable:local-tokenizer-not-found"
    return tokenizer, f"huggingface-chat-template:{repository}@{revision or 'default'}"


def measure_prompt_tokens(
    messages: list[dict[str, str]],
    *,
    tokenizer: Any | None,
    tokenizer_method: str,
    chat_template_kwargs: dict[str, Any] | None = None,
) -> tuple[int, str, bool]:
    if tokenizer is not None:
        try:
            encoded = tokenizer.apply_chat_template(
                messages,
                tokenize=True,
                add_generation_prompt=True,
                **(chat_template_kwargs or {}),
            )
            if encoded and isinstance(encoded[0], list):
                encoded = encoded[0]
            return len(encoded), tokenizer_method, True
        except (AttributeError, TypeError, ValueError, KeyError):
            pass
    serialized = "\n".join(f"<|{message['role']}|>\n{message['content']}" for message in messages)
    return count_tokens(serialized).tokens, "fallback:regex", False


def assess_context_budget(
    messages: list[dict[str, str]],
    *,
    model: dict[str, Any],
    serving: dict[str, Any],
    runner: dict[str, Any],
    output_tokens: int,
) -> dict[str, Any]:
    tokenizer, tokenizer_method = load_context_tokenizer(model)
    input_tokens, method, exact = measure_prompt_tokens(
        messages,
        tokenizer=tokenizer,
        tokenizer_method=tokenizer_method,
        chat_template_kwargs=model.get("generation", {}).get("chat_template_kwargs"),
    )
    context_window = serving.get("max_model_length")
    safety_margin = runner.get("context_safety_margin_tokens", 1024)
    required = input_tokens + output_tokens + safety_margin
    if context_window is None:
        status = "not_configured"
    elif not exact:
        status = "unverified_estimate"
    elif required > context_window:
        status = "rejected"
    else:
        status = "within_limit"
    return {
        "status": status,
        "input_tokens": input_tokens,
        "input_token_count_method": method,
        "input_token_count_exact": exact,
        "context_window_tokens": context_window,
        "reserved_output_tokens": output_tokens,
        "safety_margin_tokens": safety_margin,
        "required_total_tokens": required,
    }
