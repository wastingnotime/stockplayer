# Refinement check

Slice 006 confirms that one reservation can support multiple execution facts.
Each partial fill settles actual cost, releases only the unused hold for that
fill, and preserves exact remaining quantity and reservation for the next fill.

The next refinement should test duplicate execution delivery and protect the
economic effect with idempotency before adding broader order projections.
