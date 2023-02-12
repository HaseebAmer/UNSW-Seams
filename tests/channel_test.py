# import pytest
# from src.error import InputError, AccessError
# from src.channel import channel_join_v1, channel_details_v1, channel_messages_v1, channel_invite_v1
# from src.other import clear_v1
# from src.channels import channels_create_v1, channels_list_v1
# from src.auth import auth_register_v1

# @pytest.fixture
# def clear():
#     clear_v1()

# @pytest.fixture
# def u_id_1():
#     u_id_dict = auth_register_v1('bill.nye@gmail.com', 'thescienceguy', 'Bill', 'Nye')
#     return u_id_dict
# @pytest.fixture
# def u_id_2():
#     u_id_dict = auth_register_v1('george.bush@gmail.com', 'carsandbikes', 'George', 'Bush')
#     return u_id_dict

# @pytest.fixture
# def u_id_3():
#     u_id_dict = auth_register_v1('tom.jerry@unsw.edu.au', 'tomlikesjerry', 'Tom', 'Jerry')
#     return u_id_dict

# def test_join_invalid_channel():
#     clear_v1()
#     token_id_1 = auth_register_v1('tom.jerry@unsw.edu.au', 'tomlikesjerry', 'Tom', 'Jerry')["token"]
#     token_id_2 = auth_register_v1('gary.vee@unsw.edu.au', 'GaryVee321', 'Gary', 'Vee')["token"]
#     channel_id = channels_create_v1(token_id_1, "Aus", True)["channel_id"]
#     channel_id_invalid = channel_id + 20
#     with pytest.raises(InputError):
#         channel_join_v1(token_id_2, channel_id_invalid)

# def test_join_authorised_user_repeat_join():
#     clear_v1()
#     token_id_1 = auth_register_v1('tom.jerry@unsw.edu.au', 'tomlikesjerry', 'Tom', 'Jerry')["token"]
#     channel_id = channels_create_v1(token_id_1, "Aus", True)["channel_id"]
#     with pytest.raises(AccessError):
#         channel_join_v1(token_id_1, channel_id)

# def test_join_private_channel_unauthorised_user():
#     clear_v1()
#     token_id_1 = auth_register_v1('tom.jerry@unsw.edu.au', 'tomlikesjerry', 'Tom', 'Jerry')["token"]
#     token_id_2 = auth_register_v1('gary.vee@unsw.edu.au', 'GaryVee321', 'Gary', 'Vee')["token"]
#     channel_id = channels_create_v1(token_id_1, "Aus", False)["channel_id"]
#     with pytest.raises(AccessError):
#         channel_join_v1(token_id_2, channel_id)

# def test_join_private_channel_global_user():
#     clear_v1()
#     au1_id = auth_register_v1('tom.jerry@unsw.edu.au', 'tomlikesjerry', 'Tom', 'Jerry')
#     au2_id = auth_register_v1('gary.vee@unsw.edu.au', 'GaryVee321', 'Gary', 'Vee')
#     auth1_user_id = au1_id["token"]
#     auth2_user_id = au2_id["token"]
#     channel_id = channels_create_v1(auth2_user_id, "Aus", False)["channel_id"]
#     channel_join_v1(auth1_user_id, channel_id)
#     return_value = channel_details_v1(auth1_user_id, channel_id)
#     assert len(return_value['all_members']) == 2
#     assert return_value == {
#             'all_members': [{'email': 'gary.vee@unsw.edu.au',
#                                 'handle_str': 'garyvee',
#                                 'name_first': 'Gary',
#                                 'name_last': 'Vee',
#                                 'u_id': 2},
#                             {'email': 'tom.jerry@unsw.edu.au',
#                                 'handle_str': 'tomjerry',
#                                 'name_first': 'Tom',
#                                 'name_last': 'Jerry',
#                                 'u_id': 1}],
#             'is_public': False,
#             'name': 'Aus',
#             'owner_members': [{'email': 'gary.vee@unsw.edu.au',
#                                 'handle_str': 'garyvee',
#                                 'name_first': 'Gary',
#                                 'name_last': 'Vee',
#                                 'u_id': 2}],
#             }


