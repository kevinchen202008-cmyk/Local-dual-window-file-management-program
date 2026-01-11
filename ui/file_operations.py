"""
文件操作工具模块
"""

import os
import shutil
import subprocess
from pathlib import Path


class FileOperationManager:
    """文件操作管理器"""
    
    @staticmethod
    def open_file(file_path):
        """打开文件"""
        if not os.path.exists(file_path):
            return False
        
        try:
            if os.name == 'nt':  # Windows
                os.startfile(file_path)
            elif os.name == 'posix':  # Linux/macOS
                subprocess.Popen(['xdg-open', file_path])
            return True
        except:
            return False
    
    @staticmethod
    def open_folder(folder_path):
        """打开文件夹"""
        if not os.path.isdir(folder_path):
            return False
        
        try:
            if os.name == 'nt':  # Windows
                os.startfile(folder_path)
            elif os.name == 'posix':  # Linux/macOS
                subprocess.Popen(['xdg-open', folder_path])
            return True
        except:
            return False
    
    @staticmethod
    def get_file_info(file_path):
        """获取文件信息"""
        try:
            stat = os.stat(file_path)
            return {
                'size': stat.st_size,
                'modified': stat.st_mtime,
                'accessed': stat.st_atime,
                'created': stat.st_ctime,
                'is_dir': os.path.isdir(file_path),
                'is_link': os.path.islink(file_path),
                'permissions': oct(stat.st_mode)[-3:]
            }
        except:
            return None
    
    @staticmethod
    def format_size(size_bytes):
        """格式化文件大小"""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size_bytes < 1024:
                return f"{size_bytes:.2f} {unit}"
            size_bytes /= 1024
        return f"{size_bytes:.2f} PB"
    
    @staticmethod
    def get_folder_size(folder_path):
        """获取文件夹大小"""
        total_size = 0
        try:
            for dirpath, dirnames, filenames in os.walk(folder_path):
                for f in filenames:
                    fp = os.path.join(dirpath, f)
                    try:
                        total_size += os.path.getsize(fp)
                    except:
                        pass
        except:
            pass
        return total_size
    
    @staticmethod
    def create_folder(parent_path, folder_name):
        """创建文件夹"""
        try:
            folder_path = os.path.join(parent_path, folder_name)
            os.makedirs(folder_path, exist_ok=True)
            return True
        except:
            return False
    
    @staticmethod
    def rename_file(old_path, new_name):
        """重命名文件"""
        try:
            parent = os.path.dirname(old_path)
            new_path = os.path.join(parent, new_name)
            os.rename(old_path, new_path)
            return True
        except:
            return False
    
    @staticmethod
    def get_disk_usage(path):
        """获取磁盘使用情况"""
        try:
            import shutil
            usage = shutil.disk_usage(path)
            return {
                'total': usage.total,
                'used': usage.used,
                'free': usage.free,
                'percent': (usage.used / usage.total) * 100 if usage.total > 0 else 0
            }
        except:
            return None
