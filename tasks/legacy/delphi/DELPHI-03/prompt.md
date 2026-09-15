# Delphi payment surcharge

The Pascal fixture is the business reference. Correct `PaymentRule.totalCents`: add a
2% surcharge (integer cents, truncated) only when the payment is at least 10,000 cents
and uses method `CARD`; all other payments keep their original amount. Treat method
codes case-insensitively, reject negative amounts with `IllegalArgumentException`, and
leave inputs unchanged. Keep the Java API and do not modify tests.
