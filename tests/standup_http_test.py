import pytest
import json
from src import config
import requests
import time

BASE_ADDRESS = 'http://127.0.0.1'
BASE_PORT = config.port
URL = f"{BASE_ADDRESS}:{BASE_PORT}"
OK = 200
ACCESSERROR = 403
INPUTERROR = 400

@pytest.fixture
def auth_user_1():
    auth_user_1 = {
    "email":"tomjerry@unsw.edu.au", "password":"tomandjerry", "name_first":"tom", "name_last":"jerry",
    }
    return auth_user_1

@pytest.fixture
def auth_user_2():
    auth_user_2 = {
        "email":"jimcook@unsw.edu.au", "password":"jimcooksfood", "name_first":"jim", "name_last":"cook",
    }
    return auth_user_2

@pytest.fixture
def auth_user_3():
    auth_user_3 = {
        "email":"peterpan@unsw.edu.au", "password":"peterhaspan", "name_first":"peter", "name_last":"pan",
    }
    return auth_user_3

#STANDUP START

def test_standup_start_working(auth_user_1):
    requests.delete(f"{URL}/clear/v1")
    requests.post(f"{URL}/auth/register/v2", json = auth_user_1)
    login_user_1 = requests.post(f"{URL}/auth/login/v2", json = auth_user_1)
    login_user_1_return = json.loads(login_user_1.text)
    token_user_1 = login_user_1_return['token']

    channel_1 = requests.post(f"{URL}/channels/create/v2", json = {"token": token_user_1, "name": "Aus", "is_public": False})
    channel_1_id = json.loads(channel_1.text)['channel_id']
    assert channel_1.status_code == OK

    time_start =requests.post(f"{URL}/standup/start/v1", json = {"token": token_user_1, "channel_id": channel_1_id, "length": 5})

    assert time_start.status_code == OK
    time_finish = json.loads(time_start.text)['time_finish']
    time_current = int(time.time())
    assert isinstance(time_finish, int)

    assert time_finish - (time_current + 5) < 1

def test_standup_start_invalid_channel_id(auth_user_1):
    requests.delete(f"{URL}/clear/v1")
    requests.post(f"{URL}/auth/register/v2", json = auth_user_1)
    login_user_1 = requests.post(f"{URL}/auth/login/v2", json = auth_user_1)
    login_user_1_return = json.loads(login_user_1.text)
    token_user_1 = login_user_1_return['token']

    channel_1 = requests.post(f"{URL}/channels/create/v2", json = {"token": token_user_1, "name": "Aus", "is_public": False})
    channel_1_id = json.loads(channel_1.text)['channel_id']
    assert channel_1.status_code == OK

    invalid_channel_id = channel_1_id + 20

    time_start =requests.post(f"{URL}/standup/start/v1", json = {"token": token_user_1, "channel_id": invalid_channel_id, "length": 5})
    assert time_start.status_code == INPUTERROR

def test_standup_start_invalid_token_id(auth_user_1):
    requests.delete(f"{URL}/clear/v1")
    requests.post(f"{URL}/auth/register/v2", json = auth_user_1)
    login_user_1 = requests.post(f"{URL}/auth/login/v2", json = auth_user_1)
    login_user_1_return = json.loads(login_user_1.text)
    token_user_1 = login_user_1_return['token']

    channel_1 = requests.post(f"{URL}/channels/create/v2", json = {"token": token_user_1, "name": "Aus", "is_public": False})
    channel_1_id = json.loads(channel_1.text)['channel_id']
    assert channel_1.status_code == OK

    invalid_token = f"{token_user_1}2725"

    time_start =requests.post(f"{URL}/standup/start/v1", json = {"token": invalid_token, "channel_id": channel_1_id, "length": 5})

    assert time_start.status_code == 403

