# Slice 005: execution of a reserved limit buy

- **Implementation pack:** WNT Python event-sourced simulation
- **Runtime target:** headless Python
- **Architecture mode:** reservation settlement and projection update

## Use-case contract

An open limit-buy reservation executes at a current price at or below its
limit. The reserved hold is settled at the execution cost, unused cash is
released, the position increases, and the reservation closes. A price above
the limit leaves the reservation untouched.

## Deterministic scenario

Reserve 20 AUR at a 2,000 minor-unit limit with 100,000 cash. Execute at 1,800.
Final available cash is 64,000, reserved cash is zero, and the position is 20
AUR. The ledger records a 36,000 minor-unit settlement.

## Done criteria

- Execution and release are represented by one auditable domain fact.
- Replayed state matches cash, position, ledger, and reservation projections.
- Above-limit execution has no economic effect.

Out of scope: partial fills, duplicate execution delivery, sell orders, and
order-status projections.
