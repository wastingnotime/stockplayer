# Refinement check

Slice 009 confirms the cash-account ownership invariant on the sell path. A
successful sell settles proceeds and reduces the position; an oversell is an
auditable rejection with no economic mutation.

The next refinement should introduce sell-side quantity reservations or
average-cost projection, depending on which architectural lesson is selected.
