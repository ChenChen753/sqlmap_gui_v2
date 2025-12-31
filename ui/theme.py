"""
SQLMap GUI v2 主题样式
现代深色主题，采用渐变色和圆角设计
"""

# 主色调定义
COLORS = {
    # 背景色
    'bg_primary': '#1a1b26',      # 主背景
    'bg_secondary': '#24283b',    # 次级背景（卡片）
    'bg_tertiary': '#1f2335',     # 第三级背景
    'bg_hover': '#292e42',        # 悬停背景
    
    # 文字色
    'text_primary': '#c0caf5',    # 主文字
    'text_secondary': '#9aa5ce',  # 次级文字
    'text_muted': '#565f89',      # 暗淡文字
    
    # 强调色
    'accent_blue': '#7aa2f7',     # 蓝色强调
    'accent_green': '#9ece6a',    # 绿色强调
    'accent_purple': '#bb9af7',   # 紫色强调
    'accent_orange': '#ff9e64',   # 橙色强调
    'accent_red': '#f7768e',      # 红色强调
    'accent_cyan': '#7dcfff',     # 青色强调
    
    # 边框色
    'border': '#3b4261',          # 边框
    'border_focus': '#7aa2f7',    # 聚焦边框
    
    # 状态色
    'success': '#9ece6a',
    'warning': '#e0af68',
    'error': '#f7768e',
    'info': '#7aa2f7',
}

# 字体定义
FONTS = {
    'primary': 'Microsoft YaHei UI',
    'secondary': 'Segoe UI',
    'monospace': 'Consolas',
    'size_small': 11,
    'size_normal': 13,
    'size_large': 15,
    'size_title': 18,
    'size_header': 24,
}

