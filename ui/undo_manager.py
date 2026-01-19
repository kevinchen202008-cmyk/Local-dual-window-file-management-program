"""
撤销/重做管理器
"""

from collections import deque
from enum import Enum
import os
import shutil


class OperationType(Enum):
    """操作类型"""
    COPY = "copy"
    MOVE = "move"
    DELETE = "delete"
    RENAME = "rename"
    CREATE_FILE = "create_file"
    CREATE_FOLDER = "create_folder"


class Operation:
    """操作记录"""
    
    def __init__(self, op_type, source_paths, dest_path=None, old_names=None, new_names=None):
        self.op_type = op_type
        self.source_paths = source_paths if isinstance(source_paths, list) else [source_paths]
        self.dest_path = dest_path
        self.old_names = old_names or []
        self.new_names = new_names or []
        self.timestamp = None
    
    def can_undo(self):
        """是否可以撤销"""
        return self.op_type in [
            OperationType.COPY,
            OperationType.MOVE,
            OperationType.DELETE,
            OperationType.RENAME,
            OperationType.CREATE_FILE,
            OperationType.CREATE_FOLDER
        ]
    
    def can_redo(self):
        """是否可以重做"""
        return self.op_type in [
            OperationType.DELETE,
            OperationType.CREATE_FILE,
            OperationType.CREATE_FOLDER
        ]


class UndoManager:
    """撤销/重做管理器"""
    
    def __init__(self, max_size=50):
        self.max_size = max_size
        self.undo_stack = deque(maxlen=max_size)  # 撤销栈
        self.redo_stack = deque(maxlen=max_size)  # 重做栈
    
    def push_operation(self, operation):
        """添加操作到撤销栈"""
        from datetime import datetime
        operation.timestamp = datetime.now()
        self.undo_stack.append(operation)
        self.redo_stack.clear()  # 新操作清空重做栈
    
    def can_undo(self):
        """是否可以撤销"""
        return len(self.undo_stack) > 0
    
    def can_redo(self):
        """是否可以重做"""
        return len(self.redo_stack) > 0
    
    def undo(self):
        """撤销操作"""
        if not self.can_undo():
            return None, "没有可撤销的操作"
        
        operation = self.undo_stack.pop()
        
        try:
            if operation.op_type == OperationType.COPY:
                # 撤销复制：删除目标文件
                for source_path in operation.source_paths:
                    dest_file = os.path.join(operation.dest_path, os.path.basename(source_path))
                    if os.path.exists(dest_file):
                        if os.path.isdir(dest_file):
                            shutil.rmtree(dest_file)
                        else:
                            os.remove(dest_file)
                self.redo_stack.append(operation)
                return True, f"已撤销复制操作"
            
            elif operation.op_type == OperationType.MOVE:
                # 撤销移动：移回原位置
                for source_path in operation.source_paths:
                    dest_file = os.path.join(operation.dest_path, os.path.basename(source_path))
                    if os.path.exists(dest_file):
                        shutil.move(dest_file, source_path)
                self.redo_stack.append(operation)
                return True, f"已撤销移动操作"
            
            elif operation.op_type == OperationType.DELETE:
                # 撤销删除：恢复文件（需要从回收站或备份恢复）
                # 注意：实际删除的文件无法完全恢复，这里只是记录操作
                self.redo_stack.append(operation)
                return True, f"已撤销删除操作（注意：文件可能无法完全恢复）"
            
            elif operation.op_type == OperationType.RENAME:
                # 撤销重命名：恢复原名
                for old_name, new_name in zip(operation.old_names, operation.new_names):
                    old_path = os.path.join(operation.dest_path, new_name)
                    new_path = os.path.join(operation.dest_path, old_name)
                    if os.path.exists(old_path):
                        os.rename(old_path, new_path)
                self.redo_stack.append(operation)
                return True, f"已撤销重命名操作"
            
            elif operation.op_type == OperationType.CREATE_FILE:
                # 撤销创建文件：删除文件
                for source_path in operation.source_paths:
                    if os.path.exists(source_path):
                        os.remove(source_path)
                self.redo_stack.append(operation)
                return True, f"已撤销创建文件操作"
            
            elif operation.op_type == OperationType.CREATE_FOLDER:
                # 撤销创建文件夹：删除文件夹
                for source_path in operation.source_paths:
                    if os.path.exists(source_path):
                        shutil.rmtree(source_path)
                self.redo_stack.append(operation)
                return True, f"已撤销创建文件夹操作"
            
            return False, "未知的操作类型"
        
        except Exception as e:
            # 撤销失败，将操作放回栈
            self.undo_stack.append(operation)
            return False, f"撤销失败: {str(e)}"
    
    def redo(self):
        """重做操作"""
        if not self.can_redo():
            return None, "没有可重做的操作"
        
        operation = self.redo_stack.pop()
        
        try:
            if operation.op_type == OperationType.DELETE:
                # 重做删除：再次删除（如果文件存在）
                for source_path in operation.source_paths:
                    if os.path.exists(source_path):
                        if os.path.isdir(source_path):
                            shutil.rmtree(source_path)
                        else:
                            os.remove(source_path)
                self.undo_stack.append(operation)
                return True, f"已重做删除操作"
            
            elif operation.op_type == OperationType.CREATE_FILE:
                # 重做创建文件：重新创建空文件
                for source_path in operation.source_paths:
                    with open(source_path, 'w', encoding='utf-8') as f:
                        pass
                self.undo_stack.append(operation)
                return True, f"已重做创建文件操作"
            
            elif operation.op_type == OperationType.CREATE_FOLDER:
                # 重做创建文件夹：重新创建文件夹
                for source_path in operation.source_paths:
                    os.makedirs(source_path, exist_ok=True)
                self.undo_stack.append(operation)
                return True, f"已重做创建文件夹操作"
            
            return False, "该操作类型不支持重做"
        
        except Exception as e:
            # 重做失败，将操作放回栈
            self.redo_stack.append(operation)
            return False, f"重做失败: {str(e)}"
    
    def clear(self):
        """清空所有操作记录"""
        self.undo_stack.clear()
        self.redo_stack.clear()
    
    def get_undo_list(self, count=10):
        """获取撤销操作列表"""
        return list(self.undo_stack)[-count:]
    
    def get_redo_list(self, count=10):
        """获取重做操作列表"""
        return list(self.redo_stack)[-count:]
