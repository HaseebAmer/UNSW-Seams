from lib2to3.pgen2.token import OP
import pytest
import json
import requests
from src import config

BASE_ADDRESS = 'http://127.0.0.1'
BASE_PORT = config.port
url = f"{BASE_ADDRESS}:{BASE_PORT}"

OK = 200


@pytest.fixture
def clear():
    requests.delete(f"{url}/clear/v1")


@pytest.fixture
def u_id_1():
    auth_user_id_json = requests.post(f"{url}/auth/register/v2", json={
        "email": "bill.nye@gmail.com", "password": "thescienceguy", "name_first": "Bill", "name_last": "Thescienceguy"
    })
    assert auth_user_id_json.status_code == OK
    return json.loads(auth_user_id_json.text)


@pytest.fixture
def u_id_2():
    u_id_json = requests.post(f"{url}/auth/register/v2", json={
        'email': "roshan.m@gmail.com", 'password': "wowzers123", 'name_first': "Roshan", 'name_last': "Mujeeb"
    })
    assert u_id_json.status_code == OK
    return json.loads(u_id_json.text)


@pytest.fixture
def u_id_3():
    u_id_json = requests.post(f"{url}/auth/register/v2", json={
        'email': "bambabalaklava@gmail.com", 'password': "rdjisironmAN12", 'name_first': "ghostface", 'name_last': "killah"
    })
    assert u_id_json.status_code == OK
    return json.loads(u_id_json.text)


def test_message_send_invalid_channel_id(clear, u_id_1):
    ch_dict = requests.post(f"{url}/channels/create/v2", json={
        'token': u_id_1['token'], 'name': 'happytreefriends', 'is_public': True
    })
    assert ch_dict.status_code == OK
    msg_send = requests.post(f"{url}/message/send/v1", json={
        'token': u_id_1['token'], 'channel_id': 3, 'message': "hey!"
    })
    assert msg_send.status_code == 400


def test_message_send_size_zero(clear, u_id_1):
    ch_dict = requests.post(f"{url}/channels/create/v2", json={
        'token': u_id_1['token'], 'name': 'happytreefriends', 'is_public': True
    })
    assert ch_dict.status_code == OK
    channel_id = ch_dict.json()['channel_id']
    msg_send = requests.post(f"{url}/message/send/v1", json={
        'token': u_id_1['token'], 'channel_id': channel_id, 'message': ""
    })
    assert msg_send.status_code == 400


def test_message_send_size_large(clear, u_id_1):
    ch_dict = requests.post(f"{url}/channels/create/v2", json={
        'token': u_id_1['token'], 'name': 'happytreefriends', 'is_public': True
    })
    assert ch_dict.status_code == OK
    channel_id = ch_dict.json()['channel_id']
    long_msg = "a" * 1000
    msg_send = requests.post(f"{url}/message/send/v1", json={
        'token': u_id_1['token'], 'channel_id': channel_id, 'message': long_msg
    })
    assert msg_send.status_code == OK


def test_message_send_oversized(clear, u_id_1):
    ch_dict = requests.post(f"{url}/channels/create/v2", json={
        'token': u_id_1['token'], 'name': 'happytreefriends', 'is_public': True
    })
    assert ch_dict.status_code == OK
    channel_id = ch_dict.json()['channel_id']
    long_msg = "a" * 1001
    msg_send = requests.post(f"{url}/message/send/v1", json={
        'token': u_id_1['token'], 'channel_id': channel_id, 'message': long_msg
    })
    assert msg_send.status_code == 400


def test_message_send_correct_functioning(clear, u_id_1):
    ch_dict = requests.post(f"{url}/channels/create/v2", json={
        'token': u_id_1['token'], 'name': 'happytreefriends', 'is_public': True
    })
    assert ch_dict.status_code == OK
    channel_id = ch_dict.json()['channel_id']
    msg_send = requests.post(f"{url}/message/send/v1", json={
        'token': u_id_1['token'], 'channel_id': channel_id, 'message': "hey"
    })
    assert msg_send.status_code == OK
    long_msg = "a" * 1000
    msg_long_send = requests.post(f"{url}/message/send/v1", json={
        'token': u_id_1['token'], 'channel_id': channel_id, 'message': long_msg
    })
    assert msg_long_send.status_code == OK
    message_list = requests.get(
        f"{url}/channel/messages/v2?token={u_id_1['token']}&channel_id={channel_id}&start=0")
    assert message_list.status_code == OK
    messages = message_list.json()
    assert messages['start'] == 0
    assert messages['end'] == -1
    assert len(messages['messages']) == 2
    assert messages['messages'][0]['message'] == long_msg
    assert messages['messages'][1]['message'] == "hey"


def test_message_send_unauthorised_user(clear, u_id_1, u_id_2):
    ch_dict = requests.post(f"{url}/channels/create/v2", json={
        'token': u_id_1['token'], 'name': 'happytreefriends', 'is_public': True
    })
    assert ch_dict.status_code == OK
    channel_id = ch_dict.json()['channel_id']
    msg_send = requests.post(f"{url}/message/send/v1", json={
        'token': u_id_2['token'], 'channel_id': channel_id, 'message': "hey"
    })
    assert msg_send.status_code == 403


def test_message_send_invalid_token(clear, u_id_1):
    ch_dict = requests.post(f"{url}/channels/create/v2", json={
        'token': u_id_1['token'], 'name': 'happytreefriends', 'is_public': True
    })
    assert ch_dict.status_code == OK
    channel_id = ch_dict.json()['channel_id']
    msg_send = requests.post(f"{url}/message/send/v1", json={
        'token': f"{u_id_1['token']}69", 'channel_id': channel_id, 'message': "hey"
    })
    assert msg_send.status_code == 403


def test_message_edit_overlong(clear, u_id_1):
    ch_dict = requests.post(f"{url}/channels/create/v2", json={
        'token': u_id_1['token'], 'name': 'happytreefriends', 'is_public': True
    })
    assert ch_dict.status_code == OK
    channel_id = ch_dict.json()['channel_id']
    msg_send = requests.post(f"{url}/message/send/v1", json={
        'token': u_id_1['token'], 'channel_id': channel_id, 'message': "hey"
    })
    assert msg_send.status_code == OK
    message_id = msg_send.json()['message_id']
    long_msg = "a" * 1001
    msg_edit = requests.put(f"{url}/message/edit/v1", json={
        'token': u_id_1['token'], 'message_id': message_id, 'message': long_msg
    })
    assert msg_edit.status_code == 400


def test_message_edit_overlong_dm(clear, u_id_1, u_id_2):
    dm_dict = requests.post(f"{url}/dm/create/v1", json={
        'token': u_id_1['token'], 'u_ids': [u_id_2['auth_user_id']]
    })
    assert dm_dict.status_code == OK
    dm_id = dm_dict.json()['dm_id']
    msg_send = requests.post(f"{url}/message/senddm/v1", json={
        'token': u_id_1['token'], 'dm_id': dm_id, 'message': "hey"
    })
    assert msg_send.status_code == OK
    message_id = msg_send.json()['message_id']
    msg_edit = requests.put(f"{url}/message/edit/v1", json={
        'token': u_id_1['token'], 'message_id': message_id, 'message': "z" * 1002
    })
    assert msg_edit.status_code == 400


def test_message_edit_invalid_msg_id(clear, u_id_1):
    ch_dict = requests.post(f"{url}/channels/create/v2", json={
        'token': u_id_1['token'], 'name': 'happytreefriends', 'is_public': True
    })
    assert ch_dict.status_code == OK
    channel_id = ch_dict.json()['channel_id']
    msg_send = requests.post(f"{url}/message/send/v1", json={
        'token': u_id_1['token'], 'channel_id': channel_id, 'message': "hey"
    })
    assert msg_send.status_code == OK
    msg_edit = requests.put(f"{url}/message/edit/v1", json={
        'token': u_id_1['token'], 'message_id': -1, 'message': "heya"
    })
    assert msg_edit.status_code == 400


def test_message_edit_invalid_msg_id_dm(clear, u_id_1):
    dm_dict = requests.post(f"{url}/dm/create/v1", json={
        'token': u_id_1['token'], 'u_ids': []
    })
    assert dm_dict.status_code == OK
    dm_id = dm_dict.json()['dm_id']
    msg_send = requests.post(f"{url}/message/senddm/v1", json={
        'token': u_id_1['token'], 'dm_id': dm_id, 'message': "hey"
    })
    assert msg_send.status_code == OK
    msg_edit = requests.put(f"{url}/message/edit/v1", json={
        'token': u_id_1['token'], 'message_id': -1, 'message': "huh"
    })
    assert msg_edit.status_code == 400


def test_message_edit_access_error(clear, u_id_1, u_id_2):
    ch_dict = requests.post(f"{url}/channels/create/v2", json={
        'token': u_id_1['token'], 'name': 'happytreefriends', 'is_public': True
    })
    assert ch_dict.status_code == OK
    channel_id = ch_dict.json()['channel_id']
    join = requests.post(f"{url}/channel/join/v2",
                         json={'token': u_id_2['token'], 'channel_id': channel_id})
    assert join.status_code == OK
    msg_send = requests.post(f"{url}/message/send/v1", json={
        'token': u_id_1['token'], 'channel_id': channel_id, 'message': "hey"
    })
    assert msg_send.status_code == OK
    message_id = msg_send.json()['message_id']
    msg_edit = requests.put(f"{url}/message/edit/v1", json={
        'token': u_id_2['token'], 'message_id': message_id, 'message': "heya"
    })
    assert msg_edit.status_code == 403


def test_message_edit_access_error_dm(clear, u_id_1, u_id_2):
    dm_dict = requests.post(f"{url}/dm/create/v1", json={
        'token': u_id_1['token'], 'u_ids': [u_id_2['auth_user_id']]
    })
    assert dm_dict.status_code == OK
    dm_id = dm_dict.json()['dm_id']
    msg_send = requests.post(f"{url}/message/senddm/v1", json={
        'token': u_id_1['token'], 'dm_id': dm_id, 'message': "hey"
    })
    assert msg_send.status_code == OK
    message_id = msg_send.json()['message_id']
    msg_edit = requests.put(f"{url}/message/edit/v1", json={
        'token': u_id_2['token'], 'message_id': message_id, 'message': "wubawubawoomwoom"
    })
    assert msg_edit.status_code == 403


