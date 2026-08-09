# Slice 015: market-session state

- **Implementation pack:** WNT Python event-sourced simulation
- **Runtime target:** headless Python
- **Architecture mode:** replayable availability state machine

## Use-case contract

A market session transitions through scheduled, open, paused, and closed.
Scheduled sessions may open; open sessions may pause or close; paused sessions
may resume or close; closed sessions are terminal. Every transition is a fact
with simulated time.

## Deterministic scenario

Open, pause, resume, and close a session. Rebuilding a fresh session from the
transition facts yields closed state and an identical event history. Attempting
to reopen after close is rejected.

## Done criteria

- Allowed transitions are explicit.
- Invalid transitions have no appended fact.
- State rebuild is deterministic.

Out of scope: order-handler enforcement, holidays, calendars, time zones, and
real exchange hours.
