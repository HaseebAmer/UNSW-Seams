from src.data_store import data_store
from src.error import InputError, AccessError
from src.channels import token_to_id
from src.helpers import check_token_valid, decode_token, update_user_channel_stats



def check_channel_and_auth_user(channel_id, auth_user_id, is_ch_valid):
    store = data_store.get()
    is_user_auth = False
    for channel in store['channels']:
        if channel['channel_id'] == channel_id:
            is_ch_valid = True
            for member in channel['members']:
                if member['u_id'] == auth_user_id:
                    is_user_auth = True
    if is_ch_valid is False: 
        raise InputError("invalid channel id")
    elif is_user_auth is False:
        raise AccessError(description="user does not have permissions to this channel")
    return 

def channel_by_channel_id(channel_id: int):
    store = data_store.get()
    for channel in store['channels']:
        if channel['channel_id'] == channel_id:
            return channel
    return None


'''
=====================================================================================================================

channel_invite_v1

Invites a user with ID u_id to join a channel with ID channel_id. Once
invited, user is immediately added. All members are able to invite user
in both private and public channels.

Arguments:
    auth_user_id (str)    - Registered user's email string
    channel_id (int)    - ID of  specified channel
    u_id (int)    - ID of authorised user

Exceptions:
    Input Error - occurs when channel_id does not refer to a valid channel
    Input Error - occurs when u_id does not refer to a valid user
    Input Error - ocurs when u_id refers to a user who is already a member of the channel
    Access Error - occurs when channel_id is valid and authorised user is not a member of the channel
    Access Error - occurs when auth_user_id is invalid

Return Value:
    Returns empty dictionary

=====================================================================================================================
'''

def channel_invite_v1(token, channel_id, u_id):
    store = data_store.get()
    is_u_id_valid = False
    is_ch_id_valid = False

    if check_token_valid(token) is False:
        raise AccessError(description="token is invalid!")

    auth_user_id = token_to_id(token)

    for user in store['users']:
        if user['auth_user_id'] == u_id:
            is_u_id_valid = True

    check_channel_and_auth_user(channel_id, auth_user_id, is_ch_id_valid)

    for channel in store['channels']:
        if channel['channel_id'] == channel_id:
            for user_in_channel in channel['members']:
                if user_in_channel['u_id'] == u_id:
                    raise InputError(description="user is already in channel")

    if not is_u_id_valid:
        raise InputError("user invalid")

    channel_name = ''
    for user in store['users']:
        if user['auth_user_id'] == u_id:
            for channel in store['channels']:
                if channel['channel_id'] == channel_id:
                    channel_name = channel['name']
                    channel['members'].append(user['userdata'])
                    if user['global_perms'] == 1:
                        channel['owner_perms'].append(user['auth_user_id'])

    inviter_handle = ''
    for user in store['users']:
        if user['auth_user_id'] == auth_user_id:
            update_user_channel_stats(user, False)
            inviter_handle = user['handle']
        if user['auth_user_id'] == u_id:
            user['in_channels'].append(channel_id)
            user['notifications'].append({
                'channel_id': channel_id,
                'dm_id': -1,
                'notification_message': f"{inviter_handle} added you to {channel_name}",
            })

    data_store.set(store)
    return {
    }
'''
=====================================================================================================================

channel_details_v1

Given a channel with specific channel_id and the token of a user in that channel,
provide basic details about that channel

Arguments:
    token (str)    - Registered user's token string
    channel_id (int)    - ID of  specified channel

Exceptions:
    Input Error - occurs when channel_id does not refer to a valid channel
    Access Error - occurs when channel_id is valid and authorised user is not a member of channel
    Access Error - occurs when user has invalid token_id

Return Value:
Returns list containing dictionaries, with name, is_public,
owner_members and all_members

=====================================================================================================================
'''

def channel_details_v1(token, channel_id):

    store = data_store.get()
    channel_id = int(channel_id)
    token = str(token)
    if not check_token_valid(token):
        raise AccessError(description="Token invalid")

    auth_id_check = False

    specific_channel = {}

    if not channel_by_channel_id(channel_id):
        raise InputError(description="Invalid Channel")

    for channel in store['channels']:
        if channel['channel_id'] == channel_id:
            specific_channel = channel

    token_payload = decode_token(token)
    auth_user_id = token_payload['u_id']

    for channel in store['channels']:
        if channel['channel_id'] == channel_id:
            for member in channel['members']:
                if member['u_id'] == auth_user_id:
                    auth_id_check = True


    if not auth_id_check:
        raise AccessError(description="User is not a member of this channel")

    all_members = []

    for member in specific_channel['members']:
        all_members.append(member)

    owner_members = []

    for owner in specific_channel['owners']:
        owner_members.append(owner)

    return {
        'name': specific_channel['name'],
        'is_public': specific_channel['is_public'],
        'owner_members': owner_members,
        'all_members': all_members
    }

