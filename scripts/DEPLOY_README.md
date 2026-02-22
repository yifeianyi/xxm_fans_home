# XXM Fans Home 部署脚本说明

本文档说明如何使用新创建的部署脚本将代码部署到生产服务器。

## 脚本列表

| 脚本 | 用途 | 说明 |
|------|------|------|
| `build-frontend.sh` | 构建前端 | 本地构建 Next.js 前端，可选自动部署 |
| `deploy-to-server.sh` | 部署前端 | 上传前端构建产物到服务器并重启服务 |
| `deploy-backend.sh` | 部署后端 | 上传后端代码到服务器并重启服务 |
| `deploy-all.sh` | 完整部署 | 一键部署前端和后端 |
| `reload-nginx.sh` | 重载 Nginx | 使用 `nginx -s reload` 重载配置 |

## 配置

所有脚本自动从以下配置文件读取服务器信息：

```
/home/yifeianyi/Desktop/xxm_fans_home/.agents/skills/prod-env-connect/config.yaml
```

当前配置：
- 服务器: `47.92.253.0:22`
- 用户名: `yifeianyi`
- 远程路径: `/home/yifeianyi/Desktop/xxm_fans_home`

## 前置要求

1. **SSH 密钥配置**：确保本地 SSH 密钥已添加到服务器
   ```bash
   ssh-copy-id yifeianyi@47.92.253.0
   ```

2. **rsync 安装**：确保本地已安装 rsync（用于文件同步）
   ```bash
   # Ubuntu/Debian
   sudo apt-get install rsync
   
   # macOS
   brew install rsync
   ```

## 使用示例

### 1. 仅构建前端（不部署）

```bash
cd /home/yifeianyi/Desktop/xxm_fans_home/scripts
./build-frontend.sh
```

### 2. 构建并自动部署前端

```bash
./build-frontend.sh --deploy
# 或
./build-frontend.sh -d
```

### 3. 使用现有构建产物部署前端

```bash
./build-frontend.sh -d -s
# 或
./deploy-to-server.sh --skip-build
```

### 4. 仅部署前端（不构建）

```bash
./deploy-to-server.sh
```

### 5. 部署后端

```bash
./deploy-backend.sh
```

跳过数据库迁移：
```bash
./deploy-backend.sh --skip-migrate
```

### 6. 一键完整部署（前端+后端）

```bash
./deploy-all.sh
```

仅部署前端：
```bash
./deploy-all.sh --frontend-only
```

仅部署后端：
```bash
./deploy-all.sh --backend-only
```

跳过前端构建：
```bash
./deploy-all.sh --skip-build
```

跳过数据库迁移：
```bash
./deploy-all.sh --skip-migrate
```

### 7. 仅重载 Nginx

```bash
./reload-nginx.sh
```

## 部署流程

### 前端部署流程

1. **本地构建**（可选）
   - 清理旧构建
   - 安装依赖
   - 执行 `npm run build`
   - 复制 `public` 到 `standalone`

2. **创建备份**
   - 在服务器上备份当前版本（保留最近3个）

3. **上传代码**
   - 使用 rsync 同步构建产物到服务器

4. **重启服务**
   - 停止现有 Next.js 进程
   - 启动新的 Next.js 服务

5. **重载 Nginx**
   - 测试 Nginx 配置
   - 执行 `nginx -s reload`

### 后端部署流程

1. **创建备份**
   - 在服务器上备份当前代码（保留最近3个）

2. **上传代码**
   - 使用 rsync 同步后端代码到服务器
   - 排除: `.git`, `venv`, `__pycache__`, `db.sqlite3` 等

3. **执行部署命令**
   - 安装依赖
   - 数据库迁移（可选）
   - 收集静态文件
   - 重启后端服务

4. **重载 Nginx**

## 备份与回滚

### 前端备份位置

```
/home/yifeianyi/Desktop/xxm_fans_home/repo/xxm_fans_frontend/.next/backups/
```

### 后端备份位置

```
/home/yifeianyi/Desktop/xxm_fans_home/repo/backups/
```

### 手动回滚

查看备份列表：
```bash
ssh yifeianyi@47.92.253.0 'ls -la /home/yifeianyi/Desktop/xxm_fans_home/repo/xxm_fans_frontend/.next/backups/'
```

回滚前端（示例）：
```bash
ssh yifeianyi@47.92.253.0 '
  cd /home/yifeianyi/Desktop/xxm_fans_home/repo/xxm_fans_frontend/.next
  rm -rf standalone
  cp -r backups/standalone_20240101_120000 standalone
  # 重启服务...
'
```

## 故障排查

### SSH 连接失败

```bash
# 测试连接
ssh -o ConnectTimeout=5 yifeianyi@47.92.253.0 "echo 'OK'"

# 检查密钥
ls -la ~/.ssh/id_rsa*

# 重新添加密钥
ssh-copy-id yifeianyi@47.92.253.0
```

### 部署后服务未更新

1. 检查 Next.js 进程：
   ```bash
   ssh yifeianyi@47.92.253.0 'pgrep -f next-server'
   ```

2. 查看日志：
   ```bash
   ssh yifeianyi@47.92.253.0 'tail -f /tmp/nextjs.log'
   ```

3. 检查后端服务状态：
   ```bash
   ssh yifeianyi@47.92.253.0 'sudo systemctl status xxm-home-backend.service'
   ```

### Nginx 配置错误

```bash
# 测试配置
ssh yifeianyi@47.92.253.0 'sudo nginx -t'

# 查看 Nginx 错误日志
ssh yifeianyi@47.92.253.0 'sudo tail -f /var/log/nginx/error.log'
```

## 安全注意事项

1. **备份优先**：每次部署会自动创建备份
2. **配置验证**：Nginx 配置会在重载前自动测试
3. **服务检查**：后端服务会在部署后检查状态
4. **低峰期部署**：建议在生产环境低峰期进行部署

## 其他说明

- 所有脚本在执行前会询问确认
- 使用颜色输出便于识别执行状态
- 支持 `-h` 或 `--help` 查看帮助信息
