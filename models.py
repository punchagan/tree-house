from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.lastuser.sqlalchemy import UserBase

from app import app

__all__ = ['db', 'User', 'Room']


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

class User(UserBase, db.Model):
    __tablename__ = 'user'
    description = db.Column(db.Text, default=u'', nullable=True)

class OccupiedSpace(BaseMixin, db.Model):
    __tablename__ = 'occupiedspace'
    type = db.Column(db.Integer, nullable=True)
    count = db.Column(db.Integer, default=0, nullable=False)

    def __init__(self, **kwargs):
        super(OccupiedSpace, self).__init__(**kwargs)
        self.count = 0

    def occupied(self, user):
        occupiedob = Occupied.query.filter_by(user=user, space=self).first()
        if not occupiedob:
            occupiedob = Occupied(user=user, space=self)
            self.count += 1
            db.session.add(occupiedob)
        return occupiedob

class Occupied(BaseMixin, db.Model):
    __tablename__ = 'occupied'
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship(User, primaryjoin=user_id == User.id,
        backref=db.backref('occupieds', cascade="all, delete-orphan"))
    space_id = db.Column(db.Integer, db.ForeignKey('occupiedspace.id'), nullable=False)
    space = db.relationship(OccupiedSpace, primaryjoin=space_id == OccupiedSpace.id,
        backref=db.backref('occupieds', cascade="all, delete-orphan"))

    __table_args__ = (db.UniqueConstraint("user_id", "space_id"), {})

class Room(BaseMixin, db.Model):
    __tablename__ = 'room'
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship(User, primaryjoin=user_id == User.id,
                    backref=db.backref('rooms', cascade="all, delete-orphan"))

    address = db.Column(db.Text, default=u'', nullable=False) # Without city
    city = db.Column(db.Text, default=u'', nullable=False) # Can reduce query time for distances
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)

    urlname = db.Column(db.Text, nullable=False)

    starting = db.Column(db.Date, nullable=False) # required/available starting from
    is_available = db.Column(db.Boolean, default=True, nullable=False) # available/required

    room_type = db.Column(db.Integer, default=ROOM_TYPES.BHK1, nullable=False)
    room_rent = db.Column(db.Integer, default=0, nullable=False)
    room_pref = db.Column(db.Integer, default=ROOM_PREF.FAMILY, nullable=True)
    room_description = db.Column(db.Text, default=u'', nullable=False)

    dead = db.Column(db.Boolean, default=False, nullable=False)

    occupieds_id = db.Column(db.Integer, db.ForeignKey('occupiedspace.id'), nullable=False)
    occupieds = db.relationship(OccupiedSpace, uselist=False)

    def __repr__(self):
        return '%(address)s, %(city)s, %(room_type)s, %(latitude)s, %(longitude)s' % self.__dict__

    @staticmethod
    def distance_subquery(coords, drange=5):
        t = db.session.query(Room.id, Room.calculate_haversine(Room.coords(), coords).label('distance')).subquery('t')
        return t

    @staticmethod
    def calculate_haversine(coord1, coord2):
        lat1, lng1 = coord1
        lat2, lng2 = coord2
        f = db.func
        haversine = 3959 * f.acos(
                            f.cos(f.radians(lat1)) * f.cos(f.radians(lat2)) *
                                f.cos( f.radians(lng2) - f.radians(lng1) ) +
                            f.sin(f.radians(lat1)) * f.sin(f.radians(lat2))
                            )
        return haversine

    @classmethod
    def coords(cls):
        return cls.latitude, cls.longitude
