from app import db
from datetime import datetime

itinerary_destinations = db.Table('itinerary_destinations',
    db.Column('itinerary_id', db.Integer, db.ForeignKey('itineraries.id'), primary_key=True),
    db.Column('destination_id', db.Integer, db.ForeignKey('destinations.id'), primary_key=True),
    db.Column('visit_order', db.Integer, default=0)  # 访问顺序
)

class Destination(db.Model):
    __tablename__ = 'destinations'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)

    # 地理分类
    region_type = db.Column(db.String(20), nullable=False, default='domestic')  # domestic(境内), international(境外), cruise(邮轮), weekend(周末近郊), theme(主题乐园)

    # 境内字段
    province = db.Column(db.String(50))  # 省份(境内)

    # 境外字段
    continent = db.Column(db.String(50))  # 大洲(境外)
    area = db.Column(db.String(50))  # 地区(境外),如东南亚、西欧等
    country = db.Column(db.String(100))  # 国家
    city = db.Column(db.String(100))

    # 地理坐标
    latitude = db.Column(db.Float)  # 纬度
    longitude = db.Column(db.Float)  # 经度

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

    @property
    def display_location(self):
        """显示完整地址"""
        if self.region_type == 'domestic':
            return f"{self.province}" if self.province else self.name
        elif self.region_type == 'cruise':
            return f"{self.province} - {self.name}" if self.province else self.name
        elif self.region_type == 'weekend':
            return f"{self.province} - {self.name}" if self.province else self.name
        elif self.region_type == 'theme':
            return f"{self.province} - {self.name}" if self.province else self.name
        else:
            parts = [self.continent, self.area, self.country]
            parts = [p for p in parts if p]
            return " - ".join(parts) if parts else self.name

    def __repr__(self):
        return f'<Destination {self.name}>'

