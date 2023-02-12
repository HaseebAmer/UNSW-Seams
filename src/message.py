from src.data_store import data_store
from src.error import InputError, AccessError
from src.channels import token_to_id
from src.channel import check_channel_and_auth_user
from src.helpers import check_token_valid, decode_token, update_user_message_stats
import time

'''
=====================================================================================================================

message_send_v1

Send a message from the authorised user to the channel specified by channel ID.
Each message should have its own unique message ID - non-dependant on similarity or channels.

Arguments:
    token (str)    - Registered user's token string
    channel_id (int)    - ID of  specified channel
    message(str)    - Registered user's message

Exceptions:
    Input Error - occurs when channel_id does not refer to a valid channel
    Input Error - length of message is less than 1 or over 1000 characters

    Access Error - channel_id is valid and the authorised user is not a member of the channel

Return Value:
    Returns message_id of a specific message

=====================================================================================================================
'''


def message_send_v1(token, channel_id, message):
    is_channel_val = False
    message_id = 0
    store = data_store.get()
    if check_token_valid(token) is False:
        raise AccessError(description="Invalid token!")
    auth_user_id = token_to_id(token)
    # raises access error if msg sender isn't in channel + checks chid.
    check_channel_and_auth_user(channel_id, auth_user_id, is_channel_val)
    length = len(message)
    if length < 1 or length > 1000:
        raise InputError(
            description="length of message must be 1-1000 characters")

    for channel in store['channels']:
        message_id += len(channel['messages'])

    message_dict = {
        'message_id': message_id,
        'u_id': auth_user_id,
        'message': message,
        'time_sent': time.time(),
        'reacts': [],
        'is_pinned': False,
    }

    tagged = []
    contains_tag = False
    split = message.split(' ')

    if '@' in message:
        contains_tag = True
        for word in split:
            if word.startswith('@'):
                taggees = word.split('@')
                for taggee in taggees:
                    if taggee not in tagged:
                        tagged.append(taggee)
            elif '@' in word:
                # get rid of substring without taggee.
                word = word.split('@')
                word.pop(0)
                for taggee in word:
                    if taggee not in tagged:
                        tagged.append(taggee)

    for taggee in tagged:
        if taggee == '':
            tagged.remove(taggee)

    tagger_handle = ''
    for channel in store['channels']:
        if channel['channel_id'] == channel_id:
            channel['messages'].insert(0, message_dict)
            if contains_tag:
                for member in channel['members']:
                    if member['u_id'] == auth_user_id:
                        tagger_handle = member['handle_str']
                    if member['handle_str'] in tagged:
                        for user in store['users']:
                            if user['handle'] in tagged and user['handle'] == member['handle_str']:
                                user['notifications'].append({
                                    'channel_id': channel['channel_id'],
                                    'dm_id': -1,
                                    'notification_message': f"{tagger_handle} tagged you in {channel['name']}: {message[:20]}",
                                })
                                update_user_message_stats(user)

    data_store.set(store)
    return {'message_id': message_id}


'''
=====================================================================================================================

message_edit_v1

Given message, update its text with new text. If the new message is an empty string, the message is
then deleted.

Arguments:
    token (str)    - Registered user's token string
    message_id (int)    - Message ID of  specified channel
    message(str)    - Registered user's message

Exceptions:
    Input Error - length of message is over 1000 characters
    Input Error - message_id does not refer to a valid message within a channel/DM that the authorised user has joined
    Access Error - when message_id refers to a valid message in a joined channel/DM
                    and none of the following are true:
                        - the message was sent by the authorised user making this request
                        - the authorised user has owner permissions in the channel/DM


Return Value:
    Returns message_id of a specific message

=====================================================================================================================
'''


