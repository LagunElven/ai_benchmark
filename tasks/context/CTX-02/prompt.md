# CTX-02 - long-context repository repair at 30k tokens

This workspace is the 30k-token variant of the same repository-understanding task.
It contains many unrelated architecture notes, fixtures and generated distractors.
Locate the billing implementation and fix `calculate_total` without changing
its public signature or unrelated files.

The business rule is: sum line amounts, apply the percentage discount before tax,
then apply tax; round only the final result to two decimals using
`Decimal`/`ROUND_HALF_UP`. A missing discount or tax is zero. Preserve input order
and avoid binary floating point. Do not modify tests, reference notes or generated
distractors. Return only the `file_changes_v1` JSON object.
