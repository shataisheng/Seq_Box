"""
Seq_Box - FASTA 工具页面
"""

from datetime import datetime
from pathlib import Path
from PyQt6.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QLineEdit,
    QTextEdit, QComboBox, QSpinBox, QCheckBox, QGroupBox,
    QTabWidget, QWidget, QFileDialog, QMessageBox, QGridLayout,
    QSplitter, QApplication
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QClipboard

from .base_page import BasePage, COLORS


def get_default_results_dir() -> Path:
    """获取默认结果目录 (项目目录/results/YYYYMMDD_HHMMSS)"""
    project_root = Path(__file__).parent.parent.parent.parent  # 项目根目录
    results_dir = project_root / "results"
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return results_dir / timestamp


class FastaPage(BasePage):
    """FASTA 工具页面"""
    
    def __init__(self, parent=None):
        super().__init__("FASTA 工具", parent)
    
    def setup_ui(self):
        super().setup_ui()
        
        # Tab 容器
        self.tabs = QTabWidget()
        
        # 各个功能 Tab
        self.tabs.addTab(self.create_clean_tab(), "🧹 清洗")
        self.tabs.addTab(self.create_split_tab(), "✂️ 分割")
        self.tabs.addTab(self.create_merge_tab(), "🔗 合并")
        self.tabs.addTab(self.create_info_tab(), "ℹ️ 信息")
        
        self.layout.addWidget(self.tabs)
    
    def create_clean_tab(self):
        """创建清洗功能 Tab - 优化对齐布局"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)
        
        # ===== 第一行：输入输出并排（高度对齐） =====
        io_row = QHBoxLayout()
        
        # 输入文件 (左) - 包含粘贴框
        input_group = QGroupBox("输入")
        input_layout = QVBoxLayout(input_group)
        input_layout.setSpacing(8)
        
        # 文件选择行
        file_row = QHBoxLayout()
        self.clean_input = QLineEdit()
        self.clean_input.setPlaceholderText("选择 FASTA 文件...")
        btn_browse_input = QPushButton("浏览...")
        btn_browse_input.clicked.connect(lambda: self.browse_file(self.clean_input, "选择 FASTA 文件", "FASTA Files (*.fa *.fasta *.fna);;All Files (*)"))
        file_row.addWidget(self.clean_input)
        file_row.addWidget(btn_browse_input)
        input_layout.addLayout(file_row)
        
        # 剪贴板按钮
        btn_clipboard = QPushButton("📋 从剪贴板粘贴")
        btn_clipboard.setToolTip("从系统剪贴板读取 FASTA 格式的序列")
        btn_clipboard.clicked.connect(self.paste_from_clipboard_clean)
        input_layout.addWidget(btn_clipboard)
        
        # 粘贴区域 - 增大高度，带滚动条
        self.clean_paste_area = QTextEdit()
        self.clean_paste_area.setPlaceholderText("粘贴 FASTA 序列或 Excel 两列表格...")
        self.clean_paste_area.setMinimumHeight(120)
        self.clean_paste_area.setMaximumHeight(200)
        self.clean_paste_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.clean_paste_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        input_layout.addWidget(self.clean_paste_area)
        
        io_row.addWidget(input_group, 1)
        
        # 输出文件 (右) - 包含清洗选项
        output_group = QGroupBox("输出")
        output_layout = QVBoxLayout(output_group)
        output_layout.setSpacing(8)
        
        output_row = QHBoxLayout()
        self.clean_output = QLineEdit()
        default_output = get_default_results_dir() / "cleaned.fasta"
        self.clean_output.setText(str(default_output))
        self.clean_output.setPlaceholderText("输出文件路径...")
        btn_browse_output = QPushButton("浏览...")
        btn_browse_output.clicked.connect(lambda: self.browse_save(self.clean_output, "保存为", "FASTA Files (*.fa *.fasta);;All Files (*)"))
        output_row.addWidget(self.clean_output)
        output_row.addWidget(btn_browse_output)
        output_layout.addLayout(output_row)
        
        # 执行按钮 - 与剪贴板按钮对齐
        btn_execute = QPushButton("🚀 开始清洗")
        btn_execute.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['green']};
                color: {COLORS['bg_dark']};
                font-size: 13px;
                padding: 10px 20px;
                font-weight: bold;
            }}
        """)
        btn_execute.clicked.connect(self.execute_clean)
        output_layout.addWidget(btn_execute)
        
        # 清洗选项 - 与粘贴框对齐
        options_frame = QGroupBox("清洗选项")
        options_layout = QGridLayout(options_frame)
        options_layout.setSpacing(8)
        
        # 第一行选项
        type_layout = QHBoxLayout()
        type_layout.addWidget(QLabel("类型:"))
        self.clean_type = QComboBox()
        self.clean_type.addItems(["自动", "DNA", "RNA", "蛋白质"])
        self.clean_type.setFixedWidth(70)
        type_layout.addWidget(self.clean_type)
        options_layout.addLayout(type_layout, 0, 0)
        
        self.clean_remove_invalid = QCheckBox("去非法字符")
        self.clean_remove_invalid.setChecked(True)
        options_layout.addWidget(self.clean_remove_invalid, 0, 1)
        
        self.clean_remove_duplicates = QCheckBox("去重复")
        options_layout.addWidget(self.clean_remove_duplicates, 0, 2)
        
        # 第二行选项
        len_layout = QHBoxLayout()
        len_layout.addWidget(QLabel("长度:"))
        self.clean_min_len = QSpinBox()
        self.clean_min_len.setRange(0, 999999)
        self.clean_min_len.setValue(0)
        self.clean_min_len.setFixedWidth(55)
        len_layout.addWidget(self.clean_min_len)
        len_layout.addWidget(QLabel("-"))
        self.clean_max_len = QSpinBox()
        self.clean_max_len.setRange(0, 9999999)
        self.clean_max_len.setValue(0)
        self.clean_max_len.setSpecialValueText("∞")
        self.clean_max_len.setFixedWidth(55)
        len_layout.addWidget(self.clean_max_len)
        options_layout.addLayout(len_layout, 1, 0)
        
        wrap_layout = QHBoxLayout()
        wrap_layout.addWidget(QLabel("换行:"))
        self.clean_line_wrap = QComboBox()
        self.clean_line_wrap.addItems(["60", "80", "100", "不换"])
        self.clean_line_wrap.setCurrentIndex(0)
        self.clean_line_wrap.setFixedWidth(60)
        wrap_layout.addWidget(self.clean_line_wrap)
        options_layout.addLayout(wrap_layout, 1, 1)
        
        options_layout.setColumnStretch(3, 1)
        output_layout.addWidget(options_frame)
        
        io_row.addWidget(output_group, 1)
        layout.addLayout(io_row)
        
        # ===== 第二行：结果预览（带滚动条） =====
        # 使用自定义标题栏布局，按钮放在标题右侧
        result_header = QHBoxLayout()
        result_header.addWidget(QLabel("结果预览"))
        result_header.addStretch()
        
        btn_copy = QPushButton("📋 复制")
        btn_copy.setToolTip("复制结果到剪贴板")
        btn_copy.setFixedWidth(80)
        btn_copy.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['bg_light']};
                color: {COLORS['fg_bright']};
                border: 1px solid {COLORS['border']};
                border-radius: 4px;
                padding: 4px 8px;
                font-size: 11px;
            }}
            QPushButton:hover {{
                background-color: {COLORS['blue']};
                color: {COLORS['bg_dark']};
            }}
        """)
        btn_copy.clicked.connect(self.copy_clean_result)
        result_header.addWidget(btn_copy)
        layout.addLayout(result_header)
        
        self.clean_result_preview = QTextEdit()
        self.clean_result_preview.setPlaceholderText("清洗后的序列将显示在这里，可直接复制...")
        self.clean_result_preview.setMinimumHeight(380)
        self.clean_result_preview.setReadOnly(True)
        self.clean_result_preview.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.clean_result_preview.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        layout.addWidget(self.clean_result_preview, 1)
        
        return tab
    
    def create_split_tab(self):
        """创建分割功能 Tab - 优化对齐布局"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)
        
        # ===== 第一行：输入输出并排（高度对齐） =====
        io_row = QHBoxLayout()
        
        # 输入 (左) - 包含粘贴框
        input_group = QGroupBox("输入")
        input_layout = QVBoxLayout(input_group)
        input_layout.setSpacing(8)
        
        file_row = QHBoxLayout()
        self.split_input = QLineEdit()
        self.split_input.setPlaceholderText("选择 FASTA 文件...")
        btn_browse = QPushButton("浏览...")
        btn_browse.clicked.connect(lambda: self.browse_file(self.split_input))
        file_row.addWidget(self.split_input)
        file_row.addWidget(btn_browse)
        input_layout.addLayout(file_row)
        
        btn_clipboard = QPushButton("📋 从剪贴板粘贴")
        btn_clipboard.clicked.connect(self.paste_from_clipboard_split)
        input_layout.addWidget(btn_clipboard)
        
        self.split_paste_area = QTextEdit()
        self.split_paste_area.setPlaceholderText("粘贴 FASTA 序列或 Excel 两列表格...")
        self.split_paste_area.setMinimumHeight(120)
        self.split_paste_area.setMaximumHeight(200)
        self.split_paste_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.split_paste_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        input_layout.addWidget(self.split_paste_area)
        
        io_row.addWidget(input_group, 1)
        
        # 输出 (右) - 包含分割方式
        output_group = QGroupBox("输出")
        output_layout = QVBoxLayout(output_group)
        output_layout.setSpacing(8)
        
        dir_row = QHBoxLayout()
        self.split_output_dir = QLineEdit()
        default_output_dir = get_default_results_dir()
        self.split_output_dir.setText(str(default_output_dir))
        self.split_output_dir.setPlaceholderText("输出目录...")
        btn_browse_dir = QPushButton("浏览...")
        btn_browse_dir.clicked.connect(lambda: self.browse_dir(self.split_output_dir))
        dir_row.addWidget(self.split_output_dir)
        dir_row.addWidget(btn_browse_dir)
        output_layout.addLayout(dir_row)
        
        # 执行按钮 - 与剪贴板按钮对齐
        btn_execute = QPushButton("🚀 开始分割")
        btn_execute.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['cyan']};
                color: {COLORS['bg_dark']};
                font-size: 13px;
                padding: 10px 20px;
                font-weight: bold;
            }}
        """)
        btn_execute.clicked.connect(self.execute_split)
        output_layout.addWidget(btn_execute)
        
        # 分割方式 - 与粘贴框对齐
        mode_frame = QGroupBox("分割方式")
        mode_layout = QGridLayout(mode_frame)
        mode_layout.setSpacing(8)
        
        # 第一行
        count_layout = QHBoxLayout()
        self.split_by_count = QCheckBox("按记录数")
        self.split_by_count.setChecked(True)
        count_layout.addWidget(self.split_by_count)
        self.split_count = QSpinBox()
        self.split_count.setRange(1, 999999)
        self.split_count.setValue(100)
        self.split_count.setFixedWidth(70)
        count_layout.addWidget(self.split_count)
        count_layout.addWidget(QLabel("条/文件"))
        mode_layout.addLayout(count_layout, 0, 0)
        
        n_layout = QHBoxLayout()
        self.split_into_n = QCheckBox("平均分割为")
        n_layout.addWidget(self.split_into_n)
        self.split_n = QSpinBox()
        self.split_n.setRange(2, 999)
        self.split_n.setValue(10)
        self.split_n.setFixedWidth(60)
        n_layout.addWidget(self.split_n)
        n_layout.addWidget(QLabel("个文件"))
        mode_layout.addLayout(n_layout, 0, 1)
        
        # 第二行
        single_layout = QHBoxLayout()
        self.split_single = QCheckBox("每条序列单独一个文件")
        single_layout.addWidget(self.split_single)
        single_layout.addWidget(QLabel("  前缀:"))
        self.split_prefix = QLineEdit()
        self.split_prefix.setText("split")
        self.split_prefix.setFixedWidth(80)
        single_layout.addWidget(self.split_prefix)
        single_layout.addStretch()
        mode_layout.addLayout(single_layout, 1, 0, 1, 2)
        
        output_layout.addWidget(mode_frame)
        
        io_row.addWidget(output_group, 1)
        layout.addLayout(io_row)
        
        # ===== 第二行：结果预览（带滚动条） =====
        # 使用自定义标题栏布局，按钮放在标题右侧
        result_header = QHBoxLayout()
        result_header.addWidget(QLabel("结果预览 (第一个文件)"))
        result_header.addStretch()
        
        btn_copy = QPushButton("📋 复制")
        btn_copy.setToolTip("复制结果到剪贴板")
        btn_copy.setFixedWidth(80)
        btn_copy.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['bg_light']};
                color: {COLORS['fg_bright']};
                border: 1px solid {COLORS['border']};
                border-radius: 4px;
                padding: 4px 8px;
                font-size: 11px;
            }}
            QPushButton:hover {{
                background-color: {COLORS['cyan']};
                color: {COLORS['bg_dark']};
            }}
        """)
        btn_copy.clicked.connect(self.copy_split_result)
        result_header.addWidget(btn_copy)
        layout.addLayout(result_header)
        
        self.split_result_preview = QTextEdit()
        self.split_result_preview.setPlaceholderText("分割后的序列将显示在这里 (仅显示第一个文件内容)，可直接复制...")
        self.split_result_preview.setMinimumHeight(380)
        self.split_result_preview.setReadOnly(True)
        self.split_result_preview.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.split_result_preview.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        layout.addWidget(self.split_result_preview, 1)
        
        return tab
    
    def create_merge_tab(self):
        """创建合并功能 Tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)
        
        # 输入文件列表
        input_group = QGroupBox("输入文件 (每行一个文件路径)")
        input_layout = QVBoxLayout(input_group)
        
        self.merge_input_list = QTextEdit()
        self.merge_input_list.setPlaceholderText("输入 FASTA 文件路径，每行一个...\n或点击浏览选择多个文件")
        self.merge_input_list.setMaximumHeight(120)
        input_layout.addWidget(self.merge_input_list)
        
        btn_browse = QPushButton("📁 添加文件...")
        btn_browse.clicked.connect(self.browse_multiple_files)
        input_layout.addWidget(btn_browse)
        
        layout.addWidget(input_group)
        
        # 输出文件
        output_group = QGroupBox("输出文件")
        output_layout = QHBoxLayout(output_group)
        self.merge_output = QLineEdit()
        self.merge_output.setPlaceholderText("选择输出文件路径...")
        btn_browse_output = QPushButton("浏览...")
        btn_browse_output.clicked.connect(lambda: self.browse_save(self.merge_output))
        output_layout.addWidget(self.merge_output)
        output_layout.addWidget(btn_browse_output)
        layout.addWidget(output_group)
        
        # 选项
        options_group = QGroupBox("合并选项")
        options_layout = QGridLayout(options_group)
        
        options_layout.addWidget(QLabel("ID 冲突处理:"), 0, 0)
        self.merge_duplicate_handling = QComboBox()
        self.merge_duplicate_handling.addItems(["自动重命名", "报错", "跳过", "覆盖"])
        options_layout.addWidget(self.merge_duplicate_handling, 0, 1)
        
        self.merge_remove_duplicates = QCheckBox("去除序列内容完全相同的记录")
        options_layout.addWidget(self.merge_remove_duplicates, 1, 0, 1, 2)
        
        layout.addWidget(options_group)
        
        # 执行按钮
        btn_execute = QPushButton("🚀 开始合并")
        btn_execute.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['purple']};
                color: {COLORS['bg_dark']};
                font-size: 14px;
                padding: 12px 24px;
            }}
        """)
        btn_execute.clicked.connect(self.execute_merge)
        layout.addWidget(btn_execute)
        
        layout.addStretch()
        return tab
    
    def create_info_tab(self):
        """创建信息查看 Tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)
        
        # 输入文件
        input_group = QGroupBox("输入文件")
        input_layout = QHBoxLayout(input_group)
        self.info_input = QLineEdit()
        self.info_input.setPlaceholderText("选择 FASTA 文件...")
        btn_browse = QPushButton("浏览...")
        btn_browse.clicked.connect(lambda: self.browse_file(self.info_input))
        input_layout.addWidget(self.info_input)
        input_layout.addWidget(btn_browse)
        layout.addWidget(input_group)
        
        # 执行按钮
        btn_execute = QPushButton("📊 查看信息")
        btn_execute.clicked.connect(self.execute_info)
        layout.addWidget(btn_execute)
        
        # 结果显示
        result_group = QGroupBox("文件信息")
        result_layout = QVBoxLayout(result_group)
        self.info_result = QTextEdit()
        self.info_result.setReadOnly(True)
        self.info_result.setPlaceholderText("文件统计信息将显示在这里...")
        result_layout.addWidget(self.info_result)
        layout.addWidget(result_group)
        
        layout.addStretch()
        return tab
    
    # ===== 工具方法 =====
    
    def browse_file(self, line_edit, title="选择文件", filter_str="FASTA Files (*.fa *.fasta *.fna);;All Files (*)"):
        """浏览选择文件"""
        file_path, _ = QFileDialog.getOpenFileName(self, title, "", filter_str)
        if file_path:
            line_edit.setText(file_path)
    
    def browse_save(self, line_edit, title="保存文件", filter_str="FASTA Files (*.fa *.fasta);;All Files (*)"):
        """浏览保存文件"""
        file_path, _ = QFileDialog.getSaveFileName(self, title, "", filter_str)
        if file_path:
            line_edit.setText(file_path)
    
    def browse_dir(self, line_edit):
        """浏览选择目录"""
        dir_path = QFileDialog.getExistingDirectory(self, "选择目录")
        if dir_path:
            line_edit.setText(dir_path)
    
    def browse_multiple_files(self):
        """选择多个文件"""
        files, _ = QFileDialog.getOpenFileNames(
            self, "选择多个 FASTA 文件", "",
            "FASTA Files (*.fa *.fasta *.fna);;All Files (*)"
        )
        if files:
            current = self.merge_input_list.toPlainText()
            if current and not current.endswith('\n'):
                current += '\n'
            self.merge_input_list.setText(current + '\n'.join(files))
    
    def paste_from_clipboard_clean(self):
        """从剪贴板粘贴序列到清洗页面"""
        clipboard = QApplication.clipboard()
        text = clipboard.text()
        if text:
            converted = self._convert_excel_to_fasta(text)
            self.clean_paste_area.setPlainText(converted)
            if converted != text:
                self.log("已从剪贴板粘贴并转换 Excel 格式为 FASTA")
            else:
                self.log("已从剪贴板粘贴序列到清洗页面")
        else:
            QMessageBox.information(self, "提示", "剪贴板中没有文本内容")
    
    def paste_from_clipboard_split(self):
        """从剪贴板粘贴序列到分割页面"""
        clipboard = QApplication.clipboard()
        text = clipboard.text()
        if text:
            converted = self._convert_excel_to_fasta(text)
            self.split_paste_area.setPlainText(converted)
            if converted != text:
                self.log("已从剪贴板粘贴并转换 Excel 格式为 FASTA")
            else:
                self.log("已从剪贴板粘贴序列到分割页面")
        else:
            QMessageBox.information(self, "提示", "剪贴板中没有文本内容")
    
    def _convert_excel_to_fasta(self, text: str) -> str:
        """
        自动识别并转换 Excel 表格格式为 FASTA 格式
        
        支持的格式：
        1. 两列格式: Header \t Sequence (如 Excel A列>B列)
        2. 标准 FASTA: >header\nsequence
        """
        lines = text.strip().split('\n')
        if not lines:
            return text
        
        # 检查是否是表格格式（包含制表符）
        is_table_format = False
        tab_separated_lines = []
        
        for line in lines:
            if '\t' in line:
                parts = line.split('\t')
                if len(parts) >= 2:
                    is_table_format = True
                    tab_separated_lines.append(parts)
        
        if not is_table_format:
            # 不是表格格式，检查是否已经是 FASTA 格式
            return text
        
        # 转换为 FASTA 格式
        fasta_lines = []
        for parts in tab_separated_lines:
            header = parts[0].strip()
            sequence = parts[1].strip() if len(parts) > 1 else ""
            
            # 确保 header 以 > 开头
            if header and not header.startswith('>'):
                header = '>' + header
            
            if header and sequence:
                fasta_lines.append(header)
                fasta_lines.append(sequence)
        
        return '\n'.join(fasta_lines)
    
    def _save_temp_fasta(self, text: str) -> Path:
        """将粘贴的文本保存为临时 FASTA 文件"""
        temp_dir = get_default_results_dir()
        temp_dir.mkdir(parents=True, exist_ok=True)
        temp_file = temp_dir / "temp_input.fasta"
        temp_file.write_text(text, encoding='utf-8')
        return temp_file
    
    def _reformat_fasta_wrapping(self, file_path: Path, line_width: int):
        """重新格式化 FASTA 文件的序列换行"""
        from seqbox.io.fasta import FastaReader, FastaWriter
        
        # 读取所有记录
        reader = FastaReader(file_path)
        records = reader.read_all()
        
        # 写回文件，使用新的行宽
        with FastaWriter(file_path, line_width=line_width) as writer:
            for record in records:
                writer.write_record(record)
    
    def copy_clean_result(self):
        """复制清洗结果到剪贴板"""
        text = self.clean_result_preview.toPlainText()
        if text:
            clipboard = QApplication.clipboard()
            clipboard.setText(text)
            self.log("清洗结果已复制到剪贴板")
            QMessageBox.information(self, "提示", "结果已复制到剪贴板")
        else:
            QMessageBox.warning(self, "提示", "没有可复制的内容")
    
    def copy_split_result(self):
        """复制分割结果到剪贴板"""
        text = self.split_result_preview.toPlainText()
        if text:
            clipboard = QApplication.clipboard()
            clipboard.setText(text)
            self.log("分割结果已复制到剪贴板")
            QMessageBox.information(self, "提示", "结果已复制到剪贴板")
        else:
            QMessageBox.warning(self, "提示", "没有可复制的内容")
    
    # ===== 执行方法 =====
    
    def execute_clean(self):
        """执行清洗"""
        # 检查粘贴区域是否有内容
        pasted_text = self.clean_paste_area.toPlainText().strip()
        
        if pasted_text:
            # 使用粘贴的内容
            try:
                input_path = self._save_temp_fasta(pasted_text)
                self.log(f"使用粘贴的序列内容 ({len(pasted_text)} 字符)")
            except Exception as e:
                QMessageBox.critical(self, "错误", f"保存粘贴内容失败: {str(e)}")
                return
        else:
            # 使用文件输入
            input_path = self.clean_input.text()
            if not input_path:
                QMessageBox.warning(self, "警告", "请选择输入文件或粘贴序列内容")
                return
        
        output_path = self.clean_output.text()
        if not output_path:
            QMessageBox.warning(self, "警告", "请选择输出文件路径")
            return
        
        # 确保输出目录存在
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        
        try:
            from seqbox.io.fasta import clean_fasta, SeqType
            
            seq_type_map = {
                0: SeqType.AUTO,
                1: SeqType.DNA,
                2: SeqType.RNA,
                3: SeqType.PROTEIN,
            }
            
            stats = clean_fasta(
                input_path=input_path,
                output_path=output_path,
                seq_type=seq_type_map[self.clean_type.currentIndex()],
                remove_invalid=self.clean_remove_invalid.isChecked(),
                remove_duplicates=self.clean_remove_duplicates.isChecked(),
                min_length=self.clean_min_len.value() if self.clean_min_len.value() > 0 else None,
                max_length=self.clean_max_len.value() if self.clean_max_len.value() > 0 else None,
            )
            
            self.log(f"清洗完成: {stats.input_count} → {stats.output_count} 条序列")
            
            # 根据换行设置重新格式化输出文件
            line_width_map = {0: 60, 1: 80, 2: 100, 3: None}
            line_width = line_width_map[self.clean_line_wrap.currentIndex()]
            
            if line_width is not None:
                try:
                    self._reformat_fasta_wrapping(output_path, line_width)
                except Exception as fmt_err:
                    self.log(f"格式化换行失败: {fmt_err}")
            
            # 读取并显示结果预览
            try:
                with open(output_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    # 限制预览长度，避免大文件卡死
                    max_preview = 10000
                    if len(content) > max_preview:
                        preview = content[:max_preview] + f"\n\n... (内容已截断，共 {len(content)} 字符)"
                    else:
                        preview = content
                    self.clean_result_preview.setPlainText(preview)
            except Exception as read_err:
                self.clean_result_preview.setPlainText(f"(无法读取预览: {read_err})")
            
            QMessageBox.information(
                self, "完成",
                f"清洗完成！\n\n"
                f"输入: {stats.input_count} 条\n"
                f"输出: {stats.output_count} 条\n"
                f"去除重复: {stats.removed_duplicates} 条\n\n"
                f"输出文件: {output_path}\n\n"
                f"结果已显示在预览框，可直接复制使用。"
            )
            
        except Exception as e:
            QMessageBox.critical(self, "错误", f"清洗失败: {str(e)}")
            self.log(f"清洗错误: {e}")
    
    def execute_split(self):
        """执行分割"""
        # 检查粘贴区域是否有内容
        pasted_text = self.split_paste_area.toPlainText().strip()
        
        if pasted_text:
            # 使用粘贴的内容
            try:
                input_path = self._save_temp_fasta(pasted_text)
                self.log(f"使用粘贴的序列内容 ({len(pasted_text)} 字符)")
            except Exception as e:
                QMessageBox.critical(self, "错误", f"保存粘贴内容失败: {str(e)}")
                return
        else:
            # 使用文件输入
            input_path = self.split_input.text()
            if not input_path:
                QMessageBox.warning(self, "警告", "请选择输入文件或粘贴序列内容")
                return
        
        output_dir = self.split_output_dir.text()
        if not output_dir:
            QMessageBox.warning(self, "警告", "请选择输出目录")
            return
        
        # 确保输出目录存在
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        
        try:
            from seqbox.io.fasta import (
                split_fasta_by_count,
                split_fasta_into_n_files,
                split_fasta_to_single_files
            )
            
            files = []
            if self.split_by_count.isChecked():
                files = split_fasta_by_count(
                    input_path=input_path,
                    output_dir=output_dir,
                    records_per_file=self.split_count.value(),
                    prefix=self.split_prefix.text()
                )
                self.log(f"分割完成: 生成 {len(files)} 个文件")
                
            elif self.split_into_n.isChecked():
                files = split_fasta_into_n_files(
                    input_path=input_path,
                    output_dir=output_dir,
                    n_files=self.split_n.value(),
                    prefix=self.split_prefix.text()
                )
                self.log(f"分割完成: 生成 {len(files)} 个文件")
                
            elif self.split_single.isChecked():
                files = split_fasta_to_single_files(
                    input_path=input_path,
                    output_dir=output_dir,
                    naming="id"
                )
                self.log(f"分割完成: 生成 {len(files)} 个单序列文件")
            else:
                QMessageBox.warning(self, "警告", "请选择一种分割方式")
                return
            
            # 读取并显示第一个文件作为预览
            if files:
                try:
                    with open(files[0], 'r', encoding='utf-8') as f:
                        content = f.read()
                        max_preview = 10000
                        if len(content) > max_preview:
                            preview = content[:max_preview] + f"\n\n... (内容已截断，共 {len(content)} 字符)"
                        else:
                            preview = content
                        header = f"# 第一个文件: {Path(files[0]).name}\n\n"
                        self.split_result_preview.setPlainText(header + preview)
                except Exception as read_err:
                    self.split_result_preview.setPlainText(f"(无法读取预览: {read_err})")
            
            QMessageBox.information(
                self, "完成", 
                f"分割完成！生成 {len(files)} 个文件\n\n"
                f"输出目录: {output_dir}\n\n"
                f"第一个文件内容已显示在预览框，可直接复制使用。"
            )
                
        except Exception as e:
            QMessageBox.critical(self, "错误", f"分割失败: {str(e)}")
            self.log(f"分割错误: {e}")
    
    def execute_merge(self):
        """执行合并"""
        input_text = self.merge_input_list.toPlainText()
        output_path = self.merge_output.text()
        
        if not input_text or not output_path:
            QMessageBox.warning(self, "警告", "请输入文件列表和输出路径")
            return
        
        input_paths = [p.strip() for p in input_text.split('\n') if p.strip()]
        
        try:
            from seqbox.io.fasta import merge_fasta_files, DuplicateIDHandling
            
            handling_map = {
                0: DuplicateIDHandling.RENAME,
                1: DuplicateIDHandling.ERROR,
                2: DuplicateIDHandling.SKIP,
                3: DuplicateIDHandling.OVERWRITE,
            }
            
            stats = merge_fasta_files(
                input_paths=input_paths,
                output_path=output_path,
                duplicate_handling=handling_map[self.merge_duplicate_handling.currentIndex()],
                remove_duplicates=self.merge_remove_duplicates.isChecked()
            )
            
            self.log(f"合并完成: {stats.records_read} → {stats.records_written} 条序列")
            QMessageBox.information(
                self, "完成",
                f"合并完成！\n\n"
                f"处理文件: {stats.files_processed} 个\n"
                f"读取记录: {stats.records_read} 条\n"
                f"写入记录: {stats.records_written} 条\n"
                f"ID 冲突: {stats.duplicates_found} 个"
            )
            
        except Exception as e:
            QMessageBox.critical(self, "错误", f"合并失败: {str(e)}")
            self.log(f"合并错误: {e}")
    
    def execute_info(self):
        """执行信息查看"""
        input_path = self.info_input.text()
        
        if not input_path:
            QMessageBox.warning(self, "警告", "请选择输入文件")
            return
        
        try:
            from seqbox.io.fasta import FastaReader
            
            reader = FastaReader(input_path)
            records = reader.read_all()
            
            total_seqs = len(records)
            total_length = sum(len(r.seq) for r in records)
            avg_length = total_length / total_seqs if total_seqs > 0 else 0
            min_len = min(len(r.seq) for r in records) if records else 0
            max_len = max(len(r.seq) for r in records) if records else 0
            
            info_text = f"""文件: {input_path}

序列数量: {total_seqs}
总长度: {total_length:,} bp/aa
平均长度: {avg_length:.1f}
最短: {min_len}
最长: {max_len}

序列列表:
"""
            for r in records:
                desc = f" {r.description}" if r.description else ""
                info_text += f"  >{r.id}{desc} [{len(r.seq)}]\n"
            
            self.info_result.setText(info_text)
            self.log(f"查看文件信息: {input_path}, {total_seqs} 条序列")
            
        except Exception as e:
            QMessageBox.critical(self, "错误", f"读取失败: {str(e)}")
            self.log(f"信息查看错误: {e}")
