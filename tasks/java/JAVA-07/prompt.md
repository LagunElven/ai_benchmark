# Catalog lookup optimization

Optimize `CatalogSearch.findByPrefix` while preserving its behavior. Match product SKUs
by a case-insensitive, trimmed prefix, preserve input order, skip null products and
return an independent empty/result list for null inputs or blank prefixes. The method
must not mutate the source list or return an alias. Keep the record and method
signatures, do not modify tests, and change only the implementation file.
