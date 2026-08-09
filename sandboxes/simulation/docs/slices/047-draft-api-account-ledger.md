# Slice 047 — Draft API account ledger

## Build

Include projected ledger entries in the draft account query. Entries are
serialized from the existing `LedgerEntry` projection with type, integer
minor-unit amount, and reference.

## Refinement check

The adapter does not calculate balances or synthesize ledger facts. A facade
test verifies the deposit and market-buy entries produced by existing domain
events.

## Boundary

Pagination, statement formatting, and production retention guarantees remain
outside this unreleased draft query.
