# 社群功能使用指南

本文档介绍 Voyago 新增的社群功能和个人资料扩展功能。

---

## 🎯 功能概览

### 社群功能
- 创建和加入旅行社群
- 社群可以关联特定目的地
- 管理员可以举办社群活动
- 社员可以报名参加活动

### 个人资料扩展
- 真实姓名、性别、出生日期
- 所在地、联系电话
- 兴趣爱好、旅行风格
- 旅行兴趣偏好

---

## 📋 数据库迁移

### 执行迁移

```bash
python migrate_community.py
```

该脚本会：
1. 为用户表添加扩展字段
2. 创建社群相关表（4个）
3. 验证迁移结果

### 迁移内容

**新增用户字段：**
- `real_name` - 真实姓名 (VARCHAR(50))
- `gender` - 性别 (VARCHAR(10))
- `birth_date` - 出生日期 (DATE)
- `location` - 所在地 (VARCHAR(100))
- `phone` - 联系电话 (VARCHAR(20))
- `hobbies` - 兴趣爱好 (TEXT)
- `travel_style` - 旅行风格 (VARCHAR(50))
- `travel_interests` - 旅行兴趣 (VARCHAR(200))
- `updated_at` - 更新时间 (DATETIME)

**新增表：**
- `communities` - 社群表
- `community_members` - 社群成员关联表
- `community_events` - 社群活动表
- `event_registrations` - 活动报名表

---

## 🚀 功能使用

### 1. 创建社群

1. 登录后点击导航栏 "用户" → "创建社群"
2. 填写社群信息：
   - 社群名称（必填）
   - 社群描述（必填）
   - 关联目的地（可选）
   - 最大成员数
   - 社群封面
   - 是否公开
3. 点击"创建社群"
4. 创建者自动成为社群管理员

### 2. 加入社群

1. 访问"社群"页面
2. 浏览可加入的社群
3. 点击"查看详情"
4. 点击"加入社群"按钮

**限制条件：**
- 社群必须是公开状态
- 成员数量未达到上限
- 用户未加入该社群

### 3. 创建活动

1. 进入社群详情页
2. 点击"创建活动"按钮
3. 填写活动信息：
   - 活动标题（必填）
   - 活动描述（必填）
   - 活动地点
   - 开始时间（必填）
   - 结束时间（必填）
   - 最大参与人数
   - 活动封面
4. 点击"创建活动"

### 4. 报名活动

1. 进入活动详情页
2. 点击"立即报名"按钮

**限制条件：**
- 用户已登录
- 活动名额未满
- 活动未结束
- 用户未报名该活动

### 5. 编辑个人资料

1. 登录后点击导航栏 "用户" → "编辑资料"
2. 填写个人信息：
   - 基本信息：真实姓名、性别、出生日期、所在地、联系电话
   - 个人简介
   - 兴趣偏好：兴趣爱好、旅行风格、旅行兴趣
   - 上传头像
3. 点击"保存修改"

**旅行风格选项：**
- 背包客
- 豪华游
- 探险游
- 休闲游
- 文化游
- 美食游

---

## 📂 文件结构

```
voyago v1.0.0/
├── models.py                    # 数据模型（新增 Community 等 4 个模型）
├── routes.py                   # 路由（新增 11 个社群相关路由）
├── templates/
│   ├── communities.html          # 社群列表
│   ├── community_detail.html     # 社群详情
│   ├── create_community.html     # 创建社群
│   ├── edit_community.html       # 编辑社群
│   ├── community_events.html     # 社群活动列表
│   ├── event_detail.html        # 活动详情
│   ├── create_event.html        # 创建活动
│   ├── edit_event.html          # 编辑活动
│   ├── profile.html             # 个人中心（已更新）
│   └── edit_profile.html       # 编辑个人资料（新增）
├── utils.py                    # 工具函数
├── init_uploads.py             # 上传目录初始化（已更新）
└── migrate_community.py        # 社群功能迁移脚本（新增）
```

---

## 🔗 路由列表

### 社群路由
| 路由 | 方法 | 说明 | 权限 |
|------|------|------|------|
| `/communities` | GET | 社群列表 | 公开 |
| `/community/<id>` | GET | 社群详情 | 公开 |
| `/create-community` | GET/POST | 创建社群 | 登录 |
| `/community/<id>/join` | POST | 加入社群 | 登录 |
| `/community/<id>/leave` | POST | 退出社群 | 登录 |
| `/community/<id>/edit` | GET/POST | 编辑社群 | 管理员 |
| `/community/<id>/events` | GET | 社群活动列表 | 公开 |
| `/event/<id>` | GET | 活动详情 | 公开 |
| `/community/<id>/create-event` | GET/POST | 创建活动 | 社员 |
| `/event/<id>/register` | POST | 报名活动 | 登录 |
| `/event/<id>/unregister` | POST | 取消报名 | 登录 |
| `/event/<id>/edit` | GET/POST | 编辑活动 | 管理员/版主 |

