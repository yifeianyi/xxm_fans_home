# 数据库混合架构迁移方案（MySQL主从 + SQLite3单库）

## 1. 迁移背景

### 1.1 当前问题
- **数据库类型**: SQLite3
- **写入频率**: 每小时 200-300 条数据
- **需求**: 实现读写分离，主数据库负责写入，从数据库负责读取
- **架构要求**: 混合数据库架构（MySQL + SQLite3）

### 1.2 迁移策略
采用**混合数据库架构**：
- **主数据库（default）**: 迁移到 MySQL，实现读写分离，应对核心业务的高并发写入
- **歌单数据库（songlist_db）**: 继续使用 SQLite3，保持轻量级和简单部署

### 1.3 SQLite3 的局限性
- ❌ **不支持主从复制**: SQLite3 是文件型数据库，无法实现主从架构
- ❌ **并发写入限制**: SQLite3 在高并发写入场景下性能较差
- ❌ **无法实现读写分离**: 无法将读写操作分离到不同的数据库实例
- ❌ **扩展性差**: 不适合大规模生产环境

### 1.4 MySQL 的优势
- ✅ **支持主从复制**: 原生支持主从复制，实现读写分离
- ✅ **高并发性能**: 支持高并发读写操作
- ✅ **成熟稳定**: 广泛应用于生产环境
- ✅ **易于扩展**: 支持水平扩展和垂直扩展
- ✅ **丰富的工具**: 生态完善，监控和备份工具丰富

### 1.5 混合架构优势
- ✅ **核心业务高性能**: 主数据库使用 MySQL 读写分离
- ✅ **歌单系统轻量级**: 歌单数据库继续使用 SQLite3
- ✅ **降低迁移复杂度**: 只迁移主数据库，减少风险
- ✅ **节省资源**: 不需要为歌单数据库配置 MySQL 主从
- ✅ **灵活扩展**: 未来可以根据需要独立扩展各数据库

---

## 2. MySQL 主从架构设计

### 2.1 架构拓扑

```
                    ┌─────────────┐
                    │   应用层    │
                    │  (Django)  │
                    └──────┬──────┘
                           │
              ┌────────────┴────────────┐
              │                         │
              ▼                         ▼
    ┌─────────────────┐       ┌─────────────────┐
    │   主数据库      │       │   从数据库      │
    │  (MySQL Master) │◄──────│  (MySQL Slave)  │
    │   写操作        │       │   读操作        │
    │  (default)      │       │  (default)      │
    └─────────────────┘       └─────────────────┘
              ▲                         │
              └─────────────────────────┘
                    二进制日志复制

                    ┌─────────────────┐
                    │  歌单数据库     │
                    │  (SQLite3)      │
                    │  读写操作       │
                    │ (songlist_db)   │
                    └─────────────────┘
```

**架构说明**:
- **MySQL 主从**: 用于核心业务（歌曲管理、网站设置、数据分析），实现读写分离
- **SQLite3 单库**: 用于模板化歌单系统，保持轻量级和简单部署

### 2.2 数据库规划

根据项目当前结构，采用混合数据库架构：

| 数据库名称 | 用途 | 数据库类型 | 读写分离 |
|-----------|------|-----------|----------|
| `default` | 主数据库（歌曲管理、网站设置、数据分析等） | MySQL | ✅ 是（Master写 + Slave读） |
| `songlist_db` | 模板化歌单数据库 | SQLite3 | ❌ 否（单库读写） |

**说明**:
- **主数据库（default）**: 迁移到 MySQL 并实现读写分离，应对每小时 200-300 条数据写入
- **歌单数据库（songlist_db）**: 继续使用 SQLite3，配置简单，无需读写分离
- **view_data_db**: 已废弃，数据已合并到主数据库

**混合架构优势**:
- ✅ 核心业务数据库（主库）获得 MySQL 的高性能和读写分离能力
- ✅ 歌单数据库保持 SQLite3 的轻量级和易部署特性
- ✅ 减少迁移复杂度和运维成本

---

## 3. 环境准备

### 3.1 安装 MySQL

#### Ubuntu/Debian
```bash
sudo apt update
sudo apt install mysql-server mysql-client
sudo systemctl start mysql
sudo systemctl enable mysql
```

