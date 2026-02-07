# 小满虫之家 - 用户查询场景分析

## 文档概述

本文档基于小满虫之家项目的现有API接口和数据模型，推测了粉丝用户可能使用的查询场景。这些场景将作为Agent Skills智能查询系统设计和测试的重要参考。

**项目背景**：
- 项目积累了多维度数据：歌曲、演唱记录、粉丝数据、直播记录、二创作品、图集等
- 传统的固定页面无法满足所有个性化查询需求
- 通过Agent Skills架构，让LLM自由组合基础查询操作来满足各种场景

**数据来源**：
- 歌曲：歌曲信息、演唱记录、曲风、标签
- 直播：直播记录、歌切列表、分段视频
- 粉丝：粉丝数增长、统计数据
- 二创：作品合集、作品信息
- 图集：图集分类、图片项

---

## 场景分类

### 一、歌曲相关查询

#### 1.1 简单查询

| 查询示例 | 语义分析 | 需要的Skills |
|---------|---------|-------------|
| "2024年唱得最多的10首歌" | 按年份筛选 + 按演唱次数排序 | query-songs |
| "所有古风风格的歌曲" | 按曲风筛选 | query-songs |
| "含有'Ban位'标签的歌曲" | 按标签筛选 | query-songs |
| "2023年新唱的歌曲有哪些" | 按首次演唱年份筛选 | query-songs |
| "演唱次数超过20次的歌曲" | 按演唱次数下限筛选 | query-songs |

**实现方式**：
```python
query_songs(
    filter={year: 2024},
    sort={field: "perform_count", order: "desc"},
    limit: 10
)
```

#### 1.2 组合查询

| 查询示例 | 语义分析 | 需要的Skills |
|---------|---------|-------------|
| "2024年唱得最多的5首古风歌" | 年份 + 曲风 + 排序 | query-songs |
| "过去半年内演唱次数超过10次的翻唱歌曲" | 时间范围 + 次数下限 + 标签 | query-songs |
| "2023-2024年每年最热门的5首歌对比" | 两次查询 + 对比 | query-songs × 2 + correlate-data |

**实现方式**：
```python
# 步骤1：查询2024年古风歌
result1 = query_songs(
    filter={year: 2024, style: "古风"},
    sort={field: "perform_count", order: "desc"},
    limit: 5
)

# 步骤2：查询2023年古风歌
result2 = query_songs(
    filter={year: 2023, style: "古风"},
    sort={field: "perform_count", order: "desc"},
    limit: 5
)

# 步骤3：对比分析
correlate_data(data1=result1, data2=result2)
```

---

### 二、演唱记录分析

#### 2.1 时间维度分析

| 查询示例 | 语义分析 | 需要的Skills |
|---------|---------|-------------|
| "上周哪一天唱得最多" | 按周聚合 + 最大值查询 | query-songs + calculate-statistics |
| "2024年1月演唱了多少首歌" | 按月聚合 + 计数 | query-songs + calculate-statistics |
| "最近30天的演唱频率变化" | 时间序列 + 趋势分析 | query-songs + calculate-growth |

**实现方式**：
```python
# 获取最近30天的演唱记录
songs = query_songs(filter={date_range: {start_date: "30天前"}})

# 按天聚合并计算演唱频率
stats = calculate_statistics(
    data=songs,
    aggregation="daily",
    metrics=["count", "frequency"]
)
```

#### 2.2 演唱习惯分析

| 查询示例 | 语义分析 | 需要的Skills |
|---------|---------|-------------|
| "周末和工作日哪个唱得更多" | 按星期分组 + 对比 | query-songs + calculate-statistics |
| "晚上（18点后）的直播演唱情况" | 时间范围筛选 + 统计 | query-songs + query-livestreams |
| "平均每次直播唱多少首歌" | 聚合计算 | query-livestreams + calculate-statistics |

---

### 三、粉丝增长与数据分析

#### 3.1 增长趋势分析

| 查询示例 | 语义分析 | 需要的Skills |
|---------|---------|-------------|
| "最近3个月粉丝增长了多少" | 时间范围 + 总量计算 | query-fans + calculate-growth |
| "哪个月粉丝增长最快" | 按月聚合 + 最大值 | query-fans + calculate-statistics |
| "粉丝增长速度有没有变化趋势" | 时间序列 + 趋势分析 | query-fans + calculate-growth |

**实现方式**：
```python
# 获取最近90天粉丝数据
fans_data = query_fans(days=90)

# 计算增长率指标
growth = calculate_growth(
    data=fans_data,
    metrics=["avg_growth", "growth_rate", "trend", "peak_date"]
)
```

