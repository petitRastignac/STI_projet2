# ---------------------------
#Fichier : decorators.py
#Date : 14.10.2020
#But :
#Remarque :
#------------------------------

import datetime as dt
from functools import wraps

from flask import request, redirect, flash

from messenger.models import Session, User
from messenger.jwt import jwt_decode

def is_logged_in(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # check if session cookie is present
        cookie = request.cookies.get('auth')
        if not cookie:
            flash('You must log in first to access this page.', 'alert-danger')
            return redirect('/login')

        # check if a valid JWT came in the cookie
        payload = jwt_decode(cookie)
        if not payload:
            flash('You must log in first to access this page.', 'alert-danger')
            return redirect('/login')

        # check if the named session exists
        session = Session.select(payload['session'])
        if not session:
            flash('You must log in first to access this page.', 'alert-danger')
            return redirect('/login')

        # check if the session has expired
        if session.expiry <= dt.datetime.now():
            flash('Session expired, please log in again.', 'alert-danger')
            Session.delete(session.id)
            return redirect('/login')

        return f(*args, **kwargs)
    return decorated_function

def is_admin(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # What is GEN ? Baby don't duplicate me, don't duplicate me, oh no

        # check if session cookie is present
        cookie = request.cookies.get('auth')
        if not cookie:
            flash('You must log in first to access this page.', 'alert-danger')
            return redirect('/login')

        # check if a valid JWT came in the cookie
        payload = jwt_decode(cookie)
        if not payload:
            flash('You must log in first to access this page.', 'alert-danger')
            return redirect('/login')

        # check if the named session exists
        session = Session.select(payload['session'])
        if not session:
            flash('You must log in first to access this page.', 'alert-danger')
            return redirect('/login')

        # check if the session has expired
        if session.expiry <= dt.datetime.now():
            flash('Session expired, please log in again.', 'alert-danger')
            Session.delete(session.id)
            return redirect('/login')

        # check if the named session exists
        user = User.select(session.username)
        if not user.admin:
            flash('This resource is currently unavailable.', 'alert-danger')
            return redirect('/inbox')

        return f(*args, **kwargs)
    return decorated_function
