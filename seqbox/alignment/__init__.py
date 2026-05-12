"""
Seq_Box - Sequence Alignment Module
"""

from .cluster import (
    align_sequences,
    calculate_identity_matrix,
    format_identity_matrix_uniprot,
    generate_html_report,
    format_msa_text,
    format_msa_html_colored,
    CLUSTAL_OMEGA_AVAILABLE,
    CLUSTAL_OMEGA_PATH,
)

__all__ = [
    "align_sequences",
    "calculate_identity_matrix",
    "format_identity_matrix_uniprot",
    "generate_html_report",
    "format_msa_text",
    "format_msa_html_colored",
    "CLUSTAL_OMEGA_AVAILABLE",
    "CLUSTAL_OMEGA_PATH",
]
