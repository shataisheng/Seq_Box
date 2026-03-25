# Seq_Box

**DNA / 蛋白质序列操作工具箱**

Seq_Box 是一个面向生物信息学研究者的序列处理工具，支持命令行和桌面 GUI 两种使用方式。核心功能涵盖 FASTA 文件处理、DNA 基础操作与转换、蛋白质分析，零第三方依赖（GUI 除外），可轻松共享给同学和同事。

---

## 功能概览

### FASTA 文件处理
- **清洗**：去除非法字符、去重复序列、按长度过滤，支持 DNA / RNA / 蛋白质类型自动识别
- **分割**：按记录数分割、平均分割为 N 个文件、每条序列单独一个文件
- **合并**：合并多个 FASTA 文件，支持重复 ID 的自动重命名 / 报错 / 跳过 / 覆盖处理
- **信息**：查看序列数量、总长度、平均 / 最短 / 最长长度

### DNA 操作
- **基础转换**：互补链、反向互补、转录（DNA→RNA）、逆转录（RNA→DNA）
- **翻译**：支持 4 套密码子表（标准 / 脊椎动物线粒体 / 细菌 / 酵母线粒体），支持六框翻译
- **ORF 搜索**：正反六框扫描，可设置最小 ORF 长度
- **统计分析**：GC 含量、碱基组成、分子量、熔解温度（Wallace / Salt-adjusted / Nearest-neighbor）

### 蛋白质分析
- **格式转换**：氨基酸单字母 ↔ 三字母互转
- **氨基酸信息**：全名、性质分类查询
- **理化属性**：分子量、消光系数、等电点、特定 pH 下净电荷

---

## 安装

```bash
# 仅安装核心功能（命令行）
pip install seqbox

# 安装含 GUI 的完整版
pip install seqbox[gui]
```

> **Python 版本要求**：Python ≥ 3.9

---

## 快速上手

### 命令行

```bash
# 查看帮助
seqbox --help
seqbox fasta --help

# 查看 FASTA 文件信息
seqbox fasta info input.fasta

# 清洗序列（去非法字符，DNA 类型）
seqbox fasta clean input.fasta output.fasta --type dna --remove-invalid

# 按每 100 条分割
seqbox fasta split input.fasta ./split_output --by-count 100 --prefix part

# 合并多个文件
seqbox fasta merge file1.fa file2.fa file3.fa -o merged.fasta
```

### Python API

```python
from seqbox.io.fasta import FastaReader, FastaWriter, clean_fasta
from seqbox.dna.basic import complement, reverse_complement, gc_content
from seqbox.dna.convert import transcribe, translate, find_orfs
from seqbox.protein.convert import to_triple, calculate_isoelectric_point

# 读取 FASTA 文件
reader = FastaReader("input.fasta")
records = reader.read_all()
for r in records:
    print(r.id, len(r.seq))

# DNA 操作
seq = "ATGAAATTTGCCTAA"
print(reverse_complement(seq))       # 反向互补
print(gc_content(seq))               # GC 含量
print(transcribe(seq))               # 转录为 RNA
print(translate(seq))                # 翻译为蛋白质

# 搜索 ORF
orfs = find_orfs(seq, min_length=30)
for orf in orfs:
    print(orf)

# 蛋白质分析
protein = "MKAAA"
print(to_triple(protein))                      # 三字母
print(calculate_isoelectric_point(protein))    # 等电点

# 清洗 FASTA 文件
from seqbox.io.fasta import SeqType
stats = clean_fasta("raw.fasta", "clean.fasta", seq_type=SeqType.DNA, remove_invalid=True)
print(f"输入 {stats.input_count} 条 → 输出 {stats.output_count} 条")
```

---

## GUI 使用

```bash
# 启动桌面 GUI（需安装 PyQt6）
pip install PyQt6
seqbox-gui
```

GUI 提供以下页面：

| 页面 | 功能 |
|------|------|
| FASTA 工具 | 清洗、分割、合并、信息查看 |
| DNA 操作 | 基础转换、翻译、ORF 搜索、统计分析 |
| 蛋白质 | 格式转换、理化属性分析 |
| 历史记录 | 操作历史 |
| 设置 | 主题与偏好设置 |

### GUI 特色功能

- **剪贴板粘贴**：支持直接粘贴 FASTA 序列，无需保存文件
- **Excel 表格兼容**：从 Excel 复制两列数据（A 列 Header、B 列序列）可自动转换为 FASTA 格式
- **结果预览与快速复制**：操作完成后在界面内直接预览结果，一键复制到剪贴板
- **默认结果目录**：所有输出自动保存到 `results/YYYYMMDD_HHMMSS/` 时间戳子文件夹
- **FASTA 换行设置**：支持 60 / 80 / 100 字符换行或不换行

---

## 项目结构

```
seqbox/
├── core/           # 序列基类（DNA / RNA / Protein），IUPAC 校验
├── io/
│   └── fasta.py    # FASTA 读写、清洗、分割、合并
├── dna/
│   ├── basic.py    # 互补、RC、GC、碱基统计、Tm 计算
│   └── convert.py  # 转录、翻译、六框翻译、ORF 搜索
├── protein/
│   └── convert.py  # 单/三字母互转、理化属性
├── gui/            # PyQt6 桌面 GUI
│   ├── main_window.py
│   └── pages/      # 各功能页面
└── cli.py          # 命令行接口（argparse）
```

---

## 版本路线图

| 版本 | 状态 | 内容 |
|------|------|------|
| v0.1.x | ✅ 完成 | 核心基类、FASTA I/O、清洗、分割、合并、CLI |
| v0.1.6 | ✅ 完成 | DNA 基础操作、转换、ORF 搜索 |
| v0.3.0 | ✅ 完成 | 蛋白质格式转换与理化分析 |
| v0.4.0 | ✅ 完成 | PyQt6 桌面 GUI |
| v2.0.0 | 📋 规划中 | 理化属性增强、引物/酶切、模式搜索、统计 |
| v3.0.0 | 📋 规划中 | 序列比对、可视化、密码子优化、质谱模拟 |

---

## 依赖

| 依赖 | 用途 | 是否必需 |
|------|------|----------|
| Python ≥ 3.9 | 运行环境 | ✅ 必需 |
| PyQt6 | 桌面 GUI | ⭕ 可选 |

核心库（`seqbox.core`、`seqbox.io`、`seqbox.dna`、`seqbox.protein`）**零第三方依赖**，仅使用 Python 标准库。

---

## License

MIT License
