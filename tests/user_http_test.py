import pytest
import json
import requests
from src import config
BASE_ADDRESS = 'http://127.0.0.1'
BASE_PORT = config.port
BASE_URL = f"{BASE_ADDRESS}:{BASE_PORT}"


@pytest.fixture
def clear():
    requests.delete(f"{BASE_URL}/clear/v1")


@pytest.fixture
def user_dict1():
    response = requests.post(f"{BASE_URL}/auth/register/v2", json={'email': "third@gmail.com",
                                                                   'password': "hello123", 'name_first': "Trent", 'name_last': "Arnold"})
    dict = json.loads(response.text)
    return dict


@pytest.fixture
def user_dict2():
    response = requests.post(f"{BASE_URL}/auth/register/v2", json={'email': "second@gmail.com",
                                                                   'password': "password", 'name_first': "Ben", 'name_last': "Mendy"})
    dict = json.loads(response.text)
    return dict


@pytest.fixture
def image_link_jpeg():
    link = 'https://s.ndtvimg.com/images/content/2015/sep/806/roshan-mahanama.jpg'
    return link


@pytest.fixture
def image_link_png():
    link = 'https://www.cse.unsw.edu.au/~richardb/index_files/RichardBuckland-200.png'
    return link


@pytest.fixture
def default_link():
    link = f'{BASE_URL}/src/static/default.jpg'
    return link


def test_invalid_token_all_users(clear, user_dict1):
    token = user_dict1['token']
    invalid_token = f"{token}123"
    all_users_response = requests.get(
        f"{BASE_URL}/users/all/v1?token={invalid_token}")
    assert all_users_response.status_code == 403


def test_one_all_users(clear, user_dict1):
    token = user_dict1['token']
    all_users_response = requests.get(f"{BASE_URL}/users/all/v1?token={token}")
    assert all_users_response.status_code == 200
    all_users_data = json.loads(all_users_response.text)
    assert len(all_users_data) == 1
    assert all_users_data[0]['email'] == "third@gmail.com"
    assert all_users_data[0]['name_last'] == "Arnold"


def test_multiple_all_users(clear, user_dict1, user_dict2):
    token = user_dict1['token']
    all_users_response = requests.get(f"{BASE_URL}/users/all/v1?token={token}")
    assert all_users_response.status_code == 200
    all_users_data = json.loads(all_users_response.text)
    assert len(all_users_data) == 2
    assert all_users_data[0]['email'] == "third@gmail.com"
    assert all_users_data[0]['name_last'] == "Arnold"
    assert all_users_data[1]['email'] == "second@gmail.com"
    assert all_users_data[1]['name_last'] == "Mendy"


def test_invalid_token_user_profile(clear, user_dict1):
    token = user_dict1['token']
    u_id = user_dict1['auth_user_id']
    invalid_token = f"{token}123"
    profile_response = requests.get(
        f"{BASE_URL}/user/profile/v1?token={invalid_token}&u_id={u_id}")
    assert profile_response.status_code == 403


def test_invalid_u_id_user_profile(clear, user_dict1):
    token = user_dict1['token']
    u_id = user_dict1['auth_user_id']
    invalid_id = u_id + 1
    profile_response = requests.get(
        f"{BASE_URL}/user/profile/v1?token={token}&u_id={invalid_id}")
    assert profile_response.status_code == 400


def test_working_user_profile(clear, user_dict1):
    token = user_dict1['token']
    u_id = user_dict1['auth_user_id']
    profile_response = requests.get(
        f"{BASE_URL}/user/profile/v1?token={token}&u_id={u_id}")
    assert profile_response.status_code == 200
    profile_data = json.loads(profile_response.text)['user']
    assert profile_data['name_first'] == "Trent"
    assert profile_data['name_last'] == "Arnold"


