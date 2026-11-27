import pytest
from sqlalchemy.orm import Session
from src.main.api.classes.api_manager import ApiManager
from src.main.api.generators.model_generator import RandomModelGenerator
from src.main.api.models.create_user_request import CreateUserRequest
from src.main.api.models.credit_request_request import CreditRequestRequest
from src.main.api.db.crud.credit_crud import CreditCrudDb as Credit
from src.main.api.db.crud.account_crud import AccountCrudDb as Account


@pytest.mark.api
class TestCreditRequest:
    def test_credit_request_valid(self, api_manager: ApiManager, create_credit_user_request: CreateUserRequest, credit_account, db_session: Session):
        credit_request = RandomModelGenerator.generate(CreditRequestRequest)
        credit_request.accountId = credit_account.id

        credit = api_manager.user_steps.request_credit(create_credit_user_request, credit_request)

        credit_history = api_manager.user_steps.get_credit_history(create_credit_user_request)

        assert credit.amount == credit_request.amount, 'Сумма кредита в ответе не совпадает с запрошенной'
        assert credit.id == credit_account.id, 'ID в ответе не совпадает с ID аккаунта'
        assert credit_history.credits[0].amount == credit_request.amount, 'Сумма кредита в истории не совпадает с запрошенной'
        assert credit_history.credits[0].accountId == credit_account.id, 'ID аккаунта в истории не совпадает'

        credit_from_db = Credit.get_credit_by_id(db_session, credit.creditId)
        assert credit_from_db is not None, 'Кредит не найден в БД'
        assert credit_from_db.account_id == credit_account.id, 'ID аккаунта в БД не совпадает'
        assert credit_from_db.amount == credit_request.amount, 'Сумма кредита в БД не совпадает'
        assert credit_from_db.balance == -credit_request.amount, 'Баланс кредита в БД неверный'


    def test_credit_request_invalid(self, api_manager: ApiManager, create_user_request: CreateUserRequest, account, db_session: Session):
        credit_request = RandomModelGenerator.generate(CreditRequestRequest)
        credit_request.accountId = account.id

        balance_before = Account.get_account_by_id(db_session, account.id).balance

        api_manager.user_steps.request_credit_invalid(create_user_request, credit_request)
        transactions = api_manager.user_steps.get_account_transfactions(create_user_request, account.id)

        assert transactions.balance == account.balance, 'Баланс в ответе API изменился, хотя кредит должен был быть отклонен'

        account_from_db = Account.get_account_by_id(db_session, account.id)
        assert account_from_db.balance == balance_before, 'Баланс в БД изменился, хотя кредит должен был быть отклонен'

        credits_from_db = Credit.get_credits_by_account_id(db_session, account.id)
        assert len(credits_from_db) == 0, 'Кредит создан, хотя запрос должен был быть отклонен'