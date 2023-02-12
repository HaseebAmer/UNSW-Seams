import requests
import pytest
import json
from src.error import AccessError
from src import config


BASE_ADDRESS = 'http://127.0.0.1'
BASE_PORT = config.port
URL = f"{BASE_ADDRESS}:{BASE_PORT}"
OK = 200
ACCESSERROR = 403
INPUTERROR = 400


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


# ADMIN USER PERMISSION CHANGE
def test_admin_user_permission_working(auth_user_1, auth_user_2, auth_user_3):

    requests.delete(f"{URL}/clear/v1")
    requests.post(f"{URL}/auth/register/v2", json=auth_user_1)
    login_user_1 = requests.post(f"{URL}/auth/login/v2", json=auth_user_1)
    login_user_1_return = json.loads(login_user_1.text)
    token_user_1 = login_user_1_return['token']

    requests.post(f"{URL}/auth/register/v2", json=auth_user_2)
    login_user_2 = requests.post(f"{URL}/auth/login/v2", json=auth_user_2)
    login_user_2_return = json.loads(login_user_2.text)
    token_user_2 = login_user_2_return['token']
    id_user_2 = login_user_2_return['auth_user_id']

    requests.post(f"{URL}/auth/register/v2", json=auth_user_3)
    login_user_3 = requests.post(f"{URL}/auth/login/v2", json=auth_user_3)
    login_user_3_return = json.loads(login_user_3.text)
    id_user_3 = login_user_3_return['auth_user_id']
    login_user_3_return['token']

    channel_1 = requests.post(
        f"{URL}/channels/create/v2", json={"token": token_user_1, "name": "Aus", "is_public": False})
    assert channel_1.status_code == OK

    channel_1_id = json.loads(channel_1.text)['channel_id']

    user_2_becomes_global = requests.post(f"{URL}/admin/userpermission/change/v1", json={
                                          'token': token_user_1, 'u_id': id_user_2, 'permission_id': 1})
    assert user_2_becomes_global.status_code == OK

    user_2_joins_priv_channel = requests.post(
        f"{URL}/channel/join/v2", json={"token": token_user_2, "channel_id": channel_1_id})
    assert user_2_joins_priv_channel.status_code == OK

    user_3_member_of_channel_1 = requests.post(f"{URL}/channel/invite/v2", json={
                                               "token": token_user_2, "channel_id": channel_1_id, 'u_id': id_user_3})
    assert user_3_member_of_channel_1.status_code == OK

    user_2_adds_user_3 = requests.post(f"{URL}/channel/addowner/v1", json={
                                       "token": token_user_2, 'channel_id': channel_1_id, 'u_id': id_user_3})
    assert user_2_adds_user_3.status_code == OK

    user_2_gets_demoted = requests.post(f"{URL}/admin/userpermission/change/v1", json={
                                        'token': token_user_1, 'u_id': id_user_2, 'permission_id': 2})

    assert user_2_gets_demoted.status_code == OK

    user_2_removes_user_3 = requests.post(f"{URL}/channel/removeowner/v1", json={
                                          "token": token_user_2, 'channel_id': channel_1_id, 'u_id': id_user_3})

    assert user_2_removes_user_3.status_code == 403


def test_admin_user_permission_invalid_u_id(auth_user_1):
    requests.delete(f"{URL}/clear/v1")
    requests.post(f"{URL}/auth/register/v2", json=auth_user_1)
    login_user_1 = requests.post(f"{URL}/auth/login/v2", json=auth_user_1)
    login_user_1_return = json.loads(login_user_1.text)
    token_user_1 = login_user_1_return['token']
    id_user_1 = login_user_1_return['auth_user_id']
    invalid_id_user_1 = id_user_1 + 10
    invalid_user_becomes_global = requests.post(f"{URL}/admin/userpermission/change/v1", json={
                                                'token': token_user_1, 'u_id': invalid_id_user_1, 'permission_id': 1})
    assert invalid_user_becomes_global.status_code == 400


