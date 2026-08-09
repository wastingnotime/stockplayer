# Slice 025: sell-reservation cancellation

- **Implementation pack:** WNT Python event-sourced simulation
- **Runtime target:** headless Python
- **Architecture mode:** owned-quantity release lifecycle

## Use-case contract

Cancelling an open sell reservation emits `SellReservationCancelled` and
releases its held quantity. The position remains unchanged, and the released
units can be reserved by a later sell order.

## Deterministic scenario

Buy 10 AUR, reserve 6, cancel that reservation, then reserve all 10 for a new
order. Replaying the stream leaves no first reservation and one active
10-unit reservation.

## Done criteria

- Release is explicit and replayable.
- Position ownership is unchanged by cancellation.
- Released quantity can be reserved again.

Out of scope: sell execution, partial sell fills, and order-status projections.
