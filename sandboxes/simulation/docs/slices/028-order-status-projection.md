# Slice 028: order-status projection

- **Implementation pack:** WNT Python event-sourced simulation
- **Runtime target:** headless Python
- **Architecture mode:** event-derived lifecycle read model

## Use-case contract

Existing domain facts produce order views with side, requested quantity,
remaining quantity, and status: accepted, partially filled, filled, cancelled,
or rejected. The read model adds no new economic authority.

## Done criteria

- Buy and sell reservation lifecycles are visible.
- Partial fills expose remaining quantity.
- Projection rebuild reconstructs statuses from facts.

Out of scope: API serialization, pagination, and mutable order-status commands.
