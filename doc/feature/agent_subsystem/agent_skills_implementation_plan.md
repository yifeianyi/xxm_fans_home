# 小满虫之家 - Agent Skills智能查询系统实现方案

## 一、项目概述

### 1.1 背景

XXM Fans Home 项目积累了多维度数据（歌曲、直播、二创作品、图集、粉丝数据等），粉丝们有各种个性化查询需求。传统的固定页面无法满足所有需求，需要构建一个灵活的智能查询系统。

### 1.2 核心概念

#### Function Calling 与 Agent Skills 的关系

**Function Calling（实现机制）**：
- LLM调用工具的标准化协议
- 定义工具名称、描述、参数（JSON Schema）
- 示例：`search_songs(year=2024, limit=5)`

**Agent Skills（架构范式）**：
- 智能体能力的抽象、封装与管理方式
- 将复杂能力拆解为独立的、可复用的技能模块
- 本方案中，Skills设计为**最基础的数据库查询操作**
- LLM自由组合这些基础操作完成复杂任务

**关系图**：
```
Agent Skills (架构层)
    ↓
┌─────────────────────────────┐
│  基础查询Skills              │
│  - 查询歌曲数据               │
│  - 查询粉丝数据               │
│  - 查询直播记录               │
│  - 查询图集信息               │
└─────────────────────────────┘
            ↓
    LLM自由组合基础查询：
    用户："分析最近3个月粉丝增长"
    ↓
    LLM规划：
    1. 调用：查询粉丝数据(days=90)
    2. 调用：查询直播记录(period=90)
    3. 调用：计算增长率(data)
    4. 调用：关联分析(data1, data2)
    5. 生成分析报告
```

**设计理念**：
- **原子化**：每个Skill只做一件事，不做复杂逻辑
- **可组合**：LLM可以根据需求自由组合多个Skills
- **最大化灵活性**：让LLM发挥其理解和规划能力

### 1.3 技术选型

采用 **Agent Skills 架构 + Function Calling 实现** 的方案：

**优势**：
- ✅ **原子化设计**：每个Skill专注于单一数据库查询
- ✅ **最大化灵活性**：LLM自由组合，不受预设流程限制
- ✅ **可扩展**：新增基础查询操作只需添加新Skill
- ✅ **易于维护**：Skill简单明了，问题易定位
- ✅ **懒加载**：只加载被选中的Skill内容，降低Token消耗

---

## 二、系统架构

### 2.1 整体架构

```
┌─────────────────────────────────────────────────────────┐
│                      用户界面                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐   │
│  │  聊天界面      │  │  快捷查询     │  │  历史记录     │   │
│  └──────────────┘  └──────────────┘  └──────────────┘   │
└─────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────┐
│            Skills Manager (Skills管理器)                 │
│  ├─ 加载Skills描述列表                                   │
│  ├─ 智能路由：选择合适的Skill                            │
│  └─ 懒加载：加载被选中的Skill完整内容                    │
└─────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────┐
│           Skills Repository (Skills仓库)                  │
│  ┌─────────────────────────────────────────────┐        │
│  │ Skills描述列表（轻量级，启动时加载）          │        │
│  │ - query_songs: 查询歌曲数据                 │
│  │ - query_fans: 查询粉丝数据                   │
│  │ - query_livestreams: 查询直播记录             │
│  │ - query_galleries: 查询图集信息              │
│  │ - calculate_growth: 计算增长率               │
│  │ - correlate_data: 数据关联分析               │
│  └─────────────────────────────────────────────┘        │
│                      ┌───────┐                          │
│                      │ SKILL │ ← 懒加载：只加载被选中的  │
│                      │ 文件  │                          │
│                      └───────┘                          │
└─────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────┐
│           Function Calling (工具调用层)                  │
│  ┌─────────────────────────────────────────────┐        │
│  │ 工具定义（JSON Schema）                      │        │
│  │ - query_songs(filter, sort, limit)          │
│  │ - query_fans(days, date_range)              │
│  │ - query_livestreams(filter, limit)          │
│  │ - calculate_growth(data, metric)            │
│  │ - correlate_data(data1, data2, method)      │
│  └─────────────────────────────────────────────┘        │
└─────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────┐
│                  数据访问层                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐   │
│  │ Django ORM   │  │ 数据查询      │  │ 结果格式化    │   │
│  └──────────────┘  └──────────────┘  └──────────────┘   │
└─────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────┐
│                  数据存储层                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐   │
│  │ PostgreSQL   │  │ SQLite       │  │ 缓存层        │   │
│  └──────────────┘  └──────────────┘  └──────────────┘   │
└─────────────────────────────────────────────────────────┘
```

