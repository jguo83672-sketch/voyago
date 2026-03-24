# Voyago 部署到 PythonAnywhere 指南

## 一、前置准备

### 1.1 确认 PythonAnywhere 账户信息
- 用户名：`_______` (需要你填写)
- Web 应用 URL：`http://你的用户名.pythonanywhere.com`

### 1.2 本地准备代码
将项目文件打包成 zip：
```bash
# 在项目根目录执行
zip -r voyago.zip . -x "*.pyc" "__pycache__/*" ".git/*" "instance/*" "backups/*"
```

---

## 二、上传代码到 PythonAnywhere

### 2.1 打开 Bash Console
1. 登录 PythonAnywhere
2. 点击右上角 **$ Bash console 45358592** 打开控制台

### 2.2 上传文件
**方式一：使用文件管理器上传**
1. 点击 **Files** 标签
2. 进入 `/home/你的用户名/` 目录
3. 点击 **Upload a file** 上传 `voyago.zip`
4. 上传后在 Bash 控制台解压：

```bash
# 进入用户目录
cd ~

# 解压文件
unzip voyago.zip -d voyago

# 删除 zip 包（可选）
rm voyago.zip

# 进入项目目录
cd voyago

# 查看文件结构
ls -la
```

---

## 三、创建虚拟环境并安装依赖

### 3.1 创建虚拟环境
```bash
# 在项目目录下创建虚拟环境
python3 -m venv venv

# 激活虚拟环境
source venv/bin/activate
```

### 3.2 安装依赖
```bash
# 确保 pip 最新
pip install --upgrade pip

# 安装项目依赖
pip install -r requirements.txt

# 额外安装 gunicorn（生产环境服务器）
pip install gunicorn
```

---

## 四、配置环境变量

### 4.1 创建 .env 文件
```bash
# 在项目根目录创建 .env 文件
nano .env
```

### 4.2 复制以下内容到 .env（替换占位符）
```env
SECRET_KEY=请生成一个随机密钥（可使用命令：python -c 'import secrets; print(secrets.token_hex(32))'）

# 数据库配置（使用 PostgreSQL，PythonAnywhere 免费账户自带）
DATABASE_URL=postgresql://用户名:密码@用户名-db.postgres.database.azure.com:5432/默认数据库

# DeepSeek API（可选）
DEEPSEEK_API_KEY=你的DeepSeek_API_KEY

# Google Search API（可选）
SEARCH_API_KEY=你的Google_Search_API_KEY
SEARCH_ENGINE_ID=你的Search_Engine_ID
```

**获取 PostgreSQL 连接信息**：
1. 在 PythonAnywhere 点击 **Databases** 标签
2. 复制 **PostgreSQL** 连接字符串（格式：`postgresql://username:password@host:port/dbname`）

### 4.3 保存并退出
按 `Ctrl+X`，然后按 `Y`，再按 `Enter` 保存

---

## 五、配置 WSGI 应用

### 5.1 打开 Web 配置
1. 点击 **Web** 标签
2. 找到你的应用，点击 **WSGI configuration file** 链接

### 5.2 编辑 WSGI 文件
将原有内容替换为：

```python
import sys
import os

# 项目路径（将 你的用户名 替换为实际值）
project_home = '/home/你的用户名/voyago'

if project_home not in sys.path:
    sys.path = [project_home] + sys.path

# 导入 Flask 应用
from app import app as application

# 配置日志
import logging
logging.basicConfig(stream=sys.stderr, level=logging.INFO)
```

### 5.3 保存并重启
1. 点击 **Save**
2. 点击页面顶部的绿色 **Reload** 按钮

---

## 六、初始化数据库

### 6.1 初始化数据库表
```bash
# 在项目目录下，虚拟环境激活状态
cd ~/voyago
source venv/bin/activate

# 初始化数据库
python -c "from app import app, db; app.app_context().push(); db.create_all(); print('数据库初始化成功')"
```

### 6.2 创建管理员账户（可选）
```bash
# 创建管理脚本
cat > create_admin.py << 'EOF'
from app import app, db
from models import User
from werkzeug.security import generate_password_hash

with app.app_context():
    # 检查是否已存在
    if User.query.filter_by(username='admin').first():
        print('管理员账户已存在')
    else:
        admin = User(
            username='admin',
            email='admin@example.com',
            password_hash=generate_password_hash('admin123')
        )
        db.session.add(admin)
        db.session.commit()
        print('管理员创建成功！用户名: admin, 密码: admin123')
EOF

# 执行脚本
python create_admin.py
```

---

## 七、配置静态文件和上传目录

### 7.1 创建上传目录
```bash
mkdir -p static/uploads/destinations
mkdir -p static/uploads/itineraries
mkdir -p static/uploads/products
```

### 7.2 设置静态文件路径（PythonAnywhere Web 配置）
1. 在 **Web** 标签下找到 **Static files** 部分
2. 添加以下静态文件映射：
   - URL: `/static/` → Directory: `/home/你的用户名/voyago/static`

---

## 八、测试访问

### 8.1 检查应用日志
1. 在 **Web** 标签点击 **Log files**
2. 查看 `error.log` 和 `server.log` 确认无错误

### 8.2 访问应用
打开浏览器访问：
```
https://你的用户名.pythonanywhere.com
```

---

## 九、常见问题排查

### 问题 1：500 Internal Server Error
```bash
# 查看错误日志
tail -f ~/logs/error.log

# 常见原因：
# - 依赖未安装完整 → 重新运行 pip install -r requirements.txt
# - .env 文件配置错误 → 检查环境变量
# - 数据库连接失败 → 检查 DATABASE_URL
```

### 问题 2：静态文件 404
确保在 Web 配置中添加了静态文件路径映射。

### 问题 3：上传文件失败
```bash
# 检查上传目录权限
chmod 755 ~/voyago/static/uploads
chmod -R 755 ~/voyago/static/uploads/*
```

### 问题 4：Python 版本不匹配
```bash
# 检查 Python 版本
python3 --version

# 如果不是 3.10+，在 PythonAnywhere Web 配置中选择正确的 Python 版本
```

---

## 十、后续更新代码

### 更新流程
```bash
# 1. 上传新的 voyago.zip 到 Files
# 2. 在 Bash 中解压覆盖
cd ~
unzip -o voyago.zip -d voyago

# 3. 激活虚拟环境
cd voyago
source venv/bin/activate

# 4. 更新依赖（如有变更）
pip install -r requirements.txt

# 5. 重启应用
# 在 PythonAnywhere Web 标签点击 Reload 按钮
```

---

## 十一、部署检查清单

- [ ] 代码已上传到 `/home/你的用户名/voyago`
- [ ] 虚拟环境已创建并激活
- [ ] 所有依赖已安装（包括 gunicorn）
- [ ] .env 文件已配置（SECRET_KEY, DATABASE_URL）
- [ ] WSGI 配置文件已更新
- [ ] 数据库已初始化
- [ ] 静态文件路径已映射
- [ ] 上传目录已创建
- [ ] 应用已重新加载
- [ ] 测试访问成功

---

## 联系支持

如遇到问题，可以在 PythonAnywhere 的 **Console** 中运行以下命令获取帮助：

```bash
# 测试 Flask 应用是否正常启动
python -c "from app import app; print('Flask 应用导入成功')"
```

祝部署顺利！🚀
