# -*- coding: utf-8 -*-

# Standard libary imports
from uuid import uuid4
from datetime import datetime
from hashlib import md5

# Hasgeek imports
from flask import render_template, flash, redirect, url_for, g, request, abort
from flask.ext.lastuser import LastUser
from flask.ext.lastuser.sqlalchemy import UserManager
from coaster.views import get_next_url

# Local imports
from app import app
from forms import (AvailableAdForm, WantedAdForm, ConfirmActionForm,
    CommentForm, DeleteCommentForm, SearchForm)
from models import (db, User, Room, OccupiedSpace, Comment, Occupied, OLD_DAYS,
    OCCUPIED_DAYS)
from utils import get_days_ago, factorize, product
from mailclient import send_email_found_person, send_email_found_room

lastuser = LastUser(app)
lastuser.init_usermanager(UserManager(db, User))

# --- Routes: --------------------------------------------------------------

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

@app.route('/', methods=['GET', 'POST'])
def index():
    form = SearchForm()

    if form.validate_on_submit():
        room = Room()
        form.populate_obj(room)

        # Change room_pref and room_type if they are None
        if not room.room_pref:
            room.room_pref = 0 if room.is_available else 1
        if not room.room_type:
            room.room_type = 1 if room.is_available else 0

        # Search for matching rooms
        rooms_distance = Room.search_rooms(room)
        return render_template('found.html', rooms_distance=rooms_distance)
    return render_template('autoform.html', form=form,
                            title="Search Acco.",
                            submit="Search ad")

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/new/<state>', methods=['GET', 'POST'])
@lastuser.requires_login
def post_ad(state='available'):
    is_available = state == 'available'
    if is_available:
        form = AvailableAdForm()
    else:
        form = WantedAdForm()
    form.starting.flags.is_date = True
    if request.method == 'GET':
        form.email.data = g.user.email
    if form.validate_on_submit():
        room = Room(user=g.user, is_available=is_available)
        if room.is_available:
            form.room_pref.data = product(form.room_pref.data)
        else:
            form.room_type.data = product(form.room_type.data)
        form.populate_obj(room)
        room.urlname = str(uuid4())[:8]
        db.session.add(room)
        db.session.commit()

        # Search for matching rooms
        rooms_distance = Room.search_rooms(room)
        # Send emails to interested users
        for r, distance in rooms_distance:
            if room.is_available: # ad poster is looking for a person
                send_email_found_room(r.user, room, distance)
            else: # ad poster is looking for a room.
                send_email_found_person(r.user, room, distance)

        flash("Your ad has been posted!", category="info")
        return render_template('found.html', room=room, rooms_distance=rooms_distance)
    return render_template('autoform.html', form=form,
                            title="Post a new advertisement",
                            submit="Post ad")

@app.route('/ad/<url>/edit', methods=['GET', 'POST'])
@lastuser.requires_login
def edit_ad(url):
    room = Room.query.filter_by(urlname=url).first()
    if not room and room.user == g.user:
        abort(404)
    if room.dead or get_days_ago(room.created_at) > OLD_DAYS.days:
        abort(404)
    occupied = Occupied.query.filter_by(space=room.occupieds).order_by('created_at').first()
    if occupied and get_days_ago(occupied.created_at) > OCCUPIED_DAYS.days:
        abort(404)
    if room.is_available:
        form = AvailableAdForm()
    else:
        form = WantedAdForm()
    form.starting.flags.is_date = True
    if request.method == 'GET':
        form.process(obj=room)
        if room.is_available:
            form.room_pref.data = factorize(room.room_pref)
        else:
            form.room_type.data = factorize(room.room_type)
        form.email.data = g.user.email
    elif form.validate_on_submit():
        if room.is_available:
            form.room_pref.data = product(form.room_pref.data)
        else:
            form.room_type.data = product(form.room_type.data)
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
    if room.dead or get_days_ago(room.created_at) > OLD_DAYS.days:
        abort(404)
    occupied = Occupied.query.filter_by(space=room.occupieds).order_by('created_at').first()
    if occupied and get_days_ago(occupied.created_at) > OCCUPIED_DAYS.days:
        abort(404)
    # URL is okay. Show the ad.
    comments = Comment.query.filter_by(commentspace=room.comments, parent=None).order_by('created_at').all()
    commentform = CommentForm()
    delcommentform = DeleteCommentForm()
    if request.method == 'POST':
        if request.form.get('form.id') == 'newcomment' and commentform.validate():
            if commentform.edit_id.data:
                comment = Comment.query.get(int(commentform.edit_id.data))
                if comment:
                    if comment.user == g.user:
                        comment.message = commentform.message.data
                        flash("Your comment has been edited", category="info")
                    else:
                        flash("You can only edit your own comments", category="info")
                else:
                    flash("No such comment", category="error")
            else:
                comment = Comment(user=g.user, commentspace=room.comments, message=commentform.message.data)
                if commentform.parent_id.data:
                    parent = Comment.query.get(int(commentform.parent_id.data))
                    if parent and parent.commentspace == room.comments:
                        comment.parent = parent
                room.comments.count += 1
                db.session.add(comment)
                flash("Your comment has been posted", category="success")
            db.session.commit()
            # Redirect despite this being the same page because HTTP 303 is required to not break
            # the browser Back button
            return redirect(url_for('view_ad', url=room.urlname) + "#c" + str(comment.id),
                code=303)
        elif request.form.get('form.id') == 'delcomment' and delcommentform.validate():
            comment = Comment.query.get(int(delcommentform.comment_id.data))
            if comment:
                if comment.user == g.user:
                    comment.delete()
                    room.comments.count -= 1
                    db.session.commit()
                    flash("Your comment was deleted.", category="success")
                else:
                    flash("You did not post that comment.", category="error")
            else:
                flash("No such comment.", category="error")
            return redirect(url_for('view_ad', url=room.urlname), code=303)
    return render_template('room.html', room=room, comments=comments,
                        commentform=commentform, delcommentform=delcommentform)