### 2.2 Skill定义结构

```
.iflow/skills/
├── query/                    # 基础查询Skills
│   ├── songs/
│   │   ├── SKILL.md          # Skill定义
│   │   └── template.md       # 输出模板
│   ├── fans/
│   │   ├── SKILL.md
│   │   └── template.md
│   ├── livestreams/
│   │   ├── SKILL.md
│   │   └── template.md
│   └── galleries/
│       ├── SKILL.md
│       └── template.md
├── analysis/                # 基础分析Skills
│   ├── calculate/
│   │   ├── growth/
│   │   │   └── SKILL.md
│   │   └── statistics/
│   │       └── SKILL.md
│   └── correlate/
│       └── SKILL.md
└── api/                      # API参考（已存在）
    ├── song_management.md
    ├── data_analytics.md
    └── fansdiy.md
```

### 2.3 Skill工作流程

```
用户查询："分析最近3个月粉丝增长趋势并找出影响因素"
    ↓
[Skills Manager] 从描述列表中提供所有可用Skills
    ↓
[LLM] 分析需求，自主规划执行流程
    ↓
[LLM] 决定需要调用的Skills（自由组合）：
    1. query_fans(days=90)
    2. query_livestreams(date_range=90天)
    3. calculate_growth(data=fans_data)
    4. correlate_data(data1=fans_data, data2=livestreams)
    ↓
[执行] 按顺序或并行调用Skills
    ↓
[LLM] 整合结果，生成分析报告
    ↓
返回给用户
```

---

## 三、基础Skills实现

### 3.1 歌曲查询Skill

```markdown
# .iflow/skills/query/songs/SKILL.md
---
name: query-songs
description: 基础歌曲数据查询，支持多种筛选和排序条件
---

## 功能
从数据库查询歌曲数据，返回符合条件的结果。

## 参数
通过 Function Calling 传递以下参数：

### filter (object, 可选)
筛选条件：
- song_name (string): 歌曲名称
- year (integer): 年份
- style (string): 曲风
- tags (array): 标签列表
- perform_count_min (integer): 最低演唱次数
- perform_count_max (integer): 最高演唱次数

### sort (object, 可选)
排序条件：
- field (string): 排序字段（perform_count, first_perform, last_performed）
- order (string): 排序方向（asc, desc）

### limit (integer, 可选)
返回数量限制，默认10，最大100

## 返回
返回歌曲列表，每项包含：
- id: 歌曲ID
- song_name: 歌曲名称
- singer: 歌手
- perform_count: 演唱次数
- first_perform: 首次演唱日期
- last_performed: 最近演唱日期
- styles: 曲风列表
- tags: 标签列表

## 说明
这是一个纯数据查询操作，不包含任何分析逻辑。LLM可以自由组合多个查询来完成复杂任务。
```

### 3.2 粉丝数据查询Skill

```markdown
# .iflow/skills/query/fans/SKILL.md
---
name: query-fans
description: 基础粉丝数据查询
---

## 功能
从数据库查询粉丝数据，支持时间范围和聚合查询。

## 参数

### days (integer, 可选)
查询最近N天的数据，默认30

### date_range (object, 可选)
精确日期范围：
- start_date (string): 开始日期 (YYYY-MM-DD)
- end_date (string): 结束日期 (YYYY-MM-DD)

### aggregation (string, 可选)
聚合方式：
- 'daily': 按天聚合
- 'weekly': 按周聚合
- 'monthly': 按月聚合
- 'hourly': 按小时聚合

## 返回
返回粉丝数据列表，每项包含：
- date: 日期
- fans_count: 粉丝数
- daily_growth: 日增长数

## 说明
这是基础数据查询操作，不包含增长率计算。如果需要计算增长率，请使用 calculate-growth Skill。
```

### 3.3 直播记录查询Skill