### 用户路由
| 路由 | 方法 | 说明 | 权限 |
|------|------|------|------|
| `/profile` | GET | 个人中心 | 登录 |
| `/profile/edit` | GET/POST | 编辑个人资料 | 登录 |

---

## 📊 数据模型说明

### Community（社群）
- `name` - 社群名称
- `description` - 社群描述
- `destination_id` - 关联目的地
- `max_members` - 最大成员数
- `member_count` - 当前成员数
- `is_public` - 是否公开
- `status` - 状态（active/inactive/archived）
- `creator_id` - 创建者

### CommunityMember（社群成员）
- `role` - 角色（admin/moderator/member）
- `status` - 状态（active/inactive）
- `joined_at` - 加入时间

### CommunityEvent（社群活动）
- `title` - 活动标题
- `description` - 活动描述
- `location` - 活动地点
- `start_time` - 开始时间
- `end_time` - 结束时间
- `max_participants` - 最大参与人数
- `participant_count` - 当前参与人数
- `status` - 状态（upcoming/ongoing/completed/cancelled）

### EventRegistration（活动报名）
- `status` - 报名状态（registered/cancelled/attended）
- `note` - 备注

---

## ✅ 功能测试

### 社群功能测试
- [ ] 创建社群成功
- [ ] 社群列表显示正常
- [ ] 加入社群成功
- [ ] 退出社群成功
- [ ] 社群详情显示正常
- [ ] 社群成员列表正常

### 活动功能测试
- [ ] 创建活动成功
- [ ] 活动列表显示正常
- [ ] 报名活动成功
- [ ] 取消报名成功
- [ ] 活动详情显示正常
- [ ] 活动报名列表正常

### 用户资料测试
- [ ] 编辑个人资料成功
- [ ] 个人中心显示新增字段
- [ ] 头像上传成功
- [ ] 社群和活动标签页显示正常

---

## 🎨 UI 特性

- 响应式设计，适配移动设备
- Bootstrap 5 界面
- 社群封面图片支持
- 活动封面图片支持
- 成员头像显示
- 标签页切换内容
- 状态标签（活跃/暂停/已归档等）
- 分页显示

---

## 📸 上传文件说明

### 支持的目录
- `static/uploads/avatars/` - 用户头像
- `static/uploads/communities/` - 社群封面
- `static/uploads/events/` - 活动封面

### 文件限制
- 支持格式：PNG, JPG, JPEG, GIF, WEBP
- 最大文件大小：16MB
- 自动压缩图片（最大 1200x800）
- 自动生成缩略图（最大 400x300）

---

## 🔧 故障排查

### 迁移失败

**问题**：执行 `migrate_community.py` 时报错

**解决方案**：
1. 备份数据库：`python backup_database.py`
2. 检查错误信息
3. 确保没有其他应用正在使用数据库
4. 重新运行迁移脚本

### 图片上传失败

**问题**：上传图片时出错

**解决方案**：
1. 检查文件大小是否超过 16MB
2. 检查文件格式是否支持
3. 运行 `python init_uploads.py` 创建上传目录
4. 检查目录权限

### 社群无法加入

**问题**：无法加入社群

**解决方案**：
1. 检查社群是否为公开状态
2. 检查成员数是否已满
3. 检查是否已加入该社群

---

## 🚀 部署注意事项

### 数据库迁移
部署时需要执行：
```bash
python migrate_community.py
```

### 上传目录
确保服务器上存在以下目录：
```bash
mkdir -p static/uploads/avatars
mkdir -p static/uploads/communities
mkdir -p static/uploads/events
```

### 权限设置
确保应用有权限读写上传目录。

---

## 📝 后续扩展建议

1. **社群功能**
   - 社群帖子/讨论区
   - 社群分类和标签
   - 社群推荐算法
   - 社群统计和数据分析

2. **活动功能**
   - 活动日历视图
   - 活动提醒通知
   - 活动评价和反馈
   - 活动相册

3. **用户资料**
   - 社交账号绑定
   - 旅行足迹地图
   - 旅行相册
   - 好友关注系统

4. **通知系统**
   - 新活动通知
   - 活动即将开始提醒
   - 社群动态推送
   - 邮件通知

---

## 📞 技术支持

如遇问题，请：
1. 查看应用日志
2. 检查数据库表结构
3. 参考 `MIGRATION_GUIDE.md`
4. 联系开发团队

---

**版本**：v1.1.0
**更新日期**：2026
