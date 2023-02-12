from src.data_store import data_store
from src.error import InputError, AccessError
from src.helpers import check_token_valid, decode_token
from src.channel import channel_by_channel_id
import time
from src.message import message_send_v1
from threading import Timer


def standup_start_v1(token, channel_id, length):
    '''=====================================================================================================================

    standup/start/v1

    For a given channel, start the standup period whereby for the next "length" seconds if someone calls "standup/send" 
    with a message, it is buffered during the X second window then at the end of the X second window a message will be 
    added to the message queue in the channel from the user who started the standup. "length" is an integer that denotes 
    the number of seconds that the standup occurs for. If no standup messages were sent during the duration of the 
    standup, no message should be sent at the end.

    Arguments:
        token (str)    - Registered user's token string
        channel_id(int) - Message ID integer
        length(int) - Integer representing standup length


    Exceptions:
        InputError - channel_id does not refer to a valid channel
        InputError -    length is a negative integer
        InputError - invalid token
        AccessError - an active standup is currently running in the channel

    Return Value:
        Returns time the standup finishes

    =====================================================================================================================
    '''
    store = data_store.get()
    token = str(token)
    channel_id = int(channel_id)
    length = int(length)

    auth_id_check = False

    if check_token_valid(token) is False:
        raise AccessError(description="token is invalid!")

    if not channel_by_channel_id(channel_id):
        raise InputError(description="Invalid Channel")

    if length < 0:
        raise InputError(description="Invalid length")

    token_payload = decode_token(token)
    auth_user_id = token_payload['u_id']
    curr_channel = channel_by_channel_id(channel_id)

    for member in curr_channel['members']:
        if member['u_id'] == auth_user_id:
            auth_id_check = True

    if not auth_id_check:
        raise AccessError(description="User is not a member of this channel")

    if curr_channel['standup']['is_active'] == True:
        raise InputError("Already a standup running in this channel")

    start_time = int(time.time())
    finish_time = start_time + length

    return_value = standup_active_v1(token, channel_id)
    if return_value["is_active"]:
        raise InputError(
            "An active standup is currently running in this channel")

    curr_channel['standup']['time_start'] = start_time
    curr_channel['standup']['time_finish'] = finish_time
    curr_channel['standup']['creator_id'].append(auth_user_id)

    timer = Timer(int(length), standup_send_package, [token, channel_id])
    timer.start()

    data_store.set(store)

    return {'time_finish': finish_time}


def standup_active_v1(token, channel_id):
    '''=====================================================================================================================

    standup/active/v1

    For a given channel, return whether a standup is active in it, and what time the standup finishes.
    If no standup is active, then time_finish returns None.


    Arguments:
        token (str)    - Registered user's token string
        channel_id(int) - Message ID integer


    Exceptions:
        InputError - channel_id does not refer to a valid channel
        AccessError - channel_id is valid and the authorised user is not a member of the channel
        InputError - invalid token


    Return Value:
        Returns dict containing whether standup is active and time the standup will finish.

    =====================================================================================================================
    '''
    data_store.get()
    token = str(token)
    channel_id = int(channel_id)
    auth_id_check = False

    if check_token_valid(token) is False:
        raise AccessError(description="token is invalid!")

    if not channel_by_channel_id(channel_id):
        raise InputError(description="Invalid Channel")

    token_payload = decode_token(token)
    auth_user_id = token_payload['u_id']
    specific_channel = channel_by_channel_id(channel_id)

    for member in specific_channel['members']:
        if member['u_id'] == auth_user_id:
            auth_id_check = True

    if not auth_id_check:
        raise AccessError(description="User is not a member of this channel")

    return_dict = {}
    is_active = False

    if specific_channel['standup']['time_finish'] != None:
        if int(time.time()) < specific_channel['standup']['time_finish']:
            is_active = True
            finish_time = specific_channel['standup']['time_finish']

    return_dict['is_active'] = is_active
    if return_dict['is_active']:
        return_dict['time_finish'] = finish_time
    else:
        return_dict['time_finish'] = None

    return return_dict


def standup_send_v1(token, channel_id, message):
    '''=====================================================================================================================

    standup/send/v1

    Sending a message to get buffered in the standup queue, assuming a standup is currently active.
    Note: @ tags should not be parsed as proper tags when sending to standup/send


    Arguments:
        token (str)    - Registered user's token string
        channel_id(int) - Message ID integer
        message(str)    - 

    Exceptions:
        InputError - channel_id does not refer to a valid channel
        InputError - length of message is over 1000 characters
        AccessError  - channel_id is valid and the authorised user is not a member of the channel
        InputError - invalid token


    Return Value:
        Returns empty dictionary
    =====================================================================================================================
    '''
    store = data_store.get()
    token = str(token)
    channel_id = int(channel_id)
    message = str(message)
    auth_id_check = False

    if check_token_valid(token) is False:
        raise AccessError(description="token is invalid!")

    if not channel_by_channel_id(channel_id):
        raise InputError(description="Invalid Channel")

    if len(message) > 1000:
        raise InputError(description="Message is over 1000 characters")

    token_payload = decode_token(token)
    auth_user_id = token_payload['u_id']

    specific_channel = channel_by_channel_id(channel_id)

    for member in specific_channel['members']:
        if member['u_id'] == auth_user_id:
            auth_id_check = True
            handle_str = member['handle_str']

    if not auth_id_check:
        raise AccessError(description="User is not a member of this channel")

    return_value = standup_active_v1(token, channel_id)
    if return_value["is_active"] == False:
        raise InputError(
            "An active standup is not currently running in this channel")

    standup_msg = f"{handle_str}: {message}"
    specific_channel['standup_package'].append(standup_msg)

    data_store.set(store)
    return {}


def standup_send_package(token, channel_id):

    specific_channel = channel_by_channel_id(channel_id)

    if len(specific_channel['standup_package']) > 0:
        packaged_msg = "\n".join(specific_channel['standup_package'])
        message_send_v1(token, channel_id, packaged_msg)

    specific_channel['standup']['is_active'] = False
    specific_channel['standup_package'] = []
    specific_channel['standup']['time_finish'] = None
    specific_channel['standup']['creator_id'] = []
