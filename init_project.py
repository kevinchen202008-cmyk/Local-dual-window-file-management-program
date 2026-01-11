#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
项目初始化脚本 - 自动设置本地版本控制和优化计划
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from local_vcs import LocalVCS
from optimize_tasks import TaskTracker


def init_vcs():
    """初始化本地版本控制"""
    print("\n" + "="*70)
    print("初始化本地版本控制系统...")
    print("="*70)
    
    vcs = LocalVCS()
    
    # 创建初始提交
    success, msg = vcs.commit("Initial commit: File Manager v1.0", "core")
    print(f"✓ {msg}")
    
    # 创建开发分支
    success, msg = vcs.create_branch("develop", "Development branch")
    print(f"✓ {msg}")
    
    # 创建功能分支
    branches = [
        ("feature/ui-modernization", "UI modernization and flat design"),
        ("feature/performance-optimization", "Performance optimization features"),
        ("feature/shortcuts", "Keyboard shortcuts support"),
        ("feature/themes", "Light/dark theme support"),
        ("hotfix/bugs", "Bug fixes")
    ]
    
    for branch_name, description in branches:
        success, msg = vcs.create_branch(branch_name, description)
        print(f"✓ {msg}")
    
    # 创建标签
    success, msg = vcs.create_tag("v1.0.0", "Release v1.0.0 - Initial production release")
    print(f"✓ {msg}")
    
    # 显示状态
    status = vcs.get_status()
    print("\n仓库状态:")
    print(f"  分支数: {status['total_branches']}")
    print(f"  提交数: {status['total_commits']}")
    print(f"  当前分支: {status['current_branch']}")
    
    return vcs


def init_optimization():
    """初始化优化计划"""
    print("\n" + "="*70)
    print("初始化优化计划...")
    print("="*70)
    
    tm = TaskTracker()
    
    # 定义优化任务
    tasks = [
        # v1.1 任务 (2个月)
        ("UI modern design", "实现扁平设计和现代UI", "high", "v1.1.0"),
        ("Light/Dark theme", "添加亮色和暗色主题支持", "high", "v1.1.0"),
        ("Icon improvements", "改进和替换图标集", "medium", "v1.1.0"),
        
        # v1.2 任务 (3个月)
        ("Virtual scrolling", "为大型目录实现虚拟滚动", "high", "v1.2.0"),
        ("Search optimization", "优化搜索算法和索引", "high", "v1.2.0"),
        ("Keyboard shortcuts", "实现全面的键盘快捷键支持", "medium", "v1.2.0"),
        
        # v2.0 任务 (6个月)
        ("Network support", "添加网络文件浏览支持", "high", "v2.0.0"),
        ("Advanced search", "实现高级搜索过滤器", "medium", "v2.0.0"),
        ("Plugin system", "添加插件系统支持", "medium", "v2.0.0")
    ]
    
    # 添加任务
    for title, desc, priority, version in tasks:
        tm.add_task(title, desc, priority, version)
    
    # 显示任务统计
    print("\n任务列表:")
    tm.list_tasks()
    
    return tm


def create_git_hook():
    """创建预提交钩子"""
    print("\n" + "="*70)
    print("创建Git钩子...")
    print("="*70)
    
    hook_content = """#!/bin/bash
# Pre-commit hook for code quality checks

echo "Running pre-commit checks..."

# Check Python syntax
for file in $(git diff --cached --name-only | grep '\\.py$'); do
    python -m py_compile "$file" || exit 1
done

echo "✓ All checks passed"
exit 0
"""
    
    hooks_dir = os.path.join(".local_vcs", "hooks")
    os.makedirs(hooks_dir, exist_ok=True)
    
    hook_file = os.path.join(hooks_dir, "pre-commit")
    with open(hook_file, 'w') as f:
        f.write(hook_content)
    
    print(f"✓ 预提交钩子已创建: {hook_file}")


def print_summary():
    """打印总结"""
    print("\n" + "="*70)
    print("项目初始化完成！")
    print("="*70)
    
    print("\n📋 已完成的操作:")
    print("  ✓ 本地版本控制系统初始化")
    print("    - main 分支 (主分支)")
    print("    - develop 分支 (开发分支)")
    print("    - 5 个功能分支")
    print("    - v1.0.0 标签")
    
    print("\n  ✓ 优化任务计划")
    print("    - v1.1.0: 3 个任务 (UI现代化)")
    print("    - v1.2.0: 3 个任务 (性能优化)")
    print("    - v2.0.0: 3 个任务 (功能扩展)")
    
    print("\n🚀 后续步骤:")
    print("  1. 启动任务跟踪: python optimize_tasks.py")
    print("  2. 管理版本控制: python local_vcs.py")
    print("  3. 查看优化计划: cat OPTIMIZATION_PLAN.md")
    print("  4. 开始v1.1开发: python local_vcs.py → 切换到 feature/ui-modernization")
    
    print("\n📁 项目文件:")
    print("  - local_vcs.py: 本地版本控制管理")
    print("  - optimize_tasks.py: 任务跟踪管理")
    print("  - git_manager.py: Git操作助手")
    print("  - .local_vcs/: 版本控制数据目录")
    
    print("\n" + "="*70)


if __name__ == '__main__':
    print("\n" + "="*70)
    print("📦 项目初始化脚本")
    print("="*70)
    
    try:
        # 初始化版本控制
        vcs = init_vcs()
        
        # 初始化优化任务
        tm = init_optimization()
        
        # 创建钩子
        create_git_hook()
        
        # 显示总结
        print_summary()
        
    except Exception as e:
        print(f"\n❌ 初始化失败: {e}")
        sys.exit(1)