def test_message_edit_correct_delete(clear, u_id_1):
    ch_dict = requests.post(f"{url}/channels/create/v2", json={
        'token': u_id_1['token'], 'name': 'happytreefriends', 'is_public': True
    })
    assert ch_dict.status_code == OK
    channel_id = ch_dict.json()['channel_id']
    msg_send = requests.post(f"{url}/message/send/v1", json={
        'token': u_id_1['token'], 'channel_id': channel_id, 'message': "hey"
    })
    assert msg_send.status_code == OK
    message_id = msg_send.json()['message_id']
    msg_edit = requests.put(f"{url}/message/edit/v1", json={
        'token': u_id_1['token'], 'message_id': message_id, 'message': ""
    })
    assert msg_edit.status_code == OK
    message_list = requests.get(
        f"{url}/channel/messages/v2?token={u_id_1['token']}&channel_id={channel_id}&start=0")
    assert message_list.status_code == OK
    messages = message_list.json()
    assert messages == {'messages': [], 'start': 0, 'end': -1}


def test_message_edit_correct_delete_dm(clear, u_id_1, u_id_2):
    dm_dict = requests.post(f"{url}/dm/create/v1", json={
        'token': u_id_1['token'], 'u_ids': [u_id_2['auth_user_id']]
    })
    assert dm_dict.status_code == OK
    dm_id = dm_dict.json()['dm_id']
    msg_send = requests.post(f"{url}/message/senddm/v1", json={
        'token': u_id_1['token'], 'dm_id': dm_id, 'message': "hey"
    })
    assert msg_send.status_code == OK
    message_id = msg_send.json()['message_id']
    requests.put(f"{url}/message/edit/v1", json={
        'token': u_id_1['token'], 'message_id': message_id, 'message': ""
    })
    message_list = requests.get(
        f"{url}/dm/messages/v1?token={u_id_1['token']}&dm_id={dm_id}&start=0")
    assert message_list.status_code == OK
    message = message_list.json()['messages']
    assert len(message) == 0
    # ADD DM MESSAGES PART


def test_message_edit_correct(clear, u_id_1):
    ch_dict = requests.post(f"{url}/channels/create/v2", json={
        'token': u_id_1['token'], 'name': 'happytreefriends', 'is_public': True
    })
    assert ch_dict.status_code == OK
    channel_id = ch_dict.json()['channel_id']
    msg_send = requests.post(f"{url}/message/send/v1", json={
        'token': u_id_1['token'], 'channel_id': channel_id, 'message': "hey"
    })
    assert msg_send.status_code == OK
    message_id = msg_send.json()['message_id']
    msg_edit = requests.put(f"{url}/message/edit/v1", json={
        'token': u_id_1['token'], 'message_id': message_id, 'message': "wassupppp!!"
    })
    assert msg_edit.status_code == OK
    message_list = requests.get(
        f"{url}/channel/messages/v2?token={u_id_1['token']}&channel_id={channel_id}&start=0")
    assert message_list.status_code == OK
    messages = message_list.json()
    assert messages['messages'][0]['message'] == "wassupppp!!"


def test_message_edit_correct_dm(clear, u_id_1, u_id_2):
    dm_dict = requests.post(f"{url}/dm/create/v1", json={
        'token': u_id_1['token'], 'u_ids': [u_id_2['auth_user_id']]
    })
    assert dm_dict.status_code == OK
    dm_id = dm_dict.json()['dm_id']
    msg_send = requests.post(f"{url}/message/senddm/v1", json={
        'token': u_id_1['token'], 'dm_id': dm_id, 'message': "hey"
    })
    assert msg_send.status_code == OK
    message_id = msg_send.json()['message_id']
    requests.put(f"{url}/message/edit/v1", json={
        'token': u_id_1['token'], 'message_id': message_id, 'message': "HILLARYBEN"
    })
    message_list = requests.get(
        f"{url}/dm/messages/v1?token={u_id_1['token']}&dm_id={dm_id}&start=0")
    assert message_list.status_code == OK
    messages = message_list.json()['messages']
    assert len(messages) == 1
    assert messages[0]['message'] == "HILLARYBEN"
    # ADD DM MESSAGES PART


def test_message_edit_invalid_token(clear, u_id_1):
    ch_dict = requests.post(f"{url}/channels/create/v2", json={
        'token': u_id_1['token'], 'name': 'happytreefriends', 'is_public': True
    })
    assert ch_dict.status_code == OK
    channel_id = ch_dict.json()['channel_id']
    msg_send = requests.post(f"{url}/message/send/v1", json={
        'token': u_id_1['token'], 'channel_id': channel_id, 'message': "hey"
    })
    assert msg_send.status_code == OK
    message_id = msg_send.json()['message_id']
    msg_edit = requests.put(f"{url}/message/edit/v1", json={
        'token': -1, 'message_id': message_id, 'message': "wassupppp!!"
    })
    assert msg_edit.status_code == 403


def test_message_edit_global_correct(clear, u_id_1, u_id_2):
    ch_dict = requests.post(f"{url}/channels/create/v2", json={
        'token': u_id_2['token'], 'name': 'happytreefriends', 'is_public': False
    })
    assert ch_dict.status_code == OK
    channel_id = ch_dict.json()['channel_id']
    resp = requests.post(f"{url}/channel/invite/v2", json={
        'token': u_id_2['token'], 'channel_id': channel_id, 'u_id': u_id_1['auth_user_id']
    })
    assert resp.status_code == OK
    msg_send = requests.post(f"{url}/message/send/v1", json={
        'token': u_id_2['token'], 'channel_id': channel_id, 'message': "hey"
    })
    assert msg_send.status_code == OK
    message_id = msg_send.json()['message_id']
    msg_edit = requests.put(f"{url}/message/edit/v1", json={
        'token': u_id_1['token'], 'message_id': message_id, 'message': "wassupppp!!"
    })
    assert msg_edit.status_code == OK
    message_list = requests.get(
        f"{url}/channel/messages/v2?token={u_id_1['token']}&channel_id={channel_id}&start=0")
    assert message_list.status_code == OK
    messages = message_list.json()
    assert messages['messages'][0]['message'] == "wassupppp!!"


def test_message_senddm_invalid_dmid(clear, u_id_1):
    dm_dict = requests.post(f"{url}/dm/create/v1", json={
        'token': u_id_1['token'], 'u_ids': []
    })
    assert dm_dict.status_code == OK
    msg_send = requests.post(f"{url}/message/senddm/v1", json={
        'token': u_id_1['token'], 'dm_id': -1, 'message': "hey"
    })
    assert msg_send.status_code == 400


def test_message_senddm_undersized(clear, u_id_1):
    dm_dict = requests.post(f"{url}/dm/create/v1", json={
        'token': u_id_1['token'], 'u_ids': []
    })
    assert dm_dict.status_code == OK
    dm_id = dm_dict.json()['dm_id']
    msg_send = requests.post(f"{url}/message/senddm/v1", json={
        'token': u_id_1['token'], 'dm_id': dm_id, 'message': ""
    })
    assert msg_send.status_code == 400


def test_message_senddm_oversized(clear, u_id_1):
    dm_dict = requests.post(f"{url}/dm/create/v1", json={
        'token': u_id_1['token'], 'u_ids': []
    })
    assert dm_dict.status_code == OK
    dm_id = dm_dict.json()['dm_id']
    msg_send = requests.post(f"{url}/message/senddm/v1", json={
        'token': u_id_1['token'], 'dm_id': dm_id, 'message': "a" * 1001
    })
    assert msg_send.status_code == 400


def test_message_senddm_invalid_token(clear, u_id_1):
    dm_dict = requests.post(f"{url}/dm/create/v1", json={
        'token': u_id_1['token'], 'u_ids': []
    })
    assert dm_dict.status_code == OK
    dm_id = dm_dict.json()['dm_id']
    msg_send = requests.post(f"{url}/message/senddm/v1", json={
        'token': -1, 'dm_id': dm_id, 'message': "a message duh"
    })
    assert msg_send.status_code == 403


def test_message_senddm_unauth_token(clear, u_id_1, u_id_2):
    dm_dict = requests.post(f"{url}/dm/create/v1", json={
        'token': u_id_1['token'], 'u_ids': []
    })
    assert dm_dict.status_code == OK
    dm_id = dm_dict.json()['dm_id']
    msg_send = requests.post(f"{url}/message/senddm/v1", json={
        'token': u_id_2['token'], 'dm_id': dm_id, 'message': "a message duh"
    })
    assert msg_send.status_code == 403


def test_message_senddm_correct_functioning(clear, u_id_1, u_id_2):
    dm_dict = requests.post(f"{url}/dm/create/v1", json={
        'token': u_id_1['token'], 'u_ids': [u_id_2['auth_user_id']]
    })
    assert dm_dict.status_code == OK
    dm_id = dm_dict.json()['dm_id']
    for i in range(2):
        msg_send = requests.post(f"{url}/message/senddm/v1", json={
            'token': u_id_2['token'], 'dm_id': dm_id, 'message': f"{i}"
        })
        assert msg_send.status_code == OK
    msg_list = requests.get(
        f"{url}/dm/messages/v1?token={u_id_1['token']}&dm_id={dm_id}&start=0")
    assert msg_list.status_code == OK
    msg = msg_list.json()
    assert len(msg['messages']) == 2
    assert msg['start'] == 0
    assert msg['end'] == -1
    assert msg['messages'][0]['message'] == "1"
    assert msg['messages'][1]['message'] == "0"
# MESSAGE REMOVE


def test_message_remove_v1_invalid_msg_id(clear, u_id_1):
    ch_dict = requests.post(f"{url}/channels/create/v2", json={
        'token': u_id_1['token'], 'name': 'happytreefriends', 'is_public': True
    })
    assert ch_dict.status_code == OK
    channel_id = ch_dict.json()['channel_id']
    msg_send = requests.post(f"{url}/message/send/v1", json={
        'token': u_id_1['token'], 'channel_id': channel_id, 'message': "hey"
    })
    assert msg_send.status_code == OK
    # message_id = msg_send.json()['message_id']
    remove = requests.delete(f"{url}/message/remove/v1", json={
        'token': u_id_1['token'], 'message_id': -1
    })
    assert remove.status_code == 400


def test_message_remove_v1_invalid_msg_id_dm(clear, u_id_1):
    dm_dict = requests.post(f"{url}/dm/create/v1", json={
        'token': u_id_1['token'], 'u_ids': []
    })
    assert dm_dict.status_code == OK
    dm_id = dm_dict.json()['dm_id']
    requests.post(f"{url}/message/senddm/v1", json={
        'token': u_id_1['token'], 'dm_id': dm_id, 'message': "baha"
    })
    remove = requests.delete(f"{url}/message/remove/v1", json={
        'token': u_id_1['token'], 'message_id': -1
    })
    assert remove.status_code == 400


