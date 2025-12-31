"""
日志面板
用于显示扫描日志和命令输出 - 使用全局样式
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTextEdit,
    QPushButton, QCheckBox, QLineEdit, QFileDialog
)
from PyQt6.QtCore import pyqtSignal, Qt, QTimer
from PyQt6.QtGui import QTextCursor, QColor, QTextCharFormat


class LogPanel(QWidget):
    """日志面板"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._auto_scroll = True
        self._log_buffer = []
        self._update_timer = QTimer()
        self._update_timer.timeout.connect(self._flush_buffer)
        self._update_timer.setInterval(100)  # 100ms 刷新一次
        
        self.setup_ui()
    
    def setup_ui(self):
        """设置 UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        # ==================== 工具栏 ====================
        toolbar = QHBoxLayout()
        toolbar.setSpacing(8)
        
        # 搜索框
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 搜索日志...")
        self.search_input.setMinimumWidth(150)
        self.search_input.setMaximumWidth(250)
        self.search_input.textChanged.connect(self._on_search)
        toolbar.addWidget(self.search_input)
        
        toolbar.addStretch()
        
        # 过滤选项
        self.filter_info = QCheckBox("INFO")
        self.filter_info.setChecked(True)
        toolbar.addWidget(self.filter_info)
        
        self.filter_warning = QCheckBox("WARNING")
        self.filter_warning.setChecked(True)
        toolbar.addWidget(self.filter_warning)
        
        self.filter_error = QCheckBox("ERROR")
        self.filter_error.setChecked(True)
        toolbar.addWidget(self.filter_error)
        
        self.filter_debug = QCheckBox("DEBUG")
        toolbar.addWidget(self.filter_debug)
        
        # 自动滚动
        self.auto_scroll_check = QCheckBox("自动滚动")
        self.auto_scroll_check.setChecked(True)
        self.auto_scroll_check.stateChanged.connect(self._on_auto_scroll_changed)
        toolbar.addWidget(self.auto_scroll_check)
        
        layout.addLayout(toolbar)
        
        # ==================== 日志显示区 ====================
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setObjectName("logTextEdit")
        # 只设置字体，颜色由全局样式控制
        self.log_text.setStyleSheet("""
            QTextEdit#logTextEdit {
                font-family: 'Consolas', 'Courier New', monospace;
                font-size: 12px;
            }
        """)
        layout.addWidget(self.log_text)
        
        # ==================== 底部按钮 ====================
        bottom_layout = QHBoxLayout()
        bottom_layout.setSpacing(8)
        
        # 日志统计
        self.stats_label = QLabel("共 0 条日志")
        self.stats_label.setObjectName("statsLabel")
        bottom_layout.addWidget(self.stats_label)
        
        bottom_layout.addStretch()
        
        # 清空按钮
        clear_btn = QPushButton("🗑️ 清空")
        clear_btn.setProperty("class", "secondary")
        clear_btn.clicked.connect(self.clear)
        clear_btn.setMinimumWidth(100)
        bottom_layout.addWidget(clear_btn)
        
        # 保存按钮
        save_btn = QPushButton("💾 保存")
        save_btn.setProperty("class", "secondary")
        save_btn.clicked.connect(self._save_log)
        save_btn.setMinimumWidth(100)
        bottom_layout.addWidget(save_btn)
        
        # 复制按钮
        copy_btn = QPushButton("📋 复制")
        copy_btn.setProperty("class", "secondary")
        copy_btn.clicked.connect(self._copy_log)
        copy_btn.setMinimumWidth(100)
        bottom_layout.addWidget(copy_btn)
        
        layout.addLayout(bottom_layout)
    
    def _on_auto_scroll_changed(self, state):
        """自动滚动状态变化"""
        self._auto_scroll = state == Qt.CheckState.Checked.value
    
    def _on_search(self, text):
        """搜索日志"""
        if not text:
            # 清除高亮
            cursor = self.log_text.textCursor()
            cursor.select(QTextCursor.SelectionType.Document)
            format = QTextCharFormat()
            format.setBackground(QColor("transparent"))
            cursor.mergeCharFormat(format)
            return
        
        # 高亮搜索结果
        self._highlight_text(text)
    
    def _highlight_text(self, text: str):
        """高亮文本"""
        document = self.log_text.document()
        cursor = QTextCursor(document)
        
        # 清除之前的高亮
        cursor.select(QTextCursor.SelectionType.Document)
        format = QTextCharFormat()
        format.setBackground(QColor("transparent"))
        cursor.mergeCharFormat(format)
        
        # 高亮匹配的文本
        highlight_format = QTextCharFormat()
        highlight_format.setBackground(QColor("#7aa2f7"))
        
        cursor = QTextCursor(document)
        while not cursor.isNull():
            cursor = document.find(text, cursor)
            if not cursor.isNull():
                cursor.mergeCharFormat(highlight_format)
    
    def _flush_buffer(self):
        """刷新缓冲区"""
        if not self._log_buffer:
            return
        
        # 合并所有缓冲的日志
        text = "".join(self._log_buffer)
        self._log_buffer.clear()
        
        # 添加到日志框
        self.log_text.moveCursor(QTextCursor.MoveOperation.End)
        self.log_text.insertPlainText(text)
        
        # 自动滚动
        if self._auto_scroll:
            self.log_text.moveCursor(QTextCursor.MoveOperation.End)
            self.log_text.ensureCursorVisible()
        
        # 更新统计
        self._update_stats()
    
    def _update_stats(self):
        """更新统计信息"""
        line_count = self.log_text.document().lineCount()
        self.stats_label.setText(f"共 {line_count} 条日志")
    
    def _save_log(self):
        """保存日志"""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "保存日志", "sqlmap_log.txt",
            "文本文件 (*.txt);;所有文件 (*.*)"
        )
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(self.log_text.toPlainText())
            except Exception as e:
                pass
    
    def _copy_log(self):
        """复制日志到剪贴板"""
        from PyQt6.QtWidgets import QApplication
        clipboard = QApplication.clipboard()
        clipboard.setText(self.log_text.toPlainText())
    
    # ==================== 公共方法 ====================
    
    def append(self, text: str):
        """追加日志（带缓冲）"""
        self._log_buffer.append(text)
        if not self._update_timer.isActive():
            self._update_timer.start()
    
    def append_line(self, text: str, level: str = "INFO"):
        """追加一行日志"""
        formatted = f"[{level}] {text}\n"
        self.append(formatted)
    
    def append_colored(self, text: str, color: str):
        """追加带颜色的文本"""
        self.append(text)
    
    def clear(self):
        """清空日志"""
        self._log_buffer.clear()
        self.log_text.clear()
        self._update_stats()
    
    def get_log(self) -> str:
        """获取日志内容"""
        return self.log_text.toPlainText()
    
    def start_logging(self):
        """开始记录日志"""
        self._update_timer.start()
    
    def stop_logging(self):
        """停止记录日志"""
        self._flush_buffer()
        self._update_timer.stop()