#### CentOS/RHEL
```bash
sudo yum install mysql-server
sudo systemctl start mysqld
sudo systemctl enable mysqld
```

#### macOS
```bash
brew install mysql
brew services start mysql
```

### 3.2 安装 Python MySQL 驱动

```bash
cd /home/yifeianyi/Desktop/xxm_fans_home/repo/xxm_fans_backend
pip install mysqlclient
```

**注意**: `mysqlclient` 需要 MySQL 开发库，如果安装失败，先安装：

```bash
# Ubuntu/Debian
sudo apt install default-libmysqlclient-dev build-essential

# CentOS/RHEL
sudo yum install mysql-devel gcc
```

### 3.3 安装 MySQL 主从复制工具

```bash
# 主从同步监控工具（可选）
pip install mysql-replication
```

---

## 4. MySQL 配置

### 4.1 主数据库配置 (Master)

编辑 `/etc/mysql/mysql.conf.d/mysqld.cnf` 或 `/etc/my.cnf`：

```ini
[mysqld]
# 服务器唯一ID，主从必须不同
server-id = 1

# 启用二进制日志
log-bin = mysql-bin

# 二进制日志格式（推荐使用ROW）
binlog_format = ROW

# 需要复制的数据库
binlog-do-db = xxm_fans_home
binlog-do-db = songlist_db

# 不需要复制的数据库
binlog-ignore-db = mysql
binlog-ignore-db = information_schema
binlog-ignore-db = performance_schema
binlog-ignore-db = sys

# GTID 模式（推荐，更可靠的复制方式）
gtid_mode = ON
enforce_gtid_consistency = ON

# 性能优化
innodb_buffer_pool_size = 1G
innodb_log_file_size = 256M
innodb_flush_log_at_trx_commit = 1
sync_binlog = 1
```

重启 MySQL：
```bash
sudo systemctl restart mysql
```

### 4.2 从数据库配置 (Slave)

编辑从数据库的配置文件：

```ini
[mysqld]
# 服务器唯一ID，必须与主库不同
server-id = 2

# 启用中继日志
relay-log = relay-bin

# GTID 模式
gtid_mode = ON
enforce_gtid_consistency = ON

# 只读模式（防止从库被误写）
read_only = 1
super_read_only = 1

# 性能优化
innodb_buffer_pool_size = 1G
```

重启 MySQL：
```bash
sudo systemctl restart mysql
```

### 4.3 创建复制用户

在主数据库上执行：

```sql
-- 登录 MySQL
sudo mysql

-- 创建复制用户
CREATE USER 'replication_user'@'%' IDENTIFIED BY 'your_strong_password';

-- 授予复制权限
GRANT REPLICATION SLAVE ON *.* TO 'replication_user'@'%';

-- 刷新权限
FLUSH PRIVILEGES;

-- 查看主库状态
SHOW MASTER STATUS;
```

记录下 `File` 和 `Position` 的值，配置从库时需要使用。

### 4.4 配置从数据库同步

在从数据库上执行：

```sql
-- 登录 MySQL
sudo mysql

-- 配置主库信息（使用 GTID 方式，推荐）
CHANGE MASTER TO
  MASTER_HOST='master_db_ip',
  MASTER_USER='replication_user',
  MASTER_PASSWORD='your_strong_password',
  MASTER_PORT=3306,
  MASTER_AUTO_POSITION=1;

-- 启动复制
START SLAVE;

-- 查看复制状态
SHOW SLAVE STATUS\G
```

检查 `Slave_IO_Running` 和 `Slave_SQL_Running` 是否都为 `Yes`。

---

## 5. Django 配置修改

### 5.1 修改 `requirements.txt`

添加 MySQL 客户端库：

```txt
Django==5.2.3
djangorestframework==3.15.2
python-dotenv==1.0.1
requests==2.31.0
Pillow==10.2.0
django-cors-headers==4.9.0
mysqlclient==2.2.0  # 新增
```

### 5.2 修改环境变量

编辑 `env/backend.env`：