def test_message_remove_unauth_user_no_permissions(clear, u_id_1, u_id_2):
    ch_dict = requests.post(f"{url}/channels/create/v2", json={
        'token': u_id_1['token'], 'name': 'happytreefriends', 'is_public': True
    })
    assert ch_dict.status_code == OK
    channel_id = ch_dict.json()['channel_id']
    join = requests.post(f"{url}/channel/join/v2",
                         json={'token': u_id_2['token'], 'channel_id': channel_id})
    assert join.status_code == OK

    msg_send = requests.post(f"{url}/message/send/v1", json={
        'token': u_id_1['token'], 'channel_id': channel_id, 'message': "hey"
    })
    assert msg_send.status_code == OK
    message_id = msg_send.json()['message_id']
    delete = requests.delete(f"{url}/message/remove/v1", json={
        "token": u_id_2['token'], 'message_id': message_id
    })
    assert delete.status_code == 403


def test_message_remove_unauth_user_dm(clear, u_id_1, u_id_2):
    dm_dict = requests.post(f"{url}/dm/create/v1", json={
        'token': u_id_1['token'], 'u_ids': [u_id_2['auth_user_id']]
    })
    assert dm_dict.status_code == OK
    dm_id = dm_dict.json()['dm_id']
    msg_send = requests.post(f"{url}/message/senddm/v1", json={
        'token': u_id_1['token'], 'dm_id': dm_id, 'message': "wazzupsizzurp!"
    })
    assert msg_send.status_code == OK
    message_id = msg_send.json()['message_id']
    remove = requests.delete(f"{url}/message/remove/v1", json={
        'token': u_id_2['token'], 'message_id': message_id
    })
    assert remove.status_code == 403


def test_message_remove_unauth_user_dm_2(clear, u_id_1, u_id_2):
    dm_dict = requests.post(f"{url}/dm/create/v1", json={
        'token': u_id_1['token'], 'u_ids': []
    })
    assert dm_dict.status_code == OK
    dm_id = dm_dict.json()['dm_id']
    msg_send = requests.post(f"{url}/message/senddm/v1", json={
        'token': u_id_1['token'], 'dm_id': dm_id, 'message': "sizzurpinmycup!!"
    })
    assert msg_send.status_code == OK
    message_id = msg_send.json()['message_id']
    remove = requests.delete(f"{url}/message/remove/v1", json={
        'token': u_id_2['token'], 'message_id': message_id
    })
    assert remove.status_code == 403


def test_message_remove_correct(clear, u_id_1):
    ch_dict = requests.post(f"{url}/channels/create/v2", json={
        'token': u_id_1['token'], 'name': 'happytreefriends', 'is_public': True
    })
    assert ch_dict.status_code == OK
    channel_id = ch_dict.json()['channel_id']
    msg_send = requests.post(f"{url}/message/send/v1", json={
        'token': u_id_1['token'], 'channel_id': channel_id, 'message': "hey"
    })
    assert msg_send.status_code == OK
    message_id = msg_send.json()['message_id']
    delete = requests.delete(f"{url}/message/remove/v1", json={
        'token': u_id_1['token'], 'message_id': message_id
    })
    assert delete.status_code == OK
    msg_list = requests.get(
        f"{url}/channel/messages/v2?token={u_id_1['token']}&channel_id={channel_id}&start=0")
    assert msg_list.status_code == OK
    messages = msg_list.json()
    assert messages == {'messages': [], 'start': 0, 'end': -1}


def test_message_remove_comprehensive(clear, u_id_1):
    ch_dict = requests.post(f"{url}/channels/create/v2", json={
        'token': u_id_1['token'], 'name': 'happytreefriends', 'is_public': True
    })
    assert ch_dict.status_code == OK
    channel_id = ch_dict.json()['channel_id']
    for i in range(5):
        msg_send = requests.post(f"{url}/message/send/v1", json={
            'token': u_id_1['token'], 'channel_id': channel_id, 'message': f"hey{i}"
        })
        message_id = msg_send.json()['message_id']
        delete = requests.delete(f"{url}/message/remove/v1", json={
            'token': u_id_1['token'], 'message_id': message_id
        })
    assert delete.status_code == OK
    msg_list = requests.get(
        f"{url}/channel/messages/v2?token={u_id_1['token']}&channel_id={channel_id}&start=0")
    assert msg_list.status_code == OK
    messages = msg_list.json()
    assert messages == {'messages': [], 'start': 0, 'end': -1}


def test_message_remove_correct_dm(clear, u_id_1):
    dm_dict = requests.post(f"{url}/dm/create/v1", json={
        'token': u_id_1['token'], 'u_ids': []
    })
    assert dm_dict.status_code == OK
    dm_id = dm_dict.json()['dm_id']
    msg_send = requests.post(f"{url}/message/senddm/v1", json={
        'token': u_id_1['token'], 'dm_id': dm_id, 'message': "sizzurpinmycup!!"
    })
    assert msg_send.status_code == OK
    message_id = msg_send.json()['message_id']
    delete = requests.delete(f"{url}/message/remove/v1", json={
        'token': u_id_1['token'], 'message_id': message_id
    })
    assert delete.status_code == OK
    msg_list = requests.get(
        f"{url}/dm/messages/v1?token={u_id_1['token']}&dm_id={dm_id}&start=0")
    assert msg_list.status_code == OK
    messages = msg_list.json()
    assert messages == {'messages': [], 'start': 0, 'end': -1}


def test_message_remove_invalid_token(clear, u_id_1):
    dm_dict = requests.post(f"{url}/dm/create/v1", json={
        'token': u_id_1['token'], 'u_ids': []
    })
    assert dm_dict.status_code == OK
    dm_id = dm_dict.json()['dm_id']
    msg_send = requests.post(f"{url}/message/senddm/v1", json={
        'token': u_id_1['token'], 'dm_id': dm_id, 'message': "sizzurpinmycup!!"
    })
    assert msg_send.status_code == OK
    message_id = msg_send.json()['message_id']
    delete = requests.delete(f"{url}/message/remove/v1", json={
        'token': -1, 'message_id': message_id
    })
    assert delete.status_code == 403


def test_message_remove_global_correct(clear, u_id_1, u_id_2):
    ch_dict = requests.post(f"{url}/channels/create/v2", json={
        'token': u_id_2['token'], 'name': 'happytreefriends', 'is_public': False
    })
    assert ch_dict.status_code == OK
    channel_id = ch_dict.json()['channel_id']
    resp = requests.post(f"{url}/channel/invite/v2", json={
        'token': u_id_2['token'], 'channel_id': channel_id, 'u_id': u_id_1['auth_user_id']
    })
    assert resp.status_code == OK
    msg_send = requests.post(f"{url}/message/send/v1", json={
        'token': u_id_2['token'], 'channel_id': channel_id, 'message': "hey"
    })
    assert msg_send.status_code == OK
    message_id = msg_send.json()['message_id']
    msg_remove = requests.delete(f"{url}/message/remove/v1", json={
        'token': u_id_1['token'], 'message_id': message_id
    })
    assert msg_remove.status_code == OK
    message_list = requests.get(
        f"{url}/channel/messages/v2?token={u_id_1['token']}&channel_id={channel_id}&start=0")
    assert message_list.status_code == OK
    messages = message_list.json()
    assert len(messages['messages']) == 0


def test_message_share_channel_dm_id_invalid_1(clear, u_id_1):
    ch_dict = requests.post(f"{url}/channels/create/v2", json={
        'token': u_id_1['token'], 'name': 'happytreefriends', 'is_public': False
    })
    assert ch_dict.status_code == OK
    channel_id = ch_dict.json()['channel_id']

    msg_send = requests.post(f"{url}/message/send/v1", json={
        'token': u_id_1['token'], 'channel_id': channel_id, 'message': "hey"
    })
    assert msg_send.status_code == OK
    message_id = msg_send.json()['message_id']

    msg_share = requests.post(f"{url}/message/share/v1", json={
        'token': u_id_1['token'], 'og_message_id': message_id, 'message': '', 'channel_id': -1, 'dm_id': -1
    })
    assert msg_share.status_code == 400


def test_message_share_channel_dm_id_invalid_2(clear, u_id_1):
    ch_dict = requests.post(f"{url}/channels/create/v2", json={
        'token': u_id_1['token'], 'name': 'happytreefriends', 'is_public': False
    })
    assert ch_dict.status_code == OK
    channel_id = ch_dict.json()['channel_id']

    msg_send = requests.post(f"{url}/message/send/v1", json={
        'token': u_id_1['token'], 'channel_id': channel_id, 'message': "hey"
    })
    assert msg_send.status_code == OK
    message_id = msg_send.json()['message_id']

    msg_share = requests.post(f"{url}/message/share/v1", json={
        'token': u_id_1['token'], 'og_message_id': message_id, 'message': '', 'channel_id': 2, 'dm_id': -1
    })
    assert msg_share.status_code == 400


def test_message_share_channel_dm_id_invalid_3(clear, u_id_1):
    ch_dict = requests.post(f"{url}/channels/create/v2", json={
        'token': u_id_1['token'], 'name': 'happytreefriends', 'is_public': False
    })
    assert ch_dict.status_code == OK
    channel_id = ch_dict.json()['channel_id']

    msg_send = requests.post(f"{url}/message/send/v1", json={
        'token': u_id_1['token'], 'channel_id': channel_id, 'message': "hey"
    })
    assert msg_send.status_code == OK
    message_id = msg_send.json()['message_id']

    msg_share = requests.post(f"{url}/message/share/v1", json={
        'token': u_id_1['token'], 'og_message_id': message_id, 'message': '', 'channel_id': -1, 'dm_id': 1
    })
    assert msg_share.status_code == 400


def test_message_share_channel_dm_id_invalid_4(clear, u_id_1):
    ch_dict = requests.post(f"{url}/channels/create/v2", json={
        'token': u_id_1['token'], 'name': 'happytreefriends', 'is_public': False
    })
    assert ch_dict.status_code == OK
    channel_id = ch_dict.json()['channel_id']

    msg_send = requests.post(f"{url}/message/send/v1", json={
        'token': u_id_1['token'], 'channel_id': channel_id, 'message': "hey"
    })
    assert msg_send.status_code == OK
    message_id = msg_send.json()['message_id']

    dm_dict = requests.post(f"{url}/dm/create/v1", json={
        'token': u_id_1['token'], 'u_ids': []
    })
    assert dm_dict.status_code == OK
    msg_share = requests.post(f"{url}/message/share/v1", json={
        'token': u_id_1['token'], 'og_message_id': message_id, 'message': '', 'channel_id': -1, 'dm_id': 2
    })
    assert msg_share.status_code == 400


def test_message_share_no_negative_one(clear, u_id_1):
    ch_dict = requests.post(f"{url}/channels/create/v2", json={
        'token': u_id_1['token'], 'name': 'happytreefriends', 'is_public': False
    })
    assert ch_dict.status_code == OK
    channel_id = ch_dict.json()['channel_id']

    msg_send = requests.post(f"{url}/message/send/v1", json={
        'token': u_id_1['token'], 'channel_id': channel_id, 'message': "hey"
    })
    assert msg_send.status_code == OK
    message_id = msg_send.json()['message_id']

    dm_dict = requests.post(f"{url}/dm/create/v1", json={
        'token': u_id_1['token'], 'u_ids': []
    })
    assert dm_dict.status_code == OK
    msg_share = requests.post(f"{url}/message/share/v1", json={
        'token': u_id_1['token'], 'og_message_id': message_id, 'message': '', 'channel_id': 1, 'dm_id': 1
    })
    assert msg_share.status_code == 400


