# Next.js 迁移执行 TODO 文档

> 文档版本：v1.0  
> 创建日期：2026-02-18  
> 预计工期：3-4 周（1 名开发者）  
> 关联文档：
> - [技术调研报告](./nextjs-technical-research.md)
> - [改造分析报告](./nextjs-migration-analysis.md)
> - [Git 工作流指南](./nextjs-migration-git-workflow.md)

---

## 📋 项目概述

将现有 Vite + React + SWR 项目迁移至 Next.js 15 + App Router，实现 SSR/SSG/ISR 混合渲染模式，提升 SEO 和首屏性能。

### 关键目标

| 目标 | 当前值 | 目标值 | 提升幅度 |
|------|--------|--------|----------|
| SEO 评分 | 65/100 | 95/100 | +46% |
| FCP | 1.8s | 0.8s | -56% |
| LCP | 2.5s | 1.2s | -52% |
| 搜索引擎索引 | 低 | 高 | +40-60% |

---

## 🗂️ 执行阶段总览

```
Phase 1: 环境准备与基础搭建 (Week 1) ─────────────────────────────┐
Phase 2: 核心架构迁移 (Week 1-2) ─────────────────────────────────┤
Phase 3: 静态页面迁移 (Week 2) ───────────────────────────────────┤
Phase 4: 数据驱动页面迁移 (Week 2-3) ─────────────────────────────┤
Phase 5: 复杂交互页面迁移 (Week 3) ───────────────────────────────┤
Phase 6: 测试优化与上线 (Week 4) ─────────────────────────────────┘
```

### 开发环境脚本

| 脚本 | 说明 | 使用阶段 |
|------|------|----------|
| `scripts/dev_start_nextjs.sh` | 启动 Next.js 开发环境（含后端 API） | Phase 1-6 |
| `scripts/dev_stop_nextjs.sh` | 停止 Next.js 开发环境 | Phase 1-6 |

---

## Phase 1: 环境准备与基础搭建

**工期**：3-4 天  
**目标**：创建独立开发环境，初始化 Next.js 项目，配置基础架构

### 1.1 独立开发环境搭建

| 序号 | 任务 | 详细说明 | 验收标准 | 状态 |
|------|------|----------|----------|------|
| 1.1.1 | 创建独立工作目录 | `mkdir -p repo/xxm_nextjs` | 目录存在且可访问 | ⬜ |
| 1.1.2 | 初始化 Git 仓库 | `git init`，配置用户名邮箱 | `git status` 正常工作 | ⬜ |

**注意**：本项目仅在本地开发，**不需要**添加远程仓库或推送到远程。

**功能测试**：
```bash
# 验收命令
cd repo/xxm_nextjs
git status
git log --oneline
```

---

### 1.2 Next.js 项目初始化

| 序号 | 任务 | 详细说明 | 验收标准 | 状态 |
|------|------|----------|----------|------|
| 1.2.1 | 创建 Next.js 项目 | `npx create-next-app@latest . --typescript --tailwind --eslint --app --src-dir=false --import-alias="@/*" --use-npm` | 项目初始化成功，无报错 | ⬜ |
| 1.2.2 | 验证开发服务器 | `npm run dev`，访问 `http://localhost:3000` | 默认首页正常显示 | ⬜ |
| 1.2.3 | 提交初始代码 | `git add -A && git commit -m "init: initialize Next.js project"` | 首次提交完成 | ⬜ |

**功能测试**：
```bash
# 验收命令
curl http://localhost:3000 | head -20
```

---

### 1.3 基础依赖安装

| 序号 | 任务 | 详细说明 | 验收标准 | 状态 |
|------|------|----------|----------|------|
| 1.3.1 | 安装 UI/图标库 | `npm install lucide-react` | package.json 更新 | ⬜ |
| 1.3.2 | 安装数据获取库 | `npm install swr` | SWR 可用于客户端组件 | ⬜ |
| 1.3.3 | 安装动画库（可选） | `npm install framer-motion` | 动画库可用 | ⬜ |
| 1.3.4 | 安装类型定义 | 检查并安装缺失的 @types | TypeScript 无类型错误 | ⬜ |

**功能测试**：
```bash
# 验收命令
npm ls lucide-react swr
npx tsc --noEmit
```

---

### 1.4 配置文件设置

| 序号 | 任务 | 详细说明 | 验收标准 | 状态 |
|------|------|----------|----------|------|
| 1.4.1 | 配置 next.config.ts | 设置 `output: 'standalone'`，图片域名白名单 | 配置可编译 | ⬜ |
| 1.4.2 | 配置 Tailwind CSS | 迁移原项目主题变量到 `@theme` | 样式变量生效 | ⬜ |
| 1.4.3 | 配置环境变量 | 创建 `.env.local`，设置 API_BASE_URL | 环境变量可读取 | ⬜ |
| 1.4.4 | 配置 TypeScript | 启用严格模式，配置路径别名 | `tsconfig.json` 无错误 | ⬜ |

**next.config.ts 配置参考**：
```typescript
import type { NextConfig } from 'next';

const nextConfig: NextConfig = {
    output: 'standalone',
    images: {
        formats: ['image/webp', 'image/avif'],
        remotePatterns: [
            { protocol: 'https', hostname: '**.bilibili.com' },
            { protocol: 'https', hostname: '**.hdslb.com' },
        ],
    },
    experimental: {
        typedRoutes: true,
        optimizePackageImports: ['lucide-react'],
    },
};

export default nextConfig;
```

**功能测试**：
```bash
# 验收命令
npm run build
# 构建成功无错误
```

---

### Phase 1 阶段验收 ✅

| 验收项 | 验收标准 | 结果 |
|--------|----------|------|
| 开发环境 | 独立目录 `repo/xxm_nextjs` 可用 | ⬜ |
| 基础架构 | `./dev_start_nextjs.sh` 正常启动，访问 3000 端口成功 | ⬜ |
| 构建能力 | `npm run build` 成功生成 `.next` 目录 | ⬜ |
| 代码提交 | 至少 1 个 commit，Git 历史正常 | ⬜ |
| 配置文件 | next.config.ts、tailwind.config.ts 配置完成 | ⬜ |

