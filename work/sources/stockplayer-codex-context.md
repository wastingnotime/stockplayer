# Stockplayer — Codex Seed Context

## 1. Purpose

Build an open-source stock-market simulation used as a practical architecture laboratory.

Stockplayer is not an investment product.

It exists to demonstrate, exercise, and explain architectural ideas through a domain that is:

- time-dependent;
- stateful;
- financially constrained;
- concurrency-sensitive;
- event-rich;
- easy to visualize;
- suitable for deterministic simulation and replay.

The project should make complex system behavior observable and understandable.

---

## 2. Position Inside Wasting No Time

Stockplayer is a Wasting No Time demonstration application.

Its role is different from user-validation products such as Cat Care, motorcycle maintenance, or condominium management.

Those projects test whether WNT can reduce cognitive burden for real users.

Stockplayer tests whether WNT can make complex software behavior:

- explicit;
- deterministic;
- observable;
- replayable;
- testable;
- explainable;
- recoverable.

Stockplayer is an engineering lab, not the primary WNT product.

---

## 3. Core Intent

Use a fictional stock exchange to demonstrate architectural solutions without becoming bound to the full real-world complexity of B3, Nasdaq, broker regulation, tax law, or real-time exchange connectivity.

The project should allow contributors and visitors to:

- run the complete system locally;
- observe price movement;
- submit simulated buy and sell orders;
- watch orders execute;
- inspect portfolio changes;
- replay scenarios;
- compare engine versions;
- inject failures;
- observe recovery;
- inspect traces, events, and projections;
- understand why a given architectural choice exists.

The application should be useful as a reference implementation and technical portfolio artifact.

---

## 4. Product Disclaimer

The system must clearly state:

> Stockplayer is a fictional market simulation for software engineering and educational use. It does not provide investment advice, market predictions, brokerage services, or recommendations.

The project must not encourage real-money speculation.

Do not frame short-term trading as a path to wealth.

Do not integrate with real brokerage accounts.

Do not execute real orders.

---

## 5. Delivery Boundary

The complete system must run through Docker Compose.

A contributor should be able to clone the repository and run:

```bash
docker compose up --build
```

The local environment should provide:

- web interface;
- application API;
- market simulator;
- order execution engine;
- persistent storage;
- optional event transport;
- seeded fictional securities;
- deterministic demo scenarios;
- observability surfaces or exported telemetry.

The application does not need to run on the WNT production environment.

Avoid dependencies on WNT private infrastructure.

The repository must remain independently understandable and runnable.

---

## 6. Open-source Goals

The repository should demonstrate professional engineering quality without becoming an oversized framework.

Prioritize:

- clear README;
- documented architecture;
- explicit trade-offs;
- reproducible scenarios;
- approachable local setup;
- meaningful tests;
- visible failure cases;
- contributor-friendly module boundaries;
- documented architectural decisions;
- deterministic seeds;
- small and understandable deployment topology.

Avoid:

- hidden dependencies;
- unnecessary cloud requirements;
- private services;
- excessive repository bootstrapping;
- architecture that only makes sense at hypothetical scale;
- abstractions with no demonstrated purpose.

---

## 7. Fictional Market Scope

Use a deliberately simplified fictional exchange.

Possible name:

> Stockplayer Exchange

Use fictional securities rather than real listed companies.

Example symbols:

- `AUR`
- `NOVA`
- `GRN`
- `VLT`
- `ORB`

Each security may have:

- symbol;
- display name;
- current reference price;
- tick size;
- trading status;
- optional volatility profile.

The system should make it obvious that all market data is simulated.

---

## 8. Initial Market Rules

Initial supported behavior:

- cash accounts only;
- one currency;
- fictional securities;
- market orders;
- limit orders;
- buy orders;
- sell orders;
- order cancellation;
- full fills;
- optional partial fills;
- fixed trading sessions;
- configurable fees;
- no leverage;
- no margin;
- no short selling;
- no options;
- no futures;
- no real exchange connectivity;
- no external real-time market feed.

