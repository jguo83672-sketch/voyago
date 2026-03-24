# 团队协作指南

## 🌿 分支策略

本项目采用 Git Flow 工作流：

```
main (生产环境)
  ↑
  ↓ 合并
develop (开发环境)
  ↑
  ↓
feature/* (功能分支)
hotfix/* (紧急修复)
```

### 分支说明

| 分支 | 用途 | 合并方向 |
|------|------|----------|
| **main** | 生产环境代码，稳定版本 | develop → main |
| **develop** | 开发环境，日常开发 | feature → develop |
| **feature/xxx** | 新功能开发 | feature → develop |
| **hotfix/xxx** | 紧急修复 | hotfix → develop + main |

---

## 🚀 开发流程

### 1. 开始新功能开发

```bash
# 1. 切换到 develop 分支
git checkout develop

# 2. 拉取最新代码
git pull origin develop

# 3. 创建功能分支（功能名示例）
git checkout -b feature/user-authentication

# 4. 开始开发...
```

### 2. 提交代码

```bash
# 1. 查看更改
git status

# 2. 添加修改的文件
git add .

# 3. 提交（使用清晰的消息）
git commit -m "feature-add-user-login"
```

**提交消息格式：**

```
type-scope-short-description
```

| Type | 说明 |
|------|------|
| `feature` | 新功能 |
| `fix` | Bug 修复 |
| `docs` | 文档更新 |
| `style` | 代码格式调整 |
| `refactor` | 代码重构 |
| `test` | 测试相关 |
| `chore` | 构建/工具更新 |

### 3. 推送到远程

```bash
# 1. 推送功能分支
git push -u origin feature/user-authentication
```

### 4. 创建 Pull Request (PR)

1. 访问 GitHub 仓库页面
2. 点击 "Pull requests" → "New pull request"
3. 选择 `feature/user-authentication` → `develop`
4. 填写 PR 描述：
   - **标题**：清晰描述功能
   - **描述**：说明变更内容、测试情况
5. 提交 PR 并等待代码审查

### 5. 合并代码

**PR 审查通过后：**

```bash
# 1. 切换到 develop 分支
git checkout develop

# 2. 拉取最新代码（已合并的 PR）
git pull origin develop

# 3. 删除本地功能分支
git branch -d feature/user-authentication
```

---

## 🔁 与 main 分支同步

当 `develop` 分支有重要更新需要发布到生产环境时：

```bash
# 1. 切换到 main 分支
git checkout main

# 2. 拉取最新代码
git pull origin main

# 3. 合并 develop 分支
git merge develop

# 4. 推送到 main
git push origin main

# 5. 创建版本标签（可选）
git tag -a v1.1.0 -m "Release version 1.1.0"
git push origin v1.1.0
```

---

## 🐛 紧急修复流程

```bash
# 1. 从 main 创建修复分支
git checkout main
git pull origin main
git checkout -b hotfix/critical-bug

# 2. 修复 Bug 并提交
git commit -m "hotfix-fix-critical-security-issue"

# 3. 同时合并到 main 和 develop
git checkout main
git merge hotfix/critical-bug
git push origin main

git checkout develop
git merge hotfix/critical-bug
git push origin develop

# 4. 删除修复分支
git branch -d hotfix/critical-bug
```

---

## ⚠️ 协作规范

### 禁止直接推送
- ❌ **禁止**直接推送到 `main` 分支
- ❌ **禁止**直接推送到 `develop` 分支（除维护者）
- ✅ **必须**通过 Pull Request 合并代码

### 代码审查
- 每个功能分支都需要至少 1 人审查
- 审查通过后才能合并到 `develop`

### 冲突解决
```bash
# 1. 拉取最新代码
git pull origin develop

# 2. 如果有冲突，手动解决后
git add .
git commit
git push
```

---

## 📋 常用命令速查

| 命令 | 说明 |
|------|------|
| `git branch` | 查看本地分支 |
| `git branch -r` | 查看远程分支 |
| `git checkout -b feature/xxx` | 创建并切换分支 |
| `git merge develop` | 合并 develop 分支 |
| `git stash` | 暂存当前修改 |
| `git stash pop` | 恢复暂存的修改 |

---

## 🔐 环境配置

每个开发者需要：

1. 复制环境变量模板：
```bash
cp .env.example .env
```

2. 修改 `.env` 文件，填入自己的配置：
   - 数据库配置
   - API Keys（百度 OCR 等）
   - 其他敏感信息

3. `.env` 文件已添加到 `.gitignore`，不会上传到 GitHub

---

## 📦 当前项目结构

```
voyago/
├── main          # 生产环境（稳定版本）
└── develop       # 开发环境（当前工作分支）
```

**当前状态：**
- ✅ `main` 分支：版本 1.0.0
- ✅ `develop` 分支：已创建，用于日常开发
- 🔄 所有团队成员应基于 `develop` 创建功能分支

---

## 📞 联系方式

如有问题，请联系团队负责人或创建 Issue。

---

**最后更新：** 2025-03-23
