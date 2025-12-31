"""
设置对话框
用于配置 SQLMap 路径、界面主题和语言
"""

import os
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QComboBox, QGroupBox, QFileDialog, QTabWidget,
    QWidget, QFormLayout, QMessageBox
)
from PyQt6.QtCore import pyqtSignal, Qt

from ..theme import COLORS, get_theme_names, get_theme_colors


class SettingsDialog(QDialog):
    """设置对话框"""
    
    # 信号
    settings_changed = pyqtSignal()
    theme_changed = pyqtSignal(str)
    language_changed = pyqtSignal(str)
    
    def __init__(self, config_manager, parent=None):
        super().__init__(parent)
        self.config = config_manager
        self.setWindowTitle("⚙️ 设置")
        self.setMinimumSize(520, 480)
        self.setup_ui()
        self.load_settings()
    
    def setup_ui(self):
        """设置 UI"""
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        
        # 标签页
        tabs = QTabWidget()
        
        # 常规设置标签页
        general_tab = QWidget()
        self._setup_general_tab(general_tab)
        tabs.addTab(general_tab, "🔧 常规")
        
        # 外观设置标签页
        appearance_tab = QWidget()
        self._setup_appearance_tab(appearance_tab)
        tabs.addTab(appearance_tab, "🎨 外观")
        
        layout.addWidget(tabs)
        
        # 按钮区
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        apply_btn = QPushButton("应用")
        apply_btn.setMinimumWidth(80)
        apply_btn.clicked.connect(self.apply_settings)
        btn_layout.addWidget(apply_btn)
        
        ok_btn = QPushButton("确定")
        ok_btn.setMinimumWidth(80)
        ok_btn.setProperty("class", "primary")
        ok_btn.clicked.connect(self.accept_settings)
        btn_layout.addWidget(ok_btn)
        
        cancel_btn = QPushButton("取消")
        cancel_btn.setMinimumWidth(80)
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)
        
        layout.addLayout(btn_layout)
    
    def _setup_general_tab(self, tab):
        """设置常规标签页"""
        layout = QVBoxLayout(tab)
        layout.setSpacing(15)
        
        # SQLMap 路径设置
        sqlmap_group = QGroupBox("📁 SQLMap 配置")
        sqlmap_layout = QVBoxLayout(sqlmap_group)
        
        # 路径输入
        path_layout = QHBoxLayout()
        path_layout.addWidget(QLabel("SQLMap 路径:"))
        
        self.sqlmap_path_input = QLineEdit()
        self.sqlmap_path_input.setPlaceholderText("选择 sqlmap.py 文件路径...")
        path_layout.addWidget(self.sqlmap_path_input)
        
        browse_btn = QPushButton("浏览...")
        browse_btn.clicked.connect(self._browse_sqlmap)
        path_layout.addWidget(browse_btn)
        
        sqlmap_layout.addLayout(path_layout)
        
        # Python 路径
        python_layout = QHBoxLayout()
        python_layout.addWidget(QLabel("Python 路径:"))
        
        self.python_path_input = QLineEdit()
        self.python_path_input.setPlaceholderText("留空使用系统默认 Python")
        python_layout.addWidget(self.python_path_input)
        
        browse_python_btn = QPushButton("浏览...")
        browse_python_btn.clicked.connect(self._browse_python)
        python_layout.addWidget(browse_python_btn)
        
        sqlmap_layout.addLayout(python_layout)
        
        # 自动检测按钮
        detect_btn = QPushButton("🔍 自动检测 SQLMap")
        detect_btn.clicked.connect(self._auto_detect_sqlmap)
        sqlmap_layout.addWidget(detect_btn)
        
        layout.addWidget(sqlmap_group)
        
        # 扫描设置
        scan_group = QGroupBox("⚡ 扫描设置")
        scan_layout = QFormLayout(scan_group)
        
        self.default_threads = QComboBox()
        for i in range(1, 11):
            self.default_threads.addItem(str(i), i)
        self.default_threads.setCurrentIndex(2)  # 默认3线程
        scan_layout.addRow("默认线程数:", self.default_threads)
        
        self.default_timeout = QComboBox()
        for t in [10, 20, 30, 60, 120]:
            self.default_timeout.addItem(f"{t} 秒", t)
        self.default_timeout.setCurrentIndex(2)  # 默认30秒
        scan_layout.addRow("默认超时:", self.default_timeout)
        
        layout.addWidget(scan_group)
        
        layout.addStretch()
    
    def _setup_appearance_tab(self, tab):
        """设置外观标签页"""
        layout = QVBoxLayout(tab)
        layout.setSpacing(15)
        
        # 语言设置（仅保留中文）
        lang_group = QGroupBox("🌐 语言设置")
        lang_layout = QVBoxLayout(lang_group)
        
        lang_row = QHBoxLayout()
        lang_row.addWidget(QLabel("界面语言:"))
        
        self.language_combo = QComboBox()
        self.language_combo.addItem("简体中文", "zh_CN")
        lang_row.addWidget(self.language_combo)
        lang_row.addStretch()
        
        lang_layout.addLayout(lang_row)
        
        # 语言提示
        lang_note = QLabel("✓ 当前仅支持简体中文界面")
        lang_note.setStyleSheet("color: #9ece6a; font-size: 11px;")
        lang_layout.addWidget(lang_note)
        
        layout.addWidget(lang_group)
        
        # 主题设置
        theme_group = QGroupBox("🎨 主题")
        theme_layout = QVBoxLayout(theme_group)
        
        theme_row = QHBoxLayout()
        theme_row.addWidget(QLabel("界面主题:"))
        
        self.theme_combo = QComboBox()
        theme_names = get_theme_names()
        for name, display_name in theme_names.items():
            self.theme_combo.addItem(display_name, name)
        self.theme_combo.currentIndexChanged.connect(self._on_theme_preview)
        theme_row.addWidget(self.theme_combo)
        theme_row.addStretch()
        
        theme_layout.addLayout(theme_row)
        
        # 主题预览
        self.preview_label = QLabel("主题预览效果")
        self.preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.preview_label.setMinimumHeight(80)
        self.preview_label.setStyleSheet(f"""
            background-color: {COLORS['bg_primary']};
            color: {COLORS['text_primary']};
            border: 2px solid {COLORS['border']};
            border-radius: 8px;
            padding: 15px;
            font-size: 13px;
        """)
        theme_layout.addWidget(self.preview_label)
        
        layout.addWidget(theme_group)
        
        # 字体设置
        font_group = QGroupBox("📝 字体")
        font_layout = QFormLayout(font_group)
        
        self.font_size_combo = QComboBox()
        for size in [9, 10, 11, 12, 13, 14]:
            self.font_size_combo.addItem(f"{size}pt", size)
        self.font_size_combo.setCurrentIndex(1)  # 默认10pt
        font_layout.addRow("字体大小:", self.font_size_combo)
        
        layout.addWidget(font_group)
        
        layout.addStretch()
    
    def _browse_sqlmap(self):
        """浏览 SQLMap 路径"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择 sqlmap.py", "",
            "Python 文件 (*.py);;所有文件 (*.*)"
        )
        if file_path:
            self.sqlmap_path_input.setText(file_path)
    
    def _browse_python(self):
        """浏览 Python 路径"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择 Python 解释器", "",
            "可执行文件 (*.exe);;所有文件 (*.*)"
        )
        if file_path:
            self.python_path_input.setText(file_path)
    
    def _auto_detect_sqlmap(self):
        """自动检测 SQLMap"""
        from ...core.sqlmap_engine import SqlmapFinder
        path = SqlmapFinder.find_sqlmap()
        if path:
            self.sqlmap_path_input.setText(path)
            QMessageBox.information(self, "检测成功", f"找到 SQLMap:\n{path}")
        else:
            QMessageBox.warning(self, "检测失败", "未能自动检测到 SQLMap，请手动选择路径。")
    
    def _on_theme_preview(self, index):
        """主题预览"""
        theme_name = self.theme_combo.currentData()
        colors = get_theme_colors(theme_name)
        self.preview_label.setStyleSheet(f"""
            background-color: {colors['bg_primary']};
            color: {colors['text_primary']};
            border: 2px solid {colors['border']};
            border-radius: 8px;
            padding: 15px;
            font-size: 13px;
        """)
        self.preview_label.setText(f"✨ {self.theme_combo.currentText()} 主题预览")
    
    def load_settings(self):
        """加载设置"""
        # SQLMap 路径
        sqlmap_path = self.config.get("sqlmap", "path", "")
        self.sqlmap_path_input.setText(sqlmap_path)
        
        # Python 路径
        python_path = self.config.get("sqlmap", "python_path", "")
        self.python_path_input.setText(python_path)
        
        # 语言
        language = self.config.get("ui", "language", "zh_CN")
        lang_index = self.language_combo.findData(language)
        if lang_index >= 0:
            self.language_combo.setCurrentIndex(lang_index)
        
        # 主题
        theme = self.config.get("ui", "theme", "dark")
        index = self.theme_combo.findData(theme)
        if index >= 0:
            self.theme_combo.setCurrentIndex(index)
    
    def apply_settings(self):
        """应用设置"""
        # 保存 SQLMap 路径
        self.config.set("sqlmap", "path", self.sqlmap_path_input.text())
        self.config.set("sqlmap", "python_path", self.python_path_input.text())
        
        # 保存语言
        language = self.language_combo.currentData()
        old_language = self.config.get("ui", "language", "zh_CN")
        self.config.set("ui", "language", language)
        
        # 保存主题
        theme = self.theme_combo.currentData()
        self.config.set("ui", "theme", theme)
        
        # 保存扫描设置
        self.config.set("scan", "default_threads", str(self.default_threads.currentData()))
        self.config.set("scan", "default_timeout", str(self.default_timeout.currentData()))
        
        # 保存字体大小
        self.config.set("ui", "font_size", str(self.font_size_combo.currentData()))
        
        self.config.save()
        self.settings_changed.emit()
        self.theme_changed.emit(theme)
        
        # 如果语言变化，发送信号
        if language != old_language:
            self.language_changed.emit(language)
    
    def accept_settings(self):
        """确定并关闭"""
        self.apply_settings()
        self.accept()
