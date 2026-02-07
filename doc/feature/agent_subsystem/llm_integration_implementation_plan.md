# XXM Fans Home - Agent 大模型接入实现方案

## 一、方案概述

本方案基于《Agent 智能查询子系统实现方案》的基础上，详细规划如何接入大语言模型（LLM）以提升系统的自然语言理解能力和交互体验。

### 1.1 目标

1. **提升意图识别准确率**：从规则的85%提升到LLM的95%+
2. **支持复杂查询**：处理多条件组合、模糊语义、上下文引用
3. **智能推荐**：基于用户偏好和历史提供个性化推荐
4. **自然对话**：实现更流畅的多轮对话体验
5. **成本可控**：通过缓存、降级策略控制API调用成本

### 1.2 接入策略

采用**渐进式接入**策略：
- **阶段一**：LLM仅用于意图识别和参数提取
- **阶段二**：LLM用于结果解释和自然语言生成
- **阶段三**：完全LLM驱动的智能对话

---

## 二、大模型选型与对比

### 2.1 主流LLM对比

| 特性 | OpenAI GPT-4 | 通义千问 | 文心一言 | Claude 3 | DeepSeek-V3 |
|-----|-------------|---------|---------|----------|-------------|
| **中文理解** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **推理能力** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| **API稳定性** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |
| **价格** | $$$ | $$ | $$ | $$$$ | $ |
| **响应速度** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **上下文长度** | 128K | 32K | 8K | 200K | 128K |
| **国内访问** | ❌ 需VPN | ✅ | ✅ | ❌ 需VPN | ✅ |

### 2.2 推荐方案

**主选模型**：通义千问 Qwen-Max
- 优势：中文理解能力强、国内访问稳定、价格合理
- 适用：意图识别、参数提取、结果解释

**备选模型**：OpenAI GPT-4o mini
- 优势：推理能力强、API生态完善
- 适用：复杂推理、多轮对话

**降级方案**：本地模型（Qwen-14B-Chat-Int4）
- 优势：零成本、隐私安全
- 适用：离线场景、成本敏感

### 2.3 多模型策略

```python
# agent/llm/model_selector.py

class ModelSelector:
    """多模型选择器"""
    
    # 配置优先级
    MODELS = [
        {
            'name': 'qwen-max',
            'provider': 'aliyun',
            'priority': 1,
            'capabilities': ['intent', 'explanation', 'chat'],
            'cost_per_1k_tokens': 0.04
        },
        {
            'name': 'gpt-4o-mini',
            'provider': 'openai',
            'priority': 2,
            'capabilities': ['intent', 'explanation', 'chat', 'reasoning'],
            'cost_per_1k_tokens': 0.15
        },
        {
            'name': 'qwen-14b-local',
            'provider': 'local',
            'priority': 3,
            'capabilities': ['intent'],
            'cost_per_1k_tokens': 0
        }
    ]
    
    @classmethod
    def select_model(cls, capability: str, budget: float = None) -> dict:
        """根据能力和预算选择模型"""
        available = [m for m in cls.MODELS if capability in m['capabilities']]
        
        if budget:
            available = [m for m in available if m['cost_per_1k_tokens'] <= budget]
        
        # 按优先级排序
        available.sort(key=lambda x: x['priority'])
        
        return available[0] if available else None
```

---

## 三、架构设计

### 3.1 LLM集成架构

```
┌─────────────────────────────────────────────────────────────┐
│                         用户层                                │
│  用户查询: "最近一个月演唱的古风歌曲有哪些？"                    │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                    LLM 意图识别层                              │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  LLM Client (Qwen-Max)                               │   │
│  │  - 意图识别: song_search + filter                    │   │
│  │  - 参数提取: {style: "古风", time_range: "last_month"}│   │
│  └──────────────────────────────────────────────────────┘   │
│  ↓ Redis缓存 (intent:hash)                                   │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                    混合查询层                                 │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  Query Executor                                      │   │
│  │  - 路由到对应的查询服务                               │   │
│  │  - 执行Django ORM查询                                 │   │
│  │  - 返回结构化数据                                     │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                    LLM 结果生成层                             │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  LLM Client (Qwen-Turbo - 更快更便宜)                 │   │
│  │  - 将结构化数据转换为自然语言                         │   │
│  │  - 生成友好的回复文本                                 │   │
│  │  - 添加解释和建议                                     │   │
│  └──────────────────────────────────────────────────────┘   │
│  ↓ Redis缓存 (response:hash)                                │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                         响应层                                │
│  {                                                             │
│    "success": true,                                           │
│    "response": "最近一个月，咻咻满演唱了5首古风歌曲：...",    │
│    "data": [...],                                            │
│    "model_used": "qwen-max"                                 │
│  }                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 3.2 数据流对比

| 阶段 | 规则引擎方案 | LLM方案 |
|-----|------------|---------|
| **意图识别** | 正则匹配 (0.05s) | LLM调用 (0.5s) |
| **参数提取** | 正则提取 (0.01s) | LLM提取 (包含在意图识别中) |
| **查询执行** | Django ORM (0.12s) | Django ORM (0.12s) |
| **结果生成** | 模板渲染 (0.01s) | LLM生成 (0.3s) |
| **总耗时** | 0.19s | 0.92s |
| **准确率** | 85% | 95%+ |

---

## 四、Prompt工程设计

### 4.1 意图识别Prompt

```python
# agent/llm/prompts/intent_recognition.py

