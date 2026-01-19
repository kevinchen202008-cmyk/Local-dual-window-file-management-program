"""
压缩/解压对话框
"""

import os
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QPushButton, QFileDialog, QMessageBox, QProgressBar,
    QGroupBox, QRadioButton, QButtonGroup
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from .archive_service import ArchiveService


class ArchiveWorker(QThread):
    """压缩/解压工作线程"""
    
    progress = pyqtSignal(int, int, str)  # current, total, filename
    finished = pyqtSignal(str)  # result message
    error = pyqtSignal(str)
    
    def __init__(self, operation, zip_path, source_paths=None, extract_to=None):
        super().__init__()
        self.operation = operation  # 'create' or 'extract'
        self.zip_path = zip_path
        self.source_paths = source_paths
        self.extract_to = extract_to
        self.cancelled = False
    
    def run(self):
        """执行操作"""
        try:
            if self.operation == 'create':
                ArchiveService.create_zip(
                    self.zip_path,
                    self.source_paths,
                    self.progress.emit
                )
                self.finished.emit(f"压缩完成: {os.path.basename(self.zip_path)}")
            
            elif self.operation == 'extract':
                extract_dir = ArchiveService.extract_zip(
                    self.zip_path,
                    self.extract_to,
                    self.progress.emit
                )
                self.finished.emit(f"解压完成: {extract_dir}")
        
        except Exception as e:
            if not self.cancelled:
                self.error.emit(str(e))
    
    def cancel(self):
        """取消操作"""
        self.cancelled = True


