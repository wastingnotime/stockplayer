# Slice 017: session observations

- **Implementation pack:** WNT Python event-sourced simulation
- **Runtime target:** WNT MRL Runtime supervised scenario
- **Architecture mode:** observable market availability

## Use-case contract

The supervised scenario emits semantic observations when the market session
opens and closes. These observations correlate session availability with the
purchase and price-valuation timeline without creating economic ledger facts.

## Deterministic scenario

The scenario opens at setup, buys at simulated second one, advances price at
second two, and closes at second three. Repeated runs emit identical session
observations and leave settled cash unchanged.

## Done criteria

- Session transitions are visible in runtime JSONL.
- Opening and closing are ordered around the existing scenario actions.
- Session observations do not alter account projections.

Out of scope: browser session indicators, calendars, holidays, and queued-order
policy.
