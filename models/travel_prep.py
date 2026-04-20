from app import db
from datetime import datetime

class TravelPrep(db.Model):
    """旅行准备记录"""
    __tablename__ = 'travel_preps'

    id = db.Column(db.Integer, primary_key=True)
    itinerary_id = db.Column(db.Integer, db.ForeignKey('itineraries.id'), nullable=False)
    check_in_date = db.Column(db.Date, nullable=False)
    check_out_date = db.Column(db.Date, nullable=False)
    guest_count = db.Column(db.Integer, default=1)
    budget = db.Column(db.Float)
    notes = db.Column(db.Text)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    itinerary = db.relationship('Itinerary', backref='travel_prep', uselist=False)
    hotel_recommendations = db.relationship('HotelRecommendation', backref='prep', lazy=True, cascade='all, delete-orphan')
    flight_recommendations = db.relationship('FlightRecommendation', backref='prep', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<TravelPrep for itinerary {self.itinerary_id}>'

class HotelRecommendation(db.Model):
    """酒店推荐记录"""
    __tablename__ = 'hotel_recommendations'

    id = db.Column(db.Integer, primary_key=True)
    prep_id = db.Column(db.Integer, db.ForeignKey('travel_preps.id'), nullable=False)

    hotel_name = db.Column(db.String(200), nullable=False)
    rating = db.Column(db.Float)
    price_per_night = db.Column(db.Float)
    currency = db.Column(db.String(10), default='CNY')
    location = db.Column(db.String(500))
    amenities = db.Column(db.Text)  # JSON格式存储设施列表
    image_url = db.Column(db.String(500))
    booking_url = db.Column(db.String(500))
    source = db.Column(db.String(50))  # 推荐来源

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    @property
    def amenities_list(self):
        import json
        if not self.amenities:
            return []
        try:
            return json.loads(self.amenities)
        except json.JSONDecodeError:
            return []

    def __repr__(self):
        return f'<HotelRecommendation {self.hotel_name}>'

class FlightRecommendation(db.Model):
    """机票推荐记录"""
    __tablename__ = 'flight_recommendations'

    id = db.Column(db.Integer, primary_key=True)
    prep_id = db.Column(db.Integer, db.ForeignKey('travel_preps.id'), nullable=False)

    airline = db.Column(db.String(100), nullable=False)
    flight_number = db.Column(db.String(50))
    departure_city = db.Column(db.String(100), nullable=False)
    arrival_city = db.Column(db.String(100), nullable=False)
    departure_time = db.Column(db.DateTime)
    arrival_time = db.Column(db.DateTime)
    duration = db.Column(db.String(50))  # 如 "2小时30分"
    price = db.Column(db.Float)
    currency = db.Column(db.String(10), default='CNY')
    class_type = db.Column(db.String(20))  # 经济舱、商务舱等
    stops = db.Column(db.Integer, default=0)  # 中转次数
    booking_url = db.Column(db.String(500))
    source = db.Column(db.String(50))

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<FlightRecommendation {self.airline} {self.flight_number}>'

