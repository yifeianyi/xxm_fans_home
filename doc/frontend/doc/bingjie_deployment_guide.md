# Bingjie歌单部署指南

## 项目概述

Bingjie歌单是一个基于Django + Vue.js的歌手歌单展示网站，完全复刻了youyou歌单的功能和结构。该应用提供了歌曲列表展示、筛选、随机推荐等功能。

## 项目结构

```
bingjie_SongList/              # Django后端应用
├── migrations/               # 数据库迁移文件
├── admin.py                  # Django管理后台配置
├── models.py                 # 数据模型定义
├── urls.py                   # URL路由配置
└── views.py                  # API视图函数

bingjie_SongList_frontend/     # Vue.js前端项目
├── public/
│   └── photos/               # 图片资源目录
├── src/
│   ├── components/
│   │   ├── HeadIcon.vue      # 头像组件
│   │   └── SongList.vue      # 歌曲列表组件
│   ├── App.vue               # 根组件
│   └── main.js               # 入口文件
├── index.html                # HTML模板
├── package.json              # 前端依赖配置
└── vite.config.js            # Vite构建配置
```

## 环境要求

- Python 3.8+
- Node.js 16+
- Django 5.2.3
- Vue.js 3
- SQLite (开发环境)

## 部署步骤

### 1. 后端部署

#### 1.1 安装依赖
```bash
# 激活虚拟环境
venv\Scripts\activate

# 安装Python依赖
pip install -r requirements.txt
```

#### 1.2 数据库配置
```bash
# 创建并应用数据库迁移
python manage.py makemigrations bingjie_SongList
python manage.py migrate
```

#### 1.3 创建超级管理员
```bash
python manage.py createsuperuser
```

#### 1.4 启动后端服务
```bash
python manage.py runserver
```

后端服务将在 `http://localhost:8000` 启动

### 2. 前端部署

#### 2.1 安装依赖
```bash
cd bingjie_SongList_frontend
npm install
```

#### 2.2 启动开发服务器
```bash
npm run dev
```

前端服务将在 `http://localhost:3001` 启动

### 3. 数据管理

#### 3.1 添加歌曲数据
1. 访问 `http://localhost:8000/admin`
2. 使用超级管理员账号登录
3. 在"Bingjie Songs"部分添加歌曲信息
4. 在"Bingjie Site Settings"部分配置网站设置

#### 3.2 配置网站设置
- Position 1: 头像图片
- Position 2: 背景图片

图片文件需要放置在 `bingjie_SongList_frontend/photos/` 目录下

### 4. 生产环境部署

#### 4.1 前端构建
```bash
cd bingjie_SongList_frontend
npm run build
```

#### 4.2 配置Nginx
```nginx
server {
    listen 80;
    server_name your-domain.com;

    # 前端静态文件
    location / {
        root /path/to/bingjie_SongList_frontend/dist;
        try_files $uri $uri/ /index.html;
    }

    # API接口代理
    location /api/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    # 图片文件
    location /bingjie_SongList_frontend/photos/ {
        alias /path/to/bingjie_SongList_frontend/photos/;
    }
}
```

#### 4.3 Django生产环境配置
1. 设置 `DEBUG = False`
2. 配置 `ALLOWED_HOSTS`
3. 设置安全的 `SECRET_KEY`
4. 配置静态文件服务

```bash
# 收集静态文件
python manage.py collectstatic
```

#### 4.4 使用Gunicorn运行Django
```bash
pip install gunicorn
gunicorn --bind 127.0.0.1:8000 xxm_fans_home.wsgi:application
```

### 5. API接口说明

#### 5.1 歌曲相关接口
- `GET /api/bingjie/songs/` - 获取歌曲列表
  - 参数: `language` (语言), `style` (曲风), `search` (搜索)
- `GET /api/bingjie/languages/` - 获取语言列表
- `GET /api/bingjie/styles/` - 获取曲风列表
- `GET /api/bingjie/random-song/` - 获取随机歌曲

#### 5.2 网站设置接口
- `GET /api/bingjie/site-settings/` - 获取网站设置
- `GET /api/bingjie/favicon.ico` - 获取favicon

### 6. 开发注意事项

1. **端口配置**: 前端开发服务器使用3001端口，避免与youyou歌单的3000端口冲突
2. **API路径**: 所有API接口以 `/api/bingjie/` 开头，与youyou的 `/api/youyou/` 区分
3. **静态文件**: 图片资源存放在各自的 `photos/` 目录中
4. **数据库模型**: 使用 `bingjie_` 前缀命名模型，避免与youyou冲突

### 7. 故障排除

#### 7.1 常见问题
1. **端口冲突**: 确保前端端口3001未被占用
2. **API连接失败**: 检查后端服务是否正常运行
3. **图片不显示**: 确认图片路径和静态文件配置正确

#### 7.2 调试方法
1. 检查浏览器控制台错误信息
2. 查看Django开发服务器日志
3. 验证数据库迁移是否成功应用

## 总结

Bingjie歌单应用已成功复刻youyou歌单的所有功能，包括：
- 歌曲列表展示
- 语言和曲风筛选
- 随机歌曲推荐
- 网站设置管理
- 响应式界面设计

按照本指南的步骤，您可以成功部署并运行Bingjie歌单应用。