The first release may use a simple execution model before implementing a complete order book.

---

## 9. Initial Users

The primary users are:

- software engineers;
- architecture learners;
- open-source contributors;
- interviewers or recruiters reviewing the project;
- developers exploring event-driven and simulation-based design.

The application may also be enjoyable as a small fictional trading simulator, but entertainment is secondary.

The main success criterion is that architectural behavior becomes visible.

---

## 10. Core User Flow

A user should be able to:

1. start with a fictional cash balance;
2. inspect available securities;
3. observe simulated price movement;
4. submit a buy or sell order;
5. see the order status;
6. observe an execution;
7. inspect cash reservations;
8. inspect current positions;
9. inspect realized and unrealized results;
10. inspect account history;
11. replay or reset a deterministic scenario.

The interface should explain important state transitions.

---

## 11. Core Domain Concepts

### 11.1 Account

Represents a simulated participant.

Possible attributes:

- account ID;
- display name;
- available cash;
- reserved cash;
- status;
- created at.

An account may own positions and submit orders.

---

### 11.2 Security

Represents a fictional tradable instrument.

Possible attributes:

- security ID;
- symbol;
- name;
- tick size;
- trading status;
- reference price;
- currency.

---

### 11.3 Order

Represents an instruction to buy or sell.

Possible attributes:

- order ID;
- account ID;
- security ID;
- side;
- type;
- quantity;
- remaining quantity;
- limit price;
- status;
- submitted at;
- accepted at;
- completed at;
- version.

Initial order sides:

- buy;
- sell.

Initial order types:

- market;
- limit.

Initial statuses:

- submitted;
- accepted;
- partially filled;
- filled;
- cancelled;
- rejected.

---

### 11.4 Execution

Represents a completed trade for an order.

Possible attributes:

- execution ID;
- order ID;
- account ID;
- security ID;
- quantity;
- execution price;
- fee;
- executed at.

One order may have multiple executions when partial fills are supported.

---

### 11.5 Position

Represents current ownership of a security.

Possible attributes:

- account ID;
- security ID;
- quantity;
- average acquisition cost;
- realized result;
- last updated at.

Position is preferably a projection derived from executions.

---

### 11.6 Cash ledger

Represents movement of simulated money.

Possible entry types:

- initial deposit;
- funds reserved;
- reservation released;
- trade settlement;
- fee charged;
- dividend;
- adjustment.

Cash balance must be explainable from ledger entries.

---

### 11.7 Market session

Represents exchange time and availability.

Possible states:

- scheduled;
- open;
- paused;
- closed.

Orders may behave differently depending on session state.

---

### 11.8 Price tick

Represents a simulated market-price update.

Possible attributes:

- security ID;
- price;
- occurred at;
- simulation sequence;
- source seed.

Price ticks must be reproducible in deterministic scenarios.

---

## 12. Initial Domain Invariants

Treat these as initial invariants to implement and test.

1. An account cannot spend more available cash than it owns.
2. Cash reserved by an open buy order cannot be reserved by another order.
3. A sell order cannot exceed the available owned quantity when short selling is disabled.
4. Reserved quantity cannot be sold twice.
5. Filled quantity cannot exceed requested quantity.
6. Remaining quantity cannot be negative.
7. A filled order cannot later be cancelled.
8. A cancelled order cannot receive new executions.
9. A rejected order reserves no cash or quantity.
10. Every execution must reference an accepted order.
11. Every cash movement must be represented in the cash ledger.
12. Every position change must be explainable through executions or explicit adjustments.
13. Replaying the same deterministic scenario from the same initial state must produce the same result.
14. Duplicate commands or events must not create duplicate economic effects.
15. Price and quantity must respect configured precision.
16. Market orders cannot execute without a valid execution price.
17. Limit buy orders cannot execute above their limit.
18. Limit sell orders cannot execute below their limit.
19. Closing a market session must not corrupt accepted open orders.
20. A projection rebuild must produce the same state as the current validated projection.

