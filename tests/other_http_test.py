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
    requests.delete(f"{URL}/clear/v1") # clear datastore


# NOTIFICATIONS/GET/V1 HTTP TESTS

# notifications/get/v1 test AccessError for invalid token
def test_invalid_token_notifications_get_v1_http(clear):
    # register user
    register_user1 = requests.post(f"{URL}/auth/register/v2", json = {"email": "user1@gmail.com", "password": "password",  "name_first": "name", "name_last": "surname"})
    assert register_user1.status_code == OK
    user1_token = register_user1.json()['token']
    invalid_token = user1_token + "r9384hf93"
    # call notifications get with the wrong token and expect AccessError
    notifications = requests.get(f"{URL}/notifications/get/v1" + f"?token={invalid_token}")
    assert notifications.status_code == ACCESSERROR

# notifications/get/v1 test order from most recent to most least recent
def test_order_notifications_get_v1_http(clear):
    # register 2 users
    register_user1 = requests.post(f"{URL}/auth/register/v2", json = {"email": "user1@gmail.com", "password": "password",  "name_first": "name", "name_last": "surname"})
    assert register_user1.status_code == OK
    user1_token = register_user1.json()['token']
    user1_id = register_user1.json()['auth_user_id']
    register_user2 = requests.post(f"{URL}/auth/register/v2", json = {"email": "user2@gmail.com", "password": "password",  "name_first": "name", "name_last": "surname"})
    assert register_user2.status_code == OK
    user2_token = register_user2.json()['token']
    user2_id = register_user2.json()['auth_user_id']
    # user1 creates 2 channels
    channel1_create_resp = requests.post(f"{URL}/channels/create/v2", json={'token': user1_token, 'name': "channel1", 'is_public': True})
    assert channel1_create_resp.status_code == OK
    channel1_id = channel1_create_resp.json()['channel_id']
    channel2_create_resp = requests.post(f"{URL}/channels/create/v2", json={'token': user1_token, 'name': "channel2", 'is_public': True})
    assert channel2_create_resp.status_code == OK
    channel2_id = channel2_create_resp.json()['channel_id']
    # user 2 is invited into channel 1 (check notif has one entry) (least recent)
    invite1_resp = requests.post(f"{URL}/channel/invite/v2", json={'token': user1_token, 'channel_id': channel1_id, 'u_id': user2_id})
    assert invite1_resp.status_code == OK
    notifications1 = requests.get(f"{URL}/notifications/get/v1" + f"?token={user2_token}")
    assert notifications1.status_code == OK
    assert len(notifications1.json()['notifications']) == 1
    # user 2 is invited into channel 2 (check notif has two entries) (most recent)
    invite2_resp = requests.post(f"{URL}/channel/invite/v2", json={'token': user1_token, 'channel_id': channel2_id, 'u_id': user2_id})
    assert invite2_resp.status_code == OK
    notifications2 = requests.get(f"{URL}/notifications/get/v1" + f"?token={user2_token}")
    assert notifications2.status_code == OK
    assert len(notifications2.json()['notifications']) == 2
    # check notif orders from most to least recent ("{User's handle} added you to {channel/DM name}")
    profile_resp = requests.get(f"{URL}/user/profile/v1" + f"?token={user1_token}&u_id={user1_id}")
    assert profile_resp.status_code == OK
    user1_handle = profile_resp.json()['user']['handle_str']
    assert notifications2.json()['notifications'][0]['notification_message'] == f"{user1_handle} added you to channel2"
    assert notifications2.json()['notifications'][1]['notification_message'] == f"{user1_handle} added you to channel1"

# SEARCH/V1 HTTP TESTS

# search/v1 test AccessError for invalid token
def test_invalid_token_search_v1_http(clear):
    # register 1 user
    register_user1 = requests.post(f"{URL}/auth/register/v2", json = {"email": "user1@gmail.com", "password": "password",  "name_first": "name", "name_last": "surname"})
    assert register_user1.status_code == OK
    user1_token = register_user1.json()['token']
    invalid_token = user1_token + f"f3984hgvo3i"
    # call search with invalid token and check for AccessError
    search_resp = requests.get(f"{URL}/search/v1" + f"?token={invalid_token}&query_str=hi")
    assert search_resp.status_code == ACCESSERROR

# search/v1 test InputError for invalid query_str length < 0
def test_invalid_query_str_length_0_search_v1_http(clear):
    # register 1 user
    register_user1 = requests.post(f"{URL}/auth/register/v2", json = {"email": "user1@gmail.com", "password": "password",  "name_first": "name", "name_last": "surname"})
    assert register_user1.status_code == OK
    user1_token = register_user1.json()['token']
    # call search with invalid token and check for AccessError
    search_resp = requests.get(f"{URL}/search/v1" + f"?token={user1_token}&query_str=")
    assert search_resp.status_code == INPUTERROR

