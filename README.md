# Stockplayer

Stockplayer is a deterministic fictional stock-market simulation and software
architecture laboratory. The first repository surface is the domain simulation
under `sandboxes/simulation`; production applications and Docker Compose will
follow released model contracts.

> Stockplayer is a fictional market simulation for software engineering and
> educational use. It does not provide investment advice, market predictions,
> brokerage services, or recommendations.

## Current quick start

```bash
python3 -m unittest discover -s sandboxes/simulation/tests -v
PYTHONPATH="$HOME/.wnt/runtime/mrl:sandboxes/simulation/src" mrl-simulation supervise
```

See [the simulation project](sandboxes/simulation/README.md) for its boundaries
and current behavior.
