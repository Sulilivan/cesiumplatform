# Docker 开发指南

本文档介绍如何使用 Docker 进行开发和部署。

## 目录结构

```
cesiumapartment/
├── docker-compose.yml          # 默认开发环境配置
├── docker-compose.dev.yml      # 开发环境配置（同上）
├── docker-compose.prod.yml     # 生产环境配置
├── nginx.conf                  # Nginx 反向代理配置（可选）
├── backend/
│   ├── Dockerfile              # 后端 Docker 镜像
│   ├── .dockerignore           # Docker 构建忽略文件
│   ├── .env                    # 环境变量
│   └── .env.example            # 环境变量模板
└── frontend/
    ├── Dockerfile              # 前端生产镜像
    ├── Dockerfile.dev          # 前端开发镜像
    ├── Dockerfile.prod         # 前端生产镜像（多阶段构建）
    ├── .dockerignore           # Docker 构建忽略文件
    ├── .env                    # 环境变量
    └── .env.production         # 生产环境变量
```

## 前置要求

- Docker Desktop (Windows/Mac) 或 Docker Engine (Linux)
- Docker Compose v2.0+

## 开发环境

### 快速启动

```bash
# 在项目根目录执行
docker-compose up
```

或者使用开发配置文件：

```bash
docker-compose -f docker-compose.dev.yml up
```

### 访问地址

| 服务 | 地址 |
|------|------|
| 前端 | http://localhost:5173 |
| 后端 API | http://localhost:8000 |
| API 文档 | http://localhost:8000/docs |

### 开发特性

1. **热重载**：前端和后端代码修改后自动重新加载
2. **代码挂载**：本地代码目录挂载到容器内，无需重新构建
3. **数据库持久化**：SQLite 数据库文件持久化到本地

### 常用命令

```bash
# 后台启动
docker-compose up -d

# 查看日志
docker-compose logs -f

# 查看特定服务日志
docker-compose logs -f backend
docker-compose logs -f frontend

# 重新构建镜像
docker-compose build

# 重新构建并启动
docker-compose up --build

# 停止服务
docker-compose down

# 停止并删除数据卷
docker-compose down -v

# 进入后端容器
docker-compose exec backend bash

# 进入前端容器
docker-compose exec frontend sh
```

## 生产环境

### 构建并启动

```bash
docker-compose -f docker-compose.prod.yml up -d --build
```

### 访问地址

| 服务 | 地址 |
|------|------|
| 前端 | http://localhost:3000 |
| 后端 API | http://localhost:8000 |

### 使用 Nginx 反向代理（可选）

如需统一入口，编辑 `docker-compose.prod.yml`，取消 nginx 服务的注释：

```yaml
nginx:
  image: nginx:alpine
  container_name: water-platform-nginx
  ports:
    - "80:80"
  volumes:
    - ./nginx.conf:/etc/nginx/nginx.conf:ro
  depends_on:
    - frontend
    - backend
  restart: always
  networks:
    - water-platform-network
```

然后访问 http://localhost 即可。

## 单独构建镜像

### 后端镜像

```bash
cd backend
docker build -t water-platform-backend .

# 运行
docker run -p 8000:8000 -v $(pwd)/water_platform.db:/app/water_platform.db water-platform-backend
```

### 前端开发镜像

```bash
cd frontend
docker build -f Dockerfile.dev -t water-platform-frontend-dev .

# 运行
docker run -p 5173:5173 -v $(pwd):/app water-platform-frontend-dev
```

### 前端生产镜像

```bash
cd frontend
docker build -f Dockerfile.prod -t water-platform-frontend .

# 运行
docker run -p 3000:3000 water-platform-frontend
```

## 环境变量配置

### 前端环境变量

在 `frontend/.env` 中配置：

```env
VITE_API_URL=http://localhost:8000
VITE_CESIUM_BASE_URL=/Cesium
```

### 后端环境变量

在 `backend/.env` 中配置：

```env
DATABASE_URL=sqlite:///./water_platform.db
SECRET_KEY=your-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
CORS_ORIGINS=http://localhost:5173,http://localhost:3000
```

## 故障排除

### 端口被占用

```bash
# Windows - 查找占用端口的进程
netstat -ano | findstr :8000

# 杀死进程
taskkill /PID <进程ID> /F

# 或者修改 docker-compose.yml 中的端口映射
ports:
  - "8001:8000"  # 改为其他端口
```

### 容器无法访问宿主机

如果容器内需要访问宿主机服务，使用：
- Windows/Mac: `host.docker.internal`
- Linux: 使用 `--network host` 或配置 `extra_hosts`

### 前端无法连接后端

1. 确保后端容器正在运行
2. 检查 `VITE_API_URL` 环境变量
3. 检查后端 CORS 配置

### 数据库丢失

确保在 `docker-compose.yml` 中配置了卷挂载：
```yaml
volumes:
  - ./backend/water_platform.db:/app/water_platform.db
```

### 重新安装依赖

```bash
# 后端
docker-compose exec backend pip install -r requirements.txt

# 前端
docker-compose exec frontend npm install
```

## 清理资源

```bash
# 停止并删除容器
docker-compose down

# 删除所有未使用的镜像
docker image prune -a

# 删除所有未使用的卷
docker volume prune

# 删除所有未使用的资源
docker system prune -a
```

## 持续集成/部署 (CI/CD)

### GitHub Actions 示例

```yaml
name: Build and Push Docker Images

on:
  push:
    branches: [main]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Login to Docker Hub
        uses: docker/login-action@v2
        with:
          username: ${{ secrets.DOCKER_USERNAME }}
          password: ${{ secrets.DOCKER_TOKEN }}
      
      - name: Build and push backend
        uses: docker/build-push-action@v4
        with:
          context: ./backend
          push: true
          tags: yourusername/water-platform-backend:latest
      
      - name: Build and push frontend
        uses: docker/build-push-action@v4
        with:
          context: ./frontend
          file: ./frontend/Dockerfile.prod
          push: true
          tags: yourusername/water-platform-frontend:latest
```
