from flask.ext.sqlalchemy import SQLAlchemy
from app import app

db = SQLAlchemy(app)

class ROOM_TYPES:
    PG = 0
    BHK1 = 1
    BHK2 = 2
    BHK3 = 3
    STUDIO = 4
    OTHERS = 5

class ROOM_PREF:
    FAMILY = 0
    MALE = 1
    FEMALE = 2
    STUDENTS = 3
    OTHERS = 4

# --- Mixins ------------------------------------------------------------------

class BaseMixin(object):
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=db.func.now(), nullable=False)
    updated_at = db.Column(db.DateTime, default=db.func.now(), onupdate=db.func.now(), nullable=False)

# --- Models ------------------------------------------------------------------

# FIXME: Use lastuser stuff later
class UserBase(BaseMixin, db.Model):
    """
    Base class for user definition.
    """
    __tablename__ = 'user'
    userid = db.Column(db.String(22), unique=True, nullable=False)
    username = db.Column(db.Unicode(80), unique=True, nullable=True)  # Usernames are optional
    fullname = db.Column(db.Unicode(80), default=u'', nullable=False)
    email = db.Column(db.Unicode(80), unique=True, nullable=True)  # We may not get an email address
    # room = db.relationship('Room')

    def __repr__(self):
        return "<User('%s','%s', '%s')>" % (self.userid, self.fullname, self.email)

class Room(BaseMixin, db.Model):
    __tablename__ = 'room'
    user_id = db.Column(db.Integer, db.ForeignKey('user.userid'), nullable=False)
    user = db.relationship(UserBase, primaryjoin=user_id == UserBase.userid,
                           backref=db.backref('room',
                                              cascade="all, delete-orphan"))
    address = db.Column(db.Text, default=u'', nullable=False)
    room_type = db.Column(db.Integer, default=ROOM_TYPES.BHK1, nullable=False)
    room_rent = db.Column(db.Integer, default=0, nullable=False)
    room_pref = db.Column(db.Integer, default=ROOM_PREF.FAMILY, nullable=True)
    available_from = db.Column(db.DateTime, nullable=False)    