# 主样式表
DARK_THEME = f"""
/* ==================== 全局样式 ==================== */
QMainWindow {{
    background-color: {COLORS['bg_primary']};
}}

QWidget {{
    background-color: transparent;
    color: {COLORS['text_primary']};
    font-family: '{FONTS['primary']}', '{FONTS['secondary']}', sans-serif;
    font-size: {FONTS['size_normal']}px;
}}

/* ==================== 标签样式 ==================== */
QLabel {{
    color: {COLORS['text_primary']};
    background: transparent;
    padding: 2px;
}}

QLabel[class="title"] {{
    font-size: {FONTS['size_title']}px;
    font-weight: bold;
    color: {COLORS['accent_blue']};
}}

QLabel[class="subtitle"] {{
    font-size: {FONTS['size_large']}px;
    color: {COLORS['text_secondary']};
}}

/* ==================== 输入框样式 ==================== */
QLineEdit {{
    background-color: {COLORS['bg_tertiary']};
    border: 2px solid {COLORS['border']};
    border-radius: 8px;
    padding: 10px 15px;
    color: {COLORS['text_primary']};
    selection-background-color: {COLORS['accent_blue']};
}}

QLineEdit:focus {{
    border-color: {COLORS['accent_blue']};
}}

QLineEdit:hover {{
    border-color: {COLORS['text_muted']};
}}

QLineEdit::placeholder {{
    color: {COLORS['text_muted']};
}}

QLineEdit:disabled {{
    background-color: {COLORS['bg_primary']};
    color: {COLORS['text_muted']};
}}

/* ==================== 文本编辑框样式 ==================== */
QTextEdit {{
    background-color: {COLORS['bg_tertiary']};
    border: 2px solid {COLORS['border']};
    border-radius: 8px;
    padding: 10px;
    color: {COLORS['text_primary']};
    font-family: '{FONTS['monospace']}', monospace;
    selection-background-color: {COLORS['accent_blue']};
}}

QTextEdit:focus {{
    border-color: {COLORS['accent_blue']};
}}

/* ==================== 按钮样式 ==================== */
QPushButton {{
    background-color: {COLORS['accent_blue']};
    color: #1a1b26;
    border: none;
    border-radius: 8px;
    padding: 10px 20px;
    font-weight: bold;
    font-size: {FONTS['size_normal']}px;
}}

QPushButton:hover {{
    background-color: #89b4fa;
}}

QPushButton:pressed {{
    background-color: #6a8fd6;
}}

QPushButton:disabled {{
    background-color: {COLORS['text_muted']};
    color: {COLORS['bg_primary']};
}}

/* 主要按钮 - 渐变色 */
QPushButton[class="primary"] {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 {COLORS['accent_blue']}, 
        stop:1 {COLORS['accent_cyan']});
}}

QPushButton[class="primary"]:hover {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #89b4fa, 
        stop:1 #99d9ff);
}}

/* 成功按钮 */
QPushButton[class="success"] {{
    background-color: {COLORS['accent_green']};
}}

QPushButton[class="success"]:hover {{
    background-color: #b5e07a;
}}

/* 危险按钮 */
QPushButton[class="danger"] {{
    background-color: {COLORS['accent_red']};
}}

QPushButton[class="danger"]:hover {{
    background-color: #f99bab;
}}

/* 次要按钮 */
QPushButton[class="secondary"] {{
    background-color: {COLORS['bg_secondary']};
    border: 2px solid {COLORS['border']};
    color: {COLORS['text_primary']};
}}

QPushButton[class="secondary"]:hover {{
    background-color: {COLORS['bg_hover']};
    border-color: {COLORS['accent_blue']};
}}

/* ==================== 复选框样式 ==================== */
QCheckBox {{
    spacing: 8px;
    color: {COLORS['text_primary']};
}}

QCheckBox::indicator {{
    width: 20px;
    height: 20px;
    border-radius: 4px;
    border: 2px solid {COLORS['border']};
    background-color: {COLORS['bg_tertiary']};
}}

QCheckBox::indicator:hover {{
    border-color: {COLORS['accent_blue']};
}}

QCheckBox::indicator:checked {{
    background-color: {COLORS['accent_blue']};
    border-color: {COLORS['accent_blue']};
}}

QCheckBox::indicator:checked:hover {{
    background-color: #89b4fa;
}}

QCheckBox:disabled {{
    color: {COLORS['text_muted']};
}}

/* ==================== 单选按钮样式 ==================== */
QRadioButton {{
    spacing: 8px;
    color: {COLORS['text_primary']};
}}

QRadioButton::indicator {{
    width: 20px;
    height: 20px;
    border-radius: 10px;
    border: 2px solid {COLORS['border']};
    background-color: {COLORS['bg_tertiary']};
}}

QRadioButton::indicator:hover {{
    border-color: {COLORS['accent_blue']};
}}

QRadioButton::indicator:checked {{
    background-color: {COLORS['accent_blue']};
    border-color: {COLORS['accent_blue']};
}}

/* ==================== 下拉框样式 ==================== */
QComboBox {{
    background-color: {COLORS['bg_tertiary']};
    border: 2px solid {COLORS['border']};
    border-radius: 8px;
    padding: 8px 15px;
    color: {COLORS['text_primary']};
    min-width: 100px;
}}

QComboBox:hover {{
    border-color: {COLORS['text_muted']};
}}

QComboBox:focus {{
    border-color: {COLORS['accent_blue']};
}}

QComboBox::drop-down {{
    border: none;
    width: 30px;
}}

QComboBox::down-arrow {{
    image: none;
    border-left: 5px solid transparent;
    border-right: 5px solid transparent;
    border-top: 6px solid {COLORS['text_secondary']};
    margin-right: 10px;
}}

QComboBox QAbstractItemView {{
    background-color: {COLORS['bg_secondary']};
    border: 2px solid {COLORS['border']};
    border-radius: 8px;
    selection-background-color: {COLORS['accent_blue']};
    selection-color: #1a1b26;
    outline: none;
}}

/* ==================== 数字输入框样式 ==================== */
QSpinBox {{
    background-color: {COLORS['bg_tertiary']};
    border: 2px solid {COLORS['border']};
    border-radius: 8px;
    padding: 8px 15px;
    color: {COLORS['text_primary']};
}}

QSpinBox:focus {{
    border-color: {COLORS['accent_blue']};
}}

QSpinBox::up-button, QSpinBox::down-button {{
    background-color: {COLORS['bg_hover']};
    border: none;
    width: 20px;
}}

QSpinBox::up-button:hover, QSpinBox::down-button:hover {{
    background-color: {COLORS['accent_blue']};
}}

/* ==================== 分组框样式 ==================== */
QGroupBox {{
    background-color: {COLORS['bg_secondary']};
    border: 2px solid {COLORS['border']};
    border-radius: 12px;
    margin-top: 15px;
    padding: 20px 15px 15px 15px;
    font-weight: bold;
}}

QGroupBox::title {{
    subcontrol-origin: margin;
    subcontrol-position: top left;
    left: 15px;
    top: 3px;
    padding: 0 8px;
    color: {COLORS['accent_blue']};
    background-color: {COLORS['bg_secondary']};
}}

/* ==================== 标签页样式 ==================== */
QTabWidget::pane {{
    background-color: {COLORS['bg_secondary']};
    border: 2px solid {COLORS['border']};
    border-radius: 12px;
    margin-top: -1px;
}}

QTabBar::tab {{
    background-color: {COLORS['bg_tertiary']};
    color: {COLORS['text_secondary']};
    border: 2px solid {COLORS['border']};
    border-bottom: none;
    border-top-left-radius: 8px;
    border-top-right-radius: 8px;
    padding: 10px 20px;
    margin-right: 2px;
}}

QTabBar::tab:hover {{
    background-color: {COLORS['bg_hover']};
    color: {COLORS['text_primary']};
}}

QTabBar::tab:selected {{
    background-color: {COLORS['bg_secondary']};
    color: {COLORS['accent_blue']};
    border-color: {COLORS['accent_blue']};
    border-bottom: 2px solid {COLORS['bg_secondary']};
}}

/* ==================== 进度条样式 ==================== */
QProgressBar {{
    background-color: {COLORS['bg_tertiary']};
    border: none;
    border-radius: 8px;
    height: 16px;
    text-align: center;
    color: {COLORS['text_primary']};
}}

QProgressBar::chunk {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 {COLORS['accent_blue']}, 
        stop:1 {COLORS['accent_cyan']});
    border-radius: 8px;
}}

/* ==================== 滚动条样式 ==================== */
QScrollBar:vertical {{
    background-color: {COLORS['bg_tertiary']};
    width: 12px;
    border-radius: 6px;
    margin: 0;
}}

QScrollBar::handle:vertical {{
    background-color: {COLORS['border']};
    border-radius: 6px;
    min-height: 30px;
}}

QScrollBar::handle:vertical:hover {{
    background-color: {COLORS['text_muted']};
}}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0;
}}

QScrollBar:horizontal {{
    background-color: {COLORS['bg_tertiary']};
    height: 12px;
    border-radius: 6px;
    margin: 0;
}}

QScrollBar::handle:horizontal {{
    background-color: {COLORS['border']};
    border-radius: 6px;
    min-width: 30px;
}}

QScrollBar::handle:horizontal:hover {{
    background-color: {COLORS['text_muted']};
}}

QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
    width: 0;
}}

/* ==================== 分割器样式 ==================== */
QSplitter::handle {{
    background-color: {COLORS['border']};
}}

QSplitter::handle:horizontal {{
    width: 2px;
}}

QSplitter::handle:vertical {{
    height: 2px;
}}

QSplitter::handle:hover {{
    background-color: {COLORS['accent_blue']};
}}

/* ==================== 树形视图样式 ==================== */
QTreeWidget {{
    background-color: {COLORS['bg_tertiary']};
    border: 2px solid {COLORS['border']};
    border-radius: 8px;
    outline: none;
}}

QTreeWidget::item {{
    padding: 6px;
    border-radius: 4px;
}}

QTreeWidget::item:hover {{
    background-color: {COLORS['bg_hover']};
}}

QTreeWidget::item:selected {{
    background-color: {COLORS['accent_blue']};
    color: #1a1b26;
}}

QTreeWidget::branch:has-children:closed {{
    image: none;
    border-image: none;
}}

QTreeWidget::branch:has-children:open {{
    image: none;
    border-image: none;
}}

QHeaderView::section {{
    background-color: {COLORS['bg_secondary']};
    color: {COLORS['text_secondary']};
    padding: 8px;
    border: none;
    border-bottom: 2px solid {COLORS['border']};
    font-weight: bold;
}}

/* ==================== 菜单栏样式 ==================== */
QMenuBar {{
    background-color: {COLORS['bg_primary']};
    color: {COLORS['text_primary']};
    border-bottom: 1px solid {COLORS['border']};
    padding: 5px;
}}

QMenuBar::item {{
    padding: 8px 15px;
    border-radius: 6px;
}}

QMenuBar::item:selected {{
    background-color: {COLORS['bg_hover']};
}}

QMenu {{
    background-color: {COLORS['bg_secondary']};
    border: 2px solid {COLORS['border']};
    border-radius: 8px;
    padding: 5px;
}}

QMenu::item {{
    padding: 8px 30px;
    border-radius: 4px;
}}

QMenu::item:selected {{
    background-color: {COLORS['accent_blue']};
    color: #1a1b26;
}}

QMenu::separator {{
    height: 1px;
    background-color: {COLORS['border']};
    margin: 5px 10px;
}}

/* ==================== 状态栏样式 ==================== */
QStatusBar {{
    background-color: {COLORS['bg_secondary']};
    color: {COLORS['text_secondary']};
    border-top: 1px solid {COLORS['border']};
    padding: 5px 10px;
}}

QStatusBar::item {{
    border: none;
}}

/* ==================== 工具提示样式 ==================== */
QToolTip {{
    background-color: {COLORS['bg_secondary']};
    color: {COLORS['text_primary']};
    border: 1px solid {COLORS['border']};
    border-radius: 6px;
    padding: 8px;
}}

/* ==================== 消息框样式 ==================== */
QMessageBox {{
    background-color: {COLORS['bg_secondary']};
}}

QMessageBox QLabel {{
    color: {COLORS['text_primary']};
}}

QMessageBox QPushButton {{
    min-width: 80px;
}}
"""

