"""
文件对比选择对话框 - 让用户选择对比模式和文件
"""

from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QRadioButton,
    QButtonGroup, QWidget, QTableWidget, QTableWidgetItem, QHeaderView,
    QMessageBox, QListWidget, QListWidgetItem, QScrollArea
)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QFont, QColor
from .file_compare import find_same_named_files, FileComparer


class CompareSelectDialog(QDialog):
    """文件对比模式选择对话框"""
    
    def __init__(self, main_window):
        super().__init__(main_window)
        self.main_window = main_window
        
        # 获取选中的文件
        self.left_selected = main_window.left_panel.get_selected_files()
        self.right_selected = main_window.right_panel.get_selected_files()
        self.left_dir = main_window.left_panel.current_path
        self.right_dir = main_window.right_panel.current_path
        
        # 查找同名文件
        self.same_named_files = find_same_named_files(self.left_dir, self.right_dir)
        
        self.setWindowTitle("文件对比 - 选择模式")
        self.setGeometry(200, 200, 800, 500)
        self.setModal(True)
        
        self.setup_ui()
        
    def setup_ui(self):
        """创建UI"""
        main_layout = QVBoxLayout()
        
        # 标题
        title_label = QLabel("选择对比方式")
        title_font = QFont()
        title_font.setPointSize(11)
        title_font.setBold(True)
        title_label.setFont(title_font)
        main_layout.addWidget(title_label)
        main_layout.addSpacing(10)
        
        # 方式1: 指定文件对比
        if len(self.left_selected) == 1 and len(self.right_selected) == 1:
            mode1_widget = self._create_mode1_widget()
            if mode1_widget:
                main_layout.addWidget(mode1_widget)
                main_layout.addSpacing(10)
        
        # 方式2: 从同名文件列表中选择
        if len(self.same_named_files) > 0:
            mode2_widget = self._create_mode2_widget()
            main_layout.addWidget(mode2_widget)
        
        # 按钮
        main_layout.addStretch()
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        close_btn = QPushButton("关闭")
        close_btn.clicked.connect(self.close)
        button_layout.addWidget(close_btn)
        
        main_layout.addLayout(button_layout)
        
        self.setLayout(main_layout)
    
    def _create_mode1_widget(self):
        """创建指定文件对比模式"""
        if len(self.left_selected) != 1 or len(self.right_selected) != 1:
            return None
        
        widget = QWidget()
        layout = QVBoxLayout()
        
        # 标题
        mode_label = QLabel("模式1: 对比指定的两个文件")
        mode_font = QFont()
        mode_font.setBold(True)
        mode_label.setFont(mode_font)
        layout.addWidget(mode_label)
        
        # 文件信息
        file_layout = QHBoxLayout()
        
        # 左文件
        left_file_name = self.left_selected[0].split('\\')[-1]
        left_label = QLabel(f"左: {left_file_name}")
        file_layout.addWidget(left_label)
        
        file_layout.addStretch()
        
        vs_label = QLabel("vs")
        file_layout.addWidget(vs_label)
        
        file_layout.addStretch()
        
        # 右文件
        right_file_name = self.right_selected[0].split('\\')[-1]
        right_label = QLabel(f"右: {right_file_name}")
        file_layout.addWidget(right_label)
        
        layout.addLayout(file_layout)
        
        # 按钮
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        compare_btn = QPushButton("对比这两个文件")
        compare_btn.clicked.connect(self._compare_selected_files)
        btn_layout.addWidget(compare_btn)
        layout.addLayout(btn_layout)
        
        widget.setLayout(layout)
        return widget
    
    def _create_mode2_widget(self):
        """创建同名文件列表对比模式"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # 标题
        mode_label = QLabel(f"模式2: 从 {len(self.same_named_files)} 个同名文件中选择")
        mode_font = QFont()
        mode_font.setBold(True)
        mode_label.setFont(mode_font)
        layout.addWidget(mode_label)
        
        # 文件列表
        table = QTableWidget()
        table.setColumnCount(4)
        table.setHorizontalHeaderLabels(["文件名", "左文件大小", "右文件大小", "状态"])
        table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        table.horizontalHeader().setSectionResizeMode(3, QHeaderView.Stretch)
        table.setRowCount(len(self.same_named_files))
        table.setMaximumHeight(250)
        
        for row, file_info in enumerate(self.same_named_files):
            name = file_info['name']
            path1 = file_info['path1']
            path2 = file_info['path2']
            
            # 获取文件信息
            import os
            size1 = os.path.getsize(path1)
            size2 = os.path.getsize(path2)
            
            # 格式化大小
            size1_str = self._format_size(size1)
            size2_str = self._format_size(size2)
            
            # 判断是否相同
            result = FileComparer.compare_files(path1, path2)
            status = "✓ 相同" if result['are_identical'] else "✗ 不同"
            status_color = QColor(0, 128, 0) if result['are_identical'] else QColor(255, 0, 0)
            
            # 添加行
            name_item = QTableWidgetItem(name)
            size1_item = QTableWidgetItem(size1_str)
            size2_item = QTableWidgetItem(size2_str)
            status_item = QTableWidgetItem(status)
            status_item.setForeground(status_color)
            
            table.setItem(row, 0, name_item)
            table.setItem(row, 1, size1_item)
            table.setItem(row, 2, size2_item)
            table.setItem(row, 3, status_item)
            
            # 行高
            table.resizeRowToContents(row)
        
        # 保存表格，用于查询选中行
        self.same_files_table = table
        table.itemSelectionChanged.connect(self._on_file_selected)
        
        layout.addWidget(table)
        
        # 按钮
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        view_btn = QPushButton("查看详细对比")
        view_btn.clicked.connect(self._compare_selected_from_list)
        self.view_btn = view_btn
        view_btn.setEnabled(False)
        btn_layout.addWidget(view_btn)
        
        batch_btn = QPushButton("查看全部对比")
        batch_btn.clicked.connect(self._show_batch_compare)
        btn_layout.addWidget(batch_btn)
        
        layout.addLayout(btn_layout)
        
        widget.setLayout(layout)
        return widget
    
    def _on_file_selected(self):
        """表格选中行变化"""
        if self.same_files_table.selectedIndexes():
            self.view_btn.setEnabled(True)
        else:
            self.view_btn.setEnabled(False)
    
    def _compare_selected_files(self):
        """对比指定的两个文件"""
        from .compare_dialog import CompareDialog
        
        file1 = self.left_selected[0]
        file2 = self.right_selected[0]
        
        compare_dialog = CompareDialog(file1, file2, self.main_window)
        compare_dialog.exec_()
    
    def _compare_selected_from_list(self):
        """对比列表中选中的文件"""
        from .compare_dialog import CompareDialog
        
        selected_rows = self.same_files_table.selectedIndexes()
        if not selected_rows:
            QMessageBox.warning(self, "提示", "请先选择要对比的文件")
            return
        
        row = selected_rows[0].row()
        file_info = self.same_named_files[row]
        
        compare_dialog = CompareDialog(
            file_info['path1'], 
            file_info['path2'], 
            self.main_window
        )
        compare_dialog.exec_()
    
    def _show_batch_compare(self):
        """显示所有同名文件的对比结果"""
        from .batch_compare_dialog import BatchCompareDialog
        
        batch_dialog = BatchCompareDialog(
            self.same_named_files,
            self.main_window
        )
        batch_dialog.exec_()
    
    @staticmethod
    def _format_size(size):
        """格式化文件大小"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024:
                return f"{size:.1f} {unit}"
            size /= 1024
        return f"{size:.1f} TB"