'''
=====================================================================================================================

channel_messages_v1

Given a channel with ID channel_id that the authorised user is a member of, return up to 50 messages between index "start" and "start + 50".
Index 0 refers to the most recent message in the channel. Function returns a new index "end", referring to index "start + 50", or if this
function has returned the least recent messages in the channel, returns
-1 in "end" to indicate there are no more messages to load.

Arguments:
    token (str)    - Registered user's token string
    channel_id (int)    - ID of  specified channel
    start(int)    - index of messages

Exceptions:
    Input Error - occurs when channel_id does not refer to a valid channel
    Input Error - start is greater than total number of messages in channel
    Access Error - occurs when channel_id is valid and authorised user is not a member of the channel
    Access Error - occurs when token is invalid

Return Value:
Returns messages, start and end - all messages in between indexes
"start" and "end"

=====================================================================================================================

'''
def channel_messages_v1(token, channel_id, start):
    start_int = int(start)
    channel_id_int = int(channel_id)
    store = data_store.get()
    is_channel_val = False
    msg_count = 0
    end = start

    if check_token_valid(token) is False:
        raise AccessError(description="token is invalid!")

    auth_user_id = token_to_id(token)

    check_channel_and_auth_user(channel_id_int, auth_user_id, is_channel_val)
    for channel in store['channels']:
        if channel['channel_id'] == channel_id_int:
            msg_count = len(channel['messages'])

    if start_int != 0 and start_int >= msg_count:
        raise InputError("invalid start")

    for channel in store['channels']:
        if channel['channel_id'] == int(channel_id):
            for msg in channel['messages']:
                for react in msg['reacts']:
                    if auth_user_id in react['u_ids']:
                        react['is_this_user_reacted'] = True

    messages = []
    i = 0
    for channel in store['channels']:
        if channel['channel_id'] == channel_id_int:
            for msg in channel['messages']:
                if len(messages) > 50:
                    break
                if (i >= start_int):
                    messages.append(msg)
                i = i + 1

    if start_int + 50 >= msg_count:
        end = -1
    else:
        end = start_int + 50
    data_store.set(store)
    return {
        'messages': messages,
        'start': start_int,
        'end': end,
    }


'''
=====================================================================================================================

channel_join_v1

Given an existing channel_id that the authorised user can join, add them
to that channel

Arguments:
    token (str)    - Registered user's token string
    channel_id (int)    - ID of  specified channel

Exceptions:
    Input Error - occurs when channel_id does not refer to a valid channel
    Input Error - ocurs when authorised user is already a member of the channel
    Access Error - occurs when channel_id refers to private channel authorised user is not a member of  and is not a global owner.
    Access Error - occurs when user has invalid token


Return Value:
    Returns empty dictionary

=====================================================================================================================
'''
def channel_join_v1(token, channel_id):

    store = data_store.get()
    channel_id = int(channel_id)
    token = str(token)
    if not check_token_valid(token):
        raise AccessError(description="Token invalid")


    data = decode_token(token)
    auth_user_id = data['u_id']

    if not channel_by_channel_id(channel_id):
        raise InputError(description="Invalid Channel")

    specific_channel = channel_by_channel_id(channel_id)

    for member in specific_channel['members']:
        if member['u_id'] == auth_user_id:
            raise AccessError(
                description="User is already a member of this channel")

    global_perms = 500
    for user in store['users']:
        if user['auth_user_id'] == auth_user_id:
            global_perms = user['global_perms']


    for user in store['users']:
        if auth_user_id == user['auth_user_id']:
            joiner = user

    for channel in store['channels']:
        if channel['channel_id'] == channel_id:
            
            if global_perms == 1:
                channel['owner_perms'].append(auth_user_id)
                channel['members'].append(joiner['userdata'])
                joiner['in_channels'].append(channel['channel_id'])

            elif global_perms == 2:
                if not channel['is_public']:
                    raise AccessError(description="This is a private channel")
                channel['members'].append(joiner['userdata'])
                joiner['in_channels'].append(channel['channel_id'])


    for user in store['users']:
        if user['auth_user_id'] == auth_user_id:
            update_user_channel_stats(user, False)

    data_store.set(store)

    return {}