INTENT_RECOGNITION_PROMPT = """
你是一个智能查询助手，专门帮助用户查询咻咻满（XXM）的音乐、直播、二创作品等数据。

## 任务
分析用户的自然语言查询，识别查询意图并提取参数。

## 支持的意图类型

1. **song_search** - 歌曲搜索
   - 参数：song_name, keywords, style, tags, language, singer
   - 示例："搜索《稻香》" → song_name="稻香"

2. **song_stats** - 歌曲统计
   - 参数：year, month, time_range, limit, sort_by
   - 示例："2024年唱得最多的5首歌" → year=2024, limit=5

3. **record_search** - 演唱记录查询
   - 参数：song_name, date, date_range, limit
   - 示例："找一下2023年12月25日的演唱记录" → date="2023-12-25"

4. **livestream_search** - 直播查询
   - 参数：date, date_range, time_range, limit
   - 示例："上周有哪些直播？" → time_range="last_week"

5. **fansdiy_search** - 二创作品搜索
   - 参数：keywords, author, collection, limit
   - 示例："找找咻咻满相关的二创视频" → keywords="咻咻满"

6. **gallery_search** - 图集查询
   - 参数：keywords, date, date_range, category, limit
   - 示例："2024年的演唱会图片" → year=2024

7. **analytics_query** - 数据分析
   - 参数：metric, time_range, account_name
   - 示例："粉丝数增长最快的月份" → metric="fans_growth"

8. **comparison** - 对比查询
   - 参数：metric, value1, value2, time_range
   - 示例："对比2023和2024年的演唱次数" → metric="perform_count", value1=2023, value2=2024

9. **recommendation** - 推荐查询
   - 参数：style, tags, limit
   - 示例："推荐一些古风歌曲" → style="古风"

10. **unknown** - 未知意图
    - 当无法识别时使用

## 输出格式
请以JSON格式返回，不要包含任何其他文字：
```json
{
  "intent_type": "意图类型",
  "parameters": {
    "参数名": "参数值"
  },
  "confidence": 0.95,
  "reasoning": "简要说明识别理由"
}
```

## 用户查询
{query}

## 上下文信息（如果有）
{context}

## 输出
"""
```

### 4.2 结果生成Prompt

```python
# agent/llm/prompts/result_generation.py

RESULT_GENERATION_PROMPT = """
你是一个友好的音乐助手，正在为用户展示查询结果。

## 任务
将结构化的查询数据转换为自然、友好的中文回复。

## 回复要求
1. 语气亲切自然，像粉丝之间的交流
2. 突出关键信息，使用适当的emoji表情
3. 如果数据较多，进行适当总结
4. 提供相关的延伸建议
5. 保持回复简洁，不超过200字

## 查询结果数据
{data}

## 查询意图
{intent}

## 用户查询原文
{query}

## 输出格式
```json
{
  "response": "自然语言回复",
  "highlights": ["关键点1", "关键点2"],
  "suggestions": ["建议1", "建议2"]
}
```

## 输出
"""
```

### 4.3 上下文增强Prompt

```python
# agent/llm/prompts/context_enhancement.py

CONTEXT_ENHANCEMENT_PROMPT = """
你是一个上下文理解助手，帮助解析多轮对话中的指代关系。

## 任务
根据对话历史，解析当前查询中的指代词（如"这首歌"、"刚才"、"它"等）。

## 对话历史
{history}

## 当前查询
{current_query}

## 可用的实体
{entities}

## 输出格式
```json
{
  "resolved_query": "解析后的完整查询",
  "resolved_parameters": {
    "参数名": "解析后的值"
  },
  "references": ["引用的历史实体"]
}
```

## 输出
"""
```

### 4.4 Prompt优化策略

**1. Few-Shot Learning（少样本学习）**

```python
INTENT_RECOGNITION_PROMPT_WITH_EXAMPLES = """
...（前文同上）...

## 示例

示例1:
查询: "2024年唱得最多的5首歌"
输出:
{
  "intent_type": "song_stats",
  "parameters": {"year": 2024, "limit": 5, "sort_by": "perform_count"},
  "confidence": 0.98,
  "reasoning": "明确提到了年份2024和数量5，要求统计演唱次数最多的歌曲"
}

示例2:
查询: "上周有哪些直播？"
输出:
{
  "intent_type": "livestream_search",
  "parameters": {"time_range": "last_week"},
  "confidence": 0.95,
  "reasoning": "询问'上周'的直播，使用time_range参数"
}

示例3:
查询: "这首歌第一次唱是什么时候？"
输出:
{
  "intent_type": "record_search",
  "parameters": {"song_name": "{current_entity}", "sort_by": "first_perform"},
  "confidence": 0.90,
  "reasoning": "引用了'这首歌'，需要从上下文获取实体"
}

## 当前查询
{query}

## 输出
"""
```

**2. Chain-of-Thought（思维链）**

```python
INTENT_RECOGNITION_PROMPT_WITH_COT = """
...（前文同上）...

## 思考步骤
请按照以下步骤进行分析：
1. 识别查询中的关键词
2. 判断关键词匹配的意图类型
3. 提取查询中的具体参数值
4. 评估识别的置信度
5. 给出识别理由

## 用户查询
{query}

## 逐步分析

## 输出
"""
```

---

## 五、核心实现

### 5.1 LLM客户端封装

```python
# agent/llm/llm_client.py

import os
import json
from typing import Optional, Dict, Any
from abc import ABC, abstractmethod
import dashscope
from openai import OpenAI

class LLMProvider(ABC):
    """LLM提供商抽象基类"""
    
    @abstractmethod
    def chat(self, messages: list, **kwargs) -> str:
        """聊天接口"""
        pass
    
    @abstractmethod
    def count_tokens(self, text: str) -> int:
        """计算token数量"""
        pass

class QwenProvider(LLMProvider):
    """通义千问提供商"""
    
    def __init__(self, api_key: str = None):
        dashscope.api_key = api_key or os.getenv('DASHSCOPE_API_KEY')
        self.model = "qwen-max"
    
    def chat(self, messages: list, **kwargs) -> str:
        """调用通义千问API"""
        response = dashscope.Generation.call(
            model=self.model,
            messages=messages,
            result_format='message',
            **kwargs
        )
        
        if response.status_code == 200:
            return response.output.choices[0].message.content
        else:
            raise Exception(f"API调用失败: {response.message}")
    
    def count_tokens(self, text: str) -> int:
        """估算token数量（中文约1.5字符=1token）"""
        return len(text) // 1.5

