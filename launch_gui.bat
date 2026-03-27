@echo off
chcp 65001 >nul
title Seq_Box

::: 切换到脚本所在目录（项目根目录）
cd /d "%~dp0"

::: 优先使用 venv，其次 conda，最后系统 Python
if exist ".venv\Scripts\python.exe" (
    set PYTHON=".venv\Scripts\python.exe"
) else if exist "venv\Scripts\python.exe" (
    set PYTHON="venv\Scripts\python.exe"
) else (
    set PYTHON=python
)

::: 检查 Python 是否可用
%PYTHON% --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未找到 Python，请先安装 Python 3.9+
    pause
    exit /b 1
)

::: 检查依赖
%PYTHON% -c "import PyQt6" >nul 2>&1
if errorlevel 1 (
    echo [提示] 正在安装 PyQt6 依赖...
    %PYTHON% -m pip install PyQt6 -q
)

::: 启动 GUI
echo 正在启动 Seq_Box...
%PYTHON% launch.py