def test_standup_start_invalid_length(auth_user_1):
    requests.delete(f"{URL}/clear/v1")
    requests.post(f"{URL}/auth/register/v2", json = auth_user_1)
    login_user_1 = requests.post(f"{URL}/auth/login/v2", json = auth_user_1)
    login_user_1_return = json.loads(login_user_1.text)
    token_user_1 = login_user_1_return['token']

    channel_1 = requests.post(f"{URL}/channels/create/v2", json = {"token": token_user_1, "name": "Aus", "is_public": False})
    channel_1_id = json.loads(channel_1.text)['channel_id']
    assert channel_1.status_code == OK

    time_start =requests.post(f"{URL}/standup/start/v1", json = {"token": token_user_1, "channel_id": channel_1_id, "length": -1})

    assert time_start.status_code == 400

def test_standup_start_standup_already_active(auth_user_1):
    requests.delete(f"{URL}/clear/v1")
    requests.post(f"{URL}/auth/register/v2", json = auth_user_1)
    login_user_1 = requests.post(f"{URL}/auth/login/v2", json = auth_user_1)
    login_user_1_return = json.loads(login_user_1.text)
    token_user_1 = login_user_1_return['token']

    channel_1 = requests.post(f"{URL}/channels/create/v2", json = {"token": token_user_1, "name": "Aus", "is_public": False})
    channel_1_id = json.loads(channel_1.text)['channel_id']
    assert channel_1.status_code == OK

    time_start =requests.post(f"{URL}/standup/start/v1", json = {"token": token_user_1, "channel_id": channel_1_id, "length": 10})
    assert time_start.status_code == OK

    time_start_2 = requests.post(f"{URL}/standup/start/v1", json = {"token": token_user_1, "channel_id": channel_1_id, "length": 5})
    assert time_start_2.status_code == 400

def test_standup_start_nonmember(auth_user_1, auth_user_2):
    requests.delete(f"{URL}/clear/v1")
    requests.post(f"{URL}/auth/register/v2", json = auth_user_1)
    login_user_1 = requests.post(f"{URL}/auth/login/v2", json = auth_user_1)
    login_user_1_return = json.loads(login_user_1.text)
    token_user_1 = login_user_1_return['token']

    requests.post(f"{URL}/auth/register/v2", json = auth_user_2)
    login_user_2 = requests.post(f"{URL}/auth/login/v2", json = auth_user_2)
    login_user_2_return = json.loads(login_user_2.text)
    token_user_2 = login_user_2_return['token']

    channel_1 = requests.post(f"{URL}/channels/create/v2", json = {"token": token_user_1, "name": "Aus", "is_public": False})
    channel_1_id = json.loads(channel_1.text)['channel_id']
    assert channel_1.status_code == OK

    time_start = requests.post(f"{URL}/standup/start/v1", json = {"token": token_user_2, "channel_id": channel_1_id, "length": 5})
    assert time_start.status_code == 403


# STANDUP ACTIVE

def test_standup_active_working(auth_user_1):
    
    requests.delete(f"{URL}/clear/v1")
    requests.post(f"{URL}/auth/register/v2", json = auth_user_1)
    login_user_1 = requests.post(f"{URL}/auth/login/v2", json = auth_user_1)
    login_user_1_return = json.loads(login_user_1.text)
    token_user_1 = login_user_1_return['token']

    channel_1 = requests.post(f"{URL}/channels/create/v2", json = {"token": token_user_1, "name": "Aus", "is_public": False})
    channel_1_id = json.loads(channel_1.text)['channel_id']
    assert channel_1.status_code == OK

    time_start = requests.post(f"{URL}/standup/start/v1", json = {"token": token_user_1, "channel_id": channel_1_id, "length": 5})
    assert time_start.status_code == OK

    active_input = {
        "token": token_user_1,
        "channel_id": channel_1_id
    }

    active_check = requests.get(f"{URL}/standup/active/v1", params= active_input)    
    active_check_return = json.loads(active_check.text)
    assert active_check.status_code == OK

    time_finish = active_check_return["time_finish"]
    assert isinstance(time_finish, int) == True
    assert active_check_return["is_active"] == True