**里程碑标签**：`v0.1.0-init`

---

### Phase 1 快速启动命令

创建脚本后，使用以下命令快速启动开发环境：

```bash
# 启动 Next.js 开发环境（自动启动后端 API + Next.js）
cd /home/yifeianyi/Desktop/xxm_fans_home/scripts
./dev_start_nextjs.sh

# 输出示例：
# =========================================
# XXM Fans Home - Next.js 开发环境启动
# =========================================
# ...
# 访问地址：
#   - Next.js 前端:      http://localhost:3000/
#   - 后端 API:          http://localhost:8000/api/
```

```bash
# 停止开发环境
./dev_stop_nextjs.sh

# 查看实时日志
tail -f /tmp/nextjs_dev.log
tail -f /tmp/backend_nextjs.log
```

---

## Phase 2: 核心架构迁移

**工期**：5-6 天  
**目标**：迁移 DDD 架构，建立 Server/Client Components 分层

### 2.1 目录结构创建

| 序号 | 任务 | 详细说明 | 验收标准 | 状态 |
|------|------|----------|----------|------|
| 2.1.1 | 创建领域层 | `app/domain/types.ts` - 迁移原类型定义 | 所有类型可导入 | ⬜ |
| 2.1.2 | 创建基础设施层 | `app/infrastructure/api/` - API 服务 | 服务类可实例化 | ⬜ |
| 2.1.3 | 创建共享层 | `app/shared/hooks/`, `app/shared/utils/` | 工具函数可复用 | ⬜ |
| 2.1.4 | 创建组件目录 | `app/components/common/`, `app/components/features/` | 目录结构清晰 | ⬜ |

**目录结构**：
```
app/
├── domain/              # 领域层
│   └── types.ts         # 领域模型类型
├── infrastructure/      # 基础设施层
│   ├── api/             # API 服务
│   │   ├── songService.ts
│   │   ├── galleryService.ts
│   │   └── ...
│   └── config/          # 配置
├── components/          # 组件层
│   ├── common/          # 通用组件
│   └── features/        # 功能组件
├── shared/              # 共享层
│   ├── hooks/           # 自定义 Hooks
│   └── utils/           # 工具函数
└── (routes)/            # 路由页面
```

---

### 2.2 类型定义迁移

| 序号 | 任务 | 详细说明 | 验收标准 | 状态 |
|------|------|----------|----------|------|
| 2.2.1 | 迁移 Song 类型 | 从原项目复制 Song, SongRecord 类型 | TypeScript 编译通过 | ⬜ |
| 2.2.2 | 迁移 Gallery 类型 | Gallery, GalleryItem 类型 | 类型定义完整 | ⬜ |
| 2.2.3 | 迁移 FansDIY 类型 | Collection, Work 类型 | 类型定义完整 | ⬜ |
| 2.2.4 | 迁移其他类型 | Livestream, DataAnalytics 等 | 无类型错误 | ⬜ |

**功能测试**：
```bash
# 验收命令
npx tsc --noEmit
# 无类型错误
```

---

### 2.3 API 服务层迁移

| 序号 | 任务 | 详细说明 | 验收标准 | 状态 |
|------|------|----------|----------|------|
| 2.3.1 | 创建基础请求 | `app/infrastructure/api/base.ts` - 封装 fetch | 请求封装可用 | ⬜ |
| 2.3.2 | 迁移 SongService | 适配 Server Components | 服务端可调用 | ⬜ |
| 2.3.3 | 迁移 GalleryService | 适配 Server Components | 服务端可调用 | ⬜ |
| 2.3.4 | 迁移其他 Services | FansDIY, Livestream, DataAnalytics | 全部迁移完成 | ⬜ |

**API 服务示例**：
```typescript
// app/infrastructure/api/songService.ts
import { Song } from '@/app/domain/types';

const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000/api';

export async function getSongs(params?: { page?: number; search?: string }): Promise<Song[]> {
    const query = new URLSearchParams();
    if (params?.page) query.set('page', String(params.page));
    if (params?.search) query.set('search', params.search);
    
    const res = await fetch(`${API_BASE}/songs?${query}`, {
        next: { revalidate: 60 }, // 1 分钟缓存
    });
    
    if (!res.ok) throw new Error('Failed to fetch songs');
    return res.json();
}
```

**功能测试**：
```typescript
// 测试代码
import { getSongs } from './app/infrastructure/api/songService';

async function test() {
    const songs = await getSongs({ page: 1 });
    console.assert(Array.isArray(songs), 'Should return array');
}
```

---

### 2.4 全局布局迁移

| 序号 | 任务 | 详细说明 | 验收标准 | 状态 |
|------|------|----------|----------|------|
| 2.4.1 | 创建根布局 | `app/layout.tsx` - RootLayout | 布局渲染正常 | ⬜ |
| 2.4.2 | 迁移全局样式 | `app/globals.css` - 迁移 Tailwind 变量 | 样式生效 | ⬜ |
| 2.4.3 | 创建元数据 | `app/layout.tsx` - metadata | SEO 标签正确 | ⬜ |
| 2.4.4 | 迁移导航组件 | Navbar 组件适配 Next.js | 导航正常显示 | ⬜ |
| 2.4.5 | 迁移页脚组件 | Footer 组件适配 Next.js | 页脚正常显示 | ⬜ |

**根布局参考**：
```typescript
// app/layout.tsx
import type { Metadata } from 'next';
import './globals.css';
import { Navbar } from '@/app/components/layout/Navbar';
import { Footer } from '@/app/components/layout/Footer';

export const metadata: Metadata = {
    title: '小满虫之家 - 咻咻满粉丝站',
    description: '咻咻满歌曲列表、二创作品、直播日历、图集展示',
    keywords: ['咻咻满', '小满虫之家', '歌曲', '翻唱', '直播'],
    openGraph: {
        title: '小满虫之家',
        description: '咻咻满粉丝站',
        images: ['/og-image.jpg'],
    },
};

export default function RootLayout({
    children,
}: {
    children: React.ReactNode;
}) {
    return (
        <html lang="zh-CN">
            <body className="antialiased min-h-screen flex flex-col">
                <Navbar />
                <main className="flex-1">{children}</main>
                <Footer />
            </body>
        </html>
    );
}
```

