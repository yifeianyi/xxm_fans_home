# XXM Fans Home - Agent 智能查询子系统实现方案

## 一、项目背景

XXM Fans Home 项目积累了大量关于咻咻满（XXM）的多维度数据，包括：
- **音乐作品数据**：歌曲信息、演唱记录、曲风、标签
- **粉丝二创数据**：作品合集、作品详情、作者信息
- **直播数据**：直播记录、歌切列表、直播截图
- **图集数据**：多层级图集分类、图片资源
- **数据分析**：作品静态信息、粉丝数指标、爬取任务

粉丝们的查询需求多样化，无法通过固定前端页面一一满足。因此需要构建一个智能查询Agent子系统，通过自然语言理解用户需求，灵活查询数据并返回个性化结果。

---

## 二、核心目标

1. **自然语言查询**：用户可以用自然语言提问，如"2024年唱得最多的5首歌"、"上周直播的截图"、"粉丝数增长最快的月份"
2. **智能意图识别**：自动识别用户查询意图（搜索、统计、对比、推荐等）
3. **多维度数据聚合**：支持跨模块数据查询和关联分析
4. **灵活结果展示**：根据查询类型返回文本、表格、图表、图片等多种格式
5. **可扩展性**：易于添加新的查询类型和数据源

---

## 三、技术架构

### 3.1 整体架构

```
┌─────────────────────────────────────────────────────────────┐
│                         前端层                                │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐       │
│  │  聊天界面组件  │  │  查询结果展示  │  │  历史记录管理  │       │
│  └──────────────┘  └──────────────┘  └──────────────┘       │
└─────────────────────────────────────────────────────────────┘
                              ↓ HTTPS
┌─────────────────────────────────────────────────────────────┐
│                      API网关层                                │
│  ┌──────────────────────────────────────────────────────┐   │
│  │         Agent查询API (/api/agent/query)              │   │
│  │  - 接收自然语言查询                                   │   │
│  │  - 返回结构化结果                                     │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                    Agent核心层                                │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐       │
│  │  意图识别器    │  │  查询执行器    │  │  结果格式化器  │       │
│  └──────────────┘  └──────────────┘  └──────────────┘       │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐       │
│  │  上下文管理器  │  │  缓存管理器    │  │  安全过滤器    │       │
│  └──────────────┘  └──────────────┘  └──────────────┘       │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                   数据访问层 (Services)                       │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐       │
│  │ 歌曲管理服务   │  │ 二创作品服务   │  │ 直播数据服务   │       │
│  └──────────────┘  └──────────────┘  └──────────────┘       │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐       │
│  │ 图集管理服务   │  │ 数据分析服务   │  │ 搜索服务      │       │
│  └──────────────┘  └──────────────┘  └──────────────┘       │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                      数据存储层                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐       │
│  │   SQLite    │  │    Redis     │  │  文件存储     │       │
│  └──────────────┘  └──────────────┘  └──────────────┘       │
└─────────────────────────────────────────────────────────────┘
```

### 3.2 技术选型

| 组件 | 技术方案 | 说明 |
|------|---------|------|
| **意图识别** | 基于规则的意图识别 + 关键词匹配 | 第一阶段使用规则引擎，后期可接入LLM |
| **查询执行** | Django ORM + 原生SQL | 利用现有ORM框架，复杂查询使用原生SQL |
| **缓存** | Redis | 缓存常用查询结果，提升响应速度 |
| **API框架** | Django REST Framework | 复用现有技术栈 |
| **前端UI** | React + Tailwind CSS | 复用现有技术栈 |

---

## 四、功能模块设计

### 4.1 核心模块

#### 4.1.1 意图识别器 (Intent Recognizer)

**职责**：解析用户自然语言查询，识别查询意图和提取参数

**支持的意图类型**：

