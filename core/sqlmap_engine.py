"""
SQLMap 执行引擎
负责执行 sqlmap 命令并处理输出
"""

import subprocess
import os
import re
from PyQt6.QtCore import QThread, pyqtSignal


class SqlmapEngine(QThread):
    """SQLMap 命令执行引擎"""
    
    # 信号定义
    output_received = pyqtSignal(str)      # 接收到输出
    progress_updated = pyqtSignal(int)     # 进度更新
    result_found = pyqtSignal(dict)        # 发现结果
    scan_finished = pyqtSignal(int)        # 扫描完成（返回码）
    status_changed = pyqtSignal(str)       # 状态变化
    
    def __init__(self, command: str, sqlmap_path: str = None, parent=None):
        """
        初始化执行引擎
        
        参数:
            command: 完整的 sqlmap 命令
            sqlmap_path: sqlmap.py 的路径
            parent: 父对象，确保线程不会被意外销毁
        """
        super().__init__(parent)
        self.command = command
        self.sqlmap_path = sqlmap_path
        self.process = None
        self.running = False
        
        # 扫描结果
        self.results = {
            'injection_found': False,      # 是否发现注入
            'injection_type': [],          # 注入类型
            'dbms': '',                    # 数据库类型
            'current_db': '',              # 当前数据库
            'current_user': '',            # 当前用户
            'databases': [],               # 数据库列表
            'tables': {},                  # 表列表 {db: [tables]}
            'columns': {},                 # 列列表 {(db, table): [columns]}
            'data': {},                    # 数据内容
        }
        
        # 进度追踪
        self.progress = 0
        self.total_tests = 0
        self.current_test = 0
    
    def run(self):
        """执行 sqlmap 命令"""
        return_code = -1
        try:
            self.running = True
            self.status_changed.emit("正在启动...")
            self.output_received.emit(f"[命令] {self.command}\n")
            self.output_received.emit("-" * 60 + "\n")
            
            # 创建子进程
            startupinfo = None
            if os.name == 'nt':  # Windows
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                startupinfo.wShowWindow = subprocess.SW_HIDE
            
            self.process = subprocess.Popen(
                self.command,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                stdin=subprocess.PIPE,
                universal_newlines=True,
                startupinfo=startupinfo,
                bufsize=1
            )
            
            self.status_changed.emit("扫描进行中...")
            
            # 读取输出
            while self.running and self.process.poll() is None:
                try:
                    line = self.process.stdout.readline()
                    if line:
                        self.output_received.emit(line)
                        self._parse_output(line)
                except Exception:
                    pass
            
            # 读取剩余输出
            try:
                if self.process and self.process.stdout:
                    remaining = self.process.stdout.read()
                    if remaining:
                        self.output_received.emit(remaining)
                        for line in remaining.split('\n'):
                            self._parse_output(line)
            except Exception:
                pass
            
            # 获取返回码
            return_code = self.process.returncode if self.process else -1
            
        except Exception as e:
            self.output_received.emit(f"[错误] 执行失败: {str(e)}\n")
            return_code = -1
        
        finally:
            # 确保信号在 finally 块中发送
            try:
                # 保存未保存的数据
                self._save_data_buffer()
                self.result_found.emit(self.results)
                self.scan_finished.emit(return_code)
                
                if return_code == 0:
                    self.status_changed.emit("扫描完成")
                elif return_code == -1:
                    self.status_changed.emit("执行出错")
                else:
                    self.status_changed.emit("扫描结束")
            except Exception:
                pass
    
    def stop(self):
        """停止执行"""
        self.running = False
        if self.process and self.process.poll() is None:
            try:
                # Windows 上需要使用 taskkill 递归终止进程树
                # 因为 shell=True 创建的是 cmd.exe 进程，terminate() 无法终止其子进程
                if os.name == 'nt':
                    # 使用 taskkill /T (终止子进程) /F (强制) /PID (进程ID)
                    subprocess.run(
                        ['taskkill', '/T', '/F', '/PID', str(self.process.pid)],
                        capture_output=True,
                        timeout=10
                    )
                    self.output_received.emit("[信息] 扫描进程已终止\n")
                else:
                    # Linux/Mac 使用标准终止信号
                    self.process.terminate()
                    self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                # 强制终止
                try:
                    self.process.kill()
                except Exception:
                    pass
                self.output_received.emit("[警告] 进程已强制终止\n")
            except Exception as e:
                self.output_received.emit(f"[错误] 停止进程失败: {str(e)}\n")
        
        self.status_changed.emit("已停止")
    
    def send_input(self, text: str):
        """发送输入到进程"""
        if self.process and self.process.poll() is None:
            try:
                self.process.stdin.write(text + '\n')
                self.process.stdin.flush()
            except Exception:
                pass
    
    def _save_data_buffer(self):
        """保存数据缓冲区中的数据"""
        self._parsing_data = False
        self._in_data_grid = False
        if hasattr(self, '_data_buffer') and self._data_buffer:
            table_name = getattr(self, '_current_dump_table', 'data')
            row_count = len(self._data_buffer)
            # 使用替换而不是累加，避免重复数据
            self.results['data'][table_name] = self._data_buffer.copy()
            # 输出调试信息
            self.output_received.emit(f"[数据] 表 '{table_name}' 提取了 {row_count} 条记录\n")
            self._data_buffer = []
    
    def _parse_output(self, line: str):
        """解析 sqlmap 输出"""
        line = line.strip()
        if not line:
            return
        
        # 检测注入点
        if any(keyword in line for keyword in [
            "is vulnerable",
            "is injectable",
            "injection point",
            "SQL injection vulnerability"
        ]):
            self.results['injection_found'] = True
            self.output_received.emit("[发现] 检测到 SQL 注入漏洞！\n")
        
        # 提取注入类型
        if "Type:" in line:
            match = re.search(r"Type:\s*(.+)", line)
            if match:
                injection_type = match.group(1).strip()
                if injection_type not in self.results['injection_type']:
                    self.results['injection_type'].append(injection_type)
        
        # 提取数据库类型
        if "back-end DBMS" in line.lower():
            match = re.search(r"back-end DBMS[:\s]+(.+)", line, re.IGNORECASE)
            if match:
                self.results['dbms'] = match.group(1).strip().strip("'")
        
        # 提取当前数据库 - 只匹配 "current database: 'xxx'" 格式（必须有冒号）
        # 排除警告信息如 "use the current database to enumerate"
        if "current database:" in line.lower():
            # 只匹配带冒号的格式
            match = re.search(r"current database:\s*['\"]?(\w+)['\"]?", line, re.IGNORECASE)
            if match:
                db = match.group(1).strip()
                # 验证是有效的数据库名（不包含无效关键词）
                invalid_words = ['to', 'the', 'enumerate', 'entries', 'table', 'NULL', 'None']
                if db and db.lower() not in invalid_words and ' ' not in db:
                    self.results['current_db'] = db
                    self._current_parsing_db = db  # 同时设置当前解析数据库
                    if db not in self.results['databases']:
                        self.results['databases'].append(db)
        
        # 提取当前用户
        if "current user" in line.lower():
            match = re.search(r"current user[:\s]+['\"]?([^'\"]+)['\"]?", line, re.IGNORECASE)
            if match:
                self.results['current_user'] = match.group(1).strip()
        
        # 提取数据库列表 - 使用更严格的匹配
        # 检测 "fetching database names" 开始解析
        if "fetching database names" in line.lower():
            self._parsing_db_names = True
            self.results['databases'] = []  # 清空旧数据，防止重复
        
        # 从 "retrieved: 'xxx'" 格式解析数据库名（当正在获取数据库列表时）
        # 注意：只匹配单值格式，避免将 'db','table' 格式误解析
        if hasattr(self, '_parsing_db_names') and self._parsing_db_names:
            if "retrieved:" in line.lower():
                # 只匹配单值格式: retrieved: 'db_name' (行尾是单引号)
                # 不匹配 'db','table' 格式
                if "','" not in line:  # 排除 'db','table' 格式
                    # 修改正则：排除换行符和其他控制字符，只允许常规字符
                    match = re.search(r"retrieved:\s*'([^'\n\r\t]+)'$", line, re.IGNORECASE)
                    if match:
                        db = match.group(1).strip()
                        # 再次清洗以防万一
                        db = db.replace('\n', '').replace('\r', '')
                        if db and db not in self.results['databases']:
                            self.results['databases'].append(db)
            # 遇到 fetching tables 时停止解析数据库
            if "fetching tables" in line.lower():
                self._parsing_db_names = False
        
        if "available databases" in line.lower():
            self.results['databases'] = []
            self._parsing_databases = True
            self._parsing_tables = False
            self._parsing_columns = False
        elif hasattr(self, '_parsing_databases') and self._parsing_databases:
            # 如果遇到空行或新的段落，停止解析
            if line.startswith("[INFO]") or line.startswith("[WARNING]"):
                self._parsing_databases = False
            elif line.startswith("[*]"):
                db = line[3:].strip().strip("'\"")
                # 更严格的数据库名过滤（不过滤 information_schema 等系统库）
                invalid_patterns = [
                    'NULL', 'None', '', 'Database', 'available', 'fetching', 
                    'the back-end', 'web server', 'web application', 'target',
                    'starting', 'testing', 'heuristic',
                    'enumerate', 'entries', 'table(s)', 'tables'
                ]
                if db and not any(inv.lower() in db.lower() for inv in invalid_patterns):
                    # 检查是否是有效的数据库名格式（不包含太多特殊字符和空格）
                    if len(db) < 64 and not db.startswith('[') and ':' not in db and ' ' not in db:
                        if db not in self.results['databases']:
                            self.results['databases'].append(db)
        
        # 检测表列表开始 - 格式: "Database: xxx" 后面跟着表格
        # 注意：只匹配单独的 "Database: xxx" 行，不是警告信息
        if "Database:" in line and "tables" not in line.lower() and "enumerate" not in line.lower():
            match = re.search(r"Database:\s*(\S+)", line)
            if match:
                db_name = match.group(1).strip().strip("'\"")
                # 验证数据库名不包含无效关键词
                if db_name and ' ' not in db_name and 'enumerate' not in db_name.lower():
                    self._current_parsing_db = db_name
                    if db_name not in self.results['databases']:
                        self.results['databases'].append(db_name)
                    if db_name not in self.results['tables']:
                        self.results['tables'][db_name] = []
        
        # 检测表列表开始 - 格式: "[X tables]" 或 "fetching tables for database(s): 'xxx'"
        if "fetching tables" in line.lower():
            # 先尝试匹配多数据库格式: "fetching tables for databases: 'db1, db2, db3'"
            if "databases:" in line.lower():
                dbs_match = re.search(r"databases:\s*'([^']+)'", line, re.IGNORECASE)
                if dbs_match:
                    dbs_str = dbs_match.group(1).strip()
                    for db_name in dbs_str.split(','):
                        db_name = db_name.strip().replace('\n', '').replace('\r', '')
                        if db_name and db_name not in self.results['databases']:
                            self.results['databases'].append(db_name)
                        if db_name and db_name not in self.results['tables']:
                            self.results['tables'][db_name] = []
            # 尝试匹配单数据库格式: "fetching tables for database: 'patient'"
            elif "database:" in line.lower():
                db_match = re.search(r"for database:\s*'([^']+)'", line, re.IGNORECASE)
                if db_match:
                    db_name = db_match.group(1).strip().replace('\n', '').replace('\r', '')
                    if db_name and db_name.lower() not in ['to', 'the', 'enumerate']:
                        self._current_parsing_db = db_name
                        if db_name not in self.results['databases']:
                            self.results['databases'].append(db_name)
                        if db_name not in self.results['tables']:
                            self.results['tables'][db_name] = []
            
            # 设置解析状态
            self._parsing_tables = True
            self._parsing_columns = False
            self._parsing_databases = False
            self._parsing_db_names = False
            self._in_table_grid = False
        elif re.search(r'\[\d+\s+tables?\]', line.lower()):
            self._parsing_tables = True
            self._parsing_columns = False
            self._parsing_databases = False
            self._in_table_grid = False
        
        # 检测 "Database: xxx" 行，更新当前解析的数据库
        if "Database:" in line and "fetching" not in line.lower():
            db_match = re.search(r"Database:\s*(\w+)", line)
            if db_match:
                db_name = db_match.group(1).strip()
                if db_name:
                    self._current_parsing_db = db_name
                    if db_name not in self.results['tables']:
                        self.results['tables'][db_name] = []
        
        # 检测表格边界 (表名以表格形式输出)
        if line.startswith("+") and "-" in line:
            # 这是表格的分隔线
            if hasattr(self, '_parsing_tables') and self._parsing_tables:
                self._in_table_grid = not getattr(self, '_in_table_grid', False)
            if hasattr(self, '_parsing_columns') and self._parsing_columns:
                self._in_column_grid = not getattr(self, '_in_column_grid', False)
        
        # 解析表名 - 支持两种格式：
        # 1. retrieved: 'db','table' (多数据库批量获取)
        # 2. retrieved: 'table' (单数据库获取)
        if "retrieved:" in line.lower() and hasattr(self, '_parsing_tables') and self._parsing_tables:
            # 首先尝试匹配 'db','table' 格式
            db_table_match = re.search(r"retrieved:\s*'([^']+)'\s*,\s*'([^']+)'", line, re.IGNORECASE)
            if db_table_match:
                db_name = db_table_match.group(1).strip()
                table_name = db_table_match.group(2).strip()
                if db_name and table_name:
                    # 确保数据库在列表中
                    if db_name not in self.results['databases']:
                        self.results['databases'].append(db_name)
                    if db_name not in self.results['tables']:
                        self.results['tables'][db_name] = []
                    if table_name not in self.results['tables'][db_name]:
                        self.results['tables'][db_name].append(table_name)
            else:
                # 尝试匹配单值格式: retrieved: 'table_name'
                simple_match = re.search(r"retrieved:\s*'([^']+)'$", line, re.IGNORECASE)
                if simple_match:
                    table_name = simple_match.group(1).strip()
                    if table_name:
                        # 使用当前解析的数据库名
                        db = getattr(self, '_current_parsing_db', None) or self.results.get('current_db', 'default')
                        if db not in self.results['tables']:
                            self.results['tables'][db] = []
                        if table_name not in self.results['tables'][db]:
                            self.results['tables'][db].append(table_name)
        
        # 解析表格格式的表名: | table_name |
        if hasattr(self, '_parsing_tables') and self._parsing_tables:
            if line.startswith("|") and not line.startswith("+-"):
                # 提取表格中的内容
                parts = [p.strip() for p in line.split("|") if p.strip()]
                if parts and len(parts) >= 1:
                    table_name = parts[0].strip()
                    # 过滤掉表头和无效项
                    if table_name and table_name.lower() not in ['table', 'tables', '']:
                        # 使用正确的数据库名
                        db = getattr(self, '_current_parsing_db', None) or self.results.get('current_db', 'default')
                        if db not in self.results['tables']:
                            self.results['tables'][db] = []
                        if table_name not in self.results['tables'][db]:
                            self.results['tables'][db].append(table_name)
            # 检测表列表结束 - 当开始获取列时
            if "fetching columns" in line.lower():
                self._parsing_tables = False
                self._in_table_grid = False
        
        # 检测列列表开始 - 格式: "Table: xxx" 或 "[X columns]"
        if "Table:" in line:
            match = re.search(r"Table:\s*(\S+)", line)
            if match:
                table_name = match.group(1).strip().strip("'\"")
                self._current_parsing_table = table_name
                db = getattr(self, '_current_parsing_db', 'default')
                key = (db, table_name)
                if key not in self.results['columns']:
                    self.results['columns'][key] = []
                self._parsing_columns = True
                self._parsing_tables = False
                self._in_column_grid = False
        
        if re.search(r'\[\d+\s+columns?\]', line.lower()) or "fetching columns" in line.lower():
            self._parsing_columns = True
            self._parsing_tables = False
            self._in_column_grid = False
        
        # 解析表格格式的列名: | column_name | type |
        if hasattr(self, '_parsing_columns') and self._parsing_columns:
            if line.startswith("|") and not line.startswith("+-"):
                parts = [p.strip() for p in line.split("|") if p.strip()]
                if parts and len(parts) >= 1:
                    col_name = parts[0].strip()
                    col_type = parts[1].strip() if len(parts) > 1 else ""
                    # 过滤掉表头和无效项
                    if col_name and col_name.lower() not in ['column', 'columns', 'type', '']:
                        if hasattr(self, '_current_parsing_table'):
                            db = getattr(self, '_current_parsing_db', 'default')
                            key = (db, self._current_parsing_table)
                            if key not in self.results['columns']:
                                self.results['columns'][key] = []
                            self.results['columns'][key].append((col_name, col_type))
            # 检测列列表结束
            if line.startswith("[") and "INFO" in line:
                self._parsing_columns = False
                self._in_column_grid = False
        
        # 检测 "Database: xxx" 行，更新当前数据提取的数据库
        if line.strip().startswith("Database:") and "fetching" not in line.lower():
            db_match = re.search(r"Database:\s*(\S+)", line)
            if db_match:
                self._current_dump_db = db_match.group(1).strip().strip("'\"")
                
        # 检测数据提取开始 - 格式: "dumping entries for table" 或 "[X entries]" 或 "Table:"
        if "dumping entries" in line.lower() or "fetching entries" in line.lower():
            # 先保存之前的缓冲区
            self._save_data_buffer()
            self._parsing_data = True
            self._data_buffer = []
            self._in_data_grid = False
            
            # 尝试从行中提取数据库名 "in database 'xxx'"
            db_in_line = re.search(r"in database\s*['\"]([^'\"]+)['\"]", line, re.IGNORECASE)
            if db_in_line:
                self._current_dump_db = db_in_line.group(1).strip()
            
            # 提取表名 - 优先匹配引号内的表名
            table_name = None
            # 匹配 'db.table' 或 "db.table" 或 `db.table` 格式
            quote_patterns = [
                r"'([^']+)'",      # 'table_name' 或 'db.table'
                r'"([^"]+)"',      # "table_name"
                r'`([^`]+)`',      # `table_name`
            ]
            for pattern in quote_patterns:
                # 排除 'in database' 后面的匹配
                # 这种简单的循环可能会匹配到 database 的名字作为 table，所以需要更精确
                # 如果我们已经找到了 database，我们可以排除它
                matches = list(re.finditer(pattern, line))
                for match in matches:
                    val = match.group(1).strip()
                    # 如果这好像是数据库名，跳过
                    if hasattr(self, '_current_dump_db') and val == self._current_dump_db:
                        continue
                     # 或者是 'entries' 这样的关键词
                    if val.lower() in ['entries', 'table', 'database']:
                        continue
                    table_name = val
                    break
                if table_name:
                    break
            
            if not table_name:
                # 尝试匹配 "table xxx" 格式
                match = re.search(r'table\s+(\S+)', line, re.IGNORECASE)
                if match:
                    table_name = match.group(1).strip().strip("'\"`.`")
            
            # 提取真正的表名（去掉可能的数据库前缀保留格式如 db.table）
            if table_name:
                # 去掉多余的引号和反引号
                table_name = table_name.strip("'\"`.`")
                # 如果有当前数据库，确保加上前缀
                if hasattr(self, '_current_dump_db') and self._current_dump_db:
                     if '.' not in table_name:
                         table_name = f"{self._current_dump_db}.{table_name}"
                self._current_dump_table = table_name
            else:
                self._current_dump_table = "unknown"
        
        # 检测数据条目数量
        entries_match = re.search(r'\[(\d+)\s+entries?\]', line.lower())
        if entries_match:
            self._parsing_data = True
            self._in_data_grid = False
            if not hasattr(self, '_data_buffer'):
                self._data_buffer = []
        
        # 检测 "Table: xxx" 格式开始数据输出
        if line.strip().startswith("Table:") and "dump" not in line.lower():
            match = re.search(r'Table:\s*([^\s]+)', line)
            if match:
                # 先保存之前的数据
                self._save_data_buffer()
                self._parsing_data = True
                self._data_buffer = []
                self._in_data_grid = False
                # 清理表名 - 去掉引号
                table_name = match.group(1).strip().strip("'\"`.`")
                
                # 如果有当前数据库，确保加上前缀
                if hasattr(self, '_current_dump_db') and self._current_dump_db:
                     if '.' not in table_name:
                         table_name = f"{self._current_dump_db}.{table_name}"
                
                self._current_dump_table = table_name
        
        # 解析提取的数据行 (表格格式)
        if hasattr(self, '_parsing_data') and self._parsing_data:
            # 检测表格边界线
            if line.startswith("+-"):
                if not hasattr(self, '_in_data_grid'):
                    self._in_data_grid = False
                self._in_data_grid = not self._in_data_grid
                # 如果表格结束，保存数据
                if not self._in_data_grid and hasattr(self, '_data_buffer') and self._data_buffer:
                    # 不要在这里保存，等待下一个表格开始或扫描结束时保存
                    pass
            elif line.startswith("|") and not line.startswith("+-"):
                parts = [p.strip() for p in line.split("|") if p.strip()]
                if parts:
                    row_data = " | ".join(parts)
                    if not hasattr(self, '_data_buffer'):
                        self._data_buffer = []
                    self._data_buffer.append(row_data)
            elif line.startswith("[") and ("INFO" in line or "WARNING" in line):
                # 检测数据段结束 - 更精确的条件
                end_keywords = ["dump", "file", "table", "fetched", "stored", "written", "entries"]
                if any(kw in line.lower() for kw in end_keywords):
                    self._save_data_buffer()
        
        # 进度估算
        if "testing" in line.lower():
            self.current_test += 1
            if self.total_tests > 0:
                progress = min(int(self.current_test / self.total_tests * 100), 99)
                self.progress_updated.emit(progress)
        
        # 完成时设置进度为100
        if "all tested parameters" in line.lower() or "sqlmap identified" in line.lower():
            self.progress_updated.emit(100)


