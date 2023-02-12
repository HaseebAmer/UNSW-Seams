# import pytest
# from src.channels import channels_create_v1, channels_listall_v1, channels_list_v1
# from src.auth import auth_register_v1, auth_login_v1
# from src.other import clear_v1
# from src.error import InputError, AccessError
# from src.channel import channel_invite_v1, channel_join_v1


# # test if channel name is too short (< 1 character)
# def test_short_name_channel_create():
#     clear_v1()
#     return_value = auth_register_v1("last123@gmail.com", "hello123", "Franz", "Beckenbauer")
#     token = return_value['token']
#     with pytest.raises(InputError):
#         assert channels_create_v1(token, "", True)

# # test if channel name is too long
# def test_long_name_channel_create():
#     clear_v1()
#     return_value = auth_register_v1("last123@gmail.com", "helloworld", "Trent", "Arnold")
#     token = return_value['token']
#     with pytest.raises(InputError):
#         assert channels_create_v1(token, "veryverylongchannelname", True)

# # test for if an invalid user_id is passed into the function
# def test_invalid_token_channel_create():
#     clear_v1()
#     return_value = auth_register_v1("last123@gmail.com", "helloworld", "Trent", "Arnold")
#     token = return_value['token']
#     token = token + 'S'
#     with pytest.raises(AccessError):
#         assert channels_create_v1(token, "channel_name", True)

# # check correct implementation

# def test_working_channel_create():
#     clear_v1()
#     return_value1 = auth_register_v1("last123@gmail.com", "hello123", "Franz", "Beckenbauer")
#     token = return_value1['token']
#     return_value2 = channels_create_v1(token, "name", True)
#     channel_id = return_value2['channel_id']

#     list_return = channels_listall_v1(token)
#     flag = 0
#     for channel in list_return['channels']:
#         if channel['channel_id'] == channel_id:
#             flag = 1
#     assert flag == 1

# # Tests if channels_list_v1 works for no members in channel
# # def test_auth_user_not_part_of_any_channels():
# #     clear_v1()
# #     auth_id = auth_register_v1('email@gmail.com', 'password', 'firstname', 'surname')
# #     auth_user_id = auth_id['auth_user_id']
# #     assert channels_list_v1(auth_user_id) == {'channels' : []}

# # # Tests if channels_list_v1 works person creating
# # def test_auth_user_create_channel_channels_list():
# #     clear_v1()
# #     auth_id = auth_register_v1('email@gmail.com', 'password', 'firstname', 'surname')
# #     auth_user_id = auth_id['auth_user_id']
# #     channelid = channels_create_v1(auth_user_id, 'channel1', True)
# #     channel_id = channelid['channel_id']
# #     assert channels_list_v1(auth_user_id) == {'channels' : [{'channel_id' : channel_id, 'name' : 'channel1'}]}

# # # Test if channels_list_v1 works for person invited
# # def test_user_invited_to_public_channel_channels_list():
# #     clear_v1()
# #     auth_id_owner = auth_register_v1('email@gmail.com', 'password', 'firstname', 'surname')
# #     owner_id = auth_id_owner['auth_user_id']
# #     auth_id_joiner = auth_register_v1('joiner@gmail.com', 'password', '1stname', 'lastname')
# #     joiner_id = auth_id_joiner['auth_user_id']
# #     channel_id = channels_create_v1(owner_id, 'channelname', True)
# #     channel = channel_id['channel_id']
# #     channel_invite_v1(owner_id, channel, joiner_id)
# #     assert channels_list_v1(joiner_id) == {'channels' : [{'channel_id' : channel, 'name' : 'channelname'}]}

# # # Test to see if channels_list_v1 works for person joining a public channel
# # def test_user_joins_channel_channels_list():
# #     clear_v1()
# #     auth_id = auth_register_v1('email@gmail.com', 'password', 'firstname', 'surname')
# #     id = auth_id['auth_user_id']
# #     auth_id_joiner = auth_register_v1('joiner@gmail.com', 'password', '1stname', 'lastname')
# #     joiner_id = auth_id_joiner['auth_user_id']
# #     channel_id = channels_create_v1(id, 'channelname', True)
# #     channel = channel_id['channel_id']
# #     channel_join_v1(joiner_id, channel)
# #     assert channels_list_v1(joiner_id) == {'channels' : [{'channel_id' : channel, 'name' : 'channelname'}]}


