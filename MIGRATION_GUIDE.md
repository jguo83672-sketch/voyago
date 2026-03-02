# 数据库迁移指南

本文档记录了 Voyago 项目的所有数据库迁移操作。

---

## 📋 迁移历史

### 迁移 1：支持行程多目的地

**日期**：2026

**日期**：2026

**变更内容**：

1. 新增关联表 `itinerary_destinations`
   - 用于存储行程与目的地的多对多关系
   - 支持一个行程包含多个目的地

2. 修改 `Itinerary` 模型
   - 移除了 `destination_id` 外键字段
   - 添加了 `destinations` 多对多关系

**表结构变化**：

```sql
-- 新增关联表
CREATE TABLE itinerary_destinations (
    itinerary_id INTEGER NOT NULL,
    destination_id INTEGER NOT NULL,
    PRIMARY KEY (itinerary_id, destination_id),
    FOREIGN KEY (itinerary_id) REFERENCES itineraries(id),
    FOREIGN KEY (destination_id) REFERENCES destinations(id)
);
```

---

### 迁移 2：UI 优化和功能增强

**日期**：2026

**变更内容**：

1. 新增 `comments2` 表（通用评论表）
2. 新增 `favorites2` 表（通用收藏表）
3. `destinations` 表新增字段：
   - `like_count` - 点赞数
   - `comment_count` - 评论数
   - `updated_at` - 更新时间
4. `itineraries` 表新增字段：
   - `comment_count` - 评论数

**新增表结构**：

```sql
CREATE TABLE comments2 (
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
);

CREATE TABLE favorites2 (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    user_id INTEGER NOT NULL,
    itinerary_id INTEGER NULL,
    destination_id INTEGER NULL,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (itinerary_id) REFERENCES itineraries(id),
    FOREIGN KEY (destination_id) REFERENCES destinations(id)
);
```

---

### 迁移 3：社群功能和用户资料扩展

**日期**：2026

**变更内容**：

1. 扩展 `User` 模型，新增个人资料字段：
   - `real_name` - 真实姓名
   - `gender` - 性别
   - `birth_date` - 出生日期
   - `location` - 所在地
   - `phone` - 联系电话
   - `hobbies` - 兴趣爱好
   - `travel_style` - 旅行风格
   - `travel_interests` - 旅行兴趣
   - `updated_at` - 更新时间

2. 新增社群功能表：
   - `communities` - 社群表
   - `community_members` - 社群成员表
   - `community_events` - 社群活动表
   - `event_registrations` - 活动报名表

**功能特性**：
- 用户可以创建和加入旅行社群
- 社群可以关联目的地
- 社群管理员可以举办活动
- 社员可以报名参加活动
- 支持活动状态管理（即将开始、进行中、已结束、已取消）

---

### 迁移 4：个人足迹功能

**日期**：2026

**变更内容**：

1. 新增 `travel_footprints` 表用于记录用户的旅行足迹：
   - `id` - 主键
   - `destination_id` - 目的地外键
   - `visit_date` - 访问日期
   - `note` - 备注说明
   - `photos` - 照片（预留）
   - `rating` - 评分（1-5星）
   - `created_at` - 创建时间
   - `user_id` - 用户外键
   - 唯一约束：用户、目的地、日期组合唯一

2. 扩展 `User` 模型关系：
   - 添加 `travel_footprints` 关联关系

**功能特性**：
- 用户可以记录去过的地方
- 支持地图可视化展示足迹
- 可以给每个地点评分和添加备注
- 统计访问过的国家和城市数量

**新增表结构**：

```sql
CREATE TABLE travel_footprints (
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
);
```

---

## 🚀 执行迁移

### 迁移顺序说明

新项目应按以下顺序执行迁移：

```bash
# 迁移 1 + 2（多目的地支持 + UI优化）：python migrate.py
# 迁移 3（社群功能）：python migrate_community.py
# 迁移 4（个人足迹）：python migrate_footprints.py
```

