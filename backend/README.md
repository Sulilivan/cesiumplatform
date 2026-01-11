# 智慧水利监测平台后端 API 文档

## 项目概述

智慧水利监测平台后端提供完整的水利监测数据管理服务，包括测点管理、数据录入、数据查询、统计分析、告警检测、用户认证等功能。

## 技术栈

- **框架**: FastAPI 0.104.1
- **数据库**: SQLite (SQLAlchemy ORM)
- **数据验证**: Pydantic 2.5.2
- **服务器**: Uvicorn 0.24.0
- **认证**: JWT (python-jose)
- **密码加密**: passlib + bcrypt

## 快速开始

### 环境要求

- Python 3.8+
- pip

### 安装依赖

```bash
pip install -r requirements.txt
```

### 启动服务

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

服务启动后访问:
- API 文档: http://localhost:8000/docs
- ReDoc 文档: http://localhost:8000/redoc

## 项目结构

```
backend/
├── main.py              # FastAPI 主入口，路由定义
├── sql_app/
│   ├── __init__.py
│   ├── database.py      # 数据库连接配置
│   ├── models.py        # SQLAlchemy ORM 模型
│   ├── schemas.py       # Pydantic 数据验证模型
│   ├── crud.py          # 数据库 CRUD 操作
│   └── auth.py          # JWT 认证逻辑
├── data/                # 数据导入脚本使用的数据文件
├── water_platform.db    # SQLite 数据库文件
├── requirements.txt     # Python 依赖
└── README.md
```

## 数据库模型

### users (用户表)

| 字段 | 类型 | 说明 |
|------|------|------|
| id | Integer | 用户ID (主键) |
| username | String | 用户名 (唯一) |
| email | String | 邮箱 (唯一) |
| hashed_password | String | 加密后的密码 |
| role | String | 角色: admin 或 user |
| is_active | Boolean | 是否激活 |
| created_at | DateTime | 创建时间 |

### monitor_points (测点表)

| 字段 | 类型 | 说明 |
|------|------|------|
| id | Integer | ID (主键) |
| point_code | String | 测点编号 (唯一) |
| point_name | String | 测点名称 |
| device_type | String | 设备类型 (倒垂线/引张线/静力水准/水位) |
| longitude | Float | 经度 |
| latitude | Float | 纬度 |
| height | Float | 高程 |
| bind_model_id | String | 绑定的3D模型构件ID |

### measurements (监测数据表)

| 字段 | 类型 | 说明 |
|------|------|------|
| id | Integer | 数据ID (主键) |
| point_code | String | 测点编号 (外键) |
| value | Float | 监测值 |
| time | DateTime | 监测时间 |
| measurement_type | String | 测量类型 (左右岸/上下游/沉降/位移/其他) |

### inverted_plumb_data (倒垂线数据表)

| 字段 | 类型 | 说明 |
|------|------|------|
| id | Integer | ID (主键) |
| point_code | String | 测点编号 (外键) |
| left_right_value | Float | 左右岸值 |
| up_down_value | Float | 上下游值 |
| time | DateTime | 监测时间 |

### static_level_data (静力水准数据表)

| 字段 | 类型 | 说明 |
|------|------|------|
| id | Integer | ID (主键) |
| point_code | String | 测点编号 (外键) |
| value | Float | 沉降值 |
| time | DateTime | 监测时间 |

### tension_line_data (引张线数据表)

| 字段 | 类型 | 说明 |
|------|------|------|
| id | Integer | ID (主键) |
| point_code | String | 测点编号 (外键) |
| value | Float | 位移值 |
| time | DateTime | 监测时间 |

### water_level_data (水位数据表)

| 字段 | 类型 | 说明 |
|------|------|------|
| id | Integer | ID (主键) |
| point_code | String | 测点编号 (外键) |
| value | Float | 水位值 |
| time | DateTime | 监测时间 |

---

## API 接口文档

### 基础信息

- **Base URL**: `http://localhost:8000`
- **Content-Type**: `application/json`
- **认证方式**: Bearer Token (大部分接口需要)

---

