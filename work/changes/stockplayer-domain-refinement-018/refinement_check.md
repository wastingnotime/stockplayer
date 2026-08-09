# Refinement check

Slice 018 demonstrates the event-before-projection failure boundary. A failed
projection leaves the event stream authoritative; rebuilding restores cash,
position, and ledger state without duplicating the execution.

The next refinement can add runtime observations for failure and recovery or
model projection lag explicitly.