def test_admin_user_permission_only_global_owner_demotes_to_user(auth_user_1):

    requests.delete(f"{URL}/clear/v1")
    requests.post(f"{URL}/auth/register/v2", json=auth_user_1)
    login_user_1 = requests.post(f"{URL}/auth/login/v2", json=auth_user_1)
    login_user_1_return = json.loads(login_user_1.text)
    token_user_1 = login_user_1_return['token']
    id_user_1 = login_user_1_return['auth_user_id']
    one_global_demotes_himself = requests.post(f"{URL}/admin/userpermission/change/v1", json={
                                               'token': token_user_1, 'u_id': id_user_1, 'permission_id': 2})
    assert one_global_demotes_himself.status_code == 400


def test_admin_user_permission_invalid_permission_id(auth_user_1, auth_user_2):
    requests.delete(f"{URL}/clear/v1")
    requests.post(f"{URL}/auth/register/v2", json=auth_user_1)
    login_user_1 = requests.post(f"{URL}/auth/login/v2", json=auth_user_1)
    login_user_1_return = json.loads(login_user_1.text)
    token_user_1 = login_user_1_return['token']

    requests.post(f"{URL}/auth/register/v2", json=auth_user_2)
    login_user_2 = requests.post(f"{URL}/auth/login/v2", json=auth_user_2)
    login_user_2_return = json.loads(login_user_2.text)
    login_user_2_return['token']
    id_user_2 = login_user_2_return['auth_user_id']

    invalid_permission_id = requests.post(f"{URL}/admin/userpermission/change/v1", json={
                                          'token': token_user_1, 'u_id': id_user_2, 'permission_id': -5})

    assert invalid_permission_id.status_code == 400


def test_admin_user_permission_invalid_token_id(auth_user_1, auth_user_2):
    requests.delete(f"{URL}/clear/v1")
    requests.post(f"{URL}/auth/register/v2", json=auth_user_1)
    login_user_1 = requests.post(f"{URL}/auth/login/v2", json=auth_user_1)
    login_user_1_return = json.loads(login_user_1.text)
    token_user_1 = login_user_1_return['token']

    requests.post(f"{URL}/auth/register/v2", json=auth_user_2)
    login_user_2 = requests.post(f"{URL}/auth/login/v2", json=auth_user_2)
    login_user_2_return = json.loads(login_user_2.text)
    login_user_2_return['token']
    id_user_2 = login_user_2_return['auth_user_id']

    invalid_token = f"{token_user_1}2725"

    invalid_permission_id = requests.post(f"{URL}/admin/userpermission/change/v1", json={
                                          'token': invalid_token, 'u_id': id_user_2, 'permission_id': 1})

    assert invalid_permission_id.status_code == 403


def test_admin_user_permission_non_global_already_has_permission_id(auth_user_1, auth_user_2):

    requests.delete(f"{URL}/clear/v1")
    requests.post(f"{URL}/auth/register/v2", json=auth_user_1)
    login_user_1 = requests.post(f"{URL}/auth/login/v2", json=auth_user_1)
    login_user_1_return = json.loads(login_user_1.text)
    token_user_1 = login_user_1_return['token']

    requests.post(f"{URL}/auth/register/v2", json=auth_user_2)
    login_user_2 = requests.post(f"{URL}/auth/login/v2", json=auth_user_2)
    login_user_2_return = json.loads(login_user_2.text)
    id_user_2 = login_user_2_return['auth_user_id']

    same_permission_id = requests.post(f"{URL}/admin/userpermission/change/v1", json={
                                       'token': token_user_1, 'u_id': id_user_2, 'permission_id': 2})

    assert same_permission_id.status_code == 400


