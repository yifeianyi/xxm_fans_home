# TempSongListFrontend 项目结构重构方案

## 📋 文档信息

- **项目名称**: TempSongListFrontend（悠悠歌单前端模板）
- **文档版本**: v1.0
- **创建日期**: 2026-01-27
- **文档类型**: 架构重构方案

---

## 🎯 重构目标

### 核心目标
1. **高可扩展性**: 支持快速添加新歌手、新功能、新主题
2. **高可用性**: 提升代码健壮性、错误处理、性能优化
3. **高可读性**: 代码结构清晰、注释完善、易于维护

### 关键改进点
- 从单一 App.vue 拆分为模块化组件架构
- 引入状态管理和路由管理
- 统一 API 调用和错误处理
- 完善的类型定义和代码规范
- 优化构建配置和性能

---

## 📊 现状分析

### 当前项目结构

```
TempSongListFrontend/
├── public/                  # 静态资源
├── src/
│   ├── components/         # 组件（仅1个）
│   │   └── HeadIcon.vue   # 头像组件
│   ├── App.vue            # 主应用组件（640+行）
│   └── main.js            # 应用入口
├── .env                   # 环境变量配置
├── .env.example           # 环境变量示例
├── package.json           # 项目配置
├── vite.config.js         # Vite 配置
└── index.html             # HTML 入口
```

### 存在的问题

#### 1. **架构层面**
- ❌ **单文件过度臃肿**: App.vue 包含 640+ 行代码，违反单一职责原则
- ❌ **缺乏状态管理**: 所有状态分散在 setup 函数中，难以追踪和维护
- ❌ **无路由管理**: 虽然是单页应用，但缺乏路由概念，不利于未来扩展
- ❌ **缺乏分层架构**: 业务逻辑、UI 渲染、数据获取混在一起

#### 2. **代码质量**
- ❌ **类型安全缺失**: 使用 JavaScript 而非 TypeScript，缺乏类型检查
- ❌ **错误处理不完善**: 部分接口调用缺乏完善的错误处理
- ❌ **代码重复**: 筛选、搜索等功能存在重复逻辑
- ❌ **魔法数字**: 硬编码的数字（如 768）缺乏语义化

#### 3. **可维护性**
- ❌ **组件耦合度高**: 大型组件难以拆分和复用
- ❌ **配置分散**: 环境变量、API 路径、常量分散在各处
- ❌ **缺乏文档**: 关键逻辑缺乏注释和文档说明
- ❌ **测试缺失**: 无单元测试、集成测试

#### 4. **性能优化**
- ❌ **图片验证低效**: 多次图片验证未进行缓存
- ❌ **缺乏缓存机制**: API 响应无缓存策略
- ❌ **未使用虚拟滚动**: 大量数据列表未优化

#### 5. **开发体验**
- ❌ **缺乏代码规范**: 无 ESLint、Prettier 配置
- ❌ **调试困难**: 缺乏统一的日志和错误追踪
- ❌ **构建配置不完善**: 缺少生产环境优化配置

---

## 🏗️ 重构方案

### 1. 整体架构设计

采用 **分层架构 + 模块化设计**，参考业界最佳实践：

```
┌─────────────────────────────────────────┐
│         Presentation Layer              │
│  (UI Components, Pages, Views)          │
├─────────────────────────────────────────┤
│         Business Logic Layer            │
│  (Composables, Hooks, Services)         │
├─────────────────────────────────────────┤
│         Data Access Layer               │
│  (API Services, State Management)       │
├─────────────────────────────────────────┤
│         Infrastructure Layer            │
│  (Config, Utils, Constants)             │
└─────────────────────────────────────────┘
```

### 2. 新项目结构

