"""
Seq_Box - 核心序列类

提供统一的序列对象，支持切片、索引、迭代
"""

from __future__ import annotations
from typing import Iterator, Optional, Any
from dataclasses import dataclass, field

from .alphabets import (
    DNA_IUPAC, DNA_COMPLEMENT,
    RNA_IUPAC, RNA_COMPLEMENT,
    PROTEIN_EXTENDED,
    validate_dna, validate_rna, validate_protein,
    clean_sequence, guess_sequence_type
)


class Sequence:
    """
    通用序列基类（不可变）
    
    Attributes:
        seq: 序列字符串（大写）
        id: 序列 ID
        description: 序列描述
        seq_type: 序列类型（'dna', 'rna', 'protein', 'unknown'）
    """
    
    __slots__ = ('seq', 'id', 'description', 'seq_type')
    
    def __init__(
        self,
        seq: str,
        id: str = "",
        description: str = "",
        seq_type: str = "unknown"
    ):
        object.__setattr__(self, 'seq', seq.upper())
        object.__setattr__(self, 'id', id)
        object.__setattr__(self, 'description', description)
        object.__setattr__(self, 'seq_type', seq_type)
    
    def __setattr__(self, name, value):
        object.__setattr__(self, name, value)
    
    def __len__(self) -> int:
        return len(self.seq)
    
    def __getitem__(self, key: int | slice) -> str | Sequence:
        """支持切片和索引"""
        result = self.seq[key]
        if isinstance(key, slice):
            return Sequence(
                seq=result,
                id=f"{self.id}_slice",
                description=f"Slice of {self.id}",
                seq_type=self.seq_type
            )
        return result
    
    def __iter__(self) -> Iterator[str]:
        return iter(self.seq)
    
    def __str__(self) -> str:
        return self.seq
    
    def __repr__(self) -> str:
        desc = f" desc='{self.description}'" if self.description else ""
        return f"Sequence({self.seq_type}, id='{self.id}', len={len(self)}{desc})"
    
    def __eq__(self, other: Any) -> bool:
        """基于序列内容比较，忽略 ID"""
        if not isinstance(other, Sequence):
            return NotImplemented
        return self.seq == other.seq
    
    def __hash__(self) -> int:
        """基于序列内容哈希，用于去重"""
        return hash(self.seq)
    
    @property
    def length(self) -> int:
        """序列长度"""
        return len(self.seq)
    
    def to_fasta(self, line_width: int = 60) -> str:
        """
        转换为 FASTA 格式字符串
        
        Args:
            line_width: 每行字符数
            
        Returns:
            FASTA 格式字符串
        """
        header = f">{self.id}"
        if self.description:
            header += f" {self.description}"
        
        lines = [header]
        for i in range(0, len(self.seq), line_width):
            lines.append(self.seq[i:i + line_width])
        
        return '\n'.join(lines)
    
    def subseq(self, start: int, end: int) -> Sequence:
        """
        提取子序列（1-based，包含 start 和 end）
        
        Args:
            start: 起始位置（1-based）
            end: 终止位置（1-based，包含）
            
        Returns:
            子序列对象
        """
        # 处理负索引
        if start < 0:
            start = len(self.seq) + start + 1
        if end < 0:
            end = len(self.seq) + end + 1
        
        # 转换为 0-based
        start_idx = max(0, start - 1)
        end_idx = min(len(self.seq), end)
        
        return Sequence(
            seq=self.seq[start_idx:end_idx],
            id=f"{self.id}_{start}_{end}",
            description=f"Subsequence {start}-{end} of {self.id}",
            seq_type=self.seq_type
        )


class DNASequence(Sequence):
    """DNA 序列子类"""
    
    def __init__(
        self,
        seq: str,
        id: str = "",
        description: str = "",
        validate: bool = True,
        allow_iupac: bool = True
    ):
        seq = seq.upper()
        
        if validate:
            is_valid, invalid = validate_dna(seq, allow_iupac)
            if not is_valid:
                invalid_str = ', '.join(sorted(invalid))
                raise ValueError(f"Invalid DNA characters: {invalid_str}")
        
        # 使用 object.__setattr__ 绕过 frozen dataclass 的限制
        object.__setattr__(self, 'seq', seq)
        object.__setattr__(self, 'id', id)
        object.__setattr__(self, 'description', description)
        object.__setattr__(self, 'seq_type', 'dna')
        object.__setattr__(self, '_allow_iupac', allow_iupac)
    
    def complement(self) -> DNASequence:
        """返回互补链"""
        comp_seq = ''.join(DNA_COMPLEMENT.get(c, 'N') for c in self.seq)
        return DNASequence(
            seq=comp_seq,
            id=f"{self.id}_complement",
            description=f"Complement of {self.id}",
            validate=False
        )
    
    def reverse_complement(self) -> DNASequence:
        """返回反向互补链"""
        return DNASequence(
            seq=self.complement().seq[::-1],
            id=f"{self.id}_reverse_complement",
            description=f"Reverse complement of {self.id}",
            validate=False
        )
    
    def gc_content(self) -> float:
        """计算 GC 含量百分比"""
        if not self.seq:
            return 0.0
        gc_count = sum(1 for c in self.seq if c in 'GCS')
        return (gc_count / len(self.seq)) * 100
    
    def base_composition(self) -> dict[str, int]:
        """计算碱基组成"""
        composition = {base: 0 for base in 'ACGT'}
        for c in self.seq:
            if c in composition:
                composition[c] += 1
            elif c == 'N':
                # N 不计入标准碱基
                pass
        return composition
    
    def transcribe(self) -> RNASequence:
        """转录为 RNA（T → U）"""
        rna_seq = self.seq.replace('T', 'U')
        return RNASequence(
            seq=rna_seq,
            id=self.id,
            description=self.description,
            validate=False
        )


