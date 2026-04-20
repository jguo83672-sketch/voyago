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


main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    featured_destinations = Destination.query.order_by(Destination.rating.desc()).limit(6).all()
    popular_guides = Guide.query.filter_by(is_published=True).order_by(Guide.view_count.desc()).limit(6).all()
    latest_itineraries = Itinerary.query.filter_by(is_public=True).order_by(Itinerary.created_at.desc()).limit(6).all()
    return render_template('index.html', 
                         destinations=featured_destinations,
                         guides=popular_guides,
                         itineraries=latest_itineraries)

@main_bp.route('/toggle-favorite/<int:item_type>/<int:item_id>')
@login_required
def toggle_favorite(item_type, item_id):
    existing_favorite = None
    
    if item_type == 'itinerary':
        existing_favorite = Favorite.query.filter_by(
            user_id=current_user.id,
            itinerary_id=item_id
        ).first()
        if not existing_favorite:
            new_favorite = Favorite(user_id=current_user.id, itinerary_id=item_id)
            db.session.add(new_favorite)
            itinerary = Itinerary.query.get(item_id)
            itinerary.like_count += 1
            db.session.commit()
            return jsonify({'favorited': True})
    elif item_type == 'guide':
        existing_favorite = Favorite.query.filter_by(
            user_id=current_user.id,
            guide_id=item_id
        ).first()
        if not existing_favorite:
            new_favorite = Favorite(user_id=current_user.id, guide_id=item_id)
            db.session.add(new_favorite)
            guide = Guide.query.get(item_id)
            guide.like_count += 1
            db.session.commit()
            return jsonify({'favorited': True})
    
    if existing_favorite:
        if item_type == 'itinerary':
            itinerary = Itinerary.query.get(item_id)
            itinerary.like_count -= 1
        elif item_type == 'guide':
            guide = Guide.query.get(item_id)
            guide.like_count -= 1
        db.session.delete(existing_favorite)
        db.session.commit()
        return jsonify({'favorited': False})
    
    return jsonify({'favorited': False})

@main_bp.route('/favorites')
@login_required
def favorites():
    favorite_items = Favorite.query.filter_by(user_id=current_user.id).all()
    return render_template('favorites.html', favorites=favorite_items)

@main_bp.route('/search')
def search():
    query = request.args.get('q', '')
    if not query:
        return redirect(url_for('main.index'))
    
    destinations = Destination.query.filter(
        Destination.name.contains(query) | 
        Destination.country.contains(query)
    ).all()
    
    guides = Guide.query.filter(
        Guide.title.contains(query) | 
        Guide.content.contains(query)
    ).filter_by(is_published=True).all()
    
    itineraries = Itinerary.query.filter(
        Itinerary.title.contains(query) | 
        Itinerary.description.contains(query)
    ).filter_by(is_public=True).all()
    
    return render_template('search.html',
                         query=query,
                         destinations=destinations,
                         guides=guides,
                         itineraries=itineraries)

@main_bp.route('/api/tasks/<task_id>', methods=['GET'])
@login_required
def get_task_status(task_id):
    """获取后台任务状态"""
    task = task_manager.get_task_status(task_id)
    if not task:
        return jsonify({'success': False, 'message': '任务不存在'}), 404
        
    if task['status'] == 'completed':
        return jsonify({'success': True, 'status': 'completed', 'data': task['result']})
    elif task['status'] == 'failed':
        return jsonify({'success': False, 'status': 'failed', 'error': task['error']})
    else:
        return jsonify({'success': True, 'status': task['status']})

@main_bp.app_context_processor
def inject_user_data():
    """为所有模板提供全局数据"""
    user_itineraries = []
    if current_user.is_authenticated:
        user_itineraries = Itinerary.query.filter_by(
            user_id=current_user.id
        ).order_by(Itinerary.created_at.desc()).limit(3).all()

    return {
        'user_itineraries': user_itineraries
    }
