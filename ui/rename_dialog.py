"""
批量重命名对话框
"""

import os
import re
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QPushButton, QTableWidget, QTableWidgetItem, QMessageBox,
    QComboBox, QSpinBox, QCheckBox, QGroupBox, QTextEdit
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont


class RenameDialog(QDialog):
    """批量重命名对话框"""
    
    def __init__(self, parent=None, file_list=None):
        super().__init__(parent)
        self.parent_window = parent
        self.file_list = file_list or []  # [(name, path), ...]
        self.preview_data = []
        
        self.setWindowTitle("批量重命名")
        self.setMinimumWidth(700)
        self.setMinimumHeight(500)
        
        self.init_ui()
        self.update_preview()
    
    def init_ui(self):
        """初始化UI"""
        layout = QVBoxLayout()
        
        # 说明
        info_label = QLabel("选择重命名模式并设置参数，预览结果后确认重命名")
        info_label.setStyleSheet("color: #666; padding: 5px;")
        layout.addWidget(info_label)
        
        # 重命名模式选择
        mode_group = QGroupBox("重命名模式")
        mode_layout = QVBoxLayout()
        
        self.mode_combo = QComboBox()
        self.mode_combo.addItems([
            "序号模式 - 添加序号前缀/后缀",
            "替换模式 - 查找并替换文本",
            "插入模式 - 在指定位置插入文本",
            "大小写模式 - 转换大小写",
            "日期模式 - 添加日期前缀/后缀"
        ])
        self.mode_combo.currentIndexChanged.connect(self.on_mode_changed)
        mode_layout.addWidget(self.mode_combo)
        
        # 参数设置区域
        self.params_widget = QWidget()
        self.params_layout = QVBoxLayout()
        self.params_widget.setLayout(self.params_layout)
        mode_layout.addWidget(self.params_widget)
        
        mode_group.setLayout(mode_layout)
        layout.addWidget(mode_group)
        
        # 创建参数控件
        self.create_mode_params()
        
        # 预览表格
        preview_label = QLabel("预览结果:")
        preview_label.setStyleSheet("font-weight: bold; margin-top: 10px;")
        layout.addWidget(preview_label)
        
        self.preview_table = QTableWidget()
        self.preview_table.setColumnCount(3)
        self.preview_table.setHorizontalHeaderLabels(["原文件名", "新文件名", "状态"])
        self.preview_table.horizontalHeader().setStretchLastSection(False)
        self.preview_table.horizontalHeader().setSectionResizeMode(0, QTableWidget.Stretch)
        self.preview_table.horizontalHeader().setSectionResizeMode(1, QTableWidget.Stretch)
        self.preview_table.horizontalHeader().setSectionResizeMode(2, QTableWidget.ResizeToContents)
        self.preview_table.setEditTriggers(QTableWidget.NoEditTriggers)
        layout.addWidget(self.preview_table)
        
        # 按钮
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        preview_btn = QPushButton("更新预览")
        preview_btn.clicked.connect(self.update_preview)
        button_layout.addWidget(preview_btn)
        
        apply_btn = QPushButton("应用重命名")
        apply_btn.setStyleSheet("background-color: #0078d4; color: white; padding: 6px 20px;")
        apply_btn.clicked.connect(self.apply_rename)
        button_layout.addWidget(apply_btn)
        
        cancel_btn = QPushButton("取消")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
    
    def create_mode_params(self):
        """创建不同模式的参数控件"""
        # 清空现有控件
        while self.params_layout.count():
            child = self.params_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        
        mode = self.mode_combo.currentIndex()
        
        if mode == 0:  # 序号模式
            layout = QVBoxLayout()
            
            # 序号位置
            pos_layout = QHBoxLayout()
            pos_layout.addWidget(QLabel("位置:"))
            self.pos_combo = QComboBox()
            self.pos_combo.addItems(["前缀", "后缀"])
            pos_layout.addWidget(self.pos_combo)
            layout.addLayout(pos_layout)
            
            # 起始序号
            start_layout = QHBoxLayout()
            start_layout.addWidget(QLabel("起始序号:"))
            self.start_spin = QSpinBox()
            self.start_spin.setMinimum(1)
            self.start_spin.setMaximum(99999)
            self.start_spin.setValue(1)
            start_layout.addWidget(self.start_spin)
            layout.addLayout(start_layout)
            
            # 序号格式
            format_layout = QHBoxLayout()
            format_layout.addWidget(QLabel("格式:"))
            self.format_combo = QComboBox()
            self.format_combo.addItems(["1, 2, 3...", "01, 02, 03...", "001, 002, 003..."])
            format_layout.addWidget(self.format_combo)
            layout.addLayout(format_layout)
            
            # 分隔符
            sep_layout = QHBoxLayout()
            sep_layout.addWidget(QLabel("分隔符:"))
            self.sep_input = QLineEdit()
            self.sep_input.setText("_")
            self.sep_input.setMaximumWidth(100)
            sep_layout.addWidget(self.sep_input)
            layout.addLayout(sep_layout)
            
            self.params_widget.setLayout(layout)
            
        elif mode == 1:  # 替换模式
            layout = QVBoxLayout()
            
            find_layout = QHBoxLayout()
            find_layout.addWidget(QLabel("查找:"))
            self.find_input = QLineEdit()
            find_layout.addWidget(self.find_input)
            layout.addLayout(find_layout)
            
            replace_layout = QHBoxLayout()
            replace_layout.addWidget(QLabel("替换为:"))
            self.replace_input = QLineEdit()
            replace_layout.addWidget(self.replace_input)
            layout.addLayout(replace_layout)
            
            self.case_check = QCheckBox("区分大小写")
            layout.addWidget(self.case_check)
            
            self.params_widget.setLayout(layout)
            
        elif mode == 2:  # 插入模式
            layout = QVBoxLayout()
            
            pos_layout = QHBoxLayout()
            pos_layout.addWidget(QLabel("位置:"))
            self.insert_pos_combo = QComboBox()
            self.insert_pos_combo.addItems(["文件名开头", "文件名末尾", "扩展名前"])
            pos_layout.addWidget(self.insert_pos_combo)
            layout.addLayout(pos_layout)
            
            text_layout = QHBoxLayout()
            text_layout.addWidget(QLabel("插入文本:"))
            self.insert_text = QLineEdit()
            text_layout.addWidget(self.insert_text)
            layout.addLayout(text_layout)
            
            self.params_widget.setLayout(layout)
            
        elif mode == 3:  # 大小写模式
            layout = QVBoxLayout()
            
            case_layout = QHBoxLayout()
            case_layout.addWidget(QLabel("转换方式:"))
            self.case_combo = QComboBox()
            self.case_combo.addItems(["全部大写", "全部小写", "首字母大写", "单词首字母大写"])
            case_layout.addWidget(self.case_combo)
            layout.addLayout(case_layout)
            
            self.params_widget.setLayout(layout)
            
        elif mode == 4:  # 日期模式
            layout = QVBoxLayout()
            
            pos_layout = QHBoxLayout()
            pos_layout.addWidget(QLabel("位置:"))
            self.date_pos_combo = QComboBox()
            self.date_pos_combo.addItems(["前缀", "后缀"])
            pos_layout.addWidget(self.date_pos_combo)
            layout.addLayout(pos_layout)
            
            format_layout = QHBoxLayout()
            format_layout.addWidget(QLabel("日期格式:"))
            self.date_format_combo = QComboBox()
            self.date_format_combo.addItems([
                "YYYY-MM-DD",
                "YYYYMMDD",
                "YY-MM-DD",
                "MM-DD"
            ])
            format_layout.addWidget(self.date_format_combo)
            layout.addLayout(format_layout)
            
            sep_layout = QHBoxLayout()
            sep_layout.addWidget(QLabel("分隔符:"))
            self.date_sep_input = QLineEdit()
            self.date_sep_input.setText("_")
            self.date_sep_input.setMaximumWidth(100)
            sep_layout.addWidget(self.date_sep_input)
            layout.addLayout(sep_layout)
            
            self.params_widget.setLayout(layout)
    
    def on_mode_changed(self):
        """模式改变时更新参数控件"""
        self.create_mode_params()
        self.update_preview()
    
    def generate_new_name(self, old_name, index):
        """根据模式生成新文件名"""
        mode = self.mode_combo.currentIndex()
        
        # 分离文件名和扩展名
        if '.' in old_name and not old_name.startswith('.'):
            name_part, ext_part = old_name.rsplit('.', 1)
            ext = '.' + ext_part
        else:
            name_part = old_name
            ext = ''
        
        if mode == 0:  # 序号模式
            start = self.start_spin.value()
            format_idx = self.format_combo.currentIndex()
            sep = self.sep_input.text()
            
            if format_idx == 0:
                num_str = str(start + index)
            elif format_idx == 1:
                num_str = f"{start + index:02d}"
            else:
                num_str = f"{start + index:03d}"
            
            if self.pos_combo.currentText() == "前缀":
                new_name = f"{num_str}{sep}{name_part}{ext}"
            else:
                new_name = f"{name_part}{sep}{num_str}{ext}"
        
        elif mode == 1:  # 替换模式
            find_text = self.find_input.text()
            replace_text = self.replace_input.text()
            case_sensitive = self.case_check.isChecked()
            
            if case_sensitive:
                new_name = old_name.replace(find_text, replace_text)
            else:
                # 不区分大小写替换
                import re
                pattern = re.compile(re.escape(find_text), re.IGNORECASE)
                new_name = pattern.sub(replace_text, old_name)
        
        elif mode == 2:  # 插入模式
            insert_text = self.insert_text.text()
            pos = self.insert_pos_combo.currentText()
            
            if pos == "文件名开头":
                new_name = f"{insert_text}{name_part}{ext}"
            elif pos == "文件名末尾":
                new_name = f"{name_part}{insert_text}{ext}"
            else:  # 扩展名前
                new_name = f"{name_part}{insert_text}{ext}"
        
        elif mode == 3:  # 大小写模式
            case_type = self.case_combo.currentText()
            if case_type == "全部大写":
                new_name = old_name.upper()
            elif case_type == "全部小写":
                new_name = old_name.lower()
            elif case_type == "首字母大写":
                new_name = old_name.capitalize()
            else:  # 单词首字母大写
                new_name = old_name.title()
        
        elif mode == 4:  # 日期模式
            from datetime import datetime
            date_format = self.date_format_combo.currentText()
            sep = self.date_sep_input.text()
            
            # 转换格式
            format_map = {
                "YYYY-MM-DD": "%Y-%m-%d",
                "YYYYMMDD": "%Y%m%d",
                "YY-MM-DD": "%y-%m-%d",
                "MM-DD": "%m-%d"
            }
            date_str = datetime.now().strftime(format_map[date_format])
            
            if self.date_pos_combo.currentText() == "前缀":
                new_name = f"{date_str}{sep}{name_part}{ext}"
            else:
                new_name = f"{name_part}{sep}{date_str}{ext}"
        
        return new_name
    
    def update_preview(self):
        """更新预览"""
        self.preview_data = []
        self.preview_table.setRowCount(0)
        
        for idx, (name, path) in enumerate(self.file_list):
            try:
                new_name = self.generate_new_name(name, idx)
                
                # 检查新文件名是否有效
                new_path = os.path.join(os.path.dirname(path), new_name)
                status = "✓ 正常"
                
                # 检查是否与现有文件冲突
                if os.path.exists(new_path) and new_path != path:
                    status = "⚠ 文件名冲突"
                elif not new_name or new_name.strip() == "":
                    status = "✗ 无效文件名"
                elif new_name == name:
                    status = "— 无变化"
                
                self.preview_data.append({
                    'old_name': name,
                    'new_name': new_name,
                    'old_path': path,
                    'new_path': new_path,
                    'status': status
                })
                
                # 添加到表格
                row = self.preview_table.rowCount()
                self.preview_table.insertRow(row)
                
                self.preview_table.setItem(row, 0, QTableWidgetItem(name))
                self.preview_table.setItem(row, 1, QTableWidgetItem(new_name))
                
                status_item = QTableWidgetItem(status)
                if "冲突" in status:
                    status_item.setForeground(Qt.red)
                elif "无效" in status:
                    status_item.setForeground(Qt.red)
                elif "无变化" in status:
                    status_item.setForeground(Qt.gray)
                self.preview_table.setItem(row, 2, status_item)
                
            except Exception as e:
                self.preview_data.append({
                    'old_name': name,
                    'new_name': name,
                    'old_path': path,
                    'new_path': path,
                    'status': f"✗ 错误: {str(e)}"
                })
    
    def apply_rename(self):
        """应用重命名"""
        # 检查是否有错误
        errors = [d for d in self.preview_data if "✗" in d['status'] or "冲突" in d['status']]
        if errors:
            reply = QMessageBox.question(
                self,
                "确认",
                f"有 {len(errors)} 个文件存在问题，是否继续？",
                QMessageBox.Yes | QMessageBox.No
            )
            if reply == QMessageBox.No:
                return
        
        # 执行重命名
        success_count = 0
        failed_count = 0
        
        for data in self.preview_data:
            if data['status'] in ["— 无变化", "✗ 错误"]:
                continue
            
            try:
                if os.path.exists(data['old_path']):
                    os.rename(data['old_path'], data['new_path'])
                    success_count += 1
                else:
                    failed_count += 1
            except Exception as e:
                failed_count += 1
                QMessageBox.warning(self, "错误", f"重命名失败: {data['old_name']}\n{str(e)}")
        
        QMessageBox.information(
            self,
            "完成",
            f"重命名完成！\n成功: {success_count}\n失败: {failed_count}"
        )
        
        self.accept()
