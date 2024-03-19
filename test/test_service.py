import asyncio
import time
import pytest
from src.auth.util import BcryptUtil, JwtUtil
from src.auth.service import AuthService, UserService
from src.auth.scheme import LoginAuthScheme, ModelUserScheme, RegisterAuthScheme, TokensScheme
from src.auth.model import User

from src.auth.service import RoleService
from src.auth.scheme import ModelRoleScheme
from src.auth.model import Role
from unittest.mock import AsyncMock, MagicMock, patch

@pytest.fixture
def mock_role_rep():
    return AsyncMock()

@pytest.fixture
def mock_db_session():
    return AsyncMock()

@pytest.fixture
def mock_user_rep():
    return AsyncMock()

@pytest.fixture
def mock_role_serv():
    return AsyncMock()

@pytest.fixture
def mock_user_schema():
    return MagicMock()

@pytest.fixture
def mock_db_session():
    return AsyncMock()

@pytest.mark.asyncio
async def test_get_all(mock_db_session, mock_role_rep):
    with patch('src.auth.service.roleRep', mock_role_rep):
        mock_role_rep.get_all.return_value = [Role()]
        roles = await RoleService.get_all(mock_db_session)
        assert len(roles) == 1
        mock_role_rep.get_all.assert_called_once()

@pytest.mark.asyncio
async def test_get_model_scheme_all(mock_db_session, mock_role_rep):
    with patch('src.auth.service.roleRep', mock_role_rep):
        mock_role_rep.get_all.return_value = [Role(id=0, name='admin')]
        model_roles = await RoleService.get_model_scheme_all(mock_db_session)
        assert len(model_roles) == 1
        assert isinstance(model_roles[0], ModelRoleScheme)
        mock_role_rep.get_all.assert_called_once()

@pytest.mark.asyncio
async def test_get_all_by_id(mock_db_session, mock_role_rep):
    with patch('src.auth.service.roleRep', mock_role_rep):
        mock_role_rep.get_all_by_id.return_value = [Role()]
        roles = await RoleService.get_all_by_id([1], mock_db_session)
        assert len(roles) == 1
        mock_role_rep.get_all_by_id.assert_called_once()


@pytest.mark.asyncio
async def test_create(mock_db_session, mock_user_rep, mock_role_serv, mock_user_schema):
    with patch('src.auth.service.userRep', mock_user_rep), patch('src.auth.service.roleServ', mock_role_serv):
        mock_role_serv.get_all_by_id.return_value = []
        mock_user_rep.create.return_value = User()
        user = await UserService.create(mock_user_schema, mock_db_session)
        assert isinstance(user, User)
        mock_role_serv.get_all_by_id.assert_called_once()
        mock_user_rep.create.assert_called_once()

@pytest.mark.asyncio
async def test_create_and_get_model_scheme(mock_db_session, mock_user_rep, mock_role_serv, mock_user_schema):
    with patch('src.auth.service.userRep', mock_user_rep), patch('src.auth.service.roleServ', mock_role_serv):
        mock_role_serv.get_all_by_id.return_value = []
        mock_user_rep.create.return_value = User(id=0, username='test', password='test', email='test')
        model_user_scheme = await UserService.create_and_get_model_scheme(mock_user_schema, mock_db_session)
        assert isinstance(model_user_scheme, ModelUserScheme)
        mock_role_serv.get_all_by_id.assert_called_once()
        mock_user_rep.create.assert_called_once()

@pytest.mark.asyncio
async def test_register(mock_db_session, mock_user_rep, mock_user_schema):
    with patch('src.auth.service.userServ', mock_user_rep):
        mock_user_rep.create_and_get_model_scheme.return_value = ModelUserScheme(username='test', password='test', 
                                                                                 email='test', id=0, 
                                                                                 roles=[ModelRoleScheme(id=0, name='user'), ])
        register_auth_scheme = RegisterAuthScheme(username='test', password='test', email='test')
        registered_user = await AuthService.register(register_auth_scheme, mock_db_session)
        assert isinstance(registered_user, ModelUserScheme)
        mock_user_rep.create_and_get_model_scheme.assert_called_once()

