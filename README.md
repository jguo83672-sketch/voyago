# Voyago - 智能旅行规划与攻略分享平台

一个基于 Flask 的全功能旅行平台，集成 AI 智能规划、攻略分享、社群互动、旅行准备和电商服务。

![Voyago](https://img.shields.io/badge/version-1.0.0-blue)
![Python](https://img.shields.io/badge/python-3.10+-green)
![Flask](https://img.shields.io/badge/flask-3.0.0-red)

## 核心功能

### 1. 目的地管理
- **多分类浏览**：国内游、出国游、邮轮游、周末近郊游、主题乐园
- **智能筛选**：按省份、大洲、地区、国家筛选
- **目的地详情**：评分、评论、攻略、行程关联

### 2. 攻略分享系统
- **OCR 智能导入**：百度 OCR + DeepSeek AI 自动识别和分类
- **多分类支持**：美食、交通、住宿、景点、购物等 16 种分类
- **互动功能**：评论、点赞、收藏
- **发布管理**：支持封面图片、标签编辑

### 3. AI 行程规划
- **智能规划**：根据目的地、天数、预算自动生成行程
- **多目的地支持**：一个行程可关联多个目的地
- **每日安排**：详细的活动时间表
- **行程分享**：公开/私有设置，分享给其他用户

### 4. 旅行社群
- **创建社群**：基于目的地组建旅行社群
- **活动组织**：发起线下活动，成员报名参与
- **权限管理**：管理员、版主、成员角色

### 5. 旅行准备模块
- **智能推荐**：酒店、机票推荐与预订
- **准备清单**：自动生成出行物品清单
- **行程关联**：为每个行程提供专属准备页面

### 6. 旅行用品电商
- **商品商城**：行李箱、洗漱包、转换插头等旅行用品
- **购物车系统**：添加商品、数量管理、运费计算
- **订单管理**：订单状态跟踪、订单详情查看
- **商品评价**：用户评分、评论、图片上传

### 7. 用户中心
- **个人资料**：头像、昵称、简介、旅行偏好
- **足迹管理**：记录去过的地方
- **我的内容**：我的行程、攻略、收藏管理

## 技术栈

| 组件 | 技术 |
|--------|------|
| **后端框架** | Flask 3.0.0 |
| **数据库** | SQLite (本地) / PostgreSQL (生产) |
| **ORM** | SQLAlchemy |
| **前端** | Bootstrap 5 + Jinja2 模板 |
| **认证** | Flask-Login |
| **OCR 服务** | 百度智能云 OCR |
| **AI 分类** | DeepSeek Chat API |
| **搜索** | Google Custom Search API |

## 项目结构

```
voyago v1.0.0/
├── app.py                      # Flask 应用主文件
├── models.py                   # SQLAlchemy 数据库模型
├── routes.py                   # 路由和视图函数
├── requirements.txt            # Python 依赖包
├── .env                      # 环境变量配置
├── .env.example              # 环境变量示例
├── .env.production         # 生产环境配置
├── Procfile                 # Heroku/PythonAnywhere 部署配置
├── runtime.txt              # Python 版本要求
├── wsgi_production.py      # 生产环境 WSGI 配置
├──
├── # 核心服务模块
├── ai_planner.py            # AI 行程规划服务
├── travel_prep.py           # 旅行准备服务
├── ocr_service.py           # 百度 OCR 文字识别
├── guide_classifier.py       # DeepSeek AI 攻略分类
├── web_search.py           # 搜索服务
├── utils.py               # 工具函数（文件上传等）
├── init_destination_regions.py   # 目的地区域初始化
├── init_products.py       # 商品数据初始化
├──
├── templates/              # Jinja2 模板目录
│   ├── base.html         # 基础模板
│   ├── index.html        # 首页
│   ├── destinations.html  # 目的地列表
│   ├── destination_detail.html
│   ├── guides.html       # 攻略列表
│   ├── guide_detail.html
│   ├── itineraries.html  # 行程列表
│   ├── itinerary_detail.html
│   ├── create_itinerary.html
│   ├── create_guide.html
│   ├── import_guide_ocr.html    # OCR 导入页面
│   ├── profile.html      # 个人中心
│   ├── favorites.html    # 收藏管理
│   ├── communities.html  # 社群列表
│   ├── community_detail.html
│   ├── travel_footprints.html # 旅行足迹
│   ├── itinerary_prepare.html  # 旅行准备页面
│   ├── travel_shop.html       # 电商首页
│   ├── product_detail.html
│   ├── cart.html
│   ├── checkout.html
│   └── orders.html
├──
└── static/                # 静态资源
    ├── css/
    │   └── style.css
    ├── js/
    │   └── main.js
    └── uploads/         # 上传文件目录
        ├── destinations/
        ├── itineraries/
        └── products/
```

## 快速开始

### 1. 克隆项目

```bash
git clone <repository-url>
cd voyago
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 配置环境变量

复制 `.env.example` 为 `.env` 并修改配置：

```bash
cp .env.example .env
```

编辑 `.env` 文件：

```env
# Flask 配置
SECRET_KEY=your-secret-key-here
DEBUG=True

# 数据库配置（开发环境使用 SQLite）
DATABASE_URL=sqlite:///voyago.db

# DeepSeek AI（用于 OCR 分类）
DEEPSEEK_API_KEY=your-deepseek-api-key

# 百度 OCR（用于图片文字识别）
BAIDU_OCR_API_KEY=your-baidu-ocr-api-key
BAIDU_OCR_SECRET_KEY=your-baidu-ocr-secret-key

# Google Search（可选，用于搜索功能）
SEARCH_API_KEY=your-google-search-api-key
SEARCH_ENGINE_ID=your-search-engine-id
```

### 4. 初始化数据库

```bash
python init_destination_regions.py  # 初始化目的地数据（可选）
python init_products.py           # 初始化商品数据（可选）
python app.py                     # 首次运行自动创建数据库表
```

### 5. 启动应用

```bash
python app.py
```

应用将在 `http://127.0.0.1:5000` 启动。

## 数据库模型

### 核心模型

| 模型 | 说明 |
|------|------|
| **User** | 用户信息（用户名、邮箱、密码、头像、旅行偏好） |
| **Destination** | 目的地（名称、分类、省份/国家、评分、浏览量） |
| **Itinerary** | 行程（标题、天数、日期、预算、多目的地关联） |
| **ItineraryDay** | 行程每日安排（活动列表） |
| **Guide** | 攻略（标题、内容、分类、浏览量、点赞） |
| **Community** | 社群（名称、描述、成员上限、状态） |
| **CommunityMember** | 社群成员（角色、状态） |
| **CommunityEvent** | 社群活动（时间、地点、参与者） |
| **TravelFootprint** | 旅行足迹（目的地、日期、评分） |

### 旅行准备模块

| 模型 | 说明 |
|------|------|
| **TravelPrep** | 旅行准备记录（入住/退房日期、人数、预算） |
| **HotelRecommendation** | 酒店推荐（名称、评分、价格、预订链接） |
| **FlightRecommendation** | 机票推荐（航班号、时间、价格、预订链接） |

### 电商模块

| 模型 | 说明 |
|------|------|
| **TravelProduct** | 商品（名称、分类、价格、库存、评分） |
| **ProductReview** | 商品评论（评分、内容、图片） |
| **CartItem** | 购物车商品（用户、商品、数量） |
| **Order** | 订单（订单号、收货地址、支付、状态） |
| **OrderItem** | 订单商品项（快照数据） |

### 互动模型

| 模型 | 说明 |
|------|------|
| **Comment/Comment2** | 评论（攻略、行程、目的地的评论） |
| **Favorite/Favorite2** | 收藏（收藏行程、攻略、目的地） |
| **EventRegistration** | 活动报名（用户、活动、状态） |

## 主要路由

### 公开路由

| 路由 | 说明 |
|--------|------|
| `/` | 首页 |
| `/destinations` | 目的地列表（支持分类和筛选） |
| `/destination/<id>` | 目的地详情 |
| `/guides` | 攻略列表 |
| `/guide/<id>` | 攻略详情 |
| `/itineraries` | 行程列表 |
| `/itinerary/<id>` | 行程详情 |
| `/communities` | 社群列表 |
| `/community/<id>` | 社群详情 |
| `/travel-shop` | 旅行用品商店 |

### 用户路由（需登录）

| 路由 | 说明 |
|--------|------|
| `/register` | 用户注册 |
| `/login` | 用户登录 |
| `/logout` | 用户登出 |
| `/profile` | 个人中心 |
| `/create-destination` | 添加目的地 |
| `/edit-destination/<id>` | 编辑目的地 |
| `/create-itinerary` | 创建行程 |
| `/create-guide` | 发布攻略 |
| `/import-guide-ocr` | OCR 导入攻略 |
| `/itinerary/<id>/prepare` | 旅行准备页面 |
| `/cart` | 购物车 |
| `/checkout` | 结账 |
| `/orders` | 订单列表 |

## 特色功能详解

### OCR 智能导入

系统支持通过上传旅行攻略截图，自动识别文字并智能分类：

1. **上传图片**：支持 JPG、PNG、JPEG 等格式
2. **OCR 识别**：百度智能云高精度文字识别
3. **AI 分类**：DeepSeek 自动识别攻略类型（美食、交通、住宿等 16 种）
4. **标题生成**：AI 自动生成吸引人的标题
5. **目的地提取**：智能提取攻略中的目的地信息

### 目的地分类系统

支持 5 种目的地类型：

| 类型 | 说明 | 筛选维度 |
|------|------|----------|
| **国内游** | 中国境内目的地 | 按省份筛选（北京、上海、浙江等） |
| **出国游** | 境外目的地 | 按大洲→地区→国家筛选 |
| **邮轮游** | 邮轮度假 | 按省份/地区筛选 |
| **周末近郊游** | 城市周边短途 | 按省份/地区筛选 |
| **主题乐园** | 迪士尼、长隆、环球影城等 | 按省份/地区筛选 |

### 旅行准备清单

自动生成的准备清单包含：

- **证件类**：身份证、护照、签证、驾驶证
- **衣物类**：根据天数和目的地天气推荐
- **洗漱用品**：牙刷、牙膏、洗浴用品
- **电子设备**：手机、充电器、相机
- **药品类**：常用药品、特殊药品
- **其他**：转换插头、雨伞、旅行枕

## 部署指南

### 部署到 PythonAnywhere

详细的部署步骤请参考：[PYTHONANYWHERE_DEPLOY.md](PYTHONANYWHERE_DEPLOY.md)

快速流程：

1. 准备代码包并上传
2. 创建虚拟环境并安装依赖
3. 配置环境变量（.env 文件）
4. 配置 WSGI 应用
5. 初始化数据库
6. 配置静态文件和上传目录
7. 测试访问

### 环境变量配置

**生产环境需要配置以下变量：**

```env
SECRET_KEY=<强随机密钥>
DEBUG=False
DATABASE_URL=postgresql://user:pass@host/db
```

获取 API Keys：

- **DeepSeek**: https://platform.deepseek.com/
- **百度 OCR**: https://cloud.baidu.com/
- **Google Search**: https://console.cloud.google.com/

## 开发计划

### 短期优化
- [ ] 支持多图片批量 OCR 识别
- [ ] 添加商品收藏功能
- [ ] 支持订单取消和退款
- [ ] 添加物流查询接口

### 中期优化
- [ ] 接入真实酒店/机票 API（携程、飞猪）
- [ ] 增加更多商品分类（户外装备、摄影器材）
- [ ] 支持商品评价图片上传
- [ ] 添加优惠券系统

### 长期规划
- [ ] AI 智能推荐商品（基于行程目的地）
- [ ] 跨境电商（海外商品直邮）
- [ ] 积分兑换系统
- [ ] 会员体系
- [ ] 地图集成
- [ ] 邮件通知
- [ ] 数据分析统计

## 常见问题

### Q: 如何重置数据库？

```bash
# 删除数据库文件
rm instance/voyago.db

# 重新运行应用初始化
python app.py
```

### Q: OCR 识别失败怎么办？

检查以下内容：
- 图片是否清晰（避免反光、模糊）
- 网络连接是否正常
- API 配置是否正确（BAIDU_OCR_API_KEY 和 BAIDU_OCR_SECRET_KEY）

### Q: AI 分类不准确怎么办？

系统会自动分类，但可以在编辑页面手动修改为更合适的类型。

### Q: 上传文件大小限制？

- 默认限制：32MB
- 可在 `app.py` 中修改 `app.config['MAX_CONTENT_LENGTH']`

## 贡献指南

欢迎贡献代码、报告问题或提出建议！

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## License

MIT License

## 联系与支持

如有问题或建议，请通过以下方式联系：

- 提交 Issue
- 发送邮件
- 查看详细文档：
  - [OCR 导入功能说明](OCR_IMPORT_GUIDE.md)
  - [旅行准备模块说明](TRAVEL_PREP_README.md)
  - [PythonAnywhere 部署指南](PYTHONANYWHERE_DEPLOY.md)

---

**Voyago** - 让每一次旅行都完美无缺 🌍✈️