```
TempSongListFrontend/
├── public/                           # 静态资源
│   ├── favicon.ico
│   └── images/                       # 默认图片资源
├── src/
│   ├── assets/                       # 资源文件
│   │   ├── styles/                   # 全局样式
│   │   │   ├── variables.scss        # CSS 变量
│   │   │   ├── mixins.scss           # 样式混入
│   │   │   ├── global.scss           # 全局样式
│   │   │   └── themes/               # 主题样式
│   │   │       ├── default.scss      # 默认主题
│   │   │       └── dark.scss         # 暗色主题
│   │   └── images/                   # 图片资源
│   │       ├── default-avatar.svg    # 默认头像
│   │       └── default-bg.svg        # 默认背景
│   │
│   ├── components/                   # 组件库
│   │   ├── common/                   # 通用组件
│   │   │   ├── AppHeader.vue         # 页面头部
│   │   │   ├── AppFooter.vue         # 页面底部
│   │   │   ├── LoadingSpinner.vue    # 加载动画
│   │   │   ├── ErrorAlert.vue        # 错误提示
│   │   │   └── HeadIcon.vue          # 头像组件（保留）
│   │   │
│   │   ├── features/                 # 功能组件
│   │   │   ├── songlist/             # 歌单相关
│   │   │   │   ├── SongTable.vue     # 歌曲表格
│   │   │   │   ├── SongFilters.vue   # 筛选器
│   │   │   │   ├── SongSearch.vue    # 搜索框
│   │   │   │   └── SongCard.vue      # 歌曲卡片（可选）
│   │   │   │
│   │   │   └── random/               # 盲盒功能
│   │   │       ├── RandomSongDialog.vue  # 盲盒弹窗
│   │   │       └── RandomSongButton.vue  # 盲盒按钮
│   │   │
│   │   └── layout/                   # 布局组件
│   │       ├── AppLayout.vue         # 主布局
│   │       └── BackgroundLayer.vue   # 背景层
│   │
│   ├── composables/                  # 组合式函数（业务逻辑）
│   │   ├── useArtist.ts              # 歌手相关逻辑
│   │   ├── useSongs.ts               # 歌曲数据逻辑
│   │   ├── useFilters.ts             # 筛选逻辑
│   │   ├── useSearch.ts              # 搜索逻辑
│   │   ├── useRandomSong.ts          # 盲盒逻辑
│   │   ├── useSiteSettings.ts        # 网站设置逻辑
│   │   ├── useImageVerification.ts   # 图片验证逻辑
│   │   └── useResponsive.ts          # 响应式逻辑
│   │
│   ├── services/                     # 服务层
│   │   ├── api/                      # API 服务
│   │   │   ├── client.ts             # HTTP 客户端
│   │   │   ├── songlistApi.ts        # 歌单 API
│   │   │   ├── artistApi.ts          # 歌手 API
│   │   │   └── settingsApi.ts        # 设置 API
│   │   │
│   │   ├── state/                    # 状态管理
│   │   │   ├── stores/               # Pinia stores
│   │   │   │   ├── artistStore.ts    # 歌手状态
│   │   │   │   ├── songStore.ts      # 歌曲状态
│   │   │   │   ├── filterStore.ts    # 筛选状态
│   │   │   │   └── uiStore.ts        # UI 状态
│   │   │   └── index.ts              # 状态管理入口
│   │   │
│   │   └── cache/                    # 缓存服务
│   │       ├── memoryCache.ts        # 内存缓存
│   │       └── imageCache.ts         # 图片缓存
│   │
│   ├── config/                       # 配置管理
│   │   ├── index.ts                  # 配置入口
│   │   ├── app.config.ts             # 应用配置
│   │   ├── api.config.ts             # API 配置
│   │   └── constants.ts              # 常量定义
│   │
│   ├── types/                        # 类型定义
│   │   ├── index.ts                  # 类型入口
│   │   ├── song.types.ts             # 歌曲类型
│   │   ├── artist.types.ts           # 歌手类型
│   │   ├── filter.types.ts           # 筛选类型
│   │   ├── api.types.ts              # API 类型
│   │   └── common.types.ts           # 通用类型
│   │
│   ├── utils/                        # 工具函数
│   │   ├── index.ts                  # 工具入口
│   │   ├── validators.ts             # 验证工具
│   │   ├── formatters.ts             # 格式化工具
│   │   ├── device.ts                 # 设备检测
│   │   ├── logger.ts                 # 日志工具
│   │   └── performance.ts            # 性能工具
│   │
│   ├── views/                        # 页面视图
│   │   ├── SongListView.vue          # 歌单列表页
│   │   └── ErrorView.vue             # 错误页
│   │
│   ├── router/                       # 路由管理
│   │   ├── index.ts                  # 路由配置
│   │   ├── guards.ts                 # 路由守卫
│   │   └── routes.ts                 # 路由定义
│   │
│   ├── App.vue                       # 应用根组件（简化）
│   └── main.ts                       # 应用入口
│
├── tests/                            # 测试目录
│   ├── unit/                         # 单元测试
│   │   ├── composables/              # 组合式函数测试
│   │   ├── services/                 # 服务测试
│   │   └── utils/                    # 工具函数测试
│   ├── components/                   # 组件测试
│   └── e2e/                          # E2E 测试
│
├── docs/                             # 项目文档
│   ├── ARCHITECTURE.md               # 架构文档
│   ├── API.md                        # API 文档
│   ├── DEPLOYMENT.md                 # 部署文档
│   └── DEVELOPMENT.md                # 开发文档
│
├── .env                              # 环境变量
├── .env.development                  # 开发环境
├── .env.production                   # 生产环境
├── .env.example                      # 环境变量示例
├── .eslintrc.js                      # ESLint 配置
├── .prettierrc                       # Prettier 配置
├── .editorconfig                     # 编辑器配置
├── tsconfig.json                     # TypeScript 配置
├── vite.config.ts                    # Vite 配置
├── vite.config.development.ts        # 开发环境配置
├── vite.config.production.ts         # 生产环境配置
├── package.json                      # 项目配置
├── README.md                         # 项目说明
└── nginx.example.conf                # Nginx 配置示例
```

### 3. 技术栈升级

#### 核心依赖更新

```json
{
  "dependencies": {
    "vue": "^3.4.0",                    // 升级到最新稳定版
    "element-plus": "^2.5.0",           // 升级到最新稳定版
    "vue-router": "^4.2.0",             // 新增：路由管理
    "pinia": "^2.1.0",                  // 新增：状态管理
    "axios": "^1.6.0",                  // 新增：HTTP 客户端
    "@vueuse/core": "^10.7.0"           // 新增：Vue 组合式工具库
  },
  "devDependencies": {
    "@vitejs/plugin-vue": "^5.0.0",
    "vite": "^5.0.0",
    "typescript": "^5.3.0",             // 新增：TypeScript
    "vue-tsc": "^1.8.0",                // 新增：Vue TypeScript 检查
    "@types/node": "^20.10.0",          // 新增：Node.js 类型
    "sass": "^1.69.0",                  // 新增：Sass 支持
    "eslint": "^8.56.0",                // 新增：代码检查
    "eslint-plugin-vue": "^9.19.0",     // 新增：Vue ESLint 插件
    "@typescript-eslint/parser": "^6.18.0",
    "@typescript-eslint/eslint-plugin": "^6.18.0",
    "prettier": "^3.1.0",               // 新增：代码格式化
    "prettier-plugin-scss": "^1.0.0",   // 新增：SCSS 格式化
    "vitest": "^1.1.0",                 // 新增：单元测试
    "@vue/test-utils": "^2.4.0",        // 新增：Vue 测试工具
    "cypress": "^13.6.0"                // 新增：E2E 测试
  }
}
```

