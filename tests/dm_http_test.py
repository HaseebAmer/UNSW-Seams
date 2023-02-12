import requests
import pytest
import json
from src import config

BASE_ADDRESS = 'http://127.0.0.1'
BASE_PORT = config.port
URL = f"{BASE_ADDRESS}:{BASE_PORT}"

OK = 200
ACCESSERROR = 403
INPUTERROR = 400


@pytest.fixture
def clear():
    requests.delete(f"{URL}/clear/v1")  # clear datastore


@pytest.fixture
def auth_user_1():
    auth_user_1 = {
        "email": "tomjerry@unsw.edu.au", "password": "tomandjerry", "name_first": "tom", "name_last": "jerry",
    }
    return auth_user_1


@pytest.fixture
def auth_user_2():
    auth_user_2 = {
        "email": "jimcook@unsw.edu.au", "password": "jimcooksfood", "name_first": "jim", "name_last": "cook",
    }
    return auth_user_2


@pytest.fixture
def auth_user_3():
    auth_user_3 = {
        "email": "peterpan@unsw.edu.au", "password": "peterhaspan", "name_first": "peter", "name_last": "pan",
    }
    return auth_user_3


@pytest.fixture
def u_id_1():
    auth_user_id_json = requests.post(f"{URL}/auth/register/v2", json={
        "email": "bill.nye@gmail.com", "password": "thescienceguy", "name_first": "Bill", "name_last": "Thescienceguy"
    })
    assert auth_user_id_json.status_code == OK
    return json.loads(auth_user_id_json.text)


@pytest.fixture
def u_id_2():
    u_id_json = requests.post(f"{URL}/auth/register/v2", json={
        'email': "roshan.m@gmail.com", 'password': "wowzers123", 'name_first': "Roshan", 'name_last': "Mujeeb"
    })
    assert u_id_json.status_code == OK
    return json.loads(u_id_json.text)


@pytest.fixture
def u_id_3():
    u_id_json = requests.post(f"{URL}/auth/register/v2", json={
        'email': "bambabalaklava@gmail.com", 'password': "rdjisironmAN12", 'name_first': "ghostface", 'name_last': "killah"
    })
    assert u_id_json.status_code == OK
    return json.loads(u_id_json.text)


'''================================================================================================================'''

# DM/CREATE/V1
# Test for access error when creating DM with invalid token


def test_invalid_token_dm_create_v1_http(clear):
    # register user
    register_user1 = requests.post(f"{URL}/auth/register/v2", json={"email": "user1@gmail.com",
                                                                    "password": "password",  "name_first": "name", "name_last": "surname"})
    assert register_user1.status_code == OK
    user1_token = register_user1.json()['token']
    invalid_token = user1_token + "12345"
    # user makes dm with invalid token, raising access error
    dm = requests.post(f"{URL}/dm/create/v1",
                       json={'token': invalid_token, 'u_ids': []})
    assert dm.status_code == ACCESSERROR
# Test for input error when u_ids contain invalid id


def test_invalid_u_id_dm_create_v1_http(clear):
    # register user
    register_user1 = requests.post(f"{URL}/auth/register/v2", json={"email": "user1@gmail.com",
                                                                    "password": "password",  "name_first": "name", "name_last": "surname"})
    assert register_user1.status_code == OK
    user1_token = register_user1.json()['token']
    # user makes dm with invalid token, raising access error
    dm = requests.post(f"{URL}/dm/create/v1",
                       json={'token': user1_token, 'u_ids': [69]})
    assert dm.status_code == INPUTERROR
# Test for input error when u_ids contain duplicate u_id


def test_duplicate_u_id_in_u_ids_dm_create_v1_http(clear):
    # register 2 users
    register_user1 = requests.post(f"{URL}/auth/register/v2", json={"email": "user1@gmail.com",
                                                                    "password": "password",  "name_first": "name", "name_last": "surname"})
    assert register_user1.status_code == OK
    user1_token = register_user1.json()['token']
    register_user2 = requests.post(f"{URL}/auth/register/v2", json={"email": "user2@gmail.com",
                                                                    "password": "password",  "name_first": "name", "name_last": "surname"})
    assert register_user2.status_code == OK
    user2_id = register_user2.json()['auth_user_id']
    # user 1 creates dm with user2 in it
    dm = requests.post(
        f"{URL}/dm/create/v1", json={'token': user1_token, 'u_ids': [user2_id, user2_id]})
    assert dm.status_code == INPUTERROR
# Test for input error when u_ids contains creator's u_id


def test_owner_u_id_in_u_ids_dm_create_v1_http(clear):
    # register user
    register_user1 = requests.post(f"{URL}/auth/register/v2", json={"email": "user1@gmail.com",
                                                                    "password": "password",  "name_first": "name", "name_last": "surname"})
    assert register_user1.status_code == OK
    user1_token = register_user1.json()['token']
    user1_id = register_user1.json()['auth_user_id']
    # user makes dm with invalid token, raising access error
    dm = requests.post(f"{URL}/dm/create/v1",
                       json={'token': user1_token, 'u_ids': [user1_id]})
    assert dm.status_code == INPUTERROR
# Normal function


def test_empty_dm_create_v1_http(clear):
    # register user
    register_user1 = requests.post(f"{URL}/auth/register/v2", json={"email": "user1@gmail.com",
                                                                    "password": "password",  "name_first": "name", "name_last": "surname"})
    assert register_user1.status_code == OK
    user1_token = register_user1.json()['token']
    # user makes dm with invalid token, raising access error
    dm = requests.post(f"{URL}/dm/create/v1",
                       json={'token': user1_token, 'u_ids': []})
    assert dm.status_code == OK