@pytest.mark.asyncio
async def test_login(mock_db_session, mock_user_rep):
    with patch('src.auth.service.userServ', mock_user_rep):
        mock_user_rep.get_by_username.return_value = ModelUserScheme(username='test', password=BcryptUtil.hash_password('test'), 
                                                                     email='test', id=0, roles=[ModelRoleScheme(id=0, name='user'), ])
        login_auth_scheme = LoginAuthScheme(username='test', password='test')
        tokens = await AuthService.login(login_auth_scheme, mock_db_session)
        assert isinstance(tokens, TokensScheme)
        mock_user_rep.get_by_username.assert_called_once()

@pytest.mark.asyncio
async def test_logout(mock_user_rep):
    with patch('src.auth.service.userServ', mock_user_rep):
        mock_user_rep.get_by_username.return_value = ModelUserScheme(username='test', password=BcryptUtil.hash_password('test'), 
                                                                     email='test', id=0, roles=[ModelRoleScheme(id=0, name='user'), ])
        login_auth_scheme = LoginAuthScheme(username='test', password='test')
        tokens = await AuthService.login(login_auth_scheme, mock_db_session)
        assert isinstance(tokens, TokensScheme)
        mock_user_rep.get_by_username.assert_called_once()
        await AuthService.logout(tokens.access_token)
        assert tokens.access_token not in AuthService.access_tokens
        assert tokens.refresh_token not in AuthService.refresh_tokens
        assert tokens.access_token not in AuthService.access_refresh_tokens

@pytest.mark.asyncio
async def test_is_authenticated():
    user_data = User(id=0, username='test', password='test', email='test')
    model_user_scheme = ModelUserScheme.model_validate(user_data, from_attributes=True)
    payload_user= model_user_scheme.model_dump()
    data = JwtUtil.create_tokens(payload_user)
    AuthService.access_tokens.add(data[0])
    #AuthService.access_tokens.add('test_access_token')
    assert await AuthService.is_authenticated(data[0]) is True
    AuthService.access_tokens.remove(data[0])
    assert await AuthService.is_authenticated(data[0]) is False

@pytest.mark.asyncio
async def test_get_user_by_token(mock_db_session, mock_user_rep):
    with patch('src.auth.service.userServ', mock_user_rep):
        user_data = User(id=0, username='test', password='test', email='test')
        model_user_scheme = ModelUserScheme.model_validate(user_data, from_attributes=True)
        payload_user= model_user_scheme.model_dump()
        data = JwtUtil.create_tokens(payload_user)
        AuthService.access_tokens.add(data[0])
        mock_user_rep.get_by_id.return_value = User(id=0, username='test', password='test', email='test')
        user = await AuthService.get_user_by_token(data[0], mock_db_session)
        assert user_data != user
        mock_user_rep.get_by_id.assert_called_once()
        AuthService.access_tokens.remove(data[0])

@pytest.mark.asyncio
async def test_update_access_token(mock_db_session, mock_user_rep):
    with patch('src.auth.service.userServ', mock_user_rep):
        mock_user_rep.get_by_username.return_value = ModelUserScheme(username='test', password=BcryptUtil.hash_password('test'), 
                                                                     email='test', id=0, roles=[ModelRoleScheme(id=0, name='user'), ])
        login_auth_scheme = LoginAuthScheme(username='test', password='test')
        tokens = await AuthService.login(login_auth_scheme, mock_db_session)
        assert isinstance(tokens, TokensScheme)
        mock_user_rep.get_by_username.assert_called_once()
        time.sleep(2)
        new_tokens = await AuthService.update_access_token(tokens)
        assert isinstance(new_tokens, TokensScheme)
        assert new_tokens.access_token in AuthService.access_tokens
        assert new_tokens.refresh_token in AuthService.refresh_tokens
        assert tokens.access_token not in AuthService.access_refresh_tokens