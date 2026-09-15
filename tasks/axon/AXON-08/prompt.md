# Replay and projection rebuild

Implement `BalanceProjection.replay`. A replay must clear prior state and apply the
events in list order so the result is independent of the projection's previous live
state. `Credited` increases an account, `Debited` decreases it only when enough balance
exists, and invalid/null events are ignored. `balance` returns zero for unknown accounts.
Do not modify tests.
