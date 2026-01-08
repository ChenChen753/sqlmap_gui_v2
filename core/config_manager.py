"""
配置管理器
管理应用配置和用户设置
"""

import os
import configparser
from typing import Any, Optional


class ConfigManager:
    """配置管理器"""
    
    # 默认配置
    DEFAULT_CONFIG = {
        'General': {
            'sqlmap_path': 'python ../sqlmap-master/sqlmap.py',
            'language': 'zh_CN',
            'auto_save': 'true',
        },
        'Scan': {
            'default_level': '1',
            'default_risk': '1',
            'default_threads': '3',
            'default_timeout': '30',
            'default_retries': '3',
            'default_delay': '0',
        },
        'UI': {
            'window_width': '1400',
            'window_height': '900',
            'window_x': '100',
            'window_y': '100',
            'theme': 'dark',
            'font_size': '13',
        },
        'Advanced': {
            'batch_mode': 'true',
            'fresh_queries': 'true',
            'random_agent': 'false',
        },
        'AI': {
            # 当前选择的 AI 服务
            'provider': 'ollama',
            
            # Ollama 本地模型
            'ollama_url': 'http://localhost:11434',
            'ollama_model': 'qwen2:7b',
            
            # OpenAI
            'openai_api_key': '',
            'openai_base_url': 'https://api.openai.com/v1',
            'openai_model': 'gpt-4o-mini',
            
            # Claude
            'claude_api_key': '',
            'claude_base_url': 'https://api.anthropic.com',
            'claude_model': 'claude-3-haiku-20240307',
            
            # DeepSeek（国内推荐）
            'deepseek_api_key': '',
            'deepseek_model': 'deepseek-chat',
            
            # 阿里通义千问
            'qwen_api_key': '',
            'qwen_model': 'qwen-turbo',
            
            # 智谱 GLM
            'zhipu_api_key': '',
            'zhipu_model': 'glm-4-flash',
            
            # 月之暗面 Kimi
            'moonshot_api_key': '',
            'moonshot_model': 'moonshot-v1-8k',
            
            # 自定义 API
            'custom_api_key': '',
            'custom_base_url': '',
            'custom_model': '',
            
            # 通用参数
            'max_tokens': '2000',
            'temperature': '0.7',
            'timeout': '60',
        }
    }
    
    def __init__(self, config_path: str = None):
        """
        初始化配置管理器
        
        参数:
            config_path: 配置文件路径，默认为脚本所在目录的 config.ini
        """
        if config_path is None:
            script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            config_path = os.path.join(script_dir, 'config.ini')
        
        self.config_path = config_path
        self.config = configparser.ConfigParser()
        
        # 加载或创建配置
        self.load_or_create()
    
    def load_or_create(self):
        """加载配置文件，如果不存在则创建默认配置"""
        if os.path.exists(self.config_path):
            self.config.read(self.config_path, encoding='utf-8')
            # 补充缺失的默认值
            self._ensure_defaults()
        else:
            self._create_default_config()
    
    def _create_default_config(self):
        """创建默认配置文件"""
        for section, options in self.DEFAULT_CONFIG.items():
            self.config[section] = options
        self.save()
    
    def _ensure_defaults(self):
        """确保所有默认配置项都存在"""
        modified = False
        for section, options in self.DEFAULT_CONFIG.items():
            if section not in self.config:
                self.config[section] = options
                modified = True
            else:
                for key, value in options.items():
                    if key not in self.config[section]:
                        self.config[section][key] = value
                        modified = True
        
        if modified:
            self.save()
    
    def save(self):
        """保存配置到文件"""
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                self.config.write(f)
            return True
        except Exception as e:
            print(f"保存配置失败: {e}")
            return False
    
    def get(self, section: str, key: str, fallback: Any = None) -> str:
        """获取配置值"""
        try:
            return self.config.get(section, key, fallback=fallback)
        except (configparser.NoSectionError, configparser.NoOptionError):
            return fallback
    
    def get_int(self, section: str, key: str, fallback: int = 0) -> int:
        """获取整数配置值"""
        try:
            return self.config.getint(section, key, fallback=fallback)
        except (configparser.NoSectionError, configparser.NoOptionError, ValueError):
            return fallback
    
    def get_bool(self, section: str, key: str, fallback: bool = False) -> bool:
        """获取布尔配置值"""
        try:
            return self.config.getboolean(section, key, fallback=fallback)
        except (configparser.NoSectionError, configparser.NoOptionError, ValueError):
            return fallback
    
    def get_float(self, section: str, key: str, fallback: float = 0.0) -> float:
        """获取浮点数配置值"""
        try:
            return self.config.getfloat(section, key, fallback=fallback)
        except (configparser.NoSectionError, configparser.NoOptionError, ValueError):
            return fallback
    
    def set(self, section: str, key: str, value: Any) -> bool:
        """设置配置值"""
        try:
            if section not in self.config:
                self.config[section] = {}
            self.config[section][key] = str(value)
            return True
        except Exception:
            return False
    
    # ==================== 便捷方法 ====================
    
    @property
    def sqlmap_path(self) -> str:
        """获取 sqlmap 路径"""
        return self.get('General', 'sqlmap_path', 'python sqlmap.py')
    
    @sqlmap_path.setter
    def sqlmap_path(self, value: str):
        """设置 sqlmap 路径"""
        self.set('General', 'sqlmap_path', value)
    
    @property
    def default_level(self) -> int:
        """获取默认扫描等级"""
        return self.get_int('Scan', 'default_level', 1)
    
    @property
    def default_risk(self) -> int:
        """获取默认风险等级"""
        return self.get_int('Scan', 'default_risk', 1)
    
    @property
    def default_threads(self) -> int:
        """获取默认线程数"""
        return self.get_int('Scan', 'default_threads', 3)
    
    @property
    def window_size(self) -> tuple:
        """获取窗口大小"""
        width = self.get_int('UI', 'window_width', 1400)
        height = self.get_int('UI', 'window_height', 900)
        return (width, height)
    
    @property
    def window_position(self) -> tuple:
        """获取窗口位置"""
        x = self.get_int('UI', 'window_x', 100)
        y = self.get_int('UI', 'window_y', 100)
        return (x, y)
    
    def save_window_geometry(self, x: int, y: int, width: int, height: int):
        """保存窗口几何信息"""
        self.set('UI', 'window_x', x)
        self.set('UI', 'window_y', y)
        self.set('UI', 'window_width', width)
        self.set('UI', 'window_height', height)
        self.save()
