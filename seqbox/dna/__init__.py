"""
Seq_Box - DNA 操作模块

提供 DNA 序列的基础操作和转换功能
"""

from .basic import (
    complement,
    reverse_complement,
    gc_content,
    base_composition,
    melting_temperature,
)

from .convert import (
    transcribe,
    reverse_transcribe,
    translate,
    translate_six_frames,
    find_orfs,
    get_codon_table,
)

__all__ = [
    # basic
    'complement',
    'reverse_complement',
    'gc_content',
    'base_composition',
    'melting_temperature',
    # convert
    'transcribe',
    'reverse_transcribe',
    'translate',
    'translate_six_frames',
    'find_orfs',
    'get_codon_table',
]