class OpenAIProvider(LLMProvider):
    """OpenAI提供商"""
    
    def __init__(self, api_key: str = None):
        self.client = OpenAI(api_key=api_key or os.getenv('OPENAI_API_KEY'))
        self.model = "gpt-4o-mini"
    
    def chat(self, messages: list, **kwargs) -> str:
        """调用OpenAI API"""
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            **kwargs
        )
        
        return response.choices[0].message.content
    
    def count_tokens(self, text: str) -> int:
        """使用tiktoken计算token数量"""
        import tiktoken
        encoding = tiktoken.encoding_for_model(self.model)
        return len(encoding.encode(text))

class LLMClient:
    """LLM客户端（统一接口）"""
    
    def __init__(self, provider: LLMProvider = None):
        self.provider = provider or self._get_default_provider()
        self.cache_enabled = True
    
    def _get_default_provider(self) -> LLMProvider:
        """获取默认提供商"""
        # 优先使用通义千问
        if os.getenv('DASHSCOPE_API_KEY'):
            return QwenProvider()
        # 其次使用OpenAI
        elif os.getenv('OPENAI_API_KEY'):
            return OpenAIProvider()
        # 最后降级到本地模型
        else:
            return LocalLLMProvider()
    
    def complete(self, prompt: str, system_prompt: str = None, 
                 temperature: float = 0.7, max_tokens: int = 1000) -> str:
        """完成文本生成"""
        messages = []
        
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        
        messages.append({"role": "user", "content": prompt})
        
        # 检查缓存
        if self.cache_enabled:
            cache_key = self._generate_cache_key(prompt, system_prompt)
            cached = self._get_from_cache(cache_key)
            if cached:
                return cached
        
        # 调用API
        response = self.provider.chat(
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens
        )
        
        # 缓存结果
        if self.cache_enabled:
            self._save_to_cache(cache_key, response)
        
        return response
    
    def json_complete(self, prompt: str, system_prompt: str = None,
                      temperature: float = 0.3, max_tokens: int = 1000) -> dict:
        """完成JSON生成"""
        # 强制要求返回JSON
        if not system_prompt:
            system_prompt = "你是一个助手，请以JSON格式返回结果，不要包含其他文字。"
        
        response = self.complete(prompt, system_prompt, temperature, max_tokens)
        
        try:
            # 尝试解析JSON
            # 提取JSON部分（可能包含markdown代码块）
            json_str = self._extract_json(response)
            return json.loads(json_str)
        except json.JSONDecodeError as e:
            # 如果解析失败，尝试修复
            return self._fix_and_parse_json(response)
    
    def _extract_json(self, text: str) -> str:
        """从文本中提取JSON"""
        # 移除markdown代码块标记
        text = text.strip()
        if text.startswith('```json'):
            text = text[7:]
        if text.startswith('```'):
            text = text[3:]
        if text.endswith('```'):
            text = text[:-3]
        return text.strip()
    
    def _fix_and_parse_json(self, text: str) -> dict:
        """修复并解析JSON"""
        # 简单的修复策略
        text = self._extract_json(text)
        
        # 尝试使用正则提取JSON对象
        import re
        json_match = re.search(r'\{.*\}', text, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group())
            except:
                pass
        
        # 最后降级：返回默认结构
        return {
            "error": "JSON解析失败",
            "raw_response": text
        }
    
    def _generate_cache_key(self, prompt: str, system_prompt: str = None) -> str:
        """生成缓存键"""
        import hashlib
        content = f"{system_prompt or ''}:{prompt}"
        return f"llm:{hashlib.md5(content.encode()).hexdigest()}"
    
    def _get_from_cache(self, key: str) -> Optional[str]:
        """从缓存获取"""
        from django.core.cache import cache
        return cache.get(key)
    
    def _save_to_cache(self, key: str, value: str, timeout: int = 3600):
        """保存到缓存"""
        from django.core.cache import cache
        cache.set(key, value, timeout)
```

### 5.2 LLM意图识别器

```python
# agent/intent_recognizer/llm_recognizer.py

from enum import Enum
from typing import Dict, Any
from agent.llm.llm_client import LLMClient
from agent.llm.prompts.intent_recognition import INTENT_RECOGNITION_PROMPT

class IntentType(Enum):
    """意图类型枚举"""
    SONG_SEARCH = "song_search"
    SONG_STATS = "song_stats"
    RECORD_SEARCH = "record_search"
    LIVESTREAM_SEARCH = "livestream_search"
    FANSDIY_SEARCH = "fansdiy_search"
    GALLERY_SEARCH = "gallery_search"
    ANALYTICS_QUERY = "analytics_query"
    COMPARISON = "comparison"
    RECOMMENDATION = "recommendation"
    UNKNOWN = "unknown"

class Intent:
    """意图对象"""
    
    def __init__(self, type: IntentType, parameters: Dict[str, Any], 
                 confidence: float, reasoning: str = ""):
        self.type = type
        self.parameters = parameters
        self.confidence = confidence
        self.reasoning = reasoning
    
    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            "type": self.type.value,
            "parameters": self.parameters,
            "confidence": self.confidence,
            "reasoning": self.reasoning
        }

