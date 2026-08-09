# Slice 042 — Draft API partial sell-reservation execution

## Build

Expose partial execution for a reserved market sell through the draft facade.
The adapter translates fill quantity, execution identity, and price, then
returns projected proceeds, remaining hold, position, and order lifecycle.

## Refinement check

Partial-fill validation, hold consumption, proceeds settlement, and
idempotency remain in the existing application and domain. A facade test
verifies a two-unit fill from a four-unit reservation.

## Boundary

This remains unreleased draft behavior; transport streaming and authorization
are deferred.
