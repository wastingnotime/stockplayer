# Slice 052 — Draft API timestamp errors

## Refinement

Normalize malformed `occurred_at` input at the draft adapter boundary. Invalid
ISO-8601 text receives a stable `ValueError` message, while naive timestamps
continue to receive the explicit-offset error.

## Refinement check

Tests cover both malformed text and missing offsets. No domain command is
constructed when adapter timestamp parsing fails.

## Boundary

Transport error envelopes and HTTP status mapping remain deferred.
