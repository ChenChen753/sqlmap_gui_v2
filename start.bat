@echo off
chcp 65001 >nul
title SQLMap GUI v2

echo ========================================
echo   SQLMap GUI v2 - 智能 SQL 注入检测工具
echo ========================================
echo.

REM 检查 Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未找到 Python，请先安装 Python 3.7+
    echo 下载地址: https://www.python.org/downloads/
    pause
    exit /b 1
)

REM 切换到脚本所在目录
cd /d "%~dp0"

REM 检查依赖
echo [信息] 检查依赖...
python -c "import PyQt6" >nul 2>&1
if errorlevel 1 (
    echo [信息] 正在安装 PyQt6...
    pip install PyQt6 -q
)

REM 启动程序
echo [信息] 启动 SQLMap GUI v2...
echo.
python main.py

if errorlevel 1 (
    echo.
    echo [错误] 程序异常退出
    pause
)
