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


guide_bp = Blueprint('guide', __name__)

@guide_bp.route('/guides')
def guides():
    page = request.args.get('page', 1, type=int)
    category = request.args.get('category')
    
    query = Guide.query.filter_by(is_published=True)
    if category:
        query = query.filter_by(category=category)
    
    guides = query.order_by(Guide.created_at.desc()).paginate(
        page=page, per_page=12, error_out=False
    )
    return render_template('guides.html', guides=guides, category=category)

@guide_bp.route('/guide/<int:id>')
def guide_detail(id):
    guide = Guide.query.get_or_404(id)
    guide.view_count += 1
    db.session.commit()
    
    comments = Comment.query.filter_by(guide_id=id).order_by(Comment.created_at.desc()).all()
    
    return render_template('guide_detail.html', guide=guide, comments=comments)

@guide_bp.route('/create-guide', methods=['GET', 'POST'])
@login_required
def create_guide():
    if request.method == 'POST':
        cover_image = None
        if 'cover_image' in request.files:
            file = request.files['cover_image']
            if file.filename:
                cover_image = save_upload_file(file, app.config['UPLOAD_FOLDER'], 'guides')

        guide = Guide(
            title=request.form.get('title'),
            content=request.form.get('content'),
            category=request.form.get('category'),
            destination_id=int(request.form.get('destination_id')),
            user_id=current_user.id,
            cover_image=cover_image
        )
        db.session.add(guide)
        db.session.commit()

        flash('攻略发布成功', 'success')
        return redirect(url_for('guide.guide_detail', id=guide.id))

    # GET 请求：检查是否从 OCR 导入过来
    ocr_import = None
    if request.args.get('title') or request.args.get('content'):
        ocr_import = {
            'title': request.args.get('title', ''),
            'content': request.args.get('content', ''),
            'category': request.args.get('category', ''),
            'destination_id': request.args.get('destination_id')
        }

    destinations = Destination.query.all()
    return render_template('create_guide.html', destinations=destinations, ocr_import=ocr_import)

@guide_bp.route('/guide/import-ocr', methods=['GET', 'POST'])
@login_required
def import_guide_ocr():
    """通过 OCR 导入攻略"""
    if request.method == 'POST':
        try:
            # 检查是否有上传的图片
            if 'guide_image' not in request.files:
                flash('请上传攻略图片', 'error')
                return redirect(request.url)

            file = request.files['guide_image']
            if not file.filename:
                flash('请选择要上传的图片', 'error')
                return redirect(request.url)

            # 读取图片数据
            image_data = file.read()

            # 使用 OCR 识别文字
            flash('正在识别文字，请稍候...', 'info')
            recognized_text = recognize_guide_image(image_data)

            # 使用 AI 分类
            flash('正在自动分类...', 'info')
            category_result = classify_guide("", recognized_text)

            # 生成建议标题
            suggested_title = suggest_guide_title(recognized_text)

            # 保存识别的图片作为封面
            import tempfile
            import os
            with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as tmp:
                tmp.write(image_data)
                tmp_path = tmp.name

            try:
                from werkzeug.datastructures import FileStorage
                file_storage = FileStorage(
                    stream=open(tmp_path, 'rb'),
                    filename=f"ocr_import_{uuid.uuid4().hex[:8]}.jpg"
                )
                cover_image = save_upload_file(file_storage, app.config['UPLOAD_FOLDER'], 'guides')
            finally:
                os.unlink(tmp_path)

            # 传递数据到创建攻略页面
            destinations = Destination.query.all()

            return render_template('create_guide.html',
                                  destinations=destinations,
                                  ocr_import={
                                      'title': suggested_title,
                                      'content': recognized_text,
                                      'category': category_result['category'],
                                      'cover_image': cover_image
                                  })

        except Exception as e:
            flash(f'OCR 识别失败: {str(e)}', 'error')
            return redirect(url_for('guide.create_guide'))

    return render_template('import_guide_ocr.html')

@guide_bp.route('/guide/ocr-analyze', methods=['POST'])
@login_required
def ocr_analyze():
    """OCR 分析接口（用于 AJAX 请求）"""
    try:
        # 检查是否有上传的图片
        if 'guide_image' not in request.files:
            return jsonify({'success': False, 'error': '请上传攻略图片'}), 400

        file = request.files['guide_image']
        if not file.filename:
            return jsonify({'success': False, 'error': '请选择要上传的图片'}), 400

        # 读取图片数据
        image_data = file.read()

        def _ocr_task():
            # 使用 OCR 识别文字
            recognized_text = recognize_guide_image(image_data)

            # 使用 AI 分类
            category_result = classify_guide("", recognized_text)

            # 生成建议标题
            suggested_title = suggest_guide_title(recognized_text)

            # 尝试提取目的地
            suggested_destination = suggest_destination(suggested_title, recognized_text)

            # 查找匹配的目的地
            destination_id = None
            if suggested_destination:
                destination = Destination.query.filter(
                    Destination.name.like(f'%{suggested_destination}%')
                ).first()
                if destination:
                    destination_id = destination.id

            return {
                'title': suggested_title,
                'content': recognized_text,
                'category': category_result['category'],
                'destination_name': suggested_destination,
                'destination_id': destination_id
            }

        task_id = task_manager.submit_task(app, _ocr_task)
        return jsonify({'success': True, 'task_id': task_id, 'message': '正在分析图片...'})

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@guide_bp.route('/add-comment/<int:guide_id>', methods=['POST'])
@login_required
def add_comment(guide_id):
    content = request.form.get('content')
    if content:
        comment = Comment(
            content=content,
            user_id=current_user.id,
            guide_id=guide_id
        )
        db.session.add(comment)
        
        guide = Guide.query.get(guide_id)
        guide.comment_count += 1
        
        db.session.commit()
        flash('评论成功', 'success')
    else:
        flash('评论内容不能为空', 'danger')
    
    return redirect(url_for('guide.guide_detail', id=guide_id))

@guide_bp.route('/guide/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_guide(id):
    guide = Guide.query.get_or_404(id)
    if request.method == 'POST':
        old_image = guide.cover_image

        if 'cover_image' in request.files:
            file = request.files['cover_image']
            if file.filename:
                guide.cover_image = save_upload_file(file, app.config['UPLOAD_FOLDER'], 'guides')
                if old_image:
                    delete_file(old_image, app.config['UPLOAD_FOLDER'])

        guide.title = request.form.get('title')
        guide.content = request.form.get('content')
        guide.category = request.form.get('category')
        guide.destination_id = int(request.form.get('destination_id'))

        db.session.commit()
        flash('攻略更新成功', 'success')
        return redirect(url_for('guide.guide_detail', id=guide.id))

    destinations = Destination.query.all()
    return render_template('edit_guide.html', guide=guide, destinations=destinations)

@guide_bp.route('/guide/<int:id>/delete', methods=['POST'])
@login_required
def delete_guide(id):
    guide = Guide.query.get_or_404(id)
    if guide.cover_image:
        delete_file(guide.cover_image, app.config['UPLOAD_FOLDER'])
    db.session.delete(guide)
    db.session.commit()
    flash('攻略已删除', 'success')
    return redirect(url_for('guide.guides'))
