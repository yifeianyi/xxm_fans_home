# 前端性能优化实施总结

## 优化日期
2026-01-29

## 优化范围
- Tailwind CSS 本地构建（方案1）
- 字体加载优化（方案2）

---

## 一、Tailwind CSS 本地构建优化

### 1.1 优化前的问题

**问题描述**：
- 使用 `cdn.tailwindcss.com` 引入 Tailwind CSS
- CDN 请求返回 302 重定向，增加延迟
- 每次请求都要下载完整的 Tailwind CSS 库（100KB+）
- 生产环境无法利用浏览器缓存

**影响**：
- 增加约 1-2s 加载时间
- 占用宝贵的网络带宽
- 阻塞首屏渲染

### 1.2 实施步骤

#### 步骤 1：安装依赖
```bash
npm install -D tailwindcss postcss autoprefixer @tailwindcss/postcss terser
```

#### 步骤 2：创建配置文件

**tailwind.config.js**：
```javascript
/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // 自定义主题色
        'sage-bg': '#f2f9f1',
        'meadow-green': '#8eb69b',
        'peach-accent': '#f8b195',
        'butter-yellow': '#fff4d1',
        'earthy-brown': '#4a3728',
      },
      fontFamily: {
        'quicksand': ['Quicksand', 'sans-serif'],
        'noto-sans': ['Noto Sans SC', 'sans-serif'],
      },
    },
  },
  plugins: [],
}
```

**postcss.config.js**：
```javascript
export default {
  plugins: {
    '@tailwindcss/postcss': {},
    autoprefixer: {},
  },
}
```

#### 步骤 3：创建 CSS 入口文件

**styles/index.css**（使用 Tailwind CSS 4.x CSS-first 配置）：
```css
@import "tailwindcss";

@theme {
  --color-sage-bg: #f2f9f1;
  --color-meadow-green: #8eb69b;
  --color-peach-accent: #f8b195;
  --color-butter-yellow: #fff4d1;
  --color-earth-brown: #4a3728;

  --font-family-quicksand: 'Quicksand', sans-serif;
  --font-family-noto-sans: 'Noto Sans SC', sans-serif;
}

/* 自定义样式 */
:root {
  --sage-bg: #f2f9f1;
  --meadow-green: #8eb69b;
  --peach-accent: #f8b195;
  --butter-yellow: #fff4d1;
  --earthy-brown: #4a3728;
}

body {
  font-family: 'Quicksand', 'Noto Sans SC', sans-serif;
  background-color: var(--sage-bg);
  color: var(--earthy-brown);
  overflow-x: hidden;
}

/* 其他自定义样式... */
```

#### 步骤 4：在入口文件中引入 CSS

**index.tsx**：
```typescript
import React from 'react';
import ReactDOM from 'react-dom/client';
import './styles/index.css';  // 新增
import App from './App';

// ... 其他代码
```

#### 步骤 5：移除 CDN 引用

**index.html**（删除）：
```html
<script src="https://cdn.tailwindcss.com"></script>
```

#### 步骤 6：创建生产环境配置

**vite.config.prod.ts**：
```typescript
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
    plugins: [react()],
    css: {
        devSourcemap: false,
    },
    build: {
        rollupOptions: {
            input: {
                main: './index.html'
            },
            output: {
                manualChunks: {
                    'react-vendor': ['react', 'react-dom', 'react-router-dom'],
                    'lucide': ['lucide-react'],
                },
                chunkFileNames: 'assets/[name]-[hash].js',
                entryFileNames: 'assets/[name]-[hash].js',
                assetFileNames: 'assets/[name]-[hash].[ext]',
            },
        },
        chunkSizeWarningLimit: 1000,
        minify: 'terser',
        terserOptions: {
            compress: {
                drop_console: true,
                drop_debugger: true,
            },
        },
    }
})
```

#### 步骤 7：更新开发环境配置

**vite.config.ts**：
```typescript
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
    plugins: [react()],
    css: {
        devSourcemap: true,
    },
    // ... 其他配置
})
```

### 1.3 优化效果

**构建产物**：
```
dist/index.html                         5.67 kB │ gzip:  2.09 kB
dist/assets/main-rcsRmS9t.css          66.90 kB │ gzip: 11.14 kB
dist/assets/lucide-DVxGwBIk.js         10.18 kB │ gzip:  3.85 kB
dist/assets/react-vendor-Nujau_xw.js   45.71 kB │ gzip: 15.96 kB
dist/assets/main-D95IXnQc.js          317.73 kB │ gzip: 90.88 kB
```

**性能提升**：
- CSS 文件大小：66.90 KB（gzip 后 11.14 KB）
- 相比 CDN 版本（100KB+）减少了约 34%
- 支持浏览器缓存，无需每次下载
- 移除了 302 重定向延迟

---

## 二、字体加载优化

### 2.1 优化前的问题

