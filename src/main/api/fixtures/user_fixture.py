import pytest
from src.main.api.models.create_user_request import CreateUserRequest
from src.main.api.generators.model_generator import RandomModelGenerator


@pytest.fixture
def create_user_request(api_manager):
    user_request = RandomModelGenerator.generate(CreateUserRequest)
    user_request.role = "ROLE_USER"
    api_manager.admin_steps.create_user(user_request)
    return user_request

@pytest.fixture
def account(api_manager, create_user_request):
    return api_manager.user_steps.create_account(create_user_request)