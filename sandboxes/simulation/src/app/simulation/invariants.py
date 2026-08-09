from __future__ import annotations

from app.infrastructure.memory import AccountProjections


def cash_non_negative(projections: AccountProjections) -> bool:
    return all(value >= 0 for value in projections.cash_minor.values())


def positions_non_negative(projections: AccountProjections) -> bool:
    return all(value >= 0 for value in projections.positions.values())


def reservations_non_negative(projections: AccountProjections) -> bool:
    return all(value >= 0 for value in projections.reserved_cash_minor.values())


def ledger_explains_total_cash(projections: AccountProjections) -> bool:
    return all(sum(entry.amount_minor for entry in projections.ledger[account_id]) == projections.cash_minor[account_id] + projections.reserved_cash_minor.get(account_id, 0) for account_id in projections.cash_minor)