```bash
# 主数据库配置（写操作）- MySQL
MASTER_DB_HOST=localhost
MASTER_DB_PORT=3306
MASTER_DB_NAME=xxm_fans_home
MASTER_DB_USER=xxm_master_user
MASTER_DB_PASSWORD=your_master_password

# 从数据库配置（读操作）- MySQL
SLAVE_DB_HOST=localhost
SLAVE_DB_PORT=3307
SLAVE_DB_NAME=xxm_fans_home
SLAVE_DB_USER=xxm_slave_user
SLAVE_DB_PASSWORD=your_slave_password

# 注意：歌单数据库（songlist_db）继续使用 SQLite3，无需额外配置
```

### 5.3 修改 `settings.py`

替换数据库配置部分：

```python
# Database
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases

# 主数据库配置（写操作）
MASTER_DB = {
    'ENGINE': 'django.db.backends.mysql',
    'NAME': os.getenv('MASTER_DB_NAME', 'xxm_fans_home'),
    'USER': os.getenv('MASTER_DB_USER', 'xxm_master_user'),
    'PASSWORD': os.getenv('MASTER_DB_PASSWORD', ''),
    'HOST': os.getenv('MASTER_DB_HOST', 'localhost'),
    'PORT': os.getenv('MASTER_DB_PORT', '3306'),
    'OPTIONS': {
        'charset': 'utf8mb4',
        'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
    },
    'CONN_MAX_AGE': 60,  # 连接池
}

# 从数据库配置（读操作）
SLAVE_DB = {
    'ENGINE': 'django.db.backends.mysql',
    'NAME': os.getenv('SLAVE_DB_NAME', 'xxm_fans_home'),
    'USER': os.getenv('SLAVE_DB_USER', 'xxm_slave_user'),
    'PASSWORD': os.getenv('SLAVE_DB_PASSWORD', ''),
    'HOST': os.getenv('SLAVE_DB_HOST', 'localhost'),
    'PORT': os.getenv('SLAVE_DB_PORT', '3307'),
    'OPTIONS': {
        'charset': 'utf8mb4',
        'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
    },
    'CONN_MAX_AGE': 60,
}

# 歌单数据库配置（继续使用 SQLite3）
SONGLIST_DB = {
    'ENGINE': 'django.db.backends.sqlite3',
    'NAME': str(DATA_DIR / 'songlist.sqlite3'),
    'OPTIONS': {
        'timeout': 20,
    },
}

# 默认数据库配置（混合架构：MySQL主从 + SQLite3单库）
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': os.getenv('MASTER_DB_NAME', 'xxm_fans_home'),
        'USER': os.getenv('MASTER_DB_USER', 'xxm_master_user'),
        'PASSWORD': os.getenv('MASTER_DB_PASSWORD', ''),
        'HOST': os.getenv('MASTER_DB_HOST', 'localhost'),
        'PORT': os.getenv('MASTER_DB_PORT', '3306'),
        'OPTIONS': {
            'charset': 'utf8mb4',
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
        },
        'CONN_MAX_AGE': 60,
    },
    'slave': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': os.getenv('SLAVE_DB_NAME', 'xxm_fans_home'),
        'USER': os.getenv('SLAVE_DB_USER', 'xxm_slave_user'),
        'PASSWORD': os.getenv('SLAVE_DB_PASSWORD', ''),
        'HOST': os.getenv('SLAVE_DB_HOST', 'localhost'),
        'PORT': os.getenv('SLAVE_DB_PORT', '3307'),
        'OPTIONS': {
            'charset': 'utf8mb4',
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
        },
        'CONN_MAX_AGE': 60,
    },
    'songlist_db': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': str(DATA_DIR / 'songlist.sqlite3'),
        'OPTIONS': {
            'timeout': 20,
        },
    },
}
```

### 5.4 创建数据库路由

创建 `xxm_fans_home/db_routers.py`：