#### 技术选择理由

| 技术 | 理由 |
|------|------|
| **TypeScript** | 提供类型安全，减少运行时错误，提升开发体验 |
| **Vue Router** | 支持路由管理，便于未来扩展多页面功能 |
| **Pinia** | 官方推荐的状态管理方案，替代 Vuex，更轻量 |
| **Axios** | 成熟的 HTTP 客户端，支持拦截器、请求取消等 |
| **@vueuse/core** | 提供丰富的组合式函数，减少重复代码 |
| **Vitest** | 与 Vite 深度集成的测试框架，性能优秀 |
| **ESLint + Prettier** | 统一代码风格，提升代码质量 |
| **Sass** | 提供变量、嵌套、混入等高级 CSS 功能 |

### 4. 核心模块设计

#### 4.1 类型定义（types/）

**song.types.ts**
```typescript
export interface Song {
  id: number
  song_name: string
  language: string
  singer: string
  style: string
  note: string | null
}

export interface SongFilters {
  language?: string
  style?: string
  search?: string
}

export interface PaginatedSongs {
  total: number
  page: number
  page_size: number
  results: Song[]
}
```

**artist.types.ts**
```typescript
export interface Artist {
  key: string
  name: string
}

export interface ArtistInfo {
  name: string
  description?: string
}

export interface DomainMapping {
  [domain: string]: string
}
```

**api.types.ts**
```typescript
export interface ApiResponse<T> {
  code: number
  message: string
  data: T
}

export interface ApiError {
  code: number
  message: string
  details?: any
}

export interface ApiRequestConfig {
  timeout?: number
  retries?: number
  cache?: boolean
}
```

#### 4.2 配置管理（config/）

**constants.ts**
```typescript
// 设备断点
export const BREAKPOINTS = {
  MOBILE: 768,
  TABLET: 992,
  DESKTOP: 1200,
} as const

// API 路径
export const API_PATHS = {
  SONGS: '/songs',
  LANGUAGES: '/languages',
  STYLES: '/styles',
  RANDOM_SONG: '/random-song',
  ARTIST_INFO: '/artist-info',
  SITE_SETTINGS: '/site-settings',
} as const

// 默认值
export const DEFAULTS = {
  ARTIST: 'youyou',
  HEAD_ICON: '/favicon.ico',
  BACKGROUND: 'linear-gradient(135deg, #8eb69b 0%, #f8b195 100%)',
  PAGE_SIZE: 50,
} as const

// 缓存时间（毫秒）
export const CACHE_DURATION = {
  SHORT: 5 * 60 * 1000,      // 5分钟
  MEDIUM: 15 * 60 * 1000,    // 15分钟
  LONG: 60 * 60 * 1000,      // 1小时
  IMAGE: 24 * 60 * 60 * 1000, // 24小时
} as const
```

**api.config.ts**
```typescript
import { API_PATHS, DEFAULTS } from './constants'

export const apiConfig = {
  baseURL: import.meta.env.VITE_API_BASE_URL || '/api/songlist',
  timeout: 10000,
  retries: 2,
  headers: {
    'Content-Type': 'application/json',
  },
} as const

export const getApiPath = (path: keyof typeof API_PATHS): string => {
  return API_PATHS[path]
}
```

#### 4.3 API 服务（services/api/）

**client.ts**
```typescript
import axios, { AxiosInstance, AxiosError, AxiosRequestConfig } from 'axios'
import { apiConfig } from '@/config/api.config'
import { ApiResponse, ApiError } from '@/types/api.types'
import { logger } from '@/utils/logger'

class ApiClient {
  private client: AxiosInstance

  constructor() {
    this.client = axios.create(apiConfig)
    this.setupInterceptors()
  }

  private setupInterceptors() {
    // 请求拦截器
    this.client.interceptors.request.use(
      (config) => {
        logger.debug('API Request:', config.method?.toUpperCase(), config.url)
        return config
      },
      (error) => {
        logger.error('API Request Error:', error)
        return Promise.reject(error)
      }
    )

    // 响应拦截器
    this.client.interceptors.response.use(
      (response) => {
        logger.debug('API Response:', response.status, response.config.url)
        return response.data
      },
      (error: AxiosError<ApiError>) => {
        const errorMessage = this.handleError(error)
        logger.error('API Response Error:', errorMessage)
        return Promise.reject(new Error(errorMessage))
      }
    )
  }

  private handleError(error: AxiosError<ApiError>): string {
    if (error.response) {
      const { data, status } = error.response
      return data?.message || `请求失败: ${status}`
    } else if (error.request) {
      return '网络错误，请检查网络连接'
    } else {
      return error.message || '未知错误'
    }
  }

  async get<T>(url: string, config?: AxiosRequestConfig): Promise<ApiResponse<T>> {
    return this.client.get(url, config)
  }

  async post<T>(url: string, data?: any, config?: AxiosRequestConfig): Promise<ApiResponse<T>> {
    return this.client.post(url, data, config)
  }
}

export const apiClient = new ApiClient()
```

