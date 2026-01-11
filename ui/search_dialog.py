"""
搜索对话框
"""

from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QCheckBox, QPushButton, QTableWidget, QTableWidgetItem, QMessageBox
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
import os
from pathlib import Path


class SearchWorker(QThread):
    """后台搜索线程"""
    found_file = pyqtSignal(str)  # 信号
    finished = pyqtSignal()
    
    def __init__(self, root_path, pattern):
        super().__init__()
        self.root_path = root_path
        self.pattern = pattern
        self.stop_flag = False
    
    def run(self):
        """执行搜索"""
        try:
            for root, dirs, files in os.walk(self.root_path):
                if self.stop_flag:
                    break
                
                # 搜索文件
                for file_name in files:
                    if self.stop_flag:
                        break
                    
                    if self._match_pattern(file_name):
                        file_path = os.path.join(root, file_name)
                        self.found_file.emit(file_path)
        except PermissionError:
            pass
        finally:
            self.finished.emit()
    
    def stop(self):
        """停止搜索"""
        self.stop_flag = True
    
    @staticmethod
    def _match_pattern(text):
        """匹配模式"""
        import re
        pattern = '*'  # 简化版本，可扩展
        regex_pattern = pattern.replace('.', r'\.').replace('*', '.*').replace('?', '.')
        return bool(re.match(f'^{regex_pattern}$', text, re.IGNORECASE))


class SearchDialog(QDialog):
    """搜索对话框"""
    
    def __init__(self, parent=None, root_path=None):
        super().__init__(parent)
        self.root_path = root_path or str(Path.home())
        self.setWindowTitle("搜索文件")
        self.setGeometry(200, 200, 600, 400)
        self.search_worker = None
        
        # 创建布局
        layout = QVBoxLayout()
        
        # 搜索条件
        search_layout = QHBoxLayout()
        search_layout.addWidget(QLabel("文件名:"))
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("输入文件名或使用 * 通配符")
        search_layout.addWidget(self.search_input)
        
        search_btn = QPushButton("搜索")
        search_btn.clicked.connect(self.start_search)
        search_layout.addWidget(search_btn)
        
        layout.addLayout(search_layout)
        
        # 选项
        options_layout = QHBoxLayout()
        self.include_dirs = QCheckBox("包含文件夹")
        self.include_dirs.setChecked(True)
        options_layout.addWidget(self.include_dirs)
        options_layout.addStretch()
        layout.addLayout(options_layout)
        
        # 结果表格
        self.result_table = QTableWidget()
        self.result_table.setColumnCount(2)
        self.result_table.setHorizontalHeaderLabels(["文件名", "路径"])
        layout.addWidget(self.result_table)
        
        # 底部按钮
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        open_btn = QPushButton("打开")
        open_btn.clicked.connect(self.open_selected)
        button_layout.addWidget(open_btn)
        
        close_btn = QPushButton("关闭")
        close_btn.clicked.connect(self.close)
        button_layout.addWidget(close_btn)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
    
    def start_search(self):
        """开始搜索"""
        pattern = self.search_input.text().strip()
        if not pattern:
            QMessageBox.warning(self, "警告", "请输入搜索条件")
            return
        
        self.result_table.setRowCount(0)
        self.search_worker = SearchWorker(self.root_path, pattern)
        self.search_worker.found_file.connect(self.add_result)
        self.search_worker.finished.connect(self.on_search_finished)
        self.search_worker.start()
    
    def add_result(self, file_path):
        """添加搜索结果"""
        row = self.result_table.rowCount()
        self.result_table.insertRow(row)
        
        file_name = os.path.basename(file_path)
        name_item = QTableWidgetItem(file_name)
        path_item = QTableWidgetItem(file_path)
        
        self.result_table.setItem(row, 0, name_item)
        self.result_table.setItem(row, 1, path_item)
    
    def on_search_finished(self):
        """搜索完成"""
        count = self.result_table.rowCount()
        QMessageBox.information(self, "搜索完成", f"找到 {count} 个结果")
    
    def open_selected(self):
        """打开选中项"""
        current_row = self.result_table.currentRow()
        if current_row >= 0:
            file_path = self.result_table.item(current_row, 1).text()
            if os.path.exists(file_path):
                os.startfile(file_path) if os.name == 'nt' else os.system(f'open "{file_path}"')
            else:
                QMessageBox.warning(self, "错误", "文件不存在")
