# WEB-03 — latest search result

`searchLatest(api, queries, onResult)` is the core of an Angular/RxJS search
pipeline. Start one request for every query, but emit only the result belonging
to the latest query that was started (the behavior of `switchMap`). Preserve
the input order when starting requests, return a promise that settles after all
requests have settled, and do not emit rejected stale requests. An error from
the latest request should reject the returned promise. Do not add dependencies
or modify tests. Return only the `file_changes_v1` JSON object.

The Node harness models the observable semantics without installing RxJS.
