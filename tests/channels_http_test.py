import pytest
import json
import requests
from src import config
BASE_ADDRESS = 'http://127.0.0.1'
BASE_PORT = config.port
BASE_URL = f"{BASE_ADDRESS}:{BASE_PORT}"
OK = 200
ACCESSERROR = 403
INPUTERROR = 400

@pytest.fixture
def clear():
    requests.delete(f"{BASE_URL}/clear/v1")
    
@pytest.fixture
def register_user1():
    response = requests.post(f"{BASE_URL}/auth/register/v2", json={'email': "third7678@gmail.com", 'password': "hello123", 'name_first': "Trent", 'name_last': "Arnold"})
    dict = json.loads(response.text)
    return dict
    
# test if channel name is too short (< 1 character)
def test_short_name_channel_create(clear, register_user1):
    response = requests.post(f"{BASE_URL}/channels/create/v2", json={'token': register_user1['token'], 'name': "", 'is_public': True})
    assert response.status_code == 400

# test if channel name is too long (> 20 characters)
def test_long_name_channel_create(clear, register_user1):
    response = requests.post(f"{BASE_URL}/channels/create/v2", json={'token': register_user1['token'], 'name': "averyverylongchannelname", 'is_public': True})
    assert response.status_code == 400

# test for if an invalid token is passed into the function
def test_invalid_token_channel_create(clear, register_user1):
    invalid_token = register_user1['token'] + 'd'
    response = requests.post(f"{BASE_URL}/channels/create/v2", json={'token': invalid_token, 'name': "channel", 'is_public': True})
    assert response.status_code == 403

# check correct implementation
def test_working_channel_create(clear, register_user1):
    rego_response = requests.post(f"{BASE_URL}/channels/create/v2", json={'token': register_user1['token'], 'name': "channel", 'is_public': True})
    resp = json.loads(rego_response.text)
    token = register_user1['token']
    channel_id = resp['channel_id']
    list_response = requests.get(f"{BASE_URL}/channels/listall/v2?token={token}")
    assert list_response.status_code == 200
    data = list_response.json()
    create_works = False
    for channel in data['channels']:
        if channel['channel_id'] == channel_id:
            create_works = True
    assert create_works == True

# CHANNELS/LISTALL/V2
def test_channels_listall_v2_http(clear):
    # register a user
    register_user = requests.post(f"{BASE_URL}/auth/register/v2", json = {"email": "email@gmail.com", "password": "password",  "name_first": "first", "name_last": "last"})
    assert register_user.status_code == OK
    register_user_return = register_user.json()
    register_token = register_user_return['token']

    # tests channels/listall/v2 for empty list
    response = requests.get(f"{BASE_URL}/channels/listall/v2" + f"?token={register_token}")
    assert response.status_code == OK # test status
    assert response.json() == {'channels': []} # testing webpage is empty after clear

    # log the user in
    login_user = requests.post(f"{BASE_URL}/auth/login/v2", json = {"email": "email@gmail.com", "password": "password"})
    assert login_user.status_code == OK
    login_return = login_user.json()
    login_token = login_return['token']

    # user creates a channel
    channel_info = requests.post(f"{BASE_URL}/channels/create/v2", json = {"token": login_token, "name": "channel_name", "is_public": True })
    assert channel_info.status_code == OK
    channel_id = channel_info.json()


    # test to see if channels/listall/v2 returns a list of dictionary with that channel id and name
    listall_data = requests.get(f"{BASE_URL}/channels/listall/v2" + f"?token={login_token}")
    assert listall_data.status_code == OK
    assert listall_data.json() == {"channels" : [
        {
            "channel_id": channel_id['channel_id'],
            "name": "channel_name"
        },
    ]}


def test_invalid_channels_listall_v2_http(clear):
    # register a user
    register_user = requests.post(f"{BASE_URL}/auth/register/v2", json = {"email": "email@gmail.com", "password": "password",  "name_first": "first", "name_last": "last"})
    assert register_user.status_code == OK

    # log the user in
    login_user = requests.post(f"{BASE_URL}/auth/login/v2", json = {"email": "email@gmail.com", "password": "password"})
    assert login_user.status_code == OK
    login_return = login_user.json()
    login_token = login_return['token']
    invalid_token = f"{login_token}1212"

    # user creates a channel
    channel_info = requests.post(f"{BASE_URL}/channels/create/v2", json = {"token": login_token, "name": "channel_name", "is_public": True })
    assert channel_info.status_code == OK

    listall_data = requests.get(f"{BASE_URL}/channels/listall/v2" + f"?token={invalid_token}")
    assert listall_data.status_code == ACCESSERROR


# CHANNELS/LIST/V2

