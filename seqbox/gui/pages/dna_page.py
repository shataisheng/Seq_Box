"""
Seq_Box - DNA 操作页面
"""

from PyQt6.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QLineEdit,
    QTextEdit, QComboBox, QSpinBox, QCheckBox, QGroupBox,
    QTabWidget, QWidget, QGridLayout
)
from PyQt6.QtCore import Qt

from .base_page import BasePage, COLORS


class DnaPage(BasePage):
    """DNA 操作页面"""
    
    def __init__(self, parent=None):
        super().__init__("DNA 操作", parent)
    
    def setup_ui(self):
        super().setup_ui()
        
        # Tab 容器
        self.tabs = QTabWidget()
        
        # 各个功能 Tab
        self.tabs.addTab(self.create_basic_tab(), "🔄 基础转换")
        self.tabs.addTab(self.create_translate_tab(), "🧬 翻译")
        self.tabs.addTab(self.create_orf_tab(), "🔍 ORF 搜索")
        self.tabs.addTab(self.create_stats_tab(), "📊 统计分析")
        
        self.layout.addWidget(self.tabs)
    
    def create_basic_tab(self):
        """基础转换 Tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)
        
        # 输入
        input_group = QGroupBox("输入序列")
        input_layout = QVBoxLayout(input_group)
        self.basic_input = QTextEdit()
        self.basic_input.setPlaceholderText("输入 DNA 序列...")
        self.basic_input.setMaximumHeight(120)
        input_layout.addWidget(self.basic_input)
        layout.addWidget(input_group)
        
        # 操作按钮
        btn_layout = QHBoxLayout()
        
        btn_comp = QPushButton("互补链")
        btn_comp.clicked.connect(lambda: self.do_basic_op('complement'))
        btn_layout.addWidget(btn_comp)
        
        btn_rc = QPushButton("反向互补")
        btn_rc.clicked.connect(lambda: self.do_basic_op('reverse_complement'))
        btn_layout.addWidget(btn_rc)
        
        btn_transcribe = QPushButton("转录 (→RNA)")
        btn_transcribe.clicked.connect(lambda: self.do_basic_op('transcribe'))
        btn_layout.addWidget(btn_transcribe)
        
        btn_reverse_transcribe = QPushButton("逆转录 (→DNA)")
        btn_reverse_transcribe.clicked.connect(lambda: self.do_basic_op('reverse_transcribe'))
        btn_layout.addWidget(btn_reverse_transcribe)
        
        btn_layout.addStretch()
        layout.addLayout(btn_layout)
        
        # 输出
        output_group = QGroupBox("结果")
        output_layout = QVBoxLayout(output_group)
        self.basic_output = QTextEdit()
        self.basic_output.setReadOnly(True)
        self.basic_output.setPlaceholderText("结果将显示在这里...")
        output_layout.addWidget(self.basic_output)
        layout.addWidget(output_group)
        
        layout.addStretch()
        return tab
    
    def create_translate_tab(self):
        """翻译 Tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)
        
        # 输入
        input_group = QGroupBox("输入序列")
        input_layout = QVBoxLayout(input_group)
        self.translate_input = QTextEdit()
        self.translate_input.setPlaceholderText("输入 DNA/RNA 序列...")
        self.translate_input.setMaximumHeight(120)
        input_layout.addWidget(self.translate_input)
        layout.addWidget(input_group)
        
        # 选项
        options_layout = QHBoxLayout()
        
        options_layout.addWidget(QLabel("密码子表:"))
        self.translate_table = QComboBox()
        self.translate_table.addItems([
            "标准密码子表",
            "脊椎动物线粒体",
            "细菌",
            "酵母线粒体"
        ])
        options_layout.addWidget(self.translate_table)
        
        self.translate_to_stop = QCheckBox("遇到终止密码子停止")
        self.translate_to_stop.setChecked(True)
        options_layout.addWidget(self.translate_to_stop)
        
        options_layout.addStretch()
        layout.addLayout(options_layout)
        
        # 操作按钮
        btn_layout = QHBoxLayout()
        
        btn_translate = QPushButton("翻译")
        btn_translate.clicked.connect(self.do_translate)
        btn_layout.addWidget(btn_translate)
        
        btn_six_frames = QPushButton("六框翻译")
        btn_six_frames.setStyleSheet(f"background-color: {COLORS['cyan']};")
        btn_six_frames.clicked.connect(self.do_six_frames)
        btn_layout.addWidget(btn_six_frames)
        
        btn_layout.addStretch()
        layout.addLayout(btn_layout)
        
        # 输出
        output_group = QGroupBox("翻译结果")
        output_layout = QVBoxLayout(output_group)
        self.translate_output = QTextEdit()
        self.translate_output.setReadOnly(True)
        self.translate_output.setPlaceholderText("蛋白质序列将显示在这里...")
        output_layout.addWidget(self.translate_output)
        layout.addWidget(output_group)
        
        layout.addStretch()
        return tab
    
    def create_orf_tab(self):
        """ORF 搜索 Tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)
        
        # 输入
        input_group = QGroupBox("输入序列")
        input_layout = QVBoxLayout(input_group)
        self.orf_input = QTextEdit()
        self.orf_input.setPlaceholderText("输入 DNA 序列...")
        self.orf_input.setMaximumHeight(120)
        input_layout.addWidget(self.orf_input)
        layout.addWidget(input_group)
        
        # 选项
        options_group = QGroupBox("搜索选项")
        options_layout = QGridLayout(options_group)
        
        options_layout.addWidget(QLabel("密码子表:"), 0, 0)
        self.orf_table = QComboBox()
        self.orf_table.addItems(["标准密码子表", "脊椎动物线粒体", "细菌", "酵母线粒体"])
        options_layout.addWidget(self.orf_table, 0, 1)
        
        options_layout.addWidget(QLabel("最小蛋白质长度 (aa):"), 1, 0)
        self.orf_min_len = QSpinBox()
        self.orf_min_len.setRange(10, 9999)
        self.orf_min_len.setValue(100)
        options_layout.addWidget(self.orf_min_len, 1, 1)
        
        options_layout.setColumnStretch(2, 1)
        layout.addWidget(options_group)
        
        # 执行按钮
        btn_execute = QPushButton("🔍 搜索 ORF")
        btn_execute.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['green']};
                color: {COLORS['bg_dark']};
                font-size: 14px;
                padding: 12px 24px;
            }}
        """)
        btn_execute.clicked.connect(self.do_find_orfs)
        layout.addWidget(btn_execute)
        
        # 输出
        output_group = QGroupBox("ORF 结果")
        output_layout = QVBoxLayout(output_group)
        self.orf_output = QTextEdit()
        self.orf_output.setReadOnly(True)
        self.orf_output.setPlaceholderText("ORF 搜索结果将显示在这里...")
        output_layout.addWidget(self.orf_output)
        layout.addWidget(output_group)
        
        layout.addStretch()
        return tab
    
    def create_stats_tab(self):
        """统计分析 Tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)
        
        # 输入
        input_group = QGroupBox("输入序列")
        input_layout = QVBoxLayout(input_group)
        self.stats_input = QTextEdit()
        self.stats_input.setPlaceholderText("输入 DNA 序列...")
        self.stats_input.setMaximumHeight(120)
        input_layout.addWidget(self.stats_input)
        layout.addWidget(input_group)
        
        # 执行按钮
        btn_execute = QPushButton("📊 分析")
        btn_execute.clicked.connect(self.do_stats)
        layout.addWidget(btn_execute)
        
        # 输出
        output_group = QGroupBox("统计结果")
        output_layout = QVBoxLayout(output_group)
        self.stats_output = QTextEdit()
        self.stats_output.setReadOnly(True)
        self.stats_output.setPlaceholderText("统计结果将显示在这里...")
        output_layout.addWidget(self.stats_output)
        layout.addWidget(output_group)
        
        layout.addStretch()
        return tab
    
    # ===== 操作方法 =====
    
    def do_basic_op(self, op_type: str):
        """执行基础操作"""
        seq = self.basic_input.toPlainText().strip().upper()
        if not seq:
            return
        
        try:
            from seqbox.dna import basic, convert
            
            if op_type == 'complement':
                result = basic.complement(seq)
                self.basic_output.setText(f">complement\n{result}")
            elif op_type == 'reverse_complement':
                result = basic.reverse_complement(seq)
                self.basic_output.setText(f">reverse_complement\n{result}")
            elif op_type == 'transcribe':
                result = convert.transcribe(seq)
                self.basic_output.setText(f">RNA\n{result}")
            elif op_type == 'reverse_transcribe':
                result = convert.reverse_transcribe(seq)
                self.basic_output.setText(f">DNA\n{result}")
            
            self.log(f"DNA {op_type} 完成")
            
        except Exception as e:
            self.basic_output.setText(f"错误: {e}")
    
    def do_translate(self):
        """执行翻译"""
        seq = self.translate_input.toPlainText().strip().upper()
        if not seq:
            return
        
        try:
            from seqbox.dna import convert
            
            table_map = {
                0: 'standard',
                1: 'vertebrate_mitochondrial',
                2: 'bacterial',
                3: 'yeast_mitochondrial',
            }
            
            result = convert.translate(
                seq,
                table=table_map[self.translate_table.currentIndex()],
                to_stop=self.translate_to_stop.isChecked()
            )
            
            self.translate_output.setText(f">Protein\n{result}")
            self.log("翻译完成")
            
        except Exception as e:
            self.translate_output.setText(f"错误: {e}")
    
    def do_six_frames(self):
        """执行六框翻译"""
        seq = self.translate_input.toPlainText().strip().upper()
        if not seq:
            return
        
        try:
            from seqbox.dna import convert
            
            table_map = {
                0: 'standard',
                1: 'vertebrate_mitochondrial',
                2: 'bacterial',
                3: 'yeast_mitochondrial',
            }
            
            results = convert.translate_six_frames(
                seq,
                table=table_map[self.translate_table.currentIndex()]
            )
            
            output = []
            for frame, protein in sorted(results.items()):
                output.append(f">Frame {frame:+d}\n{protein}")
            
            self.translate_output.setText('\n\n'.join(output))
            self.log("六框翻译完成")
            
        except Exception as e:
            self.translate_output.setText(f"错误: {e}")
    
    def do_find_orfs(self):
        """执行 ORF 搜索"""
        seq = self.orf_input.toPlainText().strip().upper()
        if not seq:
            return
        
        try:
            from seqbox.dna import convert
            
            table_map = {
                0: 'standard',
                1: 'vertebrate_mitochondrial',
                2: 'bacterial',
                3: 'yeast_mitochondrial',
            }
            
            orfs = convert.find_orfs(
                seq,
                table=table_map[self.orf_table.currentIndex()],
                min_length=self.orf_min_len.value()
            )
            
            if not orfs:
                self.orf_output.setText("未找到符合条件的 ORF")
                return
            
            output = [f"找到 {len(orfs)} 个 ORF:\n"]
            for i, orf in enumerate(orfs, 1):
                output.append(
                    f"ORF #{i}:\n"
                    f"  位置: {orf.start}-{orf.end} (读框 {orf.frame:+d})\n"
                    f"  长度: {len(orf)} nt / {orf.protein_length} aa\n"
                    f"  起始密码子: {orf.start_codon}\n"
                    f"  终止密码子: {orf.stop_codon}\n"
                    f"  蛋白质: {orf.protein}\n"
                )
            
            self.orf_output.setText('\n'.join(output))
            self.log(f"ORF 搜索完成: 找到 {len(orfs)} 个")
            
        except Exception as e:
            self.orf_output.setText(f"错误: {e}")
    
    def do_stats(self):
        """执行统计分析"""
        seq = self.stats_input.toPlainText().strip().upper()
        if not seq:
            return
        
        try:
            from seqbox.dna import basic
            
            gc = basic.gc_content(seq)
            composition = basic.base_composition(seq, include_iupac=True)
            mw = basic.molecular_weight(seq, strand='ds')
            
            # 格式化碱基组成
            comp_str = '\n'.join(f"    {base}: {count}" for base, count in sorted(composition.items()) if count > 0)
            
            result = f"""序列长度: {len(seq)} bp

GC 含量: {gc:.2f}%

碱基组成:
{comp_str}

分子量:
  单链: {basic.molecular_weight(seq, 'ss'):.2f} Da
  双链: {mw:.2f} Da

熔解温度 (Wallace):
  {basic.melting_temperature(seq, 'wallace'):.1f} °C
"""
            
            self.stats_output.setText(result)
            self.log("统计分析完成")
            
        except Exception as e:
            self.stats_output.setText(f"错误: {e}")
