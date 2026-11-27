import pytest
import random
from sqlalchemy.orm import Session
from src.main.api.classes.api_manager import ApiManager
from src.main.api.models.create_user_request import CreateUserRequest
from src.main.api.models.deposit_request import DepositRequest
from src.main.api.generators.model_generator import RandomModelGenerator
from src.main.api.db.crud.account_crud import AccountCrudDb as Account
from src.main.api.db.crud.transaction_crud import TransactionCrudDb as Transaction


@pytest.mark.api
class TestDeposit:
    def test_deposit_valid(self, api_manager: ApiManager, create_user_request: CreateUserRequest, account, db_session: Session):
        deposit_request = RandomModelGenerator.generate(DepositRequest)
        deposit_request.accountId = account.id

        api_manager.user_steps.deposit(create_user_request, deposit_request)

        transactions = api_manager.user_steps.get_account_transfactions(create_user_request, account.id)
        assert transactions.balance == account.balance + deposit_request.amount, 'Баланс на счете не соответствует ожидаемому после пополнения'

        account_from_db = Account.get_account_by_id(db_session, account.id)
        assert account_from_db is not None, 'Счёт не найден в БД'
        assert account_from_db.balance == account.balance + deposit_request.amount, 'Баланс в БД не соответствует ожидаемому'

        transaction_from_db = Transaction.get_transaction_by_id(db_session, transactions.transactions[0].transactionId)
        assert transaction_from_db is not None, 'Транзакция не найдена в БД'
        assert transaction_from_db.transaction_type == "deposit", 'Тип транзакции в БД не deposit'
        assert transaction_from_db.to_account_id == account.id, 'Транзакция привязана не к тому счету'

    def test_deposit_invalid(self, api_manager: ApiManager, create_user_request: CreateUserRequest, account, db_session: Session):
        invalid_amount = random.randint(1, 999)
        deposit_request = DepositRequest(accountId=account.id, amount=invalid_amount)

        balance_before = Account.get_account_by_id(db_session, account.id).balance

        api_manager.user_steps.deposit_invalid(create_user_request, deposit_request)

        transactions = api_manager.user_steps.get_account_transfactions(create_user_request, account.id)
        assert transactions.balance == account.balance, 'Баланс в API изменился при невалидном пополнении'

        account_from_db = Account.get_account_by_id(db_session, account.id)
        assert account_from_db.balance == balance_before, 'Баланс изменился, хотя пополнение должно было быть отклонено'