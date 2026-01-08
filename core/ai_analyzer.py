"""
AI 分析模块
支持多种 AI 后端进行扫描日志分析和命令推荐
"""

import json
import requests
from enum import Enum
from typing import Optional, Dict, Any, Callable
from dataclasses import dataclass


class AIProvider(Enum):
    """AI 服务提供商"""
    OLLAMA = "ollama"           # 本地 Ollama
    OPENAI = "openai"           # OpenAI
    CLAUDE = "claude"           # Anthropic Claude
    DEEPSEEK = "deepseek"       # DeepSeek（国内推荐）
    QWEN = "qwen"               # 阿里通义千问
    ZHIPU = "zhipu"             # 智谱 GLM
    MOONSHOT = "moonshot"       # 月之暗面 Kimi
    CUSTOM = "custom"           # 自定义 API


# AI 服务预设配置
AI_PROVIDER_PRESETS = {
    AIProvider.OLLAMA: {
        "name": "Ollama（本地）",
        "base_url": "http://localhost:11434",
        "default_model": "qwen2:7b",
        "is_local": True,
    },
    AIProvider.OPENAI: {
        "name": "OpenAI",
        "base_url": "https://api.openai.com/v1",
        "default_model": "gpt-4o-mini",
        "is_local": False,
    },
    AIProvider.CLAUDE: {
        "name": "Claude",
        "base_url": "https://api.anthropic.com",
        "default_model": "claude-3-haiku-20240307",
        "is_local": False,
    },
    AIProvider.DEEPSEEK: {
        "name": "DeepSeek",
        "base_url": "https://api.deepseek.com",
        "default_model": "deepseek-chat",
        "is_local": False,
    },
    AIProvider.QWEN: {
        "name": "阿里通义千问",
        "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
        "default_model": "qwen-turbo",
        "is_local": False,
    },
    AIProvider.ZHIPU: {
        "name": "智谱GLM",
        "base_url": "https://open.bigmodel.cn/api/paas/v4",
        "default_model": "glm-4-flash",
        "is_local": False,
    },
    AIProvider.MOONSHOT: {
        "name": "月之暗面Kimi",
        "base_url": "https://api.moonshot.cn/v1",
        "default_model": "moonshot-v1-8k",
        "is_local": False,
    },
    AIProvider.CUSTOM: {
        "name": "自定义 API",
        "base_url": "",
        "default_model": "",
        "is_local": False,
    },
}


@dataclass
class AIConfig:
    """AI 配置"""
    provider: AIProvider
    api_key: str = ""
    base_url: str = ""
    model: str = ""
    max_tokens: int = 2000
    temperature: float = 0.7
    timeout: int = 60


@dataclass
class AIResponse:
    """AI 响应结果"""
    success: bool
    content: str = ""
    error: str = ""
    usage: Dict[str, int] = None
    
    def __post_init__(self):
        if self.usage is None:
            self.usage = {}