# test for invalid token in channels_list_v2
def test_invalid_token_channels_list_http(clear):
    # register a user
    register_user = requests.post(f"{BASE_URL}/auth/register/v2", json = {"email": "email@gmail.com", "password": "password",  "name_first": "first", "name_last": "last"})
    assert register_user.status_code == OK

    # log the user in
    login_user = requests.post(f"{BASE_URL}/auth/login/v2", json = {"email": "email@gmail.com", "password": "password"})
    assert login_user.status_code == OK
    login_return = login_user.json()
    login_token = login_return['token']
    invalid_token = f"{login_token}1212"

    # user creates a channel
    channel_info = requests.post(f"{BASE_URL}/channels/create/v2", json = {"token": login_token, "name": "channel_name", "is_public": True })
    assert channel_info.status_code == OK

    listall_data = requests.get(f"{BASE_URL}/channels/list/v2" + f"?token={invalid_token}")
    assert listall_data.status_code == ACCESSERROR

# test if channels/list/v2 works for no members in channel
def test_user_not_part_of_channel_channels_list_v2_http(clear):
    # register user
    register_user = requests.post(f"{BASE_URL}/auth/register/v2", json = {"email": "email@gmail.com", "password": "password",  "name_first": "first", "name_last": "last"})
    assert register_user.status_code == OK
    # log in user
    login_user = requests.post(f"{BASE_URL}/auth/login/v2", json = {"email": "email@gmail.com", "password": "password"})
    assert login_user.status_code == OK
    login_return = login_user.json()
    login_token = login_return['token']

    list_data = requests.get(f"{BASE_URL}/channels/list/v2" + f"?token={login_token}")
    assert list_data.status_code == OK
    assert list_data.json() == {'channels': []}

# test if channels/list/v2 works for member creating channel
def test_user_creating_channel_channels_list_v2_http(clear):
    # register user
    register_user = requests.post(f"{BASE_URL}/auth/register/v2", json = {"email": "email@gmail.com", "password": "password",  "name_first": "first", "name_last": "last"})
    assert register_user.status_code == OK
    # log in user
    login_user = requests.post(f"{BASE_URL}/auth/login/v2", json = {"email": "email@gmail.com", "password": "password"})
    assert login_user.status_code == OK
    login_return = login_user.json()
    login_token = login_return['token']
    # create channel
    channel_info = requests.post(f"{BASE_URL}/channels/create/v2", json = {"token": login_token, "name": "channel_name", "is_public": True })
    assert channel_info.status_code == OK

    list_data = requests.get(f"{BASE_URL}/channels/list/v2" + f"?token={login_token}")
    assert list_data.status_code == OK
    assert len(list_data.json()['channels']) == 1

# # test if channels/list/v2 works for member invited
def test_user_invited_channels_list_v2_http(clear):
    # register owner
    register_owner = requests.post(f"{BASE_URL}/auth/register/v2", json = {"email": "email@gmail.com", "password": "password",  "name_first": "first", "name_last": "last"})
    assert register_owner.status_code == OK
    # log in owner
    login_owner = requests.post(f"{BASE_URL}/auth/login/v2", json = {"email": "email@gmail.com", "password": "password"})
    assert login_owner.status_code == OK
    owner_return = login_owner.json()
    owner_token = owner_return['token']

    # register joiner
    register_joiner = requests.post(f"{BASE_URL}/auth/register/v2", json = {"email": "joiner@gmail.com", "password": "password",  "name_first": "first", "name_last": "last"})
    assert register_joiner.status_code == OK
    # log in joiner
    login_joiner = requests.post(f"{BASE_URL}/auth/login/v2", json = {"email": "joiner@gmail.com", "password": "password"})
    assert login_joiner.status_code == OK
    joiner_return = login_joiner.json()
    joiner_token = joiner_return['token']
    joiner_id = joiner_return['auth_user_id']

    # owner creates channel
    channel_info = requests.post(f"{BASE_URL}/channels/create/v2", json = {"token": owner_token, "name": "channel_name", "is_public": True })
    assert channel_info.status_code == OK
    channel_id = channel_info.json()['channel_id']

    invite_response = requests.post(f"{BASE_URL}/channel/invite/v2", json = {"token": owner_token, "channel_id": channel_id, "u_id": joiner_id})
    assert invite_response.status_code == OK

    list_data = requests.get(f"{BASE_URL}/channels/list/v2" + f"?token={joiner_token}")
    assert list_data.status_code == OK
    assert len(list_data.json()['channels']) == 1

# # test if channel list v2 works for user joining
def test_user_joins_channels_list_v2_http(clear):
    # register owner
    register_owner = requests.post(f"{BASE_URL}/auth/register/v2", json = {"email": "email@gmail.com", "password": "password",  "name_first": "first", "name_last": "last"})
    assert register_owner.status_code == OK
    # log in owner
    login_owner = requests.post(f"{BASE_URL}/auth/login/v2", json = {"email": "email@gmail.com", "password": "password"})
    assert login_owner.status_code == OK
    owner_return = login_owner.json()
    owner_token = owner_return['token']

    # register joiner
    register_joiner = requests.post(f"{BASE_URL}/auth/register/v2", json = {"email": "joiner@gmail.com", "password": "password",  "name_first": "first", "name_last": "last"})
    assert register_joiner.status_code == OK
    # log in joiner
    login_joiner = requests.post(f"{BASE_URL}/auth/login/v2", json = {"email": "joiner@gmail.com", "password": "password"})
    assert login_joiner.status_code == OK
    joiner_return = login_joiner.json()
    joiner_token = joiner_return['token']

    # owner creates channel
    channel_info = requests.post(f"{BASE_URL}/channels/create/v2", json = {"token": owner_token, "name": "channel_name", "is_public": True })
    assert channel_info.status_code == OK
    channel_id = channel_info.json()['channel_id']

    channel_join = requests.post(f"{BASE_URL}/channel/join/v2", json = {"token": joiner_token, "channel_id": channel_id})
    assert channel_join.status_code == OK

    list_data = requests.get(f"{BASE_URL}/channels/list/v2" + f"?token={joiner_token}")
    assert list_data.status_code == OK
    assert len(list_data.json()['channels']) == 1

