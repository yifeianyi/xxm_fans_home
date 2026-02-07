# Livestream 封面迁移脚本报告

## 概述

本文档记录了为 `Livestream` 模型添加 `cover_url` 字段并从 `SongRecord` 迁移封面数据的完整过程。

## 背景

为了完善直播回放功能，需要在 `Livestream` 模型中存储回放的封面图片地址。由于 `SongRecord` 表中已经存储了演唱记录的封面信息，可以通过日期匹配将相关封面同步到 `Livestream` 表中。

## 实施内容

### 1. 数据库模型修改

**文件**: `repo/xxm_fans_backend/livestream/models.py`

在 `Livestream` 模型中添加了 `cover_url` 字段：

```python
# 回放封面
cover_url = models.CharField(
    max_length=300,
    blank=True,
    null=True,
    verbose_name='回放封面URL',
    help_text='直播回放的封面图片URL'
)
```

### 2. 数据库迁移

**迁移文件**: `livestream/migrations/0002_livestream_cover_url.py`

```bash
cd /home/yifeianyi/Desktop/xxm_fans_home/repo/xxm_fans_backend
python3 manage.py makemigrations livestream
```

迁移内容：为 `livestream` 表添加 `cover_url` 字段。

### 3. 数据迁移脚本

**脚本文件**: `repo/xxm_fans_backend/tools/migrate_livestream_cover.py`

**功能说明**：
- 遍历所有 `Livestream` 记录
- 根据日期匹配查找当天的 `SongRecord` 记录
- 优先选择第一个有封面的演唱记录
- 将封面 URL 设置到 `Livestream.cover_url` 字段

**核心逻辑**：
```python
# 查找当天的演唱记录（按日期匹配，并优先选择有封面的记录）
song_records = SongRecord.objects.filter(
    performed_at=livestream.date
).exclude(cover_url__isnull=True).exclude(cover_url='').order_by('id')

# 取第一个有封面的演唱记录
first_record = song_records.first()

# 更新直播记录的封面
livestream.cover_url = first_record.cover_url
livestream.save(update_fields=['cover_url'])
```

## 迁移结果

执行脚本后的统计信息：

| 统计项 | 数量 |
|--------|------|
| 总直播记录数 | 1828 |
| 成功更新封面 | 1675 |
| 当天无演唱记录 | 153 |
| 迁移成功率 | 91.63% |

### 结果分析

- **1675 条直播记录**成功从 `SongRecord` 中获取了封面
- **153 条直播记录**因为当天没有对应的演唱记录而未设置封面
  - 这些直播可能是非歌唱类直播，或者数据缺失
  - 可以通过 `live_moment` 目录中的截图作为备选封面

## 脚本使用流程

### 前置条件

1. 确保 Django 环境已正确配置
2. 确保数据库迁移已执行
3. 确保 `SongRecord` 表中存在封面数据

### 使用步骤

#### 步骤 1：创建数据库迁移

```bash
cd /home/yifeianyi/Desktop/xxm_fans_home/repo/xxm_fans_backend
python3 manage.py makemigrations livestream
```

#### 步骤 2：应用数据库迁移

```bash
python3 manage.py migrate livestream
```

#### 步骤 3：运行数据迁移脚本

```bash
python3 tools/migrate_livestream_cover.py
```

**输出示例**：
```
============================================================
开始迁移直播回放封面...
============================================================

找到 1828 条直播记录

处理: 2025-11-30 - 咻咻满-2025年11月30日-录播
  ✓ 已设置封面: /covers/2025/11/2025-11-30.jpg
处理: 2025-11-29 - 咻咻满-2025年11月29日-录播
  ✓ 已设置封面: /covers/2025/11/2025-11-29.jpg
...
============================================================
迁移完成!
============================================================
成功更新: 1675 条
当天没有演唱记录: 153 条
当天没有封面: 0 条
============================================================
```

### 重复执行

脚本可以安全地重复执行。如果某条直播记录已经有 `cover_url`，脚本会重新设置为当天第一个有封面的演唱记录的封面。

## 注意事项

1. **数据库备份**：在大规模数据迁移前，建议先备份数据库
   ```bash
   cp data/db.sqlite3 data/backups/db_backup_$(date +%Y%m%d_%H%M%S).sqlite3
   ```

2. **测试环境**：建议先在测试环境中运行脚本，验证结果后再在生产环境执行

3. **封面格式**：脚本假设 `SongRecord.cover_url` 存储的是相对路径（如 `/covers/2025/11/2025-11-30.jpg`），如果需要支持完整 URL，可能需要调整脚本逻辑

4. **缺失封面处理**：对于当天没有演唱记录的直播，后续可以通过以下方式补充封面：
   - 使用 `live_moment` 目录中的第一张截图
   - 使用默认封面图片
   - 手动指定封面

## 后续优化建议

1. **自动化同步**：可以考虑添加信号机制，在新增 `SongRecord` 或 `Livestream` 时自动同步封面

2. **封面优先级**：完善封面选择逻辑，例如优先选择封面尺寸最大的图片

3. **日志记录**：增强脚本的日志记录功能，记录更多详细信息以便追踪

4. **错误处理**：添加更完善的异常处理，确保单个记录失败不影响整体迁移

## 相关文件

- **模型定义**: `repo/xxm_fans_backend/livestream/models.py`
- **迁移文件**: `repo/xxm_fans_backend/livestream/migrations/0002_livestream_cover_url.py`
- **迁移脚本**: `repo/xxm_fans_backend/tools/migrate_livestream_cover.py`

## 版本信息

- **创建日期**: 2026-01-31
- **Django 版本**: 5.2.3
- **Python 版本**: 3.10.12