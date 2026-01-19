"""
文件浏览面板 - 单个面板的实现
"""

import os
import shutil
import fnmatch
import re
from pathlib import Path
from datetime import datetime
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QTableWidget, 
    QTableWidgetItem, QMessageBox, QFileDialog, QHeaderView, QMenu, QPushButton,
    QTreeView, QSplitter
)
from PyQt5.QtCore import Qt, QSize, QDir
from PyQt5.QtGui import QIcon, QFont
from PyQt5.QtWidgets import QFileSystemModel


class FilePanel(QWidget):
    def __init__(self, panel_name="", initial_path=None, show_tree=False, filter_mode="wildcard", on_path_changed_callback=None):
        super().__init__()
        self.panel_name = panel_name
        self.current_path = initial_path or str(Path.home())
        self.filter_mode = filter_mode  # wildcard or regex
        self.filter_pattern = ""
        self.show_tree_flag = show_tree
        self.on_path_changed_callback = on_path_changed_callback  # 路径改变时的回调函数
        
        # 验证初始路径
        if not os.path.isdir(self.current_path):
            self.current_path = str(Path.home())
        
        # 初始化历史记录管理器
        from .history_manager import HistoryManager
        self.history = HistoryManager()
        self.history.navigate_to(self.current_path)

        # 排序配置（默认按名称升序）
        self.sort_by = 'name'   # name, size, date, type
        self.sort_order = 'asc' # asc, desc
        
        self.sePlected_files = []
        self.setFocusPolicy(Qt.StrongFocus)  # 允许获得焦点
        
        # 主布局
        layout = QVBoxLayout()
        layout.setSpacing(8)
        
        # 路径输入框
        path_layout = QHBoxLayout()
        self.path_input = QLineEdit()
        self.path_input.setText(self.current_path)
        self.path_input.returnPressed.connect(self.on_path_changed)
        self.path_input.setStyleSheet("""
            QLineEdit {
                background-color: #FFFFFF;
                border: 1px solid #D0D0D0;
                border-radius: 3px;
                padding: 4px;
                font-size: 10pt;
            }
            QLineEdit:focus {
                border: 1px solid #ADD8E6;
                background-color: #FFFFFF;
            }
        """)
        path_layout.addWidget(self.path_input)
        
        browse_btn = QPushButton("浏览...")
        browse_btn.clicked.connect(self.browse_folder)
        browse_btn.setStyleSheet("""
            QPushButton {
                padding: 4px 12px;
                border-radius: 3px;
                border: 1px solid #D0D0D0;
                background-color: #F5F5F5;
            }
            QPushButton:hover {
                background-color: #EFEFEF;
            }
            QPushButton:pressed {
                background-color: #E8E8E8;
            }
        """)
        path_layout.addWidget(browse_btn)
        layout.addLayout(path_layout)
        
        # 过滤输入框
        filter_layout = QHBoxLayout()
        self.filter_input = QLineEdit()
        self.filter_input.setPlaceholderText("过滤（支持通配符，例：*.txt；正则请切换模式）")
        self.filter_input.returnPressed.connect(self.apply_filter)
        filter_layout.addWidget(self.filter_input)
        
        clear_filter_btn = QPushButton("清除过滤")
        clear_filter_btn.clicked.connect(self.clear_filter)
        clear_filter_btn.setStyleSheet("""
            QPushButton {
                padding: 4px 10px;
                border-radius: 3px;
                border: 1px solid #D0D0D0;
                background-color: #F5F5F5;
            }
            QPushButton:hover { background-color: #EFEFEF; }
            QPushButton:pressed { background-color: #E8E8E8; }
        """)
        filter_layout.addWidget(clear_filter_btn)
        layout.addLayout(filter_layout)
        
        # 分割器：目录树 + 文件列表
        splitter = QSplitter()
        splitter.setOrientation(Qt.Horizontal)
        
        # 目录树
        self.dir_model = QFileSystemModel()
        self.dir_model.setFilter(QDir.NoDotAndDotDot | QDir.AllDirs)
        self.dir_model.setRootPath(QDir.rootPath())
        
        self.dir_tree = QTreeView()
        self.dir_tree.setModel(self.dir_model)
        self.dir_tree.setRootIndex(self.dir_model.index(self.current_path))
        self.dir_tree.clicked.connect(self.on_tree_clicked)
        self.dir_tree.setHeaderHidden(True)
        self.dir_tree.setVisible(self.show_tree_flag)
        
        # 文件列表表格
        self.file_list = QTableWidget()
        self.file_list.setColumnCount(4)
        self.file_list.setHorizontalHeaderLabels(["名称", "类型", "大小", "修改时间"])
        self.file_list.horizontalHeader().setStretchLastSection(False)
        self.file_list.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.file_list.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.file_list.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.file_list.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        
        self.file_list.setStyleSheet("""
            QTableWidget {
                background-color: #FFFFFF;
                border: 1px solid #D0D0D0;
                border-radius: 3px;
                gridline-color: #E8E8E8;
            }
            QTableWidget::item {
                padding: 2px 4px;
            }
            QTableWidget::item:selected {
                background-color: #0078d4;
                color: white;
            }
            QHeaderView::section {
                background-color: #F5F5F5;
                padding: 4px;
                border: none;
                border-right: 1px solid #E0E0E0;
                border-bottom: 1px solid #E0E0E0;
            }
        """)
        
        self.file_list.setSelectionBehavior(QTableWidget.SelectRows)
        self.file_list.setSelectionMode(QTableWidget.ExtendedSelection)
        self.file_list.itemDoubleClicked.connect(self.on_item_double_clicked)
        self.file_list.setContextMenuPolicy(Qt.CustomContextMenu)
        self.file_list.customContextMenuRequested.connect(self.show_context_menu)
        self.file_list.selectionModel().selectionChanged.connect(self.update_status)
        
        splitter.addWidget(self.dir_tree)
        splitter.addWidget(self.file_list)
        splitter.setStretchFactor(0, 0)
        splitter.setStretchFactor(1, 1)
        layout.addWidget(splitter)
        
        # 状态栏
        status_layout = QHBoxLayout()
        self.status_label = QLineEdit()
        self.status_label.setReadOnly(True)
        self.status_label.setStyleSheet("""
            QLineEdit {
                background-color: #F5F5F5;
                border: 1px solid #D0D0D0;
                border-radius: 3px;
                padding: 4px;
                font-size: 9pt;
                color: #666666;
            }
        """)
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
            
            # 排序：目录优先，然后按配置的排序方式排序
            items = self._sort_items(items)
            
            # 过滤
            filtered_items = []
            for item in items:
                if self._match_filter(item['name']):
                    filtered_items.append(item)
            
            # 填充表格
            for item in filtered_items:
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
            # 静默跳过无权限目录，不弹对话框，行为类似 FreeCommander
            # 保持当前路径不变，文件列表保持上一次可访问状态
            return
        except Exception as e:
            QMessageBox.critical(self, "错误", f"加载目录失败: {str(e)}")
    
    def _sort_items(self, items):
        """排序文件列表"""
        # 目录优先
        dirs = [item for item in items if item.get('is_dir', False) and item['name'] != '..']
        files = [item for item in items if not item.get('is_dir', False)]
        parent = [item for item in items if item.get('is_dir', False) and item['name'] == '..']
        
        # 对目录和文件分别排序
        def sort_key(item):
            if self.sort_by == 'name':
                return item['name'].lower()
            elif self.sort_by == 'size':
                # 目录返回0，文件返回实际大小
                if item.get('is_dir', False):
                    return 0
                try:
                    return os.path.getsize(item['path'])
                except:
                    return 0
            elif self.sort_by == 'date':
                # 使用修改时间
                try:
                    return os.path.getmtime(item['path'])
                except:
                    return 0
            elif self.sort_by == 'type':
                # 按扩展名排序
                if item.get('is_dir', False):
                    return ('', item['name'].lower())
                ext = os.path.splitext(item['name'])[1].lower()
                return (ext, item['name'].lower())
            return item['name'].lower()
        
        dirs.sort(key=sort_key, reverse=(self.sort_order == 'desc'))
        files.sort(key=sort_key, reverse=(self.sort_order == 'desc'))
        
        # 合并：父目录 + 目录 + 文件
        return parent + dirs + files
    
    def set_sort(self, sort_by, sort_order='asc'):
        """设置排序方式"""
        self.sort_by = sort_by
        self.sort_order = sort_order
        self.refresh()
    
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
        try:
            if item is None:
                return
            
            row = item.row()
            name_item = self.file_list.item(row, 0)
            if name_item is None:
                return
            
            name = name_item.text()
            if not name:
                return
            
            if name == '..':
                self.go_up()
            else:
                item_path = os.path.join(self.current_path, name)
                if os.path.isdir(item_path):
                    self.change_path(item_path)
                elif os.path.isfile(item_path):
                    # 双击文件时，使用系统默认程序打开
                    try:
                        if os.name == 'nt':  # Windows
                            os.startfile(item_path)
                        elif os.name == 'posix':  # Linux/macOS
                            import subprocess
                            subprocess.Popen(['xdg-open', item_path] if os.uname().sysname != 'Darwin' else ['open', item_path])
                    except Exception as e:
                        QMessageBox.warning(self, "错误", f"无法打开文件: {str(e)}")
        except Exception as e:
            # 捕获所有异常，防止程序崩溃
            import traceback
            print(f"双击事件处理错误: {e}")
            print(traceback.format_exc())
            QMessageBox.warning(self, "错误", f"处理双击事件时发生错误: {str(e)}")
    
    def on_path_changed(self):
        """路径改变"""
        new_path = self.path_input.text().strip()
        if os.path.isdir(new_path):
            self.change_path(new_path)
        else:
            QMessageBox.warning(self, "错误", "路径不存在或无效")
            self.path_input.setText(self.current_path)
    
    def change_path(self, path, add_to_history=True):
        """改变当前路径"""
        path = os.path.abspath(path)
        if os.path.isdir(path):
            old_path = self.current_path
            self.current_path = path
            
            # 添加到历史记录
            if add_to_history:
                self.history.navigate_to(self.current_path)
            
            if self.show_tree_flag:
                try:
                    self.dir_tree.setRootIndex(self.dir_model.index(self.current_path))
                except Exception:
                    pass
            self.path_input.setText(self.current_path)
            self.refresh()
            
            # 通知主窗口更新标签标题
            if self.on_path_changed_callback:
                self.on_path_changed_callback(self)
        else:
            QMessageBox.warning(self, "错误", "路径无效")
    
    def set_path(self, path):
        """设置路径（用于外部调用，会添加到历史）"""
        self.change_path(path, add_to_history=True)
    
    def go_up(self):
        """返回上级目录"""
        parent = os.path.dirname(self.current_path)
        if parent != self.current_path:
            self.change_path(parent)
    
    def go_back(self):
        """后退"""
        path = self.history.go_back()
        if path:
            self.change_path(path, add_to_history=False)
            return True
        return False
    
    def go_forward(self):
        """前进"""
        path = self.history.go_forward()
        if path:
            self.change_path(path, add_to_history=False)
            return True
        return False
    
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
    
    def get_selected_files(self):
        """获取选中文件的完整路径列表"""
        files = []
        for index in self.file_list.selectedIndexes():
            row = index.row()
            name = self.file_list.item(row, 0).text()
            if name != '..' and os.path.isfile(os.path.join(self.current_path, name)):
                files.append(os.path.join(self.current_path, name))
        return files
    
    def _match_filter(self, name):
        """根据当前过滤规则匹配名称"""
        if name == '..' or not self.filter_pattern:
            return True
        pattern = self.filter_pattern
        if self.filter_mode == 'regex':
            try:
                return re.search(pattern, name, re.IGNORECASE) is not None
            except re.error:
                return True  # 正则错误时不阻断显示
        return fnmatch.fnmatch(name.lower(), pattern.lower())
    
    def apply_filter(self):
        """应用过滤"""
        self.filter_pattern = self.filter_input.text().strip()
        self.refresh()
    
    def clear_filter(self):
        """清除过滤"""
        self.filter_pattern = ""
        self.filter_input.clear()
        self.refresh()
    
    def on_tree_clicked(self, index):
        """目录树点击"""
        path = self.dir_model.filePath(index)
        if os.path.isdir(path):
            self.change_path(path)
    
    def set_show_tree(self, show: bool):
        """显示/隐藏目录树"""
        self.show_tree_flag = show
        self.dir_tree.setVisible(show)
    
    def set_filter_mode(self, mode: str):
        """设置过滤模式"""
        if mode in ("wildcard", "regex"):
            self.filter_mode = mode
            self.refresh()
    
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
        
        # 获取选中的项
        selected_items = self.get_selected_items()
        is_single_file = len(selected_items) == 1 and not os.path.isdir(selected_items[0][1])
        is_multiple = len(selected_items) > 1
        
        # 预览（仅单个文件）
        if is_single_file:
            preview_action = menu.addAction("快速预览")
            menu.addSeparator()
        
        copy_action = menu.addAction("复制")
        move_action = menu.addAction("移动")
        delete_action = menu.addAction("删除")
        
        menu.addSeparator()
        
        # 新建功能
        new_folder_action = menu.addAction("新建文件夹")
        new_file_action = menu.addAction("新建文件")
        menu.addSeparator()
        
        # 压缩/解压
        if is_multiple or (len(selected_items) == 1 and os.path.isdir(selected_items[0][1])):
            compress_action = menu.addAction("压缩为ZIP...")
            menu.addSeparator()
        
        # 解压（如果选中ZIP文件）
        if len(selected_items) == 1:
            file_path = selected_items[0][1]
            if os.path.isfile(file_path) and file_path.lower().endswith('.zip'):
                extract_action = menu.addAction("解压ZIP...")
                menu.addSeparator()
        
        # 批量重命名（多个文件）
        if is_multiple:
            rename_action = menu.addAction("批量重命名")
            menu.addSeparator()
        
        refresh_action = menu.addAction("刷新")
        
        menu.addSeparator()
        
        # 排序菜单
        sort_menu = menu.addMenu("排序方式")
        sort_name_asc = sort_menu.addAction("按名称 (升序)")
        sort_name_desc = sort_menu.addAction("按名称 (降序)")
        sort_size_asc = sort_menu.addAction("按大小 (升序)")
        sort_size_desc = sort_menu.addAction("按大小 (降序)")
        sort_date_asc = sort_menu.addAction("按日期 (升序)")
        sort_date_desc = sort_menu.addAction("按日期 (降序)")
        sort_type_asc = sort_menu.addAction("按类型 (升序)")
        sort_type_desc = sort_menu.addAction("按类型 (降序)")
        
        menu.addSeparator()
        
        properties_action = menu.addAction("属性")
        
        action = menu.exec_(self.file_list.mapToGlobal(position))
        
        # 处理排序操作
        if action == sort_name_asc:
            self.set_sort('name', 'asc')
        elif action == sort_name_desc:
            self.set_sort('name', 'desc')
        elif action == sort_size_asc:
            self.set_sort('size', 'asc')
        elif action == sort_size_desc:
            self.set_sort('size', 'desc')
        elif action == sort_date_asc:
            self.set_sort('date', 'asc')
        elif action == sort_date_desc:
            self.set_sort('date', 'desc')
        elif action == sort_type_asc:
            self.set_sort('type', 'asc')
        elif action == sort_type_desc:
            self.set_sort('type', 'desc')
        
        if action == preview_action:
            self.show_preview(selected_items[0][1])
        elif action == copy_action:
            self.copy_to(self.current_path)
        elif action == move_action:
            self.move_to(self.current_path)
        elif action == delete_action:
            self.delete_files()
        elif action == new_folder_action:
            self.create_new_folder()
        elif action == new_file_action:
            self.create_new_file()
        elif action == compress_action:
            self.compress_files()
        elif action == extract_action:
            self.extract_archive(selected_items[0][1])
        elif action == rename_action:
            self.batch_rename()
        elif action == refresh_action:
            self.refresh()
        elif action == properties_action:
            self.show_properties()
    
    def show_preview(self, file_path):
        """显示文件预览"""
        # 通过父窗口获取预览面板
        parent = self.parent()
        while parent and not hasattr(parent, 'preview_panel'):
            parent = parent.parent()
        
        if parent and hasattr(parent, 'preview_panel'):
            parent.preview_panel.preview_file(file_path)
            parent.preview_panel.show()
        else:
            QMessageBox.information(self, "提示", "预览功能未初始化")
    
    def batch_rename(self):
        """批量重命名"""
        from .rename_dialog import RenameDialog
        
        selected = self.get_selected_items()
        if not selected:
            QMessageBox.information(self, "提示", "请先选择要重命名的文件")
            return
        
        dialog = RenameDialog(self, selected)
        if dialog.exec_() == RenameDialog.Accepted:
            self.refresh()
    
    def create_new_folder(self):
        """新建文件夹"""
        from PyQt5.QtWidgets import QInputDialog
        
        name, ok = QInputDialog.getText(
            self,
            "新建文件夹",
            "请输入文件夹名称:",
            text="新建文件夹"
        )
        
        if ok and name:
            new_path = os.path.join(self.current_path, name)
            if os.path.exists(new_path):
                QMessageBox.warning(self, "错误", "文件夹已存在")
                return
            
            try:
                os.makedirs(new_path)
                self.refresh()
                QMessageBox.information(self, "成功", f"文件夹已创建: {name}")
            except Exception as e:
                QMessageBox.critical(self, "错误", f"创建失败: {str(e)}")
    
    def create_new_file(self):
        """新建文件"""
        from PyQt5.QtWidgets import QInputDialog
        
        name, ok = QInputDialog.getText(
            self,
            "新建文件",
            "请输入文件名:",
            text="新建文件.txt"
        )
        
        if ok and name:
            new_path = os.path.join(self.current_path, name)
            if os.path.exists(new_path):
                QMessageBox.warning(self, "错误", "文件已存在")
                return
            
            try:
                with open(new_path, 'w', encoding='utf-8') as f:
                    pass  # 创建空文件
                self.refresh()
                QMessageBox.information(self, "成功", f"文件已创建: {name}")
            except Exception as e:
                QMessageBox.critical(self, "错误", f"创建失败: {str(e)}")
    
    def compress_files(self):
        """压缩文件"""
        from .archive_dialog import ArchiveDialog
        
        selected = self.get_selected_items()
        if not selected:
            QMessageBox.information(self, "提示", "请先选择要压缩的文件或文件夹")
            return
        
        file_paths = [path for _, path in selected]
        
        # 获取主窗口
        parent = self.parent()
        while parent and not hasattr(parent, 'preview_panel'):
            parent = parent.parent()
        
        dialog = ArchiveDialog(parent, file_paths, operation='create')
        dialog.exec_()
    
    def extract_archive(self, zip_path):
        """解压文件"""
        from .archive_dialog import ArchiveDialog
        
        # 获取主窗口
        parent = self.parent()
        while parent and not hasattr(parent, 'preview_panel'):
            parent = parent.parent()
        
        dialog = ArchiveDialog(parent, [zip_path], operation='extract')
        dialog.exec_()
    
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