# def test_join_public_channel_global_user():
#     clear_v1()
#     au1_id = auth_register_v1('tom.jerry@unsw.edu.au', 'tomlikesjerry', 'Tom', 'Jerry')
#     au2_id = auth_register_v1('gary.vee@unsw.edu.au', 'GaryVee321', 'Gary', 'Vee')
#     auth1_user_id = au1_id["token"]
#     auth2_user_id = au2_id["token"]
#     channel_id = channels_create_v1(auth2_user_id, "Aus", True)["channel_id"]
#     channel_join_v1(auth1_user_id, channel_id)
#     return_value = channel_details_v1(auth1_user_id, channel_id)
#     assert len(return_value['all_members']) == 2
#     assert return_value == {
#             'all_members': [{'email': 'gary.vee@unsw.edu.au',
#                                 'handle_str': 'garyvee',
#                                 'name_first': 'Gary',
#                                 'name_last': 'Vee',
#                                 'u_id': 2},
#                             {'email': 'tom.jerry@unsw.edu.au',
#                                 'handle_str': 'tomjerry',
#                                 'name_first': 'Tom',
#                                 'name_last': 'Jerry',
#                                 'u_id': 1}],
#             'is_public': True,
#             'name': 'Aus',
#             'owner_members': [{'email': 'gary.vee@unsw.edu.au',
#                                 'handle_str': 'garyvee',
#                                 'name_first': 'Gary',
#                                 'name_last': 'Vee',
#                                 'u_id': 2}],
#             }


# def test_join_invalid_token_id_1():
#     clear_v1()
#     token_id_1 = auth_register_v1('tom.jerry@unsw.edu.au', 'tomlikesjerry', 'Tom', 'Jerry')["token"]
#     auth1_token_id_invalid = f"{token_id_1}222"
#     channel_id = channels_create_v1(token_id_1,"Aus", True)["channel_id"]
#     with pytest.raises(AccessError):
#         channel_join_v1(auth1_token_id_invalid, channel_id)


# def test_join_invalid_token_id_and_channel_id_1():
#     clear_v1()
#     token_id_1 = auth_register_v1('tom.jerry@unsw.edu.au', 'tomlikesjerry', 'Tom', 'Jerry')["token"]
#     channel_id = channels_create_v1(token_id_1, "Aus", True)["channel_id"]
#     channel_id_invalid = channel_id + 20
#     auth1_token_id_invalid = f"{token_id_1}222"
#     with pytest.raises(AccessError):
#         channel_join_v1(auth1_token_id_invalid, channel_id_invalid)


# #CHANNEL DETAILS TESTS

# def test_details_invalid_channel_2():
#      clear_v1()
#      token_id_1 = auth_register_v1('tom.jerry@unsw.edu.au', 'tomlikesjerry', 'Tom', 'Jerry')["token"]
#      channel_id = channels_create_v1(token_id_1, "Aus", True)["channel_id"]
#      channel_id_invalid = channel_id + 20
#      with pytest.raises(InputError):
#           channel_details_v1(token_id_1, channel_id_invalid)

# def test_details_invalid_token_id_2():
#     clear_v1()
#     token_id_1 = auth_register_v1('tom.jerry@unsw.edu.au', 'tomlikesjerry', 'Tom', 'Jerry')["token"]
#     auth1_token_id_invalid = f"{token_id_1}222"
#     channel_id = channels_create_v1(token_id_1,"Aus", True)["channel_id"]
#     with pytest.raises(AccessError):
#         channel_details_v1(auth1_token_id_invalid, channel_id)

# def test_details_invalid_token_id_and_channel_id():
#     clear_v1()
#     token_id_1 = auth_register_v1('tom.jerry@unsw.edu.au', 'tomlikesjerry', 'Tom', 'Jerry')["token"]
#     channel_id = channels_create_v1(token_id_1, "Aus", True)["channel_id"]
#     channel_id_invalid = channel_id + 20
#     auth1_token_id_invalid = f"{token_id_1}222"
#     with pytest.raises(AccessError):
#         channel_details_v1(auth1_token_id_invalid, channel_id_invalid)

# def test_details_authorised_channel_member():
#     clear_v1()
#     token_id_1 = auth_register_v1('tom.jerry@unsw.edu.au', 'tomlikesjerry', 'Tom', 'Jerry')["token"]
#     token_id_2 = auth_register_v1('gary.vee@unsw.edu.au', 'GaryVee321', 'Gary', 'Vee')["token"]
#     channel_id = channels_create_v1(token_id_1, "Aus", True)["channel_id"]
#     with pytest.raises(AccessError):
#         channel_details_v1(token_id_2, channel_id)