**功能测试**：
```bash
# 验收命令
npm run dev
# 检查：
# 1. 页面结构完整（html/head/body/main）
# 2. 导航栏和页脚正常显示
# 3. 查看源代码包含 meta 标签
curl http://localhost:3000 | grep -E '<meta|title>'
```

---

### 2.5 客户端 Hooks 迁移

| 序号 | 任务 | 详细说明 | 验收标准 | 状态 |
|------|------|----------|----------|------|
| 2.5.1 | 迁移 useClickOutside | `app/shared/hooks/useClickOutside.ts` | 功能正常 | ⬜ |
| 2.5.2 | 迁移 useDebounce | `app/shared/hooks/useDebounce.ts` | 功能正常 | ⬜ |
| 2.5.3 | 迁移 useLocalStorage | `app/shared/hooks/useLocalStorage.ts` | 功能正常 | ⬜ |
| 2.5.4 | 创建 SWR Hooks | `app/infrastructure/hooks/useSongs.ts` | 客户端数据获取正常 | ⬜ |

**SWR Hook 示例**：
```typescript
// app/infrastructure/hooks/useSongs.ts
'use client';

import useSWR from 'swr';
import { Song } from '@/app/domain/types';

const fetcher = (url: string) => fetch(url).then(r => r.json());

export function useSongs(initialData?: Song[]) {
    const { data, error, isLoading, mutate } = useSWR(
        '/api/songs',
        fetcher,
        { fallbackData: initialData }
    );
    
    return {
        songs: data?.results || [],
        total: data?.total || 0,
        isLoading,
        error,
        mutate,
    };
}
```

---

### Phase 2 阶段验收 ✅

| 验收项 | 验收标准 | 结果 |
|--------|----------|------|
| 类型系统 | `npx tsc --noEmit` 无错误 | ⬜ |
| API 服务 | 所有服务可在 Server Component 中调用 | ⬜ |
| 全局布局 | 根布局包含 Navbar/Footer，children 渲染正常 | ⬜ |
| SEO 基础 | 查看源代码包含完整的 title 和 meta 标签 | ⬜ |
| 客户端 Hooks | SWR Hooks 可在 Client Component 中正常使用 | ⬜ |
| 构建测试 | `npm run build` 成功 | ⬜ |

**里程碑标签**：`v0.2.0-foundation`

---

### Phase 2 测试命令

```bash
# 确保开发环境已启动
./dev_start_nextjs.sh

# 类型检查
cd repo/xxm_nextjs
npx tsc --noEmit

# 构建测试
npm run build

# 验证页面访问
curl http://localhost:3000/ | grep -o '<title>.*</title>'
curl http://localhost:3000/ | grep -E '<nav|<footer'
```

---

## Phase 3: 静态页面迁移

**工期**：3-4 天  
**目标**：迁移首页、关于页、联系页等静态内容页面（SSG 模式）

### 3.1 首页迁移 (/)

| 序号 | 任务 | 详细说明 | 验收标准 | 状态 |
|------|------|----------|----------|------|
| 3.1.1 | 创建页面文件 | `app/page.tsx` | 文件存在 | ⬜ |
| 3.1.2 | 迁移 Hero 区域 | 首页头部展示区域 | 显示正常 | ⬜ |
| 3.1.3 | 迁移推荐内容区 | 歌曲推荐、二创推荐 | 数据展示正常 | ⬜ |
| 3.1.4 | 迁移快捷入口 | 各功能模块入口 | 链接可点击 | ⬜ |
| 3.1.5 | 配置 ISR | 设置 `revalidate = 3600` | 每小时自动更新 | ⬜ |

**首页实现参考**：
```typescript
// app/page.tsx
import { getFeaturedSongs } from '@/app/infrastructure/api/songService';
import { getRecentWorks } from '@/app/infrastructure/api/fansDIYService';
import { HeroSection } from '@/app/components/features/HeroSection';
import { SongPreview } from '@/app/components/features/SongPreview';
import { WorksPreview } from '@/app/components/features/WorksPreview';

export const revalidate = 3600; // ISR: 1 小时

export default async function HomePage() {
    const [songs, works] = await Promise.all([
        getFeaturedSongs(),
        getRecentWorks(),
    ]);

    return (
        <div className="space-y-12 py-8">
            <HeroSection />
            <SongPreview songs={songs} />
            <WorksPreview works={works} />
        </div>
    );
}
```

**功能测试**：
```bash
# 验收命令
curl http://localhost:3000/ | grep -E '<h1|<title>'
# 检查：
# 1. 返回 HTML 包含完整内容（非空 root）
# 2. title 标签正确
# 3. h1 标签包含关键内容
```

---

### 3.2 关于页迁移 (/about)

| 序号 | 任务 | 详细说明 | 验收标准 | 状态 |
|------|------|----------|----------|------|
| 3.2.1 | 创建页面文件 | `app/about/page.tsx` | 文件存在 | ⬜ |
| 3.2.2 | 迁移内容 | 关于小满虫之家的介绍 | 内容完整 | ⬜ |
| 3.2.3 | 配置 SSG | 纯静态生成，无 revalidate | HTML 静态生成 | ⬜ |
| 3.2.4 | 添加动态元数据 | generateMetadata | SEO 正确 | ⬜ |

**功能测试**：
```bash
# 验收命令
curl http://localhost:3000/about | grep -o '<title>.*</title>'
# 检查：title 包含"关于"
```

---

### 3.3 联系页迁移 (/contact)

| 序号 | 任务 | 详细说明 | 验收标准 | 状态 |
|------|------|----------|----------|------|
| 3.3.1 | 创建页面文件 | `app/contact/page.tsx` | 文件存在 | ⬜ |
| 3.3.2 | 迁移联系表单 | 联系方式展示 | 内容完整 | ⬜ |
| 3.3.3 | 配置 SSG | 纯静态生成 | HTML 静态生成 | ⬜ |

