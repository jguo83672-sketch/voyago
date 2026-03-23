# 文档目录

本目录包含 Voyago 项目的详细功能说明文档。

## 📚 可用文档

| 文档 | 说明 |
|--------|------|
| **README.md** | 项目总览、快速开始、完整功能说明 |
| **OCR_IMPORT_GUIDE.md** | OCR 智能导入功能详细说明 |
| **TRAVEL_PREP_README.md** | 旅行准备模块功能说明 |
| **PYTHONANYWHERE_DEPLOY.md** | PythonAnywhere 部署指南 |

## 🚀 快速导航

### 新用户
1. 首先阅读 **[README.md](README.md)** 了解项目概况
2. 按照"快速开始"步骤配置和运行项目
3. 查看各功能模块的详细文档

### 功能模块详解

#### OCR 智能导入
查看 **[OCR_IMPORT_GUIDE.md](OCR_IMPORT_GUIDE.md)** 了解：
- 百度 OCR 文字识别配置
- DeepSeek AI 自动分类
- 攻略识别技巧和最佳实践
- API 配置说明

#### 旅行准备系统
查看 **[TRAVEL_PREP_README.md](TRAVEL_PREP_README.md)** 了解：
- 出行预订系统（酒店、机票推荐）
- 旅行准备清单
- 数据模型和技术架构
- 扩展建议

### 部署相关
查看 **[PYTHONANYWHERE_DEPLOY.md](PYTHONANYWHERE_DEPLOY.md)** 了解：
- PythonAnywhere 平台部署步骤
- 环境配置
- 常见问题排查
- 代码更新流程

## 📋 检查清单

### 开发环境搭建
- [ ] 已阅读 README.md
- [ ] 已安装 Python 3.10+
- [ ] 已安装所有依赖 (`pip install -r requirements.txt`)
- [ ] 已配置 `.env` 文件
- [ ] 已初始化数据库
- [ ] 应用成功启动

### 功能测试
- [ ] 用户注册/登录正常
- [ ] 目的地浏览和筛选正常
- [ ] 创建行程和攻略正常
- [ ] OCR 导入功能测试
- [ ] 旅行准备功能测试
- [ ] 电商购物流程测试

### 部署准备
- [ ] 已阅读部署指南
- [ ] 已准备生产环境配置
- [ ] 已配置数据库连接
- [ ] 已配置 API Keys
- [ ] 已设置静态文件路径
- [ ] 已测试部署访问

## 🔗 相关链接

- [Flask 官方文档](https://flask.palletsprojects.com/)
- [SQLAlchemy 文档](https://docs.sqlalchemy.org/)
- [Bootstrap 5 文档](https://getbootstrap.com/)
- [百度智能云 OCR](https://cloud.baidu.com/product/ocr.html)
- [DeepSeek API](https://platform.deepseek.com/)

## 💡 使用建议

### 开发时
1. 使用虚拟环境隔离依赖
2. 定期备份数据库文件
3. 使用 Git 版本控制
4. 在提交前测试所有功能

### 部署前
1. 确保所有环境变量已正确配置
2. 检查敏感信息是否已移除（如 API Keys 不应提交到代码库）
3. 测试生产环境的数据库迁移
4. 准备回滚方案

---

**文档更新日期**：2026年3月
**项目版本**：v1.0.0