```markdown
# .iflow/skills/query/livestreams/SKILL.md
---
name: query-livestreams
description: 基础直播记录查询
---

## 功能
从数据库查询直播记录，支持时间范围筛选。

## 参数

### filter (object, 可选)
筛选条件：
- start_date (string): 开始日期
- end_date (string): 结束日期
- song_cuts_min (integer): 最低歌切数
- song_cuts_max (integer): 最高歌切数
- duration_min (integer): 最短时长（分钟）
- duration_max (integer): 最长时长（分钟）

### sort (object, 可选)
排序条件：
- field (string): 排序字段（date, song_cuts, duration）
- order (string): 排序方向

### limit (integer, 可选)
返回数量限制，默认10

## 返回
返回直播记录列表，每项包含：
- id: 直播ID
- date: 直播日期
- song_cuts: 歌切数量
- duration: 时长（分钟）
- cover_url: 封面图URL

## 说明
这是基础数据查询操作，不包含任何分析逻辑。
```

### 3.4 增长率计算Skill

```markdown
# .iflow/skills/analysis/calculate/growth/SKILL.md
---
name: calculate-growth
description: 计算增长率指标
---

## 功能
对粉丝数据进行增长率计算。

## 参数

### data (array, 必需)
粉丝数据数组，每项应包含：
- date: 日期
- fans_count: 粉丝数
- daily_growth: 日增长数

### metrics (array, 可选)
需要计算的指标，默认全部：
- 'avg_growth': 平均增长率
- 'total_growth': 总增长
- 'growth_rate': 增长率百分比
- 'peak_date': 峰值日期
- 'valley_date': 谷值日期
- 'trend': 趋势方向

## 返回
返回计算结果，包含：
- metrics: 指标对象
- details: 详细计算过程

## 说明
这是纯计算操作，不包含数据获取。需要先使用 query-fans 获取数据。
```

### 3.5 数据关联分析Skill

```markdown
# .iflow/skills/analysis/correlate/SKILL.md
---
name: correlate-data
description: 数据关联分析
---

## 功能
分析两组数据之间的关联关系。

## 参数

### data1 (array, 必需)
第一组数据

### data2 (array, 必需)
第二组数据

### method (string, 可选)
关联分析方法：
- 'pearson': 皮尔逊相关系数（默认）
- 'spearman': 斯皮尔曼相关系数
- 'kendall': 肯德尔相关系数

### date_field (string, 可选)
日期字段名，用于时间对齐，默认'date'

## 返回
返回关联分析结果，包含：
- correlation: 相关系数
- p_value: 显著性水平
- interpretation: 解释说明

## 说明
这是纯分析操作，不包含数据获取。
```

---

## 四、模板文件

### 4.1 歌曲查询模板

```markdown
# .iflow/skills/query/songs/template.md

## 查询结果

找到 **{{total}}** 首歌曲

### 歌曲列表
{{#each songs}}
{{@index}}. **{{song_name}}** - {{singer}}
   - 演唱次数：{{perform_count}}
   - 首次演唱：{{first_perform}}
   - 最近演唱：{{last_performed}}
   - 曲风：{{styles}}
   - 标签：{{tags}}

{{/each}}

---
查询时间：{{timestamp}}
```

### 4.2 粉丝数据模板

```markdown
# .iflow/skills/query/fans/template.md

## 粉丝数据

### 时间范围
- 开始日期：{{start_date}}
- 结束日期：{{end_date}}

### 数据列表
{{#each data}}
- {{date}}: {{fans_count}} 粉丝 ({{daily_growth > 0 ? '+' : ''}}{{daily_growth}})
{{/each}}

---
查询时间：{{timestamp}}
```

---

## 五、后端实现

### 5.1 Skills管理器

