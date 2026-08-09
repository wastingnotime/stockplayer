# Slice 029: runtime order timeline

- **Implementation pack:** WNT Python event-sourced simulation
- **Runtime target:** WNT MRL Runtime supervised scenario
- **Architecture mode:** observable order read model

## Use-case contract

The scenario emits projected order status after the initial execution and after
projection recovery. Observations include order ID, lifecycle status, and
remaining quantity and are correlated with command/recovery evidence.

## Done criteria

- Order status is visible after normal projection.
- Rebuild emits the recovered order status.
- Runtime order evidence is deterministic.

Out of scope: API pagination, browser timeline rendering, and mutable status
commands.
