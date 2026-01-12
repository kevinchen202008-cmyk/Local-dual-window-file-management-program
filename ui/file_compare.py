"""
文件对比模块 - 比较两个文件的内容、大小、修改时间等
支持文本文件、二进制文件和目录对比
"""

import os
import hashlib
from datetime import datetime
from pathlib import Path


class FileComparer:
    """文件对比器"""
    
    @staticmethod
    def compare_files(file1_path, file2_path):
        """
        对比两个文件
        
        Returns:
            dict: {
                'are_identical': bool,
                'comparison': str,  # 对比结果描述
                'file1': {...},     # 文件1信息
                'file2': {...},     # 文件2信息
                'differences': [...]  # 差异列表
            }
        """
        result = {
            'are_identical': False,
            'comparison': '',
            'file1': FileComparer._get_file_info(file1_path),
            'file2': FileComparer._get_file_info(file2_path),
            'differences': []
        }
        
        # 检查文件是否存在
        if not os.path.exists(file1_path):
            result['comparison'] = f"文件不存在: {file1_path}"
            return result
        
        if not os.path.exists(file2_path):
            result['comparison'] = f"文件不存在: {file2_path}"
            return result
        
        # 检查是否为文件
        if not os.path.isfile(file1_path) or not os.path.isfile(file2_path):
            result['comparison'] = "路径必须是文件，不能是目录"
            return result
        
        # 获取文件信息
        file1_info = result['file1']
        file2_info = result['file2']
        
        # 记录差异
        differences = []
        
        # 1. 比较大小
        if file1_info['size'] != file2_info['size']:
            differences.append({
                'type': 'size',
                'description': f"文件大小不同: {file1_info['size_formatted']} vs {file2_info['size_formatted']}"
            })
        
        # 2. 比较修改时间
        if file1_info['modified'] != file2_info['modified']:
            differences.append({
                'type': 'mtime',
                'description': f"修改时间不同: {file1_info['modified_str']} vs {file2_info['modified_str']}"
            })
        
        # 3. 比较哈希值（内容）
        hash1 = FileComparer._get_file_hash(file1_path)
        hash2 = FileComparer._get_file_hash(file2_path)
        
        if hash1 != hash2:
            differences.append({
                'type': 'content',
                'description': '文件内容不同'
            })
        else:
            result['are_identical'] = True
        
        result['differences'] = differences
        
        # 生成对比总结
        if result['are_identical']:
            result['comparison'] = "✅ 文件内容完全相同"
            if differences:
                result['comparison'] += f"\n⚠️ 但存在{len(differences)}个其他差异"
        else:
            result['comparison'] = f"❌ 文件存在{len(differences)}个差异"
        
        return result
    
    @staticmethod
    def _get_file_info(file_path):
        """获取文件信息"""
        try:
            stat = os.stat(file_path)
            size = stat.st_size
            mtime = stat.st_mtime
            
            return {
                'path': file_path,
                'name': os.path.basename(file_path),
                'size': size,
                'size_formatted': FileComparer._format_size(size),
                'modified': mtime,
                'modified_str': datetime.fromtimestamp(mtime).strftime('%Y-%m-%d %H:%M:%S'),
                'is_text': FileComparer._is_text_file(file_path)
            }
        except Exception as e:
            return {
                'path': file_path,
                'name': os.path.basename(file_path),
                'error': str(e)
            }
    
    @staticmethod
    def _get_file_hash(file_path, block_size=8192):
        """计算文件哈希值"""
        hasher = hashlib.md5()
        try:
            with open(file_path, 'rb') as f:
                while True:
                    block = f.read(block_size)
                    if not block:
                        break
                    hasher.update(block)
            return hasher.hexdigest()
        except Exception as e:
            return f"Error: {str(e)}"
    
    @staticmethod
    def _is_text_file(file_path):
        """判断是否为文本文件"""
        text_extensions = {
            '.txt', '.py', '.java', '.cpp', '.c', '.h', '.js', '.ts',
            '.html', '.htm', '.css', '.xml', '.json', '.yaml', '.yml',
            '.md', '.markdown', '.sh', '.bat', '.cmd', '.ini', '.cfg',
            '.conf', '.config', '.log', '.sql', '.r', '.rb', '.go'
        }
        
        ext = os.path.splitext(file_path)[1].lower()
        if ext in text_extensions:
            return True
        
        # 尝试读取文件的第一部分来判断
        try:
            with open(file_path, 'rb') as f:
                chunk = f.read(512)
                # 检查是否包含null字节（二进制文件的特征）
                return b'\x00' not in chunk
        except:
            return False
    
    @staticmethod
    def _format_size(size_bytes):
        """格式化文件大小"""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size_bytes < 1024:
                return f"{size_bytes:.2f} {unit}"
            size_bytes /= 1024
        return f"{size_bytes:.2f} PB"
    
    @staticmethod
    def get_text_file_diff(file1_path, file2_path):
        """
        获取文本文件的行级差异
        
        Returns:
            dict: {
                'file1_lines': list,
                'file2_lines': list,
                'added_lines': int,
                'removed_lines': int,
                'modified_lines': int
            }
        """
        try:
            with open(file1_path, 'r', encoding='utf-8', errors='ignore') as f:
                lines1 = f.readlines()
        except:
            lines1 = []
        
        try:
            with open(file2_path, 'r', encoding='utf-8', errors='ignore') as f:
                lines2 = f.readlines()
        except:
            lines2 = []
        
        # 简单的差异统计
        set1 = set(lines1)
        set2 = set(lines2)
        
        added = len(set2 - set1)
        removed = len(set1 - set2)
        
        return {
            'file1_lines': lines1,
            'file2_lines': lines2,
            'line_count1': len(lines1),
            'line_count2': len(lines2),
            'added_lines': added,
            'removed_lines': removed,
            'total_changes': added + removed
        }
    
    @staticmethod
    def compare_by_content(file1_path, file2_path):
        """
        详细的内容对比（逐字节比较）
        
        Returns:
            dict: 对比结果
        """
        try:
            with open(file1_path, 'rb') as f:
                content1 = f.read()
        except:
            content1 = b''
        
        try:
            with open(file2_path, 'rb') as f:
                content2 = f.read()
        except:
            content2 = b''
        
        if content1 == content2:
            return {
                'are_identical': True,
                'description': '文件内容完全相同'
            }
        
        # 查找第一个不同的位置
        min_len = min(len(content1), len(content2))
        first_diff_pos = -1
        
        for i in range(min_len):
            if content1[i] != content2[i]:
                first_diff_pos = i
                break
        
        if first_diff_pos == -1 and len(content1) != len(content2):
            first_diff_pos = min_len
        
        return {
            'are_identical': False,
            'size1': len(content1),
            'size2': len(content2),
            'first_diff_pos': first_diff_pos,
            'difference_count': sum(1 for i in range(min_len) if content1[i] != content2[i]),
            'description': f'文件在第{first_diff_pos}字节处出现不同'
        }


def find_same_named_files(dir1, dir2):
    """
    查找两个目录中的同名文件
    
    Returns:
        list: [(file_name, file1_path, file2_path), ...]
    """
    same_files = []
    
    try:
        files1 = {f: os.path.join(dir1, f) for f in os.listdir(dir1) 
                  if os.path.isfile(os.path.join(dir1, f))}
    except:
        files1 = {}
    
    try:
        files2 = {f: os.path.join(dir2, f) for f in os.listdir(dir2) 
                  if os.path.isfile(os.path.join(dir2, f))}
    except:
        files2 = {}
    
    # 找出同名文件
    common_names = set(files1.keys()) & set(files2.keys())
    
    for name in sorted(common_names):
        same_files.append({
            'name': name,
            'path1': files1[name],
            'path2': files2[name]
        })
    
    return same_files
