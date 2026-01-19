"""
压缩/解压服务模块
"""

import os
import zipfile
import shutil
from pathlib import Path


class ArchiveService:
    """压缩/解压服务"""
    
    @staticmethod
    def create_zip(zip_path, source_paths, progress_callback=None):
        """创建ZIP压缩文件
        
        Args:
            zip_path: 目标ZIP文件路径
            source_paths: 要压缩的文件/文件夹路径列表
            progress_callback: 进度回调函数 (current, total, filename)
        
        Returns:
            bool: 是否成功
        """
        try:
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                total_files = ArchiveService._count_files(source_paths)
                current = 0
                
                for source_path in source_paths:
                    if os.path.isfile(source_path):
                        # 压缩单个文件
                        zipf.write(source_path, os.path.basename(source_path))
                        current += 1
                        if progress_callback:
                            progress_callback(current, total_files, os.path.basename(source_path))
                    
                    elif os.path.isdir(source_path):
                        # 压缩文件夹
                        for root, dirs, files in os.walk(source_path):
                            for file in files:
                                file_path = os.path.join(root, file)
                                arcname = os.path.relpath(file_path, os.path.dirname(source_path))
                                zipf.write(file_path, arcname)
                                current += 1
                                if progress_callback:
                                    progress_callback(current, total_files, arcname)
            
            return True
        except Exception as e:
            raise Exception(f"创建压缩文件失败: {str(e)}")
    
    @staticmethod
    def extract_zip(zip_path, extract_to=None, progress_callback=None):
        """解压ZIP文件
        
        Args:
            zip_path: ZIP文件路径
            extract_to: 解压目标目录（默认为ZIP文件所在目录）
            progress_callback: 进度回调函数 (current, total, filename)
        
        Returns:
            str: 解压到的目录路径
        """
        try:
            if extract_to is None:
                extract_to = os.path.dirname(zip_path)
            
            # 创建解压目录
            zip_name = os.path.splitext(os.path.basename(zip_path))[0]
            extract_dir = os.path.join(extract_to, zip_name)
            
            # 如果目录已存在，添加序号
            counter = 1
            original_extract_dir = extract_dir
            while os.path.exists(extract_dir):
                extract_dir = f"{original_extract_dir}_{counter}"
                counter += 1
            
            os.makedirs(extract_dir, exist_ok=True)
            
            with zipfile.ZipFile(zip_path, 'r') as zipf:
                file_list = zipf.namelist()
                total = len(file_list)
                
                for idx, member in enumerate(file_list):
                    zipf.extract(member, extract_dir)
                    if progress_callback:
                        progress_callback(idx + 1, total, member)
            
            return extract_dir
        except Exception as e:
            raise Exception(f"解压文件失败: {str(e)}")
    
    @staticmethod
    def _count_files(paths):
        """统计要压缩的文件总数"""
        count = 0
        for path in paths:
            if os.path.isfile(path):
                count += 1
            elif os.path.isdir(path):
                for root, dirs, files in os.walk(path):
                    count += len(files)
        return count
    
    @staticmethod
    def is_zip_file(file_path):
        """检查是否为ZIP文件"""
        return os.path.isfile(file_path) and file_path.lower().endswith('.zip')
    
    @staticmethod
    def get_zip_info(zip_path):
        """获取ZIP文件信息"""
        try:
            with zipfile.ZipFile(zip_path, 'r') as zipf:
                return {
                    'file_count': len(zipf.namelist()),
                    'total_size': sum(info.file_size for info in zipf.infolist()),
                    'compressed_size': os.path.getsize(zip_path),
                    'files': zipf.namelist()[:10]  # 前10个文件
                }
        except Exception:
            return None