def test_admin_user_permission_global_already_has_permission_id(auth_user_1):
    requests.delete(f"{URL}/clear/v1")
    requests.post(f"{URL}/auth/register/v2", json=auth_user_1)
    login_user_1 = requests.post(f"{URL}/auth/login/v2", json=auth_user_1)
    login_user_1_return = json.loads(login_user_1.text)
    token_user_1 = login_user_1_return['token']
    id_user_1 = login_user_1_return['auth_user_id']
    one_global_demotes_himself = requests.post(f"{URL}/admin/userpermission/change/v1", json={
                                               'token': token_user_1, 'u_id': id_user_1, 'permission_id': 1})
    assert one_global_demotes_himself.status_code == 400


def test_admin_user_permission_authorised_user_not_global(auth_user_1, auth_user_2):
    requests.delete(f"{URL}/clear/v1")
    requests.post(f"{URL}/auth/register/v2", json=auth_user_1)
    login_user_1 = requests.post(f"{URL}/auth/login/v2", json=auth_user_1)
    login_user_1_return = json.loads(login_user_1.text)
    login_user_1_return['token']
    id_user_1 = login_user_1_return['auth_user_id']

    requests.post(f"{URL}/auth/register/v2", json=auth_user_2)
    login_user_2 = requests.post(f"{URL}/auth/login/v2", json=auth_user_2)
    login_user_2_return = json.loads(login_user_2.text)
    login_user_2_return['auth_user_id']
    token_user_2 = login_user_2_return['token']

    same_permission_id = requests.post(f"{URL}/admin/userpermission/change/v1", json={
                                       'token': token_user_2, 'u_id': id_user_1, 'permission_id': 2})

    assert same_permission_id.status_code == 403

# # InputError when any of:
# #        1. u_id does not refer to a valid user
# #        2.u_id refers to a user who is the only global owner and they are being demoted to a user
# #        3.permission_id is invalid
# #        4. the user already has the permissions level of permission_id

# #       AccessError when:

# #         the authorised user is not a global owner


def test_admin_user_permission_perms_removed_in_all_channels(auth_user_1, auth_user_2, auth_user_3):
    requests.delete(f"{URL}/clear/v1")
    requests.post(f"{URL}/auth/register/v2", json=auth_user_1)
    login_user_1 = requests.post(f"{URL}/auth/login/v2", json=auth_user_1)
    login_user_1_return = json.loads(login_user_1.text)
    token_user_1 = login_user_1_return['token']
    login_user_1_return['auth_user_id']

    requests.post(f"{URL}/auth/register/v2", json=auth_user_2)
    login_user_2 = requests.post(f"{URL}/auth/login/v2", json=auth_user_2)
    login_user_2_return = json.loads(login_user_2.text)
    token_user_2 = login_user_2_return['token']
    id_user_2 = login_user_2_return['auth_user_id']

    requests.post(f"{URL}/auth/register/v2", json=auth_user_3)
    login_user_3 = requests.post(f"{URL}/auth/login/v2", json=auth_user_3)
    login_user_3_return = json.loads(login_user_3.text)
    id_user_3 = login_user_3_return['auth_user_id']
    token_user_3 = login_user_3_return['token']

    channel_1 = requests.post(
        f"{URL}/channels/create/v2", json={"token": token_user_1, "name": "Aus", "is_public": True})
    assert channel_1.status_code == OK
    channel_1_id = json.loads(channel_1.text)['channel_id']

    channel_2 = requests.post(
        f"{URL}/channels/create/v2", json={"token": token_user_3, "name": "Hello", "is_public": True})
    assert channel_2.status_code == OK
    channel_2_id = json.loads(channel_2.text)['channel_id']

    user_2_becomes_global = requests.post(f"{URL}/admin/userpermission/change/v1", json={
                                          'token': token_user_1, 'u_id': id_user_2, 'permission_id': 1})
    assert user_2_becomes_global.status_code == OK

    user_2_joins_channel_1 = requests.post(
        f"{URL}/channel/join/v2", json={"token": token_user_2, "channel_id": channel_1_id})
    assert user_2_joins_channel_1.status_code == OK

    user_3_joins_channel_1 = requests.post(
        f"{URL}/channel/join/v2", json={"token": token_user_3, "channel_id": channel_1_id})
    assert user_3_joins_channel_1.status_code == OK

    user_2_joins_channel_2 = requests.post(
        f"{URL}/channel/join/v2", json={"token": token_user_2, "channel_id": channel_2_id})
    assert user_2_joins_channel_2.status_code == OK

    user_1_joins__channel_2 = requests.post(
        f"{URL}/channel/join/v2", json={"token": token_user_1, "channel_id": channel_2_id})
    assert user_1_joins__channel_2.status_code == OK

    user_2_demotes = requests.post(f"{URL}/admin/userpermission/change/v1", json={
                                   'token': token_user_1, 'u_id': id_user_2, 'permission_id': 2})
    assert user_2_demotes.status_code == OK

    user_2_removes_user_3 = requests.post(f"{URL}/channel/removeowner/v1", json={
                                          "token": token_user_2, 'channel_id': channel_1_id, 'u_id': id_user_3})
    assert user_2_removes_user_3.status_code == 403

    user_2_removes_user_1 = requests.post(f"{URL}/channel/removeowner/v1", json={
                                          "token": token_user_2, 'channel_id': channel_2_id, 'u_id': id_user_3})
    assert user_2_removes_user_1.status_code == 403

