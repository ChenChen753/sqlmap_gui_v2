# SQLMap GUI v2

🔒 **Intelligent SQL Injection Detection Graphical Tool**

[![Python](https://img.shields.io/badge/Python-3.7+-blue.svg)](https://python.org)
[![PyQt6](https://img.shields.io/badge/PyQt6-6.4+-green.svg)](https://pypi.org/project/PyQt6/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## ✨ Features

- 🎨 **Modern UI** - 5 themes available (Dark/Light/Blue/Purple/Green)
- 🌐 **Multi-language** - Chinese/English interface
- ⚡ **Quick Config** - Quick/Standard/Deep/Aggressive presets
- 🛡️ **Tamper Scripts** - 70+ bypass scripts in 7 categories
- 📊 **Result Display** - Real-time logs, DB structure tree, data extraction
- 📂 **Batch Scan** - Scan multiple URLs from file, each URL scanned independently
- 💾 **Config Management** - Save/Load scan configurations

## 📋 Requirements

- Windows 10/11
- Python 3.7+
- PyQt6 6.4+
- sqlmap (auto-detect or manual config)

## 🚀 Quick Start

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Launch Application

**Option 1: Double-click start script**
```
Double-click start.bat
```

**Option 2: Command line**
```bash
python main.py
```

## 📖 Usage Guide

### 1️⃣ Configure Target

1. Enter URL in the **Target** tab
2. Optionally set POST data, Cookie, User-Agent
3. **Batch Scan**: Check "Batch URL Scan" and select a file containing URLs (one per line)

### Batch Scan Feature

The batch scan feature allows scanning multiple URLs from a file:
- **Independent Scanning**: Each URL is scanned independently, ensuring complete detection for every target
- **No Skip**: Unlike SQLMap's built-in batch mode, this feature scans all URLs completely
- **Real-time Progress**: Status bar shows current progress `[1/3]`, `[2/3]`, etc.
- **Result Table**: Dedicated tab displays all scan results in a table format
- **Filtering**: Filter results by "All", "Vulnerable", "Safe", "Skipped"
- **Export**: Export batch results to CSV or JSON
- **Copy to Clipboard**: Quick copy results for sharing

### 2️⃣ Select Scan Mode

| Mode | Level | Risk | Description |
|------|-------|------|-------------|
| 🚀 Quick | 1 | 1 | Quick injection detection |
| 🔍 Standard | 2 | 2 | Recommended for daily use |
| 🔬 Deep | 5 | 3 | Comprehensive scan |
| ⚔️ Aggressive | 5 | 3 | All techniques + bypass |

### 3️⃣ Advanced Options

- **Performance**: Threads, timeout, delay
- **Tamper Scripts**: Select WAF bypass scripts
- **Proxy Settings**: HTTP proxy, Tor network
- **OS Features**: OS Shell, file read/write

### 4️⃣ Start Scan

Click **Start Scan** button and view real-time output in the log panel.

## ⚙️ Settings

Menu → Tools → Settings

- **SQLMap Path**: Set sqlmap.py location
- **Theme**: 5 themes available
- **Language**: Chinese/English

## 📁 Project Structure

```
sqlmap_gui_v2/
├── main.py              # Entry point
├── start.bat            # Windows launcher
├── requirements.txt     # Dependencies
├── core/                # Core modules
│   ├── sqlmap_engine.py # SQLMap execution engine
│   ├── command_builder.py # Command builder
│   ├── config_manager.py  # Config manager
│   ├── history_manager.py # History manager
│   └── i18n.py           # Multi-language support
└── ui/                  # UI modules
    ├── theme.py         # Theme styles
    ├── main_window.py   # Main window
    ├── dialogs/         # Dialogs
    ├── panels/          # Panel components
    └── widgets/         # Common widgets
```

## ⚠️ Disclaimer

This tool is for authorized security testing only. Please ensure you have legal authorization before testing any target system.

---

**Developer: ChenChen** | **Version: 2.0.0**
