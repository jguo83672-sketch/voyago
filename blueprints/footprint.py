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


footprint_bp = Blueprint('footprint', __name__)

@footprint_bp.route('/footprints/add', methods=['GET', 'POST'])
@login_required
def add_footprint():
    if request.method == 'POST':
        destination_id = request.form.get('destination_id', type=int)
        visit_date = request.form.get('visit_date')
        note = request.form.get('note')
        rating = request.form.get('rating', type=float)

        # 检查是否已存在相同记录
        existing_footprint = TravelFootprint.query.filter_by(
            user_id=current_user.id,
            destination_id=destination_id,
            visit_date=datetime.strptime(visit_date, '%Y-%m-%d').date()
        ).first()

        if existing_footprint:
            flash('该日期的足迹记录已存在！', 'warning')
            return redirect(url_for('auth.profile'))

        footprint = TravelFootprint(
            user_id=current_user.id,
            destination_id=destination_id,
            visit_date=datetime.strptime(visit_date, '%Y-%m-%d').date(),
            note=note,
            rating=rating
        )

        # 保存经纬度
        latitude = request.form.get('latitude')
        longitude = request.form.get('longitude')
        if latitude and longitude:
            footprint.latitude = float(latitude)
            footprint.longitude = float(longitude)

        db.session.add(footprint)
        db.session.commit()

        flash('足迹添加成功！', 'success')
        return redirect(url_for('auth.profile'))

    destinations = Destination.query.all()
    return render_template('add_footprint.html', destinations=destinations)

@footprint_bp.route('/footprint/<int:id>/delete', methods=['POST'])
@login_required
def delete_footprint(id):
    footprint = TravelFootprint.query.get_or_404(id)
    if footprint.user_id != current_user.id:
        flash('您没有权限删除此足迹！', 'danger')
        return redirect(url_for('auth.profile'))

    db.session.delete(footprint)
    db.session.commit()
    flash('足迹已删除', 'success')
    return redirect(url_for('auth.profile'))

@footprint_bp.route('/footprint/<int:id>/edit', methods=['GET', 'POST'])
@footprint_bp.route('/edit-footprint/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_footprint(id):
    """编辑足迹"""
    footprint = TravelFootprint.query.get_or_404(id)

    if footprint.user_id != current_user.id:
        flash('您没有权限编辑此足迹！', 'danger')
        return redirect(url_for('auth.profile'))

    if request.method == 'POST':
        footprint.destination_id = request.form.get('destination_id', type=int)
        footprint.visit_date = datetime.strptime(request.form.get('visit_date'), '%Y-%m-%d').date()
        footprint.note = request.form.get('note')
        footprint.rating = request.form.get('rating', type=float)

        db.session.commit()
        flash('足迹更新成功！', 'success')
        return redirect(url_for('auth.profile'))

    destinations = Destination.query.all()
    return render_template('edit_footprint.html', footprint=footprint, destinations=destinations)
