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


ai_tools_bp = Blueprint('ai_tools', __name__)

@ai_tools_bp.route('/ai-planner')
@login_required
def ai_planner_page():
    """AI行程规划页面"""
    destinations = Destination.query.all()
    return render_template('ai_planner.html', destinations=destinations)

@ai_tools_bp.route('/test-ai-api')
@login_required
def test_ai_api_page():
    """AI API测试页面"""
    return render_template('test_ai_api.html')

@ai_tools_bp.route('/api/ai/plan', methods=['POST'])
@login_required
def ai_plan_itinerary():
    """AI规划行程API"""
    import traceback

    try:
        data = request.get_json()

        if not data:
            print("[AI Plan] Error: No JSON data received")
            return jsonify({'success': False, 'message': '请求数据为空'}), 400

        # 获取用户输入
        destination_name = data.get('destination')
        destination_id = data.get('destination_id')
        days = int(data.get('days', 3))
        budget = data.get('budget')
        start_date = data.get('start_date')
        travelers = int(data.get('travelers', 1))
        interests = data.get('interests', [])
        style = data.get('style', '休闲舒适')
        special_needs = data.get('special_needs', '')

        print(f"[AI Plan] Request: destination={destination_name}, days={days}, budget={budget}")

        if not destination_name:
            return jsonify({'success': False, 'message': '请选择目的地'}), 400

        if days < 1 or days > 30:
            return jsonify({'success': False, 'message': '天数必须在1-30天之间'}), 400

        def _plan_task():
            # 创建AI规划器
            print("[AI Plan Task] Creating planner...")
            planner = create_planner()

            # 收集上下文数据
            context_data = {}

            # 收集目的地信息
            print("[AI Plan Task] Collecting destination data...")
            if destination_id:
                destination = Destination.query.get(destination_id)
                if destination:
                    destinations_data = [{
                        'name': destination.name,
                        'country': destination.country,
                        'city': destination.city,
                        'description': destination.description,
                        'rating': destination.rating,
                        'tags': destination.tags
                    }]
                else:
                    destinations_data = []
            else:
                # 根据名称搜索相似目的地
                destinations = Destination.query.filter(
                    Destination.name.contains(destination_name)
                ).limit(3).all()
                destinations_data = [{
                    'name': d.name,
                    'country': d.country,
                    'city': d.city,
                    'description': d.description,
                    'rating': d.rating,
                    'tags': d.tags
                } for d in destinations]

            context_data['destinations'] = planner.collect_destination_data(destinations_data)

            # 收集相关攻略
            print("[AI Plan Task] Collecting guide data...")
            if destination_id:
                guides = Guide.query.filter_by(
                    destination_id=destination_id,
                    is_published=True
                ).limit(5).all()
            else:
                guides = Guide.query.filter_by(is_published=True).limit(5).all()

            guides_data = [{
                'title': g.title,
                'content': g.content,
                'category': g.category,
                'view_count': g.view_count
            } for g in guides]
            context_data['guides'] = planner.collect_guide_data(guides_data)

            # 收集参考行程
            print("[AI Plan Task] Collecting itinerary data...")
            itineraries = Itinerary.query.filter_by(is_public=True).limit(3).all()
            itineraries_data = [{
                'title': i.title,
                'days': i.days,
                'budget': i.budget,
                'description': i.description
            } for i in itineraries]
            context_data['itineraries'] = planner.collect_itinerary_data(itineraries_data)

            # 调用AI规划
            print("[AI Plan Task] Calling AI...")
            result = planner.plan_itinerary(
                destination=destination_name,
                days=days,
                budget=float(budget) if budget and budget.strip() else None,
                start_date=start_date,
                travelers=travelers,
                interests=interests or [],
                style=style,
                special_needs=special_needs,
                context_data=context_data
            )
            return result

        # 提交后台任务
        task_id = task_manager.submit_task(app, _plan_task)
        return jsonify({'success': True, 'task_id': task_id, 'message': 'AI规划已提交，正在后台生成...'})

    except Exception as e:
        print(f"[AI Plan] Error: {str(e)}")
        print(traceback.format_exc())
        return jsonify({'success': False, 'error': str(e)}), 500

@ai_tools_bp.route('/api/ai/suggest', methods=['POST'])
@login_required
def ai_suggest_destinations():
    """AI推荐目的地API"""
    try:
        data = request.get_json()
        if not data:
            print("[AI Suggest] Error: No JSON data received")
            return jsonify({'success': False, 'message': '请求数据为空'}), 400

        interests = data.get('interests', [])
        days = int(data.get('days', 3))
        budget = data.get('budget')

        # 确保interests不为None
        if interests is None:
            interests = []

        # 转换budget
        budget_value = None
        if budget and str(budget).strip():
            try:
                budget_value = float(budget)
            except ValueError:
                pass

        def _suggest_task():
            planner = create_planner()
            return planner.suggest_destinations(interests, days, budget_value)

        # 提交后台任务
        task_id = task_manager.submit_task(app, _suggest_task)
        return jsonify({'success': True, 'task_id': task_id, 'message': '正在请求AI推荐...'})

    except Exception as e:
        print(f"[AI Suggest] Error: {str(e)}")
        import traceback
        print(traceback.format_exc())
        return jsonify({'success': False, 'error': str(e)}), 500

@ai_tools_bp.route('/api/ai/save-itinerary', methods=['POST'])
@login_required
def save_ai_itinerary():
    """保存AI生成的行程"""
    try:
        data = request.get_json()
        itinerary_data = data.get('itinerary')

        if not itinerary_data:
            return jsonify({'success': False, 'message': '行程数据为空'}), 400

        # 创建行程
        itinerary = Itinerary(
            title=f"{itinerary_data.get('destination', '')} - {itinerary_data.get('days', 3)}天行程",
            description=itinerary_data.get('summary', ''),
            days=itinerary_data.get('days', 3),
            budget=float(itinerary_data.get('total_budget', '0').replace('元', '')) if itinerary_data.get('total_budget') else None,
            user_id=current_user.id,
            is_public=True
        )

        db.session.add(itinerary)
        db.session.flush()

        # 创建每日行程
        daily_plans = itinerary_data.get('daily_plans', [])
        for day_plan in daily_plans:
            day = ItineraryDay(
                itinerary_id=itinerary.id,
                day_number=day_plan.get('day', 1),
                title=day_plan.get('title', ''),
                description=day_plan.get('description', ''),
                activities=json.dumps(day_plan.get('activities', []), ensure_ascii=False)
            )
            db.session.add(day)

        db.session.commit()
        flash('行程保存成功！', 'success')
        return jsonify({'success': True, 'itinerary_id': itinerary.id})

    except Exception as e:
        db.session.rollback()
        print(f"[Save Itinerary] Error: {str(e)}")
        import traceback
        print(traceback.format_exc())
        return jsonify({'success': False, 'error': str(e)}), 500
