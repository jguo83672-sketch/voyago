# Voyago 部署指南

完整的 PythonAnywhere 部署指南。

---

## 🚀 快速开始（5-10 分钟）

### 前置要求
- GitHub 账户（可选，推荐）
- PythonAnywhere 账户（免费）
- SECRET_KEY（访问 https://randomkeygen.com/ 选择 "CodeIgniter Encryption Keys"）

---

## 📋 部署步骤

### 第 1 步：准备本地代码（2 分钟）

```bash
# 1. 备份数据库
python backup_database.py

# 2. 运行部署准备工具
START_DEPLOYMENT.bat
```

---

### 第 2 步：推送到 GitHub（可选，2 分钟）

```bash
# 初始化 Git
git init
git add .

# 排除敏感文件
echo ".env" >> .gitignore
echo "backups/" >> .gitignore
echo "instance/" >> .gitignore
echo "__pycache__/" >> .gitignore
echo "*.pyc" >> .gitignore
echo ".snapshots/" >> .gitignore

# 提交代码
git commit -m "准备部署"
git remote add origin https://github.com/你的用户名/voyago.git
git branch -M main
git push -u origin main
```

---

### 第 3 步：PythonAnywhere 部署（5-10 分钟）

#### 3.1 注册账户

1. 访问：https://www.pythonanywhere.com
2. 点击 "Pricing & signup"
3. 选择 "Beginner"（免费）
4. 完成注册并验证邮箱

#### 3.2 创建 Web 应用

1. 登录后点击左侧 "Web"
2. 点击 "Add a new web app"
3. 选择 "Manual configuration"
4. 选择 "Python 3.12"
5. 点击 "Next"

#### 3.3 上传代码

**方法 A：使用 Git（推荐）**

在 PythonAnywhere 的 "Bash" 控制台：

```bash
cd ~
git clone https://github.com/你的用户名/voyago.git
cd voyago
```

**方法 B：直接上传文件**

1. 在 PythonAnywhere 左侧菜单点击 "Files"
2. 进入 `/home/你的用户名/`
3. 创建 `voyago` 文件夹
4. 点击 "Upload files" 上传所有文件

#### 3.4 安装依赖

在 Bash 控制台执行：

```bash
cd ~/voyago

# 创建虚拟环境
python3.12 -m venv venv

# 激活虚拟环境
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
pip install gunicorn
```

#### 3.5 创建必要目录

```bash
mkdir -p instance
mkdir -p static/uploads/destinations
mkdir -p static/uploads/guides
mkdir -p static/uploads/itineraries
```

#### 3.6 上传数据库文件

**方法 A：使用 FileZilla**

1. 下载 FileZilla：https://filezilla-project.org/
2. 连接到 PythonAnywhere：
   - 主机：`ssh.pythonanywhere.com`
   - 用户：您的 PythonAnywhere 用户名
   - 密码：您的 PythonAnywhere 密码
3. 上传 `instance/voyago.db` 到 `/home/你的用户名/voyago/instance/`

**方法 B：使用 scp 命令**

在本地 PowerShell 运行：

```powershell
scp "d:\研究生课程\IBA6318\voyago v1.0.0\instance\voyago.db" 你的用户名@ssh.pythonanywhere.com:/home/你的用户名/voyago/instance/
```

#### 3.7 配置 Web 应用

在 PythonAnywhere 的 "Web" 页面修改配置：

**1. WSGI 配置文件**

点击 "WSGI configuration file" 链接，修改为：

```python
import sys
import os

project_home = '/home/你的用户名/voyago'

if project_home not in sys.path:
    sys.path = [project_home] + sys.path

from app import app as application
```

**2. Virtualenv 路径**

```
/home/你的用户名/voyago/venv
```

**3. Working directory**

```
/home/你的用户名/voyago
```

**4. Environment variables**

添加以下环境变量：

| 变量名 | 值 |
|--------|-----|
| `SECRET_KEY` | 您在步骤 1 生成的随机密钥（32 字符） |
| `FLASK_ENV` | `production` |
| `DATABASE_URL` | `sqlite:////home/你的用户名/voyago/instance/voyago.db` |

