#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SQLMap GUI v2 - 现代化 SQL 注入检测工具
程序入口
"""

import sys
import os
import traceback

# 确保导入路径正确
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

def exception_hook(exctype, value, tb):
    """全局异常处理钩子 - 防止未捕获异常导致程序闪退"""
    error_msg = ''.join(traceback.format_exception(exctype, value, tb))
    print(f"[错误] 未捕获的异常:\n{error_msg}")
    # 不调用原始钩子，避免程序退出
    # sys.__excepthook__(exctype, value, tb)

# 安装全局异常钩子
sys.excepthook = exception_hook

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from ui.main_window import MainWindow


def main():
    """程序入口"""
    # 创建应用
    app = QApplication(sys.argv)
    
    # 设置应用属性
    app.setApplicationName("SQLMap GUI v2")
    app.setApplicationVersion("2.0.0")
    app.setOrganizationName("SQLMap GUI")
    
    # 确保仅在最后一个窗口关闭时退出
    app.setQuitOnLastWindowClosed(True)
    
    # 设置默认字体
    font = QFont("Microsoft YaHei UI", 10)
    app.setFont(font)
    
    # 创建主窗口
    window = MainWindow()
    window.show()
    
    # 运行应用
    app.exec()


if __name__ == "__main__":
    main()