def message_edit_v1(token, message_id, message):
    store = data_store.get()
    if check_token_valid(token) is False:
        raise AccessError(description="Invalid token!")

    u_id = token_to_id(token)
    length = len(message)
    is_msg_id_valid = False
    is_owner = False
    is_sender = False
    ch = 0

    for channel in store['channels']:
        for msg in channel['messages']:
            if msg['message_id'] == message_id:
                ch = 1
                is_msg_id_valid = True
                if msg['u_id'] == u_id:
                    is_sender = True
                for owner in channel['owners']:
                    if owner['u_id'] == u_id:
                        is_owner = True
                for gl_owner in channel['owner_perms']:
                    if gl_owner == u_id:
                        is_owner = True

                break
    if ch == 0:
        for dm in store['dms']:
            for msg in dm['messages']:
                if msg['message_id'] == message_id:
                    is_msg_id_valid = True
                    if msg['u_id'] == u_id:
                        is_sender = True
                    for owner in dm['owners']:
                        if owner['u_id'] == u_id:
                            is_owner = True
                    break

    if is_msg_id_valid is False:
        raise InputError(description="invalid message id")

    if not is_owner and not is_sender:
        raise AccessError(
            description="User does not have permissions to edit this msg.")

    if length > 1000:
        raise InputError(description="Max size is 1000 characters.")

    if length == 0:
        message_remove_v1(token, message_id)

    tagged = []
    contains_tag = False
    split = message.split(' ')

    if '@' in message:
        contains_tag = True
        for word in split:
            if word.startswith('@'):
                taggees = word.split('@')
                for taggee in taggees:
                    if taggee not in tagged:
                        tagged.append(taggee)
            elif '@' in word:
                # get rid of substring without taggee.
                word = word.split('@')
                word.pop(0)
                for taggee in word:
                    if taggee not in tagged:
                        tagged.append(taggee)

    for taggee in tagged:
        if taggee == '':
            tagged.remove(taggee)

    if ch == 1:
        for channel in store['channels']:
            for msg in channel['messages']:
                if msg['message_id'] == message_id:
                    msg['message'] = message
                    if contains_tag:
                        for member in channel['members']:
                            if member['u_id'] == u_id:
                                tagger_handle = member['handle_str']
                            if member['handle_str'] in tagged:
                                for user in store['users']:
                                    if user['handle'] in tagged and user['handle'] == member['handle_str']:
                                        user['notifications'].append({
                                            'channel_id': channel['channel_id'],
                                            'dm_id': -1,
                                            'notification_message': f"{tagger_handle} tagged you in {channel['name']}: {message[:20]}",
                                        })
    for dm in store['dms']:
        for msg in dm['messages']:
            if msg['message_id'] == message_id:
                msg['message'] = message
                if contains_tag:
                    for member in dm['members']:
                        if member['u_id'] == u_id:
                            tagger_handle = member['handle_str']
                        if member['handle_str'] in tagged:
                            for user in store['users']:
                                if user['handle'] in tagged and user['handle'] == member['handle_str']:
                                    user['notifications'].append({
                                        'channel_id': -1,
                                        'dm_id': dm['dm_id'],
                                        'notification_message': f"{tagger_handle} tagged you in {dm['name']}: {message[:20]}",
                                    })

    data_store.set(store)
    return {}


'''
=====================================================================================================================

message_remove_v1

Given a message_id for a message, this message is removed from the channel/DM


Arguments:
    token (str)    - Registered user's token string
    message_id(int)    - Registered user's message

Exceptions:
    Input Error - message_id does not refer to a valid message within a
                channel/DM that the authorised user has joined

    Access Error - when message_id refers to a valid message in a joined channel/DM
                    and none of the following are true:
                        - the message was sent by the authorised user making this request
                        - the authorised user has owner permissions in the channel/DM

Return Value:
    Returns empty dictionary.

=====================================================================================================================
'''


