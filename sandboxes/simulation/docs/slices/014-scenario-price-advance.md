# Slice 014: scenario price advancement

- **Implementation pack:** WNT Python event-sourced simulation
- **Runtime target:** WNT MRL Runtime supervised scenario
- **Architecture mode:** scheduled market actor and valuation observation

## Use-case contract

The shared scenario schedules a seeded market actor after a purchase. The actor
appends a deterministic price tick, updates the market adapter, and emits a
valuation observation. Settlement cash and account event history remain
unchanged by the valuation update.

## Deterministic scenario

The simple-purchase scenario buys AUR at 2,500, advances one seeded tick at
simulated second two, and emits both `price_tick` and
`unrealized_result_updated`. Running the scenario twice produces identical
JSONL observations.

## Done criteria

- The runtime adapter exposes market and valuation observations.
- Price advancement is scheduled on simulated time.
- Deterministic supervision evidence includes the new observations.

Out of scope: browser refresh timing, live feeds, prediction, and market-session
rules.