def test_non_empty_dm_create_v1_http(clear):
    # register user
    register_user1 = requests.post(f"{URL}/auth/register/v2", json={"email": "user1@gmail.com",
                                                                    "password": "password",  "name_first": "name", "name_last": "surname"})
    assert register_user1.status_code == OK
    user1_token = register_user1.json()['token']
    register_user2 = requests.post(f"{URL}/auth/register/v2", json={"email": "user2@gmail.com",
                                                                    "password": "password",  "name_first": "name", "name_last": "surname"})
    assert register_user2.status_code == OK
    user2_id = register_user2.json()['auth_user_id']
    # user makes dm with invalid token, raising access error
    dm = requests.post(f"{URL}/dm/create/v1",
                       json={'token': user1_token, 'u_ids': [user2_id]})
    assert dm.status_code == OK

# Test u_ids not a list


def test_u_id_not_a_list_dm_create_http(clear):
    # register user
    register_user1 = requests.post(f"{URL}/auth/register/v2", json={"email": "user1@gmail.com",
                                                                    "password": "password",  "name_first": "name", "name_last": "surname"})
    assert register_user1.status_code == OK
    user1_token = register_user1.json()['token']
    # user makes dm with invalid token, raising access error
    dm = requests.post(f"{URL}/dm/create/v1",
                       json={'token': user1_token, 'u_ids': 5})
    assert dm.status_code == INPUTERROR

# Test notifications for DM create
# def test_notifications_dm_create_http(clear):
#     # register 2 users
#     register_user1 = requests.post(f"{URL}/auth/register/v2", json = {"email": "user1@gmail.com", "password": "password",  "name_first": "name", "name_last": "surname"})
#     assert register_user1.status_code == OK
#     user1_token = register_user1.json()['token']
#     user1_id = register_user1.json()['auth_user_id']
#     register_user2 = requests.post(f"{URL}/auth/register/v2", json = {"email": "user2@gmail.com", "password": "password",  "name_first": "name", "name_last": "surname"})
#     assert register_user2.status_code == OK
#     user2_token = register_user2.json()['token']
#     user2_id = register_user2.json()['auth_user_id']
#     # assert notif of user2 to be empty
#     notifications = requests.get(f"{URL}/notifications/get/v1" + f"?token={user2_token}")
#     assert notifications.status_code == OK
#     assert len(notifications.json()['notifications']) == 0
#     # user1 slides into user2's dms
#     dm = requests.post(f"{URL}/dm/create/v1", json = {'token': user1_token, 'u_ids': [user2_id]})
#     assert dm.status_code == OK
#     dm_id = dm.json()['dm_id']
#     # assert notif of user2 to be {-1, dm_id, "{user_handle} added you to {dm_name}"}
#     user_profile = requests.get(f"{URL}/user/profile/v1"+f"?token={user1_token}&u_id={user1_id}")
#     assert user_profile.status_code == OK
#     user_handle = user_profile.json()['handle_str']
#     dm_details = requests.get(f"{URL}/dm/details/v1"+f"?token={user1_token}&dm_id={dm_id}")
#     dm_details.status_code == OK
#     dm_name = dm_details.json()['name']
#     notifications1 = requests.get(f"{URL}/notifications/get/v1" + f"?token={user2_token}")
#     assert notifications1.status_code == OK
#     assert len(notifications1.json()['notifications']) == 1
#     assert notifications1.json()['notifications'][0] == {'channel_id': -1, 'dm_id': 1, 'notification_message': f"{user_handle} added you to {dm_name}"}

    '''================================================================================================================'''


# DM/LIST/V1 TESTS
# test invalid token in dm/list/v1
def test_invalid_token_dm_list_v1_http(clear):
    # register user
    register_user1 = requests.post(f"{URL}/auth/register/v2", json={"email": "user1@gmail.com",
                                                                    "password": "password",  "name_first": "name", "name_last": "surname"})
    assert register_user1.status_code == OK
    user1_token = register_user1.json()['token']
    invalid_token = user1_token + "121212"
    # create a dm with invalid token and return access error
    dm_create = requests.post(
        f"{URL}/dm/create/v1", json={'token': user1_token, 'u_ids': []})
    assert dm_create.status_code == OK
    dm_list = requests.get(f"{URL}/dm/list/v1"+f"?token={invalid_token}")
    dm_list.status_code == ACCESSERROR
# test normal functionality