| 意图类型 | 说明 | 示例查询 |
|---------|------|---------|
| `song_search` | 歌曲搜索 | "搜索咻咻满唱过的《稻香》" |
| `song_stats` | 歌曲统计 | "2024年唱得最多的5首歌" |
| `record_search` | 演唱记录查询 | "找一下2023年12月25日的演唱记录" |
| `livestream_search` | 直播查询 | "上周有哪些直播？" |
| `fansdiy_search` | 二创作品搜索 | "找找咻咻满相关的二创视频" |
| `gallery_search` | 图集查询 | "2024年的演唱会图片" |
| `analytics_query` | 数据分析 | "粉丝数增长最快的月份" |
| `comparison` | 对比查询 | "对比2023和2024年的演唱次数" |
| `recommendation` | 推荐查询 | "推荐一些古风歌曲" |

**实现方式**：
```python
# agent/intent_recognizer.py

class IntentType(Enum):
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
    def __init__(self, type: IntentType, parameters: dict, confidence: float):
        self.type = type
        self.parameters = parameters
        self.confidence = confidence

class IntentRecognizer:
    """意图识别器"""
    
    def __init__(self):
        self.rules = self._load_rules()
    
    def recognize(self, query: str) -> Intent:
        """识别查询意图"""
        query_lower = query.lower()
        
        # 规则匹配
        for rule in self.rules:
            if rule['pattern'].search(query_lower):
                parameters = self._extract_parameters(query, rule)
                confidence = self._calculate_confidence(query, rule)
                return Intent(rule['intent'], parameters, confidence)
        
        return Intent(IntentType.UNKNOWN, {}, 0.0)
    
    def _load_rules(self) -> list:
        """加载意图识别规则"""
        return [
            {
                'intent': IntentType.SONG_SEARCH,
                'pattern': re.compile(r'(搜索|找|查|查询).*歌|.*《(.+?)》'),
                'parameters': ['song_name', 'keywords']
            },
            {
                'intent': IntentType.SONG_STATS,
                'pattern': re.compile(r'(唱得最多|演唱最多|统计).*歌|(\d{4})年.*歌'),
                'parameters': ['year', 'limit', 'sort_by']
            },
            # ... 更多规则
        ]
    
    def _extract_parameters(self, query: str, rule: dict) -> dict:
        """从查询中提取参数"""
        params = {}
        for param_name in rule['parameters']:
            # 实现参数提取逻辑
            pass
        return params
    
    def _calculate_confidence(self, query: str, rule: dict) -> float:
        """计算置信度"""
        # 基于关键词匹配度计算置信度
        return 0.85
```

#### 4.1.2 查询执行器 (Query Executor)

**职责**：根据识别的意图和参数，调用相应的数据服务执行查询

```python
# agent/query_executor.py

class QueryExecutor:
    """查询执行器"""
    
    def __init__(self):
        self.services = {
            'song': SongService(),
            'record': SongRecordService(),
            'livestream': LivestreamService(),
            'fansdiy': FansDIYService(),
            'gallery': GalleryService(),
            'analytics': AnalyticsService(),
        }
        self.cache = CacheManager()
    
    def execute(self, intent: Intent) -> QueryResult:
        """执行查询"""
        # 检查缓存
        cache_key = self._generate_cache_key(intent)
        cached_result = self.cache.get(cache_key)
        if cached_result:
            return cached_result
        
        # 根据意图类型执行相应查询
        result = None
        try:
            if intent.type == IntentType.SONG_SEARCH:
                result = self._execute_song_search(intent.parameters)
            elif intent.type == IntentType.SONG_STATS:
                result = self._execute_song_stats(intent.parameters)
            elif intent.type == IntentType.RECORD_SEARCH:
                result = self._execute_record_search(intent.parameters)
            # ... 其他意图类型
            
            # 缓存结果
            if result:
                self.cache.set(cache_key, result, timeout=300)
            
            return result
        except Exception as e:
            return QueryResult(success=False, error=str(e))
    
    def _execute_song_search(self, params: dict) -> QueryResult:
        """执行歌曲搜索"""
        song_name = params.get('song_name')
        keywords = params.get('keywords')
        
        songs = self.services['song'].search_songs(
            name=song_name,
            keywords=keywords,
            limit=params.get('limit', 10)
        )
        
        return QueryResult(
            success=True,
            data=songs,
            result_type='song_list'
        )
    
    def _execute_song_stats(self, params: dict) -> QueryResult:
        """执行歌曲统计"""
        year = params.get('year')
        limit = params.get('limit', 5)
        sort_by = params.get('sort_by', 'perform_count')
        
        stats = self.services['song'].get_songs_stats(
            year=year,
            limit=limit,
            sort_by=sort_by
        )
        
        return QueryResult(
            success=True,
            data=stats,
            result_type='stats',
            summary=f"{year}年演唱最多的{limit}首歌"
        )
```

