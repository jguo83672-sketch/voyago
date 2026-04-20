from app import db
from datetime import datetime

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

