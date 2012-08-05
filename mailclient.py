# -*- coding: utf-8 -*-

from markdown import markdown
from flask import render_template
from flask.ext.mail import Mail, Message
from app import app

mail = Mail(app)
SITE = app.config['SITE_TITLE']


def send_email_found_room(user, room, distance):
    """ Mail a room found notification to user
    """
    subject = "%s -- Found a room!" %SITE
    msg = Message(subject=subject, recipients=[user.email])
    msg.body = render_template("room_found.md", user=user, room=room)
    msg.html = markdown(msg.body)
    mail.send(msg)

def send_email_found_person(user, room, distance):
    """ Mail a person found notification to user
    #FIXME: room is really person!
    """
    subject = "%s -- Found a prospective tenant!" %SITE
    msg = Message(subject=subject, recipients=[user.email])
    msg.body = render_template("person_found.md", user=user, room=room)
    msg.html = markdown(msg.body)
    mail.send(msg)
