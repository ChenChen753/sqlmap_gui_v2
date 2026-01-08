"""
AI 分析面板
用于展示 AI 分析结果和提供分析操作
整合日志分析和命令推荐，支持安全/激进方案选择
"""

import re
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTextEdit,
    QPushButton, QProgressBar, QMessageBox, QApplication, QGroupBox,
    QRadioButton, QButtonGroup, QFrame
)
from PyQt6.QtCore import pyqtSignal, Qt, QThread, pyqtSlot
from PyQt6.QtGui import QTextCursor

from core.ai_analyzer import AIAnalyzer, AIResponse, create_analyzer_from_config


# 危险参数定义
DANGEROUS_PARAMS = {
    'risk': {
        'threshold': 2,  # risk >= 2 视为危险
        'warning': '高风险等级可能执行危险的 SQL 语句，可能导致数据修改或删除'
    },
    'level': {
        'threshold': 4,  # level >= 4 视为危险
        'warning': '高扫描等级会发送大量请求，可能触发安全设备告警或影响目标性能'
    },
    'os_shell': {
        'warning': '尝试获取操作系统 Shell，可能触发入侵检测系统'
    },
    'os_pwn': {
        'warning': '尝试通过带外连接获取 Shell，高度危险操作'
    },
    'file_read': {
        'warning': '尝试读取服务器敏感文件'
    },
    'file_write': {
        'warning': '尝试向服务器写入文件，可能造成严重后果'
    }
}


class AnalyzeThread(QThread):
    """分析线程"""
    # 信号
    chunk_received = pyqtSignal(str)    # 流式输出
    finished = pyqtSignal(bool, str)    # 完成信号 (成功, 内容/错误)
    
    def __init__(self, analyzer: AIAnalyzer, log_content: str, current_command: str = ""):
        super().__init__()
        self.analyzer = analyzer
        self.log_content = log_content
        self.current_command = current_command
    
    def run(self):
        try:
            # 使用整合的分析方法
            result = self.analyzer.analyze_and_suggest(
                self.log_content,
                self.current_command,
                callback=self._on_chunk
            )
            
            if result.success:
                self.finished.emit(True, result.content)
            else:
                self.finished.emit(False, result.error)
        except Exception as e:
            self.finished.emit(False, str(e))
    
    def _on_chunk(self, chunk: str):
        """流式输出回调"""
        self.chunk_received.emit(chunk)