```python
"""
数据库路由配置 - 实现读写分离
"""
import random
from django.conf import settings

class MasterSlaveRouter:
    """
    混合数据库路由
    - songlist 应用：使用 SQLite3（songlist_db），不进行读写分离
    - 其他应用：使用 MySQL 主从，实现读写分离
    """

    def db_for_read(self, model, **hints):
        """读操作路由"""
        # songlist 应用使用 SQLite3
        if model._meta.app_label == 'songlist':
            return 'songlist_db'
        # 其他应用使用从库
        return 'slave'

    def db_for_write(self, model, **hints):
        """写操作路由"""
        # songlist 应用使用 SQLite3
        if model._meta.app_label == 'songlist':
            return 'songlist_db'
        # 其他应用使用主库
        return 'default'

    def allow_relation(self, obj1, obj2, **hints):
        """允许跨数据库关系"""
        # songlist 应用内部的关系
        if obj1._meta.app_label == 'songlist' and obj2._meta.app_label == 'songlist':
            return True
        # MySQL 主从之间的关系
        db_set = {'default', 'slave'}
        if obj1._state.db in db_set and obj2._state.db in db_set:
            return True
        # 不允许跨数据库的关系（songlist 和其他应用）
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        """控制数据库迁移"""
        # songlist 应用只能迁移到 songlist_db（SQLite3）
        if app_label == 'songlist':
            return db == 'songlist_db'
        # 其他应用只能迁移到 MySQL（default 和 slave）
        return db in ('default', 'slave')


class MultiDbRouter:
    """
    多数据库路由（保留原有逻辑，用于兼容）
    """
    def db_for_read(self, model, **hints):
        if model._meta.app_label == 'songlist':
            return 'songlist_db'  # SQLite3
        return 'default'  # MySQL 主库

    def db_for_write(self, model, **hints):
        if model._meta.app_label == 'songlist':
            return 'songlist_db'  # SQLite3
        return 'default'  # MySQL 主库

    def allow_relation(self, obj1, obj2, **hints):
        db_set = {'default', 'slave', 'songlist_db'}
        if obj1._state.db in db_set and obj2._state.db in db_set:
            return True
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        if app_label == 'songlist':
            return db == 'songlist_db'  # SQLite3
        return db in ('default', 'slave')  # MySQL
```

### 5.5 修改数据库路由配置

在 `settings.py` 中：

```python
# Database routers - 使用读写分离路由
DATABASE_ROUTERS = ['xxm_fans_home.db_routers.MasterSlaveRouter']
```

---

## 6. 数据迁移步骤

### 6.1 创建数据库和用户

在主数据库上执行：

```sql
-- 创建主数据库（MySQL）
CREATE DATABASE xxm_fans_home CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- 创建主库用户（用于写操作）
CREATE USER 'xxm_master_user'@'%' IDENTIFIED BY 'your_master_password';
GRANT ALL PRIVILEGES ON xxm_fans_home.* TO 'xxm_master_user'@'%';
FLUSH PRIVILEGES;

-- 创建从库用户（用于读操作）
CREATE USER 'xxm_slave_user'@'%' IDENTIFIED BY 'your_slave_password';
GRANT SELECT ON xxm_fans_home.* TO 'xxm_slave_user'@'%';
FLUSH PRIVILEGES;

-- 注意：歌单数据库（songlist_db）继续使用 SQLite3，无需在 MySQL 中创建
```

### 6.2 导出 SQLite 数据

```bash
cd /home/yifeianyi/Desktop/xxm_fans_home

# 导出主数据库数据（用于迁移到 MySQL）
sqlite3 data/db.sqlite3 <<EOF
.output /tmp/xxm_fans_home.sql
.dump
.quit
EOF

# 注意：歌单数据库（songlist.sqlite3）继续使用 SQLite3，无需导出
```

### 6.3 转换并导入到 MySQL

**注意**: SQLite 的 `.dump` 命令生成的 SQL 语法与 MySQL 不完全兼容，需要使用工具转换。

使用 `sqlite3-to-mysql` 工具：

```bash
pip install sqlite3-to-mysql

# 转换主数据库（只迁移主数据库到 MySQL）
sqlite3mysql \
  --sqlite-file data/db.sqlite3 \
  --mysql-user xxm_master_user \
  --mysql-password your_master_password \
  --mysql-host localhost \
  --mysql-port 3306 \
  --mysql-database xxm_fans_home

# 注意：歌单数据库继续使用 SQLite3，无需转换
```

或者使用 Django 的数据导出/导入工具：