# # # Tests to see if channels_list_v1 works for person with global perms joining a private channel
# # def test_global_perms_user_can_join_private_channel_without_invite_channels_list():
# #     clear_v1()
# #     auth_id = auth_register_v1('email@gmail.com', 'password', 'firstname', 'surname')
# #     id = auth_id['auth_user_id']
# #     auth_id_joiner = auth_register_v1('joiner@gmail.com', 'password', '1stname', 'lastname')
# #     joiner_id = auth_id_joiner['auth_user_id']
# #     channel_id = channels_create_v1(joiner_id, 'channelname', False)
# #     channel = channel_id['channel_id']
# #     channel_join_v1(id, channel)
# #     assert channels_list_v1(id) == {'channels' : [{'channel_id' : channel, 'name' : 'channelname'}]}

# # # Test to see if channels_list_v1 works for a person invited by a non-owner member of a private channel
# # def test_user_invited_by_nonowner_in_private_channel_channels_list():
# #     clear_v1()
# #     auth_id_owner = auth_register_v1('email@gmail.com', 'password', 'firstname', 'surname')
# #     owner_id = auth_id_owner['auth_user_id']
# #     auth_id_joiner = auth_register_v1('joiner@gmail.com', 'password', '1stname', 'lastname')
# #     joiner_id = auth_id_joiner['auth_user_id']
# #     auth_id_inviter = auth_register_v1('inviter@gmail.com', 'password', 'name1', 'name2')
# #     inviter_id = auth_id_inviter['auth_user_id']
# #     channel_id = channels_create_v1(owner_id, 'channelname', False)
# #     channel = channel_id['channel_id']
# #     channel_invite_v1(owner_id, channel, inviter_id)
# #     channel_invite_v1(inviter_id, channel, joiner_id)
# #     assert channels_list_v1(joiner_id) == {'channels' : [{'channel_id' : channel, 'name' : 'channelname'}]}

# # # Test to see if access error is raised for invalid auth_user_id
# # def test_access_error_channels_list():
# #     clear_v1()
# #     auth_register_v1('email@gmail.com', 'password', 'firstname' , 'surname')
# #     with pytest.raises(AccessError):
# #         channels_list_v1(5)

# # # Test to see if channel_list_all works when no channels are created
# # def test_no_channel_created_channel_listall():
# #     clear_v1()
# #     auth_id = auth_register_v1('email@gmail.com', 'password', 'firstname', 'surname')
# #     id = auth_id['auth_user_id']
# #     assert channels_listall_v1(id) == {'channels' : []}

# # # Test to see if channel_list_all works for two channels
# # def test_public_and_private_channels_channel_listall():
# #     clear_v1()
# #     auth_id = auth_register_v1('email@gmail.com', 'password', 'firstname' , 'surname')
# #     id = auth_id['auth_user_id']
# #     channel_id = channels_create_v1(id, 'channelname', True)
# #     channel = channel_id['channel_id']
# #     assert channels_listall_v1(id) == {'channels' : [{'channel_id' : channel, 'name' : 'channelname'}]}
# #     channel_id2 = channels_create_v1(id, 'channel2', False)
# #     channel2 = channel_id2['channel_id']
# #     assert channels_listall_v1(id) == {'channels' : [{'channel_id' : channel, 'name' : 'channelname'}, {'channel_id' : channel2, 'name' : 'channel2'}]}

# # # Test to see if channel_list_all raises an error for invalid auth_user_id
# # def test_raise_access_error_channels_listall():
# #     clear_v1()
# #     auth_register_v1('email@gmail.com', 'password', 'firstname', 'surname')
# #     with pytest.raises(AccessError):
# #         channels_listall_v1(5)

# # def test_working_channel_create():
# #     clear_v1()
# #     return_value1 = auth_register_v1("last123@gmail.com", "hello123", "Franz", "Beckenbauer")
# #     auth_id = return_value1['auth_user_id']
# #     return_value2 = channels_create_v1(auth_id, "name", True)
# #     channel_id = return_value2['channel_id']

# #     list_return = channels_listall_v1(auth_id)
# #     flag = 0
# #     for channel in list_return['channels']:
# #         if channel['channel_id'] == channel_id:
# #             flag = 1
# #     assert flag == 1

