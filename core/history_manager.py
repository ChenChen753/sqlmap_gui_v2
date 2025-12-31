"""
历史记录管理器
管理扫描历史记录的存储和查询
"""

import os
import sqlite3
from datetime import datetime
from typing import List, Optional, Dict, Any


class HistoryManager:
    """历史记录管理器"""
    
    def __init__(self, db_path: str = None):
        """
        初始化历史记录管理器
        
        参数:
            db_path: 数据库文件路径，默认为脚本所在目录的 history.db
        """
        if db_path is None:
            script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            db_path = os.path.join(script_dir, 'history.db')
        
        self.db_path = db_path
        self._init_database()
    
    def _init_database(self):
        """初始化数据库"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 创建扫描历史表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS scan_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                target TEXT NOT NULL,
                command TEXT NOT NULL,
                scan_mode TEXT,
                start_time TEXT,
                end_time TEXT,
                duration INTEGER,
                status TEXT,
                has_vuln BOOLEAN DEFAULT 0,
                vuln_count INTEGER DEFAULT 0,
                dbms TEXT,
                current_db TEXT,
                result_summary TEXT,
                log_file TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 创建目标收藏表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS favorites (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                target TEXT UNIQUE NOT NULL,
                name TEXT,
                description TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def _get_connection(self) -> sqlite3.Connection:
        """获取数据库连接"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    # ==================== 扫描历史 ====================
    
    def add_scan(self, target: str, command: str, scan_mode: str = "") -> int:
        """添加扫描记录，返回记录ID"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO scan_history (target, command, scan_mode, start_time, status)
            VALUES (?, ?, ?, ?, ?)
        ''', (target, command, scan_mode, datetime.now().isoformat(), 'running'))
        
        record_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return record_id
    
    def update_scan(self, record_id: int, **kwargs):
        """更新扫描记录"""
        if not kwargs:
            return
        
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # 构建更新语句
        set_parts = [f"{key} = ?" for key in kwargs.keys()]
        values = list(kwargs.values())
        values.append(record_id)
        
        cursor.execute(f'''
            UPDATE scan_history 
            SET {', '.join(set_parts)}
            WHERE id = ?
        ''', values)
        
        conn.commit()
        conn.close()
    
    def complete_scan(self, record_id: int, has_vuln: bool = False, 
                      vuln_count: int = 0, dbms: str = "", 
                      current_db: str = "", result_summary: str = ""):
        """完成扫描，更新结果"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        end_time = datetime.now().isoformat()
        
        # 计算持续时间
        cursor.execute('SELECT start_time FROM scan_history WHERE id = ?', (record_id,))
        row = cursor.fetchone()
        duration = 0
        if row and row['start_time']:
            try:
                start = datetime.fromisoformat(row['start_time'])
                duration = int((datetime.now() - start).total_seconds())
            except Exception:
                pass
        
        cursor.execute('''
            UPDATE scan_history 
            SET end_time = ?, duration = ?, status = ?, has_vuln = ?,
                vuln_count = ?, dbms = ?, current_db = ?, result_summary = ?
            WHERE id = ?
        ''', (end_time, duration, 'completed', has_vuln, vuln_count, 
              dbms, current_db, result_summary, record_id))
        
        conn.commit()
        conn.close()
    
    def get_history(self, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """获取扫描历史列表"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM scan_history 
            ORDER BY start_time DESC
            LIMIT ? OFFSET ?
        ''', (limit, offset))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    def get_scan(self, record_id: int) -> Optional[Dict[str, Any]]:
        """获取单条扫描记录"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM scan_history WHERE id = ?', (record_id,))
        row = cursor.fetchone()
        conn.close()
        
        return dict(row) if row else None
    
    def search_history(self, keyword: str, limit: int = 50) -> List[Dict[str, Any]]:
        """搜索扫描历史"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM scan_history 
            WHERE target LIKE ? OR command LIKE ? OR result_summary LIKE ?
            ORDER BY start_time DESC
            LIMIT ?
        ''', (f'%{keyword}%', f'%{keyword}%', f'%{keyword}%', limit))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    def delete_scan(self, record_id: int, vacuum: bool = False) -> bool:
        """
        删除扫描记录
        
        参数:
            record_id: 记录ID
            vacuum: 是否执行 VACUUM 清除已删除数据，默认 False（考虑性能）
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM scan_history WHERE id = ?', (record_id,))
        affected = cursor.rowcount
        
        conn.commit()
        
        # 可选：执行 VACUUM 清除已删除数据
        if vacuum and affected > 0:
            cursor.execute('VACUUM')
        
        conn.close()
        
        return affected > 0
    
    def clear_history(self) -> int:
        """清空所有历史记录，返回删除的记录数"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT COUNT(*) as count FROM scan_history')
        count = cursor.fetchone()['count']
        
        cursor.execute('DELETE FROM scan_history')
        
        conn.commit()
        
        # 执行 VACUUM 清除已删除数据并收缩数据库文件
        # 这确保删除的数据不会残留在数据库文件中
        cursor.execute('VACUUM')
        
        conn.close()
        
        return count
    
    # ==================== 目标收藏 ====================
    
    def add_favorite(self, target: str, name: str = "", description: str = "") -> bool:
        """添加收藏目标"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO favorites (target, name, description)
                VALUES (?, ?, ?)
            ''', (target, name or target, description))
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False
        finally:
            conn.close()
    
    def get_favorites(self) -> List[Dict[str, Any]]:
        """获取收藏列表"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM favorites ORDER BY created_at DESC')
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    def remove_favorite(self, target: str) -> bool:
        """移除收藏"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM favorites WHERE target = ?', (target,))
        affected = cursor.rowcount
        
        conn.commit()
        conn.close()
        
        return affected > 0
    
    def is_favorite(self, target: str) -> bool:
        """检查是否已收藏"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT 1 FROM favorites WHERE target = ?', (target,))
        row = cursor.fetchone()
        conn.close()
        
        return row is not None
    
    # ==================== 统计信息 ====================
    
    def get_statistics(self) -> Dict[str, Any]:
        """获取统计信息"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # 总扫描次数
        cursor.execute('SELECT COUNT(*) as count FROM scan_history')
        total_scans = cursor.fetchone()['count']
        
        # 发现漏洞的扫描次数
        cursor.execute('SELECT COUNT(*) as count FROM scan_history WHERE has_vuln = 1')
        vuln_scans = cursor.fetchone()['count']
        
        # 总漏洞数
        cursor.execute('SELECT SUM(vuln_count) as total FROM scan_history')
        row = cursor.fetchone()
        total_vulns = row['total'] if row['total'] else 0
        
        # 最近扫描
        cursor.execute('SELECT * FROM scan_history ORDER BY start_time DESC LIMIT 1')
        last_scan = cursor.fetchone()
        
        conn.close()
        
        return {
            'total_scans': total_scans,
            'vuln_scans': vuln_scans,
            'total_vulns': total_vulns,
            'success_rate': round(vuln_scans / total_scans * 100, 1) if total_scans > 0 else 0,
            'last_scan': dict(last_scan) if last_scan else None
        }