def test_dm_list_v1_http(clear):
    # register 3 users
    register_user1 = requests.post(f"{URL}/auth/register/v2", json={"email": "user1@gmail.com",
                                                                    "password": "password",  "name_first": "name", "name_last": "surname"})
    assert register_user1.status_code == OK
    user1_token = register_user1.json()['token']
    register_user2 = requests.post(f"{URL}/auth/register/v2", json={"email": "user2@gmail.com",
                                                                    "password": "password",  "name_first": "name", "name_last": "surname"})
    assert register_user2.status_code == OK
    user2_id = register_user2.json()['auth_user_id']
    user2_token = register_user2.json()['token']
    register_user3 = requests.post(f"{URL}/auth/register/v2", json={"email": "user3@gmail.com",
                                                                    "password": "password",  "name_first": "name", "name_last": "surname"})
    assert register_user3.status_code == OK
    user3_id = register_user3.json()['auth_user_id']
    dm_list = requests.get(f"{URL}/dm/list/v1"+f"?token={user1_token}")
    assert dm_list.status_code == OK
    assert len(dm_list.json()['dms']) == 0
    # user 1 creates dm with user 2
    dm_create1 = requests.post(
        f"{URL}/dm/create/v1", json={'token': user1_token, 'u_ids': [user2_id]})
    assert dm_create1.status_code == OK
    dm_list0 = requests.get(f"{URL}/dm/list/v1"+f"?token={user1_token}")
    assert dm_list0.status_code == OK
    assert len(dm_list0.json()['dms']) == 1
    assert dm_list0.json()['dms'][0]['dm_id'] == 1
    # user 1 creates dm with user 3
    dm_create2 = requests.post(
        f"{URL}/dm/create/v1", json={'token': user1_token, 'u_ids': [user3_id]})
    assert dm_create2.status_code == OK
    # list user1's dms
    dm_list1 = requests.get(f"{URL}/dm/list/v1"+f"?token={user1_token}")
    assert dm_list1.status_code == OK
    assert len(dm_list1.json()['dms']) == 2

    dm_list2 = requests.get(f"{URL}/dm/list/v1" + f"?token={user2_token}")
    assert dm_list2.status_code == OK
    assert len(dm_list2.json()['dms']) == 1


'''================================================================================================================'''

# DM/REMOVE/V1 TEST
# test for invalid dm_id INPUTERROR in dm_remove


def test_invalid_dm_id_dm_remove_v1_http(clear):
    # register user
    register_user1 = requests.post(f"{URL}/auth/register/v2", json={"email": "user1@gmail.com",
                                                                    "password": "password",  "name_first": "name", "name_last": "surname"})
    assert register_user1.status_code == OK
    user1_token = register_user1.json()['token']
    # user creates dm
    dm_create = requests.post(
        f"{URL}/dm/create/v1", json={'token': user1_token, 'u_ids': []})
    assert dm_create.status_code == OK
    dm_id = dm_create.json()['dm_id']
    invalid_dm_id = dm_id + 69
    # user removes dm with invalid dm_id raising input error
    dm_remove = requests.delete(
        f"{URL}/dm/remove/v1", json={'token': user1_token, 'dm_id': invalid_dm_id})
    assert dm_remove.status_code == INPUTERROR
# test for invalid token ACCESSERROR in dm_remove


def test_invalid_token_dm_remove_v1_http(clear):
    # register user
    register_user1 = requests.post(f"{URL}/auth/register/v2", json={"email": "user1@gmail.com",
                                                                    "password": "password",  "name_first": "name", "name_last": "surname"})
    assert register_user1.status_code == OK
    user1_token = register_user1.json()['token']
    invalid_token = user1_token + "kekw"
    # user creates dm
    dm_create = requests.post(
        f"{URL}/dm/create/v1", json={'token': user1_token, 'u_ids': []})
    assert dm_create.status_code == OK
    dm_id = dm_create.json()['dm_id']
    # user removes dm with invalid token raising access error
    dm_remove = requests.delete(
        f"{URL}/dm/remove/v1", json={'token': invalid_token, 'dm_id': dm_id})
    assert dm_remove.status_code == ACCESSERROR
# test for token not belonging to owner ACCESSERROR dm_remove


def test_token_does_not_belong_to_creator_dm_remove_v1_http(clear):
    # register 2 users
    register_user1 = requests.post(f"{URL}/auth/register/v2", json={"email": "user1@gmail.com",
                                                                    "password": "password",  "name_first": "name", "name_last": "surname"})
    assert register_user1.status_code == OK
    user1_token = register_user1.json()['token']
    register_user2 = requests.post(f"{URL}/auth/register/v2", json={"email": "user2@gmail.com",
                                                                    "password": "password",  "name_first": "name", "name_last": "surname"})
    assert register_user2.status_code == OK
    user2_id = register_user2.json()['auth_user_id']
    user2_token = register_user2.json()['token']
    # user1 creates dm with user2
    dm_create = requests.post(
        f"{URL}/dm/create/v1", json={'token': user1_token, 'u_ids': [user2_id]})
    assert dm_create.status_code == OK
    dm_id = dm_create.json()['dm_id']
    # user2 removes dm, raising access error
    dm_remove = requests.delete(
        f"{URL}/dm/remove/v1", json={'token': user2_token, 'dm_id': dm_id})
    assert dm_remove.status_code == ACCESSERROR

# test for token of creator that left the dm ACCESSERROR dm_remove


def test_token_of_creator_that_left_dm_remove_v1_http(clear):
    # register 2 users
    register_user1 = requests.post(f"{URL}/auth/register/v2", json={"email": "user1@gmail.com",
                                                                    "password": "password",  "name_first": "name", "name_last": "surname"})
    assert register_user1.status_code == OK
    user1_token = register_user1.json()['token']
    register_user2 = requests.post(f"{URL}/auth/register/v2", json={"email": "user2@gmail.com",
                                                                    "password": "password",  "name_first": "name", "name_last": "surname"})
    assert register_user2.status_code == OK
    user2_id = register_user2.json()['auth_user_id']
    # user 1 creates dm and invites user 2
    dm_create = requests.post(
        f"{URL}/dm/create/v1", json={'token': user1_token, 'u_ids': [user2_id]})
    assert dm_create.status_code == OK
    dm_id = dm_create.json()['dm_id']
    # user 1 leaves dm
    dm_leave = requests.post(f"{URL}/dm/leave/v1",
                             json={'token': user1_token, 'dm_id': dm_id})
    assert dm_leave.status_code == OK
    # user 1 removes dm, resulting in access error
    dm_remove = requests.delete(
        f"{URL}/dm/remove/v1", json={'token': user1_token, 'dm_id': dm_id})
    assert dm_remove.status_code == ACCESSERROR


