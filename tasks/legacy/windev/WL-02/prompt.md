# HFSQL-style customer query

Correct `CustomerRepository.findActiveByRegion`. It must return active customers whose
region equals the requested region case-insensitively after trimming. Preserve input
order, return an empty list for a null/blank region or null input list, skip null
customers, and never mutate the source list. The returned list must be independent of
the input. Keep the Java API and do not modify tests.
