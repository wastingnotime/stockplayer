# Slice 021: runtime engine comparison

- **Implementation pack:** WNT Python event-sourced simulation
- **Runtime target:** WNT MRL Runtime supervised scenario
- **Architecture mode:** candidate decision evidence

## Use-case contract

The scenario sends one deterministic execution request to engine v1 and engine
v2, then emits both versioned decisions in one correlated comparison
observation. Neither decision mutates the account stream or projections.

## Deterministic scenario

At simulated 2.75 seconds, request 10 AUR with four units of liquidity. The
scenario records v1's no-fill decision and v2's four-unit partial-fill decision,
then closes the market.

## Done criteria

- Runtime evidence includes both engine versions and reasons.
- Candidate comparison runs after recovery and before session close.
- Account state remains authoritative and unchanged by comparison.

Out of scope: promotion, engine selection, production benchmarking, and order
book implementation.
