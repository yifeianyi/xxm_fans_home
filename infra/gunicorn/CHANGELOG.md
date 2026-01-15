# Gunicorn 配置优化记录

## 优化内容

### 1. 创建配置文件
- **文件**: `infra/gunicorn/gunicorn_config.py`
- **功能**: 集中管理 Gunicorn 所有配置参数
- **优势**:
  - 配置统一管理，便于维护
  - 支持钩子函数，增强监控能力
  - 参数调优更方便

### 2. 配置功能
- **进程管理**: 4个工作进程，每个进程2个线程
- **性能优化**: 预加载应用，减少内存占用
- **日志管理**: 分离访问日志和错误日志
- **监控钩子**: 启动、重载、工作进程生命周期钩子
- **资源控制**: 最大请求数限制，防止内存泄漏

### 3. 启动脚本优化
- **文件**: `scripts/build_start_services.sh`
- **改动**: 使用配置文件启动 Gunicorn
- **命令**:
  ```bash
  gunicorn -c /home/yifeianyi/Desktop/xxm_fans_home/infra/gunicorn/gunicorn_config.py xxm_fans_home.wsgi:application
  ```

### 4. 停止脚本优化
- **文件**: `scripts/build_stop_services.sh`
- **改动**: 使用进程名称停止服务
- **进程名称**: `xxm_fans_home_gunicorn`

## 配置参数说明

### 基本配置
```python
bind = "0.0.0.0:8000"          # 绑定地址
workers = 4                     # 工作进程数
worker_class = "sync"           # 工作进程类型
threads = 2                     # 每个进程的线程数
```

### 性能配置
```python
max_requests = 1000             # 最大请求数
max_requests_jitter = 100       # 请求抖动
timeout = 120                   # 超时时间
keepalive = 5                   # Keep-Alive 超时
```

### 日志配置
```python
accesslog = "/tmp/gunicorn_access.log"  # 访问日志
errorlog = "/tmp/gunicorn_error.log"    # 错误日志
loglevel = "info"                        # 日志级别
```

### 进程管理
```python
proc_name = "xxm_fans_home_gunicorn"    # 进程名称
preload_app = True                       # 预加载应用
graceful_timeout = 30                    # 优雅关闭超时
worker_timeout = 30                      # 工作进程启动超时
```

## 使用方法

### 启动服务
```bash
cd /home/yifeianyi/Desktop/xxm_fans_home/scripts
./build_start_services.sh
```

### 停止服务
```bash
cd /home/yifeianyi/Desktop/xxm_fans_home/scripts
./build_stop_services.sh
```

### 查看日志
```bash
# 访问日志
tail -f /tmp/gunicorn_access.log

# 错误日志
tail -f /tmp/gunicorn_error.log
```

### 查看进程
```bash
ps aux | grep xxm_fans_home_gunicorn
```

## 测试结果

### 集成测试
- ✅ 前端页面: 200 OK
- ✅ 歌曲列表API: 200 OK
- ✅ 曲风列表API: 200 OK
- ✅ 标签列表API: 200 OK
- ✅ 推荐语API: 200 OK
- ✅ 粉丝二创合集API: 200 OK
- ✅ 默认封面图片: 200 OK
- ✅ 咻咻满头像: 200 OK

### 进程状态
- Gunicorn 主进程: 1个
- Gunicorn 工作进程: 4个
- Nginx 主进程: 1个
- Nginx 工作进程: 20个

## 优化效果

### 1. 配置管理
- ✅ 配置集中化，便于维护
- ✅ 参数调优更方便
- ✅ 支持版本控制

### 2. 监控能力
- ✅ 启动日志记录
- ✅ 工作进程生命周期监控
- ✅ 请求日志记录

### 3. 性能优化
- ✅ 预加载应用，减少内存占用
- ✅ 请求限制，防止内存泄漏
- ✅ 线程支持，提高并发能力

### 4. 运维便利
- ✅ 进程名称统一，便于管理
- ✅ 日志分离，便于排查问题
- ✅ 配置文件化，便于部署

## 后续优化建议

1. **性能调优**
   - 根据服务器配置调整 worker 数量
   - 监控内存使用情况
   - 优化超时时间

2. **监控增强**
   - 添加 Prometheus 监控
   - 配置告警规则
   - 集成日志分析工具

3. **高可用**
   - 配置多实例部署
   - 使用负载均衡
   - 实现健康检查

4. **安全加固**
   - 配置 HTTPS
   - 添加安全头
   - 限制访问频率

## 文件清单

```
infra/gunicorn/
├── gunicorn_config.py    # Gunicorn 配置文件
├── README.md             # 使用说明文档
└── CHANGELOG.md          # 优化记录（本文件）
```

## 日期

- **创建日期**: 2026-01-15
- **优化版本**: v1.0
- **测试状态**: ✅ 通过