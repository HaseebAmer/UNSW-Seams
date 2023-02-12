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
def clear():
    requests.delete(f"{URL}/clear/v1")  # clear datastore


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


# CHANNEL/LEAVE/V1
# test function for channel leave v1 member leaving channel [PASSES]
def test_user_joins_then_leaves_channel_leave_v1_http(clear):
    # register users
    register_ahri = requests.post(f"{URL}/auth/register/v2", json={"email": "ahri@gmail.com",
                                                                   "password": "password",  "name_first": "ahri", "name_last": "mage"})
    assert register_ahri.status_code == OK

    register_amumu = requests.post(f"{URL}/auth/register/v2", json={"email": "amumu@gmail.com",
                                                                    "password": "password",  "name_first": "amumu", "name_last": "sadge"})
    assert register_amumu.status_code == OK

    # login users
    login_ahri = requests.post(
        f"{URL}/auth/login/v2", json={"email": "ahri@gmail.com", "password": "password"})
    assert login_ahri.status_code == OK
    ahri_return = login_ahri.json()
    ahri_token = ahri_return['token']

    login_amumu = requests.post(
        f"{URL}/auth/login/v2", json={"email": "amumu@gmail.com", "password": "password"})
    assert login_amumu.status_code == OK
    amumu_return = login_amumu.json()
    amumu_token = amumu_return['token']
    amumu_id = amumu_return['auth_user_id']

    # user creates a channel
    channel_info = requests.post(
        f"{URL}/channels/create/v2", json={"token": ahri_token, "name": "midlane", "is_public": True})
    assert channel_info.status_code == OK
    channel_id = channel_info.json()['channel_id']

    # user invites member to channel
    channel_invite = requests.post(f"{URL}/channel/invite/v2", json={
                                   "token": ahri_token, "channel_id": channel_id, "u_id": amumu_id})
    assert channel_invite.status_code == OK

    # member leaves channel
    channel_leave = requests.post(
        f"{URL}/channel/leave/v1", json={'token': amumu_token, 'channel_id': channel_id})
    assert channel_leave.status_code == OK

    # check if channel_leave works using channel_details
    channel_details = requests.get(
        f"{URL}/channel/details/v2" + f"?token={ahri_token}&channel_id={channel_id}")
    assert channel_details.status_code == OK
    assert len(channel_details.json()['all_members']) == 1
    assert channel_details.json()['all_members'][0]['name_first'] == 'ahri'

# test channel leave v1 for owner leaving their own channel [PASSES]


def test_owner_leaves_channel_channel_leave_v1_http(clear):
    # register users
    register_asol = requests.post(f"{URL}/auth/register/v2", json={"email": "asol@gmail.com",
                                                                   "password": "password",  "name_first": "aurelion", "name_last": "mage"})
    assert register_asol.status_code == OK

    register_ahri = requests.post(f"{URL}/auth/register/v2", json={"email": "ahri@gmail.com",
                                                                   "password": "password",  "name_first": "ahri", "name_last": "mage"})
    assert register_ahri.status_code == OK

    register_amumu = requests.post(f"{URL}/auth/register/v2", json={"email": "amumu@gmail.com",
                                                                    "password": "password",  "name_first": "amumu", "name_last": "sadge"})
    assert register_amumu.status_code == OK

    # login users
    login_ahri = requests.post(
        f"{URL}/auth/login/v2", json={"email": "ahri@gmail.com", "password": "password"})
    assert login_ahri.status_code == OK
    ahri_return = login_ahri.json()
    ahri_token = ahri_return['token']

    login_amumu = requests.post(
        f"{URL}/auth/login/v2", json={"email": "amumu@gmail.com", "password": "password"})
    assert login_amumu.status_code == OK
    amumu_return = login_amumu.json()
    amumu_token = amumu_return['token']
    amumu_id = amumu_return['auth_user_id']

    # user creates a channel
    channel_info = requests.post(
        f"{URL}/channels/create/v2", json={"token": ahri_token, "name": "midlane", "is_public": True})
    assert channel_info.status_code == OK
    channel_id = channel_info.json()['channel_id']

    # user invites member to channel
    channel_invite = requests.post(f"{URL}/channel/invite/v2", json={
                                   "token": ahri_token, "channel_id": channel_id, "u_id": amumu_id})
    assert channel_invite.status_code == OK

    # member leaves channel
    channel_leave = requests.post(
        f"{URL}/channel/leave/v1", json={'token': ahri_token, 'channel_id': channel_id})
    assert channel_leave.status_code == OK

    # check if channel_leave works using channel_details
    channel_details = requests.get(
        f"{URL}/channel/details/v2" + f"?token={amumu_token}&channel_id={channel_id}")
    assert channel_details.status_code == OK
    assert len(channel_details.json()['all_members']) == 1
    assert len(channel_details.json()['owner_members']) == 0

# # test for input error for invalid channel id for channel_leave_v1 [PASSES]


def test_invalid_channel_id_channel_leave_v1_http(clear):
    # register users
    register_ahri = requests.post(f"{URL}/auth/register/v2", json={"email": "ahri@gmail.com",
                                                                   "password": "password",  "name_first": "ahri", "name_last": "mage"})
    assert register_ahri.status_code == OK

    register_amumu = requests.post(f"{URL}/auth/register/v2", json={"email": "amumu@gmail.com",
                                                                    "password": "password",  "name_first": "amumu", "name_last": "sadge"})
    assert register_amumu.status_code == OK

    # login users
    login_ahri = requests.post(
        f"{URL}/auth/login/v2", json={"email": "ahri@gmail.com", "password": "password"})
    assert login_ahri.status_code == OK
    ahri_return = login_ahri.json()
    ahri_token = ahri_return['token']

    login_amumu = requests.post(
        f"{URL}/auth/login/v2", json={"email": "amumu@gmail.com", "password": "password"})
    assert login_amumu.status_code == OK
    amumu_return = login_amumu.json()
    amumu_token = amumu_return['token']
    amumu_id = amumu_return['auth_user_id']

    # user creates a channel
    channel_info = requests.post(
        f"{URL}/channels/create/v2", json={"token": ahri_token, "name": "midlane", "is_public": True})
    assert channel_info.status_code == OK
    channel_id = channel_info.json()['channel_id']
    channel_id_invalid = channel_id + 70 - 1
    # user invites member to channel
    channel_invite = requests.post(f"{URL}/channel/invite/v2", json={
                                   "token": ahri_token, "channel_id": channel_id, "u_id": amumu_id})
    assert channel_invite.status_code == OK

    # member leaves channel
    channel_leave = requests.post(
        f"{URL}/channel/leave/v1", json={'token': amumu_token, 'channel_id': channel_id_invalid})
    assert channel_leave.status_code == INPUTERROR

# test for access error for user leaving channel they are not in for channel/leave/v2 [PASSES]


def test_wrong_channel_id_channel_leave_v1_http(clear):
    # register users
    register_ahri = requests.post(f"{URL}/auth/register/v2", json={"email": "ahri@gmail.com",
                                                                   "password": "password",  "name_first": "ahri", "name_last": "mage"})
    assert register_ahri.status_code == OK

    register_amumu = requests.post(f"{URL}/auth/register/v2", json={"email": "amumu@gmail.com",
                                                                    "password": "password",  "name_first": "amumu", "name_last": "sadge"})
    assert register_amumu.status_code == OK

    # login users
    login_ahri = requests.post(
        f"{URL}/auth/login/v2", json={"email": "ahri@gmail.com", "password": "password"})
    assert login_ahri.status_code == OK
    ahri_return = login_ahri.json()
    ahri_token = ahri_return['token']

    login_amumu = requests.post(
        f"{URL}/auth/login/v2", json={"email": "amumu@gmail.com", "password": "password"})
    assert login_amumu.status_code == OK
    amumu_return = login_amumu.json()
    amumu_token = amumu_return['token']

    # user creates a channel
    channel_info = requests.post(
        f"{URL}/channels/create/v2", json={"token": ahri_token, "name": "midlane", "is_public": True})
    assert channel_info.status_code == OK
    channel_id = channel_info.json()['channel_id']

    # member leaves channel
    channel_leave = requests.post(
        f"{URL}/channel/leave/v1", json={'token': amumu_token, 'channel_id': channel_id})
    assert channel_leave.status_code == ACCESSERROR

# test invalid token input in channel_leave_v1 [PASSES]


