# B站投稿数据爬虫 - Cron定时任务设置指南

本文档介绍如何使用 cron 定时任务来自动运行 B站投稿数据爬虫。

---

## 一、Cron 简介

Cron 是 Linux 系统下的定时任务工具，可以按照设定的时间周期自动执行命令或脚本。

### Cron 语法

```
* * * * * command
│ │ │ │ │
│ │ │ │ └─── 星期几 (0-7, 0或7表示星期日)
│ │ │ └───── 月份 (1-12)
│ │ └─────── 日期 (1-31)
│ └───────── 小时 (0-23)
└─────────── 分钟 (0-59)
```

---

## 二、设置步骤

### 步骤 1: 确保脚本有执行权限

```bash
chmod +x /home/yifeianyi/Desktop/xxm_fans_home/scripts/bilibili_views_cron.sh
```

### 步骤 2: 编辑 crontab

```bash
crontab -e
```

首次运行时会提示选择编辑器，推荐选择 `nano`（选项 1）或 `vim`。

### 步骤 3: 添加定时任务

在文件末尾添加以下内容：

```bash
# B站投稿数据爬虫 - 每小时运行一次
0 * * * * /home/yifeianyi/Desktop/xxm_fans_home/scripts/bilibili_views_cron.sh >> /home/yifeianyi/Desktop/xxm_fans_home/logs/spider/cron_execution.log 2>&1
```

### 步骤 4: 保存并退出

- **如果使用 nano**: 按 `Ctrl+O` 保存，然后按 `Ctrl+X` 退出
- **如果使用 vim**: 按 `Esc`，输入 `:wq`，按回车保存并退出

### 步骤 5: 查看定时任务

```bash
crontab -l
```

---

## 三、常用时间表达式

| 表达式 | 说明 | 使用场景 |
|--------|------|----------|
| `0 * * * *` | 每小时的第0分钟执行 | **推荐**，每小时爬取一次 |
| `*/30 * * * *` | 每30分钟执行一次 | 高频监控 |
| `0 */2 * * *` | 每2小时执行一次 | 低频监控 |
| `0 0 * * *` | 每天凌晨0点执行 | 每日汇总 |
| `0 9,18 * * *` | 每天上午9点和下午6点执行 | 早晚两次 |

---

## 四、完整配置示例

### 基础配置（推荐）

```bash
# 每小时运行一次B站投稿数据爬虫
0 * * * * /home/yifeianyi/Desktop/xxm_fans_home/scripts/bilibili_views_cron.sh >> /home/yifeianyi/Desktop/xxm_fans_home/logs/spider/cron_execution.log 2>&1
```

### 多任务配置

```bash
# B站投稿数据爬虫 - 每小时运行
0 * * * * /home/yifeianyi/Desktop/xxm_fans_home/scripts/bilibili_views_cron.sh >> /home/yifeianyi/Desktop/xxm_fans_home/logs/spider/cron_execution.log 2>&1

# B站粉丝数爬虫 - 每小时运行（与投稿爬虫错开5分钟）
5 * * * * /home/yifeianyi/Desktop/xxm_fans_home/scripts/bilibili_fans_count_cron.sh >> /home/yifeianyi/Desktop/xxm_fans_home/logs/cron_fans.log 2>&1
```

---

## 五、查看与管理

### 查看定时任务列表

```bash
crontab -l
```

### 查看 Cron 执行日志

```bash
# 查看系统 cron 日志
grep CRON /var/log/syslog | tail -20

# 实时查看 cron 日志
tail -f /var/log/syslog | grep CRON

# 查看爬虫执行日志
cat /home/yifeianyi/Desktop/xxm_fans_home/logs/bilibili_views_crawler.json

# 查看实时爬虫日志
tail -f /home/yifeianyi/Desktop/xxm_fans_home/logs/spider/views/$(date +%Y)/$(date +%m)/crawl_views_$(date +%Y%m%d).log
```

### 检查 Cron 服务状态

```bash
# 查看 cron 服务状态
sudo systemctl status cron

# 重启 cron 服务
sudo systemctl restart cron
```

---

## 六、手动测试

在设置定时任务前，建议先手动测试脚本：

