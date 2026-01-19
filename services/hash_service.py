"""
哈希计算服务模块
"""

import hashlib
import os
from pathlib import Path


class HashService:
    """哈希计算服务"""
    
    @staticmethod
    def calculate_md5(file_path, chunk_size=8192):
        """计算文件的MD5哈希值"""
        md5_hash = hashlib.md5()
        try:
            with open(file_path, 'rb') as f:
                while chunk := f.read(chunk_size):
                    md5_hash.update(chunk)
            return md5_hash.hexdigest()
        except Exception as e:
            raise Exception(f"计算MD5失败: {str(e)}")
    
    @staticmethod
    def calculate_sha1(file_path, chunk_size=8192):
        """计算文件的SHA1哈希值"""
        sha1_hash = hashlib.sha1()
        try:
            with open(file_path, 'rb') as f:
                while chunk := f.read(chunk_size):
                    sha1_hash.update(chunk)
            return sha1_hash.hexdigest()
        except Exception as e:
            raise Exception(f"计算SHA1失败: {str(e)}")
    
    @staticmethod
    def calculate_sha256(file_path, chunk_size=8192):
        """计算文件的SHA256哈希值"""
        sha256_hash = hashlib.sha256()
        try:
            with open(file_path, 'rb') as f:
                while chunk := f.read(chunk_size):
                    sha256_hash.update(chunk)
            return sha256_hash.hexdigest()
        except Exception as e:
            raise Exception(f"计算SHA256失败: {str(e)}")
    
    @staticmethod
    def calculate_hash(file_path, algorithm='md5', chunk_size=8192):
        """计算文件哈希值（通用方法）"""
        algorithms = {
            'md5': hashlib.md5,
            'sha1': hashlib.sha1,
            'sha256': hashlib.sha256
        }
        
        if algorithm.lower() not in algorithms:
            raise ValueError(f"不支持的算法: {algorithm}")
        
        hash_obj = algorithms[algorithm.lower()]()
        try:
            with open(file_path, 'rb') as f:
                while chunk := f.read(chunk_size):
                    hash_obj.update(chunk)
            return hash_obj.hexdigest()
        except Exception as e:
            raise Exception(f"计算{algorithm.upper()}失败: {str(e)}")
    
    @staticmethod
    def verify_hash(file_path, expected_hash, algorithm='md5'):
        """验证文件哈希值"""
        calculated_hash = HashService.calculate_hash(file_path, algorithm)
        return calculated_hash.lower() == expected_hash.lower()
    
    @staticmethod
    def find_duplicates(directory, algorithm='md5', progress_callback=None):
        """查找重复文件
        
        Args:
            directory: 要搜索的目录
            algorithm: 哈希算法 (md5, sha1, sha256)
            progress_callback: 进度回调函数 (current, total)
        
        Returns:
            dict: {hash_value: [file_paths], ...}
        """
        hash_map = {}
        file_list = []
        
        # 收集所有文件
        for root, dirs, files in os.walk(directory):
            for file in files:
                file_path = os.path.join(root, file)
                file_list.append(file_path)
        
        total = len(file_list)
        
        # 计算每个文件的哈希值
        for idx, file_path in enumerate(file_list):
            try:
                file_hash = HashService.calculate_hash(file_path, algorithm)
                
                if file_hash not in hash_map:
                    hash_map[file_hash] = []
                hash_map[file_hash].append(file_path)
                
                if progress_callback:
                    progress_callback(idx + 1, total)
                    
            except Exception:
                continue
        
        # 返回只有重复的文件（哈希值对应多个文件）
        duplicates = {h: paths for h, paths in hash_map.items() if len(paths) > 1}
        return duplicates
