# ---------------------------
#Fichier : views.py
#Date : 14.10.2020
#But : ensemble des pages html
#Remarque :
#------------------------------

import datetime as dt

from flask import render_template, request, flash, redirect, make_response

from messenger import APP
from messenger.models import User, Session, Message, Model, get_current_timestamp
from messenger.security import check_pw, hash_pw, gen_rand_string
from messenger.decorators import is_logged_in, is_admin
from messenger.jwt import jwt_decode, jwt_encode, get_current_jwt

def current_user():
    # What is GEN ? Baby don't duplicate me, don't duplicate me, oh no

    # check if session cookie is present
    cookie = request.cookies.get('auth')
    if not cookie:
        return None

    # check if a valid JWT came in the cookie
    payload = jwt_decode(cookie)
    if not payload:
        return None

    # check if the named session exists
    session = Session.select(payload['session'])
    if not session:
        return None

    # check if the session has expired
    if session.expiry <= dt.datetime.now():
        return None

    return User.from_session(get_current_jwt()['session'])

@APP.route('/')
def index():
    return redirect('/inbox')

@APP.route('/inbox')
@is_logged_in
def inbox():
    user = current_user()

    senders = {}
    if user.messages:
        for msg in user.messages:
            senders[msg.sender_name] = '{}'.format(User.select(msg.sender_name))

    return render_template(
        'inbox.html',
        title='Inbox',
        user=user,
        senders=senders
    )

@APP.route('/compose', methods=['GET', 'POST'])
@is_logged_in
def compose(msg_title=None, msg_recipient=None):
    user = current_user()

    if request.method == 'POST':
        # retrieve form data
        args = {
            'recipient': request.form.get('recipient', type=str),
            'title': request.form.get('title', type=str),
            'body': request.form.get('body', type=str),
        }

        # ensure fields are present and within database limits
        if any(x == None for x in args.values()):
            flash('All fields are required', 'alert-danger')
        elif any(len(x) > Model.TEXT_MAX_LEN for x in args.values()):
            flash(
                'Fields may not exceed {} characters'.format(Model.TEXT_MAX_LEN),
                'alert-danger'
            )
        # check if recipient exists
        elif not User.find(args['recipient']):
            flash("Recipient doesn't exist", 'alert-danger')
        # create new message
        else:
            message = Message.insert(
                sender_name=user.username,
                recipient_name=args['recipient'],
                date=get_current_timestamp(),
                title=args['title'],
                body=args['body']
            )
            flash('Message successfully sent', 'alert-success')

    return render_template(
        'compose.html',
        title='New message',
        user=user,
        msg_title=msg_title,
        msg_recipient=msg_recipient
    )

@APP.route('/message/<string:message_id>')
@is_logged_in
def message_id(message_id):
    user = current_user()

    if len(message_id) > Model.TEXT_MAX_LEN:
        flash('Bad message ID', 'alert-danger')
        return redirect('/inbox')

    message = Message.select(message_id)
    if not message:
        flash("Message doesn't exist", 'alert-danger')
        return redirect('/inbox')
    elif message.recipient_name != user.username:
        flash("Can't view messages from other users", 'alert-danger')
        return redirect('/inbox')

    sender = '{}'.format(User.select(message.sender_name))

    return render_template(
        'message_id.html',
        title=message.title,
        user=user,
        message=message,
        sender=sender
    )

@APP.route('/message/<string:message_id>/reply')
@is_logged_in
def message_reply(message_id):
    user = current_user()

    if len(message_id) > Model.TEXT_MAX_LEN:
        flash('Bad message ID', 'alert-danger')
        return redirect('/inbox')

    message = Message.select(message_id)
    if not message:
        flash("Message doesn't exist", 'alert-danger')
        return redirect('/inbox')
    elif message.recipient_name != user.username:
        flash("Can't view messages from other users", 'alert-danger')
        return redirect('/inbox')

    return redirect('/compose?title={}&recipient={}'.format(
        'Re: {}'.format(message.title),
        message.sender_name
    ))

