"""
Seq_Box - GUI 页面模块
"""

from .fasta_page import FastaPage
from .dna_page import DnaPage
from .protein_page import ProteinPage
from .history_page import HistoryPage
from .settings_page import SettingsPage
from .align_page import AlignPage

__all__ = ['FastaPage', 'DnaPage', 'ProteinPage', 'HistoryPage', 'SettingsPage', 'AlignPage']
