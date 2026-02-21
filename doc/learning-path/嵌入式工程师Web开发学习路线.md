# 嵌入式工程师 Web 开发学习路线

> 基于「小满虫之家」(XXM Fans Home) 项目源码的实战学习指南

---

## 前言

### 写给嵌入式工程师

作为一名嵌入式工程师，你已经具备：
- ✅ 扎实的 C/C++ 编程基础
- ✅ 对计算机系统底层原理的理解
- ✅ Linux 系统操作经验
- ✅ 调试和解决问题的能力

这些基础将帮助你快速掌握 Web 开发。本路线将利用你的现有知识，通过「小满虫之家」项目的实际源码，带你系统学习现代 Web 开发技术栈。

### 学习理念

```
┌─────────────────────────────────────────────────────────────────┐
│                    嵌入式 → Web 思维转换                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  嵌入式开发                Web 开发                             │
│  ─────────────           ───────────                            │
│                                                                 │
│  单片机/处理器    ──────▶  服务器 (Django)                       │
│  ├─ 处理请求             ├─ 处理 HTTP 请求                       │
│  ├─ 管理内存             ├─ 管理数据库连接                       │
│  └─ 硬件中断             └─ URL 路由分发                         │
│                                                                 │
│  固件程序        ──────▶   前端应用 (React)                      │
│  ├─ 主循环               ├─ 组件生命周期                         │
│  ├─ 事件处理             ├─ 事件监听                             │
│  ├─ 状态机               ├─ 状态管理 (useState)                  │
│  └─ 显示刷新             └─ 虚拟 DOM 更新                        │
│                                                                 │
│  通信协议        ──────▶   API 接口 (REST)                       │
│  ├─ SPI/I2C/UART         ├─ HTTP/HTTPS                          │
│  ├─ 数据帧格式           ├─ JSON 数据格式                        │
│  └─ 主从模式             └─ 客户端-服务器模式                    │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 第一阶段：Python 与后端基础（2-3 周）

### 第 1 周：Python 快速入门

#### 学习目标
掌握 Python 基础语法，理解 Pythonic 编程风格。

#### 学习资源
- 📚 [Python 官方教程](https://docs.python.org/zh-cn/3/tutorial/)（第 1-9 章）
- 🎬 [廖雪峰 Python 教程](https://www.liaoxuefeng.com/wiki/1016959663602400)

#### 嵌入式工程师重点关注

```python
# Python vs C 对比学习

# 1. 变量定义 - 无需类型声明，类似脚本语言
# C: int count = 0;
count = 0  # Python

# 2. 列表 vs 数组
# C: int arr[] = {1, 2, 3};
arr = [1, 2, 3]  # Python 列表，动态扩容

# 3. 字典 vs 结构体
# C: struct Person { char* name; int age; };
person = {"name": "XXM", "age": 25}  # Python 字典

# 4. 函数定义
# C: int add(int a, int b) { return a + b; }
def add(a, b):  # Python，类型可选
    return a + b

# 5. 类定义 - 类似 C++，但更简洁
# C++: class Song { private: string name; public: void play(); };
class Song:
    def __init__(self, name):  # 构造函数
        self.name = name       # self 类似 this
    
    def play(self):
        print(f"Playing: {self.name}")

# 6. 列表推导式 - Python 特有，高效简洁
# C: 需要 for 循环
# Python: 一行代码
squares = [x**2 for x in range(10)]
```

#### 实战练习
```python
# 练习 1：实现歌曲信息解析（参考项目中的 Song 模型）
# 目标：将字符串 " song_name | singer | perform_count " 解析为字典

def parse_song_info(song_str):
    """
    输入: "告白气球 | 周杰伦 | 5"
    输出: {"name": "告白气球", "singer": "周杰伦", "count": 5}
    """
    parts = song_str.split("|")
    return {
        "name": parts[0].strip(),
        "singer": parts[1].strip(),
        "count": int(parts[2].strip())
    }