#### 4.1.3 结果格式化器 (Result Formatter)

**职责**：将查询结果格式化为多种输出格式（文本、表格、图表等）

```python
# agent/result_formatter.py

class ResultFormat(Enum):
    TEXT = "text"
    TABLE = "table"
    LIST = "list"
    CHART = "chart"
    IMAGE = "image"

class ResultFormatter:
    """结果格式化器"""
    
    def format(self, result: QueryResult, format: ResultFormat) -> dict:
        """格式化查询结果"""
        if not result.success:
            return self._format_error(result.error)
        
        formatters = {
            ResultFormat.TEXT: self._format_text,
            ResultFormat.TABLE: self._format_table,
            ResultFormat.LIST: self._format_list,
            ResultFormat.CHART: self._format_chart,
            ResultFormat.IMAGE: self._format_image,
        }
        
        formatter = formatters.get(format, self._format_text)
        return formatter(result)
    
    def _format_text(self, result: QueryResult) -> dict:
        """格式化为文本"""
        if result.result_type == 'song_list':
            songs = result.data
            text = f"找到 {len(songs)} 首歌曲：\n"
            for i, song in enumerate(songs, 1):
                text += f"{i}. {song['song_name']} - 演唱{song['perform_count']}次\n"
            return {'type': 'text', 'content': text}
        
        return {'type': 'text', 'content': str(result.data)}
    
    def _format_table(self, result: QueryResult) -> dict:
        """格式化为表格"""
        columns = []
        rows = []
        
        if result.result_type == 'song_list':
            columns = ['歌曲名称', '歌手', '演唱次数', '首次演唱', '最近演唱']
            rows = [
                [
                    song['song_name'],
                    song.get('singer', '-'),
                    song['perform_count'],
                    song.get('first_perform', '-'),
                    song.get('last_performed', '-')
                ]
                for song in result.data
            ]
        
        return {
            'type': 'table',
            'columns': columns,
            'rows': rows,
            'summary': result.summary
        }
    
    def _format_chart(self, result: QueryResult) -> dict:
        """格式化为图表数据"""
        # 返回ECharts等图表库可用的数据格式
        return {
            'type': 'chart',
            'chart_type': 'bar',
            'xAxis': [item['song_name'] for item in result.data],
            'yAxis': [item['perform_count'] for item in result.data],
            'title': result.summary
        }
```

#### 4.1.4 上下文管理器 (Context Manager)

**职责**：管理查询上下文，支持多轮对话

