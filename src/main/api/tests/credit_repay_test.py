import pytest
from sqlalchemy.orm import Session
from src.main.api.classes.api_manager import ApiManager
from src.main.api.models.credit_request_request import CreditRequestRequest
from src.main.api.models.credit_repay_request import CreditRepayRequest
from src.main.api.models.deposit_request import DepositRequest
from src.main.api.db.crud.credit_crud import CreditCrudDb as Credit
from src.main.api.models.create_user_request import CreateUserRequest


@pytest.mark.api
class TestCreditRepay:
    def test_credit_repay_valid(self, api_manager: ApiManager, create_credit_user_request: CreateUserRequest, db_session: Session):
        account = api_manager.user_steps.create_account(create_credit_user_request)

        api_manager.user_steps.deposit(
            create_credit_user_request,
            DepositRequest(accountId=account.id, amount=5000)
        )

        credit = api_manager.user_steps.request_credit(
            create_credit_user_request,
            CreditRequestRequest(accountId=account.id, amount=5000, termMonths=12)
        )

        credit_repay_request = CreditRepayRequest(creditId=credit.creditId, accountId=account.id, amount=5000)
        api_manager.user_steps.repay_credit(create_credit_user_request, credit_repay_request)

        credit_history = api_manager.user_steps.get_credit_history(create_credit_user_request)
        assert credit_history.credits[0].balance == 0

        credit_from_db = Credit.get_credit_by_id(db_session, credit.creditId)
        assert credit_from_db is not None
        assert credit_from_db.balance == 0, 'Баланс кредита в БД не обнулился'


    def test_credit_repay_invalid(self, api_manager: ApiManager, create_credit_user_request: CreateUserRequest, db_session: Session):
        account = api_manager.user_steps.create_account(create_credit_user_request)

        api_manager.user_steps.deposit(
            create_credit_user_request,
            DepositRequest(accountId=account.id, amount=5000)
        )

        credit = api_manager.user_steps.request_credit(
            create_credit_user_request,
            CreditRequestRequest(accountId=account.id, amount=5000, termMonths=12)
        )

        credit_repay_request = CreditRepayRequest(creditId=credit.creditId, accountId=account.id, amount=5000)
        api_manager.user_steps.repay_credit(create_credit_user_request, credit_repay_request)

        balance_after_first = api_manager.user_steps.get_account_transfactions(
            create_credit_user_request,
            account.id
        ).balance
        credit_balance_after_first = Credit.get_credit_by_id(db_session, credit.creditId).balance

        api_manager.user_steps.repay_credit_invalid(create_credit_user_request, credit_repay_request)

        balance_after_second = api_manager.user_steps.get_account_transfactions(
            create_credit_user_request,
            account.id
        ).balance

        assert balance_after_first == balance_after_second

        credit_balance_after_second = Credit.get_credit_by_id(db_session, credit.creditId).balance
        assert credit_balance_after_second == credit_balance_after_first, 'Баланс кредита изменился при повторном погашении'