# test for normal functioning dm_remove
def test_dm_remove_v1_http(clear):
    # register 2 user
    register_user1 = requests.post(f"{URL}/auth/register/v2", json={"email": "user1@gmail.com",
                                                                    "password": "password",  "name_first": "name", "name_last": "surname"})
    assert register_user1.status_code == OK
    user1_token = register_user1.json()['token']
    register_user2 = requests.post(f"{URL}/auth/register/v2", json={"email": "user2@gmail.com",
                                                                    "password": "password",  "name_first": "name", "name_last": "surname"})
    assert register_user2.status_code == OK
    user2_id = register_user2.json()['auth_user_id']
    user2_token = register_user2.json()['token']
    # user1 creates dm with user2
    dm_create2 = requests.post(
        f"{URL}/dm/create/v1", json={'token': user1_token, 'u_ids': [user2_id]})
    assert dm_create2.status_code == OK
    dm_id2 = dm_create2.json()['dm_id']
    dm_list0 = requests.get(f"{URL}/dm/list/v1"+f"?token={user2_token}")
    assert dm_list0.status_code == OK
    assert len(dm_list0.json()['dms']) == 1
    # user1 removes dm
    dm_remove = requests.delete(
        f"{URL}/dm/remove/v1", json={'token': user1_token, 'dm_id': dm_id2})
    assert dm_remove.status_code == OK
    # dm_list user2 length is 0
    dm_list = requests.get(f"{URL}/dm/list/v1"+f"?token={user2_token}")
    assert dm_list.status_code == OK
    assert len(dm_list.json()['dms']) == 0
    dm_list2 = requests.get(f"{URL}/dm/list/v1"+f"?token={user1_token}")
    assert dm_list2.status_code == OK
    len(dm_list.json()['dms']) == 0

# DM REMOVE test removing user not in dm!


def test_remove_user_not_in_dm_dm_remove_http(clear):
    # Register 2 users
    register_user1 = requests.post(f"{URL}/auth/register/v2", json={"email": "user1@gmail.com",
                                                                    "password": "password",  "name_first": "name", "name_last": "surname"})
    assert register_user1.status_code == OK
    user1_token = register_user1.json()['token']
    register_user2 = requests.post(f"{URL}/auth/register/v2", json={"email": "user2@gmail.com",
                                                                    "password": "password",  "name_first": "name", "name_last": "surname"})
    assert register_user2.status_code == OK
    user2_token = register_user2.json()['token']
    # user1 creates dm with no one
    dm_create = requests.post(
        f"{URL}/dm/create/v1", json={'token': user1_token, 'u_ids': []})
    assert dm_create.status_code == OK
    dm_id = dm_create.json()['dm_id']
    # user1 tries to remove user2, raising access error
    dm_remove = requests.delete(
        f"{URL}/dm/remove/v1", json={'token': user2_token, 'dm_id': dm_id})
    assert dm_remove.status_code == ACCESSERROR

# DM REMOVE test removing 2nd dm created and seeing how many dms exist with dm list


def test_remove_2nd_dm_dm_remove_http(clear):
    # Register 2 users
    register_user1 = requests.post(f"{URL}/auth/register/v2", json={"email": "user1@gmail.com",
                                                                    "password": "password",  "name_first": "name", "name_last": "surname"})
    assert register_user1.status_code == OK
    user1_token = register_user1.json()['token']
    register_user2 = requests.post(f"{URL}/auth/register/v2", json={"email": "user2@gmail.com",
                                                                    "password": "password",  "name_first": "name", "name_last": "surname"})
    assert register_user2.status_code == OK
    user2_id = register_user2.json()['auth_user_id']
    # User 1 creates dm with no one
    dm_create = requests.post(
        f"{URL}/dm/create/v1", json={'token': user1_token, 'u_ids': []})
    assert dm_create.status_code == OK
    # user1 creates dm with user 2
    dm_create = requests.post(
        f"{URL}/dm/create/v1", json={'token': user1_token, 'u_ids': [user2_id]})
    assert dm_create.status_code == OK
    dm_id = dm_create.json()['dm_id']
    # user 1 deletes dm with user 2
    dm_remove = requests.delete(
        f"{URL}/dm/remove/v1", json={'token': user1_token, 'dm_id': dm_id})
    assert dm_remove.status_code == OK
    # dm list on user1 to assert there is 1 dm
    dm_list = requests.get(f"{URL}/dm/list/v1"+f"?token={user1_token}")
    assert dm_list.status_code == OK
    assert len(dm_list.json()['dms']) == 1


'''================================================================================================================================'''

# DM MESSAGES


def test_dm_messages_v1_dm_id_invalid(clear, u_id_1):
    dm_dict = requests.post(f"{URL}/dm/create/v1", json={
        'token': u_id_1['token'], 'u_ids': []
    })
    assert dm_dict.status_code == OK
    data = requests.get(
        f"{URL}/dm/messages/v1?token={u_id_1['token']}&dm_id=-1&start=0")
    assert data.status_code == 400


def test_dm_messages_v1_invalid_start(clear, u_id_1):
    dm_dict = requests.post(f"{URL}/dm/create/v1", json={
        'token': u_id_1['token'], 'u_ids': []
    })
    assert dm_dict.status_code == OK
    dm_id = dm_dict.json()['dm_id']
    data = requests.get(
        f"{URL}/dm/messages/v1?token={u_id_1['token']}&dm_id={dm_id}&start=1")
    assert data.status_code == 400


