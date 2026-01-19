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
    
    new_folder_action = edit_menu.addAction("新建文件夹")
    new_folder_action.setShortcut("Ctrl+Shift+N")
    new_folder_action.triggered.connect(lambda: on_new_folder(main_window))
    
    new_file_action = edit_menu.addAction("新建文件")
    new_file_action.setShortcut("Ctrl+N")
    new_file_action.triggered.connect(lambda: on_new_file(main_window))
    
    edit_menu.addSeparator()
    
    undo_action = edit_menu.addAction("撤销(&U)")
    undo_action.setShortcut(QKeySequence.Undo)
    undo_action.triggered.connect(lambda: on_undo(main_window))
    
    redo_action = edit_menu.addAction("重做(&R)")
    redo_action.setShortcut(QKeySequence.Redo)
    redo_action.triggered.connect(lambda: on_redo(main_window))
    
    edit_menu.addSeparator()
    
    refresh_action = edit_menu.addAction("刷新")
    refresh_action.setShortcut(QKeySequence.Refresh)
    refresh_action.triggered.connect(main_window.refresh_panels)
    
    # 查看菜单
    view_menu = menubar.addMenu("查看(&V)")
    
    up_action = view_menu.addAction("返回上级目录")
    up_action.setShortcut("Backspace")
    up_action.triggered.connect(main_window.go_up)
    
    back_action = view_menu.addAction("后退")
    back_action.setShortcut("Alt+Left")
    back_action.triggered.connect(main_window.go_back)
    
    forward_action = view_menu.addAction("前进")
    forward_action.setShortcut("Alt+Right")
    forward_action.triggered.connect(main_window.go_forward)
    
    view_menu.addSeparator()
    
    bookmark_action = view_menu.addAction("书签管理")
    bookmark_action.setShortcut("Ctrl+B")
    bookmark_action.triggered.connect(lambda: on_bookmarks(main_window))
    
    view_menu.addSeparator()
    
    sync_action = view_menu.addAction("同步路径")
    sync_action.triggered.connect(main_window.sync_paths)
    
    view_menu.addSeparator()
    
    # 主题菜单
    theme_menu = view_menu.addMenu("主题")
    light_theme_action = theme_menu.addAction("浅色主题")
    light_theme_action.triggered.connect(lambda: on_change_theme(main_window, 'light'))
    
    dark_theme_action = theme_menu.addAction("深色主题")
    dark_theme_action.triggered.connect(lambda: on_change_theme(main_window, 'dark'))
    
    default_theme_action = theme_menu.addAction("默认主题")
    default_theme_action.triggered.connect(lambda: on_change_theme(main_window, 'default'))
    
    # 工具菜单
    tools_menu = menubar.addMenu("工具(&T)")
    
    search_action = tools_menu.addAction("搜索文件")
    search_action.setShortcut("Ctrl+F")
    search_action.triggered.connect(lambda: on_search(main_window))
    
    compare_action = tools_menu.addAction("对比文件")
    compare_action.setShortcut("Ctrl+Shift+C")
    compare_action.triggered.connect(lambda: on_compare_files(main_window))
    
    tools_menu.addSeparator()
    
    rename_action = tools_menu.addAction("批量重命名")
    rename_action.setShortcut("Ctrl+M")
    rename_action.triggered.connect(lambda: on_batch_rename(main_window))
    
    duplicate_action = tools_menu.addAction("查找重复文件")
    duplicate_action.setShortcut("Ctrl+Shift+D")
    duplicate_action.triggered.connect(lambda: on_find_duplicates(main_window))
    
    tools_menu.addSeparator()
    
    compress_action = tools_menu.addAction("压缩为ZIP...")
    compress_action.setShortcut("Ctrl+Shift+Z")
    compress_action.triggered.connect(lambda: on_compress(main_window))
    
    extract_action = tools_menu.addAction("解压ZIP...")
    extract_action.setShortcut("Ctrl+Shift+X")
    extract_action.triggered.connect(lambda: on_extract(main_window))
    
    tools_menu.addSeparator()
    
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


def on_compare_files(main_window):
    """对比文件 - 支持多种模式"""
    from .compare_dialog import CompareDialog
    from .file_compare import find_same_named_files
    from .compare_select_dialog import CompareSelectDialog
    
    # 获取两个面板的选中文件
    left_selected = main_window.left_panel.get_selected_files()
    right_selected = main_window.right_panel.get_selected_files()
    
    # 模式1: 只在左面板选中了一个文件，自动在右面板查找同名文件
    if len(left_selected) == 1 and len(right_selected) == 0:
        file1_path = left_selected[0]
        file1_name = file1_path.split('\\')[-1]
        
        # 在右面板目录中查找同名文件
        right_dir = main_window.right_panel.current_path
        file2_path = f"{right_dir}\\{file1_name}"
        
        import os
        if os.path.exists(file2_path):
            compare_dialog = CompareDialog(file1_path, file2_path, main_window)
            compare_dialog.exec_()
        else:
            QMessageBox.warning(main_window, "提示", f"在右面板目录中未找到同名文件: {file1_name}")
    
    # 模式2: 只在右面板选中了一个文件，自动在左面板查找同名文件
    elif len(right_selected) == 1 and len(left_selected) == 0:
        file2_path = right_selected[0]
        file2_name = file2_path.split('\\')[-1]
        
        # 在左面板目录中查找同名文件
        left_dir = main_window.left_panel.current_path
        file1_path = f"{left_dir}\\{file2_name}"
        
        import os
        if os.path.exists(file1_path):
            compare_dialog = CompareDialog(file1_path, file2_path, main_window)
            compare_dialog.exec_()
        else:
            QMessageBox.warning(main_window, "提示", f"在左面板目录中未找到同名文件: {file2_name}")
    
    # 模式3: 在左右两个面板都选中了文件，显示选择对话框
    elif (len(left_selected) > 0 and len(right_selected) > 0) or len(left_selected) > 1 or len(right_selected) > 1:
        # 弹出选择对话框，让用户选择对比方式
        select_dialog = CompareSelectDialog(main_window)
        select_dialog.exec_()
    
    else:
        # 模式4: 都没选或其他情况，显示选择对话框
        select_dialog = CompareSelectDialog(main_window)
        select_dialog.exec_()


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


