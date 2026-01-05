"""
Tamper 脚本选择对话框
用于选择绕过 WAF 的 Tamper 脚本
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTreeWidget, QTreeWidgetItem,
    QPushButton, QCheckBox, QLabel, QLineEdit, QGroupBox, QScrollArea,
    QWidget, QGridLayout, QDialogButtonBox, QFrame
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from ..theme import COLORS


# 完整的 Tamper 脚本列表（按功能分类）
TAMPER_SCRIPTS = {
    "编码绕过": [
        ("base64encode", "Base64 编码 payload"),
        ("charencode", "URL 编码字符"),
        ("chardoubleencode", "双重 URL 编码"),
        ("charunicodeencode", "Unicode 编码"),
        ("charunicodeescape", "Unicode 转义"),
        ("htmlencode", "HTML 编码"),
        ("overlongutf8", "长 UTF-8 编码"),
        ("overlongutf8more", "更多长 UTF-8"),
        ("percentage", "百分号编码"),
        ("decentities", "十进制 HTML 实体"),
        ("hexentities", "十六进制 HTML 实体"),
    ],
    "空格替换": [
        ("space2comment", "空格转注释 /**/"),
        ("space2dash", "空格转 -- 加换行"),
        ("space2hash", "空格转 # 加换行"),
        ("space2plus", "空格转加号"),
        ("space2morecomment", "空格转多个注释"),
        ("space2morehash", "空格转多个 #"),
        ("space2mssqlblank", "MSSQL 空白字符替换"),
        ("space2mssqlhash", "MSSQL 空格转 #"),
        ("space2mysqlblank", "MySQL 空白字符替换"),
        ("space2mysqldash", "MySQL 空格转 --"),
        ("space2randomblank", "空格转随机空白"),
        ("multiplespaces", "多空格替换"),
    ],
    "关键字处理": [
        ("randomcase", "随机大小写"),
        ("lowercase", "转小写"),
        ("uppercase", "转大写"),
        ("versionedkeywords", "MySQL 版本注释包裹"),
        ("versionedmorekeywords", "更多版本注释包裹"),
        ("halfversionedmorekeywords", "半版本注释包裹"),
        ("randomcomments", "随机注释插入"),
    ],
    "函数替换": [
        ("between", "用 BETWEEN 替换 >"),
        ("greatest", "用 GREATEST 替换 >"),
        ("least", "用 LEAST 替换 <"),
        ("equaltolike", "用 LIKE 替换 ="),
        ("equaltorlike", "用 RLIKE 替换 ="),
        ("concat2concatws", "CONCAT 转 CONCAT_WS"),
        ("ifnull2casewhenisnull", "IFNULL 转 CASE WHEN"),
        ("ifnull2ifisnull", "IFNULL 转 IF(ISNULL())"),
        ("if2case", "IF 转 CASE"),
        ("substring2leftright", "SUBSTRING 转 LEFT/RIGHT"),
        ("ord2ascii", "ORD 转 ASCII"),
        ("hex2char", "十六进制转 CHAR"),
        ("plus2concat", "加号转 CONCAT"),
        ("plus2fnconcat", "加号转 fn CONCAT"),
    ],
    "WAF 绕过": [
        ("apostrophemask", "单引号转 UTF-8 全角"),
        ("apostrophenullencode", "单引号加 %00"),
        ("appendnullbyte", "末尾加 %00"),
        ("bluecoat", "BlueCoat WAF 绕过"),
        ("modsecurityversioned", "ModSecurity 版本绕过"),
        ("modsecurityzeroversioned", "ModSecurity 零版本绕过"),
        ("varnish", "Varnish 缓存绕过"),
        ("xforwardedfor", "添加 X-Forwarded-For"),
        ("luanginx", "Nginx Lua WAF 绕过"),
        ("luanginxmore", "更多 Nginx Lua 绕过"),
    ],
    "UNION 注入": [
        ("0eunion", "0e 开头的 UNION"),
        ("dunion", "D 开头的 UNION"),
        ("misunion", "MIS 开头的 UNION"),
        ("unionalltounion", "UNION ALL 转 UNION"),
    ],
    "其他技巧": [
        ("binary", "二进制后缀"),
        ("commalesslimit", "无逗号 LIMIT"),
        ("commalessmid", "无逗号 MID"),
        ("commentbeforeparentheses", "括号前加注释"),
        ("escapequotes", "转义引号"),
        ("informationschemacomment", "information_schema 加注释"),
        ("schemasplit", "Schema 分割"),
        ("scientific", "科学计数法"),
        ("sleep2getlock", "SLEEP 转 GET_LOCK"),
        ("sp_password", "sp_password 绕过日志"),
        ("symboliclogical", "符号逻辑运算符"),
        ("unmagicquotes", "绕过 magic_quotes"),
    ],
}


class TamperSelectionDialog(QDialog):
    """Tamper 脚本选择对话框"""
    
    def __init__(self, parent=None, selected_scripts: list = None):
        super().__init__(parent)
        self.selected_scripts = selected_scripts or []
        self.script_checkboxes = {}  # 存储所有脚本复选框
        self.category_checkboxes = {}  # 存储分类复选框
        self.setup_ui()
        self.apply_styles()
        self._restore_selection()
    
    def setup_ui(self):
        """设置 UI"""
        self.setWindowTitle("🛡️ Tamper 绕过脚本选择")
        self.setMinimumSize(700, 600)
        self.resize(750, 650)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(16, 16, 16, 16)
        
        # 标题和说明
        title_label = QLabel("选择需要的 Tamper 绕过脚本")
        title_label.setFont(QFont("Microsoft YaHei UI", 12, QFont.Weight.Bold))
        layout.addWidget(title_label)
        
        desc_label = QLabel("勾选脚本以启用，取消勾选以禁用。可以选择多个脚本组合使用。")
        desc_label.setStyleSheet(f"color: {COLORS['text_secondary']};")
        layout.addWidget(desc_label)
        
        # 全选/取消全选按钮行
        control_layout = QHBoxLayout()
        
        self.select_all_btn = QPushButton("✅ 全选")
        self.select_all_btn.setFixedWidth(100)
        self.select_all_btn.clicked.connect(self._toggle_select_all)
        control_layout.addWidget(self.select_all_btn)
        
        self.clear_all_btn = QPushButton("❌ 清空选择")
        self.clear_all_btn.setFixedWidth(100)
        self.clear_all_btn.clicked.connect(self._clear_all)
        control_layout.addWidget(self.clear_all_btn)
        
        control_layout.addStretch()
        
        # 已选数量显示
        self.selected_count_label = QLabel("已选: 0 个脚本")
        self.selected_count_label.setStyleSheet(f"color: {COLORS['accent_blue']}; font-weight: bold;")
        control_layout.addWidget(self.selected_count_label)
        
        layout.addLayout(control_layout)
        
        # 分隔线
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setStyleSheet(f"background-color: {COLORS['border']};")
        layout.addWidget(line)
        
        # 可滚动的脚本区域
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)
        scroll_layout.setSpacing(12)
        scroll_layout.setContentsMargins(4, 4, 4, 4)
        
        # 为每个分类创建分组
        for category, scripts in TAMPER_SCRIPTS.items():
            category_group = self._create_category_group(category, scripts)
            scroll_layout.addWidget(category_group)
        
        scroll_layout.addStretch()
        scroll_area.setWidget(scroll_widget)
        layout.addWidget(scroll_area, 1)
        
        # 底部按钮
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.cancel_btn = QPushButton("取消")
        self.cancel_btn.setFixedWidth(80)
        self.cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_btn)
        
        self.confirm_btn = QPushButton("确定")
        self.confirm_btn.setFixedWidth(80)
        self.confirm_btn.setDefault(True)
        self.confirm_btn.clicked.connect(self.accept)
        button_layout.addWidget(self.confirm_btn)
        
        layout.addLayout(button_layout)
    
    def _create_category_group(self, category: str, scripts: list) -> QGroupBox:
        """创建分类分组"""
        group = QGroupBox()
        group_layout = QVBoxLayout(group)
        group_layout.setSpacing(6)
        group_layout.setContentsMargins(10, 8, 10, 8)
        
        # 分类标题行（带复选框用于全选该分类）
        header_layout = QHBoxLayout()
        
        category_checkbox = QCheckBox(f"📂 {category}")
        category_checkbox.setFont(QFont("Microsoft YaHei UI", 10, QFont.Weight.Bold))
        category_checkbox.setTristate(True)
        category_checkbox.stateChanged.connect(
            lambda state, cat=category: self._on_category_checkbox_changed(cat, state)
        )
        self.category_checkboxes[category] = category_checkbox
        header_layout.addWidget(category_checkbox)
        
        header_layout.addStretch()
        
        # 显示该分类的脚本数量
        count_label = QLabel(f"共 {len(scripts)} 个脚本")
        count_label.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 11px;")
        header_layout.addWidget(count_label)
        
        group_layout.addLayout(header_layout)
        
        # 脚本列表（使用网格布局，每行2个）
        scripts_layout = QGridLayout()
        scripts_layout.setSpacing(4)
        scripts_layout.setContentsMargins(20, 4, 4, 4)
        
        for i, (name, desc) in enumerate(scripts):
            row = i // 2
            col = i % 2
            
            checkbox = QCheckBox(f"{name} - {desc}")
            checkbox.setProperty("script_name", name)
            checkbox.stateChanged.connect(self._on_script_checkbox_changed)
            
            self.script_checkboxes[name] = checkbox
            scripts_layout.addWidget(checkbox, row, col)
        
        group_layout.addLayout(scripts_layout)
        
        return group
    
    def _on_category_checkbox_changed(self, category: str, state: int):
        """分类复选框状态变化"""
        # 当用户点击产生"部分选中"状态时，将其转换为"全选"操作
        if state == Qt.CheckState.PartiallyChecked.value:
            # 强制设置为选中状态
            category_cb = self.category_checkboxes.get(category)
            if category_cb:
                category_cb.blockSignals(True)
                category_cb.setCheckState(Qt.CheckState.Checked)
                category_cb.blockSignals(False)
            checked = True
        else:
            checked = state == Qt.CheckState.Checked.value
        
        # 更新该分类下所有脚本的选中状态
        for name, _ in TAMPER_SCRIPTS[category]:
            if name in self.script_checkboxes:
                self.script_checkboxes[name].blockSignals(True)
                self.script_checkboxes[name].setChecked(checked)
                self.script_checkboxes[name].blockSignals(False)
        
        self._update_selected_count()
    
    def _on_script_checkbox_changed(self):
        """脚本复选框状态变化"""
        self._update_category_checkbox_states()
        self._update_selected_count()
    
    def _update_category_checkbox_states(self):
        """更新分类复选框的状态"""
        for category, scripts in TAMPER_SCRIPTS.items():
            checked_count = 0
            total_count = len(scripts)
            
            for name, _ in scripts:
                if name in self.script_checkboxes and self.script_checkboxes[name].isChecked():
                    checked_count += 1
            
            category_cb = self.category_checkboxes.get(category)
            if category_cb:
                category_cb.blockSignals(True)
                if checked_count == 0:
                    category_cb.setCheckState(Qt.CheckState.Unchecked)
                elif checked_count == total_count:
                    category_cb.setCheckState(Qt.CheckState.Checked)
                else:
                    category_cb.setCheckState(Qt.CheckState.PartiallyChecked)
                category_cb.blockSignals(False)
    
    def _update_selected_count(self):
        """更新已选数量显示"""
        count = sum(1 for cb in self.script_checkboxes.values() if cb.isChecked())
        self.selected_count_label.setText(f"已选: {count} 个脚本")
        
        # 更新全选按钮状态
        total = len(self.script_checkboxes)
        if count == total:
            self.select_all_btn.setText("❎ 取消全选")
        else:
            self.select_all_btn.setText("✅ 全选")
    
    def _toggle_select_all(self):
        """切换全选/取消全选"""
        # 检查当前是否全部选中
        all_checked = all(cb.isChecked() for cb in self.script_checkboxes.values())
        
        # 切换所有脚本的选中状态
        for checkbox in self.script_checkboxes.values():
            checkbox.blockSignals(True)
            checkbox.setChecked(not all_checked)
            checkbox.blockSignals(False)
        
        self._update_category_checkbox_states()
        self._update_selected_count()
    
    def _clear_all(self):
        """清空所有选择"""
        for checkbox in self.script_checkboxes.values():
            checkbox.blockSignals(True)
            checkbox.setChecked(False)
            checkbox.blockSignals(False)
        
        self._update_category_checkbox_states()
        self._update_selected_count()
    
    def _restore_selection(self):
        """恢复之前的选择"""
        for name in self.selected_scripts:
            if name in self.script_checkboxes:
                self.script_checkboxes[name].setChecked(True)
        
        self._update_category_checkbox_states()
        self._update_selected_count()
    
    def get_selected_scripts(self) -> list:
        """获取所有选中的脚本名称"""
        return [name for name, cb in self.script_checkboxes.items() if cb.isChecked()]
    
    def apply_styles(self):
        """应用样式"""
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {COLORS['bg_primary']};
            }}
            
            QLabel {{
                color: {COLORS['text_primary']};
            }}
            
            QGroupBox {{
                background-color: {COLORS['bg_secondary']};
                border: 1px solid {COLORS['border']};
                border-radius: 6px;
                margin-top: 0px;
                padding-top: 8px;
            }}
            
            QCheckBox {{
                color: {COLORS['text_primary']};
                spacing: 6px;
            }}
            
            QCheckBox::indicator {{
                width: 16px;
                height: 16px;
                border: 2px solid {COLORS['border']};
                border-radius: 3px;
                background-color: {COLORS['bg_secondary']};
            }}
            
            QCheckBox::indicator:checked {{
                background-color: {COLORS['accent_blue']};
                border-color: {COLORS['accent_blue']};
            }}
            
            QCheckBox::indicator:indeterminate {{
                background-color: {COLORS['accent_blue']};
                border-color: {COLORS['accent_blue']};
            }}
            
            QCheckBox:hover {{
                color: {COLORS['accent_blue']};
            }}
            
            QPushButton {{
                background-color: {COLORS['bg_tertiary']};
                color: {COLORS['text_primary']};
                border: 1px solid {COLORS['border']};
                border-radius: 4px;
                padding: 6px 12px;
                min-height: 24px;
            }}
            
            QPushButton:hover {{
                background-color: {COLORS['bg_hover']};
                border-color: {COLORS['accent_blue']};
            }}
            
            QPushButton:pressed {{
                background-color: {COLORS['bg_secondary']};
            }}
            
            QPushButton#confirm_btn {{
                background-color: {COLORS['accent_blue']};
                border-color: {COLORS['accent_blue']};
            }}
            
            QScrollArea {{
                background-color: transparent;
                border: none;
            }}
            
            QScrollBar:vertical {{
                background: {COLORS['bg_secondary']};
                width: 10px;
                border-radius: 5px;
            }}
            
            QScrollBar::handle:vertical {{
                background: {COLORS['border']};
                border-radius: 5px;
                min-height: 30px;
            }}
            
            QScrollBar::handle:vertical:hover {{
                background: {COLORS['accent_blue']};
            }}
            
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                height: 0px;
            }}
        """)
        
        # 设置确定按钮的特殊样式
        self.confirm_btn.setObjectName("confirm_btn")