def test_dm_messages_v1_invalid_start_not_empty(clear, u_id_1):
    dm_dict = requests.post(f"{URL}/dm/create/v1", json={
        'token': u_id_1['token'], 'u_ids': []
    })
    assert dm_dict.status_code == OK
    dm_id = dm_dict.json()['dm_id']
    for i in range(5):
        msg_send = requests.post(f"{URL}/message/senddm/v1", json={
            'token': u_id_1['token'], 'dm_id': dm_id, 'message': f"{i}sizzurpinmycup!!"
        })
        assert msg_send.status_code == OK
    data = requests.get(
        f"{URL}/dm/messages/v1?token={u_id_1['token']}&dm_id={dm_id}&start=5")
    assert data.status_code == 400


def test_dm_messages_v1_invalid_token(clear, u_id_1):
    dm_dict = requests.post(f"{URL}/dm/create/v1", json={
        'token': u_id_1['token'], 'u_ids': []
    })
    assert dm_dict.status_code == OK
    dm_id = dm_dict.json()['dm_id']
    data = requests.get(f"{URL}/dm/messages/v1?token=-1&dm_id={dm_id}&start=0")
    assert data.status_code == 403


def test_dm_messages_v1_user_notindm(clear, u_id_1, u_id_2):
    dm_dict = requests.post(f"{URL}/dm/create/v1", json={
        'token': u_id_1['token'], 'u_ids': []
    })
    assert dm_dict.status_code == OK
    dm_id = dm_dict.json()['dm_id']
    data = requests.get(
        f"{URL}/dm/messages/v1?token={u_id_2['token']}&dm_id={dm_id}&start=0")
    assert data.status_code == 403


def test_dm_messages_v1_comprehensive(clear, u_id_1, u_id_2, u_id_3):
    dm_dict = requests.post(f"{URL}/dm/create/v1", json={
        'token': u_id_1['token'], 'u_ids': []
    })
    assert dm_dict.status_code == OK
    dm_id = dm_dict.json()['dm_id']
    msg_send = requests.post(f"{URL}/message/senddm/v1", json={
        'token': u_id_1['token'], 'dm_id': dm_id, 'message': "sizzurpinmycup!!"
    })
    assert msg_send.status_code == OK
    message_id = msg_send.json()['message_id']
    data = requests.get(
        f"{URL}/dm/messages/v1?token={u_id_1['token']}&dm_id={dm_id}&start=0")
    assert data.status_code == OK
    data_msgs = data.json()['messages']
    assert data_msgs[0]['message'] == "sizzurpinmycup!!"
    edit_request = requests.put(f"{URL}/message/edit/v1", json={
        'token': u_id_1['token'], 'message_id': message_id, 'message': "HILLARYBEN"
    })
    assert edit_request.status_code == OK
    data = requests.get(
        f"{URL}/dm/messages/v1?token={u_id_1['token']}&dm_id={dm_id}&start=0")
    assert data.status_code == OK
    data_msgs = data.json()['messages']
    assert data_msgs[0]['message'] == "HILLARYBEN"
    edit_request = requests.put(f"{URL}/message/edit/v1", json={
        'token': u_id_1['token'], 'message_id': message_id, 'message': ""
    })
    assert edit_request.status_code == OK
    data = requests.get(
        f"{URL}/dm/messages/v1?token={u_id_1['token']}&dm_id={dm_id}&start=0")
    assert data.status_code == OK
    data_msgs = data.json()
    assert data_msgs == {'messages': [], 'start': 0, 'end': -1}

    for i in range(100):
        msg_send = requests.post(f"{URL}/message/senddm/v1", json={
            'token': u_id_1['token'], 'dm_id': dm_id, 'message': f"message {i}"
        })
        assert msg_send.status_code == OK

    data = requests.get(
        f"{URL}/dm/messages/v1?token={u_id_1['token']}&dm_id={dm_id}&start=0")
    assert data.status_code == OK
    data_msgs = data.json()
    assert data_msgs['start'] == 0
    assert data_msgs['end'] == 50
    assert len(data_msgs['messages']) == 50
    assert data_msgs['messages'][0]['message'] == "message 99"

    for i in range(100):
        msg_send = requests.post(f"{URL}/message/senddm/v1", json={
            'token': u_id_1['token'], 'dm_id': dm_id, 'message': f"heya {i}"
        })
        message_id = msg_send.json()['message_id']
        assert msg_send.status_code == OK
        msg_delete = requests.delete(f"{URL}/message/remove/v1", json={
            'token': u_id_1['token'], 'message_id': message_id
        })
        assert msg_delete.status_code == OK

    data = requests.get(
        f"{URL}/dm/messages/v1?token={u_id_1['token']}&dm_id={dm_id}&start=50")
    assert data.status_code == OK
    data_msgs = data.json()
    assert data_msgs['start'] == 50
    assert data_msgs['end'] == -1
    assert len(data_msgs['messages']) == 50
    assert data_msgs['messages'][0]['message'] == "message 49"


'''================================================================================================================================'''

# DM DETAILS