# ^^^
# c1: Ou1, u2,u3.
# c2:  Ou3, u1, u2


# u2 loses his perms

# u2 remove u3 outt of c1...error
# u2 remove u1 out of c2...error


# TESTS FOR ADMIN/USER/REMOVE

def test_admin_user_remove_working_test(auth_user_1, auth_user_2):

    requests.delete(f"{URL}/clear/v1")
    requests.post(f"{URL}/auth/register/v2", json=auth_user_1)
    login_user_1 = requests.post(f"{URL}/auth/login/v2", json=auth_user_1)
    login_user_1_return = json.loads(login_user_1.text)
    token_user_1 = login_user_1_return['token']
    login_user_1_return['auth_user_id']

    requests.post(f"{URL}/auth/register/v2", json=auth_user_2)
    login_user_2 = requests.post(f"{URL}/auth/login/v2", json=auth_user_2)
    login_user_2_return = json.loads(login_user_2.text)
    token_user_2 = login_user_2_return['token']
    id_user_2 = login_user_2_return['auth_user_id']

    channel_1 = requests.post(
        f"{URL}/channels/create/v2", json={"token": token_user_1, "name": "Aus", "is_public": True})
    assert channel_1.status_code == OK
    channel_1_id = json.loads(channel_1.text)['channel_id']

    user_2_member_of_channel_1 = requests.post(f"{URL}/channel/invite/v2", json={
                                               "token": token_user_1, "channel_id": channel_1_id, 'u_id': id_user_2})
    assert user_2_member_of_channel_1.status_code == OK

    remove_user_2_from_seams = requests.delete(
        f"{URL}/admin/user/remove/v1", json={'token': token_user_1, 'u_id': id_user_2})

    assert remove_user_2_from_seams.status_code == OK

    # try removing user 2 from channel 1. should raise an error

    channel_leave = requests.post(
        f"{URL}/channel/leave/v1", json={'token': token_user_2, 'channel_id': channel_1_id})

    assert channel_leave.status_code == 403


# basic test.
# GU1 promotes GU2. GU2 removes GU1 from seams.

# user is not global.

def test_admin_user_remove_invalid_token_id(auth_user_1, auth_user_2):

    requests.delete(f"{URL}/clear/v1")
    requests.post(f"{URL}/auth/register/v2", json=auth_user_1)
    login_user_1 = requests.post(f"{URL}/auth/login/v2", json=auth_user_1)
    login_user_1_return = json.loads(login_user_1.text)
    token_user_1 = login_user_1_return['token']
    login_user_1_return['auth_user_id']

    invalid_token_id = f"{token_user_1}2725"

    requests.post(f"{URL}/auth/register/v2", json=auth_user_2)
    login_user_2 = requests.post(f"{URL}/auth/login/v2", json=auth_user_2)
    login_user_2_return = json.loads(login_user_2.text)
    login_user_2_return['token']
    id_user_2 = login_user_2_return['auth_user_id']

    remove_user_2_from_seams = requests.delete(
        f"{URL}/admin/user/remove/v1", json={'token': invalid_token_id, 'u_id': id_user_2})
    assert remove_user_2_from_seams.status_code == 403