def test_standup_active_no_standup(auth_user_1):
    requests.delete(f"{URL}/clear/v1")
    requests.post(f"{URL}/auth/register/v2", json = auth_user_1)
    login_user_1 = requests.post(f"{URL}/auth/login/v2", json = auth_user_1)
    login_user_1_return = json.loads(login_user_1.text)
    token_user_1 = login_user_1_return['token']

    channel_1 = requests.post(f"{URL}/channels/create/v2", json = {"token": token_user_1, "name": "Aus", "is_public": False})
    channel_1_id = json.loads(channel_1.text)['channel_id']
    assert channel_1.status_code == OK

    active_input = {
        "token": token_user_1,
        "channel_id": channel_1_id
    }

    active_check = requests.get(f"{URL}/standup/active/v1", params= active_input)    
    active_check_return = json.loads(active_check.text)
    assert active_check.status_code == OK

    assert active_check_return["is_active"] == False
    time_finish = active_check_return["time_finish"]
    assert time_finish == None

def test_standup_active_invalid_channel_id(auth_user_1):

    requests.delete(f"{URL}/clear/v1")
    requests.post(f"{URL}/auth/register/v2", json = auth_user_1)
    login_user_1 = requests.post(f"{URL}/auth/login/v2", json = auth_user_1)
    login_user_1_return = json.loads(login_user_1.text)
    token_user_1 = login_user_1_return['token']

    channel_1 = requests.post(f"{URL}/channels/create/v2", json = {"token": token_user_1, "name": "Aus", "is_public": False})
    channel_1_id = json.loads(channel_1.text)['channel_id']
    assert channel_1.status_code == OK

    time_start = requests.post(f"{URL}/standup/start/v1", json = {"token": token_user_1, "channel_id": channel_1_id, "length": 5})
    assert time_start.status_code == OK
    
    invalid_channel_id = channel_1_id + 10

    active_input = {
        "token": token_user_1,
        "channel_id": invalid_channel_id
    }

    active_check = requests.get(f"{URL}/standup/active/v1", params= active_input)    
    assert active_check.status_code == 400
    
def test_standup_active_nonmember(auth_user_1, auth_user_2):
    
    requests.delete(f"{URL}/clear/v1")
    requests.post(f"{URL}/auth/register/v2", json = auth_user_1)
    login_user_1 = requests.post(f"{URL}/auth/login/v2", json = auth_user_1)
    login_user_1_return = json.loads(login_user_1.text)
    token_user_1 = login_user_1_return['token']
    
    requests.post(f"{URL}/auth/register/v2", json=auth_user_2)
    login_user_2 = requests.post(f"{URL}/auth/login/v2", json=auth_user_2)
    login_user_2_return = json.loads(login_user_2.text)
    token_user_2 = login_user_2_return['token']

    channel_1 = requests.post(f"{URL}/channels/create/v2", json = {"token": token_user_1, "name": "Aus", "is_public": False})
    channel_1_id = json.loads(channel_1.text)['channel_id']
    assert channel_1.status_code == OK

    time_start = requests.post(f"{URL}/standup/start/v1", json = {"token": token_user_1, "channel_id": channel_1_id, "length": 5})
    assert time_start.status_code == OK

    active_input = {
        "token": token_user_2,
        "channel_id": channel_1_id
    }

    active_check = requests.get(f"{URL}/standup/active/v1", params= active_input)    
    assert active_check.status_code == 403

#STANDUP SEND

