from src.data_store import data_store
from src.error import InputError, AccessError
from src.helpers import check_token_valid, update_user_dm_stats
from src.channels import token_to_id


'''=====================================================================================================================

dm_create_v1

Creates a DM with u_ids and a creator. The creator is the owner of the DM. DM name is automatically generated
based on alphabetically-sorted, comma-and-space sorted seperated list of user handles.

Arguments:
    token (str)    - Registered user's token string
    u_id (int)    - Registered user's u_id

Exceptions:
    InputError  - any u_id in u_ids does not refer to a valid user
    InputError - there are duplicate 'u_id's in u_ids
    AccessError - Occurs when an invalid token_id is passed into the function


Return Value:
    Returns dm_id of newly created dm

=====================================================================================================================
'''

def dm_create_v1(token, u_ids):
    store = data_store.get()
    # check if token is valid, else raise accesserror
    if not check_token_valid(token):
        raise AccessError(description="Invalid Token")
    # check u_id is a list
    if not isinstance(u_ids, list):
        raise InputError(description="u_ids is not a list")
    # check owner is not in u_ids
    creator_id = token_to_id(token)
    if creator_id in u_ids:
        raise InputError(description="Invalid u_id: creator's id is in u_ids")
    # check no duplicate elements in u_ids
    if len(u_ids) != len(set(u_ids)):
        raise InputError(description="u_ids contains duplicate u_id")
        
    # check that every u_id is valid
    user_count = 0
    for id in u_ids:
        for user in store['users']:
            if id == user['auth_user_id']:
                user_count += 1
    if len(u_ids) != user_count:
        raise InputError(description="u_id in u_ids is invalid")
    
    # generate dm_id
    dm_id = len(store['dms']) + 1
    # generate name
    handles_list = []
    for id in u_ids:
        for user in store['users']:
            if id == user['auth_user_id']:
                handles_list.append(user['handle'])
    
    owner_id = token_to_id(token)
    for user in store['users']:
        if owner_id == user['auth_user_id']:
            handles_list.append(user['handle'])
    handles_list.sort()
    name = ", ".join(handles_list)
    # add all information in datastore: store['dms']

    store['dms'].append({
        'dm_id': dm_id,
        'name': name,
        'members': [],
        'owners': [],
        'messages': [],
    })
    # append owners
    for user in store['users']:
        if creator_id == user['auth_user_id']:
            for dm in store['dms']:
                if dm_id == dm['dm_id']:
                    dm['owners'].append(user['userdata'])
                    dm['members'].append(user['userdata'])
    # append members
    for user in store['users']:
        for u_id in u_ids:
            if u_id == user['auth_user_id']:
                for dm in store['dms']:
                    if dm_id == dm['dm_id']:
                        dm['members'].append(user['userdata'])

    # send notification to all users in u_ids for joining dm "{User’s handle} added you to {channel/DM name}"
    for user in store['users']:
        if creator_id == user['auth_user_id']:
            owner_handle = user['handle']
    
    for user in store['users']:
        if user['auth_user_id'] in u_ids:
            user['notifications'].append({'channel_id': -1, 'dm_id': dm_id, 'notification_message': f"{owner_handle} added you to {name}"})

    # update dm stats for each user being invited to dm
    all_users_in_dm = u_ids
    all_users_in_dm.append(creator_id)
    for user in store['users']:
        if user['auth_user_id'] in all_users_in_dm:
            update_user_dm_stats(user, False)



    data_store.set(store)
    return {
        'dm_id' : dm_id,
    }

'''
=====================================================================================================================

dm_list_v1

Returns the list of DMs that the user is a member of.
    
Arguments:
    token (str)    - Registered user's token string

Exceptions:
    AccessError - Occurs when an invalid token_id is passed into the function


Return Value:
    Returns list of DM's in the form of a dictionary.

=====================================================================================================================
'''

def dm_list_v1(token):
    store = data_store.get()
    # check if token is valid
    if not check_token_valid(token):
        raise AccessError(description="Invalid token")
    
    id = token_to_id(token)
    # add list functionality
    dm_list = []
    for dm in store['dms']:
        for member in dm['members']:
            if id == member['u_id']:
                dm_list.append({'dm_id': dm['dm_id'], 'name': dm['name']})

    return {
        'dms': dm_list
    }