---

### Phase 3 阶段验收 ✅

| 验收项 | 验收标准 | 结果 |
|--------|----------|------|
| 首页 | `/` 路由正常，包含完整内容，ISR 配置生效 | ⬜ |
| 关于页 | `/about` 路由正常，静态生成 | ⬜ |
| 联系页 | `/contact` 路由正常，静态生成 | ⬜ |
| SEO 验证 | 每个页面查看源代码都有独立的 title 和 meta | ⬜ |
| 导航链接 | Navbar 中的链接可正常跳转 | ⬜ |
| 构建产物 | `npm run build` 生成静态 HTML 文件 | ⬜ |

**里程碑标签**：`v0.3.0-static-pages`

---

## Phase 4: 数据驱动页面迁移

**工期**：6-7 天  
**目标**：迁移歌曲列表、热歌榜、原唱作品、二创展厅等数据驱动页面

### 4.1 歌曲列表页迁移 (/songs)

| 序号 | 任务 | 详细说明 | 验收标准 | 状态 |
|------|------|----------|----------|------|
| 4.1.1 | 创建页面文件 | `app/songs/page.tsx` | 文件存在 | ⬜ |
| 4.1.2 | 服务端获取数据 | Server Component 获取歌曲列表 | 数据正常 | ⬜ |
| 4.1.3 | 创建客户端组件 | `app/songs/SongListClient.tsx` | 组件可用 | ⬜ |
| 4.1.4 | 迁移搜索功能 | 搜索框、筛选器 | 搜索可用 | ⬜ |
| 4.1.5 | 迁移分页功能 | 分页组件 | 分页正常 | ⬜ |
| 4.1.6 | 迁移排序功能 | 排序选项 | 排序正常 | ⬜ |
| 4.1.7 | 配置 SSR | 动态渲染 | 每次请求获取最新数据 | ⬜ |
| 4.1.8 | 动态元数据 | generateMetadata 包含歌曲数量 | SEO 优化 | ⬜ |

**页面实现参考**：
```typescript
// app/songs/page.tsx
import { getSongs, getStyles, getTags } from '@/app/infrastructure/api/songService';
import { SongListClient } from './SongListClient';
import type { Metadata } from 'next';

export const dynamic = 'force-dynamic'; // SSR 模式

export async function generateMetadata(): Promise<Metadata> {
    return {
        title: '咻咻满歌曲列表 | 翻唱合集 - 小满虫之家',
        description: '收录咻咻满全部翻唱、原唱作品，支持搜索、筛选、排序',
    };
}

export default async function SongsPage({
    searchParams,
}: {
    searchParams: { page?: string; search?: string; style?: string };
}) {
    const page = Number(searchParams.page) || 1;
    const [songsData, styles, tags] = await Promise.all([
        getSongs({ page, search: searchParams.search, style: searchParams.style }),
        getStyles(),
        getTags(),
    ]);

    return (
        <div className="container mx-auto py-8">
            <h1 className="text-3xl font-bold mb-6">歌曲列表</h1>
            <SongListClient 
                initialSongs={songsData.results} 
                initialTotal={songsData.total}
                styles={styles}
                tags={tags}
            />
        </div>
    );
}
```

**客户端组件参考**：
```typescript
// app/songs/SongListClient.tsx
'use client';

import { useState } from 'react';
import { useSongs } from '@/app/infrastructure/hooks/useSongs';
import { Song } from '@/app/domain/types';

interface Props {
    initialSongs: Song[];
    initialTotal: number;
    styles: string[];
    tags: string[];
}

export function SongListClient({ initialSongs, initialTotal, styles, tags }: Props) {
    const [search, setSearch] = useState('');
    const { songs, total, isLoading } = useSongs({ 
        fallbackData: { results: initialSongs, total: initialTotal }
    });

    return (
        <div>
            {/* 搜索、筛选、列表 */}
        </div>
    );
}
```

**功能测试**：
```bash
# 验收命令
curl "http://localhost:3000/songs" | grep -o '<title>.*</title>'
curl "http://localhost:3000/songs?page=2" | grep -c '<tr'  # 检查列表行数

# 检查：
# 1. title 包含"歌曲列表"
# 2. HTML 包含歌曲数据（非空）
# 3. 分页参数生效
```

---

### 4.2 热歌榜页迁移 (/songs/hot)

| 序号 | 任务 | 详细说明 | 验收标准 | 状态 |
|------|------|----------|----------|------|
| 4.2.1 | 创建页面文件 | `app/songs/hot/page.tsx` | 文件存在 | ⬜ |
| 4.2.2 | 迁移排行榜组件 | 排名列表展示 | 组件正常 | ⬜ |
| 4.2.3 | 配置 ISR | `revalidate = 3600`（每小时更新） | ISR 配置生效 | ⬜ |
| 4.2.4 | 动态元数据 | 包含排名信息 | SEO 正确 | ⬜ |

**功能测试**：
```bash
# 验收命令
curl http://localhost:3000/songs/hot | grep -o '<title>.*</title>'
# 检查：title 包含"热歌榜"或"排行榜"
```

---

### 4.3 原唱作品页迁移 (/originals)

| 序号 | 任务 | 详细说明 | 验收标准 | 状态 |
|------|------|----------|----------|------|
| 4.3.1 | 创建页面文件 | `app/originals/page.tsx` | 文件存在 | ⬜ |
| 4.3.2 | 迁移原唱列表 | 原唱歌曲展示 | 数据正常 | ⬜ |
| 4.3.3 | 配置 SSR | 动态渲染 | 最新数据 | ⬜ |

---

### 4.4 二创展厅页迁移 (/fansDIY)

