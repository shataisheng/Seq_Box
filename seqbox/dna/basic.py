"""
Seq_Box - DNA 基础操作模块

提供 DNA 序列的基础操作：互补、反向互补、GC 含量、碱基组成等
"""

from __future__ import annotations
from typing import Dict, Optional, Union
from collections import Counter

from seqbox.core.alphabets import DNA_COMPLEMENT, DNA_IUPAC


def complement(sequence: str, allow_iupac: bool = True) -> str:
    """
    获取 DNA 互补链
    
    Args:
        sequence: DNA 序列
        allow_iupac: 是否支持简并碱基
        
    Returns:
        互补序列
        
    Example:
        >>> complement("ATCG")
        'TAGC'
        >>> complement("MRWS")
        'KYWS'
    """
    seq = sequence.upper()
    
    if not allow_iupac:
        # 只处理标准碱基
        comp_map = {'A': 'T', 'T': 'A', 'G': 'C', 'C': 'G'}
        return ''.join(comp_map.get(c, 'N') for c in seq)
    
    return ''.join(DNA_COMPLEMENT.get(c, 'N') for c in seq)


def reverse_complement(sequence: str, allow_iupac: bool = True) -> str:
    """
    获取 DNA 反向互补链
    
    Args:
        sequence: DNA 序列
        allow_iupac: 是否支持简并碱基
        
    Returns:
        反向互补序列
        
    Example:
        >>> reverse_complement("ATCG")
        'CGAT'
    """
    return complement(sequence, allow_iupac)[::-1]


def gc_content(sequence: str, count_s: bool = True) -> float:
    """
    计算 GC 含量百分比
    
    Args:
        sequence: DNA 序列
        count_s: 是否将 S (G or C) 计入 GC
        
    Returns:
        GC 含量百分比 (0-100)
        
    Example:
        >>> gc_content("ATCG")
        50.0
        >>> gc_content("GCGC")
        100.0
    """
    seq = sequence.upper()
    if not seq:
        return 0.0
    
    gc_chars = {'G', 'C'}
    if count_s:
        gc_chars.add('S')
    
    gc_count = sum(1 for c in seq if c in gc_chars)
    return (gc_count / len(seq)) * 100


def base_composition(sequence: str, include_iupac: bool = False) -> Dict[str, int]:
    """
    计算碱基组成
    
    Args:
        sequence: DNA 序列
        include_iupac: 是否统计简并碱基
        
    Returns:
        碱基计数字典
        
    Example:
        >>> base_composition("ATCGATCG")
        {'A': 2, 'T': 2, 'C': 2, 'G': 2}
    """
    seq = sequence.upper()
    composition = Counter(seq)
    
    if not include_iupac:
        # 只返回标准碱基
        standard_bases = {'A', 'C', 'G', 'T'}
        return {base: composition.get(base, 0) for base in standard_bases}
    
    # 返回所有 IUPAC 碱基
    all_bases = set(DNA_IUPAC)
    return {base: composition.get(base, 0) for base in sorted(all_bases)}


