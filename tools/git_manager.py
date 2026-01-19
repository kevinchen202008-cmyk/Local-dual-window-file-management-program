#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Git 管理工具 - 简化Git操作
"""

import subprocess
import os
from pathlib import Path


def run_cmd(cmd, description=""):
    """运行命令"""
    print(f"\n$ {cmd}")
    if description:
        print(f"  ({description})")
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(f"错误: {result.stderr}")
        return result.returncode == 0
    except Exception as e:
        print(f"执行失败: {e}")
        return False


def print_menu():
    """打印菜单"""
    print("\n" + "="*70)
    print("🔧 Git 管理工具")
    print("="*70)
    print("分支管理:")
    print("  1. 创建功能分支")
    print("  2. 切换分支")
    print("  3. 列出分支")
    print("  4. 删除分支")
    print("\n提交操作:")
    print("  5. 查看状态")
    print("  6. 暂存所有文件")
    print("  7. 提交更改")
    print("  8. 推送到远程")
    print("\n日志和标签:")
    print("  9. 查看提交日志")
    print(" 10. 创建标签")
    print(" 11. 查看标签")
    print("\n高级操作:")
    print(" 12. 合并分支")
    print(" 13. 变基分支")
    print(" 14. 撤销提交")
    print(" 15. 清理分支")
    print("\n快捷操作:")
    print(" 20. 完整提交流程 (add → commit → push)")
    print(" 21. 功能完成流程 (merge → tag → clean)")
    print(" 22. 显示仓库信息")
    print("\n  0. 退出")
    print("="*70)


def git_status():
    """显示状态"""
    run_cmd("git status", "显示仓库状态")


def git_log():
    """显示日志"""
    run_cmd("git log --oneline -15 --decorate", "显示最近15条提交")


def git_branch():
    """列出分支"""
    run_cmd("git branch -vv", "列出所有分支")


def create_feature_branch():
    """创建功能分支"""
    feature_name = input("功能名称 (如: file-preview): ").strip()
    if feature_name:
        cmd = f"git checkout -b feature/{feature_name}"
        if run_cmd(cmd, f"创建功能分支 feature/{feature_name}"):
            print(f"✓ 分支 feature/{feature_name} 已创建")


def switch_branch():
    """切换分支"""
    branch = input("分支名称: ").strip()
    if branch:
        run_cmd(f"git checkout {branch}", f"切换到分支 {branch}")


def delete_branch():
    """删除分支"""
    branch = input("分支名称: ").strip()
    if branch:
        force = input("强制删除? (y/n): ").lower() == 'y'
        flag = "-D" if force else "-d"
        run_cmd(f"git branch {flag} {branch}", f"删除分支 {branch}")


def stage_all():
    """暂存所有文件"""
    run_cmd("git add -A", "暂存所有修改")


def commit_changes():
    """提交更改"""
    print("\n提交类型: feat, fix, docs, style, refactor, perf, test, chore")
    scope = input("作用域 (如: ui, core, search): ").strip()
    msg_type = input("类型: ").strip()
    msg = input("消息: ").strip()
    
    if msg_type and msg:
        commit_msg = f"{msg_type}({scope}): {msg}" if scope else f"{msg_type}: {msg}"
        run_cmd(f'git commit -m "{commit_msg}"', "提交更改")


def push_changes():
    """推送到远程"""
    branch = input("分支名称 (默认: 当前分支): ").strip()
    if branch:
        run_cmd(f"git push origin {branch}", f"推送到远程 {branch}")
    else:
        run_cmd("git push", "推送到远程")


def create_tag():
    """创建标签"""
    tag = input("标签名称 (如: v1.1.0): ").strip()
    msg = input("标签消息: ").strip()
    
    if tag:
        if msg:
            run_cmd(f'git tag -a {tag} -m "{msg}"', f"创建带消息的标签 {tag}")
        else:
            run_cmd(f"git tag {tag}", f"创建轻量级标签 {tag}")
        
        push = input("推送标签到远程? (y/n): ").lower() == 'y'
        if push:
            run_cmd(f"git push origin {tag}", f"推送标签 {tag}")


def merge_branch():
    """合并分支"""
    print("当前分支信息:")
    run_cmd("git branch -vv | grep '*'", "显示当前分支")
    
    branch = input("要合并的分支: ").strip()
    if branch:
        run_cmd(f"git merge {branch}", f"合并分支 {branch}")


def rebase_branch():
    """变基分支"""
    branch = input("基分支: ").strip()
    if branch:
        run_cmd(f"git rebase {branch}", f"变基到 {branch}")


def undo_commit():
    """撤销提交"""
    print("1. 撤销最后一次提交（保留更改）")
    print("2. 撤销最后一次提交（丢弃更改）")
    choice = input("选择: ").strip()
    
    if choice == '1':
        run_cmd("git reset --soft HEAD~1", "撤销提交（保留更改）")
    elif choice == '2':
        run_cmd("git reset --hard HEAD~1", "撤销提交（丢弃更改）")


def cleanup_branches():
    """清理分支"""
    print("1. 删除本地已合并的分支")
    print("2. 删除远程已删除的本地跟踪")
    print("3. 清理所有已合并的分支")
    choice = input("选择: ").strip()
    
    if choice == '1':
        run_cmd("git branch --merged | grep -v '^*' | xargs -r git branch -d", 
               "删除本地已合并的分支")
    elif choice == '2':
        run_cmd("git fetch -p", "删除远程已删除的跟踪")
    elif choice == '3':
        run_cmd("git branch -vv | grep gone | awk '{print $1}' | xargs -r git branch -d",
               "清理所有已删除的分支")


def show_repo_info():
    """显示仓库信息"""
    print("\n" + "="*70)
    print("📊 仓库信息")
    print("="*70)
    
    run_cmd("git config --local --get user.name", "用户名")
    run_cmd("git config --local --get user.email", "邮箱")
    run_cmd("git rev-parse --git-dir", "仓库目录")
    run_cmd("git rev-parse --show-toplevel", "工作目录")
    
    print("\n分支信息:")
    run_cmd("git branch -vv", "本地分支")
    
    print("\n标签信息:")
    run_cmd("git tag -l | head -10", "最近的标签")
    
    print("\n提交统计:")
    run_cmd("git rev-list --count HEAD", "总提交数")


def complete_commit_flow():
    """完整提交流程"""
    print("\n完整提交流程: add → commit → push")
    print("="*70)
    
    run_cmd("git status", "1. 显示状态")
    
    input("\n按 Enter 暂存所有文件...")
    run_cmd("git add -A", "2. 暂存文件")
    
    print("\n提交类型: feat, fix, docs, style, refactor, perf, test, chore")
    msg_type = input("类型: ").strip()
    scope = input("作用域 (可选): ").strip()
    msg = input("消息: ").strip()
    
    if msg:
        commit_msg = f"{msg_type}({scope}): {msg}" if scope else f"{msg_type}: {msg}"
        run_cmd(f'git commit -m "{commit_msg}"', "3. 提交更改")
        
        if input("\n推送到远程? (y/n): ").lower() == 'y':
            run_cmd("git push", "4. 推送到远程")


def complete_feature_flow():
    """功能完成流程"""
    print("\n功能完成流程: merge → tag → clean")
    print("="*70)
    
    print("\n当前分支:")
    run_cmd("git branch -vv | grep '*'", "显示当前分支")
    
    if input("\n切换到develop分支? (y/n): ").lower() == 'y':
        run_cmd("git checkout develop", "切换分支")
        run_cmd("git pull origin develop", "更新develop")
        
        feature = input("功能分支名称: ").strip()
        if feature:
            run_cmd(f"git merge feature/{feature}", f"合并 {feature}")
            
            version = input("版本号 (如: v1.1.0): ").strip()
            if version:
                run_cmd(f'git tag -a {version} -m "Release {version}"', 
                       f"创建标签 {version}")
                
                if input("推送到远程? (y/n): ").lower() == 'y':
                    run_cmd("git push origin develop", "推送develop")
                    run_cmd(f"git push origin {version}", "推送标签")
            
            if input("\n删除功能分支? (y/n): ").lower() == 'y':
                run_cmd(f"git branch -d feature/{feature}", f"删除 feature/{feature}")


def main():
    """主函数"""
    print("欢迎使用 Git 管理工具！")
    
    while True:
        print_menu()
        choice = input("请选择操作: ").strip()
        
        if choice == '0':
            print("👋 再见！")
            break
        elif choice == '1':
            create_feature_branch()
        elif choice == '2':
            switch_branch()
        elif choice == '3':
            git_branch()
        elif choice == '4':
            delete_branch()
        elif choice == '5':
            git_status()
        elif choice == '6':
            stage_all()
        elif choice == '7':
            commit_changes()
        elif choice == '8':
            push_changes()
        elif choice == '9':
            git_log()
        elif choice == '10':
            create_tag()
        elif choice == '11':
            run_cmd("git tag -l", "列出所有标签")
        elif choice == '12':
            merge_branch()
        elif choice == '13':
            rebase_branch()
        elif choice == '14':
            undo_commit()
        elif choice == '15':
            cleanup_branches()
        elif choice == '20':
            complete_commit_flow()
        elif choice == '21':
            complete_feature_flow()
        elif choice == '22':
            show_repo_info()
        else:
            print("❌ 无效选择")


if __name__ == '__main__':
    main()
