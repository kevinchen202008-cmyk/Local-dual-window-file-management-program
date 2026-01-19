"""
主窗口类 - 双面板布局
"""

import os
from pathlib import Path
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, 
    QMenuBar, QToolBar, QPushButton, QMessageBox, QShortcut, QMenu,
    QTabWidget
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
        
        # 左侧标签容器
        self.left_tabs = self._create_tab_widget("left")
        panels_layout.addWidget(self.left_tabs)
        
        # 右侧标签容器
        self.right_tabs = self._create_tab_widget("right")
        panels_layout.addWidget(self.right_tabs)
        
        # 默认焦点在左面板
        self.left_panel = self._current_panel("left")
        self.right_panel = self._current_panel("right")
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
        
        # 标签快捷键
        QShortcut(QKeySequence("Ctrl+T"), self, self.new_tab)
        QShortcut(QKeySequence("Ctrl+W"), self, self.close_tab)
        QShortcut(QKeySequence("Ctrl+Tab"), self, lambda: self.switch_tab(1))
        QShortcut(QKeySequence("Ctrl+Shift+Tab"), self, lambda: self.switch_tab(-1))
        
        # 目录树显示/隐藏
        QShortcut(QKeySequence("Alt+D"), self, self.toggle_tree)
        
        # 清除过滤
        QShortcut(QKeySequence("Ctrl+L"), self, self.clear_filter)
    
    def _on_panel_focus(self, panel, event):
        """面板获得焦点时的处理"""
        self.focused_panel = panel
        self.update_panel_highlight()

    def _create_tab_widget(self, side: str):
        """创建带默认标签的Tab容器"""
        tabs = QTabWidget()
        tabs.setTabsClosable(True)
        tabs.tabCloseRequested.connect(lambda idx, s=side: self._close_tab(s, idx))
        tabs.currentChanged.connect(lambda idx, s=side: self._on_tab_changed(s, idx))
        
        stored_paths = self.config.get(f"{side}_tabs", [])
        if not stored_paths:
            stored_paths = [self.config.get(f"{side}_panel_path", None)]
        if not stored_paths:
            stored_paths = [str(Path.home())]
        
        for p in stored_paths:
            self._add_tab(side, p, tabs)
        
        active = self.config.get(f"{side}_active_tab", 0)
        if active < tabs.count():
            tabs.setCurrentIndex(active)
        
        return tabs
    
    def _add_tab(self, side: str, path: str = None, tabs: QTabWidget = None):
        """创建并添加一个新标签"""
        if tabs is None:
            tabs = self.left_tabs if side == "left" else self.right_tabs
        panel = FilePanel(
            panel_name=side,
            initial_path=path,
            show_tree=self.config.get('show_tree', False),
            filter_mode=self.config.get('filter_mode', 'wildcard')
        )
        self._register_panel_focus(panel)
        tab_title = os.path.basename(panel.current_path) or panel.current_path
        tabs.addTab(panel, tab_title)
        tabs.setCurrentWidget(panel)
        if side == "left":
            self.left_panel = panel
        else:
            self.right_panel = panel
        self.focused_panel = panel
        self.update_panel_highlight()
        return panel
    
    def _register_panel_focus(self, panel: FilePanel):
        """给面板控件绑定焦点事件以追踪当前面板"""
        panel.file_list.focusInEvent = lambda e, p=panel: self._on_panel_focus(p, e)
        panel.path_input.focusInEvent = lambda e, p=panel: self._on_panel_focus(p, e)
        if hasattr(panel, "filter_input"):
            panel.filter_input.focusInEvent = lambda e, p=panel: self._on_panel_focus(p, e)
    
    def _current_panel(self, side: str):
        """获取指定侧的当前面板"""
        tabs = self.left_tabs if side == "left" else self.right_tabs
        return tabs.currentWidget()
    
    def _on_tab_changed(self, side: str, index: int):
        """标签切换时更新焦点与高亮"""
        panel = self._current_panel(side)
        if panel:
            if side == "left":
                self.left_panel = panel
            else:
                self.right_panel = panel
            self.focused_panel = panel
            tab_title = os.path.basename(panel.current_path) or panel.current_path
            tabs = self.left_tabs if side == "left" else self.right_tabs
            if index >= 0:
                tabs.setTabText(index, tab_title)
        self.update_panel_highlight()
    
    def new_tab(self):
        """在当前侧新建标签"""
        focused = self.get_focused_panel()
        side = focused.panel_name if hasattr(focused, "panel_name") else "left"
        base_path = focused.current_path if focused else str(Path.home())
        self._add_tab(side, base_path)
    
    def close_tab(self):
        """关闭当前标签，保留至少一个"""
        focused = self.get_focused_panel()
        side = focused.panel_name if hasattr(focused, "panel_name") else "left"
        tabs = self.left_tabs if side == "left" else self.right_tabs
        if tabs.count() <= 1:
            QMessageBox.information(self, "提示", "至少保留一个标签")
            return
        idx = tabs.currentIndex()
        tabs.removeTab(idx)
        self.focused_panel = self._current_panel(side)
        self.update_panel_highlight()
    
    def _close_tab(self, side: str, idx: int):
        tabs = self.left_tabs if side == "left" else self.right_tabs
        if tabs.count() <= 1:
            QMessageBox.information(self, "提示", "至少保留一个标签")
            return
        tabs.removeTab(idx)
        self.focused_panel = self._current_panel(side)
        self.update_panel_highlight()
    
    def switch_tab(self, delta: int):
        """切换标签"""
        focused = self.get_focused_panel()
        side = focused.panel_name if hasattr(focused, "panel_name") else "left"
        tabs = self.left_tabs if side == "left" else self.right_tabs
        if tabs.count() <= 1:
            return
        idx = tabs.currentIndex()
        new_idx = (idx + delta) % tabs.count()
        tabs.setCurrentIndex(new_idx)
    
    def toggle_tree(self):
        """显示/隐藏目录树（当前面板）"""
        panel = self.get_focused_panel()
        if panel:
            panel.set_show_tree(not panel.show_tree_flag)
            self.config.set('show_tree', panel.show_tree_flag)
            self.update_panel_highlight()
    
    def clear_filter(self):
        """清除当前面板过滤"""
        panel = self.get_focused_panel()
        if panel:
            panel.clear_filter()
    
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
        
        if self.focused_panel and self.left_panel and self.right_panel:
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
        if self.left_panel:
            self.left_panel.refresh()
        if self.right_panel:
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
        # 保存窗口位置和大小 + 标签状态
        left_paths = [self.left_tabs.widget(i).current_path for i in range(self.left_tabs.count())]
        right_paths = [self.right_tabs.widget(i).current_path for i in range(self.right_tabs.count())]
        self.config.update({
            'window_width': self.width(),
            'window_height': self.height(),
            'window_x': self.x(),
            'window_y': self.y(),
            'left_panel_path': self.left_panel.current_path if self.left_panel else str(Path.home()),
            'right_panel_path': self.right_panel.current_path if self.right_panel else str(Path.home()),
            'left_tabs': left_paths,
            'right_tabs': right_paths,
            'left_active_tab': self.left_tabs.currentIndex(),
            'right_active_tab': self.right_tabs.currentIndex(),
            'show_tree': self.left_panel.show_tree_flag if self.left_panel else False,
        })
        event.accept()