def message_remove_v1(token, message_id):
    store = data_store.get()

    if check_token_valid(token) is False:
        raise AccessError(description="Invalid token!")
    u_id = token_to_id(token)
    is_msg_id_valid = False
    is_owner = False
    is_sender = False
    ch = 0

    for channel in store['channels']:
        for message in channel['messages']:
            if message['message_id'] == message_id:
                ch = 1
                is_msg_id_valid = True
                if message['u_id'] == u_id:
                    is_sender = True
                for owner in channel['owners']:
                    if owner['u_id'] == u_id:
                        is_owner = True
                for gl_owner in channel['owner_perms']:
                    if gl_owner == u_id:
                        is_owner = True
                break

    if ch == 0:
        for dm in store['dms']:
            for message in dm['messages']:
                if message['message_id'] == message_id:
                    is_msg_id_valid = True
                    if message['u_id'] == u_id:
                        is_sender = True
                for owner in dm['owners']:
                    if owner['u_id'] == u_id:
                        is_owner = True
                break

    if is_msg_id_valid == False:
        raise InputError(description="invalid message id")

    if is_owner is False and is_sender is False:
        raise AccessError(
            description="user does not have permissions to channel/dm")

    if ch == 1:
        for channel in store['channels']:
            for message in channel['messages']:
                if message['message_id'] == message_id:
                    channel['messages'].remove(message)

    for dm in store['dms']:
        for message in dm['messages']:
            if message['message_id'] == message_id:
                dm['messages'].remove(message)

    data_store.set(store)
    return {}


'''
=====================================================================================================================

message_senddm_v1

Send a message from authorised_user to the DM specified by dm_id.

Arguments:
    token (str)     - Registered user's token string
    dm_id(int)    - ID of a particular DM
    Message(str)    - String of registered user's message.
Exceptions:
    Input Error - dm_id does not refer to a valid DM
    Input Error - length of message is less than 1 or over 1000 characters

    Access Error - dm_id is valid and the authorised user is not a member of the DM

Return Value:
    Returns message_id of a specific message

=====================================================================================================================
'''


def message_senddm_v1(token, dm_id, message):
    store = data_store.get()

    if check_token_valid(token) is False:
        raise AccessError(description="Invalid token!")
    u_id = token_to_id(token)

    is_dm_id_valid = False
    is_auth = False
    message_id = 1

    for dm in store['dms']:
        if dm['dm_id'] == dm_id:
            is_dm_id_valid = True
            for member in dm['members']:
                if member['u_id'] == u_id:
                    is_auth = True
                    break

    if is_dm_id_valid is False:
        raise InputError(description="dm_id does not refer to a valid DM")

    if is_auth is False:
        raise AccessError("user is not a member of the DM")
    length = len(message)
    if length < 1 or length > 1000:
        raise InputError(description="message must be 1-1000 characters long")

    for dm in store['dms']:
        message_id += len(dm['messages'])
    message_dict = {
        'message_id': message_id,
        'u_id': u_id,
        'message': message,
        'time_sent': time.time(),
        'reacts': [],
        'is_pinned': False,
    }

    tagged = []
    contains_tag = False
    split = message.split(' ')

    if '@' in message:
        contains_tag = True
        for word in split:
            if word.startswith('@'):
                taggees = word.split('@')
                for taggee in taggees:
                    if taggee not in tagged:
                        tagged.append(taggee)
            elif '@' in word:
                # get rid of substring without taggee.
                word = word.split('@')
                word.pop(0)
                for taggee in word:
                    if taggee not in tagged:
                        tagged.append(taggee)

    for taggee in tagged:
        if taggee == '':
            tagged.remove(taggee)

    for dm in store['dms']:
        if dm['dm_id'] == dm_id:
            dm['messages'].insert(0, message_dict)
            if contains_tag:
                for member in dm['members']:
                    if member['u_id'] == u_id:
                        tagger_handle = member['handle_str']
                    if member['handle_str'] in tagged:
                        for user in store['users']:
                            if user['handle'] in tagged and user['handle'] == member['handle_str']:
                                user['notifications'].append({
                                    'channel_id': -1,
                                    'dm_id': dm['dm_id'],
                                    'notification_message': f"{tagger_handle} tagged you in {dm['name']}: {message[:20]}",
                                })
                                update_user_message_stats
    data_store.set(store)
    return {
        'message_id': message_id,
    }


