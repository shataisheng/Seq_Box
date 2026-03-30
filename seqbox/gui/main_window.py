"""
Seq_Box - 主窗口

主窗口类，包含侧边导航和 Tab 操作区
"""

import sys
from pathlib import Path
from typing import Optional

# Tokyo Night 主题颜色
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

try:
    from PyQt6.QtWidgets import (
        QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
        QPushButton, QLabel, QStackedWidget, QTextEdit, QFrame,
        QFileDialog, QMessageBox, QSplitter, QStatusBar
    )
    from PyQt6.QtCore import Qt, QSize
    from PyQt6.QtGui import QFont, QIcon, QAction
    HAS_QT = True
except ImportError:
    HAS_QT = False


def main():
    """GUI 入口"""
    if not HAS_QT:
        print("Error: PyQt6 is required for GUI.")
        print("Install with: pip install PyQt6")
        sys.exit(1)
    
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    
    # 设置应用字体
    font = QFont("Microsoft YaHei", 10)
    app.setFont(font)
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())


if HAS_QT:
    class SidebarButton:
        """侧边栏导航按钮 - 工厂函数"""
        
        @staticmethod
        def create(text: str, parent=None):
            btn = QPushButton(text, parent)
            btn.setCheckable(True)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setMinimumHeight(40)
            btn.setFont(QFont("Microsoft YaHei", 10))
            SidebarButton.update_style(btn, False)
            return btn
        
        @staticmethod
        def update_style(btn, selected: bool):
            if selected:
                btn.setStyleSheet(f"""
                    QPushButton {{
                        background-color: {COLORS['blue']};
                        color: {COLORS['bg_dark']};
                        border: none;
                        border-radius: 6px;
                        padding: 8px 16px;
                        text-align: left;
                        font-weight: bold;
                    }}
                """)
            else:
                btn.setStyleSheet(f"""
                    QPushButton {{
                        background-color: transparent;
                        color: {COLORS['fg']};
                        border: none;
                        border-radius: 6px;
                        padding: 8px 16px;
                        text-align: left;
                    }}
                    QPushButton:hover {{
                        background-color: {COLORS['bg_light']};
                        color: {COLORS['fg_bright']};
                    }}
                """)


    class Sidebar(QWidget):
        """侧边导航栏"""
        
        def __init__(self, parent=None):
            super().__init__(parent)
            self.main_window = None
            self.buttons = []
            self.setup_ui()
        
        def setup_ui(self):
            layout = QVBoxLayout(self)
            layout.setContentsMargins(12, 20, 12, 20)
            layout.setSpacing(8)
            
            # Logo/标题
            title = QLabel("Seq Box")
            title.setFont(QFont("Microsoft YaHei", 18, QFont.Weight.Bold))
            title.setStyleSheet(f"color: {COLORS['blue']}; padding: 10px;")
            title.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(title)
            
            subtitle = QLabel("序列操作工具箱")
            subtitle.setFont(QFont("Microsoft YaHei", 9))
            subtitle.setStyleSheet(f"color: {COLORS['fg']}; padding-bottom: 20px;")
            subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(subtitle)
            
            # 分隔线
            line = QFrame()
            line.setFrameShape(QFrame.Shape.HLine)
            line.setStyleSheet(f"background-color: {COLORS['border']}; max-height: 1px;")
            layout.addWidget(line)
            layout.addSpacing(20)
            
            # 导航按钮
            nav_items = [
                ("FASTA 工具", "fasta", "📁"),
                ("DNA 操作", "dna", "🧬"),
                ("蛋白质", "protein", "🧪"),
                ("历史记录", "history", "📜"),
                ("设置", "settings", "⚙️"),
            ]
            
            for text, page_id, icon in nav_items:
                btn = SidebarButton.create(f"  {icon}  {text}")
                btn.clicked.connect(lambda checked, pid=page_id: self.on_nav_clicked(pid))
                self.buttons.append(btn)
                layout.addWidget(btn)
            
            layout.addStretch()
            
            # 版本信息
            version = QLabel("v0.4.1")
            version.setFont(QFont("Microsoft YaHei", 8))
            version.setStyleSheet(f"color: {COLORS['border']}; padding: 10px;")
            version.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(version)
            
            self.setStyleSheet(f"background-color: {COLORS['bg_dark']};")
            self.setFixedWidth(200)
        
        def on_nav_clicked(self, page_id: str):
            if self.main_window:
                self.main_window.switch_page(page_id)
        
        def set_active_button(self, page_id: str):
            for btn in self.buttons:
                btn.setChecked(False)
                SidebarButton.update_style(btn, False)
            
            # 根据 page_id 激活对应按钮
            page_map = {
                "fasta": 0, "dna": 1, "protein": 2, "history": 3, "settings": 4
            }
            if page_id in page_map:
                self.buttons[page_map[page_id]].setChecked(True)
                SidebarButton.update_style(self.buttons[page_map[page_id]], True)


    class MainWindow(QMainWindow):
        """主窗口"""
        
        def __init__(self):
            super().__init__()
            self.setWindowTitle("Seq Box - 序列操作工具箱")
            self.setMinimumSize(1400, 900)
            self.resize(1600, 1000)
            
            self.setup_ui()
            self.apply_theme()
        
        def setup_ui(self):
            # 中央部件
            central = QWidget()
            self.setCentralWidget(central)
            
            layout = QHBoxLayout(central)
            layout.setContentsMargins(0, 0, 0, 0)
            layout.setSpacing(0)
            
            # 侧边栏
            self.sidebar = Sidebar()
            self.sidebar.main_window = self
            layout.addWidget(self.sidebar)
            
            # 主内容区
            content = QWidget()
            content_layout = QVBoxLayout(content)
            content_layout.setContentsMargins(0, 0, 0, 0)
            content_layout.setSpacing(0)
            
            # 页面堆叠
            self.stack = QStackedWidget()
            
            # 导入页面模块
            from .pages import FastaPage, DnaPage, ProteinPage, HistoryPage, SettingsPage
            
            self.pages = {
                "fasta": FastaPage(),
                "dna": DnaPage(),
                "protein": ProteinPage(),
                "history": HistoryPage(),
                "settings": SettingsPage(),
            }
            
            for page_id, page in self.pages.items():
                self.stack.addWidget(page)
                page.page_id = page_id
            
            content_layout.addWidget(self.stack)
            
            # 底部输出区（包装一层以对齐上方页面内容的 24px 边距）
            log_wrapper = QWidget()
            log_wrapper.setStyleSheet("background-color: transparent;")
            log_layout = QHBoxLayout(log_wrapper)
            log_layout.setContentsMargins(24, 0, 24, 12)
            log_layout.setSpacing(0)
            self.output_panel = QTextEdit()
            self.output_panel.setReadOnly(True)
            self.output_panel.setMaximumHeight(120)
            self.output_panel.setPlaceholderText("输出日志...")
            log_layout.addWidget(self.output_panel)
            content_layout.addWidget(log_wrapper)
            
            layout.addWidget(content)
            
            # 状态栏
            self.status_bar = QStatusBar()
            self.setStatusBar(self.status_bar)
            self.status_bar.showMessage("就绪")
            
            # 默认显示 FASTA 页面
            self.switch_page("fasta")
        
        def switch_page(self, page_id: str):
            """切换页面"""
            if page_id in self.pages:
                index = list(self.pages.keys()).index(page_id)
                self.stack.setCurrentIndex(index)
                self.sidebar.set_active_button(page_id)
                self.status_bar.showMessage(f"当前: {self.pages[page_id].windowTitle()}")
        
        def apply_theme(self):
            """应用暗色主题"""
            self.setStyleSheet(f"""
                QMainWindow {{
                    background-color: {COLORS['bg']};
                }}
                QWidget {{
                    background-color: {COLORS['bg']};
                    color: {COLORS['fg']};
                    font-family: "Microsoft YaHei", "Segoe UI", sans-serif;
                }}
                QTextEdit {{
                    background-color: {COLORS['bg_dark']};
                    color: {COLORS['fg_bright']};
                    border: 1px solid {COLORS['border']};
                    border-radius: 6px;
                    padding: 8px;
                    font-family: "Consolas", "Monaco", monospace;
                    font-size: 12px;
                }}
                QStatusBar {{
                    background-color: {COLORS['bg_dark']};
                    color: {COLORS['fg']};
                    border-top: 1px solid {COLORS['border']};
                }}
            """)
        
        def log(self, message: str):
            """添加日志"""
            from datetime import datetime
            timestamp = datetime.now().strftime("%H:%M:%S")
            self.output_panel.append(f"[{timestamp}] {message}")


else:
    # PyQt6 不可用时提供占位符
    class MainWindow:
        def __init__(self):
            raise ImportError("PyQt6 is required for GUI. Install with: pip install PyQt6")


if __name__ == "__main__":
    main()
