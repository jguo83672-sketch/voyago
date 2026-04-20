from app import db
from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    avatar = db.Column(db.String(200), default='default_avatar.png')
    bio = db.Column(db.Text)

    # 扩展用户资料
    real_name = db.Column(db.String(50))
    gender = db.Column(db.String(10))
    birth_date = db.Column(db.Date)
    location = db.Column(db.String(100))
    phone = db.Column(db.String(20))
    hobbies = db.Column(db.Text)
    travel_style = db.Column(db.String(50))
    travel_interests = db.Column(db.String(200))

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    itineraries = db.relationship('Itinerary', backref='author', lazy=True, cascade='all, delete-orphan')
    guides = db.relationship('Guide', backref='author', lazy=True, cascade='all, delete-orphan')
    favorites = db.relationship('Favorite', backref='user', lazy=True, cascade='all, delete-orphan')
    communities = db.relationship('Community', backref='creator', lazy=True, cascade='all, delete-orphan')
    community_memberships = db.relationship('CommunityMember', backref='user', lazy=True, cascade='all, delete-orphan')
    event_registrations = db.relationship('EventRegistration', backref='user', lazy=True, cascade='all, delete-orphan')
    travel_footprints = db.relationship('TravelFootprint', backref='user', lazy=True, cascade='all, delete-orphan')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @property
    def hobbies_list(self):
        return self.hobbies.split(',') if self.hobbies else []

    @property
    def interests_list(self):
        return self.travel_interests.split(',') if self.travel_interests else []

    def __repr__(self):
        return f'<User {self.username}>'

