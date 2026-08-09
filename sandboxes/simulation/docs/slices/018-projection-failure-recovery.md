# Slice 018: projection failure and recovery

- **Implementation pack:** WNT Python event-sourced simulation
- **Runtime target:** headless Python
- **Architecture mode:** persisted event before rebuildable projection

## Use-case contract

If projection processing fails after event append, the event remains authoritative
and the read model may temporarily lag. Rebuilding from the complete stream
replays the missing economic effect exactly once.

## Deterministic scenario

Inject a projection failure during a market buy. The account stream contains the
buy event while cash remains at its pre-buy projection. Rebuild from history;
cash becomes 75,000 and the position becomes 10 AUR.

## Done criteria

- Failure occurs after append and before projection mutation.
- Rebuild catches up without duplicate settlement.
- Recovery state matches normal incremental projection.

Out of scope: process supervision, durable snapshots, message brokers, and
distributed consensus.