'''
=====================================================================================================================

channel_leave_v1

Given an existing channel_id that the authorised user is a member of, remove them as channel member.
Messages should remain in channel and if the channel owner leaves, the channel will remain.

Arguments:
    token (str)    - Registered user's token string
    channel_id (int)    - ID of  specified channel

Exceptions:
    Input Error - occurs when channel_id does not refer to a valid channel
    Input Error - ocurs when authorised user is not a member of the channel
    Access Error - occurs when channel_id refers to private channel authorised user is not a member of  and is not a global owner.
    Access Error - occurs when user has invalid token


Return Value:
    Returns empty dictionary

=====================================================================================================================
'''

# channel/leave/v1
def channel_leave_v1(token, channel_id):
    store = data_store.get()
    # check if token is valid
    if not check_token_valid(token):
        raise AccessError(description='Invalid Token')

    user_id = token_to_id(token)
   
    # check if channel_id exists
    channel_id_exists = False
    for channel in store['channels']:
        if channel_id == channel['channel_id']:
            channel_id_exists = True
    
    if not channel_id_exists:
        raise InputError(description="Channel ID does not exist")

    # check if user is part of channel
    user_is_in_channel = False
    for channel in store['channels']:
        if channel_id == channel['channel_id']:
            for member in channel['members']:
                if user_id == member['u_id']:
                    user_is_in_channel = True

    if not user_is_in_channel:
        raise AccessError(description="User is not part of this channel")          

    # update user stats for user leaving channel
    for user in store['users']:
        if user['auth_user_id'] == user_id:
            update_user_channel_stats(user, True)


    # Implement function: remove user from members; # if user is also owner, remove them from owner 
    channel_index = 0
    member_index = 0
    owner_index = 0
    index_owner = -5
    for channel in store['channels']:
        if channel['channel_id'] == channel_id:
            index_channel = channel_index
            for member in channel['members']:
                if user_id == member['u_id']:
                    index_member = member_index
                    break
                member_index += 1
            for owner in channel['owners']:
                if user_id == owner['u_id']:
                    index_owner = owner_index
                    break
                owner_index += 1
        channel_index += 1

    store['channels'][index_channel]['members'].pop(index_member)
    if index_owner == owner_index:
        store['channels'][index_channel]['owners'].pop(index_owner)
    
    # if a global owner leaves, remove them from owner_perms
    for user in store['users']:
        if user_id == user['auth_user_id']:
            if user['global_perms'] == 1:
                store['channels'][index_channel]['owner_perms'].remove(user_id)

    data_store.set(store)
    
    return {}


'''
=====================================================================================================================

channel_addowner_v1

Given an existing channel_id that the authorised user is a member of, remove them as channel member.
Messages should remain in channel and if the channel owner leaves, the channel will remain.

Arguments:
    token (str)    - Registered user's token string
    channel_id (int)    - ID of  specified channel

Exceptions:
    Input Error - occurs when channel_id does not refer to a valid channel
    Input Error - ocurs when authorised user is not a member of the channel
    Access Error - occurs when channel_id refers to private channel authorised user is not a member of  and is not a global owner.
    Access Error - occurs when user has invalid token


Return Value:
    Returns empty dictionary

=====================================================================================================================
'''

