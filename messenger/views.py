from flask import render_template, request, flash, redirect

from messenger import APP
from messenger.models import User

@APP.route('/')
def index():
    return render_template(
        'index.html'
    )

@APP.route('/inbox')
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
def manageUser():
    # TODO only show if admin
    return render_template(
        'manageUser.html'
    )

@APP.route('/changePassword')
def changePassword():
    # TODO condition si déjà login->changePassword sinon->login
    return render_template(
        'changePassword.html'
    )

@APP.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # TODO process form
        pass

    return render_template(
        'login.html'
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
                args['firstname'], args['lastname'],
                args['username'], args['password']
            )
            flash('Account created successfully', 'alert-success')
            return redirect('/login')

    return render_template(
        'signup.html',
        title='Create an account'
    )
