# Hibernate dirty-field update

Implement `CustomerDirtyUpdate.apply`. The `dirtyFields` map contains only fields
actually changed by a request; update those fields and leave every other entity field
untouched. A present key with a null value is an intentional null assignment. Supported
keys are `name`, `status` and `points`; reject unknown keys or incompatible value types
with `IllegalArgumentException`. Reject a null entity/map. Do not modify tests.