# 练习 2：歌曲列表排序（参考项目中的排序功能）
songs = [
    {"name": "歌1", "perform_count": 3},
    {"name": "歌2", "perform_count": 10},
    {"name": "歌3", "perform_count": 1},
]
# 按演唱次数降序排序
sorted_songs = sorted(songs, key=lambda x: x["perform_count"], reverse=True)
```

### 第 2 周：Django 基础

#### 学习目标
理解 Django 的 MTV 架构，能够创建简单的模型和视图。

#### 核心概念对照

```
┌─────────────────────────────────────────────────────────────────┐
│                 Django  vs  嵌入式系统                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Django 概念          嵌入式类比                                 │
│  ───────────          ──────────                                 │
│                                                                 │
│  Model (模型)    ──▶  数据结构定义                               │
│  ├─ 定义数据表         ├─ 定义结构体                              │
│  ├─ ORM 操作           ├─ 内存操作                                │
│  └─ 类似 SQL 的查询    └─ 类似寄存器访问                          │
│                                                                 │
│  View (视图)     ──▶  中断服务程序                               │
│  ├─ 处理 HTTP 请求     ├─ 处理中断请求                            │
│  ├─ 调用 Model 查询    ├─ 读取传感器数据                          │
│  └─ 返回 HTTP 响应     └─ 执行相应操作                            │
│                                                                 │
│  Template (模板) ──▶  UI 显示逻辑                                │
│  ├─ 渲染 HTML          ├─ 刷新显示屏                              │
│  └─ 动态数据插入       └─ 更新显示缓冲区                          │
│                                                                 │
│  URLConf (路由)  ──▶  中断向量表                                 │
│  ├─ URL → View 映射    ├─ 中断源 → 处理函数                       │
│  └─ 请求分发            └─ 中断分发                               │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

#### 实战：创建一个简单的歌曲管理应用

```python
# 步骤 1：创建项目（类似创建嵌入式工程）
# $ django-admin startproject mymusic
# $ cd mymusic
# $ python manage.py startapp songs

# 步骤 2：定义模型（类似定义数据结构）
# songs/models.py
from django.db import models

class Song(models.Model):
    """
    类比 C 结构体：
    struct Song {
        char song_name[200];
        char singer[200];
        int perform_count;
    };
    """
    song_name = models.CharField(max_length=200)
    singer = models.CharField(max_length=200)
    perform_count = models.IntegerField(default=0)
    
    class Meta:
        db_table = 'songs'
        ordering = ['song_name']
    
    def __str__(self):
        return f"{self.song_name} - {self.singer}"

# 步骤 3：创建视图（类似中断处理函数）
# songs/views.py
from django.http import JsonResponse
from .models import Song

def song_list(request):
    """
    类比中断处理：
    void handle_get_songs_request(Request* req, Response* resp) {
        Song* songs = db_query_all();
        resp->write_json(songs);
    }
    """
    songs = Song.objects.all()  # 类似 SELECT * FROM songs
    data = [{
        'id': song.id,
        'name': song.song_name,
        'singer': song.singer,
        'count': song.perform_count
    } for song in songs]
    return JsonResponse({'songs': data})

def song_detail(request, song_id):
    """获取单个歌曲详情"""
    try:
        song = Song.objects.get(id=song_id)
        return JsonResponse({
            'id': song.id,
            'name': song.song_name,
            'singer': song.singer,
            'count': song.perform_count
        })
    except Song.DoesNotExist:
        return JsonResponse({'error': 'Song not found'}, status=404)

# 步骤 4：配置路由（类似中断向量表）
# songs/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('songs/', views.song_list, name='song_list'),
    path('songs/<int:song_id>/', views.song_detail, name='song_detail'),
]
```

#### 阅读项目源码
```
阅读任务：
1. 查看 repo/xxm_fans_backend/song_management/models/song.py
   - 理解 Song 和 SongRecord 的关系
   - 注意 Meta 配置和索引设计

2. 查看 repo/xxm_fans_backend/song_management/api/song_views.py
   - 理解类视图和函数视图的区别
   - 学习如何使用序列化器

3. 查看 repo/xxm_fans_backend/xxm_fans_home/urls.py
   - 理解 URL 路由配置
   - 注意 include() 的用法
```

### 第 3 周：Django REST Framework

#### 学习目标
掌握 RESTful API 开发，理解序列化器和视图集。

#### 核心概念

