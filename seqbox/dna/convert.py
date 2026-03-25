"""
Seq_Box - DNA 转换模块

提供 DNA 序列的转录、翻译、ORF 搜索等功能
"""

from __future__ import annotations
from typing import Dict, List, Optional, Iterator, NamedTuple
from dataclasses import dataclass


# ========== 密码子表 ==========

# 标准密码子表 (NCBI Table 1)
STANDARD_CODON_TABLE: Dict[str, str] = {
    # Phenylalanine
    'UUU': 'F', 'UUC': 'F',
    # Leucine
    'UUA': 'L', 'UUG': 'L', 'CUU': 'L', 'CUC': 'L', 'CUA': 'L', 'CUG': 'L',
    # Isoleucine
    'AUU': 'I', 'AUC': 'I', 'AUA': 'I',
    # Methionine (Start)
    'AUG': 'M',
    # Valine
    'GUU': 'V', 'GUC': 'V', 'GUA': 'V', 'GUG': 'V',
    # Serine
    'UCU': 'S', 'UCC': 'S', 'UCA': 'S', 'UCG': 'S', 'AGU': 'S', 'AGC': 'S',
    # Proline
    'CCU': 'P', 'CCC': 'P', 'CCA': 'P', 'CCG': 'P',
    # Threonine
    'ACU': 'T', 'ACC': 'T', 'ACA': 'T', 'ACG': 'T',
    # Alanine
    'GCU': 'A', 'GCC': 'A', 'GCA': 'A', 'GCG': 'A',
    # Tyrosine
    'UAU': 'Y', 'UAC': 'Y',
    # Stop
    'UAA': '*', 'UAG': '*', 'UGA': '*',
    # Histidine
    'CAU': 'H', 'CAC': 'H',
    # Glutamine
    'CAA': 'Q', 'CAG': 'Q',
    # Asparagine
    'AAU': 'N', 'AAC': 'N',
    # Lysine
    'AAA': 'K', 'AAG': 'K',
    # Aspartic acid
    'GAU': 'D', 'GAC': 'D',
    # Glutamic acid
    'GAA': 'E', 'GAG': 'E',
    # Cysteine
    'UGU': 'C', 'UGC': 'C',
    # Tryptophan
    'UGG': 'W',
    # Arginine
    'CGU': 'R', 'CGC': 'R', 'CGA': 'R', 'CGG': 'R', 'AGA': 'R', 'AGG': 'R',
    # Glycine
    'GGU': 'G', 'GGC': 'G', 'GGA': 'G', 'GGG': 'G',
}

# 线粒体密码子表 (脊椎动物, NCBI Table 2)
VERTEBRATE_MITO_CODON_TABLE: Dict[str, str] = {
    **STANDARD_CODON_TABLE,
    'AGA': '*', 'AGG': '*',  # 精氨酸变为终止
    'AUA': 'M',              # 异亮氨酸变为甲硫氨酸
    'UGA': 'W',              # 终止变为色氨酸
}

# 细菌密码子表 (与标准相同，但起始密码子不同)
BACTERIAL_CODON_TABLE: Dict[str, str] = STANDARD_CODON_TABLE.copy()

# 酵母线粒体密码子表 (NCBI Table 3)
YEAST_MITO_CODON_TABLE: Dict[str, str] = {
    **STANDARD_CODON_TABLE,
    'CUN': 'T',  # CUN 编码苏氨酸而非亮氨酸
    'AUA': 'M',
    'UGA': 'W',
    'CGA': '*', 'CGC': '*',
}

# 起始密码子集合
START_CODONS_STANDARD = {'AUG'}
START_CODONS_BACTERIAL = {'AUG', 'GUG', 'UUG'}  # 细菌常用起始密码子

# 终止密码子集合
STOP_CODONS = {'UAA', 'UAG', 'UGA'}


class CodonTable:
    """密码子表类"""
    
    def __init__(
        self,
        table: Dict[str, str],
        name: str = "Standard",
        start_codons: Optional[set] = None
    ):
        self.table = table
        self.name = name
        self.start_codons = start_codons or START_CODONS_STANDARD
    
    def translate(self, codon: str) -> str:
        """翻译单个密码子"""
        codon = codon.upper().replace('T', 'U')
        return self.table.get(codon, 'X')
    
    def is_start(self, codon: str) -> bool:
        """检查是否为起始密码子"""
        codon = codon.upper().replace('T', 'U')
        return codon in self.start_codons
    
    def is_stop(self, codon: str) -> bool:
        """检查是否为终止密码子"""
        codon = codon.upper().replace('T', 'U')
        return self.translate(codon) == '*'


# 预定义密码子表实例
CODON_TABLES = {
    'standard': CodonTable(STANDARD_CODON_TABLE, "Standard", START_CODONS_STANDARD),
    'vertebrate_mitochondrial': CodonTable(VERTEBRATE_MITO_CODON_TABLE, "Vertebrate Mitochondrial", {'AUG', 'AUA', 'AUU'}),
    'bacterial': CodonTable(BACTERIAL_CODON_TABLE, "Bacterial", START_CODONS_BACTERIAL),
    'yeast_mitochondrial': CodonTable(YEAST_MITO_CODON_TABLE, "Yeast Mitochondrial", {'AUG'}),
}