def message_share_v1(token, og_message_id, message, channel_id, dm_id):
    '''=====================================================================================================================

    message/share/v1

    og_message_id of the ID of an original message. channel_id is the channel that the message is being shared to, and is -1 
    being sent to a DM. dm_id is the DM that a message is being shared to, and is -1 if its being sent to a channel. message
    is the optional message in addition to a shared message, it returns an empty string '' if no message is given.


    Arguments:
        token (str)    - Registered user's token string
        og_message_id(int) - Original message id integer

    Exceptions:
        InputError - both channel_id and dm_id are invalid
        InputError - neither channel_id nor dm_id are -1
        InputError - invalid token
        InputErrror - og_message_id does not refer to a valid message within a channel/DM that the authorised user has joined
        InputError - length of message is more than 1000 characters
        AccessError - the pair of channel_id and dm_id are valid (i.e. one is -1, the other is valid) and the authorised user has not joined the channel or DM they are trying to share the message to


    Return Value:
        An integer representing a shared message

    =====================================================================================================================
    '''
    store = data_store.get()
    if check_token_valid(token) is False:
        raise AccessError(description="Invalid token!")
    u_id = token_to_id(token)
    is_msg_id_valid = False
    is_channel_val = False
    is_user_in_new_ch_dm = False
    is_dm_val = False
    og_message = ''
    shared_message_id = 2
    repeat_check = False

    for channel in store['channels']:
        if channel['channel_id'] == channel_id:
            is_channel_val = True
            for user in channel['members']:
                if user['u_id'] == u_id:
                    is_user_in_new_ch_dm = True
        for member in channel['members']:
            # check if user is in og channel
            if member['u_id'] == u_id:
                for msg in channel['messages']:
                    if msg['message_id'] == og_message_id:
                        is_msg_id_valid = True
                        og_message = msg['message']
                        repeat_check = True

    for dm in store['dms']:
        if dm['dm_id'] == dm_id:
            is_dm_val = True
            for member in dm['members']:
                if member['u_id'] == u_id:
                    is_user_in_new_ch_dm = True
        for member in dm['members']:
            if member['u_id'] == u_id:
                for msg in dm['messages']:
                    if msg['message_id'] == og_message_id:
                        if repeat_check == False:
                            is_msg_id_valid = True
                            og_message = msg['message']

    if not is_channel_val and not is_dm_val:
        raise InputError(description="both channel id and dm id are invalid")

    if channel_id != -1 and dm_id != -1:
        raise InputError(description="cannot share with current channel/dm_id")

    if not is_user_in_new_ch_dm:
        raise AccessError(
            description="the authorised user is not in the channel/dm they want to share with.")

    if is_msg_id_valid is False:
        raise InputError(
            description="the og message id doesn't refer to any valid message")
    if len(message) > 1000:
        raise InputError(description="message too long")
    new_message = og_message + ' ' + message

    if dm_id == -1:
        shared_message_id = message_send_v1(
            token, channel_id, new_message)['message_id']
    elif channel_id == -1:
        shared_message_id = message_senddm_v1(
            token, dm_id, new_message)['message_id']

    data_store.set(store)
    return {
        'shared_message_id': shared_message_id,
    }


