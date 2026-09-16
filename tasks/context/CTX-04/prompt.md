# CTX-04 - long-context repository repair at 100k tokens

This workspace is the 100k-token variant of the same repository-understanding task.
It contains many unrelated architecture notes, fixtures and generated distractors.
Locate the actual billing implementation in `src/billing.py` and fix
`calculate_total` without changing its public signature or unrelated files.

The business rule is: sum line amounts, apply the percentage discount before tax,
then apply tax; round only the final result to two decimals using
`Decimal`/`ROUND_HALF_UP`. A missing discount or tax is zero. Preserve input order
and avoid binary floating point. Do not modify tests, reference notes, generated
distractors or `context-manifest.json`. Return only the `file_changes_v1` JSON object.
