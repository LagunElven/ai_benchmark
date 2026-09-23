from __future__ import annotations

import unittest
from unittest.mock import patch

from runner.context_budget import assess_context_budget


class _Tokenizer:
    def apply_chat_template(self, messages, **kwargs):
        del kwargs
        return list(range(sum(len(message["content"]) for message in messages)))


class ContextBudgetTests(unittest.TestCase):
    def test_exact_serialized_prompt_reserves_output_and_safety_margin(self) -> None:
        messages = [{"role": "user", "content": "a fairly long prompt"}]
        model = {
            "name": "local/test",
            "tokenizer_repository": "local/test",
            "tokenizer_revision": "rev-1",
            "generation": {"chat_template_kwargs": {"enable_thinking": False}},
        }
        with patch("runner.context_budget._load_huggingface_tokenizer", return_value=_Tokenizer()):
            result = assess_context_budget(
                messages,
                model=model,
                serving={"max_model_length": 30},
                runner={"context_safety_margin_tokens": 4},
                output_tokens=10,
            )
        self.assertEqual(result["status"], "rejected")
        self.assertTrue(result["input_token_count_exact"])
        self.assertEqual(result["input_tokens"], len("a fairly long prompt"))
        self.assertEqual(result["required_total_tokens"], len("a fairly long prompt") + 14)

    def test_regex_estimate_never_causes_capacity_rejection(self) -> None:
        with patch("runner.context_budget._load_huggingface_tokenizer", return_value=None):
            result = assess_context_budget(
                [{"role": "user", "content": "one two three"}],
                model={"name": "unknown", "generation": {}},
                serving={"max_model_length": 4},
                runner={"context_safety_margin_tokens": 0},
                output_tokens=1,
            )
        self.assertEqual(result["status"], "unverified_estimate")
        self.assertFalse(result["input_token_count_exact"])


if __name__ == "__main__":
    unittest.main()