def test_message_share_invalid_og_message_id_ch(clear, u_id_1):
    ch_dict = requests.post(f"{url}/channels/create/v2", json={
        'token': u_id_1['token'], 'name': 'happytreefriends', 'is_public': False
    })
    assert ch_dict.status_code == OK
    channel_id = ch_dict.json()['channel_id']

    msg_send = requests.post(f"{url}/message/send/v1", json={
        'token': u_id_1['token'], 'channel_id': channel_id, 'message': "hey"
    })
    assert msg_send.status_code == OK

    ch_dict_2 = requests.post(f"{url}/channels/create/v2", json={
        'token': u_id_1['token'], 'name': 'wazooppl', 'is_public': False
    })
    assert ch_dict_2.status_code == OK
    new_channel = ch_dict_2.json()['channel_id']
    msg_share = requests.post(f"{url}/message/share/v1", json={
        'token': u_id_1['token'], 'og_message_id': -1, 'message': '', 'channel_id': new_channel, 'dm_id': -1
    })
    assert msg_share.status_code == 400


def test_message_share_invalid_og_message_id_dm(clear, u_id_1):
    ch_dict = requests.post(f"{url}/channels/create/v2", json={
        'token': u_id_1['token'], 'name': 'happytreefriends', 'is_public': False
    })
    assert ch_dict.status_code == OK
    channel_id = ch_dict.json()['channel_id']

    msg_send = requests.post(f"{url}/message/send/v1", json={
        'token': u_id_1['token'], 'channel_id': channel_id, 'message': "hey"
    })
    assert msg_send.status_code == OK
    dm_dict = requests.post(f"{url}/dm/create/v1", json={
        'token': u_id_1['token'], 'u_ids': []
    })
    assert dm_dict.status_code == OK

    dm_id = dm_dict.json()['dm_id']

    msg_share = requests.post(f"{url}/message/share/v1", json={
        'token': u_id_1['token'], 'og_message_id': -1, 'message': '', 'channel_id': -1, 'dm_id': dm_id
    })
    assert msg_share.status_code == 400


def test_message_share_overlong_message(clear, u_id_1, u_id_2):
    ch_dict = requests.post(f"{url}/channels/create/v2", json={
        'token': u_id_1['token'], 'name': 'happytreefriends', 'is_public': False
    })
    assert ch_dict.status_code == OK
    channel_id = ch_dict.json()['channel_id']

    msg_send = requests.post(f"{url}/message/send/v1", json={
        'token': u_id_1['token'], 'channel_id': channel_id, 'message': "hey"
    })
    assert msg_send.status_code == OK
    message_id = msg_send.json()['message_id']
    dm_dict = requests.post(f"{url}/dm/create/v1", json={
        'token': u_id_1['token'], 'u_ids': []
    })
    assert dm_dict.status_code == OK

    dm_id = dm_dict.json()['dm_id']

    msg_share = requests.post(f"{url}/message/share/v1", json={
        'token': u_id_1['token'], 'og_message_id': message_id, 'message': "a" * 1001, 'channel_id': -1, 'dm_id': dm_id
    })
    assert msg_share.status_code == 400


def test_message_share_unauthorised_user_dm(clear, u_id_1, u_id_2):
    ch_dict = requests.post(f"{url}/channels/create/v2", json={
        'token': u_id_1['token'], 'name': 'happytreefriends', 'is_public': False
    })
    assert ch_dict.status_code == OK
    channel_id = ch_dict.json()['channel_id']

    msg_send = requests.post(f"{url}/message/send/v1", json={
        'token': u_id_1['token'], 'channel_id': channel_id, 'message': "hey"
    })
    assert msg_send.status_code == OK
    message_id = msg_send.json()['message_id']
    dm_dict = requests.post(f"{url}/dm/create/v1", json={
        'token': u_id_2['token'], 'u_ids': []
    })
    assert dm_dict.status_code == OK

    dm_id = dm_dict.json()['dm_id']

    msg_share = requests.post(f"{url}/message/share/v1", json={
        'token': u_id_1['token'], 'og_message_id': message_id, 'message': "bonus", 'channel_id': -1, 'dm_id': dm_id
    })
    assert msg_share.status_code == 403


def test_message_share_unauthorised_user_ch(clear, u_id_1, u_id_2):
    ch_dict = requests.post(f"{url}/channels/create/v2", json={
        'token': u_id_1['token'], 'name': 'happytreefriends', 'is_public': False
    })
    assert ch_dict.status_code == OK
    channel_id = ch_dict.json()['channel_id']

    msg_send = requests.post(f"{url}/message/send/v1", json={
        'token': u_id_1['token'], 'channel_id': channel_id, 'message': "hey"
    })
    assert msg_send.status_code == OK

    ch_dict_2 = requests.post(f"{url}/channels/create/v2", json={
        'token': u_id_2['token'], 'name': 'wazooppl', 'is_public': False
    })
    assert ch_dict_2.status_code == OK
    new_channel = ch_dict_2.json()['channel_id']
    msg_share = requests.post(f"{url}/message/share/v1", json={
        'token': f"{u_id_1['token']}", 'og_message_id': -1, 'message': "bonus", 'channel_id': new_channel, 'dm_id': -1
    })
    assert msg_share.status_code == 403


def test_message_share_invalid_token_ch(clear, u_id_1):
    ch_dict = requests.post(f"{url}/channels/create/v2", json={
        'token': u_id_1['token'], 'name': 'happytreefriends', 'is_public': False
    })
    assert ch_dict.status_code == OK
    channel_id = ch_dict.json()['channel_id']

    msg_send = requests.post(f"{url}/message/send/v1", json={
        'token': u_id_1['token'], 'channel_id': channel_id, 'message': "hey"
    })
    assert msg_send.status_code == OK

    ch_dict_2 = requests.post(f"{url}/channels/create/v2", json={
        'token': u_id_1['token'], 'name': 'wazooppl', 'is_public': False
    })
    assert ch_dict_2.status_code == OK
    new_channel = ch_dict_2.json()['channel_id']
    msg_share = requests.post(f"{url}/message/share/v1", json={
        'token': f"{u_id_1['token']}69", 'og_message_id': -1, 'message': "bonus", 'channel_id': new_channel, 'dm_id': -1
    })
    assert msg_share.status_code == 403


def test_message_share_invalid_token_dm(clear, u_id_1):
    ch_dict = requests.post(f"{url}/channels/create/v2", json={
        'token': u_id_1['token'], 'name': 'happytreefriends', 'is_public': False
    })
    assert ch_dict.status_code == OK
    channel_id = ch_dict.json()['channel_id']

    msg_send = requests.post(f"{url}/message/send/v1", json={
        'token': u_id_1['token'], 'channel_id': channel_id, 'message': "hey"
    })
    assert msg_send.status_code == OK
    dm_dict = requests.post(f"{url}/dm/create/v1", json={
        'token': u_id_1['token'], 'u_ids': []
    })
    assert dm_dict.status_code == OK

    dm_id = dm_dict.json()['dm_id']

    msg_share = requests.post(f"{url}/message/share/v1", json={
        'token': f"{u_id_1['token']}69", 'og_message_id': -1, 'message': "bonus", 'channel_id': -1, 'dm_id': dm_id
    })
    assert msg_share.status_code == 403


def test_message_share_correct_functioning(clear, u_id_1, u_id_2):
    ch_dict = requests.post(f"{url}/channels/create/v2", json={
        'token': u_id_1['token'], 'name': 'happytreefriends', 'is_public': False
    })

    assert ch_dict.status_code == OK

    channel_id = ch_dict.json()['channel_id']

    msg_ids = []
    for i in range(3):
        msg_send = requests.post(f"{url}/message/send/v1", json={
            'token': u_id_1['token'], 'channel_id': channel_id, 'message': f"hey{i}"
        })
        msg_ids.append(msg_send.json()['message_id'])

    dm_dict = requests.post(f"{url}/dm/create/v1", json={
        'token': u_id_1['token'], 'u_ids': [u_id_2['auth_user_id']]
    })
    assert dm_dict.status_code == OK
    dm_id = dm_dict.json()['dm_id']

    new_ch_dict = requests.post(f"{url}/channels/create/v2", json={
        'token': u_id_1['token'], 'name': 'thenewonewow', 'is_public': True
    })
    new_channel_id = new_ch_dict.json()['channel_id']

    for message_id in msg_ids:
        ch_msg_share = requests.post(f"{url}/message/share/v1", json={
            'token': u_id_1['token'], 'og_message_id': message_id, 'message': "bonus", 'channel_id': new_channel_id, 'dm_id': -1
        })
        assert ch_msg_share.status_code == OK
        dm_msg_share = requests.post(f"{url}/message/share/v1", json={
            'token': u_id_1['token'], 'og_message_id': message_id, 'message': "bonus", 'channel_id': -1, 'dm_id': dm_id
        })
        assert dm_msg_share.status_code == OK

    message_list = requests.get(
        f"{url}/channel/messages/v2?token={u_id_1['token']}&channel_id={new_channel_id}&start=0")
    assert message_list.status_code == OK
    ch = message_list.json()
    assert len(ch['messages']) == 3
    assert ch['messages'][0]['message'] == "hey2 bonus"
    assert ch['messages'][1]['message'] == "hey1 bonus"
    assert ch['messages'][2]['message'] == "hey0 bonus"

    dm_list = requests.get(
        f"{url}/dm/messages/v1?token={u_id_1['token']}&dm_id={dm_id}&start=0")
    assert dm_list.status_code == OK
    dm = dm_list.json()
    assert len(dm['messages']) == 3
    assert dm['messages'][0]['message'] == "hey2 bonus"
    assert dm['messages'][1]['message'] == "hey1 bonus"
    assert dm['messages'][2]['message'] == "hey0 bonus"

    # notifs = requests.get(f"{url}/notifications/get/v1?token={u_id_2['token']}")