# # Tests if channels_list_v1 works for no members in channel [x] [x]
# def test_auth_user_not_part_of_any_channels():
#     clear_v1()
#     auth_register_v1('email@gmail.com', 'password', 'firstname', 'surname')
#     login = auth_login_v1('email@gmail.com', 'password')
#     token = login['token']
#     assert channels_list_v1(token) == {'channels' : []}

# # Tests if channels_list_v1 works person creating [x] [x]
# def test_auth_user_create_channel_channels_list():
#     clear_v1()
#     auth_register_v1('email@gmail.com', 'password', 'firstname', 'surname')
#     login = auth_login_v1('email@gmail.com', 'password')
#     token = login['token']
#     channels_create_v1(token, 'channel1', True)
#     assert len(channels_list_v1(token)['channels']) == 1

# # # Test if channels_list_v1 works for person invited [x] [x]
# # def test_user_invited_to_public_channel_channels_list():
# #     clear_v1()
# #     auth_register_v1('email@gmail.com', 'password', 'firstname', 'surname')
# #     login_owner = auth_login_v1('email@gmail.com', 'password')
# #     owner_token = login_owner['token']
# #     auth_register_v1('joiner@gmail.com', 'password', '1stname', 'lastname')
# #     login_joiner = auth_login_v1('joiner@gmail.com', 'password')
# #     joiner_token = login_joiner['token']
# #     joiner_id = login_joiner['auth_user_id']
# #     channel_id = channels_create_v1(owner_token, 'channelname', True)
# #     channel = channel_id['channel_id']
# #     channel_invite_v1(owner_token, channel, joiner_id)
# #     assert channels_list_v1(joiner_token) == {'channels' : [{'channel_id' : channel, 'name' : 'channelname'}]}

# # # Test to see if channels_list_v1 works for person joining a public channel [x] [x]
# # def test_user_joins_channel_channels_list():
# #     clear_v1()
# #     auth_register_v1('email@gmail.com', 'password', 'firstname', 'surname')
# #     login_owner = auth_login_v1('email@gmail.com', 'password')
# #     owner_token = login_owner['token']
# #     auth_register_v1('joiner@gmail.com', 'password', '1stname', 'lastname')
# #     login_joiner = auth_login_v1('joiner@gmail.com', 'password')
# #     joiner_token = login_joiner['token']
# #     channel_id = channels_create_v1(owner_token, 'channelname', True)
# #     channel = channel_id['channel_id']
# #     channel_join_v1(joiner_token, channel)
# #     assert channels_list_v1(joiner_token) == {'channels' : [{'channel_id' : channel, 'name' : 'channelname'}]}


# # # Tests to see if channels_list_v1 works for person with global perms joining a private channel [x] [x]
# # def test_global_perms_user_can_join_private_channel_without_invite_channels_list():
# #     clear_v1()
# #     auth_register_v1('email@gmail.com', 'password', 'firstname', 'surname')
# #     login_global = auth_login_v1('email@gmail.com', 'password')
# #     token_global = login_global['token']
# #     auth_register_v1('owner@gmail.com', 'password', '1stname', 'lastname')
# #     login_owner = auth_login_v1('owner@gmail.com', 'password')
# #     owner_token = login_owner['token']
# #     channel_id = channels_create_v1(owner_token, 'channelname', False)
# #     channel = channel_id['channel_id']
# #     channel_join_v1(token_global, channel)
# #     assert channels_list_v1(token_global) == {'channels' : [{'channel_id' : channel, 'name' : 'channelname'}]}

# # # Test to see if channels_list_v1 works for a person invited by a non-owner member of a private channel [x] [x]
# # def test_user_invited_by_nonowner_in_private_channel_channels_list():
# #     clear_v1()
# #     # register and login users
# #     auth_register_v1('email@gmail.com', 'password', 'firstname', 'surname')
# #     owner = auth_login_v1('email@gmail.com', 'password')
# #     owner_token = owner['token']
# #     auth_register_v1('joiner@gmail.com', 'password', '1stname', 'lastname')
# #     joiner = auth_login_v1('joiner@gmail.com', 'password')
# #     joiner_id = joiner['auth_user_id']
# #     joiner_token = joiner['token']
# #     auth_register_v1('inviter@gmail.com', 'password', 'name1', 'name2')
# #     inviter = auth_login_v1('inviter@gmail.com', 'password')
# #     inviter_token = inviter['token']
# #     inviter_id = inviter['auth_user_id']
# #     # create channel
# #     channel_id = channels_create_v1(owner_token, 'channelname', False)
# #     channel = channel_id['channel_id']

