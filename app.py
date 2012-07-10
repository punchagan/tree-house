# -*- coding: utf-8 -*-

from flask import Flask

# configuration
# FIXME: will later be moved to a settings.py file
SQLALCHEMY_DATABASE_URI = 'sqlite:///test.db'
DEBUG = True
SECRET_KEY = 'development key'
USERNAME = 'admin'
PASSWORD = 'default'
SITE_TITLE = 'Tree House'
#: LastUser server
LASTUSER_SERVER = 'http://muse-amuse.in:7000/'
#: LastUser client id
LASTUSER_CLIENT_ID = 'D946G96jQnmZj9anczo0_Q'
#: LastUser client secret
LASTUSER_CLIENT_SECRET = 'xPFf9WKUQamntJ-kTmj1pAjxlWZMQZSRW-EbrMPSbsLQ'

app = Flask(__name__)

app.config.from_object(__name__)