def test_admin_user_remove_invalid_user_id(auth_user_1, auth_user_2):

    requests.delete(f"{URL}/clear/v1")
    requests.post(f"{URL}/auth/register/v2", json=auth_user_1)
    login_user_1 = requests.post(f"{URL}/auth/login/v2", json=auth_user_1)
    login_user_1_return = json.loads(login_user_1.text)
    token_user_1 = login_user_1_return['token']
    id_user_1 = login_user_1_return['auth_user_id']

    invalid_user_id = id_user_1 + 50

    requests.post(f"{URL}/auth/register/v2", json=auth_user_2)
    login_user_2 = requests.post(f"{URL}/auth/login/v2", json=auth_user_2)
    login_user_2_return = json.loads(login_user_2.text)
    login_user_2_return['token']
    login_user_2_return['auth_user_id']

    remove_user_2_from_seams = requests.delete(
        f"{URL}/admin/user/remove/v1", json={'token': token_user_1, 'u_id': invalid_user_id})
    assert remove_user_2_from_seams.status_code == 400


def test_admin_user_remove_not_a_global_owner(auth_user_1, auth_user_2):

    requests.delete(f"{URL}/clear/v1")
    requests.post(f"{URL}/auth/register/v2", json=auth_user_1)
    login_user_1 = requests.post(f"{URL}/auth/login/v2", json=auth_user_1)
    login_user_1_return = json.loads(login_user_1.text)
    login_user_1_return['token']
    id_user_1 = login_user_1_return['auth_user_id']

    requests.post(f"{URL}/auth/register/v2", json=auth_user_2)
    login_user_2 = requests.post(f"{URL}/auth/login/v2", json=auth_user_2)
    login_user_2_return = json.loads(login_user_2.text)
    token_user_2 = login_user_2_return['token']
    login_user_2_return['auth_user_id']

    remove_user_1_from_seams = requests.delete(
        f"{URL}/admin/user/remove/v1", json={'token': token_user_2, 'u_id': id_user_1})
    assert remove_user_1_from_seams.status_code == 403


def test_admin_user_remove_only_global_owner_removes_himself(auth_user_1):

    requests.delete(f"{URL}/clear/v1")
    requests.post(f"{URL}/auth/register/v2", json=auth_user_1)
    login_user_1 = requests.post(f"{URL}/auth/login/v2", json=auth_user_1)
    login_user_1_return = json.loads(login_user_1.text)
    token_user_1 = login_user_1_return['token']
    id_user_1 = login_user_1_return['auth_user_id']
    one_global_removes_himself = requests.delete(
        f"{URL}/admin/user/remove/v1", json={'token': token_user_1, 'u_id': id_user_1})
    assert one_global_removes_himself.status_code == 400

# make a test for channel
# make a test for DM


# create c1: u1 u2
# create c2: u1 u2

# remove u2 from seams
#assert c1(u1) and c2(u1) messages#

