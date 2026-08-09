# Model EGD: deterministic fictional-market core

## Review scope

This EGD reviews the bounded simulation model developed through slices 001–030:
cash accounts, exact money, fictional securities, market and limit buys,
market and reserved sells, reservations, cancellation, partial fills,
idempotency, projections, price ticks, sessions, failure recovery, engine
comparison, invariant checks, and runtime observations.

## Evidence reviewed

- Source intent preserved in `work/sources/stockplayer-codex-context.md`.
- Current vocabulary and candidate map in
  `sandboxes/simulation/docs/semantics/model_hypothesis.md`.
- Domain background in
  `sandboxes/simulation/docs/semantics/domain_background_knowledge.md`.
- Slice contracts and refinement checks under
  `sandboxes/simulation/docs/slices/` and `work/changes/`.
- 27 deterministic unit and runtime scenario tests pass.
- The common MRL supervisor loads the repository adapter and emits deterministic
  observations for commands, events, price ticks, sessions, failures,
  recovery, engine comparison, and order status.

## Findings

### Accepted

- Account economic state is event-replayable and uses integer minor units.
- Buy and sell ownership/cash invariants are explicit and tested.
- Reservation, cancellation, execution, partial-fill, and duplicate paths are
  visible in facts and projections.
- Projection failure after append has a deterministic rebuild path.
- Runtime evidence is separate from pure domain behavior.
- Engine comparison does not control authoritative account state.

### Gaps

- No released API/web adapter contract exists yet.
- Docker Compose and persistent technology projects are intentionally outside
  this model EGD.
- Fees, market calendars, and external delivery are not modeled.
- The runtime scenario is a focused evidence path, not the complete scenario
  catalog execution surface.

## EGD result

**Accepted for the deterministic domain-core boundary; not a full model release.**

The core model is coherent for continued simulation work. The gaps are known
technology or explicitly deferred domain scope, not unresolved contradictions.