def test_invalid_token_channel_leave_v1(clear):
    # register users
    register_ahri = requests.post(f"{URL}/auth/register/v2", json={"email": "ahri@gmail.com",
                                                                   "password": "password",  "name_first": "ahri", "name_last": "mage"})
    assert register_ahri.status_code == OK

    # login users
    login_ahri = requests.post(
        f"{URL}/auth/login/v2", json={"email": "ahri@gmail.com", "password": "password"})
    assert login_ahri.status_code == OK
    ahri_return = login_ahri.json()
    ahri_token = ahri_return['token']

    # user creates a channel
    channel_info = requests.post(
        f"{URL}/channels/create/v2", json={"token": ahri_token, "name": "midlane", "is_public": True})
    assert channel_info.status_code == OK
    channel_id = channel_info.json()['channel_id']
    invalid_token = ahri_token + "lol"

    # member leaves channel
    channel_leave = requests.post(
        f"{URL}/channel/leave/v1", json={'token': invalid_token, 'channel_id': channel_id})
    assert channel_leave.status_code == ACCESSERROR


def test_invite_correct(clear, u_id_1, u_id_2):
    auth_user_id_dict = u_id_1
    u_id_dict = u_id_2

    channel_id_req = requests.post(f"{URL}/channels/create/v2", json={
        'token': auth_user_id_dict['token'], 'name': 'happytreefriends', 'is_public': True
    })
    assert channel_id_req.status_code == OK
    channel_id = json.loads(channel_id_req.text)['channel_id']

    resp = requests.post(f"{URL}/channel/invite/v2", json={
        'token': auth_user_id_dict['token'], 'channel_id': channel_id, 'u_id': u_id_dict['auth_user_id']
    })
    assert resp.status_code == OK
    # get the users in channel
    channel_request = requests.get(
        f"{URL}/channels/list/v2" + f"?token={u_id_dict['token']}")
    assert channel_request.status_code == OK
    channel_list = json.loads(channel_request.text)
    assert channel_list['channels'] == [
        {'channel_id': channel_id, 'name': 'happytreefriends'}]


def test_invite_invalid_channel_id(clear, u_id_1, u_id_2):
    auth_user_id_dict = u_id_1
    u_id_dict = u_id_2

    channel_id_req = requests.post(f"{URL}/channels/create/v2", json={
        'token': auth_user_id_dict['token'], 'name': 'happytreefriends', 'is_public': True
    })
    assert channel_id_req.status_code == OK
    resp = requests.post(f"{URL}/channel/invite/v2", json={
        'token': auth_user_id_dict['token'], 'channel_id': 5, 'u_id': u_id_dict['auth_user_id']
    })
    assert resp.status_code == 400


def test_invite_invalid_u_id(clear, u_id_1):
    auth_user_id_dict = u_id_1
    channel_id_req = requests.post(f"{URL}/channels/create/v2", json={
        'token': auth_user_id_dict['token'], 'name': 'happytreefriends', 'is_public': True
    })
    assert channel_id_req.status_code == OK
    channel_id = json.loads(channel_id_req.text)['channel_id']
    resp = requests.post(f"{URL}/channel/invite/v2", json={
        'token': auth_user_id_dict['token'], 'channel_id': channel_id, 'u_id': 3
    })
    assert resp.status_code == 400


def test_invite_repeated_u_id(clear, u_id_1, u_id_2):
    auth_user_id_dict = u_id_1
    u_id_dict = u_id_2

    channel_id_req = requests.post(f"{URL}/channels/create/v2", json={
        'token': auth_user_id_dict['token'], 'name': 'happytreefriends', 'is_public': True
    })
    assert channel_id_req.status_code == OK
    channel_id = json.loads(channel_id_req.text)['channel_id']

    resp = requests.post(f"{URL}/channel/invite/v2", json={
        'token': auth_user_id_dict['token'], 'channel_id': channel_id, 'u_id': u_id_dict['auth_user_id']
    })
    assert resp.status_code == OK
    resp = requests.post(f"{URL}/channel/invite/v2", json={
        'token': auth_user_id_dict['token'], 'channel_id': channel_id, 'u_id': u_id_dict['auth_user_id']
    })
    assert resp.status_code == 400


def test_invite_invalid_token(clear, u_id_1, u_id_2):
    auth_user_id_dict = u_id_1
    u_id_dict = u_id_2

    channel_id_req = requests.post(f"{URL}/channels/create/v2", json={
        'token': auth_user_id_dict['token'], 'name': 'happytreefriends', 'is_public': True
    })
    assert channel_id_req.status_code == OK
    channel_id = json.loads(channel_id_req.text)['channel_id']
    resp = requests.post(f"{URL}/channel/invite/v2", json={
        'token': f"{u_id_1['token']}9000", 'channel_id': channel_id, 'u_id': u_id_dict['auth_user_id']
    })
    assert resp.status_code == 403


def test_invite_valid_channel_id_unauthorised_user(clear, u_id_1, u_id_2, u_id_3):
    auth_user_id_dict = u_id_1
    unauth_dict = u_id_2
    u_id_dict = u_id_3

    channel_id_req = requests.post(f"{URL}/channels/create/v2", json={
        'token': auth_user_id_dict['token'], 'name': 'happytreefriends', 'is_public': True
    })
    assert channel_id_req.status_code == OK
    channel_id = json.loads(channel_id_req.text)['channel_id']

    resp = requests.post(f"{URL}/channel/invite/v2", json={
        'token': unauth_dict['token'], 'channel_id': channel_id, 'u_id': u_id_dict['auth_user_id']
    })
    assert resp.status_code == 403


# CHANNEL_DETAILS_TESTS
def test_channel_details_v2_invalid_channel_id(auth_user_1):
    requests.delete(f"{URL}/clear/v1")
    register_user_1 = requests.post(
        f"{URL}/auth/register/v2", json=auth_user_1)
    register_user_1_return = json.loads(register_user_1.text)
    token_user_1 = register_user_1_return['token']
    channel_1 = requests.post(
        f"{URL}/channels/create/v2", json={"token": token_user_1, "name": "Aus", "is_public": True})
    channel_1_id = json.loads(channel_1.text)['channel_id']
    invalid_channel_id = channel_1_id + 10
    channel_details_return = requests.get(
        f"{URL}/channel/details/v2" + f"?token={token_user_1}&channel_id={invalid_channel_id}")
    assert channel_details_return.status_code == 400

# #testing channel details of a non-member


def test_channel_details_v2_unauthorised_user(auth_user_1, auth_user_2):
    requests.delete(f"{URL}/clear/v1")
    login_user_1 = requests.post(f"{URL}/auth/register/v2", json=auth_user_1)
    login_user_1_return = json.loads(login_user_1.text)
    token_user_1 = login_user_1_return['token']
    login_user_2 = requests.post(f"{URL}/auth/register/v2", json=auth_user_2)
    login_user_2_return = json.loads(login_user_2.text)
    token_user_2 = login_user_2_return['token']
    channel_1 = requests.post(
        f"{URL}/channels/create/v2", json={"token": token_user_1, "name": "Aus", "is_public": True})
    channel_1_return = json.loads(channel_1.text)
    channel_1_id = channel_1_return['channel_id']
    channel_details_return = requests.get(
        f"{URL}/channel/details/v2" + f"?token={token_user_2}&channel_id={channel_1_id}")
    assert channel_details_return.status_code == 403

# #testing channel details of user with invalid token


def test_channel_details_v2_invalid_token(auth_user_1):
    requests.delete(f"{URL}/clear/v1")
    requests.post(f"{URL}/auth/register/v2", json=auth_user_1)
    login_user_1 = requests.post(f"{URL}/auth/login/v2", json=auth_user_1)
    login_user_1_return = json.loads(login_user_1.text)
    token_user_1 = login_user_1_return['token']
    invalid_token = f"{token_user_1}2725"
    channel_1 = requests.post(
        f"{URL}/channels/create/v2", json={"token": token_user_1, "name": "Aus", "is_public": True})
    channel_1_id = json.loads(channel_1.text)['channel_id']
    channel_details_return = requests.get(
        f"{URL}/channel/details/v2" + f"?token={invalid_token}&channel_id={channel_1_id}")
    assert channel_details_return.status_code == 403


def test_channel_details_v2_invalid_channel_and_invalid_token(auth_user_1):
    requests.delete(f"{URL}/clear/v1")
    requests.post(f"{URL}/auth/register/v2", json=auth_user_1)
    login_user_1 = requests.post(f"{URL}/auth/login/v2", json=auth_user_1)
    login_user_1_return = json.loads(login_user_1.text)
    token_user_1 = login_user_1_return['token']
    invalid_token = f"{token_user_1}2725"
    channel_1 = requests.post(
        f"{URL}/channels/create/v2", json={"token": token_user_1, "name": "Aus", "is_public": True})
    channel_1_id = json.loads(channel_1.text)['channel_id']
    invalid_channel_id = channel_1_id + 10
    channel_details_return = requests.get(
        f"{URL}/channel/details/v2" + f"?token={invalid_token}&channel_id={invalid_channel_id}")
    assert channel_details_return.status_code == 403


