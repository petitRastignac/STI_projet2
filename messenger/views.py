from flask import render_template, request

from messenger import APP

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
