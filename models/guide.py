from app import db
from datetime import datetime

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

