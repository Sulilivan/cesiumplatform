# 智慧水利监测平台

基于 Vue 3 + Cesium + FastAPI 的重力坝三维可视化监测系统，实现测点数据的实时展示、历史查询、统计分析等功能。

[![Docker Hub - Backend](https://img.shields.io/badge/Docker%20Hub-Backend-blue)](https://hub.docker.com/r/rayansullivan/water-platform-backend)
[![Docker Hub - Frontend](https://img.shields.io/badge/Docker%20Hub-Frontend-blue)](https://hub.docker.com/r/rayansullivan/water-platform-frontend)

## 项目概述

本系统是一个完整的水利工程监测数据可视化平台，主要功能包括：

- 🌍 **三维场景可视化**：基于 Cesium 的重力坝三维模型展示
- 📊 **监测数据管理**：支持倒垂线、引张线、静力水准、水位等多种监测设备
- 📈 **数据分析**：历史数据查询、趋势图表、统计分析
- 🔐 **用户权限管理**：管理员/普通用户角色控制
- ⚠️ **告警检测**：支持阈值告警配置

## 技术栈

| 模块 | 技术 |
|------|------|
| 前端框架 | Vue 3 + Vite |
| 三维引擎 | Cesium.js |
| 图表库 | ECharts |
| HTTP 客户端 | Axios |
| 后端框架 | FastAPI |
| 数据库 | SQLite + SQLAlchemy ORM |
| 认证 | JWT Token |
| 容器化 | Docker |

---

## 🚀 快速开始

### 环境要求

- **Docker Desktop** (Windows/Mac) 或 **Docker Engine** (Linux)
- Docker Compose v2.0+

> 💡 如果你没有安装 Docker，请先前往 [Docker 官网](https://www.docker.com/products/docker-desktop/) 下载安装。

---

### 第一步：克隆项目

```bash
git clone https://github.com/Sulilivan/cesiumplatform.git
cd cesiumplatform
```

---

### 第二步：启动服务

```bash
docker-compose -f docker-compose.deploy.yml up -d
```

> ⏳ 首次运行会自动从 Docker Hub 下载镜像（约 500MB），请耐心等待。

---

### 第三步：访问系统

启动成功后，打开浏览器访问：

| 服务 | 地址 | 说明 |
|------|------|------|
| 🖥️ 前端界面 | http://localhost:3000 | 三维可视化主界面 |
| 📡 后端 API | http://localhost:8000 | RESTful API 服务 |
| 📖 API 文档 | http://localhost:8000/docs | Swagger 交互式文档 |

---

### 第四步：登录系统

使用默认管理员账号登录：

| 角色 | 用户名 | 密码 |
|------|--------|------|
| 管理员 | `admin` | `admin123` |

---

### 停止服务

```bash
docker-compose -f docker-compose.deploy.yml down
```

---

## 📦 Docker Hub 镜像

本项目已发布到 Docker Hub，你也可以直接拉取镜像运行：

| 镜像 | 地址 |
|------|------|
| 后端 | `rayansullivan/water-platform-backend:latest` |
| 前端 | `rayansullivan/water-platform-frontend:latest` |

```bash
# 拉取镜像
docker pull rayansullivan/water-platform-backend:latest
docker pull rayansullivan/water-platform-frontend:latest
```

---

## 🛠️ 本地开发运行（适合需要修改代码的用户）

如果你想修改源代码并自己构建，请按以下步骤操作：

### 环境要求

| 软件 | 版本要求 | 下载地址 |
|------|----------|----------|
| Node.js | >= 20.19.0 或 >= 22.12.0 | https://nodejs.org/ |
| Python | >= 3.8 | https://www.python.org/ |
| npm | 随 Node.js 安装 | - |

### 1. 克隆项目

```bash
git clone https://github.com/Sulilivan/cesiumplatform.git
cd cesiumplatform
```

### 2. 启动后端

```bash
# 进入后端目录
cd backend

# （可选）创建虚拟环境
python -m venv venv
.\venv\Scripts\activate   # Windows
# source venv/bin/activate  # Linux/Mac

# 安装依赖
pip install -r requirements.txt

# 启动服务
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

后端启动后访问：
- API 文档: http://localhost:8000/docs

### 3. 启动前端

**新开一个终端窗口**：

```bash
# 进入前端目录
cd frontend

# 安装依赖（首次运行，需要几分钟）
npm install

# 启动开发服务器
npm run dev
```

前端启动后访问：http://localhost:5173

---

## 📁 项目结构

```
cesiumplatform/
├── docker-compose.yml          # 开发环境 Docker 配置
├── docker-compose.deploy.yml   # 生产部署 Docker 配置（推荐使用）
├── frontend/                   # 前端项目
│   ├── src/
│   │   ├── components/         # Vue 组件
│   │   ├── views/              # 页面视图
│   │   ├── router/             # 路由配置
│   │   └── utils/              # 工具函数（含 API 封装）
│   ├── public/
│   │   ├── Cesium/             # Cesium 库文件
│   │   ├── modelf/             # 3D Tiles 模型
│   │   └── modeli/             # 3D Tiles 模型
│   └── package.json
├── backend/                    # 后端项目
│   ├── main.py                 # FastAPI 主入口
│   ├── sql_app/                # 数据库模块
│   │   ├── models.py           # SQLAlchemy 模型
│   │   ├── schemas.py          # Pydantic 模型
│   │   ├── crud.py             # 数据库操作
│   │   ├── auth.py             # JWT 认证
│   │   └── database.py         # 数据库配置
│   ├── water_platform.db       # SQLite 数据库
│   └── requirements.txt
└── README.md
```

---

## 🎯 功能模块

### 三维场景 (CesiumViewer)

- 加载 3D Tiles 模型
- 测点标注与高亮
- 镜头飞行定位
- 模型构件绑定
- 鼠标坐标显示

### 仪表盘 (Dashboard)

- 测点列表与筛选
- 实时数据展示
- ECharts 历史趋势图
- 场景设置控制

### 管理后台 (AdminView)

- **用户管理**：增删改查用户、角色分配
- **测点管理**：增删改查测点、位置编辑
- **数据中心**：多条件筛选、表格/图表双视图、分页展示

---

## 📡 API 概览

| 接口 | 方法 | 说明 |
|------|------|------|
| `/points/` | GET | 获取所有测点 |
| `/points/{code}` | GET/PUT/DELETE | 测点详情/更新/删除 |
| `/measurements/search` | GET | 搜索监测数据 |
| `/measurements/latest` | GET | 获取最新数据 |
| `/auth/login` | POST | 用户登录 |
| `/auth/users` | GET/POST | 用户管理 |

完整 API 文档请访问 http://localhost:8000/docs 或参阅 [backend/README.md](backend/README.md)

---

## ❓ 常见问题

### Q: 启动后访问 localhost:3000 显示"拒绝连接"？

**A**: 请检查：
1. Docker Desktop 是否正在运行
2. 执行 `docker ps` 查看容器是否正常运行
3. 如果容器未运行，执行 `docker-compose -f docker-compose.deploy.yml up -d` 重新启动

### Q: 首次启动很慢？

**A**: 首次运行需要从 Docker Hub 下载镜像（约 500MB），这取决于你的网络速度。后续启动会很快。

### Q: 如何查看容器日志？

**A**: 
```bash
# 查看所有日志
docker-compose -f docker-compose.deploy.yml logs

# 只看后端日志
docker-compose -f docker-compose.deploy.yml logs backend

# 实时跟踪日志
docker-compose -f docker-compose.deploy.yml logs -f
```

### Q: 如何完全重置？

**A**: 
```bash
# 停止并删除所有容器和数据
docker-compose -f docker-compose.deploy.yml down -v
```

---

## 📄 许可证

MIT License

## 👨‍💻 联系方式

如有问题请提交 [Issue](https://github.com/Sulilivan/cesiumplatform/issues) 或联系开发团队。
