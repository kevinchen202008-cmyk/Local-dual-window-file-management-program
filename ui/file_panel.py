"""
文件浏览面板 - 单个面板的实现
"""

import os
import shutil
from pathlib import Path
from datetime import datetime
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QTableWidget, 
    QTableWidgetItem, QMessageBox, QFileDialog, QHeaderView, QMenu, QPushButton
)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QIcon, QFont


class FilePanel(QWidget):
    def __init__(self, panel_name="", initial_path=None):
        super().__init__()
        self.panel_name = panel_name
        self.current_path = initial_path or str(Path.home())
        
        # 验证初始路径
        if not os.path.isdir(self.current_path):
            self.current_path = str(Path.home())
        
        self.selected_files = []
        self.setFocusPolicy(Qt.StrongFocus)  # 允许获得焦点
        
        # 创建布局
        layout = QVBoxLayout()
        
        # 路径输入框
        path_layout = QHBoxLayout()
        self.path_input = QLineEdit()
        self.path_input.setText(self.current_path)
        self.path_input.returnPressed.connect(self.on_path_changed)
        path_layout.addWidget(self.path_input)
        
        browse_btn = QPushButton("浏览...")
        browse_btn.clicked.connect(self.browse_folder)
        path_layout.addWidget(browse_btn)
        
        layout.addLayout(path_layout)
        
        # 文件列表表格
        self.file_list = QTableWidget()
        self.file_list.setColumnCount(4)
        self.file_list.setHorizontalHeaderLabels(["名称", "类型", "大小", "修改时间"])
        self.file_list.horizontalHeader().setStretchLastSection(False)
        self.file_list.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.file_list.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.file_list.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.file_list.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        
        self.file_list.setSelectionBehavior(QTableWidget.SelectRows)
        self.file_list.setSelectionMode(QTableWidget.ExtendedSelection)
        self.file_list.itemDoubleClicked.connect(self.on_item_double_clicked)
        self.file_list.setContextMenuPolicy(Qt.CustomContextMenu)
        self.file_list.customContextMenuRequested.connect(self.show_context_menu)
        self.file_list.selectionModel().selectionChanged.connect(self.update_status)
        
        layout.addWidget(self.file_list)
        
        # 状态栏
        status_layout = QHBoxLayout()
        self.status_label = QLineEdit()
        self.status_label.setReadOnly(True)
        status_layout.addWidget(self.status_label)
        layout.addLayout(status_layout)
        
        self.setLayout(layout)
        
        # 初始化文件列表
        self.refresh()
    
    def refresh(self):
        """刷新文件列表"""
        if not os.path.exists(self.current_path):
            QMessageBox.warning(self, "警告", "路径不存在")
            self.current_path = str(Path.home())
        
        self.path_input.setText(self.current_path)
        self.load_directory(self.current_path)
        self.update_status()
    
    def load_directory(self, path):
        """加载目录内容"""
        try:
            self.file_list.setRowCount(0)
            items = []
            
            # 添加上级目录
            if path != os.path.abspath(os.sep):
                items.append({
                    'name': '..',
                    'path': os.path.dirname(path),
                    'is_dir': True,
                    'size': '-',
                    'modified': '-'
                })
            
            # 列出目录内容
            for item in os.listdir(path):
                item_path = os.path.join(path, item)
                try:
                    if os.path.isdir(item_path):
                        items.append({
                            'name': item,
                            'path': item_path,
                            'is_dir': True,
                            'size': '-',
                            'modified': self.get_modified_time(item_path)
                        })
                    else:
                        size = os.path.getsize(item_path)
                        size_str = self.format_size(size)
                        items.append({
                            'name': item,
                            'path': item_path,
                            'is_dir': False,
                            'size': size_str,
                            'modified': self.get_modified_time(item_path)
                        })
                except (OSError, IOError):
                    continue
            
            # 排序：目录优先，然后按名称排序
            items.sort(key=lambda x: (not x['is_dir'], x['name'].lower()))
            
            # 填充表格
            for item in items:
                row = self.file_list.rowCount()
                self.file_list.insertRow(row)
                
                # 名称
                name_item = QTableWidgetItem(item['name'])
                if item['is_dir']:
                    font = QFont()
                    font.setBold(True)
                    name_item.setFont(font)
                self.file_list.setItem(row, 0, name_item)
                
                # 类型
                type_item = QTableWidgetItem("文件夹" if item['is_dir'] else "文件")
                self.file_list.setItem(row, 1, type_item)
                
                # 大小
                size_item = QTableWidgetItem(item['size'])
                self.file_list.setItem(row, 2, size_item)
                
                # 修改时间
                time_item = QTableWidgetItem(item['modified'])
                self.file_list.setItem(row, 3, time_item)
        
        except PermissionError:
            QMessageBox.warning(self, "错误", "没有权限访问此目录")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"加载目录失败: {str(e)}")
    
    @staticmethod
    def format_size(size):
        """格式化文件大小"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024:
                return f"{size:.2f} {unit}"
            size /= 1024
        return f"{size:.2f} TB"
    
    @staticmethod
    def get_modified_time(path):
        """获取修改时间"""
        try:
            timestamp = os.path.getmtime(path)
            return datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')
        except:
            return '-'
    
    def update_status(self):
        """更新状态栏"""
        try:
            total_items = self.file_list.rowCount()
            selected = len(self.file_list.selectedIndexes()) // 4 if self.file_list.selectedIndexes() else 0
            
            # 计算选中文件的总大小
            total_size = 0
            for index in self.file_list.selectedIndexes():
                row = index.row()
                size_text = self.file_list.item(row, 2).text()
                if size_text and size_text != '-':
                    try:
                        size_parts = size_text.split()
                        size_val = float(size_parts[0])
                        unit = size_parts[1] if len(size_parts) > 1 else 'B'
                        multipliers = {'B': 1, 'KB': 1024, 'MB': 1024**2, 'GB': 1024**3}
                        total_size += size_val * multipliers.get(unit, 1)
                    except:
                        pass
            
            status_text = f"总项: {total_items} | 选中: {selected} | 大小: {self.format_size(total_size)}"
            self.status_label.setText(status_text)
        except:
            self.status_label.setText("就绪")
    
    def on_item_double_clicked(self, item):
        """双击打开"""
        row = item.row()
        name = self.file_list.item(row, 0).text()
        
        if name == '..':
            self.go_up()
        else:
            item_path = os.path.join(self.current_path, name)
            if os.path.isdir(item_path):
                self.change_path(item_path)
    
    def on_path_changed(self):
        """路径改变"""
        new_path = self.path_input.text().strip()
        if os.path.isdir(new_path):
            self.change_path(new_path)
        else:
            QMessageBox.warning(self, "错误", "路径不存在或无效")
            self.path_input.setText(self.current_path)
    
    def change_path(self, path):
        """改变当前路径"""
        path = os.path.abspath(path)
        if os.path.isdir(path):
            self.current_path = path
            self.refresh()
        else:
            QMessageBox.warning(self, "错误", "路径无效")
    
    def go_up(self):
        """返回上级目录"""
        parent = os.path.dirname(self.current_path)
        if parent != self.current_path:
            self.change_path(parent)
    
    def browse_folder(self):
        """浏览文件夹"""
        folder = QFileDialog.getExistingDirectory(self, "选择文件夹", self.current_path)
        if folder:
            self.change_path(folder)
    
    def get_selected_items(self):
        """获取选中的文件"""
        selected = []
        for index in self.file_list.selectedIndexes():
            row = index.row()
            name = self.file_list.item(row, 0).text()
            if name != '..':
                selected.append((name, os.path.join(self.current_path, name)))
        return selected
    
    def copy_to(self, dest_path):
        """复制文件到目标路径"""
        selected = self.get_selected_items()
        if not selected:
            QMessageBox.information(self, "提示", "未选中文件")
            return
        
        if not os.path.isdir(dest_path):
            QMessageBox.warning(self, "错误", "目标路径不存在")
            return
        
        try:
            for name, src_path in selected:
                dest = os.path.join(dest_path, name)
                if os.path.isdir(src_path):
                    if os.path.exists(dest):
                        shutil.rmtree(dest)
                    shutil.copytree(src_path, dest)
                else:
                    shutil.copy2(src_path, dest)
            
            QMessageBox.information(self, "成功", f"已复制 {len(selected)} 个项")
            # 刷新其他面板（由主窗口处理）
        except Exception as e:
            QMessageBox.critical(self, "错误", f"复制失败: {str(e)}")
    
    def move_to(self, dest_path):
        """移动文件到目标路径"""
        selected = self.get_selected_items()
        if not selected:
            QMessageBox.information(self, "提示", "未选中文件")
            return
        
        if not os.path.isdir(dest_path):
            QMessageBox.warning(self, "错误", "目标路径不存在")
            return
        
        try:
            for name, src_path in selected:
                dest = os.path.join(dest_path, name)
                shutil.move(src_path, dest)
            
            QMessageBox.information(self, "成功", f"已移动 {len(selected)} 个项")
            self.refresh()
        except Exception as e:
            QMessageBox.critical(self, "错误", f"移动失败: {str(e)}")
    
    def delete_files(self):
        """删除文件"""
        selected = self.get_selected_items()
        if not selected:
            QMessageBox.information(self, "提示", "未选中文件")
            return
        
        reply = QMessageBox.question(
            self, 
            "确认删除", 
            f"确定要删除选中的 {len(selected)} 个项吗？",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                for name, path in selected:
                    if os.path.isdir(path):
                        shutil.rmtree(path)
                    else:
                        os.remove(path)
                
                QMessageBox.information(self, "成功", f"已删除 {len(selected)} 个项")
                self.refresh()
            except Exception as e:
                QMessageBox.critical(self, "错误", f"删除失败: {str(e)}")
    
    def show_context_menu(self, position):
        """显示右键菜单"""
        menu = QMenu(self)
        
        copy_action = menu.addAction("复制")
        move_action = menu.addAction("移动")
        delete_action = menu.addAction("删除")
        
        menu.addSeparator()
        
        refresh_action = menu.addAction("刷新")
        properties_action = menu.addAction("属性")
        
        action = menu.exec_(self.file_list.mapToGlobal(position))
        
        if action == copy_action:
            self.copy_to(self.current_path)
        elif action == move_action:
            self.move_to(self.current_path)
        elif action == delete_action:
            self.delete_files()
        elif action == refresh_action:
            self.refresh()
        elif action == properties_action:
            self.show_properties()
    
    def show_properties(self):
        """显示文件属性"""
        selected = self.get_selected_items()
        if not selected:
            return
        
        name, path = selected[0]
        try:
            stat = os.stat(path)
            size = stat.st_size
            modified = datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S')
            
            info = f"名称: {name}\n"
            info += f"路径: {path}\n"
            info += f"大小: {self.format_size(size)}\n"
            info += f"修改时间: {modified}\n"
            info += f"类型: {'文件夹' if os.path.isdir(path) else '文件'}"
            
            QMessageBox.information(self, "文件属性", info)
        except Exception as e:
            QMessageBox.critical(self, "错误", f"无法获取属性: {str(e)}")