```python
# REST Framework vs 原始 Django

# 原始 Django（类似裸机编程）
def song_list(request):
    songs = Song.objects.all()
    data = [{'id': s.id, 'name': s.song_name} for s in songs]
    return JsonResponse(data, safe=False)

# DRF（类似使用 HAL 库）
from rest_framework import serializers, viewsets

class SongSerializer(serializers.ModelSerializer):
    """序列化器 - 类似数据打包/解包"""
    class Meta:
        model = Song
        fields = ['id', 'song_name', 'singer', 'perform_count']

class SongViewSet(viewsets.ModelViewSet):
    """
    视图集 - 自动提供 CRUD 操作
    类似：一套中断处理函数处理多种请求
    """
    queryset = Song.objects.all()
    serializer_class = SongSerializer
```

#### 实战练习
```python
# 练习：为 SongRecord 创建完整的 REST API
# 参考项目中的 song_management/api/record_views.py

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

@api_view(['GET', 'POST'])
def song_record_list(request, song_id):
    """
    GET: 获取歌曲的所有演唱记录
    POST: 添加新的演唱记录
    """
    if request.method == 'GET':
        records = SongRecord.objects.filter(song_id=song_id)
        serializer = SongRecordSerializer(records, many=True)
        return Response(serializer.data)
    
    elif request.method == 'POST':
        serializer = SongRecordSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(song_id=song_id)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
```

#### 阅读项目源码
```
阅读任务：
1. repo/xxm_fans_backend/song_management/api/serializers.py
   - 理解 ModelSerializer 的用法
   - 注意嵌套序列化器（SongWithRecordsSerializer）

2. repo/xxm_fans_backend/song_management/api/views.py
   - 理解视图集的路由自动生成
   - 学习如何自定义查询

3. repo/xxm_fans_backend/core/responses.py
   - 理解统一响应格式的封装
```

---

## 第二阶段：数据库与 ORM（1-2 周）

### 第 4 周：数据库基础与 Django ORM

#### 学习目标
理解关系型数据库概念，熟练使用 Django ORM。

#### 嵌入式工程师视角

```
┌─────────────────────────────────────────────────────────────────┐
│                  数据库 vs 嵌入式存储                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  数据库              嵌入式类比                                  │
│  ───────             ──────────                                  │
│                                                                 │
│  数据库(Database)    闪存/存储芯片                               │
│  表(Table)           结构化数据区域                              │
│  行(Row)             一个数据记录                                │
│  列(Column)          数据字段                                    │
│  主键(Primary Key)   唯一标识符（如设备 ID）                     │
│  外键(Foreign Key)   指针/引用                                   │
│  索引(Index)         查找表（加速查询）                          │
│  SQL                 操作存储的指令集                            │
│  ORM                 硬件抽象层（HAL）                           │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

#### Django ORM 实战

```python
# ORM 操作 vs SQL

# 查询所有歌曲
# SQL: SELECT * FROM songs;
Song.objects.all()

# 条件查询
# SQL: SELECT * FROM songs WHERE perform_count > 5;
Song.objects.filter(perform_count__gt=5)

# 多条件查询
# SQL: SELECT * FROM songs WHERE singer='XXM' AND perform_count > 0;
Song.objects.filter(singer='XXM', perform_count__gt=0)

# 关联查询（JOIN）
# SQL: SELECT * FROM song_records JOIN songs ON ...
SongRecord.objects.select_related('song').all()

# 聚合查询
# SQL: SELECT COUNT(*), AVG(perform_count) FROM songs;
from django.db.models import Count, Avg
Song.objects.aggregate(
    total=Count('id'),
    avg_count=Avg('perform_count')
)

# 批量操作（类似 DMA）
# 比循环单条操作效率高得多
Song.objects.bulk_create([
    Song(song_name='歌1', singer='A'),
    Song(song_name='歌2', singer='B'),
])
```

#### 阅读项目源码
```
阅读任务：
1. repo/xxm_fans_backend/song_management/models/
   - 理解模型之间的关系（ForeignKey）
   - 注意 related_name 的用法

2. repo/xxm_fans_backend/gallery/models.py
   - 理解自引用外键（多级分类）
   - 学习模型方法的定义