```python
# agent/context_manager.py

class ConversationContext:
    """对话上下文"""
    
    def __init__(self):
        self.history = []
        self.current_entity = None  # 当前关注的实体
        self.temp_data = {}  # 临时数据
    
    def add_message(self, role: str, content: str, result: dict = None):
        """添加消息到历史"""
        self.history.append({
            'role': role,
            'content': content,
            'result': result,
            'timestamp': timezone.now()
        })
    
    def get_recent_entities(self, entity_type: str, limit: int = 5) -> list:
        """获取最近提到的实体"""
        # 从历史记录中提取相关实体
        pass

class ContextManager:
    """上下文管理器"""
    
    def __init__(self):
        self.contexts = {}  # user_id -> ConversationContext
    
    def get_or_create_context(self, user_id: str) -> ConversationContext:
        """获取或创建对话上下文"""
        if user_id not in self.contexts:
            self.contexts[user_id] = ConversationContext()
        return self.contexts[user_id]
    
    def update_context(self, user_id: str, query: str, result: QueryResult):
        """更新对话上下文"""
        context = self.get_or_create_context(user_id)
        context.add_message('user', query, result.to_dict())
        
        # 提取实体并更新当前关注点
        entities = self._extract_entities(result)
        if entities:
            context.current_entity = entities[0]
    
    def _extract_entities(self, result: QueryResult) -> list:
        """从结果中提取实体"""
        entities = []
        if result.result_type == 'song_list' and result.data:
            entities = [song['song_name'] for song in result.data[:3]]
        return entities
```

#### 4.1.5 缓存管理器 (Cache Manager)

**职责**：管理查询结果缓存，提升响应速度

```python
# agent/cache_manager.py

class CacheManager:
    """缓存管理器"""
    
    def __init__(self):
        self.cache = caches['default']
    
    def get(self, key: str) -> Optional[dict]:
        """获取缓存"""
        return self.cache.get(key)
    
    def set(self, key: str, value: dict, timeout: int = 300):
        """设置缓存"""
        self.cache.set(key, value, timeout)
    
    def delete(self, key: str):
        """删除缓存"""
        self.cache.delete(key)
    
    def invalidate_pattern(self, pattern: str):
        """批量删除匹配模式的缓存"""
        keys = self.cache.keys(f'*{pattern}*')
        for key in keys:
            self.cache.delete(key)
```

### 4.2 数据服务层扩展示例

#### 4.2.1 Agent专用查询服务

```python
# agent/services/agent_query_service.py

class AgentQueryService:
    """Agent专用查询服务"""
    
    def __init__(self):
        self.song_repo = SongRepository()
        self.record_repo = SongRecordRepository()
        self.livestream_repo = LivestreamRepository()
    
    def search_songs_with_stats(self, keywords: str = None, year: int = None, 
                                  limit: int = 10) -> list:
        """搜索歌曲并返回统计信息"""
        query = self.song_repo.get_queryset()
        
        if keywords:
            query = query.filter(song_name__icontains=keywords)
        
        songs = query.all()[:limit]
        
        # 为每首歌添加统计信息
        result = []
        for song in songs:
            stats = self.record_repo.get_song_stats(song.id)
            result.append({
                'id': song.id,
                'song_name': song.song_name,
                'singer': song.singer,
                'perform_count': stats['total_count'],
                'first_perform': stats['first_date'],
                'last_performed': stats['last_date'],
                'styles': song.styles,
                'tags': song.tags
            })
        
        return result
    
    def get_livestreams_in_range(self, start_date: date, end_date: date) -> list:
        """获取指定日期范围内的直播记录"""
        return self.livestream_repo.get_by_date_range(start_date, end_date)
    
    def get_fans_growth_analysis(self, account_name: str, start_date: date, 
                                   end_date: date) -> dict:
        """获取粉丝增长分析"""
        # 调用数据分析服务
        pass
    
    def compare_years(self, metric: str, year1: int, year2: int) -> dict:
        """对比两年的数据"""
        if metric == 'perform_count':
            return self._compare_perform_count(year1, year2)
        elif metric == 'livestream_count':
            return self._compare_livestream_count(year1, year2)
        # ... 其他对比维度
    
    def recommend_songs(self, style: str = None, tags: list = None, 
                         limit: int = 10) -> list:
        """推荐歌曲"""
        query = self.song_repo.get_queryset()
        
        if style:
            query = query.filter(song_styles__style__name=style)
        
        if tags:
            query = query.filter(song_tags__tag__name__in=tags)
        
        songs = query.order_by('-perform_count')[:limit]
        
        return [{
            'id': song.id,
            'song_name': song.song_name,
            'perform_count': song.perform_count,
            'cover_url': song.records.first().cover_url if song.records.exists() else None
        } for song in songs]
```