# 卡片样式
CARD_STYLE = f"""
background-color: {COLORS['bg_secondary']};
border: 2px solid {COLORS['border']};
border-radius: 12px;
padding: 15px;
"""

# 高亮卡片样式
HIGHLIGHT_CARD_STYLE = f"""
background-color: {COLORS['bg_secondary']};
border: 2px solid {COLORS['accent_blue']};
border-radius: 12px;
padding: 15px;
"""

def get_status_style(status: str) -> str:
    """根据状态获取样式"""
    styles = {
        'success': f"color: {COLORS['success']};",
        'warning': f"color: {COLORS['warning']};",
        'error': f"color: {COLORS['error']};",
        'info': f"color: {COLORS['info']};",
    }
    return styles.get(status, f"color: {COLORS['text_primary']};")


# ==================== 多主题支持 ====================

# 主题配色定义
THEMES = {
    'dark': {
        'name': '深色主题',
        'bg_primary': '#1a1b26',
        'bg_secondary': '#24283b',
        'bg_tertiary': '#1f2335',
        'bg_hover': '#292e42',
        'text_primary': '#c0caf5',
        'text_secondary': '#9aa5ce',
        'text_muted': '#565f89',
        'accent_blue': '#7aa2f7',
        'accent_green': '#9ece6a',
        'accent_purple': '#bb9af7',
        'accent_orange': '#ff9e64',
        'accent_red': '#f7768e',
        'accent_cyan': '#7dcfff',
        'border': '#3b4261',
        'border_focus': '#7aa2f7',
        'success': '#9ece6a',
        'warning': '#e0af68',
        'error': '#f7768e',
        'info': '#7aa2f7',
    },
    'light': {
        'name': '浅色主题',
        'bg_primary': '#f5f5f5',
        'bg_secondary': '#ffffff',
        'bg_tertiary': '#e8e8e8',
        'bg_hover': '#dcdcdc',
        'text_primary': '#333333',
        'text_secondary': '#666666',
        'text_muted': '#999999',
        'accent_blue': '#2196f3',
        'accent_green': '#4caf50',
        'accent_purple': '#9c27b0',
        'accent_orange': '#ff9800',
        'accent_red': '#f44336',
        'accent_cyan': '#00bcd4',
        'border': '#cccccc',
        'border_focus': '#2196f3',
        'success': '#4caf50',
        'warning': '#ff9800',
        'error': '#f44336',
        'info': '#2196f3',
    },
    'blue': {
        'name': '深蓝主题',
        'bg_primary': '#0a192f',
        'bg_secondary': '#112240',
        'bg_tertiary': '#0d1b2a',
        'bg_hover': '#1d3557',
        'text_primary': '#ccd6f6',
        'text_secondary': '#8892b0',
        'text_muted': '#495670',
        'accent_blue': '#64ffda',
        'accent_green': '#64ffda',
        'accent_purple': '#c792ea',
        'accent_orange': '#ffcb6b',
        'accent_red': '#ff5370',
        'accent_cyan': '#89ddff',
        'border': '#233554',
        'border_focus': '#64ffda',
        'success': '#64ffda',
        'warning': '#ffcb6b',
        'error': '#ff5370',
        'info': '#89ddff',
    },
    'purple': {
        'name': '紫色主题',
        'bg_primary': '#1e1e2e',
        'bg_secondary': '#302d41',
        'bg_tertiary': '#232136',
        'bg_hover': '#3e3d53',
        'text_primary': '#d9e0ee',
        'text_secondary': '#c3bac6',
        'text_muted': '#6e6a86',
        'accent_blue': '#96cdfb',
        'accent_green': '#abe9b3',
        'accent_purple': '#ddb6f2',
        'accent_orange': '#f8bd96',
        'accent_red': '#f28fad',
        'accent_cyan': '#89dceb',
        'border': '#575268',
        'border_focus': '#ddb6f2',
        'success': '#abe9b3',
        'warning': '#f8bd96',
        'error': '#f28fad',
        'info': '#96cdfb',
    },
    'green': {
        'name': '绿色护眼',
        'bg_primary': '#1d2021',
        'bg_secondary': '#282828',
        'bg_tertiary': '#1d2021',
        'bg_hover': '#3c3836',
        'text_primary': '#ebdbb2',
        'text_secondary': '#d5c4a1',
        'text_muted': '#665c54',
        'accent_blue': '#83a598',
        'accent_green': '#b8bb26',
        'accent_purple': '#d3869b',
        'accent_orange': '#fe8019',
        'accent_red': '#fb4934',
        'accent_cyan': '#8ec07c',
        'border': '#504945',
        'border_focus': '#b8bb26',
        'success': '#b8bb26',
        'warning': '#fabd2f',
        'error': '#fb4934',
        'info': '#83a598',
    },
}


