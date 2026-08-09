# Slice 037 — Draft API limit-buy execution

## Build

Expose full execution for a reserved limit buy through the draft facade. The
adapter translates execution identity and price, delegates settlement, and
returns projected cash, position, and order state.

## Refinement check

Reservation release, limit validation, idempotency, session enforcement, and
settlement remain in the existing use case and domain. A facade test verifies
execution at a price below the reserved limit.

## Boundary

Partial execution and transport-level authorization remain separate concerns.
This operation is still unreleased draft behavior.
