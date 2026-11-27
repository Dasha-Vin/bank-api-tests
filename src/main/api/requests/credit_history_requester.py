import requests
from src.main.api.requests.requester import Requester
from src.main.api.models.credit_history_response import CreditHistoryResponse

class CreditHistoryRequester(Requester):
    def get(self) -> CreditHistoryResponse:
        url = f"{self.base_url}/credit/history"
        response = requests.get(
            url=url,
            headers=self.headers
        )
        self.response_spec(response)
        return CreditHistoryResponse(**response.json())