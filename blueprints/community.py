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


community_bp = Blueprint('community', __name__)

@community_bp.route('/communities')
def communities():
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search')
    destination_id = request.args.get('destination_id', type=int)

    query = Community.query.filter_by(status='active')

    if search:
        query = query.filter(Community.name.contains(search))

    if destination_id:
        query = query.filter_by(destination_id=destination_id)

    communities = query.order_by(Community.member_count.desc()).paginate(
        page=page, per_page=12, error_out=False
    )

    return render_template('communities.html', communities=communities)

@community_bp.route('/community/<int:id>')
def community_detail(id):
    community = Community.query.get_or_404(id)
    events = CommunityEvent.query.filter_by(community_id=id).order_by(
        CommunityEvent.start_time.asc()
    ).limit(6).all()

    is_member = False
    user_role = None
    if current_user.is_authenticated:
        membership = CommunityMember.query.filter_by(
            user_id=current_user.id,
            community_id=id
        ).first()
        if membership:
            is_member = True
            user_role = membership.role

    return render_template('community_detail.html',
                         community=community,
                         events=events,
                         is_member=is_member,
                         user_role=user_role)

@community_bp.route('/create-community', methods=['GET', 'POST'])
@login_required
def create_community():
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        destination_id = request.form.get('destination_id', type=int)
        max_members = request.form.get('max_members', type=int, default=50)
        is_public = request.form.get('is_public') == 'on'

        cover_image = save_upload_file(request.files.get('cover_image'), 'communities')

        community = Community(
            name=name,
            description=description,
            destination_id=destination_id,
            max_members=max_members,
            cover_image=cover_image,
            is_public=is_public,
            creator_id=current_user.id
        )

        db.session.add(community)
        db.session.commit()

        # 创建者自动成为管理员
        member = CommunityMember(
            user_id=current_user.id,
            community_id=community.id,
            role='admin'
        )
        db.session.add(member)
        community.member_count = 1
        db.session.commit()

        flash('社群创建成功！', 'success')
        return redirect(url_for('community.community_detail', id=community.id))

    destinations = Destination.query.all()
    return render_template('create_community.html', destinations=destinations)

@community_bp.route('/community/<int:id>/join', methods=['POST'])
@login_required
def join_community(id):
    community = Community.query.get_or_404(id)

    if community.is_full:
        flash('该社群成员已满，无法加入！', 'warning')
        return redirect(url_for('community.community_detail', id=id))

    existing_member = CommunityMember.query.filter_by(
        user_id=current_user.id,
        community_id=id
    ).first()

    if existing_member:
        flash('您已经是该社群的成员了！', 'info')
        return redirect(url_for('community.community_detail', id=id))

    member = CommunityMember(user_id=current_user.id, community_id=id)
    db.session.add(member)
    community.member_count += 1
    db.session.commit()

    flash('成功加入社群！', 'success')
    return redirect(url_for('community.community_detail', id=id))

@community_bp.route('/community/<int:id>/leave', methods=['POST'])
@login_required
def leave_community(id):
    membership = CommunityMember.query.filter_by(
        user_id=current_user.id,
        community_id=id
    ).first()

    if not membership:
        flash('您未加入该社群！', 'warning')
        return redirect(url_for('community.community_detail', id=id))

    community = Community.query.get(id)

    # 管理员不能退出
    if membership.role == 'admin' and community.member_count > 1:
        flash('管理员不能退出社群！请先转让管理员权限。', 'danger')
        return redirect(url_for('community.community_detail', id=id))

    db.session.delete(membership)
    community.member_count -= 1
    db.session.commit()

    flash('已退出社群！', 'success')
    return redirect(url_for('community.communities'))

