"""
Seq_Box - DNA/蛋白质序列操作工具箱

版本: 0.1.5
"""

__version__ = "0.4.1"
__author__ = "Seq_Box Team"

from seqbox.core import Sequence, DNASequence, RNASequence, ProteinSequence
from seqbox.io.fasta import FastaRecord, FastaReader, FastaWriter

__all__ = [
    "__version__",
    "Sequence",
    "DNASequence",
    "RNASequence",
    "ProteinSequence",
    "FastaRecord",
    "FastaReader",
    "FastaWriter",
]