def test_dm_details_invalid_DM(auth_user_1, auth_user_2):
    requests.delete(f"{URL}/clear/v1")
    register_user_1 = requests.post(
        f"{URL}/auth/register/v2", json=auth_user_1)
    assert register_user_1.status_code == OK
    register_user_1_return = json.loads(register_user_1.text)
    token_user_1 = register_user_1_return['token']
    register_user_1_return['auth_user_id']

    register_user_2 = requests.post(
        f"{URL}/auth/register/v2", json=auth_user_2)
    assert register_user_2.status_code == OK
    register_user_2_return = json.loads(register_user_2.text)
    register_user_2_return['token']
    id_user_2 = register_user_2_return['auth_user_id']

    dm_create = requests.post(
        f"{URL}/dm/create/v1", json={'token': token_user_1, 'u_ids': [id_user_2]})

    assert dm_create.status_code == OK
    dm_id = json.loads(dm_create.text)['dm_id']

    invalid_dm_id = dm_id + 10

    dm_details = requests.get(
        f"{URL}/dm/details/v1" + f"?token={token_user_1}&dm_id={invalid_dm_id}")

    assert dm_details.status_code == 400


def test_dm_details_invalid_member(auth_user_1, auth_user_2):
    requests.delete(f"{URL}/clear/v1")
    register_user_1 = requests.post(
        f"{URL}/auth/register/v2", json=auth_user_1)
    assert register_user_1.status_code == OK
    register_user_1_return = json.loads(register_user_1.text)
    token_user_1 = register_user_1_return['token']
    register_user_1_return['auth_user_id']

    register_user_2 = requests.post(
        f"{URL}/auth/register/v2", json=auth_user_2)
    assert register_user_2.status_code == OK
    register_user_2_return = json.loads(register_user_2.text)
    token_user_2 = register_user_2_return['token']
    register_user_2_return['auth_user_id']

    u_ids = []

    dm_create = requests.post(
        f"{URL}/dm/create/v1", json={'token': token_user_1, 'u_ids': u_ids})
    assert dm_create.status_code == OK
    dm_id = json.loads(dm_create.text)['dm_id']

    dm_details = requests.get(
        f"{URL}/dm/details/v1" + f"?token={token_user_2}&dm_id={dm_id}")
    assert dm_details.status_code == 403


def test_dm_details_invalid_token(auth_user_1, auth_user_2):
    requests.delete(f"{URL}/clear/v1")
    register_user_1 = requests.post(
        f"{URL}/auth/register/v2", json=auth_user_1)
    assert register_user_1.status_code == OK
    register_user_1_return = json.loads(register_user_1.text)
    token_user_1 = register_user_1_return['token']
    register_user_1_return['auth_user_id']

    register_user_2 = requests.post(
        f"{URL}/auth/register/v2", json=auth_user_2)
    assert register_user_2.status_code == OK
    register_user_2_return = json.loads(register_user_2.text)
    register_user_2_return['token']
    id_user_2 = register_user_2_return['auth_user_id']

    invalid_token = f"{token_user_1}2725"

    dm_create = requests.post(
        f"{URL}/dm/create/v1", json={'token': token_user_1, 'u_ids': [id_user_2]})
    assert dm_create.status_code == OK
    dm_id = json.loads(dm_create.text)['dm_id']

    dm_details = requests.get(
        f"{URL}/dm/details/v1" + f"?token={invalid_token}&dm_id={dm_id}")
    assert dm_details.status_code == 403


def test_dm_details_invalid_token_and_invalid_id(auth_user_1, auth_user_2):

    requests.delete(f"{URL}/clear/v1")
    register_user_1 = requests.post(
        f"{URL}/auth/register/v2", json=auth_user_1)
    assert register_user_1.status_code == OK
    register_user_1_return = json.loads(register_user_1.text)
    token_user_1 = register_user_1_return['token']
    register_user_1_return['auth_user_id']

    register_user_2 = requests.post(
        f"{URL}/auth/register/v2", json=auth_user_2)
    assert register_user_2.status_code == OK
    register_user_2_return = json.loads(register_user_2.text)
    register_user_2_return['token']
    id_user_2 = register_user_2_return['auth_user_id']

    invalid_token = f"{token_user_1}2725"

    dm_create = requests.post(
        f"{URL}/dm/create/v1", json={'token': token_user_1, 'u_ids': [id_user_2]})
    assert dm_create.status_code == OK
    dm_id = json.loads(dm_create.text)['dm_id']
    invalid_dm_id = dm_id + 10

    dm_details = requests.get(
        f"{URL}/dm/details/v1" + f"?token={invalid_token}&dm_id={invalid_dm_id}")
    assert dm_details.status_code == 403


def test_dm_details_basic_functionality_owner(auth_user_1, auth_user_2):
    requests.delete(f"{URL}/clear/v1")
    register_user_1 = requests.post(
        f"{URL}/auth/register/v2", json=auth_user_1)
    assert register_user_1.status_code == OK
    register_user_1_return = json.loads(register_user_1.text)
    token_user_1 = register_user_1_return['token']
    register_user_1_return['auth_user_id']

    register_user_2 = requests.post(
        f"{URL}/auth/register/v2", json=auth_user_2)
    assert register_user_2.status_code == OK
    register_user_2_return = json.loads(register_user_2.text)
    register_user_2_return['token']
    id_user_2 = register_user_2_return['auth_user_id']

    dm_create = requests.post(
        f"{URL}/dm/create/v1", json={'token': token_user_1, 'u_ids': [id_user_2]})
    assert dm_create.status_code == OK
    dm_id = json.loads(dm_create.text)['dm_id']

    dm_details = requests.get(
        f"{URL}/dm/details/v1" + f"?token={token_user_1}&dm_id={dm_id}")

    assert dm_details.status_code == OK

    dm_return = dm_details.json()

    return_name = dm_return["name"]
    return_members = dm_return["members"]

    assert return_members[0]['name_first'] == 'tom'
    assert return_members[1]['name_first'] == 'jim'

    assert return_name == 'jimcook, tomjerry'