## 认证接口

### 1. 用户登录

**接口**: `POST /auth/login`

**请求体**:
```json
{
  "username": "admin",
  "password": "admin123"
}
```

**响应示例**:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "username": "admin",
    "email": "admin@example.com",
    "role": "admin",
    "is_active": true,
    "created_at": "2024-01-01T00:00:00"
  }
}
```

### 2. 获取当前用户信息

**接口**: `GET /auth/me`

**请求头**: `Authorization: Bearer {token}`

**响应示例**:
```json
{
  "id": 1,
  "username": "admin",
  "email": "admin@example.com",
  "role": "admin",
  "is_active": true,
  "created_at": "2024-01-01T00:00:00"
}
```

### 3. 获取用户列表 (管理员)

**接口**: `GET /auth/users`

**权限**: 管理员

### 4. 创建用户 (管理员)

**接口**: `POST /auth/users`

**权限**: 管理员

**请求体**:
```json
{
  "username": "newuser",
  "email": "newuser@example.com",
  "password": "password123",
  "role": "user"
}
```

### 5. 更新用户 (管理员)

**接口**: `PUT /auth/users/{user_id}`

**权限**: 管理员

### 6. 删除用户 (管理员)

**接口**: `DELETE /auth/users/{user_id}`

**权限**: 管理员

---

## 测点接口

### 1. 获取所有测点

**接口**: `GET /points/`

**响应示例**:
```json
[
  {
    "point_code": "IP1",
    "point_name": "IP1",
    "longitude": 120.123456,
    "latitude": 30.123456,
    "height": 100.5,
    "device_type": "倒垂线",
    "bind_model_id": "model_123"
  }
]
```

### 2. 获取测点详情

**接口**: `GET /points/{point_code}`

**响应示例**:
```json
{
  "point_code": "IP1",
  "point_name": "IP1",
  "longitude": 120.123456,
  "latitude": 30.123456,
  "height": 100.5,
  "device_type": "倒垂线",
  "latest_value": 12.3456,
  "latest_time": "2024-01-01T08:00:00",
  "data_count": 100
}
```

### 3. 创建测点 (管理员)

**接口**: `POST /points/`

**请求体**:
```json
{
  "point_code": "IP10",
  "point_name": "倒垂线10",
  "device_type": "倒垂线",
  "longitude": 120.123456,
  "latitude": 30.123456,
  "height": 100.5,
  "bind_model_id": null
}
```

### 4. 更新测点 (管理员)

**接口**: `PUT /points/{point_code}`

### 5. 删除测点 (管理员)

**接口**: `DELETE /points/{point_code}`

---

## 监测数据接口

### 1. 搜索监测数据 (数据中心)

**接口**: `GET /measurements/search`

**查询参数**:
- `start_time` (datetime, 可选): 开始时间
- `end_time` (datetime, 可选): 结束时间
- `device_type` (string, 可选): 设备类型筛选
- `point_name` (string, 可选): 测点名称筛选
- `skip` (int, 默认0): 跳过记录数
- `limit` (int, 默认200): 返回记录数

**请求示例**:
```
GET /measurements/search?device_type=倒垂线&point_name=IP1&skip=0&limit=50
```

**响应示例**:
```json
[
  {
    "id": 1,
    "point_code": "IP1左右岸",
    "value": 12.3456,
    "time": "2024-01-01T08:00:00",
    "device_type": "倒垂线",
    "point_name": "IP1",
    "measurement_type": "左右岸"
  }
]
```

### 2. 获取最新数据

**接口**: `GET /measurements/latest`

### 3. 获取测点历史数据

**接口**: `GET /measurements/{point_code}`

### 4. 获取测点最新数据

**接口**: `GET /measurements/{point_code}/latest`

### 5. 获取时间范围数据

**接口**: `GET /measurements/{point_code}/range`

**查询参数**:
- `start_time` (datetime, 必填): 开始时间
- `end_time` (datetime, 必填): 结束时间

### 6. 获取统计数据

**接口**: `GET /measurements/{point_code}/stats`

**响应示例**:
```json
{
  "point_code": "IP1",
  "max_value": 15.6789,
  "min_value": 10.1234,
  "avg_value": 12.8901,
  "count": 100,
  "latest_time": "2024-01-01T08:00:00",
  "earliest_time": "2023-01-01T08:00:00"
}
```

### 7. 添加监测数据 (管理员)

**接口**: `POST /measurements/`

**请求体**:
```json
{
  "point_code": "IP1",
  "value": 12.3456,
  "time": "2024-01-01T08:00:00",
  "measurement_type": "左右岸"
}
```

### 8. 批量添加数据 (管理员)

**接口**: `POST /measurements/batch`

### 9. 更新数据 (管理员)

**接口**: `PUT /measurements/{measurement_id}`

### 10. 删除数据 (管理员)

**接口**: `DELETE /measurements/{measurement_id}`

### 11. 数据对比

**接口**: `GET /measurements/{point_code}/compare`

---

## 专用数据接口

### 倒垂线数据

| 接口 | 方法 | 说明 |
|------|------|------|
| `/inverted-plumb/{point_code}` | GET | 获取历史数据 |
| `/inverted-plumb/{point_code}/latest` | GET | 获取最新数据 |
| `/inverted-plumb/` | POST | 添加数据 (管理员) |

### 静力水准数据

| 接口 | 方法 | 说明 |
|------|------|------|
| `/static-level/{point_code}` | GET | 获取历史数据 |
| `/static-level/{point_code}/latest` | GET | 获取最新数据 |
| `/static-level/` | POST | 添加数据 (管理员) |

### 引张线数据

| 接口 | 方法 | 说明 |
|------|------|------|
| `/tension-line/{point_code}` | GET | 获取历史数据 |
| `/tension-line/{point_code}/latest` | GET | 获取最新数据 |
| `/tension-line/` | POST | 添加数据 (管理员) |

### 水位数据

| 接口 | 方法 | 说明 |
|------|------|------|
| `/water-level/{point_code}` | GET | 获取历史数据 |
| `/water-level/{point_code}/latest` | GET | 获取最新数据 |
| `/water-level/` | POST | 添加数据 (管理员) |

---

## 告警接口

### 告警检测

**接口**: `POST /alerts/check`

**请求体**:
```json
[
  {
    "point_code": "IP1",
    "min_value": 10.0,
    "max_value": 15.0,
    "alert_enabled": true
  }
]
```

**响应示例**:
```json
[
  {
    "point_code": "IP1",
    "point_name": "IP1",
    "current_value": 16.5,
    "alert_type": "超过上限",
    "threshold": 15.0,
    "time": "2024-01-01T08:00:00"
  }
]
```

---

## 错误处理

所有错误响应遵循以下格式：

```json
{
  "detail": "错误描述信息"
}
```

### 常见错误码

| 状态码 | 说明 |
|--------|------|
| 200 | 请求成功 |
| 400 | 请求参数错误 |
| 401 | 未认证或Token无效 |
| 403 | 无权限访问 |
| 404 | 资源不存在 |
| 422 | 请求参数验证失败 |

---

## CORS 配置

当前配置允许所有来源的跨域请求：

```python
allow_origins=["*"]
```

生产环境建议修改为具体的前端地址：

```python
allow_origins=["http://your-frontend-domain.com"]
```

---

## 注意事项

1. **时间格式**: 所有时间参数使用 ISO 8601 格式，例如 `2024-01-01T08:00:00`

2. **设备类型**:
   - 倒垂线
   - 引张线
   - 静力水准
   - 水位

3. **测量类型**:
   - 左右岸
   - 上下游
   - 沉降
   - 位移
   - 其他

4. **认证说明**:
   - 大部分接口需要 JWT Token 认证
   - 管理员接口需要 role=admin 的用户
   - Token 有效期默认 30 分钟

5. **数据关联**:
   - measurements 表中的 point_code 可能包含后缀（如 "IP1左右岸"）
   - 查询时使用前缀匹配关联到 monitor_points 表

---

## 联系方式

如有问题请联系开发团队。
