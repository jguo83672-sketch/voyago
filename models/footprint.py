from app import db
from datetime import datetime

class TravelFootprint(db.Model):
    __tablename__ = 'travel_footprints'

    id = db.Column(db.Integer, primary_key=True)
    destination_id = db.Column(db.Integer, db.ForeignKey('destinations.id'), nullable=False)
    visit_date = db.Column(db.Date, nullable=False)
    note = db.Column(db.Text)
    photos = db.Column(db.String(500))
    rating = db.Column(db.Float)

    # 地理坐标
    latitude = db.Column(db.Float)  # 纬度
    longitude = db.Column(db.Float)  # 经度

    created_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    destination = db.relationship('Destination', backref='footprints')

    __table_args__ = (db.UniqueConstraint('user_id', 'destination_id', 'visit_date', name='unique_user_destination_visit'),)

    @property
    def photos_list(self):
        return self.photos.split(',') if self.photos else []

    def __repr__(self):
        return f'<TravelFootprint {self.user_id} visited {self.destination_id}>'

