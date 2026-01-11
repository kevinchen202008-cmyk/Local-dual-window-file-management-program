# 快速开始 - 本地版本控制 & 优化管理

## ⚡ 5分钟快速开始

### 1️⃣ 查看项目状态
```bash
python local_vcs.py
# 选择 9: 显示仓库信息
```

**输出示例**:
```
当前分支: main
HEAD: e88bdc5
分支数: 7
提交数: 2
用户名: File Manager Developer
```

### 2️⃣ 查看所有任务
```bash
python optimize_tasks.py
# 选择 5: 按状态列出任务
```

**输出示例**:
```
📋 任务列表

#1 ⭕ 🔴 UI modern design [v1.1.0]
#2 ⭕ 🔴 Light/Dark theme [v1.1.0]
#3 ⭕ 🟡 Icon improvements [v1.1.0]
...
```

### 3️⃣ 切换到开发分支
```bash
python local_vcs.py
# 选择 2: 切换分支
# 输入: feature/ui-modernization
```

### 4️⃣ 启动一个任务
```bash
python optimize_tasks.py
# 选择 2: 启动任务
# 输入: 1 (UI modern design)
```

### 5️⃣ 完成任务后提交
```bash
python local_vcs.py
# 选择 4: 创建提交
# 输入消息: feat(ui): 完成扁平设计实现
```

---

## 📂 项目目录结构

```
py-prj-1/
├── .local_vcs/              ← 版本控制数据
│   ├── config.json          ← 分支信息
│   ├── commits/             ← 提交记录
│   ├── branches/            ← 分支数据
│   ├── tags/                ← 标签数据
│   └── hooks/               ← Git钩子
├── .tasks.json              ← 任务列表
├── .gitignore               ← Git忽略规则
├── main.py                  ← 程序入口
├── local_vcs.py             ← 版本控制工具
├── optimize_tasks.py        ← 任务管理工具
├── git_manager.py           ← Git助手
├── init_project.py          ← 初始化脚本
├── ui/                      ← UI模块
├── OPTIMIZATION_PLAN.md     ← 优化计划
├── GIT_WORKFLOW.md          ← Git工作流
├── CHANGELOG.md             ← 更新日志
└── LOCAL_VCS_GUIDE.md       ← 本指南
```

---

## 🎯 常用任务

### 启动应用程序
```bash
python main.py
```

### 查看优化计划
```bash
cat OPTIMIZATION_PLAN.md
```

### 查看Git工作流
```bash
cat GIT_WORKFLOW.md
```

### 列出所有分支
```bash
python local_vcs.py
# 选择 3: 列出分支
```

### 查看提交日志
```bash
python local_vcs.py
# 选择 5: 查看日志
```

### 显示进度统计
```bash
python optimize_tasks.py
# 选择 6: 显示进度统计
```

---

## 🔗 分支清单

| 分支名 | 用途 | 状态 |
|--------|------|------|
| `main` | 主分支（发布版本） | ✅ 活跃 |
| `develop` | 开发分支 | ✅ 活跃 |
| `feature/ui-modernization` | UI现代化 | 📋 待开发 |
| `feature/performance-optimization` | 性能优化 | 📋 待开发 |
| `feature/shortcuts` | 快捷键支持 | 📋 待开发 |
| `feature/themes` | 主题支持 | 📋 待开发 |
| `hotfix/bugs` | 紧急修复 | 📋 备用 |

---

## 📊 任务概览

### v1.1.0 (2个月 - UI现代化)
- [ ] #1 UI modern design (高优先级)
- [ ] #2 Light/Dark theme (高优先级)
- [ ] #3 Icon improvements (中优先级)

### v1.2.0 (3个月 - 性能优化)
- [ ] #4 Virtual scrolling (高优先级)
- [ ] #5 Search optimization (高优先级)
- [ ] #6 Keyboard shortcuts (中优先级)

### v2.0.0 (6个月 - 功能扩展)
- [ ] #7 Network support (高优先级)
- [ ] #8 Advanced search (中优先级)
- [ ] #9 Plugin system (中优先级)

