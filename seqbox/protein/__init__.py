"""
Seq_Box - 蛋白质操作模块

提供蛋白质序列的转换和分析功能
"""

from .convert import (
    to_triple,
    from_triple,
    get_amino_acid_name,
    get_amino_acid_property,
)
from .property import (
    ProteinProperties,
    MultiChainProtein,
    analyze_sequence,
    analyze_sequences,
    calculate_molecular_weight,
    calculate_pi,
    calculate_absorbance,
    calculate_gravy,
)
from .analysis import (
    AnalysisResult,
    analyze_fasta_file,
    analyze_fasta_text,
    format_molecular_weight,
    format_gravy,
    format_pi,
)

__all__ = [
    # 转换
    'to_triple',
    'from_triple',
    'get_amino_acid_name',
    'get_amino_acid_property',
    # 性质计算
    'ProteinProperties',
    'MultiChainProtein',
    'analyze_sequence',
    'analyze_sequences',
    'calculate_molecular_weight',
    'calculate_pi',
    'calculate_absorbance',
    'calculate_gravy',
    # 分析
    'AnalysisResult',
    'analyze_fasta_file',
    'analyze_fasta_text',
    'format_molecular_weight',
    'format_gravy',
    'format_pi',
]
