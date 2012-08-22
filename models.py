from datetime import datetime, timedelta

OLD_DAYS = timedelta(21)
OCCUPIED_DAYS = timedelta(2)

from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.lastuser.sqlalchemy import UserBase

from app import app

__all__ = ['db', 'User', 'Room']


db = SQLAlchemy(app)

class ROOM_TYPES:
    # Trying a trick with primes...
    PG = 2
    BHK1 = 3
    BHK2 = 5
    BHK3 = 7
    STUDIO = 11
    OTHERS = 13

class ROOM_PREF:
    FAMILY = 2
    MALE = 3
    FEMALE = 5
    STUDENTS = 7
    OTHERS = 11

class COMMENTSTATUS:
    PUBLIC = 0
    SCREENED = 1
    HIDDEN = 2
    SPAM = 3
    DELETED = 4  # For when there are children to be preserved

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

class CommentSpace(BaseMixin, db.Model):
    __tablename__ = 'commentspace'
    count = db.Column(db.Integer, default=0, nullable=False)

    def __init__(self, **kwargs):
        super(CommentSpace, self).__init__(**kwargs)
        self.count = 0


class Comment(BaseMixin, db.Model):
    __tablename__ = 'comment'
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    user = db.relationship(User, primaryjoin=user_id == User.id,
        backref=db.backref('comments', cascade="all"))
    commentspace_id = db.Column(db.Integer, db.ForeignKey('commentspace.id'), nullable=False)
    commentspace = db.relationship(CommentSpace, primaryjoin=commentspace_id == CommentSpace.id,
        backref=db.backref('comments', cascade="all, delete-orphan"))

    parent_id = db.Column(db.Integer, db.ForeignKey('comment.id'), nullable=True)
    children = db.relationship("Comment", backref=db.backref("parent", remote_side="Comment.id"))

    message = db.Column(db.Text, nullable=False)

    status = db.Column(db.Integer, default=0, nullable=False)

    def delete(self):
        """
        Delete this comment.
        """
        if len(self.children) > 0:
            self.status = COMMENTSTATUS.DELETED
            self.user = None
            self.message = ''
        else:
            if self.parent and self.parent.is_deleted:
                # If the parent is deleted, ask it to reconsider removing itself
                parent = self.parent
                parent.children.remove(self)
                db.session.delete(self)
                parent.delete()
            else:
                db.session.delete(self)

    @property
    def is_deleted(self):
        return self.status == COMMENTSTATUS.DELETED

    def sorted_children(self):
        return sorted(self.children, key=lambda child: child.votes.count)

class Room(BaseMixin, db.Model):
    # FIXME: Rooms is a REALLY BAD NAME!  It should be ads or posts or ...
    __tablename__ = 'room'
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship(User, primaryjoin=user_id == User.id,
                    backref=db.backref('rooms', cascade="all, delete-orphan"))

    address = db.Column(db.Text, default=u'', nullable=False) # Without city
    city = db.Column(db.Text, default=u'', nullable=False) # Can reduce query time for distances
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    radius = db.Column(db.Float, default=0, nullable=False) # ROI

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

    comments_id = db.Column(db.Integer, db.ForeignKey('commentspace.id'), nullable=False)
    comments = db.relationship(CommentSpace, uselist=False)

    def __init__(self, **kwargs):
        super(Room, self).__init__(**kwargs)
        self.occupieds = OccupiedSpace()
        self.comments = CommentSpace()


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
        haversine = 6371 * f.acos(
                            f.cos(f.radians(lat1)) * f.cos(f.radians(lat2)) *
                                f.cos( f.radians(lng2) - f.radians(lng1) ) +
                            f.sin(f.radians(lat1)) * f.sin(f.radians(lat2))
                            )
        return haversine

    @classmethod
    def coords(cls):
        return cls.latitude, cls.longitude

    @staticmethod
    def search_rooms(room):
        """ Search for rooms/ads that match criteria

            - Within the Radius of interest
            - Toggled is_available attribute
            - Room prefs match
            - Room type matches
            - Room rent in +/- 25% range?
            - Ignore available from, for now ...

        """
        coords = room.latitude, room.longitude
        f = db.func
        now = datetime.strptime(datetime.now().strftime("%Y %m %d %H %M %S"), "%Y %m %d %H %M %S") # remove microseconds

        t = Room.distance_subquery(coords, Room.radius)
        r_ = db.session.query(Room, t.c.distance).filter(Room.is_available != room.is_available)
        r_ = r_.filter(Room.dead==False).filter(Room.created_at > now-OLD_DAYS)
        r_ = r_.filter(f.not_(Room.occupieds.has(now - OCCUPIED_DAYS < Occupied.created_at)))
        r_ = r_.order_by(t.c.distance).order_by(db.desc('created_at'))

        if room.room_rent:
            r_ = r_.filter(room.room_rent * 0.75 < Room.room_rent < room.room_rent * 1.25).order_by('room_rent')
        if room.is_available: # ad poster is looking for a person...
            r_ = r_.filter(f.mod(room.room_pref, Room.room_pref) == 0)
            r_ = r_.filter(f.mod(Room.room_type, room.room_type) == 0)
            rooms_distance = r_.filter(t.c.distance <= Room.radius, Room.id == t.c.id).all()
        else: # ad poster is looking for a room...
            r_ = r_.filter(f.mod(Room.room_pref, room.room_pref) == 0)
            r_ = r_.filter(f.mod(room.room_type, Room.room_type) == 0)
            rooms_distance = r_.filter(t.c.distance <= room.radius, Room.id == t.c.id).all()
        return rooms_distance
