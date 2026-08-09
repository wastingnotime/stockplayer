# Slice 040 — Draft API sell-reservation cancellation

## Build

Expose cancellation for a reserved market sell through the draft facade. The
adapter delegates the command and returns projected reserved quantities and
order state.

## Refinement check

Hold release, lifecycle validation, and event sequencing remain domain-owned.
A facade test verifies the canonical cancellation event, released quantity,
and cancelled order projection.

## Boundary

Sell-reservation execution remains separate. This is unreleased draft
behavior.
