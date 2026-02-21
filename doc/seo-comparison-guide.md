# Next.js 版本 SEO 对比评估指南

## 一、核心评估维度

### 1. 技术指标 (Core Web Vitals)
| 指标 | 说明 | 优秀标准 |
|------|------|---------|
| **LCP** | 最大内容绘制 | ≤ 2.5s |
| **INP** | 交互到下次绘制 | ≤ 200ms |
| **CLS** | 累积布局偏移 | ≤ 0.1 |
| **TTFB** | 首字节时间 | ≤ 600ms |
| **FCP** | 首次内容绘制 | ≤ 1.8s |

### 2. SEO 评分 (Lighthouse)
| 维度 | 权重 | 说明 |
|------|------|------|
| Performance | 30% | 页面加载性能 |
| Accessibility | 25% | 可访问性 |
| Best Practices | 20% | 最佳实践 |
| SEO | 15% | 搜索引擎优化 |
| PWA | 10% | 渐进式 Web 应用 |

---

## 二、可视化对比工具

### 方案 1：PageSpeed Insights (推荐)
**网址**: https://pagespeed.web.dev/

**操作步骤**:
1. 分别测试新旧版本（如果有测试环境）
2. 记录关键指标截图
3. 使用下方模板对比

```
┌─────────────────────────────────────────────────────────┐
│  页面: 首页 (/)                                          │
├─────────────────┬─────────────────┬─────────────────────┤
│     指标        │   旧版本(Vite)  │   新版本(Next.js)   │
├─────────────────┼─────────────────┼─────────────────────┤
│ LCP             │     2.1s  ✅    │     1.8s  ✅✅      │
│ INP             │     180ms ✅    │     150ms ✅✅      │
│ CLS             │     0.05  ✅    │     0.02  ✅✅      │
│ TTFB            │     450ms ✅    │     320ms ✅✅      │
│ Performance     │     78分       │     85分   ↑7       │
│ SEO             │     92分       │     95分   ↑3       │
└─────────────────┴─────────────────┴─────────────────────┘
```

### 方案 2：WebPageTest (深度分析)
**网址**: https://www.webpagetest.org/

**可视化报告**:
- 瀑布流对比图
- 视频对比（Visual Comparison）
- 第三方资源加载对比

### 方案 3：Chrome DevTools Performance Panel
本地对比测试方法：

```bash
# 1. 启动本地对比测试
# Vite 版本 (如果还有备份)
cd repo/xxm_fans_frontend_vite
npm run build && npm run preview

# Next.js 版本
cd repo/xxm_fans_frontend
npm run build && npm run start
```

**录制对比视频**:
1. 打开 Chrome DevTools → Performance
2. 勾选 Screenshots
3. 录制页面加载过程
4. 对比两个版本的渲染时间线

---

## 三、搜索引擎收录对比

### 1. 站点收录查询

```bash
# Google 收录对比
site:xxm8777.cn

# 检查特定页面
site:xxm8777.cn/albums
site:xxm8777.cn/songs
```

### 2. 搜索控制台 (Google Search Console)

**对比指标**:
| 指标 | 说明 |
|------|------|
| 总点击次数 | 自然搜索流量 |
| 总展示次数 | 搜索结果曝光 |
| 平均 CTR | 点击率 |
| 平均排名 | 关键词排名位置 |

**可视化方法**:
```
时间线对比图 (迁移前后 30 天)

点击次数
│
│    ╭────── Next.js 版本上线
│   ╱
│  ╱
│ ╱
│╱ 旧版本 ────────────────
└───────────────────────────
   上线前     上线后
```

---

## 四、Next.js 特有的 SEO 优势验证

### 1. 元数据检测
```bash
# 检查页面元数据
curl -s https://www.xxm8777.cn/ | grep -E '<title>|<meta|og:|twitter:'

# 预期改进 (Next.js vs Vite):
# - 更完整的 Open Graph 标签
# - 自动生成 sitemap.xml
# - 更好的 robots.txt
```

### 2. 服务端渲染 (SSR) 验证
```bash
# 查看源码是否包含完整 HTML (SSR 成功标志)
curl -s https://www.xxm8777.cn/albums | grep -o '<div.*class.*gallery\|<img.*src' | head -5

# Vite (SPA): 源码中可能只有 <div id="root"></div>
# Next.js (SSR): 源码中包含完整的图集 HTML
```

### 3. 结构化数据验证
**工具**: https://search.google.com/test/rich-results