class LLMIntentRecognizer:
    """基于LLM的意图识别器"""
    
    def __init__(self, llm_client: LLMClient = None):
        self.llm_client = llm_client or LLMClient()
        self.system_prompt = """
你是一个专业的音乐数据查询意图识别系统。
请准确识别用户查询的意图，并提取相关参数。
"""
    
    def recognize(self, query: str, context: Dict[str, Any] = None) -> Intent:
        """识别查询意图"""
        # 构建提示词
        context_str = json.dumps(context, ensure_ascii=False) if context else "无"
        
        prompt = INTENT_RECOGNITION_PROMPT.format(
            query=query,
            context=context_str
        )
        
        try:
            # 调用LLM
            result = self.llm_client.json_complete(
                prompt=prompt,
                system_prompt=self.system_prompt,
                temperature=0.3,  # 较低温度，提高确定性
                max_tokens=500
            )
            
            # 解析结果
            intent_type_str = result.get('intent_type', 'unknown')
            intent_type = IntentType(intent_type_str)
            
            parameters = result.get('parameters', {})
            confidence = result.get('confidence', 0.0)
            reasoning = result.get('reasoning', '')
            
            # 参数类型转换
            parameters = self._convert_parameters(parameters)
            
            return Intent(
                type=intent_type,
                parameters=parameters,
                confidence=confidence,
                reasoning=reasoning
            )
            
        except Exception as e:
            # 降级到规则引擎
            from agent.intent_recognizer.rule_based import RuleBasedIntentRecognizer
            fallback = RuleBasedIntentRecognizer()
            return fallback.recognize(query)
    
    def _convert_parameters(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """转换参数类型"""
        converted = {}
        
        for key, value in parameters.items():
            # 转换年份
            if key in ['year', 'value1', 'value2'] and isinstance(value, str):
                try:
                    converted[key] = int(value)
                except ValueError:
                    converted[key] = value
            # 转换数量限制
            elif key in ['limit'] and isinstance(value, str):
                try:
                    converted[key] = int(value)
                except ValueError:
                    converted[key] = 10  # 默认值
            # 转换标签列表
            elif key in ['tags'] and isinstance(value, str):
                converted[key] = [tag.strip() for tag in value.split(',')]
            else:
                converted[key] = value
        
        return converted
    
    def batch_recognize(self, queries: list) -> list[Intent]:
        """批量识别意图"""
        return [self.recognize(query) for query in queries]
```

### 5.3 上下文解析器

```python
# agent/context_manager/context_parser.py

from typing import Dict, Any, List
from agent.llm.llm_client import LLMClient
from agent.llm.prompts.context_enhancement import CONTEXT_ENHANCEMENT_PROMPT

class ContextParser:
    """上下文解析器"""
    
    def __init__(self, llm_client: LLMClient = None):
        self.llm_client = llm_client or LLMClient()
    
    def resolve_references(self, current_query: str, 
                           history: List[Dict[str, Any]],
                           entities: List[str] = None) -> Dict[str, Any]:
        """解析查询中的引用"""
        entities = entities or []
        
        # 构建对话历史字符串
        history_str = self._format_history(history)
        
        # 构建实体字符串
        entities_str = ", ".join(entities) if entities else "无"
        
        prompt = CONTEXT_ENHANCEMENT_PROMPT.format(
            current_query=current_query,
            history=history_str,
            entities=entities_str
        )
        
        try:
            result = self.llm_client.json_complete(
                prompt=prompt,
                temperature=0.3,
                max_tokens=300
            )
            
            return {
                "resolved_query": result.get("resolved_query", current_query),
                "resolved_parameters": result.get("resolved_parameters", {}),
                "references": result.get("references", [])
            }
        except Exception:
            # 降级：简单的替换规则
            return self._simple_resolve(current_query, entities)
    
    def _format_history(self, history: List[Dict[str, Any]]) -> str:
        """格式化对话历史"""
        if not history:
            return "无历史对话"
        
        lines = []
        for msg in history[-5:]:  # 只保留最近5条
            role = "用户" if msg['role'] == 'user' else "助手"
            lines.append(f"{role}: {msg['content']}")
        
        return "\n".join(lines)
    
    def _simple_resolve(self, query: str, entities: List[str]) -> Dict[str, Any]:
        """简单的引用解析"""
        resolved = query
        references = []
        
        # 常见指代词替换
        replacements = {
            "这首歌": entities[0] if entities else "",
            "那首歌": entities[1] if len(entities) > 1 else "",
            "它": entities[0] if entities else "",
        }
        
        for ref, entity in replacements.items():
            if entity and ref in query:
                resolved = resolved.replace(ref, entity)
                references.append(entity)
        
        return {
            "resolved_query": resolved,
            "resolved_parameters": {},
            "references": references
        }
```

### 5.4 结果生成器

```python
# agent/result_generator/response_generator.py

from typing import Dict, Any
from agent.llm.llm_client import LLMClient
from agent.llm.prompts.result_generation import RESULT_GENERATION_PROMPT

class ResponseGenerator:
    """响应生成器"""
    
    def __init__(self, llm_client: LLMClient = None):
        self.llm_client = llm_client or LLMClient()
        # 使用更快的模型
        if hasattr(self.llm_client.provider, 'model'):
            self.llm_client.provider.model = "qwen-turbo"
    
    def generate(self, query: str, intent: Dict[str, Any], 
                 data: Dict[str, Any]) -> Dict[str, str]:
        """生成自然语言响应"""
        prompt = RESULT_GENERATION_PROMPT.format(
            data=json.dumps(data, ensure_ascii=False),
            intent=json.dumps(intent, ensure_ascii=False),
            query=query
        )
        
        try:
            result = self.llm_client.json_complete(
                prompt=prompt,
                temperature=0.8,  # 较高温度，增加多样性
                max_tokens=300
            )
            
            return {
                "response": result.get("response", ""),
                "highlights": result.get("highlights", []),
                "suggestions": result.get("suggestions", [])
            }
        except Exception:
            # 降级到模板
            return self._template_generate(data)
    
    def _template_generate(self, data: Dict[str, Any]) -> Dict[str, str]:
        """模板生成（降级方案）"""
        if data.get("type") == "table":
            count = len(data.get("rows", []))
            summary = data.get("summary", "")
            return {
                "response": f"为您找到了{count}条{summary}，详细数据见下表：",
                "highlights": [f"共{count}条记录"],
                "suggestions": ["您可以进一步筛选数据", "查看详细信息"]
            }
        
        return {
            "response": "查询完成，请查看结果",
            "highlights": [],
            "suggestions": []
        }
```

---

## 六、成本控制策略

### 6.1 成本优化方案

```python
# agent/cost/cost_optimizer.py

class CostOptimizer:
    """成本优化器"""
    
    # Token成本（每1k tokens，单位：元）
    COSTS = {
        "qwen-max": {"input": 0.04, "output": 0.12},
        "qwen-turbo": {"input": 0.008, "output": 0.02},
        "gpt-4o-mini": {"input": 0.15, "output": 0.60}
    }
    
    def __init__(self, daily_budget: float = 50.0):
        self.daily_budget = daily_budget
        self.daily_spent = 0.0
    
    def should_use_llm(self, confidence: float = None, 
                       complexity: str = "medium") -> bool:
        """判断是否使用LLM"""
        # 简单查询使用规则引擎
        if complexity == "simple":
            return False
        
        # 检查预算
        if self.daily_spent >= self.daily_budget:
            return False
        
        # 高置信度规则匹配，可以跳过LLM
        if confidence and confidence > 0.95:
            return False
        
        return True
    
    def select_model(self, task: str, budget: float = None) -> str:
        """选择模型"""
        budget = budget or (self.daily_budget - self.daily_spent)
        
        # 意图识别使用更便宜的模型
        if task == "intent_recognition":
            return "qwen-turbo"
        
        # 结果生成使用更快的模型
        if task == "response_generation":
            return "qwen-turbo"
        
        # 复杂推理使用更强的模型
        if task == "complex_reasoning":
            if budget > 5.0:
                return "qwen-max"
            else:
                return "qwen-turbo"
        
        return "qwen-turbo"
    
    def calculate_cost(self, model: str, input_tokens: int, 
                       output_tokens: int) -> float:
        """计算成本"""
        costs = self.COSTS.get(model, {"input": 0, "output": 0})
        input_cost = (input_tokens / 1000) * costs["input"]
        output_cost = (output_tokens / 1000) * costs["output"]
        return input_cost + output_cost
    
    def record_cost(self, cost: float):
        """记录成本"""
        self.daily_spent += cost
```

### 6.2 缓存策略

```python
# agent/cache/llm_cache.py

from django.core.cache import cache
from typing import Optional
import hashlib
import json

class LLMCache:
    """LLM专用缓存"""
    
    # 不同任务的缓存时间
    CACHE_TIMEOUTS = {
        "intent_recognition": 86400,  # 1天 - 意图识别结果稳定
        "response_generation": 3600,  # 1小时 - 响应可以个性化
        "context_enhancement": 1800,  # 30分钟 - 上下文变化较快
    }
    
    @classmethod
    def get(cls, task: str, prompt: str) -> Optional[str]:
        """获取缓存"""
        key = cls._generate_key(task, prompt)
        return cache.get(key)
    
    @classmethod
    def set(cls, task: str, prompt: str, result: str):
        """设置缓存"""
        key = cls._generate_key(task, prompt)
        timeout = cls.CACHE_TIMEOUTS.get(task, 3600)
        cache.set(key, result, timeout)
    
    @classmethod
    def invalidate_pattern(cls, pattern: str):
        """批量失效"""
        keys = cache.keys(f"llm:{pattern}:*")
        for key in keys:
            cache.delete(key)
    
    @classmethod
    def _generate_key(cls, task: str, prompt: str) -> str:
        """生成缓存键"""
        hash_value = hashlib.md5(prompt.encode()).hexdigest()
        return f"llm:{task}:{hash_value}"
```

### 6.3 成本监控

```python
# agent/monitoring/cost_monitor.py

from django.db import models
from django.utils import timezone

class LLMApiUsage(models.Model):
    """LLM API使用记录"""
    
    model = models.CharField(max_length=50, verbose_name="模型")
    task = models.CharField(max_length=50, verbose_name="任务类型")
    input_tokens = models.IntegerField(verbose_name="输入tokens")
    output_tokens = models.IntegerField(verbose_name="输出tokens")
    cost = models.FloatField(verbose_name="成本(元)")
    cache_hit = models.BooleanField(default=False, verbose_name="是否命中缓存")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="时间")
    
    class Meta:
        db_table = 'llm_api_usage'
        verbose_name = "LLM API使用记录"
        ordering = ['-created_at']

