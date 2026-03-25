"""
Seq_Box - 序列字符集定义

提供 DNA、RNA、蛋白质的 IUPAC 标准字符集及校验功能
"""

from typing import Set, FrozenSet


# ========== DNA IUPAC 字符集 ==========

# 标准碱基
DNA_STANDARD: FrozenSet[str] = frozenset('ACGT')

# IUPAC 简并碱基（含标准碱基）
DNA_IUPAC: FrozenSet[str] = frozenset('ACGTRYSWKMBDHVN')

# DNA IUPAC 简并碱基含义表
DNA_IUPAC_MEANING: dict[str, str] = {
    'A': 'Adenine',
    'C': 'Cytosine',
    'G': 'Guanine',
    'T': 'Thymine',
    'R': 'A or G (puRine)',
    'Y': 'C or T (pYrimidine)',
    'S': 'G or C (Strong)',
    'W': 'A or T (Weak)',
    'K': 'G or T (Keto)',
    'M': 'A or C (aMino)',
    'B': 'C or G or T (not A)',
    'D': 'A or G or T (not C)',
    'H': 'A or C or T (not G)',
    'V': 'A or C or G (not T)',
    'N': 'Any base',
}

# DNA 互补配对表（支持简并碱基）
DNA_COMPLEMENT: dict[str, str] = {
    'A': 'T', 'T': 'A', 'G': 'C', 'C': 'G',
    'R': 'Y', 'Y': 'R', 'S': 'S', 'W': 'W',
    'K': 'M', 'M': 'K', 'B': 'V', 'V': 'B',
    'D': 'H', 'H': 'D', 'N': 'N',
}


# ========== RNA IUPAC 字符集 ==========

# 标准碱基
RNA_STANDARD: FrozenSet[str] = frozenset('ACGU')

# IUPAC 简并碱基（含标准碱基）
RNA_IUPAC: FrozenSet[str] = frozenset('ACGURYSWKMBDHVN')

# RNA 互补配对表
RNA_COMPLEMENT: dict[str, str] = {
    'A': 'U', 'U': 'A', 'G': 'C', 'C': 'G',
    'R': 'Y', 'Y': 'R', 'S': 'S', 'W': 'W',
    'K': 'M', 'M': 'K', 'B': 'V', 'V': 'B',
    'D': 'H', 'H': 'D', 'N': 'N',
}


# ========== 蛋白质氨基酸字符集 ==========

# 标准 20 种氨基酸
PROTEIN_STANDARD: FrozenSet[str] = frozenset('ACDEFGHIKLMNPQRSTVWY')

# 扩展字符集（含简并和特殊符号）
PROTEIN_EXTENDED: FrozenSet[str] = frozenset('ACDEFGHIKLMNPQRSTVWYBXZJUO')

# 氨基酸单字母 → 三字母映射
AA_SINGLE_TO_TRIPLE: dict[str, str] = {
    'A': 'Ala', 'C': 'Cys', 'D': 'Asp', 'E': 'Glu',
    'F': 'Phe', 'G': 'Gly', 'H': 'His', 'I': 'Ile',
    'K': 'Lys', 'L': 'Leu', 'M': 'Met', 'N': 'Asn',
    'P': 'Pro', 'Q': 'Gln', 'R': 'Arg', 'S': 'Ser',
    'T': 'Thr', 'V': 'Val', 'W': 'Trp', 'Y': 'Tyr',
}

# 氨基酸三字母 → 单字母映射
AA_TRIPLE_TO_SINGLE: dict[str, str] = {v: k for k, v in AA_SINGLE_TO_TRIPLE.items()}

# 氨基酸名称表
AA_NAMES: dict[str, str] = {
    'A': 'Alanine',       'C': 'Cysteine',    'D': 'Aspartic acid',
    'E': 'Glutamic acid', 'F': 'Phenylalanine', 'G': 'Glycine',
    'H': 'Histidine',     'I': 'Isoleucine',  'K': 'Lysine',
    'L': 'Leucine',       'M': 'Methionine',  'N': 'Asparagine',
    'P': 'Proline',       'Q': 'Glutamine',   'R': 'Arginine',
    'S': 'Serine',        'T': 'Threonine',   'V': 'Valine',
    'W': 'Tryptophan',    'Y': 'Tyrosine',
}

