from src.data_store import data_store
from src.error import InputError, AccessError
from src.helpers import check_token_valid
from src.channels import token_to_id

'''
=====================================================================================================================

admin_userpermission_change_v1

Given a u_id, set that user to specified permissions dictated by permission_id

Arguments:
    token (str)    - Registered user's token string
    u_id (int)    - user id of  specified user
    permission_id(int)      - Integer of permission id.

Exceptions:
    Input Error - u_id does not refer to a valid user
    InputError - u_id refers to a user who is the only global owner and they are being demoted to a user
    InputError - permission_id is invalid
    InputError - the user already has the permissions level of permission_id
    AccessError - the authorised user is not a global owner
    AccessError - the token is invalid

Return Value:
Returns empty dictionary

=====================================================================================================================
'''
def admin_userpermission_change_v1(token, u_id, permission_id):

    store = data_store.get()

    token = str(token)
    u_id = int(u_id)
    permission_id = int(permission_id)

    if not check_token_valid(token):
        raise AccessError(description="Invalid token")

    u_id_check = False
    for user in store['users']:
        if u_id == user['auth_user_id']:
            u_id_check = True

    if not u_id_check:
        raise InputError(description="u_id is invalid")
    
    valid_owner = False
    owner_id = token_to_id(token)

    for user in store['users']:
        if user['auth_user_id'] == owner_id:
            if user['global_perms'] == 1:
                valid_owner = True

    if not valid_owner:
        raise AccessError(description="User is not a global owner") 

    if permission_id != 1 and permission_id != 2:
        raise InputError(description="This is an invalid permission id")

    global_count = 0
    for user in store['users']:
        if user['global_perms'] == 1:
            global_count +=1

    if global_count == 1 and owner_id == u_id:
        raise InputError(description="This user is the only global owner and cannot be demoted to a user")

    for user in store['users']:
        if user['auth_user_id'] == u_id:
            if user['global_perms'] == permission_id:
                raise InputError(description="User already has the permission levels of permission_id")


    for user in store['users']:
        if user['auth_user_id'] == u_id and user['global_perms'] == 1 and permission_id == 2:
            for channel in store['channels']:
                for member in channel['members']:
                    if member['u_id'] == u_id:
                        channel['owner_perms'].remove(member['u_id'])
                    

    for user in store['users']:
        if user['auth_user_id'] == u_id:
                user['global_perms'] = permission_id

    data_store.set(store)

    return {}

'''
=====================================================================================================================

admin_user_remove_v1

Given a user by u_id, remove them from Seams. Remove the from all channels/DMs, they will not be included in the list
of users returned by users/all. Seams owners can remove other Seams owners. The message contents will be replaced by
'Removed user' and name_first will be replaced to 'Removed', respectively name_last will be replaced to 'user'.
Arguments:
    token (str)    - Registered user's token string
    u_id (int)    - user id of  specified user

Exceptions:
    Input Error - u_id does not refer to a valid user
    InputError - u_id refers to a user who is the only global owner.
    AccessError - the authorised user is not a global owner
    AccessError - the token is invalid
        
Return Value:
Returns empty dictionary

=====================================================================================================================
'''
def admin_user_remove_v1(token, u_id):

    store = data_store.get()
    token = str(token)
    u_id = int(u_id)

    if not check_token_valid(token):
        raise AccessError(description="Invalid token")

    u_id_check = False
    for user in store['users']:
        if u_id == user['auth_user_id']:
            u_id_check = True

    if not u_id_check:
        raise InputError(description="u_id is invalid")
    
    valid_owner = False

    owner_id = token_to_id(token)

    for user in store['users']:
        if user['auth_user_id'] == owner_id:
            if user['global_perms'] == 1:
                valid_owner = True

    if not valid_owner:
        raise AccessError(description="User is not a global owner")

    
    global_count = 0
    for user in store['users']:
        if user['global_perms'] == 1:
            global_count +=1

    if global_count == 1 and owner_id == u_id:
        raise InputError(description="This user is the only global owner and cannot be demoted to a user")


    for user in store['users']:
        if user['auth_user_id'] == u_id: 
            user['first_name'] = 'Removed'
            user['last_name'] = 'user'
            
            user['userdata']['name_first'] == 'Removed'
            user['userdata']['name_last'] == 'user'

    for channel in store['channels']:
        for message in channel['messages']:
            if message['u_id'] == u_id:
                message['message'] = 'Removed user'
        for member in channel['members']:
            if member['u_id'] == u_id:
                channel['members'].remove(member)
        for owner in channel['owners']:
            if owner['u_id'] == u_id:
                channel['owners'].remove(owner)


    for dm in store['dms']:
        for message in dm['messages']:
            if message['u_id'] == u_id:
                message.clear()
                message['message'] = 'Removed user'
        for member in dm['members']:
            if member['u_id'] == u_id:
                dm['members'].remove(member)
        for owner in dm['owners']:
            if owner['u_id'] == u_id:
                dm['owners'].remove(owner)

    data_store.set(store)

    return {}
