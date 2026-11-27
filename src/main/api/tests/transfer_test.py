import pytest
import random
from sqlalchemy.orm import Session
from src.main.api.classes.api_manager import ApiManager
from src.main.api.models.create_user_request import CreateUserRequest
from src.main.api.generators.model_generator import RandomModelGenerator
from src.main.api.models.transfer_request import TransferRequest
from src.main.api.db.crud.account_crud import AccountCrudDb as Account
from src.main.api.db.crud.transaction_crud import TransactionCrudDb as Transaction
from src.main.api.utils.helpers import find_transfer_transactions, has_no_transfer_out


@pytest.mark.api
class TestTransfer:
    def test_transfer_valid(self, api_manager: ApiManager, create_user_request: CreateUserRequest, two_funded_accounts, db_session: Session):
        first_account, second_account, dep_first, dep_second = two_funded_accounts

        transfer_request = RandomModelGenerator.generate(TransferRequest)
        transfer_request.fromAccountId = first_account.id
        transfer_request.toAccountId = second_account.id
        transfer_request.amount = min(transfer_request.amount, dep_first.amount)

        api_manager.user_steps.transfer(create_user_request, transfer_request)

        first_transactions = api_manager.user_steps.get_account_transfactions(create_user_request, first_account.id)
        second_transactions = api_manager.user_steps.get_account_transfactions(create_user_request, second_account.id)

        assert first_transactions.balance == dep_first.amount - transfer_request.amount, 'Баланс отправителя в API не уменьшился'
        assert second_transactions.balance == dep_second.amount + transfer_request.amount, 'Баланс получателя в API не увеличился'

        first_account_from_db = Account.get_account_by_id(db_session, first_account.id)
        second_account_from_db = Account.get_account_by_id(db_session, second_account.id)

        assert first_account_from_db.balance == dep_first.amount - transfer_request.amount, 'Баланс отправителя в БД не уменьшился'
        assert second_account_from_db.balance == dep_second.amount + transfer_request.amount, 'Баланс получателя в БД не увеличился'

        first_db_transactions = Transaction.get_transactions_by_account_id(db_session, first_account.id)
        transfer_tx = find_transfer_transactions(first_db_transactions, first_account.id, second_account.id, transfer_request.amount)

        assert len(transfer_tx) == 1, 'Транзакция перевода не найдена в БД'

        second_db_transactions = Transaction.get_transactions_by_account_id(db_session, second_account.id)
        transfer_tx_second = find_transfer_transactions(second_db_transactions, first_account.id, second_account.id, transfer_request.amount)
        assert len(transfer_tx_second) == 1, 'Транзакция перевода не найдена в БД у получателя'


    def test_transfer_invalid(self, api_manager: ApiManager, create_user_request: CreateUserRequest, two_funded_accounts, db_session: Session):
        first_account, second_account, dep_first, dep_second = two_funded_accounts

        first_balance_before = Account.get_account_by_id(db_session, first_account.id).balance
        second_balance_before = Account.get_account_by_id(db_session, second_account.id).balance

        invalid_amount = random.randint(1, 499)
        transfer_request = TransferRequest(
            fromAccountId=first_account.id,
            toAccountId=second_account.id,
            amount=invalid_amount
        )

        api_manager.user_steps.transfer_invalid(create_user_request, transfer_request)

        first_transactions = api_manager.user_steps.get_account_transfactions(create_user_request, first_account.id)
        second_transactions = api_manager.user_steps.get_account_transfactions(create_user_request, second_account.id)

        assert first_transactions.balance == dep_first.amount, 'Баланс отправителя в API изменился при неудачном переводе'
        assert second_transactions.balance == dep_second.amount, 'Баланс получателя в API изменился при неудачном переводе'

        first_account_from_db = Account.get_account_by_id(db_session, first_account.id)
        second_account_from_db = Account.get_account_by_id(db_session, second_account.id)

        assert first_account_from_db.balance == first_balance_before, 'Баланс отправителя изменился при неудачном переводе'
        assert second_account_from_db.balance == second_balance_before, 'Баланс получателя изменился при неудачном переводе'

        first_db_transactions = Transaction.get_transactions_by_account_id(db_session, first_account.id)
        assert has_no_transfer_out(first_db_transactions), 'Транзакция transfer_out создана, хотя перевод должен был быть отклонен'



