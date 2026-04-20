import os
import re
import ast

ROUTE_MAPPING = {
    # auth
    'register': 'auth',
    'login': 'auth',
    'logout': 'auth',
    'profile': 'auth',
    'edit_profile': 'auth',
    
    # main
    'index': 'main',
    'search': 'main',
    'favorites': 'main',
    'toggle_favorite': 'main',
    'get_task_status': 'main',
    'inject_user_data': 'main',
    
    # destination
    'destinations': 'destination',
    'destination_detail': 'destination',
    'create_destination': 'destination',
    'edit_destination': 'destination',
    'delete_destination': 'destination',
    'add_destination_comment': 'destination',
    'like_destination': 'destination',
    
    # guide
    'guides': 'guide',
    'guide_detail': 'guide',
    'create_guide': 'guide',
    'import_guide_ocr': 'guide',
    'ocr_analyze': 'guide',
    'add_comment': 'guide',
    'edit_guide': 'guide',
    'delete_guide': 'guide',
    
    # itinerary
    'itineraries': 'itinerary',
    'itinerary_detail': 'itinerary',
    'create_itinerary': 'itinerary',
    'edit_itinerary': 'itinerary',
    'update_itinerary_days': 'itinerary',
    'delete_itinerary': 'itinerary',
    'add_itinerary_comment': 'itinerary',
    'like_itinerary': 'itinerary',
    'itinerary_prepare': 'itinerary',
    'save_itinerary_prep': 'itinerary',
    'get_hotel_recommendations': 'itinerary',
    'get_flight_recommendations': 'itinerary',
    'day_detail': 'itinerary',
    'edit_day_detail': 'itinerary',
    'manage_day_activities': 'itinerary',
    
    # community
    'communities': 'community',
    'community_detail': 'community',
    'create_community': 'community',
    'join_community': 'community',
    'leave_community': 'community',
    'edit_community': 'community',
    'community_events': 'community',
    'event_detail': 'community',
    'create_event': 'community',
    'register_event': 'community',
    'unregister_event': 'community',
    'edit_event': 'community',
    
    # ecommerce
    'travel_shop': 'ecommerce',
    'product_detail': 'ecommerce',
    'cart': 'ecommerce',
    'add_to_cart': 'ecommerce',
    'update_cart_item': 'ecommerce',
    'remove_from_cart': 'ecommerce',
    'checkout': 'ecommerce',
    'orders': 'ecommerce',
    'order_detail': 'ecommerce',
    
    # ai_tools
    'ai_planner_page': 'ai_tools',
    'test_ai_api_page': 'ai_tools',
    'ai_plan_itinerary': 'ai_tools',
    'ai_suggest_destinations': 'ai_tools',
    'save_ai_itinerary': 'ai_tools',
    
    # footprint
    'add_footprint': 'footprint',
    'delete_footprint': 'footprint',
    'edit_footprint': 'footprint',
}

COMMON_IMPORTS = """from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
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
"""

def split_routes_file():
    with open('routes.py', 'r', encoding='utf-8') as f:
        source_code = f.read()
    
    lines = source_code.splitlines()
    tree = ast.parse(source_code)
    
    blueprints = {bp: [] for bp in set(ROUTE_MAPPING.values())}
    
    for node in tree.body:
        if isinstance(node, ast.FunctionDef):
            is_route = False
            for dec in node.decorator_list:
                # check if decorator is @app.route or @app.context_processor
                if isinstance(dec, ast.Call) and isinstance(dec.func, ast.Attribute):
                    if dec.func.value.id == 'app' and dec.func.attr == 'route':
                        is_route = True
                elif isinstance(dec, ast.Attribute):
                    if dec.value.id == 'app' and dec.attr == 'context_processor':
                        is_route = True
            
            if is_route:
                func_name = node.name
                bp_name = ROUTE_MAPPING.get(func_name, 'main')
                
                # Extract source lines for this function, including decorators
                # node.lineno is 1-indexed, but decorator_list[0].lineno is the top
                start_line = node.decorator_list[0].lineno - 1
                end_line = node.end_lineno
                
                func_lines = lines[start_line:end_line]
                
                # Replace decorators
                for i in range(len(func_lines)):
                    if '@app.route' in func_lines[i]:
                        func_lines[i] = func_lines[i].replace('@app.route', f'@{bp_name}_bp.route')
                    elif '@app.context_processor' in func_lines[i]:
                        func_lines[i] = func_lines[i].replace('@app.context_processor', f'@{bp_name}_bp.app_context_processor')
                
                blueprints[bp_name].append('\n'.join(func_lines))

    os.makedirs('blueprints', exist_ok=True)
    
    with open('blueprints/__init__.py', 'w', encoding='utf-8') as f:
        f.write("# Blueprints package\\n")
        
    for bp_name, bp_funcs in blueprints.items():
        bp_content = "\n\n".join(bp_funcs)
        
        # 替换 Blueprint Python 代码中的 url_for
        for func_name, b_name in ROUTE_MAPPING.items():
            bp_content = re.sub(
                rf"url_for\(\s*['\"]{func_name}['\"]", 
                f"url_for('{b_name}.{func_name}'", 
                bp_content
            )
            
        with open(f'blueprints/{bp_name}.py', 'w', encoding='utf-8') as f:
            f.write(COMMON_IMPORTS + "\n\n")
            f.write(f"{bp_name}_bp = Blueprint('{bp_name}', __name__)\n\n")
            f.write(bp_content)
            f.write("\n")

def update_templates():
    template_dir = 'templates'
    for root, dirs, files in os.walk(template_dir):
        for file in files:
            if file.endswith('.html'):
                path = os.path.join(root, file)
                with open(path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                for func_name, bp_name in ROUTE_MAPPING.items():
                    # url_for('func_name' -> url_for('bp.func_name'
                    content = re.sub(
                        rf"url_for\(\s*['\"]{func_name}['\"]", 
                        f"url_for('{bp_name}.{func_name}'", 
                        content
                    )
                
                with open(path, 'w', encoding='utf-8') as f:
                    f.write(content)

def update_app_py():
    with open('app.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Replace 'from routes import *' with blueprint registrations
    bp_imports = "\\n".join([f"from blueprints.{bp} import {bp}_bp" for bp in set(ROUTE_MAPPING.values())])
    bp_registers = "\\n    ".join([f"app.register_blueprint({bp}_bp)" for bp in set(ROUTE_MAPPING.values())])
    
    replacement = f"{bp_imports}\\n\\n    {bp_registers}\\n"
    
    content = content.replace("from routes import *", replacement)
    
    with open('app.py', 'w', encoding='utf-8') as f:
        f.write(content)

if __name__ == "__main__":
    split_routes_file()
    update_templates()
    update_app_py()
    print("Done refactoring routes to blueprints.")
