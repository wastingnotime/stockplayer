# Slice 030: order-command idempotency

- **Implementation pack:** WNT Python event-sourced simulation
- **Runtime target:** headless Python
- **Architecture mode:** order identity boundary

## Use-case contract

An order ID identifies one command intent. Retrying that command with a new
execution ID produces no new event or economic effect once the order ID is
already present in the stream, including after a successful fill or rejection.

## Deterministic scenario

Submit a 10-unit market buy as `buy-1`, then repeat `buy-1` with a different
execution ID. The retry returns no events, the stream is unchanged, and cash
remains 75,000.

## Done criteria

- Order IDs are reconstructed during replay.
- Buy, sell, and reservation command handlers treat duplicates as no-ops.
- Execution-level idempotency remains distinct and active.

Out of scope: cross-account idempotency keys and distributed deduplication
stores.
