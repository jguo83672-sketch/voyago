"""
Migration 4: 添加个人足迹功能
创建 travel_footprints 表用于记录用户的旅行足迹
"""

from app import app, db
from sqlalchemy import text
from datetime import datetime

def migrate_footprints():
    """迁移 4: 创建个人足迹表"""
    with app.app_context():
        # 创建足迹表
        db.session.execute(text('''
            CREATE TABLE IF NOT EXISTS travel_footprints (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                destination_id INTEGER NOT NULL,
                visit_date DATE NOT NULL,
                note TEXT,
                photos TEXT,
                rating REAL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                user_id INTEGER NOT NULL,
                FOREIGN KEY (destination_id) REFERENCES destinations (id),
                FOREIGN KEY (user_id) REFERENCES users (id),
                UNIQUE(user_id, destination_id, visit_date)
            )
        '''))
        db.session.commit()

        print("✓ 迁移 4 完成: 创建 travel_footprints 表")

def rollback_footprints():
    """回滚迁移 4"""
    with app.app_context():
        db.session.execute(text('DROP TABLE IF EXISTS travel_footprints'))
        db.session.commit()
        print("✓ 回滚迁移 4: 删除 travel_footprints 表")

if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == 'rollback':
        rollback_footprints()
    else:
        migrate_footprints()