| 序号 | 任务 | 详细说明 | 验收标准 | 状态 |
|------|------|----------|----------|------|
| 4.4.1 | 创建列表页 | `app/fansDIY/page.tsx` | 文件存在 | ⬜ |
| 4.4.2 | 创建详情页 | `app/fansDIY/[id]/page.tsx` | 动态路由可用 | ⬜ |
| 4.4.3 | 迁移合集展示 | 合集卡片列表 | 样式正常 | ⬜ |
| 4.4.4 | 迁移作品列表 | 详情页作品列表 | 数据正常 | ⬜ |
| 4.4.5 | 配置 SSR | 动态渲染 | 最新数据 | ⬜ |
| 4.4.6 | 动态元数据 | 详情页元数据包含合集名称 | SEO 正确 | ⬜ |

**动态路由参考**：
```typescript
// app/fansDIY/[id]/page.tsx
import { getCollection, getCollectionWorks } from '@/app/infrastructure/api/fansDIYService';
import type { Metadata } from 'next';

interface Props {
    params: Promise<{ id: string }>;
}

export async function generateMetadata({ params }: Props): Promise<Metadata> {
    const { id } = await params;
    const collection = await getCollection(id);
    return {
        title: `${collection.name} | 二创作品 - 小满虫之家`,
        description: collection.description,
    };
}

export default async function CollectionPage({ params }: Props) {
    const { id } = await params;
    const [collection, works] = await Promise.all([
        getCollection(id),
        getCollectionWorks(id),
    ]);

    return (
        <div className="container mx-auto py-8">
            <h1 className="text-3xl font-bold">{collection.name}</h1>
            {/* 作品列表 */}
        </div>
    );
}
```

---

### Phase 4 阶段验收 ✅

| 验收项 | 验收标准 | 结果 |
|--------|----------|------|
| 歌曲列表 | `/songs` 正常显示，支持搜索/筛选/分页 | ⬜ |
| 热歌榜 | `/songs/hot` 正常显示，ISR 每小时更新 | ⬜ |
| 原唱作品 | `/originals` 正常显示 | ⬜ |
| 二创展厅 | `/fansDIY` 和 `/fansDIY/:id` 正常显示 | ⬜ |
| 动态元数据 | 详情页查看源代码有独立 title | ⬜ |
| 服务端渲染 | 禁用 JS 后页面内容仍然可见 | ⬜ |
| 构建测试 | `npm run build` 成功 | ⬜ |

**里程碑标签**：`v0.4.0-data-pages`

---

## Phase 5: 复杂交互页面迁移

**工期**：4-5 天  
**目标**：迁移图集页、直播日历页、数据分析页等复杂交互页面

### 5.1 图集页迁移 (/gallery)

| 序号 | 任务 | 详细说明 | 验收标准 | 状态 |
|------|------|----------|----------|------|
| 5.1.1 | 创建列表页 | `app/gallery/page.tsx` | 文件存在 | ⬜ |
| 5.1.2 | 创建详情页 | `app/gallery/[id]/page.tsx` | 动态路由可用 | ⬜ |
| 5.1.3 | 迁移图片展示 | 图片画廊组件 | 图片正常显示 | ⬜ |
| 5.1.4 | 迁移懒加载 | 图片懒加载功能 | 懒加载可用 | ⬜ |
| 5.1.5 | 适配 next/image | 使用 Next.js Image 组件 | 图片优化生效 | ⬜ |
| 5.1.6 | 迁移灯箱功能 | 图片放大查看 | 交互正常 | ⬜ |
| 5.1.7 | 配置 SSR | 动态渲染 | 最新数据 | ⬜ |

**Image 组件迁移**：
```typescript
// 原代码
<img src="/gallery/xxx.jpg" alt="xxx" loading="lazy" />

// 新代码
import Image from 'next/image';

<Image
    src="/gallery/xxx.jpg"
    alt="xxx"
    width={800}
    height={600}
    loading="lazy"
    placeholder="blur"
    blurDataURL="data:image/jpeg;base64,..."
/>
```

**功能测试**：
```bash
# 验收命令
curl http://localhost:3000/gallery | grep -o '<title>.*</title>'
# 检查：页面正常，图片使用 next/image
```

---

### 5.2 直播日历页迁移 (/live)

| 序号 | 任务 | 详细说明 | 验收标准 | 状态 |
|------|------|----------|----------|------|
| 5.2.1 | 创建页面文件 | `app/live/page.tsx` | 文件存在 | ⬜ |
| 5.2.2 | 迁移日历组件 | 日历展示（Client Component） | 日历正常显示 | ⬜ |
| 5.2.3 | 迁移直播列表 | 直播记录展示 | 数据正常 | ⬜ |
| 5.2.4 | 迁移视频播放 | 直播回放播放 | 播放正常 | ⬜ |
| 5.2.5 | 服务端获取数据 | 获取直播日历数据 | 服务端渲染日历 | ⬜ |

**混合架构参考**：
```typescript
// app/live/page.tsx
import { getLivestreams } from '@/app/infrastructure/api/livestreamService';
import { LiveCalendar } from './LiveCalendar';
import { LiveList } from './LiveList';

export default async function LivePage() {
    const livestreams = await getLivestreams();

    return (
        <div className="container mx-auto py-8">
            <h1 className="text-3xl font-bold mb-6">直播日历</h1>
            {/* 服务端渲染列表 */}
            <LiveList initialData={livestreams} />
            {/* 客户端交互日历 */}
            <LiveCalendar initialData={livestreams} />
        </div>
    );
}
```

---

### 5.3 数据分析页迁移 (/data)

| 序号 | 任务 | 详细说明 | 验收标准 | 状态 |
|------|------|----------|----------|------|
| 5.3.1 | 创建页面文件 | `app/data/page.tsx` | 文件存在 | ⬜ |
| 5.3.2 | 迁移图表组件 | 数据图表（Client Component） | 图表正常显示 | ⬜ |
| 5.3.3 | 配置 CSR | 客户端渲染模式 | 图表交互正常 | ⬜ |
| 5.3.4 | 服务端获取元数据 | 获取基础统计数据 | SEO 有基础内容 | ⬜ |

