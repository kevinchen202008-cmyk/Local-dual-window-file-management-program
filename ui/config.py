"""
配置管理模块
"""

import json
import os
from pathlib import Path


class ConfigManager:
    """配置管理器"""
    
    def __init__(self):
        self.config_dir = Path.home() / '.filemanager'
        self.config_file = self.config_dir / 'config.json'
        self.default_config = {
            'left_panel_path': str(Path.home()),
            'right_panel_path': str(Path.home()),
            'window_width': 1400,
            'window_height': 800,
            'window_x': 100,
            'window_y': 100,
            'show_hidden_files': False,
            'sort_by': 'name',  # name, size, date, type
            'sort_order': 'asc',  # asc, desc
            'theme': 'default'
        }
        
        self.config = self.load_config()
    
    def load_config(self):
        """加载配置"""
        if not self.config_file.exists():
            self.save_config(self.default_config)
            return self.default_config.copy()
        
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
                # 合并默认配置和加载的配置
                result = self.default_config.copy()
                result.update(config)
                return result
        except:
            return self.default_config.copy()
    
    def save_config(self, config=None):
        """保存配置"""
        if config is None:
            config = self.config
        
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=4, ensure_ascii=False)
            return True
        except:
            return False
    
    def get(self, key, default=None):
        """获取配置值"""
        return self.config.get(key, default)
    
    def set(self, key, value):
        """设置配置值"""
        self.config[key] = value
        self.save_config()
    
    def update(self, updates):
        """批量更新配置"""
        self.config.update(updates)
        self.save_config()