class RNASequence(Sequence):
    """RNA 序列子类"""
    
    def __init__(
        self,
        seq: str,
        id: str = "",
        description: str = "",
        validate: bool = True,
        allow_iupac: bool = True
    ):
        seq = seq.upper()
        
        if validate:
            is_valid, invalid = validate_rna(seq, allow_iupac)
            if not is_valid:
                invalid_str = ', '.join(sorted(invalid))
                raise ValueError(f"Invalid RNA characters: {invalid_str}")
        
        # 使用 object.__setattr__ 绕过 frozen dataclass 的限制
        object.__setattr__(self, 'seq', seq)
        object.__setattr__(self, 'id', id)
        object.__setattr__(self, 'description', description)
        object.__setattr__(self, 'seq_type', 'rna')
        object.__setattr__(self, '_allow_iupac', allow_iupac)
    
    def complement(self) -> RNASequence:
        """返回互补链"""
        comp_seq = ''.join(RNA_COMPLEMENT.get(c, 'N') for c in self.seq)
        return RNASequence(
            seq=comp_seq,
            id=f"{self.id}_complement",
            description=f"Complement of {self.id}",
            validate=False
        )
    
    def reverse_complement(self) -> RNASequence:
        """返回反向互补链"""
        return RNASequence(
            seq=self.complement().seq[::-1],
            id=f"{self.id}_reverse_complement",
            description=f"Reverse complement of {self.id}",
            validate=False
        )
    
    def reverse_transcribe(self) -> DNASequence:
        """逆转录为 DNA（U → T）"""
        dna_seq = self.seq.replace('U', 'T')
        return DNASequence(
            seq=dna_seq,
            id=self.id,
            description=self.description,
            validate=False
        )


class ProteinSequence(Sequence):
    """蛋白质序列子类"""
    
    def __init__(
        self,
        seq: str,
        id: str = "",
        description: str = "",
        validate: bool = True,
        allow_extended: bool = True
    ):
        seq = seq.upper()
        
        if validate:
            is_valid, invalid = validate_protein(seq, allow_extended)
            if not is_valid:
                invalid_str = ', '.join(sorted(invalid))
                raise ValueError(f"Invalid protein characters: {invalid_str}")
        
        # 使用 object.__setattr__ 绕过 frozen dataclass 的限制
        object.__setattr__(self, 'seq', seq)
        object.__setattr__(self, 'id', id)
        object.__setattr__(self, 'description', description)
        object.__setattr__(self, 'seq_type', 'protein')
        object.__setattr__(self, '_allow_extended', allow_extended)
    
    def to_triple(self, separator: str = '-') -> str:
        """
        单字母转换为三字母表示
        
        Args:
            separator: 分隔符，默认 '-'
            
        Returns:
            三字母序列，如 "Ala-Cys-Asp"
        """
        from .alphabets import AA_SINGLE_TO_TRIPLE
        triple_list = [AA_SINGLE_TO_TRIPLE.get(aa, 'Xaa') for aa in self.seq]
        return separator.join(triple_list)
    
    @classmethod
    def from_triple(cls, triple_seq: str, id: str = "", description: str = "") -> ProteinSequence:
        """
        从三字母表示创建蛋白质序列
        
        Args:
            triple_seq: 三字母序列，如 "Ala Cys Asp" 或 "Ala-Cys-Asp"
            id: 序列 ID
            description: 序列描述
            
        Returns:
            ProteinSequence 对象
        """
        from .alphabets import AA_TRIPLE_TO_SINGLE
        
        # 统一分隔符为空格
        triple_seq = triple_seq.replace('-', ' ')
        triples = triple_seq.split()
        
        single_seq = ''.join(AA_TRIPLE_TO_SINGLE.get(t, 'X') for t in triples)
        
        return cls(
            seq=single_seq,
            id=id,
            description=description,
            validate=False
        )
    
    def reverse(self) -> ProteinSequence:
        """序列反转（N端 ↔ C端）"""
        return ProteinSequence(
            seq=self.seq[::-1],
            id=f"{self.id}_reversed",
            description=f"Reversed {self.id}",
            validate=False
        )


def create_sequence(
    seq: str,
    seq_type: Optional[str] = None,
    id: str = "",
    description: str = "",
    auto_detect: bool = True
) -> Sequence:
    """
    工厂函数：根据类型或自动检测创建对应序列对象
    
    Args:
        seq: 序列字符串
        seq_type: 指定类型 ('dna', 'rna', 'protein')，None 则自动检测
        id: 序列 ID
        description: 序列描述
        auto_detect: 是否允许自动检测类型
        
    Returns:
        Sequence / DNASequence / RNASequence / ProteinSequence 对象
    """
    if seq_type is None and auto_detect:
        seq_type = guess_sequence_type(seq)
    
    seq_type = (seq_type or 'unknown').lower()
    
    if seq_type == 'dna':
        return DNASequence(seq=seq, id=id, description=description)
    elif seq_type == 'rna':
        return RNASequence(seq=seq, id=id, description=description)
    elif seq_type == 'protein':
        return ProteinSequence(seq=seq, id=id, description=description)
    else:
        return Sequence(seq=seq, id=id, description=description, seq_type='unknown')
