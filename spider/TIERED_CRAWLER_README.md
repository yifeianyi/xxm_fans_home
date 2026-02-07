# 分层爬虫优化方案

## 概述

针对B站投稿数据爬虫的优化方案，根据发布时间将作品分为**热数据**和**冷数据**，采用不同的爬取频率。

> **投稿频率参考**：新投稿一般一周最多1个，一个月最多不超过10个。

## 分层策略

| 数据类型 | 发布时间 | 典型数量 | 爬取频率 | 爬取时段 |
|---------|---------|---------|---------|---------|
| **🔥 热数据** | ≤ 7天 | **0-1个** | **每小时** | 全天24小时 |
| **❄️ 冷数据** | > 7天 | **数百个** | **每天3次** | 00:00, 08:00, 16:00 |

## 优势

基于投稿频率特点（周更≤1个，月更≤10个）：

1. **大幅降低服务器压力**：每小时只需爬取0-1个热数据，而非全部作品
2. **保证新作品实时性**：新投稿每小时更新，第一时间获取数据
3. **历史数据适度更新**：冷数据每天3次更新足够满足需求
4. **可扩展性**：支持自定义热数据时间阈值（默认7天）

## 文件结构

```
xxm_fans_home/
├── spider/
│   ├── run_tiered_crawler.py          # 分层爬虫主控脚本
│   └── TIERED_CRAWLER_README.md       # 本说明文档
│
├── repo/xxm_fans_backend/tools/spider/
│   └── export_tiered.py               # 分层数据导出模块
│
├── scripts/
│   └── bilibili_tiered_cron.sh        # 定时任务脚本
│
└── infra/systemd/
    ├── bilibili-tiered-crawler.service # systemd 服务配置
    └── bilibili-tiered-crawler.timer   # systemd 定时器配置
```

## 使用方法

### 1. 手动执行

```bash
# 进入项目目录
cd /home/yifeianyi/Desktop/xxm_fans_home

# 查看分层统计信息（了解热/冷数据分布）
python spider/run_tiered_crawler.py --stats

# 只爬取热数据（7天内发布的作品）
python spider/run_tiered_crawler.py --hot

# 只爬取冷数据（7天前发布的作品）
python spider/run_tiered_crawler.py --cold

# 爬取全部数据（热+冷）
python spider/run_tiered_crawler.py --all

# 根据当前时间自动选择（用于定时任务）
python spider/run_tiered_crawler.py --scheduled
```

### 2. 定时任务

#### 方式一：systemd timer（推荐）

```bash
# 启用并启动定时任务
sudo systemctl enable --now /home/yifeianyi/Desktop/xxm_fans_home/infra/systemd/bilibili-tiered-crawler.timer

# 查看定时任务状态
systemctl list-timers --all | grep bilibili-tiered

# 手动触发执行
sudo systemctl start bilibili-tiered-crawler.service

# 查看服务日志
sudo journalctl -u bilibili-tiered-crawler.service -f
```

#### 方式二：crontab

```bash
# 编辑 crontab
crontab -e

# 添加以下行（每小时执行）
0 * * * * /home/yifeianyi/Desktop/xxm_fans_home/scripts/bilibili_tiered_cron.sh
```

## 输出文件

### 数据文件

```
data/spider/
├── views_hot.json          # 热数据导出（7天内作品，通常0-2条）
├── views_cold.json         # 冷数据导出（7天前作品，历史积累）
├── views.json              # 全部数据导出（兼容旧版）
└── views/
    └── {YYYY}/{MM}/{DD}/
        └── {YYYY-MM-DD}-{HH}_views_data.json   # 按小时存储的爬取结果
```

### 日志文件

```
logs/
├── bilibili_tiered_crawler.json              # JSON格式执行日志
└── spider/
    ├── run_tiered_crawler_YYYYMMDD.log       # 主控脚本日志
    ├── views_crawler_YYYYMMDD.log            # 爬虫模块日志
    └── views_import_YYYYMMDD.log             # 导入模块日志
```

## 配置说明

### 热数据时间阈值

默认热数据为 **7天内** 发布的作品，可以通过参数修改：

```bash
# 修改热数据为14天
python repo/xxm_fans_backend/tools/spider/export_tiered.py --hot --days 14
```

或在代码中修改 `DEFAULT_HOT_DAYS` 常量。

> **建议**：考虑到投稿频率（周更1个），7天阈值能很好地覆盖新作品。如投稿频率变化，可适当调整。

### 冷数据爬取时段

默认冷数据每天爬取3次：00:00, 08:00, 16:00

修改 `run_tiered_crawler.py` 中的 `COLD_CRAWL_HOURS` 常量：

```python
# 例如改为每天2次：00:00, 12:00
COLD_CRAWL_HOURS = [0, 12]
```

### 爬虫参数