```bash
cd /home/yifeianyi/Desktop/xxm_fans_home/repo/xxm_fans_backend

# 从 SQLite 导出主数据库数据
python manage.py dumpdata --database=default > /tmp/xxm_fans_home_data.json

# 导入到 MySQL
python manage.py loaddata /tmp/xxm_fans_home_data.json --database=default

# 注意：歌单数据库继续使用 SQLite3，无需迁移
```

### 6.4 运行数据库迁移

```bash
cd /home/yifeianyi/Desktop/xxm_fans_home/repo/xxm_fans_backend

# 运行主数据库迁移（MySQL）
python manage.py migrate --database=default

# 运行歌单数据库迁移（SQLite3，保持不变）
python manage.py migrate --database=songlist_db

# 创建超级用户
python manage.py createsuperuser
```

---

## 7. 验证步骤

### 7.1 测试读写分离

```python
# 在 Django shell 中测试
python manage.py shell

from song_management.models import Song
from django.db import connections

# 测试写操作（应该使用主库）
song = Song.objects.create(
    song_name='测试歌曲',
    singer='测试歌手'
)
print(f"创建歌曲: {song.id}")

# 测试读操作（应该使用从库）
songs = Song.objects.all()
print(f"查询到 {songs.count()} 首歌曲")

# 检查数据库连接
print("主库连接:", connections['default'].ensure_connection())
print("从库连接:", connections['slave'].ensure_connection())
```

### 7.2 测试主从同步

在主数据库上执行：

```sql
USE xxm_fans_home;
INSERT INTO song_management_song (song_name, singer) VALUES ('同步测试', '测试歌手');
SELECT * FROM song_management_song ORDER BY id DESC LIMIT 1;
```

在从数据库上执行：

```sql
USE xxm_fans_home;
SELECT * FROM song_management_song ORDER BY id DESC LIMIT 1;
```

检查数据是否同步。

### 7.3 检查复制状态

在从数据库上执行：

```sql
SHOW SLAVE STATUS\G
```

检查关键指标：
- `Slave_IO_Running`: Yes
- `Slave_SQL_Running`: Yes
- `Seconds_Behind_Master`: 0 或很小的值

### 7.4 性能测试

```bash
# 使用 Locust 进行性能测试
cd /home/yifeianyi/Desktop/xxm_fans_home/repo/xxm_fans_backend/test
./run_performance_test.sh
```

对比迁移前后的性能指标。

---

## 8. 监控和维护

### 8.1 主从复制监控

创建监控脚本 `scripts/check_mysql_replication.sh`：

```bash
#!/bin/bash

# 检查主从复制状态
mysql -h localhost -P 3307 -u xxm_slave_user -p${SLAVE_DB_PASSWORD} -e "SHOW SLAVE STATUS\G" | grep -E "Slave_IO_Running|Slave_SQL_Running|Seconds_Behind_Master"

# 如果复制失败，发送告警
if [ $? -ne 0 ]; then
    echo "主从复制异常！"
    # 发送邮件或其他告警
fi
```

### 8.2 定期备份

创建备份脚本 `scripts/backup_databases.sh`：

```bash
#!/bin/bash

BACKUP_DIR="/home/yifeianyi/Desktop/xxm_fans_home/data/backups"
DATE=$(date +%Y%m%d_%H%M%S)

# 备份主数据库（MySQL）
mysqldump -h localhost -P 3306 -u xxm_master_user -p${MASTER_DB_PASSWORD} \
  xxm_fans_home > ${BACKUP_DIR}/xxm_fans_home_${DATE}.sql

# 备份歌单数据库（SQLite3）
cp /home/yifeianyi/Desktop/xxm_fans_home/data/songlist.sqlite3 \
  ${BACKUP_DIR}/songlist_db_${DATE}.sqlite3

# 压缩 MySQL 备份
gzip ${BACKUP_DIR}/xxm_fans_home_${DATE}.sql
gzip ${BACKUP_DIR}/songlist_db_${DATE}.sqlite3

# 删除7天前的备份
find ${BACKUP_DIR} -name "*.sql.gz" -mtime +7 -delete
find ${BACKUP_DIR} -name "*.sqlite3.gz" -mtime +7 -delete
```

