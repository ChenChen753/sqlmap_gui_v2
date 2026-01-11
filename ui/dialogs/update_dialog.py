"""
更新对话框
显示版本信息、更新日志和下载进度
"""

import os
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QProgressBar, QTextEdit, QMessageBox, QFrame, QApplication
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QFont

from ..theme import COLORS
from core.updater import Updater, VersionInfo, CURRENT_VERSION


class DownloadThread(QThread):
    """下载线程"""
    
    # 信号
    progress = pyqtSignal(int, int)  # 已下载, 总大小
    finished = pyqtSignal(bool, str)  # 是否成功, 错误信息
    
    def __init__(self, updater: Updater, download_type: str, version_info: VersionInfo = None):
        """
        初始化下载线程
        
        参数:
            updater: 更新器实例
            download_type: 下载类型 ('gui' 或 'sqlmap')
            version_info: 版本信息（仅 GUI 更新需要）
        """
        super().__init__()
        self.updater = updater
        self.download_type = download_type
        self.version_info = version_info
    
    def run(self):
        """执行下载"""
        if self.download_type == 'gui':
            success, error = self.updater.download_gui_update(
                self.version_info,
                self._on_progress
            )
        else:
            success, error = self.updater.download_sqlmap(
                self._on_progress
            )
        
        self.finished.emit(success, error)
    
    def _on_progress(self, downloaded: int, total: int):
        """进度回调"""
        self.progress.emit(downloaded, total)


