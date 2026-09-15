# Legacy fixtures

Legacy tasks keep the original source, a fixture manifest and an executable
Java equivalence target together. The manifest records whether source syntax is
verified or deliberately synthetic. A native compiler is never implied by a
fixture status.

- COBOL-05 uses a standard fixed-format source and falls back to Java while
  GnuCOBOL (cobc) is unavailable.
- DELPHI-04 uses a small standard Object Pascal subset and executable Java
  vectors because Delphi is not installed.
- WL-04 is explicitly synthetic WLanguage pseudocode with a supplied semantic
  reference; it is not a claim about proprietary WinDev syntax.
- ABAL-04 is explicitly synthetic ABAL pseudocode with supplied documentation;
  ABAL is Advanced Business Application Language, not ABAP.

Run python scripts/check_legacy_toolchains.py --json to record the native
toolchains available on the current machine.