**songlistApi.ts**
```typescript
import { apiClient } from './client'
import { getApiPath } from '@/config/api.config'
import { Song, SongFilters, PaginatedSongs } from '@/types/song.types'
import { ApiResponse } from '@/types/api.types'

export const songlistApi = {
  // 获取歌曲列表
  async getSongs(filters: SongFilters & { artist: string }): Promise<Song[]> {
    const params = new URLSearchParams()
    Object.entries(filters).forEach(([key, value]) => {
      if (value) params.append(key, String(value))
    })

    const response = await apiClient.get<Song[]>(
      `${getApiPath('SONGS')}?${params.toString()}`
    )
    return response.data as Song[]
  },

  // 获取语言列表
  async getLanguages(artist: string): Promise<string[]> {
    const response = await apiClient.get<string[]>(
      `${getApiPath('LANGUAGES')}?artist=${artist}`
    )
    return response.data as string[]
  },

  // 获取曲风列表
  async getStyles(artist: string): Promise<string[]> {
    const response = await apiClient.get<string[]>(
      `${getApiPath('STYLES')}?artist=${artist}`
    )
    return response.data as string[]
  },

  // 获取随机歌曲
  async getRandomSong(filters: SongFilters & { artist: string }): Promise<Song | null> {
    const params = new URLSearchParams()
    Object.entries(filters).forEach(([key, value]) => {
      if (value) params.append(key, String(value))
    })

    try {
      const response = await apiClient.get<Song>(
        `${getApiPath('RANDOM_SONG')}?${params.toString()}`
      )
      return response.data as Song
    } catch (error) {
      if ((error as any).message?.includes('404')) {
        return null
      }
      throw error
    }
  },
}
```

#### 4.4 组合式函数（composables/）

**useArtist.ts**
```typescript
import { ref, computed, watch } from 'vue'
import { Artist, DomainMapping, ArtistInfo } from '@/types/artist.types'
import { DEFAULTS } from '@/config/constants'
import { artistApi } from '@/services/api/artistApi'
import { logger } from '@/utils/logger'

export function useArtist() {
  const currentArtist = ref<Artist['key']>(getArtistFromDomain())
  const artistInfo = ref<ArtistInfo | null>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)

  const siteTitle = computed(() => {
    return artistInfo.value ? `${artistInfo.value.name}的歌单` : `${currentArtist.value}的歌单`
  })

  // 根据域名获取歌手标识
  function getArtistFromDomain(): Artist['key'] {
    // 优先检查 URL 参数
    const urlParams = new URLSearchParams(window.location.search)
    const artistFromUrl = urlParams.get('artist')
    if (artistFromUrl) {
      logger.info('使用 URL 参数 artist:', artistFromUrl)
      return artistFromUrl
    }

    const hostname = window.location.hostname
    const port = window.location.port
    const fullHostname = port ? `${hostname}:${port}` : hostname

    // 从环境变量获取域名映射
    let domainMappings: DomainMapping = {}
    try {
      const mappings = import.meta.env.VITE_DOMAIN_MAPPINGS
      if (typeof mappings === 'object' && mappings !== null) {
        domainMappings = mappings
      } else if (typeof mappings === 'string') {
        domainMappings = JSON.parse(mappings)
      }
    } catch (e) {
      logger.error('解析域名映射失败:', e)
    }

    // 检查完整域名匹配
    if (domainMappings[fullHostname]) {
      logger.info('使用完整域名匹配:', domainMappings[fullHostname])
      return domainMappings[fullHostname]
    }

    // 检查仅主机名匹配
    if (domainMappings[hostname]) {
      logger.info('使用主机名匹配:', domainMappings[hostname])
      return domainMappings[hostname]
    }

    // 使用默认值
    logger.info('使用默认值:', DEFAULTS.ARTIST)
    return DEFAULTS.ARTIST
  }

  // 获取歌手信息
  async function fetchArtistInfo() {
    loading.value = true
    error.value = null

    try {
      artistInfo.value = await artistApi.getArtistInfo(currentArtist.value)
      document.title = siteTitle.value
    } catch (err) {
      error.value = '获取歌手信息失败'
      logger.error('获取歌手信息失败:', err)
      // 使用默认值
      artistInfo.value = { name: currentArtist.value }
      document.title = siteTitle.value
    } finally {
      loading.value = false
    }
  }

  // 更新歌手
  function updateArtist(artist: Artist['key']) {
    if (artist !== currentArtist.value) {
      currentArtist.value = artist
      fetchArtistInfo()
    }
  }

  // 监听 currentArtist 变化
  watch(currentArtist, (newArtist) => {
    logger.info('currentArtist 变化:', newArtist)
    fetchArtistInfo()
  })

  return {
    currentArtist,
    artistInfo,
    siteTitle,
    loading,
    error,
    getArtistFromDomain,
    fetchArtistInfo,
    updateArtist,
  }
}
```

**useSongs.ts**
```typescript
import { ref, computed } from 'vue'
import { Song, SongFilters } from '@/types/song.types'
import { songlistApi } from '@/services/api/songlistApi'
import { useArtist } from './useArtist'
import { logger } from '@/utils/logger'

export function useSongs() {
  const { currentArtist } = useArtist()

  const songs = ref<Song[]>([])
  const filteredSongs = ref<Song[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)

  // 获取歌曲列表
  async function fetchSongs() {
    loading.value = true
    error.value = null

    try {
      songs.value = await songlistApi.getSongs({ artist: currentArtist.value })
      filteredSongs.value = [...songs.value]
      logger.info('获取歌曲列表成功:', songs.value.length)
    } catch (err) {
      error.value = '获取歌曲列表失败'
      logger.error('获取歌曲列表失败:', err)
    } finally {
      loading.value = false
    }
  }

  // 筛选歌曲
  async function filterSongs(filters: SongFilters) {
    loading.value = true
    error.value = null

    try {
      filteredSongs.value = await songlistApi.getSongs({
        artist: currentArtist.value,
        ...filters,
      })
      logger.info('筛选歌曲成功:', filteredSongs.value.length)
    } catch (err) {
      error.value = '筛选歌曲失败'
      logger.error('筛选歌曲失败:', err)
    } finally {
      loading.value = false
    }
  }

  // 重置筛选
  function resetFilters() {
    filteredSongs.value = [...songs.value]
  }

  return {
    songs,
    filteredSongs,
    loading,
    error,
    fetchSongs,
    filterSongs,
    resetFilters,
  }
}
```

