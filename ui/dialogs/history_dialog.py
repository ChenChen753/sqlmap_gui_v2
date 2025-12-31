"""
扫描历史对话框
显示历史扫描记录列表和详细信息
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QTableWidget,
    QPushButton, QTableWidgetItem, QHeaderView, QTextEdit,
    QSplitter, QGroupBox, QWidget, QAbstractItemView, QMessageBox
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from core.history_manager import HistoryManager


class HistoryDialog(QDialog):
    """扫描历史对话框"""
    
    # 信号：选择历史记录并加载到主界面
    load_target = pyqtSignal(str)
    
    def __init__(self, history_manager: HistoryManager, parent=None):
        super().__init__(parent)
        self.history = history_manager
        self.setWindowTitle("📜 扫描历史")
        self.setMinimumSize(900, 600)
        self.setup_ui()
        self.load_history()
    
    def setup_ui(self):
        """设置 UI"""
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        
        # 主分割器
        splitter = QSplitter(Qt.Orientation.Vertical)
        
        # ==================== 历史列表 ====================
        list_widget = QWidget()
        list_layout = QVBoxLayout(list_widget)
        list_layout.setContentsMargins(0, 0, 0, 0)
        
        list_label = QLabel("📋 扫描记录")
        list_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        list_layout.addWidget(list_label)
        
        self.history_table = QTableWidget()
        self.history_table.setColumnCount(6)
        self.history_table.setHorizontalHeaderLabels([
            "ID", "目标 URL", "扫描模式", "开始时间", "状态", "发现漏洞"
        ])
        self.history_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.history_table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.history_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        # 隐藏垂直表头（行号），避免对齐问题
        self.history_table.verticalHeader().setVisible(False)
        # 设置列宽
        self.history_table.setColumnWidth(0, 50)   # ID
        self.history_table.setColumnWidth(2, 80)   # 扫描模式
        self.history_table.setColumnWidth(3, 140)  # 开始时间
        self.history_table.setColumnWidth(4, 80)   # 状态
        self.history_table.setColumnWidth(5, 80)   # 发现漏洞
        self.history_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.history_table.itemSelectionChanged.connect(self._on_selection_changed)
        list_layout.addWidget(self.history_table)
        
        splitter.addWidget(list_widget)
        
        # ==================== 详细信息 ====================
        detail_widget = QWidget()
        detail_layout = QVBoxLayout(detail_widget)
        detail_layout.setContentsMargins(0, 0, 0, 0)
        
        detail_label = QLabel("📝 详细信息")
        detail_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        detail_layout.addWidget(detail_label)
        
        self.detail_text = QTextEdit()
        self.detail_text.setReadOnly(True)
        self.detail_text.setPlaceholderText("选择一条记录查看详细信息...")
        self.detail_text.setStyleSheet("""
            QTextEdit {
                font-family: 'Consolas', 'Courier New', monospace;
                font-size: 12px;
            }
        """)
        detail_layout.addWidget(self.detail_text)
        
        splitter.addWidget(detail_widget)
        
        # 设置分割比例
        splitter.setSizes([300, 200])
        layout.addWidget(splitter)
        
        # ==================== 按钮区 ====================
        btn_layout = QHBoxLayout()
        
        # 刷新按钮
        refresh_btn = QPushButton("🔄 刷新")
        refresh_btn.clicked.connect(self.load_history)
        btn_layout.addWidget(refresh_btn)
        
        # 加载目标按钮
        self.load_btn = QPushButton("📎 加载到扫描")
        self.load_btn.setEnabled(False)
        self.load_btn.clicked.connect(self._load_target)
        btn_layout.addWidget(self.load_btn)
        
        # 删除按钮
        self.delete_btn = QPushButton("🗑️ 删除记录")
        self.delete_btn.setProperty("class", "danger")
        self.delete_btn.setEnabled(False)
        self.delete_btn.clicked.connect(self._delete_record)
        btn_layout.addWidget(self.delete_btn)
        
        btn_layout.addStretch()
        
        # 关闭按钮
        close_btn = QPushButton("关闭")
        close_btn.clicked.connect(self.close)
        btn_layout.addWidget(close_btn)
        
        layout.addLayout(btn_layout)
    
    def load_history(self):
        """加载历史记录"""
        self.history_table.setRowCount(0)
        records = self.history.get_history(limit=100)
        
        for record in records:
            row = self.history_table.rowCount()
            self.history_table.insertRow(row)
            
            # ID
            id_item = QTableWidgetItem(str(record.get('id', '')))
            id_item.setData(Qt.ItemDataRole.UserRole, record)
            self.history_table.setItem(row, 0, id_item)
            
            # 目标 URL（截断显示）
            target = record.get('target', '')
            if len(target) > 60:
                target = target[:60] + "..."
            self.history_table.setItem(row, 1, QTableWidgetItem(target))
            
            # 扫描模式
            self.history_table.setItem(row, 2, QTableWidgetItem(record.get('scan_mode', '')))
            
            # 开始时间
            start_time = record.get('start_time', '')
            if start_time:
                # 简化显示
                start_time = start_time.replace('T', ' ')[:19]
            self.history_table.setItem(row, 3, QTableWidgetItem(start_time))
            
            # 状态
            status = record.get('status', '')
            status_item = QTableWidgetItem(status)
            if status == 'completed':
                status_item.setForeground(QColor('#9ece6a'))
                status_item.setText('✅ 完成')
            elif status == 'running':
                status_item.setForeground(QColor('#e0af68'))
                status_item.setText('🔄 运行中')
            else:
                status_item.setForeground(QColor('#f7768e'))
                status_item.setText('❌ 失败')
            self.history_table.setItem(row, 4, status_item)
            
            # 发现漏洞
            has_vuln = record.get('has_vuln', False)
            vuln_item = QTableWidgetItem('是' if has_vuln else '否')
            if has_vuln:
                vuln_item.setForeground(QColor('#f7768e'))
                vuln_item.setText('⚠️ 是')
            self.history_table.setItem(row, 5, vuln_item)
        
        # 调整列宽
        self.history_table.resizeColumnsToContents()
        self.history_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
    
    def _on_selection_changed(self):
        """选择变化"""
        selected = self.history_table.selectedItems()
        if selected:
            self.load_btn.setEnabled(True)
            self.delete_btn.setEnabled(True)
            
            # 获取记录数据
            row = selected[0].row()
            record = self.history_table.item(row, 0).data(Qt.ItemDataRole.UserRole)
            self._show_detail(record)
        else:
            self.load_btn.setEnabled(False)
            self.delete_btn.setEnabled(False)
            self.detail_text.clear()
    
    def _show_detail(self, record: dict):
        """显示详细信息"""
        detail = []
        detail.append("=" * 60)
        detail.append("📋 扫描记录详情")
        detail.append("=" * 60)
        detail.append("")
        
        detail.append(f"🔗 目标 URL: {record.get('target', 'N/A')}")
        detail.append(f"📌 扫描模式: {record.get('scan_mode', 'N/A')}")
        detail.append(f"⏰ 开始时间: {record.get('start_time', 'N/A')}")
        detail.append(f"⏱️ 结束时间: {record.get('end_time', 'N/A')}")
        detail.append(f"⌛ 持续时间: {record.get('duration', 0)} 秒")
        detail.append("")
        
        detail.append("-" * 60)
        detail.append("🔍 扫描结果")
        detail.append("-" * 60)
        
        has_vuln = record.get('has_vuln', False)
        if has_vuln:
            detail.append("⚠️ 发现 SQL 注入漏洞！")
            detail.append(f"   漏洞数量: {record.get('vuln_count', 0)}")
        else:
            detail.append("✅ 未发现漏洞")
        
        if record.get('dbms'):
            detail.append(f"🗄️ 数据库类型: {record.get('dbms')}")
        
        if record.get('current_db'):
            detail.append(f"📁 当前数据库: {record.get('current_db')}")
        
        detail.append("")
        detail.append("-" * 60)
        detail.append("💻 执行命令")
        detail.append("-" * 60)
        detail.append(record.get('command', 'N/A'))
        
        if record.get('result_summary'):
            detail.append("")
            detail.append("-" * 60)
            detail.append("📝 结果摘要")
            detail.append("-" * 60)
            detail.append(record.get('result_summary'))
        
        self.detail_text.setPlainText("\n".join(detail))
    
    def _load_target(self):
        """加载目标到扫描"""
        selected = self.history_table.selectedItems()
        if selected:
            row = selected[0].row()
            record = self.history_table.item(row, 0).data(Qt.ItemDataRole.UserRole)
            target = record.get('target', '')
            if target:
                self.load_target.emit(target)
                self.close()
    
    def _delete_record(self):
        """删除记录"""
        selected = self.history_table.selectedItems()
        if not selected:
            return
        
        reply = QMessageBox.question(
            self, "确认删除", "确定要删除这条扫描记录吗？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            row = selected[0].row()
            record = self.history_table.item(row, 0).data(Qt.ItemDataRole.UserRole)
            record_id = record.get('id')
            
            if record_id and self.history.delete_scan(record_id):
                self.history_table.removeRow(row)
                self.detail_text.clear()
