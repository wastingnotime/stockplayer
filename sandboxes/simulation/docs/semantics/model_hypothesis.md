# Model hypothesis

## Boundary

The simulation owns fictional accounts, securities, market time and price,
orders, executions, cash-ledger facts, position projections, and deterministic
scenario evidence. Technology adapters and persistence products are outside the
model boundary until model release.

## Current vocabulary

- **Account**: event-sourced authority for fictional cash and purchased units.
- **Security**: fictional instrument with a symbol and current valid price.
- **Order**: instruction whose lifecycle is submitted, accepted, filled, or
  rejected; rejection is now an explicit event fact.
- **Execution**: full fill of an accepted order at an exact price.
- **Cash ledger**: projection of deposits and trade settlement.
- **Position**: execution-derived quantity and cost projection.
- **Reservation**: cash held against an accepted limit-buy order until execution
  or cancellation releases it.
- **Scenario**: seeded initial state, explicit clock, scheduled intentions, and
  monitored invariants.

## Current rules

Cash is integer minor units and quantity is a positive integer. A market buy
requires a positive current price and sufficient available cash. Acceptance and
execution are atomic in the first engine; fees and reservations are zero/not
needed for immediate full fills. Insufficient cash produces `OrderRejected`
without changing economic projections. Every balance change is explained by an
event, and replaying an event stream reconstructs the same account state.

## Candidate slice map

1. Simple deterministic market purchase (built).
2. Insufficient-funds rejection (built).
3. Limit-buy cash reservation and cancellation.
4. Market sell and quantity reservation.
3. Limit-buy cash reservation (built).
4. Cancellation and reservation release (built).
5. Reserved execution and settlement (built).
6. Partial execution and remaining reservation (built).
7. Duplicate execution defense and projection rebuild (built).
8. Market sell and no-short-selling (built).
9. Position cost basis and realized result (built).
10. Unrealized result valuation (built).
11. Deterministic price ticks (built).
12. Seeded price generation (built).
13. Scenario price advancement and valuation observations (built).
14. Market-session state machine (built).
15. Session-aware order enforcement (built).
16. Session observations (built).
17. Projection failure and recovery (built).
18. Runtime failure/recovery evidence (built).
19. Execution-engine comparison (built).
20. Released API and browser adapter contracts.

The order is a hypothesis and must change when refinement evidence reveals a
better boundary.

## Open questions

- Which fictional currency name and precision should become public contract?
- Should fractional quantities ever be supported?
- What deterministic liquidity rule best exposes partial fills?
- Which order facts belong to the account stream versus a dedicated stream?
