@echo off
chcp 936 >nul
:: ==========================================
:: Seq_Box 一键打包脚本 (修复版)
:: ==========================================

REM ---------- 检测 Python 环境 ----------
set VENV_PYTHON=.venv\Scripts\python.exe
if exist "%VENV_PYTHON%" (
    echo [OK] 使用虚拟环境: %VENV_PYTHON%
) else (
    echo [警告] 未找到虚拟环境，使用系统 Python
    set VENV_PYTHON=python
)

%VENV_PYTHON% --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未检测到 Python，请先安装 Python 3.9+
    pause
    exit /b 1
)
echo [OK] Python 已就绪

REM ---------- 前置检查 ----------
if not exist "launch.py" (
    echo [错误] 未找到 launch.py，请在 Seq_Box 项目根目录执行此脚本
    pause
    exit /b 1
)
if not exist "seqbox\__init__.py" (
    echo [错误] 未找到 seqbox 模块目录
    pause
    exit /b 1
)

REM ---------- [1/6] 检测包管理器 ----------
echo.
echo [1/6] 检测包管理器...
set USE_UV=0
uv --version >nul 2>&1
if not errorlevel 1 set USE_UV=1
%VENV_PYTHON% -m uv --version >nul 2>&1
if not errorlevel 1 set USE_UV=1

if "%USE_UV%"=="1" (
    echo     使用 UV
) else (
    echo     使用 pip
)

REM ---------- [2/6] 安装项目依赖 ----------
echo.
echo [2/6] 安装项目依赖...
if "%USE_UV%"=="1" (
    uv sync
) else (
    %VENV_PYTHON% -m pip show PyQt6 >nul 2>&1
    if errorlevel 1 (
        echo     正在安装 PyQt6...
        %VENV_PYTHON% -m pip install PyQt6
    ) else (
        echo     PyQt6 已安装
    )
)

REM ---------- [3/6] 安装 PyInstaller ----------
echo.
echo [3/6] 安装 PyInstaller...
if "%USE_UV%"=="1" (
    uv pip install pyinstaller
) else (
    %VENV_PYTHON% -m pip show pyinstaller >nul 2>&1
    if errorlevel 1 (
        echo     PyInstaller 未安装，正在安装...
        %VENV_PYTHON% -m pip install pyinstaller
    ) else (
        echo     PyInstaller 已安装
    )
)

REM ---------- [4/6] 清理旧构建 ----------
echo.
echo [4/6] 清理旧构建...
if exist "build" rmdir /s /q "build" 2>nul
if exist "dist\SeqBox" rmdir /s /q "dist\SeqBox" 2>nul
if exist "SeqBox.spec" del /q "SeqBox.spec" 2>nul
echo     清理完毕

REM ---------- [5/6] PyInstaller 打包 ----------
echo.
echo [5/6] 开始打包（需要几分钟）...
%VENV_PYTHON% -m PyInstaller ^
    --name "SeqBox" ^
    --onedir ^
    --windowed ^
    --noconfirm ^
    --add-data "seqbox;seqbox" ^
    --add-data "clustal-omega-1.2.4-win64;clustal-omega-1.2.4-win64" ^
    --hidden-import PyQt6.QtCore ^
    --hidden-import PyQt6.QtGui ^
    --hidden-import PyQt6.QtWidgets ^
    --hidden-import seqbox.core ^
    --hidden-import seqbox.core.alphabets ^
    --hidden-import seqbox.core.sequence ^
    --hidden-import seqbox.io ^
    --hidden-import seqbox.io.fasta ^
    --hidden-import seqbox.alignment ^
    --hidden-import seqbox.alignment.cluster ^
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

if errorlevel 1 (
    echo.
    echo ==========================================
    echo [失败] PyInstaller 打包过程出错
    echo ==========================================
    pause
    exit /b 1
)

REM ---------- [6/6] 复制启动脚本 ----------
echo.
echo [6/6] 复制启动脚本...
if exist "dist\SeqBox" (
    copy /y "launch_gui.bat" "dist\SeqBox" >nul
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
    echo 注意: Clustal Omega 需在系统 PATH 中或同目录下才能使用比对功能
) else (
    echo [失败] 未找到 SeqBox.exe，请检查上方错误信息
)
echo ==========================================
pause

