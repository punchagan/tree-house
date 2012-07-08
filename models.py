from flask.ext.sqlalchemy import SQLAlchemy
from app import app

db = SQLAlchemy(app)

# --- Mixins ------------------------------------------------------------------

class BaseMixin(object):
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=db.func.now(), nullable=False)
    updated_at = db.Column(db.DateTime, default=db.func.now(), onupdate=db.func.now(), nullable=False)

# FIXME: Use lastuser stuff later
class UserBase(BaseMixin):
    """
    Base class for user definition.
    """
    __tablename__ = 'user'
    userid = db.Column(db.String(22), unique=True, nullable=False)
    username = db.Column(db.Unicode(80), unique=True, nullable=True)  # Usernames are optional
    fullname = db.Column(db.Unicode(80), default=u'', nullable=False)
    email = db.Column(db.Unicode(80), unique=True, nullable=True)  # We may not get an email address


# --- Models ------------------------------------------------------------------

class User(UserBase, db.Model):
    __tablename__ = 'user'
    description = db.Column(db.Text, default=u'', nullable=False)