---

## 13. Economic Precision

Do not use binary floating-point values for money or quantity-sensitive domain calculations.

Use:

- integer minor units; or
- exact decimal types.

Define:

- currency precision;
- price precision;
- quantity precision;
- rounding policy;
- fee rounding policy.

Make these decisions explicit and tested.

---

## 14. Deterministic Simulation

Deterministic simulation is a primary feature.

A scenario should be defined by:

- initial accounts;
- initial balances;
- securities;
- starting prices;
- market rules;
- random seed;
- scheduled user actions;
- scheduled market actions;
- simulated clock.

Running the same scenario with the same seed should produce:

- the same price sequence;
- the same accepted and rejected orders;
- the same executions;
- the same cash ledger;
- the same final positions;
- the same derived metrics.

Simulation must not depend on wall-clock timing for correctness.

Use an explicit simulated clock.

---

## 15. Initial Scenarios

Provide a small scenario catalog.

### Scenario A — Simple purchase

- account starts with sufficient cash;
- user submits a market buy;
- order fills;
- cash decreases;
- position is created.

Demonstrates:

- command handling;
- cash settlement;
- position projection;
- event history.

---

### Scenario B — Insufficient funds

- account submits a buy order above available cash;
- order is rejected;
- no reservation is created.

Demonstrates:

- invariants;
- rejection reasons;
- consistency.

---

### Scenario C — Cash reservation

- account submits two limit buy orders;
- first order reserves part of the cash;
- second order is rejected or reduced according to policy.

Demonstrates:

- concurrency;
- reservations;
- available versus total balance.

---

### Scenario D — Partial execution

- a large order is executed in multiple parts;
- remaining quantity decreases;
- average acquisition cost updates correctly.

Demonstrates:

- partial fills;
- repeated events;
- projection correctness.

---

### Scenario E — Cancellation

- accepted order is cancelled before execution;
- reservation is released;
- later execution attempts are rejected.

Demonstrates:

- lifecycle rules;
- reservation release;
- stale-message defense.

---

### Scenario F — Duplicate event

- the same execution event is delivered twice;
- the economic effect occurs only once.

Demonstrates:

- idempotency;
- message deduplication;
- ledger protection.

---

### Scenario G — Projection rebuild

- current position projection is deleted;
- projection is rebuilt from event history;
- rebuilt state matches previous validated state.

Demonstrates:

- replay;
- recoverability;
- event-derived state.

---

### Scenario H — Engine comparison

- matching or execution engine v1 and v2 process the same scenario;
- outputs are compared;
- differences are surfaced explicitly.

Demonstrates:

- behavioral versioning;
- deterministic validation;
- safe evolution.

---

### Scenario I — Failure and recovery

- execution processing stops after event persistence but before projection update;
- system restarts;
- projection catches up without duplicating effects.

Demonstrates:

- failure boundaries;
- eventual recovery;
- observability.

---

## 16. Event Model

Event sourcing may be used where it provides visible value.

Possible domain events:

- `AccountOpened`
- `CashDeposited`
- `OrderSubmitted`
- `OrderAccepted`
- `OrderRejected`
- `CashReserved`
- `QuantityReserved`
- `OrderPartiallyFilled`
- `OrderFilled`
- `ExecutionRecorded`
- `OrderCancelled`
- `CashReservationReleased`
- `QuantityReservationReleased`
- `PositionChanged`
- `FeeCharged`
- `MarketSessionOpened`
- `MarketSessionClosed`
- `PriceChanged`
- `ProjectionRebuilt`

Do not emit redundant events merely to increase event count.

Separate:

- domain facts;
- integration messages;
- projection updates;
- telemetry events.

---

## 17. Command Model

Possible commands:

