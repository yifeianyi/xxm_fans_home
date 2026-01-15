# Gunicorn 配置说明

## 配置文件

- `gunicorn_config.py` - Gunicorn 主配置文件

## 使用方法

### 直接使用配置文件启动

```bash
cd /home/yifeianyi/Desktop/xxm_fans_home/repo/xxm_fans_backend
gunicorn -c /home/yifeianyi/Desktop/xxm_fans_home/infra/gunicorn/gunicorn_config.py xxm_fans_home.wsgi:application
```

### 使用启动脚本

```bash
cd /home/yifeianyi/Desktop/xxm_fans_home/scripts
./build_start_services.sh
```

## 配置说明

### 基本配置

- `bind = "0.0.0.0:8000"` - 绑定地址和端口
- `workers = 4` - 工作进程数
- `worker_class = "sync"` - 工作进程类型
- `threads = 2` - 每个工作进程的线程数

### 性能配置

- `max_requests = 1000` - 每个工作进程处理的最大请求数
- `max_requests_jitter = 100` - 最大请求数的随机抖动
- `timeout = 120` - 请求超时时间（秒）
- `keepalive = 5` - Keep-Alive 超时时间（秒）

### 日志配置

- `accesslog = "/tmp/gunicorn_access.log"` - 访问日志路径
- `errorlog = "/tmp/gunicorn_error.log"` - 错误日志路径
- `loglevel = "info"` - 日志级别

### 进程管理

- `proc_name = "xxm_fans_home_gunicorn"` - 进程名称
- `preload_app = True` - 预加载应用
- `graceful_timeout = 30` - 优雅关闭超时
- `worker_timeout = 30` - 工作进程启动超时

## 调优建议

### CPU 核心数较少（1-2核）

```python
workers = 2
threads = 4
```

### CPU 核心数适中（4-8核）

```python
workers = 4
threads = 2
```

### CPU 核心数较多（8+核）

```python
workers = 8
threads = 2
```

### 内存受限环境

```python
workers = 2
threads = 2
max_requests = 500
```

## 监控

### 查看进程状态

```bash
ps aux | grep gunicorn
```

### 查看日志

```bash
# 访问日志
tail -f /tmp/gunicorn_access.log

# 错误日志
tail -f /tmp/gunicorn_error.log
```

### 查看进程资源使用

```bash
top -p $(pgrep -d',' gunicorn)
```

## 故障排查

### 端口被占用

```bash
# 查找占用端口的进程
lsof -i :8000

# 杀死进程
kill -9 <PID>
```

### 内存泄漏

```bash
# 查看进程内存使用
ps aux | grep gunicorn | awk '{print $6}'

# 如果内存持续增长，降低 max_requests
max_requests = 500
```

### 响应慢

```bash
# 检查工作进程数
ps aux | grep gunicorn | wc -l

# 增加工作进程数
workers = 8
```

## 生产环境建议

1. 使用 systemd 管理 Gunicorn 进程
2. 配置日志轮转
3. 使用 Nginx 作为反向代理
4. 启用 HTTPS
5. 配置监控和告警
6. 定期备份数据库