---

## 五、API设计

### 5.1 核心API端点

#### 5.1.1 查询API

```python
# POST /api/agent/query

Request:
{
    "query": "2024年唱得最多的5首歌",
    "user_id": "user_123",  // 可选，用于上下文管理
    "format": "table"  // 可选，默认text
}

Response:
{
    "success": true,
    "intent": {
        "type": "song_stats",
        "parameters": {
            "year": 2024,
            "limit": 5,
            "sort_by": "perform_count"
        },
        "confidence": 0.92
    },
    "result": {
        "type": "table",
        "columns": ["歌曲名称", "演唱次数", "首次演唱", "最近演唱"],
        "rows": [
            ["稻香", 12, "2024-03-15", "2024-12-20"],
            ["青花瓷", 10, "2024-01-08", "2024-11-25"],
            ...
        ],
        "summary": "2024年演唱最多的5首歌"
    },
    "execution_time": 0.15,
    "from_cache": false
}
```

#### 5.1.2 意图测试API

```python
# POST /api/agent/test-intent

Request:
{
    "query": "上周有哪些直播？"
}

Response:
{
    "success": true,
    "intent": {
        "type": "livestream_search",
        "parameters": {
            "time_range": "last_week"
        },
        "confidence": 0.88
    }
}
```

#### 5.1.3 上下文管理API

```python
# GET /api/agent/context?user_id=user_123

Response:
{
    "success": true,
    "context": {
        "history": [
            {
                "role": "user",
                "content": "2024年唱得最多的5首歌",
                "timestamp": "2026-02-03T10:30:00Z"
            },
            {
                "role": "assistant",
                "content": "...",
                "result": {...},
                "timestamp": "2026-02-03T10:30:01Z"
            }
        ],
        "current_entity": "稻香"
    }
}

# DELETE /api/agent/context?user_id=user_123

Response:
{
    "success": true,
    "message": "上下文已清除"
}
```

#### 5.1.4 快捷查询API

```python
# GET /api/agent/quick?category=popular_songs&limit=10

Response:
{
    "success": true,
    "category": "popular_songs",
    "data": [...]
}
```

---

## 六、前端设计

### 6.1 聊天界面组件

```typescript
// AgentChat.tsx

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  result?: QueryResult;
  timestamp: Date;
}

interface QueryResult {
  type: 'text' | 'table' | 'list' | 'chart' | 'image';
  content?: string;
  columns?: string[];
  rows?: any[][];
  summary?: string;
}

const AgentChat: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);

  const sendMessage = async () => {
    if (!input.trim()) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: input,
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setLoading(true);

    try {
      const response = await fetch('/api/agent/query', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: input })
      });

      const data = await response.json();

      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: data.result.summary || '查询完成',
        result: data.result,
        timestamp: new Date()
      };

      setMessages(prev => [...prev, assistantMessage]);
    } catch (error) {
      console.error('查询失败:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="agent-chat-container">
      <div className="messages-container">
        {messages.map(message => (
          <MessageBubble key={message.id} message={message} />
        ))}
        {loading && <LoadingBubble />}
      </div>
      
      <div className="input-container">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
          placeholder="问我任何关于咻咻满的问题..."
          className="chat-input"
        />
        <button onClick={sendMessage} className="send-button">
          <Send />
        </button>
      </div>
    </div>
  );
};
```

### 6.2 结果展示组件