'''
=====================================================================================================================

dm_remove_v1

Remove an existing DM, so all members are no longer in the DM. 
This can only be done by the original creator of the DM.
        
Arguments:
    token (str)    - Registered user's token string
    dm_id(int)     - dm ID of a particular DM

Exceptions:
    InputError - dm_id does not refer to a valid DM
    AccessError - dm_id is valid and the authorised user is not the original DM creator
    AccessError - dm_id is valid and the authorised user is no longer in the DM
      
Return Value:
    Returns list of DM's in the form of a dictionary.

=====================================================================================================================
'''

def dm_remove_v1(token, dm_id):
    store = data_store.get()
    # test invalid token accesserror
    if not check_token_valid(token):
        raise AccessError(description="Invalid token")
    # test invalid dm_id input error
    valid_dm_id = False
    for dm in store['dms']:
        if dm_id == dm['dm_id']:
            valid_dm_id = True

    if not valid_dm_id:
        raise InputError(description="Invalid dm_id")
    # test token not of creator accesserror
    token_of_creator = False
    id = token_to_id(token)
    for dm in store['dms']:
        if dm_id == dm['dm_id']:
            for owner in dm['owners']:
                if owner['u_id'] == id:
                    token_of_creator = True

    if not token_of_creator:
        raise AccessError(description="authorised user is not the original DM creator")

    # updating dm_stats for removing dm
    all_users_in_dm = []
    for dm in store['dms']:
        if dm['dm_id'] == dm_id:
            for member in dm['members']:
                all_users_in_dm.append(member['u_id'])
    
    for user in store['users']:
        if user['auth_user_id'] in all_users_in_dm:
            update_user_dm_stats(user, True)

    # removing dm
    index = 0
    for dm in store['dms']:
        if dm_id == dm['dm_id']:
            break
        index += 1
    
    store['dms'].pop(index)
    
    data_store.set(store)
    return {}

'''
=====================================================================================================================

dm_messages_v1

Given DM with dm_id, that the authorised user is a member of, return up to 50 messages between
index "start" and "start +50". Message with index 0 is the most recent message in the DM. This function
returns a new index "end" which is the value of "start + 50" or if this function has returned the least
recent messages in the DM, will return -1 in "end" to indicate there are no more messages.
        
Arguments:
    token (str)    - Registered user's token string
    dm_id(int)     - dm ID of a particular DM
    start(int)    - index of messages

Exceptions:
    InputError - dm_id does not refer to a valid DM
    InputError - start is greater than the total number of messages in the channel
    AccessError - dm_id is valid and the authorised user is not a member of the DM
      
Return Value:
    Returns messages, start and end - all messages in between indexes
    "start" and "end"
=====================================================================================================================
'''

def dm_messages_v1(token, dm_id, start):
    store = data_store.get()
    end = int(start)
    msg_count = 0

    if check_token_valid(token) is False:
        raise AccessError(description="token is invalid!")

    u_id = token_to_id(token)
    is_user_in = False
    is_dm_id_val = False
    for dm in store['dms']:
        if int(dm_id) == dm['dm_id']:
            is_dm_id_val = True
            for member in dm['members']:
                if u_id == member['u_id']:
                    is_user_in = True

    if is_dm_id_val is False:
        raise InputError(description="dm_id must refer to a valid DM")
    if is_user_in is False:
        raise AccessError(description="the user is not in this DM")

    for dm in store['dms']:
        if dm['dm_id'] == int(dm_id):
            msg_count = len(dm['messages'])

    if int(start) != 0 and int(start) >= msg_count:
        raise InputError(description="invalid start")

    for dm in store['dms']:
        if dm['dm_id'] == int(dm_id):
            for msg in dm['messages']:
                for react in msg['reacts']:
                    if u_id in react['u_ids']:
                        react['is_this_user_reacted'] = True

    messages = []
    i = 0
    for dm in store['dms']:
        if dm['dm_id'] == int(dm_id):
            for msg in dm['messages']:
                if len(messages) == 50:
                    break
                if (i >= int(start)):
                    messages.append(msg)
                i = i + 1

    if int(start) + 50 >= msg_count:
        end = -1
    else:
        end = int(start) + 50
    data_store.set(store)
    return {
        'messages': messages,
        'start': int(start),
        'end': end,
    }