- `OpenAccount`
- `DepositCash`
- `SubmitBuyOrder`
- `SubmitSellOrder`
- `CancelOrder`
- `OpenMarketSession`
- `CloseMarketSession`
- `AdvanceSimulation`
- `ResetScenario`
- `RebuildProjection`
- `InjectFailure`
- `ReplayScenario`

Commands should be validated against current state and domain invariants.

A command may be rejected with an explicit reason.

---

## 18. Matching and Execution Strategy

Start simple.

Possible first implementation:

- simulated execution against current market price;
- deterministic fill rules;
- configurable liquidity;
- optional partial fill behavior.

A complete price-time-priority order book may be implemented later as a separate engine version.

Do not begin with exchange-grade matching complexity.

The architecture should allow the engine to evolve behind a clear contract.

Possible engine interface responsibilities:

- receive accepted orders;
- inspect market state;
- produce zero or more proposed executions;
- remain deterministic for the same ordered inputs;
- expose engine version;
- produce auditable decisions.

---

## 19. Architectural Demonstrations

Every advanced architectural feature must demonstrate a visible property.

Potential demonstrations:

### Event sourcing

Show:

- event timeline;
- state reconstruction;
- projection rebuild;
- historical replay.

### CQRS

Show:

- command-side decision;
- read-side projection;
- projection delay;
- recovery.

### Idempotency

Show:

- duplicate delivery;
- duplicate ignored;
- final state unchanged.

### Optimistic concurrency

Show:

- concurrent order commands;
- one accepted state transition;
- conflicting command rejected or retried.

### Behavioral versioning

Show:

- engine v1;
- engine v2;
- identical scenario;
- compared outputs.

### Observability

Show:

- command trace;
- event persistence;
- execution processing;
- projection update;
- latency and failure location.

### Failure injection

Show:

- selected failure point;
- visible degraded state;
- recovery path;
- final consistency.

### Blue-green or candidate validation

Show:

- stable engine processes authoritative simulation;
- candidate engine processes copied inputs;
- outputs are compared;
- candidate does not control official state until validated.

Do not add an architectural pattern unless its demonstration can be explained.

---

## 20. Suggested Initial Architecture

Prefer a modular monolith plus explicitly separated worker processes where useful.

Suggested components:

- `web` — browser interface;
- `api` — commands and queries;
- `simulator` — deterministic market clock and price generation;
- `worker` — asynchronous event or projection processing, if needed;
- PostgreSQL — transactional state, events, ledgers, and projections;
- NATS — optional event transport when the demonstration requires it;
- OpenTelemetry Collector — optional local observability path;
- a trace/metrics/log viewer suitable for Docker Compose.

Avoid unnecessary service decomposition.

A valid initial topology may be:

```text
Browser
   |
   v
Web/API
   |
   +---- PostgreSQL
   |
   +---- NATS ---- Worker
   |
   +---- Simulator
```

The exact implementation may vary, but local operability must stay simple.

---

## 21. Repository Structure

A possible monorepo structure:

```text
/
├── apps/
│   ├── web/
│   ├── api/
│   ├── simulator/
│   └── worker/
├── internal/
│   ├── domain/
│   ├── application/
│   ├── execution/
│   ├── projections/
│   ├── simulation/
│   └── observability/
├── scenarios/
├── docs/
│   ├── architecture/
│   ├── decisions/
│   └── demonstrations/
├── deployments/
│   └── compose/
├── scripts/
├── docker-compose.yml
└── README.md
```

Do not force this structure when the chosen language ecosystem has a clearer convention.

---

## 22. Technology Direction

Preferred implementation characteristics:

- strong typing;
- explicit domain types;
- exact decimal handling;
- deterministic tests;
- straightforward concurrency model;
- simple local builds;
- good container support.

Go is a strong candidate for backend services and simulation.

The frontend may use the existing WNT-preferred web stack, but should remain easy to run and contribute to.

Use REST unless a different transport demonstrates a specific architectural lesson.

Do not introduce gRPC only to appear sophisticated.

---

## 23. API Direction

