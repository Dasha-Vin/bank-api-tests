import pytest
from src.main.api.generators.model_generator import RandomModelGenerator
from src.main.api.models.create_user_request import CreateUserRequest
from src.main.api.models.deposit_request import DepositRequest
from src.main.api.models.credit_request_request import CreditRequestRequest


@pytest.fixture
def create_credit_user_request(api_manager):
    user_request = RandomModelGenerator.generate(CreateUserRequest)
    user_request.role = "ROLE_CREDIT_SECRET"
    api_manager.admin_steps.create_user(user_request)
    return user_request

@pytest.fixture
def credit_account(api_manager, create_credit_user_request):
    return api_manager.user_steps.create_account(create_credit_user_request)

@pytest.fixture
def credited_account(api_manager, create_credit_user_request, credit_account):
    # Создает аккаунт, пополняет его и оформляет кредит
    deposit_req = RandomModelGenerator.generate(DepositRequest)
    deposit_req.accountId = credit_account.id
    api_manager.user_steps.deposit(create_credit_user_request, deposit_req)

    credit_req = RandomModelGenerator.generate(CreditRequestRequest)
    credit_req.accountId = credit_account.id
    credit = api_manager.user_steps.request_credit(create_credit_user_request, credit_req)

    return credit_account, credit