class UpdateDialog(QDialog):
    """GUI 更新对话框"""
    
    def __init__(self, version_info: VersionInfo, parent=None):
        super().__init__(parent)
        self.version_info = version_info
        self.updater = Updater()
        self.download_thread = None
        
        self.setWindowTitle("发现新版本")
        self.setFixedSize(500, 400)
        self.setup_ui()
    
    def setup_ui(self):
        """设置 UI"""
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(25, 25, 25, 25)
        
        # 标题
        title = QLabel("🎉 发现新版本！")
        title.setFont(QFont("Microsoft YaHei UI", 16, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet(f"color: {COLORS['accent_blue']};")
        layout.addWidget(title)
        
        # 版本信息
        version_frame = QFrame()
        version_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS['bg_tertiary']};
                border-radius: 8px;
                padding: 10px;
            }}
        """)
        version_layout = QHBoxLayout(version_frame)
        
        current_label = QLabel(f"当前版本: {CURRENT_VERSION}")
        current_label.setStyleSheet(f"color: {COLORS['text_muted']};")
        version_layout.addWidget(current_label)
        
        arrow_label = QLabel("→")
        arrow_label.setStyleSheet(f"color: {COLORS['accent_blue']}; font-size: 18px;")
        version_layout.addWidget(arrow_label)
        
        new_label = QLabel(f"最新版本: {self.version_info.version}")
        new_label.setStyleSheet(f"color: {COLORS['success']}; font-weight: bold;")
        version_layout.addWidget(new_label)
        
        version_layout.addStretch()
        layout.addWidget(version_frame)
        
        # 更新日志
        notes_label = QLabel("更新日志:")
        notes_label.setStyleSheet(f"color: {COLORS['text_secondary']}; font-weight: bold;")
        layout.addWidget(notes_label)
        
        self.notes_text = QTextEdit()
        self.notes_text.setPlainText(self.version_info.release_notes or "暂无更新说明")
        self.notes_text.setReadOnly(True)
        self.notes_text.setMaximumHeight(120)
        self.notes_text.setStyleSheet(f"""
            QTextEdit {{
                background-color: {COLORS['bg_secondary']};
                border: 1px solid {COLORS['border']};
                border-radius: 6px;
                padding: 8px;
                color: {COLORS['text_secondary']};
            }}
        """)
        layout.addWidget(self.notes_text)
        
        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setStyleSheet(f"""
            QProgressBar {{
                border: none;
                border-radius: 4px;
                background-color: {COLORS['bg_tertiary']};
                height: 20px;
                text-align: center;
            }}
            QProgressBar::chunk {{
                border-radius: 4px;
                background-color: {COLORS['accent_blue']};
            }}
        """)
        layout.addWidget(self.progress_bar)
        
        # 状态标签
        self.status_label = QLabel("")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet(f"color: {COLORS['text_muted']};")
        layout.addWidget(self.status_label)
        
        layout.addStretch()
        
        # 按钮
        btn_layout = QHBoxLayout()
        
        self.later_btn = QPushButton("稍后再说")
        self.later_btn.setFixedWidth(100)
        self.later_btn.clicked.connect(self.reject)
        btn_layout.addWidget(self.later_btn)
        
        btn_layout.addStretch()
        
        self.update_btn = QPushButton("🚀 立即更新")
        self.update_btn.setProperty("class", "primary")
        self.update_btn.setFixedWidth(120)
        self.update_btn.clicked.connect(self._start_update)
        self.update_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['accent_blue']};
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px 20px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: #89b4fa;
            }}
        """)
        btn_layout.addWidget(self.update_btn)
        
        layout.addLayout(btn_layout)
    
    def _start_update(self):
        """开始更新"""
        self.update_btn.setEnabled(False)
        self.later_btn.setEnabled(False)
        self.progress_bar.setVisible(True)
        # 先设置为动画模式，让用户知道正在下载
        self.progress_bar.setMaximum(0)
        self.status_label.setText("正在连接服务器...")
        QApplication.processEvents()  # 强制刷新界面
        
        # 启动下载线程
        self.download_thread = DownloadThread(
            self.updater, 'gui', self.version_info
        )
        self.download_thread.progress.connect(self._on_progress, Qt.ConnectionType.QueuedConnection)
        self.download_thread.finished.connect(self._on_finished, Qt.ConnectionType.QueuedConnection)
        self.download_thread.start()
    
    def _on_progress(self, downloaded: int, total: int):
        """更新进度"""
        if total > 0:
            # 有总大小时显示百分比
            percent = int(downloaded * 100 / total)
            self.progress_bar.setMaximum(100)
            self.progress_bar.setValue(percent)
            
            # 显示大小
            downloaded_mb = downloaded / (1024 * 1024)
            total_mb = total / (1024 * 1024)
            self.status_label.setText(f"正在下载: {downloaded_mb:.1f} MB / {total_mb:.1f} MB")
        else:
            # 无法获取总大小时使用无限进度条动画
            self.progress_bar.setMaximum(0)  # 设置为无限模式
            downloaded_mb = downloaded / (1024 * 1024)
            self.status_label.setText(f"正在下载: {downloaded_mb:.1f} MB ...")
        
        QApplication.processEvents()  # 强制刷新界面
    
    def _on_finished(self, success: bool, error: str):
        """下载完成"""
        if success:
            self.progress_bar.setMaximum(100)
            self.progress_bar.setValue(100)
            self.status_label.setText("更新完成！")
            self.status_label.setStyleSheet(f"color: {COLORS['success']};")
            
            QMessageBox.information(
                self,
                "更新完成",
                "更新已完成！请重启程序以应用更新。"
            )
            self.accept()
        else:
            self.progress_bar.setMaximum(100)  # 恢复正常模式
            self.status_label.setText(f"更新失败: {error}")
            self.status_label.setStyleSheet(f"color: {COLORS['error']};")
            self.update_btn.setEnabled(True)
            self.later_btn.setEnabled(True)


