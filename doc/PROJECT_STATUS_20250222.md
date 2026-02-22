# XXM Fans Home 项目状态报告

**日期**: 2026-02-22  
**版本**: v2.0 (Vite + React 18)  
**状态**: 已稳定部署

---

## 1. 当前技术架构

### 1.1 前端技术栈
| 项目 | 版本 | 说明 |
|------|------|------|
| React | 18.3.1 | UI 框架（已从 React 19 降级） |
| React Router | 7.12.0 | 路由管理 |
| Vite | 6.2.0 | 构建工具 |
| TypeScript | 5.x | 类型系统 |
| Tailwind CSS | 3.x | 样式框架 |
| SWR | 2.4.0 | 数据获取与缓存 |
| Lucide React | 0.562.0 | 图标库 |

### 1.2 后端技术栈
| 项目 | 版本 | 说明 |
|------|------|------|
| Django | 5.2.3 | Web 框架 |
| Django REST Framework | 3.15.2 | API 框架 |
| Python | 3.10+ | 编程语言 |
| SQLite | - | 数据库 |

### 1.3 部署架构
```
用户 → Nginx (443/80) → 静态文件 (dist/)
                ↓
         API 请求 (/api) → Django (8000)
```

- **Web 服务器**: Nginx
- **前端部署**: 静态文件（dist 目录）
- **后端部署**: Gunicorn + Django
- **域名**: https://www.xxm8777.cn

---

## 2. 近期重要变更

### 2.1 回滚 Next.js 迁移 (2026-02-22)
**原因**: Next.js 16 在生产环境出现严重的部署问题
- standalone 构建产物上传后缺失 static 目录
- Nginx 需要额外配置 `/_next/static` 路径
- React 19 与 Vite 代码分割产生兼容性问题

**解决方案**: 回滚到稳定的 Vite + React 18 方案

**操作步骤**:
```bash
# 切换到 v2.0 tag
git checkout v2.0

# 降级 React 版本
npm install react@18 react-dom@18

# 修复构建配置（移除 manualChunks）
# 见 vite.config.prod.ts

# 构建并部署
npm run build
rsync -avz dist/ server:/path/to/dist/
```

### 2.2 演唱记录懒加载修复 (2026-02-22)
**问题**: 展开演唱记录只显示一页内容（20条），无法加载更多

**解决方案**: 重写 `RecordList.tsx` 组件
- 使用 Intersection Observer 实现无限滚动
- 使用 `loadedPages` Set 防止重复加载
- 使用 `loadingRef` 防止并发请求
- 修复 `hasMore` 判断逻辑

**关键代码**:
```typescript
// 防止重复加载
const loadedPages = useRef(new Set<number>());

// 无限滚动
const observer = new IntersectionObserver((entries) => {
    if (entries[0].isIntersecting && hasMore && !isLoading) {
        loadMore();
    }
});
```

---

## 3. 已知问题与解决方案

### 3.1 已修复
| 问题 | 状态 | 修复方案 |
|------|------|----------|
| 演唱记录只显示一页 | ✅ 已修复 | 无限滚动懒加载 |
| Next.js 部署样式丢失 | ✅ 已修复 | 回滚到 Vite |
| React 19 兼容性问题 | ✅ 已修复 | 降级到 React 18 |
| Vite 代码分割报错 | ✅ 已修复 | 移除 manualChunks |

### 3.2 待处理
| 问题 | 优先级 | 说明 |
|------|--------|------|
| Nginx 配置警告 | P3 | server name 冲突警告，不影响功能 |
| 字体 404 | P3 | Google Fonts 部分资源加载失败 |

---

## 4. 部署指南

### 4.1 开发环境
```bash
# 1. 启动后端
cd repo/xxm_fans_backend
python manage.py runserver 0.0.0.0:8000

# 2. 启动前端
cd repo/xxm_fans_frontend
npm run dev

# 访问 http://localhost:5173
```

### 4.2 生产部署
```bash
# 1. 构建前端
cd repo/xxm_fans_frontend
npm run build

# 2. 复制静态资源
cp -r public dist/

# 3. 部署到服务器
rsync -avz --delete dist/ server:/path/to/dist/

# 4. 重载 Nginx
sudo nginx -s reload
```

---

## 5. 前端构建配置

### vite.config.prod.ts 关键配置
```typescript
export default defineConfig({
    plugins: [react()],
    build: {
        minify: 'terser',
        terserOptions: {
            compress: {
                drop_console: true,
                drop_debugger: true,
                // 注意: drop_comments 不是标准选项
            },
        },
        // 移除了 manualChunks 以避免循环依赖
    }
})
```

**注意事项**:
- `drop_comments` 不是 Terser 标准选项，已移除
- 不推荐使用 `manualChunks` 进行复杂的代码分割，可能导致 React 加载顺序问题

---

## 6. 项目目录结构

```
xxm_fans_home/
├── repo/xxm_fans_backend/     # Django 后端
│   ├── song_management/       # 歌曲管理
│   ├── fansDIY/              # 粉丝二创
│   ├── gallery/              # 图集管理
│   └── ...
├── repo/xxm_fans_frontend/    # Vite + React 前端 (v2.0)
│   ├── dist/                 # 构建产物
│   ├── presentation/         # UI 组件和页面
│   ├── infrastructure/       # API 服务和数据获取
│   ├── domain/               # 类型定义和业务逻辑
│   └── ...
├── infra/nginx/              # Nginx 配置
├── media/                    # 媒体文件
└── doc/                      # 文档
```

---

## 7. API 接口状态

| 模块 | 状态 | 说明 |
|------|------|------|
| 歌曲列表 | ✅ 正常 | `/api/songs/` |
| 演唱记录 | ✅ 正常 | `/api/songs/{id}/records/` |
| 粉丝二创 | ✅ 正常 | `/api/fansDIY/` |
| 图集 | ✅ 正常 | `/api/gallery/` |
| 直播日历 | ✅ 正常 | `/api/livestream/` |

---

## 8. 后续建议

### 8.1 短期优化
1. **演唱记录分页**: 当前已修复，建议测试大数据量表现
2. **图片懒加载**: 图集页面可添加图片懒加载优化
3. **Nginx 配置**: 清理重复的 server name 配置

### 8.2 长期规划
1. **Next.js 迁移评估**: 
   - 当前 v2.0 (Vite) 稳定运行
   - 如需再次迁移到 Next.js，建议：
     - 先在测试环境完整验证
     - 确保 standalone 构建产物完整
     - 准备完整的回滚方案

2. **性能优化**:
   - 添加 Service Worker 缓存
   - 图片 CDN 加速
   - 路由懒加载

3. **监控告警**:
   - 添加前端错误监控 (Sentry)
   - 后端性能监控
   - 服务可用性告警

---

## 9. 相关文档

- `DEPLOY_README.md` - 部署脚本说明
- `AGENTS.md` - 项目技术规范
- `README.md` - 项目说明

---

**记录人**: AI Assistant  
**更新时间**: 2026-02-22 12:25
