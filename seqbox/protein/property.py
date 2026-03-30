"""
Seq_Box - 蛋白质理化性质计算模块

参考:
- Expasy ProtParam 计算逻辑
- Bjellqvist pI 计算方法 (1993, 1994)
- Kyte-Doolittle 疏水性尺度

计算方法:
- 分子量: 氨基酸平均同位素质量之和 + 水分子质量
- 等电点: Bjellqvist 方案，二分法找净电荷为0的pH
- 吸光度: E(Prot) / Molecular_weight
- 疏水性: GRAVY = 疏水性之和 / 残基数
"""

from dataclasses import dataclass
from typing import List, Optional
from collections import Counter


# ============== 氨基酸平均同位素质量 (来自 Expasy) ==============
# 单位: Da (Dalton)
AA_AVERAGE_MASS = {
    'A': 71.0788,   # Alanine
    'R': 156.1875,  # Arginine
    'N': 114.1038,  # Asparagine
    'D': 115.0886,  # Aspartic Acid
    'C': 103.1388,  # Cysteine
    'E': 129.1155,  # Glutamic Acid
    'Q': 128.1307,  # Glutamine
    'G': 57.0519,   # Glycine
    'H': 137.1411,  # Histidine
    'I': 113.1594,  # Isoleucine
    'L': 113.1594,  # Leucine
    'K': 128.1741,  # Lysine
    'M': 131.1925,  # Methionine
    'F': 147.1766,  # Phenylalanine
    'P': 97.1167,   # Proline
    'S': 87.0782,   # Serine
    'T': 101.1051,  # Threonine
    'W': 186.2132,  # Tryptophan
    'Y': 163.1760,  # Tyrosine
    'V': 99.1326,   # Valine
}

# 水分子平均质量
WATER_MASS = 18.015


# ============== 氨基酸消光系数 (用于吸光度计算) ==============
# 单位: M^-1 cm^-1
# 还原型 Cysteine (形成二硫键时不同)
EXTINCTION_COEFFICIENTS = {
    'W': 5500,   # Tryptophan
    'Y': 1490,   # Tyrosine
    'C': 125,    # Cysteine (还原型)
}


# ============== Kyte-Doolittle 疏水性尺度 ==============
# 正值: 疏水, 负值: 亲水
KYTE_DOOLITTLE_HYDROPATHY = {
    'A': 1.8,   'R': -4.5,  'N': -3.5,  'D': -3.5,
    'C': 2.5,   'E': -3.5,  'Q': -3.5,  'G': -0.4,
    'H': -3.2,  'I': 4.5,   'L': 3.8,   'K': -3.9,
    'M': 1.9,   'F': 2.8,   'P': -1.6,  'S': -0.8,
    'T': -0.7,  'W': -0.9,  'Y': -1.3,  'V': 4.2,
}


# ============== Bjellqvist pI 计算 pKa 值 ==============
PKA_DEFAULT = {
    'K': 10.0,   # Lysine
    'R': 12.0,   # Arginine
    'H': 5.98,   # Histidine
    'D': 4.05,   # Aspartic Acid
    'E': 4.45,   # Glutamic Acid
    'C': 9.0,    # Cysteine
    'Y': 10.0,   # Tyrosine
    'Nterm': 7.5,   # N-末端氨基
    'Cterm': 3.55,  # C-末端羧基
}

# N-末端修正表
PKA_NTERM_TABLE = {
    'A': 7.59, 'M': 7.00, 'S': 6.93, 'P': 8.36,
    'T': 6.82, 'V': 7.44, 'E': 7.70,
}

# C-末端修正表
PKA_CTERM_TABLE = {
    'D': 4.55, 'E': 4.75,
}


@dataclass
class ProteinProperties:
    """蛋白质理化性质数据类"""
    sequence: str           # 序列（大写）
    length: int             # 氨基酸残基数
    molecular_weight: float # 分子量 (Da)
    pi: float               # 等电点
    extinction_coeff: int   # 摩尔消光系数
    absorbance: float       # 吸光度 (AU)
    gravy: float            # 疏水性指数
    
    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            'sequence': self.sequence,
            'length': self.length,
            'molecular_weight': self.molecular_weight,
            'pi': self.pi,
            'extinction_coeff': self.extinction_coeff,
            'absorbance': self.absorbance,
            'gravy': self.gravy,
        }


