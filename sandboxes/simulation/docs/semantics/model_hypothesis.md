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
  rejected in the first slice.
- **Execution**: full fill of an accepted order at an exact price.
- **Cash ledger**: projection of deposits and trade settlement.
- **Position**: execution-derived quantity and cost projection.
- **Scenario**: seeded initial state, explicit clock, scheduled intentions, and
  monitored invariants.

## Current rules

Cash is integer minor units and quantity is a positive integer. A market buy
requires a positive current price and sufficient available cash. Acceptance and
execution are atomic in the first engine; fees and reservations are zero/not
needed for immediate full fills. Every balance change is explained by an event,
and replaying an event stream reconstructs the same account state.

## Candidate slice map

1. Simple deterministic market purchase (selected and built).
2. Insufficient-funds rejection.
3. Limit-buy cash reservation and cancellation.
4. Market sell and quantity reservation.
5. Partial execution and average acquisition cost.
6. Duplicate execution defense and projection rebuild.
7. Failure/recovery and projection lag.
8. Execution-engine comparison.
9. Released API and browser adapter contracts.

The order is a hypothesis and must change when refinement evidence reveals a
better boundary.

## Open questions

- Which fictional currency name and precision should become public contract?
- Should fractional quantities ever be supported?
- What deterministic liquidity rule best exposes partial fills?
- Which order facts belong to the account stream versus a dedicated stream?
