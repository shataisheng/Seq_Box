"""
Seq_Box - Sequence Alignment Page
"""

from PyQt6.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QLineEdit,
    QTextEdit, QComboBox, QGroupBox, QWidget, QFileDialog,
    QMessageBox, QGridLayout, QApplication, QTabWidget,
    QTableWidget, QTableWidgetItem, QHeaderView, QSizePolicy,
    QSplitter, QFrame, QScrollArea, QStackedWidget,
)
from PyQt6.QtCore import Qt, QSize, QMargins
from PyQt6.QtGui import QFont, QColor

from datetime import datetime
from pathlib import Path

from .base_page import BasePage, COLORS
from seqbox.io.fasta import FastaReader


def get_default_results_dir() -> Path:
    """获取默认结果目录 (项目目录/results/YYYYMMDD_HHMMSS)"""
    project_root = Path(__file__).parent.parent.parent.parent
    results_dir = project_root / "results"
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return results_dir / timestamp


class AlignPage(BasePage):
    """Sequence Alignment Page"""

    def __init__(self, parent=None):
        super().__init__("序列比对", parent)

    def setup_ui(self):
        super().setup_ui()

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(8, 8, 8, 8)
        main_layout.setSpacing(6)

        main_splitter = QSplitter(Qt.Orientation.Vertical)
        main_splitter.setHandleWidth(8)
        main_splitter.setStyleSheet("""
            QSplitter::handle {
                background-color: #e0e0e0;
                border-radius: 4px;
            }
            QSplitter::handle:hover {
                background-color: #c0c0c0;
            }
        """)

        top_panel = QWidget()
        top_layout = QVBoxLayout(top_panel)
        top_layout.setContentsMargins(0, 0, 0, 0)
        top_layout.setSpacing(6)

        input_group = QGroupBox("输入")
        input_group.setStyleSheet("""
            QGroupBox {
                font-weight: 600;
                color: #333;
                border: 1px solid #ddd;
                border-radius: 6px;
                padding-top: 8px;
                margin-bottom: 4px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 6px 0 6px;
            }
        """)
        input_layout = QVBoxLayout(input_group)
        input_layout.setSpacing(6)
        input_layout.setContentsMargins(10, 6, 10, 10)

        file_layout = QHBoxLayout()
        file_layout.setSpacing(6)
        self.input_file = QLineEdit()
        self.input_file.setPlaceholderText("选择 FASTA 文件...")
        self.input_file.setFixedHeight(28)
        self.input_file.setStyleSheet("""
            QLineEdit {
                border: 1px solid #ddd;
                border-radius: 4px;
                padding: 0 8px;
                font-size: 12px;
            }
            QLineEdit:focus {
                border-color: #336699;
                outline: none;
            }
        """)
        btn_browse = QPushButton("浏览")
        btn_browse.setFixedSize(70, 28)
        btn_browse.setStyleSheet("""
            QPushButton {
                background-color: #336699;
                color: white;
                border: none;
                border-radius: 4px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #244a73;
            }
        """)
        btn_browse.clicked.connect(lambda: self.browse_file(self.input_file))
        file_layout.addWidget(self.input_file, 1)
        file_layout.addWidget(btn_browse)
        input_layout.addLayout(file_layout)

        clipboard_layout = QHBoxLayout()
        clipboard_layout.setSpacing(6)
        btn_clipboard = QPushButton("从剪贴板粘贴")
        btn_clipboard.setFixedHeight(26)
        btn_clipboard.setStyleSheet("""
            QPushButton {
                background-color: #f0f0f0;
                color: #333;
                border: 1px solid #ddd;
                border-radius: 4px;
                font-size: 12px;
                padding: 0 12px;
            }
            QPushButton:hover {
                background-color: #e8e8e8;
            }
        """)
        btn_clipboard.clicked.connect(self.paste_from_clipboard)
        clipboard_layout.addWidget(btn_clipboard)
        clipboard_layout.addStretch(1)
        input_layout.addLayout(clipboard_layout)

        self.paste_area = QTextEdit()
        self.paste_area.setPlaceholderText("粘贴 FASTA 格式序列...")
        self.paste_area.setMaximumHeight(70)
        self.paste_area.setFont(QFont("Consolas", 10))
        self.paste_area.setStyleSheet("""
            QTextEdit {
                border: 1px solid #ddd;
                border-radius: 4px;
                font-family: 'Consolas', monospace;
                font-size: 11px;
            }
            QTextEdit:focus {
                border-color: #336699;
                outline: none;
            }
        """)
        input_layout.addWidget(self.paste_area)

        top_layout.addWidget(input_group)

        option_group = QGroupBox("比对选项")
        option_group.setStyleSheet("""
            QGroupBox {
                font-weight: 600;
                color: #333;
                border: 1px solid #ddd;
                border-radius: 6px;
                padding-top: 8px;
                margin-bottom: 4px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 6px 0 6px;
            }
        """)
        option_layout = QGridLayout(option_group)
        option_layout.setSpacing(8)
        option_layout.setContentsMargins(10, 6, 10, 10)

        option_layout.addWidget(QLabel("比对方法:"), 0, 0)
        self.method_combo = QComboBox()
        self.method_combo.addItems(["自动检测", "Clustal Omega", "Needleman-Wunsch"])
        self.method_combo.setFixedHeight(26)
        self.method_combo.setStyleSheet("""
            QComboBox {
                border: 1px solid #ddd;
                border-radius: 4px;
                padding: 2px 20px 2px 8px;
                font-size: 12px;
                min-width: 150px;
            }
            QComboBox:focus {
                border-color: #336699;
            }
            QComboBox::drop-down {
                border-left: none;
            }
        """)
        option_layout.addWidget(self.method_combo, 0, 1)

        option_layout.addWidget(QLabel("Gap 开口:"), 0, 2)
        self.gap_open = QLineEdit("-10")
        self.gap_open.setFixedSize(60, 26)
        self.gap_open.setStyleSheet("""
            QLineEdit {
                border: 1px solid #ddd;
                border-radius: 4px;
                padding: 0 6px;
                font-size: 12px;
                text-align: center;
            }
            QLineEdit:focus {
                border-color: #336699;
                outline: none;
            }
        """)
        option_layout.addWidget(self.gap_open, 0, 3)

        option_layout.addWidget(QLabel("Gap 延长:"), 0, 4)
        self.gap_extend = QLineEdit("-1")
        self.gap_extend.setFixedSize(60, 26)
        self.gap_extend.setStyleSheet("""
            QLineEdit {
                border: 1px solid #ddd;
                border-radius: 4px;
                padding: 0 6px;
                font-size: 12px;
                text-align: center;
            }
            QLineEdit:focus {
                border-color: #336699;
                outline: none;
            }
        """)
        option_layout.addWidget(self.gap_extend, 0, 5)

        option_layout.addWidget(QLabel("矩阵格式:"), 1, 0)
        self.matrix_format = QComboBox()
        self.matrix_format.addItems(["UniProt 格式", "简洁格式"])
        self.matrix_format.setFixedHeight(26)
        self.matrix_format.setStyleSheet("""
            QComboBox {
                border: 1px solid #ddd;
                border-radius: 4px;
                padding: 2px 20px 2px 8px;
                font-size: 12px;
                min-width: 120px;
            }
            QComboBox:focus {
                border-color: #336699;
            }
        """)
        option_layout.addWidget(self.matrix_format, 1, 1)

        option_layout.addWidget(QLabel(), 1, 2, 1, 4)

        top_layout.addWidget(option_group)

        btn_align = QPushButton("开始比对")
        btn_align.setFixedHeight(36)
        btn_align.setStyleSheet("""
            QPushButton {
                background-color: #22c55e;
                color: white;
                font-size: 14px;
                font-weight: 600;
                border: none;
                border-radius: 6px;
                padding: 8px 24px;
            }
            QPushButton:hover {
                background-color: #16a34a;
            }
            QPushButton:pressed {
                background-color: #15803d;
            }
        """)
        btn_align.clicked.connect(self.execute_alignment)
        top_layout.addWidget(btn_align, alignment=Qt.AlignmentFlag.AlignCenter)

        main_splitter.addWidget(top_panel)

        bottom_panel = QWidget()
        bottom_layout = QVBoxLayout(bottom_panel)
        bottom_layout.setContentsMargins(0, 0, 0, 0)
        bottom_layout.setSpacing(6)

        result_tab = QTabWidget()
        result_tab.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #e0e0e0;
                border-radius: 6px;
                background: white;
            }
            QTabBar::tab {
                background: #f5f5f5;
                padding: 10px 20px;
                margin-right: 2px;
                margin-bottom: -1px;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
                font-size: 13px;
                font-weight: 500;
                color: #666;
            }
            QTabBar::tab:selected {
                background: white;
                color: #336699;
                font-weight: 600;
                border: 1px solid #e0e0e0;
                border-bottom: 2px solid #336699;
            }
            QTabBar::tab:hover {
                background: #eeeeee;
            }
        """)

        msa_widget = self._create_msa_table_widget()
        result_tab.addTab(msa_widget, "MSA 比对结果")

        matrix_widget = self._create_matrix_widget()
        result_tab.addTab(matrix_widget, "Identity Matrix")

        bottom_layout.addWidget(result_tab, 1)

        btn_layout = self._create_button_layout()
        bottom_layout.addLayout(btn_layout)

        main_splitter.addWidget(bottom_panel)
        
        main_splitter.setStretchFactor(0, 1)
        main_splitter.setStretchFactor(1, 4)

        main_layout.addWidget(main_splitter, 1)

        info_label = QLabel()
        info_label.setTextFormat(Qt.TextFormat.RichText)
        info_label.setText(
            "<b>说明：</b> 序列比对使用 Clustal Omega 算法（如果可用），"
            "否则使用 Biopython 的 Needleman-Wunsch 算法。"
        )
        info_label.setStyleSheet("color: #666; font-size: 11px; padding: 4px 0;")
        info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(info_label)

        self.layout.addLayout(main_layout)

        self._original_records = []
        self._aligned_records = []
        self._identity_matrix = []
        self._alignment_text = ""
        self._msa_text = ""
        self._last_results_dir = ""

    def _create_msa_table_widget(self) -> QWidget:
        """创建 MSA 表格显示组件"""
        msa_widget = QWidget()
        msa_layout = QVBoxLayout(msa_widget)
        msa_layout.setContentsMargins(0, 0, 0, 0)
        msa_layout.setSpacing(0)
        
        self.msa_stacked = QStackedWidget()
        
        self.msa_placeholder = QLabel("请先执行序列比对")
        self.msa_placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.msa_placeholder.setStyleSheet("""
            QLabel {
                color: #999;
                font-size: 16px;
                font-style: italic;
            }
        """)
        self.msa_stacked.addWidget(self.msa_placeholder)
        
        self.msa_scroll = QScrollArea()
        self.msa_scroll.setWidgetResizable(True)
        self.msa_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.msa_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.msa_scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: #ffffff;
            }
            QScrollBar:vertical {
                width: 10px;
                background: #f5f5f5;
            }
            QScrollBar::handle:vertical {
                background: #c0c0c0;
                border-radius: 5px;
            }
            QScrollBar::handle:vertical:hover {
                background: #a0a0a0;
            }
            QScrollBar:horizontal {
                height: 10px;
                background: #f5f5f5;
            }
            QScrollBar::handle:horizontal {
                background: #c0c0c0;
                border-radius: 5px;
            }
            QScrollBar::handle:horizontal:hover {
                background: #a0a0a0;
            }
        """)
        
        self.msa_table = QTableWidget()
        self.msa_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.msa_table.setSelectionMode(QTableWidget.SelectionMode.NoSelection)
        self.msa_table.verticalHeader().setVisible(False)
        self.msa_table.horizontalHeader().setVisible(False)
        self.msa_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Fixed)
        self.msa_table.verticalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Fixed)
        self.msa_table.setFont(QFont("Consolas", 10))
        self.msa_table.setShowGrid(False)
        self.msa_table.setStyleSheet("""
            QTableWidget {
                background-color: #ffffff;
                border: none;
                gridline-color: transparent;
            }
            QTableWidget::item {
                padding: 1px 2px;
                text-align: center;
            }
        """)
        
        self.msa_scroll.setWidget(self.msa_table)
        self.msa_stacked.addWidget(self.msa_scroll)
        
        msa_layout.addWidget(self.msa_stacked)
        
        return msa_widget

    def _create_matrix_widget(self) -> QWidget:
        """创建 Matrix 表格组件"""
        matrix_widget = QWidget()
        matrix_layout = QVBoxLayout(matrix_widget)
        matrix_layout.setContentsMargins(0, 0, 0, 0)
        matrix_layout.setSpacing(0)
        
        self.matrix_table = QTableWidget()
        self.matrix_table.setFont(QFont("Segoe UI", 11))
        self.matrix_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.matrix_table.setSelectionMode(QTableWidget.SelectionMode.NoSelection)
        self.matrix_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectItems)
        self.matrix_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        self.matrix_table.verticalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        self.matrix_table.horizontalHeader().setMinimumSectionSize(80)
        self.matrix_table.verticalHeader().setMinimumSectionSize(60)
        self.matrix_table.setStyleSheet("""
            QTableWidget {
                gridline-color: #e0e0e0;
                border: 1px solid #e0e0e0;
                border-radius: 6px;
            }
            QHeaderView::section {
                background: linear-gradient(to bottom, #f8f9fa, #e9ecef);
                color: #495057;
                font-weight: 600;
                padding: 8px 12px;
                border: none;
                border-bottom: 2px solid #dee2e6;
                border-right: 1px solid #dee2e6;
            }
            QHeaderView::section:last {
                border-right: none;
            }
            QTableWidget QScrollBar:vertical {
                width: 8px;
                background: #f5f5f5;
            }
            QTableWidget QScrollBar::handle:vertical {
                background: #c0c0c0;
                border-radius: 4px;
            }
            QTableWidget QScrollBar:horizontal {
                height: 8px;
                background: #f5f5f5;
            }
            QTableWidget QScrollBar::handle:horizontal {
                background: #c0c0c0;
                border-radius: 4px;
            }
        """)
        
        matrix_layout.addWidget(self.matrix_table)
        
        self.matrix_legend = QWidget()
        legend_layout = QHBoxLayout(self.matrix_legend)
        legend_layout.setSpacing(16)
        legend_layout.setContentsMargins(12, 8, 12, 8)
        
        legend_items = [
            ("#c23b22", "90-100%"),
            ("#e87d0d", "70-89%"),
            ("#f7b801", "50-69%"),
            ("#fde047", "30-49%"),
            ("#86efac", "15-29%"),
            ("#16a34a", "0-14%"),
        ]
        
        for color, label in legend_items:
            legend_item = QWidget()
            item_layout = QHBoxLayout(legend_item)
            item_layout.setSpacing(4)
            
            color_box = QFrame()
            color_box.setFixedSize(16, 14)
            color_box.setStyleSheet(f"background-color: {color}; border-radius: 2px;")
            item_layout.addWidget(color_box)
            
            label_widget = QLabel(label)
            label_widget.setStyleSheet("font-size: 11px; color: #666;")
            item_layout.addWidget(label_widget)
            
            legend_layout.addWidget(legend_item)
        
        legend_layout.addStretch(1)
        matrix_layout.addWidget(self.matrix_legend)
        
        return matrix_widget

    def _create_button_layout(self) -> QHBoxLayout:
        """创建按钮布局"""
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(8)
        btn_layout.setContentsMargins(8, 0, 8, 0)

        btn_copy = QPushButton("复制结果")
        btn_copy.setFixedHeight(28)
        btn_copy.setStyleSheet("""
            QPushButton {
                background-color: #f5f5f5;
                color: #333;
                border: 1px solid #ddd;
                border-radius: 4px;
                font-size: 12px;
                padding: 0 16px;
            }
            QPushButton:hover {
                background-color: #e8e8e8;
            }
        """)
        btn_copy.clicked.connect(self.copy_result)

        btn_save = QPushButton("保存结果")
        btn_save.setFixedHeight(28)
        btn_save.setStyleSheet("""
            QPushButton {
                background-color: #f5f5f5;
                color: #333;
                border: 1px solid #ddd;
                border-radius: 4px;
                font-size: 12px;
                padding: 0 16px;
            }
            QPushButton:hover {
                background-color: #e8e8e8;
            }
        """)
        btn_save.clicked.connect(self.save_result)

        btn_copy_matrix = QPushButton("复制矩阵")
        btn_copy_matrix.setFixedHeight(28)
        btn_copy_matrix.setStyleSheet("""
            QPushButton {
                background-color: #f5f5f5;
                color: #333;
                border: 1px solid #ddd;
                border-radius: 4px;
                font-size: 12px;
                padding: 0 16px;
            }
            QPushButton:hover {
                background-color: #e8e8e8;
            }
        """)
        btn_copy_matrix.clicked.connect(self.copy_matrix)

        btn_save_matrix = QPushButton("保存矩阵")
        btn_save_matrix.setFixedHeight(28)
        btn_save_matrix.setStyleSheet("""
            QPushButton {
                background-color: #f5f5f5;
                color: #333;
                border: 1px solid #ddd;
                border-radius: 4px;
                font-size: 12px;
                padding: 0 16px;
            }
            QPushButton:hover {
                background-color: #e8e8e8;
            }
        """)
        btn_save_matrix.clicked.connect(self.save_matrix)

        btn_export_html = QPushButton("导出 HTML 报告")
        btn_export_html.setFixedHeight(28)
        btn_export_html.setStyleSheet("""
            QPushButton {
                background-color: #336699;
                color: white;
                border: none;
                border-radius: 4px;
                font-size: 12px;
                font-weight: 500;
                padding: 0 16px;
            }
            QPushButton:hover {
                background-color: #244a73;
            }
        """)
        btn_export_html.clicked.connect(self.export_html_report)

        btn_layout.addWidget(btn_copy)
        btn_layout.addWidget(btn_save)
        btn_layout.addWidget(btn_copy_matrix)
        btn_layout.addWidget(btn_save_matrix)
        btn_layout.addWidget(btn_export_html)
        btn_layout.addStretch(1)
        
        return btn_layout

    def browse_file(self, line_edit):
        """浏览选择文件"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择 FASTA 文件", "",
            "FASTA Files (*.fa *.fasta *.fna);;All Files (*)"
        )
        if file_path:
            line_edit.setText(file_path)

    def paste_from_clipboard(self):
        """从剪贴板粘贴序列"""
        clipboard = QApplication.clipboard()
        text = clipboard.text()
        if text:
            self.paste_area.setPlainText(text)
            self.log("已从剪贴板粘贴序列")
        else:
            QMessageBox.information(self, "提示", "剪贴板中没有文本内容")

    def _get_input_records(self):
        """获取输入序列"""
        file_path = self.input_file.text().strip()
        paste_text = self.paste_area.toPlainText().strip()

        records = []

        if paste_text:
            from seqbox.io.fasta import parse_fasta_string
            records = parse_fasta_string(paste_text)
            if not records:
                raise ValueError("粘贴的文本无法解析为 FASTA 格式")
            self.log(f"使用粘贴的序列: {len(records)} 条")
        elif file_path:
            reader = FastaReader(file_path)
            records = reader.read_all()
            if not records:
                raise ValueError(f"文件为空或无法解析: {file_path}")
            self.log(f"读取文件 {len(records)} 条序列: {file_path}")
        else:
            raise ValueError("请选择输入文件或粘贴序列内容")

        if len(records) < 2:
            raise ValueError("比对需要至少 2 条序列")

        return records

    def execute_alignment(self):
        """执行序列比对"""
        try:
            records = self._get_input_records()

            method_map = {
                0: "auto",
                1: "clustalo",
                2: "needleman-wunsch",
            }
            method = method_map[self.method_combo.currentIndex()]

            try:
                gap_open = float(self.gap_open.text())
                gap_extend = float(self.gap_extend.text())
            except ValueError:
                gap_open = -10.0
                gap_extend = -1.0

            self.log(f"开始比对 ({len(records)} 条序列, 方法: {method})...")

            from seqbox.alignment import align_sequences, format_identity_matrix_uniprot, format_msa_text

            self._original_records = records

            aligned_records, align_text, identity_matrix = align_sequences(
                records,
                method=method,
                gap_open=gap_open,
                gap_extend=gap_extend,
            )

            self._aligned_records = aligned_records
            self._alignment_text = align_text
            self._identity_matrix = identity_matrix

            msa_text = format_msa_text(records, aligned_records)
            self._msa_text = msa_text

            self._update_msa_display(records, aligned_records)

            self._update_matrix_display(records, identity_matrix)

            results_dir = get_default_results_dir()
            results_dir.mkdir(parents=True, exist_ok=True)
            self._last_results_dir = str(results_dir)

            aligned_fasta_path = results_dir / "aligned.fasta"
            with open(aligned_fasta_path, "w", encoding="utf-8") as f:
                for rec in aligned_records:
                    f.write(f">{rec.id}")
                    if rec.description:
                        f.write(f" {rec.description}")
                    f.write(f"\n{rec.seq}\n")

            matrix_text = format_identity_matrix_uniprot(records, identity_matrix)
            matrix_path = results_dir / "identity_matrix.txt"
            with open(matrix_path, "w", encoding="utf-8") as f:
                f.write(matrix_text)

            msa_path = results_dir / "msa_alignment.txt"
            with open(msa_path, "w", encoding="utf-8") as f:
                f.write(self._msa_text)

            self.log(f"比对完成！结果已保存到: {results_dir.name}")
            self.log(f"  - aligned.fasta")
            self.log(f"  - identity_matrix.txt")
            self.log(f"  - msa_alignment.txt")

        except Exception as e:
            QMessageBox.critical(self, "错误", f"比对失败: {str(e)}")
            self.log(f"比对错误: {e}")

    def _update_msa_display(self, records, aligned_records):
        """使用 QTableWidget 显示 MSA 比对结果"""
        self.msa_stacked.setCurrentIndex(1)
        
        seq_ids = [r.id for r in records]
        seqs = [r.seq for r in aligned_records]
        align_len = len(seqs[0]) if seqs else 0
        block_size = 50
        
        num_rows = len(records) + 2
        num_blocks = (align_len + block_size - 1) // block_size
        total_cols = 1 + num_blocks * block_size
        
        self.msa_table.setRowCount(num_rows)
        self.msa_table.setColumnCount(total_cols)
        self.msa_table.setColumnWidth(0, 140)
        self.msa_table.setRowHeight(0, 16)
        
        for row in range(num_rows):
            self.msa_table.setRowHeight(row, 18)
        
        for col_idx in range(total_cols):
            self.msa_table.setColumnWidth(col_idx, 11)
        
        STRONG_SIMILARITY = {
            ('A', 'G'), ('G', 'A'), ('S', 'T'), ('T', 'S'),
            ('D', 'E'), ('E', 'D'), ('N', 'Q'), ('Q', 'N'),
            ('K', 'R'), ('R', 'K'), ('I', 'L'), ('L', 'I'),
            ('I', 'V'), ('V', 'I'), ('L', 'V'), ('V', 'L'),
            ('F', 'Y'), ('Y', 'F'),
        }
        WEAK_SIMILARITY = {
            ('A', 'S'), ('S', 'A'), ('A', 'T'), ('T', 'A'), ('S', 'N'), ('N', 'S'),
            ('D', 'N'), ('N', 'D'), ('E', 'Q'), ('Q', 'E'), ('D', 'Q'), ('Q', 'D'), ('E', 'N'), ('N', 'E'),
            ('R', 'Q'), ('Q', 'R'), ('K', 'Q'), ('Q', 'K'), ('R', 'E'), ('E', 'R'), ('K', 'E'), ('E', 'K'),
            ('V', 'M'), ('M', 'V'), ('L', 'M'), ('M', 'L'), ('I', 'M'), ('M', 'I'),
            ('F', 'W'), ('W', 'F'), ('Y', 'W'), ('W', 'Y'), ('F', 'H'), ('H', 'F'), ('Y', 'H'), ('H', 'Y'),
            ('A', 'V'), ('V', 'A'), ('G', 'V'), ('V', 'G'), ('G', 'S'), ('S', 'G'),
        }
        
        for block_idx in range(num_blocks):
            start = block_idx * block_size
            end = min(start + block_size, align_len)
            
            for pos in range(start, end):
                col = 1 + block_idx * block_size + (pos - start)
                
                if pos % 10 == 0 and block_idx == 0:
                    item = QTableWidgetItem(str(pos + 1))
                else:
                    item = QTableWidgetItem("")
                item.setBackground(QColor("#f8f9fa"))
                item.setForeground(QColor("#999"))
                item.setFont(QFont("Segoe UI", 7))
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.msa_table.setItem(0, col, item)
                
                for row_idx, seq in enumerate(seqs):
                    aa = seq[pos]
                    col_residues = [s[pos] for s in seqs]
                    
                    if aa == '-':
                        bg_color = QColor("#f3f4f6")
                        fg_color = QColor("#9ca3af")
                    else:
                        non_gap = [r for r in col_residues if r != '-']
                        if len(set(non_gap)) == 1:
                            bg_color = QColor("#1e3a8a")
                            fg_color = QColor("#ffffff")
                        else:
                            first = non_gap[0]
                            if (first, aa) in STRONG_SIMILARITY or first == aa:
                                bg_color = QColor("#3b82f6")
                                fg_color = QColor("#ffffff")
                            elif (first, aa) in WEAK_SIMILARITY:
                                bg_color = QColor("#93c5fd")
                                fg_color = QColor("#1f2937")
                            else:
                                bg_color = QColor("#ffffff")
                                fg_color = QColor("#1f2937")
                    
                    item = QTableWidgetItem(aa)
                    item.setBackground(bg_color)
                    item.setForeground(fg_color)
                    item.setFont(QFont("Consolas", 10, QFont.Weight.Medium))
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                    self.msa_table.setItem(row_idx + 1, col, item)
                
                non_gap = [r for r in col_residues if r != '-']
                if len(non_gap) == 0:
                    sym = ' '
                elif len(set(non_gap)) == 1:
                    sym = '*'
                else:
                    first = non_gap[0]
                    all_match = all((first == r) or ((first, r) in STRONG_SIMILARITY) for r in non_gap)
                    if all_match:
                        sym = ':'
                    else:
                        all_weak = all(
                            (first == r) or ((first, r) in STRONG_SIMILARITY) or ((first, r) in WEAK_SIMILARITY)
                            for r in non_gap
                        )
                        sym = '.' if all_weak else ' '
                
                item = QTableWidgetItem(sym)
                if sym == '*':
                    item.setForeground(QColor("#c23b22"))
                elif sym == ':':
                    item.setForeground(QColor("#e87d0d"))
                elif sym == '.':
                    item.setForeground(QColor("#f7b801"))
                else:
                    item.setForeground(QColor("#9ca3af"))
                item.setFont(QFont("Consolas", 9, QFont.Weight.Bold))
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.msa_table.setItem(len(records) + 1, col, item)
        
        for row_idx, seq_id in enumerate(seq_ids):
            display_id = seq_id[:18] + "..." if len(seq_id) > 21 else seq_id
            item = QTableWidgetItem(display_id)
            item.setBackground(QColor("#f3f4f6"))
            item.setForeground(QColor("#1e40af"))
            item.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
            item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            self.msa_table.setItem(row_idx + 1, 0, item)
        
        item = QTableWidgetItem("")
        item.setBackground(QColor("#f3f4f6"))
        self.msa_table.setItem(0, 0, item)
        
        item = QTableWidgetItem("")
        item.setBackground(QColor("#f3f4f6"))
        self.msa_table.setItem(len(records) + 1, 0, item)

    def _update_matrix_display(self, records, identity_matrix):
        """更新 matrix 显示表格"""
        n = len(records)

        self.matrix_table.clear()
        self.matrix_table.setRowCount(n)
        self.matrix_table.setColumnCount(n)
        
        headers = [r.id[:20] + "..." if len(r.id) > 23 else r.id for r in records]
        self.matrix_table.setHorizontalHeaderLabels(headers)
        self.matrix_table.setVerticalHeaderLabels(headers)

        for i in range(n):
            for j in range(n):
                val = identity_matrix[i][j]
                item = QTableWidgetItem(f"{val:.1f}%")
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

                if i == j:
                    item.setBackground(QColor("#f0f0f0"))
                    item.setForeground(QColor("#666666"))
                    item.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
                elif val >= 90:
                    item.setBackground(QColor("#c23b22"))
                    item.setForeground(QColor("#ffffff"))
                    item.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
                elif val >= 70:
                    item.setBackground(QColor("#e87d0d"))
                    item.setForeground(QColor("#ffffff"))
                    item.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
                elif val >= 50:
                    item.setBackground(QColor("#f7b801"))
                    item.setForeground(QColor("#1a1a1a"))
                    item.setFont(QFont("Segoe UI", 11, QFont.Weight.Medium))
                elif val >= 30:
                    item.setBackground(QColor("#fde047"))
                    item.setForeground(QColor("#1a1a1a"))
                    item.setFont(QFont("Segoe UI", 11, QFont.Weight.Medium))
                elif val >= 15:
                    item.setBackground(QColor("#86efac"))
                    item.setForeground(QColor("#1a1a1a"))
                    item.setFont(QFont("Segoe UI", 11, QFont.Weight.Medium))
                else:
                    item.setBackground(QColor("#16a34a"))
                    item.setForeground(QColor("#ffffff"))
                    item.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))

                self.matrix_table.setItem(i, j, item)
        
        self.matrix_table.resizeColumnsToContents()
        self.matrix_table.resizeRowsToContents()

    def copy_result(self):
        """复制 MSA 比对结果"""
        if self._msa_text:
            clipboard = QApplication.clipboard()
            clipboard.setText(self._msa_text)
            self.log("MSA 结果已复制到剪贴板")
        else:
            self.log("没有可复制的结果")

    def save_result(self):
        """保存 MSA 比对结果"""
        if not self._msa_text:
            self.log("没有可保存的结果")
            return

        file_path, _ = QFileDialog.getSaveFileName(
            self, "保存 MSA 结果", "msa_alignment.txt",
            "Text Files (*.txt);;All Files (*)"
        )
        if file_path:
            try:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(self._msa_text)
                self.log(f"MSA 结果已保存: {file_path}")
            except Exception as e:
                QMessageBox.critical(self, "错误", f"保存失败: {str(e)}")

    def copy_matrix(self):
        """复制 Identity Matrix"""
        if not self._identity_matrix:
            self.log("没有可复制的矩阵，请先执行比对")
            return

        try:
            from seqbox.alignment import format_identity_matrix_uniprot

            records = self._aligned_records
            matrix_format = self.matrix_format.currentIndex()
            is_shorter = (matrix_format == 1)

            matrix_text = format_identity_matrix_uniprot(
                records,
                self._identity_matrix,
                shorter=is_shorter,
            )

            clipboard = QApplication.clipboard()
            clipboard.setText(matrix_text)
            self.log("Identity Matrix 已复制到剪贴板")

        except Exception as e:
            QMessageBox.critical(self, "错误", f"复制失败: {str(e)}")

    def save_matrix(self):
        """保存 Identity Matrix"""
        if not self._identity_matrix:
            self.log("没有可保存的矩阵，请先执行比对")
            return

        file_path, _ = QFileDialog.getSaveFileName(
            self, "保存 Identity Matrix", "identity_matrix.txt",
            "Text Files (*.txt);;All Files (*)"
        )
        if file_path:
            try:
                from seqbox.alignment import format_identity_matrix_uniprot

                records = self._aligned_records
                matrix_format = self.matrix_format.currentIndex()
                is_shorter = (matrix_format == 1)

                matrix_text = format_identity_matrix_uniprot(
                    records,
                    self._identity_matrix,
                    shorter=is_shorter,
                )

                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(matrix_text)
                self.log(f"Identity Matrix 已保存: {file_path}")

            except Exception as e:
                QMessageBox.critical(self, "错误", f"保存失败: {str(e)}")

    def export_html_report(self):
        """导出 UniProt 风格的 HTML 报告"""
        if not self._aligned_records or not self._identity_matrix:
            self.log("没有可导出的数据，请先执行比对")
            return

        file_path, _ = QFileDialog.getSaveFileName(
            self, "导出 HTML 报告", "alignment_report.html",
            "HTML Files (*.html);;All Files (*)"
        )
        if file_path:
            try:
                from seqbox.alignment import generate_html_report

                html_report = generate_html_report(
                    records=self._original_records,
                    aligned_records=self._aligned_records,
                    matrix=self._identity_matrix,
                    title="Sequence Alignment Report"
                )

                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(html_report)
                
                self.log(f"HTML 报告已导出: {file_path}")
                QMessageBox.information(self, "导出成功", f"HTML 报告已成功导出到:\n{file_path}")

            except Exception as e:
                QMessageBox.critical(self, "错误", f"导出失败: {str(e)}")