def get_codon_table(table_name: str = 'standard') -> CodonTable:
    """
    获取密码子表
    
    Args:
        table_name: 密码子表名称
                   ('standard', 'vertebrate_mitochondrial', 
                    'bacterial', 'yeast_mitochondrial')
    
    Returns:
        CodonTable 对象
    """
    if table_name not in CODON_TABLES:
        raise ValueError(f"Unknown codon table: {table_name}. "
                        f"Available: {list(CODON_TABLES.keys())}")
    return CODON_TABLES[table_name]


# ========== 转录功能 ==========

def transcribe(dna_sequence: str) -> str:
    """
    DNA 转录为 RNA (T → U)
    
    Args:
        dna_sequence: DNA 序列
        
    Returns:
        RNA 序列
        
    Example:
        >>> transcribe("ATCG")
        'AUCG'
    """
    return dna_sequence.upper().replace('T', 'U')


def reverse_transcribe(rna_sequence: str) -> str:
    """
    RNA 逆转录为 DNA (U → T)
    
    Args:
        rna_sequence: RNA 序列
        
    Returns:
        DNA 序列
        
    Example:
        >>> reverse_transcribe("AUCG")
        'ATCG'
    """
    return rna_sequence.upper().replace('U', 'T')


# ========== 翻译功能 ==========

def translate(
    sequence: str,
    table: str | CodonTable = 'standard',
    to_stop: bool = True,
    cds: bool = False
) -> str:
    """
    翻译核酸序列为蛋白质
    
    Args:
        sequence: DNA 或 RNA 序列
        table: 密码子表名称或对象
        to_stop: 遇到终止密码子是否停止
        cds: 序列是否为完整 CDS（必须包含起始密码子并以终止密码子结束）
        
    Returns:
        蛋白质序列（单字母表示）
        
    Raises:
        ValueError: 如果 cds=True 但序列不符合 CDS 格式
        
    Example:
        >>> translate("ATGAAATTT")
        'MKF'
        >>> translate("AUGAAAUUU")  # RNA 也可以
        'MKF'
    """
    # 统一转为 RNA（U）
    seq = sequence.upper().replace('T', 'U')
    
    # 获取密码子表
    if isinstance(table, str):
        codon_table = get_codon_table(table)
    else:
        codon_table = table
    
    # CDS 验证
    if cds:
        if len(seq) % 3 != 0:
            raise ValueError("CDS length must be a multiple of 3")
        if not codon_table.is_start(seq[:3]):
            raise ValueError(f"CDS must start with a start codon, got {seq[:3]}")
        if not codon_table.is_stop(seq[-3:]):
            raise ValueError(f"CDS must end with a stop codon, got {seq[-3:]}")
    
    # 翻译
    protein = []
    for i in range(0, len(seq) - 2, 3):
        codon = seq[i:i+3]
        aa = codon_table.translate(codon)
        
        if aa == '*':
            if to_stop:
                break
            else:
                protein.append(aa)
        else:
            protein.append(aa)
    
    return ''.join(protein)


def translate_six_frames(
    sequence: str,
    table: str | CodonTable = 'standard',
    min_length: int = 0
) -> Dict[int, str]:
    """
    六框翻译（3个正向读框 + 3个反向互补读框）
    
    Args:
        sequence: DNA 序列
        table: 密码子表名称或对象
        min_length: 最小蛋白质长度过滤
        
    Returns:
        字典 {读框: 蛋白质序列}
        
    Example:
        >>> result = translate_six_frames("ATGAAATGATAA")
        >>> result[1]  # 正向读框 1
        'MK*'
    """
    from .basic import reverse_complement
    
    seq = sequence.upper()
    results = {}
    
    # 正向 3 个读框
    for frame in range(3):
        protein = translate(seq[frame:], table, to_stop=False)
        if len(protein) >= min_length:
            results[frame + 1] = protein
    
    # 反向互补 3 个读框
    rc_seq = reverse_complement(seq)
    for frame in range(3):
        protein = translate(rc_seq[frame:], table, to_stop=False)
        if len(protein) >= min_length:
            results[-(frame + 1)] = protein  # -1, -2, -3
    
    return results


# ========== ORF 搜索 ==========

@dataclass
class ORF:
    """开放阅读框对象"""
    start: int           # 起始位置 (1-based)
    end: int             # 终止位置 (1-based, 包含)
    frame: int           # 读框 (1, 2, 3, -1, -2, -3)
    sequence: str        # DNA 序列
    protein: str         # 蛋白质序列
    start_codon: str     # 起始密码子
    stop_codon: str      # 终止密码子
    
    def __len__(self) -> int:
        """ORF 长度 (nt)"""
        return self.end - self.start + 1
    
    @property
    def protein_length(self) -> int:
        """蛋白质长度 (aa)"""
        return len(self.protein)
    
    def to_fasta(self, prefix: str = "ORF") -> str:
        """转换为 FASTA 格式"""
        header = f">{prefix}_frame{self.frame}_{self.start}-{self.end} len={self.protein_length}aa"
        return f"{header}\n{self.sequence}"


