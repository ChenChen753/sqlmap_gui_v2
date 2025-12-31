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
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)
        
        # 标题
        title = QLabel(f"🗄️ {self.table_name}")
        title.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(title)
        
        # 统计信息
        count_label = QLabel(f"共 {len(self.data)} 条记录")
        count_label.setStyleSheet("color: #888; font-size: 12px;")
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
        
        # 填充数据
        for i, row in enumerate(rows):
            for j, cell in enumerate(row):
                if j < len(headers):
                    item = QTableWidgetItem(cell)
                    table.setItem(i, j, item)
        
        # 设置样式
        table.horizontalHeader().setStretchLastSection(True)
        table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        table.setAlternatingRowColors(True)
        table.setStyleSheet("""
            QTableWidget {
                font-family: 'Consolas', 'Courier New', monospace;
                font-size: 12px;
                gridline-color: #444;
            }
            QTableWidget::item {
                padding: 5px;
            }
            QHeaderView::section {
                background-color: #2d2d2d;
                padding: 5px;
                border: 1px solid #444;
                font-weight: bold;
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
    """列详情对话框"""
    
    def __init__(self, db_name: str, table_name: str, columns: list, parent=None):
        super().__init__(parent)
        self.db_name = db_name
        self.table_name = table_name
        self.columns = columns
        self.setup_ui()
    
    def setup_ui(self):
        """设置 UI"""
        self.setWindowTitle(f"📋 表结构: {self.db_name}.{self.table_name}")
        self.setMinimumSize(500, 400)
        self.resize(600, 500)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)
        
        # 标题
        title = QLabel(f"🗄️ {self.db_name}.{self.table_name}")
        title.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(title)
        
        # 统计信息
        count_label = QLabel(f"共 {len(self.columns)} 个字段")
        count_label.setStyleSheet("color: #888; font-size: 12px;")
        layout.addWidget(count_label)
        
        # 创建表格
        table = QTableWidget()
        table.setColumnCount(2)
        table.setRowCount(len(self.columns))
        table.setHorizontalHeaderLabels(["字段名", "类型"])
        
        # 隐藏行号
        table.verticalHeader().setVisible(False)
        
        for i, col in enumerate(self.columns):
            if isinstance(col, tuple):
                table.setItem(i, 0, QTableWidgetItem(col[0]))
                table.setItem(i, 1, QTableWidgetItem(col[1]))
            else:
                table.setItem(i, 0, QTableWidgetItem(str(col)))
                table.setItem(i, 1, QTableWidgetItem(""))
        
        # 设置列宽
        table.setColumnWidth(0, 200)
        table.horizontalHeader().setStretchLastSection(True)
        table.setAlternatingRowColors(True)
        table.setStyleSheet("""
            QTableWidget {
                font-family: 'Consolas', 'Courier New', monospace;
                font-size: 12px;
            }
            QTableWidget::item {
                padding: 5px;
            }
            QHeaderView::section {
                background-color: #2d2d2d;
                padding: 5px;
                border: 1px solid #444;
                font-weight: bold;
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