测试项目：
- 音乐作品 Schema
- 图片集 Schema
- 面包屑导航 Schema

---

## 五、自动化监控方案

### 1. Lighthouse CI 集成

创建 `.github/workflows/lighthouse.yml`:

```yaml
name: Lighthouse CI
on: [push]
jobs:
  lighthouse:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run Lighthouse
        uses: treosh/lighthouse-ci-action@v9
        with:
          urls: |
            https://www.xxm8777.cn/
            https://www.xxm8777.cn/albums
            https://www.xxm8777.cn/songs
          budgetPath: ./lighthouse-budget.json
```

### 2. 性能预算配置
`lighthouse-budget.json`:

```json
{
  "budgets": [{
    "path": "/*",
    "resourceSizes": [
      {"resourceType": "script", "budget": 300},
      {"resourceType": "image", "budget": 1000}
    ],
    "timings": [
      {"metric": "largest-contentful-paint", "budget": 2500},
      {"metric": "interactive", "budget": 3500}
    ]
  }]
}
```

---

## 六、可视化报告模板

### 使用 Google Data Studio 创建 SEO 仪表盘

**数据源**:
- Google Search Console
- Google Analytics 4
- PageSpeed Insights API

**可视化组件**:
1. 折线图：核心指标趋势对比
2. 柱状图：各页面性能对比
3. 饼图：流量来源占比
4. 表格：关键词排名变化

### 命令行生成对比报告

```bash
#!/bin/bash
# lighthouse-compare.sh

echo "=== Lighthouse SEO 对比报告 ==="
echo "测试时间: $(date)"
echo ""

# Next.js 版本测试
echo "【Next.js 版本】"
lighthouse https://www.xxm8777.cn/ \
  --only-categories=seo,performance \
  --output=json \
  --chrome-flags="--headless" \
  > nextjs-report.json

# 提取关键指标
cat nextjs-report.json | jq -r '
  "Performance: \(.categories.performance.score * 100)",
  "SEO: \(.categories.seo.score * 100)",
  "LCP: \(.audits["largest-contentful-paint"].displayValue)",
  "CLS: \(.audits["cumulative-layout-shift"].displayValue)"
'
```

---

## 七、实操检查清单

### 立即执行 (今日)
- [ ] 使用 PageSpeed Insights 测试首页
- [ ] 使用 PageSpeed Insights 测试图集页
- [ ] 使用 PageSpeed Insights 测试歌曲页
- [ ] 检查 Google Search Console 抓取统计

### 短期监控 (本周)
- [ ] 对比新旧版本的 Lighthouse 评分
- [ ] 检查搜索引擎收录变化
- [ ] 验证所有页面的元数据完整性
- [ ] 测试移动端 SEO 表现

### 长期追踪 (每月)
- [ ] 分析搜索流量趋势
- [ ] 监控 Core Web Vitals 变化
- [ ] 检查关键词排名变化
- [ ] 更新 SEO 优化策略

---

## 八、预期改进点

### Next.js 相比 Vite 的 SEO 优势

| 特性 | Vite (SPA) | Next.js (SSR) | 影响 |
|------|-----------|---------------|------|
| 首屏 HTML | 空 div | 完整内容 | ⬆️ 爬虫友好 |
| 元数据 | 客户端注入 | 服务端渲染 | ⬆️ 社交分享 |
| Sitemap | 手动维护 | 自动生成 | ⬆️ 收录率 |
| 图片优化 | 手动 | 自动 WebP/AVIF | ⬆️ 加载速度 |
| 路由预渲染 | 无 | ISR/SSG | ⬆️ TTFB |

### 可能的下降点
- 首次加载 JS 可能增加 (React + Next.js runtime)
- 需要优化以抵消框架开销

---

## 参考工具汇总

| 工具 | 用途 | 链接 |
|------|------|------|
| PageSpeed Insights | 综合性能/SEO评分 | https://pagespeed.web.dev/ |
| WebPageTest | 深度性能分析 | https://www.webpagetest.org/ |
| GTmetrix | 性能监控 | https://gtmetrix.com/ |
| Google Search Console | 搜索表现 | https://search.google.com/search-console |
| Ahrefs/SEMrush | 关键词排名 | 付费工具 |
| Screaming Frog | 站点爬虫 | https://www.screamingfrog.co.uk/ |
| Lighthouse CI | 自动化测试 | GitHub Actions |