```python
# repo/xxm_fans_backend/agent/skills_manager.py

import os
import json
import re
import requests
from typing import Dict, List, Any
from pathlib import Path

class SkillsManager:
    """Skills管理器（懒加载机制）"""

    def __init__(self, skills_dir: str = None):
        if skills_dir is None:
            project_root = Path(__file__).parent.parent.parent.parent
            skills_dir = project_root / '.iflow' / 'skills'

        self.skills_dir = Path(skills_dir)
        self.api_base = "http://localhost:8080"
        self.skills_descriptions = self._load_skills_descriptions()

    def _load_skills_descriptions(self) -> List[Dict[str, Any]]:
        """加载所有Skills的描述列表（轻量级，启动时调用）"""
        descriptions = []

        for skill_path in self.skills_dir.rglob('SKILL.md'):
            info = self._parse_skill_frontmatter(skill_path)
            if info:
                descriptions.append({
                    'name': info.get('name'),
                    'description': info.get('description'),
                    'path': str(skill_path)
                })

        return descriptions

    def _parse_skill_frontmatter(self, skill_path: Path) -> Dict[str, Any]:
        """解析Skill的frontmatter"""
        content = skill_path.read_text()

        match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
        if not match:
            return None

        frontmatter_text = match.group(1)
        frontmatter = self._parse_yaml_frontmatter(frontmatter_text)

        if 'description' not in frontmatter:
            after_frontmatter = content[match.end():]
            desc_match = re.search(r'^(.+?)(?:\n\n|\n#{1,2} )', after_frontmatter)
            if desc_match:
                frontmatter['description'] = desc_match.group(1).strip()

        frontmatter['path'] = str(skill_path)
        frontmatter['name'] = frontmatter.get('name', skill_path.parent.name)

        return frontmatter

    def _parse_yaml_frontmatter(self, text: str) -> Dict[str, Any]:
        """解析YAML frontmatter"""
        result = {}
        for line in text.split('\n'):
            if ':' in line:
                key, value = line.split(':', 1)
                key = key.strip().lower()
                value = value.strip()

                if value.lower() in ['true', 'false']:
                    result[key] = value.lower() == 'true'
                elif value.startswith('['):
                    result[key] = [v.strip() for v in value[1:-1].split(',')]
                elif value.startswith('"') or value.startswith("'"):
                    result[key] = value[1:-1]
                else:
                    result[key] = value

        return result

    def get_skills_manifest(self) -> str:
        """获取Skills清单（用于发送给LLM）"""
        manifest = "可用的基础Skills：\n\n"

        for skill in self.skills_descriptions:
            manifest += f"- {skill['name']}: {skill['description']}\n"

        return manifest

    def route_query(self, query: str) -> Dict[str, Any]:
        """智能路由查询到合适的Skill"""

        # 将所有Skills描述发送给LLM，让LLM自由选择和组合
        result = self._execute_with_llm(query)

        return result

    def _execute_with_llm(self, query: str) -> Dict[str, Any]:
        """使用LLM执行查询（让LLM自由组合Skills）"""
        import os

        # 构建提示词：提供所有Skills，让LLM自由组合
        prompt = f"""你是一个智能查询助手，可以自由组合以下基础Skills来回答用户问题。

{self.get_skills_manifest()}

用户查询：{query}

请分析用户需求，规划需要调用的Skills，并按照以下格式返回：
```json
{{
  "steps": [
    {{
      "skill": "skill-name",
      "params": {{}}
    }}
  ],
  "reasoning": "执行步骤说明"
}}
```
只返回JSON，不要包含其他内容。"""

        try:
            api_key = os.environ.get('LLM_API_KEY')
            if not api_key:
                return {
                    "success": False,
                    "error": "LLM_API_KEY未配置"
                }

            # 第一步：让LLM规划执行步骤
            plan_result = self._call_llm_api_simple(prompt)
            plan = json.loads(plan_result.strip())

            # 第二步：执行规划中的每个步骤
            results = []
            for step in plan.get('steps', []):
                skill_name = step.get('skill')
                params = step.get('params', {})

                skill_result = self.execute_skill(skill_name, json.dumps(params))
                results.append({
                    'skill': skill_name,
                    'params': params,
                    'result': skill_result
                })

            # 第三步：让LLM整合结果并生成最终回答
            final_result = self._integrate_results(query, results)

            return {
                "success": True,
                "plan": plan,
                "results": results,
                "final_answer": final_result
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"执行失败: {str(e)}"
            }

    def execute_skill(self, skill_name: str, arguments: str = "") -> Dict[str, Any]:
        """执行指定的Skill（懒加载：只加载被选中的skill内容）"""
        skill_path = self._find_skill_by_name(skill_name)
        if not skill_path:
            return {
                "success": False,
                "error": f"Skill not found: {skill_name}"
            }

        skill_content = skill_path.read_text()
        processed_content = self._process_placeholders(skill_content, arguments)

        try:
            llm_result = self._call_llm_with_functions(processed_content, arguments)
            return {
                "success": True,
                "skill": skill_name,
                "result": llm_result
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"LLM API调用失败: {str(e)}"
            }

    def _find_skill_by_name(self, skill_name: str) -> Path:
        """根据名称查找Skill文件"""
        for skill_desc in self.skills_descriptions:
            if skill_desc['name'] == skill_name:
                return Path(skill_desc['path'])
        return None

    def _process_placeholders(self, content: str, arguments: str) -> str:
        """处理占位符"""
        content = content.replace('$ARGUMENTS', arguments)

        args = arguments.split() if arguments else []
        for i, arg in enumerate(args):
            content = content.replace(f'${i}', arg)
            content = content.replace(f'$ARGUMENTS[{i}]', arg)

        import uuid
        session_id = str(uuid.uuid4())[:8]
        content = content.replace('${CLAUDE_SESSION_ID}', session_id)

        return content

    def _integrate_results(self, query: str, results: List[Dict]) -> str:
        """整合所有Skills的执行结果，生成最终回答"""
        import os

        results_text = "\n".join([
            f"Skill: {r['skill']}\n结果: {json.dumps(r['result'], ensure_ascii=False)}"
            for r in results
        ])

        prompt = f"""根据以下Skills的执行结果，回答用户问题。

用户问题：{query}

Skills执行结果：
{results_text}

请生成清晰、准确的回答。"""

        try:
            return self._call_llm_api_simple(prompt)
        except Exception as e:
            return f"整合结果失败: {str(e)}"

    def _call_llm_with_functions(self, skill_content: str, user_query: str) -> Dict[str, Any]:
        """调用LLM API执行Skill（使用Function Calling）"""
        import os

        api_key = os.environ.get('LLM_API_KEY')
        api_url = os.environ.get('LLM_API_URL', 'https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation')

        if not api_key:
            raise Exception("LLM_API_KEY未配置")

        tools = self._get_available_tools()

        headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }

        payload = {
            'model': os.environ.get('LLM_MODEL', 'qwen-plus'),
            'input': {
                'messages': [
                    {
                        'role': 'system',
                        'content': skill_content
                    },
                    {
                        'role': 'user',
                        'content': user_query
                    }
                ]
            },
            'parameters': {
                'result_format': 'message',
                'max_tokens': 2000,
                'temperature': 0.7,
                'tools': tools
            }
        }

        response = requests.post(api_url, headers=headers, json=payload, timeout=30)
        response.raise_for_status()

        result = response.json()

        if 'output' in result and 'choices' in result['output']:
            return {
                'content': result['output']['choices'][0]['message']['content'],
                'usage': result.get('usage', {})
            }
        else:
            raise Exception("API返回格式异常")

    def _get_available_tools(self) -> List[Dict]:
        """获取可用的工具定义（Function Calling）"""
        return [
            {
                'type': 'function',
                'function': {
                    'name': 'query_songs',
                    'description': '查询歌曲数据',
                    'parameters': {
                        'type': 'object',
                        'properties': {
                            'filter': {
                                'type': 'object',
                                'description': '筛选条件',
                                'properties': {
                                    'song_name': {'type': 'string'},
                                    'year': {'type': 'integer'},
                                    'style': {'type': 'string'},
                                    'perform_count_min': {'type': 'integer'},
                                    'perform_count_max': {'type': 'integer'}
                                }
                            },
                            'sort': {
                                'type': 'object',
                                'description': '排序条件',
                                'properties': {
                                    'field': {'type': 'string'},
                                    'order': {'type': 'string'}
                                }
                            },
                            'limit': {'type': 'integer', 'default': 10}
                        }
                    }
                }
            },
            {
                'type': 'function',
                'function': {
                    'name': 'query_fans',
                    'description': '查询粉丝数据',
                    'parameters': {
                        'type': 'object',
                        'properties': {
                            'days': {'type': 'integer', 'description': '查询最近N天'},
                            'date_range': {
                                'type': 'object',
                                'description': '日期范围',
                                'properties': {
                                    'start_date': {'type': 'string'},
                                    'end_date': {'type': 'string'}
                                }
                            },
                            'aggregation': {'type': 'string', 'description': '聚合方式'}
                        }
                    }
                }
            },
            {
                'type': 'function',
                'function': {
                    'name': 'query_livestreams',
                    'description': '查询直播记录',
                    'parameters': {
                        'type': 'object',
                        'properties': {
                            'filter': {
                                'type': 'object',
                                'description': '筛选条件',
                                'properties': {
                                    'start_date': {'type': 'string'},
                                    'end_date': {'type': 'string'},
                                    'song_cuts_min': {'type': 'integer'},
                                    'song_cuts_max': {'type': 'integer'}
                                }
                            },
                            'sort': {'type': 'object'},
                            'limit': {'type': 'integer', 'default': 10}
                        }
                    }
                }
            },
            {
                'type': 'function',
                'function': {
                    'name': 'calculate_growth',
                    'description': '计算增长率',
                    'parameters': {
                        'type': 'object',
                        'properties': {
                            'data': {'type': 'array', 'description': '粉丝数据'},
                            'metrics': {
                                'type': 'array',
                                'description': '需要计算的指标',
                                'items': {'type': 'string'}
                            }
                        }
                    }
                }
            },
            {
                'type': 'function',
                'function': {
                    'name': 'correlate_data',
                    'description': '数据关联分析',
                    'parameters': {
                        'type': 'object',
                        'properties': {
                            'data1': {'type': 'array', 'description': '第一组数据'},
                            'data2': {'type': 'array', 'description': '第二组数据'},
                            'method': {'type': 'string', 'description': '关联分析方法'}
                        }
                    }
                }
            }
        ]

    def _call_llm_api_simple(self, prompt: str) -> str:
        """简单的LLM API调用"""
        import os
        import requests

        api_key = os.environ.get('LLM_API_KEY')
        api_url = os.environ.get('LLM_API_URL', 'https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation')

        headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }

        payload = {
            'model': os.environ.get('LLM_MODEL', 'qwen-plus'),
            'input': {
                'messages': [
                    {
                        'role': 'user',
                        'content': prompt
                    }
                ]
            },
            'parameters': {
                'result_format': 'message',
                'max_tokens': 1000,
                'temperature': 0.7
            }
        }

        response = requests.post(api_url, headers=headers, json=payload, timeout=30)
        response.raise_for_status()

        result = response.json()

        if 'output' in result and 'choices' in result['output']:
            return result['output']['choices'][0]['message']['content']
        else:
            raise Exception("API返回格式异常")
```