class CostMonitor:
    """成本监控器"""
    
    @classmethod
    def record_usage(cls, model: str, task: str, input_tokens: int, 
                     output_tokens: int, cost: float, cache_hit: bool):
        """记录API使用"""
        LLMApiUsage.objects.create(
            model=model,
            task=task,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            cost=cost,
            cache_hit=cache_hit
        )
    
    @classmethod
    def get_daily_cost(cls, date: timezone.datetime = None) -> dict:
        """获取每日成本"""
        date = date or timezone.now().date()
        
        usage = LLMApiUsage.objects.filter(
            created_at__date=date
        ).aggregate(
            total_cost=models.Sum('cost'),
            total_tokens=models.Sum(models.F('input_tokens') + models.F('output_tokens')),
            cache_hits=models.Count('id', filter=models.Q(cache_hit=True)),
            total_requests=models.Count('id')
        )
        
        return {
            "date": date,
            "total_cost": usage['total_cost'] or 0,
            "total_tokens": usage['total_tokens'] or 0,
            "cache_hits": usage['cache_hits'] or 0,
            "total_requests": usage['total_requests'] or 0,
            "cache_hit_rate": (usage['cache_hits'] / usage['total_requests'] * 100) 
                              if usage['total_requests'] else 0
        }
```

---

## 七、混合查询策略

### 7.1 规则+LLM混合引擎

```python
# agent/intent_recognizer/hybrid_recognizer.py

from agent.intent_recognizer.llm_recognizer import LLMIntentRecognizer
from agent.intent_recognizer.rule_based import RuleBasedIntentRecognizer

