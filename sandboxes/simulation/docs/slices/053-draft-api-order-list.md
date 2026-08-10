# Slice 053 — Draft API order listing

## Build

Expose a focused `orders(account_id)` query beside the single-order lookup.
The adapter returns projected order views in deterministic order and an empty
list for accounts without orders.

## Refinement check

The query reads existing order projections and does not rebuild lifecycle
state. Tests cover a known order and an empty unknown-account result.

## Boundary

Pagination, filtering, and authorization remain deferred to the released API
contract.
