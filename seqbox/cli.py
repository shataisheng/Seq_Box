"""
Seq_Box - 命令行接口 (CLI)

提供 FASTA 文件的清洗、分割、合并等操作的命令行入口
"""

from __future__ import annotations
import argparse
import sys
from pathlib import Path
from typing import List, Optional

from seqbox.io.fasta import (
    clean_fasta,
    split_fasta_by_count,
    split_fasta_into_n_files,
    split_fasta_by_id_list,
    split_fasta_to_single_files,
    merge_fasta_files,
    merge_fasta_from_directory,
    SeqType,
    DuplicateIDHandling,
)


def create_parser() -> argparse.ArgumentParser:
    """创建命令行参数解析器"""
    parser = argparse.ArgumentParser(
        prog="seqbox",
        description="Seq_Box - DNA/蛋白质序列操作工具箱",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  seqbox fasta clean input.fa output.fa --type dna --remove-invalid
  seqbox fasta split input.fa ./output --by-count 100
  seqbox fasta merge file1.fa file2.fa output.fa
  seqbox fasta merge-dir ./fasta_dir output.fa --recursive
        """
    )
    
    subparsers = parser.add_subparsers(dest="command", help="可用命令")
    
    # fasta 子命令
    fasta_parser = subparsers.add_parser(
        "fasta",
        help="FASTA 文件操作",
        description="FASTA 文件的清洗、分割、合并等操作"
    )
    fasta_subparsers = fasta_parser.add_subparsers(dest="fasta_action", help="FASTA 操作")
    
    # clean 子命令
    clean_parser = fasta_subparsers.add_parser(
        "clean",
        help="清洗 FASTA 文件",
        description="去除非法字符、去重、长度过滤等"
    )
    clean_parser.add_argument("input", help="输入 FASTA 文件路径")
    clean_parser.add_argument("output", help="输出 FASTA 文件路径")
    clean_parser.add_argument(
        "--type", "-t",
        choices=["auto", "dna", "rna", "protein"],
        default="auto",
        help="序列类型 (默认: auto)"
    )
    clean_parser.add_argument(
        "--remove-invalid", "-r",
        action="store_true",
        help="去除非法字符"
    )
    clean_parser.add_argument(
        "--remove-duplicates", "-d",
        action="store_true",
        help="去除重复序列"
    )
    clean_parser.add_argument(
        "--min-length",
        type=int,
        help="最小长度限制"
    )
    clean_parser.add_argument(
        "--max-length",
        type=int,
        help="最大长度限制"
    )
    clean_parser.add_argument(
        "--max-ambiguous",
        type=float,
        help="最大模糊字符比例 (0-1)"
    )
    clean_parser.add_argument(
        "--line-width", "-w",
        type=int,
        default=60,
        help="每行字符数 (默认: 60)"
    )
    
    # split 子命令
    split_parser = fasta_subparsers.add_parser(
        "split",
        help="分割 FASTA 文件",
        description="将 FASTA 文件分割成多个小文件"
    )
    split_parser.add_argument("input", help="输入 FASTA 文件路径")
    split_parser.add_argument("output_dir", help="输出目录")
    split_parser.add_argument(
        "--by-count", "-c",
        type=int,
        help="每个文件的记录数"
    )
    split_parser.add_argument(
        "--into-n", "-n",
        type=int,
        help="平均分割为 N 个文件"
    )
    split_parser.add_argument(
        "--by-id-list",
        help="按 ID 列表分割，参数为包含 ID 的文件路径"
    )
    split_parser.add_argument(
        "--single",
        action="store_true",
        help="每条序列单独一个文件"
    )
    split_parser.add_argument(
        "--exclude",
        action="store_true",
        help="与 --by-id-list 配合，排除列表中的 ID"
    )
    split_parser.add_argument(
        "--naming",
        choices=["id", "number"],
        default="id",
        help="单文件命名方式 (默认: id)"
    )
    split_parser.add_argument(
        "--prefix", "-p",
        default="split",
        help="输出文件名前缀 (默认: split)"
    )
    split_parser.add_argument(
        "--line-width", "-w",
        type=int,
        default=60,
        help="每行字符数 (默认: 60)"
    )
    
    # merge 子命令
    merge_parser = fasta_subparsers.add_parser(
        "merge",
        help="合并 FASTA 文件",
        description="合并多个 FASTA 文件为一个"
    )
    merge_parser.add_argument(
        "inputs",
        nargs="+",
        help="输入 FASTA 文件路径"
    )
    merge_parser.add_argument("output", help="输出 FASTA 文件路径")
    merge_parser.add_argument(
        "--duplicate-handling", "-d",
        choices=["error", "rename", "skip", "overwrite"],
        default="rename",
        help="ID 冲突处理方式 (默认: rename)"
    )
    merge_parser.add_argument(
        "--remove-duplicates", "-r",
        action="store_true",
        help="去除序列内容完全相同的记录"
    )
    merge_parser.add_argument(
        "--line-width", "-w",
        type=int,
        default=60,
        help="每行字符数 (默认: 60)"
    )
    
    # merge-dir 子命令
    merge_dir_parser = fasta_subparsers.add_parser(
        "merge-dir",
        help="合并目录中的 FASTA 文件",
        description="合并目录中所有匹配的 FASTA 文件"
    )
    merge_dir_parser.add_argument("input_dir", help="输入目录")
    merge_dir_parser.add_argument("output", help="输出 FASTA 文件路径")
    merge_dir_parser.add_argument(
        "--pattern", "-p",
        default="*.fa",
        help="文件匹配模式 (默认: *.fa)"
    )
    merge_dir_parser.add_argument(
        "--recursive", "-r",
        action="store_true",
        help="递归子目录"
    )
    merge_dir_parser.add_argument(
        "--duplicate-handling", "-d",
        choices=["error", "rename", "skip", "overwrite"],
        default="rename",
        help="ID 冲突处理方式 (默认: rename)"
    )
    merge_dir_parser.add_argument(
        "--remove-duplicates",
        action="store_true",
        help="去除序列内容完全相同的记录"
    )
    merge_dir_parser.add_argument(
        "--line-width", "-w",
        type=int,
        default=60,
        help="每行字符数 (默认: 60)"
    )
    
    # info 子命令
    info_parser = fasta_subparsers.add_parser(
        "info",
        help="查看 FASTA 文件信息",
        description="显示 FASTA 文件的基本统计信息"
    )
    info_parser.add_argument("input", help="输入 FASTA 文件路径")
    info_parser.add_argument(
        "--detailed", "-d",
        action="store_true",
        help="显示详细信息"
    )
    
    return parser


def cmd_clean(args: argparse.Namespace) -> int:
    """执行清洗命令"""
    input_path = Path(args.input)
    output_path = Path(args.output)
    
    if not input_path.exists():
        print(f"错误: 输入文件不存在: {input_path}", file=sys.stderr)
        return 1
    
    # 转换序列类型
    seq_type_map = {
        "auto": SeqType.AUTO,
        "dna": SeqType.DNA,
        "rna": SeqType.RNA,
        "protein": SeqType.PROTEIN,
    }
    seq_type = seq_type_map[args.type]
    
    try:
        stats = clean_fasta(
            input_path=input_path,
            output_path=output_path,
            seq_type=seq_type,
            remove_invalid=args.remove_invalid,
            remove_duplicates=args.remove_duplicates,
            min_length=args.min_length,
            max_length=args.max_length,
            max_ambiguous_ratio=args.max_ambiguous,
            line_width=args.line_width,
        )
        
        print(f"[OK] 清洗完成")
        print(f"  输入记录数: {stats.input_count}")
        print(f"  输出记录数: {stats.output_count}")
        print(f"  去除重复: {stats.removed_duplicates}")
        print(f"  长度过滤: {stats.removed_by_length}")
        print(f"  模糊字符过滤: {stats.removed_by_ambiguous}")
        print(f"  清洗字符数: {stats.cleaned_chars}")
        print(f"  输出文件: {output_path}")
        return 0
        
    except Exception as e:
        print(f"错误: {e}", file=sys.stderr)
        return 1


def cmd_split(args: argparse.Namespace) -> int:
    """执行分割命令"""
    input_path = Path(args.input)
    output_dir = Path(args.output_dir)
    
    if not input_path.exists():
        print(f"错误: 输入文件不存在: {input_path}", file=sys.stderr)
        return 1
    
    # 检查分割方式
    split_modes = [
        args.by_count is not None,
        args.into_n is not None,
        args.by_id_list is not None,
        args.single,
    ]
    
    if sum(split_modes) == 0:
        print("错误: 请指定一种分割方式 (--by-count, --into-n, --by-id-list, --single)", file=sys.stderr)
        return 1
    
    if sum(split_modes) > 1:
        print("错误: 只能指定一种分割方式", file=sys.stderr)
        return 1
    
    try:
        if args.by_count:
            files = split_fasta_by_count(
                input_path=input_path,
                output_dir=output_dir,
                records_per_file=args.by_count,
                prefix=args.prefix,
                line_width=args.line_width,
            )
            print(f"[OK] 按记录数分割完成，生成 {len(files)} 个文件")
            
        elif args.into_n:
            files = split_fasta_into_n_files(
                input_path=input_path,
                output_dir=output_dir,
                n_files=args.into_n,
                prefix=args.prefix,
                line_width=args.line_width,
            )
            print(f"[OK] 平均分割完成，生成 {len(files)} 个文件")
            
        elif args.by_id_list:
            id_list_path = Path(args.by_id_list)
            if not id_list_path.exists():
                print(f"错误: ID 列表文件不存在: {id_list_path}", file=sys.stderr)
                return 1
            
            with open(id_list_path, 'r') as f:
                id_list = [line.strip() for line in f if line.strip()]
            
            included_path, excluded_path = split_fasta_by_id_list(
                input_path=input_path,
                output_dir=output_dir,
                id_list=id_list,
                include_mode=not args.exclude,
                prefix_included=f"{args.prefix}_included",
                prefix_excluded=f"{args.prefix}_excluded",
                line_width=args.line_width,
            )
            print(f"[OK] 按 ID 列表分割完成")
            print(f"  包含文件: {included_path}")
            if excluded_path:
                print(f"  排除文件: {excluded_path}")
                
        elif args.single:
            files = split_fasta_to_single_files(
                input_path=input_path,
                output_dir=output_dir,
                naming=args.naming,
                line_width=args.line_width,
            )
            print(f"[OK] 单文件分割完成，生成 {len(files)} 个文件")
        
        print(f"  输出目录: {output_dir}")
        return 0
        
    except Exception as e:
        print(f"错误: {e}", file=sys.stderr)
        return 1


def cmd_merge(args: argparse.Namespace) -> int:
    """执行合并命令"""
    input_paths = [Path(p) for p in args.inputs]
    output_path = Path(args.output)
    
    # 检查输入文件
    for p in input_paths:
        if not p.exists():
            print(f"错误: 输入文件不存在: {p}", file=sys.stderr)
            return 1
    
    # 转换冲突处理方式
    handling_map = {
        "error": DuplicateIDHandling.ERROR,
        "rename": DuplicateIDHandling.RENAME,
        "skip": DuplicateIDHandling.SKIP,
        "overwrite": DuplicateIDHandling.OVERWRITE,
    }
    duplicate_handling = handling_map[args.duplicate_handling]
    
    try:
        stats = merge_fasta_files(
            input_paths=input_paths,
            output_path=output_path,
            duplicate_handling=duplicate_handling,
            remove_duplicates=args.remove_duplicates,
            line_width=args.line_width,
        )
        
        print(f"[OK] 合并完成")
        print(f"  处理文件数: {stats.files_processed}")
        print(f"  读取记录数: {stats.records_read}")
        print(f"  写入记录数: {stats.records_written}")
        print(f"  ID 冲突: {stats.duplicates_found}")
        print(f"  重命名: {stats.renamed_ids}")
        print(f"  跳过: {stats.skipped_records}")
        print(f"  输出文件: {output_path}")
        return 0
        
    except Exception as e:
        print(f"错误: {e}", file=sys.stderr)
        return 1


def cmd_merge_dir(args: argparse.Namespace) -> int:
    """执行目录合并命令"""
    input_dir = Path(args.input_dir)
    output_path = Path(args.output)
    
    if not input_dir.exists():
        print(f"错误: 输入目录不存在: {input_dir}", file=sys.stderr)
        return 1
    
    # 转换冲突处理方式
    handling_map = {
        "error": DuplicateIDHandling.ERROR,
        "rename": DuplicateIDHandling.RENAME,
        "skip": DuplicateIDHandling.SKIP,
        "overwrite": DuplicateIDHandling.OVERWRITE,
    }
    duplicate_handling = handling_map[args.duplicate_handling]
    
    try:
        stats = merge_fasta_from_directory(
            input_dir=input_dir,
            output_path=output_path,
            pattern=args.pattern,
            recursive=args.recursive,
            duplicate_handling=duplicate_handling,
            remove_duplicates=args.remove_duplicates,
            line_width=args.line_width,
        )
        
        print(f"[OK] 目录合并完成")
        print(f"  处理文件数: {stats.files_processed}")
        print(f"  读取记录数: {stats.records_read}")
        print(f"  写入记录数: {stats.records_written}")
        print(f"  ID 冲突: {stats.duplicates_found}")
        print(f"  重命名: {stats.renamed_ids}")
        print(f"  跳过: {stats.skipped_records}")
        print(f"  输出文件: {output_path}")
        return 0
        
    except Exception as e:
        print(f"错误: {e}", file=sys.stderr)
        return 1


def cmd_info(args: argparse.Namespace) -> int:
    """执行信息查看命令"""
    input_path = Path(args.input)
    
    if not input_path.exists():
        print(f"错误: 输入文件不存在: {input_path}", file=sys.stderr)
        return 1
    
    try:
        from seqbox.io.fasta import FastaReader
        
        reader = FastaReader(input_path)
        records = reader.read_all()
        
        total_seqs = len(records)
        total_length = sum(len(r.seq) for r in records)
        avg_length = total_length / total_seqs if total_seqs > 0 else 0
        min_len = min(len(r.seq) for r in records) if records else 0
        max_len = max(len(r.seq) for r in records) if records else 0
        
        print(f"FASTA 文件信息: {input_path}")
        print(f"  序列数量: {total_seqs}")
        print(f"  总长度: {total_length:,} bp/aa")
        print(f"  平均长度: {avg_length:.1f}")
        print(f"  最短: {min_len}")
        print(f"  最长: {max_len}")
        
        if args.detailed and records:
            print(f"\n序列列表:")
            for r in records:
                desc = f" {r.description}" if r.description else ""
                print(f"  >{r.id}{desc} [{len(r.seq)}]")
        
        return 0
        
    except Exception as e:
        print(f"错误: {e}", file=sys.stderr)
        return 1


def main(args: Optional[List[str]] = None) -> int:
    """CLI 入口函数"""
    parser = create_parser()
    parsed_args = parser.parse_args(args)
    
    if parsed_args.command is None:
        parser.print_help()
        return 0
    
    if parsed_args.command == "fasta":
        if parsed_args.fasta_action is None:
            parser.parse_args(["fasta", "--help"])
            return 0
        
        if parsed_args.fasta_action == "clean":
            return cmd_clean(parsed_args)
        elif parsed_args.fasta_action == "split":
            return cmd_split(parsed_args)
        elif parsed_args.fasta_action == "merge":
            return cmd_merge(parsed_args)
        elif parsed_args.fasta_action == "merge-dir":
            return cmd_merge_dir(parsed_args)
        elif parsed_args.fasta_action == "info":
            return cmd_info(parsed_args)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