def message_react_v1(token, message_id, react_id):
    '''=====================================================================================================================

    message/react/v1

    Given message within Channel/DM, react to that particular message


    Arguments:
        token (str)    - Registered user's token string
        message_id(int) - Message ID integer
        react_id(int) - Integer of React ID

    Exceptions:
        InputError - message_id is not a valid message within a channel or DM that the authorised user has joined
        InputError - react_id is not a valid react ID - currently, the only valid react ID the frontend has is 1
        InputError - invalid token
        InputError - the message already contains a react with ID react_id from the authorised user

    Return Value:
        Returns empty dictionary

    =====================================================================================================================
    '''
    store = data_store.get()
    if check_token_valid(token) is False:
        raise AccessError(description="Invalid token!")
    u_id = token_to_id(token)

    is_msg_id_valid = False
    is_repeat = False
    is_user_in = False
    specific_member = 0
    ch = 0
    user_handle = ''

    for channel in store['channels']:
        for member in channel['members']:
            if member['u_id'] == u_id:
                specific_member = member

    for channel in store['channels']:
        for msg in channel['messages']:
            if msg['message_id'] == message_id:
                is_msg_id_valid = True
                if specific_member in channel['members']:
                    is_user_in = True
            for react in msg['reacts']:
                if react['react_id'] == react_id:
                    if u_id in react['u_ids']:
                        is_repeat = True

    for dm in store['dms']:
        for member in dm['members']:
            if member['u_id'] == u_id:
                specific_member = member

    for dm in store['dms']:
        for msg in dm['messages']:
            if msg['message_id'] == message_id:
                is_msg_id_valid = True
                if specific_member in dm['members']:
                    is_user_in = True
            for react in msg['reacts']:
                if react['react_id'] == react_id:
                    if u_id in react['u_ids']:
                        is_repeat = True

    if not is_user_in:
        raise InputError(
            description="message id is invalid in your channel/dm")

    if not is_msg_id_valid:
        raise InputError(
            description="message id is invalid in your channel/dm")

    if react_id != 1:
        raise InputError(description="react id is invalid")

    if is_repeat:
        raise InputError(
            description="user has already reacted to this message")

    for channel in store['channels']:
        for msg in channel['messages']:
            if msg['message_id'] == message_id:
                ch = 1
                if msg['reacts'] == []:
                    msg['reacts'].append({
                        'react_id': react_id,
                        'u_ids': [u_id],
                        'is_this_user_reacted': False,
                    })
                else:
                    for react in msg['reacts']:
                        if react['react_id'] == react_id:
                            if u_id not in react['u_ids']:
                                react['u_ids'].append(u_id)

    if ch == 0:
        for dm in store['dms']:
            for msg in dm['messages']:
                if msg['message_id'] == message_id:
                    if msg['reacts'] == []:
                        msg['reacts'].append({
                            'react_id': react_id,
                            'u_ids': [u_id],
                            'is_this_user_reacted': False,
                        })
                    else:
                        for react in msg['reacts']:
                            if react['react_id'] == react_id:
                                if u_id not in react['u_ids']:
                                    react['u_ids'].append(u_id)
    reactee_id = 0
    channel_id = -1
    dm_id = -1
    channel_name = ''

    if ch == 0:
        for dm in store['dms']:
            for msg in dm['messages']:
                if msg['message_id'] == message_id:
                    reactee_id = msg['u_id']
                    dm_id = dm['dm_id']

    else:
        for channel in store['channels']:
            for msg in channel['messages']:
                if msg['message_id'] == message_id:
                    reactee_id = msg['u_id']
                    channel_id = channel['channel_id']
                    channel_name = channel['name']

    for user in store['users']:
        if user['auth_user_id'] == u_id:
            user_handle = user['handle']
        if user['userdata']['u_id'] == reactee_id:
            user['notifications'].append({
                'channel_id': channel_id,
                'dm_id': dm_id,
                'notification_message': f"{user_handle} reacted to your message in {channel_name}"
            })

    data_store.set(store)
    return {}