# test to see if channels/list/v2 works for user with global perms joining a private channel
def test_global_perm_user_joins_private_channel_channels_list_v2_http(clear):
    # register perm
    register_perm = requests.post(f"{BASE_URL}/auth/register/v2", json = {"email": "perm@gmail.com", "password": "password",  "name_first": "first", "name_last": "last"})
    assert register_perm.status_code == OK
    # log in perm
    login_perm = requests.post(f"{BASE_URL}/auth/login/v2", json = {"email": "perm@gmail.com", "password": "password"})
    assert login_perm.status_code == OK
    perm_return = login_perm.json()
    perm_token = perm_return['token']

    # register owner
    register_owner = requests.post(f"{BASE_URL}/auth/register/v2", json = {"email": "email@gmail.com", "password": "password",  "name_first": "first", "name_last": "last"})
    assert register_owner.status_code == OK
    # log in owner
    login_owner = requests.post(f"{BASE_URL}/auth/login/v2", json = {"email": "email@gmail.com", "password": "password"})
    assert login_owner.status_code == OK
    owner_return = login_owner.json()
    owner_token = owner_return['token']

    # owner creates channel
    channel_info = requests.post(f"{BASE_URL}/channels/create/v2", json = {"token": owner_token, "name": "channel_name", "is_public": False })
    assert channel_info.status_code == OK
    channel_id = channel_info.json()['channel_id']

    channel_join = requests.post(f"{BASE_URL}/channel/join/v2", json = {"token": perm_token, "channel_id": channel_id})
    assert channel_join.status_code == OK

    list_data = requests.get(f"{BASE_URL}/channels/list/v2"+f"?token={perm_token}")
    assert len(list_data.json()['channels']) == 1

 

# test to see if channels/list/v2 works for a person invited by a non-owner to a private channel
def test_user_invited_to_private_channel_by_non_owner_channels_list_v2_http(clear):
    # register owner
    register_owner = requests.post(f"{BASE_URL}/auth/register/v2", json = {"email": "email@gmail.com", "password": "password",  "name_first": "first", "name_last": "last"})
    assert register_owner.status_code == OK
    # log in owner
    login_owner = requests.post(f"{BASE_URL}/auth/login/v2", json = {"email": "email@gmail.com", "password": "password"})
    assert login_owner.status_code == OK
    owner_return = login_owner.json()
    owner_token = owner_return['token']

    # register joiner
    register_joiner = requests.post(f"{BASE_URL}/auth/register/v2", json = {"email": "joiner@gmail.com", "password": "password",  "name_first": "first", "name_last": "last"})
    assert register_joiner.status_code == OK
    # log in joiner
    login_joiner = requests.post(f"{BASE_URL}/auth/login/v2", json = {"email": "joiner@gmail.com", "password": "password"})
    assert login_joiner.status_code == OK
    joiner_return = login_joiner.json()
    joiner_token = joiner_return['token']
    joiner_id = joiner_return['auth_user_id']

    # register inviter
    register_inviter = requests.post(f"{BASE_URL}/auth/register/v2", json = {"email": "inviter@gmail.com", "password": "password",  "name_first": "first", "name_last": "last"})
    assert register_inviter.status_code == OK
    # log in joiner
    login_inviter = requests.post(f"{BASE_URL}/auth/login/v2", json = {"email": "inviter@gmail.com", "password": "password"})
    assert login_inviter.status_code == OK
    inviter_return = login_inviter.json()
    inviter_token = inviter_return['token']
    inviter_id = inviter_return['auth_user_id']

    # owner creates channel
    channel_info = requests.post(f"{BASE_URL}/channels/create/v2", json = {"token": owner_token, "name": "channel_name", "is_public": False })
    assert channel_info.status_code == OK
    channel_id = channel_info.json()['channel_id']

    # owner of private channel invites inviter
    channel_invite = requests.post(f"{BASE_URL}/channel/invite/v2", json = {"token": owner_token, "channel_id": channel_id,"u_id": inviter_id})
    assert channel_invite.status_code == OK
    # inviter invites joiner
    channel_invite2 = requests.post(f"{BASE_URL}/channel/invite/v2", json = {"token": inviter_token, "channel_id": channel_id, "u_id": joiner_id})
    assert channel_invite2.status_code == OK

    list_data = requests.get(f"{BASE_URL}/channels/list/v2" + f"?token={joiner_token}")
    assert list_data.status_code == OK
    assert len(list_data.json()['channels']) == 1
