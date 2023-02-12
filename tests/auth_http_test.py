import pytest
import json
import requests
from src import config
BASE_ADDRESS = 'http://127.0.0.1'
BASE_PORT = config.port
BASE_URL = f"{BASE_ADDRESS}:{BASE_PORT}"


@pytest.fixture
def user_dict1():
    requests.post(f"{BASE_URL}/auth/register/v2", json={'email': "third@gmail.com",
                                                        'password': "hello123", 'name_first': "Trent", 'name_last': "Arnold"})
    return {'email': "third@gmail.com", 'password': "hello123", 'name_first': "Trent", 'name_last': "Arnold"}


@pytest.fixture
def user_dict2():
    response = requests.post(f"{BASE_URL}/auth/register/v2", json={'email': "second@gmail.com",
                                                                   'password': "password", 'name_first': "Ben", 'name_last': "Mendy"})
    dict = json.loads(response.text)
    return dict


@pytest.fixture
def clear():
    requests.delete(f"{BASE_URL}/clear/v1")


def test_register_invalid_email(clear):
    response = requests.post(f"{BASE_URL}/auth/register/v2", json={'email': "first.com",
                                                                   'password': "helloworld", 'name_first': "John", 'name_last': "Doe"})
    assert response.status_code == 400

    response = requests.post(f"{BASE_URL}/auth/register/v2", json={'email': "first/last@gmail.com",
                                                                   'password': "helloworld", 'name_first': "John", 'name_last': "Doe"})
    assert response.status_code == 400

    response = requests.post(f"{BASE_URL}/auth/register/v2", json={'email': "    @gmail.com",
                                                                   'password': "helloworld", 'name_first': "John", 'name_last': "Doe"})
    assert response.status_code == 400

    response = requests.post(f"{BASE_URL}/auth/register/v2", json={'email': "first&last@gmail.com",
                                                                   'password': "helloworld", 'name_first': "John", 'name_last': "Doe"})
    assert response.status_code == 400

    response = requests.post(f"{BASE_URL}/auth/register/v2", json={'email': "",
                                                                   'password': "helloworld", 'name_first': "John", 'name_last': "Doe"})
    assert response.status_code == 400


def test_register_email_in_use(clear, user_dict1):
    response = requests.post(f"{BASE_URL}/auth/register/v2", json={
                             'email': user_dict1['email'], 'password': "helloworld", 'name_first': "John", 'name_last': "Doe"})
    assert response.status_code == 400


def test_register_short_password(clear):
    response = requests.post(f"{BASE_URL}/auth/register/v2", json={'email': "first@gmail.com",
                                                                   'password': "hello", 'name_first': "John", 'name_last': "Doe"})
    assert response.status_code == 400


def test_register_short_firstname(clear):
    response = requests.post(f"{BASE_URL}/auth/register/v2", json={'email': "first@gmail.com",
                                                                   'password': "helloworld", 'name_first': "", 'name_last': "Doe"})
    assert response.status_code == 400


def test_register_long_firstname(clear):
    response = requests.post(f"{BASE_URL}/auth/register/v2", json={'email': "first@gmail.com", 'password': "helloworld",
                                                                   'name_first': "Johnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnn", 'name_last': "Doe"})
    assert response.status_code == 400


def test_register_short_lastname(clear):
    response = requests.post(f"{BASE_URL}/auth/register/v2", json={'email': "first@gmail.com",
                                                                   'password': "helloworld", 'name_first': "John", 'name_last': ""})
    assert response.status_code == 400


def test_register_long_surname(clear):
    response = requests.post(f"{BASE_URL}/auth/register/v2", json={'email': "first@gmail.com", 'password': "helloworld",
                                                                   'name_first': "John", 'name_last': "Doeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee"})
    assert response.status_code == 400


def test_login_email_not_registered(clear, user_dict1):
    response = requests.post(f"{BASE_URL}/auth/login/v2",
                             json={'email': "not_registered@gmail.com", 'password': "password"})
    assert response.status_code == 400


def test_login_wrong_password(clear, user_dict1):
    response = requests.post(f"{BASE_URL}/auth/login/v2",
                             json={'email': user_dict1['email'], 'password': "password"})
    assert response.status_code == 400


def test_login_invalid_email():
    response = requests.post(f"{BASE_URL}/auth/login/v2",
                             json={'email': "first/last@gmail.com", 'password': "password"})
    assert response.status_code == 400
    response = requests.post(
        f"{BASE_URL}/auth/login/v2", json={'email': "first.com", 'password': "password"})
    assert response.status_code == 400


def test_register_login_works(clear):
    rego_response = requests.post(f"{BASE_URL}/auth/register/v2", json={'email': "third7678@gmail.com",
                                                                        'password': "hello123", 'name_first': "Trent", 'name_last': "Arnold"})
    assert rego_response.status_code == 200
    rego_res = json.loads(rego_response.text)
    login_response = requests.post(
        f"{BASE_URL}/auth/login/v2", json={'email': "third7678@gmail.com", 'password': "hello123"})
    login_res = json.loads(login_response.text)
    assert rego_res['auth_user_id'] == login_res['auth_user_id']
    assert rego_res['token'] != login_res['token']