**CSR 模式参考**：
```typescript
// app/data/page.tsx
import { getBasicStats } from '@/app/infrastructure/api/analyticsService';
import { DataCharts } from './DataCharts';

// 提供基础元数据用于 SEO
export async function generateMetadata() {
    const stats = await getBasicStats();
    return {
        title: `数据分析 | 小满虫之家`,
        description: `收录 ${stats.totalSongs} 首歌曲，${stats.totalWorks} 个二创作品`,
    };
}

export default async function DataPage() {
    const basicStats = await getBasicStats();

    return (
        <div className="container mx-auto py-8">
            <h1 className="text-3xl font-bold mb-6">数据分析</h1>
            {/* 服务端渲染基础数据 */}
            <StatsSummary stats={basicStats} />
            {/* 客户端渲染复杂图表 */}
            <DataCharts />
        </div>
    );
}
```

---

### Phase 5 阶段验收 ✅

| 验收项 | 验收标准 | 结果 |
|--------|----------|------|
| 图集页 | `/gallery` 和 `/gallery/:id` 正常显示，图片使用 next/image | ⬜ |
| 直播日历 | `/live` 正常显示，日历交互正常 | ⬜ |
| 数据分析 | `/data` 正常显示，图表渲染正常 | ⬜ |
| 混合架构 | Server/Client Components 协同工作正常 | ⬜ |
| 图片优化 | next/image 自动优化生效（检查网络请求） | ⬜ |
| 构建测试 | `npm run build` 成功 | ⬜ |

**里程碑标签**：`v0.5.0-complex-pages`

---

## Phase 6: 测试优化与上线

**工期**：4-5 天  
**目标**：全面测试、性能优化、部署上线

### 6.1 功能测试

| 序号 | 任务 | 详细说明 | 验收标准 | 状态 |
|------|------|----------|----------|------|
| 6.1.1 | 路由测试 | 访问所有页面路由 | 无 404 错误 | ⬜ |
| 6.1.2 | 导航测试 | 点击所有导航链接 | 页面切换正常 | ⬜ |
| 6.1.3 | 数据获取测试 | 检查各页面数据加载 | 数据正确显示 | ⬜ |
| 6.1.4 | 搜索筛选测试 | 歌曲列表搜索/筛选 | 功能正常 | ⬜ |
| 6.1.5 | 分页测试 | 列表分页功能 | 分页正常 | ⬜ |
| 6.1.6 | 图片加载测试 | 检查图片懒加载 | 懒加载生效 | ⬜ |
| 6.1.7 | 响应式测试 | 移动端/平板/桌面适配 | 各尺寸显示正常 | ⬜ |

**功能测试检查清单**：

```bash
# 确保开发环境已启动
./dev_start_nextjs.sh

# 自动化路由测试
#!/bin/bash
ROUTES=(
    "/"
    "/about"
    "/contact"
    "/songs"
    "/songs/hot"
    "/originals"
    "/fansDIY"
    "/fansDIY/1"
    "/gallery"
    "/gallery/1"
    "/live"
    "/data"
)

for route in "${ROUTES[@]}"; do
    status=$(curl -s -o /dev/null -w "%{http_code}" "http://localhost:3000$route")
    echo "$route: $status"
done
```

---

### 6.2 SEO 测试

| 序号 | 任务 | 详细说明 | 验收标准 | 状态 |
|------|------|----------|----------|------|
| 6.2.1 | 元数据检查 | 检查各页面 title/meta | 每个页面独立 | ⬜ |
| 6.2.2 | OG 标签检查 | Open Graph 标签 | 社交分享可用 | ⬜ |
| 6.2.3 | 结构化数据 | 添加 JSON-LD | 搜索引擎可解析 | ⬜ |
| 6.2.4 | Robots.txt | 创建 robots.txt | 可访问 | ⬜ |
| 6.2.5 | Sitemap | 生成 sitemap.xml | 包含所有路由 | ⬜ |

**SEO 测试命令**：

```bash
# 确保开发环境已启动
./dev_start_nextjs.sh

# 检查各页面 title
curl -s http://localhost:3000/ | grep -o '<title>[^<]*</title>'
curl -s http://localhost:3000/songs | grep -o '<title>[^<]*</title>'
curl -s http://localhost:3000/songs/hot | grep -o '<title>[^<]*</title>'

# 检查 meta description
curl -s http://localhost:3000/ | grep -o '<meta name="description" content="[^"]*"'

# 检查 og 标签
curl -s http://localhost:3000/ | grep -o '<meta property="og:[^"]*" content="[^"]*"'
```

---

### 6.3 性能测试

| 序号 | 任务 | 详细说明 | 验收标准 | 状态 |
|------|------|----------|----------|------|
| 6.3.1 | Lighthouse 测试 | 运行 Lighthouse | 评分 > 90 | ⬜ |
| 6.3.2 | Core Web Vitals | LCP, FCP, CLS 测量 | 达到 Good 等级 | ⬜ |
| 6.3.3 | 首字节时间 | TTFB 测量 | < 200ms | ⬜ |
| 6.3.4 | 构建分析 | `npm run analyze` | 包体积分析 | ⬜ |
| 6.3.5 | 图片优化检查 | 检查图片加载 | 使用 WebP/AVIF | ⬜ |

**性能测试目标**：

| 指标 | 当前值 | 目标值 | 等级 |
|------|--------|--------|------|
| LCP | 2.5s | 1.2s | 🟢 Good |
| FCP | 1.8s | 0.8s | 🟢 Good |
| CLS | 0.05 | 0.01 | 🟢 Good |
| TTFB | 50ms | 80ms | 🟢 Good |
| Lighthouse | 72 | 92 | 🟢 Good |

**性能测试命令**：

```bash
# 确保开发环境已启动
./dev_start_nextjs.sh

# 安装 Lighthouse
npm install -g lighthouse

# 运行测试（确保 Next.js 在 3000 端口运行）
lighthouse http://localhost:3000 --output html --output-path ./lighthouse-report.html

# 或 Chrome DevTools 手动测试
```

---

### 6.4 兼容性测试

