# Slice 046 — Draft API single market-price query

## Build

Add a focused symbol price lookup beside the complete market-price mapping.
The facade delegates directly to the existing market-data adapter.

## Refinement check

Known symbols return integer minor-unit prices. Unknown symbols preserve the
market adapter's `ValueError` semantics; the facade does not invent transport
errors or fallback prices.

## Boundary

Price freshness, streaming, and production error mapping remain deferred.
