# Slice 034 — Draft API timestamp boundary

## Build

Validate that `occurred_at` values supplied to the draft facade carry an
explicit UTC offset. The adapter normalizes `Z` to UTC and rejects naive
timestamps before constructing an application command.

## Refinement check

This is transport-shape validation only. Event ordering and business-time
policy remain owned by the application and domain layers. A unit test covers a
naive timestamp rejection while existing offset-bearing commands continue to
pass.

## Boundary

The validation is draft behavior, not a released wire-format guarantee.
