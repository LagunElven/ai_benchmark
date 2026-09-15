# Null-safe email selection

`EmailSelector.firstUsable` is used when importing customer contact data. Return the
first usable address from the supplied list while preserving list order:

- a `null` list or a `null` element is allowed;
- trim surrounding whitespace;
- ignore blank values;
- normalize the selected value to lowercase with a locale-independent rule;
- return `Optional.empty()` when no value is usable.

Keep the public method and class names unchanged, do not modify tests, and only change
the implementation file. Return a `file_changes_v1` response.
