# Slice 036 — Draft API limit-buy cancellation

## Build

Expose cancellation for a reserved limit buy through the draft facade. The
adapter delegates to the existing cancellation use case and returns the
projected account state.

## Refinement check

Reservation release, lifecycle validation, and event sequencing remain domain
responsibilities. A facade test verifies the canonical `OrderCancelled` event,
released cash, and cancelled order projection.

## Boundary

This remains an unreleased draft operation. Authorization and transport error
mapping are deferred to the released API contract.
