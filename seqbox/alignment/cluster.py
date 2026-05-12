"""
Sequence Alignment Module
支持 Clustal Omega 和纯 Python 算法
"""

import subprocess
import tempfile
import shutil
from pathlib import Path
from typing import List, Optional, Tuple
import sys

try:
    from Bio import Align
    from Bio.Align import PairwiseAligner
    BIOPYTHON_AVAILABLE = True
except ImportError:
    BIOPYTHON_AVAILABLE = False

_clustalo_path_cache: Optional[str] = None
_clustalo_searched: bool = False


def _find_clustalo_executable() -> Optional[str]:
    """查找 clustalo 可执行文件路径（惰性查找，结果缓存）"""
    global _clustalo_path_cache, _clustalo_searched
    if _clustalo_searched:
        return _clustalo_path_cache
    _clustalo_searched = True

    import os
    # 优先从项目目录查找（相对于本文件向上两级）
    project_clustalo = os.path.join(
        os.path.dirname(__file__), "..", "..",
        "clustal-omega-1.2.4-win64", "clustalo.exe"
    )
    possible_paths = [
        "clustalo",
        os.path.normpath(project_clustalo),
    ]
    for path in possible_paths:
        try:
            result = subprocess.run(
                [path, "--version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                _clustalo_path_cache = path
                return path
        except (FileNotFoundError, subprocess.TimeoutExpired, OSError):
            continue
    return None


def _get_clustalo_info():
    """惰性获取 Clustal Omega 信息"""
    path = _find_clustalo_executable()
    return path, path is not None


# 模块级变量保持兼容，但不再在导入时执行 subprocess
CLUSTAL_OMEGA_PATH: Optional[str] = None
CLUSTAL_OMEGA_AVAILABLE: bool = False

from seqbox.io.fasta import FastaRecord


def align_sequences(
    records: List[FastaRecord],
    method: str = "auto",
    gap_open: float = -10.0,
    gap_extend: float = -1.0,
) -> Tuple[List[FastaRecord], str, List[List[float]]]:
    """
    对序列进行多序列比对

    Args:
        records: FastaRecord 列表
        method: 比对方法，"clustalo", "needleman-wunsch", "auto"
        gap_open: gap 开口罚分
        gap_extend: gap 延长罚分

    Returns:
        Tuple[List[FastaRecord], str, List[List[float]]]: 比对后的序列列表、比对结果字符串和 identity 矩阵
    """
    if len(records) < 2:
        raise ValueError("需要至少 2 条序列进行比对")

    for record in records:
        if not record.seq:
            raise ValueError(f"序列 {record.id} 为空")

    seqs = [r.seq for r in records]

    if method == "auto":
        if _find_clustalo_executable():
            method = "clustalo"
        elif BIOPYTHON_AVAILABLE:
            method = "needleman-wunsch"
        else:
            raise RuntimeError(
                "无可用的比对工具。请安装 Clustal Omega 或 Biopython:\n"
                "  Clustal Omega: conda install -c bioconda clustalo\n"
                "  Biopython: pip install biopython"
            )

    if method == "clustalo":
        return _align_with_clustalo(records, seqs)
    elif method == "needleman-wunsch":
        aligned_records, align_text = _align_with_needleman_wunsch(records, seqs, gap_open, gap_extend)
        identity_matrix = calculate_identity_matrix(aligned_records)
        return aligned_records, align_text, identity_matrix
    else:
        raise ValueError(f"未知的比对方法: {method}")


def _align_with_clustalo(
    records: List[FastaRecord],
    seqs: List[str],
) -> Tuple[List[FastaRecord], str, List[List[float]]]:
    """使用 Clustal Omega 进行多序列比对"""
    temp_dir = Path(tempfile.mkdtemp())
    try:
        input_file = temp_dir / "input.fasta"
        output_file = temp_dir / "output.aln"

        _write_fasta(records, input_file)

        clustalo_path = _find_clustalo_executable()
        if not clustalo_path:
            raise RuntimeError("Clustal Omega 不可用")
        result = subprocess.run(
            [clustalo_path, "-i", str(input_file), "-o", str(output_file),
             "--outfmt=clustal", "--full", "-v"],
            capture_output=True,
            text=True,
            timeout=300,
        )

        if result.returncode != 0:
            raise RuntimeError(f"Clustal Omega 运行失败: {result.stderr}")

        aligned_records, align_text = _parse_clustal_output(output_file, records)

        # 使用比对后的序列计算 identity 矩阵（确保准确性和一致性）
        identity_matrix = calculate_identity_matrix(aligned_records)

        matrix_text = format_identity_matrix_uniprot(records, identity_matrix)
        align_text = align_text + "\n\n" + matrix_text

        return aligned_records, align_text, identity_matrix

    finally:
        shutil.rmtree(temp_dir)


def _parse_distance_matrix(
    distmat_file: Path,
    original_records: List[FastaRecord],
) -> List[List[float]]:
    """解析 Clustal Omega 生成的 distance matrix 文件"""
    matrix = []
    current_line = 0
    
    with open(distmat_file, "r", encoding="utf-8") as f:
        lines = f.readlines()
    
    if len(lines) < 2:
        return matrix
    
    n = int(lines[0].strip())
    
    for i in range(n):
        if i + 1 >= len(lines):
            break
        parts = lines[i + 1].split()
        if len(parts) < n + 1:
            continue
        row = []
        for j in range(n):
            try:
                val = float(parts[j + 1])
                # Clustal Omega 使用 --distmat-out 时输出的是距离值
                # 需要转换为 identity: identity = 100 - distance
                # 但有时候它也可能直接输出 identity（取决于版本和参数）
                # 这里我们假设输出的是 identity 值（使用 --percent-id 参数时）
                # 如果值超过100，则说明是距离值，需要转换
                if val > 100:
                    val = 100.0 - val
                elif val < 0:
                    val = 0.0
                row.append(val)
            except ValueError:
                row.append(0.0)
        matrix.append(row)
    
    return matrix


def _align_with_needleman_wunsch(
    records: List[FastaRecord],
    seqs: List[str],
    gap_open: float,
    gap_extend: float,
) -> Tuple[List[FastaRecord], str]:
    """使用 Needleman-Wunsch 算法进行全局比对"""
    if not BIOPYTHON_AVAILABLE:
        raise RuntimeError("需要安装 Biopython 才能使用 Needleman-Wunsch 算法")

    aligner = PairwiseAligner()
    aligner.mode = "global"
    aligner.match_score = 0
    aligner.mismatch_score = -1
    aligner.open_gap_score = gap_open
    aligner.extend_gap_score = gap_extend

    consensus = seqs[0]
    for seq in seqs[1:]:
        alignments = aligner.align(consensus, seq)
        consensus = str(alignments[0].aligned[0])

    aligned = [consensus]
    for seq in seqs[1:]:
        alignments = aligner.align(consensus, seq)
        aligned_seq = str(alignments[0].aligned[1])
        aligned.append(aligned_seq)

    result_lines = []
    for i, (rec, aln_seq) in enumerate(zip(records, aligned)):
        header = f">{rec.id}"
        if rec.description:
            header += f" {rec.description}"
        result_lines.append(header)
        for j in range(0, len(aln_seq), 60):
            result_lines.append(aln_seq[j:j+60])

    result_text = "\n".join(result_lines)

    aligned_records = []
    for rec, aln_seq in zip(records, aligned):
        aligned_records.append(FastaRecord(
            id=rec.id,
            description=rec.description,
            seq=aln_seq.replace("-", "")
        ))

    return aligned_records, result_text


def _write_fasta(records: List[FastaRecord], file_path: Path):
    """写入 FASTA 文件"""
    with open(file_path, "w", encoding="utf-8") as f:
        for record in records:
            header = f">{record.id}"
            if record.description:
                header += f" {record.description}"
            f.write(header + "\n")
            f.write(record.seq + "\n")


def _parse_clustal_output(
    aln_file: Path,
    original_records: List[FastaRecord],
) -> Tuple[List[FastaRecord], str]:
    """解析 Clustal 输出格式"""
    aligned_records = []
    seq_map = {}

    with open(aln_file, "r", encoding="utf-8") as f:
        for line in f:
            # 不要使用 strip()，因为会丢失末尾的空格（代表 gaps）
            if not line.strip():
                continue
            if line.startswith("CLUSTAL") or line.startswith("STOCKHOLM"):
                continue
            # 检查是否是序列行（包含空格且不是比对行）
            if " " in line and not line.startswith(" ") and not line.startswith("*") and not line.startswith(":"):
                # 找到第一个空格的位置，分割序列 ID 和序列部分
                space_pos = line.find(" ")
                if space_pos != -1:
                    seq_id = line[:space_pos].strip()
                    # 从空格位置开始，提取序列部分，直到行尾或数字（行号）
                    seq_part = line[space_pos:].strip()
                    # 移除行号（如果有）
                    if seq_part and seq_part[-1].isdigit():
                        # 找到最后一个空格的位置
                        last_space = seq_part.rfind(" ")
                        if last_space != -1:
                            seq_part = seq_part[:last_space].strip()
                    if seq_id not in seq_map:
                        seq_map[seq_id] = ""
                    seq_map[seq_id] += seq_part

    align_text = aln_file.read_text(encoding="utf-8")

    for record in original_records:
        rec_id = record.id
        aligned_seq = seq_map.get(rec_id, record.seq)
        aligned_records.append(FastaRecord(
            id=record.id,
            description=record.description,
            seq=aligned_seq  # 保存包含 gaps 的比对序列
        ))

    return aligned_records, align_text


def calculate_identity_matrix(records: List[FastaRecord]) -> List[List[float]]:
    """
    计算序列间的 identity 矩阵

    Args:
        records: FastaRecord 列表（应该已经比对过）

    Returns:
        二维矩阵，表示序列间的 identity 百分比 (0-100)
    """
    n = len(records)
    matrix = [[0.0] * n for _ in range(n)]

    aligned_seqs = [r.seq.upper() for r in records]
    align_len = min(len(s) for s in aligned_seqs)

    for i in range(n):
        for j in range(i, n):
            if i == j:
                matrix[i][j] = 100.0
            else:
                seq1 = aligned_seqs[i]
                seq2 = aligned_seqs[j]

                matches = 0
                aligned_positions = 0
                
                for a, b in zip(seq1[:align_len], seq2[:align_len]):
                    if a != "-" or b != "-":
                        aligned_positions += 1
                        if a == b:
                            matches += 1

                if aligned_positions > 0:
                    identity = (matches / aligned_positions) * 100.0
                else:
                    identity = 0.0

                matrix[i][j] = matrix[j][i] = identity

    return matrix


def format_identity_matrix_uniprot(
    records: List[FastaRecord],
    matrix: List[List[float]],
    shorter: bool = False,
) -> str:
    """
    格式化为 UniProt 风格的 Identity Matrix

    Args:
        records: FastaRecord 列表
        matrix: identity 矩阵
        shorter: 是否使用更紧凑的格式

    Returns:
        UniProt 格式的字符串
    """
    n = len(records)
    if n == 0:
        return ""

    max_id_len = max(len(r.id) for r in records)

    if shorter:
        lines = ["", "Scoredistances:", ""]
        for i in range(n):
            row_id = records[i].id
            row = f"{row_id:<{max_id_len}}"
            for j in range(n):
                if i == j:
                    row += f"    *  "
                else:
                    val = matrix[i][j]
                    if val < 10:
                        row += f"  {val:.0f}  "
                    elif val < 100:
                        row += f" {val:.0f}  "
                    else:
                        row += f" {val:.0f} "
            lines.append(row)
        return "\n".join(lines)

    lines = [
        "",
        "Sequences (15 rows, 17 columns):",
        "Aligned sequences:",
        "",
    ]

    header = " " * max_id_len + "          "
    for i in range(n):
        seq_id = records[i].id
        if len(seq_id) > 15:
            seq_id = seq_id[:12] + "..."
        header += f"{seq_id:>15}"

    lines.append(header)

    for i in range(n):
        row_id = records[i].id
        if len(row_id) > 15:
            row_id = row_id[:12] + "..."

        row = f"{row_id:<{max_id_len}}"

        for j in range(n):
            val = matrix[i][j]
            row += f" {val:>6.1f}%"

        lines.append(row)

    lines.append("")
    lines.append("Distance Matrix:")
    lines.append("")

    matrix_header = " " * max_id_len + "  "
    for i in range(n):
        matrix_header += f"{i+1:>6}"
    lines.append(matrix_header)

    for i in range(n):
        row = f"{i+1:>{max_id_len}}"
        for j in range(n):
            dist = 100.0 - matrix[i][j]
            row += f" {dist:>6.1f}"
        lines.append(row)

    lines.append("")
    lines.append("Identity Matrix (x100):")
    lines.append("")

    for i in range(n):
        row = f"{i+1:>{max_id_len}}"
        for j in range(n):
            val = matrix[i][j]
            row += f" {val:>6.0f}"
        lines.append(row)

    lines.append("")

    return "\n".join(lines)


def format_msa_html_colored(records: List[FastaRecord], aligned_records: List[FastaRecord]) -> str:
    """生成带颜色标记的多序列比对HTML显示（UniProt风格）

    颜色方案（蓝色系代表一致性）：
    - 完全保守的残基：深蓝色背景 (#1e40af)
    - 高度相似的残基：蓝色背景 (#3b82f6)
    - 中度相似的残基：浅蓝色背景 (#93c5fd)
    - 间隙：浅灰色背景 (#f3f4f6)
    - 非匹配：白色背景
    - 保守性符号：深蓝色

    保守性标记行：
    - * (asterisk): 该列所有残基相同
    - : (colon): 该列所有残基具有强相似性
    - . (period): 该列所有残基具有弱相似性
    """
    if not aligned_records or not records:
        return "<p>No alignment data</p>"

    n = len(records)
    max_id_len = max(len(r.id) for r in records)
    if max_id_len < 15:
        max_id_len = 15

    seq_ids = [r.id for r in records]
    seqs = [r.seq for r in aligned_records]
    align_len = len(seqs[0]) if seqs else 0

    STRONG_SIMILARITY = {
        ('A', 'G'), ('G', 'A'),
        ('S', 'T'), ('T', 'S'),
        ('D', 'E'), ('E', 'D'),
        ('N', 'Q'), ('Q', 'N'),
        ('K', 'R'), ('R', 'K'),
        ('I', 'L'), ('L', 'I'), ('I', 'V'), ('V', 'I'), ('L', 'V'), ('V', 'L'),
        ('F', 'Y'), ('Y', 'F'),
    }

    WEAK_SIMILARITY = {
        ('A', 'S'), ('S', 'A'), ('A', 'T'), ('T', 'A'), ('S', 'N'), ('N', 'S'),
        ('D', 'N'), ('N', 'D'), ('E', 'Q'), ('Q', 'E'), ('D', 'Q'), ('Q', 'D'), ('E', 'N'), ('N', 'E'),
        ('R', 'Q'), ('Q', 'R'), ('K', 'Q'), ('Q', 'K'), ('R', 'E'), ('E', 'R'), ('K', 'E'), ('E', 'K'),
        ('V', 'M'), ('M', 'V'), ('L', 'M'), ('M', 'L'), ('I', 'M'), ('M', 'I'),
        ('F', 'W'), ('W', 'F'), ('Y', 'W'), ('W', 'Y'), ('F', 'H'), ('H', 'F'), ('Y', 'H'), ('H', 'Y'),
        ('A', 'V'), ('V', 'A'), ('G', 'V'), ('V', 'G'), ('G', 'S'), ('S', 'G'),
    }

    def calculate_conservation_symbol(column_residues: list) -> str:
        non_gap_residues = [r for r in column_residues if r != '-']
        if not non_gap_residues:
            return ' '

        unique_residues = set(non_gap_residues)
        if len(unique_residues) == 1:
            return '*'

        all_strong = True
        first_residue = non_gap_residues[0]
        for r in non_gap_residues[1:]:
            if (first_residue, r) not in STRONG_SIMILARITY and first_residue != r:
                all_strong = False
                break

        if all_strong:
            return ':'

        all_weak = True
        for r in non_gap_residues[1:]:
            if (first_residue, r) not in STRONG_SIMILARITY and (first_residue, r) not in WEAK_SIMILARITY and first_residue != r:
                all_weak = False
                break

        if all_weak:
            return '.'

        return ' '

    def get_cell_color(column_residues: list, residue: str) -> str:
        if residue == '-':
            return '#f3f4f6'

        unique_residues = set([r for r in column_residues if r != '-'])
        if len(unique_residues) == 1:
            return '#1e40af'

        first_residue = [r for r in column_residues if r != '-'][0]
        if (first_residue, residue) in STRONG_SIMILARITY or first_residue == residue:
            return '#3b82f6'
        if (first_residue, residue) in WEAK_SIMILARITY:
            return '#93c5fd'

        return '#ffffff'

    def get_text_color(bg_color: str, residue: str) -> str:
        if residue == '-':
            return '#6b7280'
        if bg_color in ['#1e40af', '#3b82f6']:
            return '#ffffff'
        return '#1f2937'

    block_size = 60
    html_parts = []

    css = """
    <style>
        body {
            margin: 0;
            padding: 0;
        }
        .msa-container {
            font-family: 'Consolas', 'Courier New', monospace;
            font-size: 11px;
            line-height: 1.6;
            background: #ffffff;
            padding: 12px;
            width: calc(100% - 24px);
            display: block;
        }
        .msa-block {
            margin-bottom: 8px;
            display: block;
            width: 100%;
        }
        .msa-pos-header {
            display: flex;
            margin-bottom: 2px;
            color: #6b7280;
            font-size: 9px;
            width: 100%;
        }
        .msa-id-spacer {
            display: inline-block;
            width: 120px;
            flex-shrink: 0;
            flex-grow: 0;
        }
        .msa-pos {
            display: inline-block;
            width: 8px;
            text-align: center;
            font-weight: bold;
        }
        .msa-row {
            display: flex;
            width: 100%;
        }
        .msa-id {
            display: inline-block;
            width: 120px;
            flex-shrink: 0;
            flex-grow: 0;
            color: #1e40af;
            font-weight: 600;
            background: #f3f4f6;
            padding-right: 8px;
            text-align: right;
            border-right: 1px solid #d1d5db;
            margin-right: 4px;
            text-overflow: ellipsis;
            white-space: nowrap;
        }
        .msa-seq {
            display: inline-flex;
            letter-spacing: 0.4px;
            flex-shrink: 0;
        }
        .msa-residue {
            display: inline-block;
            width: 11px;
            text-align: center;
            padding: 1px 0;
            border-radius: 2px;
            font-weight: 500;
            flex-shrink: 0;
        }
        .msa-conservation {
            display: flex;
            margin-top: 2px;
            margin-bottom: 4px;
            width: 100%;
        }
        .msa-conservation-line {
            display: inline-flex;
            letter-spacing: 0.4px;
            color: #1e40af;
            font-weight: 700;
            font-size: 10px;
            flex-shrink: 0;
        }
        .msa-conservation-spacer {
            display: inline-block;
            width: 125px;
            flex-shrink: 0;
            flex-grow: 0;
        }
    </style>
    """

    html_parts.append('<div class="msa-container">')

    for start in range(0, align_len, block_size):
        end = min(start + block_size, align_len)

        html_parts.append(f'<div class="msa-block">')

        html_parts.append('<div class="msa-pos-header">')
        html_parts.append('<div class="msa-id-spacer"></div>')
        for pos in range(start, end):
            col_idx = pos - start
            if col_idx % 10 == 0:
                pos_str = str(pos + 1)
                html_parts.append(f'<span class="msa-pos">{pos_str}</span>')
                remaining = 10 - len(pos_str)
                for _ in range(remaining):
                    html_parts.append('<span class="msa-pos">&nbsp;</span>')
            else:
                html_parts.append('<span class="msa-pos">&nbsp;</span>')
        html_parts.append('</div>')

        conservation_line = []
        for col_idx in range(start, end):
            col_residues = [seq[col_idx] for seq in seqs]
            symbol = calculate_conservation_symbol(col_residues)
            conservation_line.append(symbol)

        for i, (seq_id, seq) in enumerate(zip(seq_ids, seqs)):
            truncated_id = seq_id[:11] + "..." if len(seq_id) > 14 else seq_id
            padded_id = truncated_id.ljust(max_id_len)
            html_parts.append(f'<div class="msa-row">')
            html_parts.append(f'<span class="msa-id">{padded_id}</span>')
            html_parts.append('<span class="msa-seq">')
            for col_idx, pos in enumerate(range(start, end)):
                aa = seq[pos]
                col_residues = [seq[pos] for seq in seqs]
                bg_color = get_cell_color(col_residues, aa)
                text_color = get_text_color(bg_color, aa)
                html_parts.append(f'<span class="msa-residue" style="background-color: {bg_color}; color: {text_color};">{aa}</span>')
            html_parts.append('</span>')
            html_parts.append('</div>')

        html_parts.append('<div class="msa-conservation">')
        html_parts.append('<div class="msa-conservation-spacer"></div>')
        html_parts.append('<span class="msa-conservation-line">')
        for symbol in conservation_line:
            html_parts.append(f'<span class="msa-residue">{symbol}</span>')
        html_parts.append('</span>')
        html_parts.append('</div>')

        html_parts.append('</div>')

    html_parts.append('</div>')

    full_html = f"<!DOCTYPE html><html><head><meta charset='utf-8'>{css}</head><body>"
    full_html += "".join(html_parts)
    full_html += "</body></html>"

    return full_html


def format_msa_text(records: List[FastaRecord], aligned_records: List[FastaRecord]) -> str:
    """生成纯文本格式的多序列比对显示（类似 UniProt/Clustal 风格）"""
    if not aligned_records or not records:
        return "No alignment data"

    n = len(records)
    max_id_len = max(len(r.id) for r in records)

    seq_ids = [r.id for r in records]
    seqs = [r.seq for r in aligned_records]
    align_len = len(seqs[0]) if seqs else 0

    block_size = 60
    lines = []

    for start in range(0, align_len, block_size):
        end = min(start + block_size, align_len)
        pos_width = len(str(end))

        lines.append("")

        pos_line = " " * max_id_len + "  "
        for pos in range(start, end):
            col_idx = pos - start
            if col_idx % 10 == 0:
                val = pos + 1
                spaces = pos_width - len(str(val))
                pos_line += ' ' * spaces + str(val)
            else:
                pos_line += ' ' * pos_width
        lines.append(pos_line.strip())

        for i, (seq_id, seq) in enumerate(zip(seq_ids, seqs)):
            padded_id = seq_id.ljust(max_id_len)
            lines.append(f"{padded_id}  {seq[start:end]}")

        if end < align_len:
            lines.append("...")

    return "\n".join(lines)


def _format_msa_html(records: List[FastaRecord], aligned_records: List[FastaRecord]) -> str:
    """生成 UniProt 风格的多序列比对显示"""
    if not aligned_records or not records:
        return "<p>No alignment data</p>"

    n = len(records)
    max_id_len = max(len(r.id) for r in records)

    seq_ids = [r.id for r in records]
    seqs = [r.seq for r in aligned_records]
    align_len = len(seqs[0]) if seqs else 0

    block_size = 60
    html = '<div class="msa-container">'

    for start in range(0, align_len, block_size):
        end = min(start + block_size, align_len)
        pos_width = len(str(end))

        html += f'<div class="msa-block">'

        html += f'<div class="msa-pos-header">'
        html += f'<div class="msa-id-spacer"></div>'
        for pos in range(start, end):
            col_idx = pos - start
            if col_idx % 10 == 0:
                val = pos + 1
                spaces = pos_width - len(str(val))
                html += f'<span class="msa-pos">' + ' ' * spaces + str(val) + '</span>'
            else:
                html += '<span class="msa-pos">' + ' ' * pos_width + '</span>'
        html += '</div>'

        for i, (seq_id, seq) in enumerate(zip(seq_ids, seqs)):
            padded_id = seq_id.ljust(max_id_len)
            html += f'<div class="msa-row">'
            html += f'<span class="msa-id">{padded_id}</span>'
            html += f'<span class="msa-seq">{seq[start:end]}</span>'
            html += '</div>'

        html += '</div>'

    html += '</div>'
    return html


def generate_html_report(
    records: List[FastaRecord],
    aligned_records: List[FastaRecord],
    matrix: List[List[float]],
    title: str = "Sequence Alignment Report",
) -> str:
    """
    生成 UniProt 风格的 HTML 报告

    Args:
        records: 原始 FastaRecord 列表
        aligned_records: 比对后的 FastaRecord 列表
        matrix: identity 矩阵
        title: 报告标题

    Returns:
        HTML 格式的字符串
    """
    n = len(records)
    if n == 0:
        return "<html><body>No sequences to display</body></html>"

    align_len = len(aligned_records[0].seq) if aligned_records else 0

    def get_identity_class(val):
        """根据 identity 值返回 UniProt 风格的 CSS 类名"""
        if val >= 90:
            return "cell-red"
        elif val >= 70:
            return "cell-orange"
        elif val >= 50:
            return "cell-yellow"
        elif val >= 30:
            return "cell-lightyellow"
        elif val >= 15:
            return "cell-lightgreen"
        else:
            return "cell-green"

    avg_identity = sum(matrix[i][j] for i in range(n) for j in range(i+1, n)) / (n * (n - 1) / 2) if n > 1 else 0

    summary_html = f'''
    <div class="summary-section">
        <div class="summary-grid">
            <div class="summary-item">
                <span class="summary-label">Number of sequences</span>
                <span class="summary-value">{n}</span>
            </div>
            <div class="summary-item">
                <span class="summary-label">Alignment length</span>
                <span class="summary-value">{align_len}</span>
            </div>
            <div class="summary-item">
                <span class="summary-label">Average identity</span>
                <span class="summary-value">{avg_identity:.1f}%</span>
            </div>
        </div>
    </div>
    '''

    msa_html = format_msa_html_colored(records, aligned_records)

    matrix_rows_html = ""
    for i in range(n):
        row_id = records[i].id[:20] + "..." if len(records[i].id) > 23 else records[i].id
        matrix_rows_html += f'<tr><td class="row-header">{row_id}</td>'
        for j in range(n):
            val = matrix[i][j]
            css_class = get_identity_class(val)
            if i == j:
                matrix_rows_html += f'<td class="diag">-</td>'
            else:
                matrix_rows_html += f'<td class="{css_class}">{val:.1f}%</td>'
        matrix_rows_html += '</tr>'

    col_headers_html = ""
    for i in range(n):
        col_id = records[i].id[:15] + "..." if len(records[i].id) > 18 else records[i].id
        col_headers_html += f'<th title="{records[i].id}">{col_id}</th>'

    dist_rows_html = ""
    for i in range(n):
        dist_rows_html += f'<tr><td class="row-header">{i+1}</td>'
        for j in range(n):
            dist = 100.0 - matrix[i][j]
            if i == j:
                dist_rows_html += f'<td class="diag">-</td>'
            else:
                dist_rows_html += f'<td>{dist:.1f}</td>'
        dist_rows_html += '</tr>'

    sorted_pairs = []
    for i in range(n):
        for j in range(i+1, n):
            sorted_pairs.append((matrix[i][j], records[i].id, records[j].id))
    sorted_pairs.sort(key=lambda x: x[0], reverse=True)

    guide_tree = _generate_guide_tree(records, matrix)

    html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif;
            background: #f5f5f5;
            padding: 20px;
            line-height: 1.4;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border: 1px solid #ddd;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.08);
            overflow: hidden;
        }}
        .header {{
            background: linear-gradient(135deg, #336699 0%, #244a73 100%);
            color: white;
            padding: 16px 24px;
            border-bottom: 4px solid #f5c814;
        }}
        .header h1 {{
            font-size: 18px;
            font-weight: 600;
        }}
        .header-subtitle {{
            font-size: 12px;
            opacity: 0.9;
            margin-top: 4px;
        }}
        .tabs {{
            background: #f8f8f8;
            border-bottom: 1px solid #e0e0e0;
            display: flex;
        }}
        .tab {{
            padding: 10px 20px;
            cursor: pointer;
            font-size: 13px;
            color: #666;
            font-weight: 500;
            transition: all 0.2s;
        }}
        .tab:hover {{ 
            background: #e8e8e8;
            color: #333;
        }}
        .tab.active {{
            background: white;
            color: #336699;
            font-weight: 600;
            border-bottom: 3px solid #336699;
            margin-bottom: -1px;
        }}
        .tab-content {{
            display: none;
            padding: 20px;
        }}
        .tab-content.active {{ 
            display: block; 
            animation: fadeIn 0.3s ease;
        }}
        @keyframes fadeIn {{
            from {{ opacity: 0; }}
            to {{ opacity: 1; }}
        }}
        .section {{
            margin-bottom: 24px;
        }}
        .section-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 12px;
        }}
        .section h2 {{
            font-size: 15px;
            color: #2c3e50;
            font-weight: 600;
            padding-bottom: 6px;
            border-bottom: 2px solid #e0e0e0;
        }}
        .summary-section {{
            background: #fafafa;
            border-radius: 6px;
            padding: 12px 16px;
            margin-bottom: 20px;
        }}
        .summary-grid {{
            display: flex;
            gap: 30px;
        }}
        .summary-item {{
            display: flex;
            flex-direction: column;
        }}
        .summary-label {{
            font-size: 11px;
            color: #888;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        .summary-value {{
            font-size: 18px;
            font-weight: 700;
            color: #336699;
        }}
        .matrix-table {{
            border-collapse: collapse;
            font-size: 11px;
            margin: 12px 0;
            width: 100%;
            max-width: 600px;
        }}
        .matrix-table th, .matrix-table td {{
            border: 1px solid #e0e0e0;
            padding: 6px 8px;
            text-align: center;
            white-space: nowrap;
        }}
        .matrix-table th {{
            background: #f5f5f5;
            font-weight: 600;
            color: #444;
            font-size: 11px;
        }}
        .matrix-table .row-header {{
            background: #f0f4f8;
            font-weight: 600;
            text-align: left;
            color: #336699;
            min-width: 80px;
        }}
        .matrix-table .diag {{
            background: #e8e8e8;
            color: #999;
            font-weight: 500;
        }}
        .matrix-table .cell-red {{
            background: #c23b22;
            color: white;
            font-weight: 600;
        }}
        .matrix-table .cell-orange {{
            background: #e87d0d;
            color: white;
            font-weight: 600;
        }}
        .matrix-table .cell-yellow {{
            background: #f7b801;
            color: #333;
            font-weight: 600;
        }}
        .matrix-table .cell-lightyellow {{
            background: #fde047;
            color: #333;
            font-weight: 500;
        }}
        .matrix-table .cell-lightgreen {{
            background: #86efac;
            color: #333;
            font-weight: 500;
        }}
        .matrix-table .cell-green {{
            background: #16a34a;
            color: white;
            font-weight: 500;
        }}
        .msa-wrapper {{
            background: #fff;
            border: 1px solid #e0e0e0;
            border-radius: 6px;
            margin-top: 8px;
        }}
        .msa-container {{
            font-family: 'SF Mono', 'Consolas', 'Courier New', monospace;
            font-size: 11px;
            line-height: 1.6;
            background: #FFFFFF;
            padding: 16px;
        }}
        .msa-block {{
            margin-bottom: 8px;
        }}
        .msa-pos-header {{
            display: flex;
            margin-bottom: 2px;
            color: #888888;
            font-size: 8px;
        }}
        .msa-id-spacer {{
            display: inline-block;
            width: 120px;
            flex-shrink: 0;
        }}
        .msa-pos {{
            display: inline-block;
            width: 8px;
            text-align: center;
            font-weight: bold;
        }}
        .msa-row {{
            display: flex;
        }}
        .msa-id {{
            display: inline-block;
            width: 120px;
            flex-shrink: 0;
            color: #1a4b8c;
            font-weight: 600;
            background: #F5F8FC;
            padding-right: 8px;
            text-align: right;
            border-right: 1px solid #D0D7DE;
            margin-right: 4px;
            white-space: nowrap;
        }}
        .msa-seq {{
            display: inline-block;
            letter-spacing: 0.4px;
        }}
        .msa-residue {{
            display: inline-block;
            width: 11px;
            text-align: center;
            padding: 1px 0;
            border-radius: 2px;
        }}
        .msa-conservation {{
            display: flex;
            margin-top: 2px;
            margin-bottom: 4px;
        }}
        .msa-conservation-line {{
            display: inline-block;
            letter-spacing: 0.4px;
            color: #c23b22;
            font-weight: 700;
            font-size: 10px;
        }}
        .msa-conservation-spacer {{
            display: inline-block;
            width: 125px;
            flex-shrink: 0;
        }}
        .tree-view {{
            background: #f8fafc;
            border: 1px solid #e2e8f0;
            border-radius: 6px;
            padding: 16px;
            font-family: 'SF Mono', 'Courier New', monospace;
            font-size: 12px;
            line-height: 1.6;
            white-space: pre;
            overflow-x: auto;
        }}
        .legend {{
            display: flex;
            gap: 15px;
            font-size: 11px;
            margin: 12px 0;
            flex-wrap: wrap;
            padding: 10px;
            background: #fafafa;
            border-radius: 4px;
        }}
        .legend-item {{
            display: flex;
            align-items: center;
            gap: 5px;
        }}
        .legend-box {{
            width: 18px;
            height: 14px;
            border-radius: 2px;
            border: 1px solid #ddd;
        }}
        .legend-label {{
            color: #555;
        }}
        .footer {{
            background: #f8f8f8;
            border-top: 1px solid #e0e0e0;
            padding: 12px 24px;
            font-size: 11px;
            color: #666;
            text-align: center;
        }}
        .footer a {{
            color: #336699;
            text-decoration: none;
        }}
        .footer a:hover {{
            text-decoration: underline;
        }}
        .conservation-info {{
            display: flex;
            gap: 20px;
            font-size: 11px;
            color: #666;
            margin-top: 8px;
            padding-left: 4px;
        }}
        .conservation-symbol {{
            font-family: 'Courier New', monospace;
            font-weight: bold;
            margin-right: 4px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>{title}</h1>
            <div class="header-subtitle">Multiple Sequence Alignment (MSA) Analysis</div>
        </div>

        <div class="tabs">
            <div class="tab active" onclick="showTab('overview')">Alignment</div>
            <div class="tab" onclick="showTab('matrix')">Identity Matrix</div>
            <div class="tab" onclick="showTab('tree')">Guide Tree</div>
        </div>

        <div id="overview" class="tab-content active">
            {summary_html}
            
            <div class="section">
                <div class="section-header">
                    <h2>Aligned Sequences</h2>
                </div>
                <div class="msa-wrapper">
                    {msa_html}
                </div>
                <div class="conservation-info">
                    <span><span class="conservation-symbol" style="color: #c23b22;">*</span> Identical residues</span>
                    <span><span class="conservation-symbol" style="color: #c23b22;">:</span> Strongly similar</span>
                    <span><span class="conservation-symbol" style="color: #c23b22;">.</span> Weakly similar</span>
                </div>
            </div>
        </div>

        <div id="matrix" class="tab-content">
            <div class="section">
                <h2>Percent Identity Matrix</h2>
                <div class="legend">
                    <div class="legend-item"><div class="legend-box cell-red"></div><span class="legend-label">90-100%</span></div>
                    <div class="legend-item"><div class="legend-box cell-orange"></div><span class="legend-label">70-89%</span></div>
                    <div class="legend-item"><div class="legend-box cell-yellow"></div><span class="legend-label">50-69%</span></div>
                    <div class="legend-item"><div class="legend-box cell-lightyellow"></div><span class="legend-label">30-49%</span></div>
                    <div class="legend-item"><div class="legend-box cell-lightgreen"></div><span class="legend-label">15-29%</span></div>
                    <div class="legend-item"><div class="legend-box cell-green"></div><span class="legend-label">0-14%</span></div>
                </div>
                <table class="matrix-table">
                    <tr><th></th>{col_headers_html}</tr>
                    {matrix_rows_html}
                </table>
            </div>

            <div class="section">
                <h2>Distance Matrix</h2>
                <p class="legend-label" style="margin-bottom: 8px; font-size: 11px;">Distance = 100% - Identity</p>
                <table class="matrix-table">
                    <tr><th></th>{''.join(f'<th>{i+1}</th>' for i in range(n))}</tr>
                    {dist_rows_html}
                </table>
            </div>
        </div>

        <div id="tree" class="tab-content">
            <div class="section">
                <h2>Guide Tree</h2>
                <div class="tree-view">{guide_tree}</div>
            </div>
        </div>

        <div class="footer">
            Generated by <strong>Seq_Box</strong> | Powered by <strong>Clustal Omega</strong>
        </div>
    </div>

    <script>
        function showTab(tabName) {{
            document.querySelectorAll('.tab-content').forEach(el => el.classList.remove('active'));
            document.querySelectorAll('.tab').forEach(el => el.classList.remove('active'));
            document.getElementById(tabName).classList.add('active');
            event.target.classList.add('active');
        }}
    </script>
</body>
</html>'''

    return html


def _generate_guide_tree(records: List[FastaRecord], matrix: List[List[float]]) -> str:
    """生成简化的 guide tree 表示"""
    n = len(records)
    if n == 0:
        return "No sequences"

    if n == 1:
        return records[0].id

    if n == 2:
        return f"({records[0].id}, {records[1].id})"

    sorted_pairs = []
    for i in range(n):
        for j in range(i+1, n):
            sorted_pairs.append((matrix[i][j], i, j, records[i].id, records[j].id))
    sorted_pairs.sort(key=lambda x: x[0], reverse=True)

    tree_lines = ["Guide Tree (based on identity):", ""]

    if n <= 4:
        tree_lines.append("    " + records[0].id)
        tree_lines.append("    |")
        tree_lines.append("    +--" + records[1].id)
        for k in range(2, n):
            tree_lines.append("    |")
            tree_lines.append("    +--" + records[k].id)
    else:
        tree_lines.append(f"  {'/' * 40}")
        tree_lines.append(f" /{'':^38}\\")
        tree_lines.append(f"({records[0].id[:15]:^15}   {records[1].id[:15]:^15})")
        tree_lines.append(f" \\{'':^38}/")
        tree_lines.append(f"  {'/' * 40}")
        tree_lines.append(f"         |")
        tree_lines.append(f"      Other sequences...")

    tree_lines.append("")
    tree_lines.append("Top 3 most similar pairs:")
    for idx, (identity, i, j, id1, id2) in enumerate(sorted_pairs[:3]):
        tree_lines.append(f"  {idx+1}. {id1} - {id2}: {identity:.1f}% identity")

    return "\n".join(tree_lines)


def get_msa_table_data(
    records: List[FastaRecord],
    aligned_records: List[FastaRecord],
    block_size: int = 50,
) -> list:
    """
    生成 MSA 表格数据，用于 QTableWidget 显示
    
    返回: list of blocks, 每个 block 包含:
      - start: 起始位置
      - end: 结束位置
      - rows: 每行数据 (seq_id, residues)
      - conservation: 保守性符号行
    
    每个 residue 是 dict: {"residue": str, "bg_color": str, "text_color": str}
    """
    if not aligned_records or not records:
        return []

    seq_ids = [r.id for r in records]
    seqs = [r.seq for r in aligned_records]
    align_len = len(seqs[0]) if seqs else 0
    
    STRONG_SIMILARITY = {
        ('A', 'G'), ('G', 'A'),
        ('S', 'T'), ('T', 'S'),
        ('D', 'E'), ('E', 'D'),
        ('N', 'Q'), ('Q', 'N'),
        ('K', 'R'), ('R', 'K'),
        ('I', 'L'), ('L', 'I'), ('I', 'V'), ('V', 'I'), ('L', 'V'), ('V', 'L'),
        ('F', 'Y'), ('Y', 'F'),
    }
    
    WEAK_SIMILARITY = {
        ('A', 'S'), ('S', 'A'), ('A', 'T'), ('T', 'A'), ('S', 'N'), ('N', 'S'),
        ('D', 'N'), ('N', 'D'), ('E', 'Q'), ('Q', 'E'), ('D', 'Q'), ('Q', 'D'), ('E', 'N'), ('N', 'E'),
        ('R', 'Q'), ('Q', 'R'), ('K', 'Q'), ('Q', 'K'), ('R', 'E'), ('E', 'R'), ('K', 'E'), ('E', 'K'),
        ('V', 'M'), ('M', 'V'), ('L', 'M'), ('M', 'L'), ('I', 'M'), ('M', 'I'),
        ('F', 'W'), ('W', 'F'), ('Y', 'W'), ('W', 'Y'), ('F', 'H'), ('H', 'F'), ('Y', 'H'), ('H', 'Y'),
        ('A', 'V'), ('V', 'A'), ('G', 'V'), ('V', 'G'), ('G', 'S'), ('S', 'G'),
    }

    def get_cell_color(column_residues, residue):
        if residue == '-':
            return '#f3f4f6'
        non_gap = [r for r in column_residues if r != '-']
        if not non_gap:
            return '#ffffff'
        if len(set(non_gap)) == 1:
            return '#1e3a8a'
        first = non_gap[0]
        if (first, residue) in STRONG_SIMILARITY or first == residue:
            return '#3b82f6'
        if (first, residue) in WEAK_SIMILARITY:
            return '#93c5fd'
        return '#ffffff'

    def get_text_color(bg_color, residue):
        if residue == '-':
            return '#6b7280'
        if bg_color in ['#1e3a8a', '#3b82f6']:
            return '#ffffff'
        return '#1f2937'

    def calc_conservation_symbol(col_residues):
        non_gap = [r for r in col_residues if r != '-']
        if not non_gap:
            return ' '
        if len(set(non_gap)) == 1:
            return '*'
        if len(non_gap) < 2:
            return ' '
        first = non_gap[0]
        all_match = True
        for r in non_gap[1:]:
            if (first, r) not in STRONG_SIMILARITY and first != r:
                all_match = False
                break
        if all_match:
            return ':'
        all_weak = True
        for r in non_gap[1:]:
            if (first, r) not in STRONG_SIMILARITY and (first, r) not in WEAK_SIMILARITY and first != r:
                all_weak = False
                break
        if all_weak:
            return '.'
        return ' '

    blocks = []
    for start in range(0, align_len, block_size):
        end = min(start + block_size, align_len)
        block_rows = []
        
        for i, (seq_id, seq) in enumerate(zip(seq_ids, seqs)):
            residues = []
            for pos in range(start, end):
                aa = seq[pos]
                col_residues = [s[pos] for s in seqs]
                bg_color = get_cell_color(col_residues, aa)
                text_color = get_text_color(bg_color, aa)
                residues.append({
                    "residue": aa,
                    "bg_color": bg_color,
                    "text_color": text_color,
                })
            block_rows.append({"seq_id": seq_id, "residues": residues})
        
        conservation = []
        for pos in range(start, end):
            col_residues = [s[pos] for s in seqs]
            conservation.append(calc_conservation_symbol(col_residues))
        
        blocks.append({
            "start": start,
            "end": end,
            "rows": block_rows,
            "conservation": conservation,
        })
    
    return blocks
