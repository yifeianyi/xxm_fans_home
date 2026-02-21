# WorkStatic 封面下载工具使用说明

## 概述

`download_workstatic_covers.py` 脚本用于将 WorkStatic 表中使用B站网络链接的封面下载到本地，并自动更新数据库中的URL。

## 功能特点

✅ **自动检测B站链接**：识别 `bilibili.com`、`hdslb.com` 等B站CDN链接  
✅ **自动下载封面**：使用项目已有的 `BilibiliCoverDownloader` 工具  
✅ **自动更新数据库**：下载成功后自动更新 `cover_url` 字段  
✅ **自动生成缩略图**：下载封面后自动生成优化的缩略图  
✅ **防重复下载**：检查文件是否存在，避免重复下载  
✅ **详细统计报告**：显示处理进度、成功/失败统计  
✅ **预览模式**：支持 dry-run 模式，只查看不下载  
✅ **智能限速**：每下载一个封面后随机延迟 1-3 秒，避免请求过快  
✅ **批量休息**：每处理 5 个封面后休息 10 秒，保护服务器资源  

## 脚本位置

```
tools/download_workstatic_covers.py      # 主脚本
tools/run_download_workstatic_covers.sh # 便捷运行脚本
```

## 使用方法

### 方法1：直接运行Python脚本

```bash
# 进入项目根目录
cd /home/yifeianyi/Desktop/xxm_fans_home

# 预览模式（只显示将要下载的封面，不实际下载）
python3 tools/download_workstatic_covers.py --dry-run

# 实际执行下载
python3 tools/download_workstatic_covers.py
```

### 方法2：使用Shell脚本

```bash
# 预览模式
./tools/run_download_workstatic_covers.sh --dry-run

# 实际执行下载
./tools/run_download_workstatic_covers.sh
```

## 参数说明

| 参数 | 说明 |
|------|------|
| `--dry-run` 或 `-d` | 预览模式，只显示将要下载的封面，不实际下载 |
| `--force` | 强制重新下载已存在的封面（当前未实现） |

## 输出示例

```
================================================================================
WorkStatic 封面下载工具
================================================================================

总共找到 223 个作品
================================================================================

处理作品 #221: 有多少人因为这首歌而认识了张韶涵？
  平台: 哔哩哔哩
  作品ID: BV1T8iKB9EQJ
  当前封面: http://i2.hdslb.com/bfs/archive/f5ae9088e370c70eb72b92c28919b15fe0ec6032.jpg
  🎯 检测到B站链接，准备下载
  开始下载封面: http://i2.hdslb.com/bfs/archive/f5ae9088e370c70eb72b92c28919b15fe0ec6032.jpg -> data_analytics/covers/BV1T8iKB9EQJ.jpg
  封面已下载: data_analytics/covers/BV1T8iKB9EQJ.jpg (123456 bytes)
  ✅ 缩略图生成成功: data_analytics/thumbnails/covers/BV1T8iKB9EQJ.webp
  ✅ 封面下载成功
     旧URL: http://i2.hdslb.com/bfs/archive/f5ae9088e370c70eb72b92c28919b15fe0ec6032.jpg
     新URL: /media/data_analytics/covers/BV1T8iKB9EQJ.jpg
  ⏱️  等待 2.3 秒后继续...

处理作品 #222: 当《长安姑娘》遇见长安幻想，一起打开盛唐奇幻之门！
  平台: bilibili
  作品ID: BV1d6qPBwEvr
  当前封面: /media/data_analytics/covers/BV1d6qPBwEvr.jpg
  ✅ 非B站链接或已是本地路径，跳过

================================================================================
处理完成
================================================================================
总作品数: 223
B站封面: 120
本地封面: 103
已下载: 120
跳过: 0
失败: 0
================================================================================
```

## 处理逻辑

### 1. 检测B站链接

脚本会检测以下B站相关的链接：
- `bilibili.com`
- `hdslb.com`
- `i0.hdslb.com`
- `i1.hdslb.com`
- `i2.hdslb.com`

### 2. 生成本地文件名

- 如果 `work_id` 是BV号（如 `BV1T8iKB9EQJ`），直接使用：`BV1T8iKB9EQJ.jpg`
- 如果不是BV号，添加平台前缀：`{platform}_{work_id}.jpg`