def message_unreact_v1(token, message_id, react_id):
    '''=====================================================================================================================

    message/unreact/v1

    Given message within Channel/DM, unreact to that particular message

    Arguments:
        token (str)    - Registered user's token string
        message_id(int) - Message ID integer
        react_id(int) - Integer of React ID

    Exceptions:
        InputError - message_id is not a valid message within a channel or DM that the authorised user has joined
        InputError - react_id is not a valid react ID
        InputError - invalid token
        InputError - the message does not contain a react with ID react_id from the authorised user

    Return Value:
        Returns empty dictionary

    =====================================================================================================================
    '''
    store = data_store.get()
    if check_token_valid(token) is False:
        raise AccessError(description="Invalid token!")
    u_id = token_to_id(token)

    is_msg_id_valid = False
    is_user_in = False
    is_user_reacted = False
    specific_member = 0
    ch = 0

    for channel in store['channels']:
        for member in channel['members']:
            if member['u_id'] == u_id:
                specific_member = member

    for channel in store['channels']:
        for msg in channel['messages']:
            if msg['message_id'] == message_id:
                is_msg_id_valid = True
                if specific_member in channel['members']:
                    is_user_in = True
            for react in msg['reacts']:
                if react['react_id'] == react_id:
                    if u_id in react['u_ids']:
                        is_user_reacted = True

    for dm in store['dms']:
        for member in dm['members']:
            if member['u_id'] == u_id:
                specific_member = member

    for dm in store['dms']:
        for msg in dm['messages']:
            if msg['message_id'] == message_id:
                is_msg_id_valid = True
                if specific_member in dm['members']:
                    is_user_in = True
            for react in msg['reacts']:
                if react['react_id'] == react_id:
                    if u_id in react['u_ids']:
                        is_user_reacted = True

    if not is_user_in:
        raise InputError(
            description="message id is invalid in your channel/dm")

    if not is_msg_id_valid:
        raise InputError(
            description="message id is invalid in your channel/dm")

    if react_id != 1:
        raise InputError(description="react id is invalid")

    if not is_user_reacted:
        raise InputError(
            description="the user has not reacted to this message")

    for channel in store['channels']:
        for msg in channel['messages']:
            if msg['message_id'] == message_id:
                ch = 1
                for react in msg['reacts']:
                    if react['react_id'] == react_id:
                        if u_id in react['u_ids']:
                            react['u_ids'].remove(u_id)
                        if len(react['u_ids']) == 0:
                            msg['reacts'].remove(react)

    if ch == 0:
        for dm in store['dms']:
            for msg in dm['messages']:
                if msg['message_id'] == message_id:
                    for react in msg['reacts']:
                        if react['react_id'] == react_id:
                            if u_id in react['u_ids']:
                                react['u_ids'].remove(u_id)
                            if len(react['u_ids']) == 0:
                                msg['reacts'].remove(react)

    data_store.set(store)
    return {}


def message_pin_v1(token, message_id):
    '''=====================================================================================================================

    message/pin/v1

    Given a message within a channel or DM, mark it as "pinned".

    Arguments:
        token (str)    - Registered user's token string
        message_id(int) - Message ID integer
        react_id(int) - Integer of React ID

    Exceptions:
        InputError - message_id is not a valid message within a channel or DM that the authorised user has joined
        InputError - the message is already pinned
        InputError - invalid token
        AccessError - message_id refers to a valid message in a joined channel/DM and the authorised user does not have owner permissions in the channel/DM

    Return Value:
        Returns empty dictionary

    =====================================================================================================================
    '''
    store = data_store.get()
    if check_token_valid(token) is False:
        raise AccessError(description="Invalid token!")
    u_id = token_to_id(token)

    is_msg_id_valid = False
    is_user_in = False
    is_pinned = False
    is_owner = False
    specific_member = 0
    ch = 0

    for channel in store['channels']:
        for member in channel['members']:
            if member['u_id'] == u_id:
                specific_member = member

    for channel in store['channels']:
        for msg in channel['messages']:
            if msg['message_id'] == message_id:
                is_msg_id_valid = True
                if specific_member in channel['members']:
                    is_user_in = True
                if msg['is_pinned'] == True:
                    is_pinned = True
                for owner in channel['owners']:
                    if owner['u_id'] == u_id:
                        is_owner = True
                for gl_owner in channel['owner_perms']:
                    if gl_owner == u_id:
                        is_owner = True

    for dm in store['dms']:
        for member in dm['members']:
            if member['u_id'] == u_id:
                specific_member = member

    for dm in store['dms']:
        for msg in dm['messages']:
            if msg['message_id'] == message_id:
                is_msg_id_valid = True
                if specific_member in dm['members']:
                    is_user_in = True
                if msg['is_pinned'] == True:
                    is_pinned = True
                for owner in dm['owners']:
                    if owner['u_id'] == u_id:
                        is_owner = True

    if not is_user_in:
        raise InputError(
            description="message id is invalid in your channel/dm")

    if not is_msg_id_valid:
        raise InputError(
            description="message id is invalid in your channel/dm")

    if not is_owner:
        raise AccessError(description="user doesn't have owner permissions")

    if is_pinned:
        raise InputError(description="message is already pinned")

    for channel in store['channels']:
        for msg in channel['messages']:
            if msg['message_id'] == message_id:
                ch = 1
                msg['is_pinned'] = True

    if ch == 0:
        for dm in store['dms']:
            for msg in dm['messages']:
                if msg['message_id'] == message_id:
                    msg['is_pinned'] = True

    data_store.set(store)
    return {}


