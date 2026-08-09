# Slice 050 — Draft API command idempotency

## Refinement

Document and test the draft facade's retry behavior for duplicate market-buy
commands. The facade delegates duplicate detection to the existing use case,
returns no new event types, and reports the unchanged account projection.

## Refinement check

The test retries the same order with a different execution ID and verifies
that no second fill or cash mutation occurs. Idempotency remains domain and
application policy, not adapter logic.

## Boundary

Transport idempotency keys and request deduplication windows remain deferred
to the released API contract.
