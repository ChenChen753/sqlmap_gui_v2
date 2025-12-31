"""
数据详情对话框
用于展示提取的表数据
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QTextEdit,
    QPushButton, QTableWidget, QTableWidgetItem, QHeaderView,
    QSplitter, QFrame
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont


class DataDetailDialog(QDialog):
    """数据详情对话框"""
    
    def __init__(self, table_name: str, data: list, parent=None):
        super().__init__(parent)
        self.table_name = table_name
        self.data = data
        self.setup_ui()
    
    def setup_ui(self):
        """设置 UI"""
        self.setWindowTitle(f"📊 表数据: {self.table_name}")
        self.setMinimumSize(800, 500)
        self.resize(900, 600)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)
        
        # 设置对话框样式
        self.setStyleSheet("""
            QDialog {
                background-color: #1a1a2e;
            }
            QLabel {
                color: #E0E0E0;
            }
            QPushButton {
                background-color: #2d3a4a;
                color: #FFFFFF;
                border: 1px solid #4FC3F7;
                border-radius: 4px;
                padding: 8px 16px;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #3d4a5a;
            }
        """)
        
        # 标题
        title = QLabel(f"🗄️ {self.table_name}")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #E0E0E0;")
        layout.addWidget(title)
        
        # 统计信息 - 更清晰的描述
        count_label = QLabel(f"📊 共 {len(self.data)} 条数据记录")
        count_label.setStyleSheet("color: #4FC3F7; font-size: 13px; padding: 5px 0;")
        layout.addWidget(count_label)
        
        # 解析数据并显示
        if self.data and len(self.data) > 0:
            # 尝试解析表格格式
            first_row = self.data[0] if self.data else ""
            if " | " in first_row:
                # 表格格式数据
                self._create_table_view(layout)
            else:
                # 纯文本格式
                self._create_text_view(layout)
        else:
            # 无数据
            no_data = QLabel("暂无数据")
            no_data.setAlignment(Qt.AlignmentFlag.AlignCenter)
            no_data.setStyleSheet("color: #666; font-size: 14px; padding: 50px;")
            layout.addWidget(no_data)
        
        # 按钮栏
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        copy_btn = QPushButton("📋 复制全部")
        copy_btn.clicked.connect(self._copy_all)
        btn_layout.addWidget(copy_btn)
        
        close_btn = QPushButton("关闭")
        close_btn.clicked.connect(self.close)
        btn_layout.addWidget(close_btn)
        
        layout.addLayout(btn_layout)
    
    def _create_table_view(self, layout):
        """创建表格视图"""
        # 解析列头和数据
        headers = []
        rows = []
        
        for i, row in enumerate(self.data):
            parts = [p.strip() for p in row.split(" | ")]
            if i == 0:
                # 检查是否是表头
                if all(not p.isdigit() for p in parts):
                    headers = parts
                    continue
            rows.append(parts)
        
        # 如果没有检测到表头，使用默认列名
        if not headers and rows:
            headers = [f"列 {i+1}" for i in range(len(rows[0]))]
        
        # 创建表格
        table = QTableWidget()
        table.setColumnCount(len(headers))
        table.setRowCount(len(rows))
        table.setHorizontalHeaderLabels(headers)
        
        # 隐藏行号（垂直表头）
        table.verticalHeader().setVisible(False)
        
        # 填充数据
        for i, row in enumerate(rows):
            for j, cell in enumerate(row):
                if j < len(headers):
                    item = QTableWidgetItem(cell)
                    item.setTextAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
                    table.setItem(i, j, item)
        
        # 设置样式 - 统一深色背景
        table.horizontalHeader().setStretchLastSection(True)
        table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        table.setAlternatingRowColors(True)
        table.setStyleSheet("""
            QTableWidget {
                font-family: 'Consolas', 'Courier New', 'Microsoft YaHei', monospace;
                font-size: 13px;
                background-color: #1a1a2e;
                alternate-background-color: #232340;
                gridline-color: #3a3a5a;
                border: 1px solid #3a3a5a;
                border-radius: 4px;
                color: #E0E0E0;
            }
            QTableWidget::item {
                padding: 6px 10px;
                color: #E0E0E0;
                border-bottom: 1px solid #2a2a4a;
            }
            QTableWidget::item:alternate {
                background-color: #232340;
            }
            QTableWidget::item:selected {
                background-color: #3a4a6a;
                color: #FFFFFF;
            }
            QHeaderView::section {
                background-color: #2a3a50;
                color: #4FC3F7;
                padding: 8px 10px;
                border: none;
                border-bottom: 2px solid #4FC3F7;
                font-weight: bold;
                font-size: 13px;
            }
            QTableCornerButton::section {
                background-color: #1a1a2e;
                border: none;
            }
        """)
        
        layout.addWidget(table)
        self._table = table
    
    def _create_text_view(self, layout):
        """创建文本视图"""
        text_edit = QTextEdit()
        text_edit.setReadOnly(True)
        text_edit.setFont(QFont("Consolas", 11))
        text_edit.setPlainText("\n".join(self.data))
        text_edit.setStyleSheet("""
            QTextEdit {
                background-color: #1e1e1e;
                color: #d4d4d4;
                border: 1px solid #333;
                border-radius: 4px;
            }
        """)
        layout.addWidget(text_edit)
        self._text_edit = text_edit
    
    def _copy_all(self):
        """复制全部数据"""
        from PyQt6.QtWidgets import QApplication
        text = "\n".join(self.data)
        QApplication.clipboard().setText(text)


class ColumnDataDialog(QDialog):
    """列详情对话框 - 显示表结构信息"""
    
    def __init__(self, db_name: str, table_name: str, columns: list, parent=None):
        super().__init__(parent)
        self.db_name = db_name
        self.table_name = table_name
        self.columns = columns
        self.setup_ui()
    
    def setup_ui(self):
        """设置 UI"""
        self.setWindowTitle(f"📋 表结构: {self.db_name}.{self.table_name}")
        self.setMinimumSize(600, 450)
        self.resize(700, 550)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)
        
        # 设置对话框背景色
        self.setStyleSheet("""
            QDialog {
                background-color: #1a1a2e;
            }
            QLabel {
                color: #E0E0E0;
            }
            QPushButton {
                background-color: #2d3a4a;
                color: #FFFFFF;
                border: 1px solid #4FC3F7;
                border-radius: 4px;
                padding: 8px 16px;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #3d4a5a;
            }
        """)
        
        # 标题
        title = QLabel(f"🗄️ {self.db_name}.{self.table_name}")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #E0E0E0;")
        layout.addWidget(title)
        
        # 统计信息 - 明确说明数字含义
        count_label = QLabel(f"📊 当前表共有 {len(self.columns)} 个字段（列）")
        count_label.setStyleSheet("color: #4FC3F7; font-size: 13px; padding: 5px 0;")
        layout.addWidget(count_label)
        
        # 创建表格
        table = QTableWidget()
        table.setColumnCount(2)
        table.setRowCount(len(self.columns))
        table.setHorizontalHeaderLabels(["Column", "Type"])
        
        # 隐藏行号（垂直表头）
        table.verticalHeader().setVisible(False)
        
        # 禁用选择功能，避免显示复选框
        table.setSelectionMode(QTableWidget.SelectionMode.NoSelection)
        table.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        
        # 填充数据
        for i, col in enumerate(self.columns):
            if isinstance(col, tuple):
                name_item = QTableWidgetItem(col[0])
                type_item = QTableWidgetItem(col[1])
            else:
                name_item = QTableWidgetItem(str(col))
                type_item = QTableWidgetItem("")
            
            # 设置文本对齐方式
            name_item.setTextAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
            type_item.setTextAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
            
            table.setItem(i, 0, name_item)
            table.setItem(i, 1, type_item)
        
        # 设置列宽 - 按比例分配
        table.setColumnWidth(0, 280)  # 字段名列宽度增加
        table.setColumnWidth(1, 350)  # 类型列宽度增加
        table.horizontalHeader().setStretchLastSection(True)
        table.setAlternatingRowColors(True)
        
        # 设置行高
        for i in range(table.rowCount()):
            table.setRowHeight(i, 32)
        
        # 优化表格样式 - 高对比度配色，确保清晰可读
        table.setStyleSheet("""
            QTableWidget {
                font-family: 'Consolas', 'Courier New', 'Microsoft YaHei', monospace;
                font-size: 14px;
                background-color: #0d0d0d;
                alternate-background-color: #1a1a1a;
                gridline-color: #444;
                border: 1px solid #555;
                border-radius: 4px;
                selection-background-color: transparent;
            }
            QTableWidget::item {
                padding: 8px 12px;
                color: #FFFFFF;
                border-bottom: 1px solid #333;
            }
            QTableWidget::item:alternate {
                background-color: #1a1a1a;
                color: #FFFFFF;
            }
            QHeaderView::section {
                background-color: #2a3a50;
                color: #FFFFFF;
                padding: 10px 12px;
                border: none;
                border-bottom: 2px solid #4FC3F7;
                font-weight: bold;
                font-size: 14px;
            }
        """)
        
        layout.addWidget(table)
        self._table = table
        
        # 按钮栏
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        copy_btn = QPushButton("📋 复制全部")
        copy_btn.clicked.connect(self._copy_all)
        btn_layout.addWidget(copy_btn)
        
        close_btn = QPushButton("关闭")
        close_btn.clicked.connect(self.close)
        btn_layout.addWidget(close_btn)
        
        layout.addLayout(btn_layout)
    
    def _copy_all(self):
        """复制全部数据"""
        from PyQt6.QtWidgets import QApplication
        lines = []
        for col in self.columns:
            if isinstance(col, tuple):
                lines.append(f"{col[0]}\t{col[1]}")
            else:
                lines.append(str(col))
        QApplication.clipboard().setText("\n".join(lines))