def test_admin_user_remove_messages_check(auth_user_1, auth_user_2, auth_user_3):
    requests.delete(f"{URL}/clear/v1")
    requests.post(f"{URL}/auth/register/v2", json=auth_user_1)
    login_user_1 = requests.post(f"{URL}/auth/login/v2", json=auth_user_1)
    login_user_1_return = json.loads(login_user_1.text)
    token_user_1 = login_user_1_return['token']
    login_user_1_return['auth_user_id']

    requests.post(f"{URL}/auth/register/v2", json=auth_user_2)
    login_user_2 = requests.post(f"{URL}/auth/login/v2", json=auth_user_2)
    login_user_2_return = json.loads(login_user_2.text)
    token_user_2 = login_user_2_return['token']
    id_user_2 = login_user_2_return['auth_user_id']

    requests.post(f"{URL}/auth/register/v2", json=auth_user_3)
    login_user_3 = requests.post(f"{URL}/auth/login/v2", json=auth_user_3)
    login_user_3_return = json.loads(login_user_3.text)
    login_user_3_return['auth_user_id']
    token_user_3 = login_user_3_return['token']

    channel_1 = requests.post(
        f"{URL}/channels/create/v2", json={"token": token_user_1, "name": "Aus", "is_public": True})
    assert channel_1.status_code == OK
    channel_1_id = json.loads(channel_1.text)['channel_id']

    channel_2 = requests.post(
        f"{URL}/channels/create/v2", json={"token": token_user_3, "name": "Hello", "is_public": True})
    assert channel_2.status_code == OK
    channel_2_id = json.loads(channel_2.text)['channel_id']

    user_2_joins_channel_1 = requests.post(
        f"{URL}/channel/join/v2", json={"token": token_user_2, "channel_id": channel_1_id})
    assert user_2_joins_channel_1.status_code == OK

    user_3_joins_channel_1 = requests.post(
        f"{URL}/channel/join/v2", json={"token": token_user_3, "channel_id": channel_1_id})
    assert user_3_joins_channel_1.status_code == OK

    user_2_joins_channel_2 = requests.post(
        f"{URL}/channel/join/v2", json={"token": token_user_2, "channel_id": channel_2_id})
    assert user_2_joins_channel_2.status_code == OK

    user_1_joins__channel_2 = requests.post(
        f"{URL}/channel/join/v2", json={"token": token_user_1, "channel_id": channel_2_id})
    assert user_1_joins__channel_2.status_code == OK

    # user 2 sends a message in channel 2

    user_2_sends_msg_channel_2 = requests.post(f"{URL}/message/send/v1", json={
        'token': token_user_2, 'channel_id': channel_2_id, 'message': "hey"
    })

    user_2_sends_msg_channel_2 = requests.post(f"{URL}/message/send/v1", json={
        'token': token_user_2, 'channel_id': channel_2_id, 'message': "HELLO"
    })

    assert user_2_sends_msg_channel_2.status_code == OK

    user_1_remove_user_2 = requests.delete(
        f"{URL}/admin/user/remove/v1", json={'token': token_user_1, 'u_id': id_user_2})
    assert user_1_remove_user_2.status_code == OK

    channel_details = requests.get(
        f"{URL}/channel/details/v2" + f"?token={token_user_1}&channel_id={channel_2_id}")

    assert channel_details.status_code == OK
    assert len(channel_details.json()['all_members']) == 2
    assert channel_details.json()['all_members'][0]['name_first'] == 'peter'
    assert channel_details.json()['all_members'][1]['name_first'] == 'tom'

    channel_details_2 = requests.get(
        f"{URL}/channel/details/v2" + f"?token={token_user_1}&channel_id={channel_1_id}")

    assert channel_details_2.status_code == OK
    assert len(channel_details_2.json()['all_members']) == 2
    assert channel_details.json()['all_members'][0]['name_first'] == 'peter'
    assert channel_details.json()['all_members'][1]['name_first'] == 'tom'

    message_list_json = requests.get(
        f"{URL}/channel/messages/v2?token={token_user_1}&channel_id={channel_2_id}&start=0")

    assert message_list_json.status_code == OK
    message_dict = json.loads(message_list_json.text)

    assert message_dict['messages'][0]['message'] == 'Removed user'
    assert message_dict['messages'][0]['message_id'] == 1
    assert message_dict['messages'][1]['message'] == 'Removed user'
    assert message_dict['messages'][1]['message_id'] == 0
    assert message_dict['messages'][0]['u_id'] == 2
    assert message_dict['messages'][1]['u_id'] == 2

    profile_response = requests.get(
        f"{URL}/user/profile/v1?token={token_user_1}&u_id={id_user_2}")
    assert profile_response.status_code == 200
    # profile_data = json.loads(profile_response.text)
    # assert profile_data['name_first'] == "Removed"
    # assert profile_data['name_last'] == "user"


