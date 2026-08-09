# Slice 039 — Draft API sell reservation

## Build

Expose market-sell quantity reservation through the draft facade. The adapter
delegates the hold command and returns projected positions, reserved
quantities, and order state.

## Refinement check

Holding availability, short-sale prevention, session enforcement, and
idempotency remain in the domain and application layers. A facade test covers
a buy followed by a four-unit sell reservation.

## Boundary

Sell-reservation execution and cancellation remain separate operations. This
is unreleased draft behavior.