@dataclass
class MultiChainProtein:
    """多链蛋白质（同一蛋白质的不同链）"""
    chains: List[ProteinProperties]

    @property
    def chain_count(self) -> int:
        """链数"""
        return len(self.chains)

    @property
    def total_molecular_weight(self) -> float:
        """总分子量（Expasy模式：多链蛋白只加1个水分子）"""
        # 各链残基质量之和 + 1个水分子（不是每条链都加水）
        residue_mass = sum(
            sum(AA_AVERAGE_MASS.get(aa, 0) for aa in chain.sequence)
            for chain in self.chains
        )
        return residue_mass + WATER_MASS

    @property
    def summed_molecular_weight(self) -> float:
        """链汇总分子量（每条链单独+1水，然后相加）"""
        return sum(chain.molecular_weight for chain in self.chains)

    @property
    def summed_absorbance(self) -> float:
        """链汇总吸光度（基于 summed_molecular_weight）"""
        total_ext = sum(chain.extinction_coeff for chain in self.chains)
        if self.summed_molecular_weight > 0:
            return total_ext / self.summed_molecular_weight
        return 0.0
    
    @property
    def total_length(self) -> int:
        """总残基数"""
        return sum(chain.length for chain in self.chains)
    
    @property
    def combined_sequence(self) -> str:
        """组合序列（用于计算整体pI）"""
        return ''.join(chain.sequence for chain in self.chains)
    
    @property
    def overall_pi(self) -> float:
        """整体等电点（基于组合序列）"""
        return calculate_pi(self.combined_sequence)
    
    @property
    def overall_extinction_coeff(self) -> int:
        """整体消光系数（Expasy模式：基于合并序列计算，所有Cys对统一配对）"""
        return calculate_extinction_coefficient(self.combined_sequence)

    @property
    def overall_absorbance(self) -> float:
        """整体吸光度（Expasy模式：消光系数基于合并序列）"""
        if self.total_molecular_weight > 0:
            return self.overall_extinction_coeff / self.total_molecular_weight
        return 0.0
    
    @property
    def overall_gravy(self) -> float:
        """整体疏水性"""
        total_hydro = sum(
            KYTE_DOOLITTLE_HYDROPATHY.get(aa, 0) 
            for chain in self.chains 
            for aa in chain.sequence
        )
        if self.total_length > 0:
            return total_hydro / self.total_length
        return 0.0
    
    def to_summary_dict(self) -> dict:
        """汇总信息字典（包含两种计算模式）"""
        return {
            'chain_count': len(self.chains),
            'total_length': self.total_length,
            # Expasy模式（合并序列计算，只+1水）
            'total_molecular_weight': self.total_molecular_weight,
            'overall_pi': self.overall_pi,
            'overall_absorbance': self.overall_absorbance,
            'overall_gravy': self.overall_gravy,
            # 链汇总模式（各链分别+1水，再相加）
            'summed_molecular_weight': self.summed_molecular_weight,
            'summed_absorbance': self.summed_absorbance,
            'chains': [chain.to_dict() for chain in self.chains],
        }


def calculate_molecular_weight(sequence: str) -> float:
    """
    计算蛋白质分子量
    
    公式: 氨基酸平均质量之和 + 水分子质量
    
    Args:
        sequence: 蛋白质序列（单字母代码）
        
    Returns:
        分子量 (Da)
    """
    sequence = sequence.upper().strip()
    if not sequence:
        return 0.0
    
    # 过滤非标准氨基酸
    valid_aas = [aa for aa in sequence if aa in AA_AVERAGE_MASS]
    if not valid_aas:
        return 0.0
    
    total = sum(AA_AVERAGE_MASS[aa] for aa in valid_aas)
    # 减去 (n-1) 个水分子（肽键形成时失去的水）
    # 实际上 ProtParam 是加 1 个水分子，不是减
    # 重新理解: 氨基酸残基质量之和 + 水分子质量
    return total + WATER_MASS


