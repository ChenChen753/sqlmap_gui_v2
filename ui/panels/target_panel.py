"""
目标配置面板
用于配置扫描目标和请求参数
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QPushButton, QComboBox, QTextEdit, QFileDialog, QCheckBox,
    QGridLayout
)
from PyQt6.QtCore import pyqtSignal, Qt

from ..theme import COLORS
from ..widgets.card_widget import CardWidget


class TargetPanel(QWidget):
    """目标配置面板"""
    
    # 信号
    target_changed = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
    
    def setup_ui(self):
        """设置 UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(15)
        
        # ==================== 目标 URL 卡片 ====================
        url_card = CardWidget("🎯 目标设置")
        
        # URL 输入区域
        url_layout = QHBoxLayout()
        
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("输入目标 URL，例如：http://example.com/page.php?id=1")
        self.url_input.setMinimumHeight(45)
        self.url_input.setStyleSheet(f"""
            QLineEdit {{
                font-size: 14px;
                padding: 12px 15px;
            }}
        """)
        self.url_input.textChanged.connect(self.target_changed.emit)
        url_layout.addWidget(self.url_input)
        
        # 粘贴按钮
        paste_btn = QPushButton("📋 粘贴")
        paste_btn.setProperty("class", "secondary")
        paste_btn.clicked.connect(self._paste_url)
        paste_btn.setMinimumWidth(90)
        url_layout.addWidget(paste_btn)
        
        # 清除按钮
        clear_btn = QPushButton("🗑️ 清除")
        clear_btn.setProperty("class", "secondary")
        clear_btn.clicked.connect(self._clear_url)
        clear_btn.setMinimumWidth(90)
        url_layout.addWidget(clear_btn)
        
        url_card.add_layout(url_layout)
        
        # 从文件加载
        file_layout = QHBoxLayout()
        
        self.file_check = QCheckBox("从文件批量扫描")
        self.file_check.stateChanged.connect(self._on_file_check_changed)
        file_layout.addWidget(self.file_check)
        
        self.file_input = QLineEdit()
        self.file_input.setPlaceholderText("选择包含 URL 列表的文件...")
        self.file_input.setEnabled(False)
        file_layout.addWidget(self.file_input)
        
        self.browse_btn = QPushButton("浏览...")
        self.browse_btn.setProperty("class", "secondary")
        self.browse_btn.clicked.connect(self._browse_file)
        self.browse_btn.setEnabled(False)
        self.browse_btn.setMinimumWidth(90)
        file_layout.addWidget(self.browse_btn)
        
        url_card.add_layout(file_layout)
        
        # 从请求包扫描（头注入检测）
        request_layout = QHBoxLayout()
        
        self.request_check = QCheckBox("从请求包扫描（头注入）")
        self.request_check.stateChanged.connect(self._on_request_check_changed)
        request_layout.addWidget(self.request_check)
        
        self.request_input = QLineEdit()
        self.request_input.setPlaceholderText("选择 HTTP 请求包文件（Burp Suite 等工具导出）...")
        self.request_input.setEnabled(False)
        request_layout.addWidget(self.request_input)
        
        self.request_browse_btn = QPushButton("浏览...")
        self.request_browse_btn.setProperty("class", "secondary")
        self.request_browse_btn.clicked.connect(self._browse_request_file)
        self.request_browse_btn.setEnabled(False)
        self.request_browse_btn.setMinimumWidth(90)
        request_layout.addWidget(self.request_browse_btn)
        
        url_card.add_layout(request_layout)
        
        # 请求包内容编辑区
        self.request_content_label = QLabel("📝 请求包内容（可直接粘贴）:")
        self.request_content_label.setVisible(False)
        url_card.add_widget(self.request_content_label)
        
        self.request_content = QTextEdit()
        self.request_content.setPlaceholderText(
            "粘贴完整的 HTTP 请求包内容，例如:\n\n"
            "GET /page.php?id=1 HTTP/1.1\n"
            "Host: example.com\n"
            "User-Agent: Mozilla/5.0\n"
            "Cookie: session=abc123\n"
            "X-Forwarded-For: 127.0.0.1\n\n"
            "（注意：可以在头部参数后加 * 标记注入点）"
        )
        self.request_content.setMinimumHeight(120)
        self.request_content.setMaximumHeight(180)
        self.request_content.setVisible(False)
        url_card.add_widget(self.request_content)
        
        layout.addWidget(url_card)
        
        # ==================== 请求配置卡片 ====================
        request_card = CardWidget("📨 请求配置")
        
        request_grid = QGridLayout()
        request_grid.setSpacing(12)
        
        # 请求方法
        request_grid.addWidget(QLabel("请求方法:"), 0, 0)
        self.method_combo = QComboBox()
        self.method_combo.addItems(["GET", "POST"])
        self.method_combo.currentTextChanged.connect(self._on_method_changed)
        request_grid.addWidget(self.method_combo, 0, 1)
        
        # 指定参数
        self.param_check = QCheckBox("指定参数")
        self.param_check.stateChanged.connect(self._on_param_check_changed)
        request_grid.addWidget(self.param_check, 0, 2)
        
        self.param_input = QLineEdit()
        self.param_input.setPlaceholderText("如: id, name")
        self.param_input.setEnabled(False)
        request_grid.addWidget(self.param_input, 0, 3)
        
        # POST 数据
        self.post_check = QCheckBox("POST 数据")
        self.post_check.stateChanged.connect(self._on_post_check_changed)
        request_grid.addWidget(self.post_check, 1, 0)
        
        self.post_input = QLineEdit()
        self.post_input.setPlaceholderText("如: username=admin&password=pass")
        self.post_input.setEnabled(False)
        request_grid.addWidget(self.post_input, 1, 1, 1, 3)
        
        # Cookie
        self.cookie_check = QCheckBox("Cookie")
        self.cookie_check.stateChanged.connect(self._on_cookie_check_changed)
        request_grid.addWidget(self.cookie_check, 2, 0)
        
        self.cookie_input = QLineEdit()
        self.cookie_input.setPlaceholderText("如: PHPSESSID=abc123; token=xyz")
        self.cookie_input.setEnabled(False)
        request_grid.addWidget(self.cookie_input, 2, 1, 1, 3)
        
        # User-Agent
        self.ua_check = QCheckBox("User-Agent")
        self.ua_check.stateChanged.connect(self._on_ua_check_changed)
        request_grid.addWidget(self.ua_check, 3, 0)
        
        self.ua_combo = QComboBox()
        self.ua_combo.addItems([
            "随机 User-Agent",
            "Chrome (Windows)",
            "Firefox (Windows)",
            "Edge (Windows)",
            "Safari (Mac)",
            "自定义"
        ])
        self.ua_combo.setEnabled(False)
        request_grid.addWidget(self.ua_combo, 3, 1, 1, 3)
        
        request_card.add_layout(request_grid)
        layout.addWidget(request_card)
        
        # 添加弹性空间
        layout.addStretch()
    
    def _paste_url(self):
        """粘贴 URL"""
        from PyQt6.QtWidgets import QApplication
        clipboard = QApplication.clipboard()
        text = clipboard.text()
        if text:
            self.url_input.setText(text.strip())
    
    def _clear_url(self):
        """清除 URL"""
        self.url_input.clear()
    
    def _browse_file(self):
        """浏览文件"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择 URL 列表文件", "", 
            "文本文件 (*.txt);;所有文件 (*.*)"
        )
        if file_path:
            self.file_input.setText(file_path)
    
    def _on_file_check_changed(self, state):
        """文件模式切换"""
        enabled = state == Qt.CheckState.Checked.value
        self.file_input.setEnabled(enabled)
        self.browse_btn.setEnabled(enabled)
        self.url_input.setEnabled(not enabled and not self.request_check.isChecked())
        # 互斥：关闭请求包模式
        if enabled:
            self.request_check.setChecked(False)
    
    def _on_request_check_changed(self, state):
        """请求包模式切换"""
        enabled = state == Qt.CheckState.Checked.value
        self.request_input.setEnabled(enabled)
        self.request_browse_btn.setEnabled(enabled)
        self.request_content_label.setVisible(enabled)
        self.request_content.setVisible(enabled)
        self.url_input.setEnabled(not enabled and not self.file_check.isChecked())
        # 互斥：关闭文件模式
        if enabled:
            self.file_check.setChecked(False)
    
    def _browse_request_file(self):
        """浏览请求包文件"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择 HTTP 请求包文件", "", 
            "请求包文件 (*.txt *.req *.http);;所有文件 (*.*)"
        )
        if file_path:
            self.request_input.setText(file_path)
            # 读取文件内容并显示
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    self.request_content.setText(content)
            except Exception:
                pass
    
    def _on_method_changed(self, method):
        """请求方法变化"""
        if method == "POST":
            self.post_check.setChecked(True)
    
    def _on_param_check_changed(self, state):
        """参数复选框变化"""
        self.param_input.setEnabled(state == Qt.CheckState.Checked.value)
    
    def _on_post_check_changed(self, state):
        """POST 数据复选框变化"""
        self.post_input.setEnabled(state == Qt.CheckState.Checked.value)
    
    def _on_cookie_check_changed(self, state):
        """Cookie 复选框变化"""
        self.cookie_input.setEnabled(state == Qt.CheckState.Checked.value)
    
    def _on_ua_check_changed(self, state):
        """User-Agent 复选框变化"""
        self.ua_combo.setEnabled(state == Qt.CheckState.Checked.value)
    
    # ==================== 公共方法 ====================
    
    def get_target(self) -> str:
        """获取目标 URL"""
        if self.file_check.isChecked():
            return self.file_input.text().strip()
        return self.url_input.text().strip()
    
    def get_post_data(self) -> str:
        """获取 POST 数据"""
        if self.post_check.isChecked():
            return self.post_input.text().strip()
        return ""
    
    def get_cookie(self) -> str:
        """获取 Cookie"""
        if self.cookie_check.isChecked():
            return self.cookie_input.text().strip()
        return ""
    
    def get_param(self) -> str:
        """获取指定参数"""
        if self.param_check.isChecked():
            return self.param_input.text().strip()
        return ""
    
    def is_file_mode(self) -> bool:
        """是否为文件模式"""
        return self.file_check.isChecked()
    
    def is_request_mode(self) -> bool:
        """是否为请求包模式"""
        return self.request_check.isChecked()
    
    def get_request_file(self) -> str:
        """获取请求包文件路径"""
        if self.request_check.isChecked():
            return self.request_input.text().strip()
        return ""
    
    def get_request_content(self) -> str:
        """获取请求包内容"""
        if self.request_check.isChecked():
            return self.request_content.toPlainText().strip()
        return ""
    
    def use_random_agent(self) -> bool:
        """是否使用随机 User-Agent"""
        return self.ua_check.isChecked() and self.ua_combo.currentIndex() == 0
    
    def set_target(self, url: str):
        """设置目标 URL"""
        self.url_input.setText(url)