class DownloadSqlmapDialog(QDialog):
    """下载 SQLMap 对话框"""
    
    # 下载完成信号
    download_completed = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.updater = Updater()
        self.download_thread = None
        
        self.setWindowTitle("下载 SQLMap")
        self.setFixedSize(500, 300)
        self.setup_ui()
    
    def setup_ui(self):
        """设置 UI"""
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(25, 25, 25, 25)
        
        # 标题
        title = QLabel("📥 下载/更新 SQLMap")
        title.setFont(QFont("Microsoft YaHei UI", 14, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet(f"color: {COLORS['accent_blue']};")
        layout.addWidget(title)
        
        # 说明
        info = QLabel(
            "将从 GitHub 官方仓库下载最新版 SQLMap\n"
            "下载完成后将自动解压到程序目录的 sqlmap 文件夹"
        )
        info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        info.setStyleSheet(f"color: {COLORS['text_secondary']};")
        info.setWordWrap(True)
        layout.addWidget(info)
        
        # 警告
        warning = QLabel("⚠️ 如已存在 sqlmap 文件夹，将被覆盖")
        warning.setAlignment(Qt.AlignmentFlag.AlignCenter)
        warning.setStyleSheet(f"color: {COLORS['warning']}; font-size: 11px;")
        layout.addWidget(warning)
        
        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setStyleSheet(f"""
            QProgressBar {{
                border: none;
                border-radius: 4px;
                background-color: {COLORS['bg_tertiary']};
                height: 20px;
                text-align: center;
            }}
            QProgressBar::chunk {{
                border-radius: 4px;
                background-color: {COLORS['success']};
            }}
        """)
        layout.addWidget(self.progress_bar)
        
        # 状态标签
        self.status_label = QLabel("")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet(f"color: {COLORS['text_muted']};")
        layout.addWidget(self.status_label)
        
        layout.addStretch()
        
        # 按钮
        btn_layout = QHBoxLayout()
        
        self.cancel_btn = QPushButton("取消")
        self.cancel_btn.setFixedWidth(100)
        self.cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(self.cancel_btn)
        
        btn_layout.addStretch()
        
        self.download_btn = QPushButton("⬇️ 开始下载")
        self.download_btn.setProperty("class", "primary")
        self.download_btn.setFixedWidth(120)
        self.download_btn.clicked.connect(self._start_download)
        self.download_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['success']};
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px 20px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: #27ae60;
            }}
        """)
        btn_layout.addWidget(self.download_btn)
        
        layout.addLayout(btn_layout)
    
    def _start_download(self):
        """开始下载"""
        self.download_btn.setEnabled(False)
        self.cancel_btn.setEnabled(False)
        self.progress_bar.setVisible(True)
        # 先设置为动画模式
        self.progress_bar.setMaximum(0)
        self.status_label.setText("正在连接服务器...")
        QApplication.processEvents()  # 强制刷新界面
        
        # 启动下载线程
        self.download_thread = DownloadThread(self.updater, 'sqlmap')
        self.download_thread.progress.connect(self._on_progress, Qt.ConnectionType.QueuedConnection)
        self.download_thread.finished.connect(self._on_finished, Qt.ConnectionType.QueuedConnection)
        self.download_thread.start()
    
    def _on_progress(self, downloaded: int, total: int):
        """更新进度"""
        if total > 0:
            # 有总大小时显示百分比
            percent = int(downloaded * 100 / total)
            self.progress_bar.setMaximum(100)
            self.progress_bar.setValue(percent)
            
            downloaded_mb = downloaded / (1024 * 1024)
            total_mb = total / (1024 * 1024)
            self.status_label.setText(f"正在下载: {downloaded_mb:.1f} MB / {total_mb:.1f} MB")
        else:
            # 无法获取总大小时使用无限进度条动画
            self.progress_bar.setMaximum(0)  # 设置为无限模式
            downloaded_mb = downloaded / (1024 * 1024)
            self.status_label.setText(f"正在下载: {downloaded_mb:.1f} MB ...")
        
        QApplication.processEvents()  # 强制刷新界面
    
    def _on_finished(self, success: bool, error: str):
        """下载完成"""
        if success:
            self.progress_bar.setMaximum(100)
            self.progress_bar.setValue(100)
            self.status_label.setText("下载完成！")
            self.status_label.setStyleSheet(f"color: {COLORS['success']};")
            
            # 发送完成信号
            self.download_completed.emit()
            
            QMessageBox.information(
                self,
                "下载完成",
                "SQLMap 下载完成！\n已解压到 sqlmap 目录。"
            )
            self.accept()
        else:
            self.progress_bar.setMaximum(100) # 恢复正常模式
            self.status_label.setText(f"下载失败: {error}")
            self.status_label.setStyleSheet(f"color: {COLORS['error']};")
            self.download_btn.setEnabled(True)
            self.cancel_btn.setEnabled(True)