**useRandomSong.ts**
```typescript
import { ref } from 'vue'
import { Song, SongFilters } from '@/types/song.types'
import { songlistApi } from '@/services/api/songlistApi'
import { useArtist } from './useArtist'
import { logger } from '@/utils/logger'

export function useRandomSong() {
  const { currentArtist } = useArtist()

  const showRandomSongDialog = ref(false)
  const randomSong = ref<Song | null>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)

  // 获取随机歌曲
  async function getRandomSong(filters: SongFilters) {
    loading.value = true
    error.value = null

    try {
      randomSong.value = await songlistApi.getRandomSong({
        artist: currentArtist.value,
        ...filters,
      })
      showRandomSongDialog.value = true
      logger.info('获取随机歌曲成功:', randomSong.value?.song_name)
    } catch (err) {
      error.value = '获取随机歌曲失败'
      randomSong.value = null
      showRandomSongDialog.value = true
      logger.error('获取随机歌曲失败:', err)
    } finally {
      loading.value = false
    }
  }

  // 关闭弹窗
  function closeDialog() {
    showRandomSongDialog.value = false
    randomSong.value = null
  }

  return {
    showRandomSongDialog,
    randomSong,
    loading,
    error,
    getRandomSong,
    closeDialog,
  }
}
```

#### 4.5 组件拆分

**App.vue（简化后）**
```vue
<template>
  <AppLayout>
    <template #background>
      <BackgroundLayer :url="backgroundUrl" />
    </template>

    <template #header>
      <AppHeader>
        <HeadIcon v-if="headIconUrl" :url="headIconUrl" />
        <h1>{{ siteTitle }}</h1>
      </AppHeader>
    </template>

    <template #content>
      <LoadingSpinner v-if="loading" />
      <ErrorAlert v-else-if="error" :message="error" />
      <SongListView v-else />
    </template>
  </AppLayout>

  <RandomSongDialog
    v-model:show="showRandomSongDialog"
    :song="randomSong"
    @retry="handleRetry"
  />
</template>

<script setup lang="ts">
import { computed, onMounted, watch } from 'vue'
import AppLayout from '@/components/layout/AppLayout.vue'
import BackgroundLayer from '@/components/layout/BackgroundLayer.vue'
import AppHeader from '@/components/common/AppHeader.vue'
import HeadIcon from '@/components/common/HeadIcon.vue'
import LoadingSpinner from '@/components/common/LoadingSpinner.vue'
import ErrorAlert from '@/components/common/ErrorAlert.vue'
import SongListView from '@/views/SongListView.vue'
import RandomSongDialog from '@/components/features/random/RandomSongDialog.vue'

import { useArtist } from '@/composables/useArtist'
import { useSiteSettings } from '@/composables/useSiteSettings'
import { useRandomSong } from '@/composables/useRandomSong'
import { useSongFilters } from '@/composables/useSongFilters'

// 组合式函数
const { currentArtist, siteTitle, loading: artistLoading, fetchArtistInfo } = useArtist()
const { headIconUrl, backgroundUrl, loading: settingsLoading, fetchSiteSettings } = useSiteSettings()
const { showRandomSongDialog, randomSong, getRandomSong, closeDialog } = useRandomSong()
const { filters, resetFilters } = useSongFilters()

// 计算属性
const loading = computed(() => artistLoading.value || settingsLoading.value)
const error = computed(() => {
  if (artistLoading.error) return artistLoading.error
  if (settingsLoading.error) return settingsLoading.error
  return null
})

// 方法
async function handleRetry() {
  await getRandomSong(filters.value)
}

// 生命周期
onMounted(async () => {
  await Promise.all([
    fetchArtistInfo(),
    fetchSiteSettings(),
  ])
})

// 监听歌手变化
watch(currentArtist, async (newArtist) => {
  if (newArtist) {
    await Promise.all([
      fetchArtistInfo(),
      fetchSiteSettings(),
    ])
  }
})
</script>

<style scoped>
#app {
  @apply min-h-screen relative overflow-hidden;
}
</style>
```

