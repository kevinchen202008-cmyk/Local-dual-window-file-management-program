"""
主窗口类 - 双面板布局
"""

from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, 
    QMenuBar, QToolBar, QPushButton, QMessageBox, QShortcut
)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QIcon
from .file_panel import FilePanel
from .menu_bar import create_menu_bar
from .config import ConfigManager


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # 加载配置
        self.config = ConfigManager()
        
        # 追踪焦点面板
        self.focused_panel = None
        
        self.setWindowTitle("文件管理器 - File Manager")
        
        # 恢复窗口大小和位置
        width = self.config.get('window_width', 1400)
        height = self.config.get('window_height', 800)
        x = self.config.get('window_x', 100)
        y = self.config.get('window_y', 100)
        self.setGeometry(x, y, width, height)
        
        # 创建中央widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 创建主布局
        main_layout = QVBoxLayout()
        
        # 创建工具栏
        self.toolbar = self.create_toolbar()
        main_layout.addWidget(self.toolbar)
        
        # 创建文件面板容器
        panels_layout = QHBoxLayout()
        
        # 左面板
        left_path = self.config.get('left_panel_path', None)
        self.left_panel = FilePanel("left", initial_path=left_path)
        # 添加焦点事件处理
        self.left_panel.file_list.focusInEvent = lambda e: self._on_panel_focus(self.left_panel, e)
        self.left_panel.path_input.focusInEvent = lambda e: self._on_panel_focus(self.left_panel, e)
        panels_layout.addWidget(self.left_panel)
        
        # 右面板
        right_path = self.config.get('right_panel_path', None)
        self.right_panel = FilePanel("right", initial_path=right_path)
        # 添加焦点事件处理
        self.right_panel.file_list.focusInEvent = lambda e: self._on_panel_focus(self.right_panel, e)
        self.right_panel.path_input.focusInEvent = lambda e: self._on_panel_focus(self.right_panel, e)
        panels_layout.addWidget(self.right_panel)
        
        # 默认焦点在左面板
        self.focused_panel = self.left_panel
        
        main_layout.addLayout(panels_layout)
        
        # 创建底部操作栏
        bottom_layout = QHBoxLayout()
        bottom_layout.addStretch()
        
        copy_btn = QPushButton("复制 (F5)")
        move_btn = QPushButton("移动 (F6)")
        delete_btn = QPushButton("删除 (Del)")
        refresh_btn = QPushButton("刷新 (F5)")
        
        copy_btn.clicked.connect(self.copy_files)
        move_btn.clicked.connect(self.move_files)
        delete_btn.clicked.connect(self.delete_files)
        refresh_btn.clicked.connect(self.refresh_panels)
        
        bottom_layout.addWidget(copy_btn)
        bottom_layout.addWidget(move_btn)
        bottom_layout.addWidget(delete_btn)
        bottom_layout.addWidget(refresh_btn)
        
        main_layout.addLayout(bottom_layout)
        
        central_widget.setLayout(main_layout)
        
        # 创建菜单栏
        self.setMenuBar(create_menu_bar(self))
        
        # 设置快捷键
        self.setup_shortcuts()
    
    def create_toolbar(self):
        """创建工具栏"""
        toolbar = QToolBar("Main Toolbar")
        toolbar.setIconSize(QSize(16, 16))
        
        # 返回上级
        up_btn = QPushButton("⬆ 上级")
        up_btn.clicked.connect(self.go_up)
        toolbar.addWidget(up_btn)
        
        toolbar.addSeparator()
        
        # 刷新
        refresh_btn = QPushButton("🔄 刷新")
        refresh_btn.clicked.connect(self.refresh_panels)
        toolbar.addWidget(refresh_btn)
        
        toolbar.addSeparator()
        
        # 同步路径
        sync_btn = QPushButton("⟷ 同步路径")
        sync_btn.clicked.connect(self.sync_paths)
        toolbar.addWidget(sync_btn)
        
        return toolbar
    
    def setup_shortcuts(self):
        """设置快捷键"""
        from PyQt5.QtGui import QKeySequence
        
        # F5 - 刷新
        QShortcut(QKeySequence("F5"), self, self.refresh_panels)
        
        # F6 - 移动
        QShortcut(QKeySequence("F6"), self, self.move_files)
        
        # Del - 删除
        QShortcut(QKeySequence("Delete"), self, self.delete_files)
    
    def _on_panel_focus(self, panel, event):
        """面板获得焦点时的处理"""
        self.focused_panel = panel
        self.update_panel_highlight()
    
    def update_panel_highlight(self):
        """更新焦点面板的高亮显示 - 现代浅色背景风格"""
        # 焦点面板：浅蓝色背景 + 微妙边框
        focused_style = """
            QWidget {
                background-color: #E8F4F8;
                border-radius: 4px;
            }
            QLineEdit {
                background-color: #FFFFFF;
                border: 1px solid #ADD8E6;
                border-radius: 3px;
                padding: 2px;
            }
            QTableWidget {
                background-color: #F5FAFB;
                border: 1px solid #ADD8E6;
                border-radius: 3px;
            }
            QTableWidget::item:selected {
                background-color: #0078d4;
            }
        """
        
        # 非焦点面板：正常样式
        unfocused_style = """
            QWidget {
                background-color: #FFFFFF;
            }
            QLineEdit {
                background-color: #FFFFFF;
                border: 1px solid #D0D0D0;
                border-radius: 3px;
                padding: 2px;
            }
            QTableWidget {
                background-color: #FFFFFF;
                border: 1px solid #D0D0D0;
                border-radius: 3px;
            }
        """
        
        if self.focused_panel == self.left_panel:
            self.left_panel.setStyleSheet(focused_style)
            self.right_panel.setStyleSheet(unfocused_style)
        else:
            self.right_panel.setStyleSheet(focused_style)
            self.left_panel.setStyleSheet(unfocused_style)
    
    def go_up(self):
        """返回上级目录"""
        focused = self.get_focused_panel()
        if focused:
            focused.go_up()
    
    def refresh_panels(self):
        """刷新两个面板"""
        self.left_panel.refresh()
        self.right_panel.refresh()
    
    def sync_paths(self):
        """同步两个面板的路径"""
        focused = self.get_focused_panel()
        if focused:
            other = self.right_panel if focused == self.left_panel else self.left_panel
            other.change_path(focused.current_path)
    
    def copy_files(self):
        """复制文件"""
        focused = self.get_focused_panel()
        if not focused:
            return
        
        other = self.right_panel if focused == self.left_panel else self.left_panel
        focused.copy_to(other.current_path)
    
    def move_files(self):
        """移动文件"""
        focused = self.get_focused_panel()
        if not focused:
            return
        
        other = self.right_panel if focused == self.left_panel else self.left_panel
        focused.move_to(other.current_path)
    
    def delete_files(self):
        """删除文件"""
        focused = self.get_focused_panel()
        if focused:
            focused.delete_files()
    
    def get_focused_panel(self):
        """获取当前焦点面板 - 使用追踪的焦点而不是实时检查"""
        return self.focused_panel if self.focused_panel else self.left_panel
    
    def closeEvent(self, event):
        """窗口关闭事件 - 保存配置"""
        # 保存窗口位置和大小
        self.config.update({
            'window_width': self.width(),
            'window_height': self.height(),
            'window_x': self.x(),
            'window_y': self.y(),
            'left_panel_path': self.left_panel.current_path,
            'right_panel_path': self.right_panel.current_path
        })
        event.accept()
