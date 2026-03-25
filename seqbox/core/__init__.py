"""
Seq_Box - 核心模块

提供序列对象和字符集定义
"""

from .alphabets import (
    # DNA
    DNA_STANDARD,
    DNA_IUPAC,
    DNA_IUPAC_MEANING,
    DNA_COMPLEMENT,
    # RNA
    RNA_STANDARD,
    RNA_IUPAC,
    RNA_COMPLEMENT,
    # Protein
    PROTEIN_STANDARD,
    PROTEIN_EXTENDED,
    AA_SINGLE_TO_TRIPLE,
    AA_TRIPLE_TO_SINGLE,
    AA_NAMES,
    # Functions
    validate_dna,
    validate_rna,
    validate_protein,
    guess_sequence_type,
    clean_sequence,
)

from .sequence import (
    Sequence,
    DNASequence,
    RNASequence,
    ProteinSequence,
    create_sequence,
)

__all__ = [
    # Alphabets
    'DNA_STANDARD',
    'DNA_IUPAC',
    'DNA_IUPAC_MEANING',
    'DNA_COMPLEMENT',
    'RNA_STANDARD',
    'RNA_IUPAC',
    'RNA_COMPLEMENT',
    'PROTEIN_STANDARD',
    'PROTEIN_EXTENDED',
    'AA_SINGLE_TO_TRIPLE',
    'AA_TRIPLE_TO_SINGLE',
    'AA_NAMES',
    # Functions
    'validate_dna',
    'validate_rna',
    'validate_protein',
    'guess_sequence_type',
    'clean_sequence',
    # Classes
    'Sequence',
    'DNASequence',
    'RNASequence',
    'ProteinSequence',
    'create_sequence',
]