---

## ⌨️ 命令速查表

### 版本控制命令
```bash
# 创建分支
python local_vcs.py  # → 选择 1

# 切换分支
python local_vcs.py  # → 选择 2

# 列出分支
python local_vcs.py  # → 选择 3

# 创建提交
python local_vcs.py  # → 选择 4

# 查看日志
python local_vcs.py  # → 选择 5

# 创建标签
python local_vcs.py  # → 选择 7

# 合并分支
python local_vcs.py  # → 选择 8
```

### 任务管理命令
```bash
# 添加任务
python optimize_tasks.py  # → 选择 1

# 启动任务
python optimize_tasks.py  # → 选择 2

# 完成任务
python optimize_tasks.py  # → 选择 3

# 按版本列出
python optimize_tasks.py  # → 选择 4

# 按状态列出
python optimize_tasks.py  # → 选择 5

# 进度统计
python optimize_tasks.py  # → 选择 6
```

---

## 📝 工作流示例

### 场景: 开始v1.1.0 UI现代化开发

**第1步 - 切换分支**
```bash
python local_vcs.py
# 选择 2
# 输入: feature/ui-modernization
```

**第2步 - 启动任务**
```bash
python optimize_tasks.py
# 选择 2
# 输入: 1
```

**第3步 - 开发代码**
```
编辑 ui/main_window.py
编辑 ui/file_panel.py
...
```

**第4步 - 提交代码**
```bash
python local_vcs.py
# 选择 4
# 输入消息: feat(ui): 实现扁平设计布局
```

**第5步 - 完成任务**
```bash
python optimize_tasks.py
# 选择 3
# 输入: 1
```

**第6步 - 合并到develop**
```bash
python local_vcs.py
# 选择 2  (切换分支)
# 输入: develop
# 选择 8  (合并分支)
# 输入: feature/ui-modernization
```

**第7步 - 创建版本标签**
```bash
python local_vcs.py
# 选择 7  (创建标签)
# 输入标签: v1.1.0
```

---

## 📊 项目统计

**当前状态**:
- ✅ v1.0.0 完成
- 🔧 7个分支就绪
- 📋 9个优化任务
- 📅 18个月优化计划

**代码行数**:
- UI模块: 1200+ 行
- 工具脚本: 800+ 行
- 文档: 20000+ 字

---

## 🆘 常见问题

**Q: 如何重置项目?**
```bash
rm -r .local_vcs/
rm .tasks.json
python init_project.py
```

**Q: 如何导出任务列表?**
```bash
python optimize_tasks.py
# 选择 4 或 5 显示任务
# 手动复制或导出
```

**Q: 如何创建新分支?**
```bash
python local_vcs.py
# 选择 1: 创建分支
# 输入分支名: feature/my-feature
```

**Q: 如何撤销最后一次提交?**

目前本地VCS不支持撤销，但可以创建新提交修复：
```bash
python local_vcs.py
# 选择 4: 创建提交
# 输入: fix: 撤销之前的更改
```

---

## 🔄 版本历史

| 版本 | 日期 | 状态 | 说明 |
|------|------|------|------|
| v1.0.0 | 2026-01-11 | ✅ 完成 | 初始版本，双窗口文件管理 |
| v1.1.0 | 计划 | 📋 待开发 | UI现代化，主题支持 |
| v1.2.0 | 计划 | 📋 待开发 | 性能优化，快捷键 |
| v2.0.0 | 计划 | 📋 待开发 | 网络支持，插件系统 |

---

## 📞 获取帮助

- 查看完整指南: [LOCAL_VCS_GUIDE.md](LOCAL_VCS_GUIDE.md)
- 查看优化计划: [OPTIMIZATION_PLAN.md](OPTIMIZATION_PLAN.md)
- 查看Git工作流: [GIT_WORKFLOW.md](GIT_WORKFLOW.md)
- 查看快速参考: [QUICK_REFERENCE.md](QUICK_REFERENCE.md)

---

**最后更新**: 2026-01-11
**项目版本**: v1.0.0
**持续优化**: 就绪 ✓
