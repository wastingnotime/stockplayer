# Slice 004: cancellation and reservation release

- **Implementation pack:** WNT Python event-sourced simulation
- **Runtime target:** headless Python
- **Architecture mode:** order lifecycle fact with compensating reservation release

## Use-case contract

An open limit-buy order may be cancelled once. Cancellation emits an explicit
`OrderCancelled` fact, releases exactly the order's held cash, and leaves no
active reservation. Rehydration must reconstruct the released state.

## Deterministic scenario

Fund an account with 100,000 minor units, reserve 20 AUR at 2,000, then cancel
the order. Final available cash is 100,000, reserved cash is zero, and the
reservation map is empty.

## Done criteria

- Cancellation releases only the matching order's reservation.
- Replayed state matches the post-cancellation projection.
- Missing or already-cancelled orders are rejected without mutation.

Out of scope: execution of reserved orders, partial fills, sell-side quantity
reservations, and asynchronous cancellation delivery.
