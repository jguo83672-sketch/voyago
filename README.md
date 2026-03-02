# Voyago - 旅行攻略分享网站

一个基于 Flask 的旅行攻略分享平台，帮助用户发现目的地、分享旅行攻略、规划完美行程。

## 核心功能

### 1. 目的地管理
- 浏览热门目的地
- 目的地详情展示
- 目的地搜索和筛选

### 2. 攻略分享
- 发布旅行攻略
- 攻略分类浏览（美食、景点、购物、交通等）
- 攻略评论和收藏

### 3. 行程规划
- 创建个性化旅行行程
- 每日详细活动安排
- 行程预算管理
- 行程分享和收藏

### 4. 用户功能
- 用户注册和登录
- 个人中心管理
- 我的行程和攻略
- 收藏管理

## 技术栈

- **后端**: Flask 3.0.0
- **数据库**: SQLite (使用 SQLAlchemy ORM)
- **前端**: Bootstrap 5 + Jinja2 模板
- **认证**: Flask-Login

## 项目结构

```
voyago v1.0.0/
├── app.py                 # Flask 应用主文件
├── models.py              # 数据库模型
├── routes.py              # 路由和视图函数
├── requirements.txt       # Python 依赖
├── .env                   # 环境变量
├── templates/             # Jinja2 模板
│   ├── base.html         # 基础模板
│   ├── index.html        # 首页
│   ├── destinations.html # 目的地列表
│   ├── destination_detail.html
│   ├── guides.html       # 攻略列表
│   ├── guide_detail.html
│   ├── itineraries.html  # 行程列表
│   ├── itinerary_detail.html
│   ├── login.html
│   ├── register.html
│   ├── profile.html      # 个人中心
│   ├── create_itinerary.html
│   ├── create_guide.html
│   ├── favorites.html    # 收藏
│   └── search.html       # 搜索结果
└── static/               # 静态资源
    ├── css/
    │   └── style.css
    └── js/
        └── main.js
```

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置环境变量

编辑 `.env` 文件，修改以下配置：

```
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///voyago.db
```

### 3. 初始化数据库

```bash
python app.py
```

首次运行会自动创建数据库表。

### 4. 启动应用

```bash
python app.py
```

应用将在 `http://127.0.0.1:5000` 启动。

## 数据库模型

### User (用户)
- 用户名、邮箱、密码
- 头像、个人简介
- 关联的行程、攻略、收藏

### Destination (目的地)
- 名称、国家、城市
- 描述、封面图
- 评分、浏览量
- 标签

### Itinerary (行程)
- 标题、描述
- 天数、日期范围
- 预算
- **支持多个目的地**（多对多关系）
- 每日详细安排

### Guide (攻略)
- 标题、内容
- 分类
- 浏览量、收藏量、评论数

### Comment (评论)
- 评论内容
- 关联用户和攻略

### Favorite (收藏)
- 收藏的行程或攻略

## 主要路由

| 路由 | 说明 |
|------|------|
| `/` | 首页 |
| `/destinations` | 目的地列表 |
| `/destination/<id>` | 目的地详情 |
| `/create-destination` | 添加目的地（需登录） |
| `/guides` | 攻略列表 |
| `/guide/<id>` | 攻略详情 |
| `/create-guide` | 发布攻略（需登录） |
| `/itineraries` | 行程列表 |
| `/itinerary/<id>` | 行程详情 |
| `/create-itinerary` | 创建行程（需登录） |
| `/register` | 用户注册 |
| `/login` | 用户登录 |
| `/profile` | 个人中心 |
| `/search` | 搜索 |

## 功能特性

- **响应式设计**: 适配桌面和移动设备
- **实时搜索**: 全文搜索目的地、攻略、行程
- **收藏系统**: 收藏喜欢的行程和攻略
- **评论功能**: 对攻略进行评论互动
- **分页展示**: 大量数据分页加载
- **用户认证**: 完整的注册登录流程
- **图片上传**: 支持目的地、攻略、行程的封面图片上传
- **图片处理**: 自动压缩和优化图片，生成缩略图

## 开发计划

- [ ] 图片上传功能
- [ ] 用户头像上传
- [ ] 社交分享
- [ ] 行程导出为 PDF
- [ ] 地图集成
- [ ] 邮件通知
- [ ] 数据分析统计

## License

MIT License
