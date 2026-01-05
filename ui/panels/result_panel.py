"""
结果展示面板
用于展示扫描结果和数据库结构
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTextEdit,
    QPushButton, QTreeWidget, QTreeWidgetItem, QSplitter,
    QTabWidget, QHeaderView, QMenu, QFrame, QMessageBox
)
from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtGui import QColor, QAction

from ..theme import COLORS
from ..widgets.card_widget import CardWidget, StatCard
from ..dialogs.data_detail_dialog import DataDetailDialog, ColumnDataDialog


class ResultPanel(QWidget):
    """结果展示面板"""
    
    # 信号
    db_selected = pyqtSignal(str)

    table_selected = pyqtSignal(str, str)
    dump_requested = pyqtSignal(str)  # 请求提取数据信号 (db_name)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        # 存储提取的数据
        self._extracted_data = {}  # {table_name: [rows]}
        self._columns_data = {}    # {(db, table): [(col_name, col_type)]}
        self.setup_ui()
    
    def setup_ui(self):
        """设置 UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(15)
        
        # ==================== 统计信息 ====================
        stats_layout = QHBoxLayout()
        stats_layout.setSpacing(10)
        
        self.vuln_stat = StatCard("🔴", "发现漏洞", "0")
        stats_layout.addWidget(self.vuln_stat)
        
        self.db_stat = StatCard("🗄️", "数据库", "0")
        stats_layout.addWidget(self.db_stat)
        
        self.table_stat = StatCard("📋", "数据表", "0")
        stats_layout.addWidget(self.table_stat)
        
        self.time_stat = StatCard("⏱️", "耗时", "00:00")
        stats_layout.addWidget(self.time_stat)
        
        layout.addLayout(stats_layout)
        
        # ==================== 结果标签页 ====================
        self.result_tabs = QTabWidget()
        
        # 注入信息标签页
        self.injection_tab = QWidget()
        self._setup_injection_tab()
        self.result_tabs.addTab(self.injection_tab, "🎯 注入信息")
        
        # 数据库结构标签页
        self.db_tab = QWidget()
        self._setup_db_tab()
        self.result_tabs.addTab(self.db_tab, "🗄️ 数据库结构")
        
        # 数据内容标签页
        self.data_tab = QWidget()
        self._setup_data_tab()
        self.result_tabs.addTab(self.data_tab, "📊 数据内容")
        
        layout.addWidget(self.result_tabs)
    
    def _setup_injection_tab(self):
        """设置注入信息标签页"""
        layout = QVBoxLayout(self.injection_tab)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # 注入点信息
        self.injection_text = QTextEdit()
        self.injection_text.setReadOnly(True)
        self.injection_text.setPlaceholderText("扫描完成后将显示注入点信息...")
        self.injection_text.setStyleSheet("""
            QTextEdit {
                font-family: 'Consolas', 'Courier New', monospace;
                font-size: 12px;
            }
        """)
        layout.addWidget(self.injection_text)
    
    def _setup_db_tab(self):
        """设置数据库结构标签页"""
        layout = QHBoxLayout(self.db_tab)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # 创建分割器
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # 数据库树
        db_widget = QWidget()
        db_layout = QVBoxLayout(db_widget)
        db_layout.setContentsMargins(0, 0, 0, 0)
        
        db_label = QLabel("📁 数据库")
        db_label.setObjectName("sectionLabel")
        db_label.setStyleSheet("font-weight: bold;")
        db_layout.addWidget(db_label)
        
        self.db_tree = QTreeWidget()
        self.db_tree.setHeaderHidden(True)
        self.db_tree.itemClicked.connect(self._on_db_clicked)
        self.db_tree.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.db_tree.customContextMenuRequested.connect(self._show_db_context_menu)
        db_layout.addWidget(self.db_tree)
        
        splitter.addWidget(db_widget)
        
        # 表树
        table_widget = QWidget()
        table_layout = QVBoxLayout(table_widget)
        table_layout.setContentsMargins(0, 0, 0, 0)
        
        table_label = QLabel("📋 数据表")
        table_label.setObjectName("sectionLabel")
        table_label.setStyleSheet("font-weight: bold;")
        table_layout.addWidget(table_label)
        
        self.table_tree = QTreeWidget()
        self.table_tree.setHeaderHidden(True)
        self.table_tree.itemClicked.connect(self._on_table_clicked)
        self.table_tree.itemDoubleClicked.connect(self._on_table_double_clicked)
        table_layout.addWidget(self.table_tree)
        
        splitter.addWidget(table_widget)
        
        # 列树
        column_widget = QWidget()
        column_layout = QVBoxLayout(column_widget)
        column_layout.setContentsMargins(0, 0, 0, 0)
        
        column_label = QLabel("📝 字段")
        column_label.setObjectName("sectionLabel")
        column_label.setStyleSheet("font-weight: bold;")
        column_layout.addWidget(column_label)
        
        self.column_tree = QTreeWidget()
        self.column_tree.setHeaderLabels(["字段名", "类型"])
        self.column_tree.header().setStretchLastSection(True)
        self.column_tree.itemDoubleClicked.connect(self._on_column_double_clicked)
        column_layout.addWidget(self.column_tree)
        
        splitter.addWidget(column_widget)
        
        layout.addWidget(splitter)
    
    def _setup_data_tab(self):
        """设置数据内容标签页"""
        layout = QVBoxLayout(self.data_tab)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # 数据显示区
        self.data_text = QTextEdit()
        self.data_text.setReadOnly(True)
        self.data_text.setPlaceholderText("提取的数据将显示在这里...")
        self.data_text.setStyleSheet("""
            QTextEdit {
                font-family: 'Consolas', 'Courier New', monospace;
                font-size: 12px;
            }
        """)
        layout.addWidget(self.data_text)
        
        # 导出按钮
        export_layout = QHBoxLayout()
        export_layout.addStretch()
        
        export_csv_btn = QPushButton("📥 导出 CSV")
        export_csv_btn.setProperty("class", "secondary")
        export_csv_btn.setMinimumWidth(110)
        export_csv_btn.clicked.connect(self._export_csv)
        export_layout.addWidget(export_csv_btn)
        
        export_json_btn = QPushButton("📥 导出 JSON")
        export_json_btn.setProperty("class", "secondary")
        export_json_btn.setMinimumWidth(120)
        export_json_btn.clicked.connect(self._export_json)
        export_layout.addWidget(export_json_btn)
        
        layout.addLayout(export_layout)
    
    def _on_db_clicked(self, item, column):
        """数据库点击 - 更新表列表显示该数据库的表"""
        db_name = item.text(0).strip()  # 确保没有多余空格
        self._update_tables_for_db(db_name)
        self.db_selected.emit(db_name)
    
    def _update_tables_for_db(self, db_name: str):
        """更新表列表，只显示指定数据库的表"""
        self.table_tree.clear()
        self.column_tree.clear()
        
        if not hasattr(self, '_tables_data') or not self._tables_data:
            # 没有表数据，显示提示
            hint_item = QTreeWidgetItem(["(暂无表数据)"])
            self.table_tree.addTopLevelItem(hint_item)
            return
        
        # 查找该数据库的表 - 先尝试精确匹配
        tables = self._tables_data.get(db_name, [])
        
        # 如果精确匹配找不到，尝试遍历查找
        if not tables:
            for key, value in self._tables_data.items():
                if key.lower() == db_name.lower() or db_name.lower() in key.lower():
                    tables = value
                    break
        
        # 如果还是找不到，且只有一个数据库，直接使用它
        if not tables and len(self._tables_data) == 1:
            tables = list(self._tables_data.values())[0]
        
        if tables:
            for table in tables:
                item = QTreeWidgetItem([table])
                self.table_tree.addTopLevelItem(item)
            # 添加字段提示
            hint_item = QTreeWidgetItem(["(点击左侧表名查看字段)", ""])
            self.column_tree.addTopLevelItem(hint_item)
        else:
            # 没有表，显示提示
            hint_item = QTreeWidgetItem(["(该数据库暂无表数据)"])
            self.table_tree.addTopLevelItem(hint_item)
    
    def _on_table_clicked(self, item, column):
        """表点击 - 更新字段列表显示该表的字段"""
        full_table_name = item.text(0)  # 格式可能是: db.table 或 table 或其他
        
        # 提取数据库名和表名
        if "." in full_table_name:
            # 尝试从完整名称中提取
            parts = full_table_name.rsplit(".", 1)
            db_name = parts[0]
            table_name = parts[1]
        else:
            table_name = full_table_name
            # 尝试从数据库树获取数据库名
            db_item = self.db_tree.currentItem()
            db_name = db_item.text(0) if db_item else ""
        
        # 查找并显示该表的字段
        self._update_columns_for_table(db_name, table_name, full_table_name)
        
        # 发送信号
        self.table_selected.emit(db_name, table_name)
    
    def _update_columns_for_table(self, db_name: str, table_name: str, full_table_name: str):
        """更新字段列表，只显示指定表的字段"""
        self.column_tree.clear()
        
        if not self._columns_data:
            return
        
        # 尝试多种匹配方式查找列数据
        matched_columns = None
        
        for (db, tbl), cols in self._columns_data.items():
            # 精确匹配
            if db == db_name and tbl == table_name:
                matched_columns = cols
                break
            # 表名匹配
            if tbl == table_name:
                matched_columns = cols
                break
            # 完整名称匹配
            if f"{db}.{tbl}" == full_table_name:
                matched_columns = cols
                break
            # 表名在完整名称中
            if tbl in full_table_name:
                matched_columns = cols
                break
        
        if matched_columns:
            for col in matched_columns:
                if isinstance(col, tuple):
                    item = QTreeWidgetItem([col[0], col[1]])
                else:
                    item = QTreeWidgetItem([str(col), ""])
                self.column_tree.addTopLevelItem(item)
    
    def _on_table_double_clicked(self, item, column):
        """表双击 - 显示表数据"""
        full_table_name = item.text(0)  # 格式: db.table 或 table
        
        # 提取表名
        if "." in full_table_name:
            db_name, table_name = full_table_name.rsplit(".", 1)
        else:
            table_name = full_table_name
            db_name = ""
        
        # 调试：打印可用的数据键
        available_keys = list(self._extracted_data.keys()) if self._extracted_data else []
        
        # 查找表数据 - 使用多种匹配方式
        table_data = self._find_table_data(full_table_name, db_name, table_name)
        
        if table_data:
            # 显示数据详情对话框
            dialog = DataDetailDialog(full_table_name, table_data, self)
            dialog.exec()
        else:
            # 检查是否有列信息
            column_data = None
            matched_db = db_name
            for (db, tbl), cols in self._columns_data.items():
                # 更灵活的匹配
                if tbl == table_name or f"{db}.{tbl}" == full_table_name or tbl in full_table_name:
                    column_data = cols
                    matched_db = db
                    break
            
            if column_data:
                # 显示列详情
                dialog = ColumnDataDialog(matched_db, table_name, column_data, self)
                dialog.exec()
            else:
                # 显示更详细的调试信息
                debug_info = f"表 '{full_table_name}' 暂无提取数据。\n\n"
                if available_keys:
                    debug_info += f"已提取的数据表：\n"
                    for k in available_keys[:10]:  # 最多显示10个
                        debug_info += f"  • {k}\n"
                    if len(available_keys) > 10:
                        debug_info += f"  ... 共 {len(available_keys)} 个表\n"
                else:
                    debug_info += "当前没有已提取的数据。\n请使用 --dump 选项提取数据。"
                
                QMessageBox.information(self, "提示", debug_info)
    
    def _find_table_data(self, full_table_name: str, db_name: str, table_name: str):
        """查找表数据 - 使用多种匹配方式"""
        if not self._extracted_data:
            return None
        
        # 1. 精确匹配
        possible_keys = [
            full_table_name,
            table_name,
            f"{db_name}.{table_name}" if db_name else table_name,
            f"`{db_name}`.`{table_name}`" if db_name else f"`{table_name}`",
        ]
        
        for key in possible_keys:
            if key in self._extracted_data:
                return self._extracted_data[key]
        
        # 2. 遍历所有键，查找包含表名的
        for key, data in self._extracted_data.items():
            # 提取键中的纯表名（去掉数据库前缀和引号）
            clean_key = key.replace('`', '').replace("'", '').replace('"', '')
            
            # 如果键包含点号，提取表名部分
            if '.' in clean_key:
                key_table = clean_key.split('.')[-1]
            else:
                key_table = clean_key
            
            # 匹配表名
            if key_table == table_name:
                return data
            
            # 检查键是否以表名结尾
            if key.endswith(table_name) or key.endswith(f".{table_name}"):
                return data
            
            # 检查键中是否包含表名
            if table_name in clean_key:
                return data
        
        # 3. 如果都没找到，尝试模糊匹配（忽略大小写）
        table_name_lower = table_name.lower()
        for key, data in self._extracted_data.items():
            if table_name_lower in key.lower():
                return data
        
        return None
    
    def _on_column_double_clicked(self, item, column):
        """字段双击 - 显示该字段所属表的数据"""
        col_name = item.text(0)
        col_type = item.text(1)
        
        # 尝试从当前选中的表获取数据
        table_item = self.table_tree.currentItem()
        if table_item:
            full_table_name = table_item.text(0)
            
            # 提取表名
            if "." in full_table_name:
                db_name, table_name = full_table_name.rsplit(".", 1)
            else:
                table_name = full_table_name
                db_name = ""
            
            # 使用统一的查找方法
            table_data = self._find_table_data(full_table_name, db_name, table_name)
            
            if table_data:
                # 显示数据详情对话框
                dialog = DataDetailDialog(
                    f"{full_table_name} (字段: {col_name})", 
                    table_data, 
                    self
                )
                dialog.exec()
                return
        
        # 没有提取的数据，提示用户
        QMessageBox.information(
            self, "提示", 
            f"字段 '{col_name}' ({col_type}) 暂无提取数据。\n\n"
            "请先使用 --dump 选项提取该表的数据。"
        )
    
    def _show_db_context_menu(self, pos):
        """显示数据库右键菜单"""
        item = self.db_tree.itemAt(pos)
        if not item:
            return
        
        menu = QMenu(self)
        
        get_tables_action = QAction("获取表列表", self)
        get_tables_action.triggered.connect(lambda: self._request_tables(item.text(0)))
        menu.addAction(get_tables_action)
        
        dump_action = QAction("提取全部数据", self)
        dump_action.triggered.connect(lambda: self._request_dump(item.text(0)))
        menu.addAction(dump_action)
        
        menu.exec(self.db_tree.mapToGlobal(pos))
    
    def _request_tables(self, db_name):
        """请求获取表列表"""
        self.db_selected.emit(db_name)
    
    def _request_dump(self, db_name):
        """请求提取数据"""
        self.dump_requested.emit(db_name)
    
    def _export_csv(self):
        """导出 CSV"""
        if not self._extracted_data:
            QMessageBox.warning(self, "警告", "当前没有已提取的数据可导出。")
            return
            
        from PyQt6.QtWidgets import QFileDialog
        
        # 选择保存目录
        dir_path = QFileDialog.getExistingDirectory(self, "选择保存 CSV 的目录")
        if not dir_path:
            return
            
        try:
            import csv
            import os
            
            count = 0
            for table_name, rows in self._extracted_data.items():
                # 清理表名作为文件名
                safe_name = "".join([c for c in table_name if c.isalpha() or c.isdigit() or c in (' ', '-', '_', '.')]).strip()
                if not safe_name:
                    safe_name = "unknown_table"
                
                file_path = os.path.join(dir_path, f"{safe_name}.csv")
                
                with open(file_path, 'w', newline='', encoding='utf-8-sig') as f:
                    writer = csv.writer(f)
                    
                    # 尝试解析每一行
                    for row in rows:
                        if isinstance(row, str) and " | " in row:
                            parts = [p.strip() for p in row.split(" | ")]
                            writer.writerow(parts)
                        else:
                            writer.writerow([row])
                count += 1
                
            QMessageBox.information(self, "成功", f"成功导出 {count} 个表的 CSV 文件。")
            
        except Exception as e:
            QMessageBox.critical(self, "错误", f"导出失败: {str(e)}")
    
    def _export_json(self):
        """导出 JSON"""
        if not self._extracted_data:
            QMessageBox.warning(self, "警告", "当前没有已提取的数据可导出。")
            return
            
        from PyQt6.QtWidgets import QFileDialog
        import json
        
        # 选择保存文件
        file_path, _ = QFileDialog.getSaveFileName(
            self, "保存 JSON", "sqlmap_data.json", "JSON Files (*.json)"
        )
        if not file_path:
            return
            
        try:
            # 构造更结构化的数据
            export_data = {}
            for table_name, rows in self._extracted_data.items():
                # 尝试解析
                parsed_rows = []
                headers = []
                
                for i, row in enumerate(rows):
                    if isinstance(row, str) and " | " in row:
                        parts = [p.strip() for p in row.split(" | ")]
                        
                        # 尝试识别第一行为表头
                        if i == 0 and all(not p.isdigit() for p in parts):
                            headers = parts
                            continue
                            
                        if headers:
                            # 如果有表头，转为字典
                            row_dict = {}
                            for j, val in enumerate(parts):
                                if j < len(headers):
                                    row_dict[headers[j]] = val
                                else:
                                    row_dict[f"col_{j}"] = val
                            parsed_rows.append(row_dict)
                        else:
                            # 没表头，转为列表
                            parsed_rows.append(parts)
                    else:
                        parsed_rows.append(row)
                
                export_data[table_name] = parsed_rows
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, ensure_ascii=False, indent=2)
                
            QMessageBox.information(self, "成功", "数据已成功导出为 JSON。")
            
        except Exception as e:
            QMessageBox.critical(self, "错误", f"导出失败: {str(e)}")
    
    # ==================== 公共方法 ====================
    
    def update_stats(self, vuln_count: int = 0, db_count: int = 0, 
                     table_count: int = 0, elapsed_time: str = "00:00"):
        """更新统计信息"""
        self.vuln_stat.set_value(str(vuln_count))
        if vuln_count > 0:
            self.vuln_stat.set_color(COLORS['accent_red'])
        
        self.db_stat.set_value(str(db_count))
        self.table_stat.set_value(str(table_count))
        self.time_stat.set_value(elapsed_time)
    
    def set_injection_info(self, info: str):
        """设置注入信息"""
        self.injection_text.setPlainText(info)
    
    def append_injection_info(self, info: str):
        """追加注入信息"""
        self.injection_text.append(info)
    
    def add_database(self, db_name: str):
        """添加数据库"""
        item = QTreeWidgetItem([db_name])
        icon = self._get_icon("database")
        if icon:
            item.setIcon(0, icon)
        self.db_tree.addTopLevelItem(item)
    
    def set_databases(self, databases: list):
        """设置数据库列表"""
        self.db_tree.clear()
        for db in databases:
            self.add_database(db)
    
    def set_databases_with_tables(self, databases: list, tables_dict: dict):
        """设置数据库列表并存储表数据，实现点击联动"""
        self.db_tree.clear()
        
        # 确保存储的表数据键名没有多余空格
        cleaned_tables_data = {}
        if tables_dict:
            for k, v in tables_dict.items():
                cleaned_tables_data[k.strip()] = v
        
        # 如果新数据为空但旧数据存在，保留旧数据（防止意外覆盖）
        if not cleaned_tables_data and hasattr(self, '_tables_data') and self._tables_data:
            pass  # 保留旧数据
        else:
            self._tables_data = cleaned_tables_data
            
        # 确保 databases 列表也经过处理
        cleaned_databases = [db.strip() for db in databases]
        
        for db in cleaned_databases:
            self.add_database(db)
        
        # 如果有数据库，默认选中第一个并显示其表
        if cleaned_databases:
            first_db = cleaned_databases[0]
            # 选中第一个数据库
            first_item = self.db_tree.topLevelItem(0)
            if first_item:
                self.db_tree.setCurrentItem(first_item)
            # 显示第一个数据库的表
            self._update_tables_for_db(first_db)
            
            # 如果有多个数据库，显示提示
            if len(cleaned_databases) > 1:
                # 在表列表顶部添加提示
                hint_item = QTreeWidgetItem([f"💡 当前显示 {first_db} 的表，点击左侧数据库切换"])
                self.table_tree.insertTopLevelItem(0, hint_item)
    
    def set_tables(self, tables: list):
        """设置表列表"""
        self.table_tree.clear()
        for table in tables:
            item = QTreeWidgetItem([table])
            self.table_tree.addTopLevelItem(item)
    
    def add_table_if_not_exists(self, table_name: str, db_name: str = None):
        """添加表到 _tables_data（如果不存在）
        
        只更新内部数据存储，不直接修改 UI。
        UI 只通过 _update_tables_for_db 来更新，确保显示正确的数据库表。
        """
        table_name = table_name.strip()
        
        # 确定数据库名
        if db_name is None:
            # 尝试获取当前选中的数据库
            current_db_item = self.db_tree.currentItem()
            if current_db_item:
                db_name = current_db_item.text(0).strip()
            else:
                # 如果没有选中，尝试获取第一个数据库
                first_item = self.db_tree.topLevelItem(0)
                if first_item:
                    db_name = first_item.text(0).strip()
                else:
                    db_name = "default"
        
        # 确保 _tables_data 存在
        if not hasattr(self, '_tables_data'):
            self._tables_data = {}
        
        # 更新 _tables_data
        if db_name not in self._tables_data:
            self._tables_data[db_name] = []
        if table_name not in self._tables_data[db_name]:
            self._tables_data[db_name].append(table_name)
            
            # 只有当表属于当前选中的数据库时，才添加到 UI
            current_db_item = self.db_tree.currentItem()
            current_db = current_db_item.text(0).strip() if current_db_item else ""
            if db_name == current_db:
                # 检查 UI 中是否已存在
                exists_in_ui = False
                for i in range(self.table_tree.topLevelItemCount()):
                    existing_item = self.table_tree.topLevelItem(i)
                    if existing_item and existing_item.text(0) == table_name:
                        exists_in_ui = True
                        break
                if not exists_in_ui:
                    item = QTreeWidgetItem([table_name])
                    self.table_tree.addTopLevelItem(item)
    
    def set_columns(self, columns: list):
        """设置列列表"""
        self.column_tree.clear()
        for col in columns:
            if isinstance(col, tuple):
                item = QTreeWidgetItem([col[0], col[1]])
            else:
                item = QTreeWidgetItem([col, ""])
            self.column_tree.addTopLevelItem(item)
    
    def set_columns_with_data(self, columns: list, columns_dict: dict):
        """设置列列表并存储列数据（不立即显示，等待点击表时显示）"""
        self.column_tree.clear()
        self._columns_data = columns_dict
        # 不再一次性显示所有列，而是等待用户点击表时显示该表的字段
        # 添加提示项
        hint_item = QTreeWidgetItem(["(点击左侧表名查看字段)", ""])
        self.column_tree.addTopLevelItem(hint_item)
    
    def set_data(self, data: str):
        """设置数据内容"""
        self.data_text.setPlainText(data)
    
    def set_extracted_data(self, data_dict: dict):
        """存储提取的数据"""
        self._extracted_data = data_dict
    
    def clear_all(self):
        """清空所有内容"""
        self.injection_text.clear()
        self.db_tree.clear()
        self.table_tree.clear()
        self.column_tree.clear()
        self.data_text.clear()
        self._extracted_data = {}
        self._columns_data = {}
        self.update_stats()
    
    def _get_icon(self, icon_type: str):
        """获取图标"""
        from PyQt6.QtWidgets import QStyle, QApplication
        
        style = QApplication.style()
        if icon_type == "database":
            return style.standardIcon(QStyle.StandardPixmap.SP_DirIcon)
        elif icon_type == "table":
            return style.standardIcon(QStyle.StandardPixmap.SP_FileIcon)
        elif icon_type == "column":
            return style.standardIcon(QStyle.StandardPixmap.SP_ArrowRight)
        
        return None