| 序号 | 任务 | 详细说明 | 验收标准 | 状态 |
|------|------|----------|----------|------|
| 6.4.1 | 浏览器测试 | Chrome, Firefox, Safari, Edge | 无重大问题 | ⬜ |
| 6.4.2 | 移动端测试 | iOS Safari, Android Chrome | 触摸交互正常 | ⬜ |
| 6.4.3 | 无障碍测试 | 键盘导航, 屏幕阅读器 | WCAG 2.1 AA | ⬜ |
| 6.4.4 | 禁用 JS 测试 | 无 JS 环境页面展示 | 内容可见 | ⬜ |

---

### 6.5 部署准备与上线

#### 部署准备

| 序号 | 任务 | 详细说明 | 验收标准 | 状态 |
|------|------|----------|----------|------|
| 6.5.1 | 配置构建输出 | `output: 'standalone'` | 独立部署包生成成功 | ⬜ |
| 6.5.2 | 配置 Nginx | 反向代理配置 | 配置正确 | ⬜ |
| 6.5.3 | 环境变量检查 | 生产环境变量 | 配置完整 | ⬜ |
| 6.5.4 | 健康检查端点 | `/api/health` | 可访问 | ⬜ |

#### 上线部署步骤

| 序号 | 任务 | 详细说明 | 验收标准 | 状态 |
|------|------|----------|----------|------|
| 6.5.5 | 构建生产包 | `npm run build` | 构建成功 | ⬜ |
| 6.5.6 | 合并到原项目 | 按 Git 工作流合并 | 合并完成 | ⬜ |
| 6.5.7 | 部署到测试环境 | 测试服务器部署 | 测试环境可用 | ⬜ |
| 6.5.8 | 灰度发布 | 部分流量切换 | 监控正常 | ⬜ |
| 6.5.9 | 全量切换 | 全部流量切换 | 服务稳定 | ⬜ |
| 6.5.10 | 回滚方案验证 | 验证可快速回滚 | 回滚可用 | ⬜ |

**本地部署方案**：
```bash
# 1. 构建生产包
npm run build

# 2. 启动生产服务器（本地运行）
NODE_ENV=production PORT=3000 node .next/standalone/server.js

# 3. 使用 systemd 管理（推荐）
# 创建服务文件 /etc/systemd/system/xxm-nextjs.service
# 然后使用 systemctl start xxm-nextjs
```

**合并到原项目**：
```bash
# 按 Git 工作流指南操作
cd /home/yifeianyi/Desktop/xxm_fans_home/repo/xxm_fans_frontend

# 添加远程（使用绝对路径）
git remote add nextjs /home/yifeianyi/Desktop/xxm_fans_home/repo/xxm_nextjs
git fetch nextjs

# 创建孤儿分支
git checkout --orphan nextjs-clean
git rm -rf .
git pull /home/yifeianyi/Desktop/xxm_fans_home/repo/xxm_nextjs main --allow-unrelated-histories

# 添加标签
git tag -a nextjs-root -m "Next.js era begins"
git tag -a v3.0.0 -m "Next.js migration complete"

# 合并到 main
git checkout main
git merge nextjs-clean --allow-unrelated-histories -m "feat: merge Next.js migration"

git push origin main --tags
```

---

### Phase 6 阶段验收 ✅

| 验收项 | 验收标准 | 结果 |
|--------|----------|------|
| 功能测试 | 所有路由可访问，功能正常 | ⬜ |
| SEO 测试 | 各页面有独立元数据，sitemap 可用 | ⬜ |
| 性能测试 | Lighthouse 评分 > 90，Core Web Vitals 达标 | ⬜ |
| 兼容性测试 | 主流浏览器/移动端兼容 | ⬜ |
| 部署测试 | 本地构建成功，服务可运行 | ⬜ |
| 上线验证 | 生产环境稳定运行 24 小时 | ⬜ |

**最终里程碑标签**：`v1.0.0-ready`

---

## 📊 总体测试与验收矩阵

### 功能验收清单

| 模块 | 功能点 | 测试方法 | 验收标准 | 状态 |
|------|--------|----------|----------|------|
| **全局** | 路由导航 | 点击所有导航链接 | 页面切换正常，无 404 | ⬜ |
| | 响应式布局 | 调整浏览器尺寸 | 移动端/平板/桌面正常 | ⬜ |
| | 错误页面 | 访问不存在的路由 | 显示 404 页面 | ⬜ |
| **首页** | 内容展示 | 访问 `/` | Hero、推荐内容显示正常 | ⬜ |
| | ISR 更新 | 等待 1 小时后刷新 | 内容自动更新 | ⬜ |
| **歌曲列表** | 列表展示 | 访问 `/songs` | 歌曲列表渲染 | ⬜ |
| | 搜索功能 | 输入关键词搜索 | 结果过滤正确 | ⬜ |
| | 筛选功能 | 选择曲风/标签 | 结果过滤正确 | ⬜ |
| | 分页功能 | 点击分页按钮 | 页码切换正常 | ⬜ |
| | 排序功能 | 选择排序方式 | 排序正确 | ⬜ |
| **热歌榜** | 排行榜展示 | 访问 `/songs/hot` | 排名列表显示 | ⬜ |
| | ISR 更新 | 每小时检查 | 数据更新 | ⬜ |
| **二创展厅** | 合集列表 | 访问 `/fansDIY` | 合集卡片显示 | ⬜ |
| | 合集详情 | 点击合集卡片 | 详情页正常 | ⬜ |
| | 作品列表 | 访问合集详情 | 作品列表显示 | ⬜ |
| **图集** | 图集列表 | 访问 `/gallery` | 图集网格显示 | ⬜ |
| | 图片展示 | 访问图集详情 | 图片画廊显示 | ⬜ |
| | 图片懒加载 | 滚动页面 | 图片按需加载 | ⬜ |
| | 灯箱功能 | 点击图片 | 放大查看正常 | ⬜ |
| **直播日历** | 日历展示 | 访问 `/live` | 日历组件显示 | ⬜ |
| | 日期切换 | 切换月份/日期 | 交互正常 | ⬜ |
| | 直播列表 | 选择日期 | 当日直播显示 | ⬜ |
| **数据分析** | 数据展示 | 访问 `/data` | 统计数据显示 | ⬜ |
| | 图表渲染 | 查看图表区域 | 图表正常显示 | ⬜ |
| | 数据更新 | 刷新页面 | 数据获取正常 | ⬜ |

