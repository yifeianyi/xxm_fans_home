# 小满虫之家 - 设计系统规范

## 概述

本文档定义了"小满虫之家"粉丝网站的视觉设计系统，包括颜色、字体、组件和布局规范。

---

## 🎨 色彩系统

### 主色调 - 温暖珊瑚

| 变量 | 色值 | 用途 |
|------|------|------|
| `--accent` | `#f97066` | 主强调色、按钮、链接 |
| `--accent-light` | `#ffb8a3` | 悬停状态、浅色背景 |
| `--accent-dark` | `#dc2626` | 按下状态、强调文字 |
| `--accent-subtle` | `rgba(249, 112, 102, 0.1)` | 背景点缀 |

### 辅助色 - 深海蓝

| 变量 | 色值 | 用途 |
|------|------|------|
| `--secondary` | `#0ea5e9` | 次要按钮、信息提示 |
| `--secondary-light` | `#7dd3fc` | 悬停状态 |
| `--secondary-dark` | `#0369a1` | 深色强调 |

### 中性色

| 变量 | 色值 | 用途 |
|------|------|------|
| `--bg-primary` | `#fafaf9` | 主背景（暖灰白） |
| `--bg-secondary` | `#f5f5f4` | 次要背景 |
| `--bg-tertiary` | `#e7e5e4` | 边框、分割线 |
| `--bg-elevated` | `#ffffff` | 卡片背景 |
| `--text-primary` | `#1c1917` | 主文字（近黑） |
| `--text-secondary` | `#57534e` | 次要文字（灰褐） |
| `--text-tertiary` | `#a8a29e` | 弱化文字 |

### 渐变组合

```css
/* 主渐变 - 珊瑚到蓝色 */
background: linear-gradient(135deg, #f97066 0%, #0ea5e9 100%);

/* 暖色渐变 */
background: linear-gradient(135deg, #fff5f2 0%, #fafaf9 50%, #f0f9ff 100%);

/* 文字渐变 */
.text-gradient {
  background: linear-gradient(135deg, #f97066 0%, #0ea5e9 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}
```

---

## 🔤 字体系统

### 字体家族

| 用途 | 字体 | 备用字体 |
|------|------|----------|
| 标题 | Outfit | Noto Sans SC |
| 正文 | Inter | Noto Sans SC |

### 字体规格

| 元素 | 大小 | 字重 | 行高 |
|------|------|------|------|
| H1 | 3rem (48px) | 700 | 1.2 |
| H2 | 2.25rem (36px) | 700 | 1.2 |
| H3 | 1.5rem (24px) | 600 | 1.3 |
| H4 | 1.25rem (20px) | 600 | 1.4 |
| 正文 | 1rem (16px) | 400 | 1.6 |
| 小字 | 0.875rem (14px) | 400 | 1.5 |
| 标签 | 0.75rem (12px) | 500 | 1.4 |

### 字体加载

```html
<!-- 字体预连接 -->
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>

<!-- Outfit - 标题字体 -->
<link href="https://fonts.googleapis.com/css2?family=Outfit:wght@400;500;600;700&display=swap" rel="stylesheet">

<!-- Inter - 正文字体 -->
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap" rel="stylesheet">

<!-- Noto Sans SC - 中文字体 -->
<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+SC:wght@400;500;600;700&display=swap" rel="stylesheet">
```

---

## 🧩 组件规范

### 按钮

**主按钮 (Primary)**
```css
.btn-primary {
  background: linear-gradient(135deg, #f97066 0%, #dc2626 100%);
  color: white;
  padding: 0.75rem 1.5rem;
  border-radius: 0.75rem;
  font-weight: 600;
  box-shadow: 0 4px 14px 0 rgba(249, 112, 102, 0.39);
}
```

**次要按钮 (Secondary)**
```css
.btn-secondary {
  background: white;
  color: #1c1917;
  border: 1px solid #d6d3d1;
  padding: 0.75rem 1.5rem;
  border-radius: 0.75rem;
  font-weight: 600;
}
```

**幽灵按钮 (Ghost)**
```css
.btn-ghost {
  background: transparent;
  color: #57534e;
  padding: 0.75rem 1.5rem;
  border-radius: 0.75rem;
}
```

### 卡片

**标准卡片**
```css
.card {
  background: #ffffff;
  border-radius: 1rem;
  border: 1px solid rgba(231, 229, 228, 0.8);
  box-shadow: 0 1px 2px 0 rgb(0 0 0 / 0.05);
}
```

**可交互卡片**
```css
.card-interactive:hover {
  border-color: rgba(249, 112, 102, 0.3);
  box-shadow: 0 0 0 4px rgba(249, 112, 102, 0.1);
}
```

