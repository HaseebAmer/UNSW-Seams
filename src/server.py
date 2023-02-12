import signal
import pickle
from json import dumps
from flask import Flask, request
from flask_cors import CORS
from src import config
from src.auth import auth_login_v1, auth_register_v1, auth_logout
from src.channels import channels_create_v1, channels_list_v1, channels_listall_v1
from src.auth import auth_login_v1, auth_register_v1, auth_reset_password_request, auth_reset_password
from flask_mail import Message, Mail
from src.other import clear_v1
from src.dm import dm_create_v1, dm_list_v1, dm_remove_v1, dm_messages_v1, dm_details_v1, dm_leave_v1
from src.user import user_profile, user_setemail, user_sethandle, all_users, user_setname, user_stats, user_upload_photo
from src.channel import channel_leave_v1, channel_join_v1, channel_details_v1, channel_invite_v1, channel_addowner_v1, channel_removeowner_v1
from src.channel import channel_messages_v1
from src.echo import echo
from src.data_store import save, data_store
from src.message import message_send_v1, message_edit_v1, message_senddm_v1, message_remove_v1, message_share_v1, message_react_v1, message_unreact_v1, message_pin_v1, message_unpin_v1
from src.admin import admin_user_remove_v1, admin_userpermission_change_v1
from src.other import notifications_get_v1, search_v1
from src.standup import standup_active_v1, standup_send_v1, standup_start_v1

def quit_gracefully(*args):
    '''For coverage'''
    exit(0)


def defaultHandler(err):
    response = err.get_response()
    print('response', err, err.get_response())
    response.data = dumps({
        "code": err.code,
        "name": "System Error",
        "message": err.get_description(),
    })
    response.content_type = 'application/json'
    return response


APP = Flask(__name__)
CORS(APP)

APP.config['MAIL_SERVER']='smtp.gmail.com'
APP.config['MAIL_PORT'] = 465
APP.config['MAIL_USERNAME'] = 'ritalinfiend@gmail.com'
APP.config['MAIL_PASSWORD'] = 'brain_chem'
APP.config['MAIL_USE_TLS'] = False
APP.config['MAIL_USE_SSL'] = True

APP.config['TRAP_HTTP_EXCEPTIONS'] = True
APP.register_error_handler(Exception, defaultHandler)

# NO NEED TO MODIFY ABOVE THIS POINT, EXCEPT IMPORTS

# Load data
try:
    data = pickle.load(open('datastore.p', 'rb'))
    data_store.set(data)
except Exception:
    pass

def send_email(email, reset_code):
    mail = Mail(APP)
    message = Message("Password reset", sender = 'ritalinfiend@gmail.com', recipients = [email])
    message.body = reset_code
    mail.send(message)

@APP.route("/echo", methods=['GET'])
def echo_http():
    data = request.args.get('data')
    value = echo(data)
    return dumps({
        'data': value
    })


@APP.route("/clear/v1", methods=['DELETE'])
def clear():
    clear_v1()
    save()
    return dumps({})


@APP.route("/auth/login/v2", methods=['POST'])
def login():
    request_data = request.get_json()
    login_user = auth_login_v1(request_data['email'], request_data['password'])
    u_id = login_user['auth_user_id']
    token = login_user['token']
    save()
    return dumps({
        'auth_user_id': u_id,
        'token': token,
    })


@APP.route("/auth/register/v2", methods=['POST'])
def register():
    data = request.get_json()
    register_user = auth_register_v1(
        data['email'], data['password'], data['name_first'], data['name_last'])
    u_id = register_user['auth_user_id']
    token = register_user['token']
    save()
    return dumps({
        'auth_user_id': u_id,
        'token': token,
    })


@APP.route("/channels/create/v2", methods=['POST'])
def create_channel():
    data = request.get_json()
    channel_id = channels_create_v1(
        data['token'], data['name'], data['is_public'])
    save()
    return dumps({
        'channel_id': channel_id['channel_id']
    })


@APP.route("/channels/listall/v2", methods=['GET'])
def channels_listall_v2():
    token = request.args.get('token')
    result = channels_listall_v1(token)
    save()
    return dumps(result)


@APP.route("/auth/logout/v1", methods=['POST'])
def logout():
    data = request.get_json()
    logout_return = auth_logout(data['token'])
    save()
    return dumps(logout_return)


@APP.route("/users/all/v1", methods=['GET'])
def all_users_http():
    token = request.args.get('token')
    result = all_users(token)
    save()
    return dumps(result)