def test_standup_send_working(auth_user_1, auth_user_2):
    
    requests.delete(f"{URL}/clear/v1")
    requests.post(f"{URL}/auth/register/v2", json = auth_user_1)
    login_user_1 = requests.post(f"{URL}/auth/login/v2", json = auth_user_1)
    login_user_1_return = json.loads(login_user_1.text)
    token_user_1 = login_user_1_return['token']

    requests.post(f"{URL}/auth/register/v2", json=auth_user_2)
    login_user_2 = requests.post(f"{URL}/auth/login/v2", json=auth_user_2)
    login_user_2_return = json.loads(login_user_2.text)
    token_user_2 = login_user_2_return['token']

    channel_1 = requests.post(f"{URL}/channels/create/v2", json={"token": token_user_1, "name": "Aus", "is_public": True})
    channel_1_id = json.loads(channel_1.text)['channel_id']

    requests.post(f"{URL}/channel/join/v2",json={"token": token_user_2, "channel_id": channel_1_id})

    time_start = requests.post(f"{URL}/standup/start/v1", json = {"token": token_user_1, "channel_id": channel_1_id, "length": 1})
    assert time_start.status_code == OK
    
    send_standup = requests.post(f"{URL}/standup/send/v1", json = {"token": token_user_1, "channel_id": channel_1_id, "message": "a"})
    assert send_standup.status_code == 200

    send_standup_2 = requests.post(f"{URL}/standup/send/v1", json = {"token": token_user_2, "channel_id": channel_1_id, "message": "b"})
    assert send_standup_2.status_code == 200


    active_input_check = {
        "token": token_user_2,
        "channel_id": channel_1_id
    }
  
    active_check_2 = requests.get(f"{URL}/standup/active/v1", params= active_input_check)    
    assert active_check_2.status_code == OK
    active_check_2_return = json.loads(active_check_2.text)
    
    assert active_check_2_return["is_active"] == True
    time_finish = active_check_2_return["time_finish"]
    assert isinstance(time_finish, int)
    
    time.sleep(1)
    
    send_standup_return = json.loads(send_standup.text)
    
    assert send_standup_return == {}
    
    active_input = {
        "token": token_user_1,
        "channel_id": channel_1_id
    }

    active_check = requests.get(f"{URL}/standup/active/v1", params= active_input)    
    active_check_return = json.loads(active_check.text)
    assert active_check.status_code == OK

    assert active_check_return["is_active"] == False
    time_finish = active_check_return["time_finish"]
    assert time_finish == None
    
    message_list_json = requests.get(f"{URL}/channel/messages/v2?token={token_user_1}&channel_id={channel_1_id}&start=0")

    assert message_list_json.status_code == OK
    message_dict = json.loads(message_list_json.text)
    assert message_dict['messages'][0]['message'] ==  'tomjerry: a\njimcook: b'
    

def test_standup_send_invalid_channel(auth_user_1):
    requests.delete(f"{URL}/clear/v1")
    requests.post(f"{URL}/auth/register/v2", json = auth_user_1)
    login_user_1 = requests.post(f"{URL}/auth/login/v2", json = auth_user_1)
    login_user_1_return = json.loads(login_user_1.text)
    token_user_1 = login_user_1_return['token']
    
    channel_1 = requests.post(f"{URL}/channels/create/v2", json = {"token": token_user_1, "name": "Aus", "is_public": False})
    channel_1_id = json.loads(channel_1.text)['channel_id']
    assert channel_1.status_code == OK

    time_start = requests.post(f"{URL}/standup/start/v1", json = {"token": token_user_1, "channel_id": channel_1_id, "length": 5})
    assert time_start.status_code == OK
    
    invalid_channel_id = channel_1_id + 10
    
    send_standup = requests.post(f"{URL}/standup/send/v1", json = {"token": token_user_1, "channel_id": invalid_channel_id, "message": "This is a fun course!"})
    
    assert send_standup.status_code == 400
    
