"""
SQLMap GUI v2 主窗口
现代化的 SQLMap 图形界面
"""

import os
import sys
from datetime import datetime

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QSplitter, QTabWidget, QStatusBar, QMenuBar, QMenu, QMessageBox,
    QLabel, QPushButton, QProgressBar, QFrame, QScrollArea, QSizePolicy
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QAction, QFont

from .theme import DARK_THEME, COLORS, generate_theme_stylesheet
from .dialogs.settings_dialog import SettingsDialog
from .dialogs.about_dialog import AboutDialog
from .dialogs.history_dialog import HistoryDialog
from .panels.target_panel import TargetPanel
from .panels.scan_panel import ScanPanel
from .panels.advanced_panel import AdvancedPanel
from .panels.result_panel import ResultPanel
from .panels.log_panel import LogPanel

# 添加父目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.sqlmap_engine import SqlmapEngine, SqlmapFinder
from core.command_builder import CommandBuilder
from core.config_manager import ConfigManager
from core.history_manager import HistoryManager


class MainWindow(QMainWindow):
    """主窗口"""
    
    def __init__(self):
        super().__init__()
        
        # 初始化组件
        self.config = ConfigManager()
        self.history = HistoryManager()
        self.engine = None
        self.current_scan_id = None
        self.scan_start_time = None
        self.elapsed_timer = QTimer()
        self.elapsed_timer.timeout.connect(self._update_elapsed_time)
        
        # 设置窗口
        self.setWindowTitle("🔒 SQLMap GUI v2")
        self._restore_geometry()
        self.setMinimumSize(1100, 750)  # 稍微减小最小尺寸
        
        # 加载并应用保存的主题
        self._load_and_apply_theme()
        
        # 设置 UI
        self.setup_ui()
        self.setup_menu()
        self.setup_status_bar()
        
        # 查找 sqlmap
        self._find_sqlmap()
        
        # 加载保存的配置
        self.load_config()
    
    def _load_and_apply_theme(self):
        """加载并应用保存的主题"""
        saved_theme = self.config.get("ui", "theme", "dark")
        if saved_theme and saved_theme != "dark":
            # 应用保存的主题
            stylesheet = generate_theme_stylesheet(saved_theme)
            self.setStyleSheet(stylesheet)
        else:
            # 使用默认主题
            self.setStyleSheet(DARK_THEME)
    
    def _restore_geometry(self):
        """恢复窗口位置和大小"""
        size = self.config.window_size
        pos = self.config.window_position
        self.setGeometry(pos[0], pos[1], size[0], size[1])
    
    def _save_geometry(self):
        """保存窗口位置和大小"""
        geo = self.geometry()
        self.config.save_window_geometry(geo.x(), geo.y(), geo.width(), geo.height())
    
    def setup_ui(self):
        """设置 UI"""
        # 中心部件
        central = QWidget()
        self.setCentralWidget(central)
        
        main_layout = QVBoxLayout(central)
        # 增加底部边距确保不被 Windows 任务栏遮挡
        main_layout.setContentsMargins(10, 10, 10, 15)
        main_layout.setSpacing(8)
        
        # ==================== 顶部标题栏 ====================
        header = self._create_header()
        header.setFixedHeight(45)  # 稍微减小标题栏高度
        main_layout.addWidget(header)
        
        # ==================== 主分割器 ====================
        main_splitter = QSplitter(Qt.Orientation.Horizontal)
        main_splitter.setChildrenCollapsible(False)  # 防止子面板被完全折叠
        
        # 左侧配置面板（带滚动）
        left_panel = self._create_left_panel()
        main_splitter.addWidget(left_panel)
        
        # 右侧结果面板
        right_panel = self._create_right_panel()
        main_splitter.addWidget(right_panel)
        
        # 设置分割比例和拉伸策略
        main_splitter.setSizes([450, 750])
        main_splitter.setStretchFactor(0, 2)  # 左侧可拉伸
        main_splitter.setStretchFactor(1, 3)  # 右侧更多拉伸
        
        main_layout.addWidget(main_splitter, 1)  # stretch=1 让分割器占据更多空间
        
        # ==================== 底部控制栏 ====================
        control_bar = self._create_control_bar()
        control_bar.setFixedHeight(55)  # 稍微减小控制栏高度
        control_bar.setMinimumHeight(55)  # 确保最小高度
        main_layout.addWidget(control_bar)
    
    def _create_header(self) -> QWidget:
        """创建顶部标题栏"""
        header = QFrame()
        header.setObjectName("header")
        # 样式由全局主题控制
        
        layout = QHBoxLayout(header)
        layout.setContentsMargins(15, 8, 15, 8)
        
        # 标题
        title = QLabel("🔒 SQLMap GUI v2")
        title.setObjectName("headerTitle")
        title.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(title)
        
        # 副标题
        subtitle = QLabel("智能 SQL 注入检测工具")
        subtitle.setObjectName("headerSubtitle")
        subtitle.setStyleSheet("font-size: 11px;")
        layout.addWidget(subtitle)
        
        layout.addStretch()
        
        # 状态指示
        self.status_indicator = QLabel("● 就绪")
        self.status_indicator.setObjectName("statusIndicator")
        layout.addWidget(self.status_indicator)
        
        return header
    
    def _create_left_panel(self) -> QWidget:
        """创建左侧配置面板"""
        panel = QWidget()
        panel.setMinimumWidth(400)  # 设置最小宽度
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # 标签页
        tabs = QTabWidget()
        tabs.setTabPosition(QTabWidget.TabPosition.North)
        
        # 目标配置（带滚动）
        target_scroll = QScrollArea()
        target_scroll.setWidgetResizable(True)
        target_scroll.setFrameShape(QFrame.Shape.NoFrame)
        self.target_panel = TargetPanel()
        target_scroll.setWidget(self.target_panel)
        tabs.addTab(target_scroll, "🎯 目标")
        
        # 扫描设置（带滚动）
        scan_scroll = QScrollArea()
        scan_scroll.setWidgetResizable(True)
        scan_scroll.setFrameShape(QFrame.Shape.NoFrame)
        self.scan_panel = ScanPanel()
        scan_scroll.setWidget(self.scan_panel)
        tabs.addTab(scan_scroll, "⚙️ 扫描")
        
        # 高级选项（带滚动）
        advanced_scroll = QScrollArea()
        advanced_scroll.setWidgetResizable(True)
        advanced_scroll.setFrameShape(QFrame.Shape.NoFrame)
        self.advanced_panel = AdvancedPanel()
        advanced_scroll.setWidget(self.advanced_panel)
        tabs.addTab(advanced_scroll, "🔧 高级")
        
        layout.addWidget(tabs)
        
        return panel
    
    def _create_right_panel(self) -> QWidget:
        """创建右侧结果面板"""
        panel = QWidget()
        panel.setMinimumWidth(400)  # 设置最小宽度
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # 标签页
        tabs = QTabWidget()
        
        # 日志面板
        self.log_panel = LogPanel()
        tabs.addTab(self.log_panel, "📜 日志")
        
        # 结果面板
        self.result_panel = ResultPanel()
        tabs.addTab(self.result_panel, "📊 结果")
        
        layout.addWidget(tabs)
        
        return panel
    
    def _create_control_bar(self) -> QWidget:
        """创建底部控制栏"""
        bar = QFrame()
        bar.setObjectName("controlBar")
        # 样式由全局主题控制
        
        layout = QHBoxLayout(bar)
        layout.setContentsMargins(15, 8, 15, 8)
        layout.setSpacing(12)
        
        # 命令预览
        self.command_preview = QLabel("命令预览: 请配置扫描参数...")
        self.command_preview.setObjectName("commandPreview")
        self.command_preview.setStyleSheet("""
            font-family: 'Consolas', monospace;
            font-size: 10px;
        """)
        self.command_preview.setWordWrap(True)
        self.command_preview.setMaximumHeight(40)
        layout.addWidget(self.command_preview, 1)
        
        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setFixedWidth(120)
        self.progress_bar.setFixedHeight(20)
        self.progress_bar.setValue(0)
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        # 开始按钮
        self.start_btn = QPushButton("▶ 开始扫描")
        self.start_btn.setProperty("class", "primary")
        self.start_btn.setMinimumSize(120, 36)
        self.start_btn.clicked.connect(self.start_scan)
        layout.addWidget(self.start_btn)
        
        # 停止按钮
        self.stop_btn = QPushButton("⏹ 停止")
        self.stop_btn.setProperty("class", "danger")
        self.stop_btn.setMinimumSize(90, 36)
        self.stop_btn.setEnabled(False)
        self.stop_btn.clicked.connect(self.stop_scan)
        layout.addWidget(self.stop_btn)
        
        return bar
    
    def setup_menu(self):
        """设置菜单栏"""
        menubar = self.menuBar()
        
        # 文件菜单
        file_menu = menubar.addMenu("文件")
        
        new_action = QAction("新建配置", self)
        new_action.triggered.connect(self.new_config)
        file_menu.addAction(new_action)
        
        save_action = QAction("保存配置", self)
        save_action.triggered.connect(self.save_config)
        file_menu.addAction(save_action)
        
        load_action = QAction("加载配置", self)
        load_action.triggered.connect(self.load_config)
        file_menu.addAction(load_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("退出", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # 工具菜单
        tool_menu = menubar.addMenu("工具")
        
        history_action = QAction("扫描历史", self)
        history_action.triggered.connect(self.show_history)
        tool_menu.addAction(history_action)
        
        clear_history_action = QAction("清除历史", self)
        clear_history_action.triggered.connect(self.clear_history)
        tool_menu.addAction(clear_history_action)
        
        tool_menu.addSeparator()
        
        settings_action = QAction("设置", self)
        settings_action.triggered.connect(self.show_settings)
        tool_menu.addAction(settings_action)
        
        # 帮助菜单
        help_menu = menubar.addMenu("帮助")
        
        about_action = QAction("关于", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    def setup_status_bar(self):
        """设置状态栏"""
        status_bar = self.statusBar()
        
        # 耗时
        self.elapsed_label = QLabel("耗时: 00:00:00")
        status_bar.addWidget(self.elapsed_label)
        
        # 分隔符
        status_bar.addWidget(QLabel("  |  "))
        
        # 请求数
        self.request_label = QLabel("请求: 0")
        status_bar.addWidget(self.request_label)
        
        # 分隔符
        status_bar.addWidget(QLabel("  |  "))
        
        # sqlmap 路径
        self.sqlmap_label = QLabel("SQLMap: 未找到")
        status_bar.addWidget(self.sqlmap_label)
        
        # 弹性空间
        status_bar.addPermanentWidget(QLabel(""))
        
        # 状态
        self.status_label = QLabel("就绪")
        status_bar.addPermanentWidget(self.status_label)
    
    def _find_sqlmap(self):
        """查找 sqlmap"""
        path = SqlmapFinder.find_sqlmap()
        if path:
            self.sqlmap_path = path
            self.sqlmap_label.setText(f"SQLMap: {os.path.basename(os.path.dirname(path))}")
            self.sqlmap_label.setStyleSheet(f"color: {COLORS['success']};")
        else:
            self.sqlmap_path = None
            self.sqlmap_label.setText("SQLMap: 未找到")
            self.sqlmap_label.setStyleSheet(f"color: {COLORS['error']};")
    
    def _build_command(self) -> str:
        """构建 sqlmap 命令"""
        if not self.sqlmap_path:
            return ""
        
        builder = CommandBuilder(f"python \"{self.sqlmap_path}\"")
        
        # 判断扫描模式
        if self.target_panel.is_request_mode():
            # 请求包模式（头注入检测）
            request_file = self.target_panel.get_request_file()
            request_content = self.target_panel.get_request_content()
            
            if request_file:
                # 使用选择的文件
                builder.set_request_file(request_file)
            elif request_content:
                # 使用粘贴的内容，保存到临时文件
                import tempfile
                temp_file = os.path.join(
                    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                    'temp_request.txt'
                )
                try:
                    with open(temp_file, 'w', encoding='utf-8') as f:
                        f.write(request_content)
                    builder.set_request_file(temp_file)
                except Exception:
                    return ""
            else:
                return ""
        else:
            # 普通 URL 模式或批量文件模式
            target = self.target_panel.get_target()
            if not target:
                return ""
            
            if self.target_panel.is_file_mode():
                builder.set_file(target)
            else:
                builder.set_target(target)
        
        # POST 数据（仅非请求包模式下有效）
        if not self.target_panel.is_request_mode():
            post_data = self.target_panel.get_post_data()
            if post_data:
                builder.set_data(post_data)
            
            # Cookie
            cookie = self.target_panel.get_cookie()
            if cookie:
                builder.set_cookie(cookie)
        
        # 指定参数
        param = self.target_panel.get_param()
        if param:
            builder.set_param(param)
        
        # 扫描设置
        builder.set_level(self.scan_panel.get_level())
        builder.set_risk(self.scan_panel.get_risk())
        builder.set_technique(self.scan_panel.get_technique())
        builder.set_verbose(self.scan_panel.get_verbose())
        
        # 字符串匹配
        string_match = self.scan_panel.get_string_match()
        if string_match:
            builder.set_string_match(string_match)
            
        # 注入前缀/后缀
        prefix = self.advanced_panel.get_prefix()
        if prefix:
            builder.set_prefix(prefix)
            
        suffix = self.advanced_panel.get_suffix()
        if suffix:
            builder.set_suffix(suffix)
        
        # 信息获取
        builder.get_current_db(self.scan_panel.get_current_db())
        builder.get_current_user(self.scan_panel.get_current_user())
        builder.get_banner(self.scan_panel.get_banner())
        builder.get_hostname(self.scan_panel.get_hostname())
        builder.get_is_dba(self.scan_panel.get_is_dba())
        builder.get_users(self.scan_panel.get_users())
        builder.get_privileges(self.scan_panel.get_privileges())
        builder.get_roles(self.scan_panel.get_roles())
        
        # 枚举选项
        builder.enum_dbs(self.scan_panel.get_dbs())
        builder.enum_tables(self.scan_panel.get_tables())
        builder.enum_columns(self.scan_panel.get_columns())
        builder.enum_schema(self.scan_panel.get_schema())
        builder.enum_count(self.scan_panel.get_count())
        builder.enum_comments(self.scan_panel.get_comments())
        builder.enum_passwords(self.scan_panel.get_passwords())
        
        # 数据提取
        builder.dump_data(self.scan_panel.get_dump())
        builder.dump_all(self.scan_panel.get_dump_all())
        
        # 高级选项 - 性能
        builder.set_threads(self.advanced_panel.get_threads())
        builder.set_timeout(self.advanced_panel.get_timeout())
        builder.set_retries(self.advanced_panel.get_retries())
        builder.set_delay(self.advanced_panel.get_delay())
        
        # 高级选项 - 通用
        builder.set_batch(self.advanced_panel.is_batch_mode())
        builder.set_flush_session(self.advanced_panel.is_flush_session())
        builder.set_fresh_queries(self.advanced_panel.is_fresh_queries())
        
        # 新增：表单、爬取、智能模式等
        if self.advanced_panel.is_forms():
            builder.set_forms(True)
        crawl = self.advanced_panel.get_crawl()
        if crawl > 0:
            builder.set_crawl(crawl)
        if self.advanced_panel.is_smart():
            builder.set_smart(True)
        if self.advanced_panel.is_text_only():
            builder.set_text_only(True)
        
        # 绕过设置
        tamper = self.advanced_panel.get_tamper()
        if tamper:
            builder.set_tamper(tamper)
        
        proxy = self.advanced_panel.get_proxy()
        if proxy:
            builder.set_proxy(proxy)
        
        if self.advanced_panel.use_random_agent():
            builder.set_random_agent(True)
        
        if self.advanced_panel.use_tor():
            tor_type = self.advanced_panel.get_tor_type()
            builder.set_tor(True, tor_type)
        
        if self.advanced_panel.is_mobile():
            builder.set_mobile(True)
        
        if self.advanced_panel.use_hpp():
            builder.set_hpp(True)
        
        if self.advanced_panel.use_chunked():
            builder.set_chunked(True)
        
        # 新增：跳过WAF检测
        if self.advanced_panel.is_skip_waf():
            builder.set_skip_waf(True)
        
        # 数据库指定
        dbms = self.advanced_panel.get_dbms()
        if dbms:
            builder.set_dbms(dbms)
        
        # 目标数据库/表/列
        target_db = self.advanced_panel.get_target_db()
        if target_db:
            builder.enum_tables(db=target_db)
        
        target_table = self.advanced_panel.get_target_table()
        if target_table:
            builder.enum_columns(table=target_table)
        
        target_columns = self.advanced_panel.get_target_columns()
        if target_columns:
            builder.dump_data(columns=target_columns)
        
        # 操作系统功能
        if self.advanced_panel.get_os_shell():
            builder.os_shell(True)
        
        # 新增：OOB Shell
        if self.advanced_panel.get_os_pwn():
            builder.os_pwn(True)
        
        os_cmd = self.advanced_panel.get_os_cmd()
        if os_cmd:
            builder.os_cmd(os_cmd)
        
        file_read = self.advanced_panel.get_file_read()
        if file_read:
            builder.file_read(file_read)
        
        # 新增：文件写入
        file_local, file_remote = self.advanced_panel.get_file_write()
        if file_local and file_remote:
            builder.file_write(file_local, file_remote)
        
        return builder.build()
    
    def _update_command_preview(self):
        """更新命令预览"""
        try:
            command = self._build_command()
            if command:
                # 截断过长的命令
                if len(command) > 200:
                    display = command[:200] + "..."
                else:
                    display = command
                self.command_preview.setText(f"命令: {display}")
                self.command_preview.setStyleSheet(f"color: {COLORS['text_secondary']};")
            else:
                self.command_preview.setText("命令预览: 请输入目标 URL...")
                self.command_preview.setStyleSheet(f"color: {COLORS['text_muted']};")
        except Exception as e:
            self.command_preview.setText(f"命令错误: {str(e)}")
            self.command_preview.setStyleSheet(f"color: {COLORS['error']};")
    
    def _update_elapsed_time(self):
        """更新耗时"""
        if self.scan_start_time:
            elapsed = datetime.now() - self.scan_start_time
            hours, remainder = divmod(int(elapsed.total_seconds()), 3600)
            minutes, seconds = divmod(remainder, 60)
            self.elapsed_label.setText(f"耗时: {hours:02d}:{minutes:02d}:{seconds:02d}")
            self.result_panel.update_stats(
                elapsed_time=f"{hours:02d}:{minutes:02d}:{seconds:02d}"
            )
    
    # ==================== 扫描控制 ====================
    
    def start_scan(self):
        """开始扫描"""
        # 检查 sqlmap
        if not self.sqlmap_path:
            QMessageBox.warning(self, "警告", "未找到 sqlmap，请检查配置。")
            return
        
        # 检查目标（根据模式判断）
        if self.target_panel.is_request_mode():
            # 请求包模式：检查是否有请求包文件或内容
            request_file = self.target_panel.get_request_file()
            request_content = self.target_panel.get_request_content()
            if not request_file and not request_content:
                QMessageBox.warning(self, "警告", "请选择请求包文件或粘贴请求包内容。")
                return
            target = request_file if request_file else "请求包扫描"
        else:
            # URL 模式或批量文件模式
            target = self.target_panel.get_target()
            if not target:
                QMessageBox.warning(self, "警告", "请输入目标 URL。")
                return
        
        # 构建命令
        try:
            command = self._build_command()
        except Exception as e:
            QMessageBox.warning(self, "错误", f"构建命令失败: {str(e)}")
            return
        
        # 清空之前的结果
        self.log_panel.clear()
        self.result_panel.clear_all()
        
        # 更新 UI 状态
        self._set_scanning_state(True)
        
        # 记录历史
        mode = self.scan_panel.get_current_mode()
        self.current_scan_id = self.history.add_scan(target, command, mode)
        
        # 开始计时
        self.scan_start_time = datetime.now()
        self.elapsed_timer.start(1000)
        
        # 启动引擎 - 传入 self 作为父对象确保线程生命周期与主窗口绑定
        self.engine = SqlmapEngine(command, self.sqlmap_path, parent=self)
        # 使用队列连接确保信号在主线程中处理
        self.engine.output_received.connect(self._on_output, Qt.ConnectionType.QueuedConnection)
        self.engine.progress_updated.connect(self._on_progress, Qt.ConnectionType.QueuedConnection)
        self.engine.result_found.connect(self._on_result, Qt.ConnectionType.QueuedConnection)
        self.engine.scan_finished.connect(self._on_finished, Qt.ConnectionType.QueuedConnection)
        self.engine.status_changed.connect(self._on_status_changed, Qt.ConnectionType.QueuedConnection)
        self.engine.start()
        
        self.log_panel.start_logging()
    
    def stop_scan(self):
        """停止扫描"""
        if self.engine and self.engine.isRunning():
            self.engine.stop()
            self.log_panel.append_line("用户停止扫描", "WARNING")
    
    def _set_scanning_state(self, scanning: bool):
        """设置扫描状态"""
        self.start_btn.setEnabled(not scanning)
        self.stop_btn.setEnabled(scanning)
        self.progress_bar.setVisible(scanning)
        
        if scanning:
            self.status_indicator.setText("● 扫描中")
            self.status_indicator.setStyleSheet(f"color: {COLORS['warning']};")
            self.status_label.setText("扫描中...")
        else:
            self.status_indicator.setText("● 就绪")
            self.status_indicator.setStyleSheet(f"color: {COLORS['success']};")
            self.status_label.setText("就绪")
    
    def _on_output(self, text: str):
        """接收输出"""
        self.log_panel.append(text)
    
    def _on_progress(self, progress: int):
        """更新进度"""
        self.progress_bar.setValue(progress)
    
    def _on_result(self, results: dict):
        """接收结果"""
        # 更新注入信息
        if results.get('injection_found'):
            info = []
            info.append("✅ 发现 SQL 注入漏洞！\n")
            
            if results.get('dbms'):
                info.append(f"数据库类型: {results['dbms']}")
            if results.get('current_db'):
                info.append(f"当前数据库: {results['current_db']}")
            if results.get('current_user'):
                info.append(f"当前用户: {results['current_user']}")
            if results.get('injection_type'):
                info.append(f"注入类型: {', '.join(results['injection_type'])}")
            
            self.result_panel.set_injection_info("\n".join(info))
        
        # 获取表数据
        tables_dict = results.get('tables', {})
        
        # 更新数据库列表（同时传入表数据，实现点击联动）
        if results.get('databases'):
            self.result_panel.set_databases_with_tables(results['databases'], tables_dict)
        
        # 更新列列表 - 合并所有表的列
        all_columns = []
        columns_dict = results.get('columns', {})
        if columns_dict:
            for (db_name, table_name), columns in columns_dict.items():
                for col in columns:
                    if isinstance(col, tuple):
                        all_columns.append(col)
                    else:
                        all_columns.append((col, ""))
            if all_columns:
                self.result_panel.set_columns_with_data(all_columns, columns_dict)
        
        # 更新提取的数据内容
        data_dict = results.get('data', {})
        if data_dict:
            # 存储数据供双击查看使用
            self.result_panel.set_extracted_data(data_dict)
            
            # 同时将有数据的表添加到表列表中（如果还没有的话）
            for table_name in data_dict.keys():
                # 如果表名包含数据库前缀（如 patient.mg_doctor），只取表名部分
                if '.' in table_name:
                    pure_table_name = table_name.split('.')[-1]
                else:
                    pure_table_name = table_name
                # 添加到表列表（避免重复）
                self.result_panel.add_table_if_not_exists(pure_table_name)
            
            data_text = []
            for table_name, rows in data_dict.items():
                data_text.append(f"========== 表: {table_name} ==========")
                for row in rows:
                    data_text.append(row)
                data_text.append("")
            if data_text:
                self.result_panel.set_data("\n".join(data_text))
        
        # 更新统计
        vuln_count = 1 if results.get('injection_found') else 0
        db_count = len(results.get('databases', []))
        table_count = sum(len(tables) for tables in results.get('tables', {}).values())
        
        self.result_panel.update_stats(
            vuln_count=vuln_count,
            db_count=db_count,
            table_count=table_count
        )
    
    def _on_finished(self, return_code: int):
        """扫描完成"""
        try:
            self._set_scanning_state(False)
            self.elapsed_timer.stop()
            self.log_panel.stop_logging()
            
            # 更新历史记录
            if self.current_scan_id and self.engine:
                try:
                    results = self.engine.results
                    self.history.complete_scan(
                        self.current_scan_id,
                        has_vuln=results.get('injection_found', False),
                        vuln_count=1 if results.get('injection_found') else 0,
                        dbms=results.get('dbms', ''),
                        current_db=results.get('current_db', '')
                    )
                except Exception:
                    pass
            
            # 显示完成消息
            if return_code == 0:
                self.log_panel.append_line("扫描完成", "SUCCESS")
            else:
                self.log_panel.append_line(f"扫描结束 (返回码: {return_code})", "WARNING")
        except Exception:
            pass
    
    def _on_status_changed(self, status: str):
        """状态变化"""
        self.status_label.setText(status)
    
    # ==================== 菜单操作 ====================
    
    def new_config(self):
        """新建配置"""
        pass
    
    def save_config(self):
        """保存配置"""
        # 保存扫描面板配置
        self.scan_panel.save_config(self.config)
        
        # 保存配置到文件
        if self.config.save():
            QMessageBox.information(self, "提示", "配置已保存，下次启动时将自动加载。")
    
    def load_config(self):
        """加载配置"""
        self.scan_panel.load_config(self.config)
    
    def show_history(self):
        """显示历史记录"""
        dialog = HistoryDialog(self.history, self)
        dialog.load_target.connect(self._on_load_target)
        dialog.exec()
    
    def _on_load_target(self, target: str):
        """从历史加载目标"""
        self.target_panel.set_target(target)
    
    def clear_history(self):
        """清除历史"""
        reply = QMessageBox.question(
            self, "确认", "确定要清除所有扫描历史吗？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            count = self.history.clear_history()
            QMessageBox.information(self, "提示", f"已清除 {count} 条历史记录。")
    
    def show_settings(self):
        """显示设置"""
        dialog = SettingsDialog(self.config, self)
        dialog.theme_changed.connect(self._on_theme_changed)
        dialog.settings_changed.connect(self._on_settings_changed)
        dialog.exec()
    
    def _on_theme_changed(self, theme_name: str):
        """主题变化"""
        stylesheet = generate_theme_stylesheet(theme_name)
        self.setStyleSheet(stylesheet)
    
    def _on_settings_changed(self):
        """设置变化"""
        # 重新查找 sqlmap
        self._find_sqlmap()
    
    def show_about(self):
        """显示关于"""
        dialog = AboutDialog(self)
        dialog.exec()
    
    # ==================== 事件处理 ====================
    
    def closeEvent(self, event):
        """关闭事件"""
        # 停止扫描
        if self.engine and self.engine.isRunning():
            self.engine.stop()
            self.engine.wait()
        
        # 保存窗口位置和大小
        self._save_geometry()
        
        # 保存配置
        self.config.save()
        
        event.accept()