@APP.route('/message/<string:message_id>/delete')
@is_logged_in
def message_delete(message_id):
    user = current_user()

    if len(message_id) > Model.TEXT_MAX_LEN:
        flash('Bad message ID', 'alert-danger')
        return redirect('/inbox')

    message = Message.select(message_id)
    if not message:
        flash("Message doesn't exist", 'alert-danger')
    elif message.recipient_name != user.username:
        flash("Can't delete messages from other users", 'alert-danger')
    else:
        Message.delete(message.id)
        flash('Message successfully deleted', 'alert-success')

    return redirect('/inbox')

@APP.route('/admin')
@is_admin
def admin():
    user = current_user()

    return render_template(
        'admin.html',
        title='Administration',
        user=user,
        users=User.all()
    )

@APP.route('/user/<string:username>', methods=['GET', 'POST'])
@is_admin
def user_id(username):
    user = current_user()

    if len(username) > Model.TEXT_MAX_LEN:
        flash('Bad username', 'alert-danger')
        return redirect('/admin')

    otheruser = User.select(username)
    if not otheruser:
        flash("User doesn't exist", 'alert-danger')
        return redirect('/admin')

    # handle incoming form
    if request.method == 'POST':
        # retrieve form data
        args = {
            'username': request.form.get('username', type=str),
            'password': request.form.get('password', type=str),
            'active': request.form.get('active', type=bool),
            'admin': request.form.get('admin', type=bool),
        }

        # check if post username matches route
        if args['username'] != username:
            flash('Malformed request', 'alert-danger')
            return redirect('/admin')
        # prevent self corruption
        elif args['username'] == user.username:
            flash("Can't edit yourself !", 'alert-danger')
            return redirect('/admin')

        # create update dict
        update_dict = {
            'active': True if args['active'] else False,
            'admin': True if args['admin'] else False
        }
        if args['password']:
            update_dict['password'] = hash_pw(args['password'])

        # patch user
        User.update(args['username'], update_dict)
        Session.terminate_user(args['username'])

        flash('User successfully updated', 'alert-success')
        return redirect('/admin')

    return render_template(
        'user_id.html',
        title="Manager user '{}'".format(username),
        user=user,
        otheruser=otheruser
    )

@APP.route('/user/<string:username>/delete')
@is_admin
def user_delete(username):
    user = current_user()

    if len(username) > Model.TEXT_MAX_LEN:
        flash('Bad username', 'alert-danger')
        return redirect('/admin')

    otheruser = User.select(username)
    if not otheruser:
        flash("User doesn't exist", 'alert-danger')
        return redirect('/admin')

    if username == user.username:
        flash("Can't delete yourself !", 'alert-danger')
        return redirect('/admin')

    User.delete(username)
    flash('User successfully deleted', 'alert-success')
    return redirect('/admin')

@APP.route('/userAdd', methods=['GET', 'POST'])
@is_admin
def user_add():
    user = current_user()

    # handle incoming form
    if request.method == 'POST':
        # retrieve form data
        args = {
            'firstname': request.form.get('firstname', type=str),
            'lastname': request.form.get('lastname', type=str),
            'username': request.form.get('username', type=str),
            'password': request.form.get('password', type=str),
            'password_confirm': request.form.get('password_confirm', type=str)
        }

        # check for valid data and no user conflicts
        if any(x == None for x in args.values()):
            flash('All fields are required', 'alert-danger')
        elif any(len(x) > Model.TEXT_MAX_LEN for x in args.values()):
            flash(
                'Fields may not exceed {} characters'.format(Model.TEXT_MAX_LEN),
                'alert-danger'
            )
        elif args['password'] != args['password_confirm']:
            flash("Passwords don't match", 'alert-danger')
        elif User.find(args['username']):
            flash('Username is already used', 'alert-danger')
        else:
            # create new account and redirect to login page
            User.insert(
                False,
                args['firstname'], args['lastname'],
                args['username'], hash_pw(args['password'])
            )
            flash('Account created successfully', 'alert-success')
            return redirect('/admin')

    return render_template(
        'user_add.html',
        title='Add new user',
        user=user
    )

