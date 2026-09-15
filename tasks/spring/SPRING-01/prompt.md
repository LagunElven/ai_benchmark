# REST registration validation

`RegistrationValidator` is the validation layer behind a Spring REST endpoint. Return
all validation messages in the documented order, rather than stopping at the first
error:

1. `email` is required and must contain exactly one `@` with non-blank local and domain parts;
2. `tenant` is required and must contain only lowercase letters, digits and hyphens;
3. `age` is required and must be at least 18.

Trim text fields before checking them. A valid request returns an empty list. Preserve
the record and method signatures, do not add Spring dependencies, and do not modify tests.
Return a `file_changes_v1` response.