**SongFilters.vue**
```vue
<template>
  <div class="filters-container">
    <div class="filters-wrapper">
      <div class="filters">
        <LanguageSelect
          v-model="filters.language"
          :languages="languages"
          @change="handleFilterChange"
        />

        <StyleSelect
          v-model="filters.style"
          :styles="styles"
          @change="handleFilterChange"
        />

        <SongSearch
          v-model="filters.search"
          @search="handleSearch"
          @clear="handleClear"
        />

        <div class="button-container">
          <el-button @click="handleReset" type="warning" class="reset-button">
            重置
          </el-button>
          <el-button @click="handleRandom" type="success" class="random-button">
            盲盒
          </el-button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import LanguageSelect from './LanguageSelect.vue'
import StyleSelect from './StyleSelect.vue'
import SongSearch from './SongSearch.vue'
import { useSongFilters } from '@/composables/useSongFilters'
import { useFiltersData } from '@/composables/useFiltersData'

// 组合式函数
const { filters, updateFilters, resetFilters } = useSongFilters()
const { languages, styles, loading } = useFiltersData()

// 方法
function handleFilterChange() {
  emit('filter', filters.value)
}

function handleSearch() {
  emit('search', filters.value)
}

function handleClear() {
  filters.value.search = ''
  emit('clear')
}

function handleReset() {
  resetFilters()
  emit('reset')
}

function handleRandom() {
  emit('random', filters.value)
}

// 事件
const emit = defineEmits<{
  filter: [filters: SongFilters]
  search: [filters: SongFilters]
  clear: []
  reset: []
  random: [filters: SongFilters]
}>()
</script>

<style scoped lang="scss">
.filters-container {
  @apply max-w-7xl mx-4 mb-5 w-full;

  @media (min-width: 768px) {
    @apply mx-auto;
  }
}

.filters-wrapper {
  @apply w-full;
}

.filters {
  @apply flex gap-4 items-center flex-nowrap bg-white/85 p-4 rounded-lg shadow-sm;

  @media (max-width: 768px) {
    @apply flex-col items-stretch gap-2.5;
  }
}

.button-container {
  @apply flex gap-2 shrink-0 min-w-40;

  @media (max-width: 768px) {
    @apply w-full;
  }
}

.reset-button,
.random-button {
  @apply shrink-0 min-w-20;

  @media (max-width: 768px) {
    @apply flex-1;
  }
}
</style>
```

#### 4.6 路由管理

**routes.ts**
```typescript
import type { RouteRecordRaw } from 'vue-router'

const routes: RouteRecordRaw[] = [
  {
    path: '/',
    name: 'SongList',
    component: () => import('@/views/SongListView.vue'),
    meta: {
      title: '歌单列表',
      requiresAuth: false,
    },
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: () => import('@/views/ErrorView.vue'),
    meta: {
      title: '页面不存在',
    },
  },
]

export default routes
```

### 5. 性能优化方案

#### 5.1 构建优化

**vite.config.production.ts**
```typescript
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { resolve } from 'path'
import { visualizer } from 'rollup-plugin-visualizer'
import viteCompression from 'vite-plugin-compression'

export default defineConfig({
  plugins: [
    vue(),
    // Gzip 压缩
    viteCompression({
      algorithm: 'gzip',
      ext: '.gz',
      threshold: 10240, // 10KB 以上才压缩
    }),
    // Brotli 压缩
    viteCompression({
      algorithm: 'brotliCompress',
      ext: '.br',
      threshold: 10240,
    }),
    // 打包可视化
    visualizer({
      open: false,
      gzipSize: true,
      brotliSize: true,
    }),
  ],
  build: {
    target: 'es2020',
    minify: 'terser',
    terserOptions: {
      compress: {
        drop_console: true, // 生产环境移除 console
        drop_debugger: true,
      },
    },
    rollupOptions: {
      output: {
        manualChunks: {
          'vue-vendor': ['vue', 'vue-router', 'pinia'],
          'element-plus': ['element-plus'],
          'axios': ['axios'],
        },
        chunkFileNames: 'assets/js/[name]-[hash].js',
        entryFileNames: 'assets/js/[name]-[hash].js',
        assetFileNames: 'assets/[ext]/[name]-[hash].[ext]',
      },
    },
    chunkSizeWarningLimit: 1000,
  },
})
```

#### 5.2 缓存策略

**cache/imageCache.ts**
```typescript
import { CACHE_DURATION } from '@/config/constants'
import { logger } from '@/utils/logger'

interface CacheEntry {
  url: string
  loaded: boolean
  timestamp: number
}

class ImageCache {
  private cache = new Map<string, CacheEntry>()
  private loading = new Map<string, Promise<boolean>>()

  async verifyImage(url: string): Promise<boolean> {
    const cached = this.cache.get(url)

    // 检查缓存
    if (cached) {
      const isExpired = Date.now() - cached.timestamp > CACHE_DURATION.IMAGE
      if (!isExpired) {
        logger.debug('使用缓存的图片验证结果:', url, cached.loaded)
        return cached.loaded
      }
    }

    // 检查是否正在加载
    if (this.loading.has(url)) {
      logger.debug('等待图片验证完成:', url)
      return this.loading.get(url)!
    }

    // 开始验证
    const promise = new Promise<boolean>((resolve) => {
      const img = new Image()
      img.onload = () => {
        this.cache.set(url, { url, loaded: true, timestamp: Date.now() })
        logger.info('图片加载成功:', url)
        resolve(true)
      }
      img.onerror = () => {
        this.cache.set(url, { url, loaded: false, timestamp: Date.now() })
        logger.warn('图片加载失败:', url)
        resolve(false)
      }
      img.src = url
    })

    this.loading.set(url, promise)
    const result = await promise
    this.loading.delete(url)

    return result
  }

  clear() {
    this.cache.clear()
    this.loading.clear()
    logger.info('图片缓存已清空')
  }
}

export const imageCache = new ImageCache()
```

#### 5.3 虚拟滚动

对于大量歌曲列表，使用虚拟滚动优化性能：

```vue
<template>
  <VirtualList
    :data-sources="filteredSongs"
    :data-key="'id'"
    :keeps="30"
    :estimate-size="50"
  >
    <template #default="{ source }">
      <SongItem :song="source" />
    </template>
  </VirtualList>
</template>

<script setup lang="ts">
import { VirtualList } from 'vue-virtual-scroll-list'
import SongItem from './SongItem.vue'
</script>
```

### 6. 错误处理方案

#### 6.1 统一错误处理

