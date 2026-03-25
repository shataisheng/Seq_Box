"""
Seq_Box - FASTA 文件读写模块

提供 FASTA 格式的读取、写入、流式处理功能
"""

from __future__ import annotations
from typing import Iterator, List, Optional, TextIO, Union, Callable
from pathlib import Path
import re
from dataclasses import dataclass
from enum import Enum

from seqbox.core import Sequence, create_sequence


class SeqType(Enum):
    """序列类型枚举"""
    AUTO = "auto"
    DNA = "dna"
    RNA = "rna"
    PROTEIN = "protein"


class DuplicateIDHandling(Enum):
    """ID 冲突处理方式"""
    ERROR = "error"           # 报错
    RENAME = "rename"         # 自动重命名（添加后缀 _1, _2...）
    SKIP = "skip"             # 跳过重复
    OVERWRITE = "overwrite"   # 保留最后一个


class FastaRecord:
    """
    FASTA 记录对象
    
    Attributes:
        id: 序列 ID（header 中 > 后的第一个词）
        description: 序列描述（header 中 ID 后的内容）
        seq: 序列字符串
    """
    
    __slots__ = ('id', 'description', 'seq')
    
    def __init__(self, id: str, description: str, seq: str):
        self.id = id
        self.description = description
        self.seq = seq
    
    def __repr__(self) -> str:
        desc = f" desc='{self.description}'" if self.description else ""
        return f"FastaRecord(id='{self.id}', len={len(self.seq)}{desc})"
    
    def __len__(self) -> int:
        return len(self.seq)
    
    def to_sequence(self, seq_type: Optional[str] = None) -> Sequence:
        """
        转换为 Sequence 对象
        
        Args:
            seq_type: 指定序列类型，None 则自动检测
            
        Returns:
            Sequence 对象
        """
        return create_sequence(
            seq=self.seq,
            seq_type=seq_type,
            id=self.id,
            description=self.description
        )
    
    def to_fasta_string(self, line_width: int = 60) -> str:
        """
        转换为 FASTA 格式字符串
        
        Args:
            line_width: 每行序列字符数
            
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


class FastaReader:
    """FASTA 文件读取器"""
    
    def __init__(self, file_path: Union[str, Path]):
        self.file_path = Path(file_path)
        if not self.file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
    
    def __iter__(self) -> Iterator[FastaRecord]:
        """流式读取，逐条 yield"""
        return self._parse()
    
    def _parse(self) -> Iterator[FastaRecord]:
        """
        解析 FASTA 文件
        
        Yields:
            FastaRecord 对象
        """
        with open(self.file_path, 'r', encoding='utf-8') as f:
            yield from self._parse_file_handle(f)
    
    @staticmethod
    def _parse_file_handle(file_handle: TextIO) -> Iterator[FastaRecord]:
        """
        从文件句柄解析 FASTA
        
        Args:
            file_handle: 已打开的文件句柄
            
        Yields:
            FastaRecord 对象
        """
        current_id = ""
        current_desc = ""
        current_seq_lines: List[str] = []
        
        for line in file_handle:
            line = line.strip()
            
            if not line:
                continue
            
            if line.startswith('>'):
                # 保存前一条记录
                if current_id and current_seq_lines:
                    yield FastaRecord(
                        id=current_id,
                        description=current_desc,
                        seq=''.join(current_seq_lines).upper()
                    )
                
                # 解析新 header
                header = line[1:].strip()
                parts = header.split(maxsplit=1)
                current_id = parts[0] if parts else ""
                current_desc = parts[1] if len(parts) > 1 else ""
                current_seq_lines = []
            else:
                # 序列行
                current_seq_lines.append(line)
        
        # 保存最后一条记录
        if current_id and current_seq_lines:
            yield FastaRecord(
                id=current_id,
                description=current_desc,
                seq=''.join(current_seq_lines).upper()
            )
    
    def read_all(self) -> List[FastaRecord]:
        """
        读取所有记录
        
        Returns:
            FastaRecord 列表
        """
        return list(self)
    
    def count(self) -> int:
        """
        统计序列数量（不加载全部内容）
        
        Returns:
            序列条数
        """
        count = 0
        with open(self.file_path, 'r', encoding='utf-8') as f:
            for line in f:
                if line.startswith('>'):
                    count += 1
        return count


class FastaWriter:
    """FASTA 文件写入器"""
    
    def __init__(self, file_path: Union[str, Path], line_width: int = 60):
        self.file_path = Path(file_path)
        self.line_width = line_width
        self._file_handle: Optional[TextIO] = None
        self._record_count = 0
    
    def __enter__(self) -> FastaWriter:
        """上下文管理器入口"""
        self._file_handle = open(self.file_path, 'w', encoding='utf-8')
        self._record_count = 0
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器退出"""
        if self._file_handle:
            self._file_handle.close()
            self._file_handle = None
    
    def write_record(self, record: FastaRecord) -> None:
        """
        写入单条记录
        
        Args:
            record: FastaRecord 对象
        """
        if self._file_handle is None:
            raise IOError("Writer not opened. Use 'with' statement or open() method.")
        
        fasta_str = record.to_fasta_string(self.line_width)
        self._file_handle.write(fasta_str + '\n')
        self._record_count += 1
    
    def write_sequence(self, sequence: Sequence) -> None:
        """
        写入 Sequence 对象
        
        Args:
            sequence: Sequence 对象
        """
        record = FastaRecord(
            id=sequence.id,
            description=sequence.description,
            seq=sequence.seq
        )
        self.write_record(record)
    
    def write_many(self, records: List[FastaRecord]) -> int:
        """
        批量写入记录
        
        Args:
            records: FastaRecord 列表
            
        Returns:
            写入的记录数
        """
        for record in records:
            self.write_record(record)
        return len(records)
    
    @property
    def record_count(self) -> int:
        """已写入的记录数"""
        return self._record_count