3. repo/xxm_fans_backend/data_analytics/models/
   - 理解索引设计（Meta.indexes）
   - 注意唯一约束（unique_together）
```

---

## 第三阶段：前端基础（3-4 周）

### 第 5 周：HTML/CSS/JavaScript 基础

#### 学习目标
掌握 Web 前端三件套，理解 DOM 操作。

#### 嵌入式工程师视角

```
┌─────────────────────────────────────────────────────────────────┐
│                  Web 前端 vs 嵌入式 UI                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  HTML          ──▶  界面布局描述（类似界面配置文件）             │
│  CSS           ──▶  样式/主题（类似 UI 皮肤）                    │
│  JavaScript    ──▶  交互逻辑（类似事件处理程序）                 │
│  DOM           ──▶  界面元素树（类似控件树）                     │
│                                                                 │
│  类比 LVGL（嵌入式 GUI 库）：                                    │
│  - HTML ≈ lv_obj_create() 创建控件                              │
│  - CSS  ≈ lv_style 设置样式                                     │
│  - JS   ≈ lv_event 处理事件                                     │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

#### 快速入门示例

```html
<!-- index.html - 类似界面布局文件 -->
<!DOCTYPE html>
<html>
<head>
    <style>
        /* CSS - 类似样式配置 */
        .song-card {
            border: 1px solid #ddd;
            padding: 16px;
            margin: 8px;
            border-radius: 8px;
        }
        .song-title {
            font-size: 18px;
            font-weight: bold;
        }
    </style>
</head>
<body>
    <div id="song-list">
        <!-- 动态内容插入区域 -->
    </div>
    
    <script>
        // JavaScript - 类似主程序
        const songs = [
            {name: '歌1', singer: 'A'},
            {name: '歌2', singer: 'B'},
        ];
        
        // 类似渲染界面
        const container = document.getElementById('song-list');
        songs.forEach(song => {
            const card = document.createElement('div');
            card.className = 'song-card';
            card.innerHTML = `
                <div class="song-title">${song.name}</div>
                <div>${song.singer}</div>
            `;
            container.appendChild(card);
        });
    </script>
</body>
</html>
```

### 第 6-7 周：TypeScript + React 基础

#### 学习目标
掌握 TypeScript 类型系统，理解 React 组件化开发。

#### TypeScript 快速入门

```typescript
// TypeScript vs C 类型系统

// 基础类型
let count: number = 0;        // 类似 int
let name: string = "XXM";     // 类似 char[]
let isActive: boolean = true; // 类似 bool

// 接口 - 类似结构体定义
// C: struct Song { char* name; int count; };
interface Song {
    name: string;
    singer?: string;  // ? 表示可选，类似可选字段
    performCount: number;
}

// 使用接口
const song: Song = {
    name: "告白气球",
    singer: "周杰伦",
    performCount: 5
};

// 函数类型
// C: int add(int a, int b);
function add(a: number, b: number): number {
    return a + b;
}

// 泛型 - 类似 C 模板
// C++: template<T> T getMax(T a, T b);
function getMax<T>(a: T, b: T): T {
    return a > b ? a : b;
}
```

#### React 核心概念

```tsx
// React 组件 - 类似可复用的 UI 模块

import React, { useState, useEffect } from 'react';

// 函数组件 - 现代 React 推荐方式
interface SongCardProps {
    song: Song;
    onPlay: (song: Song) => void;
}

// 类似：void render_song_card(Song song, void (*on_play)(Song))
const SongCard: React.FC<SongCardProps> = ({ song, onPlay }) => {
    // useState - 类似状态变量
    // const [state, setState] = useState(initialValue);
    const [isExpanded, setIsExpanded] = useState(false);
    
    // useEffect - 类似初始化/析构处理
    // 组件挂载/更新/卸载时执行
    useEffect(() => {
        console.log(`Song ${song.name} mounted`);
        return () => {
            console.log(`Song ${song.name} unmounted`);
        };
    }, [song.name]);  // 依赖数组，类似触发条件
    
    return (
        <div className="song-card">
            <h3>{song.name}</h3>
            <p>{song.singer}</p>
            <button onClick={() => onPlay(song)}>
                播放
            </button>
            <button onClick={() => setIsExpanded(!isExpanded)}>
                {isExpanded ? '收起' : '展开'}
            </button>
            {isExpanded && (
                <div>演唱次数: {song.performCount}</div>
            )}
        </div>
    );
};

// 列表渲染
interface SongListProps {
    songs: Song[];
}

const SongList: React.FC<SongListProps> = ({ songs }) => {
    const handlePlay = (song: Song) => {
        console.log(`Playing: ${song.name}`);
    };
    
    return (
        <div className="song-list">
            {songs.map(song => (
                <SongCard 
                    key={song.name}  // 类似唯一标识
                    song={song} 
                    onPlay={handlePlay}
                />
            ))}
        </div>
    );
};
```

