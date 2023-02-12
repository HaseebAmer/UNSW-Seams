from src.data_store import data_store
from src.error import InputError, AccessError
from src.helpers import hash_password, decode_token, generate_token
from src.config import url
import re
from src.helpers import check_token_valid
from src.helpers import check_token_valid, get_unix_timestamp
from random import randint
from urllib import request

# function to check if the email inputted is valid


def check_email_validity(email):
    regex = r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}$'
    if not re.fullmatch(regex, email):
        raise InputError(description="Inputted email is not valid")


def check_valid_name(name_first, name_last):
    if len(name_first) < 1 or len(name_first) > 50 or len(name_last) < 1 or len(name_last) > 50:
        raise InputError(description="Name input not valid")


def default_photo(img_url):
    static_url = f'src/static/default.jpg'
    try:
        request.urlretrieve(img_url, static_url)
    except:
        raise InputError(
            description="img_url cannot be retrieved") from InputError
    image_url = url + static_url
    return image_url


def auth_login_v1(email, password):
    '''=====================================================================================================================

    auth_login_v2

    Given a registered user's email and password, returns their auth_user_id value and a new token

    Arguments:
        email (str)    - Registered user's email string
        password (str)    - Registered user's password string

    Exceptions:
        InputError  - Occurs when email does not follow regular expression
        InputError  - Occurs when email does not belong to a user
        InputError  - Occurs when password is incorrect


    Return Value:
        Returns auth_user id and token_id on successful login 

    =====================================================================================================================
    '''
    store = data_store.get()

    check_email_validity(email)
    # loop through users to check if email and password are correct
    for user in store['users']:
        if user['email'] == email:
            if user['password'] != hash_password(password):
                raise InputError(description="Wrong password has been entered")
            else:
                session_count = user['session_count'] + 1
                user['session_id'].append(session_count)
                token = generate_token(user['auth_user_id'], session_count)
                user['session_count'] = session_count
                user['tokens'].append(token)
                user_id = user['auth_user_id']
                data_store.set(store)
                return {'auth_user_id': user_id, 'token': token, }

    raise InputError(description="Email entered does not belong to a user")


'''   
=====================================================================================================================

auth_register_v1

Given a user's first and last name, email address, and password, register a user and return their auth_user_id and token

Arguments:
    email (str)    - Registered user's email string
    password (str)    - Registered user's password string
    name_first (str)    - Registered user's first name
    name_last (str)    - Registered user's last name

Exceptions:
    InputError  - Occurs when email does not regular expression
    InputError  - Occurs when email belongs to another user
    InputError - Occurs when email is invalid
    InputError  - Occurs when password is less than 6 characters
    InputError  - Occurs when length of name_first or name_last is not between 1 and 50 characters

Return Value:
    Returns auth_user id and token_id on successful registration

=====================================================================================================================
'''