@community_bp.route('/community/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_community(id):
    community = Community.query.get_or_404(id)

    # 检查权限
    membership = CommunityMember.query.filter_by(
        user_id=current_user.id,
        community_id=id
    ).first()

    if not membership or membership.role != 'admin':
        flash('您没有权限编辑该社群！', 'danger')
        return redirect(url_for('community.community_detail', id=id))

    if request.method == 'POST':
        community.name = request.form.get('name')
        community.description = request.form.get('description')
        community.destination_id = request.form.get('destination_id', type=int)
        community.max_members = request.form.get('max_members', type=int)
        community.is_public = request.form.get('is_public') == 'on'

        if request.files.get('cover_image'):
            if community.cover_image:
                delete_file(community.cover_image, app.config['UPLOAD_FOLDER'])
            community.cover_image = save_upload_file(request.files.get('cover_image'), 'communities')

        db.session.commit()

        flash('社群更新成功！', 'success')
        return redirect(url_for('community.community_detail', id=id))

    destinations = Destination.query.all()
    return render_template('edit_community.html', community=community, destinations=destinations)

@community_bp.route('/community/<int:community_id>/events')
def community_events(community_id):
    community = Community.query.get_or_404(community_id)
    page = request.args.get('page', 1, type=int)
    status = request.args.get('status', 'all')

    query = CommunityEvent.query.filter_by(community_id=community_id)

    if status != 'all':
        query = query.filter_by(status=status)

    events = query.order_by(CommunityEvent.start_time.desc()).paginate(
        page=page, per_page=10, error_out=False
    )

    return render_template('community_events.html',
                         community=community,
                         events=events,
                         status=status)

@community_bp.route('/event/<int:id>')
def event_detail(id):
    event = CommunityEvent.query.get_or_404(id)
    is_registered = False

    if current_user.is_authenticated:
        registration = EventRegistration.query.filter_by(
            user_id=current_user.id,
            event_id=id,
            status='registered'
        ).first()
        if registration:
            is_registered = True

    registrations = EventRegistration.query.filter_by(
        event_id=id,
        status='registered'
    ).limit(10).all()

    return render_template('event_detail.html',
                         event=event,
                         is_registered=is_registered,
                         registrations=registrations)

@community_bp.route('/community/<int:community_id>/create-event', methods=['GET', 'POST'])
@login_required
def create_event(community_id):
    community = Community.query.get_or_404(community_id)

    # 检查权限
    membership = CommunityMember.query.filter_by(
        user_id=current_user.id,
        community_id=community_id
    ).first()

    if not membership:
        flash('请先加入该社群！', 'warning')
        return redirect(url_for('community.community_detail', id=community_id))

    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        location = request.form.get('location')
        start_time = request.form.get('start_time')
        end_time = request.form.get('end_time')
        max_participants = request.form.get('max_participants', type=int, default=20)

        cover_image = save_upload_file(request.files.get('cover_image'), 'events')

        event = CommunityEvent(
            title=title,
            description=description,
            location=location,
            start_time=datetime.fromisoformat(start_time),
            end_time=datetime.fromisoformat(end_time),
            max_participants=max_participants,
            cover_image=cover_image,
            community_id=community_id
        )

        db.session.add(event)
        db.session.commit()

        flash('活动创建成功！', 'success')
        return redirect(url_for('community.event_detail', id=event.id))

    return render_template('create_event.html', community=community)

@community_bp.route('/event/<int:id>/register', methods=['POST'])
@login_required
def register_event(id):
    event = CommunityEvent.query.get_or_404(id)

    if event.is_full:
        flash('该活动名额已满！', 'warning')
        return redirect(url_for('community.event_detail', id=id))

    if event.is_past:
        flash('该活动已结束，无法报名！', 'warning')
        return redirect(url_for('community.event_detail', id=id))

    existing_registration = EventRegistration.query.filter_by(
        user_id=current_user.id,
        event_id=id
    ).first()

    if existing_registration:
        flash('您已经报名该活动！', 'info')
        return redirect(url_for('community.event_detail', id=id))

    registration = EventRegistration(user_id=current_user.id, event_id=id)
    db.session.add(registration)
    event.participant_count += 1
    db.session.commit()

    flash('报名成功！', 'success')
    return redirect(url_for('community.event_detail', id=id))

@community_bp.route('/event/<int:id>/unregister', methods=['POST'])
@login_required
def unregister_event(id):
    registration = EventRegistration.query.filter_by(
        user_id=current_user.id,
        event_id=id
    ).first()

    if not registration:
        flash('您未报名该活动！', 'warning')
        return redirect(url_for('community.event_detail', id=id))

    event = CommunityEvent.query.get(id)
    event.participant_count -= 1
    db.session.delete(registration)
    db.session.commit()

    flash('已取消报名！', 'success')
    return redirect(url_for('community.event_detail', id=id))

@community_bp.route('/event/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_event(id):
    event = CommunityEvent.query.get_or_404(id)

    # 检查权限（社群管理员或活动创建者）
    membership = CommunityMember.query.filter_by(
        user_id=current_user.id,
        community_id=event.community_id
    ).first()

    if not membership or membership.role not in ['admin', 'moderator']:
        flash('您没有权限编辑该活动！', 'danger')
        return redirect(url_for('community.event_detail', id=id))

    if request.method == 'POST':
        event.title = request.form.get('title')
        event.description = request.form.get('description')
        event.location = request.form.get('location')
        event.start_time = datetime.fromisoformat(request.form.get('start_time'))
        event.end_time = datetime.fromisoformat(request.form.get('end_time'))
        event.max_participants = request.form.get('max_participants', type=int)
        event.status = request.form.get('status')

        if request.files.get('cover_image'):
            if event.cover_image:
                delete_file(event.cover_image, app.config['UPLOAD_FOLDER'])
            event.cover_image = save_upload_file(request.files.get('cover_image'), 'events')

        db.session.commit()

        flash('活动更新成功！', 'success')
        return redirect(url_for('community.event_detail', id=id))

    return render_template('edit_event.html', event=event)