#### 实战练习
```tsx
// 练习：实现一个简单的歌曲列表组件
// 参考项目中的 presentation/components/features/SongTable.tsx

import React, { useState } from 'react';

interface Song {
    id: string;
    name: string;
    singer: string;
    performCount: number;
}

const SongTable: React.FC = () => {
    const [songs, setSongs] = useState<Song[]>([]);
    const [loading, setLoading] = useState(false);
    
    // 模拟加载数据
    const loadSongs = async () => {
        setLoading(true);
        // 实际项目中这里调用 API
        // const data = await songService.getSongs();
        setSongs([
            { id: '1', name: '歌1', singer: 'A', performCount: 5 },
            { id: '2', name: '歌2', singer: 'B', performCount: 3 },
        ]);
        setLoading(false);
    };
    
    if (loading) return <div>加载中...</div>;
    
    return (
        <table>
            <thead>
                <tr>
                    <th>歌曲名</th>
                    <th>歌手</th>
                    <th>演唱次数</th>
                </tr>
            </thead>
            <tbody>
                {songs.map(song => (
                    <tr key={song.id}>
                        <td>{song.name}</td>
                        <td>{song.singer}</td>
                        <td>{song.performCount}</td>
                    </tr>
                ))}
            </tbody>
        </table>
    );
};
```

### 第 8 周：现代前端工具链

#### 学习目标
掌握 Vite、Tailwind CSS、React Router。

#### Vite（构建工具）
```bash
# 类似 Makefile 或 CMake，但专为前端设计

# 创建项目
npm create vite@latest my-app -- --template react-ts

# 开发模式（热重载）
npm run dev

# 生产构建（优化、压缩）
npm run build
```

#### Tailwind CSS（原子化 CSS）
```tsx
// 传统 CSS：需要写样式类
// <div className="song-card">

// Tailwind：直接使用工具类
// 类似内联样式，但更高效、可复用
<div className="p-4 m-2 bg-white rounded-lg shadow-md hover:shadow-lg transition-shadow">
    <h3 className="text-lg font-bold text-gray-800">{song.name}</h3>
    <p className="text-sm text-gray-600">{song.singer}</p>
</div>

// 常用类对照：
// p-4      → padding: 1rem
// m-2      → margin: 0.5rem
// bg-white → background-color: white
// rounded-lg → border-radius: 0.5rem
// text-lg  → font-size: 1.125rem
// hover:shadow-lg → 鼠标悬停时阴影增大
```

#### React Router（路由管理）
```tsx
// 类似嵌入式中的状态机切换

import { BrowserRouter, Routes, Route, Link } from 'react-router-dom';

const App: React.FC = () => {
    return (
        <BrowserRouter>
            <nav>
                <Link to="/">首页</Link>
                <Link to="/songs">歌曲</Link>
                <Link to="/gallery">图集</Link>
            </nav>
            
            <Routes>
                <Route path="/" element={<HomePage />} />
                <Route path="/songs" element={<SongsPage />} />
                <Route path="/gallery" element={<GalleryPage />} />
            </Routes>
        </BrowserRouter>
    );
};
```

#### 阅读项目源码
```
阅读任务：
1. repo/xxm_fans_frontend/App.tsx
   - 理解路由配置
   - 注意 React.lazy 和代码分割

2. repo/xxm_fans_frontend/presentation/pages/HomePage.tsx
   - 理解页面组件结构
   - 学习如何使用自定义 hooks

3. repo/xxm_fans_frontend/presentation/components/features/SongTable.tsx
   - 理解组件的状态管理
   - 注意事件处理
```

