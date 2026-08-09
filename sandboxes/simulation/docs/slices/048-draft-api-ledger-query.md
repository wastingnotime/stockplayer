# Slice 048 — Draft API focused ledger query

## Build

Expose a focused `ledger(account_id)` query beside the account snapshot. It
returns the existing projected ledger entries in event order and returns an
empty list for an account with no projected entries.

## Refinement check

The adapter performs no balance or statement calculation. Tests cover the
known account's entries and the empty unknown-account result.

## Boundary

Pagination, filtering, and retention semantics remain outside this unreleased
draft query.