def test_admin_user_remove_dm_check(auth_user_1, auth_user_2, auth_user_3):
    requests.delete(f"{URL}/clear/v1")
    requests.post(f"{URL}/auth/register/v2", json=auth_user_1)
    login_user_1 = requests.post(f"{URL}/auth/login/v2", json=auth_user_1)
    login_user_1_return = json.loads(login_user_1.text)
    token_user_1 = login_user_1_return['token']
    id_user_1 = login_user_1_return['auth_user_id']

    requests.post(f"{URL}/auth/register/v2", json=auth_user_2)
    login_user_2 = requests.post(f"{URL}/auth/login/v2", json=auth_user_2)
    login_user_2_return = json.loads(login_user_2.text)
    token_user_2 = login_user_2_return['token']
    id_user_2 = login_user_2_return['auth_user_id']

    requests.post(f"{URL}/auth/register/v2", json=auth_user_3)
    login_user_3 = requests.post(f"{URL}/auth/login/v2", json=auth_user_3)
    login_user_3_return = json.loads(login_user_3.text)
    id_user_3 = login_user_3_return['auth_user_id']
    login_user_3_return['token']

    dm_1 = requests.post(
        f"{URL}/dm/create/v1", json={"token": token_user_1, "u_ids": [id_user_2, id_user_3]})
    assert dm_1.status_code == OK
    dm_1_id = json.loads(dm_1.text)['dm_id']

    dm_2 = requests.post(
        f"{URL}/dm/create/v1", json={"token": token_user_2, "u_ids": [id_user_1, id_user_3]})
    assert dm_2.status_code == OK
    dm_2_id = json.loads(dm_2.text)['dm_id']

    # user 2 sends a message in channel 2

    user_2_sends_msg_dm_2 = requests.post(f"{URL}/message/senddm/v1", json={
        'token': token_user_2, 'dm_id': dm_2_id, 'message': "hey"
    })

    user_2_sends_msg_dm_2 = requests.post(f"{URL}/message/senddm/v1", json={
        'token': token_user_2, 'dm_id': dm_2_id, 'message': "HELLO"
    })

    assert user_2_sends_msg_dm_2.status_code == OK

    user_1_remove_user_2 = requests.delete(
        f"{URL}/admin/user/remove/v1", json={'token': token_user_1, 'u_id': id_user_2})
    assert user_1_remove_user_2.status_code == OK

    dm_details = requests.get(
        f"{URL}/dm/details/v1" + f"?token={token_user_1}&dm_id={dm_1_id}")

    assert dm_details.status_code == OK
    assert len(dm_details.json()['members']) == 2
    assert dm_details.json()['members'][0]['name_first'] == 'tom'
    assert dm_details.json()['members'][1]['name_first'] == 'peter'
    assert dm_details.json()['name'] == 'jimcook, peterpan, tomjerry'

    # message_list_json = requests.get(
    #     f"{URL}/dm/messages/v1?token={token_user_1}&dm_id={dm_2_id}&start=0")

    # assert message_list_json.status_code == OK
    # message_dict = json.loads(message_list_json.text)

    # assert message_dict['messages'][0] == {'message': 'Removed user'}
    # assert message_dict['messages'][1] == {'message': 'Removed user'}

    # profile_response = requests.get(
    #     f"{URL}/user/profile/v1?token={token_user_1}&u_id={id_user_2}")
    # assert profile_response.status_code == 200
    # profile_data = json.loads(profile_response.text)
    # assert profile_data['name_first'] == "Removed"
    # assert profile_data['name_last'] == "user"
    # assert profile_data['email'] == "jimcook@unsw.edu.au"
    # assert profile_data['handle_str'] == "jimcook"