```bash
# 调整请求延迟（避免被反爬）
python spider/run_tiered_crawler.py --hot --delay-min 0.5 --delay-max 1.5

# 调整重试次数
python spider/run_tiered_crawler.py --hot --retries 3

# 强制重新导入（即使数据已存在）
python spider/run_tiered_crawler.py --hot --force
```

## 调度逻辑

```
每小时触发
    │
    ├─→ 始终执行：爬取热数据（7天内作品，通常0-2个）
    │   └── 开销极小，几乎瞬间完成
    │
    └─→ 条件执行：检查当前时间
            │
            ├─→ 00:00 / 08:00 / 16:00 → 爬取冷数据（历史全部作品）
            │   └── 耗时较长，错峰执行
            │
            └─→ 其他时段 → 跳过冷数据爬取
                └── 大幅节省资源
```

## 执行示例

### 场景1：平时时段（无新投稿）

```
[10:00] 开始执行分层爬虫
  ├── 🔥 热数据（0条）: ✅ 无需爬取
  └── ❄️ 冷数据（500条）: ⏸️ 跳过（下次: 16:00）
  
总计爬取: 0条作品
执行耗时: ~5秒（仅导出检查）
```

### 场景2：平时时段（有新投稿）

```
[10:00] 开始执行分层爬虫
  ├── 🔥 热数据（1条）: ✅ 执行爬取 - "本周新投稿作品"
  └── ❄️ 冷数据（500条）: ⏸️ 跳过（下次: 16:00）
  
总计爬取: 1条作品
执行耗时: ~10秒
```

### 场景3：冷数据爬取时段

```
[16:00] 开始执行分层爬虫
  ├── 🔥 热数据（1条）: ✅ 执行爬取
  └── ❄️ 冷数据（500条）: ✅ 执行爬取
  
总计爬取: 501条作品
预计耗时: ~25分钟
```

## 与原方案对比

| 指标 | 原方案 | 分层方案 | 优化效果 |
|-----|-------|---------|---------|
| 平时每小时请求数 | ~500条 | **0-1条** | **降低 99%+** |
| 冷数据时段请求数 | ~500条 | ~500条 | 持平 |
| 新作品更新延迟 | 1小时 | 1小时 | 保持一致 |
| 旧作品更新延迟 | 1小时 | 8小时 | 可接受 |
| 每日总请求数 | ~12000次 | **~1500次** | **降低 87%** |
| 平时执行耗时 | ~20分钟 | **<10秒** | **极大提升** |
| 服务器压力 | 高 | **极低** | **显著降低** |

## 注意事项

1. **投稿频率变化**：如果投稿频率显著增加（如日更），建议缩短热数据阈值或增加爬取频率
2. **首次部署**：建议先执行 `--stats` 查看当前热/冷数据分布
3. **数据一致性**：冷数据每天只更新3次，如需最新历史数据请等待冷数据爬取时段
4. **日志清理**：定期检查 `logs/bilibili_tiered_crawler.json` 大小，避免磁盘占满

## 故障排查

### 查看执行日志

```bash
# 查看最近执行记录
tail -50 logs/bilibili_tiered_crawler.json | jq '.[-5:]'

# 查看详细日志
tail -100 logs/spider/run_tiered_crawler_$(date +%Y%m%d).log
```

### 手动调试

```bash
# 测试热数据导出
python repo/xxm_fans_backend/tools/spider/export_tiered.py --hot --stats

# 测试冷数据导出
python repo/xxm_fans_backend/tools/spider/export_tiered.py --cold --stats

# 执行单次热数据爬取
python spider/run_tiered_crawler.py --hot --delay-min 0.5
```

## 适用场景建议

| 投稿频率 | 建议配置 |
|---------|---------|
| 周更 ≤1个（当前） | 默认配置（7天热数据，冷数据3次/天） |
| 周更 2-3个 | 建议热数据阈值 14天，保持冷数据3次/天 |
| 日更 1个 | 建议热数据阈值 3天，增加冷数据爬取至4次/天 |
| 日更多个 | 建议所有数据每小时爬取（恢复原版方案） |

## 迁移指南

从原方案迁移到分层方案：

```bash
# 1. 停止原定时任务
sudo systemctl stop bilibili-views-crawler.timer
sudo systemctl disable bilibili-views-crawler.timer

# 2. 验证新方案
python spider/run_tiered_crawler.py --stats

# 3. 启用新定时任务
sudo systemctl enable --now infra/systemd/bilibili-tiered-crawler.timer

# 4. 验证定时任务
systemctl list-timers --all | grep bilibili-tiered
```

## 版本历史

| 版本 | 日期 | 说明 |
|-----|------|------|
| 1.0 | 2026-02-07 | 初始版本，针对周更1个、月更10个的投稿频率优化 |
