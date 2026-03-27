"""
Seq_Box - 蛋白质理化分析页面

功能:
- FASTA序列理化性质分析
- 支持同一蛋白质多链模式
- 链数>10时确认提示
- 美观的结果展示
"""

from pathlib import Path
from PyQt6.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QLineEdit,
    QTextEdit, QCheckBox, QGroupBox, QWidget, QFileDialog, 
    QMessageBox, QGridLayout, QTableWidget, QTableWidgetItem,
    QHeaderView, QSplitter, QApplication
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QColor, QBrush

from .base_page import BasePage, COLORS


class ProteinPage(BasePage):
    """蛋白质理化分析页面"""
    
    def __init__(self, parent=None):
        super().__init__("蛋白质理化分析", parent)
        self.analysis_result = None
    
    def setup_ui(self):
        super().setup_ui()
        
        # 主布局使用分割器
        splitter = QSplitter(Qt.Orientation.Vertical)
        
        # 上半部分：输入区域
        input_widget = self._create_input_section()
        splitter.addWidget(input_widget)
        
        # 下半部分：结果展示
        result_widget = self._create_result_section()
        splitter.addWidget(result_widget)
        
        # 设置分割比例
        splitter.setSizes([400, 600])
        
        self.layout.addWidget(splitter)
    
    def _create_input_section(self):
        """创建输入区域"""
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)
        
        # 文件输入行
        file_group = QGroupBox("输入")
        file_layout = QVBoxLayout(file_group)
        
        # 文件选择
        file_row = QHBoxLayout()
        self.protein_input = QLineEdit()
        self.protein_input.setPlaceholderText("选择 FASTA 文件...")
        btn_browse = QPushButton("浏览...")
        btn_browse.clicked.connect(self._browse_file)
        file_row.addWidget(self.protein_input)
        file_row.addWidget(btn_browse)
        file_layout.addLayout(file_row)
        
        # 剪贴板按钮
        btn_clipboard = QPushButton("📋 从剪贴板粘贴")
        btn_clipboard.clicked.connect(self._paste_from_clipboard)
        file_layout.addWidget(btn_clipboard)
        
        # 粘贴区域
        self.paste_area = QTextEdit()
        self.paste_area.setPlaceholderText("粘贴 FASTA 序列...")
        self.paste_area.setMaximumHeight(150)
        self.paste_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        file_layout.addWidget(self.paste_area)
        
        layout.addWidget(file_group)
        
        # 选项区域
        options_group = QGroupBox("分析选项")
        options_layout = QHBoxLayout(options_group)
        options_layout.setSpacing(20)
        
        # 同一蛋白质选项
        self.same_protein_check = QCheckBox("同一蛋白质的多条链")
        self.same_protein_check.setChecked(True)
        self.same_protein_check.setToolTip("FASTA中的多条序列属于同一个蛋白质的不同链")
        options_layout.addWidget(self.same_protein_check)
        
        # 说明标签
        hint_label = QLabel("💡 提示: 链数超过10时会弹出确认对话框")
        hint_label.setStyleSheet(f"color: {COLORS['yellow']};")
        options_layout.addWidget(hint_label)
        options_layout.addStretch()
        
        # 分析按钮
        btn_analyze = QPushButton("🔬 开始分析")
        btn_analyze.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['purple']};
                color: {COLORS['bg_dark']};
                font-size: 13px;
                padding: 10px 24px;
                font-weight: bold;
            }}
        """)
        btn_analyze.clicked.connect(self._execute_analysis)
        options_layout.addWidget(btn_analyze)
        
        # 清除按钮
        btn_clear = QPushButton("🗑️ 清除")
        btn_clear.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['bg_light']};
                color: {COLORS['fg_bright']};
                border: 1px solid {COLORS['border']};
                font-size: 13px;
                padding: 10px 20px;
            }}
        """)
        btn_clear.clicked.connect(self._clear_results)
        options_layout.addWidget(btn_clear)
        
        layout.addWidget(options_group)
        
        return container
    
    def _create_result_section(self):
        """创建结果展示区域"""
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)
        
        # 标题栏带复制按钮
        header = QHBoxLayout()
        header.addWidget(QLabel("分析结果"))
        header.addStretch()
        
        btn_copy_csv = QPushButton("📊 复制表格")
        btn_copy_csv.setFixedWidth(90)
        btn_copy_csv.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['bg_light']};
                color: {COLORS['fg_bright']};
                border: 1px solid {COLORS['border']};
                border-radius: 4px;
                padding: 4px 8px;
                font-size: 11px;
            }}
        """)
        btn_copy_csv.clicked.connect(self._copy_result_csv)
        header.addWidget(btn_copy_csv)
        
        layout.addLayout(header)
        
        # 汇总信息卡片（已隐藏，信息直接显示在表格中）
        self.summary_card = QTextEdit()
        self.summary_card.setPlaceholderText("分析汇总信息将显示在这里...")
        self.summary_card.setMaximumHeight(0)
        self.summary_card.setVisible(False)
        self.summary_card.setReadOnly(True)
        
        # 详细数据表格
        self.result_table = QTableWidget()
        self.result_table.setColumnCount(8)
        self.result_table.setHorizontalHeaderLabels([
            "Name", "Len", "MW(Expasy)", "MW", "pI", "Ext.Coe", "Abs(Expasy)", "Abs"
        ])
        
        # 表格样式
        self.result_table.setStyleSheet(f"""
            QTableWidget {{
                background-color: {COLORS['bg_dark']};
                color: {COLORS['fg_bright']};
                border: 1px solid {COLORS['border']};
                border-radius: 8px;
                gridline-color: {COLORS['border']};
            }}
            QTableWidget::item {{
                padding: 8px;
                border-bottom: 1px solid {COLORS['border']};
                color: {COLORS['fg_bright']};
            }}
            QTableWidget::item:selected {{
                background-color: {COLORS['blue']};
                color: {COLORS['bg_dark']};
            }}
            QHeaderView::section {{
                background-color: {COLORS['bg_light']};
                color: {COLORS['fg_bright']};
                padding: 10px;
                border: none;
                border-bottom: 2px solid {COLORS['blue']};
                font-weight: bold;
            }}
        """)
        
        # 表头设置
        header = self.result_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
        self.result_table.setColumnWidth(0, 100)
        
        self.result_table.setAlternatingRowColors(False)
        self.result_table.verticalHeader().setVisible(False)
        self.result_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        
        layout.addWidget(self.result_table)
        
        return container
    
    def _browse_file(self):
        """浏览选择文件"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择 FASTA 文件", "",
            "FASTA Files (*.fa *.fasta *.fna);;All Files (*)"
        )
        if file_path:
            self.protein_input.setText(file_path)
    
    def _paste_from_clipboard(self):
        """从剪贴板粘贴"""
        clipboard = QApplication.clipboard()
        text = clipboard.text()
        if text:
            self.paste_area.setPlainText(text)
            self.log("已从剪贴板粘贴序列")
        else:
            QMessageBox.information(self, "提示", "剪贴板中没有文本内容")
    
    def _execute_analysis(self):
        """执行分析"""
        # 获取输入
        pasted_text = self.paste_area.toPlainText().strip()
        file_path = self.protein_input.text().strip()
        
        if pasted_text:
            input_source = "(剪贴板)"
            try:
                from ...protein.analysis import analyze_fasta_text
                result = analyze_fasta_text(pasted_text, same_protein=self.same_protein_check.isChecked())
            except Exception as e:
                QMessageBox.critical(self, "错误", f"分析失败: {str(e)}")
                return
        elif file_path:
            input_source = file_path
            if not Path(file_path).exists():
                QMessageBox.warning(self, "警告", "文件不存在")
                return
            try:
                from ...protein.analysis import analyze_fasta_file
                result = analyze_fasta_file(file_path, same_protein=self.same_protein_check.isChecked())
            except Exception as e:
                QMessageBox.critical(self, "错误", f"分析失败: {str(e)}")
                return
        else:
            QMessageBox.warning(self, "警告", "请选择文件或粘贴序列")
            return
        
        # 链数确认
        if result.chain_count > 10:
            reply = QMessageBox.question(
                self, "确认",
                f"检测到 {result.chain_count} 条序列，确认继续分析？",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply != QMessageBox.StandardButton.Yes:
                return
        
        self.analysis_result = result
        self._display_result(result)
        self.log(f"蛋白质分析完成: {result.chain_count} 条序列")
    
    def _display_result(self, result):
        """显示分析结果"""
        # 表格数据
        table_data = result.get_table_data()
        self.result_table.setRowCount(len(table_data))
        
        # 找到整体行的索引
        summary_row_idx = None
        
        for row_idx, row_data in enumerate(table_data):
            is_summary = row_data['type'] == 'summary'
            if is_summary:
                summary_row_idx = row_idx
            
            # 名称
            name_item = QTableWidgetItem(row_data['name'])
            self.result_table.setItem(row_idx, 0, name_item)
            
            # 长度
            self.result_table.setItem(row_idx, 1, QTableWidgetItem(f"{row_data['length']:,}"))
            
            # 分子量(Expasy)
            self.result_table.setItem(row_idx, 2, QTableWidgetItem(f"{row_data['mw_expasy']:,.2f}"))
            
            # 分子量(链汇总)
            self.result_table.setItem(row_idx, 3, QTableWidgetItem(f"{row_data['mw']:,.2f}"))
            
            # pI
            self.result_table.setItem(row_idx, 4, QTableWidgetItem(f"{row_data['pi']:.2f}"))
            
            # 消光系数
            self.result_table.setItem(row_idx, 5, QTableWidgetItem(f"{row_data['ext_coeff']:,}"))
            
            # 吸光度(Expasy)
            self.result_table.setItem(row_idx, 6, QTableWidgetItem(f"{row_data['abs_expasy']:.4f}"))
            
            # 吸光度(链汇总)
            self.result_table.setItem(row_idx, 7, QTableWidgetItem(f"{row_data['abs']:.4f}"))
        
        # 默认选中整体行（第一行）以高亮显示
        if summary_row_idx is not None:
            self.result_table.selectRow(summary_row_idx)
    
    def _format_summary_html(self, result):
        """格式化汇总信息为HTML"""
        mode_text = "同一蛋白质" if result.same_protein_mode else "多蛋白质"

        html = f"""
        <style>
            .container {{ font-family: 'Microsoft YaHei', sans-serif; line-height: 1.6; color: {COLORS['fg_bright']}; }}
            .header {{ font-size: 14px; margin-bottom: 8px; }}
            .label {{ color: {COLORS['fg']}; }}
            .value {{ color: {COLORS['blue']}; font-weight: bold; }}
            .highlight {{ color: {COLORS['purple']}; font-weight: bold; }}
            .sep {{ color: {COLORS['border']}; margin: 0 8px; }}
            .mode-title {{ color: {COLORS['yellow']}; font-weight: bold; font-size: 12px; }}
            .prop-label {{ color: {COLORS['fg']}; font-size: 12px; }}
            .prop-value {{ font-weight: bold; font-size: 12px; }}
        </style>
        <div class="container">
            <div class="header">
                <span class="label">📁 来源:</span> <span class="value">{result.input_file}</span>
                <span class="sep">|</span>
                <span class="label">模式:</span> <span class="highlight">{mode_text}</span>
                <span class="sep">|</span>
                <span class="label">序列数:</span> <span class="value">{result.chain_count}</span>
            </div>
        </div>
        """

        if result.is_multi_chain_protein():
            mp = result.data
            # Expasy模式（合并计算）
            html += f"""
            <div style="margin-top: 10px; padding: 10px; background-color: {COLORS['bg_light']}; border-radius: 6px; border-left: 3px solid {COLORS['green']};">
                <div class="mode-title">🧬 Expasy模式（合并序列计算）</div>
                <div style="margin-top: 6px;">
                    <span class="prop-label">总残基:</span> <span class="prop-value" style="color:{COLORS['green']};">{mp.total_length:,}</span> aa
                    <span class="sep">|</span>
                    <span class="prop-label">总分子量:</span> <span class="prop-value" style="color:{COLORS['blue']};">{mp.total_molecular_weight:,.2f}</span> Da
                    <span class="sep">|</span>
                    <span class="prop-label">pI:</span> <span class="prop-value" style="color:{COLORS['yellow']};">{mp.overall_pi:.2f}</span>
                    <span class="sep">|</span>
                    <span class="prop-label">吸光度:</span> <span class="prop-value" style="color:{COLORS['cyan']};">{mp.overall_absorbance:.4f}</span>
                    <span class="sep">|</span>
                    <span class="prop-label">GRAVY:</span> <span class="prop-value" style="color:{COLORS['purple']};">{mp.overall_gravy:.4f}</span>
                </div>
            </div>
            """
            # 链汇总模式
            html += f"""
            <div style="margin-top: 8px; padding: 10px; background-color: {COLORS['bg_light']}; border-radius: 6px; border-left: 3px solid {COLORS['yellow']};">
                <div class="mode-title">📊 链汇总模式（各链分别+1水）</div>
                <div style="margin-top: 6px;">
                    <span class="prop-label">总残基:</span> <span class="prop-value" style="color:{COLORS['green']};">{mp.total_length:,}</span> aa
                    <span class="sep">|</span>
                    <span class="prop-label">总分子量:</span> <span class="prop-value" style="color:{COLORS['blue']};">{mp.summed_molecular_weight:,.2f}</span> Da
                    <span class="sep">|</span>
                    <span class="prop-label">吸光度:</span> <span class="prop-value" style="color:{COLORS['cyan']};">{mp.summed_absorbance:.4f}</span>
                </div>
            </div>
            """

        return html
    
    def _copy_result_csv(self):
        """复制结果为CSV"""
        if not self.analysis_result:
            QMessageBox.warning(self, "提示", "没有可复制的分析结果")
            return
        
        table_data = self.analysis_result.get_table_data()
        lines = ["Name,Len,MW(Expasy),MW,pI,Ext.Coe,Abs(Expasy),Abs"]
        for row in table_data:
            line = f"{row['name']},{row['length']},{row['mw_expasy']:.2f},{row['mw']:.2f},{row['pi']:.2f},{row['ext_coeff']},{row['abs_expasy']:.4f},{row['abs']:.4f}"
            lines.append(line)
        
        csv_text = "\n".join(lines)
        clipboard = QApplication.clipboard()
        clipboard.setText(csv_text)
        QMessageBox.information(self, "提示", "表格已复制为CSV格式")
        self.log("分析结果已复制为CSV")
    
    def _clear_results(self):
        """清除结果，重置界面"""
        # 清空表格
        self.result_table.setRowCount(0)
        
        # 清空分析结果
        self.analysis_result = None
        
        # 清空输入
        self.protein_input.clear()
        self.paste_area.clear()
        
        self.log("界面已重置")
