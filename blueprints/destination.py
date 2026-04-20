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


destination_bp = Blueprint('destination', __name__)

@destination_bp.route('/destinations')
def destinations():
    search = request.args.get('search', '')
    region_type = request.args.get('region_type', 'all')  # all, domestic, international, cruise, weekend, theme
    province = request.args.get('province')  # 境内省份筛选
    continent = request.args.get('continent')  # 大洲筛选
    area = request.args.get('area')  # 地区筛选
    country = request.args.get('country')  # 国家筛选
    sort_by = request.args.get('sort_by', 'rating')  # rating, name

    query = Destination.query

    # 搜索
    if search:
        search_pattern = f'%{search}%'
        query = query.filter(
            (Destination.name.like(search_pattern)) |
            (Destination.description.like(search_pattern)) |
            (Destination.province.like(search_pattern)) |
            (Destination.country.like(search_pattern))
        )

    # 按境内/境外/邮轮/周末/主题乐园筛选
    if region_type != 'all':
        query = query.filter_by(region_type=region_type)

    # 按境内省份筛选（适用于国内游、邮轮、周末近郊、主题乐园）
    if province:
        query = query.filter_by(province=province)

    # 按境外地区筛选
    if continent:
        query = query.filter_by(continent=continent)
    if area:
        query = query.filter_by(area=area)
    if country:
        query = query.filter_by(country=country)

    # 排序
    if sort_by == 'name':
        destinations = query.order_by(Destination.name).paginate(
            page=1, per_page=100, error_out=False
        )
    else:
        destinations = query.order_by(Destination.rating.desc()).paginate(
            page=1, per_page=100, error_out=False
        )

    # 获取筛选条件
    filters = {
        'region_type': region_type,
        'province': province,
        'continent': continent,
        'area': area,
        'country': country,
        'sort_by': sort_by
    }

    return render_template('destinations.html', destinations=destinations, filters=filters)

@destination_bp.route('/destination/<int:id>')
def destination_detail(id):
    destination = Destination.query.get_or_404(id)
    destination.visit_count += 1
    db.session.commit()

    guides = Guide.query.filter_by(destination_id=id, is_published=True).limit(6).all()
    itineraries = Itinerary.query.filter(
        Itinerary.destinations.any(Destination.id == id),
        Itinerary.is_public == True
    ).limit(6).all()

    return render_template('destination_detail.html',
                         destination=destination,
                         guides=guides,
                         itineraries=itineraries)

@destination_bp.route('/create-destination', methods=['GET', 'POST'])
@login_required
def create_destination():
    if request.method == 'POST':
        cover_image = None
        if 'cover_image' in request.files:
            file = request.files['cover_image']
            if file.filename:
                cover_image = save_upload_file(file, app.config['UPLOAD_FOLDER'], 'destinations')

        region_type = request.form.get('region_type', 'domestic')

        destination = Destination(
            name=request.form.get('name'),
            region_type=region_type,
            description=request.form.get('description'),
            cover_image=cover_image,
            rating=float(request.form.get('rating', 0)),
            tags=request.form.get('tags'),
            city=request.form.get('city')
        )

        # 保存经纬度
        latitude = request.form.get('latitude')
        longitude = request.form.get('longitude')
        if latitude and longitude:
            destination.latitude = float(latitude)
            destination.longitude = float(longitude)

        # 根据类型设置字段
        if region_type == 'domestic':
            destination.province = request.form.get('province')
            destination.country = '中国'
            destination.continent = '亚洲'
            destination.area = '东亚'
        else:
            destination.continent = request.form.get('continent')
            destination.area = request.form.get('area')
            destination.country = request.form.get('country')

        db.session.add(destination)
        db.session.commit()

        flash('目的地添加成功', 'success')
        return redirect(url_for('destination.destination_detail', id=destination.id))

    return render_template('create_destination.html')

@destination_bp.route('/destination/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_destination(id):
    destination = Destination.query.get_or_404(id)
    if request.method == 'POST':
        old_image = destination.cover_image

        if 'cover_image' in request.files:
            file = request.files['cover_image']
            if file.filename:
                destination.cover_image = save_upload_file(file, app.config['UPLOAD_FOLDER'], 'destinations')
                if old_image:
                    delete_file(old_image, app.config['UPLOAD_FOLDER'])

        destination.name = request.form.get('name')
        destination.region_type = request.form.get('region_type', destination.region_type)
        destination.description = request.form.get('description')
        destination.rating = float(request.form.get('rating', 0))
        destination.tags = request.form.get('tags')
        destination.city = request.form.get('city')

        # 更新经纬度
        latitude = request.form.get('latitude')
        longitude = request.form.get('longitude')
        if latitude and longitude:
            destination.latitude = float(latitude)
            destination.longitude = float(longitude)

        # 根据类型更新字段
        if destination.region_type == 'domestic':
            destination.province = request.form.get('province')
            destination.country = '中国'
            destination.continent = '亚洲'
            destination.area = '东亚'
        else:
            destination.province = None
            destination.continent = request.form.get('continent')
            destination.area = request.form.get('area')
            destination.country = request.form.get('country')

        db.session.commit()
        flash('目的地更新成功', 'success')
        return redirect(url_for('destination.destination_detail', id=destination.id))

    return render_template('edit_destination.html', destination=destination)

@destination_bp.route('/destination/<int:id>/delete', methods=['POST'])
@login_required
def delete_destination(id):
    destination = Destination.query.get_or_404(id)
    if destination.cover_image:
        delete_file(destination.cover_image, app.config['UPLOAD_FOLDER'])
    db.session.delete(destination)
    db.session.commit()
    flash('目的地已删除', 'success')
    return redirect(url_for('destination.destinations'))

@destination_bp.route('/destination/<int:id>/comment', methods=['POST'])
@login_required
def add_destination_comment(id):
    content = request.form.get('content')
    if content:
        comment = Comment2(
            content=content,
            target_type='destination',
            user_id=current_user.id,
            destination_id=id
        )
        db.session.add(comment)

        destination = Destination.query.get(id)
        destination.comment_count += 1

        db.session.commit()
        flash('评论成功', 'success')
    else:
        flash('评论内容不能为空', 'danger')

    return redirect(url_for('destination.destination_detail', id=id))

@destination_bp.route('/like/destination/<int:id>')
@login_required
def like_destination(id):
    existing_like = Favorite2.query.filter_by(
        user_id=current_user.id,
        destination_id=id
    ).first()

    if not existing_like:
        new_like = Favorite2(user_id=current_user.id, destination_id=id)
        db.session.add(new_like)
        destination = Destination.query.get(id)
        destination.like_count += 1
        db.session.commit()
        return jsonify({'liked': True, 'count': destination.like_count})
    else:
        destination = Destination.query.get(id)
        destination.like_count -= 1
        db.session.delete(existing_like)
        db.session.commit()
        return jsonify({'liked': False, 'count': destination.like_count})
