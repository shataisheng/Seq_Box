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

__all__ = [
    'to_triple',
    'from_triple',
    'get_amino_acid_name',
    'get_amino_acid_property',
]
