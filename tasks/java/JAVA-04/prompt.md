# Thread-safe inventory reservation

Fix `Inventory.reserve`. A reservation succeeds only when the SKU exists and enough
stock is available; a successful reservation decrements stock by exactly the requested
quantity and returns `true`. Invalid or non-positive quantities return `false`.

Concurrent callers must not oversell stock or lose updates. Keep the API and map shape,
do not serialize unrelated instances globally, do not modify tests, and change only the
implementation file. Return a `file_changes_v1` response.