class AIAnalyzer:
    """AI 分析器 - 统一的 AI 分析接口"""
    
    # 系统提示词 - SQL 注入分析专家
    SYSTEM_PROMPT = """你是一位专业的 SQL 注入安全测试专家，精通 SQLMap 工具的使用。你的任务是分析 SQLMap 的扫描日志，并提供专业的分析和建议。

你的回答应该：
1. 使用简体中文
2. 结构清晰，使用标题和列表
3. 针对安全测试场景，提供实用建议
4. 如果推荐命令参数，请给出完整的参数格式"""
    
    def __init__(self, config: AIConfig):
        """
        初始化 AI 分析器
        
        参数:
            config: AI 配置对象
        """
        self.config = config
        self._set_default_url_if_needed()
    
    def _set_default_url_if_needed(self):
        """如果未设置 base_url，使用预设值"""
        if not self.config.base_url and self.config.provider in AI_PROVIDER_PRESETS:
            self.config.base_url = AI_PROVIDER_PRESETS[self.config.provider]["base_url"]
        if not self.config.model and self.config.provider in AI_PROVIDER_PRESETS:
            self.config.model = AI_PROVIDER_PRESETS[self.config.provider]["default_model"]
    
    def test_connection(self) -> AIResponse:
        """
        测试 AI 服务连接
        
        返回:
            AIResponse: 包含测试结果
        """
        try:
            if self.config.provider == AIProvider.OLLAMA:
                return self._test_ollama_connection()
            elif self.config.provider == AIProvider.CLAUDE:
                return self._test_claude_connection()
            else:
                # OpenAI 兼容接口（包括国内服务）
                return self._test_openai_compatible_connection()
        except requests.exceptions.Timeout:
            return AIResponse(success=False, error="连接超时，请检查网络或服务地址")
        except requests.exceptions.ConnectionError:
            return AIResponse(success=False, error="无法连接到服务，请检查服务地址是否正确")
        except Exception as e:
            return AIResponse(success=False, error=f"连接测试失败: {str(e)}")
    
    def _test_ollama_connection(self) -> AIResponse:
        """测试 Ollama 连接"""
        url = f"{self.config.base_url.rstrip('/')}/api/tags"
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            models = response.json().get("models", [])
            model_names = [m.get("name", "") for m in models]
            if self.config.model in model_names or any(self.config.model in m for m in model_names):
                return AIResponse(success=True, content=f"连接成功！已找到模型: {self.config.model}")
            else:
                available = ", ".join(model_names[:5]) if model_names else "无"
                return AIResponse(
                    success=False, 
                    error=f"模型 {self.config.model} 未找到。可用模型: {available}"
                )
        return AIResponse(success=False, error=f"服务响应异常: {response.status_code}")
    
    def _test_openai_compatible_connection(self) -> AIResponse:
        """测试 OpenAI 兼容接口连接"""
        url = f"{self.config.base_url.rstrip('/')}/chat/completions"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.config.api_key}"
        }
        data = {
            "model": self.config.model,
            "messages": [{"role": "user", "content": "你好，请回复'连接成功'"}],
            "max_tokens": 20
        }
        response = requests.post(url, headers=headers, json=data, timeout=15)
        if response.status_code == 200:
            result = response.json()
            content = result.get("choices", [{}])[0].get("message", {}).get("content", "")
            return AIResponse(success=True, content=f"连接成功！模型响应: {content[:50]}")
        else:
            error_msg = response.json().get("error", {}).get("message", response.text)
            return AIResponse(success=False, error=f"API 错误: {error_msg}")
    
    def _test_claude_connection(self) -> AIResponse:
        """测试 Claude API 连接"""
        url = f"{self.config.base_url.rstrip('/')}/v1/messages"
        headers = {
            "Content-Type": "application/json",
            "x-api-key": self.config.api_key,
            "anthropic-version": "2023-06-01"
        }
        data = {
            "model": self.config.model,
            "max_tokens": 20,
            "messages": [{"role": "user", "content": "你好，请回复'连接成功'"}]
        }
        response = requests.post(url, headers=headers, json=data, timeout=15)
        if response.status_code == 200:
            result = response.json()
            content = result.get("content", [{}])[0].get("text", "")
            return AIResponse(success=True, content=f"连接成功！模型响应: {content[:50]}")
        else:
            error_msg = response.json().get("error", {}).get("message", response.text)
            return AIResponse(success=False, error=f"API 错误: {error_msg}")
    
    def analyze_log(self, log_content: str, callback: Callable[[str], None] = None) -> AIResponse:
        """
        分析扫描日志
        
        参数:
            log_content: SQLMap 扫描日志内容
            callback: 流式输出回调函数（可选）
        
        返回:
            AIResponse: 分析结果
        """
        if not log_content or not log_content.strip():
            return AIResponse(success=False, error="日志内容为空，无法分析")
        
        # 限制日志长度，避免超出 token 限制
        max_log_length = 8000
        if len(log_content) > max_log_length:
            # 保留开头和结尾部分
            half = max_log_length // 2
            log_content = log_content[:half] + "\n\n... [日志过长，已截断] ...\n\n" + log_content[-half:]
        
        prompt = f"""请分析以下 SQLMap 扫描日志，并提供：

## 分析要求
1. **扫描状态总结**：当前扫描进度、是否发现注入点
2. **注入点信息**：如发现注入，列出注入类型、参数、Payload
3. **数据库信息**：如已获取，列出数据库类型、版本、当前数据库等
4. **问题诊断**：如有错误或警告，分析可能原因
5. **优化建议**：如何提高扫描效率或成功率

## 扫描日志
```
{log_content}
```

请用中文回答，结构清晰。"""
        
        return self._send_request(prompt, callback)
    
    def suggest_command(self, log_content: str, current_command: str = "", callback: Callable[[str], None] = None) -> AIResponse:
        """
        根据日志推荐优化命令
        
        参数:
            log_content: SQLMap 扫描日志内容
            current_command: 当前使用的命令（可选）
            callback: 流式输出回调函数（可选）
        
        返回:
            AIResponse: 命令建议
        """
        if not log_content or not log_content.strip():
            return AIResponse(success=False, error="日志内容为空，无法生成建议")
        
        # 限制日志长度
        max_log_length = 6000
        if len(log_content) > max_log_length:
            log_content = log_content[-max_log_length:]  # 保留最新的日志
        
        prompt = f"""请根据以下 SQLMap 扫描日志，推荐更优的扫描参数。

## 当前命令
```
{current_command if current_command else "未提供"}
```

## 最近扫描日志
```
{log_content}
```

## 请提供

### 1. 问题分析
简要分析当前扫描遇到的问题或可优化的地方。

### 2. 推荐参数
根据分析结果，推荐具体的 SQLMap 参数，格式如下：

| 参数 | 值 | 说明 |
|------|-----|------|
| --tamper | 脚本名 | 推荐原因 |
| --technique | 技术类型 | 推荐原因 |
| ... | ... | ... |

### 3. 完整推荐命令
给出可直接使用的完整命令行（不包含 URL，只给参数部分）。

请用中文回答。"""
        
        return self._send_request(prompt, callback)
    
    def diagnose_error(self, log_content: str, error_message: str = "", callback: Callable[[str], None] = None) -> AIResponse:
        """
        诊断扫描错误
        
        参数:
            log_content: SQLMap 扫描日志内容
            error_message: 具体错误信息（可选）
            callback: 流式输出回调函数（可选）
        
        返回:
            AIResponse: 诊断结果和解决方案
        """
        prompt = f"""请诊断以下 SQLMap 扫描中遇到的问题。

## 错误信息
```
{error_message if error_message else "未提供具体错误信息"}
```

## 扫描日志
```
{log_content[-4000:] if len(log_content) > 4000 else log_content}
```

## 请分析

### 1. 问题原因
分析导致问题的可能原因。

### 2. 解决方案
给出具体的解决步骤。

### 3. 参数调整
如需调整参数，给出具体建议。

请用中文回答，提供可操作的解决方案。"""
        
        return self._send_request(prompt, callback)
    
    def analyze_and_suggest(self, log_content: str, current_command: str = "", callback: Callable[[str], None] = None) -> AIResponse:
        """
        整合分析：分析日志并推荐优化参数
        
        参数:
            log_content: SQLMap 扫描日志内容
            current_command: 当前使用的命令（可选）
            callback: 流式输出回调函数（可选）
        
        返回:
            AIResponse: 分析结果和推荐参数
        """
        if not log_content or not log_content.strip():
            return AIResponse(success=False, error="日志内容为空，无法分析")
        
        # 限制日志长度
        max_log_length = 6000
        if len(log_content) > max_log_length:
            # 保留开头和结尾部分
            head = max_log_length // 3
            tail = max_log_length * 2 // 3
            log_content = log_content[:head] + "\n\n... [日志过长，已截断] ...\n\n" + log_content[-tail:]
        
        prompt = f"""请分析以下 SQLMap 扫描日志，给出**专业的分析结果**。

## 当前命令
```
{current_command if current_command else "未提供"}
```

## 扫描日志
```
{log_content}
```

## 分析规则
**请先判断日志中是否已经成功发现 SQL 注入漏洞。**

### 情况一：如果已发现注入漏洞（日志中有 "is vulnerable"、"identified" 等成功标志）
只需要给出以下内容，**不需要给出扫描方案**：

#### ✅ 漏洞发现报告

**1. 注入点信息**
- 漏洞参数：
- 注入类型：（布尔盲注/报错注入/联合查询/时间盲注等）
- 数据库类型：

**2. 成功的 Payload**
完整列出日志中所有成功的注入 payload，格式如：
```
Payload 1: xxx
Payload 2: xxx
```

**3. 已获取的信息**
- 数据库名：
- 数据库版本：
- 当前用户：
- 其他信息：

**4. 后续建议**
简要说明用户可以进行的下一步操作（如枚举表、提取数据等）

---

### 情况二：如果未发现注入漏洞或扫描遇到问题
给出以下内容：

#### ❌ 扫描状态分析

**1. 当前状态**
- 扫描进度
- 遇到的问题（WAF、无注入点、连接失败等）
- 问题原因分析

**2. 安全方案（🟢 推荐）**
保守稳定的优化建议，只关注漏洞检测：
- risk 保持 1
- level 控制在 1-3
- 不推荐 os-shell、dump-all 等高级功能

| 参数 | 推荐值 | 说明 |
|------|--------|------|
| --tamper | 脚本名 | 绕过过滤 |
| --level | 1-3 | 适度探测 |
| --risk | 1 | 保持安全 |

**安全方案命令：**
```
[SAFE] --tamper=xxx --level=2 --risk=1 --threads=3 --random-agent --batch
```

**3. 激进方案（🔴 谨慎）**
高风险方案，需用户确认：

```
[AGGRESSIVE] --level=5 --risk=3 --tamper=xxx
```

**4. 专家建议**
其他测试思路或绕过技巧

---

请用中文回答。根据日志实际情况选择上述两种格式之一回复。"""
        
        return self._send_request(prompt, callback)
    
    def _send_request(self, prompt: str, callback: Callable[[str], None] = None) -> AIResponse:
        """
        发送请求到 AI 服务
        
        参数:
            prompt: 用户提示词
            callback: 流式输出回调函数（可选）
        
        返回:
            AIResponse: AI 响应结果
        """
        try:
            if self.config.provider == AIProvider.OLLAMA:
                return self._send_ollama_request(prompt, callback)
            elif self.config.provider == AIProvider.CLAUDE:
                return self._send_claude_request(prompt, callback)
            else:
                # OpenAI 兼容接口（包括国内服务）
                return self._send_openai_compatible_request(prompt, callback)
        except requests.exceptions.Timeout:
            return AIResponse(success=False, error="请求超时，请稍后重试或检查网络连接")
        except requests.exceptions.ConnectionError:
            return AIResponse(success=False, error="无法连接到 AI 服务，请检查服务地址和网络")
        except Exception as e:
            return AIResponse(success=False, error=f"请求失败: {str(e)}")
    
    def _send_ollama_request(self, prompt: str, callback: Callable[[str], None] = None) -> AIResponse:
        """发送 Ollama 请求"""
        url = f"{self.config.base_url.rstrip('/')}/api/generate"
        data = {
            "model": self.config.model,
            "prompt": f"{self.SYSTEM_PROMPT}\n\n用户问题：\n{prompt}",
            "stream": callback is not None,
            "options": {
                "temperature": self.config.temperature,
                "num_predict": self.config.max_tokens,
            }
        }
        
        if callback:
            # 流式请求
            response = requests.post(url, json=data, stream=True, timeout=self.config.timeout)
            full_content = ""
            for line in response.iter_lines():
                if line:
                    try:
                        chunk = json.loads(line)
                        content = chunk.get("response", "")
                        full_content += content
                        callback(content)
                        if chunk.get("done", False):
                            break
                    except json.JSONDecodeError:
                        continue
            return AIResponse(success=True, content=full_content)
        else:
            # 非流式请求
            response = requests.post(url, json=data, timeout=self.config.timeout)
            if response.status_code == 200:
                result = response.json()
                return AIResponse(success=True, content=result.get("response", ""))
            else:
                return AIResponse(success=False, error=f"Ollama 错误: {response.text}")
    
    def _send_openai_compatible_request(self, prompt: str, callback: Callable[[str], None] = None) -> AIResponse:
        """发送 OpenAI 兼容请求（支持国内服务）"""
        url = f"{self.config.base_url.rstrip('/')}/chat/completions"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.config.api_key}"
        }
        data = {
            "model": self.config.model,
            "messages": [
                {"role": "system", "content": self.SYSTEM_PROMPT},
                {"role": "user", "content": prompt}
            ],
            "max_tokens": self.config.max_tokens,
            "temperature": self.config.temperature,
            "stream": callback is not None
        }
        
        if callback:
            # 流式请求
            response = requests.post(url, headers=headers, json=data, stream=True, timeout=self.config.timeout)
            full_content = ""
            for line in response.iter_lines():
                if line:
                    line_text = line.decode('utf-8')
                    if line_text.startswith("data: "):
                        line_text = line_text[6:]
                    if line_text == "[DONE]":
                        break
                    try:
                        chunk = json.loads(line_text)
                        delta = chunk.get("choices", [{}])[0].get("delta", {})
                        content = delta.get("content", "")
                        if content:
                            full_content += content
                            callback(content)
                    except json.JSONDecodeError:
                        continue
            return AIResponse(success=True, content=full_content)
        else:
            # 非流式请求
            response = requests.post(url, headers=headers, json=data, timeout=self.config.timeout)
            if response.status_code == 200:
                result = response.json()
                content = result.get("choices", [{}])[0].get("message", {}).get("content", "")
                usage = result.get("usage", {})
                return AIResponse(success=True, content=content, usage=usage)
            else:
                try:
                    error_msg = response.json().get("error", {}).get("message", response.text)
                except:
                    error_msg = response.text
                return AIResponse(success=False, error=f"API 错误: {error_msg}")
    
    def _send_claude_request(self, prompt: str, callback: Callable[[str], None] = None) -> AIResponse:
        """发送 Claude 请求"""
        url = f"{self.config.base_url.rstrip('/')}/v1/messages"
        headers = {
            "Content-Type": "application/json",
            "x-api-key": self.config.api_key,
            "anthropic-version": "2023-06-01"
        }
        data = {
            "model": self.config.model,
            "max_tokens": self.config.max_tokens,
            "system": self.SYSTEM_PROMPT,
            "messages": [{"role": "user", "content": prompt}],
            "stream": callback is not None
        }
        
        if callback:
            # 流式请求
            response = requests.post(url, headers=headers, json=data, stream=True, timeout=self.config.timeout)
            full_content = ""
            for line in response.iter_lines():
                if line:
                    line_text = line.decode('utf-8')
                    if line_text.startswith("data: "):
                        line_text = line_text[6:]
                    try:
                        chunk = json.loads(line_text)
                        if chunk.get("type") == "content_block_delta":
                            content = chunk.get("delta", {}).get("text", "")
                            if content:
                                full_content += content
                                callback(content)
                    except json.JSONDecodeError:
                        continue
            return AIResponse(success=True, content=full_content)
        else:
            # 非流式请求
            response = requests.post(url, headers=headers, json=data, timeout=self.config.timeout)
            if response.status_code == 200:
                result = response.json()
                content = result.get("content", [{}])[0].get("text", "")
                usage = result.get("usage", {})
                return AIResponse(success=True, content=content, usage=usage)
            else:
                try:
                    error_msg = response.json().get("error", {}).get("message", response.text)
                except:
                    error_msg = response.text
                return AIResponse(success=False, error=f"Claude 错误: {error_msg}")