class ArchiveDialog(QDialog):
    """压缩/解压对话框"""
    
    def __init__(self, parent=None, file_paths=None, operation='create'):
        super().__init__(parent)
        self.parent_window = parent
        self.file_paths = file_paths or []
        self.operation = operation  # 'create' or 'extract'
        self.worker = None
        
        if operation == 'create':
            self.setWindowTitle("压缩文件")
        else:
            self.setWindowTitle("解压文件")
        
        self.setMinimumWidth(500)
        self.init_ui()
    
    def init_ui(self):
        """初始化UI"""
        layout = QVBoxLayout()
        
        if self.operation == 'create':
            # 压缩模式
            source_group = QGroupBox("要压缩的文件/文件夹")
            source_layout = QVBoxLayout()
            
            if self.file_paths:
                source_label = QLabel("\n".join([os.path.basename(p) for p in self.file_paths[:5]]))
                if len(self.file_paths) > 5:
                    source_label.setText(source_label.text() + f"\n... 共 {len(self.file_paths)} 项")
            else:
                source_label = QLabel("未选择文件")
            
            source_layout.addWidget(source_label)
            source_group.setLayout(source_layout)
            layout.addWidget(source_group)
            
            # 目标路径
            target_layout = QHBoxLayout()
            target_layout.addWidget(QLabel("保存为:"))
            self.target_input = QLineEdit()
            self.target_input.setPlaceholderText("选择保存位置和文件名...")
            target_layout.addWidget(self.target_input)
            
            browse_btn = QPushButton("浏览...")
            browse_btn.clicked.connect(self.browse_save_path)
            target_layout.addWidget(browse_btn)
            layout.addLayout(target_layout)
        
        else:
            # 解压模式
            zip_layout = QHBoxLayout()
            zip_layout.addWidget(QLabel("ZIP文件:"))
            self.zip_input = QLineEdit()
            if self.file_paths:
                self.zip_input.setText(self.file_paths[0])
            zip_layout.addWidget(self.zip_input)
            
            browse_zip_btn = QPushButton("浏览...")
            browse_zip_btn.clicked.connect(self.browse_zip_file)
            zip_layout.addWidget(browse_zip_btn)
            layout.addLayout(zip_layout)
            
            # 解压位置
            extract_layout = QHBoxLayout()
            extract_layout.addWidget(QLabel("解压到:"))
            self.extract_input = QLineEdit()
            if self.file_paths:
                self.extract_input.setText(os.path.dirname(self.file_paths[0]))
            extract_layout.addWidget(self.extract_input)
            
            browse_extract_btn = QPushButton("浏览...")
            browse_extract_btn.clicked.connect(self.browse_extract_path)
            extract_layout.addWidget(browse_extract_btn)
            layout.addLayout(extract_layout)
        
        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        self.status_label = QLabel("")
        self.status_label.setStyleSheet("color: #666; padding: 5px;")
        layout.addWidget(self.status_label)
        
        # 按钮
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.start_btn = QPushButton("开始" if self.operation == 'create' else "解压")
        self.start_btn.setStyleSheet("background-color: #0078d4; color: white; padding: 6px 20px;")
        self.start_btn.clicked.connect(self.start_operation)
        button_layout.addWidget(self.start_btn)
        
        self.cancel_btn = QPushButton("取消")
        self.cancel_btn.setEnabled(False)
        self.cancel_btn.clicked.connect(self.cancel_operation)
        button_layout.addWidget(self.cancel_btn)
        
        close_btn = QPushButton("关闭")
        close_btn.clicked.connect(self.accept)
        button_layout.addWidget(close_btn)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
    
    def browse_save_path(self):
        """浏览保存路径"""
        default_name = "archive.zip"
        if self.file_paths:
            base_name = os.path.basename(self.file_paths[0])
            default_name = os.path.splitext(base_name)[0] + ".zip"
        
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "保存压缩文件",
            default_name,
            "ZIP文件 (*.zip)"
        )
        
        if file_path:
            self.target_input.setText(file_path)
    
    def browse_zip_file(self):
        """浏览ZIP文件"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "选择ZIP文件",
            "",
            "ZIP文件 (*.zip)"
        )
        
        if file_path:
            self.zip_input.setText(file_path)
            # 自动设置解压目录
            self.extract_input.setText(os.path.dirname(file_path))
    
    def browse_extract_path(self):
        """浏览解压路径"""
        directory = QFileDialog.getExistingDirectory(
            self,
            "选择解压目录",
            self.extract_input.text()
        )
        
        if directory:
            self.extract_input.setText(directory)
    
    def start_operation(self):
        """开始操作"""
        if self.operation == 'create':
            if not self.file_paths:
                QMessageBox.warning(self, "错误", "请先选择要压缩的文件")
                return
            
            target_path = self.target_input.text().strip()
            if not target_path:
                QMessageBox.warning(self, "错误", "请选择保存位置")
                return
            
            if not target_path.endswith('.zip'):
                target_path += '.zip'
            
            # 检查目标文件是否已存在
            if os.path.exists(target_path):
                reply = QMessageBox.question(
                    self,
                    "确认覆盖",
                    f"文件已存在，是否覆盖？\n{target_path}",
                    QMessageBox.Yes | QMessageBox.No
                )
                if reply == QMessageBox.No:
                    return
            
            self.progress_bar.setVisible(True)
            self.progress_bar.setMaximum(0)
            self.progress_bar.setValue(0)
            self.status_label.setText("正在压缩...")
            
            self.start_btn.setEnabled(False)
            self.cancel_btn.setEnabled(True)
            
            self.worker = ArchiveWorker('create', target_path, self.file_paths)
            self.worker.progress.connect(self.on_progress)
            self.worker.finished.connect(self.on_finished)
            self.worker.error.connect(self.on_error)
            self.worker.start()
        
        else:
            zip_path = self.zip_input.text().strip()
            if not zip_path or not os.path.exists(zip_path):
                QMessageBox.warning(self, "错误", "请选择有效的ZIP文件")
                return
            
            extract_to = self.extract_input.text().strip()
            if not extract_to:
                QMessageBox.warning(self, "错误", "请选择解压目录")
                return
            
            self.progress_bar.setVisible(True)
            self.progress_bar.setMaximum(0)
            self.progress_bar.setValue(0)
            self.status_label.setText("正在解压...")
            
            self.start_btn.setEnabled(False)
            self.cancel_btn.setEnabled(True)
            
            self.worker = ArchiveWorker('extract', zip_path, extract_to=extract_to)
            self.worker.progress.connect(self.on_progress)
            self.worker.finished.connect(self.on_finished)
            self.worker.error.connect(self.on_error)
            self.worker.start()
    
    def cancel_operation(self):
        """取消操作"""
        if self.worker:
            self.worker.cancel()
            self.worker.wait()
        
        self.progress_bar.setVisible(False)
        self.status_label.setText("操作已取消")
        self.start_btn.setEnabled(True)
        self.cancel_btn.setEnabled(False)
    
    def on_progress(self, current, total, filename):
        """进度更新"""
        if total > 0:
            self.progress_bar.setMaximum(total)
            self.progress_bar.setValue(current)
            self.status_label.setText(f"处理中: {filename} ({current}/{total})")
    
    def on_finished(self, message):
        """操作完成"""
        self.progress_bar.setVisible(False)
        self.status_label.setText(message)
        QMessageBox.information(self, "完成", message)
        self.start_btn.setEnabled(True)
        self.cancel_btn.setEnabled(False)
        
        # 刷新文件面板
        if self.parent_window:
            self.parent_window.refresh_panels()
    
    def on_error(self, error_msg):
        """操作错误"""
        QMessageBox.critical(self, "错误", f"操作失败: {error_msg}")
        self.progress_bar.setVisible(False)
        self.status_label.setText("操作失败")
        self.start_btn.setEnabled(True)
        self.cancel_btn.setEnabled(False)
