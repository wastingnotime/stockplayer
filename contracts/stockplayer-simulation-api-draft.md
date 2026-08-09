# Stockplayer simulation API — draft adapter contract

Status: draft; not a released production API.

The thin adapter translates structured payloads into the repository-owned
simulation use cases and queries projections. It must not duplicate domain
invariants, persistence, event sequencing, or session policy.

Command results include `accepted`, `event_types`, and the projected account.
Domain rejections set `accepted` to `false`; retries preserve repository
idempotency by returning no new event types and leaving the account unchanged.

## Current operations

- `open_account`: `account_id`, `display_name`, `cash_minor`, `occurred_at`.
- `submit_market_buy`: `account_id`, `order_id`, `execution_id`, `symbol`,
  `quantity`, `occurred_at`.
- `submit_market_sell`: `account_id`, `order_id`, `execution_id`, `symbol`,
  `quantity`, `price_minor`, `occurred_at`.
- `reserve_market_sell`: `account_id`, `order_id`, `symbol`, `quantity`,
  `occurred_at`.
- `cancel_market_sell_reservation`: `account_id`, `order_id`, `occurred_at`.
- `execute_market_sell_reservation`: `account_id`, `order_id`, `execution_id`,
  `price_minor`, `occurred_at`.
- `execute_partial_market_sell_reservation`: `account_id`, `order_id`,
  `execution_id`, `quantity`, `price_minor`, `occurred_at`.
- `submit_limit_buy`: `account_id`, `order_id`, `symbol`, `quantity`,
  `limit_price_minor`, `occurred_at`.
- `cancel_limit_buy`: `account_id`, `order_id`, `occurred_at`.
- `execute_limit_buy`: `account_id`, `order_id`, `execution_id`, `price_minor`,
  `occurred_at`.
- `execute_partial_limit_buy`: `account_id`, `order_id`, `execution_id`,
  `quantity`, `price_minor`, `occurred_at`.
- `account`: returns available/reserved cash, positions, reserved quantities,
  valuation fields, ledger entries, and order views. Valuation includes
  average cost, cost basis, realized result, and unrealized result in integer
  minor units. Ledger entries include type, amount, and reference.
- `order`: returns one projected order view, or `null` when the account has no
  order with that identifier.
- `market_session`: returns the current session state (`scheduled`, `open`,
  `paused`, or `closed`).
- `market_prices`: returns current symbol prices in integer minor units.
- `market_price`: returns one symbol price, or raises the market adapter's
  unknown-symbol error.
- `ledger`: returns projected ledger entries for one account in event order.
- `accounts`: returns projected account identifiers in deterministic lexical
  order.

Money and prices are integer minor units. Timestamps are ISO-8601 with an
explicit offset; the draft adapter rejects naive timestamps at its boundary.
Domain rejection remains represented by domain events and adapter errors until
a released transport contract is selected.

The executable draft is
`sandboxes/simulation/src/app/interfaces/api_facade.py`.