class HybridIntentRecognizer:
    """混合意图识别器"""
    
    def __init__(self):
        self.rule_recognizer = RuleBasedIntentRecognizer()
        self.llm_recognizer = LLMIntentRecognizer()
        self.cost_optimizer = CostOptimizer(daily_budget=50.0)
    
    def recognize(self, query: str, context: dict = None) -> Intent:
        """混合识别"""
        # 1. 先用规则引擎快速识别
        rule_result = self.rule_recognizer.recognize(query)
        
        # 2. 评估规则识别结果
        if rule_result.confidence > 0.95:
            # 高置信度，直接返回
            return rule_result
        
        if rule_result.confidence < 0.6:
            # 低置信度，必须使用LLM
            if self.cost_optimizer.should_use_llm(complexity="medium"):
                return self.llm_recognizer.recognize(query, context)
            else:
                # 预算不足，返回规则结果
                return rule_result
        
        # 3. 中等置信度，根据复杂度决定
        complexity = self._assess_complexity(query)
        
        if complexity == "simple":
            return rule_result
        elif complexity == "medium" and self.cost_optimizer.should_use_llm():
            return self.llm_recognizer.recognize(query, context)
        else:
            return rule_result
    
    def _assess_complexity(self, query: str) -> str:
        """评估查询复杂度"""
        # 简单查询：单一意图，明确参数
        simple_patterns = [
            r'^\d{4}年唱得最多的\d+首歌$',
            r'^搜索《.+》$',
            r'^上周有哪些直播\?$'
        ]
        
        for pattern in simple_patterns:
            if re.match(pattern, query):
                return "simple"
        
        # 复杂查询：多条件组合
        if '和' in query or '或者' in query or '对比' in query:
            return "complex"
        
        return "medium"
```

### 7.2 查询执行优化

```python
# agent/query_executor/optimized_executor.py

class OptimizedQueryExecutor:
    """优化的查询执行器"""
    
    def __init__(self):
        self.services = {...}
        self.cache = CacheManager()
        self.llm_cache = LLMCache()
    
    def execute(self, intent: Intent) -> QueryResult:
        """执行查询（优化版）"""
        # 1. 检查结果缓存
        cache_key = self._generate_cache_key(intent)
        cached_result = self.cache.get(cache_key)
        if cached_result:
            return cached_result
        
        # 2. 执行查询
        result = self._execute_query(intent)
        
        # 3. 如果成功，缓存结果
        if result.success:
            self.cache.set(cache_key, result, timeout=300)
        
        return result
    
    def _execute_query(self, intent: Intent) -> QueryResult:
        """执行查询"""
        try:
            # 根据意图类型路由
            if intent.type == IntentType.SONG_SEARCH:
                return self._execute_song_search(intent.parameters)
            elif intent.type == IntentType.SONG_STATS:
                return self._execute_song_stats(intent.parameters)
            # ... 其他意图
            
        except Exception as e:
            # 记录错误
            logger.error(f"查询执行失败: {e}")
            return QueryResult(success=False, error=str(e))
    
    def _execute_song_search(self, params: dict) -> QueryResult:
        """执行歌曲搜索（优化版）"""
        # 1. 构建查询
        query = Song.objects.all()
        
        # 2. 应用过滤器（使用select_related减少查询）
        if params.get('style'):
            query = query.filter(
                song_styles__style__name=params['style']
            ).select_related()
        
        if params.get('tags'):
            query = query.filter(
                song_tags__tag__name__in=params['tags']
            ).prefetch_related('song_tags__tag')
        
        # 3. 执行查询（使用annotate计算统计）
        songs = query.annotate(
            perform_count=Count('records')
        ).order_by('-perform_count')[:params.get('limit', 10)]
        
        # 4. 批量获取封面URL
        song_ids = [s.id for s in songs]
        covers = SongRecord.objects.filter(
            song_id__in=song_ids
        ).values('song_id', 'cover_url').distinct()
        
        cover_map = {c['song_id']: c['cover_url'] for c in covers}
        
        # 5. 组装结果
        result = []
        for song in songs:
            result.append({
                'id': song.id,
                'song_name': song.song_name,
                'singer': song.singer,
                'perform_count': song.perform_count,
                'cover_url': cover_map.get(song.id),
                'styles': [s.style.name for s in song.song_styles.all()],
                'tags': [t.tag.name for t in song.song_tags.all()]
            })
        
        return QueryResult(
            success=True,
            data=result,
            result_type='song_list'
        )
```

---

## 八、API设计

### 8.1 LLM配置API

```python
# POST /api/agent/llm/config

Request:
{
  "provider": "aliyun",  # aliyun, openai, local
  "model": "qwen-max",
  "api_key": "sk-xxx",
  "daily_budget": 50.0
}

Response:
{
  "success": true,
  "message": "LLM配置已更新",
  "config": {
    "provider": "aliyun",
    "model": "qwen-max",
    "daily_budget": 50.0
  }
}
```

### 8.2 成本查询API

```python
# GET /api/agent/llm/cost?date=2026-02-03

Response:
{
  "success": true,
  "date": "2026-02-03",
  "cost": {
    "total_cost": 12.50,
    "total_tokens": 125000,
    "cache_hits": 350,
    "total_requests": 500,
    "cache_hit_rate": 70.0,
    "by_model": {
      "qwen-max": {"cost": 8.00, "requests": 200},
      "qwen-turbo": {"cost": 4.50, "requests": 300}
    },
    "by_task": {
      "intent_recognition": {"cost": 3.00, "requests": 300},
      "response_generation": {"cost": 9.50, "requests": 200}
    }
  }
}
```

### 8.3 增强的查询API

```python
# POST /api/agent/query

Request:
{
  "query": "最近一个月演唱的古风歌曲有哪些？",
  "user_id": "user_123",
  "use_llm": true,  // 是否使用LLM
  "format": "table",
  "enable_explanation": true  // 是否生成解释
}

Response:
{
  "success": true,
  "intent": {
    "type": "song_search",
    "parameters": {
      "style": "古风",
      "time_range": "last_month"
    },
    "confidence": 0.96,
    "reasoning": "用户询问'最近一个月'的'古风歌曲'，识别为歌曲搜索并筛选风格",
    "recognizer": "llm"  // llm 或 rule
  },
  "result": {
    "type": "table",
    "columns": ["歌曲名称", "演唱次数", "首次演唱"],
    "rows": [...],
    "summary": "最近一个月演唱的古风歌曲"
  },
  "response": {
    "text": "最近一个月，咻咻满演唱了5首古风歌曲，其中《青花瓷》演唱次数最多，共3次。🎵",
    "highlights": ["共5首古风歌曲", "《青花瓷》演唱3次"],
    "suggestions": ["查看每首歌的详细演唱记录", "搜索更多古风歌曲"]
  },
  "execution_time": 0.95,
  "from_cache": false,
  "model_used": "qwen-max",
  "cost": 0.08
}
```

---

## 九、安全与隐私

### 9.1 敏感数据过滤

```python
# agent/security/sensitive_data_filter.py

