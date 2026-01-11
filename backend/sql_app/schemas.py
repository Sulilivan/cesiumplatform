from pydantic import BaseModel, Field, EmailStr
import datetime
from typing import List, Optional

class UserBase(BaseModel):
    username: str
    email: EmailStr

class UserCreate(UserBase):
    password: str
    role: Optional[str] = "user"

class PointCreate(BaseModel):
    point_code: str
    point_name: str
    device_type: str
    longitude: float
    latitude: float
    height: float
    bind_model_id: Optional[str] = None

class PointUpdate(BaseModel):
    point_name: Optional[str] = None
    device_type: Optional[str] = None
    longitude: Optional[float] = None
    latitude: Optional[float] = None
    height: Optional[float] = None
    bind_model_id: Optional[str] = None

class UserLogin(BaseModel):
    username: str
    password: str

class UserResponse(UserBase):
    id: int
    role: str
    is_active: bool
    created_at: datetime.datetime
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse

class TokenData(BaseModel):
    username: Optional[str] = None
    role: Optional[str] = None

class MeasurementCreate(BaseModel):
    point_code: str
    value: float
    time: Optional[datetime.datetime] = None
    measurement_type: Optional[str] = None 

class MeasurementUpdate(BaseModel):
    value: Optional[float] = None
    time: Optional[datetime.datetime] = None
    measurement_type: Optional[str] = None

class MeasurementOut(MeasurementCreate):
    id: int
    time: datetime.datetime
    device_type: Optional[str] = None
    measurement_type: Optional[str] = None
    class Config:
        from_attributes = True

class MeasurementSearchOut(MeasurementOut):
    point_name: Optional[str] = None

class MonitorPointOut(BaseModel):
    point_code: str
    point_name: str
    longitude: float
    latitude: float
    height: float
    device_type: str
    bind_model_id: Optional[str] = None
    class Config:
        from_attributes = True

class MonitorPointDetail(MonitorPointOut):
    latest_value: Optional[float] = None
    latest_time: Optional[datetime.datetime] = None
    data_count: int = 0

class MeasurementStats(BaseModel):
    point_code: str
    max_value: float
    min_value: float
    avg_value: float
    count: int
    latest_time: Optional[datetime.datetime] = None
    earliest_time: Optional[datetime.datetime] = None

class MeasurementBatch(BaseModel):
    measurements: List[MeasurementCreate]

class MeasurementLatest(BaseModel):
    point_code: str
    point_name: str
    value: float
    time: datetime.datetime

class AlertConfig(BaseModel):
    point_code: str
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    alert_enabled: bool = True

class AlertInfo(BaseModel):
    point_code: str
    point_name: str
    current_value: float
    alert_type: str
    threshold: float
    time: datetime.datetime

class MeasurementCompare(BaseModel):
    point_code: str
    point_name: str
    current_value: float
    previous_value: float
    change_value: float
    change_percent: float
    time: datetime.datetime

class InvertedPlumbDataCreate(BaseModel):
    point_code: str
    left_right_value: float
    up_down_value: float
    time: Optional[datetime.datetime] = None

class InvertedPlumbDataOut(BaseModel):
    id: int
    point_code: str
    left_right_value: float
    up_down_value: float
    time: datetime.datetime
    class Config:
        from_attributes = True

class StaticLevelDataCreate(BaseModel):
    point_code: str
    value: float
    time: Optional[datetime.datetime] = None

class StaticLevelDataOut(BaseModel):
    id: int
    point_code: str
    value: float
    time: datetime.datetime
    class Config:
        from_attributes = True

class TensionLineDataCreate(BaseModel):
    point_code: str
    value: float
    time: Optional[datetime.datetime] = None

class TensionLineDataOut(BaseModel):
    id: int
    point_code: str
    value: float
    time: datetime.datetime
    class Config:
        from_attributes = True

class WaterLevelDataCreate(BaseModel):
    point_code: str
    value: float
    time: Optional[datetime.datetime] = None

class WaterLevelDataOut(BaseModel):
    id: int
    point_code: str
    value: float
    time: datetime.datetime
    class Config:
        from_attributes = True