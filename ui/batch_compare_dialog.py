"""
批量文件对比对话框 - 显示所有同名文件的对比结果
"""

from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTableWidget,
    QTableWidgetItem, QHeaderView, QMessageBox, QTabWidget, QWidget,
    QTextEdit, QScrollArea
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QColor
from .file_compare import FileComparer


class BatchCompareDialog(QDialog):
    """批量文件对比对话框"""
    
    def __init__(self, same_named_files, main_window):
        super().__init__(main_window)
        self.main_window = main_window
        self.same_named_files = same_named_files
        
        self.setWindowTitle("批量文件对比结果")
        self.setGeometry(100, 100, 1000, 600)
        self.setModal(True)
        
        self.setup_ui()
    
    def setup_ui(self):
        """创建UI"""
        main_layout = QVBoxLayout()
        
        # 标题
        title_label = QLabel(f"批量对比结果 - 共 {len(self.same_named_files)} 个同名文件")
        title_font = QFont()
        title_font.setPointSize(11)
        title_font.setBold(True)
        title_label.setFont(title_font)
        main_layout.addWidget(title_label)
        
        # 统计信息
        stats = self._calculate_statistics()
        stats_label = QLabel(
            f"完全相同: {stats['identical']} | 不同: {stats['different']} | "
            f"仅大小不同: {stats['size_diff']} | 仅时间不同: {stats['time_diff']}"
        )
        main_layout.addWidget(stats_label)
        
        main_layout.addSpacing(10)
        
        # 对比结果表格
        table = self._create_comparison_table()
        main_layout.addWidget(table)
        
        # 按钮
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        # 导出按钮
        export_btn = QPushButton("导出对比报告")
        export_btn.clicked.connect(self._export_report)
        button_layout.addWidget(export_btn)
        
        close_btn = QPushButton("关闭")
        close_btn.clicked.connect(self.close)
        button_layout.addWidget(close_btn)
        
        main_layout.addLayout(button_layout)
        
        self.setLayout(main_layout)
    
    def _calculate_statistics(self):
        """计算统计信息"""
        stats = {
            'identical': 0,
            'different': 0,
            'size_diff': 0,
            'time_diff': 0
        }
        
        for file_info in self.same_named_files:
            result = FileComparer.compare_files(file_info['path1'], file_info['path2'])
            
            if result['are_identical']:
                stats['identical'] += 1
            else:
                stats['different'] += 1
                
                # 检查是什么不同
                has_size_diff = any(d['type'] == 'size' for d in result['differences'])
                has_time_diff = any(d['type'] == 'mtime' for d in result['differences'])
                has_content_diff = any(d['type'] == 'content' for d in result['differences'])
                
                if has_content_diff:
                    pass  # 内容不同，不算在其他类别中
                elif has_size_diff and has_time_diff:
                    pass  # 两者都不同
                elif has_size_diff:
                    stats['size_diff'] += 1
                elif has_time_diff:
                    stats['time_diff'] += 1
        
        return stats
    
    def _create_comparison_table(self):
        """创建对比结果表格"""
        table = QTableWidget()
        table.setColumnCount(6)
        table.setHorizontalHeaderLabels([
            "序号", "文件名", "对比结果", "大小", "修改时间", "差异详情"
        ])
        
        # 设置列宽
        header = table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.Stretch)
        
        table.setRowCount(len(self.same_named_files))
        
        for row, file_info in enumerate(self.same_named_files):
            result = FileComparer.compare_files(file_info['path1'], file_info['path2'])
            
            # 序号
            seq_item = QTableWidgetItem(str(row + 1))
            table.setItem(row, 0, seq_item)
            
            # 文件名
            name_item = QTableWidgetItem(file_info['name'])
            table.setItem(row, 1, name_item)
            
            # 对比结果
            if result['are_identical']:
                result_text = "✓ 完全相同"
                result_color = QColor(0, 128, 0)
            else:
                result_text = "✗ 不同"
                result_color = QColor(255, 0, 0)
            
            result_item = QTableWidgetItem(result_text)
            result_item.setForeground(result_color)
            table.setItem(row, 2, result_item)
            
            # 大小对比
            size1 = result['file1']['size']
            size2 = result['file2']['size']
            size_str = self._format_size(size1)
            if size1 != size2:
                size_str += f" → {self._format_size(size2)}"
                size_item = QTableWidgetItem(size_str)
                size_item.setBackground(QColor(255, 255, 0))  # 黄色背景表示不同
            else:
                size_item = QTableWidgetItem(size_str)
            table.setItem(row, 3, size_item)
            
            # 修改时间对比
            mtime1 = result['file1']['mtime']
            mtime2 = result['file2']['mtime']
            if mtime1 != mtime2:
                time_item = QTableWidgetItem("不同")
                time_item.setBackground(QColor(255, 255, 0))  # 黄色背景
            else:
                time_item = QTableWidgetItem("相同")
            table.setItem(row, 4, time_item)
            
            # 差异详情
            diff_parts = []
            for diff in result['differences']:
                if diff['type'] == 'content':
                    if 'added' in diff and 'removed' in diff:
                        diff_parts.append(f"内容: +{diff['added']}-{diff['removed']}")
                    else:
                        diff_parts.append("内容不同")
                elif diff['type'] == 'size':
                    diff_parts.append(f"大小: {diff['description'].split(':')[1].strip()}")
                elif diff['type'] == 'mtime':
                    diff_parts.append("时间不同")
            
            diff_text = "; ".join(diff_parts) if diff_parts else "无差异"
            diff_item = QTableWidgetItem(diff_text)
            table.setItem(row, 5, diff_item)
            
            # 行高
            table.resizeRowToContents(row)
        
        # 设置双击打开详细对比
        table.doubleClicked.connect(self._open_detailed_compare)
        
        return table
    
    def _open_detailed_compare(self, index):
        """打开详细对比"""
        from .compare_dialog import CompareDialog
        
        row = index.row()
        file_info = self.same_named_files[row]
        
        compare_dialog = CompareDialog(
            file_info['path1'],
            file_info['path2'],
            self.main_window
        )
        compare_dialog.exec_()
    
    def _export_report(self):
        """导出对比报告"""
        report = self._generate_report()
        
        # 保存到文件
        from PyQt5.QtWidgets import QFileDialog
        
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "保存对比报告",
            "",
            "文本文件 (*.txt);;HTML文件 (*.html)"
        )
        
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(report)
                QMessageBox.information(self, "成功", f"报告已保存到:\n{file_path}")
            except Exception as e:
                QMessageBox.critical(self, "错误", f"保存失败: {str(e)}")
    
    def _generate_report(self):
        """生成对比报告"""
        stats = self._calculate_statistics()
        
        report = f"""
{'='*60}
                   文件对比报告
{'='*60}

统计信息:
  - 同名文件总数: {len(self.same_named_files)}
  - 完全相同: {stats['identical']} 个
  - 存在差异: {stats['different']} 个
    • 仅大小不同: {stats['size_diff']} 个
    • 仅时间不同: {stats['time_diff']} 个
    • 内容不同: {stats['different'] - stats['size_diff'] - stats['time_diff']} 个

{'='*60}
                   详细对比结果
{'='*60}

"""
        
        for idx, file_info in enumerate(self.same_named_files, 1):
            result = FileComparer.compare_files(file_info['path1'], file_info['path2'])
            
            report += f"\n{idx}. 文件: {file_info['name']}\n"
            report += f"   左路径: {file_info['path1']}\n"
            report += f"   右路径: {file_info['path2']}\n"
            
            if result['are_identical']:
                report += f"   状态: ✓ 完全相同\n"
            else:
                report += f"   状态: ✗ 存在差异\n"
                report += f"   差异: \n"
                for diff in result['differences']:
                    report += f"      - {diff['description']}\n"
            
            report += f"\n"
        
        report += f"\n{'='*60}\n"
        report += f"报告生成时间: {self._get_current_time()}\n"
        report += f"{'='*60}\n"
        
        return report
    
    @staticmethod
    def _format_size(size):
        """格式化文件大小"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024:
                return f"{size:.1f} {unit}"
            size /= 1024
        return f"{size:.1f} TB"
    
    @staticmethod
    def _get_current_time():
        """获取当前时间"""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