def test_message_share_user_notin_og_channel(clear, u_id_1, u_id_2):
    ch_dict = requests.post(f"{url}/channels/create/v2", json={
        'token': u_id_1['token'], 'name': 'happytreefriends', 'is_public': False
    })

    assert ch_dict.status_code == OK

    channel_id = ch_dict.json()['channel_id']
    msg_send = requests.post(f"{url}/message/send/v1", json={
        'token': u_id_1['token'], 'channel_id': channel_id, 'message': f"hey"
    })
    assert msg_send.status_code == OK
    message_id = msg_send.json()['message_id']

    ch_dict_2 = requests.post(f"{url}/channels/create/v2", json={
        'token': u_id_2['token'], 'name': 'ladidadi', 'is_public': False
    })
    assert ch_dict_2.status_code == OK
    new_channel_id = ch_dict_2.json()['channel_id']
    ch_msg_share = requests.post(f"{url}/message/share/v1", json={
        'token': u_id_2['token'], 'og_message_id': message_id, 'message': "bonus", 'channel_id': new_channel_id, 'dm_id': -1
    })
    assert ch_msg_share.status_code == 400


def test_message_share_user_notin_og_dm(clear, u_id_1, u_id_2):
    dm_dict = requests.post(f"{url}/dm/create/v1", json={
        'token': u_id_1['token'], 'u_ids': []
    })
    assert dm_dict.status_code == OK
    dm_id = dm_dict.json()['dm_id']

    msg_send = requests.post(f"{url}/message/senddm/v1", json={
        'token': u_id_1['token'], 'dm_id': dm_id, 'message': "wagwan ppl"
    })
    assert msg_send.status_code == OK
    message_id = msg_send.json()['message_id']

    dm_dict_2 = requests.post(f"{url}/dm/create/v1", json={
        'token': u_id_2['token'], 'u_ids': []
    })
    assert dm_dict.status_code == OK
    dm_id = dm_dict_2.json()['dm_id']
    ch_msg_share = requests.post(f"{url}/message/share/v1", json={
        'token': u_id_2['token'], 'og_message_id': message_id, 'message': "bonus", 'channel_id': -1, 'dm_id': dm_id
    })
    assert ch_msg_share.status_code == 400


def test_message_send_notification_self_tag(clear, u_id_2):
    ch_dict = requests.post(f"{url}/channels/create/v2", json={
        'token': u_id_2['token'], 'name': 'happytreefriends', 'is_public': False
    })

    assert ch_dict.status_code == OK
    channel_id = ch_dict.json()['channel_id']
    message = "@roshanmujeeb@roshanmujeeb what's up!"
    msg_send = requests.post(f"{url}/message/send/v1", json={
        'token': u_id_2['token'], 'channel_id': channel_id, 'message': message
    })
    assert msg_send.status_code == OK

    notifs = requests.get(
        f"{url}/notifications/get/v1?token={u_id_2['token']}")
    assert notifs.status_code == OK

    notifs_list = notifs.json()['notifications']
    assert notifs_list == [{'channel_id': channel_id, 'dm_id': -1,
                            'notification_message': f"roshanmujeeb tagged you in happytreefriends: {message[:20]}"}]


def test_message_send_tag_no_notification_check(clear, u_id_1, u_id_2):
    ch_dict = requests.post(f"{url}/channels/create/v2", json={
        'token': u_id_2['token'], 'name': 'happytreefriends', 'is_public': False
    })
    assert ch_dict.status_code == OK
    channel_id = ch_dict.json()['channel_id']
    message = "@roshanmujeeb@roshanmujeeb@billthescienceguy what's up!"
    msg_send = requests.post(f"{url}/message/send/v1", json={
        'token': u_id_2['token'], 'channel_id': channel_id, 'message': message
    })
    assert msg_send.status_code == OK

    notifs = requests.get(
        f"{url}/notifications/get/v1?token={u_id_1['token']}")
    assert notifs.status_code == OK

    notifs_list = notifs.json()['notifications']
    assert notifs_list == []


def test_message_send_tag_another_person(clear, u_id_3, u_id_2):
    ch_dict = requests.post(f"{url}/channels/create/v2", json={
        'token': u_id_2['token'], 'name': 'happytreefriends', 'is_public': True
    })

    assert ch_dict.status_code == OK
    channel_id = ch_dict.json()['channel_id']

    user_join = requests.post(
        f"{url}/channel/join/v2", json={"token": u_id_3['token'], "channel_id": channel_id})
    assert user_join.status_code == OK

    message = "myguy@ghostfacekillah@ghostfacekillah the supreme clientele!"
    msg_send = requests.post(f"{url}/message/send/v1", json={
        'token': u_id_2['token'], 'channel_id': channel_id, 'message': message
    })
    assert msg_send.status_code == OK

    notifs = requests.get(
        f"{url}/notifications/get/v1?token={u_id_3['token']}")
    assert notifs.status_code == OK

    notifs_list = notifs.json()['notifications']
    assert notifs_list == [{'channel_id': channel_id, 'dm_id': -1,
                            'notification_message': f"roshanmujeeb tagged you in happytreefriends: {message[:20]}"}]


def test_message_senddm_tag_self(clear, u_id_2):
    dm_dict = requests.post(f"{url}/dm/create/v1", json={
        'token': u_id_2['token'], 'u_ids': []
    })
    assert dm_dict.status_code == OK
    dm_id = dm_dict.json()['dm_id']
    message = "wassup@roshanmujeeb the man@roshanmujeeb the legend@roshanmujeeb"
    msg_send = requests.post(f"{url}/message/senddm/v1", json={
        'token': u_id_2['token'], 'dm_id': dm_id, 'message': message
    })
    assert msg_send.status_code == OK

    notifs = requests.get(
        f"{url}/notifications/get/v1?token={u_id_2['token']}")
    assert notifs.status_code == OK

    notifs_list = notifs.json()['notifications']
    assert notifs_list == [{'channel_id': -1, 'dm_id': dm_id,
                            'notification_message': f"roshanmujeeb tagged you in roshanmujeeb: {message[:20]}"}]


def test_message_senddm_tag_another(clear, u_id_3, u_id_2, u_id_1):
    dm_dict = requests.post(f"{url}/dm/create/v1", json={
        'token': u_id_3['token'], 'u_ids': [u_id_2['auth_user_id']]
    })
    assert dm_dict.status_code == OK
    dm_id = dm_dict.json()['dm_id']
    message = "wassup@roshanmujeeb the man@roshanmujeeb the legend@roshanmujeeb@billthescienceguy"
    msg_send = requests.post(f"{url}/message/senddm/v1", json={
        'token': u_id_3['token'], 'dm_id': dm_id, 'message': message
    })
    assert msg_send.status_code == OK

    notifs = requests.get(
        f"{url}/notifications/get/v1?token={u_id_2['token']}")
    assert notifs.status_code == OK

    notifs_list = notifs.json()['notifications']
    assert notifs_list[0] == {'channel_id': -1, 'dm_id': dm_id,
                              'notification_message': f"ghostfacekillah tagged you in ghostfacekillah, roshanmujeeb: {message[:20]}"}

    notifs = requests.get(
        f"{url}/notifications/get/v1?token={u_id_1['token']}")
    assert notifs.status_code == OK
    notif_list = notifs.json()['notifications']
    assert len(notif_list) == 0


def test_message_share_tagging_correct(clear, u_id_2, u_id_3):
    ch_dict = requests.post(f"{url}/channels/create/v2", json={
        'token': u_id_2['token'], 'name': 'happytreefriends', 'is_public': False
    })

    assert ch_dict.status_code == OK

    channel_id = ch_dict.json()['channel_id']

    msg_ids = []
    for i in range(3):
        msg_send = requests.post(f"{url}/message/send/v1", json={
            'token': u_id_2['token'], 'channel_id': channel_id, 'message': f"hey@roshanmujeeb how's it going?@globglab@ghostfacekillah{i}"
        })
        msg_ids.append(msg_send.json()['message_id'])

    dm_dict = requests.post(f"{url}/dm/create/v1", json={
        'token': u_id_2['token'], 'u_ids': []
    })
    assert dm_dict.status_code == OK
    dm_id = dm_dict.json()['dm_id']

    new_ch_dict = requests.post(f"{url}/channels/create/v2", json={
        'token': u_id_2['token'], 'name': 'thenewonewow', 'is_public': True
    })
    new_channel_id = new_ch_dict.json()['channel_id']

    for message_id in msg_ids:
        ch_msg_share = requests.post(f"{url}/message/share/v1", json={
            'token': u_id_2['token'], 'og_message_id': message_id, 'message': "bonus", 'channel_id': new_channel_id, 'dm_id': -1
        })
        assert ch_msg_share.status_code == OK
        dm_msg_share = requests.post(f"{url}/message/share/v1", json={
            'token': u_id_2['token'], 'og_message_id': message_id, 'message': "bonus", 'channel_id': -1, 'dm_id': dm_id
        })
        assert dm_msg_share.status_code == OK

    notifs = requests.get(
        f"{url}/notifications/get/v1?token={u_id_2['token']}")
    assert notifs.status_code == OK
    notifs_list = notifs.json()['notifications']

    assert len(notifs_list) == 9
    notifs = requests.get(
        f"{url}/notifications/get/v1?token={u_id_3['token']}")
    notifs_list = notifs.json()['notifications']
    assert len(notifs_list) == 0


def test_message_edit_tag(clear, u_id_1, u_id_2, u_id_3):
    ch_dict = requests.post(f"{url}/channels/create/v2", json={
        'token': u_id_2['token'], 'name': 'happytreefriends', 'is_public': True
    })
    assert ch_dict.status_code == OK
    channel_id = ch_dict.json()['channel_id']
    msg_send = requests.post(f"{url}/message/send/v1", json={
        'token': u_id_2['token'], 'channel_id': channel_id, 'message': "hey"
    })
    assert msg_send.status_code == OK
    message = "bro@roshanmujeeb@billthescienceguy@sourcandy no one cares son@ghostfacekillah :("
    message_id = msg_send.json()['message_id']
    msg_edit = requests.put(f"{url}/message/edit/v1", json={
        'token': u_id_2['token'], 'message_id': message_id, 'message': message
    })
    assert msg_edit.status_code == OK
    notifs = requests.get(
        f"{url}/notifications/get/v1?token={u_id_3['token']}")
    assert notifs.status_code == OK
    notifs_list = notifs.json()['notifications']
    assert len(notifs_list) == 0

    notifs = requests.get(
        f"{url}/notifications/get/v1?token={u_id_1['token']}")
    assert notifs.status_code == OK
    notifs_list = notifs.json()['notifications']
    assert len(notifs_list) == 0


def test_message_react_invalid_message_id(clear, u_id_1, u_id_2):
    ch_dict = requests.post(f"{url}/channels/create/v2", json={
        'token': u_id_2['token'], 'name': 'happytreefriends', 'is_public': True
    })
    assert ch_dict.status_code == OK

    ch_dict_2 = requests.post(f"{url}/channels/create/v2", json={
        'token': u_id_1['token'], 'name': 'badabingoboomo', 'is_public': True
    })
    assert ch_dict_2.status_code == OK
    channel_id_2 = ch_dict_2.json()['channel_id']
    msg_send = requests.post(f"{url}/message/send/v1", json={
        'token': u_id_1['token'], 'channel_id': channel_id_2, 'message': "hey"
    })
    assert msg_send.status_code == OK
    wrong_message_id = msg_send.json()['message_id']
    msg_react = requests.post(f"{url}/message/react/v1", json={
        'token': u_id_2['token'], 'message_id': wrong_message_id, 'react_id': 1
    })
    assert msg_react.status_code == 400


