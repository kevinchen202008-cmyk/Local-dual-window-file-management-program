"""
历史记录管理器 - 前进/后退导航
"""

from collections import deque
from pathlib import Path


class HistoryManager:
    """历史记录管理器"""
    
    def __init__(self, max_size=50):
        self.max_size = max_size
        self.back_history = deque(maxlen=max_size)  # 后退历史
        self.forward_history = deque(maxlen=max_size)  # 前进历史
        self.current_path = None
    
    def navigate_to(self, path):
        """导航到新路径"""
        if self.current_path and self.current_path != path:
            self.back_history.append(self.current_path)
            self.forward_history.clear()  # 新导航清空前进历史
        
        self.current_path = path
    
    def can_go_back(self):
        """是否可以后退"""
        return len(self.back_history) > 0
    
    def can_go_forward(self):
        """是否可以前进"""
        return len(self.forward_history) > 0
    
    def go_back(self):
        """后退"""
        if not self.can_go_back():
            return None
        
        if self.current_path:
            self.forward_history.appendleft(self.current_path)
        
        self.current_path = self.back_history.pop()
        return self.current_path
    
    def go_forward(self):
        """前进"""
        if not self.can_go_forward():
            return None
        
        if self.current_path:
            self.back_history.append(self.current_path)
        
        self.current_path = self.forward_history.popleft()
        return self.current_path
    
    def get_back_list(self, count=10):
        """获取后退历史列表"""
        return list(self.back_history)[-count:]
    
    def get_forward_list(self, count=10):
        """获取前进历史列表"""
        return list(self.forward_history)[:count]
    
    def clear(self):
        """清空历史"""
        self.back_history.clear()
        self.forward_history.clear()
        self.current_path = None