def create_analyzer_from_config(config_manager) -> AIAnalyzer:
    """
    从配置管理器创建 AI 分析器
    
    参数:
        config_manager: ConfigManager 实例
    
    返回:
        AIAnalyzer: 配置好的分析器实例
    """
    provider_str = config_manager.get('AI', 'provider', 'ollama')
    
    try:
        provider = AIProvider(provider_str)
    except ValueError:
        provider = AIProvider.OLLAMA
    
    # 根据不同的 provider 读取对应配置
    if provider == AIProvider.OLLAMA:
        base_url = config_manager.get('AI', 'ollama_url', 'http://localhost:11434')
        model = config_manager.get('AI', 'ollama_model', 'qwen2:7b')
        api_key = ""
    elif provider == AIProvider.OPENAI:
        base_url = config_manager.get('AI', 'openai_base_url', 'https://api.openai.com/v1')
        model = config_manager.get('AI', 'openai_model', 'gpt-4o-mini')
        api_key = config_manager.get('AI', 'openai_api_key', '')
    elif provider == AIProvider.CLAUDE:
        base_url = config_manager.get('AI', 'claude_base_url', 'https://api.anthropic.com')
        model = config_manager.get('AI', 'claude_model', 'claude-3-haiku-20240307')
        api_key = config_manager.get('AI', 'claude_api_key', '')
    elif provider == AIProvider.DEEPSEEK:
        base_url = "https://api.deepseek.com"
        model = config_manager.get('AI', 'deepseek_model', 'deepseek-chat')
        api_key = config_manager.get('AI', 'deepseek_api_key', '')
    elif provider == AIProvider.QWEN:
        base_url = "https://dashscope.aliyuncs.com/compatible-mode/v1"
        model = config_manager.get('AI', 'qwen_model', 'qwen-turbo')
        api_key = config_manager.get('AI', 'qwen_api_key', '')
    elif provider == AIProvider.ZHIPU:
        base_url = "https://open.bigmodel.cn/api/paas/v4"
        model = config_manager.get('AI', 'zhipu_model', 'glm-4-flash')
        api_key = config_manager.get('AI', 'zhipu_api_key', '')
    elif provider == AIProvider.MOONSHOT:
        base_url = "https://api.moonshot.cn/v1"
        model = config_manager.get('AI', 'moonshot_model', 'moonshot-v1-8k')
        api_key = config_manager.get('AI', 'moonshot_api_key', '')
    else:  # CUSTOM
        base_url = config_manager.get('AI', 'custom_base_url', '')
        model = config_manager.get('AI', 'custom_model', '')
        api_key = config_manager.get('AI', 'custom_api_key', '')
    
    config = AIConfig(
        provider=provider,
        api_key=api_key,
        base_url=base_url,
        model=model,
        max_tokens=config_manager.get_int('AI', 'max_tokens', 2000),
        temperature=config_manager.get_float('AI', 'temperature', 0.7),
        timeout=config_manager.get_int('AI', 'timeout', 60)
    )
    
    return AIAnalyzer(config)