@APP.route('/changePassword', methods=['GET', 'POST'])
@is_logged_in
def change_password():
    user = current_user()

    # handle incoming form
    if request.method == 'POST':
        # retrieve form data
        args = {
            'newPassword': request.form.get('newPassword', type=str),
            'repeatPassword': request.form.get('repeatPassword', type=str),
            'currentPassword': request.form.get('currentPassword', type=str),
        }

        # check for valid data
        if any(x == None for x in args.values()):
            flash('All fields are required', 'alert-danger')
        elif any(len(x) > Model.TEXT_MAX_LEN for x in args.values()):
            flash(
                'Fields may not exceed {} characters'.format(Model.TEXT_MAX_LEN),
                'alert-danger'
            )
        elif args['newPassword'] != args['repeatPassword']:
            flash("New passwords don't match", 'alert-danger')
        elif args['newPassword'] == args['currentPassword']:
            flash('New password is the same as the current one', 'alert-danger')
        elif not check_pw(args['currentPassword'], user.password):
            flash('Current password is incorrect', 'alert-danger')
        else:
            User.change_pass(user.username, args['newPassword'])

            flash('Password successfully changed', 'alert-success')
            return logout(False)

    return render_template(
        'changePassword.html',
        title='Change password',
        user=user
    )

@APP.route('/login', methods=['GET', 'POST'])
def login():
    # handle incoming form
    if request.method == 'POST':
        # retrieve form data
        args = {
            'username': request.form.get('username', type=str),
            'password': request.form.get('password', type=str),
        }

        # get matching user
        user = User.select(args['username'])

        # check for valid data and no user conflicts
        if any(x == None for x in args.values()):
            flash('All fields are required', 'alert-danger')
        elif any(len(x) > Model.TEXT_MAX_LEN for x in args.values()):
            flash(
                'Fields may not exceed {} characters'.format(Model.TEXT_MAX_LEN),
                'alert-danger'
            )
        elif not (user and check_pw(args['password'], user.password)):
            flash('Bad credentials', 'alert-danger')
        elif not user.active:
            flash('Account disabled, please contact an administrator', 'alert-danger')
        else:
            # generate new session
            expiry = get_current_timestamp()
            session_id = gen_rand_string()
            Session.insert(
                session_id=session_id,
                username=user.username,
                expiry=expiry,
                ip=request.remote_addr,
                user_agent=request.user_agent.string
            )

            # set cookie in response and redirect to inbox
            res = make_response(redirect('/inbox'))
            # TODO secure=True
            res.set_cookie(
                key='auth',
                value=jwt_encode({'session': session_id, 'exp': expiry}),
                expires=expiry,
                samesite='Strict',
            )
            flash('Successfully logged in', 'alert-success')
            return res

    return render_template(
        'login.html',
        title='Log in'
    )

@APP.route('/logout')
@is_logged_in
def logout(do_flash=True):
    # delete session
    Session.delete(get_current_jwt()['session'])

    # force cookie expiry on client side
    res = make_response(redirect('/login'))
    res.set_cookie('auth', '', expires=0)

    if do_flash:
        flash('Successfully logged out', 'alert-success')

    return res

@APP.route('/signup', methods=['GET', 'POST'])
def signup():
    # handle incoming form
    if request.method == 'POST':
        # retrieve form data
        args = {
            'firstname': request.form.get('firstname', type=str),
            'lastname': request.form.get('lastname', type=str),
            'username': request.form.get('username', type=str),
            'password': request.form.get('password', type=str),
            'password_confirm': request.form.get('password_confirm', type=str)
        }

        # check for valid data and no user conflicts
        if any(x == None for x in args.values()):
            flash('All fields are required', 'alert-danger')
        elif any(len(x) > Model.TEXT_MAX_LEN for x in args.values()):
            flash(
                'Fields may not exceed {} characters'.format(Model.TEXT_MAX_LEN),
                'alert-danger'
            )
        elif args['password'] != args['password_confirm']:
            flash("Passwords don't match", 'alert-danger')
        elif User.find(args['username']):
            flash('Username is already used', 'alert-danger')
        else:
            # create new account and redirect to login page
            User.insert(
                False,
                args['firstname'], args['lastname'],
                args['username'], hash_pw(args['password'])
            )
            flash('Account created successfully', 'alert-success')
            return redirect('/login')

    return render_template(
        'signup.html',
        title='Create an account'
    )