```typescript
// ResultDisplay.tsx

interface ResultDisplayProps {
  result: QueryResult;
}

const ResultDisplay: React.FC<ResultDisplayProps> = ({ result }) => {
  switch (result.type) {
    case 'text':
      return <TextResult content={result.content} />;
    case 'table':
      return <TableResult columns={result.columns} rows={result.rows} />;
    case 'list':
      return <ListResult items={result.items} />;
    case 'chart':
      return <ChartResult data={result.chartData} />;
    case 'image':
      return <ImageResult images={result.images} />;
    default:
      return <div>未知的结果类型</div>;
  }
};

const TableResult: React.FC<{ columns: string[]; rows: any[][] }> = ({ columns, rows }) => (
  <div className="table-result">
    <table className="data-table">
      <thead>
        <tr>
          {columns.map(col => <th key={col}>{col}</th>)}
        </tr>
      </thead>
      <tbody>
        {rows.map((row, i) => (
          <tr key={i}>
            {row.map((cell, j) => <td key={j}>{cell}</td>)}
          </tr>
        ))}
      </tbody>
    </table>
  </div>
);
```

### 6.3 快捷查询建议

```typescript
// QuickSuggestions.tsx

const SUGGESTIONS = [
  { icon: Mic, text: '最近演唱的歌曲', query: '最近演唱的歌曲' },
  { icon: Calendar, text: '本周直播', query: '本周有哪些直播' },
  { icon: TrendingUp, text: '热门歌曲', query: '演唱最多的10首歌' },
  { icon: Image, text: '最新图集', query: '最新的图集' },
  { icon: Video, text: '二创作品', query: '最新的二创作品' },
  { icon: BarChart, text: '粉丝增长', query: '粉丝数增长情况' },
];

const QuickSuggestions: React.FC = () => (
  <div className="quick-suggestions">
    {SUGGESTIONS.map(s => (
      <button 
        key={s.text}
        onClick={() => handleQuery(s.query)}
        className="suggestion-chip"
      >
        <s.icon size={16} />
        <span>{s.text}</span>
      </button>
    ))}
  </div>
);
```

---

## 七、数据库设计

### 7.1 新增数据表

#### 7.1.1 查询历史表

```python
# agent/models/query_history.py

class QueryHistory(models.Model):
    """查询历史记录"""
    user_id = models.CharField(max_length=100, verbose_name="用户ID")
    query = models.TextField(verbose_name="查询内容")
    intent_type = models.CharField(max_length=50, verbose_name="意图类型")
    parameters = models.JSONField(default=dict, verbose_name="参数")
    result = models.JSONField(default=dict, verbose_name="查询结果")
    execution_time = models.FloatField(verbose_name="执行时间(秒)")
    from_cache = models.BooleanField(default=False, verbose_name="是否来自缓存")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="查询时间")
    
    class Meta:
        db_table = 'agent_query_history'
        verbose_name = "查询历史"
        verbose_name_plural = "查询历史"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user_id', '-created_at']),
            models.Index(fields=['intent_type']),
        ]
```

#### 7.1.2 查询统计表

```python
# agent/models/query_stats.py

class QueryStats(models.Model):
    """查询统计"""
    date = models.DateField(verbose_name="日期")
    intent_type = models.CharField(max_length=50, verbose_name="意图类型")
    query_count = models.IntegerField(default=0, verbose_name="查询次数")
    avg_execution_time = models.FloatField(verbose_name="平均执行时间")
    cache_hit_rate = models.FloatField(verbose_name="缓存命中率")
    
    class Meta:
        db_table = 'agent_query_stats'
        verbose_name = "查询统计"
        verbose_name_plural = "查询统计"
        unique_together = ('date', 'intent_type')
        ordering = ['-date', '-query_count']
```

---

## 八、实施计划

### 8.1 阶段划分

#### 第一阶段：核心功能开发（2周）

**任务**：
1. 创建 `agent` Django应用
2. 实现意图识别器（基于规则）
3. 实现查询执行器
4. 实现结果格式化器
5. 创建核心API端点
6. 编写单元测试

