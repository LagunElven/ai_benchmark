"""Deterministic quality metrics for OCR text and structured extraction."""

from __future__ import annotations

import json
import re
from collections.abc import Mapping, Sequence
from decimal import Decimal, InvalidOperation
from typing import Any

from jsonschema import Draft202012Validator

_DATE_NAME = re.compile(r"(^|[_-])(date|day|month|year)($|[_-])", re.IGNORECASE)
_IDENTIFIER_NAME = re.compile(
    r"(^|[_-])(id|identifier|reference|ref|iban|bic|number|code)($|[_-])", re.IGNORECASE
)


def edit_distance(reference: Sequence[Any], hypothesis: Sequence[Any]) -> int:
    """Return Levenshtein distance using O(min(n, m)) memory."""
    if len(reference) < len(hypothesis):
        reference, hypothesis = hypothesis, reference
    previous = list(range(len(hypothesis) + 1))
    for row, reference_item in enumerate(reference, start=1):
        current = [row]
        for column, hypothesis_item in enumerate(hypothesis, start=1):
            insertion = current[column - 1] + 1
            deletion = previous[column] + 1
            substitution = previous[column - 1] + (reference_item != hypothesis_item)
            current.append(min(insertion, deletion, substitution))
        previous = current
    return previous[-1]


def _error_rate(reference: Sequence[Any], hypothesis: Sequence[Any]) -> float:
    if not reference:
        return 0.0 if not hypothesis else 1.0
    return edit_distance(reference, hypothesis) / len(reference)


def character_error_rate(reference: str, hypothesis: str) -> float:
    """Compute CER without silently normalizing the OCR strings."""
    return _error_rate(list(reference), list(hypothesis))


def word_error_rate(reference: str, hypothesis: str) -> float:
    """Compute WER on whitespace-delimited words."""
    return _error_rate(reference.split(), hypothesis.split())


def score_text(reference: str, hypothesis: str) -> dict[str, float | int]:
    reference_words = reference.split()
    return {
        "cer": character_error_rate(reference, hypothesis),
        "wer": word_error_rate(reference, hypothesis),
        "reference_characters": len(reference),
        "reference_words": len(reference_words),
    }


def _flatten(value: Any, prefix: str = "") -> dict[str, Any]:
    if isinstance(value, Mapping):
        result: dict[str, Any] = {}
        for key, child in value.items():
            child_prefix = f"{prefix}.{key}" if prefix else str(key)
            result.update(_flatten(child, child_prefix))
        return result
    if isinstance(value, list):
        result = {}
        for index, child in enumerate(value):
            result.update(_flatten(child, f"{prefix}[{index}]"))
        return result
    return {prefix: value}


def _is_number(value: Any) -> bool:
    return isinstance(value, (int, float, Decimal)) and not isinstance(value, bool)


def _equal(expected: Any, actual: Any) -> bool:
    if _is_number(expected) and _is_number(actual):
        try:
            return Decimal(str(expected)) == Decimal(str(actual))
        except InvalidOperation:
            return expected == actual
    return type(expected) is type(actual) and expected == actual


def _accuracy(expected: dict[str, Any], actual: dict[str, Any], predicate: Any) -> float | None:
    selected = {path: value for path, value in expected.items() if predicate(path, value)}
    if not selected:
        return None
    matches = sum(
        path in actual and _equal(value, actual[path]) for path, value in selected.items()
    )
    return matches / len(selected)


def _is_date(path: str, value: Any) -> bool:
    del value
    return bool(_DATE_NAME.search(path.split(".")[-1].split("[")[0]))


def _is_identifier(path: str, value: Any) -> bool:
    del value
    return bool(_IDENTIFIER_NAME.search(path.split(".")[-1].split("[")[0]))


def score_fields(
    expected: Mapping[str, Any],
    actual: Mapping[str, Any] | None,
    *,
    schema: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Score leaf fields while preserving missing and hallucinated field names."""
    expected_flat = _flatten(expected)
    actual_flat = _flatten(actual) if isinstance(actual, Mapping) else {}
    missing = sorted(set(expected_flat) - set(actual_flat))
    hallucinated = sorted(set(actual_flat) - set(expected_flat))
    matches = [
        path
        for path, value in expected_flat.items()
        if path in actual_flat and _equal(value, actual_flat[path])
    ]
    total = len(expected_flat)
    result: dict[str, Any] = {
        "json_validity": actual is not None,
        "schema_validity": None,
        "exact_field_accuracy": len(matches) / total if total else 1.0,
        "numeric_field_accuracy": _accuracy(
            expected_flat, actual_flat, lambda _p, v: _is_number(v)
        ),
        "date_field_accuracy": _accuracy(expected_flat, actual_flat, _is_date),
        "identifier_field_accuracy": _accuracy(expected_flat, actual_flat, _is_identifier),
        "table_cell_accuracy": _accuracy(expected_flat, actual_flat, lambda path, _v: "[" in path),
        "missing_field_rate": len(missing) / total if total else 0.0,
        "hallucinated_field_rate": len(hallucinated) / len(actual_flat) if actual_flat else 0.0,
        "expected_field_count": total,
        "actual_field_count": len(actual_flat),
        "missing_fields": missing,
        "hallucinated_fields": hallucinated,
    }
    if schema is not None and actual is not None:
        result["schema_validity"] = not list(Draft202012Validator(schema).iter_errors(actual))
    return result


def score_json(
    expected: Mapping[str, Any], candidate: str | Mapping[str, Any]
) -> dict[str, Any]:
    """Parse and score one JSON extraction, returning validity separately."""
    actual: Mapping[str, Any] | None
    if isinstance(candidate, str):
        try:
            loaded = json.loads(candidate)
        except json.JSONDecodeError:
            loaded = None
    else:
        loaded = candidate
    actual = loaded if isinstance(loaded, Mapping) else None
    result = score_fields(expected, actual)
    result["json_validity"] = actual is not None
    return result
