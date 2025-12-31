"""
卡片组件
现代化卡片式容器 - 使用全局样式
"""

from PyQt6.QtWidgets import QFrame, QVBoxLayout, QLabel, QHBoxLayout, QWidget
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont


class CardWidget(QFrame):
    """现代化卡片组件"""
    
    def __init__(self, title: str = "", parent=None):
        """
        初始化卡片组件
        
        参数:
            title: 卡片标题
            parent: 父组件
        """
        super().__init__(parent)
        self.setup_ui(title)
    
    def setup_ui(self, title: str):
        """设置 UI"""
        # 使用 QSS 类名而非硬编码颜色
        self.setObjectName("CardWidget")
        self.setProperty("class", "card")
        
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(16, 16, 16, 16)
        self.main_layout.setSpacing(12)
        
        # 标题（如果有）
        if title:
            self.title_label = QLabel(title)
            self.title_label.setObjectName("cardTitle")
            self.title_label.setProperty("class", "card-title")
            self.main_layout.addWidget(self.title_label)
        
        # 内容区域
        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.content_layout.setSpacing(8)
        self.main_layout.addWidget(self.content_widget)
    
    def add_widget(self, widget: QWidget):
        """添加子组件"""
        self.content_layout.addWidget(widget)
    
    def add_layout(self, layout):
        """添加子布局"""
        self.content_layout.addLayout(layout)
    
    def add_stretch(self):
        """添加弹性空间"""
        self.content_layout.addStretch()
    
    def set_highlight(self, enabled: bool = True):
        """设置高亮状态"""
        self.setProperty("highlight", enabled)
        self.style().unpolish(self)
        self.style().polish(self)


class StatCard(QFrame):
    """统计卡片组件"""
    
    def __init__(self, icon: str, title: str, value: str = "0", parent=None):
        """
        初始化统计卡片
        
        参数:
            icon: 图标（emoji）
            title: 标题
            value: 数值
            parent: 父组件
        """
        super().__init__(parent)
        self.setup_ui(icon, title, value)
    
    def setup_ui(self, icon: str, title: str, value: str):
        """设置 UI"""
        self.setObjectName("StatCard")
        self.setProperty("class", "stat-card")
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 10, 12, 10)
        
        # 图标
        icon_label = QLabel(icon)
        icon_label.setStyleSheet("font-size: 24px; background: transparent;")
        layout.addWidget(icon_label)
        
        # 文本区域
        text_layout = QVBoxLayout()
        text_layout.setSpacing(2)
        
        # 标题
        self.title_label = QLabel(title)
        self.title_label.setObjectName("statTitle")
        text_layout.addWidget(self.title_label)
        
        # 数值
        self.value_label = QLabel(value)
        self.value_label.setObjectName("statValue")
        text_layout.addWidget(self.value_label)
        
        layout.addLayout(text_layout)
        layout.addStretch()
    
    def set_value(self, value: str):
        """设置数值"""
        self.value_label.setText(value)
    
    def set_color(self, color: str):
        """设置数值颜色"""
        self.value_label.setStyleSheet(f"color: {color}; font-size: 18px; font-weight: bold;")