#### 3.2 影响因素分析

| 查询示例 | 语义分析 | 需要的Skills |
|---------|---------|-------------|
| "粉丝增长和直播频率的关系" | 两个数据集关联分析 | query-fans + query-livestreams + correlate-data |
| "发新歌对粉丝增长的影响" | 歌曲发布时间与粉丝数据关联 | query-songs + query-fans + correlate-data |
| "粉丝增长和热门作品的关联" | 多维度关联分析 | query-fans + query-songs + correlate-data |

**实现方式**：
```python
# 获取粉丝数据和直播数据
fans = query_fans(days=90)
livestreams = query_livestreams(filter={start_date: "90天前"})

# 关联分析
correlation = correlate_data(
    data1=fans,
    data2=livestreams,
    method="pearson"
)
```

---

### 四、直播数据分析

#### 4.1 直播内容分析

| 查询示例 | 语义分析 | 需要的Skills |
|---------|---------|-------------|
| "最近10次直播的平均歌切数" | 聚合统计 | query-livestreams + calculate-statistics |
| "歌切最多的10场直播" | 排序查询 | query-livestreams |
| "直播时长的变化趋势" | 时间序列 + 趋势分析 | query-livestreams + calculate-growth |

#### 4.2 时间规律分析

| 查询示例 | 语义分析 | 需要的Skills |
|---------|---------|-------------|
| "通常在什么时间段直播" | 时间分布分析 | query-livestreams + calculate-statistics |
| "一周内哪几天直播最多" | 按星期聚合 | query-livestreams + calculate-statistics |
| "节假日期间的直播情况" | 特殊时间筛选 | query-livestreams + calculate-statistics |

---

### 五、多维度交叉分析

#### 5.1 歌曲-直播关联

| 查询示例 | 语义分析 | 需要的Skills |
|---------|---------|-------------|
| "热门歌曲的演唱直播时间分布" | 歌曲热度 + 直播时间 | query-songs + query-livestreams + correlate-data |
| "直播中经常演唱的歌曲类型" | 聚合分析 | query-songs + query-livestreams + calculate-statistics |

#### 5.2 粉丝-内容关联

| 查询示例 | 语义分析 | 需要的Skills |
|---------|---------|-------------|
| "粉丝增长与二创作品发布的关系" | 多数据集关联 | query-fans + query-fansdiy + correlate-data |
| "图集更新对粉丝活跃度的影响" | 时间对齐 + 关联分析 | query-fans + query-galleries + correlate-data |

---

### 六、二创内容查询

#### 6.1 作品检索

| 查询示例 | 语义分析 | 需要的Skills |
|---------|---------|-------------|
| "2024年发布的粉丝二创作品" | 按年份筛选 | query-fansdiy |
| "特定合集下的所有作品" | 按合集ID筛选 | query-fansdiy |
| "最受欢迎的二创作品" | 按热度排序 | query-fansdiy |

#### 6.2 趋势分析

| 查询示例 | 语义分析 | 需要的Skills |
|---------|---------|-------------|
| "二创作品发布频率变化" | 时间序列分析 | query-fansdiy + calculate-growth |
| "不同类型二创作品的受欢迎程度" | 分类统计 | query-fansdiy + calculate-statistics |

---

### 七、图集相关查询

#### 7.1 内容查询

| 查询示例 | 语义分析 | 需要的Skills |
|---------|---------|-------------|
| "2024年新上传的图集" | 按年份筛选 | query-galleries |
| "特定分类下的图集" | 按分类筛选 | query-galleries |
| "图片最多的10个图集" | 按图片数量排序 | query-galleries |

#### 7.2 时间分析

| 查询示例 | 语义分析 | 需要的Skills |
|---------|---------|-------------|
| "图集上传的季节性规律" | 按季节聚合 | query-galleries + calculate-statistics |
| "最近活跃的图集更新" | 时间范围筛选 | query-galleries |

---

### 八、综合报告类

#### 8.1 月度/年度总结

| 查询示例 | 语义分析 | 需要的Skills |
|---------|---------|-------------|
| "2024年演唱总结" | 多维度数据整合 | query-songs + query-livestreams + calculate-statistics |
| "2024年粉丝增长年度报告" | 粉丝数据综合分析 | query-fans + calculate-growth |
| "上个月数据综合分析" | 多数据源整合 | query-songs + query-fans + query-livestreams |

**实现方式**：
```python
# 获取多维度数据
songs = query_songs(filter={month: "上个月"})
fans = query_fans(days=30)
livestreams = query_livestreams(filter={month: "上个月"})

# 综合分析
stats = calculate_statistics(data=[songs, fans, livestreams])
```

