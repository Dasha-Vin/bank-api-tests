import pytest
from sqlalchemy.orm import Session
from src.main.api.classes.api_manager import ApiManager
from src.main.api.models.create_user_request import CreateUserRequest
from src.main.api.generators.model_generator import RandomModelGenerator
from src.main.api.models.deposit_request import DepositRequest
from src.main.api.models.transfer_request import TransferRequest
from src.main.api.db.crud.account_crud import AccountCrudDb as Account
from src.main.api.db.crud.transaction_crud import TransactionCrudDb as Transaction


@pytest.mark.api
class TestTransfer:
    def test_transfer_valid(self, api_manager: ApiManager, create_user_request: CreateUserRequest, db_session: Session):
        first_account_id = api_manager.user_steps.create_account(create_user_request).id
        second_account_id = api_manager.user_steps.create_account(create_user_request).id

        deposit_first_request = RandomModelGenerator.generate(DepositRequest)
        deposit_first_request.accountId = first_account_id
        deposit_second_request = RandomModelGenerator.generate(DepositRequest)
        deposit_second_request.accountId = second_account_id

        api_manager.user_steps.deposit(create_user_request, deposit_first_request)
        api_manager.user_steps.deposit(create_user_request, deposit_second_request)

        transfer_request = TransferRequest(
            fromAccountId=first_account_id,
            toAccountId=second_account_id,
            amount=500
        )

        api_manager.user_steps.transfer(create_user_request, transfer_request)

        first_transactions = api_manager.user_steps.get_account_transfactions(create_user_request, first_account_id)
        second_transactions = api_manager.user_steps.get_account_transfactions(create_user_request, second_account_id)
        assert first_transactions.balance == deposit_first_request.amount - 500
        assert second_transactions.balance == deposit_second_request.amount + 500

        first_account_from_db = Account.get_account_by_id(db_session, first_account_id)
        second_account_from_db = Account.get_account_by_id(db_session, second_account_id)
        assert first_account_from_db.balance == deposit_first_request.amount - 500, 'Баланс отправителя в БД не уменьшился'
        assert second_account_from_db.balance == deposit_second_request.amount + 500, 'Баланс получателя в БД не увеличился'

        first_db_transactions = Transaction.get_transactions_by_account_id(db_session, first_account_id)
        transfer_tx = [
            t for t in first_db_transactions
            if t.transaction_type.lower() == 'transfer'
               and t.from_account_id == first_account_id
               and t.to_account_id == second_account_id
               and t.amount == 500
        ]

        assert len(transfer_tx) == 1, 'Транзакция перевода не найдена в БД'
        assert transfer_tx[0].amount == 500.0
        assert transfer_tx[0].from_account_id == first_account_id
        assert transfer_tx[0].to_account_id == second_account_id

        # Проверяем, что у получателя тоже видна эта транзакция
        second_db_transactions = Transaction.get_transactions_by_account_id(db_session, second_account_id)
        transfer_tx_second = [
            t for t in second_db_transactions
            if t.transaction_type.lower() == 'transfer'
               and t.from_account_id == first_account_id
               and t.to_account_id == second_account_id
        ]
        assert len(transfer_tx_second) == 1, 'Транзакция перевода не найдена в БД у получателя'


    def test_transfer_invalid(self, api_manager: ApiManager, create_user_request: CreateUserRequest, db_session: Session):
        first_account_id = api_manager.user_steps.create_account(create_user_request).id
        second_account_id = api_manager.user_steps.create_account(create_user_request).id

        deposit_first_request = RandomModelGenerator.generate(DepositRequest)
        deposit_first_request.accountId = first_account_id
        deposit_second_request = RandomModelGenerator.generate(DepositRequest)
        deposit_second_request.accountId = second_account_id

        api_manager.user_steps.deposit(create_user_request, deposit_first_request)
        api_manager.user_steps.deposit(create_user_request, deposit_second_request)

        first_balance_before = Account.get_account_by_id(db_session, first_account_id).balance
        second_balance_before = Account.get_account_by_id(db_session, second_account_id).balance

        transfer_request = TransferRequest(
            fromAccountId=first_account_id,
            toAccountId=second_account_id,
            amount=499
        )

        api_manager.user_steps.transfer_invalid(create_user_request, transfer_request)

        first_transactions = api_manager.user_steps.get_account_transfactions(create_user_request, first_account_id)
        second_transactions = api_manager.user_steps.get_account_transfactions(create_user_request, second_account_id)
        assert first_transactions.balance == deposit_first_request.amount
        assert second_transactions.balance == deposit_second_request.amount

        first_account_from_db = Account.get_account_by_id(db_session, first_account_id)
        second_account_from_db = Account.get_account_by_id(db_session, second_account_id)
        assert first_account_from_db.balance == first_balance_before, 'Баланс отправителя изменился при неудачном переводе'
        assert second_account_from_db.balance == second_balance_before, 'Баланс получателя изменился при неудачном переводе'

        first_db_transactions = Transaction.get_transactions_by_account_id(db_session, first_account_id)
        transfer_out_tx = [t for t in first_db_transactions if t.transaction_type == 'transfer_out']
        assert len(transfer_out_tx) == 0, 'Транзакция transfer_out создана, хотя перевод должен был быть отклонен'