### 3. 下载封面

- 下载到 `data_analytics/covers/` 目录
- 使用 `BilibiliCoverDownloader` 工具
- 检查文件是否已存在，避免重复下载

### 4. 更新数据库

- 将 `cover_url` 从B站链接更新为本地路径
- 格式：`/media/data_analytics/covers/{work_id}.jpg`

### 5. 生成缩略图

- 使用 `ThumbnailGenerator` 自动生成缩略图
- 缩略图路径：`data_analytics/thumbnails/covers/{work_id}.webp`
- 缩略图尺寸：300x300px（保持宽高比）

## 文件路径规则

```
原图路径: data_analytics/covers/BV1234567890.jpg
缩略图路径: data_analytics/thumbnails/covers/BV1234567890.webp
缩略图URL: /media/data_analytics/thumbnails/covers/BV1234567890.webp
```

## 注意事项

1. **备份数据**：在执行前建议备份数据库
2. **预览模式**：首次使用建议先运行 `--dry-run` 查看将要下载的封面
3. **网络连接**：需要能够访问B站CDN的网络
4. **存储空间**：确保有足够的磁盘空间存储封面图片
5. **文件权限**：确保对 `media/data_analytics/covers/` 目录有写权限
6. **下载速度**：脚本已内置限速机制，每下载一个封面后随机延迟 1-3 秒，每处理 5 个封面后休息 10 秒

## 统计信息说明

| 字段 | 说明 |
|------|------|
| `total` | 总作品数 |
| `bilibili_covers` | 使用B站链接的封面数 |
| `local_covers` | 已是本地路径的封面数 |
| `downloaded` | 成功下载的封面数 |
| `skipped` | 跳过的封面数（已存在或非B站链接） |
| `failed` | 下载失败的封面数 |
| `errors` | 错误详情列表 |

## 故障排查

### 问题1：下载失败

**可能原因：**
- 网络连接问题
- B站CDN访问受限
- 封面URL已失效

**解决方法：**
- 检查网络连接
- 查看错误详情
- 手动访问封面URL确认是否有效

### 问题2：权限错误

**可能原因：**
- `media/data_analytics/covers/` 目录不可写

**解决方法：**
```bash
chmod -R 755 media/data_analytics/covers/
```

### 问题3：数据库更新失败

**可能原因：**
- 数据库连接问题
- 字段类型不匹配

**解决方法：**
- 检查数据库连接
- 查看 Django 日志

## 相关文件

- `tools/bilibili/cover_downloader.py` - B站封面下载器
- `core/thumbnail_generator.py` - 缩略图生成器
- `data_analytics/models.py` - WorkStatic 模型
- `data_analytics/services/bilibili_service.py` - B站导入服务

## 下载速度配置

脚本内置了智能限速机制，避免请求过快导致被B站限制：

| 配置项 | 默认值 | 说明 |
|--------|--------|------|
| `DOWNLOAD_DELAY_MIN` | 1.0 秒 | 最小延迟时间 |
| `DOWNLOAD_DELAY_MAX` | 3.0 秒 | 最大延迟时间 |
| `BATCH_SIZE` | 5 | 每批次处理数量 |

**工作原理：**
- 每下载一个封面后，随机延迟 1-3 秒
- 每处理 5 个封面后，额外休息 10 秒
- 这种方式既能保证下载速度，又不会给服务器造成压力

**修改配置：**
如果需要调整下载速度，可以修改脚本中的配置变量：

```python
# 下载配置
DOWNLOAD_DELAY_MIN = 1.0   # 最小延迟时间（秒）
DOWNLOAD_DELAY_MAX = 3.0   # 最大延迟时间（秒）
BATCH_SIZE = 5             # 每批次处理数量
```

## 后续优化建议

1. **进度条**：添加进度条显示下载进度
2. **断点续传**：支持中断后继续下载
3. **日志记录**：将处理日志保存到文件
4. **定时任务**：支持定期自动执行
5. **并发下载**：支持多线程并发下载（已有限速保护）

---

**版本：** 1.0  
**创建日期：** 2026-01-31  
**作者：** iFlow CLI