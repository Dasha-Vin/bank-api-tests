from src.main.api.models.base_model import BaseModel
from typing import Optional, List


class Transaction(BaseModel):
    transactionId: int
    type: str
    amount: float
    fromAccountId: Optional[int] = None
    toAccountId: Optional[int] = None
    createdAt: str

class AccountTransactionsResponse(BaseModel):
    id: int
    number: str
    balance: float
    transactions: List[Transaction]