class AIPanel(QWidget):
    """AI 分析面板"""
    
    # 信号 - 用于通知主窗口应用参数
    apply_params_requested = pyqtSignal(dict)  # 请求应用参数
    
    def __init__(self, config_manager, parent=None):
        super().__init__(parent)
        self.config = config_manager
        self.analyze_thread = None
        self._log_getter = None  # 获取日志的回调函数
        self._command_getter = None  # 获取当前命令的回调函数
        self._last_analysis_result = ""  # 保存最后一次分析结果
        self._safe_params = {}  # 安全方案参数
        self._aggressive_params = {}  # 激进方案参数
        self._current_scheme = 'safe'  # 当前选择的方案
        self.setup_ui()
    
    def setup_ui(self):
        """设置 UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        # ==================== 顶部工具栏 ====================
        toolbar = QHBoxLayout()
        toolbar.setSpacing(8)
        
        # 标题
        title_label = QLabel("🤖 智能分析")
        title_label.setStyleSheet("font-size: 14px; font-weight: bold;")
        toolbar.addWidget(title_label)
        
        # 说明
        desc_label = QLabel("分析日志，提供安全/激进两种方案")
        desc_label.setStyleSheet("color: #888; font-size: 12px;")
        toolbar.addWidget(desc_label)
        
        toolbar.addStretch()
        
        # AI 设置按钮
        settings_btn = QPushButton("⚙️ AI 设置")
        settings_btn.clicked.connect(self._show_ai_settings)
        toolbar.addWidget(settings_btn)
        
        layout.addLayout(toolbar)
        
        # ==================== 分析结果展示区 ====================
        self.result_text = QTextEdit()
        self.result_text.setReadOnly(True)
        self.result_text.setPlaceholderText(
            "AI 分析结果将显示在这里...\n\n"
            "点击「开始分析」按钮，AI 将自动：\n"
            "• 分析扫描日志，提取关键信息\n"
            "• 诊断遇到的问题\n"
            "• 提供 🟢 安全方案（推荐）\n"
            "• 提供 🔴 激进方案（谨慎使用）\n"
            "• 给出专家建议和手工测试思路\n\n"
            "您可以选择采纳安全方案或激进方案"
        )
        self.result_text.setStyleSheet("""
            QTextEdit {
                font-family: 'Microsoft YaHei', 'SimHei', sans-serif;
                font-size: 13px;
                line-height: 1.6;
            }
        """)
        layout.addWidget(self.result_text)
        
        # ==================== 方案选择区 ====================
        self.scheme_group = QGroupBox("📋 方案选择")
        self.scheme_group.setVisible(False)  # 初始隐藏
        scheme_layout = QVBoxLayout(self.scheme_group)
        
        # 方案单选按钮
        scheme_btn_layout = QHBoxLayout()
        self.scheme_btn_group = QButtonGroup(self)
        
        self.safe_radio = QRadioButton("🟢 安全方案（推荐）")
        self.safe_radio.setChecked(True)
        self.safe_radio.toggled.connect(lambda checked: self._on_scheme_changed('safe') if checked else None)
        self.scheme_btn_group.addButton(self.safe_radio)
        scheme_btn_layout.addWidget(self.safe_radio)
        
        self.aggressive_radio = QRadioButton("🔴 激进方案（谨慎）")
        self.aggressive_radio.toggled.connect(lambda checked: self._on_scheme_changed('aggressive') if checked else None)
        self.scheme_btn_group.addButton(self.aggressive_radio)
        scheme_btn_layout.addWidget(self.aggressive_radio)
        
        scheme_btn_layout.addStretch()
        scheme_layout.addLayout(scheme_btn_layout)
        
        # 参数展示
        self.params_label = QLabel("")
        self.params_label.setWordWrap(True)
        self.params_label.setStyleSheet("""
            QLabel {
                font-family: 'Consolas', 'Courier New', monospace;
                font-size: 12px;
                padding: 8px;
                background-color: rgba(122, 162, 247, 0.1);
                border-radius: 4px;
            }
        """)
        scheme_layout.addWidget(self.params_label)
        
        # 风险警告区域
        self.warning_frame = QFrame()
        self.warning_frame.setStyleSheet("""
            QFrame {
                background-color: rgba(247, 118, 142, 0.15);
                border: 1px solid rgba(247, 118, 142, 0.5);
                border-radius: 4px;
                padding: 8px;
            }
        """)
        self.warning_frame.setVisible(False)
        warning_layout = QVBoxLayout(self.warning_frame)
        warning_layout.setContentsMargins(8, 8, 8, 8)
        
        warning_title = QLabel("⚠️ 风险警告")
        warning_title.setStyleSheet("color: #f7768e; font-weight: bold;")
        warning_layout.addWidget(warning_title)
        
        self.warning_label = QLabel("")
        self.warning_label.setWordWrap(True)
        self.warning_label.setStyleSheet("color: #f7768e; font-size: 12px;")
        warning_layout.addWidget(self.warning_label)
        
        scheme_layout.addWidget(self.warning_frame)
        
        layout.addWidget(self.scheme_group)
        
        # ==================== 进度条 ====================
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 0)  # 不确定进度
        self.progress_bar.setVisible(False)
        self.progress_bar.setMaximumHeight(5)
        layout.addWidget(self.progress_bar)
        
        # ==================== 底部按钮 ====================
        bottom_layout = QHBoxLayout()
        bottom_layout.setSpacing(8)
        
        # 状态标签
        self.status_label = QLabel("就绪")
        self.status_label.setStyleSheet("color: #888;")
        bottom_layout.addWidget(self.status_label)
        
        bottom_layout.addStretch()
        
        # 复制按钮
        copy_btn = QPushButton("📋 复制")
        copy_btn.clicked.connect(self._copy_result)
        copy_btn.setMinimumWidth(80)
        bottom_layout.addWidget(copy_btn)
        
        # 清空按钮
        clear_btn = QPushButton("🗑️ 清空")
        clear_btn.clicked.connect(self._clear_result)
        clear_btn.setMinimumWidth(80)
        bottom_layout.addWidget(clear_btn)
        
        # 采纳推荐按钮
        self.apply_btn = QPushButton("✅ 采纳方案")
        self.apply_btn.setProperty("class", "success")
        self.apply_btn.clicked.connect(self._apply_recommendations)
        self.apply_btn.setMinimumWidth(110)
        self.apply_btn.setEnabled(False)  # 初始禁用
        self.apply_btn.setToolTip("分析完成后，选择并应用方案")
        bottom_layout.addWidget(self.apply_btn)
        
        # 开始分析按钮
        self.analyze_btn = QPushButton("🚀 开始分析")
        self.analyze_btn.setProperty("class", "primary")
        self.analyze_btn.clicked.connect(self._start_analyze)
        self.analyze_btn.setMinimumWidth(110)
        bottom_layout.addWidget(self.analyze_btn)
        
        layout.addLayout(bottom_layout)
    
    def set_log_getter(self, getter):
        """设置日志获取回调函数"""
        self._log_getter = getter
    
    def set_command_getter(self, getter):
        """设置命令获取回调函数"""
        self._command_getter = getter
    
    def _show_ai_settings(self):
        """显示 AI 设置对话框"""
        from ui.dialogs.ai_settings_dialog import AISettingsDialog
        dialog = AISettingsDialog(self.config, self)
        dialog.settings_saved.connect(self._on_settings_saved)
        dialog.exec()
    
    def _on_settings_saved(self):
        """AI 设置保存后的回调"""
        self.status_label.setText("AI 设置已更新")
    
    def _on_scheme_changed(self, scheme: str):
        """方案选择变化"""
        self._current_scheme = scheme
        self._update_params_display()
    
    def _start_analyze(self):
        """开始分析"""
        # 获取日志内容
        if self._log_getter:
            log_content = self._log_getter()
        else:
            log_content = ""
        
        if not log_content or not log_content.strip():
            QMessageBox.warning(self, "提示", "没有可分析的日志内容\n请先执行扫描")
            return
        
        # 获取当前命令
        current_command = ""
        if self._command_getter:
            current_command = self._command_getter()
        
        # 检查 AI 配置
        provider = self.config.get('AI', 'provider', 'ollama')
        if provider != 'ollama':
            key_name = f'{provider}_api_key'
            api_key = self.config.get('AI', key_name, '')
            if not api_key:
                QMessageBox.warning(
                    self, "配置错误", 
                    f"未配置 API Key\n请先在 AI 设置中配置"
                )
                return
        
        # 创建分析器
        try:
            analyzer = create_analyzer_from_config(self.config)
        except Exception as e:
            QMessageBox.critical(self, "错误", f"创建 AI 分析器失败: {e}")
            return
        
        # 开始分析
        self._set_analyzing_state(True)
        self.result_text.clear()
        self.scheme_group.setVisible(False)
        self._safe_params = {}
        self._aggressive_params = {}
        self.apply_btn.setEnabled(False)
        
        # 启动分析线程
        self.analyze_thread = AnalyzeThread(analyzer, log_content, current_command)
        self.analyze_thread.chunk_received.connect(self._on_chunk_received)
        self.analyze_thread.finished.connect(self._on_analyze_finished)
        self.analyze_thread.start()
    
    def _set_analyzing_state(self, analyzing: bool):
        """设置分析状态"""
        self.analyze_btn.setEnabled(not analyzing)
        self.progress_bar.setVisible(analyzing)
        
        if analyzing:
            self.analyze_btn.setText("分析中...")
            self.status_label.setText("正在分析...")
            self.status_label.setStyleSheet("color: #7aa2f7;")
        else:
            self.analyze_btn.setText("🚀 开始分析")
            self.status_label.setStyleSheet("color: #888;")
    
    @pyqtSlot(str)
    def _on_chunk_received(self, chunk: str):
        """接收流式输出"""
        self.result_text.moveCursor(QTextCursor.MoveOperation.End)
        self.result_text.insertPlainText(chunk)
        self.result_text.moveCursor(QTextCursor.MoveOperation.End)
    
    @pyqtSlot(bool, str)
    def _on_analyze_finished(self, success: bool, content: str):
        """分析完成"""
        self._set_analyzing_state(False)
        
        if success:
            # 如果没有流式输出，则设置完整内容
            if not self.result_text.toPlainText():
                self.result_text.setPlainText(content)
            
            # 保存分析结果
            self._last_analysis_result = self.result_text.toPlainText()
            
            # 解析两种方案的参数
            self._parse_schemes(self._last_analysis_result)
            
            self.status_label.setText("分析完成")
            self.status_label.setStyleSheet("color: #9ece6a;")
        else:
            self.result_text.setPlainText(f"❌ 分析失败\n\n{content}")
            self.status_label.setText("分析失败")
            self.status_label.setStyleSheet("color: #f7768e;")
    
    def _parse_schemes(self, content: str):
        """解析安全方案和激进方案"""
        # 解析安全方案 [SAFE]
        safe_match = re.search(r'\[SAFE\]\s*([^\n\[]*(?:\n(?!\[)[^\n]*)*)', content)
        if safe_match:
            safe_cmd = safe_match.group(1).strip()
            self._safe_params = self._parse_command_params(safe_cmd, is_safe=True)
        else:
            # 尝试从「安全方案」表格解析
            self._safe_params = self._parse_from_content(content, '安全方案', is_safe=True)
        
        # 解析激进方案 [AGGRESSIVE]
        aggressive_match = re.search(r'\[AGGRESSIVE\]\s*([^\n\[]*(?:\n(?!\[)[^\n]*)*)', content)
        if aggressive_match:
            aggressive_cmd = aggressive_match.group(1).strip()
            self._aggressive_params = self._parse_command_params(aggressive_cmd, is_safe=False)
        else:
            # 尝试从「激进方案」表格解析
            self._aggressive_params = self._parse_from_content(content, '激进方案', is_safe=False)
        
        # 显示方案选择区
        if self._safe_params or self._aggressive_params:
            self.scheme_group.setVisible(True)
            self.safe_radio.setChecked(True)
            self._current_scheme = 'safe'
            self._update_params_display()
            self.apply_btn.setEnabled(True)
        else:
            # 如果无法解析方案，尝试旧方式解析
            params = self._parse_command_params(content, is_safe=True)
            if params:
                self._safe_params = params
                self.scheme_group.setVisible(True)
                self.safe_radio.setChecked(True)
                self._update_params_display()
                self.apply_btn.setEnabled(True)
    
    def _parse_from_content(self, content: str, scheme_name: str, is_safe: bool = False) -> dict:
        """从内容中解析特定方案的参数"""
        # 找到方案段落
        pattern = rf'{scheme_name}.*?```\s*(.*?)```'
        match = re.search(pattern, content, re.DOTALL | re.IGNORECASE)
        if match:
            return self._parse_command_params(match.group(1), is_safe=is_safe)
        return {}
    
    def _parse_command_params(self, cmd: str, is_safe: bool = False) -> dict:
        """从命令字符串解析参数
        
        参数:
            cmd: 命令字符串
            is_safe: 是否为安全方案，如果是则过滤危险参数
        """
        params = {}
        
        # 安全方案禁止的危险功能
        DANGEROUS_FEATURES = ['os-shell', 'os-pwn', 'file-read', 'file-write', 'dump-all']
        
        # 如果是安全方案，检查并过滤危险功能
        if is_safe:
            for danger in DANGEROUS_FEATURES:
                if f'--{danger}' in cmd:
                    # 安全方案中跳过危险参数
                    continue
        
        # 解析 --tamper 参数
        tamper_match = re.search(r'--tamper[=\s]+["\']?([^"\'\s]+(?:,[^"\'\s]+)*)["\']?', cmd)
        if tamper_match:
            tamper_value = tamper_match.group(1)
            # 过滤无效的 tamper 值
            if tamper_value.lower() not in ['none', '无', 'no', 'null', 'xxx', '脚本名']:
                params['tamper'] = tamper_value
        
        # 解析 --technique 参数（支持多种格式）
        # 格式1: --technique=BEUT
        technique_match = re.search(r'--technique[=\s]+["\']?([BEUSTQ]+)["\']?', cmd, re.IGNORECASE)
        if technique_match:
            params['technique'] = technique_match.group(1).upper()
        else:
            # 格式2: 表格中的 | --technique | BEUT | 或 | technique | BEUT |
            technique_table_match = re.search(r'\|\s*-*technique\s*\|\s*([BEUSTQ]+)\s*\|', cmd, re.IGNORECASE)
            if technique_table_match:
                params['technique'] = technique_table_match.group(1).upper()
            else:
                # 格式3: 建议尝试 technique=B 或类似描述
                technique_suggest_match = re.search(r'technique[=:]\s*([BEUSTQ]+)', cmd, re.IGNORECASE)
                if technique_suggest_match:
                    technique_val = technique_suggest_match.group(1).upper()
                    # 如果当前解析的内容包含这个技术建议，添加到已有技术
                    if 'technique' not in params:
                        params['technique'] = technique_val
        
        # 解析 --level 参数
        level_match = re.search(r'--level[=\s]+(\d+)', cmd)
        if level_match:
            level = int(level_match.group(1))
            if 1 <= level <= 5:
                # 安全方案限制 level 最大为 3
                if is_safe and level > 3:
                    level = 3
                params['level'] = level
        
        # 解析 --risk 参数
        risk_match = re.search(r'--risk[=\s]+(\d+)', cmd)
        if risk_match:
            risk = int(risk_match.group(1))
            if 1 <= risk <= 3:
                # 安全方案限制 risk 为 1
                if is_safe and risk > 1:
                    risk = 1
                params['risk'] = risk
        
        # 解析 --threads 参数
        threads_match = re.search(r'--threads[=\s]+(\d+)', cmd)
        if threads_match:
            threads = int(threads_match.group(1))
            if 1 <= threads <= 10:
                # 安全方案限制线程数最大为 5
                if is_safe and threads > 5:
                    threads = 5
                params['threads'] = threads
        
        # 解析 --random-agent
        if '--random-agent' in cmd:
            params['random_agent'] = True
        
        # 解析 --proxy 参数
        proxy_match = re.search(r'--proxy[=\s]+["\']?([^"\'\s]+)["\']?', cmd)
        if proxy_match:
            params['proxy'] = proxy_match.group(1)
        
        # 解析 --dbms 参数
        dbms_match = re.search(r'--dbms[=\s]+["\']?(\w+)["\']?', cmd)
        if dbms_match:
            params['dbms'] = dbms_match.group(1)
        
        # 仅激进方案解析危险参数
        if not is_safe:
            if '--os-shell' in cmd:
                params['os_shell'] = True
            if '--os-pwn' in cmd:
                params['os_pwn'] = True
        
        return params
    
    def _update_params_display(self):
        """更新参数显示和警告"""
        params = self._safe_params if self._current_scheme == 'safe' else self._aggressive_params
        
        if not params:
            self.params_label.setText("未检测到可用参数")
            self.warning_frame.setVisible(False)
            return
        
        # 显示参数
        param_names = {
            'tamper': 'Tamper 脚本',
            'technique': '注入技术',
            'level': '扫描等级',
            'risk': '风险等级',
            'threads': '线程数',
            'random_agent': '随机 UA',
            'proxy': '代理',
            'dbms': '数据库类型',
            'os_shell': 'OS Shell',
            'os_pwn': 'OOB Shell'
        }
        
        param_lines = []
        warnings = []
        
        for key, value in params.items():
            name = param_names.get(key, key)
            if isinstance(value, bool):
                display_value = "是" if value else "否"
            else:
                display_value = str(value)
            param_lines.append(f"• {name}: {display_value}")
            
            # 检查危险参数
            if key in DANGEROUS_PARAMS:
                danger_info = DANGEROUS_PARAMS[key]
                if 'threshold' in danger_info:
                    if isinstance(value, int) and value >= danger_info['threshold']:
                        warnings.append(f"• {name}: {danger_info['warning']}")
                elif value:  # 布尔类型的危险参数
                    warnings.append(f"• {name}: {danger_info['warning']}")
        
        self.params_label.setText("\n".join(param_lines))
        
        # 显示警告
        if warnings or self._current_scheme == 'aggressive':
            if self._current_scheme == 'aggressive' and not warnings:
                warnings.append("• 激进方案可能触发安全设备告警或影响目标服务稳定性")
            self.warning_label.setText("\n".join(warnings))
            self.warning_frame.setVisible(True)
        else:
            self.warning_frame.setVisible(False)
    
    def _apply_recommendations(self):
        """应用推荐参数"""
        params = self._safe_params if self._current_scheme == 'safe' else self._aggressive_params
        
        if not params:
            QMessageBox.information(self, "提示", "没有可应用的推荐参数")
            return
        
        # 如果是激进方案或包含危险参数，显示确认对话框
        warnings = self._get_param_warnings(params)
        
        if warnings or self._current_scheme == 'aggressive':
            scheme_name = "激进方案" if self._current_scheme == 'aggressive' else "安全方案"
            warning_text = "\n".join(warnings) if warnings else "激进方案可能触发安全告警"
            
            reply = QMessageBox.warning(
                self, 
                f"⚠️ 确认应用{scheme_name}",
                f"您选择的方案包含以下风险：\n\n{warning_text}\n\n"
                "确定要应用这些参数吗？\n\n"
                "建议：在生产环境中谨慎使用激进参数",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
            
            if reply != QMessageBox.StandardButton.Yes:
                return
        
        # 发送信号通知主窗口应用参数
        self.apply_params_requested.emit(params)
        
        # 更新状态
        scheme_name = "安全方案" if self._current_scheme == 'safe' else "激进方案"
        self.status_label.setText(f"已应用{scheme_name}")
        self.status_label.setStyleSheet("color: #9ece6a;")
        
        # 显示提示
        param_count = len(params)
        QMessageBox.information(
            self, "应用成功", 
            f"已成功应用 {scheme_name} 的 {param_count} 个参数\n\n"
            "您可以在左侧面板查看和调整参数，然后开始新的扫描"
        )
    
    def _get_param_warnings(self, params: dict) -> list:
        """获取参数的风险警告"""
        warnings = []
        for key, value in params.items():
            if key in DANGEROUS_PARAMS:
                danger_info = DANGEROUS_PARAMS[key]
                if 'threshold' in danger_info:
                    if isinstance(value, int) and value >= danger_info['threshold']:
                        warnings.append(f"• {danger_info['warning']}")
                elif value:
                    warnings.append(f"• {danger_info['warning']}")
        return warnings
    
    def _copy_result(self):
        """复制分析结果"""
        text = self.result_text.toPlainText()
        if text:
            clipboard = QApplication.clipboard()
            clipboard.setText(text)
            self.status_label.setText("已复制到剪贴板")
    
    def _clear_result(self):
        """清空分析结果"""
        self.result_text.clear()
        self.scheme_group.setVisible(False)
        self._safe_params = {}
        self._aggressive_params = {}
        self.apply_btn.setEnabled(False)
        self.warning_frame.setVisible(False)
        self.status_label.setText("已清空")
    
    # ==================== 公共方法 ====================
    
    def get_parsed_params(self) -> dict:
        """获取当前选择方案的参数"""
        return self._safe_params.copy() if self._current_scheme == 'safe' else self._aggressive_params.copy()
