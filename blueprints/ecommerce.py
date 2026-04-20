from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from datetime import datetime
import json
import uuid
import traceback
from app import db, app
from models import (
    User, Destination, Itinerary, ItineraryDay, Guide, Comment, Comment2,
    Favorite, Favorite2, Community, CommunityMember, CommunityEvent, EventRegistration,
    TravelFootprint, TravelPrep, HotelRecommendation, FlightRecommendation,
    TravelProduct, ProductReview, CartItem, Order, OrderItem
)
from utils import save_upload_file, delete_file
from task_manager import task_manager

from ai_planner import create_planner
from travel_prep import create_prep_service
from ocr_service import recognize_guide_image
from guide_classifier import classify_guide, suggest_destination, suggest_guide_title


ecommerce_bp = Blueprint('ecommerce', __name__)

@ecommerce_bp.route('/travel-shop')
def travel_shop():
    """旅行用品商店"""
    page = request.args.get('page', 1, type=int)
    category = request.args.get('category')
    sort = request.args.get('sort', 'default')

    query = TravelProduct.query.filter_by(is_available=True)

    if category:
        query = query.filter_by(category=category)

    # 排序
    if sort == 'sales':
        query = query.order_by(TravelProduct.sales_count.desc())
    elif sort == 'price_asc':
        query = query.order_by(TravelProduct.price.asc())
    elif sort == 'price_desc':
        query = query.order_by(TravelProduct.price.desc())
    elif sort == 'rating':
        query = query.order_by(TravelProduct.rating.desc())
    else:
        query = query.order_by(TravelProduct.created_at.desc())

    products = query.paginate(page=page, per_page=12, error_out=False)
    categories = db.session.query(TravelProduct.category.distinct()).all()

    # 精选商品
    featured_products = TravelProduct.query.filter_by(
        is_featured=True,
        is_available=True
    ).limit(3).all()

    return render_template('travel_shop.html',
                         products=products,
                         categories=categories,
                         current_category=category,
                         current_sort=sort,
                         featured_products=featured_products)

@ecommerce_bp.route('/travel-shop/product/<int:id>')
def product_detail(id):
    """商品详情"""
    product = TravelProduct.query.get_or_404(id)

    # 相关商品
    related_products = TravelProduct.query.filter(
        TravelProduct.category == product.category,
        TravelProduct.id != product.id,
        TravelProduct.is_available == True
    ).limit(4).all()

    # 评价
    reviews = ProductReview.query.filter_by(product_id=id).order_by(
        ProductReview.created_at.desc()
    ).limit(10).all()

    return render_template('product_detail.html',
                         product=product,
                         related_products=related_products,
                         reviews=reviews)

@ecommerce_bp.route('/cart')
@login_required
def cart():
    """购物车"""
    cart_items = CartItem.query.filter_by(user_id=current_user.id).all()
    total = sum(item.subtotal for item in cart_items)
    return render_template('cart.html', cart_items=cart_items, total=total)

@ecommerce_bp.route('/cart/add/<int:product_id>', methods=['POST'])
@login_required
def add_to_cart(product_id):
    """添加到购物车"""
    product = TravelProduct.query.get_or_404(product_id)

    if not product.is_available:
        return jsonify({'success': False, 'message': '商品已下架'}), 400

    if product.stock <= 0:
        return jsonify({'success': False, 'message': '库存不足'}), 400

    # 检查是否已在购物车
    existing_item = CartItem.query.filter_by(
        user_id=current_user.id,
        product_id=product_id
    ).first()

    if existing_item:
        existing_item.quantity += 1
    else:
        cart_item = CartItem(
            user_id=current_user.id,
            product_id=product_id,
            quantity=1
        )
        db.session.add(cart_item)

    db.session.commit()

    # 获取购物车数量
    cart_count = CartItem.query.filter_by(user_id=current_user.id).count()

    return jsonify({'success': True, 'message': '已添加到购物车', 'cart_count': cart_count})