def find_orfs(
    sequence: str,
    table: str | CodonTable = 'standard',
    min_length: int = 100,      # 最小蛋白质长度
    max_overlap: int = 0,       # 最大重叠长度 (0 = 不允许重叠)
    find_nested: bool = False,  # 是否查找嵌套 ORF
) -> List[ORF]:
    """
    搜索序列中的开放阅读框 (ORF)
    
    Args:
        sequence: DNA 序列
        table: 密码子表名称或对象
        min_length: 最小蛋白质长度 (氨基酸数)
        max_overlap: 允许的最大 ORF 重叠 (nt)
        find_nested: 是否查找嵌套 ORF
        
    Returns:
        ORF 对象列表（按起始位置排序）
        
    Example:
        >>> orfs = find_orfs("ATGAAATAA", min_length=1)
        >>> len(orfs)
        1
        >>> orfs[0].protein
        'MK'
    """
    from .basic import reverse_complement
    
    seq = sequence.upper()
    
    # 获取密码子表
    if isinstance(table, str):
        codon_table = get_codon_table(table)
    else:
        codon_table = table
    
    orfs = []
    
    # 搜索正向读框
    for frame in range(3):
        orfs.extend(_find_orfs_in_frame(
            seq, frame + 1, codon_table, min_length
        ))
    
    # 搜索反向读框
    rc_seq = reverse_complement(seq)
    for frame in range(3):
        orfs.extend(_find_orfs_in_frame(
            rc_seq, -(frame + 1), codon_table, min_length,
            original_seq=seq, is_reverse=True
        ))
    
    # 按起始位置排序
    orfs.sort(key=lambda x: (abs(x.frame), x.start))
    
    # 处理重叠
    if not find_nested and max_overlap == 0:
        orfs = _remove_overlapping_orfs(orfs)
    
    return orfs


def _find_orfs_in_frame(
    seq: str,
    frame: int,
    codon_table: CodonTable,
    min_length: int,
    original_seq: Optional[str] = None,
    is_reverse: bool = False
) -> List[ORF]:
    """在单个读框中搜索 ORF"""
    orfs = []
    seq_len = len(seq)
    
    # 计算读框偏移
    offset = abs(frame) - 1
    
    # 查找所有起始和终止密码子位置
    i = offset
    while i <= seq_len - 3:
        codon = seq[i:i+3]
        
        if codon_table.is_start(codon):
            # 找到起始密码子，向后搜索终止密码子
            for j in range(i + 3, seq_len - 2, 3):
                stop_codon = seq[j:j+3]
                
                if codon_table.is_stop(stop_codon):
                    # 找到完整的 ORF
                    orf_seq = seq[i:j+3]
                    protein = translate(orf_seq, codon_table, to_stop=False)
                    
                    # 检查最小长度
                    if len(protein) - 1 >= min_length:  # -1 排除终止密码子
                        # 计算在原序列中的位置
                        if is_reverse:
                            # 反向互补：需要转换坐标
                            orig_start = seq_len - (j + 3) + 1
                            orig_end = seq_len - i
                        else:
                            orig_start = i + 1
                            orig_end = j + 3
                        
                        # 获取原始序列（非反向互补）
                        if is_reverse and original_seq:
                            orf_dna = reverse_complement(orf_seq)
                        else:
                            orf_dna = orf_seq
                        
                        orfs.append(ORF(
                            start=orig_start,
                            end=orig_end,
                            frame=frame,
                            sequence=orf_dna,
                            protein=protein[:-1],  # 不包含终止密码子
                            start_codon=codon,
                            stop_codon=stop_codon
                        ))
                    
                    break  # 找到最近的终止密码子
        
        i += 3
    
    return orfs


def _remove_overlapping_orfs(orfs: List[ORF]) -> List[ORF]:
    """移除重叠的 ORF，保留较长的"""
    if not orfs:
        return []
    
    # 按长度降序排序
    sorted_orfs = sorted(orfs, key=lambda x: len(x), reverse=True)
    
    kept = []
    for orf in sorted_orfs:
        # 检查是否与已保留的 ORF 重叠
        overlaps = False
        for kept_orf in kept:
            if orf.frame == kept_orf.frame:
                # 同一读框才检查重叠
                if not (orf.end < kept_orf.start or orf.start > kept_orf.end):
                    overlaps = True
                    break
        
        if not overlaps:
            kept.append(orf)
    
    # 按起始位置重新排序
    kept.sort(key=lambda x: (abs(x.frame), x.start))
    return kept


def longest_orf(sequence: str, table: str | CodonTable = 'standard') -> Optional[ORF]:
    """
    查找最长的 ORF
    
    Args:
        sequence: DNA 序列
        table: 密码子表名称或对象
        
    Returns:
        最长的 ORF，如果没有则返回 None
    """
    orfs = find_orfs(sequence, table, min_length=0)
    if not orfs:
        return None
    return max(orfs, key=lambda x: len(x))
