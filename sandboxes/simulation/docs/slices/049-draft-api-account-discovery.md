# Slice 049 — Draft API account discovery

## Build

Expose projected account identifiers through an `accounts()` query. The
adapter derives the list from the existing cash projection and returns a
deterministically sorted copy.

## Refinement check

No account-creation or authorization policy is introduced. Tests cover the
empty state and deterministic ordering of multiple opened accounts.

## Boundary

Pagination, search, tenant scoping, and production identity policy remain
outside this unreleased draft query.
