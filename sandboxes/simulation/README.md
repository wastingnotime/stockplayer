# Stockplayer domain simulation

This is the repository's single evolving MRL simulation environment. It models
Stockplayer independently of web, API, database, and deployment frameworks.

The first vertical slice is a deterministic simple purchase:

`open account -> deposit fictional cash -> publish a fictional price -> submit
market buy -> execute -> update ledger and position -> observe invariants`

Money and prices use integer minor units. Quantities are whole units in this
slice. Time is explicit UTC simulation time, IDs are supplied by the scenario,
and domain decisions do not read wall-clock time or generate randomness.

Run the checks:

```bash
python3 -m unittest discover -s sandboxes/simulation/tests -v
```

Run with the WNT MRL Runtime installed in user space:

```bash
PYTHONPATH="$HOME/.wnt/runtime/mrl:sandboxes/simulation/src" mrl-simulation supervise
```

The runtime is local supervision infrastructure, not a Stockplayer production
dependency. The selected implementation shape is the WNT Python event-sourced
simulation pack.
