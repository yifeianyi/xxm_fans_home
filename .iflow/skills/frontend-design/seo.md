# SEO 优化 Skill

## Skill 描述

本 Skill 提供 XXM Fans Home 项目的 SEO（搜索引擎优化）标准和最佳实践。用于指导开发人员为新页面和新功能添加符合 SEO 标准的代码。

## 适用场景

当需要以下情况时，使用此 Skill：

- 创建新的页面组件
- 添加新的功能模块
- 优化现有页面的 SEO
- 审查代码的 SEO 合规性

## SEO 核心标准

### 1. 页面 Title

**格式**：`{页面标题} - 咻咻满相关描述 | 小满虫之家`

**要求**：
- 必须包含"咻咻满"关键词
- 长度控制在 60 字符以内
- 以"小满虫之家"结尾

**实现方式**：
```typescript
import { Helmet } from 'react-helmet';

<Helmet>
  <title>页面标题 - 咻咻满相关描述 | 小满虫之家</title>
</Helmet>
```

### 2. Meta Description

**格式**：简洁描述页面内容，自然融入"咻咻满"关键词（1-2次）

**要求**：
- 长度控制在 150-160 字符
- 准确描述页面内容
- 避免关键词堆砌

**实现方式**：
```typescript
<Helmet>
  <meta name="description" content="页面描述，包含咻咻满关键词" />
</Helmet>
```

### 3. Meta Keywords

**标准关键词**（已在 App.tsx 根组件统一设置）：
```
咻咻满, XXM, 小满虫, 唱见, 音乐主播, 独立音乐人, 戏腔, 治愈系
```

**注意**：不需要在子页面重复设置。

### 4. H1 标签

**要求**：
- 每个页面必须有且仅有一个 H1 标签
- H1 标签必须包含"咻咻满"关键词
- H1 标签应该与 Title 相呼应

**实现方式**：
```typescript
<h1 className="text-4xl font-black text-[#4a3728]">
  咻咻满页面标题
</h1>
```

### 5. 关键词密度

**要求**：
- 核心关键词"咻咻满"在页面正文中出现 3-5 次
- 关键词密度控制在 3-5%
- 关键词应该均匀分布在：Title、H1、第一段、链接文本

### 6. 内部链接

**要求**：
- 链接文本必须包含关键词
- 建立内部链接网络
- 链接到相关页面

**示例**：
```typescript
<a href="/about">关于咻咻满</a>
<a href="/songs">咻咻满歌曲</a>
<a href="/gallery">咻咻满图集</a>
```

### 7. 图片 SEO

**要求**：
- 所有图片必须有 Alt 文本
- Alt 文本必须包含"咻咻满"关键词
- 文件名应该包含相关关键词

**示例**：
```typescript
<img src="/xxm-photo.jpg" alt="咻咻满活动照片" />
```

### 8. URL 结构

**要求**：
- 使用简洁、语义化的 URL
- 使用小写字母和连字符
- 使用静态 URL（避免查询参数）

**示例**：
```
/songs
/songs/1
/gallery
/gallery/1
```

## 检查清单

在提交代码前，必须确保：

- [ ] 页面 Title 包含"咻咻满"关键词
- [ ] Meta Description 包含"咻咻满"关键词
- [ ] 页面有且仅有一个 H1 标签
- [ ] H1 标签包含"咻咻满"关键词
- [ ] 页面正文中"咻咻满"出现 3-5 次
- [ ] 所有图片都有 Alt 文本，且包含"咻咻满"
- [ ] 内部链接使用包含关键词的文本
- [ ] 页面使用语义化的 HTML 结构
- [ ] 页面有清晰的层级结构（H1 → H2 → H3）

## 参考示例

```typescript
import React from 'react';
import { Helmet } from 'react-helmet';
import { useNavigate } from 'react-router-dom';

const MyNewPage: React.FC = () => {
  const navigate = useNavigate();
  
  return (
    <>
      <Helmet>
        <title>我的新页面 - 咻咻满相关描述 | 小满虫之家</title>
        <meta
          name="description"
          content="这是我的新页面描述，自然融入咻咻满关键词。这里介绍页面的主要内容和功能。"
        />
      </Helmet>
      
      <div className="min-h-screen">
        <section className="py-20 px-4">
          <div className="max-w-6xl mx-auto text-center space-y-8">
            <h1 className="text-4xl font-black text-[#4a3728]">
              咻咻满我的新页面
            </h1>
            <p className="text-xl text-[#8eb69b]">
              这是咻咻满的新页面，包含相关的精彩内容。
              在这里，你可以发现更多关于咻咻满的信息。
            </p>
            <button
              onClick={() => navigate('/songs')}
              className="px-8 py-4 bg-gradient-to-r from-[#f8b195] to-[#f67280] text-white rounded-full"
            >
              浏览咻咻满歌曲
            </button>
          </div>
        </section>
        
        <section className="py-20 px-4 bg-white/40">
          <div className="max-w-6xl mx-auto">
            <h2 className="text-3xl font-black text-[#4a3728] mb-8">
              关于咻咻满的更多内容
            </h2>
            <div className="space-y-6">
              <img
                src="/images/xxm-photo.jpg"
                alt="咻咻满活动照片"
                className="w-full rounded-3xl"
              />
              <p className="text-[#4a3728]">
                咻咻满，独立音乐人、音乐主播，以其独特的戏韵和治愈声线著称。
                在这里，你可以探索咻咻满的更多精彩内容。
              </p>
            </div>
          </div>
        </section>
      </div>
    </>
  );
};

export default MyNewPage;
```

## 相关资源

- **完整 SEO 标准**：`.iflow/skills/frontend-design/SEO_STANDARD.md`
- **SEO 优化方案**：`doc/咻咻满关键词SEO优化方案.md`
- **结构化数据参考**：`index.html` 中的 Schema.org JSON-LD

## 注意事项

1. **禁止关键词堆砌**：自然融入关键词，不要刻意重复
2. **用户体验优先**：SEO 不能影响用户体验
3. **保持一致性**：所有页面遵循相同的 SEO 标准
4. **持续优化**：定期检查和优化 SEO 效果
5. **合规性**：只使用白帽 SEO 技术

## 常见错误

### ❌ 错误：缺少 H1 标签
```typescript
<div>
  <h2>咻咻满页面</h2> {/* 错误：使用 H2 而不是 H1 */}
</div>
```

### ❌ 错误：关键词堆砌
```typescript
<meta name="description" content="咻咻满咻咻满咻咻满咻咻满咻咻满" />
```

### ❌ 错误：无意义的链接文本
```typescript
<a href="/about">点击这里</a>
```

### ❌ 错误：缺少 Alt 文本
```typescript
<img src="/photo.jpg" />
```

## 技能调用方式

当需要创建新页面或添加新功能时，参考此 Skill 中的标准和示例，确保代码符合 SEO 要求。

---

**最后更新**：2026-01-26
**维护者**：iFlow CLI