class SensitiveDataFilter:
    """敏感数据过滤器"""
    
    # 敏感字段列表
    SENSITIVE_FIELDS = [
        'user_id',
        'ip_address',
        'email',
        'phone',
        'real_name'
    ]
    
    @classmethod
    def filter_query(cls, query: str) -> str:
        """过滤查询中的敏感信息"""
        # 移除潜在的个人信息
        filtered = re.sub(r'\d{11}', '[手机号]', query)  # 手机号
        filtered = re.sub(r'[\w\.-]+@[\w\.-]+\.\w+', '[邮箱]', filtered)  # 邮箱
        filtered = re.sub(r'\d{18}', '[身份证]', filtered)  # 身份证
        
        return filtered
    
    @classmethod
    def filter_result(cls, data: dict) -> dict:
        """过滤结果中的敏感字段"""
        filtered = data.copy()
        
        for field in cls.SENSITIVE_FIELDS:
            if field in filtered:
                filtered[field] = '***'
        
        return filtered
```

### 9.2 API密钥管理

```python
# agent/security/api_key_manager.py

import os
from cryptography.fernet import Fernet

class APIKeyManager:
    """API密钥管理器"""
    
    def __init__(self):
        self.cipher = Fernet(self._get_or_create_key())
    
    def _get_or_create_key(self) -> bytes:
        """获取或创建加密密钥"""
        key_file = '/tmp/llm_api_key.enc'
        
        if os.path.exists(key_file):
            with open(key_file, 'rb') as f:
                return f.read()
        else:
            key = Fernet.generate_key()
            with open(key_file, 'wb') as f:
                f.write(key)
            os.chmod(key_file, 0o600)  # 仅所有者可读写
            return key
    
    def encrypt_key(self, api_key: str) -> str:
        """加密API密钥"""
        return self.cipher.encrypt(api_key.encode()).decode()
    
    def decrypt_key(self, encrypted_key: str) -> str:
        """解密API密钥"""
        return self.cipher.decrypt(encrypted_key.encode()).decode()
    
    def store_key(self, provider: str, api_key: str):
        """存储API密钥"""
        encrypted = self.encrypt_key(api_key)
        # 存储到环境变量或配置文件
        os.environ[f'LLM_{provider.upper()}_API_KEY'] = encrypted
```

---

## 十、性能优化

### 10.1 异步调用

```python
# agent/llm/async_llm_client.py

import asyncio
from concurrent.futures import ThreadPoolExecutor

