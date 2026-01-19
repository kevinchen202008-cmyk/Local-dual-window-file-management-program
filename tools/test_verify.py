"""
程序测试和验证脚本
"""

import sys
import os
from pathlib import Path

# 添加项目根目录到路径（tools目录的父目录）
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# 设置控制台编码为UTF-8（Windows）
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# 检测虚拟环境
def check_venv():
    """检测是否在虚拟环境中运行"""
    in_venv = (
        hasattr(sys, 'real_prefix') or
        (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix)
    )
    if not in_venv:
        venv_path = project_root / '.venv'
        if venv_path.exists():
            print("[提示] 建议在虚拟环境中运行此脚本:")
            print(f"      Windows: .venv\\Scripts\\python.exe {__file__}")
            print(f"      Linux/Mac: source .venv/bin/activate && python {__file__}")
            print()
    return in_venv

def test_imports():
    """测试导入"""
    print("测试导入模块...")
    try:
        from ui.main_window import MainWindow
        from ui.file_panel import FilePanel
        from ui.menu_bar import create_menu_bar
        from ui.config import ConfigManager
        from ui.search import FileSearcher
        print("[OK] 所有模块导入成功")
        return True
    except ImportError as e:
        print(f"[FAIL] 导入失败: {e}")
        return False

def test_config_manager():
    """测试配置管理器"""
    print("\n测试配置管理器...")
    try:
        from ui.config import ConfigManager
        config = ConfigManager()
        
        # 测试获取配置
        left_path = config.get('left_panel_path')
        print(f"[OK] 获取配置成功: {left_path}")
        
        # 测试设置配置
        config.set('test_key', 'test_value')
        test_val = config.get('test_key')
        assert test_val == 'test_value'
        print("[OK] 配置设置成功")
        
        return True
    except Exception as e:
        print(f"[FAIL] 配置测试失败: {e}")
        return False

def test_file_searcher():
    """测试文件搜索"""
    print("\n测试文件搜索...")
    try:
        from ui.search import FileSearcher
        searcher = FileSearcher(str(Path.home()))
        
        # 测试搜索
        results = searcher.search_by_name("*.txt", include_dirs=False)
        print(f"[OK] 搜索成功，找到 {len(results)} 个 .txt 文件")
        
        return True
    except Exception as e:
        print(f"[FAIL] 搜索测试失败: {e}")
        return False

def test_file_operations():
    """测试文件操作"""
    print("\n测试文件操作工具...")
    try:
        from ui.file_operations import FileOperationManager
        
        # 测试文件大小格式化
        size_str = FileOperationManager.format_size(1024 * 1024)
        assert "MB" in size_str
        print(f"[OK] 文件大小格式化: {size_str}")
        
        # 测试获取文件信息
        info = FileOperationManager.get_file_info(__file__)
        assert info is not None
        print(f"[OK] 获取文件信息成功")
        
        return True
    except Exception as e:
        print(f"[FAIL] 文件操作测试失败: {e}")
        return False

def test_dependencies():
    """测试依赖安装"""
    print("\n测试依赖...")
    required = ['PyQt5']
    missing = []
    
    for package in required:
        try:
            __import__(package)
            print(f"[OK] {package} 已安装")
        except ImportError:
            missing.append(package)
            print(f"[FAIL] {package} 未安装")
    
    if missing:
        print(f"\n需要安装缺失的包:")
        print(f"  pip install {' '.join(missing)}")
        return False
    
    return True

def main():
    """运行所有测试"""
    print("="*50)
    print("文件管理器 - 程序验证")
    print("="*50)
    
    # 检查虚拟环境
    check_venv()
    
    tests = [
        ("依赖检查", test_dependencies),
        ("模块导入", test_imports),
        ("配置管理器", test_config_manager),
        ("文件搜索", test_file_searcher),
        ("文件操作工具", test_file_operations),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n[FAIL] {test_name} 出错: {e}")
            results.append((test_name, False))
    
    # 总结
    print("\n" + "="*50)
    print("测试总结")
    print("="*50)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "[PASS]" if result else "[FAIL]"
        print(f"{status:8} - {test_name}")
    
    print("-"*50)
    print(f"总计: {passed}/{total} 测试通过")
    print("="*50)
    
    if passed == total:
        print("\n[OK] 所有测试通过！程序已准备就绪。")
        return 0
    else:
        print(f"\n[FAIL] 有 {total - passed} 个测试失败。")
        return 1

if __name__ == '__main__':
    sys.exit(main())