@APP.route("/user/profile/v1", methods=['GET'])
def profile():
    token = request.args.get('token')
    u_id = request.args.get('u_id')
    result = user_profile(token, u_id)
    save()
    return dumps(result)


@APP.route("/user/profile/setname/v1", methods=['PUT'])
def set_user_name():
    data = request.get_json()
    setname_return = user_setname(
        data['token'], data['name_first'], data['name_last'])
    save()
    return dumps(setname_return)


@APP.route("/user/profile/setemail/v1", methods=['PUT'])
def set_user_email():
    data = request.get_json()
    setemail_return = user_setemail(data['token'], data['email'])
    save()
    return dumps(setemail_return)


@APP.route("/user/profile/sethandle/v1", methods=['PUT'])
def set_user_handle():
    data = request.get_json()
    sethandle_return = user_sethandle(data['token'], data['handle_str'])
    save()
    return dumps(sethandle_return)


@APP.route("/channels/list/v2", methods=['GET'])
def channels_list_v2():
    token = request.args.get('token')
    result = channels_list_v1(token)
    save()
    return dumps(result)


@APP.route("/channel/invite/v2", methods=['POST'])
def channel_invite_v2():
    data = request.get_json()
    channel_invite_v1(data['token'], data['channel_id'], data['u_id'])
    save()
    return dumps({})


@APP.route("/channel/leave/v1", methods=['POST'])
def channel_leave_v1_http():
    data = request.get_json()
    channel_leave_v1(data['token'], data['channel_id'])
    save()
    return dumps({})


@APP.route("/channel/details/v2", methods=['GET'])
def channel_details_v2():
    token = request.args.get('token')
    channel_id = request.args.get('channel_id')
    result = channel_details_v1(token, channel_id)
    save()
    return dumps(result)


@APP.route('/channel/join/v2', methods=["POST"])
def channel_join():
    data = request.get_json()
    channel_join = channel_join_v1(data['token'], data['channel_id'])
    save()
    return dumps(channel_join)


@APP.route("/channel/addowner/v1", methods=['POST'])
def channel_addowner():
    data = request.get_json()
    channel_addowner_v1(data['token'], data['channel_id'], data['u_id'])
    save()
    return dumps({})


@APP.route("/channel/removeowner/v1", methods=['POST'])
def channel_removeowner():
    data = request.get_json()
    channel_removeowner_v1(data['token'], data['channel_id'], data['u_id'])
    save()
    return dumps({})


@APP.route("/dm/create/v1", methods=['POST'])
def dm_create():
    data = request.get_json()
    dm_id = dm_create_v1(data['token'], data['u_ids'])
    save()
    return dumps(dm_id)


@APP.route("/dm/list/v1", methods=['GET'])
def dm_list():
    token = request.args.get('token')
    dms = dm_list_v1(token)
    save()
    return dumps(dms)


@APP.route("/dm/remove/v1", methods=['DELETE'])
def dm_remove():
    data = request.get_json()
    dm_remove_v1(data['token'], data['dm_id'])
    save()
    return dumps({})


@APP.route("/channel/messages/v2", methods=['GET'])
def channel_messages():
    token = request.args.get('token')
    channel_id = request.args.get('channel_id')
    start = request.args.get('start')
    messages_channel = channel_messages_v1(token, channel_id, start)
    save()
    return dumps(messages_channel)


@APP.route("/message/send/v1", methods=['POST'])
def send_message():
    data = request.get_json()
    message_send = message_send_v1(
        data['token'], data['channel_id'], data['message'])
    save()
    return dumps(message_send)


@APP.route("/message/edit/v1", methods=['PUT'])
def message_edit():
    data = request.get_json()
    message_edit_v1(data['token'], data['message_id'], data['message'])
    save()
    return dumps({})


@APP.route("/message/senddm/v1", methods=['POST'])
def send_dm():
    data = request.get_json()
    dm = message_senddm_v1(data['token'], data['dm_id'], data['message'])
    save()
    return dumps(dm)


@APP.route("/message/remove/v1", methods=['DELETE'])
def delete_message():
    data = request.get_json()
    message_remove_v1(data['token'], data['message_id'])
    save()
    return dumps({})


@APP.route("/dm/details/v1", methods = ['GET'])
def dm_details():   
    token = request.args.get('token')
    dm_id = request.args.get('dm_id')
    result = dm_details_v1(token, dm_id)
    save()
    return dumps(result)