```bash
# 1. 直接运行脚本
cd /home/yifeianyi/Desktop/xxm_fans_home
./scripts/bilibili_views_cron.sh

# 2. 模拟 cron 环境运行
bash -c '/home/yifeianyi/Desktop/xxm_fans_home/scripts/bilibili_views_cron.sh >> /home/yifeianyi/Desktop/xxm_fans_home/logs/spider/test_cron.log 2>&1'

# 3. 查看测试结果
cat /home/yifeianyi/Desktop/xxm_fans_home/logs/spider/test_cron.log
```

---

## 七、调试技巧

### 测试 Cron 任务

设置一个短时间间隔进行测试：

```bash
# 编辑 crontab
crontab -e

# 添加每分钟执行的测试任务（仅用于测试）
* * * * * /home/yifeianyi/Desktop/xxm_fans_home/scripts/bilibili_views_cron.sh >> /home/yifeianyi/Desktop/xxm_fans_home/logs/spider/cron_test.log 2>&1
```

等待几分钟，检查日志是否正常生成：

```bash
tail -f /home/yifeianyi/Desktop/xxm_fans_home/logs/spider/cron_test.log
```

测试完成后，记得改回正常的时间间隔：

```bash
crontab -e
# 将 * * * * * 改为 0 * * * *
```

---

## 八、常见问题

### 问题 1: 任务没有执行

检查步骤：

```bash
# 1. 检查 cron 服务是否运行
sudo systemctl status cron

# 2. 检查脚本是否有执行权限
ls -la /home/yifeianyi/Desktop/xxm_fans_home/scripts/bilibili_views_cron.sh

# 3. 检查路径是否正确（必须使用绝对路径）
ls /home/yifeianyi/Desktop/xxm_fans_home/scripts/bilibili_views_cron.sh

# 4. 查看系统日志
grep CRON /var/log/syslog | tail -20
```

### 问题 2: 脚本执行失败

检查步骤：

```bash
# 1. 手动运行脚本看是否有错误
/home/yifeianyi/Desktop/xxm_fans_home/scripts/bilibili_views_cron.sh

# 2. 查看详细错误输出
bash -x /home/yifeianyi/Desktop/xxm_fans_home/scripts/bilibili_views_cron.sh

# 3. 检查依赖
which python3
which jq
python3 --version
```

### 问题 3: 环境变量问题

如果脚本依赖特定的环境变量，在 crontab 中设置：

```bash
# 编辑 crontab
crontab -e

# 添加环境变量（在任务之前）
SHELL=/bin/bash
PATH=/usr/local/bin:/usr/bin:/bin
HOME=/home/yifeianyi

# 然后添加任务
0 * * * * /home/yifeianyi/Desktop/xxm_fans_home/scripts/bilibili_views_cron.sh >> /home/yifeianyi/Desktop/xxm_fans_home/logs/spider/cron_execution.log 2>&1
```

---

## 九、删除定时任务

```bash
# 编辑 crontab
crontab -e

# 删除对应的行，保存退出

# 或者清空所有定时任务（谨慎使用）
crontab -r
```

---

## 十、日志轮转（可选）

为了防止日志文件过大，可以配置 logrotate：

```bash
# 创建 logrotate 配置
sudo tee /etc/logrotate.d/bilibili-views-cron << 'EOF'
/home/yifeianyi/Desktop/xxm_fans_home/logs/spider/cron_execution.log {
    daily
    rotate 30
    compress
    delaycompress
    missingok
    notifempty
    create 0644 yifeianyi yifeianyi
}
EOF

# 测试配置
sudo logrotate -d /etc/logrotate.d/bilibili-views-cron
```

---

## 十一、快速参考

```bash
# 编辑定时任务
crontab -e

# 查看定时任务
crontab -l

# 删除所有定时任务
crontab -r

# 查看 cron 日志
grep CRON /var/log/syslog | tail -20

# 查看爬虫日志
tail -f /home/yifeianyi/Desktop/xxm_fans_home/logs/spider/views/$(date +%Y)/$(date +%m)/crawl_views_$(date +%Y%m%d).log
```

---

**文档版本**: v1.0  
**创建时间**: 2026-02-06  
**适用项目**: B站投稿数据爬虫