# def test_details_of_owner_working_implementation():
#     clear_v1()
#     token_id_1 = auth_register_v1('tom.jerry@unsw.edu.au', 'tomlikesjerry', 'Tom', 'Jerry')["token"]
#     token_id_2 = auth_register_v1('gary.vee@unsw.edu.au', 'GaryVee321', 'Gary', 'Vee')["token"]
#     channel_id = channels_create_v1(token_id_1, "Aus", True)["channel_id"]
#     channel_join_v1(token_id_2, channel_id)
#     details = channel_details_v1(token_id_2, channel_id)
#     assert details == { 'name': "Aus",
#                         'is_public': True,
#                         'all_members':
#                         [
#                             {'email': 'tom.jerry@unsw.edu.au',
#                             'handle_str': 'tomjerry',
#                             'name_first': 'Tom',
#                             'name_last': 'Jerry',
#                             'u_id': 1},

#                             {'email': 'gary.vee@unsw.edu.au',
#                             'handle_str': 'garyvee',
#                             'name_first': 'Gary',
#                             'name_last': 'Vee',
#                             'u_id': 2}
#                             ],

#                         'owner_members':
#                         [
#                             {'email': 'tom.jerry@unsw.edu.au',
#                             'handle_str': 'tomjerry',
#                             'name_first': 'Tom',
#                             'name_last': 'Jerry',
#                             'u_id': 1}
#                             ],
#                         }

# def test_details_of_joiner_working_implementation():
#     clear_v1()
#     token_id_1 = auth_register_v1('tom.jerry@unsw.edu.au', 'tomlikesjerry', 'Tom', 'Jerry')["token"]
#     token_id_2 = auth_register_v1('gary.vee@unsw.edu.au', 'GaryVee321', 'Gary', 'Vee')["token"]
#     channel_id = channels_create_v1(token_id_1, "Aus", True)["channel_id"]
#     channel_join_v1(token_id_2, channel_id)
#     details = channel_details_v1(token_id_1, channel_id)
#     assert details == { 'name': "Aus",
#                         'is_public': True,
#                         'all_members':
#                         [
#                             {'email': 'tom.jerry@unsw.edu.au',
#                             'handle_str': 'tomjerry',
#                             'name_first': 'Tom',
#                             'name_last': 'Jerry',
#                             'u_id': 1},

#                             {'email': 'gary.vee@unsw.edu.au',
#                             'handle_str': 'garyvee',
#                             'name_first': 'Gary',
#                             'name_last': 'Vee',
#                             'u_id': 2}
#                             ],

#                         'owner_members':
#                         [
#                             {'email': 'tom.jerry@unsw.edu.au',
#                             'handle_str': 'tomjerry',
#                             'name_first': 'Tom',
#                             'name_last': 'Jerry',
#                             'u_id': 1}
#                             ],
#                         }

# # def test_messages_invalid_channel_id_1(clear, u_id_1):
# #     token = u_id_1['token']
# #     channels_create_v1(token, 'australia', True)
# #     with pytest.raises(InputError):
# #         channel_messages_v1(token, 3, 0)

# # def test_messages_unauthorised_user(clear, u_id_1, u_id_2):
# #     channel_dict = channels_create_v1(u_id_1['token'], 'LEANINMYCUP', True)
# #     with pytest.raises(AccessError):
# #         channel_messages_v1(u_id_2['token'], channel_dict['channel_id'], 0)

# # def test_messages_invalid_token(clear, u_id_1):
# #     channel_dict = channels_create_v1(u_id_1['token'], 'LEANINMYCUP', True)
# #     invalid_token = f"{u_id_1['token']}9000"


# # def test_messages_invalid_start_empty(clear, u_id_1):
# #     channel_id_dict = channels_create_v1(u_id_1['token'], 'america', False)
# #     with pytest.raises(InputError):
# #         channel_messages_v1(u_id_1['token'], channel_id_dict['channel_id'], 1)

# # def test_messages_invalid_start_not_empty(clear, u_id_1):
# #     channel_id_dict = channels_create_v1(u_id_1['token'], 'ukraine', True)
# #     for index in range(0, 3):
# #         message_send_v1(u_id_1['token'], channel_id_dict['channel_id'], f"message{index}")
# #     with pytest.raises(InputError):
# #         channel_messages_v1(u_id_1['token'], channel_id_dict['channel_id'], 4)

# # def test_messages_correct_empty(clear, u_id_2):
# #     channel_id_dict = channels_create_v1(u_id_2['token'], 'SIZZZUUURP', True)
# #     assert channel_messages_v1(u_id_2['token'], channel_id_dict['channel_id'], 0) == {'messages': [], 'start': 0, 'end': -1}

