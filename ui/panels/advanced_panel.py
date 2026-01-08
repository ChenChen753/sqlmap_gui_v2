"""
高级选项面板
用于配置高级参数和绕过设置
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QComboBox, QCheckBox, QGridLayout, QSpinBox,
    QGroupBox, QScrollArea, QFrame
)
from PyQt6.QtCore import pyqtSignal, Qt

from ..theme import COLORS
from ..widgets.card_widget import CardWidget


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


class AdvancedPanel(QWidget):
    """高级选项面板"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
    
    def setup_ui(self):
        """设置 UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(12)
        
        # ==================== 性能配置卡片 ====================
        perf_card = CardWidget("⚡ 性能配置")
        
        perf_grid = QGridLayout()
        perf_grid.setSpacing(10)
        
        # 线程数
        perf_grid.addWidget(QLabel("并发线程:"), 0, 0)
        self.threads_spin = QSpinBox()
        self.threads_spin.setRange(1, 10)
        self.threads_spin.setValue(3)
        self.threads_spin.setToolTip("同时进行的请求数量 (1-10)")
        perf_grid.addWidget(self.threads_spin, 0, 1)
        
        # 超时时间
        perf_grid.addWidget(QLabel("超时时间:"), 0, 2)
        self.timeout_spin = QSpinBox()
        self.timeout_spin.setRange(5, 300)
        self.timeout_spin.setValue(30)
        self.timeout_spin.setSuffix(" 秒")
        perf_grid.addWidget(self.timeout_spin, 0, 3)
        
        # 重试次数
        perf_grid.addWidget(QLabel("重试次数:"), 1, 0)
        self.retries_spin = QSpinBox()
        self.retries_spin.setRange(0, 10)
        self.retries_spin.setValue(3)
        perf_grid.addWidget(self.retries_spin, 1, 1)
        
        # 请求延迟
        perf_grid.addWidget(QLabel("请求延迟:"), 1, 2)
        self.delay_spin = QSpinBox()
        self.delay_spin.setRange(0, 30)
        self.delay_spin.setValue(0)
        self.delay_spin.setSuffix(" 秒")
        perf_grid.addWidget(self.delay_spin, 1, 3)
        
        perf_card.add_layout(perf_grid)
        layout.addWidget(perf_card)
        
        # ==================== 通用选项卡片 ====================
        general_card = CardWidget("🔧 通用选项")
        
        general_grid = QGridLayout()
        general_grid.setSpacing(8)
        
        self.batch_check = QCheckBox("非交互模式 (--batch)")
        self.batch_check.setChecked(True)
        self.batch_check.setToolTip("自动使用默认选项，不需要用户交互")
        general_grid.addWidget(self.batch_check, 0, 0)
        
        self.flush_check = QCheckBox("刷新会话 (--flush-session)")
        self.flush_check.setToolTip("刷新目标的会话文件，重新开始扫描")
        general_grid.addWidget(self.flush_check, 0, 1)
        
        self.fresh_check = QCheckBox("禁用缓存 (--fresh-queries)")
        self.fresh_check.setChecked(True)
        self.fresh_check.setToolTip("忽略已缓存的查询结果")
        general_grid.addWidget(self.fresh_check, 0, 2)
        
        self.forms_check = QCheckBox("解析表单 (--forms)")
        self.forms_check.setToolTip("自动解析页面中的表单")
        general_grid.addWidget(self.forms_check, 1, 0)
        
        self.crawl_check = QCheckBox("爬取页面 (--crawl)")
        self.crawl_check.setToolTip("从起始 URL 爬取网站")
        general_grid.addWidget(self.crawl_check, 1, 1)
        
        self.smart_check = QCheckBox("智能模式 (--smart)")
        self.smart_check.setToolTip("只对启发式判断为注入的参数进行测试")
        general_grid.addWidget(self.smart_check, 1, 2)
        
        self.null_connection_check = QCheckBox("空连接 (--null-connection)")
        self.null_connection_check.setToolTip("使用空连接检测")
        general_grid.addWidget(self.null_connection_check, 2, 0)
        
        self.text_only_check = QCheckBox("仅文本 (--text-only)")
        self.text_only_check.setToolTip("仅比较文本内容")
        general_grid.addWidget(self.text_only_check, 2, 1)
        
        self.no_cast_check = QCheckBox("禁用转换 (--no-cast)")
        self.no_cast_check.setToolTip("禁用数据类型转换")
        general_grid.addWidget(self.no_cast_check, 2, 2)
        
        general_card.add_layout(general_grid)
        layout.addWidget(general_card)
        
        # ==================== 注入载荷设置卡片 ====================
        payload_card = CardWidget("🪄 注入载荷设置")
        
        payload_grid = QGridLayout()
        payload_grid.setSpacing(10)
        
        payload_grid.addWidget(QLabel("注入前缀 (--prefix):"), 0, 0)
        self.prefix_input = QLineEdit()
        self.prefix_input.setPlaceholderText("例如: '")
        self.prefix_input.setToolTip("闭合前面的查询语句")
        payload_grid.addWidget(self.prefix_input, 0, 1)
        
        payload_grid.addWidget(QLabel("注入后缀 (--suffix):"), 0, 2)
        self.suffix_input = QLineEdit()
        self.suffix_input.setPlaceholderText("例如: -- -")
        self.suffix_input.setToolTip("注释后面的查询语句")
        payload_grid.addWidget(self.suffix_input, 0, 3)
        
        payload_card.add_layout(payload_grid)
        layout.addWidget(payload_card)
        
        # ==================== Tamper 脚本卡片 ====================
        tamper_card = CardWidget("🛡️ Tamper 绕过脚本")
        
        tamper_layout = QVBoxLayout()
        tamper_layout.setSpacing(8)
        
        # 脚本选择按钮行
        select_layout = QHBoxLayout()
        
        self.tamper_select_btn = QPushButton("🛡️ 选择绕过脚本...")
        self.tamper_select_btn.setMinimumWidth(150)
        self.tamper_select_btn.clicked.connect(self._open_tamper_dialog)
        select_layout.addWidget(self.tamper_select_btn)
        
        # 快速预设
        select_layout.addWidget(QLabel("快速预设:"))
        self.tamper_preset_combo = QComboBox()
        self.tamper_preset_combo.addItems([
            "-- 选择预设 --",
            "通用 WAF 绕过",
            "MySQL 绕过",
            "MSSQL 绕过",
            "空格替换组合",
            "编码绕过组合",
            "全部清除"
        ])
        self.tamper_preset_combo.currentIndexChanged.connect(self._on_preset_changed)
        select_layout.addWidget(self.tamper_preset_combo)
        
        select_layout.addStretch()
        
        # 已选数量
        self.selected_count_label = QLabel("已选: 0 个脚本")
        self.selected_count_label.setStyleSheet(f"color: {COLORS['accent_blue']}; font-weight: bold;")
        select_layout.addWidget(self.selected_count_label)
        
        tamper_layout.addLayout(select_layout)
        
        # 已选脚本显示区域
        self.selected_tampers_label = QLabel("暂未选择脚本")
        self.selected_tampers_label.setWordWrap(True)
        self.selected_tampers_label.setStyleSheet(f"""
            color: {COLORS['text_secondary']};
            background-color: {COLORS['bg_tertiary']};
            border: 1px solid {COLORS['border']};
            border-radius: 4px;
            padding: 8px;
            min-height: 40px;
        """)
        tamper_layout.addWidget(self.selected_tampers_label)
        
        # 存储已选脚本列表
        self._selected_tamper_scripts = []
        
        # 自定义 tamper
        custom_layout = QHBoxLayout()
        custom_layout.addWidget(QLabel("自定义:"))
        self.custom_tamper_input = QLineEdit()
        self.custom_tamper_input.setPlaceholderText("输入额外的 tamper 脚本名，用逗号分隔")
        custom_layout.addWidget(self.custom_tamper_input)
        tamper_layout.addLayout(custom_layout)
        
        tamper_card.add_layout(tamper_layout)
        layout.addWidget(tamper_card)
        
        # ==================== 代理和请求配置 ====================
        proxy_card = CardWidget("🌐 代理和请求")
        
        proxy_layout = QVBoxLayout()
        proxy_layout.setSpacing(8)
        
        # 代理设置
        proxy_row = QHBoxLayout()
        self.proxy_check = QCheckBox("使用代理:")
        self.proxy_check.stateChanged.connect(self._on_proxy_check_changed)
        proxy_row.addWidget(self.proxy_check)
        
        self.proxy_input = QLineEdit()
        self.proxy_input.setPlaceholderText("http://127.0.0.1:8080")
        self.proxy_input.setEnabled(False)
        proxy_row.addWidget(self.proxy_input)
        proxy_layout.addLayout(proxy_row)
        
        # 代理池文件
        proxy_file_row = QHBoxLayout()
        self.proxy_file_check = QCheckBox("代理池文件:")
        self.proxy_file_check.stateChanged.connect(self._on_proxy_file_check_changed)
        proxy_file_row.addWidget(self.proxy_file_check)
        
        self.proxy_file_input = QLineEdit()
        self.proxy_file_input.setPlaceholderText("选择包含多个代理地址的文件...")
        self.proxy_file_input.setEnabled(False)
        proxy_file_row.addWidget(self.proxy_file_input)
        
        self.proxy_file_browse_btn = QPushButton("浏览...")
        self.proxy_file_browse_btn.setEnabled(False)
        self.proxy_file_browse_btn.clicked.connect(self._browse_proxy_file)
        proxy_file_row.addWidget(self.proxy_file_browse_btn)
        proxy_layout.addLayout(proxy_file_row)
        
        # Tor 设置
        tor_row = QHBoxLayout()
        self.tor_check = QCheckBox("使用 Tor (--tor)")
        self.tor_check.setToolTip("通过 Tor 网络发送请求")
        tor_row.addWidget(self.tor_check)
        
        self.tor_type_combo = QComboBox()
        self.tor_type_combo.addItems(["HTTP", "SOCKS4", "SOCKS5"])
        self.tor_type_combo.setEnabled(False)
        self.tor_check.stateChanged.connect(lambda s: self.tor_type_combo.setEnabled(s == 2))
        tor_row.addWidget(self.tor_type_combo)
        tor_row.addStretch()
        proxy_layout.addLayout(tor_row)
        
        # 安全 URL 设置
        safe_url_row = QHBoxLayout()
        self.safe_url_check = QCheckBox("安全 URL:")
        self.safe_url_check.setToolTip("扫描期间定期访问安全 URL 以保持会话")
        self.safe_url_check.stateChanged.connect(self._on_safe_url_check_changed)
        safe_url_row.addWidget(self.safe_url_check)
        
        self.safe_url_input = QLineEdit()
        self.safe_url_input.setPlaceholderText("输入安全的 URL 地址...")
        self.safe_url_input.setEnabled(False)
        safe_url_row.addWidget(self.safe_url_input)
        proxy_layout.addLayout(safe_url_row)
        
        # 其他请求选项
        req_grid = QGridLayout()
        
        self.random_agent_check = QCheckBox("随机 User-Agent")
        req_grid.addWidget(self.random_agent_check, 0, 0)
        
        self.mobile_check = QCheckBox("模拟手机 (--mobile)")
        req_grid.addWidget(self.mobile_check, 0, 1)
        
        self.skip_waf_check = QCheckBox("跳过 WAF 检测")
        req_grid.addWidget(self.skip_waf_check, 1, 0)
        
        self.hpp_check = QCheckBox("HTTP 参数污染 (--hpp)")
        req_grid.addWidget(self.hpp_check, 1, 1)
        
        self.chunked_check = QCheckBox("分块传输 (--chunked)")
        req_grid.addWidget(self.chunked_check, 1, 2)
        
        proxy_layout.addLayout(req_grid)
        
        proxy_card.add_layout(proxy_layout)
        layout.addWidget(proxy_card)
        
        # ==================== 数据库指定卡片 ====================
        db_card = CardWidget("🗄️ 数据库配置")
        
        db_grid = QGridLayout()
        db_grid.setSpacing(10)
        
        # 数据库类型
        self.dbms_check = QCheckBox("数据库类型:")
        self.dbms_check.stateChanged.connect(self._on_dbms_check_changed)
        db_grid.addWidget(self.dbms_check, 0, 0)
        
        self.dbms_combo = QComboBox()
        self.dbms_combo.addItems([
            "MySQL", "PostgreSQL", "Oracle", "Microsoft SQL Server", 
            "SQLite", "Microsoft Access", "IBM DB2", "Firebird",
            "SAP MaxDB", "Sybase", "HSQLDB", "H2", "MonetDB",
            "Derby", "Vertica", "Mckoi", "Presto", "Altibase",
            "MimerSQL", "CrateDB", "Greenplum", "Drizzle", "Apache Ignite",
            "Cubrid", "InterSystems Cache", "IRIS", "eXtremeDB", "FrontBase"
        ])
        self.dbms_combo.setEnabled(False)
        db_grid.addWidget(self.dbms_combo, 0, 1)
        
        # 数据库版本
        self.dbms_version_check = QCheckBox("版本:")
        self.dbms_version_check.setEnabled(False)
        db_grid.addWidget(self.dbms_version_check, 0, 2)
        
        self.dbms_version_input = QLineEdit()
        self.dbms_version_input.setPlaceholderText("如: 5.7")
        self.dbms_version_input.setEnabled(False)
        self.dbms_version_input.setMaximumWidth(80)
        db_grid.addWidget(self.dbms_version_input, 0, 3)
        
        # 指定数据库名
        self.target_db_check = QCheckBox("指定数据库:")
        self.target_db_check.stateChanged.connect(self._on_target_db_check_changed)
        db_grid.addWidget(self.target_db_check, 1, 0)
        
        self.target_db_input = QLineEdit()
        self.target_db_input.setPlaceholderText("数据库名")
        self.target_db_input.setEnabled(False)
        db_grid.addWidget(self.target_db_input, 1, 1)
        
        # 指定表名
        self.target_table_check = QCheckBox("指定表:")
        self.target_table_check.stateChanged.connect(self._on_target_table_check_changed)
        db_grid.addWidget(self.target_table_check, 1, 2)
        
        self.target_table_input = QLineEdit()
        self.target_table_input.setPlaceholderText("表名")
        self.target_table_input.setEnabled(False)
        db_grid.addWidget(self.target_table_input, 1, 3)
        
        # 指定列
        self.target_col_check = QCheckBox("指定列:")
        self.target_col_check.stateChanged.connect(self._on_target_col_check_changed)
        db_grid.addWidget(self.target_col_check, 2, 0)
        
        self.target_col_input = QLineEdit()
        self.target_col_input.setPlaceholderText("列名，用逗号分隔")
        self.target_col_input.setEnabled(False)
        db_grid.addWidget(self.target_col_input, 2, 1, 1, 3)
        
        db_card.add_layout(db_grid)
        layout.addWidget(db_card)
        
        # ==================== 操作系统功能 ====================
        os_card = CardWidget("💻 操作系统功能")
        
        os_grid = QGridLayout()
        os_grid.setSpacing(8)
        
        self.os_shell_check = QCheckBox("获取 OS Shell (--os-shell)")
        self.os_shell_check.setToolTip("获取操作系统命令行 Shell")
        os_grid.addWidget(self.os_shell_check, 0, 0)
        
        self.os_pwn_check = QCheckBox("获取 OOB Shell (--os-pwn)")
        self.os_pwn_check.setToolTip("通过带外连接获取 Shell")
        os_grid.addWidget(self.os_pwn_check, 0, 1)
        
        self.os_cmd_check = QCheckBox("执行命令:")
        self.os_cmd_check.stateChanged.connect(self._on_os_cmd_check_changed)
        os_grid.addWidget(self.os_cmd_check, 1, 0)
        
        self.os_cmd_input = QLineEdit()
        self.os_cmd_input.setPlaceholderText("要执行的系统命令")
        self.os_cmd_input.setEnabled(False)
        os_grid.addWidget(self.os_cmd_input, 1, 1)
        
        self.file_read_check = QCheckBox("读取文件:")
        self.file_read_check.stateChanged.connect(self._on_file_read_check_changed)
        os_grid.addWidget(self.file_read_check, 2, 0)
        
        self.file_read_input = QLineEdit()
        self.file_read_input.setPlaceholderText("/etc/passwd")
        self.file_read_input.setEnabled(False)
        os_grid.addWidget(self.file_read_input, 2, 1)
        
        self.file_write_check = QCheckBox("写入文件:")
        self.file_write_check.stateChanged.connect(self._on_file_write_check_changed)
        os_grid.addWidget(self.file_write_check, 3, 0)
        
        self.file_write_input = QLineEdit()
        self.file_write_input.setPlaceholderText("本地文件路径 -> 远程路径")
        self.file_write_input.setEnabled(False)
        os_grid.addWidget(self.file_write_input, 3, 1)
        
        os_card.add_layout(os_grid)
        layout.addWidget(os_card)
        
        # 添加弹性空间
        layout.addStretch()
    
    def _open_tamper_dialog(self):
        """打开 Tamper 脚本选择对话框"""
        from ..dialogs.tamper_dialog import TamperSelectionDialog
        
        dialog = TamperSelectionDialog(self, self._selected_tamper_scripts)
        if dialog.exec() == dialog.DialogCode.Accepted:
            self._selected_tamper_scripts = dialog.get_selected_scripts()
            self._update_tamper_display()
    
    def _update_tamper_display(self):
        """更新已选脚本显示"""
        count = len(self._selected_tamper_scripts)
        self.selected_count_label.setText(f"已选: {count} 个脚本")
        
        if count == 0:
            self.selected_tampers_label.setText("暂未选择脚本")
            self.selected_tampers_label.setStyleSheet(f"""
                color: {COLORS['text_secondary']};
                background-color: {COLORS['bg_tertiary']};
                border: 1px solid {COLORS['border']};
                border-radius: 4px;
                padding: 8px;
                min-height: 40px;
            """)
        else:
            # 显示已选脚本名称
            display_text = ", ".join(self._selected_tamper_scripts)
            self.selected_tampers_label.setText(display_text)
            self.selected_tampers_label.setStyleSheet(f"""
                color: {COLORS['text_primary']};
                background-color: {COLORS['bg_tertiary']};
                border: 1px solid {COLORS['accent_blue']};
                border-radius: 4px;
                padding: 8px;
                min-height: 40px;
            """)
    
    def _on_preset_changed(self, index):
        """预设选择变化"""
        presets = {
            1: ["space2comment", "randomcase", "between", "charencode"],  # 通用 WAF
            2: ["space2comment", "randomcase", "versionedkeywords", "space2mysqlblank"],  # MySQL
            3: ["space2mssqlblank", "randomcase", "space2mssqlhash"],  # MSSQL
            4: ["space2comment", "space2hash", "space2dash", "space2plus"],  # 空格替换
            5: ["charencode", "base64encode", "charunicodeencode", "htmlencode"],  # 编码
        }
        
        if index == 6:  # 全部清除
            self._selected_tamper_scripts = []
        elif index in presets:
            self._selected_tamper_scripts = presets[index].copy()
        
        self._update_tamper_display()
        
        # 重置预设选择
        self.tamper_preset_combo.blockSignals(True)
        self.tamper_preset_combo.setCurrentIndex(0)
        self.tamper_preset_combo.blockSignals(False)
    
    def _on_proxy_check_changed(self, state):
        """代理复选框变化"""
        self.proxy_input.setEnabled(state == Qt.CheckState.Checked.value)
    
    def _on_proxy_file_check_changed(self, state):
        """代理池文件复选框变化"""
        enabled = state == Qt.CheckState.Checked.value
        self.proxy_file_input.setEnabled(enabled)
        self.proxy_file_browse_btn.setEnabled(enabled)
    
    def _browse_proxy_file(self):
        """浏览代理池文件"""
        from PyQt6.QtWidgets import QFileDialog
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择代理池文件", "", 
            "文本文件 (*.txt);;所有文件 (*.*)"
        )
        if file_path:
            self.proxy_file_input.setText(file_path)
    
    def _on_safe_url_check_changed(self, state):
        """安全URL复选框变化"""
        self.safe_url_input.setEnabled(state == Qt.CheckState.Checked.value)
    
    def _on_dbms_check_changed(self, state):
        """数据库类型复选框变化"""
        enabled = state == Qt.CheckState.Checked.value
        self.dbms_combo.setEnabled(enabled)
        self.dbms_version_check.setEnabled(enabled)
        self.dbms_version_input.setEnabled(enabled and self.dbms_version_check.isChecked())
    
    def _on_target_db_check_changed(self, state):
        """目标数据库复选框变化"""
        self.target_db_input.setEnabled(state == Qt.CheckState.Checked.value)
    
    def _on_target_table_check_changed(self, state):
        """目标表复选框变化"""
        self.target_table_input.setEnabled(state == Qt.CheckState.Checked.value)
    
    def _on_target_col_check_changed(self, state):
        """目标列复选框变化"""
        self.target_col_input.setEnabled(state == Qt.CheckState.Checked.value)
    
    def _on_os_cmd_check_changed(self, state):
        """OS 命令复选框变化"""
        self.os_cmd_input.setEnabled(state == Qt.CheckState.Checked.value)
    
    def _on_file_read_check_changed(self, state):
        """文件读取复选框变化"""
        self.file_read_input.setEnabled(state == Qt.CheckState.Checked.value)
    
    def _on_file_write_check_changed(self, state):
        """文件写入复选框变化"""
        self.file_write_input.setEnabled(state == Qt.CheckState.Checked.value)
    
    # ==================== 公共方法 ====================
    
    def get_threads(self) -> int:
        return self.threads_spin.value()
    
    def get_timeout(self) -> int:
        return self.timeout_spin.value()
    
    def get_retries(self) -> int:
        return self.retries_spin.value()
    
    def get_delay(self) -> int:
        return self.delay_spin.value()
    
    def is_batch_mode(self) -> bool:
        return self.batch_check.isChecked()
    
    def is_flush_session(self) -> bool:
        return self.flush_check.isChecked()
    
    def is_fresh_queries(self) -> bool:
        return self.fresh_check.isChecked()
    
    def get_tamper(self) -> str:
        """获取选中的 tamper 脚本"""
        selected = self._selected_tamper_scripts.copy()
        
        # 添加自定义 tamper
        custom = self.custom_tamper_input.text().strip()
        if custom:
            selected.extend([t.strip() for t in custom.split(",") if t.strip()])
        
        return ",".join(selected)
    
    def get_proxy(self) -> str:
        if self.proxy_check.isChecked():
            return self.proxy_input.text().strip()
        return ""
    
    def get_proxy_file(self) -> str:
        """获取代理池文件路径"""
        if self.proxy_file_check.isChecked():
            return self.proxy_file_input.text().strip()
        return ""
    
    def get_safe_url(self) -> str:
        """获取安全URL"""
        if self.safe_url_check.isChecked():
            return self.safe_url_input.text().strip()
        return ""
    
    def use_random_agent(self) -> bool:
        return self.random_agent_check.isChecked()
    
    def get_dbms(self) -> str:
        if self.dbms_check.isChecked():
            return self.dbms_combo.currentText()
        return ""
    
    def get_target_db(self) -> str:
        if self.target_db_check.isChecked():
            return self.target_db_input.text().strip()
        return ""
    
    def get_target_table(self) -> str:
        if self.target_table_check.isChecked():
            return self.target_table_input.text().strip()
        return ""
    
    def get_target_columns(self) -> str:
        if self.target_col_check.isChecked():
            return self.target_col_input.text().strip()
        return ""
    
    def use_tor(self) -> bool:
        return self.tor_check.isChecked()
    
    def is_mobile(self) -> bool:
        return self.mobile_check.isChecked()
    
    def use_hpp(self) -> bool:
        return self.hpp_check.isChecked()
    
    def use_chunked(self) -> bool:
        return self.chunked_check.isChecked()
    
    def get_os_shell(self) -> bool:
        return self.os_shell_check.isChecked()
    
    def get_os_cmd(self) -> str:
        if self.os_cmd_check.isChecked():
            return self.os_cmd_input.text().strip()
        return ""
    
    def get_file_read(self) -> str:
        if self.file_read_check.isChecked():
            return self.file_read_input.text().strip()
        return ""
    
    # ==================== 新增缺失的方法 ====================
    
    def is_forms(self) -> bool:
        """是否解析表单"""
        return self.forms_check.isChecked()
    
    def get_crawl(self) -> int:
        """获取爬取深度"""
        if self.crawl_check.isChecked():
            return 3  # 默认深度
        return 0
    
    def is_smart(self) -> bool:
        """是否智能模式"""
        return self.smart_check.isChecked()
    
    def is_null_connection(self) -> bool:
        """是否空连接检测"""
        return self.null_connection_check.isChecked()
    
    def is_text_only(self) -> bool:
        """是否仅文本"""
        return self.text_only_check.isChecked()
    
    def is_no_cast(self) -> bool:
        """是否禁用转换"""
        return self.no_cast_check.isChecked()
    
    def is_skip_waf(self) -> bool:
        """是否跳过WAF检测"""
        return self.skip_waf_check.isChecked()
    
    def get_os_pwn(self) -> bool:
        """是否获取OOB Shell"""
        return self.os_pwn_check.isChecked()
    
    def get_file_write(self) -> tuple:
        """获取文件写入配置 (本地路径, 远程路径)"""
        if self.file_write_check.isChecked():
            text = self.file_write_input.text().strip()
            if "->" in text:
                parts = text.split("->")
                return parts[0].strip(), parts[1].strip()
        return "", ""
    
    def get_tor_type(self) -> str:
        """获取Tor类型"""
        if self.tor_check.isChecked():
            return self.tor_type_combo.currentText()
        return ""
    
    def get_prefix(self) -> str:
        """获取注入前缀"""
        return self.prefix_input.text().strip()
    
    def get_suffix(self) -> str:
        """获取注入后缀"""
        return self.suffix_input.text().strip()

    def set_target_db(self, db_name: str):
        """设置目标数据库"""
        self.target_db_check.setChecked(True)
        self.target_db_input.setText(db_name)
    
    def set_target_table(self, table_name: str):
        """设置目标表"""
        self.target_table_check.setChecked(True)
        self.target_table_input.setText(table_name)
    
    # ==================== AI 参数应用方法 ====================
    
    def set_threads(self, threads: int):
        """设置线程数"""
        if 1 <= threads <= 10:
            self.threads_spin.setValue(threads)
    
    def set_timeout(self, timeout: int):
        """设置超时时间"""
        if 5 <= timeout <= 300:
            self.timeout_spin.setValue(timeout)
    
    def set_tamper(self, tamper: str):
        """设置 Tamper 脚本"""
        if tamper:
            self._selected_tamper_scripts = [t.strip() for t in tamper.split(',') if t.strip()]
            self._update_tamper_display()
    
    def set_proxy(self, proxy: str):
        """设置代理"""
        if proxy:
            self.proxy_check.setChecked(True)
            self.proxy_input.setText(proxy)
    
    def set_random_agent(self, enabled: bool):
        """设置随机 User-Agent"""
        self.random_agent_check.setChecked(enabled)
    
    def set_prefix(self, prefix: str):
        """设置注入前缀"""
        self.prefix_input.setText(prefix)
    
    def set_suffix(self, suffix: str):
        """设置注入后缀"""
        self.suffix_input.setText(suffix)
    
    def set_dbms(self, dbms: str):
        """设置数据库类型"""
        if dbms:
            self.dbms_check.setChecked(True)
            # 查找匹配的数据库名称
            for i in range(self.dbms_combo.count()):
                if dbms.lower() in self.dbms_combo.itemText(i).lower():
                    self.dbms_combo.setCurrentIndex(i)
                    break
