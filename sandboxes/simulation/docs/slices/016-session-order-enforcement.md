# Slice 016: session-aware order enforcement

- **Implementation pack:** WNT Python event-sourced simulation
- **Runtime target:** headless Python
- **Architecture mode:** application session gate

## Use-case contract

Buy, sell, limit reservation, and limit execution commands require an open
market session. A closed or paused session rejects new economic commands with
an explicit reason and no economic mutation. Cancellation remains available to
release an existing hold.

## Deterministic scenario

Seed and open an account, close the session, then submit a market buy. The
account stream gains `OrderRejected`, cash remains unchanged, and no execution
is recorded.

## Done criteria

- Application handlers enforce session state.
- Rejection is replayable and projection-safe.
- Existing open-session scenarios remain deterministic.

Out of scope: calendar scheduling, queued orders across sessions, and exchange
holiday policy.
