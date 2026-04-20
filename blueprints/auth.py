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


auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        
        if User.query.filter_by(username=username).first():
            flash('用户名已存在', 'danger')
            return redirect(url_for('auth.register'))
        
        if User.query.filter_by(email=email).first():
            flash('邮箱已被注册', 'danger')
            return redirect(url_for('auth.register'))
        
        user = User(username=username, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        
        flash('注册成功，请登录', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('register.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            login_user(user)
            next_page = request.args.get('next')
            flash('登录成功', 'success')
            return redirect(next_page) if next_page else redirect(url_for('main.index'))
        else:
            flash('用户名或密码错误', 'danger')
    
    return render_template('login.html')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('已退出登录', 'info')
    return redirect(url_for('main.index'))

@auth_bp.route('/profile')
@login_required
def profile():
    user_itineraries = Itinerary.query.filter_by(user_id=current_user.id).order_by(Itinerary.created_at.desc()).all()
    user_guides = Guide.query.filter_by(user_id=current_user.id).order_by(Guide.created_at.desc()).all()
    user_communities = CommunityMember.query.filter_by(user_id=current_user.id).all()
    user_events = EventRegistration.query.filter_by(
        user_id=current_user.id,
        status='registered'
    ).join(CommunityEvent).order_by(CommunityEvent.start_time.asc()).all()

    user_footprints = TravelFootprint.query.filter_by(user_id=current_user.id).order_by(
        TravelFootprint.visit_date.desc()
    ).all()

    return render_template('profile.html',
                         itineraries=user_itineraries,
                         guides=user_guides,
                         communities=[m.community for m in user_communities],
                         events=[r.event for r in user_events],
                         footprints=user_footprints)

@auth_bp.route('/profile/edit', methods=['GET', 'POST'])
@login_required
def edit_profile():
    if request.method == 'POST':
        # 基本信息
        current_user.avatar = save_upload_file(request.files.get('avatar'), 'avatars', current_user.avatar)
        current_user.bio = request.form.get('bio')
        current_user.real_name = request.form.get('real_name')
        current_user.gender = request.form.get('gender')
        current_user.location = request.form.get('location')
        current_user.phone = request.form.get('phone')

        # 日期处理
        birth_date = request.form.get('birth_date')
        if birth_date:
            current_user.birth_date = datetime.strptime(birth_date, '%Y-%m-%d').date()

        # 兴趣爱好
        current_user.hobbies = request.form.get('hobbies')
        current_user.travel_style = request.form.get('travel_style')
        current_user.travel_interests = request.form.get('travel_interests')

        db.session.commit()

        flash('个人资料更新成功！', 'success')
        return redirect(url_for('auth.profile'))

    return render_template('edit_profile.html')