**问题描述**：
- 加载了过多的字重
- Quicksand：wght@400;500;600;700（4个字重）
- Noto Sans SC：wght@400;500;700（3个字重）
- 总共加载 7 个字体文件
- 所有字体文件并行加载，阻塞渲染

**影响**：
- 增加约 1-1.5s 加载时间
- 占用大量带宽（600-800KB）
- 可能导致文字闪烁（FOIT/FOUT）

### 2.2 实施步骤

#### 步骤 1：分析实际使用的字重

通过检查项目代码，确定实际使用的字重为：
- Quicksand：400, 600, 700（移除 500）
- Noto Sans SC：400, 700（移除 500）

#### 步骤 2：优化字体加载

**index.html**（优化后）：
```html
<!-- 字体预加载 -->
<link
  rel="preload"
  href="https://fonts.gstatic.com/s/quicksand/v30/6xKtdSZaM9iE8KbpRA_hJFQNcOM.woff2"
  as="font"
  type="font/woff2"
  crossorigin
>
<link
  rel="preload"
  href="https://fonts.gstatic.com/s/notosanssc/v36/k3kXo84MPvpLmixcA63oeALZTYKLgASIOQ.woff2"
  as="font"
  type="font/woff2"
  crossorigin
>
<!-- 优化后的字体加载：只加载必要的字重，使用 display=swap -->
<link
    href="https://fonts.googleapis.com/css2?family=Quicksand:wght@400;600;700&display=swap"
    rel="stylesheet">
<link
    href="https://fonts.googleapis.com/css2?family=Noto+Sans+SC:wght@400;700&display=swap"
    rel="stylesheet">
```

#### 步骤 3：添加字体预加载

- 预加载关键字体的 WOFF2 文件
- 使用 `rel="preload"` 提前加载
- 设置 `crossorigin` 属性

#### 步骤 4：使用 font-display 策略

- Google Fonts 自动使用 `font-display: swap`
- 防止文字闪烁（FOIT/FOUT）
- 提升用户体验

### 2.3 优化效果

**优化前后对比**：

| 字体 | 优化前 | 优化后 | 减少数量 |
|------|--------|--------|----------|
| Quicksand | 4个字重 (400, 500, 600, 700) | 3个字重 (400, 600, 700) | -1个文件 |
| Noto Sans SC | 3个字重 (400, 500, 700) | 2个字重 (400, 700) | -1个文件 |
| **总计** | **7个文件** | **5个文件** | **-2个文件** |

**性能提升**：
- 字体文件数量减少 28.6%（7 → 5）
- 预计传输量减少 30-40%
- 关键字体优先加载
- 使用 `font-display: swap` 防止文字闪烁

---

## 三、遇到的问题及解决方案

### 3.1 PostCSS 配置错误

**问题**：
```
[postcss] It looks like you're trying to use `tailwindcss` directly as a PostCSS plugin. The PostCSS plugin has moved to a separate package.
```

**原因**：
- 安装了 Tailwind CSS 4.x 版本
- PostCSS 插件从 `tailwindcss` 移动到了 `@tailwindcss/postcss`

**解决方案**：
1. 安装 `@tailwindcss/postcss`：
   ```bash
   npm install -D @tailwindcss/postcss
   ```

2. 更新 `postcss.config.js`：
   ```javascript
   export default {
     plugins: {
       '@tailwindcss/postcss': {},  // 使用新插件
       autoprefixer: {},
     },
   }
   ```

### 3.2 Tailwind CSS 4.x 配置方式改变

**问题**：
```
Cannot apply unknown utility class `font-quicksand`.
```

**原因**：
- Tailwind CSS 4.x 使用 CSS-first 配置方式
- 需要在 CSS 文件中使用 `@theme` 定义主题

**解决方案**：
使用 CSS-first 配置方式：
```css
@import "tailwindcss";

@theme {
  --color-sage-bg: #f2f9f1;
  --color-meadow-green: #8eb69b;
  --color-peach-accent: #f8b195;
  --color-butter-yellow: #fff4d1;
  --color-earth-brown: #4a3728;

  --font-family-quicksand: 'Quicksand', sans-serif;
  --font-family-noto-sans: 'Noto Sans SC', sans-serif;
}
```

### 3.3 Terser 未找到

**问题**：
```
terser not found. Since Vite v3, terser has become an optional dependency.
```

**原因**：
- Vite v3+ 将 terser 设为可选依赖
- 生产构建需要 terser 进行代码压缩

**解决方案**：
```bash
npm install -D terser
```

### 3.4 开发服务器缓存问题

**问题**：
开发服务器启动时仍使用旧的 PostCSS 配置

**解决方案**：
1. 停止所有正在运行的 Vite 进程：
   ```bash
   pkill -f "vite"
   ```

2. 清理所有缓存目录：
   ```bash
   rm -rf node_modules/.vite dist .cache
   ```

3. 重新启动开发服务器

---

## 四、文件清单

### 新增文件

