# 分支操作快速参考

## 当前分支结构

```
main (生产环境)
  ↑
  ↓ 定期合并
develop (开发环境) ← 当前分支
  ↑
  ↓ 功能分支合并
feature/* (功能分支)
hotfix/* (紧急修复)
```

## 🚀 快速命令

### 开始新功能
```bash
git checkout develop
git pull origin develop
git checkout -b feature/your-feature-name
```

### 提交并推送
```bash
git add .
git commit -m "feature-your-feature-name"
git push -u origin feature/your-feature-name
```

### 创建 PR
访问：https://github.com/jguo83672-sketch/voyago/pull/new/develop

### 合并后清理
```bash
git checkout develop
git pull origin develop
git branch -d feature/your-feature-name
```

### 从 main 同步到 develop
```bash
git checkout main
git pull origin main
git checkout develop
git merge main
git push origin develop
```

## 📊 分支状态

| 分支 | 用途 | 提交 ID |
|------|------|---------|
| main | 生产环境 | a9b033c |
| develop | 开发环境 | a23d36a |

## 📖 详细文档

查看完整指南：[TEAM_COLLABORATION.md](TEAM_COLLABORATION.md)
