# Slice 035 — Draft API limit-buy adapter

## Build

Expose limit-buy submission through the draft facade. The adapter translates
the integer limit price and delegates reservation behavior to the existing
environment use case, returning the projected cash and order state.

## Refinement check

Reservation, affordability, session enforcement, and idempotency remain in the
application and domain layers. A facade test verifies reserved versus
available cash and the accepted order projection.

## Boundary

Limit-order execution and cancellation remain separate operations. This is an
unreleased draft adapter, not a production transport contract.