def get_theme_names() -> dict:
    """获取所有主题名称"""
    return {name: theme['name'] for name, theme in THEMES.items()}


def get_theme_colors(theme_name: str) -> dict:
    """获取指定主题的颜色配置"""
    if theme_name in THEMES:
        return THEMES[theme_name]
    return THEMES['dark']


def generate_theme_stylesheet(theme_name: str) -> str:
    """根据主题名称生成样式表"""
    colors = get_theme_colors(theme_name)
    
    return f"""
/* ==================== 全局样式 ==================== */
QMainWindow {{
    background-color: {colors['bg_primary']};
}}

QWidget {{
    background-color: transparent;
    color: {colors['text_primary']};
    font-family: 'Microsoft YaHei UI', 'Segoe UI', sans-serif;
    font-size: 13px;
}}

QDialog {{
    background-color: {colors['bg_primary']};
}}

/* ==================== 标签样式 ==================== */
QLabel {{
    color: {colors['text_primary']};
    background: transparent;
    padding: 2px;
}}

/* ==================== 输入框样式 ==================== */
QLineEdit {{
    background-color: {colors['bg_tertiary']};
    border: 2px solid {colors['border']};
    border-radius: 8px;
    padding: 10px 15px;
    color: {colors['text_primary']};
    selection-background-color: {colors['accent_blue']};
}}

QLineEdit:focus {{
    border-color: {colors['accent_blue']};
}}

QLineEdit:disabled {{
    background-color: {colors['bg_primary']};
    color: {colors['text_muted']};
}}

/* ==================== 按钮样式 ==================== */
QPushButton {{
    background-color: {colors['accent_blue']};
    color: {colors['bg_primary']};
    border: none;
    border-radius: 8px;
    padding: 10px 20px;
    font-weight: bold;
}}

QPushButton:hover {{
    background-color: {colors['accent_cyan']};
}}

QPushButton:disabled {{
    background-color: {colors['text_muted']};
    color: {colors['bg_primary']};
}}

QPushButton[class="primary"] {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 {colors['accent_blue']}, 
        stop:1 {colors['accent_cyan']});
}}

QPushButton[class="secondary"] {{
    background-color: {colors['bg_secondary']};
    border: 2px solid {colors['border']};
    color: {colors['text_primary']};
}}

QPushButton[class="danger"] {{
    background-color: {colors['accent_red']};
}}

/* ==================== 复选框样式 ==================== */
QCheckBox {{
    spacing: 8px;
    color: {colors['text_primary']};
}}

QCheckBox::indicator {{
    width: 20px;
    height: 20px;
    border-radius: 4px;
    border: 2px solid {colors['border']};
    background-color: {colors['bg_tertiary']};
}}

QCheckBox::indicator:checked {{
    background-color: {colors['accent_blue']};
    border-color: {colors['accent_blue']};
}}

/* ==================== 下拉框样式 ==================== */
QComboBox {{
    background-color: {colors['bg_tertiary']};
    border: 2px solid {colors['border']};
    border-radius: 8px;
    padding: 8px 15px;
    color: {colors['text_primary']};
}}

QComboBox:focus {{
    border-color: {colors['accent_blue']};
}}

QComboBox QAbstractItemView {{
    background-color: {colors['bg_secondary']};
    border: 2px solid {colors['border']};
    selection-background-color: {colors['accent_blue']};
}}

/* ==================== 分组框样式 ==================== */
QGroupBox {{
    background-color: {colors['bg_secondary']};
    border: 2px solid {colors['border']};
    border-radius: 12px;
    margin-top: 15px;
    padding: 20px 15px 15px 15px;
    font-weight: bold;
}}

QGroupBox::title {{
    subcontrol-origin: margin;
    subcontrol-position: top left;
    left: 15px;
    top: 3px;
    padding: 0 8px;
    color: {colors['accent_blue']};
    background-color: {colors['bg_secondary']};
}}

/* ==================== 标签页样式 ==================== */
QTabWidget::pane {{
    background-color: {colors['bg_secondary']};
    border: 2px solid {colors['border']};
    border-radius: 12px;
}}

QTabBar::tab {{
    background-color: {colors['bg_tertiary']};
    color: {colors['text_secondary']};
    border: 2px solid {colors['border']};
    border-bottom: none;
    border-top-left-radius: 8px;
    border-top-right-radius: 8px;
    padding: 10px 20px;
    margin-right: 2px;
}}

QTabBar::tab:selected {{
    background-color: {colors['bg_secondary']};
    color: {colors['accent_blue']};
    border-color: {colors['accent_blue']};
}}

/* ==================== 滚动条样式 ==================== */
QScrollBar:vertical {{
    background-color: {colors['bg_tertiary']};
    width: 12px;
    border-radius: 6px;
}}

QScrollBar::handle:vertical {{
    background-color: {colors['border']};
    border-radius: 6px;
    min-height: 30px;
}}

QScrollBar::handle:vertical:hover {{
    background-color: {colors['text_muted']};
}}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0;
}}

/* ==================== 菜单样式 ==================== */
QMenuBar {{
    background-color: {colors['bg_primary']};
    color: {colors['text_primary']};
    border-bottom: 1px solid {colors['border']};
}}

QMenuBar::item:selected {{
    background-color: {colors['bg_hover']};
}}

QMenu {{
    background-color: {colors['bg_secondary']};
    border: 2px solid {colors['border']};
    border-radius: 8px;
}}

QMenu::item:selected {{
    background-color: {colors['accent_blue']};
    color: {colors['bg_primary']};
}}

/* ==================== 状态栏样式 ==================== */
QStatusBar {{
    background-color: {colors['bg_secondary']};
    color: {colors['text_secondary']};
    border-top: 1px solid {colors['border']};
}}

/* ==================== 列表样式 ==================== */
QListWidget {{
    background-color: {colors['bg_tertiary']};
    border: 2px solid {colors['border']};
    border-radius: 8px;
}}

QListWidget::item {{
    padding: 5px;
    border-radius: 4px;
}}

QListWidget::item:selected {{
    background-color: {colors['accent_blue']};
    color: {colors['bg_primary']};
}}

/* ==================== 文本编辑框样式 ==================== */
QTextEdit {{
    background-color: {colors['bg_tertiary']};
    border: 2px solid {colors['border']};
    border-radius: 8px;
    padding: 10px;
    color: {colors['text_primary']};
}}

QTextEdit:focus {{
    border-color: {colors['accent_blue']};
}}

/* ==================== 进度条样式 ==================== */
QProgressBar {{
    background-color: {colors['bg_tertiary']};
    border: none;
    border-radius: 8px;
    height: 16px;
    text-align: center;
}}

QProgressBar::chunk {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 {colors['accent_blue']}, 
        stop:1 {colors['accent_cyan']});
    border-radius: 8px;
}}

/* ==================== 数字输入框样式 ==================== */
QSpinBox {{
    background-color: {colors['bg_tertiary']};
    border: 2px solid {colors['border']};
    border-radius: 8px;
    padding: 8px 15px;
    color: {colors['text_primary']};
}}

QSpinBox:focus {{
    border-color: {colors['accent_blue']};
}}

/* ==================== 工具提示样式 ==================== */
QToolTip {{
    background-color: {colors['bg_secondary']};
    color: {colors['text_primary']};
    border: 1px solid {colors['border']};
    border-radius: 6px;
    padding: 8px;
}}

/* ==================== 树形视图样式 ==================== */
QTreeWidget {{
    background-color: {colors['bg_tertiary']};
    border: 2px solid {colors['border']};
    border-radius: 8px;
}}

QTreeWidget::item:selected {{
    background-color: {colors['accent_blue']};
    color: {colors['bg_primary']};
}}

/* ==================== 卡片组件样式 ==================== */
QFrame#CardWidget, QFrame[class="card"] {{
    background-color: {colors['bg_secondary']};
    border: 2px solid {colors['border']};
    border-radius: 12px;
}}

QFrame#CardWidget[highlight="true"] {{
    border-color: {colors['accent_blue']};
}}

QLabel#cardTitle, QLabel[class="card-title"] {{
    color: {colors['accent_blue']};
    font-size: 14px;
    font-weight: bold;
    padding-bottom: 8px;
    border-bottom: 1px solid {colors['border']};
    background: transparent;
}}

/* ==================== 统计卡片样式 ==================== */
QFrame#StatCard, QFrame[class="stat-card"] {{
    background-color: {colors['bg_secondary']};
    border: 2px solid {colors['border']};
    border-radius: 10px;
}}

QLabel#statTitle {{
    color: {colors['text_secondary']};
    font-size: 11px;
    background: transparent;
}}

QLabel#statValue {{
    color: {colors['text_primary']};
    font-size: 18px;
    font-weight: bold;
    background: transparent;
}}

/* ==================== 单选按钮样式 ==================== */
QRadioButton {{
    spacing: 8px;
    color: {colors['text_primary']};
}}

QRadioButton::indicator {{
    width: 18px;
    height: 18px;
    border-radius: 9px;
    border: 2px solid {colors['border']};
    background-color: {colors['bg_tertiary']};
}}

QRadioButton::indicator:hover {{
    border-color: {colors['accent_blue']};
}}

QRadioButton::indicator:checked {{
    background-color: {colors['accent_blue']};
    border-color: {colors['accent_blue']};
}}

/* ==================== 分割器样式 ==================== */
QSplitter::handle {{
    background-color: {colors['border']};
}}

QSplitter::handle:horizontal {{
    width: 3px;
}}

QSplitter::handle:vertical {{
    height: 3px;
}}

QSplitter::handle:hover {{
    background-color: {colors['accent_blue']};
}}

/* ==================== 滚动区域样式 ==================== */
QScrollArea {{
    background-color: transparent;
    border: none;
}}

QScrollArea > QWidget > QWidget {{
    background-color: transparent;
}}

/* ==================== 水平滚动条样式 ==================== */
QScrollBar:horizontal {{
    background-color: {colors['bg_tertiary']};
    height: 10px;
    border-radius: 5px;
}}

QScrollBar::handle:horizontal {{
    background-color: {colors['border']};
    border-radius: 5px;
    min-width: 30px;
}}

QScrollBar::handle:horizontal:hover {{
    background-color: {colors['text_muted']};
}}

QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
    width: 0;
}}

/* ==================== 模式选项卡片样式 ==================== */
QFrame#modeOption {{
    background-color: {colors['bg_tertiary']};
    border: 2px solid {colors['border']};
    border-radius: 8px;
}}

QFrame#modeOption:hover {{
    border-color: {colors['accent_blue']};
}}

/* ==================== 头部区域样式 ==================== */
QFrame#header {{
    background-color: {colors['bg_secondary']};
    border-bottom: 2px solid {colors['border']};
    border-radius: 10px;
}}

QLabel#headerTitle {{
    color: {colors['accent_blue']};
    background: transparent;
}}

QLabel#headerSubtitle {{
    color: {colors['text_muted']};
    background: transparent;
}}

QLabel#statusIndicator {{
    color: {colors['success']};
    background: transparent;
}}

/* ==================== 底部控制栏样式 ==================== */
QFrame#controlBar {{
    background-color: {colors['bg_secondary']};
    border-top: 2px solid {colors['border']};
    border-radius: 10px;
}}

QLabel#commandPreview {{
    color: {colors['text_muted']};
    background: transparent;
}}

/* ==================== 区块标签样式 ==================== */
QLabel#sectionLabel {{
    color: {colors['accent_blue']};
    background: transparent;
}}

/* ==================== 按钮样式 ==================== */
QPushButton {{
    min-width: 80px;
    min-height: 34px;
    padding: 6px 12px;
}}

QPushButton[class="success"] {{
    background-color: {colors['accent_green']};
}}

/* ==================== 标签页圆角优化 ==================== */
QTabWidget::pane {{
    border-radius: 10px;
}}

/* ==================== 下拉框样式优化 ==================== */
QComboBox::drop-down {{
    border: none;
    width: 30px;
}}

QComboBox::down-arrow {{
    image: none;
    border-left: 5px solid transparent;
    border-right: 5px solid transparent;
    border-top: 6px solid {colors['text_secondary']};
    margin-right: 10px;
}}
"""