# Channel/Addowner/v1
def channel_addowner_v1(token, channel_id, u_id):
    store = data_store.get()
    # AccessError if token is not valid
    if not check_token_valid(token):
        raise AccessError(description="Invalid Token")

    # Input error if channel_id is invalid
    valid_channel_id = False
    for channel in store['channels']:
        if channel_id == channel['channel_id']:
            valid_channel_id = True

    if not valid_channel_id:
        raise InputError(description="Invalid Channel ID")
    
    # Input Error if u_id does not exist
    valid_user = False
    for user in store['users']:
        if user['auth_user_id'] == u_id:
            valid_user = True
    
    if not valid_user:
        raise InputError(description="u_id is invalid")
    
    # Input error if u_id is not member of channel
    u_id_exists_in_channel = False
    for channel in store['channels']:
        if channel['channel_id'] == channel_id:
            for member in channel['members']:
                if member['u_id'] == u_id:
                    u_id_exists_in_channel = True

    if not u_id_exists_in_channel:
        raise InputError(description="User with u_id not member of channel")

    id = token_to_id(token)

    # AccessError if token is not user with owner or does not belong global owner in channel
    token_belongs_to_global_owner_in_channel = False
    for channel in store['channels']:
        if channel_id == channel['channel_id']:
            for perms_id in channel['owner_perms']:
                if perms_id == id:
                    token_belongs_to_global_owner_in_channel = True
    
    token_belongs_to_owner = False

    for channel in store['channels']:
        if channel['channel_id'] == channel_id:
            for owner in channel['owners']:
                if id == owner['u_id']:
                    token_belongs_to_owner = True

    if not token_belongs_to_owner and not token_belongs_to_global_owner_in_channel:
        raise AccessError(description="Token does not belong to an channel owner nor global owner")

    # Input error if u_id is an owner
    for channel in store['channels']:
        if channel['channel_id'] == channel_id:
            for owner in channel['owners']:
                if u_id == owner['u_id']:
                    raise InputError(description="u_id is already an owner")

    # Normal Functionality
    for user in store['users']:
        if u_id == user['auth_user_id']:
            for channel in store['channels']:
                if channel_id == channel['channel_id']:
                    channel['owners'].append(user['userdata'])

    
    data_store.set(store)
    return {}

'''
=====================================================================================================================

channel_removeowner_v1

Remove user with user id u_id as an owner of the channel.

Arguments:
    token (str)    - Registered user's token string
    channel_id (int)    - ID of  specified channel
    u_id(int)    - Registered user's u_id

Exceptions:
    Input Error - occurs when channel_id does not refer to a valid channel
    Input Error - ocurs when authorised user is not a member of the channel
    Input Error - ocurs when u_id does not refer to a valid user.
    Input Error - ocurs when u_id refers to user who is not an owner
    Input Error - ocurs when u_id refers to the only channel owner.
    Access Error - occurs when channel_id refers to private channel authorised user is not a member of  and is not a global owner.
    Access Error - occurs when user has invalid token


Return Value:
    Returns empty dictionary

=====================================================================================================================
'''


def channel_removeowner_v1(token, channel_id, u_id):
    store = data_store.get()
    # AccessError if token is invalid
    if not check_token_valid(token):
        raise AccessError(description="Invalid Token")
    #InputError if channel_id is invalid
    valid_channel_id = False
    for channel in store['channels']:
        if channel_id == channel['channel_id']:
            valid_channel_id = True

    if not valid_channel_id:
        raise InputError(description="Channel ID does not exist")
    #InputError if u_id is invalid
    valid_id = False
    for user in store['users']:
        if u_id == user['auth_user_id']:
            valid_id = True

    if not valid_id:
        raise InputError(description="u_id does not exist")

    id = token_to_id(token)

    #AccessError: Token does not belong to channel owner and does not belong to global owner in channel
    token_belongs_to_global_owner_in_channel = False
    for channel in store['channels']:
        if channel_id == channel['channel_id']:
            for perms_id in channel['owner_perms']:
                if perms_id == id:
                    token_belongs_to_global_owner_in_channel = True
    

    token_belongs_to_owner = False

    for channel in store['channels']:
        if channel['channel_id'] == channel_id:
            for owner in channel['owners']:
                if id == owner['u_id']:
                    token_belongs_to_owner = True

    if not token_belongs_to_owner and not token_belongs_to_global_owner_in_channel:
        raise AccessError(description="Token does not belong to an channel owner nor global owner")
    
    # InputError if u_id is not an owner
    u_id_belongs_to_owner = False
    for channel in store['channels']:
        if channel['channel_id'] == channel_id:
            for owner in channel['owners']:
                if u_id == owner['u_id']:
                    u_id_belongs_to_owner = True
    
    if not u_id_belongs_to_owner:
        raise InputError(description="u_id does not belong to an owner of the channel")
    #InputError u_id is the only owner (Input error if there is only one owner)
    for channel in store['channels']:
        if channel['channel_id'] == channel_id:
            if len(channel['owners']) == 1:
                raise InputError(description="u_id is the only owner of the channel")



    #Normal Functionality: remove user with u_id from channel['owners']
    channel_index = 0
    owner_index = 0
    for channel in store['channels']:
        if channel_id == channel['channel_id']:
            index_channel = channel_index
            for owner in channel['owners']:
                if u_id == owner['u_id']:
                    index_owner = owner_index
                owner_index += 1
        channel_index += 1
    
    store['channels'][index_channel]['owners'].pop(index_owner)

    data_store.set(store)

    return {}

