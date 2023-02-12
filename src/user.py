from src.data_store import data_store
from src.error import InputError, AccessError
from src.helpers import check_token_valid
from src.auth import check_valid_name, check_email_validity
from src.config import url
from PIL import Image
import imghdr
from urllib import request


def check_dimensions(img_file, x_start, y_start, x_end, y_end):
    photo = Image.open(img_file)
    width, height = photo.size
    if x_start < 0 or x_start >= width or x_end < 0 or x_end >= width:
        raise InputError(description="Invalid crop dimensions")
    elif x_end <= x_start or y_end <= y_start:
        raise InputError(description="Invalid crop dimensions")
    elif y_start < 0 or y_start >= height or y_end < 0 or y_end >= height:
        raise InputError(description="Invalid crop dimensions")


def update_photo(user_list, u_id, profile_img_url):
    for user in user_list:
        for member in user['members']:
            if member['u_id'] == u_id:
                member['profile_img_url'] = profile_img_url
    for user in user_list:
        for owner in user['owners']:
            if owner['u_id'] == u_id:
                owner['profile_img_url'] = profile_img_url


def users_return(user):
    return {'email': user['email'], 'u_id': user['auth_user_id'], 'name_first': user['first_name'], 'name_last': user['last_name'], 'handle_str': user['handle']}


def token_to_user(token):
    store = data_store.get()
    for user in store['users']:
        for element in user['tokens']:
            if element == token:
                return user


'''
=====================================================================================================================

users_all_v1

Returns a list of all users and their associated details.

Arguments:
    token (str)    - Registered user's token string


Exceptions:
    AccessError - Occurs when an invalid token_id is passed into the function


Return Value:
    Returns list of dictionary of user information.
=====================================================================================================================
'''


def all_users(token):
    store = data_store.get()

    if not check_token_valid(token):
        raise AccessError(description="Token does not exist for user")

    user_list = []
    for user in store['users']:
        user_dict = users_return(user)
        user_list.append(user_dict)

    return user_list


'''
=====================================================================================================================

user_profile_v1

For a valid user, returns information about their user_id,
email, first name, last name, and handle
    
Arguments:
    token (str)    - Registered user's token string
    u_id(int)      - Registered user's u_id


Exceptions:
    AccessError - Occurs when an invalid token_id is passed into the function


Return Value:
    Returns list of user information
=====================================================================================================================
'''


def user_profile(token, u_id):
    store = data_store.get()

    if not check_token_valid(token):
        raise AccessError(description="Token does not exist for user")

    u_id = int(u_id)

    valid_u_id = False
    for user in store['users']:
        if user['auth_user_id'] == u_id:
            valid_u_id = True
            user_dict = users_return(user)

    if not valid_u_id:
        raise InputError(description="User does not exist")

    return {'user': user_dict}


'''
=====================================================================================================================

user_profile_setname_v1

Update the authorised user's first and last name
    
Arguments:
    token (str)    - Registered user's token string
    name_first(str)      - Registered user's first name
    name_last(str)      - Registered user's last name

Exceptions:
    InputError - length of name_first is not between 1 and 50 characters inclusive
    InputError - length of name_last is not between 1 and 50 characters inclusive
    AccessError - Occurs when an invalid token_id is passed into the function

Return Value:
    Returns empty dictionary
=====================================================================================================================
'''


def user_setname(token, name_first, name_last):
    store = data_store.get()

    if not check_token_valid(token):
        raise AccessError(description="Token does not exist for user")

    check_valid_name(name_first, name_last)

    user = token_to_user(token)
    user['first_name'] = name_first
    user['last_name'] = name_last
    user['userdata']['name_first'] = name_first
    user['userdata']['name_last'] = name_last

    data_store.set(store)
    return {}


'''
=====================================================================================================================
user_profile_setemail__v1

Update the authorised user's first and last name
    
Arguments:
    token (str)    - Registered user's token string
    email(str)    - Registered user's email.

Exceptions:
    InputError - email entered is not a valid email 
    InputError - email address is already being used by another user
    AccessError - Occurs when an invalid token_id is passed into the function

Return Value:
    Returns empty dictionary
=====================================================================================================================
'''


def user_setemail(token, email):
    store = data_store.get()

    if not check_token_valid(token):
        raise AccessError(description="Token does not exist for user")

    check_email_validity(email)

    for user in store['users']:
        if user['email'] == email:
            raise InputError(description="Email is already in use")

    user = token_to_user(token)
    user['email'] = email
    user['userdata']['email'] = email

    data_store.set(store)
    return {}