#### 8.2 专项分析

| 查询示例 | 语义分析 | 需要的Skills |
|---------|---------|-------------|
| "2024年vs2023年演唱对比" | 跨年度对比 | query-songs × 2 + correlate-data |
| "春节假期期间的数据表现" | 特殊时间分析 | query-songs + query-fans + query-livestreams |

---

### 九、对比类查询

#### 9.1 时间对比

| 查询示例 | 语义分析 | 需要的Skills |
|---------|---------|-------------|
| "2023年和2024年的演唱次数对比" | 年度对比 | query-songs × 2 + correlate-data |
| "上半年和下半年的数据对比" | 半年度对比 | query-songs × 2 + correlate-data |
| "本月与上月对比" | 月度对比 | query-songs × 2 + correlate-data |

#### 9.2 内容对比

| 查询示例 | 语义分析 | 需要的Skills |
|---------|---------|-------------|
| "古风歌vs流行歌的演唱频率" | 曲风对比 | query-songs × 2 + calculate-statistics |
| "翻唱vs原创的数量对比" | 标签对比 | query-songs × 2 + calculate-statistics |

---

### 十、预测与建议类

#### 10.1 趋势预测

| 查询示例 | 语义分析 | 需要的Skills |
|---------|---------|-------------|
| "根据当前趋势，下月可能新增多少粉丝" | 基于历史数据预测 | query-fans + calculate-growth |
| "预测下季度的演唱频率" | 趋势外推 | query-livestreams + calculate-growth |

#### 10.2 优化建议

| 查询示例 | 语义分析 | 需要的Skills |
|---------|---------|-------------|
| "如何提高粉丝增长速度" | 基于数据给出建议 | query-fans + query-livestreams + correlate-data |
| "哪类歌曲更受欢迎" | 热度分析 | query-songs + calculate-statistics |
| "最佳直播时间段建议" | 时间分布分析 | query-livestreams + calculate-statistics |

---

## Skills组合模式总结

### 单一Skill场景
- 简单筛选、排序、聚合查询
- 示例：查询2024年歌曲、查询古风歌曲

### 双Skill场景
- 查询 + 统计
- 查询 + 计算
- 示例：最近30天演唱频率、粉丝增长率计算

### 三Skill场景
- 查询1 + 查询2 + 关联分析
- 查询 + 统计 + 趋势分析
- 示例：粉丝增长与直播频率关系、年度数据对比

### 多Skill场景（4+）
- 多数据源查询 + 综合分析
- 复杂的交叉关联分析
- 示例：综合报告、多维度交叉分析

---

## 场景复杂度评估

| 复杂度级别 | Skill数量 | 典型场景 | 预计响应时间 |
|-----------|----------|---------|------------|
| 简单 | 1 | 基础查询 | < 0.5s |
| 中等 | 2-3 | 统计分析、对比 | 0.5-1s |
| 复杂 | 4+ | 综合报告、多维度分析 | 1-2s |

---

## 技术实现建议

### 1. Skills设计原则
- **原子化**：每个Skill只做一件事
- **可组合**：LLM可以自由组合
- **参数化**：支持灵活的筛选和排序

### 2. 查询优化建议
- **缓存常用查询**：高频场景可以缓存结果
- **并行执行**：独立的Skills可以并行调用
- **增量查询**：支持增量数据获取

### 3. 性能监控
- 记录每个场景的Skill组合
- 监控响应时间和Token消耗
- 优化高频场景的执行路径

---

## 附录：场景测试用例

### 测试用例1：简单查询
```
输入："2024年唱得最多的10首歌"
预期Skills组合：query-songs
预期输出：歌曲列表，按演唱次数降序
```

### 测试用例2：关联分析
```
输入："粉丝增长和直播频率的关系"
预期Skills组合：query-fans + query-livestreams + correlate-data
预期输出：相关系数、解释说明
```

### 测试用例3：综合报告
```
输入："2024年演唱总结"
预期Skills组合：query-songs + query-livestreams + calculate-statistics
预期输出：多维度数据分析报告
```

---

**文档版本**：1.0
**创建日期**：2026-02-04
**作者**：iFlow CLI
**相关文档**：
- agent_skills_implementation_plan.md - Agent Skills实现方案
- AGENTS.md - 项目技术文档

---

## 变更记录

| 版本 | 日期 | 变更内容 | 作者 |
|-----|------|---------|-----|
| 1.0 | 2026-02-04 | 初始版本，基于现有API推测用户场景 | iFlow CLI |