def calculate_extinction_coefficient(sequence: str, reduced_cysteines: bool = False) -> int:
    """
    计算摩尔消光系数

    公式:
    - 氧化型 (默认): 5500×W + 1490×Y + 125×(C/2)
      假设所有Cys都形成二硫键，每对Cys贡献125
    - 还原型: 5500×W + 1490×Y + 125×C
      每个Cys单独贡献125

    数据来源: Expasy ProtParam
    - Trp: 5500 M^-1 cm^-1
    - Tyr: 1490 M^-1 cm^-1
    - Cystine: 125 M^-1 cm^-1 (每对形成二硫键的Cys)

    Args:
        sequence: 蛋白质序列
        reduced_cysteines: 是否按还原型计算Cys（默认False，按氧化型/Cystine计算）
                          True则按还原型计算（每个Cys单独算125）

    Returns:
        摩尔消光系数 (M^-1 cm^-1)
    """
    sequence = sequence.upper().strip()
    aa_count = Counter(sequence)

    ext = 0
    ext += aa_count.get('W', 0) * EXTINCTION_COEFFICIENTS['W']
    ext += aa_count.get('Y', 0) * EXTINCTION_COEFFICIENTS['Y']

    cys_count = aa_count.get('C', 0)
    if reduced_cysteines:
        # 还原型：每个Cys单独算
        ext += cys_count * EXTINCTION_COEFFICIENTS['C']
    else:
        # 氧化型（默认）：Cys形成二硫键，每对算125
        ext += (cys_count // 2) * EXTINCTION_COEFFICIENTS['C']

    return ext


def calculate_absorbance(sequence: str, mw: Optional[float] = None) -> float:
    """
    计算吸光度 (Absorbance)
    
    公式: E(Prot) / Molecular_weight
    
    Args:
        sequence: 蛋白质序列
        mw: 分子量（可选，不传则自动计算）
        
    Returns:
        吸光度 (AU)
    """
    if mw is None:
        mw = calculate_molecular_weight(sequence)
    
    if mw <= 0:
        return 0.0
    
    ext = calculate_extinction_coefficient(sequence)
    return ext / mw


def calculate_gravy(sequence: str) -> float:
    """
    计算疏水性指数 (GRAVY)
    
    公式: 疏水性之和 / 残基数
    
    Args:
        sequence: 蛋白质序列
        
    Returns:
        GRAVY 值（正值疏水，负值亲水）
    """
    sequence = sequence.upper().strip()
    if not sequence:
        return 0.0
    
    valid_aas = [aa for aa in sequence if aa in KYTE_DOOLITTLE_HYDROPATHY]
    if not valid_aas:
        return 0.0
    
    total_hydro = sum(KYTE_DOOLITTLE_HYDROPATHY[aa] for aa in valid_aas)
    return total_hydro / len(valid_aas)


def _get_corrected_pka(sequence: str) -> dict:
    """获取修正后的pKa值（基于N/C末端）"""
    corrected = PKA_DEFAULT.copy()
    if not sequence:
        return corrected
    
    nterm = sequence[0].upper()
    cterm = sequence[-1].upper()
    
    if nterm in PKA_NTERM_TABLE:
        corrected['Nterm'] = PKA_NTERM_TABLE[nterm]
    if cterm in PKA_CTERM_TABLE:
        corrected['Cterm'] = PKA_CTERM_TABLE[cterm]
    
    return corrected


def _calculate_charge(sequence: str, ph: float) -> float:
    """计算给定pH下的净电荷"""
    pka = _get_corrected_pka(sequence)
    aa_count = Counter(sequence.upper())
    
    # 正电荷贡献 (碱性基团)
    pos_charge = (
        aa_count.get('K', 0) / (1 + 10**(ph - pka['K'])) +
        aa_count.get('R', 0) / (1 + 10**(ph - pka['R'])) +
        aa_count.get('H', 0) / (1 + 10**(ph - pka['H'])) +
        1 / (1 + 10**(ph - pka['Nterm']))  # N-末端
    )
    
    # 负电荷贡献 (酸性基团)
    neg_charge = (
        aa_count.get('D', 0) / (1 + 10**(pka['D'] - ph)) +
        aa_count.get('E', 0) / (1 + 10**(pka['E'] - ph)) +
        aa_count.get('C', 0) / (1 + 10**(pka['C'] - ph)) +
        aa_count.get('Y', 0) / (1 + 10**(pka['Y'] - ph)) +
        1 / (1 + 10**(pka['Cterm'] - ph))  # C-末端
    )
    
    return pos_charge - neg_charge


def calculate_pi(sequence: str, precision: float = 0.0001) -> float:
    """
    计算等电点 (pI) - Bjellqvist 方案
    
    使用二分法找净电荷为0的pH值
    
    Args:
        sequence: 蛋白质序列
        precision: 计算精度
        
    Returns:
        等电点 pI 值
    """
    sequence = sequence.upper().strip()
    if not sequence:
        return 0.0
    
    # 二分查找 pI (pH 范围 0-14)
    low, high = 0.0, 14.0
    
    while high - low > precision:
        mid = (low + high) / 2
        charge = _calculate_charge(sequence, mid)
        
        if charge > 0:
            low = mid
        else:
            high = mid
    
    return round((low + high) / 2, 2)


def analyze_sequence(sequence: str) -> ProteinProperties:
    """
    分析单个蛋白质序列的所有理化性质
    
    Args:
        sequence: 蛋白质序列（单字母代码）
        
    Returns:
        ProteinProperties 数据对象
    """
    sequence = sequence.upper().strip()
    valid_aas = [aa for aa in sequence if aa in AA_AVERAGE_MASS]
    clean_seq = ''.join(valid_aas)
    
    length = len(clean_seq)
    mw = calculate_molecular_weight(clean_seq)
    pi = calculate_pi(clean_seq)
    ext_coeff = calculate_extinction_coefficient(clean_seq)
    absorbance = calculate_absorbance(clean_seq, mw)
    gravy = calculate_gravy(clean_seq)
    
    return ProteinProperties(
        sequence=clean_seq,
        length=length,
        molecular_weight=mw,
        pi=pi,
        extinction_coeff=ext_coeff,
        absorbance=absorbance,
        gravy=gravy,
    )


def analyze_sequences(
    sequences: List[str], 
    same_protein: bool = True
) -> MultiChainProtein | List[ProteinProperties]:
    """
    批量分析蛋白质序列
    
    Args:
        sequences: 蛋白质序列列表
        same_protein: 是否视为同一蛋白质的多条链
        
    Returns:
        same_protein=True: MultiChainProtein 对象
        same_protein=False: ProteinProperties 列表
    """
    properties_list = [analyze_sequence(seq) for seq in sequences if seq.strip()]
    
    if same_protein:
        return MultiChainProtein(chains=properties_list)
    else:
        return properties_list
