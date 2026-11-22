import pytest
from sqlalchemy.orm import Session
from src.main.api.classes.api_manager import ApiManager
from src.main.api.models.create_user_request import CreateUserRequest
from src.main.api.models.deposit_request import DepositRequest
from src.main.api.generators.model_generator import RandomModelGenerator
from src.main.api.db.crud.account_crud import AccountCrudDb as Account
from src.main.api.db.crud.transaction_crud import TransactionCrudDb as Transaction


@pytest.mark.api
class TestDeposit:
    def test_deposit_valid(self, api_manager: ApiManager, create_user_request: CreateUserRequest, db_session: Session):
        account = api_manager.user_steps.create_account(create_user_request)
        account_id = account.id
        deposit_request = RandomModelGenerator.generate(DepositRequest)
        deposit_request.accountId = account_id

        api_manager.user_steps.deposit(create_user_request, deposit_request)

        transactions = api_manager.user_steps.get_account_transfactions(create_user_request, account_id)
        assert transactions.balance == account.balance + deposit_request.amount

        account_from_db = Account.get_account_by_id(db_session, account_id)
        assert account_from_db is not None, 'Счёт не найден в БД'
        assert account_from_db.balance == account.balance + deposit_request.amount, 'Баланс в БД не соответствует ожидаемому'

        transaction_from_db = Transaction.get_transaction_by_id(db_session, transactions.transactions[0].transactionId)
        assert transaction_from_db is not None, 'Транзакция не найдена в БД'
        assert transaction_from_db.transaction_type == "deposit", 'Тип транзакции в БД не deposit'
        assert transaction_from_db.to_account_id == account_id, 'Транзакция привязана не к тому счету'

    def test_deposit_invalid(self, api_manager: ApiManager, create_user_request: CreateUserRequest, db_session: Session):
        account = api_manager.user_steps.create_account(create_user_request)
        account_id = account.id
        deposit_request = DepositRequest(accountId=account_id, amount=999)

        balance_before = Account.get_account_by_id(db_session, account_id).balance

        api_manager.user_steps.deposit_invalid(create_user_request, deposit_request)

        transactions = api_manager.user_steps.get_account_transfactions(create_user_request, account_id)
        assert transactions.balance == account.balance

        account_from_db = Account.get_account_by_id(db_session, account_id)
        assert account_from_db.balance == balance_before, 'Баланс изменился, хотя пополнение должно было быть отклонено'