def test_channel_details_v2_functioning(auth_user_1, auth_user_2):
    requests.delete(f"{URL}/clear/v1")
    requests.post(f"{URL}/auth/register/v2", json=auth_user_1)
    login_user_1 = requests.post(f"{URL}/auth/login/v2", json=auth_user_1)
    login_user_1_return = json.loads(login_user_1.text)
    token_user_1 = login_user_1_return['token']

    requests.post(f"{URL}/auth/register/v2", json=auth_user_2)
    login_user_2 = requests.post(f"{URL}/auth/login/v2", json=auth_user_2)
    login_user_2_return = json.loads(login_user_2.text)
    token_user_2 = login_user_2_return['token']

    channel_1 = requests.post(
        f"{URL}/channels/create/v2", json={"token": token_user_1, "name": "Aus", "is_public": True})
    channel_1_id = json.loads(channel_1.text)['channel_id']

    requests.post(f"{URL}/channel/join/v2",
                  json={"token": token_user_2, "channel_id": channel_1_id})

    channel_details = requests.get(
        f"{URL}/channel/details/v2" + f"?token={token_user_1}&channel_id={channel_1_id}")
    assert channel_details.status_code == OK
    assert len(channel_details.json()['all_members']) == 2
    assert channel_details.json()['all_members'][0]['name_first'] == 'tom'
    assert channel_details.json()['all_members'][1]['name_first'] == 'jim'
    assert channel_details.json()['owner_members'][0]['name_first'] == 'tom'

def test_channel_details_v2_functioning_joiner(auth_user_1, auth_user_2):
    requests.delete(f"{URL}/clear/v1")
    requests.post(f"{URL}/auth/register/v2", json=auth_user_1)
    login_user_1 = requests.post(f"{URL}/auth/login/v2", json=auth_user_1)
    login_user_1_return = json.loads(login_user_1.text)
    token_user_1 = login_user_1_return['token']

    requests.post(f"{URL}/auth/register/v2", json=auth_user_2)
    login_user_2 = requests.post(f"{URL}/auth/login/v2", json=auth_user_2)
    login_user_2_return = json.loads(login_user_2.text)
    token_user_2 = login_user_2_return['token']

    channel_1 = requests.post(
        f"{URL}/channels/create/v2", json={"token": token_user_1, "name": "Aus", "is_public": True})
    channel_1_id = json.loads(channel_1.text)['channel_id']

    requests.post(f"{URL}/channel/join/v2",
                  json={"token": token_user_2, "channel_id": channel_1_id})

    channel_details = requests.get(
        f"{URL}/channel/details/v2" + f"?token={token_user_2}&channel_id={channel_1_id}")
    assert channel_details.status_code == OK
    assert len(channel_details.json()['all_members']) == 2
    assert channel_details.json()['all_members'][0]['name_first'] == 'tom'
    assert channel_details.json()['all_members'][1]['name_first'] == 'jim'
    assert channel_details.json()['owner_members'][0]['name_first'] == 'tom'

def test_channel_details_multiple_channels(auth_user_1, auth_user_2, auth_user_3):
    requests.delete(f"{URL}/clear/v1")
    requests.post(f"{URL}/auth/register/v2", json = auth_user_1)
    login_user_1 = requests.post(f"{URL}/auth/login/v2", json = auth_user_1)
    login_user_1_return = json.loads(login_user_1.text)
    token_user_1 = login_user_1_return['token']
    login_user_1_return['auth_user_id']

    requests.post(f"{URL}/auth/register/v2", json = auth_user_2)
    login_user_2 = requests.post(f"{URL}/auth/login/v2", json = auth_user_2)
    login_user_2_return = json.loads(login_user_2.text)
    token_user_2 = login_user_2_return['token']
    login_user_2_return['auth_user_id']

    requests.post(f"{URL}/auth/register/v2", json = auth_user_3)
    login_user_3 = requests.post(f"{URL}/auth/login/v2", json = auth_user_3)
    login_user_3_return = json.loads(login_user_3.text)
    login_user_3_return['auth_user_id']
    token_user_3 = login_user_3_return['token']

    channel_1 = requests.post(f"{URL}/channels/create/v2", json = {"token": token_user_1, "name": "Aus", "is_public": True})
    assert channel_1.status_code == OK
    channel_1_id = json.loads(channel_1.text)['channel_id']

    channel_2 = requests.post(f"{URL}/channels/create/v2", json = {"token": token_user_3, "name": "Hello", "is_public": True})
    assert channel_2.status_code == OK
    channel_2_id = json.loads(channel_2.text)['channel_id']

    user_2_joins_channel_1 = requests.post(f"{URL}/channel/join/v2", json = {"token": token_user_2, "channel_id": channel_1_id})
    assert user_2_joins_channel_1.status_code == OK

    user_3_joins_channel_1 = requests.post(f"{URL}/channel/join/v2", json = {"token": token_user_3, "channel_id": channel_1_id})
    assert user_3_joins_channel_1.status_code == OK

    user_2_joins_channel_2 = requests.post(f"{URL}/channel/join/v2", json = {"token": token_user_2, "channel_id": channel_2_id})
    assert user_2_joins_channel_2.status_code == OK

    user_1_joins_channel_2 = requests.post(f"{URL}/channel/join/v2", json = {"token": token_user_1, "channel_id": channel_2_id})
    assert user_1_joins_channel_2.status_code == OK

    channel_details = requests.get(
        f"{URL}/channel/details/v2" + f"?token={token_user_2}&channel_id={channel_1_id}")

    assert channel_details.status_code == OK
    assert len(channel_details.json()['all_members']) == 3
    assert channel_details.json()['all_members'][0]['name_first'] == 'tom'
    assert channel_details.json()['all_members'][1]['name_first'] == 'jim'
    assert channel_details.json()['all_members'][2]['name_first'] == 'peter'
    assert channel_details.json()['owner_members'][0]['name_first'] == 'tom'

# CHANNEL_JOIN_TESTS
def test_channel_join_v2_invalid_channel_id(auth_user_1, auth_user_2):
    requests.delete(f"{URL}/clear/v1")
    requests.post(f"{URL}/auth/register/v2", json=auth_user_1)
    requests.post(f"{URL}/auth/register/v2", json=auth_user_2)
    login_user_1 = requests.post(f"{URL}/auth/login/v2", json=auth_user_1)
    login_user_2 = requests.post(f"{URL}/auth/login/v2", json=auth_user_2)
    login_user_1_return = json.loads(login_user_1.text)
    login_user_2_return = json.loads(login_user_2.text)
    token_user_1 = login_user_1_return['token']
    token_user_2 = login_user_2_return['token']
    channel_1 = requests.post(
        f"{URL}/channels/create/v2", json={"token": token_user_1, "name": "Aus", "is_public": True})
    channel_1_id = json.loads(channel_1.text)['channel_id']
    invalid_channel_id = channel_1_id + 10
    channel_join_return = requests.post(
        f"{URL}/channel/join/v2", json={"token": token_user_2, "channel_id": invalid_channel_id})
    assert channel_join_return.status_code == 400


def test_channel_join_v2_repeat_join(auth_user_1):
    requests.delete(f"{URL}/clear/v1")
    requests.post(f"{URL}/auth/register/v2", json=auth_user_1)
    login_user_1 = requests.post(f"{URL}/auth/login/v2", json=auth_user_1)
    login_user_1_return = json.loads(login_user_1.text)
    token_user_1 = login_user_1_return['token']
    channel_1 = requests.post(
        f"{URL}/channels/create/v2", json={"token": token_user_1, "name": "Aus", "is_public": True})
    channel_1_return = json.loads(channel_1.text)
    channel_1_id = channel_1_return['channel_id']
    channel_join_return = requests.post(
        f"{URL}/channel/join/v2", json={"token": token_user_1, "channel_id": channel_1_id})
    assert channel_join_return.status_code == 403


