"""
书签管理器
"""

import os
from pathlib import Path
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QListWidget, 
    QListWidgetItem, QPushButton, QLineEdit, QMessageBox, QDialog,
    QDialogButtonBox, QInputDialog
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon


class BookmarkManager:
    """书签管理器 - 单例模式"""
    
    _instance = None
    _bookmarks = []
    _config_file = None
    
    def __new__(cls, config_manager=None):
        if cls._instance is None:
            cls._instance = super(BookmarkManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self, config_manager=None):
        if self._initialized:
            return
        
        self._initialized = True
        if config_manager:
            self._config_manager = config_manager
            self._config_file = config_manager.config_file.parent / 'bookmarks.json'
        else:
            from .config import ConfigManager
            self._config_manager = ConfigManager()
            self._config_file = self._config_manager.config_file.parent / 'bookmarks.json'
        
        self.load_bookmarks()
    
    def load_bookmarks(self):
        """从配置文件加载书签"""
        import json
        if self._config_file.exists():
            try:
                with open(self._config_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self._bookmarks = data.get('bookmarks', [])
            except Exception as e:
                self._bookmarks = []
        else:
            # 默认书签
            self._bookmarks = [
                {'name': '我的文档', 'path': str(Path.home() / 'Documents')},
                {'name': '下载', 'path': str(Path.home() / 'Downloads')},
                {'name': '桌面', 'path': str(Path.home() / 'Desktop')},
            ]
            self.save_bookmarks()
    
    def save_bookmarks(self):
        """保存书签到配置文件"""
        import json
        try:
            with open(self._config_file, 'w', encoding='utf-8') as f:
                json.dump({'bookmarks': self._bookmarks}, f, ensure_ascii=False, indent=2)
        except Exception as e:
            pass
    
    def get_bookmarks(self):
        """获取所有书签"""
        return self._bookmarks.copy()
    
    def add_bookmark(self, name, path):
        """添加书签"""
        if not os.path.exists(path):
            return False
        
        # 检查是否已存在
        for bookmark in self._bookmarks:
            if bookmark['path'] == path:
                return False
        
        self._bookmarks.append({'name': name, 'path': path})
        self.save_bookmarks()
        return True
    
    def remove_bookmark(self, path):
        """删除书签"""
        self._bookmarks = [b for b in self._bookmarks if b['path'] != path]
        self.save_bookmarks()
    
    def update_bookmark(self, old_path, new_name, new_path=None):
        """更新书签"""
        for bookmark in self._bookmarks:
            if bookmark['path'] == old_path:
                bookmark['name'] = new_name
                if new_path:
                    bookmark['path'] = new_path
                self.save_bookmarks()
                return True
        return False


class BookmarkDialog(QDialog):
    """书签管理对话框"""
    
    def __init__(self, parent=None, current_path=None):
        super().__init__(parent)
        self.parent_window = parent
        self.current_path = current_path
        self.bookmark_manager = BookmarkManager()
        
        self.setWindowTitle("书签管理")
        self.setMinimumWidth(500)
        self.setMinimumHeight(400)
        
        self.init_ui()
        self.load_bookmarks()
    
    def init_ui(self):
        """初始化UI"""
        layout = QVBoxLayout()
        
        # 说明
        info_label = QLabel("管理常用文件夹书签，快速访问")
        info_label.setStyleSheet("color: #666; padding: 5px;")
        layout.addWidget(info_label)
        
        # 书签列表
        self.bookmark_list = QListWidget()
        self.bookmark_list.setAlternatingRowColors(True)
        layout.addWidget(self.bookmark_list)
        
        # 按钮区域
        button_layout = QHBoxLayout()
        
        add_btn = QPushButton("添加当前路径")
        add_btn.clicked.connect(self.add_current_path)
        button_layout.addWidget(add_btn)
        
        add_custom_btn = QPushButton("添加自定义")
        add_custom_btn.clicked.connect(self.add_custom)
        button_layout.addWidget(add_custom_btn)
        
        edit_btn = QPushButton("编辑")
        edit_btn.clicked.connect(self.edit_bookmark)
        button_layout.addWidget(edit_btn)
        
        remove_btn = QPushButton("删除")
        remove_btn.clicked.connect(self.remove_bookmark)
        button_layout.addWidget(remove_btn)
        
        button_layout.addStretch()
        
        goto_btn = QPushButton("转到")
        goto_btn.setStyleSheet("background-color: #0078d4; color: white; padding: 6px 20px;")
        goto_btn.clicked.connect(self.goto_bookmark)
        button_layout.addWidget(goto_btn)
        
        layout.addLayout(button_layout)
        
        # 对话框按钮
        button_box = QDialogButtonBox(QDialogButtonBox.Close)
        button_box.rejected.connect(self.accept)
        layout.addWidget(button_box)
        
        self.setLayout(layout)
    
    def load_bookmarks(self):
        """加载书签列表"""
        self.bookmark_list.clear()
        bookmarks = self.bookmark_manager.get_bookmarks()
        
        for bookmark in bookmarks:
            name = bookmark['name']
            path = bookmark['path']
            
            # 检查路径是否存在
            exists = os.path.exists(path)
            display_text = f"{name}" if exists else f"{name} (路径不存在)"
            
            item = QListWidgetItem(display_text)
            item.setData(Qt.UserRole, path)
            if not exists:
                item.setForeground(Qt.gray)
            self.bookmark_list.addItem(item)
    
    def add_current_path(self):
        """添加当前路径为书签"""
        if not self.current_path or not os.path.exists(self.current_path):
            QMessageBox.warning(self, "错误", "当前路径无效")
            return
        
        name, ok = QInputDialog.getText(
            self, 
            "添加书签", 
            "请输入书签名称:",
            text=os.path.basename(self.current_path) or self.current_path
        )
        
        if ok and name:
            if self.bookmark_manager.add_bookmark(name, self.current_path):
                self.load_bookmarks()
                QMessageBox.information(self, "成功", "书签已添加")
            else:
                QMessageBox.warning(self, "提示", "该路径已存在书签中")
    
    def add_custom(self):
        """添加自定义书签"""
        from PyQt5.QtWidgets import QFileDialog
        
        path = QFileDialog.getExistingDirectory(self, "选择文件夹")
        if path:
            name, ok = QInputDialog.getText(
                self, 
                "添加书签", 
                "请输入书签名称:",
                text=os.path.basename(path) or path
            )
            
            if ok and name:
                if self.bookmark_manager.add_bookmark(name, path):
                    self.load_bookmarks()
                    QMessageBox.information(self, "成功", "书签已添加")
                else:
                    QMessageBox.warning(self, "提示", "该路径已存在书签中")
    
    def edit_bookmark(self):
        """编辑书签"""
        current_item = self.bookmark_list.currentItem()
        if not current_item:
            QMessageBox.information(self, "提示", "请先选择要编辑的书签")
            return
        
        old_path = current_item.data(Qt.UserRole)
        bookmarks = self.bookmark_manager.get_bookmarks()
        bookmark = next((b for b in bookmarks if b['path'] == old_path), None)
        
        if not bookmark:
            return
        
        name, ok = QInputDialog.getText(
            self, 
            "编辑书签", 
            "请输入新名称:",
            text=bookmark['name']
        )
        
        if ok and name:
            self.bookmark_manager.update_bookmark(old_path, name)
            self.load_bookmarks()
    
    def remove_bookmark(self):
        """删除书签"""
        current_item = self.bookmark_list.currentItem()
        if not current_item:
            QMessageBox.information(self, "提示", "请先选择要删除的书签")
            return
        
        path = current_item.data(Qt.UserRole)
        reply = QMessageBox.question(
            self,
            "确认删除",
            "确定要删除这个书签吗？",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.bookmark_manager.remove_bookmark(path)
            self.load_bookmarks()
    
    def goto_bookmark(self):
        """转到选中的书签"""
        current_item = self.bookmark_list.currentItem()
        if not current_item:
            QMessageBox.information(self, "提示", "请先选择一个书签")
            return
        
        path = current_item.data(Qt.UserRole)
        if not os.path.exists(path):
            QMessageBox.warning(self, "错误", "路径不存在")
            return
        
        # 通知主窗口切换路径
        if self.parent_window:
            focused = self.parent_window.get_focused_panel()
            if focused:
                focused.set_path(path)
                self.accept()