def test_message_react_invalid_message_id_dm(clear, u_id_1, u_id_2, u_id_3):
    dm_dict = requests.post(f"{url}/dm/create/v1", json={
        'token': u_id_2['token'], 'u_ids': [u_id_1['auth_user_id']]
    })
    assert dm_dict.status_code == OK

    dm_dict_2 = requests.post(f"{url}/dm/create/v1", json={
        'token': u_id_3['token'], 'u_ids': []
    })
    dm_dict_2.status_code == OK
    dm_id = dm_dict_2.json()['dm_id']

    message = "wassup@roshanmujeeb the man@roshanmujeeb the legend@roshanmujeeb@billthescienceguy"
    msg_send = requests.post(f"{url}/message/senddm/v1", json={
        'token': u_id_3['token'], 'dm_id': dm_id, 'message': message
    })
    assert msg_send.status_code == OK
    wrong_message_id = msg_send.json()['message_id']

    msg_react = requests.post(f"{url}/message/react/v1", json={
        'token': u_id_2['token'], 'message_id': wrong_message_id, 'react_id': 1
    })
    assert msg_react.status_code == 400


def test_message_react_invalid_react_id(clear, u_id_2):
    ch_dict = requests.post(f"{url}/channels/create/v2", json={
        'token': u_id_2['token'], 'name': 'happytreefriends', 'is_public': True
    })
    assert ch_dict.status_code == OK
    channel_id = ch_dict.json()['channel_id']
    msg_send = requests.post(f"{url}/message/send/v1", json={
        'token': u_id_2['token'], 'channel_id': channel_id, 'message': "hey"
    })
    assert msg_send.status_code == OK
    message_id = msg_send.json()['message_id']
    msg_react = requests.post(f"{url}/message/react/v1", json={
        'token': u_id_2['token'], 'message_id': message_id, 'react_id': 2
    })
    assert msg_react.status_code == 400


def test_message_react_already_reacted(clear, u_id_2):
    ch_dict = requests.post(f"{url}/channels/create/v2", json={
        'token': u_id_2['token'], 'name': 'happytreefriends', 'is_public': True
    })
    assert ch_dict.status_code == OK
    channel_id = ch_dict.json()['channel_id']
    msg_send = requests.post(f"{url}/message/send/v1", json={
        'token': u_id_2['token'], 'channel_id': channel_id, 'message': "hey"
    })
    assert msg_send.status_code == OK
    message_id = msg_send.json()['message_id']
    msg_react = requests.post(f"{url}/message/react/v1", json={
        'token': u_id_2['token'], 'message_id': message_id, 'react_id': 1
    })
    assert msg_react.status_code == OK
    msg_react = requests.post(f"{url}/message/react/v1", json={
        'token': u_id_2['token'], 'message_id': message_id, 'react_id': 1
    })
    assert msg_react.status_code == 400


def test_message_react_already_reacted_dm(clear, u_id_2, u_id_1):
    dm_dict = requests.post(f"{url}/dm/create/v1", json={
        'token': u_id_2['token'], 'u_ids': [u_id_1['auth_user_id']]
    })
    assert dm_dict.status_code == OK
    dm_id = dm_dict.json()['dm_id']
    msg_send = requests.post(f"{url}/message/senddm/v1", json={
        'token': u_id_1['token'], 'dm_id': dm_id, 'message': "ahahahahah"
    })
    assert msg_send.status_code == OK
    message_id = msg_send.json()['message_id']
    msg_react = requests.post(f"{url}/message/react/v1", json={
        'token': u_id_2['token'], 'message_id': message_id, 'react_id': 1
    })
    assert msg_react.status_code == OK
    msg_react = requests.post(f"{url}/message/react/v1", json={
        'token': u_id_2['token'], 'message_id': message_id, 'react_id': 1
    })
    assert msg_react.status_code == 400


def test_message_react_correct_functioning(clear, u_id_1, u_id_2):
    ch_dict = requests.post(f"{url}/channels/create/v2", json={
        'token': u_id_2['token'], 'name': 'happytreefriends', 'is_public': True
    })
    assert ch_dict.status_code == OK
    channel_id = ch_dict.json()['channel_id']
    msg_send = requests.post(f"{url}/message/send/v1", json={
        'token': u_id_2['token'], 'channel_id': channel_id, 'message': "hey"
    })
    assert msg_send.status_code == OK
    message_id = msg_send.json()['message_id']

    join = requests.post(f"{url}/channel/join/v2", json={
        'token': u_id_1['token'], 'channel_id': channel_id
    })

    assert join.status_code == OK
    msg_react = requests.post(f"{url}/message/react/v1", json={
        'token': u_id_1['token'], 'message_id': message_id, 'react_id': 1
    })
    assert msg_react.status_code == OK
    message_list = requests.get(
        f"{url}/channel/messages/v2?token={u_id_1['token']}&channel_id={channel_id}&start=0")
    assert message_list.status_code == OK
    messages = message_list.json()['messages']
    assert messages[0]['reacts'] == [{'react_id': 1, 'u_ids': [
        u_id_1['auth_user_id']], 'is_this_user_reacted': True}]
    msg_react = requests.post(f"{url}/message/react/v1", json={
        'token': u_id_2['token'], 'message_id': message_id, 'react_id': 1
    })
    assert msg_react.status_code == OK
    message_list = requests.get(
        f"{url}/channel/messages/v2?token={u_id_2['token']}&channel_id={channel_id}&start=0")
    assert message_list.status_code == OK
    messages = message_list.json()['messages']
    assert messages[0]['reacts'] == [{'react_id': 1, 'u_ids': [
        u_id_1['auth_user_id'], u_id_2['auth_user_id']], 'is_this_user_reacted': True}]

    notifs = requests.get(
        f"{url}/notifications/get/v1?token={u_id_2['token']}")
    assert notifs.status_code == OK
    notif_list = notifs.json()['notifications']
    assert len(notif_list) == 2


def test_message_react_correct_functioning_dm(clear, u_id_1, u_id_2):
    dm_dict = requests.post(f"{url}/dm/create/v1", json={
        'token': u_id_2['token'], 'u_ids': [u_id_1['auth_user_id']]
    })
    assert dm_dict.status_code == OK
    dm_id = dm_dict.json()['dm_id']
    msg_send = requests.post(f"{url}/message/senddm/v1", json={
        'token': u_id_1['token'], 'dm_id': dm_id, 'message': "ahahahahah"
    })
    assert msg_send.status_code == OK
    message_id = msg_send.json()['message_id']
    msg_react = requests.post(f"{url}/message/react/v1", json={
        'token': u_id_2['token'], 'message_id': message_id, 'react_id': 1
    })
    assert msg_react.status_code == OK
    message_list = requests.get(
        f"{url}/dm/messages/v1?token={u_id_2['token']}&dm_id={dm_id}&start=0")
    assert message_list.status_code == OK
    messages = message_list.json()['messages']
    assert messages[0]['reacts'] == [{'react_id': 1, 'u_ids': [
        u_id_2['auth_user_id']], 'is_this_user_reacted': True}]

    notifs = requests.get(
        f"{url}/notifications/get/v1?token={u_id_1['token']}")
    assert notifs.status_code == OK
    notif_list = notifs.json()['notifications']
    assert len(notif_list) == 2


def test_message_unreact_invalid_message_id(clear, u_id_1, u_id_2):
    ch_dict = requests.post(f"{url}/channels/create/v2", json={
        'token': u_id_1['token'], 'name': 'happytreefriends', 'is_public': True
    })
    assert ch_dict.status_code == OK
    channel_id = ch_dict.json()['channel_id']
    msg_send = requests.post(f"{url}/message/send/v1", json={
        'token': u_id_1['token'], 'channel_id': channel_id, 'message': "hey"
    })
    assert msg_send.status_code == OK
    message_id = msg_send.json()['message_id']
    msg_react = requests.post(f"{url}/message/react/v1", json={
        'token': u_id_1['token'], 'message_id': message_id, 'react_id': 1
    })
    assert msg_react.status_code == OK
    unreact = requests.post(f"{url}/message/unreact/v1", json={
        'token': u_id_1['token'], 'message_id': -1, 'react_id': 1
    })
    assert unreact.status_code == 400


def test_message_unreact_invalid_react_id(clear, u_id_1, u_id_2):
    ch_dict = requests.post(f"{url}/channels/create/v2", json={
        'token': u_id_1['token'], 'name': 'happytreefriends', 'is_public': True
    })
    assert ch_dict.status_code == OK
    channel_id = ch_dict.json()['channel_id']
    msg_send = requests.post(f"{url}/message/send/v1", json={
        'token': u_id_1['token'], 'channel_id': channel_id, 'message': "hey"
    })
    assert msg_send.status_code == OK
    message_id = msg_send.json()['message_id']
    msg_react = requests.post(f"{url}/message/react/v1", json={
        'token': u_id_1['token'], 'message_id': message_id, 'react_id': 1
    })
    assert msg_react.status_code == OK
    unreact = requests.post(f"{url}/message/unreact/v1", json={
        'token': u_id_1['token'], 'message_id': message_id, 'react_id': -1
    })
    assert unreact.status_code == 400


def test_message_unreact_no_react(clear, u_id_1):
    ch_dict = requests.post(f"{url}/channels/create/v2", json={
        'token': u_id_1['token'], 'name': 'happytreefriends', 'is_public': True
    })
    assert ch_dict.status_code == OK
    channel_id = ch_dict.json()['channel_id']
    msg_send = requests.post(f"{url}/message/send/v1", json={
        'token': u_id_1['token'], 'channel_id': channel_id, 'message': "hey"
    })
    assert msg_send.status_code == OK
    message_id = msg_send.json()['message_id']
    unreact = requests.post(f"{url}/message/unreact/v1", json={
        'token': u_id_1['token'], 'message_id': message_id, 'react_id': 1
    })
    assert unreact.status_code == 400


