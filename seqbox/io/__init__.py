"""
Seq_Box - I/O 模块

提供序列文件读写功能
"""

from .fasta import (
    FastaRecord,
    FastaReader,
    FastaWriter,
    SeqType,
    CleanStats,
    DuplicateIDHandling,
    MergeStats,
    read_fasta,
    parse_fasta,
    write_fasta,
    write_sequences,
    parse_fasta_string,
    to_fasta_string,
    clean_fasta,
    clean_sequence_string,
    split_fasta_by_count,
    split_fasta_into_n_files,
    split_fasta_by_id_list,
    split_fasta_to_single_files,
    merge_fasta_files,
    merge_fasta_from_directory,
)

__all__ = [
    'FastaRecord',
    'FastaReader',
    'FastaWriter',
    'SeqType',
    'CleanStats',
    'DuplicateIDHandling',
    'MergeStats',
    'read_fasta',
    'parse_fasta',
    'write_fasta',
    'write_sequences',
    'parse_fasta_string',
    'to_fasta_string',
    'clean_fasta',
    'clean_sequence_string',
    'split_fasta_by_count',
    'split_fasta_into_n_files',
    'split_fasta_by_id_list',
    'split_fasta_to_single_files',
    'merge_fasta_files',
    'merge_fasta_from_directory',
]