# #     # owner of private channel invites inviter
# #     channel_invite_v1(owner_token, channel, inviter_id)
# #     # inviter (member of private channel) invites joiner
# #     channel_invite_v1(inviter_token, channel, joiner_id)

# #     assert channels_list_v1(joiner_token) == {'channels' : [{'channel_id' : channel, 'name' : 'channelname'}]}

# # Test to see if access error is raised for invalid token for channels list [x] [x]
# def test_access_error_channels_list():
#     clear_v1()
#     # register and login user
#     auth_register_v1('email@gmail.com', 'password', 'firstname' , 'surname')
#     login = auth_login_v1('email@gmail.com', 'password')
#     token = login['token']
#     invalid_token = token + "69420"
#     # create channel
#     channels_create_v1(token, "t1", True)
#     # test invalid token
#     with pytest.raises(AccessError):
#         channels_list_v1(invalid_token)

# # Test to see if channel_list_all works when no channels are created [x]
# def test_no_channel_created_channel_listall():
#     clear_v1()
#     auth_register_v1('email@gmail.com', 'password', 'firstname', 'surname')
#     login = auth_login_v1('email@gmail.com', 'password')
#     token = login['token']
#     assert len(channels_listall_v1(token)['channels']) == 0

# # Test to see if channel_list_all works for multiple channels [x]
# def test_public_and_private_channels_channel_listall():
#     clear_v1()
#     auth_register_v1('email@gmail.com', 'password', 'firstname' , 'surname')
#     login = auth_login_v1('email@gmail.com', 'password')
#     token = login['token']
#     channel_id = channels_create_v1(token, 'channelname', True)
#     channel = channel_id['channel_id']
#     assert channels_listall_v1(token) == {'channels' : [{'channel_id' : channel, 'name' : 'channelname'}]}
#     channel_id2 = channels_create_v1(token, 'channel2', False)
#     channel2 = channel_id2['channel_id']
#     assert channels_listall_v1(token) == {'channels' : [{'channel_id' : channel, 'name' : 'channelname'}, {'channel_id' : channel2, 'name' : 'channel2'}]}

# # Test to see if channel_list_all raises an error for invalid token [x]
# def test_raise_access_error_channels_listall():
#     clear_v1()
#     auth_register_v1('email@gmail.com', 'password', 'firstname', 'surname')
#     login = auth_login_v1('email@gmail.com', 'password')
#     valid_token = login['token']
#     channels_create_v1(valid_token, "channel", True)
#     invalid_token = valid_token + "666"
#     with pytest.raises(AccessError):
#         channels_listall_v1(invalid_token)

# # Test to see if channel_listall_v1 works for multiple people [x]
# def test_multiple_users_channels_listall_v1():
#     clear_v1()
#     # Login users
#     auth_register_v1('tae@gmail.com', 'password', 'kim', 'taeyeon')
#     auth_register_v1('mf@gmail.com', 'password', 'sarah', 'misfortune')
#     login_tae = auth_login_v1('tae@gmail.com', 'password')
#     login_mf = auth_login_v1('mf@gmail.com', 'password')
#     token_tae = login_tae['token']
#     token_mf = login_mf['token']

#     # Create channels
#     channel1 = channels_create_v1(token_tae, 'fine', True)
#     channelid1 = channel1['channel_id']
#     channel2 = channels_create_v1(token_mf, 'my_parents_are_dead', False)
#     channelid2 = channel2['channel_id']

#     # asserts
#     assert channels_listall_v1(token_tae)['channels'] == [{'channel_id': channelid1, 'name': 'fine'}, {'channel_id': channelid2, 'name': 'my_parents_are_dead'}]
#     assert channels_listall_v1(token_mf)['channels'] == [{'channel_id': channelid1, 'name': 'fine'}, {'channel_id': channelid2, 'name': 'my_parents_are_dead'}]