def test_channel_join_v2_invalid_token(auth_user_1, auth_user_2):
    requests.delete(f"{URL}/clear/v1")
    requests.post(f"{URL}/auth/register/v2", json=auth_user_1)
    requests.post(f"{URL}/auth/register/v2", json=auth_user_2)
    login_user_1 = requests.post(f"{URL}/auth/login/v2", json=auth_user_1)
    login_user_2 = requests.post(f"{URL}/auth/login/v2", json=auth_user_2)
    login_user_1_return = json.loads(login_user_1.text)
    login_user_2_return = json.loads(login_user_2.text)
    token_user_1 = login_user_1_return['token']
    token_user_2 = login_user_2_return['token']
    invalid_token_2 = f"{token_user_2}2726"
    channel_1 = requests.post(
        f"{URL}/channels/create/v2", json={"token": token_user_1, "name": "Aus", "is_public": True})
    channel_1_id = json.loads(channel_1.text)['channel_id']
    channel_join_return = requests.post(
        f"{URL}/channel/join/v2", json={"token": invalid_token_2, "channel_id": channel_1_id})
    assert channel_join_return.status_code == 403


def test_channel_join_v2_private_channel(auth_user_1, auth_user_2):
    requests.delete(f"{URL}/clear/v1")
    login_user_1 = requests.post(f"{URL}/auth/register/v2", json=auth_user_1)
    login_user_2 = requests.post(f"{URL}/auth/register/v2", json=auth_user_2)
    login_user_1_return = json.loads(login_user_1.text)
    login_user_2_return = json.loads(login_user_2.text)
    token_user_1 = login_user_1_return['token']
    token_user_2 = login_user_2_return['token']
    channel_1 = requests.post(
        f"{URL}/channels/create/v2", json={"token": token_user_1, "name": "Aus", "is_public": False})
    channel_1_return = json.loads(channel_1.text)
    channel_1_id = channel_1_return['channel_id']
    channel_join_return = requests.post(
        f"{URL}/channel/join/v2", json={"token": token_user_2, "channel_id": channel_1_id})
    assert channel_join_return.status_code == 403


def test_channel_join_v2_global_owner(auth_user_1, auth_user_2):
    requests.delete(f"{URL}/clear/v1")
    requests.delete(f"{URL}/clear/v1")
    requests.post(f"{URL}/auth/register/v2", json=auth_user_1)
    login_user_1 = requests.post(f"{URL}/auth/login/v2", json=auth_user_1)
    requests.post(f"{URL}/auth/register/v2", json=auth_user_2)
    login_user_2 = requests.post(f"{URL}/auth/login/v2", json=auth_user_2)
    login_user_1_return = json.loads(login_user_1.text)
    login_user_2_return = json.loads(login_user_2.text)
    token_user_1 = login_user_1_return['token']
    token_user_2 = login_user_2_return['token']
    # user 1 is a global so let user 2 create it and see if user 1 can join

    channel_1 = requests.post(
        f"{URL}/channels/create/v2", json={"token": token_user_2, "name": "Aus", "is_public": False})
    assert channel_1.status_code == OK
    channel_1_return = json.loads(channel_1.text)
    channel_1_id = channel_1_return['channel_id']
    channel_join_user_1 = requests.post(
        f"{URL}/channel/join/v2", json={"token": token_user_1, "channel_id": channel_1_id}).status_code
    assert channel_join_user_1 == OK
    channel_1_details = requests.get(
        f"{URL}/channel/details/v2" + f"?token={token_user_2}&channel_id={channel_1_id}")
    assert channel_1_details.status_code == OK
    assert len(json.loads(channel_1_details.text)['all_members']) == 2


def test_channel_join_v2_public_channel(auth_user_1, auth_user_2):
    requests.delete(f"{URL}/clear/v1")
    requests.delete(f"{URL}/clear/v1")
    requests.post(f"{URL}/auth/register/v2", json=auth_user_1)
    login_user_1 = requests.post(f"{URL}/auth/login/v2", json=auth_user_1)
    requests.post(f"{URL}/auth/register/v2", json=auth_user_2)
    login_user_2 = requests.post(f"{URL}/auth/login/v2", json=auth_user_2)
    login_user_1_return = json.loads(login_user_1.text)
    login_user_2_return = json.loads(login_user_2.text)
    token_user_1 = login_user_1_return['token']
    token_user_2 = login_user_2_return['token']

    channel_1 = requests.post(
        f"{URL}/channels/create/v2", json={"token": token_user_1, "name": "Aus", "is_public": True})
    channel_1_return = json.loads(channel_1.text)
    channel_1_id = channel_1_return['channel_id']
    channel_join_user_1 = requests.post(
        f"{URL}/channel/join/v2", json={"token": token_user_2, "channel_id": channel_1_id}).status_code
    assert channel_join_user_1 == OK
    channel_1_details = requests.get(
        f"{URL}/channel/details/v2" + f"?token={token_user_2}&channel_id={channel_1_id}")
    assert channel_1_details.status_code == OK
    assert len(json.loads(channel_1_details.text)['all_members']) == 2


def test_channel_join_v2_invalid_channel_and_invalid_token(auth_user_1, auth_user_2):
    requests.delete(f"{URL}/clear/v1")
    requests.post(f"{URL}/auth/register/v2", json=auth_user_1)
    requests.post(f"{URL}/auth/register/v2", json=auth_user_2)
    login_user_1 = requests.post(f"{URL}/auth/login/v2", json=auth_user_1)
    login_user_2 = requests.post(f"{URL}/auth/login/v2", json=auth_user_2)
    login_user_1_return = json.loads(login_user_1.text)
    login_user_2_return = json.loads(login_user_2.text)
    token_user_1 = login_user_1_return['token']
    token_user_2 = login_user_2_return['token']
    invalid_token_2 = f"{token_user_2}2726"
    channel_1 = requests.post(
        f"{URL}/channels/create/v2", json={"token": token_user_1, "name": "Aus", "is_public": True})
    channel_1_id = json.loads(channel_1.text)['channel_id']
    invalid_channel_id = channel_1_id + 10
    channel_join_return = requests.post(
        f"{URL}/channel/join/v2", json={"token": invalid_token_2, "channel_id": invalid_channel_id})
    assert channel_join_return.status_code == 403

# CHANNEL/ADDOWNER/V1 {token, channel_id, u_id}

# Test for access error if token is not that of an owner of channel [PASSES]


def test_token_not_of_owner_channel_addowner_v1_http(clear):
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
    assert register_user1.status_code == OK
    user3_id = register_user3.json()['auth_user_id']

    # owner creates channel
    channel_info = requests.post(
        f"{URL}/channels/create/v2", json={"token": user1_token, "name": "channel", "is_public": True})
    assert channel_info.status_code == OK
    channel_id = channel_info.json()['channel_id']
    # owner invites two users
    channel_invite = requests.post(f"{URL}/channel/invite/v2", json={
                                   "token": user1_token, "channel_id": channel_id, "u_id": user2_id})
    assert channel_invite.status_code == OK
    channel_invite = requests.post(f"{URL}/channel/invite/v2", json={
                                   "token": user1_token, "channel_id": channel_id, "u_id": user3_id})
    assert channel_invite.status_code == OK

    # one user tries to make the other user the owner (AccessError)
    addowner = requests.post(f"{URL}/channel/addowner/v1", json={
                             'token': user2_token, 'channel_id': channel_id, 'u_id': user3_id})
    assert addowner.status_code == ACCESSERROR


# Test for input error if channel_id is invalid [PASSES]


def test_invalid_channel_id_channel_addowner_v1_http(clear):
    # register 2 users
    register_user1 = requests.post(f"{URL}/auth/register/v2", json={"email": "user1@gmail.com",
                                                                    "password": "password",  "name_first": "name", "name_last": "surname"})
    assert register_user1.status_code == OK
    user1_token = register_user1.json()['token']
    register_user2 = requests.post(f"{URL}/auth/register/v2", json={"email": "user2@gmail.com",
                                                                    "password": "password",  "name_first": "name", "name_last": "surname"})
    assert register_user2.status_code == OK
    user2_id = register_user2.json()['auth_user_id']

    # owner creates channel
    channel_info = requests.post(
        f"{URL}/channels/create/v2", json={"token": user1_token, "name": "channel", "is_public": True})
    assert channel_info.status_code == OK
    channel_id = channel_info.json()['channel_id']
    invalid_channel_id = channel_id + 69
    # owner invites user
    channel_invite = requests.post(f"{URL}/channel/invite/v2", json={
                                   "token": user1_token, "channel_id": channel_id, "u_id": user2_id})
    assert channel_invite.status_code == OK

    # owner makes user2 owner but uses invalid channl_id (InputError)
    addowner = requests.post(f"{URL}/channel/addowner/v1", json={
                             'token': user1_token, 'channel_id': invalid_channel_id, 'u_id': user2_id})
    assert addowner.status_code == INPUTERROR

