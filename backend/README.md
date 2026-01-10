python -m venv venv# 智慧水利监测平台后端 API 文档

## 项目概述

智慧水利监测平台后端提供完整的水利监测数据管理服务，包括测点管理、数据录入、数据查询、统计分析、告警检测等功能。

## 技术栈

- **框架**: FastAPI 0.104.1
- **数据库**: SQLite (SQLAlchemy ORM)
- **数据验证**: Pydantic 2.5.2
- **服务器**: Uvicorn 0.24.0

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

## 数据库

数据库文件位于 `water_platform.db`，首次运行时会自动创建以下表：

### monitor_points (测点表)

| 字段 | 类型 | 说明 |
|------|------|------|
| point_code | String | 测点编号 (主键) |
| point_name | String | 测点名称 |
| longitude | Float | 经度 |
| latitude | Float | 纬度 |
| height | Float | 高度 |
| device_type | String | 设备类型 (倒垂线/引张线/静力水准) |

### measurements (监测数据表)

| 字段 | 类型 | 说明 |
|------|------|------|
| id | Integer | 数据ID (主键) |
| point_code | String | 测点编号 (外键) |
| value | Float | 监测值 |
| time | DateTime | 监测时间 |
| measurement_type | String | 测量类型 (左右岸/上下游/沉降/位移/其他) |

## API 接口文档

### 基础信息

- **Base URL**: `http://localhost:8000`
- **Content-Type**: `application/json`

---

### 1. 获取所有测点

获取系统中所有测点的信息，用于地图展示。

**接口**: `GET /points/`

**请求参数**: 无

**响应示例**:
```json
[
  {
    "point_code": "IP1",
    "point_name": "倒垂线1",
    "longitude": 120.123456,
    "latitude": 30.123456,
    "height": 100.5,
    "device_type": "倒垂线"
  }
]
```

---

### 2. 获取测点历史数据

获取指定测点的所有历史监测数据，按时间排序。

**接口**: `GET /measurements/{point_code}`

**路径参数**:
- `point_code` (string): 测点编号

**响应示例**:
```json
[
  {
    "id": 1,
    "point_code": "IP1",
    "value": 12.3456,
    "time": "2024-01-01T08:00:00",
    "device_type": "倒垂线",
    "measurement_type": "左右岸"
  }
]
```

---

### 3. 添加监测数据

手动录入单条监测数据。

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

**字段说明**:
- `point_code` (string, 必填): 测点编号
- `value` (float, 必填): 监测值
- `time` (datetime, 可选): 监测时间，不填则使用当前时间
- `measurement_type` (string, 可选): 测量类型 (左右岸/上下游/沉降/位移/其他)

**响应示例**:
```json
{
  "id": 1,
  "point_code": "IP1",
  "value": 12.3456,
  "time": "2024-01-01T08:00:00",
  "device_type": "倒垂线",
  "measurement_type": "左右岸"
}
```

**错误响应**:
- `404`: 测点不存在

---

### 4. 获取测点详情

获取测点的详细信息，包括最新监测值和数据统计。

**接口**: `GET /points/{point_code}`

**路径参数**:
- `point_code` (string): 测点编号

**响应示例**:
```json
{
  "point_code": "IP1",
  "point_name": "倒垂线1",
  "longitude": 120.123456,
  "latitude": 30.123456,
  "height": 100.5,
  "device_type": "倒垂线",
  "latest_value": 12.3456,
  "latest_time": "2024-01-01T08:00:00",
  "data_count": 100
}
```

**错误响应**:
- `404`: 测点不存在

---

### 5. 获取测点数据统计

获取指定测点的统计数据。

**接口**: `GET /measurements/{point_code}/stats`

**路径参数**:
- `point_code` (string): 测点编号

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

**错误响应**:
- `404`: 测点无数据

---

### 6. 时间范围查询

获取指定测点在时间范围内的监测数据。

**接口**: `GET /measurements/{point_code}/range`

**路径参数**:
- `point_code` (string): 测点编号

**查询参数**:
- `start_time` (datetime, 必填): 开始时间 (ISO 8601格式)
- `end_time` (datetime, 必填): 结束时间 (ISO 8601格式)

**请求示例**:
```
GET /measurements/IP1/range?start_time=2024-01-01T00:00:00&end_time=2024-01-31T23:59:59
```

**响应示例**:
```json
[
  {
    "id": 1,
    "point_code": "IP1",
    "value": 12.3456,
    "time": "2024-01-01T08:00:00",
    "device_type": "倒垂线"
  }
]
```

---

### 7. 批量添加数据

批量录入多条监测数据。

**接口**: `POST /measurements/batch`

**请求体**:
```json
{
  "measurements": [
    {
      "point_code": "IP1",
      "value": 12.3456,
      "time": "2024-01-01T08:00:00",
      "measurement_type": "左右岸"
    },
    {
      "point_code": "IP2",
      "value": 13.4567,
      "time": "2024-01-01T09:00:00",
      "measurement_type": "上下游"
    }
  ]
}
```

**响应示例**:
```json
[
  {
    "id": 1,
    "point_code": "IP1",
    "value": 12.3456,
    "time": "2024-01-01T08:00:00",
    "device_type": "倒垂线",
    "measurement_type": "左右岸"
  },
  {
    "id": 2,
    "point_code": "IP2",
    "value": 13.4567,
    "time": "2024-01-01T09:00:00",
    "device_type": "倒垂线",
    "measurement_type": "上下游"
  }
]
```

---

### 8. 获取所有测点最新数据