### 8.3 慢查询日志

在 MySQL 配置中启用慢查询日志：

```ini
[mysqld]
# 慢查询日志
slow_query_log = 1
slow_query_log_file = /var/log/mysql/slow-query.log
long_query_time = 2
```

---

## 9. 回滚方案

如果迁移过程中出现问题，可以回滚到 SQLite：

```bash
cd /home/yifeianyi/Desktop/xxm_fans_home/repo/xxm_fans_backend

# 1. 备份当前 SQLite 数据库
cp ../../data/db.sqlite3 ../../data/db.sqlite3.backup
cp ../../data/songlist.sqlite3 ../../data/songlist.sqlite3.backup

# 2. 恢复 settings.py 中的 SQLite 配置
# 3. 恢复 requirements.txt（移除 mysqlclient）
# 4. 重新安装依赖
pip install -r requirements.txt

# 5. 恢复数据库路由
# 修改 settings.py 中的 DATABASE_ROUTERS
```

---

## 10. 注意事项

### 10.1 字符编码
- MySQL 使用 `utf8mb4` 字符集，支持完整的 Unicode（包括 emoji）
- SQLite 默认使用 UTF-8，迁移时需要注意字符集转换

### 10.2 数据类型差异
- SQLite 使用动态类型，MySQL 使用静态类型
- 迁移后需要检查字段类型是否正确
- 特别是 `TEXT`、`BLOB`、`DATETIME` 等字段

### 10.3 自增主键
- SQLite 的自增主键在迁移后可能需要重置
- 使用 `ALTER TABLE table_name AUTO_INCREMENT = max_id;` 重置

### 10.4 事务隔离级别
- MySQL 默认使用 `REPEATABLE READ` 隔离级别
- 可以根据需要调整：`SET TRANSACTION ISOLATION LEVEL READ COMMITTED;`

### 10.5 连接池配置
- 使用 `CONN_MAX_AGE` 配置连接池
- 避免频繁创建和销毁连接
- 根据并发量调整连接池大小

### 10.6 读写分离注意事项
- 从库可能有延迟（通常毫秒级）
- 对于需要实时数据的操作，强制使用主库
- 使用 `using('default')` 强制使用主库

```python
# 强制使用主库读取
song = Song.objects.using('default').get(id=1)
```

---

## 11. 性能优化建议

### 11.1 MySQL 配置优化

```ini
[mysqld]
# InnoDB 缓冲池大小（建议为物理内存的 50-70%）
innodb_buffer_pool_size = 2G

# InnoDB 日志文件大小
innodb_log_file_size = 512M

# InnoDB 刷盘策略
innodb_flush_log_at_trx_commit = 1
sync_binlog = 1

# 连接数
max_connections = 500

# 查询缓存（MySQL 8.0 已移除）
# query_cache_type = 1
# query_cache_size = 64M

# 临时表大小
tmp_table_size = 64M
max_heap_table_size = 64M
```

### 11.2 索引优化

```sql
-- 查看慢查询
SELECT * FROM mysql.slow_log ORDER BY start_time DESC LIMIT 10;

-- 分析查询
EXPLAIN SELECT * FROM song_management_song WHERE song_name LIKE '%测试%';

-- 添加索引
CREATE INDEX idx_song_name ON song_management_song(song_name);
CREATE INDEX idx_singer ON song_management_song(singer);
CREATE INDEX idx_perform_date ON song_management_songrecord(perform_date);
```

### 11.3 Django 查询优化

```python
# 使用 select_related 减少查询次数
songs = Song.objects.select_related('style').all()

# 使用 prefetch_related 优化多对多关系
songs = Song.objects.prefetch_related('tags').all()

# 使用 only() 只加载需要的字段
songs = Song.objects.only('id', 'song_name', 'singer').all()

# 使用 defer() 延迟加载不需要的字段
songs = Song.objects.defer('cover_url', 'notes').all()
```

---

## 12. 迁移时间表

