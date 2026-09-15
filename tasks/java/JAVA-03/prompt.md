# Cart cleanup

`Cart.removeExpired` removes expired line items from a mutable list. The current implementation
can fail while traversing the list and must also preserve the order of non-expired items.

Correct the implementation so that:

- every expired line is removed;
- non-expired lines retain their original order;
- an empty cart and a cart with no expired line are handled;
- the public API and the `CartLine` data shape remain compatible;
- only files needed for the implementation are changed.

Do not modify tests. Return the requested `file_changes_v1` JSON response.