def test_invalid_token_user_setname(clear):
    reg_response = requests.post(f"{BASE_URL}/auth/register/v2", json={'email': "third@gmail.com",
                                                                       'password': "hello123", 'name_first': "Trent", 'name_last': "Arnold"})
    reg_return = json.loads(reg_response.text)
    token = reg_return['token']
    invalid_token = f"{token}123"
    setname_response = requests.put(f"{BASE_URL}/user/profile/setname/v1", json={
                                    'token': invalid_token, 'name_first': "Trent", 'name_last': "Arnold"})
    assert setname_response.status_code == 403


def test_short_firstname_user_setname(clear, user_dict1):
    token = user_dict1['token']
    setname_response = requests.put(f"{BASE_URL}/user/profile/setname/v1", json={
                                    'token': token, 'name_first': "", 'name_last': "Arnold"})
    assert setname_response.status_code == 400


def test_long_firstname_user_setname(clear, user_dict1):
    token = user_dict1['token']
    setname_response = requests.put(f"{BASE_URL}/user/profile/setname/v1", json={'token': token,
                                                                                 'name_first': "thisnameismuchmuchmmuchmuchmuchmuchlongerthanfiftycharacters", 'name_last': "Arnold"})
    assert setname_response.status_code == 400


def test_short_surname_user_setname(clear, user_dict1):
    token = user_dict1['token']
    setname_response = requests.put(f"{BASE_URL}/user/profile/setname/v1", json={
                                    'token': token, 'name_first': "Trent", 'name_last': ""})
    assert setname_response.status_code == 400


def test_long_surname_user_setname(clear, user_dict1):
    token = user_dict1['token']
    setname_response = requests.put(f"{BASE_URL}/user/profile/setname/v1", json={'token': token,
                                                                                 'name_first': "Trent", 'name_last': "thisnameismuchmuchmmuchmuchmuchmuchlongerthanfiftycharacters"})
    assert setname_response.status_code == 400


def test_working_user_setname(clear, user_dict1):
    token = user_dict1['token']
    u_id = user_dict1['auth_user_id']
    setname_response = requests.put(f"{BASE_URL}/user/profile/setname/v1", json={
                                    'token': token, 'name_first': "Mason", 'name_last': "Greenwood"})
    assert setname_response.status_code == 200
    profile_response = requests.get(
        f"{BASE_URL}/user/profile/v1?token={token}&u_id={u_id}")
    assert profile_response.status_code == 200
    profile_data = json.loads(profile_response.text)['user']
    assert profile_data['name_first'] == "Mason"
    assert profile_data['name_last'] == "Greenwood"


def test_updates_in_channels_user_setname(clear, user_dict1):
    token = user_dict1['token']
    create_response = requests.post(
        f"{BASE_URL}/channels/create/v2", json={'token': token, 'name': "channel", 'is_public': True})
    assert create_response.status_code == 200
    create_data = json.loads(create_response.text)
    channel_id = create_data['channel_id']
    setname_response = requests.put(f"{BASE_URL}/user/profile/setname/v1", json={
                                    'token': token, 'name_first': "Mason", 'name_last': "Greenwood"})
    assert setname_response.status_code == 200
    details_response = requests.get(
        f"{BASE_URL}/channel/details/v2?token={token}&channel_id={channel_id}")
    details_data = json.loads(details_response.text)
    for member in details_data['all_members']:
        assert member['name_first'] == "Mason"
        assert member['name_last'] == "Greenwood"


def test_invalid_token_user_setemail(clear, user_dict1):
    token = user_dict1['token']
    invalid_token = f"{token}123"
    setemail_response = requests.put(f"{BASE_URL}/user/profile/setemail/v1", json={
                                     'token': invalid_token, 'email': "third@gmail.com"})
    assert setemail_response.status_code == 403


def test_email_in_use_user_setemail(clear, user_dict1, user_dict2):
    token = user_dict1['token']
    setemail_response = requests.put(
        f"{BASE_URL}/user/profile/setemail/v1", json={'token': token, 'email': "second@gmail.com"})
    assert setemail_response.status_code == 400


