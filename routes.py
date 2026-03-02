from flask import render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from app import app, db
from models import (
    User, Destination, Itinerary, ItineraryDay, Guide, Comment, Comment2,
    Favorite, Favorite2, Community, CommunityMember, CommunityEvent, EventRegistration,
    TravelFootprint
)
from datetime import datetime
import json
from utils import save_upload_file, delete_file

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
    page = request.args.get('page', 1, type=int)
    destinations = Destination.query.paginate(
        page=page, per_page=12, error_out=False
    )
    return render_template('destinations.html', destinations=destinations)

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
        
        destination = Destination(
            name=request.form.get('name'),
            country=request.form.get('country'),
            city=request.form.get('city'),
            description=request.form.get('description'),
            cover_image=cover_image,
            rating=float(request.form.get('rating', 0)),
            tags=request.form.get('tags')
        )
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
    
    destinations = Destination.query.all()
    return render_template('create_guide.html', destinations=destinations)

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
        destination.country = request.form.get('country')
        destination.city = request.form.get('city')
        destination.description = request.form.get('description')
        destination.rating = float(request.form.get('rating', 0))
        destination.tags = request.form.get('tags')

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
@login_required
def edit_footprint(id):
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

