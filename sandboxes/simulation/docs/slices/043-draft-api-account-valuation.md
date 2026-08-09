# Slice 043 — Draft API account valuation

## Build

Include projected valuation fields in the draft account query: average cost,
cost basis, realized result, and unrealized result at the environment's
current deterministic market price.

## Refinement check

The facade composes existing projection values and market data; it does not
reimplement cost-basis or result arithmetic. A buy-then-sell facade test
verifies the resulting valuation snapshot.

## Boundary

Valuation is a draft read model. Portfolio aggregation, currency formatting,
and production freshness guarantees remain deferred.
