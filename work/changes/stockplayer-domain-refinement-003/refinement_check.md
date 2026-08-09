# Refinement check

Slice 003 confirms that available cash and reserved cash are separate domain
values. The reservation is an event-sourced fact and replay reconstructs the
same held amount. A second order cannot consume funds already held by the first.

The next refinement should add cancellation and reservation release so an open
order can complete its lifecycle without introducing execution complexity yet.