@ecommerce_bp.route('/cart/update/<int:item_id>', methods=['POST'])
@login_required
def update_cart_item(item_id):
    """更新购物车"""
    item = CartItem.query.get_or_404(item_id)

    if item.user_id != current_user.id:
        return jsonify({'success': False, 'message': '权限不足'}), 403

    quantity = int(request.form.get('quantity', 1))
    if quantity < 1:
        return jsonify({'success': False, 'message': '数量必须大于0'}), 400

    item.quantity = quantity
    db.session.commit()

    cart_count = CartItem.query.filter_by(user_id=current_user.id).count()
    return jsonify({'success': True, 'cart_count': cart_count})

@ecommerce_bp.route('/cart/remove/<int:item_id>', methods=['POST'])
@login_required
def remove_from_cart(item_id):
    """从购物车移除"""
    item = CartItem.query.get_or_404(item_id)

    if item.user_id != current_user.id:
        return jsonify({'success': False, 'message': '权限不足'}), 403

    db.session.delete(item)
    db.session.commit()

    cart_count = CartItem.query.filter_by(user_id=current_user.id).count()
    return jsonify({'success': True, 'cart_count': cart_count})

@ecommerce_bp.route('/checkout', methods=['GET', 'POST'])
@login_required
def checkout():
    """结账页面"""
    if request.method == 'GET':
        cart_items = CartItem.query.filter_by(user_id=current_user.id).all()

        if not cart_items:
            flash('购物车为空', 'warning')
            return redirect(url_for('ecommerce.travel_shop'))

        total = sum(item.subtotal for item in cart_items)
        shipping_fee = 0 if total >= 200 else 15
        final_total = total + shipping_fee

        return render_template('checkout.html',
                             cart_items=cart_items,
                             total=total,
                             shipping_fee=shipping_fee,
                             final_total=final_total)

    else:
        # POST处理 - 创建订单
        try:
            cart_items = CartItem.query.filter_by(user_id=current_user.id).all()

            if not cart_items:
                return jsonify({'success': False, 'message': '购物车为空'}), 400

            total = sum(item.subtotal for item in cart_items)
            shipping_fee = 0 if total >= 200 else 15
            final_total = total + shipping_fee

            # 生成订单号
            order_number = f"VOY{datetime.now().strftime('%Y%m%d%H%M%S')}{uuid.uuid4().hex[:6].upper()}"

            # 创建订单
            order = Order(
                order_number=order_number,
                user_id=current_user.id,
                recipient_name=request.form.get('recipient_name'),
                recipient_phone=request.form.get('recipient_phone'),
                province=request.form.get('province'),
                city=request.form.get('city'),
                district=request.form.get('district'),
                address=request.form.get('address'),
                postal_code=request.form.get('postal_code'),
                total_amount=total,
                shipping_fee=shipping_fee,
                final_amount=final_total,
                payment_method=request.form.get('payment_method'),
                payment_status='pending',
                status='pending',
                notes=request.form.get('notes', '')
            )
            db.session.add(order)
            db.session.flush()

            # 创建订单项
            for item in cart_items:
                order_item = OrderItem(
                    order_id=order.id,
                    product_id=item.product_id,
                    product_name=item.product.name,
                    product_price=item.product.price,
                    quantity=item.quantity,
                    subtotal=item.subtotal
                )
                db.session.add(order_item)

            # 清空购物车
            CartItem.query.filter_by(user_id=current_user.id).delete()

            db.session.commit()
            flash('订单创建成功！', 'success')
            return jsonify({'success': True, 'order_id': order.id})

        except Exception as e:
            db.session.rollback()
            print(f"[Checkout] Error: {str(e)}")
            return jsonify({'success': False, 'message': str(e)}), 500

@ecommerce_bp.route('/orders')
@login_required
def orders():
    """我的订单"""
    status = request.args.get('status', 'all')
    page = request.args.get('page', 1, type=int)

    query = Order.query.filter_by(user_id=current_user.id)

    if status != 'all':
        query = query.filter_by(status=status)

    orders = query.order_by(Order.created_at.desc()).paginate(
        page=page, per_page=10, error_out=False
    )

    return render_template('orders.html', orders=orders, current_status=status)

@ecommerce_bp.route('/order/<int:id>')
@login_required
def order_detail(id):
    """订单详情"""
    order = Order.query.get_or_404(id)

    if order.user_id != current_user.id:
        flash('您没有权限查看此订单', 'danger')
        return redirect(url_for('ecommerce.orders'))

    return render_template('order_detail.html', order=order)
