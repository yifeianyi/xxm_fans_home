# Django SECRET_KEY 配置指南

本文档说明 Django `SECRET_KEY` 的作用、生成方法及安全配置规范。

---

## 1. SECRET_KEY 的作用

`SECRET_KEY` 是 Django 项目的**核心安全密钥**，用于以下安全功能：

| 用途 | 说明 |
|-----|------|
| **会话(Session)加密** | 保护用户 session 数据，防止篡改和伪造 |
| **密码重置令牌** | 生成和验证密码重置链接的加密签名 |
| **CSRF 保护** | 防止跨站请求伪造攻击的令牌生成 |
| **Cookie 签名** | 确保 cookie 数据未被篡改 |
| **消息框架** | 签名一次性消息（如操作成功提示） |

### 安全风险

⚠️ **如果密钥泄露，攻击者可以：**
- 伪造用户 session，冒充任意用户登录
- 破解密码重置令牌，劫持账户
- 绕过 CSRF 保护，执行恶意操作
- 篡改签名 cookie 中的数据

---

## 2. 生成安全的 SECRET_KEY

### 方法 A：Django 自带命令（推荐）

```bash
cd /home/yifeianyi/Desktop/xxm_fans_home/repo/xxm_fans_backend
source /home/yifeianyi/Desktop/venv/bin/activate

python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

输出示例：
```
django-insecure-#@&_7z=xt^z!q... (50+ 随机字符)
```

### 方法 B：Python secrets 模块

```bash
python -c "import secrets; print(secrets.token_urlsafe(50))"
```

### 方法 C：OpenSSL（命令行）

```bash
openssl rand -base64 50
```

---

## 3. 配置文件设置

### 3.1 环境变量配置

编辑 `/home/yifeianyi/Desktop/xxm_fans_home/env/backend.env`：

```bash
# Django配置 - 生产环境
DJANGO_DEBUG=False
DJANGO_SECRET_KEY=your-production-secret-key-here  # ← 替换为生成的密钥
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1,xxm8777.cn,www.xxm8777.cn,admin.xxm8777.cn
```

### 3.2 生产环境部署脚本

```bash
#!/bin/bash
# 在生产服务器上执行

PROJECT_ROOT="/home/yifeianyi/Desktop/xxm_fans_home"
ENV_FILE="$PROJECT_ROOT/env/backend.env"
PID_FILE="/tmp/xxm-fans-gunicorn.pid"

# 1. 生成新的密钥
cd "$PROJECT_ROOT/repo/xxm_fans_backend"
source /home/yifeianyi/Desktop/venv/bin/activate
NEW_KEY=$(python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())")

# 2. 备份原配置
cp "$ENV_FILE" "$ENV_FILE.bak.$(date +%Y%m%d_%H%M%S)"

# 3. 更新密钥
sed -i "s/DJANGO_SECRET_KEY=.*/DJANGO_SECRET_KEY=$NEW_KEY/" "$ENV_FILE"

# 4. 验证修改
echo "密钥已更新:"
grep "DJANGO_SECRET_KEY" "$ENV_FILE"

# 5. 重启 Gunicorn
if [ -f "$PID_FILE" ]; then
    kill -HUP $(cat "$PID_FILE")
    echo "服务已重启"
else
    echo "警告: 未找到 PID 文件，请手动重启服务"
fi
```

---

## 4. 安全规范

### 4.1 必须遵守的规则

| ❌ 禁止 | ✅ 正确做法 |
|--------|-----------|
| 使用默认/示例密钥 | 生成随机复杂的密钥 |
| 将密钥硬编码在代码中 | 使用环境变量存储 |
| 将密钥提交到 Git | 将 `.env` 加入 `.gitignore` |
| 不同环境使用相同密钥 | 生产/开发/测试环境各自独立 |
| 密钥长度小于 50 字符 | 至少 50+ 随机字符 |
| 使用可预测的密钥 | 使用密码学安全的随机生成器 |

### 4.2 环境隔离

```
开发环境          测试环境           生产环境
   │                │                │
   ▼                ▼                ▼
dev-secret-key   test-secret-key  prod-secret-key
(可简单)          (独立生成)        (强随机 + 严格保密)
```

---

## 5. 密钥泄露应急处理

如果发现密钥可能泄露，立即执行：

```bash
ssh -p 22 -i ~/.ssh/id_rsa_xxx yifeianyi@47.92.253.0

# 1. 生成并部署新密钥（见第3节）

# 2. 清空所有现有会话（强制所有用户重新登录）
cd /home/yifeianyi/Desktop/xxm_fans_home/repo/xxm_fans_backend
source /home/yifeianyi/Desktop/venv/bin/activate
python manage.py clearsessions

# 3. 重启服务
kill -HUP $(cat /tmp/xxm-fans-gunicorn.pid)

# 4. 检查日志是否有异常登录
sudo grep "login" /var/log/nginx/access.log | tail -50
```

---

## 6. 验证配置

### 6.1 检查当前密钥

```bash
# 在生产服务器上
cd /home/yifeianyi/Desktop/xxm_fans_home/repo/xxm_fans_backend
source /home/yifeianyi/Desktop/venv/bin/activate

python -c "
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'xxm_fans_home.settings')
import django
django.setup()
from django.conf import settings

print(f'DEBUG = {settings.DEBUG}')
print(f'SECRET_KEY 长度 = {len(settings.SECRET_KEY)}')
print(f'SECRET_KEY 前10字符 = {settings.SECRET_KEY[:10]}...')
"
```

### 6.2 验证安全响应

Debug 关闭时，404 错误不应显示详细调试信息：

```bash
curl http://127.0.0.1:8000/this-page-does-not-exist/
```

**正确输出（Debug=False）：**
```html
<!doctype html>
<html lang="en">
<head><title>Not Found</title></head>
<body>
  <h1>Not Found</h1>
  <p>The requested resource was not found on this server.</p>
</body>
</html>
```

**错误输出（Debug=True）：**
```html
<!-- 包含详细的堆栈跟踪、文件路径、配置信息等 -->
```

---

## 7. 项目当前配置

### 7.1 配置文件位置

| 文件 | 路径 |
|-----|------|
| 环境变量文件 | `/home/yifeianyi/Desktop/xxm_fans_home/env/backend.env` |
| 后端软链接 | `/home/yifeianyi/Desktop/xxm_fans_home/repo/xxm_fans_backend/.env` |
| Django 设置 | `xxm_fans_backend/xxm_fans_home/settings.py` |

### 7.2 配置加载流程

```
env/backend.env
      │
      ▼ (软链接)
repo/xxm_fans_backend/.env
      │
      ▼ (python-dotenv 加载)
os.environ
      │
      ▼ (Django 读取)
settings.SECRET_KEY
```

---

## 8. 常见问题

### Q1: 修改密钥后用户需要重新登录吗？
**A**: 是的，修改密钥会使所有现有 session 失效，所有用户需要重新登录。

### Q2: 开发环境可以用简单密钥吗？
**A**: 可以，但建议使用相同的生成方式，只是不需要严格保密。

### Q3: 如何检查密钥是否安全？
**A**: 确认满足以下条件：
- 长度 >= 50 字符
- 包含大小写字母、数字、特殊字符
- 随机生成，无明显规律
- 未在代码库中出现

---

## 9. 相关文档

- [Django 官方文档 - SECRET_KEY](https://docs.djangoproject.com/en/5.0/ref/settings/#secret-key)
- [Django 安全部署检查清单](https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/)
- `../server_config/` - 服务器配置相关文档

---

**维护者**: AI Agent  
**最后更新**: 2026-02-18