---

### 手动迁移

如果需要手动控制迁移过程：

#### 方法 1：使用迁移脚本

```bash
# 个人足迹功能迁移
python migrate_footprints.py

# 社群功能迁移
python migrate_community.py

# UI优化和功能增强迁移
python migrate.py
```

#### 方法 2：使用 Flask Shell

```bash
python

>>> from app import app, db
>>> from sqlalchemy import text
>>> with app.app_context():
...     # 创建新表
...     db.session.execute(text("""
...         CREATE TABLE IF NOT EXISTS comments2 (...)
...     """))
...     db.session.execute(text("""
...         CREATE TABLE IF NOT EXISTS favorites2 (...)
...     """))
...     # 添加字段
...     db.session.execute(text("ALTER TABLE destinations ADD COLUMN like_count INTEGER DEFAULT 0"))
...     # ... 其他字段
...     db.session.commit()
>>> exit()
```

---

## ✅ 验证迁移

### 检查表结构

```bash
python

>>> from app import app, db
>>> from sqlalchemy import text
>>> with app.app_context():
...     # 查看所有表
...     result = db.session.execute(text("SELECT name FROM sqlite_master WHERE type='table'"))
...     print([row[0] for row in result])
...
...     # 查看 destinations 表字段
...     result = db.session.execute(text("PRAGMA table_info(destinations)"))
...     for row in result:
...         print(f"{row[1]} ({row[2]})")
...
...     # 查看 itineraries 表字段
...     result = db.session.execute(text("PRAGMA table_info(itineraries)"))
...     for row in result:
...         print(f"{row[1]} ({row[2]})")
>>> exit()
```

### 功能测试

- [ ] 目的地详情页可以点赞和评论
- [ ] 行程详情页可以点赞和评论
- [ ] 目的地可以编辑和删除
- [ ] 行程可以编辑和删除
- [ ] 个人中心可以添加和编辑足迹
- [ ] 地图可以正确显示足迹标记
- [ ] 足迹统计信息正确显示

---

## 🔙 回滚计划

如需回滚迁移：

```sql
-- 删除新增的表
DROP TABLE IF EXISTS comments2;
DROP TABLE IF EXISTS favorites2;

-- 删除新增的字段（SQLite 不支持 DROP COLUMN，需要重建表）
-- 参考：fix_destination_id.py 的实现方式
```

---

## ⚠️ 注意事项

1. **数据备份**：在执行任何迁移前，务必备份数据库
   ```bash
   python backup_database.py
   ```

2. **测试环境**：先在测试环境中验证迁移脚本

3. **停机维护**：生产环境迁移时可能需要短暂停机

4. **SQLite 限制**：SQLite 对 `ALTER TABLE` 支持有限，某些操作需要重建表

---

## 📝 数据模型说明

### 多对多关系（行程-目的地）

使用 SQLAlchemy 的关联表实现：

```python
itinerary_destinations = db.Table('itinerary_destinations',
    db.Column('itinerary_id', db.Integer, db.ForeignKey('itineraries.id'), primary_key=True),
    db.Column('destination_id', db.Integer, db.ForeignKey('destinations.id'), primary_key=True)
)

class Itinerary(db.Model):
    destinations = db.relationship('Destination', secondary=itinerary_destinations,
                                  backref='itineraries', lazy=True)
```

### 便捷属性

```python
@property
def destination_names(self):
    return ', '.join([d.name for d in self.destinations])

@property
def primary_destination(self):
    return self.destinations[0] if self.destinations else None
```

---

## 🛠️ 工具脚本

### 备份数据库

```bash
python backup_database.py
```

### 初始化上传目录

```bash
python init_uploads.py
```

---

## 📞 获取帮助

如有问题，请查看：
- 应用日志
- 数据库迁移日志
- 或联系开发团队
