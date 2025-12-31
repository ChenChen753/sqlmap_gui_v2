"""
多语言支持模块
支持中文和英文界面切换
"""

from typing import Dict, Optional
import json
import os

# 当前语言
_current_language = "zh_CN"

# 翻译字典
TRANSLATIONS = {
    "zh_CN": {
        # 窗口标题
        "app_title": "🔒 SQLMap GUI v2",
        "app_subtitle": "智能 SQL 注入检测工具",
        
        # 菜单
        "menu_file": "文件",
        "menu_tools": "工具",
        "menu_help": "帮助",
        "menu_new_config": "新建配置",
        "menu_load_config": "加载配置",
        "menu_save_config": "保存配置",
        "menu_exit": "退出",
        "menu_settings": "设置",
        "menu_history": "扫描历史",
        "menu_clear_history": "清空历史",
        "menu_about": "关于",
        "menu_language": "语言",
        
        # 标签页
        "tab_target": "🎯 目标",
        "tab_scan": "⚙️ 扫描",
        "tab_advanced": "🔧 高级",
        "tab_log": "📜 日志",
        "tab_result": "📊 结果",
        
        # 目标面板
        "target_settings": "🎯 目标设置",
        "target_url": "目标 URL",
        "target_url_placeholder": "输入目标 URL, 例如: http://example.com/page.php?id=1",
        "btn_paste": "📋 粘贴",
        "btn_clear": "🗑️ 清空",
        "file_scan": "📁 文件扫描",
        "file_scan_placeholder": "选择包含 URL 列表的文件...",
        "btn_browse": "浏览...",
        "request_config": "📡 请求配置",
        "request_method": "请求方式:",
        "specify_param": "指定参数:",
        "specify_param_placeholder": "如: id, name",
        "post_data": "POST 数据:",
        "post_data_placeholder": "如: username=admin&password=pass",
        "cookie": "Cookie:",
        "cookie_placeholder": "如: PHPSESSID=abc123; token=xyz",
        "user_agent": "User-Agent:",
        "random_ua": "随机 User-Agent",
        
        # 扫描面板
        "quick_config": "⚡ 快速配置",
        "mode_quick": "🚀 快速检测",
        "mode_quick_desc": "Level 1, Risk 1 - 快速判断是否存在注入",
        "mode_standard": "🔍 标准扫描",
        "mode_standard_desc": "Level 2, Risk 2 - 平衡速度和深度，推荐日常使用",
        "mode_deep": "🔬 深度扫描",
        "mode_deep_desc": "Level 5, Risk 3 - 全面深入扫描，适合关键目标",
        "mode_aggressive": "⚔️ 激进模式",
        "mode_aggressive_desc": "全部技术 + 绕过 WAF，最全面但可能触发防护",
        "mode_custom": "⚙️ 自定义",
        "mode_custom_desc": "手动配置所有参数",
        "detection_config": "🎯 检测配置",
        "scan_level": "扫描等级:",
        "risk_level": "风险等级:",
        "level_default": "默认 (不指定)",
        "level_basic": "基础",
        "level_light": "轻度",
        "level_medium": "中度",
        "level_deep": "深度",
        "level_full": "完全",
        "risk_safe": "安全",
        "risk_medium": "中等",
        "risk_aggressive": "激进",
        "injection_technique": "注入技术:",
        "tech_boolean": "布尔盲注",
        "tech_error": "报错注入",
        "tech_union": "联合查询",
        "tech_stacked": "堆叠查询",
        "tech_time": "时间盲注",
        "tech_inline": "内联查询",
        "info_enum": "📊 信息枚举",
        "get_current_db": "当前数据库",
        "get_current_user": "当前用户",
        "get_banner": "数据库版本",
        "get_hostname": "主机名",
        "get_is_dba": "是否 DBA",
        "get_users": "枚举用户",
        "get_dbs": "枚举数据库",
        "get_tables": "枚举表",
        "get_columns": "枚举列",
        "get_schema": "枚举架构",
        "get_count": "统计数量",
        "get_privileges": "用户权限",
        "get_passwords": "枚举密码",
        "get_roles": "用户角色",
        "get_comments": "表注释",
        "data_extract": "📥 数据提取",
        "dump_data": "提取数据",
        "dump_all": "提取全部",
        "search_data": "搜索数据:",
        "limit_rows": "限制行数:",
        "start": "起始:",
        "end": "结束:",
        
        # 高级面板
        "performance_config": "⚡ 性能配置",
        "threads": "线程数:",
        "timeout": "超时 (秒):",
        "retries": "重试次数:",
        "delay": "请求延迟 (秒):",
        "general_options": "🔧 通用选项",
        "batch_mode": "批处理模式",
        "flush_session": "刷新会话",
        "fresh_queries": "禁用缓存",
        "parse_forms": "解析表单",
        "crawl": "爬取网站",
        "smart_mode": "智能模式",
        "null_connection": "空连接检测",
        "text_only": "仅比较文本",
        "no_cast": "禁用类型转换",
        "tamper_scripts": "🛡️ Tamper 脚本",
        "tamper_category": "分类:",
        "tamper_all": "全部",
        "tamper_preset": "快速预设:",
        "tamper_custom": "自定义 Tamper:",
        "tamper_custom_placeholder": "输入 tamper 脚本名，逗号分隔",
        "proxy_config": "🌐 代理配置",
        "proxy": "代理地址:",
        "proxy_placeholder": "如: http://127.0.0.1:8080",
        "use_tor": "使用 Tor 网络",
        "tor_type": "Tor 类型:",
        "request_options": "📡 请求选项",
        "random_agent": "随机 User-Agent",
        "mobile_emulation": "移动端模拟",
        "safe_url": "安全 URL 访问",
        "skip_waf": "跳过 WAF 检测",
        "hpp": "HTTP 参数污染",
        "chunked": "分块传输编码",
        "db_config": "🗄️ 数据库配置",
        "dbms_type": "数据库类型:",
        "dbms_auto": "自动检测",
        "target_db": "指定数据库:",
        "target_table": "指定表:",
        "target_columns": "指定列:",
        "os_features": "💻 操作系统功能",
        "os_shell": "获取 OS Shell",
        "os_pwn": "OOB Shell (Meterpreter)",
        "os_cmd": "执行命令:",
        "file_read": "读取文件:",
        "file_write": "写入文件:",
        
        # 日志面板
        "search_log": "🔍 搜索日志...",
        "auto_scroll": "自动滚动",
        "log_count": "共 {count} 条日志",
        "btn_clear_log": "🗑️ 清空",
        "btn_save_log": "💾 保存",
        "btn_copy_log": "📋 复制",
        
        # 结果面板
        "stat_vulnerabilities": "发现漏洞",
        "stat_databases": "数据库",
        "stat_tables": "数据表",
        "stat_time": "耗时",
        "injection_info": "🎯 注入信息",
        "db_structure": "🗄️ 数据库结构",
        "data_content": "📊 数据内容",
        "export_csv": "📥 导出 CSV",
        "export_json": "📥 导出 JSON",
        
        # 控制栏
        "command_preview": "命令预览: 请配置扫描参数...",
        "btn_start": "▶ 开始扫描",
        "btn_stop": "⏹ 停止",
        "status_ready": "● 就绪",
        "status_scanning": "● 扫描中...",
        "status_completed": "● 完成",
        "status_stopped": "● 已停止",
        "status_error": "● 错误",
        
        # 对话框
        "settings_title": "⚙️ 设置",
        "settings_general": "🔧 常规",
        "settings_appearance": "🎨 外观",
        "settings_sqlmap_path": "SQLMap 路径:",
        "settings_python_path": "Python 路径:",
        "settings_auto_detect": "🔍 自动检测 SQLMap",
        "settings_default_threads": "默认线程数:",
        "settings_default_timeout": "默认超时:",
        "settings_theme": "界面主题:",
        "settings_font_size": "字体大小:",
        "btn_apply": "应用",
        "btn_ok": "确定",
        "btn_cancel": "取消",
        "about_title": "关于 SQLMap GUI v2",
        "about_version": "版本 2.0.0",
        "about_author": "开发作者",
        "about_author_name": "✨ 辰辰 ✨",
        "about_warning": "⚠️ 本工具仅供授权安全测试使用",
        "about_description": """SQLMap GUI v2 是一款现代化的 SQL 注入检测图形化工具，
基于强大的 sqlmap 开源项目开发。
本工具提供友好的图形界面，让 SQL 注入检测更加简单高效。
支持多种注入技术、绕过脚本、数据提取等功能。""",
        
        # 消息
        "msg_confirm": "确认",
        "msg_info": "提示",
        "msg_warning": "警告",
        "msg_error": "错误",
        "msg_clear_history": "确定要清除所有扫描历史吗？",
        "msg_history_cleared": "已清除 {count} 条历史记录。",
        "msg_config_saved": "配置已保存。",
        "msg_sqlmap_found": "找到 SQLMap:",
        "msg_sqlmap_not_found": "未能自动检测到 SQLMap，请手动选择路径。",
        "msg_no_target": "请输入目标 URL",
        "msg_scan_started": "扫描已开始",
        "msg_scan_stopped": "扫描已停止",
        "msg_scan_completed": "扫描完成",
    },
    
    "en_US": {
        # Window title
        "app_title": "🔒 SQLMap GUI v2",
        "app_subtitle": "Intelligent SQL Injection Detection Tool",
        
        # Menu
        "menu_file": "File",
        "menu_tools": "Tools",
        "menu_help": "Help",
        "menu_new_config": "New Config",
        "menu_load_config": "Load Config",
        "menu_save_config": "Save Config",
        "menu_exit": "Exit",
        "menu_settings": "Settings",
        "menu_history": "Scan History",
        "menu_clear_history": "Clear History",
        "menu_about": "About",
        "menu_language": "Language",
        
        # Tabs
        "tab_target": "🎯 Target",
        "tab_scan": "⚙️ Scan",
        "tab_advanced": "🔧 Advanced",
        "tab_log": "📜 Log",
        "tab_result": "📊 Result",
        
        # Target panel
        "target_settings": "🎯 Target Settings",
        "target_url": "Target URL",
        "target_url_placeholder": "Enter target URL, e.g.: http://example.com/page.php?id=1",
        "btn_paste": "📋 Paste",
        "btn_clear": "🗑️ Clear",
        "file_scan": "📁 File Scan",
        "file_scan_placeholder": "Select file containing URL list...",
        "btn_browse": "Browse...",
        "request_config": "📡 Request Config",
        "request_method": "Method:",
        "specify_param": "Parameter:",
        "specify_param_placeholder": "e.g.: id, name",
        "post_data": "POST Data:",
        "post_data_placeholder": "e.g.: username=admin&password=pass",
        "cookie": "Cookie:",
        "cookie_placeholder": "e.g.: PHPSESSID=abc123; token=xyz",
        "user_agent": "User-Agent:",
        "random_ua": "Random User-Agent",
        
        # Scan panel
        "quick_config": "⚡ Quick Config",
        "mode_quick": "🚀 Quick Detect",
        "mode_quick_desc": "Level 1, Risk 1 - Quick injection detection",
        "mode_standard": "🔍 Standard Scan",
        "mode_standard_desc": "Level 2, Risk 2 - Balanced speed and depth, recommended",
        "mode_deep": "🔬 Deep Scan",
        "mode_deep_desc": "Level 5, Risk 3 - Comprehensive scan for critical targets",
        "mode_aggressive": "⚔️ Aggressive",
        "mode_aggressive_desc": "All techniques + WAF bypass, most thorough",
        "mode_custom": "⚙️ Custom",
        "mode_custom_desc": "Manually configure all parameters",
        "detection_config": "🎯 Detection Config",
        "scan_level": "Level:",
        "risk_level": "Risk:",
        "level_default": "Default (none)",
        "level_basic": "Basic",
        "level_light": "Light",
        "level_medium": "Medium",
        "level_deep": "Deep",
        "level_full": "Full",
        "risk_safe": "Safe",
        "risk_medium": "Medium",
        "risk_aggressive": "Aggressive",
        "injection_technique": "Technique:",
        "tech_boolean": "Boolean Blind",
        "tech_error": "Error-based",
        "tech_union": "UNION Query",
        "tech_stacked": "Stacked Queries",
        "tech_time": "Time Blind",
        "tech_inline": "Inline Query",
        "info_enum": "📊 Enumeration",
        "get_current_db": "Current Database",
        "get_current_user": "Current User",
        "get_banner": "DB Version",
        "get_hostname": "Hostname",
        "get_is_dba": "Is DBA",
        "get_users": "Enum Users",
        "get_dbs": "Enum Databases",
        "get_tables": "Enum Tables",
        "get_columns": "Enum Columns",
        "get_schema": "Enum Schema",
        "get_count": "Count",
        "get_privileges": "Privileges",
        "get_passwords": "Passwords",
        "get_roles": "Roles",
        "get_comments": "Comments",
        "data_extract": "📥 Data Extraction",
        "dump_data": "Dump Data",
        "dump_all": "Dump All",
        "search_data": "Search:",
        "limit_rows": "Limit Rows:",
        "start": "Start:",
        "end": "End:",
        
        # Advanced panel
        "performance_config": "⚡ Performance",
        "threads": "Threads:",
        "timeout": "Timeout (s):",
        "retries": "Retries:",
        "delay": "Delay (s):",
        "general_options": "🔧 General Options",
        "batch_mode": "Batch Mode",
        "flush_session": "Flush Session",
        "fresh_queries": "Fresh Queries",
        "parse_forms": "Parse Forms",
        "crawl": "Crawl",
        "smart_mode": "Smart Mode",
        "null_connection": "Null Connection",
        "text_only": "Text Only",
        "no_cast": "No Cast",
        "tamper_scripts": "🛡️ Tamper Scripts",
        "tamper_category": "Category:",
        "tamper_all": "All",
        "tamper_preset": "Preset:",
        "tamper_custom": "Custom Tamper:",
        "tamper_custom_placeholder": "Enter tamper scripts, comma separated",
        "proxy_config": "🌐 Proxy Config",
        "proxy": "Proxy:",
        "proxy_placeholder": "e.g.: http://127.0.0.1:8080",
        "use_tor": "Use Tor",
        "tor_type": "Tor Type:",
        "request_options": "📡 Request Options",
        "random_agent": "Random User-Agent",
        "mobile_emulation": "Mobile Emulation",
        "safe_url": "Safe URL Access",
        "skip_waf": "Skip WAF Detection",
        "hpp": "HTTP Parameter Pollution",
        "chunked": "Chunked Transfer",
        "db_config": "🗄️ Database Config",
        "dbms_type": "DBMS Type:",
        "dbms_auto": "Auto Detect",
        "target_db": "Database:",
        "target_table": "Table:",
        "target_columns": "Columns:",
        "os_features": "💻 OS Features",
        "os_shell": "Get OS Shell",
        "os_pwn": "OOB Shell (Meterpreter)",
        "os_cmd": "Execute Command:",
        "file_read": "Read File:",
        "file_write": "Write File:",
        
        # Log panel
        "search_log": "🔍 Search log...",
        "auto_scroll": "Auto Scroll",
        "log_count": "Total {count} logs",
        "btn_clear_log": "🗑️ Clear",
        "btn_save_log": "💾 Save",
        "btn_copy_log": "📋 Copy",
        
        # Result panel
        "stat_vulnerabilities": "Vulnerabilities",
        "stat_databases": "Databases",
        "stat_tables": "Tables",
        "stat_time": "Time",
        "injection_info": "🎯 Injection Info",
        "db_structure": "🗄️ DB Structure",
        "data_content": "📊 Data Content",
        "export_csv": "📥 Export CSV",
        "export_json": "📥 Export JSON",
        
        # Control bar
        "command_preview": "Command Preview: Configure scan parameters...",
        "btn_start": "▶ Start Scan",
        "btn_stop": "⏹ Stop",
        "status_ready": "● Ready",
        "status_scanning": "● Scanning...",
        "status_completed": "● Completed",
        "status_stopped": "● Stopped",
        "status_error": "● Error",
        
        # Dialogs
        "settings_title": "⚙️ Settings",
        "settings_general": "🔧 General",
        "settings_appearance": "🎨 Appearance",
        "settings_sqlmap_path": "SQLMap Path:",
        "settings_python_path": "Python Path:",
        "settings_auto_detect": "🔍 Auto Detect SQLMap",
        "settings_default_threads": "Default Threads:",
        "settings_default_timeout": "Default Timeout:",
        "settings_theme": "Theme:",
        "settings_font_size": "Font Size:",
        "btn_apply": "Apply",
        "btn_ok": "OK",
        "btn_cancel": "Cancel",
        "about_title": "About SQLMap GUI v2",
        "about_version": "Version 2.0.0",
        "about_author": "Developer",
        "about_author_name": "✨ ChenChen ✨",
        "about_warning": "⚠️ For authorized security testing only",
        "about_description": """SQLMap GUI v2 is a modern SQL injection detection tool,
built on the powerful sqlmap open source project.
This tool provides a friendly graphical interface for easier SQL injection testing.
Supports multiple injection techniques, tamper scripts, and data extraction.""",
        
        # Messages
        "msg_confirm": "Confirm",
        "msg_info": "Info",
        "msg_warning": "Warning",
        "msg_error": "Error",
        "msg_clear_history": "Are you sure to clear all scan history?",
        "msg_history_cleared": "Cleared {count} history records.",
        "msg_config_saved": "Configuration saved.",
        "msg_sqlmap_found": "Found SQLMap:",
        "msg_sqlmap_not_found": "SQLMap not detected, please select path manually.",
        "msg_no_target": "Please enter target URL",
        "msg_scan_started": "Scan started",
        "msg_scan_stopped": "Scan stopped",
        "msg_scan_completed": "Scan completed",
    }
}


def get_language() -> str:
    """获取当前语言"""
    return _current_language


def set_language(lang: str):
    """设置当前语言"""
    global _current_language
    if lang in TRANSLATIONS:
        _current_language = lang


def get_available_languages() -> Dict[str, str]:
    """获取可用语言列表"""
    return {
        "zh_CN": "简体中文",
        "en_US": "English"
    }


def tr(key: str, **kwargs) -> str:
    """
    翻译函数
    
    参数:
        key: 翻译键
        **kwargs: 格式化参数
    
    返回:
        翻译后的文本
    """
    lang_dict = TRANSLATIONS.get(_current_language, TRANSLATIONS["zh_CN"])
    text = lang_dict.get(key, key)
    
    # 格式化参数
    if kwargs:
        try:
            text = text.format(**kwargs)
        except KeyError:
            pass
    
    return text


def t(key: str, **kwargs) -> str:
    """tr 的简写"""
    return tr(key, **kwargs)
