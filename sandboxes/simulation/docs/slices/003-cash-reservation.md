# Slice 003: limit-buy cash reservation

- **Implementation pack:** WNT Python event-sourced simulation
- **Runtime target:** headless Python
- **Architecture mode:** explicit reservation state and competing commands

## Use-case contract

An accepted limit-buy order reserves its maximum settlement cost immediately.
Reserved cash is unavailable to later orders. A competing order that exceeds
remaining available cash is rejected without changing the existing reservation.

## Deterministic scenario

Fund `acct-reservation` with 100,000 minor units. Reserve 20 AUR at a 2,000
minor-unit limit (40,000 reserved), then submit 31 AUR at the same limit. The
first produces `LimitBuyReserved`; the second produces `OrderRejected`. Final
available cash is 60,000 and reserved cash is 40,000.

## Done criteria

- Reservation and available cash survive event replay.
- Competing orders cannot consume reserved funds.
- Projection state exposes available, reserved, and reservation-by-order values.

Out of scope: cancellation/release, execution of reserved orders, partial
fills, sell-side quantity reservations, and concurrency retries.
