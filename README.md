# 智慧水利监测平台

基于 Vue 3 + Cesium + FastAPI 的重力坝三维可视化监测系统，实现测点数据的实时展示、历史查询、统计分析等功能。

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

## 项目结构

```
cesiumapartment/
├── frontend/                # 前端项目
│   ├── src/
│   │   ├── components/      # Vue 组件
│   │   ├── views/           # 页面视图
│   │   ├── router/          # 路由配置
│   │   └── utils/           # 工具函数
│   ├── public/              # 静态资源
│   │   ├── Cesium/          # Cesium 库
│   │   ├── modelf/          # 3D Tiles 模型
│   │   └── modeli/          # 3D Tiles 模型
│   └── package.json
├── backend/                 # 后端项目
│   ├── main.py              # FastAPI 主入口
│   ├── sql_app/             # 数据库模型和逻辑
│   │   ├── models.py        # SQLAlchemy 模型
│   │   ├── schemas.py       # Pydantic 模型
│   │   ├── crud.py          # 数据库操作
│   │   ├── auth.py          # 认证逻辑
│   │   └── database.py      # 数据库配置
│   ├── water_platform.db    # SQLite 数据库
│   └── requirements.txt
└── README.md
```

## 快速开始

### 环境要求

- Node.js >= 20.19.0
- Python >= 3.8
- npm 或 yarn

### 1. 启动后端

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

后端服务启动后：
- API 文档: http://localhost:8000/docs
- ReDoc 文档: http://localhost:8000/redoc

### 2. 启动前端

```bash
cd frontend
npm install
npm run dev
```

前端服务启动后访问: http://localhost:5173

### 3. 默认账号

| 角色 | 用户名 | 密码 |
|------|--------|------|
| 管理员 | admin | admin123 |

## 功能模块

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
- **数据中心**：
  - 多条件筛选（时间、类型、测点）
  - 表格/图表双视图
  - 分页展示（50条/页）
  - 数据增删改查

## Docker 部署

### 前端镜像

```bash
docker pull rayansullivan/cesiumapartment:latest
docker run -p 3000:3000 rayansullivan/cesiumapartment:latest
```

### 完整部署

推荐使用 Docker Compose 进行完整部署：

```yaml
version: '3.8'
services:
  frontend:
    image: rayansullivan/cesiumapartment:latest
    ports:
      - "3000:3000"
    depends_on:
      - backend
  
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    volumes:
      - ./backend/water_platform.db:/app/water_platform.db
```

## API 概览

| 接口 | 方法 | 说明 |
|------|------|------|
| `/points/` | GET | 获取所有测点 |
| `/points/{code}` | GET/PUT/DELETE | 测点详情/更新/删除 |
| `/measurements/search` | GET | 搜索监测数据 |
| `/measurements/latest` | GET | 获取最新数据 |
| `/measurements/{code}` | GET | 获取测点历史数据 |
| `/auth/login` | POST | 用户登录 |
| `/auth/users` | GET/POST | 用户管理 |
| `/inverted-plumb/{code}` | GET | 倒垂线数据 |
| `/tension-line/{code}` | GET | 引张线数据 |
| `/static-level/{code}` | GET | 静力水准数据 |
| `/water-level/{code}` | GET | 水位数据 |

完整 API 文档请参阅 [backend/README.md](backend/README.md)

## 数据库模型

### 测点表 (monitor_points)

| 字段 | 类型 | 说明 |
|------|------|------|
| point_code | String | 测点编号 (主键) |
| point_name | String | 测点名称 |
| device_type | String | 设备类型 |
| longitude | Float | 经度 |
| latitude | Float | 纬度 |
| height | Float | 高程 |
| bind_model_id | String | 绑定的3D模型构件ID |

### 监测数据表 (measurements)

| 字段 | 类型 | 说明 |
|------|------|------|
| id | Integer | 数据ID (主键) |
| point_code | String | 测点编号 |
| value | Float | 监测值 |
| time | DateTime | 监测时间 |
| measurement_type | String | 测量类型 |

## 开发说明

### 前端开发

```bash
cd frontend
npm run dev      # 开发模式
npm run build    # 生产构建
npm run preview  # 预览构建结果
```

### 后端开发

```bash
cd backend
# 使用虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
.\venv\Scripts\activate   # Windows

pip install -r requirements.txt
uvicorn main:app --reload
```

## 许可证

MIT License

## 联系方式

如有问题请联系开发团队。