**交付物**：
- Agent核心模块代码
- REST API文档
- 单元测试覆盖

#### 第二阶段：数据服务扩展（1周）

**任务**：
1. 创建Agent专用查询服务
2. 扩展现有Service层以支持Agent查询
3. 实现缓存机制
4. 性能优化

**交付物**：
- 数据服务层代码
- 性能测试报告

#### 第三阶段：前端开发（2周）

**任务**：
1. 创建聊天界面组件
2. 实现结果展示组件
3. 实现快捷查询建议
4. 响应式设计和样式优化
5. 前端测试

**交付物**：
- 前端组件代码
- UI/UX设计文档

#### 第四阶段：集成测试与优化（1周）

**任务**：
1. 端到端测试
2. 性能测试和优化
3. 用户体验优化
4. 文档完善

**交付物**：
- 测试报告
- 用户使用文档
- API文档更新

### 8.2 里程碑

| 里程碑 | 时间 | 交付内容 |
|-------|------|---------|
| M1 | 第2周 | 核心API可用 |
| M2 | 第3周 | 数据服务完成 |
| M3 | 第5周 | 前端界面完成 |
| M4 | 第6周 | 系统上线 |

---

## 九、安全与权限

### 9.1 安全措施

1. **查询过滤**：过滤SQL注入、XSS等恶意查询
2. **权限控制**：基于Django用户系统的权限管理
3. **速率限制**：防止API滥用
4. **敏感数据保护**：不返回敏感的个人信息

```python
# agent/security/query_filter.py

class QueryFilter:
    """查询过滤器"""
    
    SQL_INJECTION_PATTERNS = [
        r';.*drop',
        r';.*delete',
        r';.*insert',
        r';.*update',
        r'<script>',
        r'on\w+\s*=',
    ]
    
    @classmethod
    def is_safe(cls, query: str) -> tuple[bool, str]:
        """检查查询是否安全"""
        query_lower = query.lower()
        
        for pattern in cls.SQL_INJECTION_PATTERNS:
            if re.search(pattern, query_lower):
                return False, "查询包含非法字符"
        
        return True, ""
    
    @classmethod
    def sanitize_query(cls, query: str) -> str:
        """清理查询"""
        # 移除潜在的恶意字符
        sanitized = re.sub(r'[<>;]', '', query)
        return sanitized.strip()
```

### 9.2 速率限制

```python
# agent/middleware/rate_limit.py

class RateLimitMiddleware:
    """速率限制中间件"""
    
    def __init__(self, get_response):
        self.get_response = get_response
        self.cache = caches['default']
    
    def __call__(self, request):
        if request.path.startswith('/api/agent/'):
            user_id = self._get_user_id(request)
            key = f'ratelimit:{user_id}'
            
            count = self.cache.get(key, 0)
            if count >= 30:  # 每分钟最多30次查询
                return JsonResponse({
                    'error': '查询过于频繁，请稍后再试'
                }, status=429)
            
            self.cache.set(key, count + 1, timeout=60)
        
        return self.get_response(request)
```

---

## 十、监控与日志

### 10.1 查询监控

```python
# agent/monitoring/query_monitor.py

class QueryMonitor:
    """查询监控器"""
    
    @staticmethod
    def log_query(intent: Intent, result: QueryResult, execution_time: float):
        """记录查询日志"""
        logger.info(f"Query: {intent.type}, Time: {execution_time}s, Success: {result.success}")
        
        # 更新统计数据
        QueryStats.objects.update_or_create(
            date=timezone.now().date(),
            intent_type=intent.type.value,
            defaults={
                'query_count': F('query_count') + 1,
                'avg_execution_time': execution_time
            }
        )
```

### 10.2 性能指标

监控以下关键指标：
- 平均查询响应时间
- 缓存命中率
- 意图识别准确率
- API调用频率
- 错误率

---

## 十一、未来扩展

