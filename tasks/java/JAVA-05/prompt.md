# Behavior-preserving pricing refactor

Simplify `OrderPricing.totalCents` without changing its business contract. Sum all line
subtotals (`quantity * unitCents`), reject null lines, non-positive quantities or
negative unit prices, and return zero for a null/empty list. Premium orders receive a
10% discount when the subtotal is at least 10,000 cents (discount truncated to whole
cents). Add 500 cents shipping unless the discounted subtotal is at least 5,000 cents.
Use exact integer arithmetic and reject a result outside the `int` range.

Keep the record and method signatures, do not modify tests, and change only the
implementation file. Return a `file_changes_v1` response.
