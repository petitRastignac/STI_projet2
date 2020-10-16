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
@is_logged_in
def index():
    user = current_user()

    return render_template(
        'index.html',
        firstname=user.firstname,
        user=user
    )

@APP.route('/inbox')
@is_logged_in
def inbox():
    return render_template(
        'inbox.html',
        title='Inbox',
        user=current_user()
    )

@APP.route('/newMessage', methods=['GET', 'POST'])
@is_logged_in
def new_message():
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
        'newMessage.html',
        title='New message',
        user=user
    )

@APP.route('/message/<string:message_id>/delete')

@APP.route('/admin')
@is_logged_in
@is_admin
def admin():
    user = current_user()

    return render_template(
        'admin.html',
        title='Administration',
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
            User.update(user.username, {'password': hash_pw(args['newPassword'])})
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