class AsyncLLMClient:
    """异步LLM客户端"""
    
    def __init__(self, sync_client):
        self.sync_client = sync_client
        self.executor = ThreadPoolExecutor(max_workers=5)
    
    async def complete_async(self, prompt: str, **kwargs) -> str:
        """异步完成"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            self.executor,
            self.sync_client.complete,
            prompt,
            **kwargs
        )
    
    async def batch_complete(self, prompts: list) -> list[str]:
        """批量完成"""
        tasks = [
            self.complete_async(prompt)
            for prompt in prompts
        ]
        return await asyncio.gather(*tasks)
```

### 10.2 Token优化

```python
# agent/llm/token_optimizer.py

class TokenOptimizer:
    """Token优化器"""
    
    @staticmethod
    def compress_prompt(prompt: str) -> str:
        """压缩提示词"""
        # 移除多余的空白
        compressed = re.sub(r'\s+', ' ', prompt)
        
        # 移除不必要的换行
        compressed = compressed.replace('\n', ' ')
        
        # 使用缩写
        abbreviations = {
            "information": "info",
            "description": "desc",
            "parameters": "params"
        }
        
        for full, abbr in abbreviations.items():
            compressed = compressed.replace(full, abbr)
        
        return compressed.strip()
    
    @staticmethod
    def truncate_history(history: list, max_tokens: int = 2000) -> list:
        """截断历史记录"""
        truncated = []
        current_tokens = 0
        
        for msg in reversed(history):
            tokens = len(msg['content']) // 1.5  # 粗略估算
            
            if current_tokens + tokens > max_tokens:
                break
            
            truncated.insert(0, msg)
            current_tokens += tokens
        
        return truncated
```

---

## 十一、监控与日志

### 11.1 LLM调用日志

```python
# agent/monitoring/llm_logger.py

import logging

logger = logging.getLogger('llm')

class LLMLogger:
    """LLM调用日志"""
    
    @staticmethod
    def log_request(model: str, task: str, prompt: str):
        """记录请求"""
        logger.info(f"[{task}] Model: {model}, Prompt length: {len(prompt)}")
    
    @staticmethod
    def log_response(model: str, task: str, response: str, 
                     tokens: int, cost: float, latency: float):
        """记录响应"""
        logger.info(
            f"[{task}] Model: {model}, "
            f"Tokens: {tokens}, "
            f"Cost: ¥{cost:.4f}, "
            f"Latency: {latency:.2f}s"
        )
    
    @staticmethod
    def log_error(model: str, task: str, error: str):
        """记录错误"""
        logger.error(f"[{task}] Model: {model}, Error: {error}")
```

### 11.2 性能指标

| 指标 | 目标值 | 监控方式 |
|-----|-------|---------|
| **意图识别准确率** | >95% | 对比规则引擎结果 |
| **平均响应时间** | <1s | API响应时间统计 |
| **缓存命中率** | >60% | Redis缓存统计 |
| **每日成本** | <¥50 | 成本监控 |
| **错误率** | <1% | 错误日志统计 |

---

## 十二、实施计划

### 12.1 阶段划分

#### 第一阶段：基础集成（1周）

**任务**：
1. 集成通义千问API
2. 实现LLM客户端封装
3. 实现LLM意图识别器
4. 实现基础缓存
5. 单元测试

**交付物**：
- LLM客户端模块
- 意图识别器
- 测试用例

#### 第二阶段：增强功能（1周）

**任务**：
1. 实现上下文解析器
2. 实现结果生成器
3. 实现混合查询引擎
4. 成本监控系统
5. API接口开发

**交付物**：
- 完整的LLM集成模块
- API文档
- 成本监控面板

#### 第三阶段：优化与部署（1周）

**任务**：
1. 性能优化（异步、缓存）
2. 成本优化（降级策略）
3. 安全加固
4. 监控告警
5. 生产环境部署

**交付物**：
- 性能测试报告
- 部署文档
- 监控面板

### 12.2 里程碑

| 里程碑 | 时间 | 交付内容 |
|-------|------|---------|
| M1 | 第1周 | LLM基础集成完成 |
| M2 | 第2周 | 增强功能完成 |
| M3 | 第3周 | 生产环境上线 |

---

## 十三、风险评估与应对

### 13.1 风险清单

| 风险 | 影响 | 概率 | 应对措施 |
|-----|-----|-----|---------|
| **API成本超支** | 高 | 中 | 预算控制、缓存、降级到规则引擎 |
| **API不稳定** | 中 | 中 | 多提供商支持、自动重试、降级 |
| **响应时间过长** | 中 | 低 | 异步调用、缓存、本地模型降级 |
| **数据泄露** | 高 | 低 | 敏感数据过滤、加密存储 |
| **识别准确率下降** | 中 | 低 | 混合引擎、人工审核 |

### 13.2 降级策略

```python
# agent/fallback/fallback_manager.py

class FallbackManager:
    """降级管理器"""
    
    LEVELS = [
        {
            'name': 'llm',
            'confidence_threshold': 0.95,
            'use_llm': True
        },
        {
            'name': 'hybrid',
            'confidence_threshold': 0.70,
            'use_llm': True,
            'fallback_to_rules': True
        },
        {
            'name': 'rules',
            'confidence_threshold': 0.0,
            'use_llm': False
        }
    ]
    
    @classmethod
    def get_level(cls, cost_budget: float, api_status: bool) -> dict:
        """获取当前降级级别"""
        # API不可用，使用规则引擎
        if not api_status:
            return cls.LEVELS[2]
        
        # 预算不足，使用混合引擎
        if cost_budget < 10.0:
            return cls.LEVELS[1]
        
        # 正常情况，使用LLM
        return cls.LEVELS[0]
```

---

## 十四、总结

### 14.1 方案优势

1. **渐进式接入**：分阶段实施，降低风险
2. **成本可控**：多层缓存、预算控制、降级策略
3. **高可用性**：多提供商支持、自动降级
4. **性能优化**：异步调用、Token优化、批量处理
5. **可观测性**：完整的监控和日志系统

### 14.2 预期效果

| 指标 | 接入前 | 接入后 | 提升 |
|-----|-------|-------|-----|
| **意图识别准确率** | 85% | 95%+ | +12% |
| **支持查询复杂度** | 简单 | 复杂 | 质的飞跃 |
| **对话自然度** | 机械 | 流畅 | 显著提升 |
| **用户满意度** | 70% | 90%+ | +20% |
| **日均成本** | ¥0 | ¥30-50 | 新增成本 |

### 14.3 后续优化方向

1. **Fine-tuning**：针对音乐领域微调模型
2. **本地部署**：部署本地模型降低成本
3. **多模态**：支持图片、音频查询
4. **个性化**：基于用户偏好优化Prompt
5. **联邦学习**：保护隐私的数据增强

---

## 附录

### A. 环境变量配置

```bash
# .env

# 通义千问配置
DASHSCOPE_API_KEY=sk-xxxxxxxxxxxxxxxx

# OpenAI配置（可选）
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxx

# 成本控制
LLM_DAILY_BUDGET=50.0
LLM_CACHE_ENABLED=true

# 降级策略
LLM_FALLBACK_TO_RULES=true
LLM_MULTI_PROVIDER=true
```

### B. 配置示例

```python
# agent/config/llm_config.py

LLM_CONFIG = {
    "default_provider": "aliyun",
    "providers": {
        "aliyun": {
            "model": "qwen-max",
            "api_key": os.getenv("DASHSCOPE_API_KEY"),
            "timeout": 30,
            "max_retries": 3
        },
        "openai": {
            "model": "gpt-4o-mini",
            "api_key": os.getenv("OPENAI_API_KEY"),
            "timeout": 30,
            "max_retries": 3
        }
    },
    "cost_control": {
        "daily_budget": 50.0,
        "alert_threshold": 40.0
    },
    "cache": {
        "enabled": True,
        "timeout": {
            "intent_recognition": 86400,
            "response_generation": 3600
        }
    }
}
```

### C. 测试用例

```python
# agent/tests/test_llm_integration.py

import pytest
from agent.intent_recognizer.llm_recognizer import LLMIntentRecognizer

class TestLLMIntentRecognition:
    
    @pytest.fixture
    def recognizer(self):
        return LLMIntentRecognizer()
    
    def test_song_search(self, recognizer):
        """测试歌曲搜索识别"""
        query = "搜索《稻香》"
        intent = recognizer.recognize(query)
        
        assert intent.type == IntentType.SONG_SEARCH
        assert intent.parameters['song_name'] == '稻香'
        assert intent.confidence > 0.9
    
    def test_complex_query(self, recognizer):
        """测试复杂查询识别"""
        query = "2024年演唱最多的5首古风歌曲"
        intent = recognizer.recognize(query)
        
        assert intent.type == IntentType.SONG_STATS
        assert intent.parameters['year'] == 2024
        assert intent.parameters['limit'] == 5
        assert intent.parameters.get('style') == '古风'
    
    def test_context_aware(self, recognizer):
        """测试上下文感知"""
        context = {
            "history": [
                {"role": "user", "content": "最近演唱的歌曲"},
                {"role": "assistant", "content": "《稻香》、《青花瓷》..."}
            ],
            "entities": ["稻香", "青花瓷"]
        }
        query = "这首歌第一次唱是什么时候？"
        
        intent = recognizer.recognize(query, context)
        assert intent.parameters.get('song_name') in context['entities']
```