# Test for input error if u_id is not member of channel [PASSES]


def test_uid_not_member_of_channel_channel_addowner_v1_http(clear):
    # register 2 users
    register_user1 = requests.post(f"{URL}/auth/register/v2", json={"email": "user1@gmail.com",
                                                                    "password": "password",  "name_first": "name", "name_last": "surname"})
    assert register_user1.status_code == OK
    user1_token = register_user1.json()['token']
    register_user2 = requests.post(f"{URL}/auth/register/v2", json={"email": "user2@gmail.com",
                                                                    "password": "password",  "name_first": "name", "name_last": "surname"})
    assert register_user2.status_code == OK
    user2_id = register_user2.json()['auth_user_id']

    # owner creates channel
    channel_info = requests.post(
        f"{URL}/channels/create/v2", json={"token": user1_token, "name": "channel", "is_public": True})
    assert channel_info.status_code == OK
    channel_id = channel_info.json()['channel_id']

    # owner makes user2 an owner but they are not part of the channel (INPUTERROR)
    addowner = requests.post(f"{URL}/channel/addowner/v1", json={
                             'token': user1_token, 'channel_id': channel_id, 'u_id': user2_id})
    assert addowner.status_code == INPUTERROR

# Test for input error if u_id does not exist [PASSES]


def test_uid_does_not_exist_channel_addowner_v1_http(clear):
    # register 2 users
    register_user1 = requests.post(f"{URL}/auth/register/v2", json={"email": "user1@gmail.com",
                                                                    "password": "password",  "name_first": "name", "name_last": "surname"})
    assert register_user1.status_code == OK
    user1_token = register_user1.json()['token']
    register_user2 = requests.post(f"{URL}/auth/register/v2", json={"email": "user2@gmail.com",
                                                                    "password": "password",  "name_first": "name", "name_last": "surname"})
    assert register_user2.status_code == OK
    user2_id = register_user2.json()['auth_user_id']

    # owner creates channel
    channel_info = requests.post(
        f"{URL}/channels/create/v2", json={"token": user1_token, "name": "channel", "is_public": True})
    assert channel_info.status_code == OK
    channel_id = channel_info.json()['channel_id']

    # owner makes an invalid u_id an owner(INPUTERROR)
    addowner = requests.post(f"{URL}/channel/addowner/v1", json={
                             'token': user1_token, 'channel_id': channel_id, 'u_id': user2_id + 69})
    assert addowner.status_code == INPUTERROR

# Test for input error if u_id is an owner [PASSES]


def test_uid_is_owner_channel_addowner_v1_http(clear):
    # register user
    register_user1 = requests.post(f"{URL}/auth/register/v2", json={"email": "user1@gmail.com",
                                                                    "password": "password",  "name_first": "name", "name_last": "surname"})
    assert register_user1.status_code == OK
    user1_token = register_user1.json()['token']
    user1_id = register_user1.json()['auth_user_id']

    # owner creates channel
    channel_info = requests.post(
        f"{URL}/channels/create/v2", json={"token": user1_token, "name": "channel", "is_public": True})
    assert channel_info.status_code == OK
    channel_id = channel_info.json()['channel_id']

    # owner makes themselves the owner (INPUTERROR)
    addowner = requests.post(f"{URL}/channel/addowner/v1", json={
                             'token': user1_token, 'channel_id': channel_id, 'u_id': user1_id})
    assert addowner.status_code == INPUTERROR

# Test normal functioning of channel_addowner_v1 [PASSES]


def test_channel_addowner_v1_http(clear):
    # register 2 users
    register_user1 = requests.post(f"{URL}/auth/register/v2", json={"email": "user1@gmail.com",
                                                                    "password": "password",  "name_first": "user1", "name_last": "surname"})
    assert register_user1.status_code == OK
    user1_token = register_user1.json()['token']
    register_user2 = requests.post(f"{URL}/auth/register/v2", json={"email": "user2@gmail.com",
                                                                    "password": "password",  "name_first": "user2", "name_last": "surname"})
    assert register_user2.status_code == OK
    user2_id = register_user2.json()['auth_user_id']

    # owner creates channel
    channel_info = requests.post(
        f"{URL}/channels/create/v2", json={"token": user1_token, "name": "channel", "is_public": True})
    assert channel_info.status_code == OK
    channel_id = channel_info.json()['channel_id']
    # owner invites user
    channel_invite = requests.post(f"{URL}/channel/invite/v2", json={
                                   "token": user1_token, "channel_id": channel_id, "u_id": user2_id})
    assert channel_invite.status_code == OK
    # owner makes user an owner
    addowner = requests.post(f"{URL}/channel/addowner/v1", json={
                             'token': user1_token, 'channel_id': channel_id, 'u_id': user2_id})
    assert addowner.status_code == OK
    # use channel details to check that there are two owners
    channel_details = requests.get(
        f"{URL}/channel/details/v2" + f"?token={user1_token}&channel_id={channel_id}")
    assert channel_details.status_code == OK
    assert len(channel_details.json()['owner_members']) == 2
    assert channel_details.json()['owner_members'][0]['name_first'] == 'user1'
    assert channel_details.json()['owner_members'][1]['name_first'] == 'user2'

# Test for invalid token for channel_addowner_v1 [PASSES]


def test_channel_addowner_invalid_token_http(clear):
    # register 2 users
    register_user1 = requests.post(f"{URL}/auth/register/v2", json={"email": "user1@gmail.com",
                                                                    "password": "password",  "name_first": "name", "name_last": "surname"})
    assert register_user1.status_code == OK
    user1_token = register_user1.json()['token']
    user1_invalid_token = user1_token + "wrong"
    register_user2 = requests.post(f"{URL}/auth/register/v2", json={"email": "user2@gmail.com",
                                                                    "password": "password",  "name_first": "name", "name_last": "surname"})
    assert register_user2.status_code == OK
    user2_id = register_user2.json()['auth_user_id']

    # owner creates channel
    channel_info = requests.post(
        f"{URL}/channels/create/v2", json={"token": user1_token, "name": "channel", "is_public": True})
    assert channel_info.status_code == OK
    channel_id = channel_info.json()['channel_id']
    # owner invites user
    channel_invite = requests.post(f"{URL}/channel/invite/v2", json={
                                   "token": user1_token, "channel_id": channel_id, "u_id": user2_id})
    assert channel_invite.status_code == OK

    # invalid token is entered, raising access error
    addowner = requests.post(f"{URL}/channel/addowner/v1", json={
                             'token': user1_invalid_token, 'channel_id': channel_id, 'u_id': user2_id})
    assert addowner.status_code == ACCESSERROR

# test for working channel add owner for global owner joining channel and is able to add owner


def test_global_owner_adds_owner_channel_addowner_http(clear):
    # register 3 users
    register_user1 = requests.post(f"{URL}/auth/register/v2", json={"email": "user1@gmail.com",
                                                                    "password": "password",  "name_first": "user1", "name_last": "surname"})
    assert register_user1.status_code == OK
    user1_token = register_user1.json()['token']
    user1_id = register_user1.json()['auth_user_id']
    register_user2 = requests.post(f"{URL}/auth/register/v2", json={"email": "user2@gmail.com",
                                                                    "password": "password",  "name_first": "user2", "name_last": "surname"})
    assert register_user2.status_code == OK
    user2_token = register_user2.json()['token']
    register_user3 = requests.post(f"{URL}/auth/register/v2", json={"email": "user3@gmail.com",
                                                                    "password": "password",  "name_first": "user3", "name_last": "surname"})
    assert register_user3.status_code == OK
    user3_id = register_user3.json()['auth_user_id']
    # user 2 creates channel
    channel_info = requests.post(
        f"{URL}/channels/create/v2", json={"token": user2_token, "name": "channel", "is_public": True})
    assert channel_info.status_code == OK
    channel_id = channel_info.json()['channel_id']
    # user 2 invites user1 and user3
    channel_invite1 = requests.post(f"{URL}/channel/invite/v2", json={
                                    "token": user2_token, "channel_id": channel_id, "u_id": user1_id})
    assert channel_invite1.status_code == OK
    channel_invite2 = requests.post(f"{URL}/channel/invite/v2", json={
                                    "token": user2_token, "channel_id": channel_id, "u_id": user3_id})
    assert channel_invite2.status_code == OK
    # user1 makes user3 owner and its OK
    addowner = requests.post(f"{URL}/channel/addowner/v1", json={
                             'token': user1_token, 'channel_id': channel_id, 'u_id': user3_id})
    assert addowner.status_code == OK

