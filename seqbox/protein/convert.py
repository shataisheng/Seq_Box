"""
Seq_Box - 蛋白质转换模块

提供蛋白质序列的单/三字母转换等功能
"""

from __future__ import annotations
from typing import Dict, List, Optional, Set


# 氨基酸单字母 → 三字母映射
AA_SINGLE_TO_TRIPLE: Dict[str, str] = {
    'A': 'Ala', 'C': 'Cys', 'D': 'Asp', 'E': 'Glu',
    'F': 'Phe', 'G': 'Gly', 'H': 'His', 'I': 'Ile',
    'K': 'Lys', 'L': 'Leu', 'M': 'Met', 'N': 'Asn',
    'P': 'Pro', 'Q': 'Gln', 'R': 'Arg', 'S': 'Ser',
    'T': 'Thr', 'V': 'Val', 'W': 'Trp', 'Y': 'Tyr',
}

# 氨基酸三字母 → 单字母映射
AA_TRIPLE_TO_SINGLE: Dict[str, str] = {v: k for k, v in AA_SINGLE_TO_TRIPLE.items()}

# 氨基酸全称
AA_NAMES: Dict[str, str] = {
    'A': 'Alanine',       'C': 'Cysteine',    'D': 'Aspartic acid',
    'E': 'Glutamic acid', 'F': 'Phenylalanine', 'G': 'Glycine',
    'H': 'Histidine',     'I': 'Isoleucine',  'K': 'Lysine',
    'L': 'Leucine',       'M': 'Methionine',  'N': 'Asparagine',
    'P': 'Proline',       'Q': 'Glutamine',   'R': 'Arginine',
    'S': 'Serine',        'T': 'Threonine',   'V': 'Valine',
    'W': 'Tryptophan',    'Y': 'Tyrosine',
}

# 扩展氨基酸
AA_EXTENDED: Dict[str, str] = {
    'B': 'Asx',   # Asp or Asn
    'Z': 'Glx',   # Glu or Gln
    'X': 'Xaa',   # Unknown
    'J': 'Xle',   # Leu or Ile
    'U': 'Sec',   # Selenocysteine
    'O': 'Pyl',   # Pyrrolysine
}

# 氨基酸性质分类
AA_PROPERTIES: Dict[str, Dict[str, any]] = {
    'A': {'name': 'Alanine',       'hydrophobic': True,  'charge': 0,  'size': 'small'},
    'C': {'name': 'Cysteine',      'hydrophobic': True,  'charge': 0,  'size': 'small'},
    'D': {'name': 'Aspartic acid', 'hydrophobic': False, 'charge': -1, 'size': 'small'},
    'E': {'name': 'Glutamic acid', 'hydrophobic': False, 'charge': -1, 'size': 'medium'},
    'F': {'name': 'Phenylalanine', 'hydrophobic': True,  'charge': 0,  'size': 'large'},
    'G': {'name': 'Glycine',       'hydrophobic': True,  'charge': 0,  'size': 'small'},
    'H': {'name': 'Histidine',     'hydrophobic': False, 'charge': 0,  'size': 'medium'},
    'I': {'name': 'Isoleucine',    'hydrophobic': True,  'charge': 0,  'size': 'medium'},
    'K': {'name': 'Lysine',        'hydrophobic': False, 'charge': +1, 'size': 'medium'},
    'L': {'name': 'Leucine',       'hydrophobic': True,  'charge': 0,  'size': 'medium'},
    'M': {'name': 'Methionine',    'hydrophobic': True,  'charge': 0,  'size': 'medium'},
    'N': {'name': 'Asparagine',    'hydrophobic': False, 'charge': 0,  'size': 'small'},
    'P': {'name': 'Proline',       'hydrophobic': True,  'charge': 0,  'size': 'small'},
    'Q': {'name': 'Glutamine',     'hydrophobic': False, 'charge': 0,  'size': 'medium'},
    'R': {'name': 'Arginine',      'hydrophobic': False, 'charge': +1, 'size': 'large'},
    'S': {'name': 'Serine',        'hydrophobic': False, 'charge': 0,  'size': 'small'},
    'T': {'name': 'Threonine',     'hydrophobic': False, 'charge': 0,  'size': 'small'},
    'V': {'name': 'Valine',        'hydrophobic': True,  'charge': 0,  'size': 'small'},
    'W': {'name': 'Tryptophan',    'hydrophobic': True,  'charge': 0,  'size': 'large'},
    'Y': {'name': 'Tyrosine',      'hydrophobic': True,  'charge': 0,  'size': 'large'},
}

