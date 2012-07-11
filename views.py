# -*- coding: utf-8 -*-

# Standard libary imports
import flask.ext.wtf as wtf

# Hasgeek imports
from flask import render_template, flash, redirect, url_for, g, request
from flask.ext.lastuser import LastUser
from flask.ext.lastuser.sqlalchemy import UserManager
from coaster.views import get_next_url

# Local imports
from app import app
from forms import RoomForm
from models import db, User, Room

lastuser = LastUser(app)
lastuser.init_usermanager(UserManager(db, User))

# --- Routes: --------------------------------------------------------------

@app.route('/')
def index():
    # FIXME: Think about what the index page should be like
    return render_template('index.html', title='Tree House')

@app.route('/login')
@lastuser.login_handler
def login():
    return {'scope': 'id email'}


@app.route('/logout')
@lastuser.logout_handler
def logout():
    flash("You are now logged out", category='info')
    return get_next_url()


@app.route('/login/redirect')
@lastuser.auth_handler
def lastuserauth():
    # Save the user object
    db.session.commit()
    return redirect(get_next_url())


@lastuser.auth_error_handler
def lastuser_error(error, error_description=None, error_uri=None):
    if error == 'access_denied':
        flash("You denied the request to login", category='error')
        return redirect(get_next_url())
    return render_template("autherror.html",
        error=error,
        error_description=error_description,
        error_uri=error_uri)

# --- Routes: ads ------------------------------------------------------------

@app.route('/new', methods=['GET', 'POST'])
@lastuser.requires_login
def post_ad():
    form = RoomForm()
    if request.method == 'GET':
        form.email.data = g.user.email
    if form.validate_on_submit():
        room = Room(user=g.user)
        form.populate_obj(room)
        db.session.add(room)
        db.session.commit()
        return redirect(url_for('show_entries'))
    return render_template('autoform.html', form=form,
                            title="Post a new advertisement",
                            submit="Post ad")

@app.route('/show_entries')
@lastuser.requires_login
def show_entries():
    rooms = Room.query.order_by(db.desc('is_available')).order_by(db.desc('created_at')).all()
    return render_template('show_entries.html', rooms=rooms)
