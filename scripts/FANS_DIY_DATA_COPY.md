# fansDIY 数据复制记录

## 任务概述

将 `data/db_backup.sqlite3` 中的 fansDIY 相关表数据复制到 `data/db.sqlite3` 的 fansDIY 中。

## 执行时间

- **日期**: 2026-01-15
- **状态**: ✅ 成功完成

## 数据库信息

### 源数据库
- **路径**: `/home/yifeianyi/Desktop/xxm_fans_home/data/db_backup.sqlite3`
- **大小**: 5.1M
- **表结构**: 包含旧的 main 应用表和 fansDIY 表

### 目标数据库
- **路径**: `/home/yifeianyi/Desktop/xxm_fans_home/data/db.sqlite3`
- **大小**: 5.4M
- **表结构**: 重构后的应用表结构

## 复制的表

### 1. fansDIY_collection
- **记录数**: 8 条
- **字段**:
  - id: 主键
  - name: 合集名称
  - works_count: 作品数量
  - created_at: 创建时间
  - updated_at: 更新时间
  - display_order: 显示顺序
  - position: 位置

### 2. fansDIY_work
- **记录数**: 70 条
- **字段**:
  - id: 主键
  - title: 作品标题
  - view_url: 观看链接
  - author: 作者
  - collection_id: 所属合集ID
  - notes: 备注
  - display_order: 显示顺序
  - position: 位置
  - cover_url: 封面URL

## 执行步骤

### 1. 创建备份
```bash
# 自动备份目标数据库
cp data/db.sqlite3 data/db.sqlite3.bak
```

### 2. 执行数据复制
```bash
python3 scripts/copy_fansdiy_data.py
```

### 3. 验证数据
```bash
python3 scripts/verify_fansdiy_data.py
```

### 4. 测试 API
```bash
# 测试合集 API
curl http://127.0.0.1:8080/api/fansDIY/collections/

# 测试作品 API
curl http://127.0.0.1:8080/api/fansDIY/works/
```

## 执行结果

### 数据复制
- ✅ fansDIY_collection: 8 条记录复制成功
- ✅ fansDIY_work: 70 条记录复制成功

### 数据验证
- ✅ 记录数匹配
- ✅ 样本数据匹配
- ✅ 数据完整性验证通过

### API 测试
- ✅ 粉丝二创合集 API: 200 OK
- ✅ 粉丝二创作品 API: 200 OK
- ✅ 集成测试: 9/9 通过

## 备份信息

### 自动备份
- **备份文件**: `data/db.sqlite3.bak`
- **创建时间**: 2026-01-15
- **用途**: 数据复制前的安全备份

### 恢复方法
如果需要恢复到复制前的状态：
```bash
cp data/db.sqlite3.bak data/db.sqlite3
```

## 数据样本

### fansDIY_collection 样本
```
1. 一、高能混剪 (16 部作品)
2. 二、"百变"满满 (12 部作品)
3. 三、历年生日 (10 部作品)
```

### fansDIY_work 样本
```
1. 【邓紫棋×咻咻满】来自天堂的魔鬼（伪合唱）
   作者: yoyowon7
   BV号: BV18dvfeAEkg

2. 【邓紫棋×咻咻满】天空没有极限 我的未来无边（伪合唱）
   作者: yoyowon7
   BV号: BV1Ht421M72Y

3. 【周深×咻咻满】《铃芽之旅》～双语双声道伪合唱
   作者: yoyowon7
   BV号: BV17m4y1674B
```

## 注意事项

### 数据完整性
- ✅ 所有主键和外键关系保持完整
- ✅ 时间戳数据正确保留
- ✅ 显示顺序和位置信息完整

### 封面路径
- 所有封面路径使用 `/footprint/` 前缀
- Nginx 已配置 `/footprint/` 路径映射
- 图片资源路径正确

### API 兼容性
- ✅ API 响应格式正确
- ✅ 分页功能正常
- ✅ 关联查询正常

## 相关文件

### 脚本文件
- `scripts/copy_fansdiy_data.py` - 数据复制脚本
- `scripts/verify_fansdiy_data.py` - 数据验证脚本

### 数据库文件
- `data/db_backup.sqlite3` - 源数据库
- `data/db.sqlite3` - 目标数据库
- `data/db.sqlite3.bak` - 备份文件

### 配置文件
- `infra/nginx/prod-xxm_nginx.conf` - 生产环境 Nginx 配置
- `infra/nginx/xxm_nginx.conf` - 开发环境 Nginx 配置

## 后续操作

### 1. 清理备份文件（可选）
如果确认数据复制无误，可以删除备份文件：
```bash
rm data/db.sqlite3.bak
```

### 2. 更新前端缓存
如果前端有缓存，需要清除缓存以显示最新数据。

### 3. 监控数据访问
监控 API 访问情况，确保数据正常使用。

## 问题排查

### 如果数据不显示
1. 检查数据库文件权限
2. 重启 Gunicorn 服务
3. 清除浏览器缓存

### 如果 API 返回错误
1. 检查 Gunicorn 日志: `/tmp/gunicorn_error.log`
2. 检查 Nginx 日志: `/tmp/nginx/error.log`
3. 验证数据库连接

### 如果封面图片无法加载
1. 检查 `/footprint/` 路径配置
2. 确认图片文件存在
3. 检查文件权限

## 总结

✅ **任务完成**: fansDIY 数据已成功从备份数据库复制到主数据库
✅ **数据验证**: 所有数据完整性检查通过
✅ **功能测试**: API 和集成测试全部通过
✅ **备份保护**: 已创建备份文件，可随时恢复

## 联系方式

如有问题或需要帮助，请联系项目维护者。