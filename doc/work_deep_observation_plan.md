# "作品深度观测" 功能执行计划

## 一、需求概述

在"满の数据"页面中，实现"作品深度观测"模块。用户选择某个作品后，展示两个标签页：

- **tag1「发布后一周」**：展示作品发布后 7 天内的小时级数据变化趋势折线图。若该作品无发布一周内的爬取数据，标签置灰不可点击。
- **tag2「累计日线」**：按天聚合作品全生命周期的数据点，描绘成折线图。

两个标签页内均支持切换六种指标：播放量、点赞、投币、收藏、弹幕、评论。

---

## 二、后端开发计划

### 任务 1：新增作品时间线聚合 Service 方法

**文件**：`repo/xxm_fans_backend/data_analytics/services/analytics_service.py`

- 新增 `get_work_timeline(platform, work_id)` 静态方法
- 从 `WorkStatic` 获取 `publish_time`
- 从 `WorkMetricsHour` 获取该作品全部小时级数据，按 `crawl_time` 正序排列
- **tag1 数据**：筛选 `crawl_time <= publish_time + 7天` 的原始记录；若结果为空，标记 `has_week_data = false`
- **tag2 数据**：按天聚合，每天取 `crawl_time` 最晚的一条记录作为当日数据点
- 返回结构：`{ has_week_data, week_series, daily_series }`

### 任务 2：新增时间线 API View

**文件**：`repo/xxm_fans_backend/data_analytics/api/views.py`

- 新增 `WorkTimelineView`，接收路径参数 `platform` + `work_id`
- 调用 `AnalyticsService.get_work_timeline()`
- 使用 `success_response()` 返回统一格式

### 任务 3：新增序列化器

**文件**：`repo/xxm_fans_backend/data_analytics/api/serializers.py`

- 新增 `TimelinePointSerializer`，字段：`time`, `view_count`, `like_count`, `coin_count`, `favorite_count`, `danmaku_count`, `comment_count`
- 新增 `WorkTimelineSerializer`，字段：`has_week_data` (boolean), `week_series` (TimelinePointSerializer[]), `daily_series` (TimelinePointSerializer[])

### 任务 4：注册路由

**文件**：`repo/xxm_fans_backend/data_analytics/urls.py`

- 新增 `path('works/<str:platform>/<str:work_id>/timeline/', WorkTimelineView.as_view(), name='work-timeline')`

---

## 三、前端类型定义计划

### 任务 5：扩展领域类型

**文件**：`repo/xxm_fans_frontend/domain/types.ts`

- 新增 `TimelinePoint` 接口：
  ```ts
  interface TimelinePoint {
    time: string;
    viewCount: number;
    likeCount: number;
    coinCount: number;
    favoriteCount: number;
    danmakuCount: number;
    commentCount: number;
  }
  ```
- 新增 `WorkTimelineResponse` 接口：
  ```ts
  interface WorkTimelineResponse {
    hasWeekData: boolean;
    weekSeries: TimelinePoint[];
    dailySeries: TimelinePoint[];
  }
  ```

---

## 四、前端基础设施计划

### 任务 6：新增 API 调用方法

**文件**：`repo/xxm_fans_frontend/infrastructure/api/RealSongService.ts`

- 在 `RealSongService` 新增 `getWorkTimeline(platform, workId): Promise<ApiResult<WorkTimelineResponse>>`
- 请求端点：`/data-analytics/works/${platform}/${workId}/timeline/`

---

## 五、前端组件开发计划

### 任务 7：创建作品选择器组件

**文件**：`repo/xxm_fans_frontend/presentation/pages/DataAnalysisPage/components/WorkSelector.tsx`

- 调用已有接口 `GET /api/data-analytics/works/?limit=100&platform=bilibili`
- 下拉列表展示作品标题 + 发布时间
- 选中后回调 `onSelect(platform, workId)` 给父组件

### 任务 8：创建"作品深度观测"主组件

**文件**：`repo/xxm_fans_frontend/presentation/pages/DataAnalysisPage/components/WorkDeepObservation.tsx`

内部结构：
- 顶部：`WorkSelector`
- 中部：两个标签页按钮 `[发布后一周]` `[累计日线]`
- 标签页按钮样式：
  - tag1：根据 `has_week_data` 决定样式，无数据时置灰并禁用点击
  - tag2：始终可点击
- 底部：图表展示区域，默认展示 tag2

### 任务 9：扩展 TrendChart 以支持多指标切换

**文件**：`repo/xxm_fans_frontend/presentation/pages/DataAnalysisPage/components/TrendChart.tsx`

- 修改 Props：支持传入指标切换按钮组 `[播放] [点赞] [投币] [收藏] [弹幕] [评论]`
- 图表内根据当前选中指标渲染对应字段
- tag1 模式：横轴为 `crawl_time`（精确到小时），展示每小时原始值折线
- tag2 模式：横轴为日期，展示日线折线

### 任务 10：更新组件导出索引

**文件**：`repo/xxm_fans_frontend/presentation/pages/DataAnalysisPage/components/index.ts`

- 导出 `WorkSelector`、`WorkDeepObservation`

---

## 六、页面集成计划

### 任务 11：替换 DataAnalysisPage 占位符

**文件**：`repo/xxm_fans_frontend/presentation/pages/DataAnalysisPage/index.tsx`

- 删除 `ComingSoonSection`（title="作品深度观测"）
- 替换为 `<WorkDeepObservation />`
- 保持 `OverviewSection` 和第二个 `ComingSoonSection`（增长关联性实验室）不动

---

## 七、验收标准

| 验收项 | 标准 |
|-------|------|
| tag1 置灰 | 作品发布后 7 天内无任何爬取数据时，`[发布后一周]` 按钮为灰色不可点击状态 |
| tag1 图表 | 有数据时，展示发布后 7 天内每小时的数据折线，横轴显示日期+小时 |
| tag2 图表 | 展示作品全生命周期按天聚合的折线，每天一个数据点，横轴显示日期 |
| 指标切换 | 两个标签页内均可切换 `[播放] [点赞] [投币] [收藏] [弹幕] [评论]` 六种指标 |
| 数据一致性 | tag1 的 7 天数据与 tag2 对应日期的数据点数值一致 |
| 空状态 | 未选择作品时，展示占位提示；选择作品后加载并展示图表 |
| 缓存 | 后端接口使用 `@cache_result(timeout=300)` 缓存，减少重复计算 |
