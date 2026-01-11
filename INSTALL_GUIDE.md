# 安装和启动指南

## 系统要求

- **操作系统**: Windows 7+、Linux 或 macOS
- **Python版本**: Python 3.7 或更高版本
- **内存**: 至少 512MB RAM
- **磁盘空间**: 至少 100MB

## 快速启动

### 方式一：使用启动脚本（推荐）

#### Windows 用户
```bash
# 直接双击以下文件：
run.bat
```

#### Linux/macOS 用户
```bash
# 打开终端并运行：
bash run.sh
```

### 方式二：手动启动

#### Windows
```bash
# 打开命令提示符或 PowerShell，进入项目目录
cd d:\Projects\py-prj-1

# 激活虚拟环境（如果还没有激活）
.venv\Scripts\activate

# 安装依赖（第一次运行）
pip install -r requirements.txt

# 运行程序
python main.py
```

#### Linux/macOS
```bash
# 打开终端，进入项目目录
cd ~/Projects/py-prj-1

# 激活虚拟环境（如果还没有激活）
source .venv/bin/activate

# 安装依赖（第一次运行）
pip install -r requirements.txt

# 运行程序
python3 main.py
```

## 第一次使用

### 安装依赖

如果运行脚本后看到错误信息关于缺少 PyQt5，请手动安装：

```bash
pip install -r requirements.txt
```

或者：

```bash
pip install PyQt5==5.15.9
```

### 验证安装

运行测试脚本验证环境是否正确：

```bash
python test_verify.py
```

应该看到类似输出：
```
==================================================
文件管理器 - 程序验证
==================================================
✓ 依赖检查...
✓ 模块导入...
✓ 配置管理器...
✓ 文件搜索...
✓ 文件操作工具...

==================================================
测试总结
==================================================
✓ PASS  - 依赖检查
✓ PASS  - 模块导入
✓ PASS  - 配置管理器
✓ PASS  - 文件搜索
✓ PASS  - 文件操作工具
--------------------------------------------------
总计: 5/5 测试通过
==================================================

✓ 所有测试通过！程序已准备就绪。
```

## 项目结构说明

```
py-prj-1/                    # 项目根目录
│
├── main.py                  # 程序入口点
├── config.py                # 应用配置常量
├── test_verify.py           # 程序验证脚本
│
├── requirements.txt         # Python 依赖列表
├── README.md                # 项目说明文档
├── USAGE_GUIDE.md          # 详细使用指南
├── QUICK_REFERENCE.md      # 快速参考卡片
├── PROJECT_SUMMARY.md      # 项目完成总结
│
├── run.bat                  # Windows 启动脚本
├── run.sh                   # Linux/macOS 启动脚本
│
├── ui/                      # UI 用户界面模块
│   ├── __init__.py          # 模块初始化
│   ├── main_window.py       # 主窗口类
│   ├── file_panel.py        # 文件浏览面板
│   ├── menu_bar.py          # 菜单栏创建
│   ├── search_dialog.py     # 搜索对话框
│   ├── search.py            # 文件搜索模块
│   ├── config.py            # 配置管理器
│   └── file_operations.py   # 文件操作工具
│
└── .venv/                   # Python 虚拟环境（自动创建）
```

## 故障排除

### 问题 1：找不到 Python

**错误信息**：`'python' is not recognized` 或 `python: command not found`

**解决方案**：
1. 检查 Python 是否已安装
   ```bash
   python --version
   ```

2. 如果未安装，请从 [python.org](https://www.python.org) 下载安装

3. Windows 用户：请确保在安装 Python 时勾选了"Add Python to PATH"

### 问题 2：PyQt5 导入错误

**错误信息**：`ModuleNotFoundError: No module named 'PyQt5'`

**解决方案**：
```bash
pip install PyQt5
```

### 问题 3：虚拟环境激活失败

**Windows**：
```bash
# 如果 .venv\Scripts\activate 不工作，尝试：
.\.venv\Scripts\activate.bat

# 或者创建新的虚拟环境：
python -m venv .venv
.venv\Scripts\activate
```

**Linux/macOS**：
```bash
# 如果 source .venv/bin/activate 不工作，尝试：
chmod +x .venv/bin/activate
source .venv/bin/activate

# 或者创建新的虚拟环境：
python3 -m venv .venv
source .venv/bin/activate
```

### 问题 4：权限被拒绝（Linux/macOS）

**错误信息**：`Permission denied`

**解决方案**：
```bash
# 给启动脚本添加执行权限
chmod +x run.sh

# 然后运行
bash run.sh
```

### 问题 5：程序启动但窗口显示异常

**解决方案**：
1. 确保你的显示驱动程序是最新的
2. 尝试在高 DPI 显示器上使用：设置环境变量
   ```bash
   set QT_AUTO_SCREEN_SCALE_FACTOR=1  # Windows
   export QT_AUTO_SCREEN_SCALE_FACTOR=1  # Linux/macOS
   ```

## 环境配置（可选）

### 创建桌面快捷方式（Windows）

1. 右键点击桌面
2. 选择"新建" → "快捷方式"
3. 位置输入：`d:\Projects\py-prj-1\run.bat`
4. 名称输入：`文件管理器`
5. 完成

### 添加到开始菜单（Windows）

1. 运行 `shell:appsfolder`
2. 创建 `run.bat` 的快捷方式到此文件夹

### 添加到应用菜单（Linux）

1. 创建 `.desktop` 文件：
   ```bash
   sudo nano /usr/share/applications/filemanager.desktop
   ```

2. 输入以下内容：
   ```ini
   [Desktop Entry]
   Type=Application
   Name=文件管理器
   Exec=/path/to/run.sh
   Icon=folder
   Categories=Utility;
   ```

## 升级和更新

### 更新依赖
```bash
pip install --upgrade PyQt5
```

### 从 GitHub 获取最新版本
```bash
git pull origin main
pip install -r requirements.txt
```

## 卸载

### 完全卸载
```bash
# 删除虚拟环境
rm -rf .venv  # Linux/macOS
rmdir /s /q .venv  # Windows

# 删除配置文件（可选）
rm -rf ~/.filemanager  # Linux/macOS
rmdir /s /q %USERPROFILE%\.filemanager  # Windows

# 删除整个项目目录
```

## 性能优化

### 对于大目录
- 如果某个目录包含数千个文件，加载可能较慢
- 可以使用搜索功能来快速查找文件

### 对于旧电脑
- 确保至少有 512MB 的可用 RAM
- 关闭其他程序以释放资源

## 获取帮助

### 查看文档
- **使用指南**: `USAGE_GUIDE.md`
- **快速参考**: `QUICK_REFERENCE.md`
- **项目说明**: `README.md`
- **项目总结**: `PROJECT_SUMMARY.md`

### 查看日志
程序日志保存在：
```
~/.filemanager/logs/app.log
```

### 报告问题
如有问题，请提供：
1. 操作系统和版本
2. Python 版本
3. 错误消息的完整内容
4. 重现问题的步骤

## 下一步

1. ✅ 阅读 [USAGE_GUIDE.md](USAGE_GUIDE.md) 了解详细使用方法
2. ✅ 查看 [QUICK_REFERENCE.md](QUICK_REFERENCE.md) 获取快捷键帮助
3. ✅ 开始使用文件管理器进行文件操作

---

**祝您使用愉快！** 🎉

有问题？请检查本指南的"故障排除"部分。
