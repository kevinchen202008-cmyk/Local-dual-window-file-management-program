# Git 工作流程指南

## 仓库信息

```
项目名称: 文件管理器 (File Manager)
版本: 1.0
状态: 已初始化Git版本控制
初始提交: Initial commit - v1.0 完整实现
```

## 分支策略

### 主分支
- **main** - 主分支，仅保持稳定的发布版本
- **develop** - 开发分支，包含最新功能开发

### 功能分支
命名规范: `feature/功能名称`
```
feature/preview          # 文件预览功能
feature/compress         # 压缩/解压缩支持
feature/theme           # 主题切换
feature/bookmarks       # 书签功能
```

### 修复分支
命名规范: `bugfix/问题名称`
```
bugfix/search-performance    # 搜索性能优化
bugfix/permission-error      # 权限处理改进
```

### 发布分支
命名规范: `release/版本号`
```
release/v1.1
release/v2.0
```

## 提交规范

### 提交信息格式
```
<type>(<scope>): <subject>

<body>

<footer>
```

### Type 类型
- **feat**: 新功能
- **fix**: 修复bug
- **docs**: 文档更新
- **style**: 代码格式（不影响功能）
- **refactor**: 重构
- **perf**: 性能优化
- **test**: 添加测试
- **chore**: 构建过程、依赖管理

### 示例

#### 新功能提交
```bash
git commit -m "feat(ui): add file preview feature

- Implement image preview in file panel
- Support PDF, text file preview
- Add preview button in toolbar"
```

#### Bug修复提交
```bash
git commit -m "fix(search): resolve slow search performance

- Implement background threading for search
- Add search cancellation support
- Reduce UI blocking time by 80%"
```

#### 文档更新
```bash
git commit -m "docs(guide): update user guide with preview feature"
```

#### 性能优化
```bash
git commit -m "perf(panel): optimize file list loading

- Implement virtual scrolling
- Reduce memory usage by 40%
- Improve loading speed for 10k+ files"
```

## 常用Git命令

### 查看状态
```bash
git status                          # 查看修改状态
git log --oneline -10               # 查看最近10条提交
git diff                            # 查看未暂存的更改
git diff --staged                   # 查看已暂存的更改
```

### 创建和切换分支
```bash
git branch feature/新功能            # 创建分支
git checkout feature/新功能          # 切换分支
git checkout -b feature/新功能       # 创建并切换分支
git branch -d feature/旧功能         # 删除分支
```

### 更新和合并
```bash
git pull origin develop             # 拉取远程更新
git push origin feature/新功能       # 推送到远程
git merge feature/新功能             # 合并分支
git rebase develop                  # 变基
```

### 撤销操作
```bash
git restore file.py                 # 撤销文件修改
git reset HEAD~1                    # 撤销上一次提交
git revert HEAD                     # 创建反向提交
```

## 开发工作流程

### 1. 开始新功能开发

```bash
# 切换到develop分支
git checkout develop

# 更新develop分支
git pull origin develop

# 创建功能分支
git checkout -b feature/新功能
```

### 2. 开发和提交

```bash
# 编写代码
# ...

# 检查更改
git status
git diff

# 暂存更改
git add 修改的文件
# 或全部暂存
git add -A

# 提交更改
git commit -m "feat(模块): 功能描述"

# 可多次提交
git add 新文件
git commit -m "feat(模块): 添加新文件"
```

### 3. 推送到远程（如果有远程仓库）

```bash
git push origin feature/新功能
```

### 4. 创建Pull Request（如果使用GitHub等）

在Web界面创建PR，进行代码审查

### 5. 合并到develop

```bash
# 切换到develop
git checkout develop

# 更新develop
git pull origin develop

# 合并功能分支
git merge feature/新功能

# 推送到远程
git push origin develop

# 删除本地分支
git branch -d feature/新功能

# 删除远程分支（如果有）
git push origin --delete feature/新功能
```

## 标签管理

### 创建版本标签
```bash
# 为当前提交创建标签
git tag -a v1.0 -m "Version 1.0 - Initial release"

# 推送标签到远程（如果有）
git push origin v1.0

# 推送所有标签
git push origin --tags
```

### 查看标签
```bash
git tag                             # 列出所有标签
git show v1.0                       # 显示标签详情
git log --oneline --decorate        # 查看带标签的日志
```

## 代码审查检查清单

在合并代码前检查：

- [ ] 代码格式是否规范
- [ ] 注释和文档是否完整
- [ ] 是否有测试覆盖
- [ ] 性能是否有影响
- [ ] 是否有安全问题
- [ ] 提交信息是否清晰
- [ ] 是否遵循命名规范
- [ ] 是否有重复代码

## 常见场景处理

### 场景1: 需要紧急修复线上bug

```bash
# 从main分支创建hotfix分支
git checkout main
git checkout -b hotfix/紧急bug

# 修复并提交
git add .
git commit -m "fix(critical): 紧急修复"

# 合并到main和develop
git checkout main
git merge hotfix/紧急bug
git checkout develop
git merge hotfix/紧急bug

# 删除hotfix分支
git branch -d hotfix/紧急bug
```

### 场景2: 需要回滚某个提交

```bash
# 方法1: 用revert创建反向提交
git revert 提交hash

# 方法2: 用reset回退（谨慎！会改写历史）
git reset --hard 提交hash
```

### 场景3: 需要整理提交历史

```bash
# 交互式变基，可以合并、重新排序、编辑提交
git rebase -i HEAD~10
```

### 场景4: 不小心删除了本地分支

```bash
# 查找删除的提交
git reflog

# 恢复分支
git checkout -b feature/恢复 提交hash
```

## 备份和恢复

### 本地备份
```bash
# 创建完整备份
git bundle create backup.bundle --all

# 从备份恢复
git clone backup.bundle
```

### 远程备份
```bash
# 如果有远程仓库，确保定期推送
git push origin --all
git push origin --tags
```

## 性能优化建议

### 保持仓库健康
```bash
# 定期垃圾回收
git gc

# 检查仓库完整性
git fsck --full

# 清理无用的本地分支
git branch -vv | grep gone | awk '{print $1}' | xargs git branch -d
```

## 注意事项

⚠️ **不要提交的文件**
- `.venv/` 虚拟环境
- `__pycache__/` Python缓存
- `.filemanager/` 用户配置
- 日志文件 `*.log`

✅ **应该提交的文件**
- 源代码 `*.py`
- 文档 `*.md`
- 配置模板 `*.example`
- 许可证文件

## Git工作流总结

```
创建分支 → 开发功能 → 提交更改 → 合并代码 → 发布版本
         ↓              ↓          ↓         ↓
    feature/*      git commit   git merge   git tag
                   遵循规范     代码审查    版本标记
```

---

更多帮助：`git help <command>`