def test_invalid_email_user_setemail(clear, user_dict1):
    token = user_dict1['token']

    setemail_response = requests.put(
        f"{BASE_URL}/user/profile/setemail/v1", json={'token': token, 'email': "first.com"})
    assert setemail_response.status_code == 400

    setemail_response = requests.put(f"{BASE_URL}/user/profile/setemail/v1", json={
                                     'token': token, 'email': "first/last@gmail.com"})
    assert setemail_response.status_code == 400

    setemail_response = requests.put(
        f"{BASE_URL}/user/profile/setemail/v1", json={'token': token, 'email': "   last@gmail.com"})
    assert setemail_response.status_code == 400


def test_working_user_setemail(clear, user_dict1):
    token = user_dict1['token']
    setemail_response = requests.put(
        f"{BASE_URL}/user/profile/setemail/v1", json={'token': token, 'email': "first@gmail.com"})
    assert setemail_response.status_code == 200
    logout_response = requests.post(
        f"{BASE_URL}/auth/logout/v1", json={'token': token})
    assert logout_response.status_code == 200
    login_response = requests.post(
        f"{BASE_URL}/auth/login/v2", json={'email': "first@gmail.com", 'password': "hello123"})
    assert login_response.status_code == 200


def test_updates_in_channels_user_setemail(clear, user_dict1):
    token = user_dict1['token']
    create_response = requests.post(
        f"{BASE_URL}/channels/create/v2", json={'token': token, 'name': "channel", 'is_public': True})
    assert create_response.status_code == 200
    create_data = json.loads(create_response.text)
    channel_id = create_data['channel_id']
    setemail_response = requests.put(
        f"{BASE_URL}/user/profile/setemail/v1", json={'token': token, 'email': "newemail@gmail.com"})
    assert setemail_response.status_code == 200
    details_response = requests.get(
        f"{BASE_URL}/channel/details/v2?token={token}&channel_id={channel_id}")
    details_data = json.loads(details_response.text)
    for member in details_data['all_members']:
        assert member['email'] == "newemail@gmail.com"


def test_invalid_token_user_sethandle(clear, user_dict1):
    token = user_dict1['token']
    invalid_token = f"{token}123"
    sethandle_response = requests.put(f"{BASE_URL}/user/profile/sethandle/v1", json={
                                      'token': invalid_token, 'handle_str': "handle123"})
    assert sethandle_response.status_code == 403


def test_invalid_length_user_sethandle(clear, user_dict1):
    token = user_dict1['token']

    sethandle_response = requests.put(f"{BASE_URL}/user/profile/sethandle/v1", json={
                                      'token': token, 'handle_str': "thishandleiswaytoolong123"})
    assert sethandle_response.status_code == 400

    sethandle_response = requests.put(
        f"{BASE_URL}/user/profile/sethandle/v1", json={'token': token, 'handle_str': "so"})
    assert sethandle_response.status_code == 400


def test_handle_in_use_user_sethandle(clear, user_dict1, user_dict2):
    token = user_dict1['token']
    sethandle_response = requests.put(
        f"{BASE_URL}/user/profile/sethandle/v1", json={'token': token, 'handle_str': "benmendy"})
    assert sethandle_response.status_code == 400


def test_handle_is_not_alphanum_user_sethandle(clear, user_dict1):
    token = user_dict1['token']
    sethandle_response = requests.put(
        f"{BASE_URL}/user/profile/sethandle/v1", json={'token': token, 'handle_str': "joe/.mama"})
    assert sethandle_response.status_code == 400


def test_working_user_handle(clear, user_dict1):
    token = user_dict1['token']
    u_id = user_dict1['auth_user_id']
    sethandle_response = requests.put(
        f"{BASE_URL}/user/profile/sethandle/v1", json={'token': token, 'handle_str': "newhandle"})
    assert sethandle_response.status_code == 200
    profile_response = requests.get(
        f"{BASE_URL}/user/profile/v1?token={token}&u_id={u_id}")
    assert profile_response.status_code == 200
    profile_data = json.loads(profile_response.text)['user']
    assert profile_data['handle_str'] == "newhandle"


