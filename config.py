"""
应用程序配置文件
Python 3.13.9+ 兼容
"""

APP_NAME = "文件管理器"
APP_VERSION = "1.0.0"
APP_AUTHOR = "Developer"

# 窗口配置
WINDOW_DEFAULT_WIDTH = 1400
WINDOW_DEFAULT_HEIGHT = 800

# 文件列表配置
FILE_LIST_COLUMNS = ["名称", "类型", "大小", "修改时间"]

# 快捷键配置
SHORTCUTS = {
    'refresh': 'F5',
    'move': 'F6',
    'delete': 'Delete',
    'go_up': 'Backspace',
    'copy': 'Ctrl+C',
    'cut': 'Ctrl+X',
    'quit': 'Ctrl+Q',
    'search': 'Ctrl+F',
}

# 日志配置
LOG_LEVEL = "INFO"
LOG_FILE = ".filemanager/logs/app.log"
