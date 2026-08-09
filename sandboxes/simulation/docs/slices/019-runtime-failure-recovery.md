# Slice 019: runtime failure and recovery evidence

- **Implementation pack:** WNT Python event-sourced simulation
- **Runtime target:** WNT MRL Runtime supervised scenario
- **Architecture mode:** observable failure boundary and rebuild recovery

## Use-case contract

The supervised scenario injects a projection failure after an execution event
has been appended. It emits failure evidence, rebuilds the projection from the
account stream, and emits recovery evidence with the restored state.

## Deterministic scenario

After the initial purchase and price tick, a second buy fails during projection
at simulated 2.5 seconds. The stream remains authoritative; recovery rebuilds
cash and position before session close. Repeated runs produce identical JSONL.

## Done criteria

- Failure and recovery observations share a correlation ID.
- Recovery runs before the session closes.
- Invariants remain true after rebuild.

Out of scope: process restart orchestration, durable snapshots, and distributed
worker coordination.
