from readline import parse_and_bind
import jwt
import hashlib
from src.data_store import data_store
from datetime import timezone
import datetime
SECRET = 'not_secret'


def generate_token(u_id, session):
    payload = {
        'u_id': u_id,
        'session_id': session,
    }
    return jwt.encode(payload, SECRET, algorithm='HS256')


def decode_token(encoded_token):
    return jwt.decode(encoded_token, SECRET, algorithms=['HS256'])


def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def check_token_valid(token):
    store = data_store.get()
    try:
        decode_token(token)
    except BaseException:
        return False

    data = decode_token(token)
    for user in store['users']:
        if user['auth_user_id'] == data['u_id']:
            for id in user['session_id']:
                if data['session_id'] == id:
                    return True
    return False

def get_unix_timestamp():
    dt = datetime.datetime.now(timezone.utc)
    utc_time = dt.replace(tzinfo=timezone.utc)
    utc_timestamp = utc_time.timestamp()
    return utc_timestamp

def update_user_channel_stats(user, left):
    if left:
        num_channels_joined = user['user_stats']['channels_joined'][-1]['num_channels_joined'] - 1
    else:
        num_channels_joined = user['user_stats']['channels_joined'][-1]['num_channels_joined'] + 1
    user['user_stats']['channels_joined'].append({'num_channels_joined': num_channels_joined, 'time_stamp': get_unix_timestamp()})

def update_user_dm_stats(user, left):
    if left:
        num_dms_joined = user['user_stats']['dms_joined'][-1]['num_dms_joined'] - 1
    else:
        num_dms_joined = user['user_stats']['dms_joined'][-1]['num_dms_joined'] + 1
    user['user_stats']['dms_joined'].append({'num_dms_joined': num_dms_joined, 'time_stamp': get_unix_timestamp()})

def update_user_message_stats(user):
    num_dms_joined = len(user['user_stats']['messages_sent']) + 1
    user['user_stats']['messages_sent'].append({'num_messages_sent': num_dms_joined, 'time_stamp': get_unix_timestamp()})
