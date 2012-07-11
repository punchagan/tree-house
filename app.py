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
LASTUSER_CLIENT_ID = 't_zvjbdjRJyH1G9iIQI9hA'
#: LastUser client secret
LASTUSER_CLIENT_SECRET = 'Xq5sKFDhQUu8GAmGUF3mqgGNo7l7ZWSm64_gjqi0J2IQ'

app = Flask(__name__)

app.config.from_object(__name__)
