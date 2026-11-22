from typing import Optional
import requests
from src.main.api.models.base_model import BaseModel
from requests import Response
from src.main.api.foundation.http_requester import HttpRequester
from src.main.api.configs.config import Config
import allure



class CrudRequester(HttpRequester):
    def post(self, model: Optional[BaseModel]) -> BaseModel | Response:
        body = model.model_dump() if model is not None else ""

        with allure.step(f"POST {Config.fetch("backendUrl")}{self.endpoint.value.url}"):
            allure.attach(str(body), "Request body", allure.attachment_type.JSON)

        response = requests.post(
            url=f"{Config.fetch("backendUrl")}{self.endpoint.value.url}",
            headers=self.request_spec,
            json=body
        )

        allure.attach(
            response.text,
            "Request body",
            allure.attachment_type.JSON
        )

        self.response_spec(response)
        return response

    def get(self, obj_id: Optional[int] = None) -> BaseModel | Response:
        base_url = Config.fetch("backendUrl")
        url = f"{base_url}{self.endpoint.value.url}"
        if obj_id is not None:
            url = f"{url}/{obj_id}"

        body = {"obj_id": obj_id} if obj_id is not None else ""

        with allure.step(f"GET {url}"):
            allure.attach(str(body), "Request body", allure.attachment_type.JSON)

        response = requests.get(
            url=url,
            headers=self.request_spec
        )

        allure.attach(
            response.text,
            "Response body",
            allure.attachment_type.JSON
        )

        self.response_spec(response)
        return response

    def delete(self, user_id: int) -> BaseModel | Response:
        response = requests.delete(
            url=f"{Config.fetch("backendUrl")}{self.endpoint.value.url}/{user_id}",
            headers=self.request_spec
        )
        self.response_spec(response)
        return response
