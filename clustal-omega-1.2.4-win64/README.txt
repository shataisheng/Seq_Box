================================================================
  Clustal Omega - 多序列比对工具 (Windows 64-bit)
================================================================

1. 使用方法
-----------
打开命令提示符(CMD)或 PowerShell，进入本目录，运行：

   clustalo.exe -i input.fasta -o output.aln

2. 常用参数
-----------
   -i, --infile=FILE       输入序列文件 (FASTA 格式)
   -o, --outfile=FILE      输出比对文件
   --outfmt=FORMAT         输出格式: clustal, fasta, msf, phylip, selex, stockholm, vie
   -t, --seqtype=TYPE      序列类型: protein, dna, rna
   --guidetree-out=FILE    输出引导树
   --force                 强制覆盖输出文件
   -h, --help              显示帮助信息

3. 示例
-------
   clustalo.exe -i sequences.fasta -o aligned.aln --outfmt=clustal
   clustalo.exe -i genes.fasta -o genes.aln -t dna --force
   clustalo.exe -i proteins.fasta -o proteins.aln --guidetree-out=tree.nwk

4. 分发说明
-----------
本目录包含 clustalo.exe 及其所有依赖 DLL，可直接拷贝到
其他 64-bit Windows 计算器运行，无需安装任何额外软件。

5. 版本信息
-----------
   Clustal Omega 版本：1.2.4
   平台：Windows 64-bit (MinGW-w64)

================================================================
