# 智慧水利监测平台前端

基于 Vue 3 + Vite + Cesium 的重力坝三维可视化监测系统前端。

## 项目概述

本前端项目实现了水利工程监测数据的三维可视化展示，主要功能包括：

- 🌍 基于 Cesium 的三维地球与模型展示
- 📊 基于 ECharts 的监测数据图表
- 🔐 JWT 认证与路由守卫
- 📱 响应式仪表盘界面

## 技术栈

- **框架**: Vue 3.5.25
- **构建工具**: Vite 7.2.4
- **三维引擎**: Cesium 1.136.0
- **路由**: Vue Router 4.6.3
- **图表**: ECharts 5.5.1 + vue-echarts 7.0.3
- **HTTP**: Axios 1.7.2

## 快速开始

### 方式一：Docker 运行（推荐）

#### 使用 Docker Hub 镜像（生产环境）

```bash
# 拉取并运行前端镜像
docker pull rayansullivan/water-platform-frontend:latest
docker run -d -p 3000:3000 --name water-frontend rayansullivan/water-platform-frontend:latest
```

生产版本前端将在 http://localhost:3000 启动。

**Docker Hub 地址**: https://hub.docker.com/r/rayansullivan/water-platform-frontend

#### 使用 Docker Compose 开发环境（在项目根目录）

```bash
# 在项目根目录（cesiumapartment）执行
docker-compose up --build
```

开发版本前端将在 http://localhost:5173 启动（支持热重载）。

### 方式二：本地运行

#### 环境要求

- Node.js ^20.19.0 或 >=22.12.0
- npm 或 yarn

#### 安装依赖

```bash
npm install
```

#### 启动开发服务器

```bash
npm run dev
```

开发服务器启动后访问: http://localhost:5173

#### 生产构建

```bash
npm run build
```

#### 预览构建结果

```bash
npm run preview
```

### 注意事项

1. **后端服务必须先启动**：前端依赖后端 API，请确保后端在 http://localhost:8000 运行
2. **首次安装较慢**：`npm install` 需要下载 Cesium 等大型依赖，请耐心等待
3. **Node.js 版本**：请使用 Node.js 20.x 或 22.x，其他版本可能不兼容

## 项目结构

```
frontend/
├── public/
│   ├── Cesium/              # Cesium 库文件
│   │   ├── Cesium.js
│   │   ├── Assets/          # 资源文件
│   │   ├── ThirdParty/      # 第三方依赖
│   │   ├── Widgets/         # UI 组件样式
│   │   └── Workers/         # Web Workers
│   ├── modelf/              # 3D Tiles 模型文件
│   └── modeli/              # 3D Tiles 模型文件
├── src/
│   ├── App.vue              # 根组件
│   ├── main.js              # 入口文件
│   ├── components/
│   │   ├── CesiumViewer.vue # Cesium 三维场景
│   │   ├── DashboardLayer.vue # 仪表盘布局层
│   │   └── Dashboard/       # 仪表盘子组件
│   │       ├── SidebarLeft.vue
│   │       ├── SidebarRight.vue
│   │       └── BottomBar.vue
│   ├── views/
│   │   ├── LoginView.vue    # 登录页面
│   │   └── AdminView.vue    # 管理后台
│   ├── router/
│   │   └── index.js         # 路由配置
│   └── utils/
│       └── api.js           # API 封装
├── index.html
├── vite.config.js           # Vite 配置
├── jsconfig.json
└── package.json
```

## 页面说明

### 登录页 (/login)

- 用户名/密码登录
- JWT Token 存储
- 动态粒子背景效果

### 主场景 (/)

- **CesiumViewer**: 三维场景渲染
  - 3D Tiles 模型加载
  - 测点标注显示
  - 构件高亮与选择
  - 镜头飞行定位
  
- **DashboardLayer**: 仪表盘覆盖层
  - SidebarLeft: 测点列表、场景设置
  - SidebarRight: 测点详情、历史图表
  - BottomBar: 鼠标坐标显示

### 管理后台 (/admin)

- **用户管理**: 用户增删改查、角色管理
- **测点管理**: 测点信息维护、位置编辑
- **数据中心**: 
  - 时间/类型/测点筛选
  - 表格视图 (分页50条/页)
  - 图表视图 (ECharts 趋势图)
  - 数据增删改查

## API 配置

API 基础地址配置在 `src/utils/api.js`:

```javascript
const API_URL = 'http://localhost:8000';
```

### 请求拦截器

- 自动添加 JWT Token 到请求头
- 401 响应自动跳转登录页

### 主要 API 调用

| 方法 | 说明 |
|------|------|
| `login(username, password)` | 用户登录 |
| `logout()` | 退出登录 |
| `api.get('/points/')` | 获取测点列表 |
| `api.get('/measurements/search')` | 搜索监测数据 |
| `api.get('/inverted-plumb/{code}')` | 获取倒垂线数据 |

## 路由配置

| 路径 | 组件 | 说明 | 权限 |
|------|------|------|------|
| `/` | CesiumViewer | 主场景 | 需登录 |
| `/login` | LoginView | 登录页 | 公开 |
| `/admin` | AdminView | 管理后台 | 需登录 |

## Cesium 配置

Cesium 基础路径通过环境变量配置:

```javascript
window.CESIUM_BASE_URL = import.meta.env.VITE_CESIUM_BASE_URL
```

### 3D Tiles 模型

模型文件放置于 `public/modelf/` 和 `public/modeli/` 目录，加载配置在 CesiumViewer.vue 中:

```javascript
const tileset = await Cesium.Cesium3DTileset.fromUrl('/modelf/tileset.json')
```

## 组件通信

### Props 传递

```
App.vue
  └── CesiumViewer.vue
        └── DashboardLayer.vue
              ├── SidebarLeft.vue
              ├── SidebarRight.vue
              └── BottomBar.vue
```

### 事件传递

- `@select-point`: 测点选择事件
- `@update:settings`: 场景设置更新
- `@bind-model`: 模型绑定事件
- `@reset-view`: 重置视角

## Docker 部署

### 使用预构建镜像

```bash
docker pull rayansullivan/cesiumapartment:latest
docker run -p 3000:3000 rayansullivan/cesiumapartment:latest
```

### 自行构建

```bash
docker build -t cesiumapartment-frontend .
docker run -p 3000:3000 cesiumapartment-frontend
```

## 开发注意事项

1. **Cesium 资源**: 确保 `public/Cesium/` 目录包含完整的 Cesium 库文件
2. **3D 模型**: 3D Tiles 模型需放置于 `public/` 下对应目录
3. **后端连接**: 开发时需确保后端服务运行在 `localhost:8000`
4. **CORS**: 后端需配置允许前端域名的跨域请求

## 浏览器支持

- Chrome >= 90
- Firefox >= 88
- Edge >= 90
- Safari >= 14

## 许可证

MIT License

## 联系方式

如有问题请联系开发团队。
