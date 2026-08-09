# Slice 007: idempotent execution delivery

- **Implementation pack:** WNT Python event-sourced simulation
- **Runtime target:** headless Python
- **Architecture mode:** execution identity and projection deduplication

## Use-case contract

An execution identified by an existing execution ID has no second economic
effect. Retrying the command returns no new event, and delivering the same
execution fact to a projection again does not duplicate ledger or position
changes.

## Deterministic scenario

Partially execute `execution-1` once, retry the same command, and deliver its
event to the projection a second time. Cash, reservation, position, ledger,
and event-stream state remain equal to the single-delivery result.

## Done criteria

- Account replay tracks execution IDs.
- Command retries are no-ops.
- Projection retries are no-ops.

Out of scope: cross-account idempotency keys, message brokers, and failure
recovery around event persistence.
