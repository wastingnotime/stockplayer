# Slice 020: execution-engine comparison

- **Implementation pack:** WNT Python event-sourced simulation
- **Runtime target:** headless Python
- **Architecture mode:** versioned deterministic strategy boundary

## Use-case contract

Execution engines receive the same order request, current price, and available
liquidity. Engine v1 requires a full fill; engine v2 caps the fill at available
liquidity. Both return auditable versioned decisions without mutating account
state.

## Deterministic scenario

Request 10 AUR at 2,500 with liquidity 4. V1 returns zero filled with an
insufficient-liquidity reason; V2 returns a four-unit partial fill. Repeating
the comparison yields identical decisions.

## Done criteria

- Engine versions have an explicit interface and output contract.
- The same input produces comparable decisions.
- Behavioral differences are visible and deterministic.

Out of scope: authoritative engine promotion, order-book priority, latency
claims, and production throughput.
