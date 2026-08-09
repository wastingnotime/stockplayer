# Stockplayer simulation API — draft adapter contract

Status: draft; not a released production API.

The thin adapter translates structured payloads into the repository-owned
simulation use cases and queries projections. It must not duplicate domain
invariants, persistence, event sequencing, or session policy.

## Current operations

- `open_account`: `account_id`, `display_name`, `cash_minor`, `occurred_at`.
- `submit_market_buy`: `account_id`, `order_id`, `execution_id`, `symbol`,
  `quantity`, `occurred_at`.
- `account`: returns available/reserved cash, positions, and order views.

Money and prices are integer minor units. Timestamps are ISO-8601 with an
explicit offset. Domain rejection remains represented by domain events and
adapter errors until a released transport contract is selected.

The executable draft is
`sandboxes/simulation/src/app/interfaces/api_facade.py`.
