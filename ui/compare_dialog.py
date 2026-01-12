"""
文件对比对话框 - 显示两个文件的对比结果
"""

from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QTextEdit, QPushButton,
    QTabWidget, QWidget, QTableWidget, QTableWidgetItem, QHeaderView,
    QScrollArea, QMessageBox
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QColor
from .file_compare import FileComparer


class CompareDialog(QDialog):
    """文件对比对话框"""
    
    def __init__(self, file1_path, file2_path, parent=None):
        super().__init__(parent)
        self.file1_path = file1_path
        self.file2_path = file2_path
        
        self.setWindowTitle("文件对比")
        self.setGeometry(100, 100, 1200, 700)
        
        # 进行对比
        self.compare_result = FileComparer.compare_files(file1_path, file2_path)
        
        # 创建UI
        self.setup_ui()
        
    def setup_ui(self):
        """创建UI"""
        layout = QVBoxLayout()
        
        # 标题
        title_layout = QHBoxLayout()
        title_label = QLabel("文件对比")
        title_font = QFont()
        title_font.setPointSize(12)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_layout.addWidget(title_label)
        title_layout.addStretch()
        layout.addLayout(title_layout)
        
        # 文件信息行
        info_layout = QHBoxLayout()
        
        # 左文件信息
        left_info = QLabel()
        left_info.setText(self._format_file_info(self.compare_result['file1'], "左"))
        info_layout.addWidget(left_info)
        
        # 中间分隔符
        sep_label = QLabel("  vs  ")
        sep_font = QFont()
        sep_font.setBold(True)
        sep_label.setFont(sep_font)
        info_layout.addWidget(sep_label)
        
        # 右文件信息
        right_info = QLabel()
        right_info.setText(self._format_file_info(self.compare_result['file2'], "右"))
        info_layout.addWidget(right_info)
        
        layout.addLayout(info_layout)
        
        # 对比结果
        result_label = QLabel(self.compare_result['comparison'])
        result_label.setStyleSheet("""
            background-color: #F5F5F5;
            border: 1px solid #D0D0D0;
            border-radius: 3px;
            padding: 8px;
            font-weight: bold;
        """)
        layout.addWidget(result_label)
        
        # 差异详情表格
        if self.compare_result['differences']:
            diff_table = self._create_differences_table()
            layout.addWidget(QLabel("差异详情:"))
            layout.addWidget(diff_table)
        
        # 标签页：显示文件内容对比
        self.tab_widget = QTabWidget()
        
        # 添加概览标签
        overview_widget = self._create_overview_tab()
        self.tab_widget.addTab(overview_widget, "概览")
        
        # 如果是文本文件，添加内容对比
        if self.compare_result['file1'].get('is_text') and self.compare_result['file2'].get('is_text'):
            content_widget = self._create_content_tab()
            self.tab_widget.addTab(content_widget, "内容对比")
        
        layout.addWidget(self.tab_widget)
        
        # 按钮行
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        close_btn = QPushButton("关闭")
        close_btn.clicked.connect(self.close)
        button_layout.addWidget(close_btn)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
    
    def _format_file_info(self, file_info, side):
        """格式化文件信息"""
        if 'error' in file_info:
            return f"{side}文件: {file_info['name']}\n错误: {file_info['error']}"
        
        info_text = f"{side}文件: {file_info['name']}\n"
        info_text += f"大小: {file_info['size_formatted']}\n"
        info_text += f"修改时间: {file_info['modified_str']}"
        
        return info_text
    
    def _create_differences_table(self):
        """创建差异表格"""
        table = QTableWidget()
        table.setColumnCount(2)
        table.setHorizontalHeaderLabels(["差异类型", "描述"])
        table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        
        for diff in self.compare_result['differences']:
            row = table.rowCount()
            table.insertRow(row)
            
            # 类型
            type_item = QTableWidgetItem(diff['type'])
            type_item.setBackground(QColor("#FFE4E1") if diff['type'] == 'content' else QColor("#FFFACD"))
            table.setItem(row, 0, type_item)
            
            # 描述
            desc_item = QTableWidgetItem(diff['description'])
            table.setItem(row, 1, desc_item)
        
        table.setMaximumHeight(150)
        return table
    
    def _create_overview_tab(self):
        """创建概览标签"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # 创建详细信息表格
        info_table = QTableWidget()
        info_table.setColumnCount(3)
        info_table.setHorizontalHeaderLabels(["项目", "左文件", "右文件"])
        info_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        
        file1 = self.compare_result['file1']
        file2 = self.compare_result['file2']
        
        # 文件名
        row = 0
        info_table.insertRow(row)
        info_table.setItem(row, 0, QTableWidgetItem("文件名"))
        info_table.setItem(row, 1, QTableWidgetItem(file1.get('name', 'N/A')))
        info_table.setItem(row, 2, QTableWidgetItem(file2.get('name', 'N/A')))
        
        # 文件大小
        row += 1
        info_table.insertRow(row)
        info_table.setItem(row, 0, QTableWidgetItem("文件大小"))
        size1_text = file1.get('size_formatted', 'N/A')
        size2_text = file2.get('size_formatted', 'N/A')
        item1 = QTableWidgetItem(size1_text)
        item2 = QTableWidgetItem(size2_text)
        if file1.get('size') != file2.get('size'):
            item1.setBackground(QColor("#FFFACD"))
            item2.setBackground(QColor("#FFFACD"))
        info_table.setItem(row, 1, item1)
        info_table.setItem(row, 2, item2)
        
        # 修改时间
        row += 1
        info_table.insertRow(row)
        info_table.setItem(row, 0, QTableWidgetItem("修改时间"))
        mtime1 = file1.get('modified_str', 'N/A')
        mtime2 = file2.get('modified_str', 'N/A')
        item1 = QTableWidgetItem(mtime1)
        item2 = QTableWidgetItem(mtime2)
        if file1.get('modified') != file2.get('modified'):
            item1.setBackground(QColor("#FFFACD"))
            item2.setBackground(QColor("#FFFACD"))
        info_table.setItem(row, 1, item1)
        info_table.setItem(row, 2, item2)
        
        # 文件类型
        row += 1
        info_table.insertRow(row)
        info_table.setItem(row, 0, QTableWidgetItem("文件类型"))
        info_table.setItem(row, 1, QTableWidgetItem("文本" if file1.get('is_text') else "二进制"))
        info_table.setItem(row, 2, QTableWidgetItem("文本" if file2.get('is_text') else "二进制"))
        
        # 内容状态
        row += 1
        info_table.insertRow(row)
        info_table.setItem(row, 0, QTableWidgetItem("内容状态"))
        status = "✅ 相同" if self.compare_result['are_identical'] else "❌ 不同"
        status_item1 = QTableWidgetItem(status)
        status_item2 = QTableWidgetItem(status)
        if not self.compare_result['are_identical']:
            status_item1.setBackground(QColor("#FFE4E1"))
            status_item2.setBackground(QColor("#FFE4E1"))
        info_table.setItem(row, 1, status_item1)
        info_table.setItem(row, 2, status_item2)
        
        layout.addWidget(info_table)
        layout.addStretch()
        widget.setLayout(layout)
        
        return widget
    
    def _create_content_tab(self):
        """创建内容对比标签"""
        widget = QWidget()
        layout = QHBoxLayout()
        
        # 获取文本差异
        diff = FileComparer.get_text_file_diff(self.file1_path, self.file2_path)
        
        # 左侧：第一个文件内容
        left_layout = QVBoxLayout()
        left_layout.addWidget(QLabel(f"【左文件】{diff['line_count1']} 行"))
        left_content = QTextEdit()
        left_content.setReadOnly(True)
        left_content.setPlainText(''.join(diff['file1_lines']))
        left_content.setStyleSheet("""
            QTextEdit {
                background-color: #FFFFFF;
                border: 1px solid #D0D0D0;
                font-family: 'Courier New', monospace;
                font-size: 10pt;
            }
        """)
        left_layout.addWidget(left_content)
        
        left_widget = QWidget()
        left_widget.setLayout(left_layout)
        
        # 右侧：第二个文件内容
        right_layout = QVBoxLayout()
        right_layout.addWidget(QLabel(f"【右文件】{diff['line_count2']} 行"))
        right_content = QTextEdit()
        right_content.setReadOnly(True)
        right_content.setPlainText(''.join(diff['file2_lines']))
        right_content.setStyleSheet("""
            QTextEdit {
                background-color: #FFFFFF;
                border: 1px solid #D0D0D0;
                font-family: 'Courier New', monospace;
                font-size: 10pt;
            }
        """)
        right_layout.addWidget(right_content)
        
        right_widget = QWidget()
        right_widget.setLayout(right_layout)
        
        # 添加到主布局
        layout.addWidget(left_widget)
        layout.addWidget(right_widget)
        
        # 差异统计信息
        if diff['total_changes'] > 0:
            info_text = f"差异统计:\n"
            info_text += f"• 新增行: {diff['added_lines']}\n"
            info_text += f"• 删除行: {diff['removed_lines']}\n"
            info_text += f"• 总变化: {diff['total_changes']}"
            
            info_label = QLabel(info_text)
            info_label.setStyleSheet("""
                background-color: #FFF8DC;
                border: 1px solid #DAA520;
                border-radius: 3px;
                padding: 8px;
            """)
            layout.addWidget(info_label)
        
        widget.setLayout(layout)
        return widget
