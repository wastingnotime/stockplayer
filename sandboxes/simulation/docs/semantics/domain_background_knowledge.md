# Domain background knowledge

## Purpose and safety boundary

Stockplayer is a fictional exchange used to make stateful, time-dependent, and
failure-sensitive architecture observable. It never connects to real markets,
brokers, accounts, or money and must not imply investment advice or likely
profit.

## Simplified market context

- Participants use cash accounts in one fictional currency.
- Securities, prices, sessions, and executions are simulated.
- No leverage, margin, short selling, derivatives, or real market feeds exist.
- Exact monetary arithmetic and explicit rounding are mandatory.
- The first execution engine fills a market order at the current valid price.
- Event history explains authoritative economic changes; projections are
  rebuildable views.

## Architecture-learning properties

The model should expose command decisions, persisted domain facts, ledger
movements, position projections, deterministic replay, idempotency, failure
boundaries, and engine differences. A pattern belongs only when its behavior is
visible and simpler behavior cannot teach the same lesson.

## Source

Extracted from `work/sources/stockplayer-codex-context.md` on 2026-08-09. The
source is product intent, not a claim about real exchange or regulatory rules.