获取所有测点的最新监测数据。

**接口**: `GET /measurements/latest`

**请求参数**: 无

**响应示例**:
```json
[
  {
    "point_code": "IP1",
    "point_name": "倒垂线1",
    "value": 12.3456,
    "time": "2024-01-01T08:00:00"
  },
  {
    "point_code": "IP2",
    "point_name": "倒垂线2",
    "value": 13.4567,
    "time": "2024-01-01T08:00:00"
  }
]
```

---

### 9. 获取指定测点最新数据

获取指定测点的最新监测数据。

**接口**: `GET /measurements/{point_code}/latest`

**路径参数**:
- `point_code` (string): 测点编号

**响应示例**:
```json
{
  "point_code": "IP1",
  "point_name": "倒垂线1",
  "value": 12.3456,
  "time": "2024-01-01T08:00:00"
}
```

**错误响应**:
- `404`: 测点无数据

---

### 10. 告警检测

检测测点数据是否超出设定的阈值范围。

**接口**: `POST /alerts/check`

**请求体**:
```json
[
  {
    "point_code": "IP1",
    "min_value": 10.0,
    "max_value": 15.0,
    "alert_enabled": true
  },
  {
    "point_code": "IP2",
    "min_value": 8.0,
    "max_value": 12.0,
    "alert_enabled": true
  }
]
```

**字段说明**:
- `point_code` (string): 测点编号
- `min_value` (float, 可选): 最小阈值
- `max_value` (float, 可选): 最大阈值
- `alert_enabled` (boolean): 是否启用告警

**响应示例**:
```json
[
  {
    "point_code": "IP1",
    "point_name": "倒垂线1",
    "current_value": 16.5,
    "alert_type": "超过上限",
    "threshold": 15.0,
    "time": "2024-01-01T08:00:00"
  }
]
```

---

### 11. 数据对比

对比同一测点在不同时间点的监测数据。

**接口**: `GET /measurements/{point_code}/compare`

**路径参数**:
- `point_code` (string): 测点编号

**查询参数**:
- `current_time` (datetime, 可选): 当前监测时间 (ISO 8601格式)
- `previous_time` (datetime, 可选): 对比监测时间 (ISO 8601格式)

**请求示例**:
```
GET /measurements/IP1/compare?current_time=2024-01-01T08:00:00&previous_time=2024-01-01T00:00:00
```

**响应示例**:
```json
{
  "point_code": "IP1",
  "point_name": "倒垂线1",
  "current_value": 12.3456,
  "previous_value": 11.2345,
  "change_value": 1.1111,
  "change_percent": 9.89,
  "time": "2024-01-01T08:00:00"
}
```

**字段说明**:
- `current_value`: 当前监测值
- `previous_value`: 对比监测值
- `change_value`: 变化值 (当前值 - 对比值)
- `change_percent`: 变化百分比

**错误响应**:
- `404`: 未找到监测数据

---

## 数据模型

### MeasurementCreate

创建监测数据的请求模型。

```typescript
{
  point_code: string;
  value: number;
  time?: string;  // ISO 8601 格式
  measurement_type?: string;  // 左右岸/上下游/沉降/位移/其他
}
```

### MeasurementOut

监测数据的响应模型。

```typescript
{
  id: number;
  point_code: string;
  value: number;
  time: string;
  device_type?: string;
  measurement_type?: string;
}
```

### MonitorPointOut

测点信息的响应模型。

```typescript
{
  point_code: string;
  point_name: string;
  longitude: number;
  latitude: number;
  height: number;
  device_type: string;
}
```

### MonitorPointDetail

测点详情的响应模型。

```typescript
{
  point_code: string;
  point_name: string;
  longitude: number;
  latitude: number;
  height: number;
  device_type: string;
  latest_value?: number;
  latest_time?: string;
  data_count: number;
}
```

### MeasurementStats

监测数据统计的响应模型。

```typescript
{
  point_code: string;
  max_value: number;
  min_value: number;
  avg_value: number;
  count: number;
  latest_time?: string;
  earliest_time?: string;
}
```

### MeasurementBatch

批量添加数据的请求模型。

```typescript
{
  measurements: MeasurementCreate[];
}
```

### MeasurementLatest

最新监测数据的响应模型。

```typescript
{
  point_code: string;
  point_name: string;
  value: number;
  time: string;
}
```

### AlertConfig

告警配置的请求模型。

```typescript
{
  point_code: string;
  min_value?: number;
  max_value?: number;
  alert_enabled: boolean;
}
```

### AlertInfo

告警信息的响应模型。

```typescript
{
  point_code: string;
  point_name: string;
  current_value: number;
  alert_type: string;  // "超过上限" 或 "低于下限"
  threshold: number;
  time: string;
}
```

### MeasurementCompare

数据对比的响应模型。

```typescript
{
  point_code: string;
  point_name: string;
  current_value: number;
  previous_value: number;
  change_value: number;
  change_percent: number;
  time: string;
}
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
| 404 | 资源不存在 (测点不存在/无数据) |
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
2. **数据类型**: 
   - `measurement_type` 支持的值: "左右岸", "上下游", "沉降", "位移", "其他"
   - `device_type` 支持的值: "倒垂线", "引张线", "静力水准"
3. **批量操作**: 批量添加数据时，如果测点不存在，该条数据会被跳过，不会影响其他数据的添加
4. **数据对比**: 如果不指定时间参数，会自动选择最新数据和前一次数据进行对比

---

## 联系方式

如有问题请联系开发团队。