@app.route('/ad/<url>/taken', methods=['GET', 'POST'])
@lastuser.requires_login
def hide_ad(url):
    room = Room.query.filter_by(urlname=url).first()
    if not room:
        abort(404)
    if room.dead or get_days_ago(room.created_at) > OLD_DAYS.days:
        abort(404)
    occupied = Occupied.query.filter_by(space=room.occupieds).order_by('created_at').first()
    if occupied and get_days_ago(occupied.created_at) > OCCUPIED_DAYS.days:
        abort(404)
    form = ConfirmActionForm()
    if form.validate_on_submit():
        if 'yes' in request.form:
            if room.user == g.user:
                room.dead = True
                db.session.commit()
                flash("Your ghosla has been marked occupied", category="success")
            else:
                room.occupieds.occupied(g.user)
                db.session.commit()
                flash("The ghosla has been marked occupied", category="success")
            return redirect(url_for('index'))
        else:
            return redirect(url_for('view_ad', url=url))
    if room.user == g.user:
        message = u"""Do you really wish to mark your Ghosla '%s, %s' as occupied?
                This will remove all comments as well. This operation is permanent
                and cannot be undone."""
    else:
        message = u"""Are you sure you want to mark '%s, %s' as occupied? Please
               do so, only if you have contacted the ad poster and confirmed."""
    return render_template('confirm_action.html', form=form, title=u"Confirm occupied",
        message=message % (room.address, room.city))

@app.route('/ad/<url>/available', methods=['GET', 'POST'])
@lastuser.requires_login
def unhide_ad(url):
    room = Room.query.filter_by(urlname=url).first()
    if not room:
        abort(404)
    if room.dead or get_days_ago(room.created_at) > OLD_DAYS.days:
        abort(404)
    occupied = Occupied.query.filter_by(space=room.occupieds).order_by('created_at').first()
    if occupied and get_days_ago(occupied.created_at) > OCCUPIED_DAYS.days:
        abort(404)
    form = ConfirmActionForm()
    if form.validate_on_submit():
        if 'yes' in request.form:
            if room.user == g.user:
                room.occupieds = OccupiedSpace()
                db.session.commit()
                flash("Your ghosla has been un-marked as occupied", category="success")
            else:
                abort(403)
            return redirect(url_for('index'))
        else:
            return redirect(url_for('view_ad', url=url))
    if room.user == g.user:
        message = u"""Do you really wish to remove all occupied marks on your Ghosla '%s, %s'?
            Please do this, only if your Ghosla is really unoccupied."""
    return render_template('confirm_action.html', form=form, title=u"Confirm un-occupied",
        message=message % (room.address, room.city))


@app.route('/ad/<url>/delete', methods=['GET', 'POST'])
@lastuser.requires_login
def delete_ad(url):
    room = Room.query.filter_by(urlname=url).first()
    if not room:
        abort(404)
    if not lastuser.has_permission('siteadmin') and room.user != g.user:
        abort(403)
    if room.dead: # We let people delete old ads... no check for age, occupied
        abort(404)
    form = ConfirmActionForm()
    if form.validate_on_submit():
        if 'yes' in request.form:
            if len(room.comments.comments) > 0:
                room.dead = True
            else:
                db.session.delete(room)
                db.session.commit()
            flash("Your ad has been deleted", category="success")
            return redirect(url_for('index'))
        else:
            return redirect(url_for('view_ad', url=url))
    return render_template('confirm_action.html', form=form, title=u"Confirm delete",
        message=u"Do you really wish to delete your ad for '%s, %s'? "
                u"This will remove all comments as well. This operation "
                u"is permanent and cannot be undone." % (room.address, room.city))

@app.route('/ads/user/<user_id>')
@lastuser.requires_login
def user_ads(user_id):
    rooms = Room.query.filter_by(user_id=user_id).order_by(db.desc('created_at')).all()
    # FIXME: Use a different template, later (can be very similar...)
    return render_template('index.html', rooms=rooms)

@app.route('/contact')
def contact():
    return 'Coming soon!'

@app.template_filter('age')
def age(dt):
    suffix = u"ago"
    delta = datetime.now() - dt
    if delta.days == 0:
        # < 1 day
        if delta.seconds < 10:
            return "seconds %s" % suffix
        elif delta.seconds < 60:
            return "%d seconds %s" % (delta.seconds, suffix)
        elif delta.seconds < 120:
            return "a minute %s" % suffix
        elif delta.seconds < 3600:  # < 1 hour
            return "%d minutes %s" % (int(delta.seconds / 60), suffix)
        elif delta.seconds < 7200:  # < 2 hours
            return "an hour %s" % suffix
        else:
            return "%d hours %s" % (int(delta.seconds / 3600), suffix)
    elif delta.days == 1:
        return u"a day %s" % suffix
    else:
        return u"%d days %s" % (delta.days, suffix)

@app.template_filter('gravatar')
def gravatar(email, size=100, style='wavatar'):
    email_hash = md5(email.lower()).hexdigest()
    gravatar_url = "http://www.gravatar.com/avatar/%s?d=%s&s=%d" %(email_hash, style, size)
    return gravatar_url

@app.template_filter('datetimeformat')
def datetime_format(date, output_fmt='%d %b'):
    return date.strftime(output_fmt)
