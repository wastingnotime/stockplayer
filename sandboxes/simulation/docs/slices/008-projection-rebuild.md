# Slice 008: projection rebuild

- **Implementation pack:** WNT Python event-sourced simulation
- **Runtime target:** headless Python
- **Architecture mode:** rebuildable read model

## Use-case contract

Given an account's complete event stream, a fresh projection can rebuild cash,
reservations, ledger, and positions to the same state as the incrementally
maintained projection.

## Deterministic scenario

Fund an account, reserve a limit buy, and partially execute it. Rebuild a fresh
projection from the stream and compare all read-model values with the live
projection.

## Done criteria

- Rebuild clears stale state before replay.
- Duplicate execution protection remains active during rebuild.
- Rebuilt and incremental read models compare equal.

Out of scope: persistence-backed snapshots, projection lag metrics, and
operator-facing rebuild APIs.
