# Slice 027: partial sell-reservation execution

- **Implementation pack:** WNT Python event-sourced simulation
- **Runtime target:** headless Python
- **Architecture mode:** repeated reserved-ownership settlement

## Use-case contract

A sell reservation may execute a positive quantity smaller than its held amount.
Proceeds and cost basis update for that fill, while remaining owned and
reserved quantities stay available for a later fill.

## Deterministic scenario

Buy 10 AUR, reserve 6, execute 2 at 3,000. Position becomes 8, reserved
quantity becomes 4, and cash becomes 81,000. A later full execution may consume
the remaining four.

## Done criteria

- Partial execution is an explicit replayable fact.
- Remaining hold is exact and cannot become negative.
- Repeated fills do not double-spend ownership.

Out of scope: partial-fill order status projections and sell-side limit prices.
