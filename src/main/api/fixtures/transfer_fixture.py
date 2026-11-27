import pytest
from src.main.api.generators.model_generator import RandomModelGenerator
from src.main.api.models.deposit_request import DepositRequest


@pytest.fixture
def two_funded_accounts(api_manager, create_user_request):
    # Создает два аккаунта и пополняет их баланс
    acc1 = api_manager.user_steps.create_account(create_user_request)
    acc2 = api_manager.user_steps.create_account(create_user_request)

    dep1 = RandomModelGenerator.generate(DepositRequest)
    dep1.accountId = acc1.id
    dep2 = RandomModelGenerator.generate(DepositRequest)
    dep2.accountId = acc2.id

    api_manager.user_steps.deposit(create_user_request, dep1)
    api_manager.user_steps.deposit(create_user_request, dep2)
    return acc1, acc2, dep1, dep2