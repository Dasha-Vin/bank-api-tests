from typing import Annotated
from src.main.api.models.base_model import BaseModel
from src.main.api.generators.creation_rule import CreationRule


class TransferRequest(BaseModel):
    fromAccountId: Annotated[int, CreationRule(regex=r'^[1-9][0-9]{0,3}$')]
    toAccountId: Annotated[int, CreationRule(regex=r'^[1-9][0-9]{0,3}$')]
    amount: Annotated[float, CreationRule(regex=r'^(5[0-9]{2}|[6-9][0-9]{2}|[1-9][0-9]{3}|10000)$')]