def test_logout_token_invalid(clear, user_dict2):
    token = user_dict2['token']
    invalid_token = f"abc{token}123"
    response = requests.post(
        f"{BASE_URL}/auth/logout/v1", json={'token': invalid_token})
    assert response.status_code == 403


def test_logout_works_for_register(clear, user_dict2):
    requests.post(f"{BASE_URL}/auth/logout/v1",
                  json={'token': user_dict2['token']})
    response = requests.post(f"{BASE_URL}/channels/create/v2", json={
                             'token': user_dict2['token'], 'name': "channel", 'is_public': True})
    assert response.status_code == 403


def test_logout_works_for_login(clear, user_dict1):
    login_response = requests.post(f"{BASE_URL}/auth/login/v2", json={
                                   'email': user_dict1['email'], 'password': user_dict1['password']})
    token = json.loads(login_response.text)['token']
    requests.post(f"{BASE_URL}/auth/logout/v1", json={'token': token})
    create_response = requests.post(
        f"{BASE_URL}/channels/create/v2", json={'token': token, 'name': "channel", 'is_public': True})
    assert create_response.status_code == 403


def test_register_correct_handle(clear):
    user1_response = requests.post(f"{BASE_URL}/auth/register/v2", json={'email': "third7678@gmail.com",
                                                                         'password': "hello123", 'name_first': "Alexander", 'name_last': "Bartholemew"})
    user1_data = json.loads(user1_response.text)
    user1_token = user1_data['token']
    user1_id = user1_data['auth_user_id']
    user1_profile_response = requests.get(
        f"{BASE_URL}/user/profile/v1?token={user1_token}&u_id={user1_id}")
    assert user1_profile_response.status_code == 200
    user1_profile_data = json.loads(user1_profile_response.text)['user']
    assert user1_profile_data['handle_str'] == "alexanderbartholemew"

    user2_response = requests.post(f"{BASE_URL}/auth/register/v2", json={'email': "first@gmail.com",
                                                                         'password': "prisonfc", 'name_first': "Alexander", 'name_last': "Bartholemew"})
    user2_data = json.loads(user2_response.text)
    user2_token = user2_data['token']
    user2_id = user2_data['auth_user_id']
    user2_profile_response = requests.get(
        f"{BASE_URL}/user/profile/v1?token={user2_token}&u_id={user2_id}")
    assert user2_profile_response.status_code == 200
    user2_profile_data = json.loads(user2_profile_response.text)['user']
    assert user2_profile_data['handle_str'] == "alexanderbartholemew0"

    user3_response = requests.post(f"{BASE_URL}/auth/register/v2", json={'email': "second@gmail.com",
                                                                         'password': "prisonfc", 'name_first': "Alexander", 'name_last': "Bartholemew"})
    user3_data = json.loads(user3_response.text)
    user3_token = user3_data['token']
    user3_id = user3_data['auth_user_id']
    user3_profile_response = requests.get(
        f"{BASE_URL}/user/profile/v1?token={user3_token}&u_id={user3_id}")
    assert user3_profile_response.status_code == 200
    user3_profile_data = json.loads(user3_profile_response.text)['user']
    assert user3_profile_data['handle_str'] == "alexanderbartholemew1"


def test_register_handle_concatenation(clear):
    register_response = requests.post(f"{BASE_URL}/auth/register/v2", json={'email': "third7678@gmail.com",
                                                                            'password': "hello123", 'name_first': "Alex", 'name_last': "OxladeChamberlain"})
    assert register_response.status_code == 200
    user1_data = json.loads(register_response.text)
    user1_token = user1_data['token']
    user1_id = user1_data['auth_user_id']
    user1_profile_response = requests.get(
        f"{BASE_URL}/user/profile/v1?token={user1_token}&u_id={user1_id}")
    assert user1_profile_response.status_code == 200
    user1_profile_data = json.loads(user1_profile_response.text)['user']
    assert user1_profile_data['handle_str'] == "alexoxladechamberlai"


def test_reset_password_request_registered_email(clear, user_dict1):
    email = user_dict1['email']
    request_response = requests.post(
        f"{BASE_URL}/auth/passwordreset/request/v1", json={'email': email})
    assert request_response.status_code == 200


def test_reset_password_request_not_registered_email(clear, user_dict2):
    email = "notregistered@gmail.com"
    request_response = requests.post(
        f"{BASE_URL}/auth/passwordreset/request/v1", json={'email': email})
    assert request_response.status_code == 200


def test_reset_password_wrong_code(clear, user_dict2):
    reset_response = requests.post(f"{BASE_URL}/auth/passwordreset/reset/v1", json={
                                   'new_password': "newpassword", 'reset_code': 99999})
    assert reset_response.status_code == 400


def test_reset_password_too_short(clear):
    reset_response = requests.post(
        f"{BASE_URL}/auth/passwordreset/reset/v1", json={'new_password': "new", 'reset_code': 111111})
    assert reset_response.status_code == 400
