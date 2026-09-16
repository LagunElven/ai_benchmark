# Conditional registration form

Implement `validateRegistration(input)` as a pure validator suitable for an Angular
reactive form. Return `{ valid, value, errors }`, where `errors` maps field names to an
array of stable error codes and `value` contains only the normalized form fields.

Normalize email to trimmed lowercase, account type to trimmed lowercase, company name by
trimming, and VAT numbers by removing internal whitespace and uppercasing. Email must be
present and syntactically valid. Password must be present, at least 12 characters, contain
an upper-case letter, a lower-case letter and a digit, and contain no whitespace.
Confirmation must match the password. Account type is `individual` or `business`.
Business registrations require a nonblank company name and a VAT number matching two
letters followed by 8 to 14 letters or digits. Terms must be exactly accepted. Individual
registrations may leave business fields blank. Do not mutate the input or return unknown
fields in `value`.
