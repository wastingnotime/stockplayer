# Refinement check

Slice 005 confirms that a reserved order can settle at a better current price:
the reservation closes, the unused hold returns to available cash, and the
position and ledger reflect the actual execution cost. A stale above-limit
price does not mutate the stream.

The next refinement should address partial fills or duplicate execution
delivery before introducing sell-side quantity reservations.
