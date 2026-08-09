# Slice 002: insufficient-funds rejection

- **Implementation pack:** WNT Python event-sourced simulation
- **Runtime target:** headless Python
- **Architecture mode:** explicit rejection fact with no economic projection

## Use-case contract

When a market-buy command costs more than available cash, reject it with an
explicit reason. Persist the rejection for audit and replay, but create no
execution, cash movement, or position change.

## Deterministic scenario

At the same simulated time as slice 001, fund `acct-insufficient` with 1,000
minor units and submit 10 AUR at 2,500 minor units. The stream gains exactly one
`OrderRejected` fact with reason `insufficient available cash`; cash remains
1,000 and the position remains empty.

## Done criteria

- Rejection is an event-sourced domain fact.
- Replaying the stream preserves the rejection without economic effects.
- Unit checks verify reason, stream append, and unchanged projections.

Out of scope: reservations, order status aggregates, sells, limits, and
asynchronous rejection delivery.
