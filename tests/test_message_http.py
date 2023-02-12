import pytest
import json
import requests
from src.error import AccessError
from src.error import InputError 

BASE_ADDRESS = 'http://127.0.0.1'
BASE_PORT = '8080'
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

def message_send_invalid_channel_id(clear, u_id_1):
    ch_dict = requests.post(f"{url}/channels/create/v2", json={
        'token': u_id_1['token'], 'name': 'happytreefriends', 'is_public': True
    })
    assert ch_dict.status_code == OK 
    msg_send = requests.post(f"{url}/message/send/v1", json={
        'token': u_id_1['token'], 'channel_id': 3, 'message': "hey!"
    })
    assert msg_send.status_code == 400 

def message_send_size_zero(clear, u_id_1):
    ch_dict = requests.post(f"{url}/channels/create/v2", json={
        'token': u_id_1['token'], 'name': 'happytreefriends', 'is_public': True
    })    
    assert ch_dict.status_code == OK 
    msg_send = requests.post(f"{url}/message/send/v1", json={
        'token': u_id_1['token'], 'channel_id': ch_dict['channel_id'], 'message': ""
    })
    assert msg_send.status_code == 400

def message_send_size_large(clear, u_id_1):
    ch_dict = requests.post(f"{url}/channels/create/v2", json={
        'token': u_id_1['token'], 'name': 'happytreefriends', 'is_public': True
    })    
    assert ch_dict.status_code == OK 
    long_msg = "a" * 1000
    msg_send = requests.post(f"{url}/message/send/v1", json={
        'token': u_id_1['token'], 'channel_id': ch_dict['channel_id'], 'message': long_msg
    })
    assert msg_send.status_code == OK

def message_send_oversized(clear, u_id_1):
    ch_dict = requests.post(f"{url}/channels/create/v2", json={
        'token': u_id_1['token'], 'name': 'happytreefriends', 'is_public': True
    })    
    assert ch_dict.status_code == OK 
    long_msg = "a" * 1001
    msg_send = requests.post(f"{url}/message/send/v1", json={
        'token': u_id_1['token'], 'channel_id': ch_dict['channel_id'], 'message': long_msg
    })
    assert msg_send.status_code == 400

def message_send_correct_functioning(clear, u_id_1):
    ch_dict = requests.post(f"{url}/channels/create/v2", json={
        'token': u_id_1['token'], 'name': 'happytreefriends', 'is_public': True
    })    
    assert ch_dict.status_code == OK 
    msg_send = requests.post(f"{url}/message/send/v1", json={
        'token': u_id_1['token'], 'channel_id': ch_dict['channel_id'], 'message': "hey"
    })
    assert msg_send.status_code == OK 
    long_msg = "a" * 1000
    msg_long_send = requests.post(f"{url}/message/send/v1", json={
        'token': u_id_1['token'], 'channel_id': ch_dict['channel_id'], 'message': long_msg
    })
    assert msg_long_send.status_code == OK
    message_list = requests.get(f"{url}/channel/messages/v2?token={u_id_1['token']}&channel_id={ch_dict['channel_id']}&start=0")                      
    assert ch_dict.status_code == OK 
    assert message_list['start'] == 0
    assert message_list['end'] == 1
    assert len(message_list['messages']) == 2
    assert message_list['messages'][0]['message'] == long_msg
    assert message_list['messages'][1]['message'] == "hey"

def message_send_unauthorised_user(clear, u_id_1, u_id_2):
    ch_dict = requests.post(f"{url}/channels/create/v2", json={
        'token': u_id_1['token'], 'name': 'happytreefriends', 'is_public': True
    })    
    assert ch_dict.status_code == OK 
    msg_send = requests.post(f"{url}/message/send/v1", json={
        'token': u_id_2['token'], 'channel_id': ch_dict['channel_id'], 'message': "hey"
    })
    assert msg_send.status_code == 403      

def message_send_invalid_token(clear, u_id_1):
    ch_dict = requests.post(f"{url}/channels/create/v2", json={
        'token': u_id_1['token'], 'name': 'happytreefriends', 'is_public': True
    })          
    assert ch_dict.status_code == OK 
    msg_send = requests.post(f"{url}/message/send/v1", json={
        'token': f"{u_id_1['token']}69", 'channel_id': ch_dict['channel_id'], 'message': "hey"
    })
    assert msg_send.status_code == 403
  
    
