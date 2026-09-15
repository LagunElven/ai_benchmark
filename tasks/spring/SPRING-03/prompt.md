# Transactional transfer rollback

Implement `TransferService.transfer` as one atomic operation over the supplied
`Accounts` store. A positive transfer debits `from` and credits `to`; it succeeds only
when both accounts exist, the amount is positive, and the destination accepts credits.
If crediting fails, the debit must be rolled back exactly. Reject self-transfers and
never leave a partial balance update. The store is shared by concurrent calls, so
protect the transaction per store without a global lock. Keep the public API and do not
modify tests.
