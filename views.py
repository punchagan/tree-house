# -*- coding: utf-8 -*-

# Standard libary imports
from uuid import uuid4

# Hasgeek imports
from flask import render_template, flash, redirect, url_for, g, request, abort
from flask.ext.lastuser import LastUser
from flask.ext.lastuser.sqlalchemy import UserManager
from coaster.views import get_next_url

# Local imports
from app import app
from forms import RoomForm, ConfirmActionForm
from models import db, User, Room, OccupiedSpace

lastuser = LastUser(app)
lastuser.init_usermanager(UserManager(db, User))

# --- Routes: --------------------------------------------------------------

@app.route('/')
def index():
    # FIXME: Think about what the index page should be like
    # FIXME: old ads shouldn't be shown
    rooms = Room.query.order_by(db.desc('is_available')).order_by(db.desc('created_at')).filter(Room.dead==False).all()
    return render_template('index.html', rooms=rooms)

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

@app.route('/about')
@lastuser.requires_login
def about():
    return render_template('about.html')

@app.route('/new', methods=['GET', 'POST'])
@lastuser.requires_login
def post_ad():
    form = RoomForm()
    if request.method == 'GET':
        form.email.data = g.user.email
    if form.validate_on_submit():
        room = Room(user=g.user)
        form.populate_obj(room)
        room.urlname = str(uuid4())[:8]
        room.occupieds = OccupiedSpace()
        db.session.add(room)
        db.session.commit()
        return redirect(url_for('view_ad', url=room.urlname))
    return render_template('autoform.html', form=form,
                            title="Post a new advertisement",
                            submit="Post ad")

@app.route('/ad/<url>/edit', methods=['GET', 'POST'])
@lastuser.requires_login
def edit_ad(url):
    room = Room.query.filter_by(urlname=url).first()
    if not room and room.user == g.user:
        abort(404)
    if room.dead: # FIXME: add checks for older than 3 weeks
        # FIXME: put a dead page?
        abort(404)
    form = RoomForm()
    if request.method == 'GET':
        form.process(obj=room)
        form.email.data = g.user.email
        print room.occupieds
    elif form.validate_on_submit():
        form.populate_obj(room)
        db.session.commit()
        return redirect(url_for('view_ad', url=room.urlname))
    return render_template('autoform.html', form=form,
                            title="Edit advertisement",
                            submit="Save")

@app.route('/ad/<url>', methods=['GET', 'POST'])
@lastuser.requires_login
def view_ad(url):
    room = Room.query.filter_by(urlname=url).first()
    if not room:
        abort(404)
    if room.dead: # FIXME: add checks for older than 3 weeks
        # FIXME: put a dead page?
        abort(404)
    # FIXME: Add comment field
    # URL is okay. Show the proposal.
    return render_template('room.html', room=room)

@app.route('/ad/<url>/taken', methods=['GET', 'POST'])
@lastuser.requires_login
def hide_ad(url):
    room = Room.query.filter_by(urlname=url).first()
    if not room:
        abort(404)
    form = ConfirmActionForm()
    if form.validate_on_submit():
        if 'yes' in request.form:
            if room.user == g.user:
                room.dead = True
                db.session.commit()
                flash("Your ghosla has been marked occupied", "info")
            else:
                room.occupieds.occupied(g.user)
                db.session.commit()
                flash("The ghosla has been marked occupied", "info")
            return redirect(url_for('index'))
        else:
            return redirect(url_for('view_ad', url=url))
    if room.user == g.user:
        message = u"""Do you really wish to mark your Ghosla '%s, %s' as occupied?
                This will remove all votes and comments as well. This operation
                is permanent and cannot be undone."""
    else:
        message = u"""Are you sure you want to mark '%s, %s' as occupied? Please
               do so, only if you have contacted the ad poster and confirmed."""
    return render_template('confirm_action.html', form=form, title=u"Confirm occupied",
        message=message % (room.address, room.city))

@app.route('/ad/<url>/delete', methods=['GET', 'POST'])
@lastuser.requires_login
def delete_ad(url):
    room = Room.query.filter_by(urlname=url).first()
    if not room:
        abort(404)
    if not lastuser.has_permission('siteadmin') and room.user != g.user:
        abort(403)
    form = ConfirmActionForm()
    if form.validate_on_submit():
        if 'yes' in request.form:
            db.session.delete(room)
            db.session.commit()
            flash("Your ad has been deleted", "info")
            return redirect(url_for('index'))
        else:
            return redirect(url_for('view_ad', url=url))
    return render_template('confirm_action.html', form=form, title=u"Confirm delete",
        message=u"Do you really wish to delete your ad for '%s, %s'? "
                u"This will remove all votes and comments as well. This operation "
                u"is permanent and cannot be undone." % (room.address, room.city))

@app.route('/distance/<coordinates>')
@lastuser.requires_login
def calculate_distance(coordinates):
    coords = [float(num) for num in coordinates.split(',')]
    drange = 3 # Distance in Kilometers
    t = Room.distance_subquery(coords, drange)
    rooms = db.session.query(Room, t.c.distance).filter(t.c.distance <= drange, Room.id == t.c.id).order_by(t.c.distance).all()
    return 'Found %d room(s)<br/>' %len(rooms) + str(rooms)
