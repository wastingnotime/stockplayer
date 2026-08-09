# Slice 012: deterministic price ticks

- **Implementation pack:** WNT Python event-sourced simulation
- **Runtime target:** headless Python
- **Architecture mode:** append-only market facts and rebuildable price view

## Use-case contract

Market prices are represented by ordered `PriceTick` facts containing symbol,
exact minor-unit price, simulated time, sequence, and source seed. A price view
rebuilds from the same ordered facts and exposes the latest price per symbol.

## Deterministic scenario

Publish AUR ticks at 2,500 and 2,700 with seed 42. The latest price is 2,700;
rebuilding from the facts produces the same history and current view. A skipped
sequence is rejected.

## Done criteria

- Price facts are separate from account economic events.
- Sequence and positive-price invariants are explicit.
- Current-price view is replayable from the tick history.

Out of scope: random-walk generation, exchange sessions, wall-clock timing,
price prediction, and external feeds.
