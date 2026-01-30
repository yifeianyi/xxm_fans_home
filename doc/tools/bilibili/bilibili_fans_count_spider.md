# B站粉丝数爬虫系统

## 概述

本系统用于定时获取B站账号（咻咻满和咻小满）的粉丝数，并将数据保存为JSON文件。

## 文件结构

```
spider/
└── get_bilibili_fans_count.py    # 爬虫脚本
scripts/
└── bilibili_fans_count_cron.sh   # 定时任务脚本
data/spider/fans_count/
└── year/month/
    └── b_fans_count_YYYY-MM-DD-HH.json  # 粉丝数据文件
logs/
└── bilibili_fans_count.json      # 执行日志
```

## 功能特性

- 自动获取咻咻满（UID: 37754047）和咻小满（UID: 480116537）的粉丝数
- 数据按年/月/小时分类保存
- JSON格式日志记录每次执行结果
- 支持成功/失败状态追踪
- 简洁的日志摘要，只保留关键信息

## 使用方法

### 手动运行

1. **运行爬虫脚本**
```bash
cd spider
python3 get_bilibili_fans_count.py
```

2. **运行定时任务脚本**
```bash
cd scripts
./bilibili_fans_count_cron.sh
```

### 设置定时任务

使用crontab每小时自动运行：

```bash
crontab -e
```

添加以下行（请根据实际项目路径修改）：
```bash
0 * * * * /path/to/xxm_fans_home/scripts/bilibili_fans_count_cron.sh
```

## 数据格式

### 粉丝数据文件

保存位置：`data/spider/fans_count/年/月/b_fans_count_YYYY-MM-DD-HH.json`

```json
{
  "update_time": "2026-01-16 13:18:53",
  "accounts": [
    {
      "uid": 37754047,
      "follower": 2737500,
      "status": "success",
      "timestamp": "2026-01-16 13:18:51",
      "name": "咻咻满"
    },
    {
      "uid": 480116537,
      "follower": 129146,
      "status": "success",
      "timestamp": "2026-01-16 13:18:52",
      "name": "咻小满"
    }
  ]
}
```

### 执行日志

保存位置：`logs/bilibili_fans_count.json`

```json
[
  {
    "start_time": "2026-01-16 13:18:51",
    "end_time": "2026-01-16 13:18:53",
    "exit_code": 0,
    "status": "success",
    "error_message": "",
    "summary": "✓ 咻咻满: 2,737,500 粉丝\n✓ 咻小满: 129,146 粉丝\n数据已保存到: data/spider/fans_count/2026/01/b_fans_count_2026-01-16-13.json"
  }
]
```

## 账号信息

| 账号名称 | UID | 说明 |
|---------|-----|------|
| 咻咻满 | 37754047 | 主账号 |
| 咻小满 | 480116537 | 小号 |

## 依赖要求

- Python 3.8+
- requests 库
- jq (JSON处理工具)

### 安装依赖

```bash
# Python依赖
pip install requests

# jq工具
sudo apt-get install jq
```

## 日志查看

```bash
# 查看执行日志
cat logs/bilibili_fans_count.json

# 查看最新的粉丝数据
ls -lt data/spider/fans_count/*/*/ | head -1
```

## 注意事项

1. 脚本会自动创建所需的目录结构
2. 每次执行都会追加日志，不会覆盖历史记录
3. 数据文件按小时命名，避免冲突
4. 如果API请求失败，会在日志中记录错误信息
5. 建议定期清理旧的日志和数据文件

## 故障排查

### 问题：日志文件未生成

检查：
1. 是否有执行权限：`chmod +x scripts/bilibili_fans_count_cron.sh`
2. 是否安装了jq：`which jq`
3. 查看脚本输出：`bash -x scripts/bilibili_fans_count_cron.sh`

### 问题：数据获取失败

检查：
1. 网络连接是否正常
2. B站API是否可访问
3. 查看详细错误信息：`cat logs/bilibili_fans_count.json | jq '.[-1]'`