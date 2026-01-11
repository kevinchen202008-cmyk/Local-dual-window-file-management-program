#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
版本管理和发布工具
用于管理项目版本和发布流程
"""

import os
import json
from pathlib import Path
from datetime import datetime
import subprocess


class VersionManager:
    """版本管理器"""
    
    def __init__(self):
        self.version_file = Path('VERSION')
        self.changelog_file = Path('CHANGELOG.md')
        self.current_version = self.load_version()
    
    def load_version(self):
        """加载当前版本"""
        if self.version_file.exists():
            return self.version_file.read_text().strip()
        return "1.0.0"
    
    def save_version(self, version):
        """保存版本"""
        self.version_file.write_text(version)
        self.current_version = version
    
    def parse_version(self, version_str):
        """解析版本号"""
        parts = version_str.split('.')
        return {
            'major': int(parts[0]),
            'minor': int(parts[1]) if len(parts) > 1 else 0,
            'patch': int(parts[2]) if len(parts) > 2 else 0
        }
    
    def format_version(self, major, minor, patch):
        """格式化版本号"""
        return f"{major}.{minor}.{patch}"
    
    def bump_major(self):
        """升级主版本"""
        v = self.parse_version(self.current_version)
        new_version = self.format_version(v['major'] + 1, 0, 0)
        self.save_version(new_version)
        print(f"✓ 版本升级: {self.current_version} → {new_version}")
        return new_version
    
    def bump_minor(self):
        """升级次版本"""
        v = self.parse_version(self.current_version)
        new_version = self.format_version(v['major'], v['minor'] + 1, 0)
        self.save_version(new_version)
        print(f"✓ 版本升级: {self.current_version} → {new_version}")
        return new_version
    
    def bump_patch(self):
        """升级修订版本"""
        v = self.parse_version(self.current_version)
        new_version = self.format_version(v['major'], v['minor'], v['patch'] + 1)
        self.save_version(new_version)
        print(f"✓ 版本升级: {self.current_version} → {new_version}")
        return new_version
    
    def create_tag(self, version=None):
        """创建Git标签"""
        version = version or self.current_version
        tag = f"v{version}"
        
        try:
            subprocess.run(['git', 'tag', '-a', tag, '-m', f'Release {tag}'], check=True)
            print(f"✓ Git标签创建: {tag}")
            return tag
        except subprocess.CalledProcessError:
            print(f"✗ Git标签创建失败: {tag}")
            return None
    
    def add_changelog_entry(self, version, changes):
        """添加更新日志条目"""
        timestamp = datetime.now().strftime('%Y-%m-%d')
        
        entry = f"""## [{version}] - {timestamp}

### Added
{self._format_changes(changes.get('added', []))}

### Changed
{self._format_changes(changes.get('changed', []))}

### Fixed
{self._format_changes(changes.get('fixed', []))}

### Removed
{self._format_changes(changes.get('removed', []))}

---

"""
        
        if self.changelog_file.exists():
            content = self.changelog_file.read_text()
            self.changelog_file.write_text(entry + content)
        else:
            header = """# Changelog

All notable changes to this project will be documented in this file.

"""
            self.changelog_file.write_text(header + entry)
        
        print(f"✓ 更新日志已更新")
    
    @staticmethod
    def _format_changes(changes):
        """格式化更改列表"""
        if not changes:
            return "- No changes\n"
        return "\n".join(f"- {change}" for change in changes) + "\n"
    
    def show_version_info(self):
        """显示版本信息"""
        print("\n" + "="*70)
        print("📦 版本管理")
        print("="*70)
        print(f"当前版本: {self.current_version}")
        print(f"版本文件: {self.version_file}")
        print(f"更新日志: {self.changelog_file}")
        print()


def print_menu():
    """打印菜单"""
    print("\n" + "="*70)
    print("🚀 版本管理工具")
    print("="*70)
    print("1. 显示当前版本")
    print("2. 升级主版本 (major)")
    print("3. 升级次版本 (minor)")
    print("4. 升级修订版本 (patch)")
    print("5. 创建发布标签")
    print("6. 添加更新日志")
    print("7. 查看更新日志")
    print("0. 返回")
    print("="*70)


def main():
    """主函数"""
    manager = VersionManager()
    
    while True:
        print_menu()
        choice = input("请选择操作 (0-7): ").strip()
        
        if choice == '0':
            break
        
        elif choice == '1':
            manager.show_version_info()
        
        elif choice == '2':
            manager.bump_major()
        
        elif choice == '3':
            manager.bump_minor()
        
        elif choice == '4':
            manager.bump_patch()
        
        elif choice == '5':
            manager.create_tag()
        
        elif choice == '6':
            print("\n添加更新日志")
            version = input("版本号 [{}]: ".format(manager.current_version)).strip() or manager.current_version
            
            added = input("Added (用逗号分隔): ").strip().split(',') if input("有新增功能吗? (y/n): ").lower() == 'y' else []
            changed = input("Changed (用逗号分隔): ").strip().split(',') if input("有改变吗? (y/n): ").lower() == 'y' else []
            fixed = input("Fixed (用逗号分隔): ").strip().split(',') if input("有修复吗? (y/n): ").lower() == 'y' else []
            removed = input("Removed (用逗号分隔): ").strip().split(',') if input("有移除吗? (y/n): ").lower() == 'y' else []
            
            changes = {
                'added': [x.strip() for x in added if x.strip()],
                'changed': [x.strip() for x in changed if x.strip()],
                'fixed': [x.strip() for x in fixed if x.strip()],
                'removed': [x.strip() for x in removed if x.strip()],
            }
            
            manager.add_changelog_entry(version, changes)
        
        elif choice == '7':
            if manager.changelog_file.exists():
                print("\n" + manager.changelog_file.read_text())
            else:
                print("更新日志文件不存在")


if __name__ == '__main__':
    main()
