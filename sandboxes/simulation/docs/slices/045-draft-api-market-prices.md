# Slice 045 — Draft API market-price query

## Build

Expose the deterministic environment market prices through the draft facade.
The response is a copy of the current symbol-to-minor-unit mapping.

## Refinement check

The adapter reads the existing market-data boundary and does not generate,
advance, or validate prices itself. A test covers multiple symbols and integer
minor-unit values.

## Boundary

Price history, streaming updates, and production freshness guarantees remain
outside this unreleased query.