1. `tailwind.config.js` - Tailwind CSS 配置文件
2. `postcss.config.js` - PostCSS 配置文件
3. `vite.config.prod.ts` - 生产环境 Vite 配置文件
4. `styles/index.css` - CSS 入口文件

### 修改文件

1. `index.html` - 移除 CDN 引用，优化字体加载
2. `index.tsx` - 引入 CSS 文件
3. `vite.config.ts` - 添加 CSS source map 配置
4. `package.json` - 添加新的依赖包

### 新增依赖

```json
{
  "devDependencies": {
    "@tailwindcss/postcss": "^4.1.18",
    "autoprefixer": "^10.4.20",
    "postcss": "^8.4.49",
    "tailwindcss": "^4.1.18",
    "terser": "^5.36.0"
  }
}
```

---

## 五、后续优化建议

### 5.1 图片优化（方案3）

- 转换为 WebP 格式
- 实现响应式图片
- 添加图片懒加载
- 预计减少 300-500ms 加载时间

### 5.2 代码分割和懒加载（方案4）

- 路由懒加载
- 组件懒加载
- 优化 Vite 配置
- 预计减少 500ms-1s 加载时间

### 5.3 资源预加载策略（方案5）

- DNS 预解析
- 预连接
- 预加载关键资源
- 预获取次要资源
- 预计减少 200-500ms 加载时间

### 5.4 进一步字体优化

**方案1：只使用2个字重**
```html
<link href="https://fonts.googleapis.com/css2?family=Quicksand:wght@400;700&display=swap" rel="stylesheet">
<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+SC:wght@400;700&display=swap" rel="stylesheet">
```

**方案2：使用可变字体（Variable Fonts）**
```html
<link href="https://fonts.googleapis.com/css2?family=Quicksand:ital,wght@0,400..700;1,400..700&display=swap" rel="stylesheet">
```

---

## 六、验证方法

### 6.1 构建验证

```bash
# 开发环境构建
npm run build:dev

# 生产环境构建
npm run build

# 预览生产构建
npm run preview
```

### 6.2 开发服务器验证

```bash
# 启动开发服务器
npm run dev
```

### 6.3 性能监控

使用以下工具监控性能：

1. **Google Lighthouse**
   - Chrome DevTools 中运行
   - 或使用命令行：`npx lighthouse https://www.xxm8777.cn --view`

2. **Chrome DevTools Performance**
   - 打开 Performance 面板
   - 录制并分析

3. **Chrome DevTools Network**
   - 查看 CSS 和字体文件大小
   - 分析加载时间

### 6.4 关键指标

| 指标 | 目标值 | 当前值 | 状态 |
|------|--------|--------|------|
| CSS 文件大小 | < 100KB | 66.90 KB | ✅ |
| CSS 文件大小 (gzip) | < 30KB | 11.14 KB | ✅ |
| 字体文件数量 | < 6 | 5 | ✅ |
| Lighthouse Performance | > 85 | 待测试 | ⏳ |

---

## 七、总结

本次优化完成了前端性能优化方案中的前两个高优先级方案：

### 成果

1. **Tailwind CSS 本地构建**
   - ✅ 移除了 CDN 依赖
   - ✅ CSS 文件大小减少 34%
   - ✅ 支持浏览器缓存
   - ✅ 消除 302 重定向延迟

2. **字体加载优化**
   - ✅ 字体文件数量减少 28.6%
   - ✅ 添加字体预加载
   - ✅ 使用 font-display: swap
   - ✅ 预计传输量减少 30-40%

### 影响

- **页面加载时间**：预计减少 1.5-3s
- **传输数据量**：预计减少 30-40%
- **用户体验**：显著提升首屏渲染速度
- **SEO**：提升 Google 页面速度评分

### 技术亮点

1. 使用 Tailwind CSS 4.x 最新特性（CSS-first 配置）
2. 实现了代码分割和代码压缩
3. 添加了关键资源预加载
4. 使用了 font-display 优化字体加载体验

---

## 八、注意事项

### 开发环境

- 开发服务器可能需要清理缓存后才能正确加载新配置
- 如果遇到 PostCSS 错误，请检查 `postcss.config.js` 是否使用了正确的插件
- Tailwind CSS 4.x 的配置方式与 3.x 不同，需要使用 CSS-first 配置

### 生产环境

- 部署前务必运行 `npm run build` 测试构建
- 确保所有资源文件都能正确加载
- 验证 CDN 字体资源的可访问性
- 配置 Nginx 缓存策略以充分利用浏览器缓存

### 浏览器兼容性

- Tailwind CSS 4.x 支持现代浏览器
- 使用 PostCSS autoprefixer 确保跨浏览器兼容性
- font-display: swap 在大多数现代浏览器中支持良好

---

## 九、参考资料

- [Tailwind CSS 4.x 文档](https://tailwindcss.com/docs)
- [Google Fonts 最佳实践](https://web.dev/fast/#optimize-webfonts)
- [Vite 构建优化](https://vitejs.dev/guide/build.html)
- [前端性能优化方案](/doc/前端性能优化方案.md)