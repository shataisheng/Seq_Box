"""
Seq_Box - 蛋白质批量分析模块

提供FASTA文件的批量蛋白质分析功能
"""

from dataclasses import dataclass
from pathlib import Path
from typing import List, Union
from collections import Counter

from .property import (
    ProteinProperties, 
    MultiChainProtein,
    analyze_sequence,
    analyze_sequences,
)
from ..io.fasta import FastaReader, FastaRecord


@dataclass
class AnalysisResult:
    """分析结果包装类"""
    input_file: str
    same_protein_mode: bool
    chain_count: int
    data: Union[MultiChainProtein, List[ProteinProperties]]
    
    def is_multi_chain_protein(self) -> bool:
        """是否为多链蛋白质模式"""
        return isinstance(self.data, MultiChainProtein)
    
    def get_summary_text(self) -> str:
        """获取汇总文本（用于显示）"""
        lines = []
        lines.append(f"📁 输入文件: {self.input_file}")
        lines.append(f"🔗 分析模式: {'同一蛋白质' if self.same_protein_mode else '多蛋白质'}")
        lines.append(f"🧬 序列条数: {self.chain_count}")
        lines.append("")
        
        if self.is_multi_chain_protein():
            mp = self.data
            lines.append("═" * 50)
            lines.append("📊 整体属性")
            lines.append("═" * 50)
            lines.append(f"  链数: {mp.chain_count}")
            lines.append(f"  总残基数: {mp.total_length:,}")
            lines.append(f"  总分子量: {mp.total_molecular_weight:,.2f} Da")
            lines.append(f"  整体pI: {mp.overall_pi:.2f}")
            lines.append(f"  整体吸光度: {mp.overall_absorbance:.4f}")
            lines.append(f"  整体疏水性 (GRAVY): {mp.overall_gravy:.4f}")
            lines.append("")
            
            if mp.chain_count > 1:
                lines.append("─" * 50)
                lines.append("📋 各链详情")
                lines.append("─" * 50)
                for i, chain in enumerate(mp.chains, 1):
                    lines.append(f"\n  链 {i}:")
                    lines.append(f"    长度: {chain.length} aa")
                    lines.append(f"    分子量: {chain.molecular_weight:,.2f} Da")
                    lines.append(f"    pI: {chain.pi:.2f}")
                    lines.append(f"    消光系数: {chain.extinction_coeff:,}")
                    lines.append(f"    吸光度: {chain.absorbance:.4f}")
                    lines.append(f"    GRAVY: {chain.gravy:.4f}")
        else:
            # 多蛋白质模式
            lines.append("═" * 50)
            lines.append("📋 各蛋白质属性")
            lines.append("═" * 50)
            for i, prop in enumerate(self.data, 1):
                lines.append(f"\n  蛋白质 {i}:")
                lines.append(f"    长度: {prop.length} aa")
                lines.append(f"    分子量: {prop.molecular_weight:,.2f} Da")
                lines.append(f"    pI: {prop.pi:.2f}")
                lines.append(f"    消光系数: {prop.extinction_coeff:,}")
                lines.append(f"    吸光度: {prop.absorbance:.4f}")
                lines.append(f"    GRAVY: {prop.gravy:.4f}")
        
        return "\n".join(lines)
    
    def get_table_data(self) -> List[dict]:
        """获取表格数据（用于GUI表格展示）"""
        rows = []
        
        if self.is_multi_chain_protein():
            mp = self.data
            # 整体汇总行
            total_ext_coeff = sum(c.extinction_coeff for c in mp.chains)
            rows.append({
                'type': 'summary',
                'name': 'Overall',
                'length': mp.total_length,
                'mw_expasy': mp.total_molecular_weight,
                'mw': mp.summed_molecular_weight,
                'pi': mp.overall_pi,
                'ext_coeff': total_ext_coeff,
                'abs_expasy': mp.overall_absorbance,
                'abs': mp.summed_absorbance,
            })
            # 各链详情
            for i, chain in enumerate(mp.chains, 1):
                rows.append({
                    'type': 'chain',
                    'name': f'Chain {i}',
                    'length': chain.length,
                    'mw_expasy': chain.molecular_weight,
                    'mw': chain.molecular_weight,
                    'pi': chain.pi,
                    'ext_coeff': chain.extinction_coeff,
                    'abs_expasy': chain.absorbance,
                    'abs': chain.absorbance,
                })
        else:
            for i, prop in enumerate(self.data, 1):
                rows.append({
                    'type': 'protein',
                    'name': f'Protein {i}',
                    'length': prop.length,
                    'mw_expasy': prop.molecular_weight,
                    'mw': prop.molecular_weight,
                    'pi': prop.pi,
                    'ext_coeff': prop.extinction_coeff,
                    'abs_expasy': prop.absorbance,
                    'abs': prop.absorbance,
                })
        
        return rows


def analyze_fasta_file(
    file_path: Union[str, Path],
    same_protein: bool = True,
    max_chains_warning: int = 10,
) -> AnalysisResult:
    """
    分析FASTA文件中的蛋白质序列
    
    Args:
        file_path: FASTA文件路径
        same_protein: 是否视为同一蛋白质的多条链
        max_chains_warning: 超过此链数时建议确认
        
    Returns:
        AnalysisResult 分析结果
    """
    file_path = Path(file_path)
    
    # 读取FASTA文件
    with FastaReader(file_path) as reader:
        sequences = [record.seq for record in reader]
    
    if not sequences:
        raise ValueError("FASTA file contains no sequences")
    
    # 分析序列
    result_data = analyze_sequences(sequences, same_protein=same_protein)
    
    return AnalysisResult(
        input_file=str(file_path),
        same_protein_mode=same_protein,
        chain_count=len(sequences),
        data=result_data,
    )


def analyze_fasta_text(
    text: str,
    same_protein: bool = True,
) -> AnalysisResult:
    """
    分析FASTA文本中的蛋白质序列
    
    Args:
        text: FASTA格式的文本
        same_protein: 是否视为同一蛋白质的多条链
        
    Returns:
        AnalysisResult 分析结果
    """
    from ..io.fasta import parse_fasta_text
    
    # 解析FASTA文本
    records = parse_fasta_text(text)
    
    if not records:
        raise ValueError("No valid FASTA sequences found")
    
    sequences = [record.seq for record in records]
    
    # 分析序列
    result_data = analyze_sequences(sequences, same_protein=same_protein)
    
    return AnalysisResult(
        input_file="(clipboard)",
        same_protein_mode=same_protein,
        chain_count=len(sequences),
        data=result_data,
    )


def format_molecular_weight(mw: float) -> str:
    """格式化分子量显示"""
    if mw >= 10000:
        return f"{mw/1000:.2f} kDa"
    return f"{mw:.2f} Da"


def format_gravy(gravy: float) -> str:
    """格式化GRAVY显示"""
    if gravy > 0:
        return f"{gravy:.4f} (疏水)"
    elif gravy < 0:
        return f"{gravy:.4f} (亲水)"
    return f"{gravy:.4f} (中性)"


def format_pi(pi: float) -> str:
    """格式化pI显示"""
    if pi < 6:
        return f"{pi:.2f} (酸性)"
    elif pi > 8:
        return f"{pi:.2f} (碱性)"
    return f"{pi:.2f} (中性)"
