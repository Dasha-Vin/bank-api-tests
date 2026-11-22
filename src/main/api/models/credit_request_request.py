from typing import Annotated
from src.main.api.models.base_model import BaseModel
from src.main.api.generators.creation_rule import CreationRule


class CreditRequestRequest(BaseModel):
    accountId: Annotated[int, CreationRule(regex=r'^[1-9][0-9]{0,3}$')]
    amount: Annotated[float, CreationRule(regex=r'^([5-9][0-9]{3}|1[0-4][0-9]{3}|15000)$')]
    termMonths: Annotated[int, CreationRule(regex=r'^12$')]