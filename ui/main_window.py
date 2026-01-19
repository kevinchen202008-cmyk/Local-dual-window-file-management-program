"""
主窗口类 - 双面板布局
"""

import os
from pathlib import Path
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, 
    QMenuBar, QToolBar, QPushButton, QMessageBox, QShortcut, QMenu,
    QTabWidget, QSplitter
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
        
        # 创建主布局 - FreeCommander风格：紧凑布局（高度增加50%）
        layout = QHBoxLayout()
        layout.setContentsMargins(4, 3, 2, 3)  # 增加上下内边距以适应更高高度
        layout.setSpacing(2)  # 最小间距
        
        # 设置背景色
        self.setStyleSheet("""
            QWidget {
                background-color: #F3F3F3;
                border-bottom: 1px solid #E0E0E0;
            }
        """)
        
        # 标题文本 - FreeCommander风格：完整显示标题
        from PyQt5.QtWidgets import QLabel
        title_label = QLabel("文件管理器")
        title_label.setStyleSheet("font-weight: bold; color: #333333; font-size: 9pt; padding: 2px 0px;")
        title_label.setMinimumWidth(120)  # 设置最小宽度，确保文字完整显示
        layout.addWidget(title_label)
        
        # 伸缩空间
        layout.addStretch()
        
        # 窗口控制按钮 - FreeCommander风格：紧凑小按钮
        if parent:
            # 紧凑的按钮样式（高度增加50%）
            button_style = """
                QPushButton {
                    background-color: transparent;
                    border: none;
                    color: #333333;
                    padding: 4px 8px;
                    min-width: 30px;
                    max-width: 30px;
                    min-height: 30px;
                    max-height: 30px;
                    font-size: 10pt;
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
                    padding: 4px 8px;
                    min-width: 30px;
                    max-width: 30px;
                    min-height: 30px;
                    max-height: 30px;
                    font-size: 10pt;
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
        # 固定标题栏高度（基于24px增加50% = 36px）
        self.setFixedHeight(36)
    
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
    
    def _create_menu_buttons(self, layout, menu_bar):
        """创建水平排列的菜单按钮"""
        from PyQt5.QtWidgets import QPushButton, QMenu, QLabel
        
        # 按钮样式
        button_style = """
            QPushButton {
                background-color: transparent;
                border: none;
                color: #333333;
                padding: 4px 8px;
                font-size: 9pt;
                text-align: left;
            }
            QPushButton:hover {
                background-color: #E0E0E0;
                border-radius: 2px;
            }
            QPushButton:pressed {
                background-color: #D0D0D0;
            }
        """
        
        # 提取菜单项并创建按钮
        actions = menu_bar.actions()
        for action in actions:
            if action.isSeparator():
                # 分隔符用竖线表示
                separator = QLabel("|")
                separator.setStyleSheet("color: #CCCCCC; padding: 0px 4px;")
                layout.addWidget(separator)
            else:
                # 创建按钮
                menu = action.menu()  # 获取菜单对象
                if menu:
                    # 这是顶级菜单（如"文件"、"编辑"），显示下拉菜单
                    btn = QPushButton(action.text().replace("&", ""))  # 移除快捷键标记
                    btn.setStyleSheet(button_style)
                    btn.setText(btn.text() + " ▼")
                    
                    # 创建下拉菜单，直接使用原始菜单
                    def create_menu_handler(m):
                        def show_menu():
                            btn_pos = btn.mapToGlobal(btn.rect().bottomLeft())
                            m.popup(btn_pos)
                        return show_menu
                    
                    btn.clicked.connect(create_menu_handler(menu))
                    layout.addWidget(btn)
                else:
                    # 这是直接动作（虽然菜单栏通常不会有直接动作，但为了兼容性保留）
                    btn = QPushButton(action.text().replace("&", ""))
                    btn.setStyleSheet(button_style)
                    btn.clicked.connect(lambda checked=False, a=action: a.trigger())
                    layout.addWidget(btn)


class ToolBar(QWidget):
    """工具栏 - 独占一行，包含上级、刷新、同步路径"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # 创建主布局 - FreeCommander风格：紧凑工具栏
        layout = QHBoxLayout()
        layout.setContentsMargins(4, 4, 4, 4)  # 增加上下内边距，避免太矮
        layout.setSpacing(2)  # 最小间距
        
        # 设置背景色
        self.setStyleSheet("""
            QWidget {
                background-color: #F5F5F5;
                border-bottom: 1px solid #E0E0E0;
            }
        """)
        
        # 返回上级 - 紧凑按钮
        self.up_btn = QPushButton("⬆ 上级")
        self.up_btn.setMinimumWidth(70)
        self.up_btn.setMinimumHeight(28)  # 增加按钮高度
        self.up_btn.setMaximumHeight(32)
        self.apply_button_style(self.up_btn)
        layout.addWidget(self.up_btn)
        
        # 分隔符 - 更细更短
        separator1 = QWidget()
        separator1.setStyleSheet("background-color: #D0D0D0;")
        separator1.setMaximumWidth(1)
        separator1.setMinimumHeight(16)
        layout.addWidget(separator1)
        
        # 刷新 - 紧凑按钮
        self.refresh_btn = QPushButton("📁 刷新")
        self.refresh_btn.setMinimumWidth(70)
        self.refresh_btn.setMinimumHeight(28)  # 增加按钮高度
        self.refresh_btn.setMaximumHeight(32)
        self.apply_button_style(self.refresh_btn)
        layout.addWidget(self.refresh_btn)
        
        # 分隔符
        separator2 = QWidget()
        separator2.setStyleSheet("background-color: #D0D0D0;")
        separator2.setMaximumWidth(1)
        separator2.setMinimumHeight(16)
        layout.addWidget(separator2)
        
        # 同步路径 - 紧凑按钮
        self.sync_btn = QPushButton("⟷ 同步")
        self.sync_btn.setMinimumWidth(70)
        self.sync_btn.setMinimumHeight(28)  # 增加按钮高度
        self.sync_btn.setMaximumHeight(32)
        self.apply_button_style(self.sync_btn)
        layout.addWidget(self.sync_btn)
        
        # 伸缩
        layout.addStretch()
        
        self.setLayout(layout)
        # 高度由MainWindow统一设置，避免重叠
    
    def apply_button_style(self, button):
        """应用按钮样式 - FreeCommander风格：紧凑按钮"""
        button.setStyleSheet("""
            QPushButton {
                background-color: #FFFFFF;
                border: 1px solid #D0D0D0;
                border-radius: 2px;
                padding: 2px 8px;
                font-weight: normal;
                font-size: 9pt;
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
        main_layout.setSpacing(0)  # 间距为0，但通过固定高度避免重叠
        
        # 创建标题栏（仅包含标题和窗口控制按钮）- FreeCommander风格
        self.title_bar = TitleBar(self, None)
        self.title_bar.setFixedHeight(36)  # 确保固定高度，避免重叠
        main_layout.addWidget(self.title_bar)
        
        # 创建自定义菜单栏（独立一行，在标题栏下方）- FreeCommander风格
        # 使用自定义widget确保所有菜单项水平展开，不被折叠
        custom_menu_bar = self._create_custom_menu_bar()
        custom_menu_bar.setFixedHeight(40)  # 增加菜单栏高度，确保字体完整显示
        main_layout.addWidget(custom_menu_bar)
        
        # 保存原始菜单栏引用（用于快捷键等功能）
        self._original_menu_bar = create_menu_bar(self)
        self._original_menu_bar.hide()
        
        # 监听窗口状态变化，更新最大化按钮
        self.installEventFilter(self)
        
        # 创建工具栏
        self.toolbar = ToolBar(self)
        self.toolbar.setFixedHeight(36)  # 增加工具栏高度，避免太矮和重叠
        self.toolbar.up_btn.clicked.connect(self.go_up)
        self.toolbar.refresh_btn.clicked.connect(self.refresh_panels)
        self.toolbar.sync_btn.clicked.connect(self.sync_paths)
        main_layout.addWidget(self.toolbar)
        
        # 创建文件面板容器（使用Splitter以支持预览面板）
        panels_splitter = QSplitter(Qt.Horizontal)
        
        # 左侧标签容器
        self.left_tabs = self._create_tab_widget("left")
        panels_splitter.addWidget(self.left_tabs)
        
        # 右侧标签容器
        self.right_tabs = self._create_tab_widget("right")
        panels_splitter.addWidget(self.right_tabs)
        
        # 创建预览面板（默认隐藏）
        from .preview_panel import PreviewPanel
        self.preview_panel = PreviewPanel(self)
        self.preview_panel.hide()
        panels_splitter.addWidget(self.preview_panel)
        
        # 设置Splitter比例
        panels_splitter.setStretchFactor(0, 1)
        panels_splitter.setStretchFactor(1, 1)
        panels_splitter.setStretchFactor(2, 0)
        
        # 默认焦点在左面板
        self.left_panel = self._current_panel("left")
        self.right_panel = self._current_panel("right")
        self.focused_panel = self.left_panel
        
        main_layout.addWidget(panels_splitter)
        
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
    
    def _create_custom_menu_bar(self):
        """创建自定义菜单栏widget，确保所有菜单项水平展开"""
        from PyQt5.QtWidgets import QPushButton, QLabel
        
        # 创建菜单栏容器
        menu_widget = QWidget()
        menu_layout = QHBoxLayout()
        menu_layout.setContentsMargins(4, 6, 4, 6)  # 增加上下内边距，确保字体完整显示
        menu_layout.setSpacing(0)
        
        # 设置背景色
        menu_widget.setStyleSheet("""
            QWidget {
                background-color: #F5F5F5;
                border-bottom: 1px solid #E0E0E0;
            }
        """)
        
        # 按钮样式
        button_style = """
            QPushButton {
                background-color: transparent;
                border: none;
                color: #333333;
                padding: 6px 10px;
                font-size: 10pt;
                text-align: left;
                min-height: 28px;
            }
            QPushButton:hover {
                background-color: #E0E0E0;
                border-radius: 2px;
            }
            QPushButton:pressed {
                background-color: #D0D0D0;
            }
        """
        
        # 获取原始菜单栏以提取菜单
        original_menu_bar = create_menu_bar(self)
        original_menu_bar.hide()  # 隐藏原始菜单栏，只用来获取菜单
        
        # 为每个菜单创建按钮
        for action in original_menu_bar.actions():
            if action.isSeparator():
                # 分隔符用竖线表示
                separator = QLabel("|")
                separator.setStyleSheet("color: #CCCCCC; padding: 0px 4px;")
                menu_layout.addWidget(separator)
            else:
                menu = action.menu()
                if menu:
                    # 创建菜单按钮（保留&符号以显示快捷键）
                    btn = QPushButton(action.text())  # 保留&符号
                    btn.setStyleSheet(button_style)
                    
                    # 连接点击事件，显示下拉菜单
                    def create_menu_handler(m, b=btn):
                        def show_menu():
                            btn_pos = b.mapToGlobal(b.rect().bottomLeft())
                            m.popup(btn_pos)
                        return show_menu
                    
                    btn.clicked.connect(create_menu_handler(menu))
                    menu_layout.addWidget(btn)
        
        menu_layout.addStretch()  # 添加伸缩空间，确保按钮靠左
        menu_widget.setLayout(menu_layout)
        
        return menu_widget
    
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
        
        # 预览快捷键
        QShortcut(QKeySequence("F3"), self, self.toggle_preview)
        
        # 目录树显示/隐藏
        QShortcut(QKeySequence("Alt+D"), self, self.toggle_tree)
        
        # 清除过滤
        QShortcut(QKeySequence("Ctrl+L"), self, self.clear_filter)
        
        # 历史记录导航
        QShortcut(QKeySequence("Alt+Left"), self, self.go_back)
        QShortcut(QKeySequence("Alt+Right"), self, self.go_forward)
        
        # 撤销/重做
        QShortcut(QKeySequence("Ctrl+Z"), self, self.undo_operation)
        QShortcut(QKeySequence("Ctrl+Y"), self, self.redo_operation)
    
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
        
        # 创建路径改变回调函数，用于更新标签标题
        def update_tab_title(panel):
            """当面板路径改变时，更新对应的标签标题"""
            tabs_widget = self.left_tabs if side == "left" else self.right_tabs
            if tabs_widget:
                for i in range(tabs_widget.count()):
                    if tabs_widget.widget(i) == panel:
                        tab_title = os.path.basename(panel.current_path) or panel.current_path
                        tabs_widget.setTabText(i, tab_title)
                        break
        
        panel = FilePanel(
            panel_name=side,
            initial_path=path,
            show_tree=self.config.get('show_tree', False),
            filter_mode=self.config.get('filter_mode', 'wildcard'),
            on_path_changed_callback=update_tab_title
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
        """获取指定侧的当前面板
        
        注意：在窗口初始化早期，Tab容器属性可能尚未创建，需做安全检查。
        """
        if side == "left":
            tabs = getattr(self, "left_tabs", None)
        else:
            tabs = getattr(self, "right_tabs", None)
        
        if tabs is None:
            return None
        
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
            tabs = getattr(self, "left_tabs", None) if side == "left" else getattr(self, "right_tabs", None)
            if tabs is not None and index >= 0:
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
        
        # 在窗口初始化早期，left_panel/right_panel 可能尚未完全创建，需做安全检查
        if not hasattr(self, "left_panel") or not hasattr(self, "right_panel"):
            return
        
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
    
    def go_back(self):
        """后退"""
        focused = self.get_focused_panel()
        if focused:
            focused.go_back()
    
    def go_forward(self):
        """前进"""
        focused = self.get_focused_panel()
        if focused:
            focused.go_forward()
    
    def undo_operation(self):
        """撤销操作"""
        from .menu_bar import on_undo
        on_undo(self)
    
    def redo_operation(self):
        """重做操作"""
        from .menu_bar import on_redo
        on_redo(self)
    
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
    
    def toggle_preview(self):
        """切换预览面板显示/隐藏，如果选中文件则预览"""
        focused = self.get_focused_panel()
        if focused:
            selected = focused.get_selected_items()
            if selected and len(selected) == 1:
                file_path = selected[0][1]
                if os.path.isfile(file_path):
                    self.preview_panel.preview_file(file_path)
                    self.preview_panel.show()
                    return
        
        # 如果没有选中文件，则切换显示状态
        if self.preview_panel.isVisible():
            self.preview_panel.hide()
        else:
            self.preview_panel.show()
    
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
