# Gunicorn 配置文件
# XXM Fans Home 生产环境

# 绑定地址
bind = "0.0.0.0:8000"

# 工作进程数 (建议设置为 (2 * CPU核心数) + 1)
workers = 4

# 工作进程类型
worker_class = "sync"

# 每个工作进程的线程数
threads = 2

# 工作进程最大请求数（重启工作进程以防止内存泄漏）
max_requests = 1000
max_requests_jitter = 100

# 超时设置
timeout = 120
keepalive = 5

# 日志配置
accesslog = "/tmp/gunicorn_access.log"
errorlog = "/tmp/gunicorn_error.log"
loglevel = "info"

# 进程名称
proc_name = "xxm_fans_home_gunicorn"

# 用户和组（可选，生产环境建议使用非root用户）
# user = "www-data"
# group = "www-data"

# 临时目录
tmp_upload_dir = None

# 预加载应用（启动时加载应用代码，减少内存占用）
preload_app = True

# 优雅关闭超时
graceful_timeout = 30

# 工作进程启动超时
worker_timeout = 30

# 限制并发连接数
worker_connections = 1000

# 最大请求数后重启
preload_app = True

# 环境变量
raw_env = [
    "DJANGO_SETTINGS_MODULE=xxm_fans_home.settings",
]

# 启动钩子
def on_starting(server):
    """启动时执行的钩子"""
    server.log.info("XXM Fans Home Gunicorn starting...")

def on_reload(server):
    """重载时执行的钩子"""
    server.log.info("XXM Fans Home Gunicorn reloading...")

def when_ready(server):
    """就绪时执行的钩子"""
    server.log.info("XXM Fans Home Gunicorn is ready. Spawning workers")

def pre_fork(server, worker):
    """fork 工作进程前执行的钩子"""
    pass

def post_fork(server, worker):
    """fork 工作进程后执行的钩子"""
    server.log.info("Worker spawned (pid: %s)", worker.pid)

def pre_exec(server):
    """fork 后但在 exec 前执行的钩子"""
    server.log.info("Forked child, re-executing.")

def worker_int(worker):
    """工作进程收到 SIGINT 信号时执行的钩子"""
    worker.log.info("Worker received INT or QUIT signal")

def pre_request(worker, req):
    """处理请求前执行的钩子"""
    worker.log.debug("%s %s", req.method, req.path)

def post_request(worker, req, environ, resp):
    """处理请求后执行的钩子"""
    pass

def child_exit(server, worker):
    """工作进程退出时执行的钩子"""
    server.log.info("Worker (pid: %s) exited", worker.pid)

def worker_abort(worker):
    """工作进程异常中止时执行的钩子"""
    worker.log.info("Worker received SIGABRT signal")

def nworkers_changed(server, new_value, old_value):
    """工作进程数量变化时执行的钩子"""
    server.log.info("Worker count changed from %s to %s", old_value, new_value)