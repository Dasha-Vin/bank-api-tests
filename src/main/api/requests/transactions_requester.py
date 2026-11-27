from src.main.api.requests.requester import Requester
from src.main.api.models.transaction_response import AccountTransactionsResponse
import requests


class TransactionsRequester(Requester):
    def get(self, account_id: int) -> AccountTransactionsResponse:
        url = f"{self.base_url}/account/transactions/{account_id}"
        response = requests.get(
            url=url,
            headers=self.headers
        )
        self.response_spec(response)
        return AccountTransactionsResponse(**response.json())