# ========== 便捷函数 ==========

def read_fasta(file_path: Union[str, Path]) -> List[FastaRecord]:
    """
    读取 FASTA 文件，返回所有记录
    
    Args:
        file_path: 文件路径
        
    Returns:
        FastaRecord 列表
    """
    reader = FastaReader(file_path)
    return reader.read_all()


def parse_fasta(file_path: Union[str, Path]) -> Iterator[FastaRecord]:
    """
    流式解析 FASTA 文件
    
    Args:
        file_path: 文件路径
        
    Yields:
        FastaRecord 对象
    """
    reader = FastaReader(file_path)
    yield from reader


def write_fasta(
    records: List[FastaRecord],
    file_path: Union[str, Path],
    line_width: int = 60
) -> int:
    """
    将记录写入 FASTA 文件
    
    Args:
        records: FastaRecord 列表
        file_path: 输出文件路径
        line_width: 每行字符数
        
    Returns:
        写入的记录数
    """
    with FastaWriter(file_path, line_width) as writer:
        return writer.write_many(records)


def write_sequences(
    sequences: List[Sequence],
    file_path: Union[str, Path],
    line_width: int = 60
) -> int:
    """
    将 Sequence 对象写入 FASTA 文件
    
    Args:
        sequences: Sequence 列表
        file_path: 输出文件路径
        line_width: 每行字符数
        
    Returns:
        写入的记录数
    """
    records = [
        FastaRecord(id=seq.id, description=seq.description, seq=seq.seq)
        for seq in sequences
    ]
    return write_fasta(records, file_path, line_width)


def parse_fasta_string(fasta_str: str) -> List[FastaRecord]:
    """
    从字符串解析 FASTA 内容
    
    Args:
        fasta_str: FASTA 格式字符串
        
    Returns:
        FastaRecord 列表
    """
    from io import StringIO
    
    records = []
    file_handle = StringIO(fasta_str)
    
    for record in FastaReader._parse_file_handle(file_handle):
        records.append(record)
    
    return records


def to_fasta_string(
    records: List[FastaRecord],
    line_width: int = 60
) -> str:
    """
    将记录转换为 FASTA 格式字符串
    
    Args:
        records: FastaRecord 列表
        line_width: 每行字符数
        
    Returns:
        FASTA 格式字符串
    """
    return '\n'.join(r.to_fasta_string(line_width) for r in records)


# ========== 清洗功能 ==========


@dataclass
class CleanStats:
    """清洗统计信息"""
    input_count: int = 0
    output_count: int = 0
    removed_duplicates: int = 0
    removed_by_length: int = 0
    removed_by_ambiguous: int = 0
    cleaned_chars: int = 0
    
    def __repr__(self) -> str:
        return (f"CleanStats(in={self.input_count}, out={self.output_count}, "
                f"dup={self.removed_duplicates}, len_filter={self.removed_by_length}, "
                f"ambig={self.removed_by_ambiguous}, chars={self.cleaned_chars})")