# search/v1 test InputError for invalid query_str length > 1000
def test_invalid_query_str_length_1000_search_v1_http(clear):
    # register 1 user
    register_user1 = requests.post(f"{URL}/auth/register/v2", json = {"email": "user1@gmail.com", "password": "password",  "name_first": "name", "name_last": "surname"})
    assert register_user1.status_code == OK
    user1_token = register_user1.json()['token']
    # call search with invalid token and check for AccessError
    search_resp = requests.get(f"{URL}/search/v1" + f"?token={user1_token}&query_str=SHTa5kSWPjYKGkZlCAYrClmXBGIkPmqgTwQqnRAyTv6TMoliayVojYxmuC0Sl2rUoUfMDHCTNvQgjzyXREtd9fySIpjI7Vkk0n5p58LY3woSISfJE5tlIfZRs8tiB5gIgIRBTdcnzMAXGsuspUM8P46dFgfZ4pVqiwCoFVrhodC6e3qGYUMRGoGbNl8lsJgyePU52gJAlYktOtDdiMBwILcQ8B8gpnVqWiW8kaNmLxeUbEIdAnoqO0k9ZtAPDdsW57CgLJJZxJWH2GfTOJwR3S8Cu186gUlbr4WcGrZHR6YpAH3Bem5myAUXN4JhP6XLcN7PUks8etwvGhngj7WSFHoHrMKsOZ9pjrNB5fnKJoysU2YRG375t0Qls7CRSPr0oMpEHzY4i2CF14ZZdKrLn8GAI6ORtdzYjd7j4cthrNCCjdfHJRm4g6BswGuCEMYyrJofvxQswRhB7GIPki3oGebdENJuvVszbcJIBXuEhdry3NscwZEhdM8uC13iXdfTqtDVHRnyuB5nf8eTxHsGniU0TSqAw6H4cWboa8WqsfojDFGRXaOnhe1P2BFB5DcwqpuqM0oEuSWlCMHYGpW3CHr4S4oxocRADxKcjun7OjN5eiie9hL1J2H26NwGUPuoOXYNp5g50PfzIbZygC7YBrWEq4f7S9H7HvJA2M9nqhFqcM1Vi8lW70eviJBhQd4zfaMHDZ6ihh9HxV4rYAlx1r3pKeA9JyFJx7363ckjiDo7GPZjXNaZQfR4QhJ2kAFqKTmHUwOjJufRw3S8OWS2PagQ4o25TBhF41MTe9kRUkaLEwxJBDLqZMxsbHZWN1pPiP2rjkgOE6iQ58ufTOgAQ6RQvxGYnHY0uNeEG88yucblp76BKZEuE3EykF8Qnt8lmmFbM80dkZt2Q18AvPv8hUYqXl3tZhKgxiF2vNU3iyt1IVLeczc7BvWJ9W2soLoyl4NWcwTeZxpQV2rMGkBHOVizWQgHqlUTKHpTocte87qwEqSntUTfMShpM4PWWgz2Vyt6WYO0jNFYZO6dksLRVHVB58ttQu1dsidodYymkXibC")
    assert search_resp.status_code == INPUTERROR

# search/v1 test normal functionality
def test_search_v1_http(clear):
    # register 1 user
    register_user1 = requests.post(f"{URL}/auth/register/v2", json = {"email": "user1@gmail.com", "password": "password",  "name_first": "name", "name_last": "surname"})
    assert register_user1.status_code == OK
    user1_token = register_user1.json()['token']
    # user1 creates channel
    channel1_create_resp = requests.post(f"{URL}/channels/create/v2", json={'token': user1_token, 'name': "channel1", 'is_public': True})
    assert channel1_create_resp.status_code == OK
    channel1_id = channel1_create_resp.json()['channel_id']
    # check search('hello') is empty
    search1_resp = requests.get(f"{URL}/search/v1" + f"?token={user1_token}&query_str=hello")
    assert search1_resp.status_code == OK
    assert len(search1_resp.json()['messages']) == 0
    # user messages hello
    message1_resp = requests.post(f"{URL}/message/send/v1", json={'token': user1_token, 'channel_id': channel1_id, 'message': "hello"})
    assert message1_resp.status_code == OK
    # check search('hello') is 1
    search2_resp = requests.get(f"{URL}/search/v1" + f"?token={user1_token}&query_str=hello")
    assert search2_resp.status_code == OK
    assert len(search2_resp.json()['messages']) == 1
    # user messages Hola
    message2_resp = requests.post(f"{URL}/message/send/v1", json={'token': user1_token, 'channel_id': channel1_id, 'message': "Hola"})
    assert message2_resp.status_code == OK
    # check search('Hola') is 1
    search3_resp = requests.get(f"{URL}/search/v1" + f"?token={user1_token}&query_str=Hola")
    assert search3_resp.status_code == OK
    assert len(search3_resp.json()['messages']) == 1
    # check search('l') is 2
    search4_resp = requests.get(f"{URL}/search/v1" + f"?token={user1_token}&query_str=l")
    assert search4_resp.status_code == OK
    assert len(search4_resp.json()['messages']) == 2
    # check search('H') is 1
    search5_resp = requests.get(f"{URL}/search/v1" + f"?token={user1_token}&query_str=H")
    assert search5_resp.status_code == OK
    assert len(search5_resp.json()['messages']) == 2
    # check search ('hellofam') is 0
    search6_resp = requests.get(f"{URL}/search/v1" + f"?token={user1_token}&query_str=hellofam")
    assert search6_resp.status_code == OK
    assert len(search6_resp.json()['messages']) == 0
    