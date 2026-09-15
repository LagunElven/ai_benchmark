# Historical decisions (read-only)

The repository contains several generations of services. These compact notes
are intentionally noisy context for CTX-01 and must not be edited.

- The first API used integer cents; the current API uses decimal money values.
- A timezone migration changed local midnight handling but not invoice math.
- The old reporting service rounded every line; the billing service rounds last.
- Discounts are represented as percentages in the public command contract.
- Tax is calculated after discounts for every supported market in this fixture.
- Null optional percentages mean zero, not an omitted calculation step.
- Decimal contexts are configured at call sites to make rounding explicit.
- Financial values are never converted through float, double or JSON strings.
- The billing package has no dependency on the HTTP, persistence or UI layers.
- Repository notes are evidence for humans and are not executable specifications.
- Tests import the public function so a signature change is a compatibility break.
- A patch should be narrow: unrelated reference files reduce file precision.
- Hidden checks include a zero discount and a half-cent final rounding case.
- The smoke task is deliberately small enough to run on an ordinary laptop.