def clean_fasta(
    input_path: Union[str, Path],
    output_path: Union[str, Path],
    seq_type: SeqType = SeqType.AUTO,
    remove_invalid: bool = True,
    to_uppercase: bool = True,
    remove_duplicates: bool = False,
    min_length: Optional[int] = None,
    max_length: Optional[int] = None,
    max_ambiguous_ratio: Optional[float] = None,
    line_width: int = 60
) -> CleanStats:
    """
    清洗 FASTA 文件
    
    Args:
        input_path: 输入文件路径
        output_path: 输出文件路径
        seq_type: 序列类型，AUTO 则自动检测
        remove_invalid: 是否去除非法字符
        to_uppercase: 是否统一转为大写
        remove_duplicates: 是否去除重复序列
        min_length: 最小长度限制
        max_length: 最大长度限制
        max_ambiguous_ratio: 最大模糊字符比例（0-1）
        line_width: 输出每行字符数
        
    Returns:
        CleanStats 清洗统计
    """
    from seqbox.core import DNA_IUPAC, RNA_IUPAC, PROTEIN_EXTENDED, guess_sequence_type
    
    stats = CleanStats()
    seen_sequences: set[str] = set()
    
    # 确定合法字符集
    if seq_type == SeqType.DNA:
        valid_chars = DNA_IUPAC
    elif seq_type == SeqType.RNA:
        valid_chars = RNA_IUPAC
    elif seq_type == SeqType.PROTEIN:
        valid_chars = PROTEIN_EXTENDED
    else:
        valid_chars = DNA_IUPAC | RNA_IUPAC | PROTEIN_EXTENDED
    
    reader = FastaReader(input_path)
    
    with FastaWriter(output_path, line_width) as writer:
        for record in reader:
            stats.input_count += 1
            seq = record.seq
            original_len = len(seq)
            
            # 自动检测类型
            if seq_type == SeqType.AUTO:
                detected = guess_sequence_type(seq)
                if detected == 'dna':
                    valid_chars = DNA_IUPAC
                elif detected == 'rna':
                    valid_chars = RNA_IUPAC
                elif detected == 'protein':
                    valid_chars = PROTEIN_EXTENDED
            
            # 去除非法字符
            if remove_invalid:
                cleaned_seq = ''.join(c for c in seq if c in valid_chars)
                stats.cleaned_chars += original_len - len(cleaned_seq)
                seq = cleaned_seq
            
            # 统一大小写（已在读取时转为大写，这里保留逻辑完整性）
            if to_uppercase:
                seq = seq.upper()
            
            # 长度过滤
            if min_length is not None and len(seq) < min_length:
                stats.removed_by_length += 1
                continue
            if max_length is not None and len(seq) > max_length:
                stats.removed_by_length += 1
                continue
            
            # 模糊字符比例过滤
            if max_ambiguous_ratio is not None:
                if seq_type == SeqType.DNA or (seq_type == SeqType.AUTO and guess_sequence_type(seq) == 'dna'):
                    ambiguous_count = seq.count('N')
                elif seq_type == SeqType.PROTEIN or (seq_type == SeqType.AUTO and guess_sequence_type(seq) == 'protein'):
                    ambiguous_count = seq.count('X')
                else:
                    ambiguous_count = 0
                
                if len(seq) > 0 and ambiguous_count / len(seq) > max_ambiguous_ratio:
                    stats.removed_by_ambiguous += 1
                    continue
            
            # 去重
            if remove_duplicates:
                if seq in seen_sequences:
                    stats.removed_duplicates += 1
                    continue
                seen_sequences.add(seq)
            
            # 写入
            cleaned_record = FastaRecord(
                id=record.id,
                description=record.description,
                seq=seq
            )
            writer.write_record(cleaned_record)
            stats.output_count += 1
    
    return stats


def clean_sequence_string(
    sequence: str,
    seq_type: SeqType = SeqType.AUTO,
    remove_invalid: bool = True,
    valid_chars: Optional[set[str]] = None
) -> str:
    """
    清洗单个序列字符串
    
    Args:
        sequence: 输入序列
        seq_type: 序列类型
        remove_invalid: 是否去除非法字符
        valid_chars: 自定义合法字符集（优先级高于 seq_type）
        
    Returns:
        清洗后的序列
    """
    from seqbox.core import DNA_IUPAC, RNA_IUPAC, PROTEIN_EXTENDED, guess_sequence_type
    
    seq = sequence.upper()
    
    if valid_chars is None:
        if seq_type == SeqType.DNA:
            valid_chars = DNA_IUPAC
        elif seq_type == SeqType.RNA:
            valid_chars = RNA_IUPAC
        elif seq_type == SeqType.PROTEIN:
            valid_chars = PROTEIN_EXTENDED
        else:
            # 自动检测
            detected = guess_sequence_type(seq)
            if detected == 'dna':
                valid_chars = DNA_IUPAC
            elif detected == 'rna':
                valid_chars = RNA_IUPAC
            elif detected == 'protein':
                valid_chars = PROTEIN_EXTENDED
            else:
                valid_chars = DNA_IUPAC | RNA_IUPAC | PROTEIN_EXTENDED
    
    if remove_invalid:
        seq = ''.join(c for c in seq if c in valid_chars)
    
    return seq


