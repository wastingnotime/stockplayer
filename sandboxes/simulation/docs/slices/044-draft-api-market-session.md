# Slice 044 — Draft API market-session query

## Build

Expose the current market-session state through the draft facade. The query
reads the repository-owned session state and returns its stable string value.

## Refinement check

The adapter does not transition sessions or reproduce calendar rules. A test
covers the scheduled initial state and the open state established by account
setup.

## Boundary

Session transition commands, calendars, and production status semantics remain
outside this unreleased draft query.