Possible routes:

### Accounts

- `POST /accounts`
- `GET /accounts`
- `GET /accounts/{account_id}`
- `POST /accounts/{account_id}/deposits`
- `GET /accounts/{account_id}/ledger`
- `GET /accounts/{account_id}/positions`

### Securities

- `GET /securities`
- `GET /securities/{symbol}`
- `GET /securities/{symbol}/prices`

### Orders

- `POST /orders`
- `GET /orders`
- `GET /orders/{order_id}`
- `POST /orders/{order_id}/cancel`

### Simulation

- `GET /simulation`
- `POST /simulation/start`
- `POST /simulation/pause`
- `POST /simulation/advance`
- `POST /simulation/reset`
- `POST /simulation/scenarios/{scenario_id}/run`

### Demonstrations

- `POST /demonstrations/failures`
- `POST /demonstrations/rebuild-projections`
- `POST /demonstrations/replay`
- `POST /demonstrations/compare-engines`

Keep routes coherent and avoid exposing internal persistence details.

---

## 24. Initial Screens

### 24.1 Market

Display:

- simulated clock;
- session state;
- securities;
- latest price;
- recent movement;
- explicit simulated-data label.

### 24.2 Order ticket

Allow:

- security selection;
- buy or sell;
- market or limit;
- quantity;
- price when applicable;
- estimated reservation;
- clear validation feedback.

### 24.3 Orders

Display:

- order status;
- requested quantity;
- remaining quantity;
- executions;
- rejection reason;
- timestamps.

### 24.4 Portfolio

Display:

- available cash;
- reserved cash;
- positions;
- average cost;
- simulated current value;
- realized result;
- unrealized result.

Do not imply future profitability.

### 24.5 Timeline

Display:

- commands;
- domain events;
- executions;
- ledger movements;
- projection updates;
- failures and recovery.

This is a core engineering-demonstration screen.

### 24.6 Scenario lab

Allow:

- scenario selection;
- seed selection;
- run;
- pause;
- advance time;
- reset;
- replay;
- inject failure;
- compare engine versions.

This may be the most important screen for the open-source purpose.

---

## 25. Observability

Observability must support explanation, not just operations.

Correlate:

- user command;
- API request;
- domain decision;
- persisted event;
- published message;
- worker handling;
- execution;
- projection update.

Use correlation and causation identifiers.

A visitor should be able to understand:

> I submitted this order, these decisions occurred, these events were persisted, this execution changed the ledger, and this projection produced the visible portfolio.

Useful signals:

- command latency;
- rejected-command count;
- event-processing lag;
- projection lag;
- duplicate-message count;
- invariant violation attempts;
- scenario duration;
- engine comparison differences.

---

## 26. Testing Strategy

### Unit tests

Cover:

- money and quantity types;
- order state transitions;
- cash reservation;
- quantity reservation;
- limit-price rules;
- execution application;
- average-cost calculation;
- fee calculation;
- duplicate handling.

### Scenario tests

Run complete deterministic scenarios.

Verify:

- final account state;
- final ledger;
- final positions;
- order histories;
- event sequence;
- projection equality.

### Property-based tests

Useful properties:

- cash never becomes negative without an explicit allowed policy;
- quantity never becomes negative;
- filled quantity never exceeds requested quantity;
- replay is deterministic;
- duplicate delivery does not change final state;
- ledger sum matches account balance;
- rebuilt projection equals validated projection.

### Integration tests

Run:

- API;
- database;
- optional NATS;
- worker;
- simulator.

### Failure tests

Test crashes and retries around:

- event persistence;
- message publication;
- execution processing;
- ledger update;
- projection update.

---

## 27. Security and Privacy

The application uses fictional money and fictional securities, but should still demonstrate sound practices.

Include:

- input validation;
- authorization boundaries when multiple accounts exist;
- secure default configuration;
- no committed secrets;
- dependency scanning where practical;
- rate limiting only when justified;
- auditability of sensitive commands.