def test_dm_details_basic_functionality_joiner(auth_user_1, auth_user_2):
    requests.delete(f"{URL}/clear/v1")
    register_user_1 = requests.post(
        f"{URL}/auth/register/v2", json=auth_user_1)
    assert register_user_1.status_code == OK
    register_user_1_return = json.loads(register_user_1.text)
    token_user_1 = register_user_1_return['token']
    register_user_1_return['auth_user_id']

    register_user_2 = requests.post(
        f"{URL}/auth/register/v2", json=auth_user_2)
    assert register_user_2.status_code == OK
    register_user_2_return = json.loads(register_user_2.text)
    token_user_2 = register_user_2_return['token']
    id_user_2 = register_user_2_return['auth_user_id']

    dm_create = requests.post(
        f"{URL}/dm/create/v1", json={'token': token_user_1, 'u_ids': [id_user_2]})
    assert dm_create.status_code == OK
    dm_id = json.loads(dm_create.text)['dm_id']

    dm_details = requests.get(
        f"{URL}/dm/details/v1" + f"?token={token_user_2}&dm_id={dm_id}")

    assert dm_details.status_code == OK

    dm_return = dm_details.json()

    return_name = dm_return["name"]
    return_members = dm_return["members"]

    assert return_members[0]['name_first'] == 'tom'
    assert return_members[1]['name_first'] == 'jim'

    assert return_name == 'jimcook, tomjerry'


def test_dm_details_multiple_dms(auth_user_1, auth_user_2, auth_user_3):

    requests.delete(f"{URL}/clear/v1")
    register_user_1 = requests.post(
        f"{URL}/auth/register/v2", json=auth_user_1)
    assert register_user_1.status_code == OK
    register_user_1_return = json.loads(register_user_1.text)
    token_user_1 = register_user_1_return['token']
    register_user_1_return['auth_user_id']

    register_user_2 = requests.post(
        f"{URL}/auth/register/v2", json=auth_user_2)
    assert register_user_2.status_code == OK
    register_user_2_return = json.loads(register_user_2.text)
    token_user_2 = register_user_2_return['token']
    id_user_2 = register_user_2_return['auth_user_id']

    register_user_3 = requests.post(
        f"{URL}/auth/register/v2", json=auth_user_3)
    assert register_user_3.status_code == OK
    register_user_3_return = json.loads(register_user_3.text)
    register_user_2_return['token']
    id_user_3 = register_user_3_return['auth_user_id']

    dm_create = requests.post(
        f"{URL}/dm/create/v1", json={'token': token_user_1, 'u_ids': [id_user_2, id_user_3]})
    assert dm_create.status_code == OK
    dm_id_1 = json.loads(dm_create.text)['dm_id']

    dm_create_2 = requests.post(
        f"{URL}/dm/create/v1", json={'token': token_user_1, 'u_ids': [id_user_2, id_user_3]})
    assert dm_create_2.status_code == OK
    json.loads(dm_create_2.text)['dm_id']

    dm_details = requests.get(
        f"{URL}/dm/details/v1" + f"?token={token_user_2}&dm_id={dm_id_1}")

    assert dm_details.status_code == OK

    dm_return = dm_details.json()

    return_members = dm_return["members"]
    return_name = dm_return["name"]

    assert return_name == 'jimcook, peterpan, tomjerry'

    assert return_members[0]['name_first'] == 'tom'
    assert return_members[1]['name_first'] == 'jim'
    assert return_members[2]['name_first'] == 'peter'


'''================================================================================================================'''

# DM LEAVE


def test_dm_leave_owner_leaves_DM(auth_user_1, auth_user_2):
    requests.delete(f"{URL}/clear/v1")

    # register user 1
    register_user_1 = requests.post(
        f"{URL}/auth/register/v2", json=auth_user_1)
    assert register_user_1.status_code == OK
    register_user_1_return = json.loads(register_user_1.text)
    token_user_1 = register_user_1_return['token']
    register_user_1_return['auth_user_id']

    # register user 2
    register_user_2 = requests.post(
        f"{URL}/auth/register/v2", json=auth_user_2)
    assert register_user_2.status_code == OK
    register_user_2_return = json.loads(register_user_2.text)
    token_user_2 = register_user_2_return['token']
    id_user_2 = register_user_2_return['auth_user_id']

    # User 1 creates a DM with User 2
    dm_create = requests.post(
        f"{URL}/dm/create/v1", json={'token': token_user_1, 'u_ids': [id_user_2]})
    assert dm_create.status_code == OK
    dm_id = json.loads(dm_create.text)['dm_id']

    # OWNER leaves the DM
    dm_leave = requests.post(f"{URL}/dm/leave/v1",
                             json={'token': token_user_1, 'dm_id': dm_id})

    assert dm_leave.status_code == OK

    # User 2 should still be in the DM as a member.
    dm_details = requests.get(
        f"{URL}/dm/details/v1" + f"?token={token_user_2}&dm_id={dm_id}")

    assert dm_details.status_code == OK

    dm_return = dm_details.json()

    return_members = dm_return["members"]
    return_name = dm_return["name"]

    assert return_name == 'jimcook, tomjerry'

    assert return_members[0]['name_first'] == 'jim'