---

## 第四阶段：前后端联调（1-2 周）

### 第 9 周：HTTP API 与数据获取

#### 学习目标
掌握 HTTP 协议，理解 RESTful API 调用。

#### 嵌入式工程师视角

```
┌─────────────────────────────────────────────────────────────────┐
│                   HTTP  vs  嵌入式通信                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  HTTP 请求       ──▶  类似带有标准格式的命令帧                    │
│  ├─ GET          ──▶  读取寄存器/数据                             │
│  ├─ POST         ──▶  写入数据/执行操作                           │
│  ├─ PUT          ──▶  更新数据                                    │
│  └─ DELETE       ──▶  删除数据                                    │
│                                                                 │
│  HTTP 响应状态码  ──▶  类似返回码                                  │
│  ├─ 200 OK       ──▶  操作成功                                    │
│  ├─ 404 Not Found ──▶ 地址/资源不存在                             │
│  ├─ 500 Error    ──▶  内部错误                                    │
│  └─ 401/403      ──▶  权限错误                                    │
│                                                                 │
│  JSON            ──▶  类似结构化的二进制协议                       │
│  Header          ──▶  类似帧头，包含元信息                         │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

#### SWR 数据获取

```tsx
// SWR - 类似带缓存的读取机制

import useSWR from 'swr';

// 数据获取函数
const fetcher = (url: string) => fetch(url).then(res => res.json());

const SongList: React.FC = () => {
    // useSWR(key, fetcher, options)
    // 类似：带缓存的传感器读取
    const { data, error, isLoading } = useSWR(
        '/api/songs/',  // 请求的 key
        fetcher,         // 数据获取函数
        {
            refreshInterval: 5000,      // 自动刷新间隔
            revalidateOnFocus: false,   // 窗口聚焦时不重新验证
        }
    );
    
    if (isLoading) return <div>加载中...</div>;
    if (error) return <div>加载失败</div>;
    
    return (
        <ul>
            {data?.results.map((song: Song) => (
                <li key={song.id}>{song.name}</li>
            ))}
        </ul>
    );
};
```

#### 阅读项目源码
```
阅读任务：
1. repo/xxm_fans_frontend/infrastructure/api/RealSongService.ts
   - 理解 API 客户端封装
   - 注意错误处理和数据转换

2. repo/xxm_fans_frontend/infrastructure/hooks/useData.ts
   - 理解 SWR 的封装使用
   - 学习如何处理分页数据

3. repo/xxm_fans_frontend/domain/types.ts
   - 理解领域模型类型定义
   - 注意前后端数据结构的对应关系
```

### 第 10 周：整合实战

#### 实战项目：实现一个完整的歌曲详情页面

```tsx
// pages/SongDetailPage.tsx

import React from 'react';
import { useParams } from 'react-router-dom';
import useSWR from 'swr';
import { Song, SongRecord } from '../domain/types';

