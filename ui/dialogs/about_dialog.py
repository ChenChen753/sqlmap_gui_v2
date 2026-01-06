"""
关于对话框
显示工具介绍和作者信息
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton
)
from PyQt6.QtCore import Qt, QUrl
from PyQt6.QtGui import QFont, QDesktopServices

from ..theme import COLORS


class AboutDialog(QDialog):
    """关于对话框"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("关于 SQLMap GUI v2")
        self.setFixedSize(450, 450)  # 稍微增加高度
        self.setup_ui()
    
    def setup_ui(self):
        """设置 UI"""
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # Logo 和标题
        title = QLabel("🔒 SQLMap GUI v2")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setFont(QFont("Microsoft YaHei UI", 20, QFont.Weight.Bold))
        title.setStyleSheet(f"color: {COLORS['accent_blue']};")
        layout.addWidget(title)
        
        # 版本
        version = QLabel("版本 2.0.0")
        version.setAlignment(Qt.AlignmentFlag.AlignCenter)
        version.setStyleSheet(f"color: {COLORS['text_muted']}; font-size: 12px;")
        layout.addWidget(version)
        
        # 分割线
        line = QLabel()
        line.setFixedHeight(2)
        line.setStyleSheet(f"background-color: {COLORS['border']};")
        layout.addWidget(line)
        
        # 工具介绍
        intro = QLabel("""
<p style="text-align: center; line-height: 1.8;">
<b>SQLMap GUI v2</b> 是一款现代化的 SQL 注入检测图形化工具，<br>
基于强大的 <b>sqlmap</b> 开源项目开发。<br><br>
本工具提供友好的图形界面，让 SQL 注入检测更加简单高效。<br>
支持多种注入技术、绕过脚本、数据提取等功能。
</p>
        """)
        intro.setWordWrap(True)
        intro.setAlignment(Qt.AlignmentFlag.AlignCenter)
        intro.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 12px;")
        layout.addWidget(intro)
        
        # 作者信息
        author_box = QLabel()
        author_box.setAlignment(Qt.AlignmentFlag.AlignCenter)
        author_box.setStyleSheet(f"""
            background-color: {COLORS['bg_tertiary']};
            border: 2px solid {COLORS['accent_blue']};
            border-radius: 10px;
            padding: 15px;
        """)
        author_box.setText(f"""
<p style="text-align: center;">
<span style="font-size: 14px; color: {COLORS['text_muted']};">开发作者</span><br><br>
<span style="font-size: 22px; font-weight: bold; color: {COLORS['accent_blue']};">✨ 辰辰 ✨</span>
</p>
        """)
        layout.addWidget(author_box)
        
        # GitHub 链接
        github_layout = QHBoxLayout()
        github_layout.addStretch()
        
        github_btn = QPushButton("🐙 GitHub 仓库")
        github_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: #24292e;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px 20px;
                font-size: 13px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: #2f363d;
            }}
            QPushButton:pressed {{
                background-color: #1a1e22;
            }}
        """)
        github_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        github_btn.clicked.connect(self._open_github)
        github_layout.addWidget(github_btn)
        
        github_layout.addStretch()
        layout.addLayout(github_layout)
        
        # 警告信息
        warning = QLabel("⚠️ 本工具仅供授权安全测试使用")
        warning.setAlignment(Qt.AlignmentFlag.AlignCenter)
        warning.setStyleSheet(f"""
            color: {COLORS['warning']};
            font-size: 11px;
            font-weight: bold;
            padding: 10px;
        """)
        layout.addWidget(warning)
        
        # 关闭按钮
        close_btn = QPushButton("关闭")
        close_btn.setFixedWidth(100)
        close_btn.clicked.connect(self.accept)
        
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        btn_layout.addWidget(close_btn)
        btn_layout.addStretch()
        layout.addLayout(btn_layout)
    
    def _open_github(self):
        """打开 GitHub 仓库"""
        QDesktopServices.openUrl(QUrl("https://github.com/ChenChen753/sqlmap_gui_v2"))