# CHANNEL/REMOVEOWNER/V1 TESTS

# Test accesserror for invalid token in channel_removeowner_v1 [PASSES]


def test_invalid_token_channel_removeowner_v1_http(clear):
    # register 2 users
    register_user1 = requests.post(f"{URL}/auth/register/v2", json={"email": "user1@gmail.com",
                                                                    "password": "password",  "name_first": "name", "name_last": "surname"})
    assert register_user1.status_code == OK
    user1_token = register_user1.json()['token']
    user1_invalid_token = user1_token + "wrong"
    register_user2 = requests.post(f"{URL}/auth/register/v2", json={"email": "user2@gmail.com",
                                                                    "password": "password",  "name_first": "name", "name_last": "surname"})
    assert register_user2.status_code == OK
    user2_id = register_user2.json()['auth_user_id']
    # user1 creates channel
    channel_info = requests.post(
        f"{URL}/channels/create/v2", json={"token": user1_token, "name": "channel", "is_public": True})
    assert channel_info.status_code == OK
    channel_id = channel_info.json()['channel_id']
    # user1 invites user2
    channel_invite = requests.post(f"{URL}/channel/invite/v2", json={
                                   "token": user1_token, "channel_id": channel_id, "u_id": user2_id})
    assert channel_invite.status_code == OK
    # user1 makes user2 owner
    addowner = requests.post(f"{URL}/channel/addowner/v1", json={
                             'token': user1_token, 'channel_id': channel_id, 'u_id': user2_id})
    assert addowner.status_code == OK
    # user1 removes user2 owner but invalid token is input resulting in access error
    removeowner = requests.post(f"{URL}/channel/removeowner/v1", json={
                                'token': user1_invalid_token, 'channel_id': channel_id, 'u_id': user2_id})
    assert removeowner.status_code == ACCESSERROR

# Test input error for invalid channel_id in channel_removeowner_v1 [PASSES]


def test_invalid_channel_id_channel_removeowner_v1_http(clear):
    # register 2 users
    register_user1 = requests.post(f"{URL}/auth/register/v2", json={"email": "user1@gmail.com",
                                                                    "password": "password",  "name_first": "name", "name_last": "surname"})
    assert register_user1.status_code == OK
    user1_token = register_user1.json()['token']
    register_user2 = requests.post(f"{URL}/auth/register/v2", json={"email": "user2@gmail.com",
                                                                    "password": "password",  "name_first": "name", "name_last": "surname"})
    assert register_user2.status_code == OK
    user2_id = register_user2.json()['auth_user_id']
    # user1 creates channel
    channel_info = requests.post(
        f"{URL}/channels/create/v2", json={"token": user1_token, "name": "channel", "is_public": True})
    assert channel_info.status_code == OK
    channel_id = channel_info.json()['channel_id']
    invalid_channel_id = channel_id + 21
    # user1 invites user2
    channel_invite = requests.post(f"{URL}/channel/invite/v2", json={
                                   "token": user1_token, "channel_id": channel_id, "u_id": user2_id})
    assert channel_invite.status_code == OK
    # user1 makes user2 owner
    addowner = requests.post(f"{URL}/channel/addowner/v1", json={
                             'token': user1_token, 'channel_id': channel_id, 'u_id': user2_id})
    assert addowner.status_code == OK
    # user1 removes user2 from owner but uses invalid channel_id resulting in input error
    removeowner = requests.post(f"{URL}/channel/removeowner/v1", json={
                                'token': user1_token, 'channel_id': invalid_channel_id, 'u_id': user2_id})
    assert removeowner.status_code == INPUTERROR

# Test for input error for invalid u_id in channel_removeowner_v1 [PASSES]


def test_invalid_u_id_channel_removeowner_v1_http(clear):
    # register 2 users
    register_user1 = requests.post(f"{URL}/auth/register/v2", json={"email": "user1@gmail.com",
                                                                    "password": "password",  "name_first": "name", "name_last": "surname"})
    assert register_user1.status_code == OK
    user1_token = register_user1.json()['token']
    register_user2 = requests.post(f"{URL}/auth/register/v2", json={"email": "user2@gmail.com",
                                                                    "password": "password",  "name_first": "name", "name_last": "surname"})
    assert register_user2.status_code == OK
    user2_id = register_user2.json()['auth_user_id']
    invalid_user2_id = user2_id + 45
    # user1 creates channel
    channel_info = requests.post(
        f"{URL}/channels/create/v2", json={"token": user1_token, "name": "channel", "is_public": True})
    assert channel_info.status_code == OK
    channel_id = channel_info.json()['channel_id']
    # user1 invites user2
    channel_invite = requests.post(f"{URL}/channel/invite/v2", json={
                                   "token": user1_token, "channel_id": channel_id, "u_id": user2_id})
    assert channel_invite.status_code == OK
    # user1 makes user2 owner
    addowner = requests.post(f"{URL}/channel/addowner/v1", json={
                             'token': user1_token, 'channel_id': channel_id, 'u_id': user2_id})
    assert addowner.status_code == OK
    # user1 removes user2 from owner but uses invalid u_id resulting in input error
    removeowner = requests.post(f"{URL}/channel/removeowner/v1", json={
                                'token': user1_token, 'channel_id': channel_id, 'u_id': invalid_user2_id})
    assert removeowner.status_code == INPUTERROR


# Test for input error for u_id does not belong to an owner in channel_removeowner_v1 [PASSES]
def test_u_id_does_not_belong_to_owner_channel_removeowner_v1_http(clear):
    # register 2 users
    register_user1 = requests.post(f"{URL}/auth/register/v2", json={"email": "user1@gmail.com",
                                                                    "password": "password",  "name_first": "name", "name_last": "surname"})
    assert register_user1.status_code == OK
    user1_token = register_user1.json()['token']
    register_user2 = requests.post(f"{URL}/auth/register/v2", json={"email": "user2@gmail.com",
                                                                    "password": "password",  "name_first": "name", "name_last": "surname"})
    assert register_user2.status_code == OK
    user2_id = register_user2.json()['auth_user_id']
    # user1 creates channel
    channel_info = requests.post(
        f"{URL}/channels/create/v2", json={"token": user1_token, "name": "channel", "is_public": True})
    assert channel_info.status_code == OK
    channel_id = channel_info.json()['channel_id']
    # user1 invites user2
    channel_invite = requests.post(f"{URL}/channel/invite/v2", json={
                                   "token": user1_token, "channel_id": channel_id, "u_id": user2_id})
    assert channel_invite.status_code == OK
    # user1 removes user2 from owner but user2 was never an owner, raising input error
    removeowner = requests.post(f"{URL}/channel/removeowner/v1", json={
                                'token': user1_token, 'channel_id': channel_id, 'u_id': user2_id})
    assert removeowner.status_code == INPUTERROR

# Test for input error for u_id being the only owner of channel in channel_removeowner_v1 [PASSES]


def test_u_id_is_the_only_owner_channel_removeowner_v1_http(clear):
    # register 1 user
    register_user1 = requests.post(f"{URL}/auth/register/v2", json={"email": "user1@gmail.com",
                                                                    "password": "password",  "name_first": "name", "name_last": "surname"})
    assert register_user1.status_code == OK
    user1_token = register_user1.json()['token']
    user1_id = register_user1.json()['auth_user_id']
    # user1 creates channel
    channel_info = requests.post(
        f"{URL}/channels/create/v2", json={"token": user1_token, "name": "channel", "is_public": True})
    assert channel_info.status_code == OK
    channel_id = channel_info.json()['channel_id']
    # user1 removes user1 from owner but they are the only owner, raising input error
    removeowner = requests.post(f"{URL}/channel/removeowner/v1", json={
                                'token': user1_token, 'channel_id': channel_id, 'u_id': user1_id})
    assert removeowner.status_code == INPUTERROR

# Test for access error if token does not belong to owner but the channel_id is valid [PASSES]


