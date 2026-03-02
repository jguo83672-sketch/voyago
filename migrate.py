"""
数据库迁移脚本 - UI优化和功能增强
执行方法: python migrate.py
"""
from app import app, db
from sqlalchemy import text

def migrate():
    """执行数据库迁移"""
    with app.app_context():
        print("开始数据库迁移...")

        # 创建新表
        print("\n1. 创建 comments2 表...")
        db.session.execute(text("""
            CREATE TABLE IF NOT EXISTS comments2 (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                content TEXT NOT NULL,
                target_type VARCHAR(20) NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                user_id INTEGER NOT NULL,
                itinerary_id INTEGER NULL,
                destination_id INTEGER NULL,
                FOREIGN KEY (user_id) REFERENCES users(id),
                FOREIGN KEY (itinerary_id) REFERENCES itineraries(id),
                FOREIGN KEY (destination_id) REFERENCES destinations(id)
            )
        """))

        print("2. 创建 favorites2 表...")
        db.session.execute(text("""
            CREATE TABLE IF NOT EXISTS favorites2 (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                user_id INTEGER NOT NULL,
                itinerary_id INTEGER NULL,
                destination_id INTEGER NULL,
                FOREIGN KEY (user_id) REFERENCES users(id),
                FOREIGN KEY (itinerary_id) REFERENCES itineraries(id),
                FOREIGN KEY (destination_id) REFERENCES destinations(id)
            )
        """))

        # 为 destinations 表添加新字段
        print("\n3. 为 destinations 表添加新字段...")
        fields_to_add = {
            'like_count': 'INTEGER DEFAULT 0',
            'comment_count': 'INTEGER DEFAULT 0',
            'updated_at': 'DATETIME DEFAULT CURRENT_TIMESTAMP'
        }

        for field_name, field_type in fields_to_add.items():
            try:
                db.session.execute(text(f"ALTER TABLE destinations ADD COLUMN {field_name} {field_type}"))
                print(f"   - 添加字段: {field_name}")
            except Exception as e:
                if "duplicate column name" in str(e).lower():
                    print(f"   - 字段 {field_name} 已存在，跳过")
                else:
                    print(f"   - 添加字段 {field_name} 失败: {e}")

        # 为 itineraries 表添加新字段
        print("\n4. 为 itineraries 表添加新字段...")
        try:
            db.session.execute(text("ALTER TABLE itineraries ADD COLUMN comment_count INTEGER DEFAULT 0"))
            print("   - 添加字段: comment_count")
        except Exception as e:
            if "duplicate column name" in str(e).lower():
                print("   - 字段 comment_count 已存在，跳过")
            else:
                print(f"   - 添加字段 comment_count 失败: {e}")

        db.session.commit()
        print("\n✅ 数据库迁移完成!")

        # 验证表结构
        print("\n5. 验证表结构...")
        result = db.session.execute(text("PRAGMA table_info(destinations)"))
        print("\nDestinations 表字段:")
        for row in result:
            print(f"   - {row[1]} ({row[2]})")

        result = db.session.execute(text("PRAGMA table_info(itineraries)"))
        print("\nItineraries 表字段:")
        for row in result:
            print(f"   - {row[1]} ({row[2]})")

        result = db.session.execute(text("SELECT name FROM sqlite_master WHERE type='table'"))
        print("\n所有表:")
        for row in result:
            print(f"   - {row[0]}")

if __name__ == '__main__':
    migrate()