def auth_register_v1(email, password, name_first, name_last):
    store = data_store.get()
    check_email_validity(email)
    if len(password) < 6:
        raise InputError(
            description="Password is too short, it must be at least 6 characters.")

    check_valid_name(name_first, name_last)

    for user in store['users']:
        if user['email'] == email:
            raise InputError(description="Email is already in use")

    user_id = len(store['users']) + 1

    # make the name lowercase and remove any non - alphanumeric characters
    fullname = (name_first + name_last).lower()
    handle = ''.join(letter for letter in fullname if letter.isalnum())
    if len(handle) > 20:
        handle = handle[:20]

    users = store['users']
    handle_length = len(handle)
    extra_index = 0
    i = 0
    while i < len(users):
        if users[i]['handle'] == handle:
            if len(handle) > handle_length:
                # if number has been added in previous iteration of the loop we concatenate again
                handle = handle[:handle_length]
            # add the number to the end of the handle
            handle = handle + str(extra_index)
            extra_index = extra_index + 1
            # we reset the loop in order to check if the new handle is also taken
            i = -1
        i = i + 1

    session_count = 0
    token = generate_token(user_id, session_count)

    # setting global permissions
    global_perm = 2
    if user_id == 1:
        global_perm = 1
        default_photo(
            'https://cdn5.vectorstock.com/i/1000x1000/17/44/person-icon-in-line-style-man-symbol-vector-24741744.jpg')
    unix_timestamp = get_unix_timestamp()
    static_url = f'src/static/default.jpg'
    image_url = url + static_url
    # stores the new users data
    store['users'].append({'first_name': name_first,
                           'last_name': name_last,
                           'email': email,
                           'handle': handle,
                           'auth_user_id': user_id,
                           'password': hash_password(password),
                           'userdata': {'name_first': name_first, 'name_last': name_last, 'email': email, 'u_id': user_id, 'handle_str': handle, 'profile_img_url': image_url},
                           'in_channels': [],
                           'global_perms': global_perm,
                           'tokens': [token],
                           'session_count': session_count,
                           'session_id': [session_count],
                           'reset_code': None,
                           'user_stats': {'channels_joined': [{'num_channels_joined': 0, 'time_stamp': unix_timestamp}],
                                          'dms_joined': [{'num_dms_joined': 0, 'time_stamp': unix_timestamp}],
                                          'messages_sent': [{'num_messages_sent': 0, 'time_stamp': unix_timestamp}], 'involvement_rate': 0},
                           'notifications': [],
                           })
    data_store.set(store)
    return {
        'auth_user_id': user_id,
        'token': token,
    }


'''   
=====================================================================================================================

auth_logout_v1

Given an active token, invalidates the token to log the user out.
    
Arguments:
    token(str)    - Registered user's token string

Exceptions:
    AccessError - the token is invalid

Return Value:
    Returns empty dictionary

=====================================================================================================================
'''


def auth_logout(token):
    store = data_store.get()
    if not check_token_valid(token):
        raise AccessError(description="Token does not exist for user")

    token_payload = decode_token(token)

    for user in store['users']:
        if user['auth_user_id'] == token_payload['u_id']:
            user['tokens'].remove(token)
            user['session_id'].remove(token_payload['session_id'])
            data_store.set(store)

    return {}


def auth_reset_password_request(email):
    '''=====================================================================================================================

    auth/passwordreset/request/v1

    Given an email address, if the user is a registered user, sends them an email containing a specific secret code, 
    that when entered in auth/passwordreset/reset, shows that the user trying to reset the password is the one who got sent
    this email. No error should be raised when passed an invalid email, as that would pose a security/privacy concern. When 
    a user requests a password reset, they should be logged out of all current sessions.


    Arguments:
        email (str)    - Registered user's email 

    Exceptions:
        InputError - Invalid email.

    Return Value:
        Returns empty dictionary
    =====================================================================================================================
    '''
    store = data_store.get()
    for user in store['users']:
        if user['email'] == email:
            user['reset_code'] = str(randint(100000, 999999))
            for token in user['tokens']:
                auth_logout(token)
    data_store.set(store)
    return {}


def auth_reset_password(reset_code, new_password):
    '''=====================================================================================================================

    auth/passwordreset/reset/v1

    Given a reset code for a user, set that user's new password to the password provided. Once a reset code has been used,
    it is then invalidated.



    Arguments:
        reset_code (str)    - Reset code of password reset
        new_password (str)  - New password string 

    Exceptions:
        InputError - reset_code is not a valid reset code
        InputError - password entered is less than 6 characters long

    Return Value:
        Returns empty dictionary
    =====================================================================================================================
    '''
    store = data_store.get()
    if len(new_password) < 6:
        raise InputError(
            description="Password is too short, it must be at least 6 characters.")
    valid_code = False
    for user in store['users']:
        if user['reset_code'] == reset_code:
            user['password'] = hash_password(new_password)
            valid_code = True
            user['reset_code'] = None
    if not valid_code:
        raise InputError(description="Reset code is invalid")
    return {}