# 性质分类集合
HYDROPHOBIC_AA: Set[str] = {k for k, v in AA_PROPERTIES.items() if v['hydrophobic']}
HYDROPHILIC_AA: Set[str] = {k for k, v in AA_PROPERTIES.items() if not v['hydrophobic']}
POSITIVE_AA: Set[str] = {k for k, v in AA_PROPERTIES.items() if v['charge'] > 0}
NEGATIVE_AA: Set[str] = {k for k, v in AA_PROPERTIES.items() if v['charge'] < 0}
NEUTRAL_AA: Set[str] = {k for k, v in AA_PROPERTIES.items() if v['charge'] == 0}
SMALL_AA: Set[str] = {k for k, v in AA_PROPERTIES.items() if v['size'] == 'small'}
MEDIUM_AA: Set[str] = {k for k, v in AA_PROPERTIES.items() if v['size'] == 'medium'}
LARGE_AA: Set[str] = {k for k, v in AA_PROPERTIES.items() if v['size'] == 'large'}


def to_triple(sequence: str, separator: str = '-') -> str:
    """
    单字母氨基酸序列转换为三字母表示
    
    Args:
        sequence: 单字母蛋白质序列
        separator: 分隔符，默认 '-'
        
    Returns:
        三字母序列，如 "Ala-Cys-Asp"
        
    Example:
        >>> to_triple("ACD")
        'Ala-Cys-Asp'
        >>> to_triple("MKV", " ")
        'Met Lys Val'
    """
    seq = sequence.upper()
    triple_list = []
    
    for aa in seq:
        if aa in AA_SINGLE_TO_TRIPLE:
            triple_list.append(AA_SINGLE_TO_TRIPLE[aa])
        elif aa in AA_EXTENDED:
            triple_list.append(AA_EXTENDED[aa])
        else:
            triple_list.append('Xaa')  # 未知氨基酸
    
    return separator.join(triple_list)


def from_triple(triple_sequence: str, separator: Optional[str] = None) -> str:
    """
    三字母氨基酸序列转换为单字母表示
    
    Args:
        triple_sequence: 三字母序列，如 "Ala Cys Asp" 或 "Ala-Cys-Asp"
        separator: 分隔符，None 则自动检测
        
    Returns:
        单字母序列
        
    Example:
        >>> from_triple("Ala-Cys-Asp")
        'ACD'
        >>> from_triple("Met Lys Val", " ")
        'MKV'
    """
    seq = triple_sequence.strip()
    
    # 自动检测分隔符
    if separator is None:
        if '-' in seq:
            separator = '-'
        else:
            separator = None  # 按空格分割
    
    if separator:
        triples = seq.split(separator)
    else:
        triples = seq.split()
    
    # 清理并转换
    single_list = []
    for t in triples:
        t = t.strip().capitalize()
        if t in AA_TRIPLE_TO_SINGLE:
            single_list.append(AA_TRIPLE_TO_SINGLE[t])
        else:
            single_list.append('X')  # 未知氨基酸
    
    return ''.join(single_list)


def get_amino_acid_name(aa: str, language: str = 'en') -> str:
    """
    获取氨基酸名称
    
    Args:
        aa: 单字母或三字母代码
        language: 'en' (英文) 或 'zh' (中文，待扩展)
        
    Returns:
        氨基酸全称
        
    Example:
        >>> get_amino_acid_name('A')
        'Alanine'
        >>> get_amino_acid_name('Ala')
        'Alanine'
    """
    aa = aa.strip()
    
    # 三字母转单字母
    if len(aa) == 3:
        aa = AA_TRIPLE_TO_SINGLE.get(aa.capitalize(), 'X')
    
    # 获取名称
    return AA_NAMES.get(aa.upper(), 'Unknown')


def get_amino_acid_property(aa: str, property_name: Optional[str] = None):
    """
    获取氨基酸性质
    
    Args:
        aa: 单字母代码
        property_name: 性质名称 ('hydrophobic', 'charge', 'size')
                      None 则返回所有性质
        
    Returns:
        性质值或性质字典
        
    Example:
        >>> get_amino_acid_property('A', 'hydrophobic')
        True
        >>> get_amino_acid_property('D', 'charge')
        -1
    """
    aa = aa.upper()
    
    if aa not in AA_PROPERTIES:
        return None
    
    props = AA_PROPERTIES[aa]
    
    if property_name:
        return props.get(property_name)
    
    return props


