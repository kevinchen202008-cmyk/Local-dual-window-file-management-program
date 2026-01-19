"""
主窗口类 - 双面板布局
"""

from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, 
    QMenuBar, QToolBar, QPushButton, QMessageBox, QShortcut, QMenu
)
from PyQt5.QtCore import Qt, QSize, QPoint, QRect, QEvent
from PyQt5.QtGui import QIcon, QMouseEvent, QColor
from .file_panel import FilePanel
from .menu_bar import create_menu_bar
from .config import ConfigManager
class TitleBar(QWidget):
    """标题栏 - 包含标题和菜单栏"""
    
    def __init__(self, parent=None, menu_bar=None):
        super().__init__(parent)
        self.parent_window = parent
        self.drag_position = None
        
        # 创建主布局
        layout = QHBoxLayout()
        layout.setContentsMargins(8, 2, 8, 2)
        layout.setSpacing(8)  # 减少间距，让菜单更紧挨标题
        
        # 设置背景色
        self.setStyleSheet("""
            QWidget {
                background-color: #F3F3F3;
                border-bottom: 1px solid #E0E0E0;
            }
        """)
        
        # 标题文本 - 与菜单栏视觉效果一致
        from PyQt5.QtWidgets import QLabel
        title_label = QLabel("文件管理器 - File Manager")
        title_label.setStyleSheet("font-weight: bold; color: #333333;")
        title_label.setMinimumWidth(200)
        title_label.setMaximumWidth(220)
        # 不设置固定高度，让它自然适应菜单栏高度
        layout.addWidget(title_label)
        
        # 菜单栏 - 紧跟在标题后面，使用系统默认大小
        if menu_bar:
            menu_bar.setStyleSheet("""
                QMenuBar {
                    background-color: transparent;
                    border: none;
                    padding: 0px;
                    margin: 0px;
                }
                QMenuBar::item {
                    padding: 4px 12px;
                    background-color: transparent;
                    border: none;
                }
                QMenuBar::item:selected {
                    background-color: #E0E0E0;
                    border-radius: 2px;
                }
            """)
            # 菜单栏紧挨标题，不添加额外间距
            layout.addWidget(menu_bar, 0, Qt.AlignLeft)
        
        # 伸缩空间
        layout.addStretch()
        
        # 窗口控制按钮（最小化、最大化、关闭）- 与菜单栏视觉效果一致
        if parent:
            # 统一的按钮样式，匹配菜单栏的padding和高度
            button_style = """
                QPushButton {
                    background-color: transparent;
                    border: none;
                    color: #333333;
                    padding: 4px 12px;
                }
                QPushButton:hover {
                    background-color: #E0E0E0;
                    border-radius: 2px;
                }
            """
            
            # 最小化按钮
            min_btn = QPushButton("—")
            min_btn.setStyleSheet(button_style)
            min_btn.clicked.connect(parent.showMinimized)
            layout.addWidget(min_btn)
            
            # 最大化/还原按钮
            self.max_btn = QPushButton("□")
            self.max_btn.setStyleSheet(button_style)
            self.max_btn.clicked.connect(self.toggle_maximize)
            layout.addWidget(self.max_btn)
            
            # 关闭按钮
            close_btn = QPushButton("×")
            close_btn.setStyleSheet("""
                QPushButton {
                    background-color: transparent;
                    border: none;
                    color: #333333;
                    padding: 4px 12px;
                }
                QPushButton:hover {
                    background-color: #E81123;
                    color: white;
                    border-radius: 2px;
                }
            """)
            close_btn.clicked.connect(parent.close)
            layout.addWidget(close_btn)
        
        self.setLayout(layout)
        # 不设置固定高度，让它自然适应菜单栏高度
    
    def toggle_maximize(self):
        """切换最大化/还原"""
        if self.parent_window:
            if self.parent_window.isMaximized():
                self.parent_window.showNormal()
                self.max_btn.setText("□")
            else:
                self.parent_window.showMaximized()
                self.max_btn.setText("❐")
    
    def mousePressEvent(self, event):
        """鼠标按下 - 记录拖拽起点"""
        if event.button() == Qt.LeftButton:
            self.drag_position = event.globalPos() - self.parent_window.frameGeometry().topLeft()
        super().mousePressEvent(event)
    
    def mouseMoveEvent(self, event):
        """鼠标移动 - 拖拽窗口"""
        if event.buttons() == Qt.LeftButton and self.drag_position is not None:
            self.parent_window.move(event.globalPos() - self.drag_position)
        super().mouseMoveEvent(event)
    
    def mouseDoubleClickEvent(self, event):
        """双击 - 切换最大化"""
        if self.parent_window:
            if self.parent_window.isMaximized():
                self.parent_window.showNormal()
            else:
                self.parent_window.showMaximized()
        super().mouseDoubleClickEvent(event)