### 5.2 API端点

```python
# repo/xxm_fans_backend/agent/api.py

from rest_framework.decorators import api_view
from rest_framework.response import Response
from .skills_manager import SkillsManager

manager = SkillsManager()

@api_view(['GET'])
def list_skills(request):
    """列出所有可用的Skills（描述列表）"""
    skills = manager.skills_descriptions
    return Response({
        "code": 200,
        "data": skills
    })

@api_view(['POST'])
def query(request):
    """智能查询接口"""
    query = request.data.get('query', '')

    result = manager.route_query(query)

    return Response({
        "code": 200 if result['success'] else 400,
        "data": result
    })
```

### 5.3 URL配置

```python
# repo/xxm_fans_backend/agent/urls.py

from django.urls import path
from . import api

urlpatterns = [
    path('skills/', api.list_skills, name='list_skills'),
    path('query/', api.query, name='query'),
]
```

---

## 六、前端实现

### 6.1 React组件

```typescript
// repo/xxm_fans_frontend/src/presentation/components/features/agent/SkillsChat.tsx

import React, { useState } from 'react';
import { Send, Sparkles } from 'lucide-react';

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  plan?: any;
  results?: any[];
}

const SkillsChat: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [availableSkills, setAvailableSkills] = useState<any[]>([]);

  React.useEffect(() => {
    fetch('/api/agent/skills/')
      .then(res => res.json())
      .then(data => setAvailableSkills(data.data));
  }, []);

  const sendMessage = async () => {
    if (!input.trim()) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: input,
    };

    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setLoading(true);

    try {
      const response = await fetch('/api/agent/query/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: input })
      });

      const data = await response.json();

      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: data.data.final_answer || '查询完成',
        plan: data.data.plan,
        results: data.data.results,
      };

      setMessages(prev => [...prev, assistantMessage]);
    } catch (error) {
      console.error('查询失败:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="skills-chat-container">
      {/* 快捷Skills */}
      <div className="quick-skills">
        <Sparkles className="icon" />
        <span>基础查询：</span>
        {availableSkills.slice(0, 5).map((skill, index) => (
          <button
            key={index}
            onClick={() => setInput(skill.description)}
            className="skill-chip"
          >
            {skill.name}
          </button>
        ))}
      </div>

      {/* 消息列表 */}
      <div className="messages">
        {messages.map(message => (
          <div key={message.id} className={`message ${message.role}`}>
            <div className="content">{message.content}</div>
            {message.plan && (
              <div className="plan">
                <h4>执行计划：</h4>
                <pre>{JSON.stringify(message.plan, null, 2)}</pre>
              </div>
            )}
            {message.results && (
              <div className="results">
                <h4>执行结果：</h4>
                {message.results.map((result, idx) => (
                  <details key={idx}>
                    <summary>{result.skill}</summary>
                    <pre>{JSON.stringify(result.result, null, 2)}</pre>
                  </details>
                ))}
              </div>
            )}
          </div>
        ))}
        {loading && <div className="loading">正在分析和组合查询...</div>}
      </div>

      {/* 输入框 */}
      <div className="input-area">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
          placeholder="输入查询，如：分析最近3个月粉丝增长趋势"
          className="chat-input"
        />
        <button onClick={sendMessage} className="send-button">
          <Send />
        </button>
      </div>
    </div>
  );
};

export default SkillsChat;
```

