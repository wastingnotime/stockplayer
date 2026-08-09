# Slice 024: sell-side quantity reservation

- **Implementation pack:** WNT Python event-sourced simulation
- **Runtime target:** headless Python
- **Architecture mode:** owned-quantity reservation

## Use-case contract

An accepted sell reservation holds owned units against the order. The position
projection remains unchanged, but later sell reservations cannot consume the
held quantity. Oversubscription produces an explicit rejection.

## Deterministic scenario

Buy 10 AUR, reserve 6 for one sell order, then attempt to reserve 5 more. The
first emits `SellQuantityReserved`; the second is rejected because only 4 units
remain available. Position remains 10.

## Done criteria

- Reserved quantity survives replay.
- Competing reservations cannot double-spend ownership.
- Rejected reservation has no economic mutation.

Out of scope: sell execution, release/cancellation, short selling, and
reservation read-model APIs.
