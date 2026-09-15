# ABAL benefit eligibility

The supplied ABAL/Open ABAL reference is intentionally marked synthetic. Correct the
Java compatibility rule: a claimant is eligible when they are retired **or** disabled,
and their monthly income is no more than 250,000 cents. Income below zero is invalid
and must raise `IllegalArgumentException`; otherwise return only the boolean decision.

Do not invent proprietary syntax, keep the method signature, and do not modify tests.
