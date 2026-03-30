# Seq_Box

DNA/蛋白质序列操作工具箱

## 简介

Seq_Box 是一个功能强大的生物信息学工具箱，专门用于 DNA 和蛋白质序列的分析与操作。它提供了命令行界面和图形用户界面，方便不同需求的用户使用。

## 功能特性

### DNA 序列操作
- 基本序列操作（反向互补、转录、翻译等）
- 序列转换工具
- 序列统计分析

### 蛋白质序列操作
- **蛋白质理化性质分析**（v0.4.1 新增）
  - 分子量计算（支持 Expasy 模式和链汇总模式）
  - 等电点（pI）预测
  - 消光系数和吸光度计算（Expasy 整体模式）
  - 疏水性（GRAVY）分析
  - 支持多链蛋白质分析
- 蛋白质序列转换
- 氨基酸分析

### FASTA 文件处理
- FASTA 文件读写
- 序列批量处理
- 文件格式转换

### 图形用户界面
- 直观的 GUI 界面（PyQt6 + Tokyo Night 暗色主题）
- 多功能页面（FASTA、DNA、蛋白质、历史记录、设置）
- 操作历史记录
- 一键复制分析结果

## 安装

### 系统要求

- Python 3.9 或更高版本
- pip 包管理器

### 从源码安装

```bash
# 克隆仓库
git clone https://github.com/seqbox/seqbox.git
cd seqbox

# 安装核心功能
pip install -e .
```

### 安装 GUI 依赖（可选）

如果需要使用图形用户界面，请安装额外的依赖：

```bash
pip install -e ".[gui]"
```

这将安装以下依赖：
- PyQt6 >= 6.0（GUI 框架）

### 开发环境安装

如果你希望参与项目开发，请安装开发依赖：

```bash
pip install -e ".[dev]"
```

## 使用方法

### 命令行界面

```bash
# 启动命令行工具
seqbox

# 查看帮助信息
seqbox --help
```

### 图形用户界面

```bash
# 启动 GUI
seqbox-gui

# 或使用启动脚本（Windows）
launch_gui.bat
```

### Python API

```python
from seqbox.dna.basic import reverse_complement
from seqbox.protein.convert import translate

# DNA 反向互补
dna_seq = "ATCGATCG"
rc_seq = reverse_complement(dna_seq)

# DNA 翻译为蛋白质
protein_seq = translate(dna_seq)
```

## 打包为可执行文件

### 使用 PyInstaller

1. 安装 PyInstaller：
```bash
pip install pyinstaller
```

2. 运行打包脚本：
```bash
build_exe.bat
```

打包完成后，可执行文件位于 `dist/SeqBox/` 目录下。

### 打包说明

- 使用 `--onedir` 模式，启动更快
- 自动包含所有资源文件
- 支持 Windows 10/11

## 项目结构

```
seqbox/
├── core/           # 核心功能模块
│   ├── alphabets.py    # 序列字母表定义
│   └── sequence.py    # 序列基础类
├── dna/            # DNA 序列操作
│   ├── basic.py        # 基本 DNA 操作
│   └── convert.py      # DNA 转换工具
├── protein/        # 蛋白质序列操作
│   ├── property.py     # 蛋白质理化性质
│   ├── analysis.py     # 批量分析工具
│   └── convert.py      # 蛋白质转换工具
├── io/             # 文件输入输出
│   └── fasta.py        # FASTA 文件处理
├── gui/            # 图形用户界面
│   ├── main_window.py  # 主窗口
│   └── pages/          # 各功能页面
└── cli.py          # 命令行界面
```

## 开发

### 测试指南

```bash
# 运行所有测试
pytest

# 运行特定测试文件
pytest tests/test_dna.py

# 显示测试覆盖率
pytest --cov=seqbox --cov-report=html
```

### 代码格式化

```bash
# 格式化所有代码
black seqbox/

# 检查代码格式
black --check seqbox/
```

### 代码检查

```bash
# 检查所有代码
flake8 seqbox/
```

## 许可证

MIT License

## 贡献

欢迎提交 Issue 和 Pull Request！

## 更新日志

### 0.4.1
- 修复多链蛋白质消光系数计算 bug
  - 整体消光系数改用 Expasy 整体模式（合并序列计算）
  - 解决奇数 Cys 链孤立 Cys 无法配对的问题
- 蛋白质分析表格新增 Hb (GRAVY) 列
- UI 微调：表格内容与表头统一左对齐，日志框边距对齐

### 0.4.0
- 新增蛋白质理化性质分析功能
  - 支持多链蛋白质分析
  - Expasy 模式和链汇总模式双显示
  - 分子量、pI、吸光度、GRAVY 计算
- 优化 GUI 界面
  - 表格结果支持一键复制 CSV
  - 默认选中整体结果高亮显示
- 修复多链蛋白质水分子计算问题
