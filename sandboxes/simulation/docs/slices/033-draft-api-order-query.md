# Slice 033 — Draft API order query

## Build

Expose a focused order query beside the account projection query. It returns
the repository-owned projected view with account and order identifiers, and
uses `null` for an unknown order instead of inventing domain state.

## Refinement check

The query reads only from `AccountProjections`; it does not load event history
or recreate order lifecycle rules. Tests cover both a filled order and an
unknown identifier.

## Boundary

This remains part of the unreleased framework-free draft. Transport status
codes, pagination, and authorization are deferred to the released contract.
