# Slice 026: sell-reservation execution

- **Implementation pack:** WNT Python event-sourced simulation
- **Runtime target:** headless Python
- **Architecture mode:** reserved ownership settlement

## Use-case contract

Executing a sell reservation consumes its held quantity, settles proceeds, and
removes the reservation. Direct sells cannot consume units already held by a
reservation. Position ownership decreases only once.

## Deterministic scenario

Buy 10 AUR, reserve 6, reject a direct sell of 5 because only 4 are available,
then execute the reservation at 3,000. Cash becomes 93,000, position becomes 4,
and the reservation disappears.

## Done criteria

- Reserved execution is replayable.
- Direct and reserved sell paths cannot double-spend quantity.
- Proceeds and position projections remain explainable.

Out of scope: partial sell fills, sell limit prices, and fees.