def get_amino_acids_by_property(property_name: str, value) -> Set[str]:
    """
    根据性质筛选氨基酸
    
    Args:
        property_name: 性质名称
        value: 性质值
        
    Returns:
        符合条件的氨基酸集合
        
    Example:
        >>> get_amino_acids_by_property('hydrophobic', True)
        {'A', 'C', 'F', 'G', 'I', 'L', 'M', 'P', 'V', 'W', 'Y'}
    """
    return {k for k, v in AA_PROPERTIES.items() if v.get(property_name) == value}


def calculate_molecular_weight(sequence: str) -> float:
    """
    计算蛋白质分子量
    
    Args:
        sequence: 单字母蛋白质序列
        
    Returns:
        分子量 (Da)
        
    Note:
        使用平均氨基酸残基分子量，加上水分子 (18.02)
    """
    # 氨基酸平均分子量 (减去水)
    aa_weights = {
        'A': 71.08,  'C': 103.14, 'D': 115.09, 'E': 129.12,
        'F': 147.18, 'G': 57.05,  'H': 137.14, 'I': 113.16,
        'K': 128.17, 'L': 113.16, 'M': 131.19, 'N': 114.10,
        'P': 97.12,  'Q': 128.13, 'R': 156.19, 'S': 87.08,
        'T': 101.11, 'V': 99.13,  'W': 186.21, 'Y': 163.18,
    }
    
    seq = sequence.upper()
    weight = sum(aa_weights.get(aa, 110.0) for aa in seq)
    weight += 18.02  # 加回水分子
    
    return weight


def calculate_extinction_coefficient(sequence: str, reduced: bool = False) -> float:
    """
    计算消光系数 (280nm)
    
    Args:
        sequence: 蛋白质序列
        reduced: 是否为还原状态（半胱氨酸形成二硫键会影响结果）
        
    Returns:
        消光系数 (M^-1 cm^-1)
        
    Note:
        基于色氨酸 (W: 5500)、酪氨酸 (Y: 1490) 和半胱氨酸 (C: 125) 的贡献
    """
    seq = sequence.upper()
    
    n_w = seq.count('W')
    n_y = seq.count('Y')
    n_c = seq.count('C')
    
    if reduced:
        # 还原状态：所有 Cys 都贡献
        return n_w * 5500 + n_y * 1490 + n_c * 125
    else:
        # 氧化状态：假设有一半 Cys 形成二硫键
        return n_w * 5500 + n_y * 1490


def calculate_charge_at_ph(sequence: str, ph: float = 7.0) -> float:
    """
    计算蛋白质在特定 pH 下的电荷
    
    Args:
        sequence: 蛋白质序列
        ph: pH 值
        
    Returns:
        估计电荷
        
    Note:
        使用 Henderson-Hasselbalch 方程近似计算
    """
    seq = sequence.upper()
    
    # pKa 值
    pka_n_term = 9.69
    pka_c_term = 2.34
    pka_side_chains = {
        'D': 3.86,  # Asp
        'E': 4.25,  # Glu
        'H': 6.0,   # His
        'C': 8.33,  # Cys
        'Y': 10.07, # Tyr
        'K': 10.5,  # Lys
        'R': 12.48, # Arg
    }
    
    charge = 0.0
    
    # N-末端
    charge += 1 / (1 + 10**(ph - pka_n_term))
    
    # C-末端
    charge -= 1 / (1 + 10**(pka_c_term - ph))
    
    # 侧链
    for aa, pka in pka_side_chains.items():
        count = seq.count(aa)
        if aa in 'KR':  # 正电荷
            charge += count / (1 + 10**(ph - pka))
        elif aa in 'DECY':  # 负电荷
            charge -= count / (1 + 10**(pka - ph))
        elif aa == 'H':  # His 特殊处理
            charge += count / (1 + 10**(ph - pka))
    
    return charge


def calculate_isoelectric_point(sequence: str, precision: float = 0.01) -> float:
    """
    计算等电点 (pI)
    
    Args:
        sequence: 蛋白质序列
        precision: 计算精度
        
    Returns:
        等电点 pH 值
    """
    # 二分查找 pI
    ph_min, ph_max = 0.0, 14.0
    
    while abs(ph_max - ph_min) > precision:
        ph_mid = (ph_min + ph_max) / 2
        charge = calculate_charge_at_ph(sequence, ph_mid)
        
        if charge > 0:
            ph_min = ph_mid
        else:
            ph_max = ph_mid
    
    return (ph_min + ph_max) / 2
