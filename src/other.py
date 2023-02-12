from src.data_store import data_store
from src.error import InputError, AccessError
from src.helpers import check_token_valid
from src.channels import token_to_id


def clear_v1():
    store = data_store.get()
    store['users'].clear()
    store['channels'].clear()
    store['dms'].clear()
    data_store.set(store)


def notifications_get_v1(token):
    '''=====================================================================================================================

    notifications/get/v1

    Return the user's most recent 20 notifications, ordered from most recent to least recent.

    Arguments:
        token (str)    - Registered user's token string


    Exceptions:
        InputError - invalid token

    Return Value:
        Returns dictionary of notifications

    =====================================================================================================================
    '''
    store = data_store.get()
    # check if token is valid for AccessError
    if not check_token_valid(token):
        raise AccessError(description="Invalid Token")
    # convert token to u_id
    user_id = token_to_id(token)
    # go to the user's notifications
    for user in store['users']:
        if user['auth_user_id'] == user_id:
            tmp_list = list(user['notifications'])
    # append last 20 elements of notifications into empty list
    if len(tmp_list) <= 20:
        notifications_list = list(reversed(tmp_list))
    else:
        notifications_list = list(reversed(tmp_list))[:20]
     # return {'notifications': list}
    return {'notifications': notifications_list}


def search_v1(token, query_str):
    '''=====================================================================================================================

    search/v1

    Given a query string, return a collection of messages in all of the channels and DMs that the user has joined that contain 
    the case-sensitive query. Messages have no expected order.

    Arguments:
        token (str)    - Registered user's token string
        query_str(str) - Query string parameter

    Exceptions:
        InputError - length of query_str is less than 1 or over 1000 characters
        InputError - invalid token


    Return Value:
        Returns dictionary of messages

    =====================================================================================================================
    '''
    store = data_store.get()
    # case insensitive search
    query_str = query_str.lower()

    # AccessError for invalid token
    if not check_token_valid(token):
        raise AccessError(description="Invalid Token")
    # InputError for query_str length
    if len(query_str) > 1000:
        raise InputError(description="query_str is above 1000 characters")
    elif len(query_str) < 1:
        raise InputError(description="query_str is below 1 character")

    user_id = token_to_id(token)
    return_list = []
    # search in channel messages
    for user in store['users']:
        if user['auth_user_id'] == user_id:
            in_channels = list(user['in_channels'])

    for channel in store['channels']:
        if channel['channel_id'] in in_channels:
            for msg in channel['messages']:
                if msg['u_id'] == user_id:
                    if query_str in msg['message'].lower():
                        return_list.append(msg)
    # search is dm messages
    for dm in store['dms']:
        if user_id == dm['members']['u_id']:
            for msg in dm['messages']:
                if msg['u_id'] == user_id:
                    if query_str in msg['message'].lower():
                        return_list.append(msg)

    return {'messages': return_list}
