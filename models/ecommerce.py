from app import db
from datetime import datetime

class TravelProduct(db.Model):
    """旅行用品商品"""
    __tablename__ = 'travel_products'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    category = db.Column(db.String(50))  # 行李箱、洗漱包、一次性用品、转换插头、电话卡等
    subcategory = db.Column(db.String(50))
    brand = db.Column(db.String(100))

    price = db.Column(db.Float, nullable=False)
    original_price = db.Column(db.Float)
    currency = db.Column(db.String(10), default='CNY')
    stock = db.Column(db.Integer, default=100)

    image_url = db.Column(db.String(500))
    images = db.Column(db.Text)  # JSON格式存储多张图片URL
    specifications = db.Column(db.Text)  # JSON格式存储规格参数

    rating = db.Column(db.Float, default=0)
    review_count = db.Column(db.Integer, default=0)
    sales_count = db.Column(db.Integer, default=0)

    is_featured = db.Column(db.Boolean, default=False)  # 是否为精选商品
    is_available = db.Column(db.Boolean, default=True)
    tags = db.Column(db.String(200))

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    @property
    def tags_list(self):
        return self.tags.split(',') if self.tags else []

    @property
    def images_list(self):
        import json
        if not self.images:
            return []
        try:
            return json.loads(self.images)
        except json.JSONDecodeError:
            return []

    @property
    def discount_percent(self):
        if self.original_price and self.original_price > self.price:
            return int((self.original_price - self.price) / self.original_price * 100)
        return 0

    def __repr__(self):
        return f'<TravelProduct {self.name}>'

class ProductReview(db.Model):
    """商品评论"""
    __tablename__ = 'product_reviews'

    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('travel_products.id'), nullable=False)

    rating = db.Column(db.Integer)  # 1-5星
    content = db.Column(db.Text)
    images = db.Column(db.Text)  # JSON格式存储图片URL列表

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    product = db.relationship('TravelProduct', backref='reviews')

    @property
    def images_list(self):
        import json
        if not self.images:
            return []
        try:
            return json.loads(self.images)
        except json.JSONDecodeError:
            return []

    def __repr__(self):
        return f'<ProductReview {self.id}>'

class CartItem(db.Model):
    """购物车商品"""
    __tablename__ = 'cart_items'

    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('travel_products.id'), nullable=False)
    quantity = db.Column(db.Integer, default=1)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    product = db.relationship('TravelProduct')

    @property
    def subtotal(self):
        return self.product.price * self.quantity if self.product else 0

    def __repr__(self):
        return f'<CartItem {self.product_id} x{self.quantity}>'

class Order(db.Model):
    """订单"""
    __tablename__ = 'orders'

    id = db.Column(db.Integer, primary_key=True)
    order_number = db.Column(db.String(50), unique=True, nullable=False)

    recipient_name = db.Column(db.String(100), nullable=False)
    recipient_phone = db.Column(db.String(20), nullable=False)
    province = db.Column(db.String(50))
    city = db.Column(db.String(50))
    district = db.Column(db.String(50))
    address = db.Column(db.String(500), nullable=False)
    postal_code = db.Column(db.String(20))

    total_amount = db.Column(db.Float, nullable=False)
    discount_amount = db.Column(db.Float, default=0)
    shipping_fee = db.Column(db.Float, default=0)
    final_amount = db.Column(db.Float, nullable=False)

    payment_method = db.Column(db.String(20))  # wechat, alipay, credit_card
    payment_status = db.Column(db.String(20), default='pending')  # pending, paid, failed
    payment_time = db.Column(db.DateTime)

    status = db.Column(db.String(20), default='pending')  # pending, paid, shipped, delivered, cancelled
    tracking_number = db.Column(db.String(100))
    shipped_at = db.Column(db.DateTime)
    delivered_at = db.Column(db.DateTime)

    notes = db.Column(db.Text)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    items = db.relationship('OrderItem', backref='order', lazy=True, cascade='all, delete-orphan')

    @property
    def item_count(self):
        return len(self.items)

    def __repr__(self):
        return f'<Order {self.order_number}>'

class OrderItem(db.Model):
    """订单商品项"""
    __tablename__ = 'order_items'

    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('travel_products.id'), nullable=False)

    product_name = db.Column(db.String(200), nullable=False)
    product_image = db.Column(db.String(500))
    price = db.Column(db.Float, nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    subtotal = db.Column(db.Float, nullable=False)

    product = db.relationship('TravelProduct')

    def __repr__(self):
        return f'<OrderItem {self.product_name} x{self.quantity}>'