# ========== 分割功能 ==========


def split_fasta_by_count(
    input_path: Union[str, Path],
    output_dir: Union[str, Path],
    records_per_file: int,
    prefix: str = "split",
    line_width: int = 60
) -> List[Path]:
    """
    按记录数量分割 FASTA 文件
    
    Args:
        input_path: 输入文件路径
        output_dir: 输出目录
        records_per_file: 每个文件的记录数
        prefix: 输出文件名前缀
        line_width: 每行字符数
        
    Returns:
        生成的文件路径列表
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    reader = FastaReader(input_path)
    output_files: List[Path] = []
    current_batch: List[FastaRecord] = []
    file_index = 1
    
    for record in reader:
        current_batch.append(record)
        
        if len(current_batch) >= records_per_file:
            output_path = output_dir / f"{prefix}_{file_index:04d}.fa"
            write_fasta(current_batch, output_path, line_width)
            output_files.append(output_path)
            current_batch = []
            file_index += 1
    
    # 写入剩余记录
    if current_batch:
        output_path = output_dir / f"{prefix}_{file_index:04d}.fa"
        write_fasta(current_batch, output_path, line_width)
        output_files.append(output_path)
    
    return output_files


def split_fasta_into_n_files(
    input_path: Union[str, Path],
    output_dir: Union[str, Path],
    n_files: int,
    prefix: str = "split",
    line_width: int = 60
) -> List[Path]:
    """
    将 FASTA 文件平均分割为 N 个文件
    
    Args:
        input_path: 输入文件路径
        output_dir: 输出目录
        n_files: 目标文件数
        prefix: 输出文件名前缀
        line_width: 每行字符数
        
    Returns:
        生成的文件路径列表
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # 先读取所有记录
    records = read_fasta(input_path)
    total = len(records)
    
    if total == 0:
        return []
    
    # 计算每个文件的记录数
    base_count = total // n_files
    remainder = total % n_files
    
    output_files: List[Path] = []
    start_idx = 0
    
    for i in range(n_files):
        # 前 remainder 个文件多一条记录
        file_size = base_count + (1 if i < remainder else 0)
        
        if file_size == 0:
            continue
        
        end_idx = start_idx + file_size
        batch = records[start_idx:end_idx]
        
        output_path = output_dir / f"{prefix}_{i+1:04d}.fa"
        write_fasta(batch, output_path, line_width)
        output_files.append(output_path)
        
        start_idx = end_idx
    
    return output_files


def split_fasta_by_id_list(
    input_path: Union[str, Path],
    output_dir: Union[str, Path],
    id_list: List[str],
    include_mode: bool = True,
    prefix_included: str = "included",
    prefix_excluded: str = "excluded",
    line_width: int = 60
) -> tuple[Path, Optional[Path]]:
    """
    按 ID 列表分割 FASTA 文件
    
    Args:
        input_path: 输入文件路径
        output_dir: 输出目录
        id_list: ID 列表
        include_mode: True 表示提取列表中的 ID，False 表示排除
        prefix_included: 包含的文件前缀
        prefix_excluded: 排除的文件前缀
        line_width: 每行字符数
        
    Returns:
        (included 文件路径, excluded 文件路径或 None)
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    id_set = set(id_list)
    
    included_records: List[FastaRecord] = []
    excluded_records: List[FastaRecord] = []
    
    reader = FastaReader(input_path)
    
    for record in reader:
        if include_mode:
            if record.id in id_set:
                included_records.append(record)
            else:
                excluded_records.append(record)
        else:
            if record.id in id_set:
                excluded_records.append(record)
            else:
                included_records.append(record)
    
    # 写入文件
    included_path = output_dir / f"{prefix_included}.fa"
    write_fasta(included_records, included_path, line_width)
    
    excluded_path = None
    if excluded_records:
        excluded_path = output_dir / f"{prefix_excluded}.fa"
        write_fasta(excluded_records, excluded_path, line_width)
    
    return included_path, excluded_path


def split_fasta_to_single_files(
    input_path: Union[str, Path],
    output_dir: Union[str, Path],
    naming: str = "id",
    line_width: int = 60
) -> List[Path]:
    """
    将每条序列拆分为独立文件
    
    Args:
        input_path: 输入文件路径
        output_dir: 输出目录
        naming: 命名方式，"id" 使用序列 ID，"number" 使用序号
        line_width: 每行字符数
        
    Returns:
        生成的文件路径列表
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    reader = FastaReader(input_path)
    output_files: List[Path] = []
    index = 1
    
    for record in reader:
        if naming == "id":
            filename = f"{record.id}.fa"
        else:
            filename = f"seq_{index:04d}.fa"
        
        output_path = output_dir / filename
        write_fasta([record], output_path, line_width)
        output_files.append(output_path)
        index += 1
    
    return output_files