def test_token_does_not_belong_to_owner_channel_removeowner_v1_http(clear):
    # register 2 users
    register_user1 = requests.post(f"{URL}/auth/register/v2", json={"email": "user1@gmail.com",
                                                                    "password": "password",  "name_first": "name", "name_last": "surname"})
    assert register_user1.status_code == OK
    user1_token = register_user1.json()['token']
    user1_id = register_user1.json()['auth_user_id']
    register_user2 = requests.post(f"{URL}/auth/register/v2", json={"email": "user2@gmail.com",
                                                                    "password": "password",  "name_first": "name", "name_last": "surname"})
    assert register_user2.status_code == OK
    user2_token = register_user2.json()['token']
    user2_id = register_user2.json()['auth_user_id']
    # owner makes channel
    channel_info = requests.post(
        f"{URL}/channels/create/v2", json={"token": user1_token, "name": "channel", "is_public": True})
    assert channel_info.status_code == OK
    channel_id = channel_info.json()['channel_id']
    # owner invites user2
    channel_invite = requests.post(f"{URL}/channel/invite/v2", json={
                                   "token": user1_token, "channel_id": channel_id, "u_id": user2_id})
    assert channel_invite.status_code == OK
    # user 2 removes owner but user2  does not have owner, so access error
    removeowner = requests.post(f"{URL}/channel/removeowner/v1", json={
                                'token': user2_token, 'channel_id': channel_id, 'u_id': user1_id})
    assert removeowner.status_code == ACCESSERROR

# Test normal functioning of channel_remove_owner_v1 [PASSES]


def test_channel_removeowner_v1_http(clear):
    # register 2 users
    register_user1 = requests.post(f"{URL}/auth/register/v2", json={"email": "user1@gmail.com",
                                                                    "password": "password",  "name_first": "user1", "name_last": "surname"})
    assert register_user1.status_code == OK
    user1_token = register_user1.json()['token']
    register_user2 = requests.post(f"{URL}/auth/register/v2", json={"email": "user2@gmail.com",
                                                                    "password": "password",  "name_first": "name", "name_last": "surname"})
    assert register_user2.status_code == OK
    user2_id = register_user2.json()['auth_user_id']
    # owner makes channel
    channel_info = requests.post(
        f"{URL}/channels/create/v2", json={"token": user1_token, "name": "channel", "is_public": True})
    assert channel_info.status_code == OK
    channel_id = channel_info.json()['channel_id']
    # owner invites user2
    channel_invite = requests.post(f"{URL}/channel/invite/v2", json={
                                   "token": user1_token, "channel_id": channel_id, "u_id": user2_id})
    assert channel_invite.status_code == OK
    # user 1 makes user2 an owner
    addowner = requests.post(f"{URL}/channel/addowner/v1", json={
                             'token': user1_token, 'channel_id': channel_id, 'u_id': user2_id})
    assert addowner.status_code == OK
    # user1 removes user 2 as owner
    removeowner = requests.post(f"{URL}/channel/removeowner/v1", json={
                                'token': user1_token, 'channel_id': channel_id, 'u_id': user2_id})
    assert removeowner.status_code == OK
    # use channel details to see if there is still only one owner
    channel_details = requests.get(
        f"{URL}/channel/details/v2"+f"?token={user1_token}&channel_id={channel_id}")
    assert channel_details.status_code == OK
    assert len(channel_details.json()['owner_members']) == 1
    assert channel_details.json()['owner_members'][0]['name_first'] == 'user1'

# Test user with global perm is allowed to remove owner channel remove owner


def test_global_owner_remove_owner_channel_remove_owner_http(clear):
    # register 3 users
    register_user1 = requests.post(f"{URL}/auth/register/v2", json={"email": "user1@gmail.com",
                                                                    "password": "password",  "name_first": "user1", "name_last": "surname"})
    assert register_user1.status_code == OK
    user1_token = register_user1.json()['token']
    user1_id = register_user1.json()['auth_user_id']
    register_user2 = requests.post(f"{URL}/auth/register/v2", json={"email": "user2@gmail.com",
                                                                    "password": "password",  "name_first": "user2", "name_last": "surname"})
    assert register_user2.status_code == OK
    user2_token = register_user2.json()['token']
    user2_id = register_user2.json()['auth_user_id']
    register_user3 = requests.post(f"{URL}/auth/register/v2", json={"email": "user3@gmail.com",
                                                                    "password": "password",  "name_first": "user3", "name_last": "surname"})
    assert register_user3.status_code == OK
    user3_id = register_user3.json()['auth_user_id']
    # user 2 creates channel
    channel_info = requests.post(
        f"{URL}/channels/create/v2", json={"token": user2_token, "name": "channel", "is_public": True})
    assert channel_info.status_code == OK
    channel_id = channel_info.json()['channel_id']
    # user 2 invites user1 and user3
    channel_invite1 = requests.post(f"{URL}/channel/invite/v2", json={
                                    "token": user2_token, "channel_id": channel_id, "u_id": user1_id})
    assert channel_invite1.status_code == OK
    channel_invite2 = requests.post(f"{URL}/channel/invite/v2", json={
                                    "token": user2_token, "channel_id": channel_id, "u_id": user3_id})
    assert channel_invite2.status_code == OK
    # user 2 makes user 3 an owner
    addowner = requests.post(f"{URL}/channel/addowner/v1", json={
                             'token': user2_token, 'channel_id': channel_id, 'u_id': user3_id})
    assert addowner.status_code == OK
    # user1 removes user2 owner and its OK
    removeowner = requests.post(f"{URL}/channel/removeowner/v1", json={
                                'token': user1_token, 'channel_id': channel_id, 'u_id': user2_id})
    assert removeowner.status_code == OK


def test_messages_correct_functioning_no_messages(clear, u_id_1):
    token = u_id_1['token']
    channel_id_req = requests.post(f"{URL}/channels/create/v2", json={
        'token': token, 'name': 'happytreefriends', 'is_public': True
    })
    assert channel_id_req.status_code == OK
    channel_id = json.loads(channel_id_req.text)['channel_id']

    message_list_json = requests.get(
        f"{URL}/channel/messages/v2?token={token}&channel_id={channel_id}&start=0")

    assert message_list_json.status_code == OK
    message_dict = json.loads(message_list_json.text)
    assert message_dict == {'messages': [], 'start': 0, 'end': -1}


def test_messages_correct_functioning_with_messages(clear, u_id_1, u_id_2, u_id_3):
    channel_params = {'token': u_id_3['token'],
                      'name': 'BOZOSRUS', 'is_public': True}
    channel = requests.post(f"{URL}/channels/create/v2", json=channel_params)
    channel_id = channel.json().get('channel_id')
    # sends messages in channel
    for i in range(50):
        msg_send_params = {
            'token': u_id_3['token'], 'channel_id': channel_id, 'message': f"{i} banana"}
        requests.post(f"{URL}/message/send/v1", json=msg_send_params)
    # check if messages were sent correctly
    get_messages = requests.get(
        f"{URL}/channel/messages/v2?token={u_id_3['token']}&channel_id={channel_id}&start=3")
    get_messages_dict = get_messages.json()
    assert get_messages_dict['messages'][0]['message'] == "46 banana"
    assert len(get_messages_dict['messages']) == 47
    assert get_messages_dict['start'] == 3
    assert get_messages_dict['end'] == -1


def test_messages_invalid_channel_id(clear, u_id_1):
    token = u_id_1['token']
    requests.post(f"{URL}/channels/create/v2", json={
        'token': token, 'name': 'happytreefriends', 'is_public': True
    })
    message_list = requests.get(
        f"{URL}/channel/messages/v2?token={token}&channel_id=2&start=0")
    assert message_list.status_code == 400


def test_messages_invalid_start_when_empty(clear, u_id_1):
    token = u_id_1['token']
    channel_id_req = requests.post(f"{URL}/channels/create/v2", json={
        'token': token, 'name': 'happytreefriends', 'is_public': True
    })
    assert channel_id_req.status_code == OK
    channel_id = json.loads(channel_id_req.text)['channel_id']
    message_list_json = requests.get(
        f"{URL}/channel/messages/v2?token={token}&channel_id={channel_id}&start=1")
    assert message_list_json.status_code == 400


def test_messages_invalid_start_not_empty(clear, u_id_1):
    channel_params = {'token': u_id_1['token'],
                      'name': 'BOZOSRUS', 'is_public': True}
    channel = requests.post(f"{URL}/channels/create/v2", json=channel_params)
    assert channel.status_code == OK
    channel_id = channel.json()['channel_id']
    for i in range(5):
        send_msg_params = {
            'token': u_id_1['token'], 'channel_id': channel_id, 'message': f"message{i}"}
        requests.post(f"{URL}/message/send/v1", json=send_msg_params)
    get_messages = requests.get(
        f"{URL}/channel/messages/v2?token={u_id_1['token']}&channel_id={channel_id}&start=7")
    assert get_messages.status_code == 400


