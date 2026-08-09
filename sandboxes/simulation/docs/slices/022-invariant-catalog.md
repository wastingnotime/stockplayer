# Slice 022: invariant catalog

- **Implementation pack:** WNT Python event-sourced simulation
- **Runtime target:** headless Python and WNT MRL Runtime
- **Architecture mode:** named repository-owned invariant checks

## Use-case contract

The simulation exposes reusable checks for non-negative cash, positions,
reservations, and ledger explanation of total cash. Runtime supervision names
these checks and records their results after scheduled actions.

## Deterministic scenario

Run the supervised purchase, price, failure/recovery, engine comparison, and
session timeline. All four named invariants remain true after projection
rebuild.

## Done criteria

- Invariants are reusable outside the runtime adapter.
- Reserved cash is included when reconciling ledger total cash.
- Runtime evidence reports named invariant results.

Out of scope: property-based generation, invariant repair, and external policy
engines.
