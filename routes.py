from flask import render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from app import app, db
from models import (
    User, Destination, Itinerary, ItineraryDay, Guide, Comment, Comment2,
    Favorite, Favorite2, Community, CommunityMember, CommunityEvent, EventRegistration,
    TravelFootprint, TravelPrep, HotelRecommendation, FlightRecommendation,
    TravelProduct, ProductReview, CartItem, Order, OrderItem
)
from datetime import datetime
import json
import uuid
from utils import save_upload_file, delete_file
from ai_planner import create_planner
from travel_prep import create_prep_service
from ocr_service import recognize_guide_image
from guide_classifier import classify_guide, suggest_destination, suggest_guide_title

@app.route('/')
def index():
    featured_destinations = Destination.query.order_by(Destination.rating.desc()).limit(6).all()
    popular_guides = Guide.query.filter_by(is_published=True).order_by(Guide.view_count.desc()).limit(6).all()
    latest_itineraries = Itinerary.query.filter_by(is_public=True).order_by(Itinerary.created_at.desc()).limit(6).all()
    return render_template('index.html', 
                         destinations=featured_destinations,
                         guides=popular_guides,
                         itineraries=latest_itineraries)

@app.route('/destinations')
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

@app.route('/destination/<int:id>')
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

@app.route('/guides')
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

@app.route('/guide/<int:id>')
def guide_detail(id):
    guide = Guide.query.get_or_404(id)
    guide.view_count += 1
    db.session.commit()
    
    comments = Comment.query.filter_by(guide_id=id).order_by(Comment.created_at.desc()).all()
    
    return render_template('guide_detail.html', guide=guide, comments=comments)

@app.route('/itineraries')
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

