# E2E-03

This task represents a legacy COBOL ledger rule modernized behind a Java service
and a Spring-style wire adapter. The COBOL source is supplied as a verified syntax
reference; the Java checks compare single entries, ordered batches, decimal scale
and invalid input behavior. Only `LedgerService.java` is expected to change.
