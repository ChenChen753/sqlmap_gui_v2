# SQLMap GUI v2

🔒 **智能 SQL 注入检测图形化工具**

[![Python](https://img.shields.io/badge/Python-3.7+-blue.svg)](https://python.org)
[![PyQt6](https://img.shields.io/badge/PyQt6-6.4+-green.svg)](https://pypi.org/project/PyQt6/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## ✨ 功能特点

- 🎨 **现代化界面** - 5 种主题可选（深色/浅色/深蓝/紫色/绿色护眼）
- ⚡ **快速配置** - 快速/标准/深度/激进等预设模式
- 🛡️ **Tamper 脚本** - 70+ 种绕过脚本，7 大分类
- 📊 **结果展示** - 实时日志、数据库结构树、数据提取
- 💾 **配置管理** - 保存/加载扫描配置，下次启动自动加载
- 📜 **扫描历史** - 查看历史扫描记录和详细结果

## 📋 系统要求

- Windows 10/11
- Python 3.7+
- PyQt6 6.4+
- sqlmap (需单独下载，放置于 `sqlmap` 目录)

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置 SQLMap

创建一个sqlmap文件夹 将 SQLmap 解压到程序目录内的 `sqlmap` 文件夹：

```
sqlmap_gui_v2/
├── main.py
├── core/
├── ui/
└── sqlmap/            # SQLMap 目录（放这里）
    ├── sqlmap.py      # SQLMap 主程序
    ├── lib/
    └── ...
```

或在程序中通过 **设置 → SQLMap 路径** 手动指定。

### 3. 启动程序

**方式一：双击启动脚本**
```
双击 start.bat
```

**方式二：命令行启动**
```bash
python main.py
```

## 📖 使用说明

### 1️⃣ 配置目标

1. 在 **目标** 标签页输入 URL（必须包含参数，如 `?id=1`）
2. 可选设置 POST 数据、Cookie、User-Agent
3. 支持从文件批量导入 URL

### 2️⃣ 选择扫描模式

| 模式 | Level | Risk | 说明 |
|------|-------|------|------|
| 🚀 快速检测 | 1 | 1 | 快速判断是否存在注入 |
| 🔍 标准扫描 | 2 | 2 | 推荐日常使用 |
| 🔬 深度扫描 | 5 | 3 | 全面深入扫描 |
| ⚔️ 激进模式 | 5 | 3 | 全部技术+绕过 |

### 3️⃣ 高级选项

- **性能配置**: 线程数、超时、延迟
- **Tamper 脚本**: 选择绕过 WAF 的脚本
- **代理设置**: HTTP 代理、Tor 网络
- **信息枚举**: 数据库、表、列、数据提取

### 4️⃣ 开始扫描

1. 点击 **开始扫描** 按钮
2. 在日志面板查看实时输出
3. 扫描完成后查看结果面板

### 5️⃣ 保存配置

- 点击 **文件 → 保存配置** 保存当前设置
- 下次启动时自动加载保存的配置

### 6️⃣ 查看历史

- 点击 **工具 → 扫描历史** 查看历史扫描记录
- 可以加载历史目标重新扫描

## 📁 打包文件清单

打包发布时需要包含以下文件：

```
sqlmap_gui_v2/
├── main.py              # 程序入口 [必需]
├── start.bat            # Windows 启动脚本 [必需]
├── requirements.txt     # 依赖列表 [必需]
├── README.md            # 使用说明 [必需]
├── core/                # 核心模块 [必需]
│   ├── __init__.py
│   ├── sqlmap_engine.py
│   ├── command_builder.py
│   ├── config_manager.py
│   ├── history_manager.py
│   └── i18n.py
└── ui/                  # 界面模块 [必需]
    ├── __init__.py
    ├── theme.py
    ├── main_window.py
    ├── dialogs/
    ├── panels/
    └── widgets/
```

**不需要打包的文件**（运行时自动生成）:
- `config.ini` - 配置文件
- `history.db` - 历史记录数据库
- `__pycache__/` - Python 缓存目录

**另需提供 SQLMap**:
- 用户需自行下载 sqlmap 并放置于 `sqlmap-master` 目录

## ⚙️ 设置

菜单 → 工具 → 设置

- **SQLMap 路径**: 设置 sqlmap.py 位置
- **主题切换**: 5 种主题可选
- **自动保存**: 启用/禁用自动保存配置

## ⚠️ 免责声明

本工具仅供授权安全测试使用。使用前请确保获得目标系统的合法授权。

---

**开发者：辰辰** | **版本：2.0.0**
