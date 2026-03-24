# 快速开始指南

欢迎使用 Voyago！本指南将在 5 分钟内帮你快速启动项目。

## 前置要求

- Python 3.10 或更高版本
- pip（Python 包管理器）
- Git（可选，用于版本控制）

## 一、安装依赖（30 秒）

```bash
# 进入项目目录
cd "voyago v1.0.0"

# 安装所有依赖包
pip install -r requirements.txt
```

等待安装完成...

## 二、配置环境变量（2 分钟）

### 方式一：使用示例文件（推荐）

```bash
# 复制示例配置文件
cp .env.example .env

# 编辑配置文件
nano .env  # 或使用你喜欢的编辑器
```

### 必需配置项

```env
# Flask 密钥（必须）
SECRET_KEY=请运行生成：python -c 'import secrets; print(secrets.token_hex(32))'

# 数据库（开发环境用 SQLite，生产用 PostgreSQL）
DATABASE_URL=sqlite:///voyago.db
```

### 可选配置项（功能需要）

```env
# DeepSeek AI（OCR 分类需要）
DEEPSEEK_API_KEY=sk-your-deepseek-key-here

# 百度 OCR（图片识别需要）
BAIDU_OCR_API_KEY=your-baidu-api-key
BAIDU_OCR_SECRET_KEY=your-baidu-secret-key

# Google Search（搜索功能需要）
SEARCH_API_KEY=your-google-api-key
SEARCH_ENGINE_ID=your-search-engine-id
```

## 三、初始化数据库（30 秒）

```bash
# 方式一：首次运行自动初始化（推荐）
python app.py

# 方式二：手动初始化（可选）
python init_destination_regions.py  # 初始化目的地数据
python init_products.py           # 初始化商品数据
```

## 四、启动应用（5 秒）

```bash
python app.py
```

看到以下信息表示启动成功：

```
 * Running on http://127.0.0.1:5000
 * Restarting with stat
```

## 五、访问应用

在浏览器中打开：

```
http://127.0.0.1:5000
```

## 六、快速测试

### 1. 注册账户

访问 `http://127.0.0.1:5000/register`，填写信息注册。

### 2. 创建第一个行程

1. 登录后点击导航栏"创建行程"
2. 填写标题、天数、目的地
3. 点击"AI 智能规划"自动生成每日安排
4. 发布行程

### 3. 发布攻略（OCR 测试）

1. 点击导航栏"发布攻略"
2. 点击右上角"OCR 导入"按钮
3. 上传一张旅行攻略截图
4. 等待 AI 自动识别和分类
5. 编辑后发布

### 4. 体验旅行准备

1. 进入刚创建的行程详情
2. 点击"开始准备"按钮
3. 查看自动生成的准备清单
4. 浏览推荐的酒店和机票

### 5. 浏览旅行商店

1. 导航栏点击"旅行商店"
2. 浏览商品分类
3. 添加商品到购物车
4. 完成订单流程

## 常见启动问题

### 问题 1：ModuleNotFoundError

```
ModuleNotFoundError: No module named 'flask'
```

**解决方法**：
```bash
pip install -r requirements.txt
```

### 问题 2：数据库错误

```
sqlite3.OperationalError: unable to open database file
```

**解决方法**：
```bash
# 创建 instance 目录
mkdir -p instance
```

### 问题 3：SECRET_KEY 配置警告

```
RuntimeWarning: SECRET_KEY is not set
```

**解决方法**：
确保 `.env` 文件中有 `SECRET_KEY` 配置。

### 问题 4：端口被占用

```
Address already in use
```

**解决方法**：
```bash
# 方法一：停止占用端口的程序
# Windows:
netstat -ano | findstr :5000
taskkill /PID <进程ID> /F

# Linux/Mac:
lsof -ti:5000 | xargs kill -9

# 方法二：更换端口
# 在 app.py 最后添加：
app.run(debug=True, port=5001)
```

## 下一步

### 浏览完整文档

- **项目总览**：[README.md](README.md)
- **OCR 功能**：[OCR_IMPORT_GUIDE.md](OCR_IMPORT_GUIDE.md)
- **旅行准备**：[TRAVEL_PREP_README.md](TRAVEL_PREP_README.md)
- **部署指南**：[PYTHONANYWHERE_DEPLOY.md](PYTHONANYWHERE_DEPLOY.md)

### 开发建议

1. **使用虚拟环境**
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate      # Windows
```

2. **启用调试模式**
在 `.env` 中设置：
```env
DEBUG=True
```

3. **查看日志**
所有错误和警告会输出到控制台，便于调试。

4. **备份数据库**
定期备份 `instance/voyago.db` 文件。

### 准备部署

在部署到生产环境前：

1. 阅读 [PYTHONANYWHERE_DEPLOY.md](PYTHONANYWHERE_DEPLOY.md)
2. 配置 PostgreSQL 数据库连接
3. 设置 `DEBUG=False`
4. 配置生产环境的 WSGI
5. 测试所有功能

## 需要帮助？

- 查看详细文档：[DOCS_INDEX.md](DOCS_INDEX.md)
- 提交 Issue：[GitHub Issues](项目仓库/issues)
- 查看更新日志：[CHANGELOG.md](CHANGELOG.md)

---

**祝使用愉快！** 🎉🌍✈️