---

## 七、成本分析

### 7.1 Token消耗

**启动成本**（一次性）：
- Skills描述列表：~100 tokens

**单次查询成本**（LLM自由组合模式）：

| 阶段 | Token消耗 | 说明 |
|-----|---------|-----|
| **规划阶段** | 300-500 | LLM分析需求，规划执行步骤 |
| **Skill执行** | 200-400 × N | N个Skill的执行 |
| **整合阶段** | 300-500 | 整合所有结果，生成最终回答 |
| **总计** | **800-1400 + 200×N** | **N为Skill数量** |

### 7.2 成本计算

**使用通义千问（¥0.04/1k tokens）**：
- 启动成本：¥0.004（一次性）
- 单次查询（3个Skills）：¥0.056-0.092
- 日查询1000次：¥56-92/天
- 月查询30000次：¥1680-2760/月

### 7.3 优化建议

1. **缓存常用查询**：高频查询可以缓存结果
2. **简化Skills描述**：优化Skill内容，减少Token消耗
3. **并行执行**：独立的Skill可以并行调用
4. **使用更便宜的模型**：规划阶段可以使用更便宜的模型

---

## 八、实施计划

### 8.1 阶段1：基础Skills开发（1周）

**任务**：
1. 创建Skills目录结构
2. 实现Skills管理器
3. 开发基础查询Skills：
   - query-songs
   - query-fans
   - query-livestreams