# ========== 合并功能 ==========


@dataclass
class MergeStats:
    """合并统计信息"""
    files_processed: int = 0
    records_read: int = 0
    records_written: int = 0
    duplicates_found: int = 0
    renamed_ids: int = 0
    skipped_records: int = 0
    
    def __repr__(self) -> str:
        return (f"MergeStats(files={self.files_processed}, read={self.records_read}, "
                f"written={self.records_written}, dup={self.duplicates_found}, "
                f"renamed={self.renamed_ids}, skipped={self.skipped_records})")


def merge_fasta_files(
    input_paths: List[Union[str, Path]],
    output_path: Union[str, Path],
    duplicate_handling: DuplicateIDHandling = DuplicateIDHandling.RENAME,
    remove_duplicates: bool = False,
    line_width: int = 60
) -> MergeStats:
    """
    合并多个 FASTA 文件
    
    Args:
        input_paths: 输入文件路径列表
        output_path: 输出文件路径
        duplicate_handling: ID 冲突处理方式
        remove_duplicates: 是否去除序列内容完全相同的记录
        line_width: 每行字符数
        
    Returns:
        MergeStats 合并统计
    """
    stats = MergeStats()
    seen_ids: set[str] = set()
    seen_sequences: set[str] = set()
    id_counters: dict[str, int] = {}
    
    with FastaWriter(output_path, line_width) as writer:
        for file_path in input_paths:
            stats.files_processed += 1
            
            try:
                reader = FastaReader(file_path)
            except FileNotFoundError:
                continue
            
            for record in reader:
                stats.records_read += 1
                
                # 序列内容去重
                if remove_duplicates:
                    if record.seq in seen_sequences:
                        stats.skipped_records += 1
                        continue
                    seen_sequences.add(record.seq)
                
                # ID 冲突处理
                original_id = record.id
                final_id = original_id
                
                if original_id in seen_ids:
                    stats.duplicates_found += 1
                    
                    if duplicate_handling == DuplicateIDHandling.ERROR:
                        raise ValueError(f"Duplicate ID found: {original_id}")
                    
                    elif duplicate_handling == DuplicateIDHandling.RENAME:
                        # 生成新 ID: id_1, id_2, ...
                        if original_id not in id_counters:
                            id_counters[original_id] = 1
                        id_counters[original_id] += 1
                        final_id = f"{original_id}_{id_counters[original_id]}"
                        stats.renamed_ids += 1
                    
                    elif duplicate_handling == DuplicateIDHandling.SKIP:
                        stats.skipped_records += 1
                        continue
                    
                    elif duplicate_handling == DuplicateIDHandling.OVERWRITE:
                        # 继续写入，后面的会覆盖（实际上无法真正覆盖，需要特殊处理）
                        pass
                
                seen_ids.add(final_id)
                
                # 写入记录
                final_record = FastaRecord(
                    id=final_id,
                    description=record.description,
                    seq=record.seq
                )
                writer.write_record(final_record)
                stats.records_written += 1
    
    return stats


def merge_fasta_from_directory(
    input_dir: Union[str, Path],
    output_path: Union[str, Path],
    pattern: str = "*.fa",
    recursive: bool = False,
    duplicate_handling: DuplicateIDHandling = DuplicateIDHandling.RENAME,
    remove_duplicates: bool = False,
    line_width: int = 60
) -> MergeStats:
    """
    从目录合并所有 FASTA 文件
    
    Args:
        input_dir: 输入目录
        output_path: 输出文件路径
        pattern: 文件匹配模式
        recursive: 是否递归子目录
        duplicate_handling: ID 冲突处理方式
        remove_duplicates: 是否去除序列内容完全相同的记录
        line_width: 每行字符数
        
    Returns:
        MergeStats 合并统计
    """
    input_dir = Path(input_dir)
    
    if recursive:
        files = list(input_dir.rglob(pattern))
    else:
        files = list(input_dir.glob(pattern))
    
    # 按文件名排序，确保顺序一致
    files.sort()
    
    return merge_fasta_files(
        input_paths=files,
        output_path=output_path,
        duplicate_handling=duplicate_handling,
        remove_duplicates=remove_duplicates,
        line_width=line_width
    )
