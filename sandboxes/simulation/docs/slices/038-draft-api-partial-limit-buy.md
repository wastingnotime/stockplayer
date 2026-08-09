# Slice 038 — Draft API partial limit-buy execution

## Build

Expose partial execution for a reserved limit buy through the draft facade.
The adapter translates fill quantity, execution identity, and price, then
returns the projected remaining reservation and order lifecycle.

## Refinement check

Partial-fill validation, cash reservation arithmetic, idempotency, and event
sequencing remain in the existing application and domain. A facade test
verifies a four-unit fill from a ten-unit reservation, including the
application's deterministic release and re-hold arithmetic.

## Boundary

This remains an unreleased draft operation. Transport authorization and fill
streaming are deferred.
