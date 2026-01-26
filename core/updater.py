"""
自动更新模块
支持 GUI 工具更新和 SQLMap 下载
"""

import os
import sys
import json
import shutil
import tempfile
import zipfile
import urllib.request
import urllib.error
from typing import Optional, Callable, Tuple
from dataclasses import dataclass


# 当前版本号
CURRENT_VERSION = "2.2.1"


@dataclass
class VersionInfo:
    """版本信息"""
    version: str
    download_url: str
    release_notes: str
    published_at: str


class Updater:
    """自动更新器"""
    
    # 仓库配置
    GUI_REPO = "ChenChen753/sqlmap_gui_v2"
    SQLMAP_REPO = "sqlmapproject/sqlmap"
    
    # GitHub API 地址
    GITHUB_API = "https://api.github.com/repos"
    
    # 保护文件列表（GUI 更新时跳过）
    PROTECTED_FILES = [
        'config.ini',
        'history.db',
        '.git',
        'sqlmap',
        'sqlmap_log.txt',
        '__pycache__',
    ]
    
    def __init__(self):
        """初始化更新器"""
        # 获取程序运行目录
        if getattr(sys, 'frozen', False):
            # 打包后的可执行文件
            self.app_dir = os.path.dirname(sys.executable)
        else:
            # 开发环境
            self.app_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
        # SQLMap 目录
        self.sqlmap_dir = os.path.join(self.app_dir, 'sqlmap')
    
    def get_current_version(self) -> str:
        """获取当前版本号"""
        return CURRENT_VERSION
    
    def check_gui_update(self) -> Tuple[bool, Optional[VersionInfo], str]:
        """
        检查 GUI 更新
        
        返回:
            (是否有更新, 版本信息, 错误信息)
        """
        try:
            api_url = f"{self.GITHUB_API}/{self.GUI_REPO}/releases/latest"
            
            request = urllib.request.Request(
                api_url,
                headers={
                    'User-Agent': 'SQLMap-GUI-Updater',
                    'Accept': 'application/vnd.github.v3+json'
                }
            )
            
            with urllib.request.urlopen(request, timeout=15) as response:
                data = json.loads(response.read().decode('utf-8'))
            
            # 解析版本信息
            tag_name = data.get('tag_name', '')
            # 移除 'v' 前缀
            latest_version = tag_name.lstrip('v')
            
            version_info = VersionInfo(
                version=latest_version,
                download_url=data.get('zipball_url', ''),
                release_notes=data.get('body', '暂无更新说明'),
                published_at=data.get('published_at', '')
            )
            
            # 比较版本
            has_update = self._compare_versions(latest_version, CURRENT_VERSION) > 0
            
            return has_update, version_info, ""
            
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return False, None, "暂无发布版本"
            return False, None, f"网络请求失败: {e.code}"
        except urllib.error.URLError as e:
            return False, None, f"网络连接失败: {str(e.reason)}"
        except Exception as e:
            return False, None, f"检查更新失败: {str(e)}"
    
    def download_gui_update(
        self,
        version_info: VersionInfo,
        progress_callback: Optional[Callable[[int, int], None]] = None
    ) -> Tuple[bool, str]:
        """
        下载并安装 GUI 更新
        
        参数:
            version_info: 版本信息
            progress_callback: 进度回调函数(已下载字节, 总字节)
        
        返回:
            (是否成功, 错误信息)
        """
        try:
            # 下载 ZIP 文件
            temp_dir = tempfile.mkdtemp()
            zip_path = os.path.join(temp_dir, 'update.zip')
            
            success, error = self._download_file(
                version_info.download_url,
                zip_path,
                progress_callback
            )
            
            if not success:
                return False, error
            
            # 解压并安装
            success, error = self._install_gui_update(zip_path)
            
            # 清理临时文件
            try:
                shutil.rmtree(temp_dir)
            except:
                pass
            
            return success, error
            
        except Exception as e:
            return False, f"更新失败: {str(e)}"
    
    def download_sqlmap(
        self,
        progress_callback: Optional[Callable[[int, int], None]] = None
    ) -> Tuple[bool, str]:
        """
        下载/更新 SQLMap
        
        参数:
            progress_callback: 进度回调函数(已下载字节, 总字节)
        
        返回:
            (是否成功, 错误信息)
        """
        try:
            # SQLMap master 分支下载地址
            download_url = f"https://github.com/{self.SQLMAP_REPO}/archive/refs/heads/master.zip"
            
            # 下载 ZIP 文件
            temp_dir = tempfile.mkdtemp()
            zip_path = os.path.join(temp_dir, 'sqlmap.zip')
            
            success, error = self._download_file(
                download_url,
                zip_path,
                progress_callback
            )
            
            if not success:
                return False, error
            
            # 解压到 sqlmap 目录
            success, error = self._install_sqlmap(zip_path)
            
            # 清理临时文件
            try:
                shutil.rmtree(temp_dir)
            except:
                pass
            
            return success, error
            
        except Exception as e:
            return False, f"下载 SQLMap 失败: {str(e)}"
    
    def _download_file(
        self,
        url: str,
        save_path: str,
        progress_callback: Optional[Callable[[int, int], None]] = None
    ) -> Tuple[bool, str]:
        """
        下载文件
        
        参数:
            url: 下载地址
            save_path: 保存路径
            progress_callback: 进度回调
        
        返回:
            (是否成功, 错误信息)
        """
        try:
            request = urllib.request.Request(
                url,
                headers={'User-Agent': 'SQLMap-GUI-Updater'}
            )
            
            with urllib.request.urlopen(request, timeout=60) as response:
                total_size = int(response.headers.get('content-length', 0))
                downloaded = 0
                block_size = 8192
                
                with open(save_path, 'wb') as f:
                    while True:
                        buffer = response.read(block_size)
                        if not buffer:
                            break
                        
                        f.write(buffer)
                        downloaded += len(buffer)
                        
                        if progress_callback:
                            progress_callback(downloaded, total_size)
            
            return True, ""
            
        except urllib.error.URLError as e:
            return False, f"下载失败: {str(e.reason)}"
        except Exception as e:
            return False, f"下载失败: {str(e)}"
    
    def _install_gui_update(self, zip_path: str) -> Tuple[bool, str]:
        """
        安装 GUI 更新
        
        参数:
            zip_path: ZIP 文件路径
        
        返回:
            (是否成功, 错误信息)
        """
        try:
            # 创建临时解压目录
            extract_dir = tempfile.mkdtemp()
            
            # 解压 ZIP
            with zipfile.ZipFile(zip_path, 'r') as zf:
                zf.extractall(extract_dir)
            
            # GitHub 的 zipball 会有一层目录，需要找到它
            extracted_items = os.listdir(extract_dir)
            if len(extracted_items) == 1:
                source_dir = os.path.join(extract_dir, extracted_items[0])
            else:
                source_dir = extract_dir
            
            # 复制文件到程序目录，跳过保护文件
            for item in os.listdir(source_dir):
                if item in self.PROTECTED_FILES:
                    continue
                
                src = os.path.join(source_dir, item)
                dst = os.path.join(self.app_dir, item)
                
                # 删除目标（如果存在）
                if os.path.exists(dst):
                    if os.path.isdir(dst):
                        shutil.rmtree(dst)
                    else:
                        os.remove(dst)
                
                # 复制
                if os.path.isdir(src):
                    shutil.copytree(src, dst)
                else:
                    shutil.copy2(src, dst)
            
            # 清理临时目录
            try:
                shutil.rmtree(extract_dir)
            except:
                pass
            
            return True, ""
            
        except Exception as e:
            return False, f"安装更新失败: {str(e)}"
    
    def _install_sqlmap(self, zip_path: str) -> Tuple[bool, str]:
        """
        安装 SQLMap
        
        参数:
            zip_path: ZIP 文件路径
        
        返回:
            (是否成功, 错误信息)
        """
        try:
            # 创建临时解压目录
            extract_dir = tempfile.mkdtemp()
            
            # 解压 ZIP
            with zipfile.ZipFile(zip_path, 'r') as zf:
                zf.extractall(extract_dir)
            
            # GitHub 的 archive 会有一层目录（如 sqlmap-master）
            extracted_items = os.listdir(extract_dir)
            if len(extracted_items) == 1:
                source_dir = os.path.join(extract_dir, extracted_items[0])
            else:
                source_dir = extract_dir
            
            # 删除旧的 sqlmap 目录（如果存在）
            if os.path.exists(self.sqlmap_dir):
                shutil.rmtree(self.sqlmap_dir)
            
            # 复制新的 sqlmap 目录
            shutil.copytree(source_dir, self.sqlmap_dir)
            
            # 清理临时目录
            try:
                shutil.rmtree(extract_dir)
            except:
                pass
            
            return True, ""
            
        except PermissionError:
            return False, "权限不足，请以管理员身份运行"
        except Exception as e:
            return False, f"安装 SQLMap 失败: {str(e)}"
    
    def _compare_versions(self, v1: str, v2: str) -> int:
        """
        比较版本号
        
        返回:
            1: v1 > v2
            0: v1 == v2
            -1: v1 < v2
        """
        try:
            # 分割版本号
            parts1 = [int(x) for x in v1.split('.')]
            parts2 = [int(x) for x in v2.split('.')]
            
            # 补齐长度
            max_len = max(len(parts1), len(parts2))
            parts1.extend([0] * (max_len - len(parts1)))
            parts2.extend([0] * (max_len - len(parts2)))
            
            # 逐位比较
            for p1, p2 in zip(parts1, parts2):
                if p1 > p2:
                    return 1
                elif p1 < p2:
                    return -1
            
            return 0
        except:
            # 如果解析失败，使用字符串比较
            if v1 > v2:
                return 1
            elif v1 < v2:
                return -1
            return 0
