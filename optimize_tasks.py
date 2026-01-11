#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
优化任务跟踪工具
用于管理和跟踪持续优化任务
"""

import json
import os
from datetime import datetime
from pathlib import Path


class TaskTracker:
    """任务跟踪器"""
    
    def __init__(self):
        self.tasks_file = Path('.tasks.json')
        self.tasks = self.load_tasks()
    
    def load_tasks(self):
        """加载任务"""
        if self.tasks_file.exists():
            with open(self.tasks_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}
    
    def save_tasks(self):
        """保存任务"""
        with open(self.tasks_file, 'w', encoding='utf-8') as f:
            json.dump(self.tasks, f, ensure_ascii=False, indent=2)
    
    def add_task(self, name, description, priority='medium', version='v1.1'):
        """添加任务"""
        task_id = len(self.tasks) + 1
        self.tasks[str(task_id)] = {
            'id': task_id,
            'name': name,
            'description': description,
            'priority': priority,
            'version': version,
            'status': 'todo',
            'created': datetime.now().isoformat(),
            'completed': None
        }
        self.save_tasks()
        print(f"✓ 任务 #{task_id} 已添加: {name}")
    
    def start_task(self, task_id):
        """开始任务"""
        if str(task_id) in self.tasks:
            self.tasks[str(task_id)]['status'] = 'in_progress'
            self.save_tasks()
            print(f"✓ 任务 #{task_id} 已开始")
    
    def complete_task(self, task_id):
        """完成任务"""
        if str(task_id) in self.tasks:
            self.tasks[str(task_id)]['status'] = 'completed'
            self.tasks[str(task_id)]['completed'] = datetime.now().isoformat()
            self.save_tasks()
            print(f"✓ 任务 #{task_id} 已完成")
    
    def list_tasks(self, status=None, version=None):
        """列出任务"""
        print("\n" + "="*70)
        print("📋 任务列表")
        print("="*70)
        
        for task_id, task in sorted(self.tasks.items(), key=lambda x: int(x[0])):
            if status and task['status'] != status:
                continue
            if version and task['version'] != version:
                continue
            
            status_icon = {
                'todo': '⭕',
                'in_progress': '🟠',
                'completed': '✅'
            }.get(task['status'], '❓')
            
            priority_icon = {
                'high': '🔴',
                'medium': '🟡',
                'low': '🟢'
            }.get(task['priority'], '⚪')
            
            print(f"\n#{task_id} {status_icon} {priority_icon} {task['name']} [{task['version']}]")
            print(f"   描述: {task['description']}")
            print(f"   创建: {task['created'][:10]}")
    
    def show_summary(self):
        """显示统计摘要"""
        total = len(self.tasks)
        completed = sum(1 for t in self.tasks.values() if t['status'] == 'completed')
        in_progress = sum(1 for t in self.tasks.values() if t['status'] == 'in_progress')
        todo = total - completed - in_progress
        
        print("\n" + "="*70)
        print("📊 任务统计")
        print("="*70)
        print(f"总任务数:    {total}")
        print(f"已完成:      {completed} ({completed*100//total if total else 0}%)")
        print(f"进行中:      {in_progress}")
        print(f"待做:        {todo}")
        
        # 按版本统计
        versions = {}
        for task in self.tasks.values():
            v = task['version']
            if v not in versions:
                versions[v] = {'total': 0, 'completed': 0}
            versions[v]['total'] += 1
            if task['status'] == 'completed':
                versions[v]['completed'] += 1
        
        print("\n版本进度:")
        for v in sorted(versions.keys()):
            c = versions[v]['completed']
            t = versions[v]['total']
            progress = c * 100 // t if t else 0
            bar = '█' * progress // 10 + '░' * (10 - progress // 10)
            print(f"  {v}: [{bar}] {c}/{t} ({progress}%)")
        
        print()


def print_menu():
    """打印菜单"""
    print("\n" + "="*70)
    print("🚀 优化任务跟踪工具")
    print("="*70)
    print("1. 列出所有任务")
    print("2. 列出待做任务")
    print("3. 列出进行中任务")
    print("4. 列出已完成任务")
    print("5. 添加新任务")
    print("6. 开始任务")
    print("7. 完成任务")
    print("8. 显示统计摘要")
    print("9. 初始化示例任务")
    print("0. 退出")
    print("="*70)


def init_sample_tasks(tracker):
    """初始化示例任务"""
    print("\n初始化示例任务...")
    
    # v1.1 任务
    tasks_v11 = [
        ("现代化UI设计", "采用现代扁平设计风格", "high", "v1.1"),
        ("主题支持", "实现浅色/深色主题切换", "high", "v1.1"),
        ("文件重命名", "添加文件重命名功能", "medium", "v1.1"),
        ("虚拟滚动", "优化大文件夹加载性能", "high", "v1.1"),
        ("搜索性能优化", "改进搜索响应速度", "medium", "v1.1"),
        ("单元测试", "添加核心功能测试", "high", "v1.1"),
    ]
    
    # v1.2 任务
    tasks_v12 = [
        ("文件预览", "实现图片和文本预览", "medium", "v1.2"),
        ("压缩支持", "添加压缩和解压支持", "medium", "v1.2"),
        ("快捷书签", "添加收藏和快速访问", "low", "v1.2"),
        ("操作历史", "记录和回溯操作", "low", "v1.2"),
    ]
    
    # v2.0 任务
    tasks_v20 = [
        ("网络支持", "支持网络文件夹访问", "high", "v2.0"),
        ("插件系统", "实现插件扩展机制", "medium", "v2.0"),
        ("云存储集成", "支持主流云存储", "low", "v2.0"),
    ]
    
    all_tasks = tasks_v11 + tasks_v12 + tasks_v20
    for name, desc, priority, version in all_tasks:
        tracker.add_task(name, desc, priority, version)
    
    print("✓ 示例任务初始化完成！")


def main():
    """主函数"""
    tracker = TaskTracker()
    
    while True:
        print_menu()
        choice = input("请选择操作 (0-9): ").strip()
        
        if choice == '0':
            print("👋 再见！")
            break
        
        elif choice == '1':
            tracker.list_tasks()
        
        elif choice == '2':
            tracker.list_tasks(status='todo')
        
        elif choice == '3':
            tracker.list_tasks(status='in_progress')
        
        elif choice == '4':
            tracker.list_tasks(status='completed')
        
        elif choice == '5':
            name = input("任务名称: ").strip()
            desc = input("任务描述: ").strip()
            priority = input("优先级 (high/medium/low) [medium]: ").strip() or "medium"
            version = input("版本 (v1.1/v1.2/v2.0) [v1.1]: ").strip() or "v1.1"
            tracker.add_task(name, desc, priority, version)
        
        elif choice == '6':
            try:
                task_id = int(input("任务ID: "))
                tracker.start_task(task_id)
            except ValueError:
                print("❌ 无效的任务ID")
        
        elif choice == '7':
            try:
                task_id = int(input("任务ID: "))
                tracker.complete_task(task_id)
            except ValueError:
                print("❌ 无效的任务ID")
        
        elif choice == '8':
            tracker.show_summary()
        
        elif choice == '9':
            init_sample_tasks(tracker)
        
        else:
            print("❌ 无效的选择")


if __name__ == '__main__':
    main()
