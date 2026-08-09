# Slice 009: market sell and short-selling protection

- **Implementation pack:** WNT Python event-sourced simulation
- **Runtime target:** headless Python
- **Architecture mode:** cash-account ownership invariant

## Use-case contract

An account may submit a market sell only for quantity it currently owns. A
successful sell records proceeds, reduces the position, and adds cash. A sell
above owned quantity is rejected without an economic effect. Short selling is
not supported.

## Deterministic scenario

Buy 10 AUR at 2,500, sell 4 at 3,000, then attempt to sell 7. Final cash is
87,000, the position is 6 AUR, and the second sell produces an explicit
`OrderRejected` fact.

## Done criteria

- Sell settlement is replayable and projection-backed.
- Owned quantity never becomes negative.
- Rejected oversells do not mutate cash or position.

Out of scope: sell reservations, short selling, realized/unrealized P&L, and
average-cost accounting.
