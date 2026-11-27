import pytest
from sqlalchemy.orm import Session
from src.main.api.classes.api_manager import ApiManager
from src.main.api.models.login_user_request import LoginUserRequest
from src.main.api.models.create_user_request import CreateUserRequest
from src.main.api.db.crud.user_crud import UserCrudDb as User


@pytest.mark.api
class TestUserLogin:
    def test_login_admin(self, api_manager: ApiManager, db_session: Session):
        login_user_request = LoginUserRequest(username="admin", password="123456")
        response = api_manager.admin_steps.login_user(login_user_request)

        assert login_user_request.username == response.user.username, 'Имя админа в ответе не совпадает'
        assert response.user.role == "ROLE_ADMIN", 'Роль админа не совпадает с ожидаемой'

        user_from_db = User.get_user_by_username(db_session, login_user_request.username)
        assert user_from_db.role == "ROLE_ADMIN", 'Роль админа в БД не совпадает с ответом API'

    def test_login_user(self, api_manager: ApiManager, create_user_request: CreateUserRequest, db_session: Session):
        response = api_manager.admin_steps.login_user(create_user_request)

        assert create_user_request.username == response.user.username, 'Имя пользователя в ответе не совпадает'
        assert response.user.role == "ROLE_USER", 'Роль пользователя не совпадает с ожидаемой'

        user_from_db = User.get_user_by_username(db_session, create_user_request.username)
        assert user_from_db.username == response.user.username, 'Пользователя нет в БД'
        assert user_from_db.role == response.user.role, 'Роль пользователя в БД не совпадает с ответом API'