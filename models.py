from app import db, login_manager
from flask_login import UserMixin
from datetime import datetime
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

itinerary_destinations = db.Table('itinerary_destinations',
    db.Column('itinerary_id', db.Integer, db.ForeignKey('itineraries.id'), primary_key=True),
    db.Column('destination_id', db.Integer, db.ForeignKey('destinations.id'), primary_key=True)
)

class Destination(db.Model):
    __tablename__ = 'destinations'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    country = db.Column(db.String(100), nullable=False)
    city = db.Column(db.String(100))
    description = db.Column(db.Text)
    cover_image = db.Column(db.String(200))
    rating = db.Column(db.Float, default=0)
    visit_count = db.Column(db.Integer, default=0)
    like_count = db.Column(db.Integer, default=0)
    comment_count = db.Column(db.Integer, default=0)
    tags = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow)

    itineraries = db.relationship('Itinerary', secondary=itinerary_destinations, back_populates='destinations', lazy=True)
    guides = db.relationship('Guide', backref='destination', lazy=True)
    comments = db.relationship('Comment2', backref='destination', lazy=True, cascade='all, delete-orphan')
    favorites = db.relationship('Favorite2', backref='destination', lazy=True, cascade='all, delete-orphan')

    @property
    def tags_list(self):
        return self.tags.split(',') if self.tags else []

    def __repr__(self):
        return f'<Destination {self.name}>'

class Itinerary(db.Model):
    __tablename__ = 'itineraries'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    days = db.Column(db.Integer, nullable=False)
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    budget = db.Column(db.Float)
    cover_image = db.Column(db.String(200))
    is_public = db.Column(db.Boolean, default=True)
    view_count = db.Column(db.Integer, default=0)
    like_count = db.Column(db.Integer, default=0)
    comment_count = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow)

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    destinations = db.relationship('Destination', secondary=itinerary_destinations, back_populates='itineraries', lazy=True)

    days_schedule = db.relationship('ItineraryDay', backref='itinerary', lazy=True, cascade='all, delete-orphan')
    comments = db.relationship('Comment2', backref='itinerary', lazy=True, cascade='all, delete-orphan')
    favorites = db.relationship('Favorite2', backref='itinerary', lazy=True, cascade='all, delete-orphan')

    @property
    def primary_destination(self):
        return self.destinations[0] if self.destinations else None

    @property
    def destination_names(self):
        return ', '.join([d.name for d in self.destinations])

    def __repr__(self):
        return f'<Itinerary {self.title}>'

class ItineraryDay(db.Model):
    __tablename__ = 'itinerary_days'
    
    id = db.Column(db.Integer, primary_key=True)
    day_number = db.Column(db.Integer, nullable=False)
    title = db.Column(db.String(200))
    description = db.Column(db.Text)
    activities = db.Column(db.Text)
    
    itinerary_id = db.Column(db.Integer, db.ForeignKey('itineraries.id'), nullable=False)
    
    @property
    def activities_list(self):
        import json
        if not self.activities or not self.activities.strip():
            return []
        try:
            return json.loads(self.activities)
        except json.JSONDecodeError:
            # 如果解析失败，返回空列表
            return []
    
    def __repr__(self):
        return f'<ItineraryDay Day {self.day_number}>'

