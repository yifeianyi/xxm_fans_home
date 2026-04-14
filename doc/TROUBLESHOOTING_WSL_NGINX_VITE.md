# WSL 开发环境白屏问题排查记录

## 问题现象

在 WSL2 中执行 `bash scripts/dev_start_services.sh` 后：
- 后端 API (`http://localhost:8080/api/`) 可以正常访问
- 前端页面 (`http://localhost:8080/`) 白屏，浏览器控制台报错：
  ```
  GET http://localhost:8080/node_modules/.vite/deps/react_jsx-dev-runtime.js?v=xxx net::ERR_ABORTED 504 (Outdated Optimize Dep)
  GET http://localhost:8080/node_modules/vite/dist/client/env.mjs net::ERR_ABORTED 404 (Not Found)
  ```

## 根因分析

问题由 **Nginx 代理配置错误** 和 **Vite 服务端口漂移** 共同导致：

### 1. Nginx 配置错误代理了主前端依赖

`infra/nginx/xxm_nginx.conf` 中原先存在如下配置：

```nginx
location /node_modules/ {
    proxy_pass http://127.0.0.1:5179/node_modules/;  # ❌ 指向了模板化歌单前端
}

location ~ ^/@(id|vite)/ {
    proxy_pass http://127.0.0.1:5179;  # ❌ 也指向了模板化歌单前端
}
```

主前端（Vite，端口 5173）在加载页面时，会请求 `/node_modules/.vite/deps/react_jsx-dev-runtime.js` 等预构建依赖。但 Nginx 将这类请求错误地代理到了 **模板化歌单前端（端口 5179）**。

模板化歌单前端使用的是另一个 Vite 实例，其依赖预构建缓存（`.vite/deps/` 下的文件 hash）与主前端不同。因此当主前端请求旧的预构建 URL 时，5179 上的 Vite 返回了 **504 Outdated Optimize Dep**，导致 React 无法初始化，页面白屏。

### 2. Vite 服务端口漂移

`scripts/dev_start_services.sh` 启动 Vite 时默认绑定 5173 端口。如果之前存在残留进程未彻底清理，Vite 会自动尝试 5174、5175 等端口。这会导致 Nginx 的 `proxy_pass http://127.0.0.1:5173` 代理到一个旧的/不匹配的 Vite 实例，进一步加剧缓存错乱问题。

### 3. WebSocket 代理配置副作用（次要）

Nginx 原配置中：
```nginx
proxy_set_header Connection "upgrade";
```
这会导致**所有 HTTP 请求**（不仅是 WebSocket）都被标记为 `Connection: upgrade`，可能干扰 Vite 客户端对 504 错误的自动恢复机制（Vite 客户端在收到 504 后本应自动刷新页面获取新资源）。

## 修复方案

### 修复 1：修正 Nginx 代理目标

将 `/node_modules/` 的 `proxy_pass` 改回主前端 5173：

```nginx
location /node_modules/ {
    proxy_pass http://127.0.0.1:5173/node_modules/;  # ✅ 指向主前端
    ...
}
```

### 修复 2：修正 WebSocket 连接头

在 `http` 块中添加 `map` 指令，让 `Connection` 头根据实际请求条件设置：

```nginx
map $http_upgrade $connection_upgrade {
    default upgrade;
    ''      close;
}

location / {
    proxy_pass http://127.0.0.1:5173;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection $connection_upgrade;  # ✅ 不再是硬编码 "upgrade"
    ...
}
```

### 修复 3：清理残留进程并固定端口

在重启服务前，先确保杀掉所有残留的前端进程：

```bash
# 停止所有服务
./scripts/dev_stop_services.sh

# 手动清理可能残留的 Vite 进程
pkill -f "node.*vite"

# 清除 Vite 缓存（可选）
rm -rf repo/xxm_fans_frontend/node_modules/.vite

# 重新启动
./scripts/dev_start_services.sh
```

启动后通过以下命令确认 Vite 确实监听在 5173：
```bash
ss -tlnp | grep 5173
```

## 验证结果

修复后：
- `curl http://localhost:8080/node_modules/.vite/deps/react_jsx-dev-runtime.js` 返回 `200 OK`
- 浏览器访问 `http://localhost:8080/` 正常渲染首页
- Windows 浏览器通过 `localhost:8080` 访问 WSL2 服务也恢复正常

## 预防措施

1. **停止服务后检查残留进程**：`dev_stop_services.sh` 的停止逻辑可能无法覆盖所有 `nohup` 启动的 Vite 实例，建议手动检查 `ss -tlnp | grep 5173`。
2. **避免多前端共用 `/node_modules/` 路径**：如果未来仍需多个 Vite 前端共存，建议通过 `base` 配置区分资源路径前缀，而不是在 Nginx 中硬编码共享的 `location /node_modules/`。
3. **WSL 访问建议**：WSL2 默认支持 `localhost` 转发。如果仍遇到连接问题，可尝试使用 WSL IP 访问（通过 `ip addr show eth0` 获取）。
