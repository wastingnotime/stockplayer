# Slice 041 — Draft API sell-reservation execution

## Build

Expose full execution for a reserved market sell through the draft facade. The
adapter translates execution identity and price, delegates settlement, and
returns projected proceeds, position, reservation, and order state.

## Refinement check

Hold consumption, proceeds settlement, idempotency, and session enforcement
remain in the existing application and domain. A facade test verifies a
four-unit sale at an explicit execution price.

## Boundary

Partial sell execution remains a separate operation. This is unreleased draft
behavior.
