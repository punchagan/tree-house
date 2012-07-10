# -*- coding: utf-8 -*-

# Standard libary imports

# Hasgeek imports
from flask import render_template, flash, redirect, url_for
from flask.ext.lastuser import LastUser
from flask.ext.lastuser.sqlalchemy import UserManager
from coaster.views import get_next_url

# Local imports
from app import app
from forms import RoomForm
from models import db, User

lastuser = LastUser(app)
lastuser.init_usermanager(UserManager(db, User))

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


@app.route('/new', methods=['GET', 'POST'])
# FIXME: enforce login requirements!
def post_ad():
    form = RoomForm()
    if form.validate_on_submit():
        # FIXME: Update the db and change the redirect url?
        return redirect(url_for('show_entries'))
    return render_template('autoform.html', form=form,
                            title="Post a new advertisement",
                            submit="Post ad")

@app.route('/show_entries')
def show_entries():
    return render_template('show_entries.html')
