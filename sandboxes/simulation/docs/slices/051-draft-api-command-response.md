# Slice 051 — Draft API command response

## Build

Give every draft command response an explicit `accepted` boolean alongside
event type names and the projected account snapshot. The flag is derived from
the existing `OrderRejected` domain event.

## Refinement check

Accepted fills report `true`; domain rejections report `false`; duplicate
commands report no new event types and remain accepted-neutral. The adapter
does not classify business failures independently of domain events.

## Boundary

HTTP status mapping, error payloads, and transport retry keys remain deferred
to the released contract.
