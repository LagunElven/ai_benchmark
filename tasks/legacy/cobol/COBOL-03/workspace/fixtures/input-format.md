# Portable record representation

The native COBOL record contains an identifier, a signed `PIC S9(7)V99 COMP-3` amount
and a one-character status. For the dependency-free Java equivalence harness, each
sequential logical record is represented as `identifier|amount|status`:

- `identifier` is nonblank;
- `amount` is a signed decimal with zero, one or two fractional digits;
- `status` is one character, and only uppercase `P` is posted.

This text format is a test adapter for the binary packed-decimal field, not a claim that
the COBOL runtime stores `COMP-3` as text.
