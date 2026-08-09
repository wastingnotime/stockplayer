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
20. Runtime engine comparison evidence (built).
21. Invariant catalog (built).
22. Scenario catalog (built).
23. Sell-side quantity reservation (built).
24. Sell-reservation cancellation (built).
25. Sell-reservation execution (built).
26. Partial sell-reservation execution (built).
27. Order-status projection (built).
28. Runtime order timeline (built).
29. Order-command idempotency (built).
30. Draft API adapter (built; unreleased).
31. Draft API sell adapter (built; unreleased).
32. Draft API order query (built; unreleased).
33. Draft API timestamp boundary (built; unreleased).
34. Draft API limit-buy adapter (built; unreleased).
35. Draft API limit-buy cancellation (built; unreleased).
36. Draft API limit-buy execution (built; unreleased).
37. Draft API partial limit-buy execution (built; unreleased).
38. Draft API sell reservation (built; unreleased).
39. Draft API sell-reservation cancellation (built; unreleased).
40. Draft API sell-reservation execution (built; unreleased).
41. Draft API partial sell-reservation execution (built; unreleased).
42. Draft API account valuation query (built; unreleased).
43. Draft API market-session query (built; unreleased).
44. Draft API market-price query (built; unreleased).
45. Draft API single market-price query (built; unreleased).
46. Released API and browser adapter contracts.

The order is a hypothesis and must change when refinement evidence reveals a
better boundary.

## Open questions

- Which fictional currency name and precision should become public contract?
- Should fractional quantities ever be supported?
- What deterministic liquidity rule best exposes partial fills?
- Which order facts belong to the account stream versus a dedicated stream?