Do not overbuild enterprise identity in the first release.

A demo mode with seeded accounts may be sufficient initially.

---

## 28. Milestones

### Milestone 1 — Deterministic core

Deliver:

- fictional securities;
- one account;
- cash deposit;
- market buy;
- market sell;
- positions;
- cash ledger;
- deterministic price simulation;
- scenario tests.

### Milestone 2 — Order lifecycle

Deliver:

- limit orders;
- reservations;
- cancellation;
- rejection reasons;
- order timeline.

### Milestone 3 — Replayable architecture

Deliver:

- persisted domain events;
- projections;
- projection rebuild;
- deterministic replay;
- duplicate protection.

### Milestone 4 — Architecture lab

Deliver:

- scenario catalog;
- failure injection;
- observability;
- engine comparison;
- scenario-lab interface.

### Milestone 5 — Open-source polish

Deliver:

- complete README;
- architecture guide;
- ADRs;
- contributor setup;
- screenshots or short demo;
- issue templates;
- license;
- example extension.

Do not start later milestones before the previous one is coherent.

---

## 29. Definition of Initial Release

The initial release is complete when a contributor can:

1. clone the repository;
2. run Docker Compose;
3. open the web interface;
4. start a deterministic scenario;
5. observe fictional prices;
6. submit a market buy;
7. see an execution;
8. inspect cash and position changes;
9. reset the scenario;
10. rerun with the same seed;
11. obtain the same result;
12. inspect tests and documentation explaining the behavior.

The initial release does not require event sourcing, NATS, multiple services, or failure injection unless they are part of the selected first demonstration.

Correct behavior comes before architectural breadth.

---

## 30. Decision Filter

Before introducing a feature or architecture pattern, ask:

1. Which visible system property does this demonstrate?
2. Can the same lesson be shown more simply?
3. Does it improve determinism, observability, correctness, recovery, or explainability?
4. Is it part of the fictional domain or accidental real-market complexity?
5. Can a contributor run and understand it locally?
6. Does it create meaningful tests?
7. Is the project becoming an exchange implementation instead of an architecture lab?
8. Can the decision be documented as an explicit trade-off?

When no clear lesson exists, do not add the feature.

---

## 31. Explicit Non-goals

Do not include in the initial project:

- real-money trading;
- broker integration;
- real B3 or Nasdaq connectivity;
- investment recommendations;
- price predictions;
- financial-advice content;
- automated trading bots intended for real markets;
- real tax reporting;
- real compliance reporting;
- options;
- futures;
- margin;
- short selling;
- high-frequency trading claims;
- production exchange throughput claims;
- Kubernetes;
- cloud-only infrastructure;
- mandatory WNT platform dependencies;
- unnecessary microservices;
- AI features without a specific architectural demonstration.

---

## 32. Documentation Requirements

The repository should contain:

- project purpose;
- disclaimer;
- quick start;
- architecture overview;
- domain glossary;
- supported market rules;
- deterministic simulation explanation;
- scenario catalog;
- invariant catalog;
- event catalog when events are used;
- failure and recovery guide;
- architectural decision records;
- contribution guide;
- roadmap;
- explicit non-goals.

Prefer diagrams that explain behavior over diagrams that merely list technologies.

---

## 33. Instruction to Codex

Build Stockplayer as a small, coherent, deterministic fictional market that demonstrates architecture through visible behavior.

Do not build a complete exchange.

Do not introduce patterns only because they are fashionable.

Start with the smallest end-to-end flow:

> create account → deposit fictional cash → simulate price → submit order → execute order → update ledger and position → show result → replay deterministically.

Keep domain invariants explicit.

Keep money calculations exact.

Keep time controllable.

Keep the local environment reproducible.

Keep architectural experiments isolated and explainable.

Every advanced feature should answer:

> What can a developer learn by watching this happen?

When uncertain, prefer the implementation that is easier to test, replay, observe, and explain.