### SEO 验收清单

| 检查项 | 测试方法 | 验收标准 | 状态 |
|--------|----------|----------|------|
| 首页 title | `curl \| grep title` | 包含"小满虫之家" | ⬜ |
| 首页 description | `curl \| grep description` | 描述完整 | ⬜ |
| 歌曲页 title | `curl /songs \| grep title` | 包含"歌曲列表" | ⬜ |
| 热歌榜 title | `curl /songs/hot \| grep title` | 包含"热歌榜"或"排行榜" | ⬜ |
| OG 标签 | `curl \| grep og:` | 包含 og:title, og:description | ⬜ |
| Robots.txt | 访问 `/robots.txt` | 可访问，配置正确 | ⬜ |
| Sitemap | 访问 `/sitemap.xml` | 可访问，包含所有路由 | ⬜ |
| 结构化数据 | 查看源代码 | 包含 JSON-LD | ⬜ |

### 性能验收清单

| 指标 | 测试工具 | 当前值 | 目标值 | 状态 |
|------|----------|--------|--------|------|
| Lighthouse Performance | Lighthouse | 72 | ≥ 90 | ⬜ |
| Lighthouse SEO | Lighthouse | 65 | ≥ 95 | ⬜ |
| FCP | Lighthouse | 1.8s | ≤ 0.8s | ⬜ |
| LCP | Lighthouse | 2.5s | ≤ 1.2s | ⬜ |
| CLS | Lighthouse | 0.05 | ≤ 0.01 | ⬜ |
| TTFB | DevTools | 50ms | ≤ 80ms | ⬜ |
| 首屏 JS 体积 | DevTools | - | ≤ 200KB | ⬜ |
| 图片格式 | DevTools Network | - | WebP/AVIF | ⬜ |

### 部署验收清单

| 检查项 | 测试方法 | 验收标准 | 状态 |
|--------|----------|----------|------|
| 本地构建 | `npm run build` | 构建成功 | ⬜ |
| 服务启动 | `node .next/standalone/server.js` | 服务可访问 | ⬜ |
| Nginx 代理 | 配置测试 | 反向代理正常 | ⬜ |
| 健康检查 | 访问 `/api/health` | 返回 200 | ⬜ |
| 环境变量 | 检查配置 | 生产环境变量正确 | ⬜ |
| 日志输出 | 查看日志 | 无异常错误 | ⬜ |
| 回滚测试 | 执行回滚 | 可快速回滚 | ⬜ |

---

## 🔄 回滚方案

### 回滚触发条件

- 生产环境出现严重功能故障
- Core Web Vitals 严重恶化
- SEO 评分大幅下降
- 用户投诉激增

### 回滚步骤

```bash
# 1. 切回原 React 版本分支
cd /home/yifeianyi/Desktop/xxm_fans_home/repo/xxm_fans_frontend
git checkout react-legacy  # 保留的原分支

# 2. 重新构建原版本
npm install
npm run build

# 3. 更新 Nginx 配置（如需要）
sudo systemctl reload nginx

# 4. 验证回滚（通过 Nginx 代理端口访问）
curl http://localhost:8080

# 5. 排查 Next.js 问题
# ...

# 6. 修复后重新部署
git checkout main
# 修复代码...
git push origin main
```

---

## 📈 项目时间线

```
Week 1: [████████░░░░░░░░░░░░] 环境准备 + 基础架构
Week 2: [░░░░░░░░████████░░░░] 静态页面 + 数据页面（前半）
Week 3: [░░░░░░░░░░░░░░████████] 数据页面（后半）+ 复杂页面
Week 4: [░░░░░░░░░░░░░░░░░░████] 测试优化 + 上线

Day 1-3:   Phase 1 - 环境准备
Day 4-9:   Phase 2 - 核心架构
Day 10-13: Phase 3 - 静态页面
Day 14-20: Phase 4 - 数据驱动页面
Day 21-24: Phase 5 - 复杂交互页面
Day 25-28: Phase 6 - 测试上线
```

---

## 🛠️ 开发环境使用指南

### 快速开始

```bash
# 1. 进入脚本目录
cd /home/yifeianyi/Desktop/xxm_fans_home/scripts

# 2. 启动开发环境（自动启动后端 + Next.js）
./dev_start_nextjs.sh

# 3. 访问 http://localhost:3000 开始开发
```

### 日常开发流程

```bash
# 终端 1：保持开发服务器运行
./dev_start_nextjs.sh

# 终端 2：查看日志
tail -f /tmp/nextjs_dev.log

# 终端 3：类型检查
cd repo/xxm_nextjs && npx tsc --noEmit

# 终端 4：构建测试
cd repo/xxm_nextjs && npm run build
```

### 停止开发

```bash
# 优雅停止所有服务
./dev_stop_nextjs.sh

# 或只停止 Next.js（保留后端）
ps aux | grep "next.*dev" | grep -v grep | awk '{print $2}' | xargs kill -TERM
```

### 故障排除

| 问题 | 原因 | 解决方案 |
|------|------|----------|
| 端口 3000 被占用 | 其他程序占用 | 脚本自动选择其他端口，或手动关闭占用程序 |
| 后端 API 无法访问 | Django 未启动 | 检查 `/tmp/backend_nextjs.log` |
| 类型错误 | TypeScript 配置问题 | 运行 `npx tsc --noEmit` 检查 |
| 构建失败 | 代码错误 | 检查 `npm run build` 输出 |

---

## 📝 变更日志

| 版本 | 日期 | 变更内容 |
|------|------|----------|
| v1.0 | 2026-02-18 | 初始版本，基于技术调研报告创建 |

---

**文档维护者**：开发团队  
**审核周期**：每周评审进度  
**关联 Issue**：Next.js 迁移项目
