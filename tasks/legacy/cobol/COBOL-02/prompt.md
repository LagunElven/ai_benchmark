# Preferred-customer discount

The supplied COBOL excerpt is the business reference. Correct the Java replacement
`DiscountRule.netCents` so that a preferred customer (`P`) receives a 10% discount
when the gross amount is at least 100,000 cents. All other customers and amounts keep
the gross amount. The result is integer cents, with the discount truncated toward zero.

Do not apply a discount to a null/other customer code, do not mutate inputs, preserve
the method signature, and do not modify tests. Return a `file_changes_v1` response.