'''
=====================================================================================================================
user_profile_sethandle__v1

Update the authorised user's handle (i.e. display name)
        
Arguments:
    token (str)    - Registered user's token string
    handle_str(str)    - Registered user's handle string.

Exceptions:
    InputError - length of handle_str is not between 3 and 20 characters inclusive
    InputError - handle_str contains characters that are not alphanumeric
    InputError - the handle is already used by another user
    AccessError - Occurs when an invalid token_id is passed into the function

Return Value:
    Returns empty dictionary
=====================================================================================================================
'''


def user_sethandle(token, handle_str):
    store = data_store.get()
    if not check_token_valid(token):
        raise AccessError(description="Token does not exist for user")

    if len(handle_str) < 3 or len(handle_str) > 20:
        raise InputError(
            description="Handle must be between 3 and 20 characters inclusive")

    for user in store['users']:
        if user['handle'] == handle_str:
            raise InputError(
                description="Handle is already used by another user")

    if handle_str.isalnum():
        user = token_to_user(token)
        user['handle'] = handle_str
        user['userdata']['handle_str'] = handle_str
    else:
        raise InputError(
            description="handle must consist of alphanumeric characters only")

    data_store.set(store)
    return {}


def user_stats(token):
    '''=====================================================================================================================

user/stats/v1

Fetches the required statistics about this user's use of UNSW Seams.

Arguments:
    token (str)    - Reset code of password reset

Exceptions:
    InputError - invalid token

Return Value:
    Returns dictionary containing channels joined, dms joined and messages joined - containing involvement rate.
=====================================================================================================================
'''
    store = data_store.get()
    if not check_token_valid(token):
        raise AccessError(description="Token does not exist for user")

    user = token_to_user(token)

    num_channels_joined = user['user_stats']['channels_joined'][-1]['num_channels_joined']
    num_dms_joined = user['user_stats']['dms_joined'][-1]['num_dms_joined']
    num_messages_sent = len(user['user_stats']['messages_sent'])
    involvement_numerator = num_messages_sent + num_dms_joined + num_channels_joined

    num_channels = len(store['channels'])
    num_dms = len(store['dms'])

    num_messages = 0
    for channel in store['channels']:
        num_messages = num_messages + len(channel['messages'])
    for dm in store['dms']:
        num_messages = num_messages + len(dm['messages'])

    involvement_denominator = num_channels + num_dms + num_messages
    if involvement_denominator == 0:
        user['user_stats']['involvement_rate'] = 0
    else:
        involvement_rate = involvement_numerator / involvement_denominator
        if involvement_rate > 1:
            involvement_rate = 1
        user['user_stats']['involvement_rate'] = involvement_rate

    data_store.set(store)
    return {'user_stats': user['user_stats']}


def user_upload_photo(token, img_url, x_start, y_start, x_end, y_end):
    '''=====================================================================================================================

    user/profile/uploadphoto/v1

    Given a URL of an image on the internet, crops the image within bounds (x_start, y_start) and (x_end, y_end). Position 
    (0,0) is the top left. Please note: the URL needs to be a non-https URL (it should just have "http://" in the URL. We 
    will only test with non-https URLs.

    Arguments:
        token (str)    - Reset code of password reset
        img_url (str)  - URL of the image
        x_start(int)   - x co-ordinates start integer
        y_start(int)   - y co-ordinates start integer
        x_end (int)    - x co-ordinates end integer
        y_end (int)    - y co-ordinates end integer
    Exceptions:
        InputError - img_url returns an HTTP status other than 200, or any other errors occur when attempting to retrieve the image
        InputError - any of x_start, y_start, x_end, y_end are not within the dimensions of the image at the URL
        InputError - x_end is less than or equal to x_start or y_end is less than or equal to y_start
        InputError - image uploaded is not a JPG
        InputError - invalid token


    Return Value:
        Returns empty dictionary
    =====================================================================================================================
    '''
    store = data_store.get()
    if not check_token_valid(token):
        raise AccessError(description="Token does not exist for user")
    user = token_to_user(token)
    u_id = user['auth_user_id']
    static_url = f'src/static/{u_id}.jpg'
    try:
        request.urlretrieve(img_url, static_url)
    except:
        raise InputError(
            description="img_url cannot be retrieved") from InputError

    check_dimensions(static_url, x_start, y_start, x_end, y_end)

    if imghdr.what(static_url) != 'jpeg':
        raise InputError('Image uploaded is not of type JPEG')

    photo = Image.open(static_url)
    save_url = f'src/static/cropped{u_id}.jpg'
    photo.crop((x_start, y_start, x_end, y_end)).save(save_url)
    profile_img_url = url + save_url
    user['userdata']['profile_img_url'] = profile_img_url

    update_photo(store['channels'], u_id, profile_img_url)
    update_photo(store['dms'], u_id, profile_img_url)

    return {}
