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
- 蛋白质序列转换
- 氨基酸分析

### FASTA 文件处理
- FASTA 文件读写
- 序列批量处理
- 文件格式转换

### 图形用户界面
- 直观的 GUI 界面
- 多功能页面（DNA、蛋白质、FASTA、历史记录、设置）
- 操作历史记录

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
- qtawesome >= 1.0（图标库）

### 开发环境安装

如果你希望参与项目开发，请安装开发依赖：

```bash
pip install -e ".[dev]"
```

这将安装以下开发工具：
- pytest >= 7.0（测试框架）
- pytest-cov（测试覆盖率）
- black（代码格式化工具）
- flake8（代码检查工具）

### 验证安装

安装完成后，可以通过以下命令验证：

```bash
# 检查命令行工具是否可用
seqbox --version

# 如果安装了 GUI
seqbox-gui --help

# 测试 Python 导入
python -c "from seqbox.dna.basic import reverse_complement; print('安装成功！')"
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

#### 运行测试

```bash
# 运行所有测试
pytest

# 运行特定测试文件
pytest tests/test_dna.py

# 运行特定测试函数
pytest tests/test_dna.py::test_reverse_complement

# 显示详细的测试输出
pytest -v

# 显示测试覆盖率
pytest --cov=seqbox --cov-report=html

# 运行测试并生成覆盖率报告
pytest --cov=seqbox --cov-report=term-missing
```

#### 测试示例

以下是一些测试示例，帮助你理解如何测试各个功能：

```python
# tests/test_dna.py
import pytest
from seqbox.dna.basic import reverse_complement, transcribe, translate

def test_reverse_complement():
    """测试 DNA 反向互补功能"""
    assert reverse_complement("ATCG") == "CGAT"
    assert reverse_complement("AATT") == "AATT"

def test_transcribe():
    """测试 DNA 转录功能"""
    assert transcribe("ATCG") == "AUCG"

def test_translate():
    """测试 DNA 翻译功能"""
    assert translate("ATG") == "M"
    assert translate("TAA") == "*"

# tests/test_protein.py
import pytest
from seqbox.protein.convert import reverse_translate

def test_reverse_translate():
    """测试蛋白质反向翻译功能"""
    assert reverse_translate("M") == "ATG"
```

#### 测试最佳实践

1. **编写清晰的测试名称**：测试函数名应该清楚地描述测试的内容
2. **使用断言**：使用 `assert` 语句验证预期结果
3. **测试边界情况**：测试空字符串、单个字符等边界情况
4. **保持测试独立**：每个测试应该独立运行，不依赖其他测试
5. **使用 fixtures**：对于重复的测试数据，使用 pytest fixtures

### 代码格式化

```bash
# 运行所有测试
pytest

# 运行特定测试文件
pytest tests/test_dna.py

# 运行特定测试函数
pytest tests/test_dna.py::test_reverse_complement

# 显示详细的测试输出
pytest -v

# 显示测试覆盖率
pytest --cov=seqbox --cov-report=html

# 运行测试并生成覆盖率报告
pytest --cov=seqbox --cov-report=term-missing
```

### 代码格式化

```bash
# 格式化所有代码
black seqbox/

# 检查代码格式（不修改文件）
black --check seqbox/

# 格式化特定文件
black seqbox/dna/basic.py
```

### 代码检查

```bash
# 检查所有代码
flake8 seqbox/

# 检查特定文件
flake8 seqbox/dna/basic.py

# 显示更详细的错误信息
flake8 --show-source seqbox/
```

### 开发工作流

推荐的开发工作流程：

```bash
# 1. 创建开发分支
git checkout -b feature/your-feature

# 2. 进行代码修改

# 3. 运行测试确保功能正常
pytest

# 4. 格式化代码
black seqbox/

# 5. 检查代码质量
flake8 seqbox/

# 6. 提交更改
git add .
git commit -m "描述你的更改"

# 7. 推送到远程仓库
git push origin feature/your-feature
```

## 许可证

MIT License

## 贡献

欢迎提交 Issue 和 Pull Request！

## 联系方式

- 项目主页：https://github.com/seqbox/seqbox
- 问题反馈：https://github.com/seqbox/seqbox/issues

## 更新日志

### 0.4.0
- 初始版本发布
- 核心功能实现
- GUI 界面完成
- 命令行工具支持
