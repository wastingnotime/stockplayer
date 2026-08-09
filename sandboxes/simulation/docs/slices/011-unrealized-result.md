# Slice 011: unrealized result

- **Implementation pack:** WNT Python event-sourced simulation
- **Runtime target:** headless Python
- **Architecture mode:** valuation query over execution-derived projection

## Use-case contract

For a current simulated price, unrealized result is current position quantity
times that price minus persisted acquisition cost. It is a read-side valuation,
not a cash movement or domain event.

## Deterministic scenario

After buying 15 AUR for 40,000 minor units, a current price of 3,000 yields an
unrealized result of 5,000. After selling 5 units and realizing 1,667, the
remaining 10-unit position has an unrealized result of 3,333 at the same price.

## Done criteria

- Valuation uses exact integer minor units.
- Unrealized result does not alter cash, ledger, or event history.
- Invalid non-positive prices are rejected.

Out of scope: price prediction, mark-to-market events, fees, tax, and financial
advice.
