from app import db
from datetime import datetime
from .destination import itinerary_destinations



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

    # 地理坐标
    latitude = db.Column(db.Float)  # 纬度
    longitude = db.Column(db.Float)  # 经度

    # 新增：关联到具体目的地（支持多目的地行程）
    destination_id = db.Column(db.Integer, db.ForeignKey('destinations.id'), nullable=True)

    # 新增：自由输入的目的地名称（不需要关联到现有目的地）
    custom_destination = db.Column(db.String(100))

    itinerary_id = db.Column(db.Integer, db.ForeignKey('itineraries.id'), nullable=False)

    # 关联关系
    destination = db.relationship('Destination', backref='itinerary_days', lazy=True)

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

    @property
    def display_location(self):
        """显示当天所在位置"""
        if self.custom_destination:
            return self.custom_destination
        elif self.destination:
            return self.destination.name
        elif self.latitude and self.longitude:
            return f"({self.latitude:.2f}, {self.longitude:.2f})"
        return "未设置位置"

    def __repr__(self):
        return f'<ItineraryDay Day {self.day_number}>'

