# 📐 项目架构速查表

## 核心概念

这是一个**双窗口文件管理程序**（类似 FreeCommander），采用**分层架构**设计：

```
┌─────────────────────────────────────┐
│        应用入口 (main.py)           │
└─────────────────────────────────────┘
              ↓
┌─────────────────────────────────────┐
│   UI层 (UI Presentation Layer)      │
│  ┌──────────┬──────────────────┐   │
│  │ 左面板   │    右面板        │   │ <- FilePanel
│  └──────────┴──────────────────┘   │
│  └─── MainWindow (双面板容器)       │
│  └─── MenuBar (菜单)                │
│  └─── SearchDialog (搜索)           │
└─────────────────────────────────────┘
              ↓
┌─────────────────────────────────────┐
│   业务层 (Business Logic Layer)    │
│  └─── FileOperationManager (文件操作)│
│  └─── ConfigManager (配置管理)     │
│  └─── FileSearcher (搜索引擎)       │
└─────────────────────────────────────┘
              ↓
┌─────────────────────────────────────┐
│  系统层 (System Integration Layer)  │
│  └─── Git Manager (版本控制)        │
│  └─── OS File System (文件系统)     │
└─────────────────────────────────────┘
```

---

## 8个核心模块

### 1️⃣ **main.py** - 程序入口
- 作用：启动应用，创建QApplication和MainWindow
- 行数：~20行
- 关键函数：`main()`

### 2️⃣ **ui/main_window.py** - 主窗口
- 作用：双面板容器，管理焦点和交互
- 行数：~210行
- 关键类：`MainWindow(QMainWindow)`
- 职责：
  - 创建和布局两个文件面板
  - 管理焦点面板（哪个窗口活跃）
  - 处理工具栏和菜单栏
  - 调度文件操作到焦点面板

### 3️⃣ **ui/file_panel.py** - 文件面板
- 作用：单个文件浏览面板（左/右）
- 行数：~378行
- 关键类：`FilePanel(QWidget)`
- 职责：
  - 显示文件列表（QTableWidget）
  - 导航路径（路径输入框）
  - 处理文件操作（复制、移动、删除）
  - 提供右键菜单

### 4️⃣ **ui/menu_bar.py** - 菜单栏
- 作用：构建菜单结构
- 行数：~150行
- 关键函数：`create_menu_bar()`
- 菜单：文件、编辑、查看、工具、帮助

### 5️⃣ **ui/file_operations.py** - 文件操作
- 作用：底层文件系统操作
- 行数：~121行
- 关键类：`FileOperationManager`
- 功能：复制、移动、删除、重命名、获取属性等

### 6️⃣ **ui/search.py** - 搜索引擎
- 作用：文件搜索逻辑
- 行数：~80行
- 关键类：`FileSearcher`
- 功能：按名称、类型、大小、日期搜索

### 7️⃣ **ui/config.py** - 配置管理
- 作用：保存和加载应用配置
- 行数：~60行
- 关键类：`ConfigManager`
- 配置项：窗口大小、面板路径、显示选项等

### 8️⃣ **git_manager.py** - Git工具
- 作用：简化Git操作
- 行数：~315行
- 功能：分支、提交、合并、标签等

---

## 关键流程

### 🔄 用户点击文件夹 → 进入该目录

```
User double-clicks folder
       ↓
FilePanel.on_item_double_clicked()
       ↓
FilePanel.change_path(new_path)
       ↓
FilePanel.refresh()
       ↓
os.listdir() / os.stat()  [获取目录内容]
       ↓
QTableWidget.setItem()  [更新表格显示]
       ↓
UI显示新目录的文件列表
```

### 🔄 用户点击工具栏"上级"按钮

```
User clicks "上级" button
       ↓
MainWindow.go_up()
       ↓
focused_panel = self.get_focused_panel()
       ↓
focused_panel.go_up()  [作用于左或右面板]
       ↓
FilePanel.go_up()
       ↓
parent_path = os.path.dirname(current_path)
       ↓
change_path(parent_path)
       ↓
刷新显示
```

### 🔄 用户复制文件

```
User selects files + clicks "复制"
       ↓
MainWindow.copy_files()
       ↓
source_panel = self.focused_panel  [源面板]
target_panel = other panel         [目标面板]
       ↓
FilePanel.copy_to(target_path)
       ↓
FileOperationManager.copy_file()   [实际复制]
       ↓
确认对话框
       ↓
两个面板都刷新
```

### 🔄 用户切换焦点到右面板

```
User clicks right panel
       ↓
FilePanel.file_list.focusInEvent()
       ↓
MainWindow._on_panel_focus(right_panel)
       ↓
self.focused_panel = right_panel
       ↓
update_panel_highlight()
       ↓
右面板显示蓝色边框
       ↓
工具栏按钮现在作用于右面板
```

---

## 数据结构

### FilePanel中的文件列表

```python
class FilePanel:
    current_path: str           # 当前目录路径
    selected_files: list        # 选中的文件
    
    # UI组件
    path_input: QLineEdit       # 路径输入框
    file_list: QTableWidget     # 文件表格
        - 列0: 文件名 (str)
        - 列1: 类型 (str)
        - 列2: 大小 (str)
        - 列3: 修改时间 (str)
    status_label: QLineEdit     # 状态栏
```