4. 开发基础分析Skills：
   - calculate-growth
   - correlate-data
5. 单元测试

**交付物**：
- Skills管理器代码
- 5个基础Skills
- 测试用例

### 8.2 阶段2：后端API开发（3天）

**任务**：
1. 创建agent Django应用
2. 实现API端点
3. 集成Skills管理器
4. 错误处理
5. API文档

**交付物**：
- agent应用代码
- REST API文档
- 集成测试

### 8.3 阶段3：前端开发（1周）

**任务**：
1. 创建聊天界面组件
2. 实现快捷Skills按钮
3. 执行计划和结果展示
4. 响应式设计
5. 前端测试

**交付物**：
- React组件代码
- 样式文件
- 用户体验文档

### 8.4 阶段4：扩展Skills（1周）

**任务**：
1. 开展更多基础Skills：
   - query-galleries
   - query-fansdiy
   - calculate-statistics
2. 优化现有Skills
3. 添加更多模板
4. 性能优化

**交付物**：
- 8个完整Skills
- 优化报告
- 性能测试

### 8.5 阶段5：测试与上线（3天）

**任务**：
1. 端到端测试
2. 性能测试
3. 用户体验测试
4. 文档完善
5. 上线部署

**交付物**：
- 测试报告
- 用户文档
- 部署文档

---

## 九、使用示例

### 9.1 基础查询

