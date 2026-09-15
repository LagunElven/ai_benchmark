# Backward-compatible greeting API

Keep the existing `greeting(String)` method behavior (`Hello, <name>!`) while making
the new `greeting(String, Locale)` overload work. Use `Bonjour,` for French, `Hallo,`
for German and `Hello,` for every other/null locale. Reject a null or blank name with
`IllegalArgumentException`, trim the name, and do not change the old method's binary
signature. Do not modify tests.
