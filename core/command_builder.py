"""
命令构建器
智能构建 sqlmap 命令
"""

import os
from typing import Optional, Dict, List


class CommandBuilder:
    """智能命令构建器"""
    
    def __init__(self, sqlmap_path: str = "python sqlmap.py"):
        """
        初始化命令构建器
        
        参数:
            sqlmap_path: sqlmap 执行路径
        """
        self.sqlmap_path = sqlmap_path
        self.reset()
    
    def reset(self):
        """重置所有参数"""
        # 目标
        self._target = ""
        self._method = "GET"
        self._data = ""
        self._cookie = ""
        self._headers = {}
        self._param = ""
        self._file = ""  # 批量扫描文件
        self._request_file = ""  # HTTP 请求包文件（-r 参数）
        
        # 检测
        self._level = 1
        self._risk = 1
        self._technique = ""
        self._dbms = ""
        self._os = ""
        self._string_match = ""  # 字符串匹配
        self._not_string = ""    # 不匹配字符串
        self._regexp = ""        # 正则匹配
        self._code = None        # HTTP 状态码
        self._text_only = False
        self._titles = False
        
        # 性能
        self._threads = 1
        self._timeout = 30
        self._retries = 3
        self._delay = 0
        self._time_sec = 5
        
        # 通用选项
        self._batch = True
        self._flush_session = False
        self._fresh_queries = False
        self._random_agent = False
        self._mobile = False
        self._verbose = 1
        self._forms = False
        self._crawl = 0
        self._smart = False
        self._null_connection = False
        self._no_cast = False
        self._hpp = False
        self._chunked = False
        
        # 绕过
        self._tamper = ""
        self._proxy = ""
        self._tor = False
        self._tor_type = ""
        self._skip_waf = False
        self._csrf_token = ""
        self._csrf_url = ""
        self._prefix = ""
        self._suffix = ""
        
        # 信息查询
        self._current_db = False
        self._current_user = False
        self._banner = False
        self._hostname = False
        self._is_dba = False
        self._users = False
        self._privileges = False
        self._roles = False
        
        # 枚举
        self._dbs = False
        self._tables = False
        self._columns = False
        self._schema = False
        self._count = False
        self._comments = False
        self._exclude_sysdbs = False
        
        # 提取
        self._dump = False
        self._dump_all = False
        self._passwords = False
        self._start = None
        self._stop = None
        self._first = None
        self._last = None
        
        # 搜索
        self._search = False
        self._search_columns = ""
        self._search_tables = ""
        self._search_dbs = ""
        
        # 目标数据库/表/列
        self._target_db = ""
        self._target_table = ""
        self._target_columns = ""
        
        # 操作系统
        self._os_shell = False
        self._os_pwn = False
        self._os_cmd = ""
        self._priv_esc = False
        
        # 文件操作
        self._file_read = ""
        self._file_write = ""
        self._file_dest = ""
        
        # 输出
        self._output_dir = ""
        self._save = ""
        self._forms = False
        
        return self
    
    # ==================== 目标设置 ====================
    
    def set_target(self, url: str, method: str = "GET") -> 'CommandBuilder':
        """设置目标 URL"""
        self._target = url.strip()
        self._method = method.upper()
        return self
    
    def set_file(self, file_path: str) -> 'CommandBuilder':
        """设置批量扫描文件"""
        self._file = file_path.strip()
        return self
    
    def set_request_file(self, file_path: str) -> 'CommandBuilder':
        """设置 HTTP 请求包文件（用于头注入检测）"""
        self._request_file = file_path.strip()
        return self
    
    def set_data(self, data: str) -> 'CommandBuilder':
        """设置 POST 数据"""
        self._data = data.strip()
        return self
    
    def set_cookie(self, cookie: str) -> 'CommandBuilder':
        """设置 Cookie"""
        self._cookie = cookie.strip()
        return self
    
    def set_param(self, param: str) -> 'CommandBuilder':
        """设置指定参数"""
        self._param = param.strip()
        return self
    
    def add_header(self, name: str, value: str) -> 'CommandBuilder':
        """添加 HTTP 头"""
        self._headers[name] = value
        return self
    
    # ==================== 检测设置 ====================
    
    def set_level(self, level: int) -> 'CommandBuilder':
        """设置扫描等级 (0=不指定, 1-5)"""
        self._level = max(0, min(5, level))
        return self
    
    def set_risk(self, risk: int) -> 'CommandBuilder':
        """设置风险等级 (0=不指定, 1-3)"""
        self._risk = max(0, min(3, risk))
        return self
    
    def set_technique(self, technique: str) -> 'CommandBuilder':
        """设置注入技术 (B E U S T Q)"""
        self._technique = technique.upper()
        return self
    
    def set_dbms(self, dbms: str) -> 'CommandBuilder':
        """设置数据库类型"""
        self._dbms = dbms
        return self
    
    def set_os(self, os_type: str) -> 'CommandBuilder':
        """设置操作系统类型"""
        self._os = os_type
        return self
    
    def set_string_match(self, string: str) -> 'CommandBuilder':
        """设置字符串匹配"""
        self._string_match = string
        return self
    
    def set_text_only(self, enabled: bool = True) -> 'CommandBuilder':
        """仅比较文本内容"""
        self._text_only = enabled
        return self
    
    def set_prefix(self, prefix: str) -> 'CommandBuilder':
        """设置注入前缀"""
        self._prefix = prefix
        return self
    
    def set_suffix(self, suffix: str) -> 'CommandBuilder':
        """设置注入后缀"""
        self._suffix = suffix
        return self
    
    # ==================== 性能设置 ====================
    
    def set_threads(self, threads: int) -> 'CommandBuilder':
        """设置线程数 (1-10)"""
        self._threads = max(1, min(10, threads))
        return self
    
    def set_timeout(self, timeout: int) -> 'CommandBuilder':
        """设置超时时间"""
        self._timeout = max(5, timeout)
        return self
    
    def set_retries(self, retries: int) -> 'CommandBuilder':
        """设置重试次数"""
        self._retries = max(0, retries)
        return self
    
    def set_delay(self, delay: float) -> 'CommandBuilder':
        """设置请求延迟"""
        self._delay = max(0, delay)
        return self
    
    def set_time_sec(self, seconds: int) -> 'CommandBuilder':
        """设置时间盲注等待时间"""
        self._time_sec = max(1, seconds)
        return self
    
    # ==================== 通用选项 ====================
    
    def set_batch(self, enabled: bool = True) -> 'CommandBuilder':
        """设置非交互模式"""
        self._batch = enabled
        return self
    
    def set_flush_session(self, enabled: bool = True) -> 'CommandBuilder':
        """设置刷新会话"""
        self._flush_session = enabled
        return self
    
    def set_fresh_queries(self, enabled: bool = True) -> 'CommandBuilder':
        """设置禁用缓存"""
        self._fresh_queries = enabled
        return self
    
    def set_random_agent(self, enabled: bool = True) -> 'CommandBuilder':
        """设置随机 User-Agent"""
        self._random_agent = enabled
        return self
    
    def set_mobile(self, enabled: bool = True) -> 'CommandBuilder':
        """设置移动端 User-Agent"""
        self._mobile = enabled
        return self
    
    def set_verbose(self, level: int) -> 'CommandBuilder':
        """设置详细程度 (0-6)"""
        self._verbose = max(0, min(6, level))
        return self
    
    def set_forms(self, enabled: bool = True) -> 'CommandBuilder':
        """解析表单"""
        self._forms = enabled
        return self
    
    def set_crawl(self, depth: int) -> 'CommandBuilder':
        """爬取深度"""
        self._crawl = max(0, depth)
        return self
    
    def set_smart(self, enabled: bool = True) -> 'CommandBuilder':
        """智能模式"""
        self._smart = enabled
        return self
    
    def set_hpp(self, enabled: bool = True) -> 'CommandBuilder':
        """HTTP 参数污染"""
        self._hpp = enabled
        return self
    
    def set_chunked(self, enabled: bool = True) -> 'CommandBuilder':
        """分块传输"""
        self._chunked = enabled
        return self
    
    # ==================== 绕过设置 ====================
    
    def set_tamper(self, tamper: str) -> 'CommandBuilder':
        """设置 tamper 脚本"""
        self._tamper = tamper
        return self
    
    def set_proxy(self, proxy: str) -> 'CommandBuilder':
        """设置代理"""
        self._proxy = proxy
        return self
    
    def set_tor(self, enabled: bool = True, tor_type: str = "") -> 'CommandBuilder':
        """设置 Tor"""
        self._tor = enabled
        self._tor_type = tor_type
        return self
    
    def set_skip_waf(self, enabled: bool = True) -> 'CommandBuilder':
        """跳过 WAF 检测"""
        self._skip_waf = enabled
        return self
    
    def set_csrf_token(self, token: str, url: str = "") -> 'CommandBuilder':
        """设置 CSRF token"""
        self._csrf_token = token
        self._csrf_url = url
        return self
    
    # ==================== 信息查询 ====================
    
    def get_current_db(self, enabled: bool = True) -> 'CommandBuilder':
        """获取当前数据库"""
        self._current_db = enabled
        return self
    
    def get_current_user(self, enabled: bool = True) -> 'CommandBuilder':
        """获取当前用户"""
        self._current_user = enabled
        return self
    
    def get_banner(self, enabled: bool = True) -> 'CommandBuilder':
        """获取数据库版本"""
        self._banner = enabled
        return self
    
    def get_hostname(self, enabled: bool = True) -> 'CommandBuilder':
        """获取主机名"""
        self._hostname = enabled
        return self
    
    def get_is_dba(self, enabled: bool = True) -> 'CommandBuilder':
        """检查是否为 DBA"""
        self._is_dba = enabled
        return self
    
    def get_users(self, enabled: bool = True) -> 'CommandBuilder':
        """枚举用户"""
        self._users = enabled
        return self
    
    def get_privileges(self, enabled: bool = True) -> 'CommandBuilder':
        """枚举权限"""
        self._privileges = enabled
        return self
    
    def get_roles(self, enabled: bool = True) -> 'CommandBuilder':
        """枚举角色"""
        self._roles = enabled
        return self
    
    # ==================== 枚举选项 ====================
    
    def enum_dbs(self, enabled: bool = True) -> 'CommandBuilder':
        """枚举数据库"""
        self._dbs = enabled
        return self
    
    def enum_tables(self, enabled: bool = True, db: str = "") -> 'CommandBuilder':
        """枚举表"""
        self._tables = enabled
        if db:
            self._target_db = db
        return self
    
    def enum_columns(self, enabled: bool = True, db: str = "", table: str = "") -> 'CommandBuilder':
        """枚举列"""
        self._columns = enabled
        if db:
            self._target_db = db
        if table:
            self._target_table = table
        return self
    
    def enum_schema(self, enabled: bool = True) -> 'CommandBuilder':
        """枚举数据库架构"""
        self._schema = enabled
        return self
    
    def enum_count(self, enabled: bool = True) -> 'CommandBuilder':
        """统计数量"""
        self._count = enabled
        return self
    
    def enum_comments(self, enabled: bool = True) -> 'CommandBuilder':
        """枚举注释"""
        self._comments = enabled
        return self
    
    def exclude_sysdbs(self, enabled: bool = True) -> 'CommandBuilder':
        """排除系统数据库"""
        self._exclude_sysdbs = enabled
        return self
    
    # ==================== 提取选项 ====================
    
    def dump_data(self, enabled: bool = True, db: str = "", table: str = "", columns: str = "") -> 'CommandBuilder':
        """提取数据"""
        self._dump = enabled
        if db:
            self._target_db = db
        if table:
            self._target_table = table
        if columns:
            self._target_columns = columns
        return self
    
    def dump_all(self, enabled: bool = True) -> 'CommandBuilder':
        """提取所有数据"""
        self._dump_all = enabled
        return self
    
    def enum_passwords(self, enabled: bool = True) -> 'CommandBuilder':
        """枚举密码"""
        self._passwords = enabled
        return self
    
    def set_limit(self, start: int = None, stop: int = None) -> 'CommandBuilder':
        """设置提取限制"""
        self._start = start
        self._stop = stop
        return self
    
    # ==================== 搜索选项 ====================
    
    def search_columns(self, columns: str) -> 'CommandBuilder':
        """搜索列"""
        self._search = True
        self._search_columns = columns
        return self
    
    def search_tables(self, tables: str) -> 'CommandBuilder':
        """搜索表"""
        self._search = True
        self._search_tables = tables
        return self
    
    def search_dbs(self, dbs: str) -> 'CommandBuilder':
        """搜索数据库"""
        self._search = True
        self._search_dbs = dbs
        return self
    
    # ==================== 操作系统 ====================
    
    def os_shell(self, enabled: bool = True) -> 'CommandBuilder':
        """获取操作系统 Shell"""
        self._os_shell = enabled
        return self
    
    def os_pwn(self, enabled: bool = True) -> 'CommandBuilder':
        """获取 OOB Shell"""
        self._os_pwn = enabled
        return self
    
    def os_cmd(self, cmd: str) -> 'CommandBuilder':
        """执行操作系统命令"""
        self._os_cmd = cmd
        return self
    
    def priv_esc(self, enabled: bool = True) -> 'CommandBuilder':
        """提权"""
        self._priv_esc = enabled
        return self
    
    # ==================== 文件操作 ====================
    
    def file_read(self, path: str) -> 'CommandBuilder':
        """读取远程文件"""
        self._file_read = path
        return self
    
    def file_write(self, local: str, remote: str) -> 'CommandBuilder':
        """写入远程文件"""
        self._file_write = local
        self._file_dest = remote
        return self
    
    # ==================== 输出设置 ====================
    
    def set_output_dir(self, path: str) -> 'CommandBuilder':
        """设置输出目录"""
        self._output_dir = path
        return self
    
    def set_save(self, path: str) -> 'CommandBuilder':
        """保存命令到文件"""
        self._save = path
        return self
    
    # ==================== 预设模板 ====================
    
    def preset_quick(self) -> 'CommandBuilder':
        """快速检测预设"""
        self._level = 1
        self._risk = 1
        self._threads = 3
        self._current_db = True
        self._batch = True
        return self
    
    def preset_standard(self) -> 'CommandBuilder':
        """标准扫描预设"""
        self._level = 2
        self._risk = 2
        self._threads = 3
        self._current_db = True
        self._current_user = True
        self._dbs = True
        self._batch = True
        return self
    
    def preset_deep(self) -> 'CommandBuilder':
        """深度扫描预设"""
        self._level = 5
        self._risk = 3
        self._threads = 5
        self._current_db = True
        self._current_user = True
        self._banner = True
        self._dbs = True
        self._batch = True
        return self
    
    def preset_aggressive(self) -> 'CommandBuilder':
        """激进模式预设"""
        self._level = 5
        self._risk = 3
        self._threads = 10
        self._technique = "BEUSTQ"
        self._current_db = True
        self._current_user = True
        self._banner = True
        self._hostname = True
        self._is_dba = True
        self._dbs = True
        self._tables = True
        self._batch = True
        self._random_agent = True
        return self
    
    # ==================== 构建命令 ====================
    
    def build(self) -> str:
        """构建完整的 sqlmap 命令"""
        if not self._target and not self._file and not self._request_file:
            raise ValueError("必须设置目标 URL、批量文件或请求包文件")
        
        parts = [self.sqlmap_path]
        
        # 目标
        if self._request_file:
            # HTTP 请求包文件（-r 参数，用于头注入）
            parts.append(f'-r "{self._request_file}"')
        elif self._file:
            parts.append(f'-m "{self._file}"')
        else:
            parts.append(f'-u "{self._target}"')
        
        # POST 数据
        if self._data:
            parts.append(f'--data="{self._data}"')
        
        # Cookie
        if self._cookie:
            parts.append(f'--cookie="{self._cookie}"')
        
        # 指定参数
        if self._param:
            parts.append(f'-p "{self._param}"')
        
        # HTTP 头
        for name, value in self._headers.items():
            parts.append(f'--header="{name}: {value}"')
        
        # 检测级别 (0 表示不指定)
        if self._level > 0:
            parts.append(f'--level={self._level}')
        if self._risk > 0:
            parts.append(f'--risk={self._risk}')
        
        # 注入技术
        if self._technique:
            parts.append(f'--technique={self._technique}')
        
        # 数据库类型
        if self._dbms:
            parts.append(f'--dbms="{self._dbms}"')
        
        # 操作系统
        if self._os:
            parts.append(f'--os="{self._os}"')
        
        # 字符串匹配
        # 字符串匹配
        if self._string_match:
            parts.append(f'--string="{self._string_match}"')
        
        # 注入前缀/后缀
        if self._prefix:
            parts.append(f'--prefix="{self._prefix}"')
        if self._suffix:
            parts.append(f'--suffix="{self._suffix}"')
        
        # 性能
        if self._threads > 1:
            parts.append(f'--threads={self._threads}')
        if self._timeout != 30:
            parts.append(f'--timeout={self._timeout}')
        if self._retries != 3:
            parts.append(f'--retries={self._retries}')
        if self._delay > 0:
            parts.append(f'--delay={self._delay}')
        if self._time_sec != 5:
            parts.append(f'--time-sec={self._time_sec}')
        
        # 通用选项
        if self._batch:
            parts.append('--batch')
        if self._flush_session:
            parts.append('--flush-session')
        if self._fresh_queries:
            parts.append('--fresh-queries')
        if self._random_agent:
            parts.append('--random-agent')
        if self._mobile:
            parts.append('--mobile')
        if self._verbose != 1:
            parts.append(f'-v {self._verbose}')
        if self._forms:
            parts.append('--forms')
        if self._crawl > 0:
            parts.append(f'--crawl={self._crawl}')
        if self._smart:
            parts.append('--smart')
        if self._text_only:
            parts.append('--text-only')
        if self._hpp:
            parts.append('--hpp')
        if self._chunked:
            parts.append('--chunked')
        
        # 绕过选项
        if self._tamper:
            parts.append(f'--tamper="{self._tamper}"')
        if self._proxy:
            parts.append(f'--proxy="{self._proxy}"')
        if self._tor:
            parts.append('--tor')
            if self._tor_type:
                parts.append(f'--tor-type={self._tor_type}')
        if self._skip_waf:
            parts.append('--skip-waf')
        if self._csrf_token:
            parts.append(f'--csrf-token="{self._csrf_token}"')
            if self._csrf_url:
                parts.append(f'--csrf-url="{self._csrf_url}"')
        
        # 信息查询
        if self._current_db:
            parts.append('--current-db')
        if self._current_user:
            parts.append('--current-user')
        if self._banner:
            parts.append('--banner')
        if self._hostname:
            parts.append('--hostname')
        if self._is_dba:
            parts.append('--is-dba')
        if self._users:
            parts.append('--users')
        if self._privileges:
            parts.append('--privileges')
        if self._roles:
            parts.append('--roles')
        
        # 枚举选项
        if self._dbs:
            parts.append('--dbs')
        if self._tables:
            parts.append('--tables')
        if self._columns:
            parts.append('--columns')
        if self._schema:
            parts.append('--schema')
        if self._count:
            parts.append('--count')
        if self._comments:
            parts.append('--comments')
        if self._exclude_sysdbs:
            parts.append('--exclude-sysdbs')
        
        # 提取选项
        if self._dump:
            parts.append('--dump')
        if self._dump_all:
            parts.append('--dump-all')
        if self._passwords:
            parts.append('--passwords')
        if self._start is not None:
            parts.append(f'--start={self._start}')
        if self._stop is not None:
            parts.append(f'--stop={self._stop}')
        
        # 搜索选项
        if self._search:
            parts.append('--search')
            if self._search_columns:
                parts.append(f'-C "{self._search_columns}"')
            if self._search_tables:
                parts.append(f'-T "{self._search_tables}"')
            if self._search_dbs:
                parts.append(f'-D "{self._search_dbs}"')
        
        # 目标数据库/表/列（非搜索情况）
        if not self._search:
            if self._target_db:
                parts.append(f'-D "{self._target_db}"')
            if self._target_table:
                parts.append(f'-T "{self._target_table}"')
            if self._target_columns:
                parts.append(f'-C "{self._target_columns}"')
        
        # 操作系统
        if self._os_shell:
            parts.append('--os-shell')
        if self._os_pwn:
            parts.append('--os-pwn')
        if self._os_cmd:
            parts.append(f'--os-cmd="{self._os_cmd}"')
        if self._priv_esc:
            parts.append('--priv-esc')
        
        # 文件操作
        if self._file_read:
            parts.append(f'--file-read="{self._file_read}"')
        if self._file_write and self._file_dest:
            parts.append(f'--file-write="{self._file_write}"')
            parts.append(f'--file-dest="{self._file_dest}"')
        
        # 输出目录
        if self._output_dir:
            parts.append(f'--output-dir="{self._output_dir}"')
        
        return ' '.join(parts)
    
    def get_command_preview(self) -> str:
        """获取命令预览（用于显示）"""
        try:
            return self.build()
        except ValueError as e:
            return f"[错误] {str(e)}"
