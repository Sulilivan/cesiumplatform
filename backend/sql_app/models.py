from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from .database import Base
from datetime import datetime

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, comment="用户名")
    email = Column(String, unique=True, index=True, comment="邮箱")
    hashed_password = Column(String, comment="加密后的密码")
    role = Column(String, default="user", comment="角色: admin 或 user")
    is_active = Column(Boolean, default=True, comment="是否激活")
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")

class MonitorPoint(Base):
    """测点表：存储位置信息，用于 Cesium 展示"""
    __tablename__ = "monitor_points"

    id = Column(Integer, primary_key=True, index=True)
    point_code = Column(String, unique=True, index=True, comment="测点编号 EX1")
    point_name = Column(String, comment="测点名称")
    device_type = Column(String, comment="仪器类型")
    longitude = Column(Float, comment="经度")
    latitude = Column(Float, comment="纬度")
    height = Column(Float, comment="高程")

    measurements = relationship("Measurement", back_populates="point")

class Measurement(Base):
    """监测数据表：存储时序数据，用于 ECharts 展示"""
    __tablename__ = "measurements"

    id = Column(Integer, primary_key=True, index=True)
    point_code = Column(String, ForeignKey("monitor_points.point_code"))
    value = Column(Float, comment="监测值")
    time = Column(DateTime, default=datetime.now, comment="监测时间")
    measurement_type = Column(String, comment="测量类型（左右岸/上下游/沉降等）")
    
    point = relationship("MonitorPoint", back_populates="measurements")