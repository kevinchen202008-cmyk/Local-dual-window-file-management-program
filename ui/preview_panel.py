"""
快速预览面板 - 支持文本、图片、Hex视图
"""

import os
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTextEdit, 
    QPushButton, QScrollArea
)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QPixmap, QImage, QFont
from PIL import Image


class PreviewPanel(QWidget):
    """快速预览面板"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_file = None
        self.max_text_size = 1024 * 1024  # 1MB
        self.max_image_size = 2048  # 最大预览图片尺寸
        
        self.init_ui()
    
    def init_ui(self):
        """初始化UI"""
        layout = QVBoxLayout()
        layout.setContentsMargins(5, 5, 5, 5)
        
        # 标题栏
        header_layout = QHBoxLayout()
        self.title_label = QLabel("快速预览")
        self.title_label.setStyleSheet("font-weight: bold; font-size: 11px;")
        header_layout.addWidget(self.title_label)
        
        header_layout.addStretch()
        
        close_btn = QPushButton("×")
        close_btn.setFixedSize(20, 20)
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #E0E0E0;
            }
        """)
        close_btn.clicked.connect(self.hide)
        header_layout.addWidget(close_btn)
        
        layout.addLayout(header_layout)
        
        # 预览内容区域
        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout()
        self.content_widget.setLayout(self.content_layout)
        
        scroll = QScrollArea()
        scroll.setWidget(self.content_widget)
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("border: 1px solid #D0D0D0;")
        
        layout.addWidget(scroll)
        
        # 信息栏
        self.info_label = QLabel("")
        self.info_label.setStyleSheet("color: #666; font-size: 9px; padding: 3px;")
        layout.addWidget(self.info_label)
        
        self.setLayout(layout)
        self.setMinimumWidth(300)
        self.setMaximumWidth(500)
    
    def preview_file(self, file_path):
        """预览文件"""
        if not os.path.exists(file_path):
            self.show_message("文件不存在")
            return
        
        if os.path.isdir(file_path):
            self.show_message("无法预览文件夹")
            return
        
        self.current_file = file_path
        file_name = os.path.basename(file_path)
        self.title_label.setText(f"预览: {file_name}")
        
        # 清空现有内容
        self.clear_content()
        
        # 获取文件扩展名
        ext = os.path.splitext(file_path)[1].lower()
        
        # 根据文件类型选择预览方式
        if ext in ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.ico', '.webp']:
            self.preview_image(file_path)
        elif ext in ['.txt', '.md', '.py', '.js', '.html', '.css', '.json', '.xml', '.log']:
            self.preview_text(file_path)
        elif ext in ['.hex', '.bin']:
            self.preview_hex(file_path)
        else:
            # 尝试作为文本预览
            try:
                self.preview_text(file_path)
            except:
                self.show_message(f"不支持预览此文件类型: {ext}")
    
    def preview_text(self, file_path):
        """预览文本文件"""
        try:
            file_size = os.path.getsize(file_path)
            
            if file_size > self.max_text_size:
                self.show_message(f"文件过大 ({self.format_size(file_size)})，仅显示前1MB")
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read(self.max_text_size)
            else:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
            
            text_edit = QTextEdit()
            text_edit.setPlainText(content)
            text_edit.setReadOnly(True)
            text_edit.setFont(QFont("Consolas", 9))
            text_edit.setStyleSheet("background-color: #FFFFFF; border: none;")
            
            self.content_layout.addWidget(text_edit)
            self.info_label.setText(f"文本文件 | {self.format_size(file_size)} | {len(content)} 字符")
            
        except Exception as e:
            self.show_message(f"预览失败: {str(e)}")
    
    def preview_image(self, file_path):
        """预览图片文件"""
        try:
            # 使用PIL加载图片
            img = Image.open(file_path)
            
            # 调整大小以适应预览
            img.thumbnail((self.max_image_size, self.max_image_size), Image.Resampling.LANCZOS)
            
            # 转换为QPixmap
            if img.mode == 'RGBA':
                img = img.convert('RGBA')
                qimage = QImage(img.tobytes(), img.width, img.height, QImage.Format_RGBA8888)
            elif img.mode == 'RGB':
                img = img.convert('RGB')
                qimage = QImage(img.tobytes(), img.width, img.height, QImage.Format_RGB888)
            else:
                img = img.convert('RGB')
                qimage = QImage(img.tobytes(), img.width, img.height, QImage.Format_RGB888)
            
            pixmap = QPixmap.fromImage(qimage)
            
            # 显示图片
            image_label = QLabel()
            image_label.setPixmap(pixmap)
            image_label.setAlignment(Qt.AlignCenter)
            image_label.setStyleSheet("background-color: #F5F5F5;")
            
            self.content_layout.addWidget(image_label)
            
            file_size = os.path.getsize(file_path)
            self.info_label.setText(f"图片 | {self.format_size(file_size)} | {img.width}x{img.height} 像素")
            
        except Exception as e:
            self.show_message(f"图片预览失败: {str(e)}")
    
    def preview_hex(self, file_path):
        """预览Hex文件"""
        try:
            file_size = os.path.getsize(file_path)
            max_bytes = 1024 * 10  # 最多显示10KB
            
            with open(file_path, 'rb') as f:
                data = f.read(max_bytes)
            
            # 转换为Hex显示
            hex_lines = []
            for i in range(0, len(data), 16):
                chunk = data[i:i+16]
                hex_str = ' '.join(f'{b:02X}' for b in chunk)
                ascii_str = ''.join(chr(b) if 32 <= b < 127 else '.' for b in chunk)
                hex_lines.append(f"{i:08X}  {hex_str:<48}  {ascii_str}")
            
            text_edit = QTextEdit()
            text_edit.setPlainText('\n'.join(hex_lines))
            text_edit.setReadOnly(True)
            text_edit.setFont(QFont("Consolas", 9))
            text_edit.setStyleSheet("background-color: #1E1E1E; color: #D4D4D4; border: none;")
            
            self.content_layout.addWidget(text_edit)
            
            if file_size > max_bytes:
                self.info_label.setText(f"Hex文件 | {self.format_size(file_size)} | 仅显示前10KB")
            else:
                self.info_label.setText(f"Hex文件 | {self.format_size(file_size)}")
            
        except Exception as e:
            self.show_message(f"Hex预览失败: {str(e)}")
    
    def clear_content(self):
        """清空预览内容"""
        while self.content_layout.count():
            child = self.content_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
    
    def show_message(self, message):
        """显示消息"""
        self.clear_content()
        label = QLabel(message)
        label.setAlignment(Qt.AlignCenter)
        label.setStyleSheet("color: #666; padding: 20px;")
        self.content_layout.addWidget(label)
        self.info_label.setText("")
    
    @staticmethod
    def format_size(size):
        """格式化文件大小"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024:
                return f"{size:.2f} {unit}"
            size /= 1024
        return f"{size:.2f} TB"
