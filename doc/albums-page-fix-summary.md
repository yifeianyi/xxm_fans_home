# Next.js 迁移后图集页面问题修复总结

## 修复时间
2026-02-22

## 问题概述
Next.js 16 生产环境部署后，图集页面(`/albums`)出现两个问题：
1. **图片无法显示** - 缩略图和封面图返回 403 或无法加载
2. **路由跳转错误** - 点击图集后跳转到错误的 `/gallery/xxx` 路径

---

## 问题 1：图片无法显示

### 现象
- 图集页面显示"图集列表加载中..."但图片不显示
- Next.js 服务器日志出现大量错误：
  ```
  ⨯ The requested resource isn't a valid image for /media/gallery/thumbnails/... received null
  ```
- 直接访问图片 URL (`https://www.xxm8777.cn/gallery/...`) 返回 200，但在页面中不渲染

### 根本原因
Next.js 的 `<Image>` 组件会尝试对图片进行优化处理，但：
1. 项目配置了 `images.unoptimized: true`，但 Next.js 仍尝试处理外部图片
2. 图片 URL 是相对路径 (`/media/gallery/...`)，Next.js 尝试通过其图片优化服务处理
3. 生产环境中图片文件实际由 Nginx 直接提供，Next.js 无法访问这些文件进行优化

### 解决方案
**将所有 Next.js Image 组件替换为原生 `<img>` 标签**

涉及文件：
- `app/albums/components/ImageGrid.tsx`
- `app/albums/components/GalleryGrid.tsx`
- `app/albums/components/ChildrenImagesDisplay.tsx`
- `app/albums/components/ImageViewer.tsx`
- `app/gallery/components/ImageGrid.tsx`
- `app/gallery/components/GalleryGrid.tsx`
- `app/gallery/components/ChildrenImagesDisplay.tsx`
- `app/gallery/components/ImageViewer.tsx`

替换示例：
```tsx
// 删除
import Image from 'next/image';

// 替换前 (Next.js Image)
<Image
    src={image.thumbnailUrl || image.url}
    alt={image.title || image.filename}
    width={400}
    height={300}
    className="w-full h-auto object-cover"
    sizes="(max-width: 768px) 50vw, 33vw"
/>

// 替换后 (原生 img)
// eslint-disable-next-line @next/next/no-img-element
<img
    src={image.thumbnailUrl || image.url}
    alt={image.title || image.filename}
    className="w-full h-auto object-cover"
    loading="lazy"
/>
```

### 验证
- 重新构建并部署后，Next.js 日志不再出现图片错误
- 图集页面图片正常显示

---

## 问题 2：路由跳转错误

### 现象
- 访问 `/albums` 页面正常
- 点击任意图集后，URL 跳转到 `/gallery/xxxxx` 而非 `/albums/xxxxx`
- 导致浏览器访问的是旧的 gallery 页面

### 根本原因
代码中存在多处硬编码的 `/gallery` 路径：

1. **`app/albums/hooks/useGalleryData.ts`** (第 127 行和第 151 行)
   ```tsx
   router.push(`/gallery/${gallery.id}`);  // 图集点击跳转
   router.push('/gallery');                 // 面包屑首页跳转
   ```

2. **`app/albums/components/GalleryDetailClient.tsx`** (第 166 行)
   ```tsx
   onClick={() => router.push('/gallery')}   // 返回按钮跳转
   ```

3. **`app/albums/[id]/page.tsx`** (第 5 行)
   ```tsx
   import GalleryDetailClient from '../../gallery/components/GalleryDetailClient';  // 导入错误的组件
   ```

### 解决方案

#### 修复 1：useGalleryData.ts
```tsx
// 修复前
router.push(`/gallery/${gallery.id}`);
router.push('/gallery');

// 修复后
router.push(`/albums/${gallery.id}`);
router.push('/albums');
```

#### 修复 2：GalleryDetailClient.tsx
```tsx
// 修复前
onClick={() => router.push('/gallery')}

// 修复后
onClick={() => router.push('/albums')}
```

#### 修复 3：albums/[id]/page.tsx
```tsx
// 修复前
import GalleryDetailClient from '../../gallery/components/GalleryDetailClient';

// 修复后
import GalleryDetailClient from '../components/GalleryDetailClient';
```

### 验证
```bash
# 测试 albums 页面
curl -s -o /dev/null -w '%{http_code}' https://www.xxm8777.cn/albums
# 返回: 200 ✓

# 测试图集详情页
curl -s -o /dev/null -w '%{http_code}' https://www.xxm8777.cn/albums/LiveMoment
# 返回: 200 ✓

# 确认没有跳转到 gallery
curl -s -o /dev/null -w '%{http_code}' https://www.xxm8777.cn/gallery/LiveMoment
# 返回: 301 (gallery 页面仍存在但不再被跳转)
```

---

## 经验教训

### 1. Next.js Image 组件使用注意事项
- 使用 `next/image` 时，外部图片（非 `_next/static` 下的）需要配置 `remotePatterns`
- 即使设置了 `unoptimized: true`，Next.js 在某些情况下仍会尝试优化
- 对于 Nginx 直接提供的静态图片资源，使用原生 `<img>` 更可靠

### 2. 路由路径管理
- 避免在代码中硬编码路径字符串
- 建议使用常量或配置对象管理路由路径
- 复制代码时（如从 gallery 复制到 albums），必须全局检查路径引用

### 3. 代码复用风险
- `app/albums/` 最初是通过复制 `app/gallery/` 创建的
- 复制后需要全面检查：
  - 导入路径
  - 路由跳转
  - API 调用
  - 组件名称

---

## 相关文件变更

```
app/albums/components/ChildrenImagesDisplay.tsx    # 移除 next/image, 修复路由
app/albums/components/GalleryGrid.tsx              # 移除 next/image
app/albums/components/ImageGrid.tsx                # 移除 next/image
app/albums/components/ImageViewer.tsx              # 移除 next/image
app/albums/hooks/useGalleryData.ts                 # 修复路由路径
app/albums/[id]/page.tsx                           # 修复导入路径
app/gallery/components/ChildrenImagesDisplay.tsx   # 移除 next/image
app/gallery/components/GalleryGrid.tsx             # 移除 next/image
app/gallery/components/ImageGrid.tsx               # 移除 next/image
app/gallery/components/ImageViewer.tsx             # 移除 next/image
```

---

## 后续建议

1. **添加路由常量文件**
   ```ts
   // app/shared/constants/routes.ts
   export const ROUTES = {
     ALBUMS: '/albums',
     GALLERY: '/gallery',
     ALBUM_DETAIL: (id: string) => `/albums/${id}`,
     GALLERY_DETAIL: (id: string) => `/gallery/${id}`,
   } as const;
   ```

2. **统一图片组件**
   创建一个统一的图片组件，根据环境自动选择使用 Next.js Image 或原生 img：
   ```tsx
   // 对于需要 SEO 的首页大图使用 Next.js Image
   // 对于图集等大量图片使用原生 img
   ```

3. **添加 E2E 测试**
   测试图集页面的点击跳转和图片加载，防止回归。