# 扩展氨基酸含义
AA_EXTENDED_MEANING: dict[str, str] = {
    'B': 'Aspartic acid or Asparagine (Asx)',
    'Z': 'Glutamic acid or Glutamine (Glx)',
    'X': 'Unknown amino acid',
    'J': 'Leucine or Isoleucine',
    'U': 'Selenocysteine',
    'O': 'Pyrrolysine',
}


# ========== 校验函数 ==========

def validate_dna(sequence: str, allow_iupac: bool = True) -> tuple[bool, set[str]]:
    """
    校验 DNA 序列合法性
    
    Args:
        sequence: 待校验序列（大写）
        allow_iupac: 是否允许简并碱基
        
    Returns:
        (是否合法, 非法字符集合)
    """
    valid_chars = DNA_IUPAC if allow_iupac else DNA_STANDARD
    seq_set = set(sequence.upper())
    invalid = seq_set - valid_chars
    return len(invalid) == 0, invalid


def validate_rna(sequence: str, allow_iupac: bool = True) -> tuple[bool, set[str]]:
    """
    校验 RNA 序列合法性
    
    Args:
        sequence: 待校验序列（大写）
        allow_iupac: 是否允许简并碱基
        
    Returns:
        (是否合法, 非法字符集合)
    """
    valid_chars = RNA_IUPAC if allow_iupac else RNA_STANDARD
    seq_set = set(sequence.upper())
    invalid = seq_set - valid_chars
    return len(invalid) == 0, invalid


def validate_protein(sequence: str, allow_extended: bool = True) -> tuple[bool, set[str]]:
    """
    校验蛋白质序列合法性
    
    Args:
        sequence: 待校验序列（大写）
        allow_extended: 是否允许扩展字符（BXZJUO）
        
    Returns:
        (是否合法, 非法字符集合)
    """
    valid_chars = PROTEIN_EXTENDED if allow_extended else PROTEIN_STANDARD
    seq_set = set(sequence.upper())
    invalid = seq_set - valid_chars
    return len(invalid) == 0, invalid


def guess_sequence_type(sequence: str, sample_size: int = 1000) -> str:
    """
    根据序列内容猜测类型（核酸或蛋白质）
    
    Args:
        sequence: 待检测序列
        sample_size: 抽样检查的字符数
        
    Returns:
        'dna', 'rna', 'protein', 或 'unknown'
    """
    seq = sequence.upper().replace(' ', '').replace('-', '')[:sample_size]
    
    if not seq:
        return 'unknown'
    
    # 计算各类字符占比
    dna_chars = set('ACGT')
    rna_chars = set('ACGU')
    protein_only_chars = set('EFILPQ')
    
    dna_count = sum(1 for c in seq if c in dna_chars)
    rna_count = sum(1 for c in seq if c in rna_chars)
    protein_only_count = sum(1 for c in seq if c in protein_only_chars)
    
    total = len(seq)
    dna_ratio = dna_count / total
    rna_ratio = rna_count / total
    protein_only_ratio = protein_only_count / total
    
    # 出现蛋白质特有氨基酸 → 确定为蛋白质
    if protein_only_ratio > 0.05:
        return 'protein'
    
    # 出现 U 且很少 T → 可能是 RNA
    if 'U' in seq and 'T' not in seq:
        return 'rna'
    
    # ACGT 占比 > 90% → 很可能是 DNA
    if dna_ratio > 0.90:
        return 'dna'
    
    # ACGU 占比 > 90% 且含 U → 很可能是 RNA
    if rna_ratio > 0.90 and 'U' in seq:
        return 'rna'
    
    # 中间情况，根据 T/U 判断
    if 'T' in seq and 'U' not in seq:
        return 'dna'
    if 'U' in seq and 'T' not in seq:
        return 'rna'
    
    return 'unknown'


def clean_sequence(sequence: str, valid_chars: Set[str]) -> str:
    """
    清洗序列，只保留合法字符
    
    Args:
        sequence: 原始序列
        valid_chars: 允许的字符集合
        
    Returns:
        清洗后的序列（大写）
    """
    return ''.join(c for c in sequence.upper() if c in valid_chars)