def message_unpin_v1(token, message_id):
    '''=====================================================================================================================

    message/unpin/v1

    Given a message within a channel or DM, remove its pinned mark.

    Arguments:
        token (str)    - Registered user's token string
        message_id(int) - Message ID integer


    Exceptions:
        InputError - message_id is not a valid message within a channel or DM that the authorised user has joined
        InputError - the message is already pinned
        InputError - invalid token
        AccessError - message_id refers to a valid message in a joined channel/DM and the authorised user does not have owner permissions in the channel/DM

    Return Value:
        Returns empty dictionary

    =====================================================================================================================
'''
    store = data_store.get()
    if check_token_valid(token) is False:
        raise AccessError(description="Invalid token!")
    u_id = token_to_id(token)

    is_msg_id_valid = False
    is_user_in = False
    is_pinned = False
    is_owner = False
    specific_member = 0
    ch = 0

    for channel in store['channels']:
        for member in channel['members']:
            if member['u_id'] == u_id:
                specific_member = member

    for channel in store['channels']:
        for msg in channel['messages']:
            if msg['message_id'] == message_id:
                is_msg_id_valid = True
                if specific_member in channel['members']:
                    is_user_in = True
                if msg['is_pinned'] == True:
                    is_pinned = True
                for owner in channel['owners']:
                    if owner['u_id'] == u_id:
                        is_owner = True
                for gl_owner in channel['owner_perms']:
                    if gl_owner == u_id:
                        is_owner = True

    for dm in store['dms']:
        for member in dm['members']:
            if member['u_id'] == u_id:
                specific_member = member

    for dm in store['dms']:
        for msg in dm['messages']:
            if msg['message_id'] == message_id:
                is_msg_id_valid = True
                if specific_member in dm['members']:
                    is_user_in = True
                if msg['is_pinned'] == True:
                    is_pinned = True
                for owner in dm['owners']:
                    if owner['u_id'] == u_id:
                        is_owner = True

    if not is_user_in:
        raise InputError(
            description="message id is invalid in your channel/dm")

    if not is_msg_id_valid:
        raise InputError(
            description="message id is invalid in your channel/dm")

    if not is_owner:
        raise AccessError(description="user doesn't have owner permissions")

    if not is_pinned:
        raise InputError(description="the message is not already pinned")

    for channel in store['channels']:
        for msg in channel['messages']:
            if msg['message_id'] == message_id:
                ch = 1
                msg['is_pinned'] = False

    if ch == 0:
        for dm in store['dms']:
            for msg in dm['messages']:
                if msg['message_id'] == message_id:
                    msg['is_pinned'] = False

    data_store.set(store)
    return {}
