# Slice 010: cost basis and realized result

- **Implementation pack:** WNT Python event-sourced simulation
- **Runtime target:** headless Python
- **Architecture mode:** execution-derived financial projection

## Use-case contract

The position projection tracks total acquisition cost and exposes average cost.
Selling units removes a deterministic proportional cost basis and records the
difference between proceeds and basis as realized result. Integer division uses
floor rounding; the remaining cost carries the unallocated remainder.

## Deterministic scenario

Buy 10 AUR at 2,500 and 5 AUR at 3,000. The position is 15 with average cost
2,666 minor units. Sell 5 at 3,000; 1,667 minor units are realized and the
remaining 10 units retain average cost 2,666.

## Done criteria

- Cost basis is rebuilt from executions.
- Average cost and realized result are deterministic.
- Sale quantity and position remain non-negative.

Out of scope: unrealized result, fees, tax, fractional quantities, and alternate
rounding policies.
