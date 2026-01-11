#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
本地版本控制管理系统 - 在没有Git的环境中使用
支持: 分支管理, 提交追踪, 版本标记, 变更日志
"""

import os
import json
import shutil
from datetime import datetime
from pathlib import Path
import hashlib


class LocalVCS:
    """本地版本控制系统"""
    
    def __init__(self, project_dir="."):
        self.project_dir = Path(project_dir)
        self.vcs_dir = self.project_dir / ".local_vcs"
        self.branches_dir = self.vcs_dir / "branches"
        self.commits_dir = self.vcs_dir / "commits"
        self.tags_dir = self.vcs_dir / "tags"
        self.config_file = self.vcs_dir / "config.json"
        
        self._init_vcs()
    
    def _init_vcs(self):
        """初始化VCS目录结构"""
        self.vcs_dir.mkdir(exist_ok=True)
        self.branches_dir.mkdir(exist_ok=True)
        self.commits_dir.mkdir(exist_ok=True)
        self.tags_dir.mkdir(exist_ok=True)
        
        if not self.config_file.exists():
            self._write_config({
                "initialized": datetime.now().isoformat(),
                "current_branch": "main",
                "branches": {
                    "main": {
                        "created": datetime.now().isoformat(),
                        "head_commit": None,
                        "description": "主分支"
                    }
                },
                "user_name": "File Manager Developer",
                "user_email": "dev@filemanager.local"
            })
    
    def _read_config(self):
        """读取配置"""
        if self.config_file.exists():
            with open(self.config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}
    
    def _write_config(self, config):
        """写入配置"""
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
    
    def _file_hash(self, filepath):
        """计算文件哈希"""
        sha256_hash = hashlib.sha256()
        with open(filepath, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()[:8]
    
    def create_branch(self, branch_name, description=""):
        """创建新分支"""
        config = self._read_config()
        
        if branch_name in config["branches"]:
            return False, f"分支 {branch_name} 已存在"
        
        current_head = config["branches"][config["current_branch"]]["head_commit"]
        
        config["branches"][branch_name] = {
            "created": datetime.now().isoformat(),
            "head_commit": current_head,
            "description": description or f"从 {config['current_branch']} 创建",
            "created_from": config["current_branch"]
        }
        
        self._write_config(config)
        return True, f"✓ 分支 {branch_name} 已创建"
    
    def switch_branch(self, branch_name):
        """切换分支"""
        config = self._read_config()
        
        if branch_name not in config["branches"]:
            return False, f"分支 {branch_name} 不存在"
        
        config["current_branch"] = branch_name
        self._write_config(config)
        return True, f"✓ 已切换到分支 {branch_name}"
    
    def commit(self, message, scope="general"):
        """创建提交"""
        config = self._read_config()
        current_branch = config["current_branch"]
        
        # 计算项目状态哈希
        project_files = [f for f in self.project_dir.rglob("*") if f.is_file() and ".local_vcs" not in str(f)]
        content_hash = hashlib.sha256()
        for f in sorted(project_files):
            try:
                content_hash.update(self._file_hash(f).encode())
            except:
                pass
        
        commit_id = content_hash.hexdigest()[:12]
        commit_time = datetime.now().isoformat()
        
        commit_data = {
            "id": commit_id,
            "message": message,
            "scope": scope,
            "timestamp": commit_time,
            "author": config["user_name"],
            "email": config["user_email"],
            "branch": current_branch,
            "parent_commit": config["branches"][current_branch]["head_commit"],
            "file_count": len(project_files)
        }
        
        commit_file = self.commits_dir / f"{commit_id}.json"
        with open(commit_file, 'w', encoding='utf-8') as f:
            json.dump(commit_data, f, indent=2, ensure_ascii=False)
        
        config["branches"][current_branch]["head_commit"] = commit_id
        self._write_config(config)
        
        return True, f"✓ 提交成功: {commit_id}\n  分支: {current_branch}\n  消息: {message}"
    
    def create_tag(self, tag_name, message=""):
        """创建标签"""
        config = self._read_config()
        current_branch = config["current_branch"]
        commit_id = config["branches"][current_branch]["head_commit"]
        
        if not commit_id:
            return False, "当前分支没有提交"
        
        tag_data = {
            "name": tag_name,
            "commit_id": commit_id,
            "message": message,
            "created": datetime.now().isoformat(),
            "branch": current_branch
        }
        
        tag_file = self.tags_dir / f"{tag_name}.json"
        with open(tag_file, 'w', encoding='utf-8') as f:
            json.dump(tag_data, f, indent=2, ensure_ascii=False)
        
        return True, f"✓ 标签 {tag_name} 已创建"
    
    def get_log(self, limit=10):
        """获取提交日志"""
        config = self._read_config()
        current_branch = config["current_branch"]
        current_commit = config["branches"][current_branch]["head_commit"]
        
        log = []
        visited = set()
        
        while current_commit and len(log) < limit:
            if current_commit in visited:
                break
            visited.add(current_commit)
            
            commit_file = self.commits_dir / f"{current_commit}.json"
            if commit_file.exists():
                with open(commit_file, 'r', encoding='utf-8') as f:
                    commit_data = json.load(f)
                    log.append(commit_data)
                    current_commit = commit_data.get("parent_commit")
            else:
                break
        
        return log
    
    def list_branches(self):
        """列出所有分支"""
        config = self._read_config()
        current = config["current_branch"]
        
        branches = []
        for name, info in config["branches"].items():
            is_current = "* " if name == current else "  "
            commit = info["head_commit"][:8] if info["head_commit"] else "未提交"
            branches.append(f"{is_current}{name:<20} {commit}")
        
        return branches
    
    def merge_branch(self, source_branch):
        """合并分支"""
        config = self._read_config()
        current_branch = config["current_branch"]
        
        if current_branch == source_branch:
            return False, "无法将分支合并到自己"
        
        if source_branch not in config["branches"]:
            return False, f"分支 {source_branch} 不存在"
        
        source_commit = config["branches"][source_branch]["head_commit"]
        if not source_commit:
            return False, f"分支 {source_branch} 没有提交"
        
        config["branches"][current_branch]["head_commit"] = source_commit
        self._write_config(config)
        
        return True, f"✓ 已将 {source_branch} 合并到 {current_branch}"
    
    def get_status(self):
        """获取状态"""
        config = self._read_config()
        current = config["current_branch"]
        commit = config["branches"][current].get("head_commit")
        
        return {
            "current_branch": current,
            "head_commit": commit[:8] if commit else "未提交",
            "user_name": config["user_name"],
            "user_email": config["user_email"],
            "total_branches": len(config["branches"]),
            "total_commits": len(list(self.commits_dir.glob("*.json")))
        }


def print_menu():
    """打印菜单"""
    print("\n" + "="*70)
    print("📦 本地版本控制管理系统 (Local VCS)")
    print("="*70)
    print("\n分支管理:")
    print("  1. 创建分支")
    print("  2. 切换分支")
    print("  3. 列出分支")
    print("\n提交操作:")
    print("  4. 创建提交")
    print("  5. 查看日志")
    print("  6. 获取状态")
    print("\n标签和合并:")
    print("  7. 创建标签")
    print("  8. 合并分支")
    print("\n工具:")
    print("  9. 显示仓库信息")
    print(" 10. 初始化演示数据")
    print("\n  0. 退出")
    print("="*70)


def main():
    """主函数"""
    vcs = LocalVCS()
    
    print("欢迎使用本地版本控制管理系统！")
    print(f"项目目录: {vcs.project_dir.absolute()}")
    
    while True:
        print_menu()
        choice = input("\n请选择操作: ").strip()
        
        if choice == '0':
            print("👋 再见！")
            break
        elif choice == '1':
            name = input("分支名称: ").strip()
            desc = input("描述 (可选): ").strip()
            success, msg = vcs.create_branch(name, desc)
            print(msg)
        elif choice == '2':
            name = input("分支名称: ").strip()
            success, msg = vcs.switch_branch(name)
            print(msg)
        elif choice == '3':
            branches = vcs.list_branches()
            print("\n分支列表:")
            for b in branches:
                print(f"  {b}")
        elif choice == '4':
            msg = input("提交消息: ").strip()
            scope = input("作用域 (默认: general): ").strip() or "general"
            success, result = vcs.commit(msg, scope)
            print(result)
        elif choice == '5':
            log = vcs.get_log()
            print("\n提交日志:")
            for commit in log:
                print(f"  {commit['id'][:8]} - {commit['message']}")
                print(f"    作者: {commit['author']}")
                print(f"    时间: {commit['timestamp'][:10]}")
        elif choice == '6':
            status = vcs.get_status()
            print("\n仓库状态:")
            print(f"  当前分支: {status['current_branch']}")
            print(f"  HEAD: {status['head_commit']}")
            print(f"  分支数: {status['total_branches']}")
            print(f"  提交数: {status['total_commits']}")
        elif choice == '7':
            tag = input("标签名称 (如: v1.1.0): ").strip()
            msg = input("标签消息: ").strip()
            success, result = vcs.create_tag(tag, msg)
            print(result)
        elif choice == '8':
            branches = vcs.list_branches()
            print("\n可用分支:")
            for b in branches:
                print(f"  {b}")
            source = input("源分支: ").strip()
            success, result = vcs.merge_branch(source)
            print(result)
        elif choice == '9':
            status = vcs.get_status()
            print("\n📊 仓库信息:")
            for key, value in status.items():
                print(f"  {key}: {value}")
        elif choice == '10':
            print("初始化演示数据...")
            vcs.commit("Initial commit: File Manager v1.0 - Complete implementation", "core")
            vcs.create_branch("develop")
            vcs.create_branch("feature/ui-modernization", "UI modernization feature")
            vcs.create_tag("v1.0.0", "Release version 1.0.0")
            print("✓ 演示数据已初始化")
        else:
            print("❌ 无效选择")


if __name__ == '__main__':
    main()
