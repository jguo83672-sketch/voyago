"""
社群功能数据库迁移脚本
执行方法: python migrate_community.py
"""
from app import app, db
from sqlalchemy import text

print("=" * 50)
print("社群功能数据库迁移")
print("=" * 50)

with app.app_context():
    print("\n[1/2] 添加用户资料字段...")

    # 检查并添加用户扩展字段
    user_fields = {
        'real_name': 'VARCHAR(50)',
        'gender': 'VARCHAR(10)',
        'birth_date': 'DATE',
        'location': 'VARCHAR(100)',
        'phone': 'VARCHAR(20)',
        'hobbies': 'TEXT',
        'travel_style': 'VARCHAR(50)',
        'travel_interests': 'VARCHAR(200)',
        'updated_at': 'DATETIME'
    }

    for field_name, field_type in user_fields.items():
        try:
            db.session.execute(text(f"ALTER TABLE users ADD COLUMN {field_name} {field_type}"))
            print(f"  ✓ 添加字段: {field_name}")
        except Exception as e:
            if "duplicate column name" in str(e).lower():
                print(f"  - 字段 {field_name} 已存在，跳过")
            else:
                print(f"  ! 添加字段 {field_name} 失败: {e}")

    # 为现有记录设置 updated_at
    try:
        db.session.execute(text("UPDATE users SET updated_at = created_at WHERE updated_at IS NULL"))
        print("  ✓ 初始化 updated_at 字段")
    except:
        pass

    print("\n[2/2] 创建社群相关表...")

    # 创建社群表
    db.session.execute(text("""
        CREATE TABLE IF NOT EXISTS communities (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name VARCHAR(100) NOT NULL,
            description TEXT,
            cover_image VARCHAR(200),
            destination_id INTEGER,
            max_members INTEGER DEFAULT 50,
            member_count INTEGER DEFAULT 1,
            is_public BOOLEAN DEFAULT 1,
            status VARCHAR(20) DEFAULT 'active',
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            creator_id INTEGER NOT NULL,
            FOREIGN KEY (creator_id) REFERENCES users(id),
            FOREIGN KEY (destination_id) REFERENCES destinations(id)
        )
    """))
    print("  ✓ communities 表已创建")

    # 创建社群成员表
    db.session.execute(text("""
        CREATE TABLE IF NOT EXISTS community_members (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            role VARCHAR(20) DEFAULT 'member',
            status VARCHAR(20) DEFAULT 'active',
            joined_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            user_id INTEGER NOT NULL,
            community_id INTEGER NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (community_id) REFERENCES communities(id),
            UNIQUE(user_id, community_id)
        )
    """))
    print("  ✓ community_members 表已创建")

    # 创建社群活动表
    db.session.execute(text("""
        CREATE TABLE IF NOT EXISTS community_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title VARCHAR(200) NOT NULL,
            description TEXT,
            location VARCHAR(200),
            start_time DATETIME NOT NULL,
            end_time DATETIME NOT NULL,
            max_participants INTEGER DEFAULT 20,
            participant_count INTEGER DEFAULT 0,
            cover_image VARCHAR(200),
            status VARCHAR(20) DEFAULT 'upcoming',
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            community_id INTEGER NOT NULL,
            FOREIGN KEY (community_id) REFERENCES communities(id)
        )
    """))
    print("  ✓ community_events 表已创建")

    # 创建活动报名表
    db.session.execute(text("""
        CREATE TABLE IF NOT EXISTS event_registrations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            status VARCHAR(20) DEFAULT 'registered',
            note TEXT,
            registered_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            user_id INTEGER NOT NULL,
            event_id INTEGER NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (event_id) REFERENCES community_events(id),
            UNIQUE(user_id, event_id)
        )
    """))
    print("  ✓ event_registrations 表已创建")

    # 提交更改
    db.session.commit()
    print("\n✅ 社群功能迁移完成!")

    # 验证
    print("\n" + "=" * 50)
    print("验证迁移结果...")
    print("=" * 50)

    result = db.session.execute(text("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"))
    tables = [row[0] for row in result]
    print(f"\n数据库中的表 ({len(tables)} 个):")
    for table in tables:
        print(f"  - {table}")

    print("\n" + "=" * 50)
    print("关键字段检查:")
    print("=" * 50)

    result = db.session.execute(text("PRAGMA table_info(users)"))
    user_columns = [row[1] for row in result]

    checks = [
        ("communities 表", "communities" in tables),
        ("community_members 表", "community_members" in tables),
        ("community_events 表", "community_events" in tables),
        ("event_registrations 表", "event_registrations" in tables),
        ("users.real_name", "real_name" in user_columns),
        ("users.hobbies", "hobbies" in user_columns),
        ("users.travel_style", "travel_style" in user_columns),
        ("users.travel_interests", "travel_interests" in user_columns),
    ]

    all_ok = True
    for name, exists in checks:
        status = "✓" if exists else "✗"
        print(f"  {status} {name}")
        if not exists:
            all_ok = False

    print("\n" + "=" * 50)
    if all_ok:
        print("✅ 迁移成功完成！")
    else:
        print("⚠️  迁移完成，但有部分字段/表缺失")
    print("=" * 50)
