"""
菜单栏创建函数
"""

from PyQt5.QtWidgets import QMenuBar, QMessageBox
from PyQt5.QtGui import QKeySequence


def create_menu_bar(main_window):
    """创建菜单栏"""
    menubar = QMenuBar(main_window)
    
    # 文件菜单
    file_menu = menubar.addMenu("文件(&F)")
    
    open_action = file_menu.addAction("打开")
    open_action.setShortcut(QKeySequence.Open)
    open_action.triggered.connect(lambda: on_open_file(main_window))
    
    file_menu.addSeparator()
    
    exit_action = file_menu.addAction("退出(&X)")
    exit_action.setShortcut(QKeySequence.Quit)
    exit_action.triggered.connect(main_window.close)
    
    # 编辑菜单
    edit_menu = menubar.addMenu("编辑(&E)")
    
    copy_action = edit_menu.addAction("复制(&C)")
    copy_action.setShortcut(QKeySequence.Copy)
    copy_action.triggered.connect(main_window.copy_files)
    
    cut_action = edit_menu.addAction("剪切(&X)")
    cut_action.setShortcut(QKeySequence.Cut)
    cut_action.triggered.connect(main_window.move_files)
    
    delete_action = edit_menu.addAction("删除(&D)")
    delete_action.setShortcut(QKeySequence.Delete)
    delete_action.triggered.connect(main_window.delete_files)
    
    edit_menu.addSeparator()
    
    refresh_action = edit_menu.addAction("刷新(&R)")
    refresh_action.setShortcut(QKeySequence.Refresh)
    refresh_action.triggered.connect(main_window.refresh_panels)
    
    # 查看菜单
    view_menu = menubar.addMenu("查看(&V)")
    
    up_action = view_menu.addAction("返回上级目录")
    up_action.setShortcut("Backspace")
    up_action.triggered.connect(main_window.go_up)
    
    view_menu.addSeparator()
    
    sync_action = view_menu.addAction("同步路径")
    sync_action.triggered.connect(main_window.sync_paths)
    
    # 工具菜单
    tools_menu = menubar.addMenu("工具(&T)")
    
    search_action = tools_menu.addAction("搜索文件")
    search_action.setShortcut("Ctrl+F")
    search_action.triggered.connect(lambda: on_search(main_window))
    
    settings_action = tools_menu.addAction("设置")
    settings_action.triggered.connect(lambda: on_settings(main_window))
    
    # 帮助菜单
    help_menu = menubar.addMenu("帮助(&H)")
    
    about_action = help_menu.addAction("关于")
    about_action.triggered.connect(lambda: on_about(main_window))
    
    return menubar


def on_open_file(main_window):
    """打开文件"""
    focused = main_window.get_focused_panel()
    if focused:
        focused.browse_folder()


def on_search(main_window):
    """打开搜索对话框"""
    from .search_dialog import SearchDialog
    
    focused = main_window.get_focused_panel()
    root_path = focused.current_path if focused else None
    
    search_dialog = SearchDialog(main_window, root_path)
    search_dialog.exec_()


def on_settings(main_window):
    """打开设置"""
    QMessageBox.information(
        main_window,
        "设置",
        "设置功能开发中...\n\n当前支持的功能:\n"
        "- 双窗口文件浏览\n"
        "- 文件复制/移动/删除\n"
        "- 文件搜索\n"
        "- 快捷键操作\n"
        "- 配置自动保存"
    )


def on_about(main_window):
    """关于"""
    QMessageBox.about(
        main_window,
        "关于文件管理器",
        "文件管理器 v1.0\n\n"
        "一个功能完整的本地双窗口文件管理程序\n"
        "类似于 FreeCommander\n\n"
        "功能特性:\n"
        "• 双窗口对比浏览\n"
        "• 文件复制、移动、删除\n"
        "• 快速导航\n"
        "• 文件属性查看\n"
        "• 文件搜索\n"
        "• 配置自动保存\n\n"
        "© 2026 All Rights Reserved"
    )