@APP.route("/dm/leave/v1", methods = ['POST'])
def dm_leave():
    data = request.get_json()
    result = dm_leave_v1(data['token'], data['dm_id'])
    save()
    return dumps(result)
    
@APP.route("/admin/userpermission/change/v1", methods = ['POST'])
def admin_userpermission_change():
    data = request.get_json()
    result = admin_userpermission_change_v1(data['token'], data['u_id'], data['permission_id'])
    save()
    return dumps(result)


@APP.route("/admin/user/remove/v1", methods = ['DELETE'])
def admin_user_remove():
    data = request.get_json()
    admin_user_remove_v1(data['token'], data['u_id'])
    save()
    return dumps({})

@APP.route("/dm/messages/v1", methods=['GET'])
def get_dms():
    token = request.args.get('token')
    dm_id = request.args.get('dm_id')
    start = request.args.get('start')
    dm_msgs = dm_messages_v1(token, dm_id, start)
    save()
    return dumps(dm_msgs)

@APP.route("/auth/passwordreset/request/v1", methods=['POST'])
def auth_password_reset_request():
    data = request.get_json()
    auth_reset_password_request(data['email'])
    save()
    store = data_store.get()
    for user in store['users']:
        if user['email'] == data['email']:
            send_email(user['email'], user['reset_code'])
    return dumps({})

@APP.route("/auth/passwordreset/reset/v1", methods=['POST'])
def auth_password_reset():
    data = request.get_json()
    result = auth_reset_password(data['reset_code'], data['new_password'])
    save()
    return dumps(result)

@APP.route("/user/stats/v1", methods=['GET'])
def get_user_stats():
    token = request.args.get('token')
    result = user_stats(token)
    save()
    return dumps(result)

@APP.route("/user/profile/uploadphoto/v1", methods=['POST'])
def upload_photo():
    data = request.get_json()
    result = user_upload_photo(data['token'], data['img_url'], data['x_start'], data['y_start'], data['x_end'], data['y_end'])
    save()
    return dumps(result)

@APP.route("/notifications/get/v1", methods = ['GET'])
def notifications_get():
    token = request.args.get('token')
    notifications = notifications_get_v1(token)
    save()
    return dumps(notifications)
    
@APP.route("/search/v1", methods = ['GET'])
def search():
    token = request.args.get('token')
    query_str = request.args.get('query_str')
    messages = search_v1(token, query_str)
    save()
    return dumps(messages)

@APP.route("/standup/start/v1", methods=['POST'])
def standup_start():
    data = request.get_json()
    result = standup_start_v1(data['token'], data['channel_id'], data['length'])
    save()
    return dumps(result)
    
@APP.route("/standup/active/v1", methods = ['GET'])
def standup_active():
    token = request.args.get('token')
    channel_id = request.args.get('channel_id')
    result = standup_active_v1(token,channel_id)
    save()
    return dumps(result)
    
@APP.route("/standup/send/v1", methods=['POST'])
def standup_send():
    data = request.get_json()
    result = standup_send_v1(data['token'], data['channel_id'], data['message'])
    save()
    return dumps(result)

@APP.route("/message/share/v1", methods=['POST'])
def message_share():
    data = request.get_json()
    result = message_share_v1(
        data['token'], data['og_message_id'], data['message'], data['channel_id'], data['dm_id'])
    save()
    return dumps(result)

@APP.route("/message/react/v1", methods=['POST'])
def message_react():
    data = request.get_json()
    message_react_v1(data['token'], data['message_id'], data['react_id'])
    save()
    return dumps({})

@APP.route("/message/unreact/v1", methods=['POST'])
def message_unreact():
    data = request.get_json()
    message_unreact_v1(data['token'], data['message_id'], data['react_id'])
    save()
    return dumps({})

@APP.route("/message/pin/v1", methods=['POST'])
def message_pin():
    data = request.get_json()
    message_pin_v1(data['token'], data['message_id'])
    save()
    return dumps({})


@APP.route("/message/unpin/v1", methods=['POST'])
def message_unpin():
    data = request.get_json()
    message_unpin_v1(data['token'], data['message_id'])
    save()
    return dumps({})





# NO NEED TO MODIFY BELOW THIS POINT


if __name__ == "__main__":
    signal.signal(signal.SIGINT, quit_gracefully)  # For coverage
    APP.run(port=config.port)  # Do not edit this port