```
用户：2024年唱得最多的5首歌
系统：LLM自由组合Skills
LLM规划：
  1. 调用：query-songs(filter={year:2024}, sort={field:"perform_count", order:"desc"}, limit=5)
执行结果：
找到 5 首歌曲
1. 稻香 - 12次
2. 青花瓷 - 10次
3. 告白气球 - 9次
4. 晴天 - 8次
5. 夜曲 - 7次
```

### 9.2 复杂分析

```
用户：分析最近3个月粉丝增长趋势
系统：LLM自由组合Skills
LLM规划：
  1. 调用：query-fans(days=90)
  2. 调用：calculate_growth(data=步骤1的结果, metrics=["avg_growth", "growth_rate", "trend"])
执行步骤1：
获取90天粉丝数据...

执行步骤2：
计算增长率指标...

最终回答：
## 粉丝增长分析报告

### 增长概况
- 起始粉丝数：100,000
- 结束粉丝数：115,000
- 净增长：+15,000
- 增长率：15%

### 关键指标
- 日均增长：167
- 趋势：持续上升

### 趋势分析
粉丝呈现稳定增长趋势，日均增长167人。
```

### 9.3 数据关联分析

```
用户：分析粉丝增长与直播频率的关系
系统：LLM自由组合Skills
LLM规划：
  1. 调用：query-fans(days=90)
  2. 调用：query-livestreams(filter={start_date:"90天前", end_date:"今天"})
  3. 调用：correlate_data(data1=步骤1的结果, data2=步骤2的结果, method="pearson")
执行步骤1-3...

最终回答：
## 关联分析报告

粉丝增长与直播频率的相关系数：0.85（强正相关）

**解释**：
直播频率与粉丝增长存在强正相关关系，说明增加直播频率有助于粉丝增长。

建议：保持每周至少2-3次直播的频率。
```

---

## 十、总结

### 10.1 核心价值

Agent Skills架构为小满虫之家提供：
- ✅ **原子化设计**：每个Skill专注于单一操作
- ✅ **最大化灵活性**：LLM自由组合，不受预设限制
- ✅ **可扩展**：新增基础操作只需添加新Skill
- ✅ **易于维护**：Skill简单明了
- ✅ **懒加载**：降低Token消耗

### 10.2 技术亮点

1. **原子化Skills**：基础查询操作，不做复杂逻辑
2. **LLM自由组合**：最大化发挥LLM的理解和规划能力
3. **三阶段执行**：规划 → 执行 → 整合
4. **完全灵活**：LLM根据需求动态规划执行流程
5. **易于维护**：Skill简单，问题易定位

### 10.3 预期效果

- 支持95%+的查询需求（更灵活的组合能力）
- 响应时间 < 2s（多次Skill调用）
- 日成本：¥56-92（1000次查询，平均3个Skills）
- 用户满意度 > 95%（更准确的个性化回答）

---

## 附录

### A. Skills清单

| Skill Name | 描述 | 类型 |
|-----------|-----|------|
| query-songs | 查询歌曲数据 | 基础查询 |
| query-fans | 查询粉丝数据 | 基础查询 |
| query-livestreams | 查询直播记录 | 基础查询 |
| query-galleries | 查询图集信息 | 基础查询 |
| calculate-growth | 计算增长率 | 基础分析 |
| calculate-statistics | 计算统计指标 | 基础分析 |
| correlate-data | 数据关联分析 | 基础分析 |

### B. API端点

| 端点 | 方法 | 说明 |
|-----|------|-----|
| /api/agent/skills/ | GET | 列出所有Skills（描述列表） |
| /api/agent/query/ | POST | 智能查询（LLM自由组合） |

### C. 环境变量配置

```bash
# LLM API配置
LLM_API_KEY=your_api_key_here
LLM_API_URL=https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation
LLM_MODEL=qwen-plus
```

### D. 技术栈

- **后端**：Python 3.8+, Django 5.2.3
- **前端**：React 19.2.3, TypeScript 5.8.2
- **架构**：Agent Skills + Function Calling
- **LLM API**：通义千问（qwen-plus）
- **HTTP客户端**：requests
- **数据格式**：JSON, YAML, Markdown

---

**文档版本**：3.0
**创建日期**：2026-02-04
**作者**：iFlow CLI
**更新说明**：完全重写，Skills改为原子化基础查询操作，最大化LLM自由组合能力