class SqlmapFinder:
    """查找 sqlmap 路径"""
    
    @staticmethod
    def find_sqlmap() -> str:
        """自动查找 sqlmap.py 路径"""
        # 程序根目录
        program_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
        # 可能的路径列表（按优先级排序）
        possible_paths = [
            # 优先：工具目录内的 sqlmap 文件夹
            os.path.join(program_dir, "sqlmap", "sqlmap.py"),
            os.path.join(program_dir, "sqlmap-master", "sqlmap.py"),
            # 次选：上级目录的 sqlmap
            os.path.join(os.path.dirname(program_dir), "sqlmap-master", "sqlmap.py"),
            os.path.join(os.path.dirname(program_dir), "sqlmap", "sqlmap.py"),
            # 常见安装路径
            r"C:\sqlmap\sqlmap.py",
            r"C:\tools\sqlmap\sqlmap.py",
            r"D:\sqlmap\sqlmap.py",
            "/usr/share/sqlmap/sqlmap.py",
            "/opt/sqlmap/sqlmap.py",
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                return path
        
        return None
    
    @staticmethod
    def validate_sqlmap(path: str) -> bool:
        """验证 sqlmap 路径是否有效"""
        if not path:
            return False
        
        if os.path.isfile(path) and path.endswith('.py'):
            return True
        
        return False
