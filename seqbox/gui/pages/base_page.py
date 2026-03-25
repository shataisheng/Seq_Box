"""
Seq_Box - 页面基类
"""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QHBoxLayout
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

# 主题颜色
COLORS = {
    'bg': '#1a1b26',
    'bg_dark': '#16161e',
    'bg_light': '#24283b',
    'fg': '#a9b1d6',
    'fg_bright': '#c0caf5',
    'blue': '#7aa2f7',
    'green': '#9ece6a',
    'cyan': '#7dcfff',
    'purple': '#bb9af7',
    'yellow': '#e0af68',
    'red': '#f7768e',
    'border': '#414868',
}


class BasePage(QWidget):
    """页面基类"""
    
    def __init__(self, title: str, parent=None):
        super().__init__(parent)
        self.page_id = ""
        self.setWindowTitle(title)
        self.setup_ui()
        self.apply_styles()
    
    def setup_ui(self):
        """子类重写此方法设置 UI"""
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(24, 24, 24, 24)
        self.layout.setSpacing(16)
        
        # 页面标题
        self.title_label = QLabel(self.windowTitle())
        self.title_label.setFont(QFont("Microsoft YaHei", 16, QFont.Weight.Bold))
        self.title_label.setStyleSheet(f"color: {COLORS['fg_bright']}; padding-bottom: 8px;")
        self.layout.addWidget(self.title_label)
    
    def apply_styles(self):
        """应用样式"""
        self.setStyleSheet(f"""
            QWidget {{
                background-color: {COLORS['bg']};
                color: {COLORS['fg']};
            }}
            QPushButton {{
                background-color: {COLORS['blue']};
                color: {COLORS['bg_dark']};
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: bold;
                min-height: 32px;
            }}
            QPushButton:hover {{
                background-color: #8ab4f8;
            }}
            QPushButton:pressed {{
                background-color: #6a92e7;
            }}
            QPushButton:disabled {{
                background-color: {COLORS['border']};
                color: {COLORS['fg']};
            }}
            QLineEdit {{
                background-color: {COLORS['bg_dark']};
                color: {COLORS['fg_bright']};
                border: 1px solid {COLORS['border']};
                border-radius: 6px;
                padding: 8px 12px;
                min-height: 20px;
            }}
            QLineEdit:focus {{
                border-color: {COLORS['blue']};
            }}
            QTextEdit {{
                background-color: {COLORS['bg_dark']};
                color: {COLORS['fg_bright']};
                border: 1px solid {COLORS['border']};
                border-radius: 6px;
                padding: 8px;
                font-family: "Consolas", "Monaco", monospace;
            }}
            QComboBox {{
                background-color: {COLORS['bg_dark']};
                color: {COLORS['fg_bright']};
                border: 1px solid {COLORS['border']};
                border-radius: 6px;
                padding: 8px 12px;
                min-height: 20px;
            }}
            QComboBox:hover {{
                border-color: {COLORS['blue']};
            }}
            QComboBox::drop-down {{
                border: none;
                width: 24px;
            }}
            QComboBox QAbstractItemView {{
                background-color: {COLORS['bg_dark']};
                color: {COLORS['fg_bright']};
                border: 1px solid {COLORS['border']};
                selection-background-color: {COLORS['blue']};
            }}
            QCheckBox {{
                color: {COLORS['fg']};
                spacing: 8px;
            }}
            QCheckBox::indicator {{
                width: 18px;
                height: 18px;
                border: 2px solid {COLORS['border']};
                border-radius: 4px;
                background-color: {COLORS['bg_dark']};
            }}
            QCheckBox::indicator:checked {{
                background-color: {COLORS['blue']};
                border-color: {COLORS['blue']};
            }}
            QSpinBox {{
                background-color: {COLORS['bg_dark']};
                color: {COLORS['fg_bright']};
                border: 1px solid {COLORS['border']};
                border-radius: 6px;
                padding: 8px;
            }}
            QLabel {{
                color: {COLORS['fg']};
            }}
            QGroupBox {{
                color: {COLORS['fg_bright']};
                border: 1px solid {COLORS['border']};
                border-radius: 8px;
                margin-top: 12px;
                padding-top: 12px;
                font-weight: bold;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 12px;
                padding: 0 8px;
            }}
            QTabWidget::pane {{
                border: 1px solid {COLORS['border']};
                border-radius: 6px;
                background-color: {COLORS['bg_dark']};
            }}
            QTabBar::tab {{
                background-color: {COLORS['bg_light']};
                color: {COLORS['fg']};
                padding: 10px 20px;
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
                margin-right: 2px;
            }}
            QTabBar::tab:selected {{
                background-color: {COLORS['blue']};
                color: {COLORS['bg_dark']};
            }}
            QTabBar::tab:hover:!selected {{
                background-color: {COLORS['border']};
            }}
        """)
    
    def log(self, message: str):
        """发送日志消息到主窗口"""
        # 通过信号或直接调用主窗口方法
        main_window = self.window()
        if hasattr(main_window, 'log'):
            main_window.log(message)