# # def test_messages_correct_50_msges(clear, u_id_1):
# #     channel_id_dict = channels_create_v1(u_id_1['token'], 'dudududrankk', True)
# #     for index in range(0, 50):
# #         message_send_v1(u_id_1['token'], channel_id_dict['channel_id'], f"message{index}")
# #         assert channel_messages(u_id_1['token'], channel_id_dict['channel_id'], index)['message'] == f"message{index}"
# #     messages = channel_messages_v1(u_id_1['token'], channel_id_dict['channel_id'], 0)['messages']
# #     assert len(messages) == 50

# # def test_messages_correct_50_msges_non_zero_start(clear, u_id_1):
# #     channel_id_dict = channels_create_v1(u_id_1['token'], 'dudududrankk', True)
# #     for index in range(50):
# #         message_send_v1(u_id_1['token'], channel_id_dict['channel_id'], f"message{index}")
# #         assert channel_messages(u_id_1['token'], channel_id_dict['channel_id'], index)['message'] == f"message{index}"
# #     messages = channel_messages_v1(u_id_1['token'], channel_id_dict['channel_id'], 45)['messages']
# #     assert len(messages) == 5

# def test_invite_channel_id_invalid(clear, u_id_1, u_id_2):
#     channels_create_v1(u_id_1['token'], 'sizzurpNATION', True)
#     with pytest.raises(InputError):
#         channel_invite_v1(u_id_1['token'], -1, u_id_2['auth_user_id'])

# def test_invite_u_id_invalid(clear, u_id_1, u_id_2):
#     channel_id_dict = channels_create_v1(u_id_1['token'], 'teamworktitans', True)
#     with pytest.raises(InputError):
#         channel_invite_v1(u_id_1['token'], channel_id_dict['channel_id'], -1)

# def test_invite_reuse_u_id(clear, u_id_1, u_id_2):
#     channel_id_dict = channels_create_v1(u_id_1['token'], 'turtlessociety', True)
#     channel_invite_v1(u_id_1['token'], channel_id_dict['channel_id'], u_id_2['auth_user_id'])
#     with pytest.raises(InputError):
#         channel_invite_v1(u_id_1['token'], channel_id_dict['channel_id'], u_id_2['auth_user_id'])

# def test_invite_unauthorised_user(clear, u_id_1, u_id_2, u_id_3):
#     channel_id_dict = channels_create_v1(u_id_1['token'], 'grass', True)
#     with pytest.raises(AccessError):
#         channel_invite_v1(u_id_2['token'], channel_id_dict['channel_id'], u_id_3['auth_user_id'])

# def test_invite_invalid_user(clear, u_id_1, u_id_2):
#     channel_id_dict = channels_create_v1(u_id_1['token'], 'mud', True)
#     with pytest.raises(AccessError):
#         channel_invite_v1(f"{u_id_1['token']}123", channel_id_dict['channel_id'], u_id_2['auth_user_id'])

# def test_invite_all_invalid(clear):
#     with pytest.raises(AccessError):
#         channel_invite_v1("123", 1234, 99)

# def test_invite_correct_functioning(clear, u_id_1, u_id_2):
#     channel_id_dict = channels_create_v1(u_id_1['token'], 'identicalish', True)
#     channel_invite_v1(u_id_1['token'], channel_id_dict['channel_id'], u_id_2['auth_user_id'])
#     assert channels_list_v1(u_id_2['token']) == {'channels' : [{'channel_id' : channel_id_dict['channel_id'], 'name' : 'identicalish'}]}

# def test_invite_correct_functioning_more_invites(clear, u_id_1, u_id_2, u_id_3):
#     channel_id_dict = channels_create_v1(u_id_1['token'], 'identicalish', True)
#     channel_invite_v1(u_id_1['token'], channel_id_dict['channel_id'], u_id_2['auth_user_id'])
#     channel_invite_v1(u_id_2['token'], channel_id_dict['channel_id'], u_id_3['auth_user_id'])
#     details = channel_details_v1(u_id_3['token'], channel_id_dict['channel_id'])
#     assert len(details['all_members']) == 3
#     assert details['all_members'][0]['name_first'] == 'Bill'
#     assert details['all_members'][1]['name_first'] == 'George'
#     assert details['all_members'][2]['name_first'] == 'Tom'
#     assert details['name'] == 'identicalish'
