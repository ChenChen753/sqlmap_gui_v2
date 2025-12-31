"""
扫描设置面板
用于配置扫描参数和预设模式
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QRadioButton,
    QPushButton, QComboBox, QButtonGroup, QCheckBox, QGridLayout,
    QSpinBox, QFrame, QLineEdit
)
from PyQt6.QtCore import pyqtSignal, Qt

from ..theme import COLORS
from ..widgets.card_widget import CardWidget


class ScanPanel(QWidget):
    """扫描设置面板"""
    
    # 信号
    mode_changed = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
    
    def setup_ui(self):
        """设置 UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(12)
        
        # ==================== 快速配置卡片 ====================
        mode_card = CardWidget("⚡ 快速配置")
        
        # 扫描模式选择
        mode_layout = QVBoxLayout()
        mode_layout.setSpacing(10)
        
        self.mode_group = QButtonGroup(self)
        
        modes = [
            ("quick", "🚀 快速检测", "Level 1, Risk 1 - 快速判断是否存在注入", True),
            ("standard", "🔍 标准扫描", "Level 2, Risk 2 - 平衡速度和深度，推荐日常使用", False),
            ("deep", "🔬 深度扫描", "Level 5, Risk 3 - 全面深入扫描，适合关键目标", False),
            ("aggressive", "⚔️ 激进模式", "全部技术 + 绕过 WAF，最全面但可能触发防护", False),
            ("custom", "⚙️ 自定义", "手动配置所有参数", False),
        ]
        
        for mode_id, title, desc, checked in modes:
            mode_widget = self._create_mode_option(mode_id, title, desc, checked)
            mode_layout.addWidget(mode_widget)
        
        mode_card.add_layout(mode_layout)
        layout.addWidget(mode_card)
        
        # ==================== 检测配置卡片 ====================
        detect_card = CardWidget("🎯 检测配置")
        
        detect_grid = QGridLayout()
        detect_grid.setSpacing(10)
        
        # 扫描等级
        detect_grid.addWidget(QLabel("扫描等级:"), 0, 0)
        self.level_combo = QComboBox()
        self.level_combo.addItem("0 - 默认 (不指定)", 0)
        for i in range(1, 6):
            desc = ["基础", "轻度", "中度", "深度", "完全"][i-1]
            self.level_combo.addItem(f"{i} - {desc}", i)
        self.level_combo.setToolTip("Level 0: 不指定, 1-5: 越高检测越全面但越慢")
        detect_grid.addWidget(self.level_combo, 0, 1)
        
        # 风险等级
        detect_grid.addWidget(QLabel("风险等级:"), 0, 2)
        self.risk_combo = QComboBox()
        self.risk_combo.addItem("0 - 默认 (不指定)", 0)
        for i in range(1, 4):
            desc = ["安全", "中等", "激进"][i-1]
            self.risk_combo.addItem(f"{i} - {desc}", i)
        self.risk_combo.setToolTip("Risk 0: 不指定, 1-3: 越高可能触发更多风险测试")
        detect_grid.addWidget(self.risk_combo, 0, 3)
        
        # 详细程度
        detect_grid.addWidget(QLabel("输出详细:"), 1, 0)
        self.verbose_combo = QComboBox()
        for i in range(0, 7):
            desc = ["最少", "基本", "更多", "详细", "调试", "超详", "完全"][i]
            self.verbose_combo.addItem(f"{i} - {desc}", i)
        self.verbose_combo.setCurrentIndex(1)
        detect_grid.addWidget(self.verbose_combo, 1, 1)
        
        # 字符串匹配
        self.string_check = QCheckBox("匹配字符串:")
        self.string_check.stateChanged.connect(self._on_string_check_changed)
        detect_grid.addWidget(self.string_check, 1, 2)
        
        self.string_input = QLineEdit()
        self.string_input.setPlaceholderText("True 时页面包含的字符串")
        self.string_input.setEnabled(False)
        detect_grid.addWidget(self.string_input, 1, 3)
        
        detect_card.add_layout(detect_grid)
        
        # 注入技术
        tech_layout = QVBoxLayout()
        tech_label = QLabel("注入技术:")
        tech_label.setStyleSheet(f"color: {COLORS['accent_blue']}; font-weight: bold;")
        tech_layout.addWidget(tech_label)
        
        tech_grid = QGridLayout()
        tech_grid.setSpacing(6)
        
        techniques = [
            ("B", "布尔盲注", "基于布尔的盲注"),
            ("E", "报错注入", "基于报错的注入"),
            ("U", "联合查询", "UNION 查询注入"),
            ("S", "堆叠查询", "多语句查询"),
            ("T", "时间盲注", "基于时间的盲注"),
            ("Q", "内联查询", "内联/嵌套查询"),
        ]
        
        self.tech_checks = {}
        for i, (code, name, tooltip) in enumerate(techniques):
            check = QCheckBox(f"{code} - {name}")
            check.setChecked(code in ["B", "E", "U"])  # 默认选中常用技术
            check.setToolTip(tooltip)
            self.tech_checks[code] = check
            tech_grid.addWidget(check, i // 3, i % 3)
        
        tech_layout.addLayout(tech_grid)
        detect_card.add_layout(tech_layout)
        
        layout.addWidget(detect_card)
        
        # ==================== 信息获取卡片 ====================
        info_card = CardWidget("📊 信息枚举")
        
        info_grid = QGridLayout()
        info_grid.setSpacing(8)
        
        # 第一行 - 基本信息
        self.current_db_check = QCheckBox("当前数据库 (--current-db)")
        self.current_db_check.setChecked(True)
        info_grid.addWidget(self.current_db_check, 0, 0)
        
        self.current_user_check = QCheckBox("当前用户 (--current-user)")
        info_grid.addWidget(self.current_user_check, 0, 1)
        
        self.banner_check = QCheckBox("数据库版本 (--banner)")
        info_grid.addWidget(self.banner_check, 0, 2)
        
        # 第二行 - 更多信息
        self.hostname_check = QCheckBox("主机名 (--hostname)")
        info_grid.addWidget(self.hostname_check, 1, 0)
        
        self.is_dba_check = QCheckBox("是否 DBA (--is-dba)")
        info_grid.addWidget(self.is_dba_check, 1, 1)
        
        self.users_check = QCheckBox("枚举用户 (--users)")
        info_grid.addWidget(self.users_check, 1, 2)
        
        # 第三行 - 枚举
        self.dbs_check = QCheckBox("枚举数据库 (--dbs)")
        info_grid.addWidget(self.dbs_check, 2, 0)
        
        self.tables_check = QCheckBox("枚举表 (--tables)")
        info_grid.addWidget(self.tables_check, 2, 1)
        
        self.columns_check = QCheckBox("枚举列 (--columns)")
        info_grid.addWidget(self.columns_check, 2, 2)
        
        # 第四行 - 高级枚举
        self.schema_check = QCheckBox("枚举架构 (--schema)")
        info_grid.addWidget(self.schema_check, 3, 0)
        
        self.count_check = QCheckBox("统计数量 (--count)")
        info_grid.addWidget(self.count_check, 3, 1)
        
        self.privileges_check = QCheckBox("用户权限 (--privileges)")
        info_grid.addWidget(self.privileges_check, 3, 2)
        
        # 第五行 - 密码和其他
        self.passwords_check = QCheckBox("枚举密码 (--passwords)")
        info_grid.addWidget(self.passwords_check, 4, 0)
        
        self.roles_check = QCheckBox("用户角色 (--roles)")
        info_grid.addWidget(self.roles_check, 4, 1)
        
        self.comments_check = QCheckBox("表注释 (--comments)")
        info_grid.addWidget(self.comments_check, 4, 2)
        
        info_card.add_layout(info_grid)
        layout.addWidget(info_card)
        
        # ==================== 数据提取卡片 ====================
        dump_card = CardWidget("📥 数据提取")
        
        dump_grid = QGridLayout()
        dump_grid.setSpacing(8)
        
        self.dump_check = QCheckBox("提取数据 (--dump)")
        self.dump_check.setToolTip("提取指定表的数据")
        dump_grid.addWidget(self.dump_check, 0, 0)
        
        self.dump_all_check = QCheckBox("提取全部 (--dump-all)")
        self.dump_all_check.setToolTip("提取所有表的数据")
        dump_grid.addWidget(self.dump_all_check, 0, 1)
        
        self.search_check = QCheckBox("搜索数据:")
        self.search_check.stateChanged.connect(self._on_search_check_changed)
        dump_grid.addWidget(self.search_check, 0, 2)
        
        # 搜索选项
        search_layout = QHBoxLayout()
        self.search_type_combo = QComboBox()
        self.search_type_combo.addItems(["列名 (-C)", "表名 (-T)", "数据库名 (-D)"])
        self.search_type_combo.setEnabled(False)
        search_layout.addWidget(self.search_type_combo)
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("搜索关键词")
        self.search_input.setEnabled(False)
        search_layout.addWidget(self.search_input)
        dump_grid.addLayout(search_layout, 1, 0, 1, 3)
        
        # 提取限制
        limit_layout = QHBoxLayout()
        self.limit_check = QCheckBox("限制行数:")
        self.limit_check.stateChanged.connect(self._on_limit_check_changed)
        limit_layout.addWidget(self.limit_check)
        
        self.limit_start_spin = QSpinBox()
        self.limit_start_spin.setRange(0, 999999)
        self.limit_start_spin.setPrefix("起始: ")
        self.limit_start_spin.setEnabled(False)
        limit_layout.addWidget(self.limit_start_spin)
        
        self.limit_stop_spin = QSpinBox()
        self.limit_stop_spin.setRange(1, 999999)
        self.limit_stop_spin.setValue(100)
        self.limit_stop_spin.setPrefix("结束: ")
        self.limit_stop_spin.setEnabled(False)
        limit_layout.addWidget(self.limit_stop_spin)
        
        limit_layout.addStretch()
        dump_grid.addLayout(limit_layout, 2, 0, 1, 3)
        
        dump_card.add_layout(dump_grid)
        layout.addWidget(dump_card)
        
        # 添加弹性空间
        layout.addStretch()
    
    def _create_mode_option(self, mode_id: str, title: str, desc: str, checked: bool) -> QWidget:
        """创建模式选项"""
        widget = QFrame()
        widget.setObjectName("modeOption")
        # 样式由全局主题控制
        
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(10, 6, 10, 6)
        
        radio = QRadioButton()
        radio.setChecked(checked)
        radio.setProperty("mode_id", mode_id)
        radio.toggled.connect(lambda checked, m=mode_id: self._on_mode_changed(m, checked))
        self.mode_group.addButton(radio)
        layout.addWidget(radio)
        
        text_layout = QVBoxLayout()
        text_layout.setSpacing(1)
        
        title_label = QLabel(title)
        title_label.setObjectName("modeTitle")
        title_label.setStyleSheet("font-weight: bold; font-size: 12px;")
        text_layout.addWidget(title_label)
        
        desc_label = QLabel(desc)
        desc_label.setObjectName("modeDesc")
        desc_label.setStyleSheet("font-size: 10px;")
        text_layout.addWidget(desc_label)
        
        layout.addLayout(text_layout)
        layout.addStretch()
        
        return widget
    
    def _on_mode_changed(self, mode_id: str, checked: bool):
        """模式变化"""
        if checked:
            self.mode_changed.emit(mode_id)
            self._apply_mode_preset(mode_id)
    
    def _on_string_check_changed(self, state):
        """字符串匹配变化"""
        self.string_input.setEnabled(state == Qt.CheckState.Checked.value)
    
    def _on_search_check_changed(self, state):
        """搜索变化"""
        enabled = state == Qt.CheckState.Checked.value
        self.search_type_combo.setEnabled(enabled)
        self.search_input.setEnabled(enabled)
    
    def _on_limit_check_changed(self, state):
        """限制变化"""
        enabled = state == Qt.CheckState.Checked.value
        self.limit_start_spin.setEnabled(enabled)
        self.limit_stop_spin.setEnabled(enabled)
    
    def _apply_mode_preset(self, mode_id: str):
        """应用模式预设"""
        presets = {
            "quick": {
                "level": 1, "risk": 1,
                "techs": ["B", "E", "U"],
                "current_db": True, "current_user": False,
                "banner": False, "hostname": False, "is_dba": False,
                "dbs": False, "tables": False, "columns": False,
                "dump": False
            },
            "standard": {
                "level": 2, "risk": 2,
                "techs": ["B", "E", "U", "T"],
                "current_db": True, "current_user": True,
                "banner": True, "hostname": False, "is_dba": False,
                "dbs": True, "tables": False, "columns": False,
                "dump": False
            },
            "deep": {
                "level": 5, "risk": 3,
                "techs": ["B", "E", "U", "S", "T", "Q"],
                "current_db": True, "current_user": True,
                "banner": True, "hostname": True, "is_dba": True,
                "dbs": True, "tables": True, "columns": False,
                "dump": False
            },
            "aggressive": {
                "level": 5, "risk": 3,
                "techs": ["B", "E", "U", "S", "T", "Q"],
                "current_db": True, "current_user": True,
                "banner": True, "hostname": True, "is_dba": True,
                "dbs": True, "tables": True, "columns": True,
                "dump": False
            },
        }
        
        if mode_id in presets:
            preset = presets[mode_id]
            # level 0 是索引0，level 1 是索引1，以此类推
            self.level_combo.setCurrentIndex(preset["level"])
            self.risk_combo.setCurrentIndex(preset["risk"])
            
            for code, check in self.tech_checks.items():
                check.setChecked(code in preset["techs"])
            
            self.current_db_check.setChecked(preset["current_db"])
            self.current_user_check.setChecked(preset["current_user"])
            self.banner_check.setChecked(preset["banner"])
            self.hostname_check.setChecked(preset["hostname"])
            self.is_dba_check.setChecked(preset["is_dba"])
            self.dbs_check.setChecked(preset["dbs"])
            self.tables_check.setChecked(preset["tables"])
            self.columns_check.setChecked(preset["columns"])
            self.dump_check.setChecked(preset["dump"])
    
    # ==================== 公共方法 ====================
    
    def get_level(self) -> int:
        """获取扫描等级"""
        return self.level_combo.currentData()
    
    def get_risk(self) -> int:
        """获取风险等级"""
        return self.risk_combo.currentData()
    
    def get_verbose(self) -> int:
        """获取详细程度"""
        return self.verbose_combo.currentData()
    
    def get_technique(self) -> str:
        """获取注入技术"""
        techs = [code for code, check in self.tech_checks.items() if check.isChecked()]
        return "".join(techs)
    
    def get_string_match(self) -> str:
        """获取字符串匹配"""
        if self.string_check.isChecked():
            return self.string_input.text().strip()
        return ""
    
    def get_current_db(self) -> bool:
        return self.current_db_check.isChecked()
    
    def get_current_user(self) -> bool:
        return self.current_user_check.isChecked()
    
    def get_banner(self) -> bool:
        return self.banner_check.isChecked()
    
    def get_hostname(self) -> bool:
        return self.hostname_check.isChecked()
    
    def get_is_dba(self) -> bool:
        return self.is_dba_check.isChecked()
    
    def get_users(self) -> bool:
        return self.users_check.isChecked()
    
    def get_dbs(self) -> bool:
        return self.dbs_check.isChecked()
    
    def get_tables(self) -> bool:
        return self.tables_check.isChecked()
    
    def get_columns(self) -> bool:
        return self.columns_check.isChecked()
    
    def get_schema(self) -> bool:
        return self.schema_check.isChecked()
    
    def get_count(self) -> bool:
        return self.count_check.isChecked()
    
    def get_privileges(self) -> bool:
        return self.privileges_check.isChecked()
    
    def get_passwords(self) -> bool:
        return self.passwords_check.isChecked()
    
    def get_roles(self) -> bool:
        return self.roles_check.isChecked()
    
    def get_comments(self) -> bool:
        return self.comments_check.isChecked()
    
    def get_dump(self) -> bool:
        return self.dump_check.isChecked()
    
    def get_dump_all(self) -> bool:
        return self.dump_all_check.isChecked()
    
    def get_current_mode(self) -> str:
        """获取当前模式"""
        for btn in self.mode_group.buttons():
            if btn.isChecked():
                return btn.property("mode_id")
        return "custom"
    
    def save_config(self, config) -> None:
        """保存配置"""
        config.set('Scan', 'mode', self.get_current_mode())
        config.set('Scan', 'level', str(self.level_combo.currentIndex()))
        config.set('Scan', 'risk', str(self.risk_combo.currentIndex()))
        config.set('Scan', 'verbose', str(self.verbose_combo.currentIndex()))
        config.set('Scan', 'technique', self.get_technique())
        
        # 信息枚举选项
        config.set('Scan', 'current_db', str(self.current_db_check.isChecked()))
        config.set('Scan', 'current_user', str(self.current_user_check.isChecked()))
        config.set('Scan', 'banner', str(self.banner_check.isChecked()))
        config.set('Scan', 'hostname', str(self.hostname_check.isChecked()))
        config.set('Scan', 'is_dba', str(self.is_dba_check.isChecked()))
        config.set('Scan', 'users', str(self.users_check.isChecked()))
        config.set('Scan', 'dbs', str(self.dbs_check.isChecked()))
        config.set('Scan', 'tables', str(self.tables_check.isChecked()))
        config.set('Scan', 'columns', str(self.columns_check.isChecked()))
        config.set('Scan', 'dump', str(self.dump_check.isChecked()))
    
    def load_config(self, config) -> None:
        """加载配置"""
        # 加载模式
        mode = config.get('Scan', 'mode', 'quick')
        for btn in self.mode_group.buttons():
            if btn.property("mode_id") == mode:
                btn.setChecked(True)
                break
        
        # 加载选项
        level = config.get_int('Scan', 'level', 1)
        if 0 <= level <= 5:
            self.level_combo.setCurrentIndex(level)
        
        risk = config.get_int('Scan', 'risk', 1)
        if 0 <= risk <= 3:
            self.risk_combo.setCurrentIndex(risk)
        
        verbose = config.get_int('Scan', 'verbose', 1)
        if 0 <= verbose <= 6:
            self.verbose_combo.setCurrentIndex(verbose)
        
        # 加载技术选项
        technique = config.get('Scan', 'technique', 'BEU')
        for code, check in self.tech_checks.items():
            check.setChecked(code in technique)
        
        # 加载信息枚举选项
        self.current_db_check.setChecked(config.get_bool('Scan', 'current_db', True))
        self.current_user_check.setChecked(config.get_bool('Scan', 'current_user', False))
        self.banner_check.setChecked(config.get_bool('Scan', 'banner', False))
        self.hostname_check.setChecked(config.get_bool('Scan', 'hostname', False))
        self.is_dba_check.setChecked(config.get_bool('Scan', 'is_dba', False))
        self.users_check.setChecked(config.get_bool('Scan', 'users', False))
        self.dbs_check.setChecked(config.get_bool('Scan', 'dbs', False))
        self.tables_check.setChecked(config.get_bool('Scan', 'tables', False))
        self.columns_check.setChecked(config.get_bool('Scan', 'columns', False))
        self.dump_check.setChecked(config.get_bool('Scan', 'dump', False))
