"""
开关组件
现代化开关按钮
"""

from PyQt6.QtWidgets import QWidget, QHBoxLayout, QLabel
from PyQt6.QtCore import Qt, pyqtSignal, QPropertyAnimation, QEasingCurve, QRect
from PyQt6.QtGui import QPainter, QColor, QPainterPath

from ..theme import COLORS


class ToggleSwitch(QWidget):
    """现代化开关组件"""
    
    # 信号
    toggled = pyqtSignal(bool)
    
    def __init__(self, parent=None, checked: bool = False):
        """
        初始化开关组件
        
        参数:
            parent: 父组件
            checked: 初始状态
        """
        super().__init__(parent)
        self._checked = checked
        self._position = 22 if checked else 2
        
        self.setFixedSize(50, 26)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        
        # 动画
        self._animation = QPropertyAnimation(self, b"position")
        self._animation.setDuration(200)
        self._animation.setEasingCurve(QEasingCurve.Type.OutCubic)
    
    @property
    def position(self):
        return self._position
    
    @position.setter
    def position(self, value):
        self._position = value
        self.update()
    
    def isChecked(self) -> bool:
        """获取选中状态"""
        return self._checked
    
    def setChecked(self, checked: bool):
        """设置选中状态"""
        if self._checked != checked:
            self._checked = checked
            self._animate()
            self.toggled.emit(checked)
    
    def toggle(self):
        """切换状态"""
        self.setChecked(not self._checked)
    
    def _animate(self):
        """执行动画"""
        self._animation.setStartValue(self._position)
        self._animation.setEndValue(22 if self._checked else 2)
        self._animation.start()
    
    def mousePressEvent(self, event):
        """鼠标点击事件"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.toggle()
    
    def paintEvent(self, event):
        """绘制组件"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # 背景
        if self._checked:
            bg_color = QColor(COLORS['accent_blue'])
        else:
            bg_color = QColor(COLORS['border'])
        
        painter.setBrush(bg_color)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(0, 0, 50, 26, 13, 13)
        
        # 滑块
        painter.setBrush(QColor("#ffffff"))
        painter.drawEllipse(int(self._position), 2, 22, 22)


class LabeledToggle(QWidget):
    """带标签的开关组件"""
    
    toggled = pyqtSignal(bool)
    
    def __init__(self, label: str, parent=None, checked: bool = False):
        """
        初始化带标签的开关
        
        参数:
            label: 标签文本
            parent: 父组件
            checked: 初始状态
        """
        super().__init__(parent)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)
        
        # 标签
        self.label = QLabel(label)
        self.label.setStyleSheet(f"color: {COLORS['text_primary']};")
        layout.addWidget(self.label)
        
        layout.addStretch()
        
        # 开关
        self.toggle = ToggleSwitch(checked=checked)
        self.toggle.toggled.connect(self.toggled.emit)
        layout.addWidget(self.toggle)
    
    def isChecked(self) -> bool:
        """获取选中状态"""
        return self.toggle.isChecked()
    
    def setChecked(self, checked: bool):
        """设置选中状态"""
        self.toggle.setChecked(checked)