| 阶段 | 任务 | 预计时间 | 负责人 |
|------|------|----------|--------|
| 准备阶段 | 安装 MySQL 和依赖 | 30分钟 | - |
| 配置阶段 | 配置主从数据库 | 1小时 | - |
| 代码修改 | 修改 Django 配置（混合架构） | 20分钟 | - |
| 数据迁移 | 导出和导入主数据库数据 | 30分钟 | - |
| 测试阶段 | 功能测试和性能测试 | 1.5小时 | - |
| 部署阶段 | 生产环境部署 | 1小时 | - |
| 监控阶段 | 监控和优化 | 持续 | - |

**总计**: 约 4.5 小时（相比全迁移节省 1.5 小时）

**说明**:
- 歌单数据库继续使用 SQLite3，无需迁移
- 只迁移主数据库到 MySQL 并实现读写分离
- 减少了数据迁移和测试的工作量

---

## 13. 总结

### 13.1 迁移优势
- ✅ **核心业务数据库（主库）**: 实现 MySQL 读写分离，提升数据库性能
- ✅ **支持主从复制**: 提高数据可靠性和可用性
- ✅ **更好的并发处理能力**: 应对每小时 200-300 条数据写入
- ✅ **歌单数据库保持轻量**: 继续使用 SQLite3，无需额外配置
- ✅ **混合架构优势**: 核心业务高性能 + 歌单系统简单易部署
- ✅ **更易于扩展和维护**: MySQL 支持水平扩展

### 13.2 风险和挑战
- ⚠️ 迁移过程复杂，需要仔细测试
- ⚠️ 需要额外的 MySQL 服务器资源（仅用于主库）
- ⚠️ 需要运维人员具备 MySQL 管理经验
- ⚠️ 从库可能有延迟（毫秒级），影响实时性
- ⚠️ 混合数据库架构增加了系统复杂度

### 13.3 建议
1. **先在测试环境完成迁移**，验证所有功能正常
2. **制定详细的回滚方案**，确保可以快速恢复
3. **只迁移主数据库**，歌单数据库保持 SQLite3 不变
4. **建立监控体系**，及时发现和处理 MySQL 主从复制问题
5. **定期备份**：MySQL 主库 + SQLite3 歌单库
6. **评估是否真的需要读写分离**：如果写入量不大，可以考虑单 MySQL 库

---

## 附录 A：常用 MySQL 命令

```sql
-- 查看数据库列表
SHOW DATABASES;

-- 查看表列表
SHOW TABLES;

-- 查看表结构
DESCRIBE table_name;

-- 查看索引
SHOW INDEX FROM table_name;

-- 查看进程
SHOW PROCESSLIST;

-- 杀死进程
KILL process_id;

-- 查看主库状态
SHOW MASTER STATUS;

-- 查看从库状态
SHOW SLAVE STATUS\G

-- 停止从库复制
STOP SLAVE;

-- 启动从库复制
START SLAVE;

-- 重置从库
RESET SLAVE ALL;

-- 查看慢查询
SHOW VARIABLES LIKE 'slow_query%';
```

---

## 附录 B：故障排查

### B.1 主从复制失败

**症状**: `Slave_IO_Running` 或 `Slave_SQL_Running` 为 `No`

**解决方法**:

```sql
-- 查看错误信息
SHOW SLAVE STATUS\G

-- 跳过错误（谨慎使用）
SET GLOBAL SQL_SLAVE_SKIP_COUNTER = 1;
START SLAVE;

-- 重新配置主从
STOP SLAVE;
RESET SLAVE ALL;
CHANGE MASTER TO ...;
START SLAVE;
```

### B.2 连接超时

**症状**: `Can't connect to MySQL server`

**解决方法**:

```sql
-- 检查 MySQL 是否运行
sudo systemctl status mysql

-- 检查防火墙
sudo ufw allow 3306

-- 检查最大连接数
SHOW VARIABLES LIKE 'max_connections';
SET GLOBAL max_connections = 500;
```

### B.3 字符编码问题

**症状**: 中文显示乱码

**解决方法**:

```sql
-- 检查字符集
SHOW VARIABLES LIKE 'character%';

-- 修改表字符集
ALTER TABLE table_name CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

---

**文档版本**: 1.0
**创建日期**: 2026-01-20
**最后更新**: 2026-01-20
**作者**: XXM Fans Home Team