def test_updates_in_channels_user_sethandle(clear, user_dict1):
    token = user_dict1['token']
    create_response = requests.post(
        f"{BASE_URL}/channels/create/v2", json={'token': token, 'name': "channel", 'is_public': True})
    assert create_response.status_code == 200
    create_data = json.loads(create_response.text)
    channel_id = create_data['channel_id']
    sethandle_response = requests.put(
        f"{BASE_URL}/user/profile/sethandle/v1", json={'token': token, 'handle_str': "newhandle"})
    assert sethandle_response.status_code == 200
    details_response = requests.get(
        f"{BASE_URL}/channel/details/v2?token={token}&channel_id={channel_id}")
    details_data = json.loads(details_response.text)
    for member in details_data['all_members']:
        assert member['handle_str'] == "newhandle"


def test_upload_not_jpeg(clear, user_dict1, image_link_png):
    token = user_dict1['token']
    upload_response = requests.post(f"{BASE_URL}/user/profile/uploadphoto/v1", json={
                                    'token': token, 'img_url': image_link_png, 'x_start': 0, 'x_end': 100, 'y_start': 0, 'y_end': 100})
    assert upload_response.status_code == 400


def test_upload_retrieve_fail(clear, user_dict1):
    token = user_dict1['token']
    upload_response = requests.post(f"{BASE_URL}/user/profile/uploadphoto/v1", json={'token': token,
                                                                                     'img_url': 'www.fakeimagelinkffwnfwnf.jpeg', 'x_start': 0, 'x_end': 100, 'y_start': 0, 'y_end': 100})
    assert upload_response.status_code == 400


def test_upload_invalid_x(clear, user_dict1, image_link_jpeg):
    token = user_dict1['token']
    upload_response = requests.post(f"{BASE_URL}/user/profile/uploadphoto/v1", json={
                                    'token': token, 'img_url': image_link_jpeg, 'x_start': -10, 'x_end': 100, 'y_start': 0, 'y_end': 100})
    assert upload_response.status_code == 400


def test_upload_invalid_y(clear, user_dict1, image_link_jpeg):
    token = user_dict1['token']
    upload_response = requests.post(f"{BASE_URL}/user/profile/uploadphoto/v1", json={
                                    'token': token, 'img_url': image_link_jpeg, 'x_start': 0, 'x_end': 100, 'y_start': -10, 'y_end': 100})
    assert upload_response.status_code == 400


def test_upload_switch_sides(clear, user_dict1, image_link_jpeg):
    token = user_dict1['token']
    upload_response = requests.post(f"{BASE_URL}/user/profile/uploadphoto/v1", json={
                                    'token': token, 'img_url': image_link_jpeg, 'x_start': 100, 'x_end': 50, 'y_start': 0, 'y_end': 100})
    assert upload_response.status_code == 400


def test_upload_working_crop(clear, user_dict1, image_link_jpeg):
    token = user_dict1['token']
    upload_response = requests.post(f"{BASE_URL}/user/profile/uploadphoto/v1", json={
                                    'token': token, 'img_url': image_link_jpeg, 'x_start': 0, 'x_end': 100, 'y_start': 0, 'y_end': 100})
    assert upload_response.status_code == 200


def test_upload_updated_user(clear, user_dict1, image_link_jpeg, default_link):
    token = user_dict1['token']
    create_response = requests.post(
        f"{BASE_URL}/channels/create/v2", json={'token': token, 'name': "channel", 'is_public': True})
    assert create_response.status_code == 200
    channel_id = json.loads(create_response.text)['channel_id']
    upload_response = requests.post(f"{BASE_URL}/user/profile/uploadphoto/v1", json={
                                    'token': token, 'img_url': image_link_jpeg, 'x_start': 0, 'x_end': 100, 'y_start': 0, 'y_end': 100})
    assert upload_response.status_code == 200
    channel_details = requests.get(
        f"{BASE_URL}/channel/details/v2" + f"?token={token}&channel_id={channel_id}")
    assert channel_details.status_code == 200
    data = json.loads(channel_details.text)
    for owner in data['owner_members']:
        assert owner['profile_img_url'] != default_link