def test_standup_send_long_message(auth_user_1):
    requests.delete(f"{URL}/clear/v1")
    requests.post(f"{URL}/auth/register/v2", json = auth_user_1)
    login_user_1 = requests.post(f"{URL}/auth/login/v2", json = auth_user_1)
    login_user_1_return = json.loads(login_user_1.text)
    token_user_1 = login_user_1_return['token']
    
    channel_1 = requests.post(f"{URL}/channels/create/v2", json = {"token": token_user_1, "name": "Aus", "is_public": False})
    channel_1_id = json.loads(channel_1.text)['channel_id']
    assert channel_1.status_code == OK

    time_start = requests.post(f"{URL}/standup/start/v1", json = {"token": token_user_1, "channel_id": channel_1_id, "length": 5})
    assert time_start.status_code == OK
    
    long_message = "theamazingspiderman" * 150
    send_standup = requests.post(f"{URL}/standup/send/v1", json = {"token": token_user_1, "channel_id": channel_1_id, "message": long_message})
    assert send_standup.status_code == 400
    
def test_standup_send_no_standup(auth_user_1):
    requests.delete(f"{URL}/clear/v1")
    requests.post(f"{URL}/auth/register/v2", json = auth_user_1)
    login_user_1 = requests.post(f"{URL}/auth/login/v2", json = auth_user_1)
    login_user_1_return = json.loads(login_user_1.text)
    token_user_1 = login_user_1_return['token']

    channel_1 = requests.post(f"{URL}/channels/create/v2", json = {"token": token_user_1, "name": "Aus", "is_public": False})
    channel_1_id = json.loads(channel_1.text)['channel_id']
    assert channel_1.status_code == OK
    
    send_standup = requests.post(f"{URL}/standup/send/v1", json = {"token": token_user_1, "channel_id": channel_1_id, "message": "This is a fun course!"})
   
    assert send_standup.status_code == 400
    
def test_standup_send_nonmember(auth_user_1, auth_user_2):
    requests.delete(f"{URL}/clear/v1")
    requests.post(f"{URL}/auth/register/v2", json = auth_user_1)
    login_user_1 = requests.post(f"{URL}/auth/login/v2", json = auth_user_1)
    login_user_1_return = json.loads(login_user_1.text)
    token_user_1 = login_user_1_return['token']
    
    requests.post(f"{URL}/auth/register/v2", json=auth_user_2)
    login_user_2 = requests.post(f"{URL}/auth/login/v2", json=auth_user_2)
    login_user_2_return = json.loads(login_user_2.text)
    token_user_2 = login_user_2_return['token']

    channel_1 = requests.post(f"{URL}/channels/create/v2", json = {"token": token_user_1, "name": "Aus", "is_public": False})
    channel_1_id = json.loads(channel_1.text)['channel_id']
    assert channel_1.status_code == OK

    time_start = requests.post(f"{URL}/standup/start/v1", json = {"token": token_user_1, "channel_id": channel_1_id, "length": 5})
    assert time_start.status_code == OK
    
    send_standup = requests.post(f"{URL}/standup/send/v1", json = {"token": token_user_2, "channel_id": channel_1_id, "message": "This is a fun course!"})
    assert send_standup.status_code == 403
    
def test_standup_send_invalid_token(auth_user_1):
    requests.delete(f"{URL}/clear/v1")
    requests.post(f"{URL}/auth/register/v2", json = auth_user_1)
    login_user_1 = requests.post(f"{URL}/auth/login/v2", json = auth_user_1)
    login_user_1_return = json.loads(login_user_1.text)
    token_user_1 = login_user_1_return['token']
 
    channel_1 = requests.post(f"{URL}/channels/create/v2", json = {"token": token_user_1, "name": "Aus", "is_public": False})
    channel_1_id = json.loads(channel_1.text)['channel_id']
    assert channel_1.status_code == OK

    time_start = requests.post(f"{URL}/standup/start/v1", json = {"token": token_user_1, "channel_id": channel_1_id, "length": 5})
    assert time_start.status_code == OK
    
    invalid_token = f"{token_user_1}2725"
    send_standup = requests.post(f"{URL}/standup/send/v1", json = {"token": invalid_token, "channel_id": channel_1_id, "message": "This is a fun course!"})
    assert send_standup.status_code == 403 
