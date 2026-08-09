# Slice 013: seeded price generation

- **Implementation pack:** WNT Python event-sourced simulation
- **Runtime target:** headless Python
- **Architecture mode:** deterministic market actor

## Use-case contract

Given a seed, current positive price, sequence, and simulated time, the market
actor emits a bounded `PriceTick`. It uses private seeded randomness and never
reads wall-clock time or global random state.

## Deterministic scenario

Two generators with seed 42 and the same starting price produce equal ordered
ticks. Each tick records seed, sequence, price, and simulated time and can be
appended to the price history.

## Done criteria

- Same seed and inputs produce the same ticks.
- Price never falls below one minor unit.
- Generated ticks remain compatible with price-history replay.

Out of scope: prediction, calibration to real markets, external feeds, and
statistical claims about generated prices.