def on_batch_rename(main_window):
    """批量重命名"""
    from .rename_dialog import RenameDialog
    
    focused = main_window.get_focused_panel()
    if not focused:
        QMessageBox.information(main_window, "提示", "请先选择一个文件面板")
        return
    
    selected = focused.get_selected_items()
    if not selected:
        QMessageBox.information(main_window, "提示", "请先选择要重命名的文件")
        return
    
    dialog = RenameDialog(main_window, selected)
    if dialog.exec_() == RenameDialog.Accepted:
        focused.refresh()


def on_find_duplicates(main_window):
    """查找重复文件"""
    from .duplicate_finder_dialog import DuplicateFinderDialog
    
    dialog = DuplicateFinderDialog(main_window)
    dialog.exec_()


def on_bookmarks(main_window):
    """书签管理"""
    from .bookmark_manager import BookmarkDialog
    
    focused = main_window.get_focused_panel()
    current_path = focused.current_path if focused else None
    
    dialog = BookmarkDialog(main_window, current_path)
    dialog.exec_()


def on_new_folder(main_window):
    """新建文件夹"""
    focused = main_window.get_focused_panel()
    if focused:
        focused.create_new_folder()


def on_new_file(main_window):
    """新建文件"""
    focused = main_window.get_focused_panel()
    if focused:
        focused.create_new_file()


def on_compress(main_window):
    """压缩文件"""
    from .archive_dialog import ArchiveDialog
    
    focused = main_window.get_focused_panel()
    if not focused:
        QMessageBox.information(main_window, "提示", "请先选择一个文件面板")
        return
    
    selected = focused.get_selected_items()
    if not selected:
        QMessageBox.information(main_window, "提示", "请先选择要压缩的文件或文件夹")
        return
    
    file_paths = [path for _, path in selected]
    dialog = ArchiveDialog(main_window, file_paths, operation='create')
    dialog.exec_()


def on_extract(main_window):
    """解压文件"""
    from .archive_dialog import ArchiveDialog
    
    focused = main_window.get_focused_panel()
    if not focused:
        QMessageBox.information(main_window, "提示", "请先选择一个文件面板")
        return
    
    selected = focused.get_selected_items()
    if not selected:
        # 如果没有选中，弹出文件选择对话框
        from PyQt5.QtWidgets import QFileDialog
        zip_path, _ = QFileDialog.getOpenFileName(
            main_window,
            "选择ZIP文件",
            focused.current_path if focused else "",
            "ZIP文件 (*.zip)"
        )
        if zip_path:
            dialog = ArchiveDialog(main_window, [zip_path], operation='extract')
            dialog.exec_()
    else:
        # 检查选中的是否为ZIP文件
        zip_files = [path for _, path in selected if path.lower().endswith('.zip')]
        if zip_files:
            dialog = ArchiveDialog(main_window, zip_files, operation='extract')
            dialog.exec_()
        else:
            QMessageBox.warning(main_window, "提示", "请选择ZIP文件")


def on_undo(main_window):
    """撤销操作"""
    focused = main_window.get_focused_panel()
    if focused and hasattr(focused, 'undo_manager'):
        success, message = focused.undo_manager.undo()
        if success:
            focused.refresh()
            QMessageBox.information(main_window, "撤销", message)
        else:
            QMessageBox.warning(main_window, "撤销失败", message)


def on_redo(main_window):
    """重做操作"""
    focused = main_window.get_focused_panel()
    if focused and hasattr(focused, 'undo_manager'):
        success, message = focused.undo_manager.redo()
        if success:
            focused.refresh()
            QMessageBox.information(main_window, "重做", message)
        else:
            QMessageBox.warning(main_window, "重做失败", message)


def on_change_theme(main_window, theme_name):
    """切换主题"""
    from .theme_manager import ThemeManager
    
    # 应用主题
    styles = ThemeManager.get_theme(theme_name)
    main_window.setStyleSheet(styles['main_window'])
    
    # 保存主题配置
    main_window.config.set('theme', theme_name)
    main_window.config.save_config(main_window.config.config)
    
    QMessageBox.information(main_window, "主题", f"已切换到{ThemeManager.THEMES[theme_name]['name']}")


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
        "• 批量重命名\n"
        "• 重复文件查找\n"
        "• 快速预览\n"
        "• 配置自动保存\n\n"
        "© 2026 All Rights Reserved"
    )
