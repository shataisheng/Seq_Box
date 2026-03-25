"""
Seq_Box - 蛋白质操作页面
"""

from PyQt6.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QLineEdit,
    QTextEdit, QComboBox, QGroupBox, QTabWidget, QWidget
)

from .base_page import BasePage, COLORS


class ProteinPage(BasePage):
    """蛋白质操作页面"""
    
    def __init__(self, parent=None):
        super().__init__("蛋白质工具", parent)
    
    def setup_ui(self):
        super().setup_ui()
        
        # Tab 容器
        self.tabs = QTabWidget()
        
        # 各个功能 Tab
        self.tabs.addTab(self.create_convert_tab(), "🔄 单/三字母转换")
        self.tabs.addTab(self.create_property_tab(), "ℹ️ 氨基酸信息")
        self.tabs.addTab(self.create_analysis_tab(), "📊 理化分析")
        
        self.layout.addWidget(self.tabs)
    
    def create_convert_tab(self):
        """单/三字母转换 Tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)
        
        # 单字母 → 三字母
        single_group = QGroupBox("单字母 → 三字母")
        single_layout = QVBoxLayout(single_group)
        
        self.single_input = QTextEdit()
        self.single_input.setPlaceholderText("输入单字母蛋白质序列，如: ACDEFG...")
        self.single_input.setMaximumHeight(80)
        single_layout.addWidget(self.single_input)
        
        options_layout = QHBoxLayout()
        options_layout.addWidget(QLabel("分隔符:"))
        self.triple_separator = QComboBox()
        self.triple_separator.addItems(["连字符 (-)", "空格", "无"])
        options_layout.addWidget(self.triple_separator)
        options_layout.addStretch()
        single_layout.addLayout(options_layout)
        
        btn_to_triple = QPushButton("转换为三字母")
        btn_to_triple.clicked.connect(self.do_to_triple)
        single_layout.addWidget(btn_to_triple)
        
        self.triple_output = QTextEdit()
        self.triple_output.setReadOnly(True)
        self.triple_output.setPlaceholderText("三字母序列将显示在这里...")
        self.triple_output.setMaximumHeight(80)
        single_layout.addWidget(self.triple_output)
        
        layout.addWidget(single_group)
        
        # 三字母 → 单字母
        triple_group = QGroupBox("三字母 → 单字母")
        triple_layout = QVBoxLayout(triple_group)
        
        self.triple_input = QTextEdit()
        self.triple_input.setPlaceholderText("输入三字母序列，如: Ala-Cys-Asp-Glu...")
        self.triple_input.setMaximumHeight(80)
        triple_layout.addWidget(self.triple_input)
        
        btn_to_single = QPushButton("转换为单字母")
        btn_to_single.clicked.connect(self.do_to_single)
        triple_layout.addWidget(btn_to_single)
        
        self.single_output = QTextEdit()
        self.single_output.setReadOnly(True)
        self.single_output.setPlaceholderText("单字母序列将显示在这里...")
        self.single_output.setMaximumHeight(80)
        triple_layout.addWidget(self.single_output)
        
        layout.addWidget(triple_group)
        
        layout.addStretch()
        return tab
    
    def create_property_tab(self):
        """氨基酸信息 Tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)
        
        # 输入
        input_group = QGroupBox("输入氨基酸代码")
        input_layout = QVBoxLayout(input_group)
        
        self.aa_input = QTextEdit()
        self.aa_input.setPlaceholderText("输入单字母或三字母氨基酸代码，如: A 或 Ala...")
        self.aa_input.setMaximumHeight(60)
        input_layout.addWidget(self.aa_input)
        
        btn_lookup = QPushButton("🔍 查询")
        btn_lookup.clicked.connect(self.do_aa_lookup)
        input_layout.addWidget(btn_lookup)
        
        layout.addWidget(input_group)
        
        # 结果
        result_group = QGroupBox("氨基酸信息")
        result_layout = QVBoxLayout(result_group)
        self.aa_info_output = QTextEdit()
        self.aa_info_output.setReadOnly(True)
        result_layout.addWidget(self.aa_info_output)
        layout.addWidget(result_group)
        
        # 氨基酸参考表
        ref_group = QGroupBox("氨基酸参考表")
        ref_layout = QVBoxLayout(ref_group)
        
        ref_text = QTextEdit()
        ref_text.setReadOnly(True)
        ref_text.setMaximumHeight(150)
        ref_text.setText("""单字母  三字母      名称
A       Ala         Alanine       丙氨酸
C       Cys         Cysteine      半胱氨酸
D       Asp         Aspartic acid 天冬氨酸
E       Glu         Glutamic acid 谷氨酸
F       Phe         Phenylalanine 苯丙氨酸
G       Gly         Glycine       甘氨酸
H       His         Histidine     组氨酸
I       Ile         Isoleucine    异亮氨酸
K       Lys         Lysine        赖氨酸
L       Leu         Leucine       亮氨酸
M       Met         Methionine    甲硫氨酸
N       Asn         Asparagine    天冬酰胺
P       Pro         Proline       脯氨酸
Q       Gln         Glutamine     谷氨酰胺
R       Arg         Arginine      精氨酸
S       Ser         Serine        丝氨酸
T       Thr         Threonine     苏氨酸
V       Val         Valine        缬氨酸
W       Trp         Tryptophan    色氨酸
Y       Tyr         Tyrosine      酪氨酸""")
        ref_layout.addWidget(ref_text)
        layout.addWidget(ref_group)
        
        layout.addStretch()
        return tab
    
    def create_analysis_tab(self):
        """理化分析 Tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)
        
        # 输入
        input_group = QGroupBox("输入蛋白质序列")
        input_layout = QVBoxLayout(input_group)
        self.analysis_input = QTextEdit()
        self.analysis_input.setPlaceholderText("输入单字母蛋白质序列...")
        self.analysis_input.setMaximumHeight(120)
        input_layout.addWidget(self.analysis_input)
        layout.addWidget(input_group)
        
        # 执行按钮
        btn_execute = QPushButton("📊 分析")
        btn_execute.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['purple']};
                color: {COLORS['bg_dark']};
                font-size: 14px;
                padding: 12px 24px;
            }}
        """)
        btn_execute.clicked.connect(self.do_analysis)
        layout.addWidget(btn_execute)
        
        # 结果
        result_group = QGroupBox("分析结果")
        result_layout = QVBoxLayout(result_group)
        self.analysis_output = QTextEdit()
        self.analysis_output.setReadOnly(True)
        self.analysis_output.setPlaceholderText("分析结果将显示在这里...")
        result_layout.addWidget(self.analysis_output)
        layout.addWidget(result_group)
        
        layout.addStretch()
        return tab
    
    # ===== 操作方法 =====
    
    def do_to_triple(self):
        """单字母转三字母"""
        seq = self.single_input.toPlainText().strip()
        if not seq:
            return
        
        try:
            from seqbox.protein import to_triple
            
            sep_map = {0: '-', 1: ' ', 2: ''}
            separator = sep_map[self.triple_separator.currentIndex()]
            
            result = to_triple(seq, separator)
            self.triple_output.setText(result)
            self.log("单字母 → 三字母转换完成")
            
        except Exception as e:
            self.triple_output.setText(f"错误: {e}")
    
    def do_to_single(self):
        """三字母转单字母"""
        seq = self.triple_input.toPlainText().strip()
        if not seq:
            return
        
        try:
            from seqbox.protein import from_triple
            
            result = from_triple(seq)
            self.single_output.setText(result)
            self.log("三字母 → 单字母转换完成")
            
        except Exception as e:
            self.single_output.setText(f"错误: {e}")
    
    def do_aa_lookup(self):
        """查询氨基酸信息"""
        aa_input = self.aa_input.toPlainText().strip()
        if not aa_input:
            return
        
        try:
            from seqbox.protein import (
                get_amino_acid_name,
                get_amino_acid_property,
                to_triple
            )
            
            results = []
            for aa in aa_input.replace(' ', '').replace('-', '').upper():
                if len(aa) == 0:
                    continue
                    
                name = get_amino_acid_name(aa)
                triple = to_triple(aa, '-')
                props = get_amino_acid_property(aa)
                
                if props:
                    hydro = "疏水" if props['hydrophobic'] else "亲水"
                    charge = {0: "中性", 1: "正电", -1: "负电"}.get(props['charge'], "未知")
                    
                    results.append(
                        f"{aa} ({triple}) - {name}\n"
                        f"  性质: {hydro}, {charge}\n"
                        f"  大小: {props['size']}\n"
                    )
                else:
                    results.append(f"{aa} - 未知氨基酸\n")
            
            self.aa_info_output.setText('\n'.join(results))
            self.log("氨基酸信息查询完成")
            
        except Exception as e:
            self.aa_info_output.setText(f"错误: {e}")
    
    def do_analysis(self):
        """执行理化分析"""
        seq = self.analysis_input.toPlainText().strip().upper()
        if not seq:
            return
        
        try:
            from seqbox.protein.convert import (
                calculate_molecular_weight,
                calculate_extinction_coefficient,
                calculate_isoelectric_point,
                calculate_charge_at_ph
            )
            
            mw = calculate_molecular_weight(seq)
            ext_coeff = calculate_extinction_coefficient(seq)
            ext_coeff_reduced = calculate_extinction_coefficient(seq, reduced=True)
            pI = calculate_isoelectric_point(seq)
            charge_at_7 = calculate_charge_at_ph(seq, 7.0)
            
            # 氨基酸组成
            from collections import Counter
            comp = Counter(seq)
            comp_str = '\n'.join(f"  {aa}: {count}" for aa, count in sorted(comp.items()))
            
            result = f"""序列长度: {len(seq)} 个氨基酸

分子量: {mw:.2f} Da

消光系数 (280nm):
  氧化状态: {ext_coeff:.0f} M⁻¹cm⁻¹
  还原状态: {ext_coeff_reduced:.0f} M⁻¹cm⁻¹

等电点 (pI): {pI:.2f}
pH 7.0 电荷: {charge_at_7:+.2f}

氨基酸组成:
{comp_str}
"""
            
            self.analysis_output.setText(result)
            self.log("蛋白质理化分析完成")
            
        except Exception as e:
            self.analysis_output.setText(f"错误: {e}")
