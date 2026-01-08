"""
AI 设置对话框
用于配置 AI 分析服务
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QComboBox, QGroupBox, QFormLayout, QMessageBox,
    QSpinBox, QDoubleSpinBox, QStackedWidget, QWidget, QTextEdit
)
from PyQt6.QtCore import pyqtSignal, Qt, QThread, pyqtSlot
from PyQt6.QtGui import QFont

from core.ai_analyzer import AIProvider, AI_PROVIDER_PRESETS, AIConfig, AIAnalyzer


class TestConnectionThread(QThread):
    """测试连接的后台线程"""
    finished = pyqtSignal(bool, str)
    
    def __init__(self, analyzer: AIAnalyzer):
        super().__init__()
        self.analyzer = analyzer
    
    def run(self):
        result = self.analyzer.test_connection()
        self.finished.emit(result.success, result.content if result.success else result.error)


class AISettingsDialog(QDialog):
    """AI 设置对话框"""
    
    # 信号
    settings_saved = pyqtSignal()
    
    def __init__(self, config_manager, parent=None):
        super().__init__(parent)
        self.config = config_manager
        self.test_thread = None
        self.setWindowTitle("🤖 AI 设置")
        self.setMinimumSize(550, 580)
        self.setup_ui()
        self.load_settings()
    
    def setup_ui(self):
        """设置 UI"""
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        
        # AI 服务选择
        provider_group = QGroupBox("🔌 AI 服务选择")
        provider_layout = QFormLayout(provider_group)
        
        self.provider_combo = QComboBox()
        # 添加所有支持的 AI 服务
        provider_order = [
            AIProvider.OLLAMA,
            AIProvider.DEEPSEEK,
            AIProvider.QWEN,
            AIProvider.ZHIPU,
            AIProvider.MOONSHOT,
            AIProvider.OPENAI,
            AIProvider.CLAUDE,
            AIProvider.CUSTOM,
        ]
        for provider in provider_order:
            preset = AI_PROVIDER_PRESETS[provider]
            self.provider_combo.addItem(preset["name"], provider.value)
        
        self.provider_combo.currentIndexChanged.connect(self._on_provider_changed)
        provider_layout.addRow("选择服务:", self.provider_combo)
        
        layout.addWidget(provider_group)
        
        # 配置区域 - 使用堆叠布局
        self.config_stack = QStackedWidget()
        
        # 本地模型配置页面
        self.local_page = self._create_local_config_page()
        self.config_stack.addWidget(self.local_page)
        
        # 在线 API 配置页面
        self.api_page = self._create_api_config_page()
        self.config_stack.addWidget(self.api_page)
        
        layout.addWidget(self.config_stack)
        
        # 高级设置
        advanced_group = QGroupBox("⚙️ 高级设置")
        advanced_layout = QFormLayout(advanced_group)
        
        self.max_tokens_spin = QSpinBox()
        self.max_tokens_spin.setRange(100, 8000)
        self.max_tokens_spin.setValue(2000)
        self.max_tokens_spin.setSingleStep(100)
        advanced_layout.addRow("最大 Token 数:", self.max_tokens_spin)
        
        self.temperature_spin = QDoubleSpinBox()
        self.temperature_spin.setRange(0.0, 2.0)
        self.temperature_spin.setValue(0.7)
        self.temperature_spin.setSingleStep(0.1)
        self.temperature_spin.setDecimals(1)
        advanced_layout.addRow("Temperature:", self.temperature_spin)
        
        self.timeout_spin = QSpinBox()
        self.timeout_spin.setRange(10, 300)
        self.timeout_spin.setValue(60)
        self.timeout_spin.setSuffix(" 秒")
        advanced_layout.addRow("请求超时:", self.timeout_spin)
        
        layout.addWidget(advanced_group)
        
        # 测试连接区域
        test_group = QGroupBox("🔗 连接测试")
        test_layout = QVBoxLayout(test_group)
        
        test_btn_layout = QHBoxLayout()
        self.test_btn = QPushButton("测试连接")
        self.test_btn.clicked.connect(self._test_connection)
        test_btn_layout.addWidget(self.test_btn)
        test_btn_layout.addStretch()
        test_layout.addLayout(test_btn_layout)
        
        self.test_result_label = QLabel("点击上方按钮测试与 AI 服务的连接")
        self.test_result_label.setWordWrap(True)
        self.test_result_label.setStyleSheet("color: #888; padding: 5px;")
        test_layout.addWidget(self.test_result_label)
        
        layout.addWidget(test_group)
        
        # 按钮区
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        save_btn = QPushButton("保存")
        save_btn.setMinimumWidth(80)
        save_btn.setProperty("class", "primary")
        save_btn.clicked.connect(self._save_settings)
        btn_layout.addWidget(save_btn)
        
        cancel_btn = QPushButton("取消")
        cancel_btn.setMinimumWidth(80)
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)
        
        layout.addLayout(btn_layout)
    
    def _create_local_config_page(self) -> QWidget:
        """创建本地模型配置页面"""
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 0, 0, 0)
        
        group = QGroupBox("🖥️ 本地模型配置 (Ollama)")
        form_layout = QFormLayout(group)
        
        self.ollama_url_input = QLineEdit()
        self.ollama_url_input.setPlaceholderText("http://localhost:11434")
        form_layout.addRow("服务地址:", self.ollama_url_input)
        
        self.ollama_model_input = QLineEdit()
        self.ollama_model_input.setPlaceholderText("qwen2:7b")
        form_layout.addRow("模型名称:", self.ollama_model_input)
        
        # 提示信息
        tip_label = QLabel("提示: 需要先安装并运行 Ollama，然后拉取模型 (ollama pull qwen2:7b)")
        tip_label.setStyleSheet("color: #888; font-size: 11px;")
        tip_label.setWordWrap(True)
        form_layout.addRow("", tip_label)
        
        layout.addWidget(group)
        layout.addStretch()
        return page
    
    def _create_api_config_page(self) -> QWidget:
        """创建在线 API 配置页面"""
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 0, 0, 0)
        
        group = QGroupBox("☁️ 在线 API 配置")
        form_layout = QFormLayout(group)
        
        self.api_key_input = QLineEdit()
        self.api_key_input.setPlaceholderText("sk-xxxxxxxxxxxxxxxxxxxxxxxx")
        self.api_key_input.setEchoMode(QLineEdit.EchoMode.Password)
        form_layout.addRow("API Key:", self.api_key_input)
        
        # 显示/隐藏 API Key 按钮
        show_key_btn = QPushButton("👁")
        show_key_btn.setFixedWidth(35)
        show_key_btn.setCheckable(True)
        show_key_btn.toggled.connect(
            lambda checked: self.api_key_input.setEchoMode(
                QLineEdit.EchoMode.Normal if checked else QLineEdit.EchoMode.Password
            )
        )
        
        key_layout = QHBoxLayout()
        key_layout.addWidget(self.api_key_input)
        key_layout.addWidget(show_key_btn)
        form_layout.addRow("API Key:", key_layout)
        
        self.api_base_url_input = QLineEdit()
        self.api_base_url_input.setPlaceholderText("API 地址将自动填充")
        form_layout.addRow("API 地址:", self.api_base_url_input)
        
        self.api_model_input = QLineEdit()
        self.api_model_input.setPlaceholderText("模型名称将自动填充")
        form_layout.addRow("模型:", self.api_model_input)
        
        # 提示信息
        self.api_tip_label = QLabel("")
        self.api_tip_label.setStyleSheet("color: #888; font-size: 11px;")
        self.api_tip_label.setWordWrap(True)
        form_layout.addRow("", self.api_tip_label)
        
        layout.addWidget(group)
        layout.addStretch()
        return page
    
    def _on_provider_changed(self, index):
        """切换 AI 服务提供商"""
        provider_value = self.provider_combo.currentData()
        try:
            provider = AIProvider(provider_value)
        except ValueError:
            provider = AIProvider.OLLAMA
        
        preset = AI_PROVIDER_PRESETS[provider]
        
        if provider == AIProvider.OLLAMA:
            # 显示本地配置页面
            self.config_stack.setCurrentIndex(0)
            self.ollama_url_input.setText(preset["base_url"])
            self.ollama_model_input.setText(preset["default_model"])
        else:
            # 显示在线 API 配置页面
            self.config_stack.setCurrentIndex(1)
            self.api_base_url_input.setText(preset["base_url"])
            self.api_model_input.setText(preset["default_model"])
            
            # 更新提示信息
            tips = {
                AIProvider.DEEPSEEK: "推荐: 性价比极高，访问 https://platform.deepseek.com 获取 API Key",
                AIProvider.QWEN: "访问 https://dashscope.console.aliyun.com 获取 API Key",
                AIProvider.ZHIPU: "访问 https://open.bigmodel.cn 获取 API Key",
                AIProvider.MOONSHOT: "访问 https://platform.moonshot.cn 获取 API Key",
                AIProvider.OPENAI: "访问 https://platform.openai.com 获取 API Key",
                AIProvider.CLAUDE: "访问 https://console.anthropic.com 获取 API Key",
                AIProvider.CUSTOM: "输入任意兼容 OpenAI API 格式的服务地址",
            }
            self.api_tip_label.setText(tips.get(provider, ""))
            
            # 如果是自定义 API，允许编辑地址
            is_custom = provider == AIProvider.CUSTOM
            self.api_base_url_input.setReadOnly(not is_custom)
            if is_custom:
                self.api_base_url_input.clear()
                self.api_model_input.clear()
        
        # 加载该服务商保存的配置
        self._load_provider_settings(provider)
    
    def _load_provider_settings(self, provider: AIProvider):
        """加载指定服务商的配置"""
        if provider == AIProvider.OLLAMA:
            url = self.config.get('AI', 'ollama_url', 'http://localhost:11434')
            model = self.config.get('AI', 'ollama_model', 'qwen2:7b')
            self.ollama_url_input.setText(url)
            self.ollama_model_input.setText(model)
        else:
            # 获取对应服务商的配置键前缀
            key_prefix = provider.value
            api_key = self.config.get('AI', f'{key_prefix}_api_key', '')
            model = self.config.get('AI', f'{key_prefix}_model', AI_PROVIDER_PRESETS[provider]["default_model"])
            
            self.api_key_input.setText(api_key)
            self.api_model_input.setText(model)
            
            if provider == AIProvider.CUSTOM:
                base_url = self.config.get('AI', 'custom_base_url', '')
                self.api_base_url_input.setText(base_url)
    
    def load_settings(self):
        """加载配置"""
        # 加载当前选择的服务商
        provider_value = self.config.get('AI', 'provider', 'ollama')
        index = self.provider_combo.findData(provider_value)
        if index >= 0:
            self.provider_combo.setCurrentIndex(index)
        
        # 加载高级设置
        self.max_tokens_spin.setValue(self.config.get_int('AI', 'max_tokens', 2000))
        self.temperature_spin.setValue(self.config.get_float('AI', 'temperature', 0.7))
        self.timeout_spin.setValue(self.config.get_int('AI', 'timeout', 60))
        
        # 触发一次服务商变更以加载对应配置
        self._on_provider_changed(self.provider_combo.currentIndex())
    
    def _get_current_config(self) -> AIConfig:
        """获取当前配置"""
        provider_value = self.provider_combo.currentData()
        try:
            provider = AIProvider(provider_value)
        except ValueError:
            provider = AIProvider.OLLAMA
        
        if provider == AIProvider.OLLAMA:
            return AIConfig(
                provider=provider,
                base_url=self.ollama_url_input.text() or "http://localhost:11434",
                model=self.ollama_model_input.text() or "qwen2:7b",
                max_tokens=self.max_tokens_spin.value(),
                temperature=self.temperature_spin.value(),
                timeout=self.timeout_spin.value()
            )
        else:
            base_url = self.api_base_url_input.text()
            if not base_url:
                base_url = AI_PROVIDER_PRESETS[provider]["base_url"]
            
            return AIConfig(
                provider=provider,
                api_key=self.api_key_input.text(),
                base_url=base_url,
                model=self.api_model_input.text() or AI_PROVIDER_PRESETS[provider]["default_model"],
                max_tokens=self.max_tokens_spin.value(),
                temperature=self.temperature_spin.value(),
                timeout=self.timeout_spin.value()
            )
    
    def _test_connection(self):
        """测试连接"""
        config = self._get_current_config()
        
        # 验证必填项
        if config.provider != AIProvider.OLLAMA and not config.api_key:
            QMessageBox.warning(self, "提示", "请先填写 API Key")
            return
        
        self.test_btn.setEnabled(False)
        self.test_btn.setText("测试中...")
        self.test_result_label.setText("正在连接...")
        self.test_result_label.setStyleSheet("color: #888; padding: 5px;")
        
        # 在后台线程测试
        analyzer = AIAnalyzer(config)
        self.test_thread = TestConnectionThread(analyzer)
        self.test_thread.finished.connect(self._on_test_finished)
        self.test_thread.start()
    
    @pyqtSlot(bool, str)
    def _on_test_finished(self, success: bool, message: str):
        """测试完成回调"""
        self.test_btn.setEnabled(True)
        self.test_btn.setText("测试连接")
        
        if success:
            self.test_result_label.setText(f"✅ {message}")
            self.test_result_label.setStyleSheet("color: #9ece6a; padding: 5px;")
        else:
            self.test_result_label.setText(f"❌ {message}")
            self.test_result_label.setStyleSheet("color: #f7768e; padding: 5px;")
    
    def _save_settings(self):
        """保存设置"""
        provider_value = self.provider_combo.currentData()
        try:
            provider = AIProvider(provider_value)
        except ValueError:
            provider = AIProvider.OLLAMA
        
        # 保存当前服务商
        self.config.set('AI', 'provider', provider.value)
        
        # 保存对应服务商的配置
        if provider == AIProvider.OLLAMA:
            self.config.set('AI', 'ollama_url', self.ollama_url_input.text())
            self.config.set('AI', 'ollama_model', self.ollama_model_input.text())
        else:
            key_prefix = provider.value
            self.config.set('AI', f'{key_prefix}_api_key', self.api_key_input.text())
            self.config.set('AI', f'{key_prefix}_model', self.api_model_input.text())
            
            if provider == AIProvider.CUSTOM:
                self.config.set('AI', 'custom_base_url', self.api_base_url_input.text())
        
        # 保存高级设置
        self.config.set('AI', 'max_tokens', str(self.max_tokens_spin.value()))
        self.config.set('AI', 'temperature', str(self.temperature_spin.value()))
        self.config.set('AI', 'timeout', str(self.timeout_spin.value()))
        
        self.config.save()
        self.settings_saved.emit()
        
        QMessageBox.information(self, "保存成功", "AI 设置已保存")
        self.accept()
