@echo off
chcp 65001 >nul 2>&1
title SQLMap GUI v2

echo ========================================
echo   SQLMap GUI v2 - 智能 SQL 注入检测工�?
echo ========================================
echo.

REM 切换到脚本所在目录（这是最重要的一步）
cd /d "%~dp0"

REM 检�?Python
where python >nul 2>&1
if errorlevel 1 (
    echo [错误] 未找�?Python，请先安�?Python 3.7+
    echo 下载地址: https://www.python.org/downloads/
    pause
    exit /b 1
)

REM 检查依�?
echo [信息] 检查依�?..
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
    echo [错误] 程序异常退�?
    pause
)
