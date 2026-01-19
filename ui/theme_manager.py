"""
主题管理器
"""


class ThemeManager:
    """主题管理器"""
    
    THEMES = {
        'light': {
            'name': '浅色主题',
            'bg_color': '#FFFFFF',
            'fg_color': '#000000',
            'panel_bg': '#F5F5F5',
            'border_color': '#D0D0D0',
            'hover_color': '#E0E0E0',
            'selected_color': '#ADD8E6',
            'title_bg': '#F3F3F3',
        },
        'dark': {
            'name': '深色主题',
            'bg_color': '#1E1E1E',
            'fg_color': '#D4D4D4',
            'panel_bg': '#252526',
            'border_color': '#3E3E42',
            'hover_color': '#2A2D2E',
            'selected_color': '#094771',
            'title_bg': '#2D2D30',
        },
        'default': {
            'name': '默认主题',
            'bg_color': '#FFFFFF',
            'fg_color': '#333333',
            'panel_bg': '#F5F5F5',
            'border_color': '#D0D0D0',
            'hover_color': '#E0E0E0',
            'selected_color': '#ADD8E6',
            'title_bg': '#F3F3F3',
        }
    }
    
    @staticmethod
    def get_theme(theme_name='default'):
        """获取主题样式"""
        theme = ThemeManager.THEMES.get(theme_name, ThemeManager.THEMES['default'])
        
        return {
            'main_window': f"""
                QMainWindow {{
                    background-color: {theme['bg_color']};
                    color: {theme['fg_color']};
                }}
            """,
            'title_bar': f"""
                QWidget {{
                    background-color: {theme['title_bg']};
                    border-bottom: 1px solid {theme['border_color']};
                }}
            """,
            'toolbar': f"""
                QWidget {{
                    background-color: {theme['panel_bg']};
                    border-bottom: 1px solid {theme['border_color']};
                }}
            """,
            'file_panel': f"""
                QWidget {{
                    background-color: {theme['bg_color']};
                    color: {theme['fg_color']};
                }}
                QTableWidget {{
                    background-color: {theme['bg_color']};
                    color: {theme['fg_color']};
                    border: 1px solid {theme['border_color']};
                    gridline-color: {theme['border_color']};
                }}
                QTableWidget::item:selected {{
                    background-color: {theme['selected_color']};
                }}
                QLineEdit {{
                    background-color: {theme['bg_color']};
                    color: {theme['fg_color']};
                    border: 1px solid {theme['border_color']};
                }}
            """,
            'menu_bar': f"""
                QMenuBar {{
                    background-color: transparent;
                    color: {theme['fg_color']};
                }}
                QMenuBar::item:selected {{
                    background-color: {theme['hover_color']};
                }}
            """,
            'button': f"""
                QPushButton {{
                    background-color: {theme['bg_color']};
                    color: {theme['fg_color']};
                    border: 1px solid {theme['border_color']};
                }}
                QPushButton:hover {{
                    background-color: {theme['hover_color']};
                }}
            """
        }
    
    @staticmethod
    def apply_theme(widget, theme_name='default'):
        """应用主题到控件"""
        styles = ThemeManager.get_theme(theme_name)
        widget.setStyleSheet(styles.get('main_window', ''))
