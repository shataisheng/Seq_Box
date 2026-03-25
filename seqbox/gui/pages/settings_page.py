"""
Seq_Box - 设置页面
"""

from PyQt6.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QComboBox,
    QCheckBox, QGroupBox, QSpinBox, QFileDialog
)

from .base_page import BasePage, COLORS


class SettingsPage(BasePage):
    """设置页面"""
    
    def __init__(self, parent=None):
        super().__init__("设置", parent)
    
    def setup_ui(self):
        super().setup_ui()
        
        # 外观设置
        appearance_group = QGroupBox("外观")
        appearance_layout = QVBoxLayout(appearance_group)
        
        theme_layout = QHBoxLayout()
        theme_layout.addWidget(QLabel("主题:"))
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Tokyo Night (暗色)", "Light (亮色)"])
        theme_layout.addWidget(self.theme_combo)
        theme_layout.addStretch()
        appearance_layout.addLayout(theme_layout)
        
        font_layout = QHBoxLayout()
        font_layout.addWidget(QLabel("字体大小:"))
        self.font_size = QSpinBox()
        self.font_size.setRange(8, 20)
        self.font_size.setValue(10)
        font_layout.addWidget(self.font_size)
        font_layout.addStretch()
        appearance_layout.addLayout(font_layout)
        
        self.layout.addWidget(appearance_group)
        
        # FASTA 默认设置
        fasta_group = QGroupBox("FASTA 默认设置")
        fasta_layout = QVBoxLayout(fasta_group)
        
        line_width_layout = QHBoxLayout()
        line_width_layout.addWidget(QLabel("默认行宽:"))
        self.default_line_width = QSpinBox()
        self.default_line_width.setRange(40, 120)
        self.default_line_width.setValue(60)
        line_width_layout.addWidget(self.default_line_width)
        line_width_layout.addStretch()
        fasta_layout.addLayout(line_width_layout)
        
        self.default_remove_invalid = QCheckBox("默认去除非法字符")
        self.default_remove_invalid.setChecked(True)
        fasta_layout.addWidget(self.default_remove_invalid)
        
        self.layout.addWidget(fasta_group)
        
        # 输出设置
        output_group = QGroupBox("输出设置")
        output_layout = QVBoxLayout(output_group)
        
        default_dir_layout = QHBoxLayout()
        default_dir_layout.addWidget(QLabel("默认输出目录:"))
        self.default_output_dir = QLabel("未设置")
        self.default_output_dir.setStyleSheet(f"color: {COLORS['fg']};")
        default_dir_layout.addWidget(self.default_output_dir)
        
        btn_browse = QPushButton("浏览...")
        btn_browse.clicked.connect(self.browse_default_dir)
        default_dir_layout.addWidget(btn_browse)
        default_dir_layout.addStretch()
        output_layout.addLayout(default_dir_layout)
        
        self.auto_save_history = QCheckBox("自动保存操作历史")
        self.auto_save_history.setChecked(True)
        output_layout.addWidget(self.auto_save_history)
        
        self.layout.addWidget(output_group)
        
        # 保存按钮
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        btn_save = QPushButton("💾 保存设置")
        btn_save.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['green']};
                color: {COLORS['bg_dark']};
                font-size: 14px;
                padding: 10px 24px;
            }}
        """)
        btn_save.clicked.connect(self.save_settings)
        btn_layout.addWidget(btn_save)
        
        btn_reset = QPushButton("重置默认")
        btn_reset.clicked.connect(self.reset_settings)
        btn_layout.addWidget(btn_reset)
        
        self.layout.addLayout(btn_layout)
        self.layout.addStretch()
    
    def browse_default_dir(self):
        """浏览默认输出目录"""
        dir_path = QFileDialog.getExistingDirectory(self, "选择默认输出目录")
        if dir_path:
            self.default_output_dir.setText(dir_path)
    
    def save_settings(self):
        """保存设置"""
        # 这里可以将设置保存到配置文件
        self.log("设置已保存")
    
    def reset_settings(self):
        """重置为默认设置"""
        self.theme_combo.setCurrentIndex(0)
        self.font_size.setValue(10)
        self.default_line_width.setValue(60)
        self.default_remove_invalid.setChecked(True)
        self.default_output_dir.setText("未设置")
        self.auto_save_history.setChecked(True)
        self.log("设置已重置为默认值")