class Guide(db.Model):
    __tablename__ = 'guides'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    cover_image = db.Column(db.String(200))
    category = db.Column(db.String(50))
    view_count = db.Column(db.Integer, default=0)
    like_count = db.Column(db.Integer, default=0)
    comment_count = db.Column(db.Integer, default=0)
    is_published = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    destination_id = db.Column(db.Integer, db.ForeignKey('destinations.id'), nullable=False)
    
    comments = db.relationship('Comment', backref='guide', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Guide {self.title}>'

class Comment(db.Model):
    __tablename__ = 'comments'

    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    guide_id = db.Column(db.Integer, db.ForeignKey('guides.id'), nullable=False)

    user = db.relationship('User', backref='guide_comments')

    def __repr__(self):
        return f'<Comment {self.id}>'

class Comment2(db.Model):
    __tablename__ = 'comments2'

    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    target_type = db.Column(db.String(20), nullable=False)  # 'itinerary' or 'destination'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    itinerary_id = db.Column(db.Integer, db.ForeignKey('itineraries.id'), nullable=True)
    destination_id = db.Column(db.Integer, db.ForeignKey('destinations.id'), nullable=True)

    user = db.relationship('User', backref='comments2')

    def __repr__(self):
        return f'<Comment2 {self.id}>'

class Favorite(db.Model):
    __tablename__ = 'favorites'

    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    itinerary_id = db.Column(db.Integer, db.ForeignKey('itineraries.id'), nullable=True)
    guide_id = db.Column(db.Integer, db.ForeignKey('guides.id'), nullable=True)

    def __repr__(self):
        return f'<Favorite {self.id}>'

class Favorite2(db.Model):
    __tablename__ = 'favorites2'

    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    itinerary_id = db.Column(db.Integer, db.ForeignKey('itineraries.id'), nullable=True)
    destination_id = db.Column(db.Integer, db.ForeignKey('destinations.id'), nullable=True)

    def __repr__(self):
        return f'<Favorite2 {self.id}>'


# 社群功能相关模型
class Community(db.Model):
    __tablename__ = 'communities'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    cover_image = db.Column(db.String(200))
    destination_id = db.Column(db.Integer, db.ForeignKey('destinations.id'))
    max_members = db.Column(db.Integer, default=50)
    member_count = db.Column(db.Integer, default=1)
    is_public = db.Column(db.Boolean, default=True)
    status = db.Column(db.String(20), default='active')  # active, inactive, archived

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    creator_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    members = db.relationship('CommunityMember', backref='community', lazy=True, cascade='all, delete-orphan')
    events = db.relationship('CommunityEvent', backref='community', lazy=True, cascade='all, delete-orphan')

    destination = db.relationship('Destination', backref='communities')

    @property
    def is_full(self):
        return self.member_count >= self.max_members

    @property
    def can_join(self):
        return self.is_public and not self.is_full and self.status == 'active'

    def __repr__(self):
        return f'<Community {self.name}>'


class CommunityMember(db.Model):
    __tablename__ = 'community_members'

    id = db.Column(db.Integer, primary_key=True)
    role = db.Column(db.String(20), default='member')  # admin, moderator, member
    status = db.Column(db.String(20), default='active')  # active, inactive
    joined_at = db.Column(db.DateTime, default=datetime.utcnow)

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    community_id = db.Column(db.Integer, db.ForeignKey('communities.id'), nullable=False)

    __table_args__ = (db.UniqueConstraint('user_id', 'community_id', name='unique_user_community'),)

    def __repr__(self):
        return f'<CommunityMember {self.user_id} in {self.community_id}>'


class CommunityEvent(db.Model):
    __tablename__ = 'community_events'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    location = db.Column(db.String(200))
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)
    max_participants = db.Column(db.Integer, default=20)
    participant_count = db.Column(db.Integer, default=0)
    cover_image = db.Column(db.String(200))
    status = db.Column(db.String(20), default='upcoming')  # upcoming, ongoing, completed, cancelled

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    community_id = db.Column(db.Integer, db.ForeignKey('communities.id'), nullable=False)

    registrations = db.relationship('EventRegistration', backref='event', lazy=True, cascade='all, delete-orphan')

    @property
    def is_full(self):
        return self.participant_count >= self.max_participants

    @property
    def is_past(self):
        return datetime.utcnow() > self.end_time

    def __repr__(self):
        return f'<CommunityEvent {self.title}>'


class EventRegistration(db.Model):
    __tablename__ = 'event_registrations'

    id = db.Column(db.Integer, primary_key=True)
    status = db.Column(db.String(20), default='registered')  # registered, cancelled, attended
    note = db.Column(db.Text)
    registered_at = db.Column(db.DateTime, default=datetime.utcnow)

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    event_id = db.Column(db.Integer, db.ForeignKey('community_events.id'), nullable=False)

    __table_args__ = (db.UniqueConstraint('user_id', 'event_id', name='unique_user_event'),)

    def __repr__(self):
        return f'<EventRegistration {self.user_id} for {self.event_id}>'


class TravelFootprint(db.Model):
    __tablename__ = 'travel_footprints'

    id = db.Column(db.Integer, primary_key=True)
    destination_id = db.Column(db.Integer, db.ForeignKey('destinations.id'), nullable=False)
    visit_date = db.Column(db.Date, nullable=False)
    note = db.Column(db.Text)
    photos = db.Column(db.String(500))
    rating = db.Column(db.Float)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    destination = db.relationship('Destination', backref='footprints')

    __table_args__ = (db.UniqueConstraint('user_id', 'destination_id', 'visit_date', name='unique_user_destination_visit'),)

    @property
    def photos_list(self):
        return self.photos.split(',') if self.photos else []

    def __repr__(self):
        return f'<TravelFootprint {self.user_id} visited {self.destination_id}>'