def test_message_unreact_correct_channel(clear, u_id_1, u_id_2):
    ch_dict = requests.post(f"{url}/channels/create/v2", json={
        'token': u_id_1['token'], 'name': 'happytreefriends', 'is_public': True
    })
    assert ch_dict.status_code == OK
    channel_id = ch_dict.json()['channel_id']
    msg_send = requests.post(f"{url}/message/send/v1", json={
        'token': u_id_1['token'], 'channel_id': channel_id, 'message': "hey"
    })
    assert msg_send.status_code == OK
    message_id = msg_send.json()['message_id']

    join = requests.post(f"{url}/channel/join/v2", json={
        'token': u_id_2['token'], 'channel_id': channel_id
    })

    assert join.status_code == OK
    msg_react = requests.post(f"{url}/message/react/v1", json={
        'token': u_id_1['token'], 'message_id': message_id, 'react_id': 1
    })
    assert msg_react.status_code == OK

    unreact = requests.post(f"{url}/message/unreact/v1", json={
        'token': u_id_1['token'], 'message_id': message_id, 'react_id': 1
    })
    assert unreact.status_code == OK
    message_list = requests.get(
        f"{url}/channel/messages/v2?token={u_id_1['token']}&channel_id={channel_id}&start=0")
    assert message_list.status_code == OK
    messages = message_list.json()['messages']
    assert messages[0]['reacts'] == []

    msg_react = requests.post(f"{url}/message/react/v1", json={
        'token': u_id_2['token'], 'message_id': message_id, 'react_id': 1
    })
    assert msg_react.status_code == OK

    unreact = requests.post(f"{url}/message/unreact/v1", json={
        'token': u_id_2['token'], 'message_id': message_id, 'react_id': 1
    })
    assert unreact.status_code == OK
    message_list = requests.get(
        f"{url}/channel/messages/v2?token={u_id_2['token']}&channel_id={channel_id}&start=0")
    assert message_list.status_code == OK
    messages = message_list.json()['messages']
    assert messages[0]['reacts'] == []


def test_message_unreact_correct_dm(clear, u_id_1, u_id_2):
    dm_dict = requests.post(f"{url}/dm/create/v1", json={
        'token': u_id_2['token'], 'u_ids': [u_id_1['auth_user_id']]
    })
    assert dm_dict.status_code == OK
    dm_id = dm_dict.json()['dm_id']
    msg_send = requests.post(f"{url}/message/senddm/v1", json={
        'token': u_id_1['token'], 'dm_id': dm_id, 'message': "ahahahahah"
    })
    assert msg_send.status_code == OK
    message_id = msg_send.json()['message_id']
    msg_react = requests.post(f"{url}/message/react/v1", json={
        'token': u_id_2['token'], 'message_id': message_id, 'react_id': 1
    })
    assert msg_react.status_code == OK
    message_list = requests.get(
        f"{url}/dm/messages/v1?token={u_id_2['token']}&dm_id={dm_id}&start=0")
    assert message_list.status_code == OK
    messages = message_list.json()['messages']
    assert messages[0]['reacts'] == [{'react_id': 1, 'u_ids': [
        u_id_2['auth_user_id']], 'is_this_user_reacted': True}]
    unreact = requests.post(f"{url}/message/unreact/v1", json={
        'token': u_id_2['token'], 'message_id': message_id, 'react_id': 1
    })
    assert unreact.status_code == OK
    message_list = requests.get(
        f"{url}/dm/messages/v1?token={u_id_2['token']}&dm_id={dm_id}&start=0")
    assert message_list.status_code == OK
    messages = message_list.json()['messages']
    assert messages[0]['reacts'] == []

    msg_react = requests.post(f"{url}/message/react/v1", json={
        'token': u_id_1['token'], 'message_id': message_id, 'react_id': 1
    })
    assert msg_react.status_code == OK

    msg_react = requests.post(f"{url}/message/react/v1", json={
        'token': u_id_2['token'], 'message_id': message_id, 'react_id': 1
    })
    assert msg_react.status_code == OK
    unreact = requests.post(f"{url}/message/unreact/v1", json={
        'token': u_id_2['token'], 'message_id': message_id, 'react_id': 1
    })
    assert unreact.status_code == OK
    message_list = requests.get(
        f"{url}/dm/messages/v1?token={u_id_2['token']}&dm_id={dm_id}&start=0")
    assert message_list.status_code == OK
    messages = message_list.json()['messages']
    assert messages[0]['reacts'] == [{'react_id': 1, 'u_ids': [
        u_id_1['auth_user_id']], 'is_this_user_reacted': False}]


def test_message_pin_invalid_message_id(clear, u_id_1):
    ch_dict = requests.post(f"{url}/channels/create/v2", json={
        'token': u_id_1['token'], 'name': 'happytreefriends', 'is_public': True
    })
    assert ch_dict.status_code == OK
    channel_id = ch_dict.json()['channel_id']
    msg_send = requests.post(f"{url}/message/send/v1", json={
        'token': u_id_1['token'], 'channel_id': channel_id, 'message': "hey"
    })
    assert msg_send.status_code == OK

    msg_pin = requests.post(f"{url}/message/pin/v1", json={
        'token': u_id_1['token'], 'message_id': -1
    })
    assert msg_pin.status_code == 400


def test_message_pin_unauth_user(clear, u_id_1, u_id_2):
    ch_dict = requests.post(f"{url}/channels/create/v2", json={
        'token': u_id_1['token'], 'name': 'happytreefriends', 'is_public': True
    })
    assert ch_dict.status_code == OK
    ch_dict_2 = requests.post(f"{url}/channels/create/v2", json={
        'token': u_id_2['token'], 'name': 'theredhairedgibbons', 'is_public': True
    })
    assert ch_dict_2.status_code == OK
    wrong_channel_id = ch_dict_2.json()['channel_id']
    msg_send = requests.post(f"{url}/message/send/v1", json={
        'token': u_id_2['token'], 'channel_id': wrong_channel_id, 'message': "hey"
    })
    assert msg_send.status_code == OK
    message_id = msg_send.json()['message_id']
    msg_pin = requests.post(f"{url}/message/pin/v1", json={
        'token': u_id_1['token'], 'message_id': message_id
    })
    assert msg_pin.status_code == 400


def test_mesage_pin_unauth_user_dm(clear, u_id_1, u_id_2):
    dm_dict = requests.post(f"{url}/dm/create/v1", json={
        'token': u_id_2['token'], 'u_ids': []
    })
    assert dm_dict.status_code == OK
    dm_id = dm_dict.json()['dm_id']
    msg_send = requests.post(f"{url}/message/senddm/v1", json={
        'token': u_id_2['token'], 'dm_id': dm_id, 'message': "ahahahahah"
    })
    assert msg_send.status_code == OK
    message_id = msg_send.json()['message_id']
    dm_dict = requests.post(f"{url}/dm/create/v1", json={
        'token': u_id_1['token'], 'u_ids': []
    })
    assert dm_dict.status_code == OK
    msg_pin = requests.post(f"{url}/message/pin/v1", json={
        'token': u_id_1['token'], 'message_id': message_id
    })
    assert msg_pin.status_code == 400


def test_message_pin_invalid_message_id_dm(clear, u_id_1, u_id_2):
    dm_dict = requests.post(f"{url}/dm/create/v1", json={
        'token': u_id_2['token'], 'u_ids': [u_id_1['auth_user_id']]
    })
    assert dm_dict.status_code == OK
    dm_id = dm_dict.json()['dm_id']
    msg_send = requests.post(f"{url}/message/senddm/v1", json={
        'token': u_id_1['token'], 'dm_id': dm_id, 'message': "ahahahahah"
    })
    assert msg_send.status_code == OK
    msg_pin = requests.post(f"{url}/message/pin/v1", json={
        'token': u_id_1['token'], 'message_id': -1
    })
    assert msg_pin.status_code == 400


def test_message_pin_already_pinned(clear, u_id_1):
    ch_dict = requests.post(f"{url}/channels/create/v2", json={
        'token': u_id_1['token'], 'name': 'happytreefriends', 'is_public': True
    })
    assert ch_dict.status_code == OK
    channel_id = ch_dict.json()['channel_id']
    msg_send = requests.post(f"{url}/message/send/v1", json={
        'token': u_id_1['token'], 'channel_id': channel_id, 'message': "hey"
    })
    assert msg_send.status_code == OK
    message_id = msg_send.json()['message_id']
    msg_pin = requests.post(f"{url}/message/pin/v1", json={
        'token': u_id_1['token'], 'message_id': message_id
    })
    assert msg_pin.status_code == OK
    msg_pin = requests.post(f"{url}/message/pin/v1", json={
        'token': u_id_1['token'], 'message_id': message_id
    })
    assert msg_pin.status_code == 400


def test_message_pin_already_pinned_dm(clear, u_id_1, u_id_2):
    dm_dict = requests.post(f"{url}/dm/create/v1", json={
        'token': u_id_2['token'], 'u_ids': [u_id_1['auth_user_id']]
    })
    assert dm_dict.status_code == OK
    dm_id = dm_dict.json()['dm_id']
    msg_send = requests.post(f"{url}/message/senddm/v1", json={
        'token': u_id_1['token'], 'dm_id': dm_id, 'message': "ahahahahah"
    })
    message_id = msg_send.json()['message_id']
    assert msg_send.status_code == OK
    msg_pin = requests.post(f"{url}/message/pin/v1", json={
        'token': u_id_2['token'], 'message_id': message_id
    })
    assert msg_pin.status_code == OK
    msg_pin = requests.post(f"{url}/message/pin/v1", json={
        'token': u_id_2['token'], 'message_id': message_id
    })
    assert msg_pin.status_code == 400


def test_message_pin_no_owner_permissions(clear, u_id_1, u_id_2):
    ch_dict = requests.post(f"{url}/channels/create/v2", json={
        'token': u_id_1['token'], 'name': 'happytreefriends', 'is_public': True
    })
    assert ch_dict.status_code == OK
    channel_id = ch_dict.json()['channel_id']
    msg_send = requests.post(f"{url}/message/send/v1", json={
        'token': u_id_1['token'], 'channel_id': channel_id, 'message': "hey"
    })
    assert msg_send.status_code == OK
    message_id = msg_send.json()['message_id']
    join = requests.post(f"{url}/channel/join/v2",
                         json={'token': u_id_2['token'], 'channel_id': channel_id})
    assert join.status_code == OK
    msg_pin = requests.post(f"{url}/message/pin/v1", json={
        'token': u_id_2['token'], 'message_id': message_id
    })
    assert msg_pin.status_code == 403


def test_message_pin_no_owner_perms_dm(clear, u_id_1, u_id_2):
    dm_dict = requests.post(f"{url}/dm/create/v1", json={
        'token': u_id_2['token'], 'u_ids': [u_id_1['auth_user_id']]
    })
    assert dm_dict.status_code == OK
    dm_id = dm_dict.json()['dm_id']
    msg_send = requests.post(f"{url}/message/senddm/v1", json={
        'token': u_id_1['token'], 'dm_id': dm_id, 'message': "ahahahahah"
    })
    message_id = msg_send.json()['message_id']
    assert msg_send.status_code == OK
    msg_pin = requests.post(f"{url}/message/pin/v1", json={
        'token': u_id_1['token'], 'message_id': message_id
    })
    assert msg_pin.status_code == 403