**utils/errorHandler.ts**
```typescript
export class AppError extends Error {
  constructor(
    message: string,
    public code?: string,
    public details?: any
  ) {
    super(message)
    this.name = 'AppError'
  }
}

export function handleError(error: unknown): AppError {
  if (error instanceof AppError) {
    return error
  }

  if (error instanceof Error) {
    return new AppError(error.message)
  }

  if (typeof error === 'string') {
    return new AppError(error)
  }

  return new AppError('未知错误')
}

export function isNetworkError(error: unknown): boolean {
  if (error instanceof AppError) {
    return error.code === 'NETWORK_ERROR'
  }
  return false
}
```

#### 6.2 全局错误捕获

**main.ts**
```typescript
import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'
import { logger } from './utils/logger'
import { handleError } from './utils/errorHandler'

const app = createApp(App)
const pinia = createPinia()

app.use(pinia)
app.use(router)

// 全局错误处理
app.config.errorHandler = (err, instance, info) => {
  const error = handleError(err)
  logger.error('全局错误:', error.message, info)
  // 可以在这里上报到错误追踪服务
}

// 未捕获的 Promise 错误
window.addEventListener('unhandledrejection', (event) => {
  const error = handleError(event.reason)
  logger.error('未捕获的 Promise 错误:', error.message)
  event.preventDefault()
})

app.mount('#app')
```

### 7. 测试方案

#### 7.1 单元测试

**tests/unit/composables/useSongs.test.ts**
```typescript
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { useSongs } from '@/composables/useSongs'
import { songlistApi } from '@/services/api/songlistApi'
import { ref } from 'vue'

vi.mock('@/services/api/songlistApi')

describe('useSongs', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('应该成功获取歌曲列表', async () => {
    const mockSongs = [
      { id: 1, song_name: '歌曲1', language: '中文', singer: '歌手1', style: '流行', note: null },
      { id: 2, song_name: '歌曲2', language: '英文', singer: '歌手2', style: '摇滚', note: '备注' },
    ]
    vi.mocked(songlistApi.getSongs).mockResolvedValue(mockSongs)

    const { songs, loading, fetchSongs } = useSongs()
    await fetchSongs()

    expect(loading.value).toBe(false)
    expect(songs.value).toEqual(mockSongs)
  })

  it('应该处理获取歌曲失败', async () => {
    vi.mocked(songlistApi.getSongs).mockRejectedValue(new Error('网络错误'))

    const { error, fetchSongs } = useSongs()
    await fetchSongs()

    expect(error.value).toBe('获取歌曲列表失败')
  })
})
```

#### 7.2 组件测试

**tests/components/SongFilters.test.ts**
```typescript
import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import SongFilters from '@/components/features/songlist/SongFilters.vue'

describe('SongFilters', () => {
  it('应该正确渲染筛选器', () => {
    const wrapper = mount(SongFilters, {
      props: {
        languages: ['中文', '英文'],
        styles: ['流行', '摇滚'],
      },
    })

    expect(wrapper.find('.filters-container').exists()).toBe(true)
  })

  it('应该在重置时触发 reset 事件', async () => {
    const wrapper = mount(SongFilters)
    await wrapper.find('.reset-button').trigger('click')
    expect(wrapper.emitted('reset')).toBeTruthy()
  })
})
```

### 8. 开发规范

#### 8.1 代码规范

**.eslintrc.js**
```javascript
module.exports = {
  root: true,
  env: {
    browser: true,
    es2021: true,
    node: true,
  },
  extends: [
    'eslint:recommended',
    'plugin:vue/vue3-recommended',
    'plugin:@typescript-eslint/recommended',
    'prettier',
  ],
  parser: 'vue-eslint-parser',
  parserOptions: {
    ecmaVersion: 'latest',
    parser: '@typescript-eslint/parser',
    sourceType: 'module',
  },
  plugins: ['vue', '@typescript-eslint'],
  rules: {
    'vue/multi-word-component-names': 'off',
    '@typescript-eslint/no-explicit-any': 'warn',
    '@typescript-eslint/no-unused-vars': ['error', { argsIgnorePattern: '^_' }],
    'no-console': process.env.NODE_ENV === 'production' ? 'warn' : 'off',
  },
}
```

**.prettierrc**
```json
{
  "semi": false,
  "singleQuote": true,
  "printWidth": 100,
  "trailingComma": "es5",
  "arrowParens": "always",
  "endOfLine": "lf"
}
```

#### 8.2 命名规范

- **组件文件**: PascalCase（如 `SongList.vue`）
- **组合式函数**: camelCase，以 `use` 开头（如 `useSongs.ts`）
- **工具函数**: camelCase（如 `formatDate.ts`）
- **常量**: UPPER_SNAKE_CASE（如 `API_BASE_URL`）
- **类型定义**: PascalCase（如 `Song.ts`）
- **接口定义**: PascalCase，以 `I` 开头（可选）

#### 8.3 注释规范

```typescript
/**
 * 获取歌曲列表
 * @param filters - 筛选条件
 * @returns 歌曲列表
 * @throws {AppError} 当网络请求失败时抛出错误
 * @example
 * ```ts
 * const songs = await fetchSongs({ language: '中文' })
 * ```
 */
async function fetchSongs(filters: SongFilters): Promise<Song[]> {
  // 实现
}
```

---

## 📅 实施计划

### 阶段一：基础设施搭建（1-2天）

1. **升级技术栈**
   - [ ] 安装 TypeScript
   - [ ] 安装 Vue Router
   - [ ] 安装 Pinia
   - [ ] 安装 Axios
   - [ ] 安装 @vueuse/core
   - [ ] 安装 ESLint、Prettier
   - [ ] 配置 tsconfig.json
   - [ ] 配置 .eslintrc.js
   - [ ] 配置 .prettierrc