### 11.1 LLM集成

在第二阶段可以接入LLM（如OpenAI API、通义千问等）提升意图识别和自然语言理解能力：

```python
# agent/intent_recognizer/llm_recognizer.py

class LLMIntentRecognizer:
    """基于LLM的意图识别器"""
    
    def __init__(self, api_key: str):
        self.client = OpenAI(api_key=api_key)
    
    def recognize(self, query: str) -> Intent:
        """使用LLM识别意图"""
        prompt = f"""
        分析以下用户查询，识别查询意图和提取参数。
        
        支持的意图类型：
        - song_search: 歌曲搜索
        - song_stats: 歌曲统计
        - record_search: 演唱记录查询
        - livestream_search: 直播查询
        - fansdiy_search: 二创作品搜索
        - gallery_search: 图集查询
        - analytics_query: 数据分析
        - comparison: 对比查询
        - recommendation: 推荐查询
        
        用户查询：{query}
        
        请以JSON格式返回：
        {{
            "intent_type": "...",
            "parameters": {{...}},
            "confidence": 0.95
        }}
        """
        
        response = self.client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}]
        )
        
        result = json.loads(response.choices[0].message.content)
        return Intent(
            type=IntentType(result['intent_type']),
            parameters=result['parameters'],
            confidence=result['confidence']
        )
```

### 11.2 语音查询

集成语音识别API，支持语音输入查询。

### 11.3 个性化推荐

基于用户查询历史和偏好，提供个性化推荐。

---

## 十二、项目结构

```
repo/xxm_fans_backend/
├── agent/                          # Agent子系统
│   ├── __init__.py
│   ├── apps.py
│   ├── models/                      # 数据模型
│   │   ├── __init__.py
│   │   ├── query_history.py
│   │   └── query_stats.py
│   ├── intent_recognizer/           # 意图识别
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── rule_based.py            # 基于规则
│   │   └── llm_based.py             # 基于LLM（扩展）
│   ├── query_executor.py            # 查询执行器
│   ├── result_formatter.py          # 结果格式化器
│   ├── context_manager.py           # 上下文管理器
│   ├── cache_manager.py             # 缓存管理器
│   ├── services/                    # Agent专用服务
│   │   ├── __init__.py
│   │   └── agent_query_service.py
│   ├── security/                    # 安全模块
│   │   ├── __init__.py
│   │   └── query_filter.py
│   ├── middleware/                  # 中间件
│   │   ├── __init__.py
│   │   └── rate_limit.py
│   ├── monitoring/                  # 监控模块
│   │   ├── __init__.py
│   │   └── query_monitor.py
│   ├── api/                         # API视图
│   │   ├── __init__.py
│   │   └── agent_api.py
│   ├── urls.py
│   └── tests/                       # 测试
│       ├── __init__.py
│       ├── test_intent_recognizer.py
│       └── test_query_executor.py

repo/xxm_fans_frontend/
├── presentation/
│   └── components/
│       └── features/
│           └── agent/               # Agent前端组件
│               ├── AgentChat.tsx
│               ├── MessageBubble.tsx
│               ├── ResultDisplay.tsx
│               ├── TableResult.tsx
│               ├── ChartResult.tsx
│               └── QuickSuggestions.tsx
```

---

## 十三、总结

本方案设计了一个完整、可扩展的Agent智能查询子系统，具有以下特点：

1. **模块化设计**：各模块职责清晰，易于维护和扩展
2. **渐进式开发**：可分阶段实施，快速交付价值
3. **性能优化**：通过缓存、索引等手段保证查询性能
4. **用户体验**：友好的聊天界面和多样化的结果展示
5. **安全可靠**：完善的安全措施和权限控制
6. **可扩展性**：预留LLM集成等扩展空间

通过该子系统，粉丝们可以通过自然语言灵活查询各种数据，满足个性化需求，大大提升网站的互动性和用户满意度。