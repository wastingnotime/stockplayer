# Slice 032 — Draft API sell adapter

## Build

Extend the framework-free draft API facade with market-sell translation. The
adapter accepts the explicit execution price required by the existing sell use
case, delegates to the environment, and returns projected account state.

## Refinement check

The adapter remains a translation boundary: session enforcement, holdings
validation, event sequencing, idempotency, and projection behavior stay in the
existing application and domain layers. A facade test covers a buy followed by
a sell and verifies cash, position, and order projection results.

## Boundary

This is still an unreleased draft. Transport schemas, authentication, and
production error mapping remain open until the API and browser contracts are
released together.
