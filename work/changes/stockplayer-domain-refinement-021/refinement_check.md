# Refinement check

Slice 021 adds correlated runtime evidence for the v1/v2 execution comparison.
Both engines receive identical input, differences are visible, and no
candidate decision controls account state. Runtime evidence also records the
evaluated price and signed fill delta alongside each versioned decision.
The payload rejects duplicate engine versions, and runtime evidence preserves
the comparison correlation id and simulated timestamp. Candidate decisions are
bounded by both requested quantity and supplied liquidity.

The next refinement can define released adapter contracts or add a scenario
catalog around the current model evidence.