def melting_temperature(
    sequence: str,
    method: str = "wallace",
    salt_conc: float = 50.0,  # mM
    dna_conc: float = 50.0,   # nM
) -> float:
    """
    计算 DNA 引物的熔解温度 (Tm)
    
    Args:
        sequence: DNA 序列（通常用于引物）
        method: 计算方法 ('wallace', 'salt_adjusted', 'nearest_neighbor')
        salt_conc: 盐浓度 (mM)
        dna_conc: DNA 浓度 (nM)
        
    Returns:
        熔解温度 (摄氏度)
        
    Note:
        - Wallace: 2°C*(A+T) + 4°C*(G+C)，适用于 <20bp
        - Salt adjusted: 适用于 20-50bp
        - Nearest neighbor: 最精确，需要热力学参数
        
    Example:
        >>> melting_temperature("ATCGATCGATCG")
        36.0
    """
    seq = sequence.upper()
    length = len(seq)
    
    if length == 0:
        return 0.0
    
    comp = base_composition(seq)
    a_count = comp.get('A', 0)
    t_count = comp.get('T', 0)
    g_count = comp.get('G', 0)
    c_count = comp.get('C', 0)
    
    if method == "wallace":
        # Wallace 法则: 2°C*(A+T) + 4°C*(G+C)
        return 2 * (a_count + t_count) + 4 * (g_count + c_count)
    
    elif method == "salt_adjusted":
        # Salt-adjusted: 64.9 + 41*(GC-16.4)/length - 500/length + 16.6*log10(salt/1000)
        import math
        gc_fraction = (g_count + c_count) / length
        tm = (64.9 + 41 * (gc_fraction * 100 - 16.4) / length 
              - 500 / length + 16.6 * math.log10(salt_conc / 1000))
        return tm
    
    elif method == "nearest_neighbor":
        # 最近邻法（简化版，使用 SantaLucia 1998 参数）
        # 完整实现需要所有二核苷酸的热力学参数
        import math
        
        # 简化的 NN 参数 (ΔH in kcal/mol, ΔS in cal/mol·K)
        nn_params = {
            'AA': (-7.9, -21.9), 'TT': (-7.9, -21.9),
            'AT': (-7.2, -20.4), 'TA': (-7.2, -20.4),
            'CA': (-8.5, -22.7), 'TG': (-8.5, -22.7),
            'GT': (-8.4, -22.4), 'AC': (-8.4, -22.4),
            'CT': (-7.8, -21.0), 'AG': (-7.8, -21.0),
            'GA': (-8.2, -22.2), 'TC': (-8.2, -22.2),
            'CG': (-10.6, -27.2), 'GC': (-9.8, -24.4),
            'GG': (-8.0, -19.9), 'CC': (-8.0, -19.9),
        }
        
        # 末端校正
        end_params = {
            'A': (2.2, 6.9), 'T': (2.2, 6.9),
            'G': (0.0, 0.0), 'C': (0.0, 0.0),
        }
        
        # 计算 ΔH 和 ΔS
        delta_h = 0.0
        delta_s = 0.0
        
        # 末端校正
        if seq[0] in end_params:
            dh, ds = end_params[seq[0]]
            delta_h += dh
            delta_s += ds
        if seq[-1] in end_params:
            dh, ds = end_params[seq[-1]]
            delta_h += dh
            delta_s += ds
        
        # 二核苷酸参数
        for i in range(length - 1):
            dinuc = seq[i:i+2]
            if dinuc in nn_params:
                dh, ds = nn_params[dinuc]
                delta_h += dh
                delta_s += ds
        
        # 盐浓度校正
        delta_s += 0.368 * (length - 1) * math.log(salt_conc / 1000)
        
        # 计算 Tm
        r = 1.987  # 气体常数 cal/mol·K
        tm = (delta_h * 1000) / (delta_s + r * math.log(dna_conc / 1e9)) - 273.15
        
        return tm
    
    else:
        raise ValueError(f"Unknown method: {method}")


def molecular_weight(sequence: str, strand: str = "ds") -> float:
    """
    计算 DNA 分子量
    
    Args:
        sequence: DNA 序列
        strand: 'ss' (单链) 或 'ds' (双链)
        
    Returns:
        分子量 (Da)
        
    Note:
        使用平均核苷酸分子量:
        dAMP: 313.21, dTMP: 304.20, dGMP: 329.21, dCMP: 289.18
        减去水分子 (18.02)
    """
    seq = sequence.upper()
    
    # 平均核苷酸分子量 (减去一个水分子)
    mw_table = {
        'A': 313.21 - 18.02,
        'T': 304.20 - 18.02,
        'G': 329.21 - 18.02,
        'C': 289.18 - 18.02,
    }
    
    # 计算单链分子量
    ss_mw = sum(mw_table.get(c, 0) for c in seq)
    ss_mw += 18.02  # 加回末端水分子
    
    if strand == "ss":
        return ss_mw
    elif strand == "ds":
        # 双链 = 单链 + 互补链
        comp_seq = complement(seq)
        comp_mw = sum(mw_table.get(c, 0) for c in comp_seq)
        comp_mw += 18.02
        return ss_mw + comp_mw
    else:
        raise ValueError(f"strand must be 'ss' or 'ds', got {strand}")


def is_palindrome(sequence: str, allow_iupac: bool = False) -> bool:
    """
    检查序列是否为回文序列（反向互补等于自身）
    
    Args:
        sequence: DNA 序列
        allow_iupac: 是否考虑简并碱基
        
    Returns:
        是否为回文序列
        
    Example:
        >>> is_palindrome("GAATTC")  # EcoRI 位点
        True
    """
    seq = sequence.upper()
    return seq == reverse_complement(seq, allow_iupac)


def find_restriction_sites(sequence: str, site: str) -> list[int]:
    """
    查找限制酶切位点位置
    
    Args:
        sequence: DNA 序列
        site: 限制酶识别位点
        
    Returns:
        位点起始位置列表 (1-based)
        
    Example:
        >>> find_restriction_sites("GAATTCGAATTC", "GAATTC")
        [1, 7]
    """
    seq = sequence.upper()
    site = site.upper()
    
    positions = []
    start = 0
    while True:
        pos = seq.find(site, start)
        if pos == -1:
            break
        positions.append(pos + 1)  # 转换为 1-based
        start = pos + 1
    
    return positions
