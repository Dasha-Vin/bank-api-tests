from typing import List
from src.main.api.db.models.transaction_table import Transaction


def find_transfer_transactions(transactions: List[Transaction], from_id: int, to_id: int, amount: float) -> List[Transaction]:
    return [
        t for t in transactions
        if t.transaction_type.lower() == 'transfer'
           and t.from_account_id == from_id
           and t.to_account_id == to_id
           and t.amount == amount
    ]

def has_no_transfer_out(transactions: List[Transaction]) -> bool:
    # Проверяет, что среди транзакций нет transfer_out
    return not any(t.transaction_type == 'transfer_out' for t in transactions)