2. **创建项目结构**
   - [ ] 创建目录结构
   - [ ] 创建类型定义文件
   - [ ] 创建配置文件
   - [ ] 创建工具函数

### 阶段二：核心模块开发（3-5天）

1. **API 服务层**
   - [ ] 实现 ApiClient
   - [ ] 实现 songlistApi
   - [ ] 实现 artistApi
   - [ ] 实现 settingsApi

2. **组合式函数**
   - [ ] 实现 useArtist
   - [ ] 实现 useSongs
   - [ ] 实现 useFilters
   - [ ] 实现 useRandomSong
   - [ ] 实现 useSiteSettings
   - [ ] 实现 useImageVerification

3. **状态管理**
   - [ ] 创建 artistStore
   - [ ] 创建 songStore
   - [ ] 创建 filterStore
   - [ ] 创建 uiStore

### 阶段三：组件开发（3-4天）

1. **通用组件**
   - [ ] 实现 AppHeader
   - [ ] 实现 AppFooter
   - [ ] 实现 LoadingSpinner
   - [ ] 实现 ErrorAlert
   - [ ] 重构 HeadIcon

2. **布局组件**
   - [ ] 实现 AppLayout
   - [ ] 实现 BackgroundLayer

3. **功能组件**
   - [ ] 实现 SongTable
   - [ ] 实现 SongFilters
   - [ ] 实现 SongSearch
   - [ ] 实现 RandomSongDialog

4. **页面组件**
   - [ ] 实现 SongListView
   - [ ] 实现 ErrorView

### 阶段四：路由和集成（1-2天）

1. **路由配置**
   - [ ] 配置路由
   - [ ] 实现路由守卫
   - [ ] 配置页面标题

2. **应用集成**
   - [ ] 重构 App.vue
   - [ ] 重构 main.ts
   - [ ] 配置全局样式

### 阶段五：性能优化（2-3天）

1. **构建优化**
   - [ ] 配置生产环境构建
   - [ ] 配置代码分割
   - [ ] 配置压缩

2. **缓存优化**
   - [ ] 实现图片缓存
   - [ ] 实现 API 响应缓存

3. **性能监控**
   - [ ] 添加性能指标收集
   - [ ] 添加错误追踪

### 阶段六：测试和文档（2-3天）

1. **单元测试**
   - [ ] 编写组合式函数测试
   - [ ] 编写服务层测试
   - [ ] 编写工具函数测试

2. **组件测试**
   - [ ] 编写组件测试

3. **文档编写**
   - [ ] 更新 README.md
   - [ ] 编写架构文档
   - [ ] 编写 API 文档
   - [ ] 编写部署文档

### 阶段七：部署和验证（1-2天）

1. **部署准备**
   - [ ] 配置环境变量
   - [ ] 配置 Nginx
   - [ ] 配置 CI/CD

2. **测试验证**
   - [ ] 功能测试
   - [ ] 性能测试
   - [ ] 兼容性测试

**总计**: 13-21 天

---

## 🎯 预期收益

### 1. 可扩展性提升

- ✅ 添加新歌手：通过配置文件即可，无需修改代码
- ✅ 添加新功能：基于模块化设计，新功能独立开发
- ✅ 添加新主题：通过 CSS 变量和主题文件快速切换
- ✅ 支持多语言：预留 i18n 接口

### 2. 可用性提升

- ✅ 错误处理：统一的错误处理机制，提升用户体验
- ✅ 性能优化：缓存、虚拟滚动、代码分割，提升性能
- ✅ 响应式设计：完善的移动端适配
- ✅ 容错能力：完善的降级方案

### 3. 可读性提升

- ✅ 代码结构：清晰的分层架构，易于理解
- ✅ 类型安全：TypeScript 提供类型检查
- ✅ 代码规范：统一的代码风格
- ✅ 文档完善：详细的注释和文档

### 4. 可维护性提升

- ✅ 模块化：功能独立，易于维护
- ✅ 测试覆盖：完善的测试体系
- ✅ 工具链：自动化的代码检查和格式化
- ✅ 监控体系：完善的错误追踪和性能监控

---

## 📝 注意事项

### 1. 向后兼容

- 重构过程中保持现有功能正常运行
- 分阶段迁移，避免一次性大规模改动
- 保留关键接口的兼容性

### 2. 性能考虑

- 避免过度设计
- 合理使用缓存
- 优化首屏加载速度

### 3. 团队协作

- 制定清晰的开发规范
- 建立代码审查机制
- 定期进行技术分享

### 4. 风险控制

- 重构前备份现有代码
- 使用 Git 分支管理
- 每个阶段完成后进行测试

---

## 📚 参考资料

- [Vue 3 官方文档](https://vuejs.org/)
- [Vue Router 官方文档](https://router.vuejs.org/)
- [Pinia 官方文档](https://pinia.vuejs.org/)
- [TypeScript 官方文档](https://www.typescriptlang.org/)
- [Vite 官方文档](https://vitejs.dev/)
- [Element Plus 官方文档](https://element-plus.org/)
- [VueUse 官方文档](https://vueuse.org/)
- [Vue 风格指南](https://vuejs.org/style-guide/)

---

## 🔗 相关文档

- [Vue 3 组合式函数最佳实践](https://vuejs.org/guide/reusability/composables.html)
- [TypeScript 最佳实践](https://www.typescriptlang.org/docs/handbook/declaration-files/do-s-and-don-ts.html)
- [前端性能优化指南](https://web.dev/fast/)
- [Vue 3 项目结构推荐](https://vuejs.org/guide/scaling-up/project-structure.html)

---

**文档维护**: 本文档应随着项目发展持续更新
**最后更新**: 2026-01-27
**维护者**: 开发团队