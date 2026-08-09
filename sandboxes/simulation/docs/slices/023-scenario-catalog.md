# Slice 023: executable scenario catalog

- **Implementation pack:** WNT Python event-sourced simulation
- **Runtime target:** headless Python
- **Architecture mode:** explicit implemented/planned scenario boundary

## Use-case contract

The catalog names each architecture demonstration, its lesson, and its status.
Consumers can retrieve one spec or list implemented specs; unknown IDs fail
explicitly.

## Done criteria

- Scenario IDs are unique.
- Implemented and planned boundaries are explicit.
- Catalog integrity is tested.

Out of scope: automatically claiming a scenario is validated merely because
it appears in the catalog.
