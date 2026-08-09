# Slice 001: simple purchase

- **Implementation pack:** WNT Python event-sourced simulation
- **Runtime target:** headless Python and WNT MRL Runtime supervision
- **Architecture mode:** event-sourced account with synchronous projections
- **Discovery scope:** the smallest end-to-end purchase from the seed context

## Use-case contract

Given an opened account with deposited fictional cash and a fictional security
with a current price, submit a positive whole-unit market buy. Accept and fully
execute it when cash is sufficient; record exact economic facts and expose the
result through cash-ledger and position projections.

## Rules and ports

- Price and money are positive integer minor units; quantity is positive whole
  units.
- Cost is `price_minor * quantity`; available cash cannot become negative.
- The use case loads and appends an account stream through an event-store port.
- The current price comes from a deterministic market-data port.
- Projection updates consume appended domain events.

## Deterministic scenario

At `2026-01-05T13:00:00Z`, open account `acct-demo`, deposit 100,000 minor
units, set AUR to 2,500, and buy 10 units. The final cash is 75,000 and the AUR
position is 10 units costing 25,000. The same inputs produce the same ordered
facts and observations.

## Done criteria

- Unit checks cover exact values, event replay, insufficient funds, ledger, and
  position results.
- A scenario test proves deterministic observations and invariant success.
- The repository-owned runtime adapter exposes the shared environment.

Out of scope: sells, limits, reservations, fees, partial fills, asynchronous
projections, databases, network APIs, and browser behavior.