def test_dm_leave_joiner_leaves_DM(auth_user_1, auth_user_2):
    requests.delete(f"{URL}/clear/v1")

    # register user 1
    register_user_1 = requests.post(
        f"{URL}/auth/register/v2", json=auth_user_1)
    assert register_user_1.status_code == OK
    register_user_1_return = json.loads(register_user_1.text)
    token_user_1 = register_user_1_return['token']
    register_user_1_return['auth_user_id']

    # register user 2
    register_user_2 = requests.post(
        f"{URL}/auth/register/v2", json=auth_user_2)
    assert register_user_2.status_code == OK
    register_user_2_return = json.loads(register_user_2.text)
    token_user_2 = register_user_2_return['token']
    id_user_2 = register_user_2_return['auth_user_id']

    # User 1 creates a DM with User 2
    dm_create = requests.post(
        f"{URL}/dm/create/v1", json={'token': token_user_1, 'u_ids': [id_user_2]})
    assert dm_create.status_code == OK
    dm_id = json.loads(dm_create.text)['dm_id']

    # USER 2 leaves the DM
    dm_leave = requests.post(f"{URL}/dm/leave/v1",
                             json={'token': token_user_2, 'dm_id': dm_id})

    assert dm_leave.status_code == OK

    # User 1 should still be in the DM as the only member
    dm_details = requests.get(
        f"{URL}/dm/details/v1" + f"?token={token_user_1}&dm_id={dm_id}")

    assert dm_details.status_code == OK

    dm_return = dm_details.json()

    return_members = dm_return["members"]
    return_name = dm_return["name"]

    # when a user leaves a channel the name should not change.
    assert return_name == 'jimcook, tomjerry'
    assert return_members[0]['name_first'] == 'tom'


def test_dm_leave_invalid_dm_id(auth_user_1, auth_user_2):

    requests.delete(f"{URL}/clear/v1")
    # register user 1
    register_user_1 = requests.post(
        f"{URL}/auth/register/v2", json=auth_user_1)
    assert register_user_1.status_code == OK
    register_user_1_return = json.loads(register_user_1.text)
    token_user_1 = register_user_1_return['token']
    register_user_1_return['auth_user_id']

    register_user_2 = requests.post(
        f"{URL}/auth/register/v2", json=auth_user_2)
    assert register_user_2.status_code == OK
    register_user_2_return = json.loads(register_user_2.text)
    token_user_2 = register_user_2_return['token']
    id_user_2 = register_user_2_return['auth_user_id']

    dm_create = requests.post(
        f"{URL}/dm/create/v1", json={'token': token_user_1, 'u_ids': [id_user_2]})
    assert dm_create.status_code == OK
    dm_id = json.loads(dm_create.text)['dm_id']

    invalid_dm_id = dm_id + 100

    dm_leave = requests.post(
        f"{URL}/dm/leave/v1", json={'token': token_user_2, 'dm_id': invalid_dm_id})

    assert dm_leave.status_code == 400


def test_dm_leave_invalid_token_id(auth_user_1, auth_user_2):
    requests.delete(f"{URL}/clear/v1")

    # register user 1
    register_user_1 = requests.post(
        f"{URL}/auth/register/v2", json=auth_user_1)
    assert register_user_1.status_code == OK
    register_user_1_return = json.loads(register_user_1.text)
    token_user_1 = register_user_1_return['token']
    register_user_1_return['auth_user_id']

    register_user_2 = requests.post(
        f"{URL}/auth/register/v2", json=auth_user_2)
    assert register_user_2.status_code == OK
    register_user_2_return = json.loads(register_user_2.text)
    register_user_2_return['token']
    id_user_2 = register_user_2_return['auth_user_id']

    dm_create = requests.post(
        f"{URL}/dm/create/v1", json={'token': token_user_1, 'u_ids': [id_user_2]})
    assert dm_create.status_code == OK
    dm_id = json.loads(dm_create.text)['dm_id']

    invalid_token_id = token_user_1 + "121212"

    dm_leave = requests.post(
        f"{URL}/dm/leave/v1", json={'token': invalid_token_id, 'dm_id': dm_id})

    assert dm_leave.status_code == 403


def test_dm_leave_valid_dm_user_is_not_in_dm(auth_user_1, auth_user_2, auth_user_3):
    requests.delete(f"{URL}/clear/v1")

    # register user 1
    register_user_1 = requests.post(
        f"{URL}/auth/register/v2", json=auth_user_1)
    assert register_user_1.status_code == OK
    register_user_1_return = json.loads(register_user_1.text)
    token_user_1 = register_user_1_return['token']
    register_user_1_return['auth_user_id']

    register_user_2 = requests.post(
        f"{URL}/auth/register/v2", json=auth_user_2)
    assert register_user_2.status_code == OK
    register_user_2_return = json.loads(register_user_2.text)
    register_user_2_return['token']
    id_user_2 = register_user_2_return['auth_user_id']

    register_user_3 = requests.post(
        f"{URL}/auth/register/v2", json=auth_user_3)
    assert register_user_3.status_code == OK
    register_user_3_return = json.loads(register_user_3.text)
    token_user_3 = register_user_3_return['token']

    dm_create = requests.post(
        f"{URL}/dm/create/v1", json={'token': token_user_1, 'u_ids': [id_user_2]})
    assert dm_create.status_code == OK
    dm_id = json.loads(dm_create.text)['dm_id']

    dm_leave = requests.post(f"{URL}/dm/leave/v1",
                             json={'token': token_user_3, 'dm_id': dm_id})

    assert dm_leave.status_code == 403
