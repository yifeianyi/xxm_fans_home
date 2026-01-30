# Cron定时任务设置指南

## 概述

本文档介绍如何使用cron定时任务来自动运行B站粉丝数爬虫脚本。

## Cron简介

Cron是Linux系统下的定时任务工具，可以按照设定的时间周期自动执行命令或脚本。

## 基本语法

```bash
* * * * * command
│ │ │ │ │
│ │ │ │ └─── 星期几 (0-7, 0或7表示星期日)
│ │ │ └───── 月份 (1-12)
│ │ └─────── 日期 (1-31)
│ └───────── 小时 (0-23)
└─────────── 分钟 (0-59)
```

## 设置步骤

### 1. 编辑crontab

```bash
crontab -e
```

首次运行时会提示选择编辑器，推荐选择 `nano` 或 `vim`。

### 2. 添加定时任务

在文件末尾添加以下内容：

```bash
# 每小时运行一次B站粉丝数爬虫
0 * * * * /home/yifeianyi/Desktop/xxm_fans_home/scripts/bilibili_fans_count_cron.sh
```

### 3. 保存并退出

- 如果使用 `nano`: 按 `Ctrl+O` 保存，然后按 `Ctrl+X` 退出
- 如果使用 `vim`: 按 `Esc`，输入 `:wq`，按回车保存并退出

### 4. 查看定时任务

```bash
crontab -l
```

## 常用时间表达式

| 表达式 | 说明 |
|--------|------|
| `0 * * * *` | 每小时的第0分钟执行 |
| `*/30 * * * *` | 每30分钟执行一次 |
| `0 0 * * *` | 每天凌晨0点执行 |
| `0 */6 * * *` | 每6小时执行一次 |
| `0 9,18 * * *` | 每天上午9点和下午6点执行 |
| `0 0 * * 0` | 每周日凌晨0点执行 |
| `0 0 1 * *` | 每月1号凌晨0点执行 |

## 完整示例

```bash
# B站粉丝数爬虫定时任务

# 每小时运行一次
0 * * * * /home/yifeianyi/Desktop/xxm_fans_home/scripts/bilibili_fans_count_cron.sh

# 每30分钟运行一次
*/30 * * * * /home/yifeianyi/Desktop/xxm_fans_home/scripts/bilibili_fans_count_cron.sh

# 每天上午9点和下午6点运行
0 9,18 * * * /home/yifeianyi/Desktop/xxm_fans_home/scripts/bilibili_fans_count_cron.sh
```

## 注意事项

1. **使用绝对路径**
   - 定时任务中的脚本路径必须使用绝对路径
   - 示例：`/home/yifeianyi/Desktop/xxm_fans_home/scripts/bilibili_fans_count_cron.sh`

2. **脚本执行权限**
   - 确保脚本有执行权限
   ```bash
   chmod +x /home/yifeianyi/Desktop/xxm_fans_home/scripts/bilibili_fans_count_cron.sh
   ```

3. **环境变量**
   - Cron任务运行时的环境变量与用户登录时不同
   - 如果脚本依赖环境变量，请在脚本中显式设置

4. **日志输出**
   - 建议将输出重定向到日志文件
   ```bash
   0 * * * * /path/to/script.sh >> /path/to/logfile.log 2>&1
   ```

## 查看Cron日志

### 方法1：查看系统日志

```bash
# 查看cron日志
grep CRON /var/log/syslog

# 实时查看cron日志
tail -f /var/log/syslog | grep CRON
```

### 方法2：查看脚本日志

```bash
# 查看B站粉丝数爬虫的执行日志
cat /home/yifeianyi/Desktop/xxm_fans_home/logs/bilibili_fans_count.json
```

## 调试技巧

### 1. 手动测试脚本

在设置定时任务前，先手动运行脚本确保正常工作：

```bash
cd /home/yifeianyi/Desktop/xxm_fans_home/scripts
./bilibili_fans_count_cron.sh
```

### 2. 测试Cron任务

设置一个短时间间隔测试是否正常执行：

```bash
# 每分钟执行一次（仅用于测试）
* * * * * /home/yifeianyi/Desktop/xxm_fans_home/scripts/bilibili_fans_count_cron.sh
```

测试完成后记得改回正常的时间间隔。

### 3. 检查Cron服务状态

```bash
# 查看cron服务状态
sudo systemctl status cron

# 重启cron服务
sudo systemctl restart cron
```

## 删除定时任务

```bash
# 编辑crontab
crontab -e

# 删除对应的行，保存退出

# 或者清空所有定时任务
crontab -r
```

## 常见问题

### 问题1：任务没有执行

检查：
1. cron服务是否运行：`sudo systemctl status cron`
2. 脚本是否有执行权限：`ls -l scripts/bilibili_fans_count_cron.sh`
3. 路径是否正确：确保使用绝对路径
4. 查看系统日志：`grep CRON /var/log/syslog`

### 问题2：脚本执行失败

检查：
1. 手动运行脚本看是否有错误
2. 查看脚本日志：`cat logs/bilibili_fans_count.json`
3. 检查依赖是否安装：`which jq`, `python3 --version`

### 问题3：环境变量问题

在脚本开头添加环境变量：

```bash
#!/bin/bash
# 设置PATH环境变量
export PATH=/usr/local/bin:/usr/bin:/bin

# 其他脚本内容...
```

## 推荐配置

对于B站粉丝数爬虫，推荐使用以下配置：

```bash
# 每小时运行一次
0 * * * * /home/yifeianyi/Desktop/xxm_fans_home/scripts/bilibili_fans_count_cron.sh
```

这样可以每小时获取一次粉丝数据，既不会过于频繁，也能及时跟踪粉丝数变化。

## 参考资料

- Cron官方文档：`man cron`
- Crontab帮助：`man crontab`
- 系统日志位置：`/var/log/syslog` (Debian/Ubuntu) 或 `/var/log/cron` (CentOS/RHEL)