### ConfigManager中的配置

```json
{
  "window_width": 1400,
  "window_height": 800,
  "window_x": 100,
  "window_y": 100,
  "left_panel_path": "C:\\Users",
  "right_panel_path": "C:\\",
  "show_hidden_files": false,
  "show_file_extensions": true
}
```

---

## 焦点管理（关键特性）

### 问题
- PyQt5 的 `widget.hasFocus()` 不够可靠

### 解决方案
- 主动追踪：`MainWindow.focused_panel` 变量
- 事件驱动：焦点面板获得焦点时更新

### 实现细节
```python
# 左面板获得焦点
left_panel.file_list.focusInEvent 
    → MainWindow._on_panel_focus(left_panel)
    → focused_panel = left_panel
    → 更新边框高亮

# 工具栏按钮
go_up() 
    → focused = self.get_focused_panel()
    → focused.go_up()  # 作用于焦点面板
```

---

## 快捷键

| 快捷键 | 功能 |
|-------|------|
| F5 | 刷新 |
| F6 | 移动 |
| Delete | 删除 |
| Ctrl+C | 复制 |
| Ctrl+X | 剪切 |
| Ctrl+V | 粘贴 |
| Ctrl+F | 搜索 |
| Ctrl+Q | 退出 |

---

## 类关系简图

```
QMainWindow
    ↓
MainWindow
    ├── FilePanel (left)
    │   ├── QTableWidget (文件列表)
    │   ├── QLineEdit (路径输入)
    │   └── FileOperationManager
    │
    ├── FilePanel (right)
    │   ├── QTableWidget (文件列表)
    │   ├── QLineEdit (路径输入)
    │   └── FileOperationManager
    │
    ├── QToolBar (工具栏)
    ├── QMenuBar (菜单栏)
    └── ConfigManager (配置)
```

---

## 文件操作流程示例

### 复制文件
```
copy_files()
  ↓
source = focused_panel
target = other panel
  ↓
source.copy_to(target.current_path)
  ↓
FileOperationManager.copy_file(src, dst)
  ↓
shutil.copy2()  [跨平台复制]
  ↓
source.refresh()
target.refresh()  [两个面板都刷新]
  ↓
show success message
```

### 删除文件
```
delete_files()
  ↓
focused = get_focused_panel()
  ↓
focused.delete_files()
  ↓
show confirm dialog
  ↓
FileOperationManager.delete_file()
  ↓
os.remove() / shutil.rmtree()
  ↓
focused.refresh()  [刷新该面板]
```

---

## 依赖关系

```
项目依赖:
├── PyQt5 (UI框架)
│   ├── QtWidgets (窗口、对话框)
│   ├── QtCore (信号槽、事件)
│   └── QtGui (图标、样式)
│
├── Python标准库
│   ├── os (文件系统)
│   ├── shutil (文件操作)
│   ├── subprocess (进程管理)
│   └── json (配置存储)
│
└── Git 2.52.0 (外部工具)
```

---

## 扩展指南

### 添加新的文件操作

1. 在 `FileOperationManager` 中添加方法
   ```python
   @staticmethod
   def compress_file(src_path, dst_path):
       # 实现压缩逻辑
       pass
   ```

2. 在 `FilePanel` 中调用
   ```python
   def compress_files(self):
       focused = self.get_focused_files()
       FileOperationManager.compress_file(focused[0], target)
   ```

3. 在菜单或工具栏中添加入口

### 添加新菜单项

1. 在 `menu_bar.py` 中添加
   ```python
   compress_action = QAction("压缩...", self)
   compress_action.triggered.connect(main_window.compress_files)
   tools_menu.addAction(compress_action)
   ```

2. 在 `MainWindow` 中实现
   ```python
   def compress_files(self):
       # 实现逻辑
       pass
   ```

---

## 性能特点

### 优势
- ✅ 双面板设计，便于文件对比和操作
- ✅ 焦点追踪精准，工具栏操作直观
- ✅ 配置持久化，关闭后恢复状态
- ✅ 跨平台支持 (Windows/Linux/macOS)

### 瓶颈
- ⚠️ 大文件夹 (>10000文件) 加载较慢
- ⚠️ 递归计算文件夹大小耗时
- ⚠️ 网络路径访问延迟

### 优化方向
- 虚拟滚动显示
- 后台线程加载
- 缩略图缓存

---

## 快速导航

| 我想... | 去看... |
|--------|--------|
| 理解整体架构 | [ARCHITECTURE.md](ARCHITECTURE.md) |
| 快速上手 | [QUICK_START.md](QUICK_START.md) |
| 学习使用 | [USAGE_GUIDE.md](USAGE_GUIDE.md) |
| 查看所有功能 | [README.md](README.md) |
| 了解优化计划 | [OPTIMIZATION_PLAN.md](OPTIMIZATION_PLAN.md) |
| Git工作流程 | [GIT_WORKFLOW.md](GIT_WORKFLOW.md) |

---

**版本**: 1.0.0  
**总代码行数**: ~1454行 (核心)  
**架构类型**: 分层MVC  
**最后更新**: 2026-01-11
