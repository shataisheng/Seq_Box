@echo off
chcp 65001 >nul
echo ==========================================
echo Seq_Box 打包工具
echo ==========================================
echo.

REM 检查 Python 是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未检测到 Python，请先安装 Python 3.9+
    pause
    exit /b 1
)

echo [1/5] 检查 PyInstaller...
pip show pyinstaller >nul 2>&1
if errorlevel 1 (
    echo     PyInstaller 未安装，正在安装...
    pip install pyinstaller
) else (
    echo     PyInstaller 已安装
)

echo.
echo [2/5] 检查项目依赖...
pip show PyQt6 >nul 2>&1
if errorlevel 1 (
    echo     正在安装 GUI 依赖...
    pip install PyQt6
) else (
    echo     GUI 依赖已安装
)

echo.
echo [3/5] 清理旧构建...
if exist "build" rmdir /s /q "build"
if exist "dist" rmdir /s /q "dist"
if exist "*.spec" del /q "*.spec"
echo     清理完成

echo.
echo [4/5] 开始打包...
python -m PyInstaller ^
    --name "SeqBox" ^
    --onedir ^
    --windowed ^
    --icon "NONE" ^
    --add-data "seqbox;seqbox" ^
    --hidden-import PyQt6.QtCore ^
    --hidden-import PyQt6.QtGui ^
    --hidden-import PyQt6.QtWidgets ^
    --hidden-import seqbox.core ^
    --hidden-import seqbox.core.alphabets ^
    --hidden-import seqbox.core.sequence ^
    --hidden-import seqbox.io ^
    --hidden-import seqbox.io.fasta ^
    --hidden-import seqbox.dna ^
    --hidden-import seqbox.dna.basic ^
    --hidden-import seqbox.dna.convert ^
    --hidden-import seqbox.protein ^
    --hidden-import seqbox.protein.property ^
    --hidden-import seqbox.protein.convert ^
    --hidden-import seqbox.protein.analysis ^
    --hidden-import seqbox.gui ^
    --hidden-import seqbox.gui.main_window ^
    --hidden-import seqbox.gui.pages ^
    --hidden-import seqbox.gui.pages.base_page ^
    --hidden-import seqbox.gui.pages.fasta_page ^
    --hidden-import seqbox.gui.pages.dna_page ^
    --hidden-import seqbox.gui.pages.protein_page ^
    --hidden-import seqbox.gui.pages.history_page ^
    --hidden-import seqbox.gui.pages.settings_page ^
    --collect-all PyQt6 ^
    --clean ^
    launch.py

echo.
echo [5/5] 复制启动脚本...
if exist "dist\SeqBox" (
    copy /y "launch_gui.bat" "dist\SeqBox\" >nul
    echo     启动脚本已复制
)

echo.
echo ==========================================
if exist "dist\SeqBox\SeqBox.exe" (
    echo [成功] 打包完成！
    echo.
    echo 输出目录: dist\SeqBox\
    echo 可执行文件: dist\SeqBox\SeqBox.exe
    echo.
    echo 提示: 可以将 dist\SeqBox 文件夹整体复制到其他电脑使用
) else (
    echo [失败] 打包过程中出现错误
)
echo ==========================================
pause