const SongDetailPage: React.FC = () => {
    const { songId } = useParams<{ songId: string }>();
    
    // 获取歌曲详情
    const { data: song, error: songError } = useSWR<Song>(
        songId ? `/api/songs/${songId}/` : null
    );
    
    // 获取演唱记录
    const { data: records, error: recordsError } = useSWR<{results: SongRecord[]}>(
        songId ? `/api/songs/${songId}/records/` : null
    );
    
    if (songError) return <div>歌曲加载失败</div>;
    if (!song) return <div>加载中...</div>;
    
    return (
        <div className="container mx-auto p-4">
            <h1 className="text-2xl font-bold">{song.name}</h1>
            <p className="text-gray-600">{song.originalArtist}</p>
            <p>演唱次数: {song.performanceCount}</p>
            
            <h2 className="text-xl font-bold mt-6">演唱记录</h2>
            {records?.results.map(record => (
                <div key={record.id} className="border p-2 mt-2 rounded">
                    <p>{record.date}</p>
                    <a href={record.videoUrl} target="_blank">观看视频</a>
                </div>
            ))}
        </div>
    );
};
```

---

## 第五阶段：部署与运维（1-2 周）

### 第 11 周：Linux 服务器部署

#### 学习目标
掌握 Nginx、Gunicorn 配置，理解生产环境部署。

#### 部署架构

```
┌─────────────────────────────────────────────────────────────────┐
│                      生产部署架构                                │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   用户请求                                                       │
│      │                                                          │
│      ▼                                                          │
│   ┌─────────────┐                                               │
│   │    Nginx    │  ◀── 反向代理，静态文件服务（类似网关）        │
│   │   (80/443)  │                                               │
│   └──────┬──────┘                                               │
│          │                                                      │
│          ├──────────────────┬──────────────────┐                │
│          │                  │                  │                │
│          ▼                  ▼                  ▼                │
│   ┌─────────────┐   ┌─────────────┐   ┌─────────────┐          │
│   │  React dist │   │  Gunicorn   │   │   media/    │          │
│   │  静态文件   │   │  Django App │   │  媒体文件   │          │
│   └─────────────┘   │  (8000端口) │   └─────────────┘          │
│                     └─────────────┘                            │
│                          │                                      │
│                          ▼                                      │
│                   ┌─────────────┐                               │
│                   │   SQLite    │                               │
│                   │   数据库    │                               │
│                   └─────────────┘                               │
│                                                                 │
│   类比嵌入式系统：                                               │
│   - Nginx    →  中断控制器，分发请求                             │
│   - Gunicorn →  主程序，处理业务逻辑                             │
│   - SQLite   →  内部存储                                         │
│   - static/  →  只读存储（固件）                                 │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

#### 部署步骤

```bash
# 1. 服务器准备（Ubuntu/Debian）
sudo apt update
sudo apt install python3-pip python3-venv nginx sqlite3

# 2. 项目部署
cd /var/www/
git clone <your-project>
cd xxm_fans_home

# 3. 后端配置
cd repo/xxm_fans_backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic

# 4. Gunicorn 配置（类似守护进程）
# /etc/systemd/system/gunicorn.service
[Unit]
Description=Django Gunicorn Daemon
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/xxm_fans_home/repo/xxm_fans_backend
ExecStart=/var/www/xxm_fans_home/repo/xxm_fans_backend/venv/bin/gunicorn \
    --access-logfile - \
    --workers 3 \
    --bind unix:/var/www/xxm_fans_home/app.sock \
    xxm_fans_home.wsgi:application

[Install]
WantedBy=multi-user.target
```

#### Nginx 配置

```nginx
# /etc/nginx/sites-available/xxm_fans_home
server {
    listen 80;
    server_name your-domain.com;

    # 前端静态文件
    location / {
        root /var/www/xxm_fans_home/repo/xxm_fans_frontend/dist;
        try_files $uri $uri/ /index.html;
    }

    # API 转发到 Gunicorn
    location /api/ {
        proxy_pass http://unix:/var/www/xxm_fans_home/app.sock;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    # 媒体文件
    location /media/ {
        alias /var/www/xxm_fans_home/media/;
    }
}
```

#### 阅读项目源码
```
阅读任务：
1. infra/nginx/prod-xxm_nginx.conf
   - 理解 Nginx 配置结构
   - 注意静态文件和 API 的路由分离

2. infra/systemd/
   - 理解 systemd 服务配置
   - 学习如何管理进程

3. scripts/
   - 理解部署脚本
   - 注意软链接的使用
```

---

## 第六阶段：源码精读与实战（持续）

### 按模块深入学习

#### 模块 1：音乐资产管理

```
学习目标：理解核心业务逻辑

阅读路径：
1. backend/song_management/models/song.py
   - 理解 Song 和 SongRecord 的关系
   - 注意数据库索引设计

2. backend/song_management/api/
   - views.py: 理解 API 实现
   - serializers.py: 理解数据序列化
   
3. frontend/presentation/pages/SongsPage.tsx
   - 理解前端页面如何调用后端 API
   - 注意状态管理和数据流

实践任务：
- 添加一个新的字段到 Song 模型
- 实现按歌手筛选功能
- 添加导出歌曲列表为 CSV 的功能
```

