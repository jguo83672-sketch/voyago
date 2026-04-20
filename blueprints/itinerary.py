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


itinerary_bp = Blueprint('itinerary', __name__)

@itinerary_bp.route('/itineraries')
def itineraries():
    page = request.args.get('page', 1, type=int)
    destination_id = request.args.get('destination_id', type=int)

    query = Itinerary.query.filter_by(is_public=True)
    if destination_id:
        query = query.filter(Itinerary.destinations.any(Destination.id == destination_id))

    itineraries = query.order_by(Itinerary.created_at.desc()).paginate(
        page=page, per_page=12, error_out=False
    )
    return render_template('itineraries.html', itineraries=itineraries)

@itinerary_bp.route('/itinerary/<int:id>')
def itinerary_detail(id):
    itinerary = Itinerary.query.get_or_404(id)
    itinerary.view_count += 1
    db.session.commit()
    
    days = ItineraryDay.query.filter_by(itinerary_id=id).order_by(ItineraryDay.day_number).all()
    
    return render_template('itinerary_detail.html', itinerary=itinerary, days=days)

@itinerary_bp.route('/create-itinerary', methods=['GET', 'POST'])
@login_required
def create_itinerary():
    if request.method == 'POST':
        cover_image = None
        if 'cover_image' in request.files:
            file = request.files['cover_image']
            if file.filename:
                cover_image = save_upload_file(file, app.config['UPLOAD_FOLDER'], 'itineraries')

        itinerary = Itinerary(
            title=request.form.get('title'),
            description=request.form.get('description'),
            days=int(request.form.get('days')),
            start_date=datetime.strptime(request.form.get('start_date'), '%Y-%m-%d'),
            end_date=datetime.strptime(request.form.get('end_date'), '%Y-%m-%d'),
            budget=float(request.form.get('budget')) if request.form.get('budget') else None,
            user_id=current_user.id,
            cover_image=cover_image
        )

        db.session.add(itinerary)
        db.session.flush()

        # 处理多目的地
        destination_ids = request.form.getlist('destination_ids')
        if destination_ids:
            for dest_id in destination_ids:
                destination = Destination.query.get(int(dest_id))
                if destination:
                    itinerary.destinations.append(destination)

        # 创建每日行程，支持为每天选择目的地
        for i in range(1, itinerary.days + 1):
            day_title = request.form.get(f'day_{i}_title', f'第{i}天')
            day_description = request.form.get(f'day_{i}_description', '')
            day_activities = request.form.get(f'day_{i}_activities', '')
            day_destination_id = request.form.get(f'day_{i}_destination', type=int)

            itinerary_day = ItineraryDay(
                day_number=i,
                title=day_title,
                description=day_description,
                activities=day_activities,
                itinerary_id=itinerary.id,
                destination_id=day_destination_id
            )
            db.session.add(itinerary_day)

        db.session.commit()
        flash('行程创建成功', 'success')
        return redirect(url_for('itinerary.itinerary_detail', id=itinerary.id))

    destinations = Destination.query.all()
    return render_template('create_itinerary.html', destinations=destinations)

