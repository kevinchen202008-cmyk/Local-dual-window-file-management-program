"""
重复文件查找对话框
"""

import os
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QTableWidget, QTableWidgetItem, QMessageBox, QFileDialog,
    QProgressBar, QGroupBox, QComboBox, QCheckBox, QLineEdit
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from services.hash_service import HashService


class DuplicateFinderWorker(QThread):
    """重复文件查找工作线程"""
    
    progress = pyqtSignal(int, int)  # current, total
    finished = pyqtSignal(dict)  # duplicates dict
    error = pyqtSignal(str)
    
    def __init__(self, directory, algorithm='md5'):
        super().__init__()
        self.directory = directory
        self.algorithm = algorithm
        self.cancelled = False
    
    def run(self):
        """执行查找"""
        try:
            duplicates = HashService.find_duplicates(
                self.directory,
                self.algorithm,
                self.progress.emit
            )
            if not self.cancelled:
                self.finished.emit(duplicates)
        except Exception as e:
            if not self.cancelled:
                self.error.emit(str(e))
    
    def cancel(self):
        """取消查找"""
        self.cancelled = True


class DuplicateFinderDialog(QDialog):
    """重复文件查找对话框"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_window = parent
        self.duplicates = {}
        self.worker = None
        
        self.setWindowTitle("查找重复文件")
        self.setMinimumWidth(800)
        self.setMinimumHeight(600)
        
        self.init_ui()
    
    def init_ui(self):
        """初始化UI"""
        layout = QVBoxLayout()
        
        # 设置区域
        settings_group = QGroupBox("查找设置")
        settings_layout = QVBoxLayout()
        
        # 目录选择
        dir_layout = QHBoxLayout()
        dir_layout.addWidget(QLabel("搜索目录:"))
        self.dir_input = QLineEdit()
        self.dir_input.setText(str(os.path.expanduser("~")))
        dir_layout.addWidget(self.dir_input)
        
        browse_btn = QPushButton("浏览...")
        browse_btn.clicked.connect(self.browse_directory)
        dir_layout.addWidget(browse_btn)
        settings_layout.addLayout(dir_layout)
        
        # 算法选择
        algo_layout = QHBoxLayout()
        algo_layout.addWidget(QLabel("哈希算法:"))
        self.algo_combo = QComboBox()
        self.algo_combo.addItems(["MD5", "SHA1", "SHA256"])
        settings_layout.addLayout(algo_layout)
        
        # 查找选项
        self.size_only_check = QCheckBox("仅比较文件大小（快速模式）")
        settings_layout.addWidget(self.size_only_check)
        
        settings_group.setLayout(settings_layout)
        layout.addWidget(settings_group)
        
        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        # 结果表格
        result_label = QLabel("重复文件列表:")
        result_label.setStyleSheet("font-weight: bold; margin-top: 10px;")
        layout.addWidget(result_label)
        
        self.result_table = QTableWidget()
        self.result_table.setColumnCount(4)
        self.result_table.setHorizontalHeaderLabels(["文件名", "路径", "大小", "哈希值"])
        self.result_table.horizontalHeader().setStretchLastSection(False)
        self.result_table.horizontalHeader().setSectionResizeMode(0, QTableWidget.ResizeToContents)
        self.result_table.horizontalHeader().setSectionResizeMode(1, QTableWidget.Stretch)
        self.result_table.horizontalHeader().setSectionResizeMode(2, QTableWidget.ResizeToContents)
        self.result_table.horizontalHeader().setSectionResizeMode(3, QTableWidget.ResizeToContents)
        self.result_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.result_table.setSelectionBehavior(QTableWidget.SelectRows)
        layout.addWidget(self.result_table)
        
        # 统计信息
        self.stats_label = QLabel("")
        self.stats_label.setStyleSheet("color: #666; padding: 5px;")
        layout.addWidget(self.stats_label)
        
        # 按钮
        button_layout = QHBoxLayout()
        
        self.find_btn = QPushButton("开始查找")
        self.find_btn.setStyleSheet("background-color: #0078d4; color: white; padding: 6px 20px;")
        self.find_btn.clicked.connect(self.start_find)
        button_layout.addWidget(self.find_btn)
        
        self.cancel_btn = QPushButton("取消")
        self.cancel_btn.setEnabled(False)
        self.cancel_btn.clicked.connect(self.cancel_find)
        button_layout.addWidget(self.cancel_btn)
        
        delete_btn = QPushButton("删除选中")
        delete_btn.clicked.connect(self.delete_selected)
        button_layout.addWidget(delete_btn)
        
        button_layout.addStretch()
        
        close_btn = QPushButton("关闭")
        close_btn.clicked.connect(self.accept)
        button_layout.addWidget(close_btn)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
    
    def browse_directory(self):
        """浏览目录"""
        directory = QFileDialog.getExistingDirectory(self, "选择搜索目录", self.dir_input.text())
        if directory:
            self.dir_input.setText(directory)
    
    def start_find(self):
        """开始查找"""
        directory = self.dir_input.text().strip()
        if not os.path.isdir(directory):
            QMessageBox.warning(self, "错误", "请选择有效的目录")
            return
        
        # 清空结果
        self.result_table.setRowCount(0)
        self.duplicates = {}
        
        # 显示进度条
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.progress_bar.setMaximum(0)
        
        # 禁用按钮
        self.find_btn.setEnabled(False)
        self.cancel_btn.setEnabled(True)
        
        # 启动工作线程
        algorithm = self.algo_combo.currentText().lower()
        self.worker = DuplicateFinderWorker(directory, algorithm)
        self.worker.progress.connect(self.on_progress)
        self.worker.finished.connect(self.on_finished)
        self.worker.error.connect(self.on_error)
        self.worker.start()
    
    def cancel_find(self):
        """取消查找"""
        if self.worker:
            self.worker.cancel()
            self.worker.wait()
        
        self.progress_bar.setVisible(False)
        self.find_btn.setEnabled(True)
        self.cancel_btn.setEnabled(False)
    
    def on_progress(self, current, total):
        """进度更新"""
        if total > 0:
            self.progress_bar.setMaximum(total)
            self.progress_bar.setValue(current)
            self.stats_label.setText(f"正在扫描: {current}/{total} 文件...")
    
    def on_finished(self, duplicates):
        """查找完成"""
        self.duplicates = duplicates
        self.display_results()
        
        self.progress_bar.setVisible(False)
        self.find_btn.setEnabled(True)
        self.cancel_btn.setEnabled(False)
    
    def on_error(self, error_msg):
        """查找错误"""
        QMessageBox.critical(self, "错误", f"查找失败: {error_msg}")
        self.progress_bar.setVisible(False)
        self.find_btn.setEnabled(True)
        self.cancel_btn.setEnabled(False)
    
    def display_results(self):
        """显示结果"""
        self.result_table.setRowCount(0)
        
        total_duplicates = 0
        total_groups = len(self.duplicates)
        
        for hash_value, file_paths in self.duplicates.items():
            for file_path in file_paths:
                row = self.result_table.rowCount()
                self.result_table.insertRow(row)
                
                file_name = os.path.basename(file_path)
                file_size = os.path.getsize(file_path)
                size_str = self.format_size(file_size)
                
                self.result_table.setItem(row, 0, QTableWidgetItem(file_name))
                self.result_table.setItem(row, 1, QTableWidgetItem(file_path))
                self.result_table.setItem(row, 2, QTableWidgetItem(size_str))
                
                hash_item = QTableWidgetItem(hash_value[:16] + "...")
                hash_item.setToolTip(hash_value)
                self.result_table.setItem(row, 3, hash_item)
                
                total_duplicates += 1
        
        self.stats_label.setText(
            f"找到 {total_groups} 组重复文件，共 {total_duplicates} 个文件"
        )
    
    def delete_selected(self):
        """删除选中的文件"""
        selected_rows = set()
        for index in self.result_table.selectedIndexes():
            selected_rows.add(index.row())
        
        if not selected_rows:
            QMessageBox.information(self, "提示", "请先选择要删除的文件")
            return
        
        file_count = len(selected_rows)
        reply = QMessageBox.question(
            self,
            "确认删除",
            f"确定要删除选中的 {file_count} 个文件吗？\n此操作不可恢复！",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            deleted_count = 0
            failed_count = 0
            
            for row in selected_rows:
                file_path = self.result_table.item(row, 1).text()
                try:
                    if os.path.isfile(file_path):
                        os.remove(file_path)
                        deleted_count += 1
                except Exception as e:
                    failed_count += 1
                    QMessageBox.warning(self, "错误", f"删除失败: {file_path}\n{str(e)}")
            
            QMessageBox.information(
                self,
                "完成",
                f"删除完成！\n成功: {deleted_count}\n失败: {failed_count}"
            )
            
            # 刷新结果
            self.start_find()
    
    @staticmethod
    def format_size(size):
        """格式化文件大小"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024:
                return f"{size:.2f} {unit}"
            size /= 1024
        return f"{size:.2f} TB"
