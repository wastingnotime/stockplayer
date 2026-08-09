# Slice 006: partial execution

- **Implementation pack:** WNT Python event-sourced simulation
- **Runtime target:** headless Python
- **Architecture mode:** repeated execution facts with remaining reservation

## Use-case contract

A reserved limit-buy order may execute a positive quantity smaller than its
remaining quantity at or below its limit. The actual cost is settled, unused
hold is released, the remaining quantity and hold stay open, and a later full
execution closes the reservation.

## Deterministic scenario

Reserve 20 AUR at 2,000. Execute 10 at 1,800, leaving 10 units and 20,000
reserved. Execute the remainder at 1,700. Final cash is 65,000 and the position
is 20 AUR, with two settlement entries.

## Done criteria

- Partial and final execution facts replay in order.
- Remaining quantity and reservation are exact after each fill.
- A partial quantity equal to or greater than remaining is rejected.

Out of scope: duplicate delivery, sell-side fills, average-cost projection, and
order-status read models.