@itinerary_bp.route('/itinerary/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_itinerary(id):
    itinerary = Itinerary.query.get_or_404(id)
    if request.method == 'POST':
        old_image = itinerary.cover_image

        if 'cover_image' in request.files:
            file = request.files['cover_image']
            if file.filename:
                itinerary.cover_image = save_upload_file(file, app.config['UPLOAD_FOLDER'], 'itineraries')
                if old_image:
                    delete_file(old_image, app.config['UPLOAD_FOLDER'])

        itinerary.title = request.form.get('title')
        itinerary.description = request.form.get('description')
        itinerary.days = int(request.form.get('days'))
        itinerary.start_date = datetime.strptime(request.form.get('start_date'), '%Y-%m-%d')
        itinerary.end_date = datetime.strptime(request.form.get('end_date'), '%Y-%m-%d')
        itinerary.budget = float(request.form.get('budget')) if request.form.get('budget') else None

        db.session.commit()
        flash('行程更新成功', 'success')
        return redirect(url_for('itinerary.itinerary_detail', id=itinerary.id))

    return render_template('edit_itinerary.html', itinerary=itinerary)

@itinerary_bp.route('/itinerary/<int:id>/days/update', methods=['POST'])
@login_required
def update_itinerary_days(id):
    """批量更新每日行程"""
    itinerary = Itinerary.query.get_or_404(id)

    # 检查权限
    if itinerary.user_id != current_user.id:
        return jsonify({'success': False, 'message': '权限不足'}), 403

    try:
        data = request.get_json()
        days_data = data.get('days', [])

        for day_data in days_data:
            day_id = day_data.get('day_id')
            day = ItineraryDay.query.get(day_id)

            if day and day.itinerary_id == id:
                day.title = day_data.get('title', day.title)
                day.description = day_data.get('description', day.description)
                day.activities = day_data.get('activities', day.activities)

                # 更新目的地
                destination_id = day_data.get('destination_id')
                if destination_id:
                    day.destination_id = destination_id
                else:
                    day.destination_id = None

        db.session.commit()
        return jsonify({'success': True, 'message': '每日行程更新成功'})

    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

@itinerary_bp.route('/itinerary/<int:id>/delete', methods=['POST'])
@login_required
def delete_itinerary(id):
    itinerary = Itinerary.query.get_or_404(id)
    if itinerary.cover_image:
        delete_file(itinerary.cover_image, app.config['UPLOAD_FOLDER'])
    db.session.delete(itinerary)
    db.session.commit()
    flash('行程已删除', 'success')
    return redirect(url_for('itinerary.itineraries'))

@itinerary_bp.route('/itinerary/<int:id>/comment', methods=['POST'])
@login_required
def add_itinerary_comment(id):
    content = request.form.get('content')
    if content:
        comment = Comment2(
            content=content,
            target_type='itinerary',
            user_id=current_user.id,
            itinerary_id=id
        )
        db.session.add(comment)

        itinerary = Itinerary.query.get(id)
        itinerary.comment_count += 1

        db.session.commit()
        flash('评论成功', 'success')
    else:
        flash('评论内容不能为空', 'danger')

    return redirect(url_for('itinerary.itinerary_detail', id=id))

@itinerary_bp.route('/like/itinerary/<int:id>')
@login_required
def like_itinerary(id):
    existing_like = Favorite2.query.filter_by(
        user_id=current_user.id,
        itinerary_id=id
    ).first()

    if not existing_like:
        new_like = Favorite2(user_id=current_user.id, itinerary_id=id)
        db.session.add(new_like)
        itinerary = Itinerary.query.get(id)
        itinerary.like_count += 1
        db.session.commit()
        return jsonify({'liked': True, 'count': itinerary.like_count})
    else:
        itinerary = Itinerary.query.get(id)
        itinerary.like_count -= 1
        db.session.delete(existing_like)
        db.session.commit()
        return jsonify({'liked': False, 'count': itinerary.like_count})

@itinerary_bp.route('/itinerary/<int:itinerary_id>/prepare', methods=['GET', 'POST'])
@login_required
def itinerary_prepare(itinerary_id):
    """行程准备页面"""
    itinerary = Itinerary.query.get_or_404(itinerary_id)

    if itinerary.user_id != current_user.id:
        flash('您没有权限访问此页面', 'danger')
        return redirect(url_for('itinerary.itineraries'))

    # 获取或创建准备信息
    prep = TravelPrep.query.filter_by(itinerary_id=itinerary_id).first()

    # 设置默认日期
    check_in = prep.check_in if prep else None
    check_out = prep.check_out if prep else None
    destination = itinerary.primary_destination

    if request.method == 'POST':
        # 保存准备信息
        data = request.form

        if not prep:
            prep = TravelPrep(
                itinerary_id=itinerary_id,
                check_in=datetime.strptime(data['check_in'], '%Y-%m-%d') if data.get('check_in') else None,
                check_out=datetime.strptime(data['check_out'], '%Y-%m-%d') if data.get('check_out') else None,
                guests=int(data['guest_count']),
                budget=float(data['budget']) if data.get('budget') else None,
                notes=data.get('notes', '')
            )
            db.session.add(prep)
        else:
            prep.check_in = datetime.strptime(data['check_in'], '%Y-%m-%d') if data.get('check_in') else None
            prep.check_out = datetime.strptime(data['check_out'], '%Y-%m-%d') if data.get('check_out') else None
            prep.guests = int(data['guest_count'])
            prep.budget = float(data['budget']) if data.get('budget') else None
            prep.notes = data.get('notes', '')

        db.session.commit()
        flash('准备信息保存成功！', 'success')
        return redirect(url_for('itinerary.itinerary_prepare', itinerary_id=itinerary_id))

    return render_template('itinerary_prepare.html',
                         itinerary=itinerary,
                         prep=prep,
                         check_in=check_in,
                         check_out=check_out,
                         destination=destination)

@itinerary_bp.route('/itinerary/<int:itinerary_id>/prepare/save', methods=['POST'])
@login_required
def save_itinerary_prep(itinerary_id):
    """保存准备信息（AJAX）"""
    itinerary = Itinerary.query.get_or_404(itinerary_id)

    if itinerary.user_id != current_user.id:
        return jsonify({'success': False, 'message': '权限不足'}), 403

    try:
        data = request.form

        prep = TravelPrep.query.filter_by(itinerary_id=itinerary_id).first()
        if not prep:
            prep = TravelPrep(
                itinerary_id=itinerary_id,
                check_in=datetime.strptime(data['check_in'], '%Y-%m-%d') if data.get('check_in') else None,
                check_out=datetime.strptime(data['check_out'], '%Y-%m-%d') if data.get('check_out') else None,
                guests=int(data['guest_count']),
                budget=float(data['budget']) if data.get('budget') else None,
                notes=data.get('notes', '')
            )
            db.session.add(prep)
        else:
            prep.check_in = datetime.strptime(data['check_in'], '%Y-%m-%d') if data.get('check_in') else None
            prep.check_out = datetime.strptime(data['check_out'], '%Y-%m-%d') if data.get('check_out') else None
            prep.guests = int(data['guest_count'])
            prep.budget = float(data['budget']) if data.get('budget') else None
            prep.notes = data.get('notes', '')

        db.session.commit()
        return jsonify({'success': True, 'message': '保存成功'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

@itinerary_bp.route('/api/itinerary/<int:itinerary_id>/hotels', methods=['GET', 'POST'])
@login_required
def get_hotel_recommendations(itinerary_id):
    """获取酒店推荐"""
    itinerary = Itinerary.query.get_or_404(itinerary_id)

    if itinerary.user_id != current_user.id:
        return jsonify({'success': False, 'message': '权限不足'}), 403

    prep = TravelPrep.query.filter_by(itinerary_id=itinerary_id).first()
    if not prep:
        return jsonify({'success': False, 'message': '请先填写准备信息'}), 400

    prep_service = create_prep_service()

    try:
        if request.method == 'POST':
            # 生成推荐
            data = request.get_json()
            departure_city = data.get('departure_city', '北京')

            destination = itinerary.primary_destination
            if not destination:
                destination = Destination.query.first()

            arrival_city = destination.city if destination else '上海'
            check_in = prep.check_in.strftime('%Y-%m-%d') if prep.check_in else None
            check_out = prep.check_out.strftime('%Y-%m-%d') if prep.check_out else None
            budget = prep.budget
            guests = prep.guests

            hotels = prep_service.get_hotel_recommendations(
                departure_city=departure_city,
                arrival_city=arrival_city,
                check_in=check_in,
                check_out=check_out,
                budget=budget,
                guests=guests
            )

            # 清除旧推荐
            HotelRecommendation.query.filter_by(prep_id=prep.id).delete()

            # 保存新推荐
            for hotel_data in hotels:
                hotel = HotelRecommendation(
                    prep_id=prep.id,
                    hotel_name=hotel_data['name'],
                    rating=hotel_data['rating'],
                    price_per_night=hotel_data['price_per_night'],
                    location=hotel_data['location'],
                    amenities=json.dumps(hotel_data['amenities'], ensure_ascii=False),
                    image_url=hotel_data.get('image'),
                    booking_url=hotel_data.get('booking_url'),
                    source=hotel_data.get('source', 'Voyago')
                )
                db.session.add(hotel)

            db.session.commit()

        return jsonify({'success': True, 'hotels': hotels})

    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@itinerary_bp.route('/api/itinerary/<int:itinerary_id>/flights', methods=['GET', 'POST'])
@login_required
def get_flight_recommendations(itinerary_id):
    """获取机票推荐"""
    itinerary = Itinerary.query.get_or_404(itinerary_id)

    if itinerary.user_id != current_user.id:
        return jsonify({'success': False, 'message': '权限不足'}), 403

    prep = TravelPrep.query.filter_by(itinerary_id=itinerary_id).first()
    if not prep:
        return jsonify({'success': False, 'message': '请先填写准备信息'}), 400

    prep_service = create_prep_service()

    try:
        if request.method == 'POST':
            data = request.get_json()
            departure_city = data.get('departure_city', '北京')
            arrival_city = data.get('arrival_city')
            travel_date = data.get('travel_date')
            budget = data.get('budget')

            if not arrival_city:
                destination = itinerary.primary_destination
                arrival_city = destination.city if destination else '上海'

            flights = prep_service.get_flight_recommendations(
                departure_city=departure_city,
                arrival_city=arrival_city,
                travel_date=travel_date,
                budget=budget
            )

            # 清除旧推荐
            FlightRecommendation.query.filter_by(prep_id=prep.id).delete()

            # 保存新推荐
            for flight_data in flights:
                flight = FlightRecommendation(
                    prep_id=prep.id,
                    airline=flight_data['airline'],
                    flight_number=flight_data['flight_number'],
                    departure_time=flight_data['departure_time'],
                    arrival_time=flight_data['arrival_time'],
                    duration=flight_data['duration'],
                    stops=flight_data['stops'],
                    price=flight_data['price'],
                    booking_url=flight_data.get('booking_url'),
                    source=flight_data.get('source', 'Voyago')
                )
                db.session.add(flight)

            db.session.commit()

        return jsonify({'success': True, 'flights': flights})

    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@itinerary_bp.route('/itinerary/<int:itinerary_id>/day/<int:day_number>')
@login_required
def day_detail(itinerary_id, day_number):
    """每日详细行程页面 - 开启我在...的旅程"""
    itinerary = Itinerary.query.get_or_404(itinerary_id)
    day = ItineraryDay.query.filter_by(itinerary_id=itinerary_id, day_number=day_number).first_or_404()

    # 检查权限
    if itinerary.user_id != current_user.id:
        flash('您没有权限编辑此行程', 'danger')
        return redirect(url_for('itinerary.itinerary_detail', id=itinerary_id))

    # 获取所有可选目的地（行程关联的目的地）
    available_destinations = itinerary.destinations if itinerary.destinations else Destination.query.all()

    return render_template('day_detail.html',
                         itinerary=itinerary,
                         day=day,
                         available_destinations=available_destinations)

@itinerary_bp.route('/itinerary/<int:itinerary_id>/day/<int:day_number>/edit', methods=['POST'])
@login_required
def edit_day_detail(itinerary_id, day_number):
    """编辑每日详细行程"""
    itinerary = Itinerary.query.get_or_404(itinerary_id)
    day = ItineraryDay.query.filter_by(itinerary_id=itinerary_id, day_number=day_number).first_or_404()

    # 检查权限
    if itinerary.user_id != current_user.id:
        return jsonify({'success': False, 'message': '权限不足'}), 403

    try:
        # 更新基本信息
        day.title = request.form.get('title', day.title)
        day.description = request.form.get('description', day.description)

        # 更新自定义目的地名称（自由输入）
        destination_name = request.form.get('destination_name')
        if destination_name is not None:
            day.custom_destination = destination_name if destination_name.strip() else None

        # 更新关联的目的地ID（从现有目的地选择）
        destination_id = request.form.get('destination_id', type=int)
        if destination_id:
            day.destination_id = destination_id

        # 更新地理坐标
        latitude = request.form.get('latitude')
        longitude = request.form.get('longitude')
        if latitude and longitude:
            day.latitude = float(latitude)
            day.longitude = float(longitude)

        # 更新活动（JSON格式）
        activities_json = request.form.get('activities')
        if activities_json:
            day.activities = activities_json

        db.session.commit()

        return jsonify({
            'success': True,
            'message': '保存成功',
            'day': {
                'id': day.id,
                'title': day.title,
                'destination': day.display_location
            }
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

@itinerary_bp.route('/itinerary/<int:itinerary_id>/day/<int:day_number>/activities', methods=['GET', 'POST'])
@login_required
def manage_day_activities(itinerary_id, day_number):
    """管理每日活动"""
    itinerary = Itinerary.query.get_or_404(itinerary_id)
    day = ItineraryDay.query.filter_by(itinerary_id=itinerary_id, day_number=day_number).first_or_404()

    # 检查权限
    if itinerary.user_id != current_user.id:
        return jsonify({'success': False, 'message': '权限不足'}), 403

    if request.method == 'GET':
        # 返回当前活动列表
        return jsonify({
            'success': True,
            'activities': day.activities_list
        })

    elif request.method == 'POST':
        try:
            data = request.get_json()
            activities = data.get('activities', [])

            # 验证活动格式
            validated_activities = []
            for activity in activities:
                validated_activity = {
                    'time': activity.get('time', ''),
                    'activity': activity.get('activity', ''),
                    'location': activity.get('location', ''),
                    'latitude': activity.get('latitude'),
                    'longitude': activity.get('longitude'),
                    'estimated_cost': activity.get('estimated_cost', ''),
                    'notes': activity.get('notes', '')
                }
                validated_activities.append(validated_activity)

            day.activities = json.dumps(validated_activities, ensure_ascii=False)
            db.session.commit()

            return jsonify({
                'success': True,
                'message': '活动保存成功',
                'activities': validated_activities
            })

        except Exception as e:
            db.session.rollback()
            return jsonify({'success': False, 'message': str(e)}), 500