#### 模块 2：图集管理

```
学习目标：理解多级树形结构

阅读路径：
1. backend/gallery/models.py
   - 理解自引用外键
   - 注意递归方法实现

2. frontend/presentation/pages/GalleryPage.tsx
   - 理解树形组件渲染
   - 注意图片懒加载实现

实践任务：
- 实现图集折叠/展开功能
- 添加图片批量上传功能
```

#### 模块 3：数据分析

```
学习目标：理解数据爬虫和统计

阅读路径：
1. spider/run_tiered_crawler.py
   - 理解分层爬虫策略
   
2. backend/data_analytics/models/
   - 理解数据模型设计

3. frontend/presentation/pages/DataAnalysisPage.tsx
   - 理解图表组件使用

实践任务：
- 添加新的统计指标
- 实现数据导出功能
```

---

## 学习资源推荐

### 官方文档（优先阅读）
| 技术 | 文档链接 | 建议章节 |
|------|----------|----------|
| Python | docs.python.org/zh-cn/3/ | 教程全篇 |
| Django | docs.djangoproject.com | 入门教程 + ORM |
| DRF | www.django-rest-framework.org | 快速入门 |
| React | react.dev | 快速入门 + 主要概念 |
| TypeScript | typescriptlang.org/docs |  handbook |
| Tailwind | tailwindcss.com/docs | 核心概念 |

### 视频教程
- 🎬 [Django 企业开发实战](https://www.bilibili.com) - B站搜索
- 🎬 [React 技术栈](https://www.bilibili.com) - B站搜索
- 🎬 [TypeScript 入门](https://www.bilibili.com) - B站搜索

### 实践项目建议
1. **个人博客系统**（2 周）
   - 文章发布/编辑/删除
   - 评论系统
   - 简单的后台管理

2. **设备管理平台**（3 周）
   - 结合你的嵌入式背景
   - 设备注册/状态监控
   - 数据可视化
   - 远程控制接口

---

## 学习时间表

```
┌─────────────────────────────────────────────────────────────────┐
│                      学习时间安排                                │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  周数    阶段              内容                        时间投入  │
│  ─────────────────────────────────────────────────────────────  │
│   1-3    第一阶段         Python + Django 基础         2-3h/天  │
│   4-5    第二阶段         数据库与 ORM                 2-3h/天  │
│   6-9    第三阶段         前端基础 (TS/React)          3-4h/天  │
│  10-11   第四阶段         前后端联调                   2-3h/天  │
│  12-13   第五阶段         部署与运维                   2h/天    │
│  14+     第六阶段         源码精读 + 实战项目          持续      │
│                                                                 │
│  总计：约 3 个月达到独立开发水平                                   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 常见问题 FAQ

### Q1: 嵌入式转 Web 有什么优势？
- 扎实的编程基础
- 熟悉 Linux 系统（部署有优势）
- 理解硬件原理（IoT 项目有优势）
- 调试能力强

### Q2: 学习过程中遇到困难怎么办？
1. 先理解概念，不要急于写代码
2. 多利用你的嵌入式知识进行类比
3. 善用 Chrome DevTools 调试
4. 参考项目源码的实现方式

### Q3: 如何快速定位问题？
```
后端问题：
- 查看 Django 错误页面（DEBUG=True 时）
- 查看日志：logs/django.log
- 使用断点调试：pdb 或 IDE 调试器

前端问题：
- F12 打开 DevTools
- Console 查看报错
- Network 查看 API 调用
- 使用 React DevTools 插件
```

### Q4: 如何贡献代码到项目？
1. 先阅读现有代码，理解代码风格
2. 从小功能开始（如添加一个字段）
3. 遵循项目的架构规范
4. 提交前进行测试

---

## 总结

作为嵌入式工程师，你已经具备了学习 Web 开发的坚实基础。通过这份路线：

1. **利用已有知识** - 将 Web 概念与嵌入式经验类比
2. **循序渐进** - 从后端到前端，从基础到实战
3. **项目驱动** - 通过小满虫之家源码学习真实项目
4. **持续实践** - 理论学习后立即动手实践

祝你学习顺利！有任何问题可以查阅项目文档或寻求社区帮助。
