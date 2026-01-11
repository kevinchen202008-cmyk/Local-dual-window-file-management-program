"""
搜索和过滤功能模块
"""

import os
import re
from pathlib import Path


class FileSearcher:
    """文件搜索器"""
    
    def __init__(self, root_path):
        self.root_path = root_path
    
    def search_by_name(self, pattern, include_dirs=True):
        """按名称搜索文件"""
        results = []
        try:
            for root, dirs, files in os.walk(self.root_path):
                if not include_dirs:
                    dirs.clear()
                
                # 搜索目录
                for dir_name in dirs:
                    if self._match_pattern(pattern, dir_name):
                        results.append(os.path.join(root, dir_name))
                
                # 搜索文件
                for file_name in files:
                    if self._match_pattern(pattern, file_name):
                        results.append(os.path.join(root, file_name))
        except PermissionError:
            pass
        
        return results
    
    def search_by_size(self, min_size=0, max_size=float('inf')):
        """按大小搜索文件"""
        results = []
        try:
            for root, dirs, files in os.walk(self.root_path):
                for file_name in files:
                    file_path = os.path.join(root, file_name)
                    try:
                        size = os.path.getsize(file_path)
                        if min_size <= size <= max_size:
                            results.append((file_path, size))
                    except OSError:
                        pass
        except PermissionError:
            pass
        
        return results
    
    def search_by_extension(self, extensions):
        """按扩展名搜索"""
        if isinstance(extensions, str):
            extensions = [extensions]
        
        results = []
        try:
            for root, dirs, files in os.walk(self.root_path):
                for file_name in files:
                    if any(file_name.endswith(ext) for ext in extensions):
                        results.append(os.path.join(root, file_name))
        except PermissionError:
            pass
        
        return results
    
    @staticmethod
    def _match_pattern(pattern, text):
        """匹配模式"""
        # 支持通配符 * 和 ?
        regex_pattern = pattern.replace('.', r'\.').replace('*', '.*').replace('?', '.')
        return bool(re.match(f'^{regex_pattern}$', text, re.IGNORECASE))