def test_user_stats_invalid_token(clear, user_dict1):
    token = user_dict1['token']
    invalid_token = f"{token}123"
    stats_response = requests.get(
        f"{BASE_URL}/user/stats/v1?token={invalid_token}")
    assert stats_response.status_code == 403


def test_user_stats_zero_denominator(clear, user_dict1):
    token = user_dict1['token']
    stats_response = requests.get(f"{BASE_URL}/user/stats/v1?token={token}")
    assert stats_response.status_code == 200
    stat_data = json.loads(stats_response.text)['user_stats']
    assert stat_data['involvement_rate'] == 0


def test_user_stats_channeldata(clear, user_dict1):
    token = user_dict1['token']
    create_response = requests.post(
        f"{BASE_URL}/channels/create/v2", json={'token': token, 'name': "channel", 'is_public': True})
    assert create_response.status_code == 200
    stats_response = requests.get(f"{BASE_URL}/user/stats/v1?token={token}")
    assert stats_response.status_code == 200
    stat_data = json.loads(stats_response.text)['user_stats']
    assert len(stat_data['channels_joined']) > 1
    assert stat_data['involvement_rate'] == 1


def test_user_stats_dmdata(clear, user_dict1):
    token = user_dict1['token']
    dm_response = requests.post(
        f"{BASE_URL}/dm/create/v1", json={'token': token, 'u_ids': []})
    assert dm_response.status_code == 200
    stats_response = requests.get(f"{BASE_URL}/user/stats/v1?token={token}")
    assert stats_response.status_code == 200
    stat_data = json.loads(stats_response.text)['user_stats']
    assert len(stat_data['dms_joined']) > 1
    assert stat_data['involvement_rate'] == 1

# def test_user_stats_messagedata(clear, user_dict1):
#     token = user_dict1['token']
#     create_response = requests.post(f"{BASE_URL}/channels/create/v2", json={'token': token, 'name': "channel", 'is_public': True})
#     assert create_response.status_code == 200
#     channel_id = json.loads(create_response.text)['channel_id']
#     msg_send = requests.post(f"{BASE_URL}/message/send/v1", json={'token': token, 'channel_id': channel_id, 'message': "hey"})
#     assert msg_send.status_code == 200
#     stats_response = requests.get(f"{BASE_URL}/user/stats/v1?token={token}")
#     assert stats_response.status_code == 200
#     stat_data = json.loads(stats_response.text)['user_stats']
#     assert len(stat_data['messages_sent']) > 1

# def test_user_stats_leave_channel(clear, user_dict1):
#     token = user_dict1['token']
#     create_response = requests.post(f"{BASE_URL}/channels/create/v2", json={'token': token, 'name': "channel", 'is_public': True})
#     assert create_response.status_code == 200
#     channel_id = json.loads(create_response.text)['channel_id']
#     leave_response = requests.post(f"{BASE_URL}/channel/leave/v1", json={'token': token, 'channel_id': channel_id})
#     assert leave_response.status_code == 200
#     stats_response = requests.get(f"{BASE_URL}/user/stats/v1?token={token}")
#     assert stats_response.status_code == 200
#     stat_data = json.loads(stats_response.text)['user_stats']
#     assert stat_data['involvement_rate'] == 0

# def test_user_stats_leave_dm(clear, user_dict1):
#     token = user_dict1['token']
#     dm_response = requests.post(f"{BASE_URL}/dm/create/v1", json = {'token': token, 'u_ids': []})
#     assert dm_response.status_code == 200
#     dm_id = json.loads(dm_response.text)['dm_id']
#     dm_leave = requests.post(f"{BASE_URL}/dm/leave/v1", json = {'token': token, 'dm_id': dm_id})
#     assert dm_leave.status_code == 200
#     stats_response = requests.get(f"{BASE_URL}/user/stats/v1?token={token}")
#     assert stats_response.status_code == 200
#     stat_data = json.loads(stats_response.text)['user_stats']
#     assert stat_data['involvement_rate'] == 0