def test_message_pin_global_perms_correct(clear, u_id_1, u_id_2):
    ch_dict = requests.post(f"{url}/channels/create/v2", json={
        'token': u_id_2['token'], 'name': 'happytreefriends', 'is_public': True
    })
    assert ch_dict.status_code == OK
    channel_id = ch_dict.json()['channel_id']
    msg_send = requests.post(f"{url}/message/send/v1", json={
        'token': u_id_2['token'], 'channel_id': channel_id, 'message': "hey"
    })
    assert msg_send.status_code == OK
    message_id = msg_send.json()['message_id']
    join = requests.post(f"{url}/channel/join/v2",
                         json={'token': u_id_1['token'], 'channel_id': channel_id})
    assert join.status_code == OK
    msg_pin = requests.post(f"{url}/message/pin/v1", json={
        'token': u_id_1['token'], 'message_id': message_id
    })
    assert msg_pin.status_code == OK
    message_list = requests.get(
        f"{url}/channel/messages/v2?token={u_id_1['token']}&channel_id={channel_id}&start=0")
    assert message_list.status_code == OK
    messages = message_list.json()['messages']
    assert messages[0]['is_pinned'] == True


def test_message_pin_regular_correct_functioning(clear, u_id_1, u_id_2):
    ch_dict = requests.post(f"{url}/channels/create/v2", json={
        'token': u_id_1['token'], 'name': 'happytreefriends', 'is_public': True
    })
    assert ch_dict.status_code == OK
    channel_id = ch_dict.json()['channel_id']
    msg_send = requests.post(f"{url}/message/send/v1", json={
        'token': u_id_1['token'], 'channel_id': channel_id, 'message': "hey"
    })
    assert msg_send.status_code == OK
    join = requests.post(f"{url}/channel/join/v2",
                         json={'token': u_id_2['token'], 'channel_id': channel_id})
    assert join.status_code == OK
    msg_send = requests.post(f"{url}/message/send/v1", json={
        'token': u_id_2['token'], 'channel_id': channel_id, 'message': "hey2"
    })
    assert msg_send.status_code == OK
    message_id = msg_send.json()['message_id']
    msg_pin = requests.post(f"{url}/message/pin/v1", json={
        'token': u_id_1['token'], 'message_id': message_id
    })
    assert msg_pin.status_code == OK
    message_list = requests.get(
        f"{url}/channel/messages/v2?token={u_id_1['token']}&channel_id={channel_id}&start=0")
    assert message_list.status_code == OK
    messages = message_list.json()['messages']
    assert messages[0]['is_pinned'] == True


def test_message_pin_correct_functioning_dm(clear, u_id_1, u_id_2):
    dm_dict = requests.post(f"{url}/dm/create/v1", json={
        'token': u_id_2['token'], 'u_ids': [u_id_1['auth_user_id']]
    })
    assert dm_dict.status_code == OK
    dm_id = dm_dict.json()['dm_id']
    msg_send = requests.post(f"{url}/message/senddm/v1", json={
        'token': u_id_1['token'], 'dm_id': dm_id, 'message': "ahahahahah"
    })
    assert msg_send.status_code == OK
    message_id = msg_send.json()['message_id']
    msg_pin = requests.post(f"{url}/message/pin/v1", json={
        'token': u_id_2['token'], 'message_id': message_id
    })
    assert msg_pin.status_code == OK
    message_list = requests.get(
        f"{url}/dm/messages/v1?token={u_id_1['token']}&dm_id={dm_id}&start=0")
    assert message_list.status_code == OK
    message = message_list.json()['messages']
    assert message[0]['is_pinned'] == True


def test_message_unpin_invalid_message_id(clear, u_id_1):
    ch_dict = requests.post(f"{url}/channels/create/v2", json={
        'token': u_id_1['token'], 'name': 'happytreefriends', 'is_public': True
    })
    assert ch_dict.status_code == OK
    channel_id = ch_dict.json()['channel_id']
    msg_send = requests.post(f"{url}/message/send/v1", json={
        'token': u_id_1['token'], 'channel_id': channel_id, 'message': "hey"
    })
    assert msg_send.status_code == OK

    message_id = msg_send.json()['message_id']
    msg_pin = requests.post(f"{url}/message/pin/v1", json={
        'token': u_id_1['token'], 'message_id': message_id
    })
    assert msg_pin.status_code == OK
    msg_unpin = requests.post(f"{url}/message/unpin/v1", json={
        'token': u_id_1['token'], 'message_id': -1
    })
    assert msg_unpin.status_code == 400


def test_message_unpin_invalid_message_id_dm(clear, u_id_1):
    dm_dict = requests.post(f"{url}/dm/create/v1", json={
        'token': u_id_1['token'], 'u_ids': []
    })
    assert dm_dict.status_code == OK
    dm_id = dm_dict.json()['dm_id']
    msg_send = requests.post(f"{url}/message/senddm/v1", json={
        'token': u_id_1['token'], 'dm_id': dm_id, 'message': "ahahahahah"
    })
    assert msg_send.status_code == OK
    message_id = msg_send.json()['message_id']
    msg_pin = requests.post(f"{url}/message/pin/v1", json={
        'token': u_id_1['token'], 'message_id': message_id
    })
    assert msg_pin.status_code == OK
    msg_unpin = requests.post(f"{url}/message/unpin/v1", json={
        'token': u_id_1['token'], 'message_id': -1
    })
    assert msg_unpin.status_code == 400


def test_message_unpin_already_pinned(clear, u_id_1):
    ch_dict = requests.post(f"{url}/channels/create/v2", json={
        'token': u_id_1['token'], 'name': 'happytreefriends', 'is_public': True
    })
    assert ch_dict.status_code == OK
    channel_id = ch_dict.json()['channel_id']
    msg_send = requests.post(f"{url}/message/send/v1", json={
        'token': u_id_1['token'], 'channel_id': channel_id, 'message': "hey"
    })
    assert msg_send.status_code == OK
    message_id = msg_send.json()['message_id']
    msg_unpin = requests.post(f"{url}/message/unpin/v1", json={
        'token': u_id_1['token'], 'message_id': message_id
    })
    assert msg_unpin.status_code == 400


def test_message_unpin_no_perms(clear, u_id_1, u_id_2):
    ch_dict = requests.post(f"{url}/channels/create/v2", json={
        'token': u_id_1['token'], 'name': 'happytreefriends', 'is_public': True
    })
    assert ch_dict.status_code == OK
    channel_id = ch_dict.json()['channel_id']
    msg_send = requests.post(f"{url}/message/send/v1", json={
        'token': u_id_1['token'], 'channel_id': channel_id, 'message': "hey"
    })
    assert msg_send.status_code == OK

    message_id = msg_send.json()['message_id']
    msg_pin = requests.post(f"{url}/message/pin/v1", json={
        'token': u_id_1['token'], 'message_id': message_id
    })
    assert msg_pin.status_code == OK
    join = requests.post(f"{url}/channel/join/v2",
                         json={'token': u_id_2['token'], 'channel_id': channel_id})
    assert join.status_code == OK
    msg_unpin = requests.post(f"{url}/message/unpin/v1", json={
        'token': u_id_2['token'], 'message_id': message_id
    })
    assert msg_unpin.status_code == 403


def test_message_unpin_no_perms_dm(clear, u_id_1, u_id_2):
    dm_dict = requests.post(f"{url}/dm/create/v1", json={
        'token': u_id_2['token'], 'u_ids': [u_id_1['auth_user_id']]
    })
    assert dm_dict.status_code == OK
    dm_id = dm_dict.json()['dm_id']
    msg_send = requests.post(f"{url}/message/senddm/v1", json={
        'token': u_id_2['token'], 'dm_id': dm_id, 'message': "ahahahahah"
    })
    assert msg_send.status_code == OK
    message_id = msg_send.json()['message_id']
    msg_pin = requests.post(f"{url}/message/pin/v1", json={
        'token': u_id_2['token'], 'message_id': message_id
    })
    assert msg_pin.status_code == OK
    msg_unpin = requests.post(f"{url}/message/unpin/v1", json={
        'token': u_id_1['token'], 'message_id': message_id
    })
    assert msg_unpin.status_code == 403


def test_message_unpin_correct_functionality(clear, u_id_1, u_id_2):
    ch_dict = requests.post(f"{url}/channels/create/v2", json={
        'token': u_id_1['token'], 'name': 'happytreefriends', 'is_public': True
    })
    assert ch_dict.status_code == OK
    channel_id = ch_dict.json()['channel_id']
    msg_send = requests.post(f"{url}/message/send/v1", json={
        'token': u_id_1['token'], 'channel_id': channel_id, 'message': "hey"
    })
    assert msg_send.status_code == OK

    message_id = msg_send.json()['message_id']
    msg_pin = requests.post(f"{url}/message/pin/v1", json={
        'token': u_id_1['token'], 'message_id': message_id
    })
    assert msg_pin.status_code == OK
    join = requests.post(f"{url}/channel/join/v2",
                         json={'token': u_id_2['token'], 'channel_id': channel_id})
    assert join.status_code == OK
    msg_unpin = requests.post(f"{url}/message/unpin/v1", json={
        'token': u_id_1['token'], 'message_id': message_id
    })
    assert msg_unpin.status_code == OK
    message_list = requests.get(
        f"{url}/channel/messages/v2?token={u_id_1['token']}&channel_id={channel_id}&start=0")
    assert message_list.status_code == OK
    message = message_list.json()['messages']
    assert message[0]['is_pinned'] == False
    message_list = requests.get(
        f"{url}/channel/messages/v2?token={u_id_1['token']}&channel_id={channel_id}&start=0")
    assert message_list.status_code == OK


def test_message_unpin_correct_dm(clear, u_id_1, u_id_2):
    dm_dict = requests.post(f"{url}/dm/create/v1", json={
        'token': u_id_2['token'], 'u_ids': [u_id_1['auth_user_id']]
    })
    assert dm_dict.status_code == OK
    dm_id = dm_dict.json()['dm_id']
    msg_send = requests.post(f"{url}/message/senddm/v1", json={
        'token': u_id_2['token'], 'dm_id': dm_id, 'message': "ahahahahah"
    })
    assert msg_send.status_code == OK
    message_id = msg_send.json()['message_id']
    msg_pin = requests.post(f"{url}/message/pin/v1", json={
        'token': u_id_2['token'], 'message_id': message_id
    })
    assert msg_pin.status_code == OK
    msg_unpin = requests.post(f"{url}/message/unpin/v1", json={
        'token': u_id_2['token'], 'message_id': message_id
    })
    assert msg_unpin.status_code == OK
    message_list = requests.get(
        f"{url}/dm/messages/v1?token={u_id_1['token']}&dm_id={dm_id}&start=0")
    assert message_list.status_code == OK
    message = message_list.json()['messages']
    assert message[0]['is_pinned'] == False