def test_messages_unauthorised_user_valid_channel(clear, u_id_1, u_id_2):
    token = u_id_1['token']
    unauth_token = u_id_2['token']
    channel_id_req = requests.post(f"{URL}/channels/create/v2", json={
        'token': token, 'name': 'happytreefriends', 'is_public': True
    })
    assert channel_id_req.status_code == OK
    channel_id = json.loads(channel_id_req.text)['channel_id']
    message_list_json = requests.get(
        f"{URL}/channel/messages/v2?token={unauth_token}&channel_id={channel_id}&start=0")
    assert message_list_json.status_code == 403


def test_messages_invalid_token(clear, u_id_1):
    token = u_id_1['token']
    channel_id_req = requests.post(f"{URL}/channels/create/v2", json={
        'token': token, 'name': 'happytreefriends', 'is_public': True
    })
    assert channel_id_req.status_code == OK
    channel_id = json.loads(channel_id_req.text)['channel_id']
    message_list_json = requests.get(
        f"{URL}/channel/messages/v2?token={token}123&channel_id={channel_id}&start=0")
    assert message_list_json.status_code == 403
    
def test_global_owner_adds_owner_but_not_in_channel_channel_addowner_v1_http(clear):
    # register 3 users
    register_user1 = requests.post(f"{URL}/auth/register/v2", json={"email": "user1@gmail.com",
                                                                    "password": "password",  "name_first": "user1", "name_last": "surname"})
    assert register_user1.status_code == OK
    user1_token = register_user1.json()['token']
    user1_id = register_user1.json()['auth_user_id']
    register_user2 = requests.post(f"{URL}/auth/register/v2", json={"email": "user2@gmail.com",
                                                                    "password": "password",  "name_first": "user2", "name_last": "surname"})
    assert register_user2.status_code == OK
    user2_token = register_user2.json()['token']
    register_user3 = requests.post(f"{URL}/auth/register/v2", json={"email": "user3@gmail.com",
                                                                    "password": "password",  "name_first": "user3", "name_last": "surname"})
    assert register_user3.status_code == OK
    user3_id = register_user3.json()['auth_user_id']
    # user 2 makes a channel
    channel_info = requests.post(
        f"{URL}/channels/create/v2", json={"token": user2_token, "name": "channel", "is_public": True})
    assert channel_info.status_code == OK
    channel_id = channel_info.json()['channel_id']
    # user 2 invites user 3 and user 1
    channel_invite1 = requests.post(f"{URL}/channel/invite/v2", json={
                                    "token": user2_token, "channel_id": channel_id, "u_id": user1_id})
    assert channel_invite1.status_code == OK
    channel_invite2 = requests.post(f"{URL}/channel/invite/v2", json={
                                    "token": user2_token, "channel_id": channel_id, "u_id": user3_id})
    assert channel_invite2.status_code == OK
    # user 1 leaves
    channel_leave = requests.post(
        f"{URL}/channel/leave/v1", json={'token': user1_token, 'channel_id': channel_id})
    assert channel_leave.status_code == OK
    # user 1 adds owner to user 3 raising access error
    addowner = requests.post(f"{URL}/channel/addowner/v1", json={
                             'token': user1_token, 'channel_id': channel_id, 'u_id': user3_id})
    assert addowner.status_code == ACCESSERROR


def test_global_owner_adds_owner_but_not_in_channel_channel_addowner_v1_http2(clear):
    register_user1 = requests.post(f"{URL}/auth/register/v2", json={"email": "user1@gmail.com",
                                                                    "password": "password",  "name_first": "user1", "name_last": "surname"})
    assert register_user1.status_code == OK
    user1_token = register_user1.json()['token']
    register_user1.json()['auth_user_id']
    register_user2 = requests.post(f"{URL}/auth/register/v2", json={"email": "user2@gmail.com",
                                                                    "password": "password",  "name_first": "user2", "name_last": "surname"})
    assert register_user2.status_code == OK
    user2_token = register_user2.json()['token']
    register_user3 = requests.post(f"{URL}/auth/register/v2", json={"email": "user3@gmail.com",
                                                                    "password": "password",  "name_first": "user3", "name_last": "surname"})
    assert register_user3.status_code == OK
    user3_id = register_user3.json()['auth_user_id']
    user3_token = register_user3.json()['token']
    # user 2 makes a channel
    channel_info = requests.post(
        f"{URL}/channels/create/v2", json={"token": user2_token, "name": "channel", "is_public": True})
    assert channel_info.status_code == OK
    channel_id = channel_info.json()['channel_id']
    # user 3 and user 1 joins channel
    channel_join_return1 = requests.post(
        f"{URL}/channel/join/v2", json={"token": user1_token, "channel_id": channel_id})
    assert channel_join_return1.status_code == OK
    channel_join_return2 = requests.post(
        f"{URL}/channel/join/v2", json={"token": user3_token, "channel_id": channel_id})
    assert channel_join_return2.status_code == OK
    # user 1 leaves
    channel_leave = requests.post(
        f"{URL}/channel/leave/v1", json={'token': user1_token, 'channel_id': channel_id})
    assert channel_leave.status_code == OK
    # user 1 adds owner to user 3 raising access error
    addowner = requests.post(f"{URL}/channel/addowner/v1", json={
                             'token': user1_token, 'channel_id': channel_id, 'u_id': user3_id})
    assert addowner.status_code == ACCESSERROR


def test_global_owner_removesowner_but_not_in_channel_channel_removeowner_v1_http(clear):
    # register 3 users:
    register_user1 = requests.post(f"{URL}/auth/register/v2", json={"email": "user1@gmail.com",
                                                                    "password": "password",  "name_first": "user1", "name_last": "surname"})
    assert register_user1.status_code == OK
    user1_token = register_user1.json()['token']
    user1_id = register_user1.json()['auth_user_id']
    register_user2 = requests.post(f"{URL}/auth/register/v2", json={"email": "user2@gmail.com",
                                                                    "password": "password",  "name_first": "user2", "name_last": "surname"})
    assert register_user2.status_code == OK
    user2_token = register_user2.json()['token']
    register_user2.json()['auth_user_id']
    register_user3 = requests.post(f"{URL}/auth/register/v2", json={"email": "user3@gmail.com",
                                                                    "password": "password",  "name_first": "user3", "name_last": "surname"})
    assert register_user3.status_code == OK
    user3_id = register_user3.json()['auth_user_id']
    # user 2 makes channel
    channel_info = requests.post(
        f"{URL}/channels/create/v2", json={"token": user2_token, "name": "channel", "is_public": True})
    assert channel_info.status_code == OK
    channel_id = channel_info.json()['channel_id']
    # user 2 invites user 3
    channel_invite2 = requests.post(f"{URL}/channel/invite/v2", json={
                                    "token": user2_token, "channel_id": channel_id, "u_id": user3_id})
    assert channel_invite2.status_code == OK
    # user 2 makes user 3 owner
    addowner = requests.post(f"{URL}/channel/addowner/v1", json={
                             'token': user2_token, 'channel_id': channel_id, 'u_id': user3_id})
    assert addowner.status_code == OK
    # user 2 invites user 1
    channel_invite1 = requests.post(f"{URL}/channel/invite/v2", json={
                                    "token": user2_token, "channel_id": channel_id, "u_id": user1_id})
    assert channel_invite1.status_code == OK
    # user 1 leaves
    channel_leave = requests.post(
        f"{URL}/channel/leave/v1", json={'token': user1_token, 'channel_id': channel_id})
    assert channel_leave.status_code == OK
    # user 1 removes user 3 owner (ACCESSERROR)
    removeowner = requests.post(f"{URL}/channel/removeowner/v1", json={
                                'token': user1_token, 'channel_id': channel_id, 'u_id': user3_id})
    assert removeowner.status_code == ACCESSERROR

def test_channel_invite_notification_check(clear, u_id_1, u_id_2):
    channel_id_req = requests.post(f"{URL}/channels/create/v2", json={
        'token': u_id_1['token'], 'name': 'happytreefriends', 'is_public': True
    })
    assert channel_id_req.status_code == OK
    channel_id = json.loads(channel_id_req.text)['channel_id']

    invite = requests.post(f"{URL}/channel/invite/v2", json={
        'token': u_id_1['token'], 'channel_id': channel_id, 'u_id': u_id_2['auth_user_id']
    })
    assert invite.status_code == OK

    notifs = requests.get(
        f"{URL}/notifications/get/v1?token={u_id_2['token']}")
    assert notifs.status_code == OK

    notifs_list = notifs.json()['notifications']
    assert notifs_list == [{'channel_id': channel_id, 'dm_id': -1,
                            'notification_message': f"billthescienceguy added you to happytreefriends"}]