### 玻璃态效果

```css
.glass-card {
  background: rgba(255, 255, 255, 0.7);
  backdrop-filter: blur(20px) saturate(180%);
  border: 1px solid rgba(255, 255, 255, 0.5);
  box-shadow: 
    0 4px 6px -1px rgba(0, 0, 0, 0.05),
    inset 0 1px 0 0 rgba(255, 255, 255, 0.8);
}
```

### 输入框

```css
.input {
  background: #ffffff;
  border: 1px solid #d6d3d1;
  border-radius: 0.75rem;
  padding: 0.625rem 1rem;
  font-size: 0.875rem;
}

.input:focus {
  border-color: #f97066;
  box-shadow: 0 0 0 3px rgba(249, 112, 102, 0.1);
}
```

---

## 📐 间距系统

| 名称 | 值 | 用途 |
|------|-----|------|
| xs | 0.25rem (4px) | 紧凑间距 |
| sm | 0.5rem (8px) | 小间距 |
| md | 1rem (16px) | 标准间距 |
| lg | 1.5rem (24px) | 大间距 |
| xl | 2rem (32px) | 区域间距 |
| 2xl | 3rem (48px) | 大区域间距 |

---

## 🎯 圆角系统

| 名称 | 值 | 用途 |
|------|-----|------|
| sm | 0.5rem (8px) | 小元素 |
| md | 0.75rem (12px) | 按钮、输入框 |
| lg | 1rem (16px) | 卡片 |
| xl | 1.5rem (24px) | 大卡片 |
| 2xl | 2rem (32px) | 特殊元素 |
| full | 9999px | 圆形、胶囊形 |

---

## 💫 阴影系统

| 名称 | 值 | 用途 |
|------|-----|------|
| sm | `0 1px 2px 0 rgb(0 0 0 / 0.05)` | 小元素 |
| md | `0 4px 6px -1px rgb(0 0 0 / 0.1)` | 卡片 |
| lg | `0 10px 15px -3px rgb(0 0 0 / 0.1)` | 浮层 |
| xl | `0 20px 25px -5px rgb(0 0 0 / 0.1)` | 模态框 |
| glow | `0 0 20px rgba(249, 112, 102, 0.3)` | 强调发光 |

---

## 🎬 动画规范

### 过渡时间

| 类型 | 时间 | 曲线 |
|------|------|------|
| 快速 | 150ms | ease-out |
| 标准 | 200ms | ease |
| 慢速 | 300ms | ease-in-out |
| 弹簧 | 300ms | cubic-bezier(0.175, 0.885, 0.32, 1.275) |

### 预设动画

```css
/* 悬浮动画 */
@keyframes float {
  0%, 100% { transform: translateY(0px); }
  50% { transform: translateY(-10px); }
}

/* 脉冲发光 */
@keyframes pulse-glow {
  0%, 100% { box-shadow: 0 0 20px rgba(249, 112, 102, 0.3); }
  50% { box-shadow: 0 0 40px rgba(249, 112, 102, 0.5); }
}

/* 渐变流动 */
@keyframes gradient-shift {
  0% { background-position: 0% 50%; }
  50% { background-position: 100% 50%; }
  100% { background-position: 0% 50%; }
}
```

---

## 📱 响应式断点

| 断点 | 宽度 | 用途 |
|------|------|------|
| sm | 640px | 手机横屏 |
| md | 768px | 平板竖屏 |
| lg | 1024px | 平板横屏/小笔记本 |
| xl | 1280px | 桌面显示器 |
| 2xl | 1536px | 大屏显示器 |

---

## 🌟 最佳实践

### 颜色使用

1. **主强调色 (#f97066)** 用于：
   - 主按钮
   - 当前导航状态
   - 重要链接
   - 装饰元素

2. **辅助色 (#0ea5e9)** 用于：
   - 次要操作
   - 信息提示
   - 与珊瑚色形成对比

3. **中性色** 用于：
   - 正文文字
   - 背景层次
   - 边框和分割线

### 字体使用

1. **Outfit** 用于所有标题
2. **Inter** 用于正文和UI元素
3. 中文自动使用 Noto Sans SC

### 布局原则

1. 最大宽度容器：`max-w-7xl` (1280px)
2. 水平内边距：`px-4` (移动端) / `px-6` (桌面端)
3. 使用玻璃态效果增强现代感
4. 保持充足的留白

---

## 🔄 更新日志

### v2.0 - 2024
- 重新设计色彩系统（从绿色系改为珊瑚+蓝色）
- 更新字体组合（Outfit + Inter）
- 优化玻璃态效果
- 改进按钮和卡片样式