#### 3.8 配置静态文件映射

在 "Web" 页面的 "Static files" 部分：

| URL directory | Directory |
|---------------|-----------|
| `/static/` | `/home/你的用户名/voyago/static/` |

#### 3.9 重载应用

点击绿色的 "Reload" 按钮

---

### 第 4 步：访问应用（1 分钟）

访问：`https://你的用户名.pythonanywhere.com`

---

## ✅ 部署检查清单

### 功能测试

- [ ] 首页正常访问
- [ ] 目的地列表和详情正常显示
- [ ] 用户可以注册和登录
- [ ] 攻略功能正常
- [ ] 行程功能正常
- [ ] 搜索功能正常
- [ ] 图片正常显示

### 数据验证

- [ ] 现有目的地数据完整
- [ ] 现有用户数据完整
- [ ] 现有攻略数据完整

---

## 🔧 故障排查

### 问题 1：500 错误

**检查步骤：**

```bash
# 在 PythonAnywhere Bash 查看日志
tail -n 50 ~/voyago/error.log

# 检查 Python 版本
python3.12 --version

# 检查依赖包
pip list
```

**常见原因：**
- 数据库文件路径错误
- 缺少依赖包
- 环境变量未设置

---

### 问题 2：数据库连接失败

**检查环境变量：**

```bash
echo $DATABASE_URL
```

验证路径格式：`sqlite:////home/你的用户名/voyago/instance/voyago.db`（4 个斜杠）

---

### 问题 3：静态文件 404

确保静态文件映射配置正确：

| URL directory | Directory |
|---------------|-----------|
| `/static/` | `/home/你的用户名/voyago/static/` |

---

## 💾 数据备份

### 本地备份

每次部署前运行：

```bash
python backup_database.py
```

备份文件保存在：`backups/` 目录

### 服务器备份

在 PythonAnywhere 设置自动备份（Cron 任务）：

```bash
0 2 * * * cp /home/你的用户名/voyago/instance/voyago.db /home/你的用户名/backups/voyago_$(date +\%Y\%m\%d).db
```

### 定期下载

使用 FileZilla 或 scp 定期下载备份到本地。

---

## 📱 自定义域名（可选）

### 配置步骤

1. **在 PythonAnywhere 添加域名**
   - 进入 Web 页面
   - 点击 "Add a domain"
   - 输入您的域名

2. **配置 DNS 记录**
   - 在域名提供商处添加 CNAME 记录
   - 主机记录：`www`
   - 记录值：`你的用户名.pythonanywhere.com`

3. **等待生效**
   - DNS 生效需要 5-10 分钟

---

## 📊 性能预期

### 免费账户限制

- **并发请求**：适中
- **CPU 时间**：每日有限额度
- **带宽**：有限
- **存储**：500 MB

### 实际表现

| 访问量 | 表现 |
|--------|------|
| 10-50 用户/天 | ✅ 完全满足 |
| 50-200 用户/天 | ✅ 基本满足 |
| 200+ 用户/天 | ⚠️ 建议升级付费账户 |

---

## 💰 成本总结

### PythonAnywhere 免费账户

| 项目 | 费用 |
|------|------|
| Web 应用 | $0/月 |
| 域名 | $0/月（使用子域名） |
| SSL 证书 | $0/月（自动提供） |
| 存储 | 500 MB |
| 数据库 | SQLite（免费） |

**总成本：$0/月** ✅

### 可选费用

| 项目 | 费用 | 说明 |
|------|------|------|
| 自定义域名 | $10-15/年 | 向域名服务商购买 |
| 付费升级 | $5/月起 | 更高性能和资源 |

---

## 📞 获取帮助

- PythonAnywhere 帮助：https://help.pythonanywhere.com/
- PythonAnywhere 论坛：https://www.pythonanywhere.com/forums/

---

## 🎉 完成！

您的 Voyago 平台现在已经在线部署！可以分享给其他人访问了。