@app.route('/itinerary/<int:id>')
def itinerary_detail(id):
    itinerary = Itinerary.query.get_or_404(id)
    itinerary.view_count += 1
    db.session.commit()
    
    days = ItineraryDay.query.filter_by(itinerary_id=id).order_by(ItineraryDay.day_number).all()
    
    return render_template('itinerary_detail.html', itinerary=itinerary, days=days)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        
        if User.query.filter_by(username=username).first():
            flash('用户名已存在', 'danger')
            return redirect(url_for('register'))
        
        if User.query.filter_by(email=email).first():
            flash('邮箱已被注册', 'danger')
            return redirect(url_for('register'))
        
        user = User(username=username, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        
        flash('注册成功，请登录', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            login_user(user)
            next_page = request.args.get('next')
            flash('登录成功', 'success')
            return redirect(next_page) if next_page else redirect(url_for('index'))
        else:
            flash('用户名或密码错误', 'danger')
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('已退出登录', 'info')
    return redirect(url_for('index'))

@app.route('/profile')
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


@app.route('/profile/edit', methods=['GET', 'POST'])
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
        return redirect(url_for('profile'))

    return render_template('edit_profile.html')

@app.route('/create-destination', methods=['GET', 'POST'])
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
            tags=request.form.get('tags')
        )

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
        return redirect(url_for('destination_detail', id=destination.id))

    return render_template('create_destination.html')

@app.route('/create-guide', methods=['GET', 'POST'])
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
        return redirect(url_for('guide_detail', id=guide.id))

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


@app.route('/guide/import-ocr', methods=['GET', 'POST'])
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
            return redirect(url_for('create_guide'))

    return render_template('import_guide_ocr.html')


@app.route('/guide/ocr-analyze', methods=['POST'])
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

        return jsonify({
            'success': True,
            'data': {
                'title': suggested_title,
                'content': recognized_text,
                'category': category_result['category'],
                'destination_name': suggested_destination,
                'destination_id': destination_id
            }
        })

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/create-itinerary', methods=['GET', 'POST'])
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
        
        for i in range(1, itinerary.days + 1):
            day_title = request.form.get(f'day_{i}_title', f'第{i}天')
            day_description = request.form.get(f'day_{i}_description', '')
            day_activities = request.form.get(f'day_{i}_activities', '')
            
            itinerary_day = ItineraryDay(
                day_number=i,
                title=day_title,
                description=day_description,
                activities=day_activities,
                itinerary_id=itinerary.id
            )
            db.session.add(itinerary_day)
        
        db.session.commit()
        flash('行程创建成功', 'success')
        return redirect(url_for('itinerary_detail', id=itinerary.id))
    
    destinations = Destination.query.all()
    return render_template('create_itinerary.html', destinations=destinations)

@app.route('/add-comment/<int:guide_id>', methods=['POST'])
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
    
    return redirect(url_for('guide_detail', id=guide_id))

@app.route('/toggle-favorite/<int:item_type>/<int:item_id>')
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

@app.route('/favorites')
@login_required
def favorites():
    favorite_items = Favorite.query.filter_by(user_id=current_user.id).all()
    return render_template('favorites.html', favorites=favorite_items)

@app.route('/search')
def search():
    query = request.args.get('q', '')
    if not query:
        return redirect(url_for('index'))
    
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

# 目的地编辑
@app.route('/destination/<int:id>/edit', methods=['GET', 'POST'])
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
                    delete_file(old_image)

        destination.name = request.form.get('name')
        destination.region_type = request.form.get('region_type', destination.region_type)
        destination.description = request.form.get('description')
        destination.rating = float(request.form.get('rating', 0))
        destination.tags = request.form.get('tags')

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
        return redirect(url_for('destination_detail', id=destination.id))

    return render_template('edit_destination.html', destination=destination)

# 目的地删除
@app.route('/destination/<int:id>/delete', methods=['POST'])
@login_required
def delete_destination(id):
    destination = Destination.query.get_or_404(id)
    if destination.cover_image:
        delete_file(destination.cover_image)
    db.session.delete(destination)
    db.session.commit()
    flash('目的地已删除', 'success')
    return redirect(url_for('destinations'))

# 行程编辑
@app.route('/itinerary/<int:id>/edit', methods=['GET', 'POST'])
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
                    delete_file(old_image)

        itinerary.title = request.form.get('title')
        itinerary.description = request.form.get('description')
        itinerary.days = int(request.form.get('days'))
        itinerary.start_date = datetime.strptime(request.form.get('start_date'), '%Y-%m-%d')
        itinerary.end_date = datetime.strptime(request.form.get('end_date'), '%Y-%m-%d')
        itinerary.budget = float(request.form.get('budget')) if request.form.get('budget') else None

        db.session.commit()
        flash('行程更新成功', 'success')
        return redirect(url_for('itinerary_detail', id=itinerary.id))

    return render_template('edit_itinerary.html', itinerary=itinerary)

# 行程删除
@app.route('/itinerary/<int:id>/delete', methods=['POST'])
@login_required
def delete_itinerary(id):
    itinerary = Itinerary.query.get_or_404(id)
    if itinerary.cover_image:
        delete_file(itinerary.cover_image)
    db.session.delete(itinerary)
    db.session.commit()
    flash('行程已删除', 'success')
    return redirect(url_for('itineraries'))

# 攻略编辑
@app.route('/guide/<int:id>/edit', methods=['GET', 'POST'])
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
                    delete_file(old_image)

        guide.title = request.form.get('title')
        guide.content = request.form.get('content')
        guide.category = request.form.get('category')
        guide.destination_id = int(request.form.get('destination_id'))

        db.session.commit()
        flash('攻略更新成功', 'success')
        return redirect(url_for('guide_detail', id=guide.id))

    destinations = Destination.query.all()
    return render_template('edit_guide.html', guide=guide, destinations=destinations)

# 攻略删除
@app.route('/guide/<int:id>/delete', methods=['POST'])
@login_required
def delete_guide(id):
    guide = Guide.query.get_or_404(id)
    if guide.cover_image:
        delete_file(guide.cover_image)
    db.session.delete(guide)
    db.session.commit()
    flash('攻略已删除', 'success')
    return redirect(url_for('guides'))

# 行程评论
@app.route('/itinerary/<int:id>/comment', methods=['POST'])
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

    return redirect(url_for('itinerary_detail', id=id))

# 目的地评论
@app.route('/destination/<int:id>/comment', methods=['POST'])
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

    return redirect(url_for('destination_detail', id=id))

# 行程点赞
@app.route('/like/itinerary/<int:id>')
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

# 目的地点赞
@app.route('/like/destination/<int:id>')
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


# ==================== 社群功能 ====================

# 社群列表
@app.route('/communities')
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


# 社群详情
@app.route('/community/<int:id>')
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


# 创建社群
@app.route('/create-community', methods=['GET', 'POST'])
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
        return redirect(url_for('community_detail', id=community.id))

    destinations = Destination.query.all()
    return render_template('create_community.html', destinations=destinations)


# 加入社群
@app.route('/community/<int:id>/join', methods=['POST'])
@login_required
def join_community(id):
    community = Community.query.get_or_404(id)

    if community.is_full:
        flash('该社群成员已满，无法加入！', 'warning')
        return redirect(url_for('community_detail', id=id))

    existing_member = CommunityMember.query.filter_by(
        user_id=current_user.id,
        community_id=id
    ).first()

    if existing_member:
        flash('您已经是该社群的成员了！', 'info')
        return redirect(url_for('community_detail', id=id))

    member = CommunityMember(user_id=current_user.id, community_id=id)
    db.session.add(member)
    community.member_count += 1
    db.session.commit()

    flash('成功加入社群！', 'success')
    return redirect(url_for('community_detail', id=id))


# 退出社群
@app.route('/community/<int:id>/leave', methods=['POST'])
@login_required
def leave_community(id):
    membership = CommunityMember.query.filter_by(
        user_id=current_user.id,
        community_id=id
    ).first()

    if not membership:
        flash('您未加入该社群！', 'warning')
        return redirect(url_for('community_detail', id=id))

    community = Community.query.get(id)

    # 管理员不能退出
    if membership.role == 'admin' and community.member_count > 1:
        flash('管理员不能退出社群！请先转让管理员权限。', 'danger')
        return redirect(url_for('community_detail', id=id))

    db.session.delete(membership)
    community.member_count -= 1
    db.session.commit()

    flash('已退出社群！', 'success')
    return redirect(url_for('communities'))


# 编辑社群
@app.route('/community/<int:id>/edit', methods=['GET', 'POST'])
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
        return redirect(url_for('community_detail', id=id))

    if request.method == 'POST':
        community.name = request.form.get('name')
        community.description = request.form.get('description')
        community.destination_id = request.form.get('destination_id', type=int)
        community.max_members = request.form.get('max_members', type=int)
        community.is_public = request.form.get('is_public') == 'on'

        if request.files.get('cover_image'):
            if community.cover_image:
                delete_file(community.cover_image)
            community.cover_image = save_upload_file(request.files.get('cover_image'), 'communities')

        db.session.commit()

        flash('社群更新成功！', 'success')
        return redirect(url_for('community_detail', id=id))

    destinations = Destination.query.all()
    return render_template('edit_community.html', community=community, destinations=destinations)


# 社群活动列表
@app.route('/community/<int:community_id>/events')
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


# 活动详情
@app.route('/event/<int:id>')
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


# 创建活动
@app.route('/community/<int:community_id>/create-event', methods=['GET', 'POST'])
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
        return redirect(url_for('community_detail', id=community_id))

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
        return redirect(url_for('event_detail', id=event.id))

    return render_template('create_event.html', community=community)


# 报名活动
@app.route('/event/<int:id>/register', methods=['POST'])
@login_required
def register_event(id):
    event = CommunityEvent.query.get_or_404(id)

    if event.is_full:
        flash('该活动名额已满！', 'warning')
        return redirect(url_for('event_detail', id=id))

    if event.is_past:
        flash('该活动已结束，无法报名！', 'warning')
        return redirect(url_for('event_detail', id=id))

    existing_registration = EventRegistration.query.filter_by(
        user_id=current_user.id,
        event_id=id
    ).first()

    if existing_registration:
        flash('您已经报名该活动！', 'info')
        return redirect(url_for('event_detail', id=id))

    registration = EventRegistration(user_id=current_user.id, event_id=id)
    db.session.add(registration)
    event.participant_count += 1
    db.session.commit()

    flash('报名成功！', 'success')
    return redirect(url_for('event_detail', id=id))


# 取消报名
@app.route('/event/<int:id>/unregister', methods=['POST'])
@login_required
def unregister_event(id):
    registration = EventRegistration.query.filter_by(
        user_id=current_user.id,
        event_id=id
    ).first()

    if not registration:
        flash('您未报名该活动！', 'warning')
        return redirect(url_for('event_detail', id=id))

    event = CommunityEvent.query.get(id)
    event.participant_count -= 1
    db.session.delete(registration)
    db.session.commit()

    flash('已取消报名！', 'success')
    return redirect(url_for('event_detail', id=id))


# 编辑活动
@app.route('/event/<int:id>/edit', methods=['GET', 'POST'])
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
        return redirect(url_for('event_detail', id=id))

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
                delete_file(event.cover_image)
            event.cover_image = save_upload_file(request.files.get('cover_image'), 'events')

        db.session.commit()

        flash('活动更新成功！', 'success')
        return redirect(url_for('event_detail', id=id))

    return render_template('edit_event.html', event=event)


# ==================== 个人足迹功能 ====================

# 添加足迹
@app.route('/footprints/add', methods=['GET', 'POST'])
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
            return redirect(url_for('profile'))

        footprint = TravelFootprint(
            user_id=current_user.id,
            destination_id=destination_id,
            visit_date=datetime.strptime(visit_date, '%Y-%m-%d').date(),
            note=note,
            rating=rating
        )
        db.session.add(footprint)
        db.session.commit()

        flash('足迹添加成功！', 'success')
        return redirect(url_for('profile'))

    destinations = Destination.query.all()
    return render_template('add_footprint.html', destinations=destinations)


# 删除足迹
@app.route('/footprint/<int:id>/delete', methods=['POST'])
@login_required
def delete_footprint(id):
    footprint = TravelFootprint.query.get_or_404(id)
    if footprint.user_id != current_user.id:
        flash('您没有权限删除此足迹！', 'danger')
        return redirect(url_for('profile'))

    db.session.delete(footprint)
    db.session.commit()
    flash('足迹已删除', 'success')
    return redirect(url_for('profile'))


# 编辑足迹
@app.route('/footprint/<int:id>/edit', methods=['GET', 'POST'])
@app.route('/edit-footprint/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_footprint(id):
    """编辑足迹"""
    footprint = TravelFootprint.query.get_or_404(id)

    if footprint.user_id != current_user.id:
        flash('您没有权限编辑此足迹！', 'danger')
        return redirect(url_for('profile'))

    if request.method == 'POST':
        footprint.destination_id = request.form.get('destination_id', type=int)
        footprint.visit_date = datetime.strptime(request.form.get('visit_date'), '%Y-%m-%d').date()
        footprint.note = request.form.get('note')
        footprint.rating = request.form.get('rating', type=float)

        db.session.commit()
        flash('足迹更新成功！', 'success')
        return redirect(url_for('profile'))

    destinations = Destination.query.all()
    return render_template('edit_footprint.html', footprint=footprint, destinations=destinations)


# ==================== AI行程规划功能 ====================
@app.route('/ai-planner')
@login_required
def ai_planner_page():
    """AI行程规划页面"""
    destinations = Destination.query.all()
    return render_template('ai_planner.html', destinations=destinations)


@app.route('/test-ai-api')
@login_required
def test_ai_api_page():
    """AI API测试页面"""
    return render_template('test_ai_api.html')


@app.route('/api/ai/plan', methods=['POST'])
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

        # 创建AI规划器
        print("[AI Plan] Creating planner...")
        planner = create_planner()

        # 收集上下文数据
        context_data = {}

        # 收集目的地信息
        print("[AI Plan] Collecting destination data...")
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
        print("[AI Plan] Collecting guide data...")
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
        print("[AI Plan] Collecting itinerary data...")
        itineraries = Itinerary.query.filter_by(is_public=True).limit(3).all()
        itineraries_data = [{
            'title': i.title,
            'days': i.days,
            'budget': i.budget,
            'description': i.description
        } for i in itineraries]
        context_data['itineraries'] = planner.collect_itinerary_data(itineraries_data)

        # 调用AI规划
        print("[AI Plan] Calling AI...")
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

        print(f"[AI Plan] Result: success={result.get('success')}")

        return jsonify(result)

    except Exception as e:
        print(f"[AI Plan] Error: {str(e)}")
        print(traceback.format_exc())
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/ai/suggest', methods=['POST'])
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

        planner = create_planner()
        result = planner.suggest_destinations(interests, days, budget_value)

        return jsonify(result)

    except Exception as e:
        print(f"[AI Suggest] Error: {str(e)}")
        import traceback
        print(traceback.format_exc())
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/ai/save-itinerary', methods=['POST'])
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


# ==================== 出行准备功能 ====================
@app.route('/itinerary/<int:itinerary_id>/prepare', methods=['GET', 'POST'])
@login_required
def itinerary_prepare(itinerary_id):
    """行程准备页面"""
    itinerary = Itinerary.query.get_or_404(itinerary_id)

    if itinerary.user_id != current_user.id:
        flash('您没有权限访问此页面', 'danger')
        return redirect(url_for('itineraries'))

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
        return redirect(url_for('itinerary_prepare', itinerary_id=itinerary_id))

    return render_template('itinerary_prepare.html',
                         itinerary=itinerary,
                         prep=prep,
                         check_in=check_in,
                         check_out=check_out,
                         destination=destination)


@app.route('/itinerary/<int:itinerary_id>/prepare/save', methods=['POST'])
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


@app.route('/api/itinerary/<int:itinerary_id>/hotels', methods=['GET', 'POST'])
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


@app.route('/api/itinerary/<int:itinerary_id>/flights', methods=['GET', 'POST'])
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


# ==================== 旅行商店功能 ====================
@app.route('/travel-shop')
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


@app.route('/travel-shop/product/<int:id>')
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


@app.route('/cart')
@login_required
def cart():
    """购物车"""
    cart_items = CartItem.query.filter_by(user_id=current_user.id).all()
    total = sum(item.subtotal for item in cart_items)
    return render_template('cart.html', cart_items=cart_items, total=total)


@app.route('/cart/add/<int:product_id>', methods=['POST'])
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


@app.route('/cart/update/<int:item_id>', methods=['POST'])
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


@app.route('/cart/remove/<int:item_id>', methods=['POST'])
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


@app.route('/checkout', methods=['GET', 'POST'])
@login_required
def checkout():
    """结账页面"""
    if request.method == 'GET':
        cart_items = CartItem.query.filter_by(user_id=current_user.id).all()

        if not cart_items:
            flash('购物车为空', 'warning')
            return redirect(url_for('travel_shop'))

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


@app.route('/orders')
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


@app.route('/order/<int:id>')
@login_required
def order_detail(id):
    """订单详情"""
    order = Order.query.get_or_404(id)

    if order.user_id != current_user.id:
        flash('您没有权限查看此订单', 'danger')
        return redirect(url_for('orders'))

    return render_template('order_detail.html', order=order)


# 全局上下文处理器
@app.context_processor
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