'''
=====================================================================================================================

dm_details_v1

Given a DM with ID dm_id that the authorised user is a member of,
provide basic details about the DM.
    

Arguments:
    token (str)    - Registered user's token string
    dm_id (int)    - ID of  specified dm

Exceptions:
    Input Error - occurs when dm_id does not refer to a valid DM
    Access Error - occurs when dm_id is valid and authorised user is not a member of DM
    Access Error - occurs when user has invalid token_id

Return Value:
Returns name and members in a specific DM.

=====================================================================================================================
'''

def dm_details_v1(token, dm_id):
    store = data_store.get()
    token = str(token)
    dm_id = int(dm_id)

    store = data_store.get()
    if not check_token_valid(token):
        raise AccessError(description="Invalid token")

    for dm in store['dms']:
        if dm_id == dm['dm_id']:
            break
        else:
            raise InputError(description="Invalid dm_id")
    
    id = token_to_id(token)

    token_of_member = False
    for dm in store['dms']:
        if dm_id == dm['dm_id']:
            for member in dm['members']:
                if member['u_id'] == id:
                    token_of_member = True

    if not token_of_member:
        raise AccessError(description="Authorised user is not in the DM")

    dm_members = []
    for dm in store['dms']:
        if dm_id == dm['dm_id']:
            dm_members = dm['members']
            dm_name = dm['name']

    member_info = []
    for member in dm_members:
        for user in store['users']:
            if user['auth_user_id'] == member['u_id']:
                member_info.append(user['userdata'])

    return {
        "name": dm_name,
        "members": member_info,
    }

'''
=====================================================================================================================

dm_leave_v1

Given a DM the user is a member of, remove them as a member. The creator can leave the DM
and the DM will still exist. This does not update the DM name.
    

Arguments:
    token (str)    - Registered user's token string
    dm_id (int)    - ID of  specified dm

Exceptions:
    Input Error - occurs when dm_id does not refer to a valid DM
    Access Error - occurs when dm_id is valid and authorised user is not a member of DM
    Access Error - occurs when user has invalid token_id

Return Value:
Returns empty dictionary.
=====================================================================================================================
'''

def dm_leave_v1(token, dm_id):
    store = data_store.get()

    token = str(token)
    dm_id = int(dm_id)
    if not check_token_valid(token):
        raise AccessError(description="This is an invalid Token")
    
    u_id = token_to_id(token)

    dm_id_exist = False

    for dm in store['dms']:
        if dm_id == dm['dm_id']:
            dm_id_exist = True
    
    if not dm_id_exist:
        raise InputError(description="Invalid DM ID")

    #check if user is in the DM

    id = token_to_id(token)

    token_of_member = False
    for dm in store['dms']:
        if dm_id == dm['dm_id']:
            for member in dm['members']:
                if member['u_id'] == id:
                    token_of_member = True

    if not token_of_member:
        raise AccessError(description="Authorised user is not in the DM")
    
    #update user_dm_stats for dm_leave
    for user in store['users']:
        if user['auth_user_id'] == id:
            update_user_dm_stats(user, True)


    # remove user from dm
    dm_index = 0
    member_index = 0
    owner_index = 0
    owner_index_copy = -50

    for dm in store['dms']:
        if dm['dm_id'] == dm_id:
            dm_index_copy = dm_index
            for member in dm['members']:
                if u_id == member['u_id']:
                    member_index_copy = member_index
                    break
                member_index +=1
            for owner in dm['owners']:
                if u_id == owner['u_id']:
                    owner_index_copy = owner_index
                    break
                owner_index +=1
        dm_index +=1

    store['dms'][dm_index_copy]['members'].pop(member_index_copy)
    if owner_index_copy == owner_index:
        store['dms'][dm_index_copy]['owners'].pop(owner_index_copy)

    data_store.set(store)
    
    return {}
