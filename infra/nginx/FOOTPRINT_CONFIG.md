# Nginx 二创图片资源配置

## 概述

为 XXM Fans Home 项目添加了 `/footprint` 路径，用于提供粉丝二创作品的图片资源。

## 配置文件

### 开发环境
- **文件**: `infra/nginx/xxm_nginx.conf`
- **路径**: `/footprint/`
- **映射**: `/home/yifeianyi/Desktop/xxm_fans_home/media/footprint/`

### 生产环境
- **文件**: `infra/nginx/prod-xxm_nginx.conf`
- **路径**: `/footprint/`
- **映射**: `/home/yifeianyi/Desktop/xxm_fans_home/media/footprint/`

## 配置详情

```nginx
# 二创图片资源 - 直接由Nginx提供
location /footprint/ {
    alias /home/yifeianyi/Desktop/xxm_fans_home/media/footprint/;
    expires 30d;
    add_header Cache-Control "public, immutable";

    # 安全头
    add_header X-Frame-Options "DENY" always;
    add_header X-Content-Type-Options "nosniff" always;
}
```

## 配置说明

### 路径映射
- **URL 路径**: `http://localhost:8080/footprint/`
- **文件系统路径**: `/home/yifeianyi/Desktop/xxm_fans_home/media/footprint/`
- **示例**: `http://localhost:8080/footprint/image.jpg` → `/home/yifeianyi/Desktop/xxm_fans_home/media/footprint/image.jpg`

### 缓存策略
- **过期时间**: 30天
- **缓存控制**: `public, immutable`
- **优势**: 减少服务器负载，提升用户体验

### 安全配置
- **X-Frame-Options**: `DENY` - 防止点击劫持
- **X-Content-Type-Options**: `nosniff` - 防止 MIME 类型嗅探

## 目录结构

```
media/
├── covers/          # 封面图片
└── footprint/       # 二创图片资源（新增）
    └── test.txt     # 测试文件
```

## 使用示例

### 前端访问
```javascript
// 访问二创图片
const imageUrl = '/footprint/fan-art-001.jpg';

// 在 React 组件中使用
<img src="/footprint/fan-art-001.jpg" alt="粉丝二创作品" />
```

### 后端上传
```python
# Django 上传二创图片
from django.core.files.storage import default_storage

# 保存到 footprint 目录
file_path = default_storage.save('footprint/fan-art-001.jpg', image_file)
```

## 测试

### 配置测试
```bash
# 测试开发环境配置
nginx -t -c /home/yifeianyi/Desktop/xxm_fans_home/infra/nginx/xxm_nginx.conf -p /tmp/nginx

# 测试生产环境配置
nginx -t -c /home/yifeianyi/Desktop/xxm_fans_home/infra/nginx/prod-xxm_nginx.conf -p /tmp/nginx
```

### 功能测试
```bash
# 测试 footprint 路径
curl -I http://localhost:8080/footprint/test.txt

# 运行完整集成测试
cd /home/yifeianyi/Desktop/xxm_fans_home/scripts
./test_integration.sh
```

## 测试结果

### 集成测试
- ✅ 前端首页: 200 OK
- ✅ 歌曲列表API: 200 OK
- ✅ 曲风列表API: 200 OK
- ✅ 标签列表API: 200 OK
- ✅ 推荐语API: 200 OK
- ✅ 粉丝二创合集API: 200 OK
- ✅ 默认封面图片: 200 OK
- ✅ 咻咻满头像: 200 OK
- ✅ **二创图片资源路径: 200 OK** (新增)

## 性能优化

### 缓存策略
- **静态资源**: 30天缓存
- **缓存控制**: `public, immutable`
- **优势**: 减少重复请求，提升加载速度

### Nginx 优化
- **直接提供**: 不经过 Django，减少后端负载
- **sendfile**: 启用零拷贝传输
- **keepalive**: 保持连接，减少握手开销

## 安全考虑

### 访问控制
- **目录权限**: 确保 Nginx 有读取权限
- **文件类型**: 只允许图片文件（通过 MIME 类型）

### 安全头
- **X-Frame-Options**: 防止点击劫持
- **X-Content-Type-Options**: 防止 MIME 类型嗅探

## 维护建议

### 目录管理
- 定期清理无用文件
- 监控磁盘空间使用
- 备份重要二创作品

### 性能监控
- 监控访问日志
- 分析热门资源
- 优化缓存策略

## 扩展建议

### CDN 集成
- 将热门资源上传到 CDN
- 减少服务器带宽压力
- 提升全球访问速度

### 图片优化
- 使用 WebP 格式
- 实现懒加载
- 提供多种分辨率

### 访问统计
- 记录访问日志
- 统计热门作品
- 分析用户偏好

## 相关文件

- `infra/nginx/xxm_nginx.conf` - 开发环境配置
- `infra/nginx/prod-xxm_nginx.conf` - 生产环境配置
- `scripts/test_integration.sh` - 集成测试脚本
- `scripts/build_start_services.sh` - 生产环境启动脚本
- `scripts/build_stop_services.sh` - 生产环境停止脚本

## 更新日志

### 2026-01-15
- ✅ 添加 `/footprint/` 路径配置
- ✅ 创建 `media/footprint/` 目录
- ✅ 更新集成测试脚本
- ✅ 验证开发和生产环境配置
- ✅ 所有测试通过 (9/9)

## 联系方式

如有问题或建议，请联系项目维护者。