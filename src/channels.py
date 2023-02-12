from src.data_store import data_store
from src.error import AccessError, InputError
from src.helpers import check_token_valid, decode_token, update_user_channel_stats

def token_to_id(token):
    store = data_store.get()
    for user in store['users']:
        for element in user['tokens']:
            if element == token:
                return user['auth_user_id']
'''
=====================================================================================================================

channels_list_v1

Provide a list of all channels that the authorised user is a member of - including their associated details.

Arguments:
    token_id (str)    - Registered user's token string

Exceptions:
    Access Error - occurs when token is invalid and not a member of the channel

Return Value:
    Returns list containing dictionaries, with channel_id and name of specific channel

=====================================================================================================================
'''
def channels_list_v1(token):
    data = data_store.get()
    channels_list = []

    if not check_token_valid(token):
        raise AccessError(description="Invalid Token")
    id = token_to_id(token)

    for channel in data['channels']:
        for member in channel['members']:
            if member['u_id'] == id:
                channels_list.append({'channel_id' : channel['channel_id'], 'name' : channel['name']})

    return {'channels' : channels_list}
    
'''
=====================================================================================================================

channels_listall_v1
Provide a list of all channels (including private channels) and their associated details.

Arguments:
    token (str)    - Registered user's token string

Exceptions:
    Access Error - occurs when token is invalid and not a member of the channel

Return Value:
    Returns list containing dictionaries, with channel_id and name of specific channel

=====================================================================================================================
'''
def channels_listall_v1(token):
    data = data_store.get()
    channels_list = []

    if not check_token_valid(token):
        raise AccessError(description="Token does not belong to any users")
    
    for channel in data['channels']:
        channels_list.append({'channel_id' : channel['channel_id'], 'name' : channel['name']})
    return {'channels' : channels_list}

'''=====================================================================================================================

channels_create_v1

Create a channel - either public or private. The user who created the channel automatically joins said channel.

Arguments:
    token (str)    - Registered user's token string
    name (str)    - name of channel
    is_public (boolean)    - Identifies private/public channel (assumed public)

Exceptions:
    InputError  - Occurs when length of name is less than 1 or more than 20 characters
    InputError - Occurs when token does not refer to a valid user
    AccessError - Occurs when an invalid token_id is passed into the function


Return Value:
    Returns channel_id of newly created channel

=====================================================================================================================
'''
def channels_create_v1(token, name, is_public):
    store = data_store.get()

    if len(name) < 1 or len(name) > 20:
        raise InputError(description="channel name entered should be between one and twenty characters")
    
    channel_id = len(store['channels']) + 1

    if not check_token_valid(token):
        raise AccessError(description="Token does not exist for user")

    token_payload = decode_token(token)
    
    owner_perm = 2
    for user in store['users']:
        if user['auth_user_id'] == token_payload['u_id']:
            update_user_channel_stats(user, False)
            user['in_channels'].append(channel_id)
            store['channels'].append({  
                            'channel_id': channel_id,
                            'is_public': is_public,
                            'owner_perms': [],
                            'name': name,
                            'members': [user['userdata']],
                            'messages': [],
                            'standup_package': [],
                            'owners': [user['userdata']],
                            'standup': {
                                'is_active': False,
                                'time_start': 0,
                                'creator_id': [],
                                'time_finish': None,
                            }
                            })
            owner_perm = user['global_perms']     

    if owner_perm == 1:
        for channel in store['channels']:
            if channel['channel_id'] == channel_id:
                channel['owner_perms'].append(token_payload['u_id'])

    data_store.set(store)
    return {
        'channel_id': channel_id,
    }