class ToolBar(QWidget):
    """工具栏 - 独占一行，包含上级、刷新、同步路径"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # 创建主布局
        layout = QHBoxLayout()
        layout.setContentsMargins(8, 0, 8, 0)
        layout.setSpacing(3)
        
        # 设置背景色
        self.setStyleSheet("""
            QWidget {
                background-color: #F5F5F5;
                border-bottom: 1px solid #E0E0E0;
            }
        """)
        
        # 返回上级 - 与菜单栏视觉效果一致
        self.up_btn = QPushButton("⬆ 上级")
        self.up_btn.setMinimumWidth(90)
        self.apply_button_style(self.up_btn)
        layout.addWidget(self.up_btn)
        
        # 分隔符
        separator1 = QWidget()
        separator1.setStyleSheet("background-color: #D0D0D0;")
        separator1.setMaximumWidth(1)
        separator1.setMinimumHeight(20)
        layout.addWidget(separator1)
        
        # 刷新 - 与菜单栏视觉效果一致
        self.refresh_btn = QPushButton("📁 刷新")
        self.refresh_btn.setMinimumWidth(90)
        self.apply_button_style(self.refresh_btn)
        layout.addWidget(self.refresh_btn)
        
        # 分隔符
        separator2 = QWidget()
        separator2.setStyleSheet("background-color: #D0D0D0;")
        separator2.setMaximumWidth(1)
        separator2.setMinimumHeight(20)
        layout.addWidget(separator2)
        
        # 同步路径 - 与菜单栏视觉效果一致
        self.sync_btn = QPushButton("⟷ 同步路径")
        self.sync_btn.setMinimumWidth(110)
        self.apply_button_style(self.sync_btn)
        layout.addWidget(self.sync_btn)
        
        # 伸缩
        layout.addStretch()
        
        self.setLayout(layout)
        # 不设置固定高度，让它自然适应按钮高度
    
    def apply_button_style(self, button):
        """应用按钮样式 - 与菜单栏视觉效果一致"""
        button.setStyleSheet("""
            QPushButton {
                background-color: #FFFFFF;
                border: 1px solid #D0D0D0;
                border-radius: 2px;
                padding: 4px 12px;
                font-weight: normal;
            }
            QPushButton:hover {
                background-color: #F0F0F0;
                border: 1px solid #A0A0A0;
            }
            QPushButton:pressed {
                background-color: #E0E0E0;
                border: 1px solid #808080;
            }
        """)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # 隐藏系统默认标题栏，使用自定义标题栏
        self.setWindowFlags(Qt.Window | Qt.FramelessWindowHint)
        
        # 加载配置
        self.config = ConfigManager()
        
        # 追踪焦点面板
        self.focused_panel = None
        
        self.setWindowTitle("文件管理器 - File Manager")
        
        # 设置窗口大小为屏幕的2/3，并居中
        from PyQt5.QtWidgets import QApplication
        screen = QApplication.primaryScreen().geometry()
        window_width = int(screen.width() * 2 / 3)
        window_height = int(screen.height() * 2 / 3)
        x = (screen.width() - window_width) // 2
        y = (screen.height() - window_height) // 2
        
        # 从配置中读取大小，如果没有则使用2/3屏幕大小
        width = self.config.get('window_width', window_width)
        height = self.config.get('window_height', window_height)
        x = self.config.get('window_x', x)
        y = self.config.get('window_y', y)
        
        self.setGeometry(x, y, width, height)
        
        # 创建中央widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 创建主布局
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # 创建菜单栏
        menu_bar = create_menu_bar(self)
        
        # 创建标题栏（包含标题和菜单栏）
        self.title_bar = TitleBar(self, menu_bar)
        main_layout.addWidget(self.title_bar)
        
        # 监听窗口状态变化，更新最大化按钮
        self.installEventFilter(self)
        
        # 创建工具栏
        self.toolbar = ToolBar(self)
        self.toolbar.up_btn.clicked.connect(self.go_up)
        self.toolbar.refresh_btn.clicked.connect(self.refresh_panels)
        self.toolbar.sync_btn.clicked.connect(self.sync_paths)
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
        
        # 创建底部操作栏 - 与菜单栏视觉效果一致
        bottom_layout = QHBoxLayout()
        bottom_layout.addStretch()
        
        # 统一的底部按钮样式，匹配菜单栏
        bottom_button_style = """
            QPushButton {
                background-color: #FFFFFF;
                border: 1px solid #D0D0D0;
                border-radius: 2px;
                padding: 4px 12px;
                font-weight: normal;
            }
            QPushButton:hover {
                background-color: #F0F0F0;
                border: 1px solid #A0A0A0;
            }
            QPushButton:pressed {
                background-color: #E0E0E0;
                border: 1px solid #808080;
            }
        """
        
        copy_btn = QPushButton("复制 (F5)")
        copy_btn.setStyleSheet(bottom_button_style)
        copy_btn.clicked.connect(self.copy_files)
        
        move_btn = QPushButton("移动 (F6)")
        move_btn.setStyleSheet(bottom_button_style)
        move_btn.clicked.connect(self.move_files)
        
        delete_btn = QPushButton("删除 (Del)")
        delete_btn.setStyleSheet(bottom_button_style)
        delete_btn.clicked.connect(self.delete_files)
        
        refresh_btn = QPushButton("刷新 (F5)")
        refresh_btn.setStyleSheet(bottom_button_style)
        refresh_btn.clicked.connect(self.refresh_panels)
        
        bottom_layout.addWidget(copy_btn)
        bottom_layout.addWidget(move_btn)
        bottom_layout.addWidget(delete_btn)
        bottom_layout.addWidget(refresh_btn)
        
        main_layout.addLayout(bottom_layout)
        
        central_widget.setLayout(main_layout)
        
        # 设置快捷键
        self.setup_shortcuts()
    
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
    
    def eventFilter(self, obj, event):
        """事件过滤器 - 监听窗口状态变化"""
        if event.type() == QEvent.WindowStateChange:
            if hasattr(self, 'title_bar') and hasattr(self.title_bar, 'max_btn'):
                if self.isMaximized():
                    self.title_bar.max_btn.setText("❐")
                else:
                    self.title_bar.max_btn.setText("□")
        return super().eventFilter(obj, event)
    
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
