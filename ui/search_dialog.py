"""
搜索对话框
"""

from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QCheckBox, QPushButton, QTableWidget, QTableWidgetItem, QMessageBox,
    QRadioButton, QButtonGroup
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
import os
from pathlib import Path


class SearchWorker(QThread):
    """后台搜索线程"""
    found_file = pyqtSignal(str)  # 信号
    finished = pyqtSignal()
    
    def __init__(self, root_path, pattern, use_regex=False, file_types=None):
        super().__init__()
        self.root_path = root_path
        self.pattern = pattern
        self.use_regex = use_regex
        self.file_types = file_types or []
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
                        # 检查文件类型过滤
                        if self.file_types:
                            ext = os.path.splitext(file_name)[1].lower()
                            if ext not in [t.lower() for t in self.file_types]:
                                continue
                        
                        file_path = os.path.join(root, file_name)
                        self.found_file.emit(file_path)
        except PermissionError:
            pass
        finally:
            self.finished.emit()
    
    def stop(self):
        """停止搜索"""
        self.stop_flag = True
    
    def _match_pattern(self, text):
        """匹配模式"""
        import re
        if self.use_regex:
            try:
                return bool(re.search(self.pattern, text, re.IGNORECASE))
            except:
                return False
        else:
            # 通配符模式
            regex_pattern = self.pattern.replace('.', r'\.').replace('*', '.*').replace('?', '.')
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
        search_layout = QVBoxLayout()
        
        # 文件名输入
        name_layout = QHBoxLayout()
        name_layout.addWidget(QLabel("文件名:"))
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("输入文件名或使用 * 通配符")
        name_layout.addWidget(self.search_input)
        search_layout.addLayout(name_layout)
        
        # 搜索模式
        mode_layout = QHBoxLayout()
        self.wildcard_radio = QRadioButton("通配符 (*, ?)")
        self.regex_radio = QRadioButton("正则表达式")
        self.wildcard_radio.setChecked(True)
        mode_group = QButtonGroup()
        mode_group.addButton(self.wildcard_radio)
        mode_group.addButton(self.regex_radio)
        mode_layout.addWidget(self.wildcard_radio)
        mode_layout.addWidget(self.regex_radio)
        mode_layout.addStretch()
        search_layout.addLayout(mode_layout)
        
        # 文件类型过滤
        type_layout = QHBoxLayout()
        type_layout.addWidget(QLabel("文件类型:"))
        self.type_filter = QLineEdit()
        self.type_filter.setPlaceholderText("例如: .txt, .py (留空表示所有类型)")
        type_layout.addWidget(self.type_filter)
        search_layout.addLayout(type_layout)
        
        # 搜索按钮
        btn_layout = QHBoxLayout()
        search_btn = QPushButton("搜索")
        search_btn.clicked.connect(self.start_search)
        btn_layout.addWidget(search_btn)
        search_layout.addLayout(btn_layout)
        
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
        
        # 解析文件类型过滤
        file_types = []
        type_filter_text = self.type_filter.text().strip()
        if type_filter_text:
            file_types = [t.strip() for t in type_filter_text.split(',') if t.strip()]
        
        # 获取搜索模式
        use_regex = self.regex_radio.isChecked()
        
        # 停止之前的搜索
        if self.search_worker:
            self.search_worker.stop()
            self.search_worker.wait()
        
        self.result_table.setRowCount(0)
        self.search_worker = SearchWorker(self.root_path, pattern, use_regex, file_types)
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
