# -*- coding: utf-8 -*-

from flask import Flask

# configuration
# FIXME: will later be moved to a settings.py file
DATABASE = '/tmp/flaskr.db'
DEBUG = True
SECRET_KEY = 'development key'
USERNAME = 'admin'
PASSWORD = 'default'
SITE_TITLE = 'Tree House'

app = Flask(__name__)

app.config.from_object(__name__)
