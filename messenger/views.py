import datetime as dt

from flask import render_template, request, flash, redirect, make_response

from messenger import APP
from messenger.models import User, Session
from messenger.security import check_pw, hash_pw, gen_rand_string
from messenger.decorators import is_logged_in, is_admin
from messenger.jwt import jwt_decode, jwt_encode

@APP.route('/')
def index():
    return render_template(
        'index.html'
    )

@APP.route('/inbox')
@is_logged_in
def inbox():
    return render_template(
        'inbox.html'
    )

@APP.route('/new')
def new():
    return render_template(
        'new.html'
    )

@APP.route('/manageUser')
@is_logged_in
@is_admin
def manageUser():
    # TODO only show if admin
    return render_template(
        'manageUser.html'
    )

@APP.route('/changePassword')
def changePassword():
    # TODO condition si déjà login->changePassword sinon->login
    # TODO trouver l'utilisateur depuis les Cookie et changer le mot de passe dans la db
    # handle incoming form
    if request.method == 'POST':
        # retrieve form data
        args = {
            'newPassword': request.form.get('password', type=str),
            'repeatPassword': request.form.get('password', type=str),
            'oldPassword': request.form.get('password', type=str),
        }

        # check for valid data
        if(args['newPassword'] == args['repeatPassword'] and args['newPassword'] != args['oldPassword']):
            flash('Successfully change password', 'alert-success')
            return redirect('/')
        else:
            flash('Change password failled', 'alert-danger')

    return render_template(
        'changePassword.html'
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
        user = User.select(args['username'], False)

        # check for valid data and no user conflicts
        if any(x == None for x in args):
            flash('All fields are required', 'alert-danger')
        elif not (user and check_pw(args['password'], user.password)):
            flash('Bad credentials', 'alert-danger')
        else:
            # generate new session
            expiry = int((
                dt.datetime.now() + Session.SESSION_DURATION
            ).replace(microsecond=0).timestamp())
            session_id = gen_rand_string()
            Session.insert(
                session_id=session_id,
                user_id=user.id,
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
        if any(x == None for x in args):
            flash('All fields are required', 'alert-danger')
        elif args['password'] != args['password_confirm']:
            flash("Passwords don't match", 'alert-danger')
        elif User.find(args['username']): # TODO implement user check
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
