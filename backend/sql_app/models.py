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
    device_type = Column(String, comment="仪器类型：倒垂线/静力水准/引张线/水位")
    longitude = Column(Float, comment="经度")
    latitude = Column(Float, comment="纬度")
    height = Column(Float, comment="高程")

    measurements = relationship("Measurement", back_populates="point")
    inverted_plumb_data = relationship("InvertedPlumbData", back_populates="point")
    static_level_data = relationship("StaticLevelData", back_populates="point")
    tension_line_data = relationship("TensionLineData", back_populates="point")
    water_level_data = relationship("WaterLevelData", back_populates="point")

class Measurement(Base):
    """监测数据表：存储时序数据，用于 ECharts 展示（保留向后兼容）"""
    __tablename__ = "measurements"

    id = Column(Integer, primary_key=True, index=True)
    point_code = Column(String, ForeignKey("monitor_points.point_code"))
    value = Column(Float, comment="监测值")
    time = Column(DateTime, default=datetime.now, comment="监测时间")
    measurement_type = Column(String, comment="测量类型（左右岸/上下游/沉降等）")
    
    point = relationship("MonitorPoint", back_populates="measurements")

class InvertedPlumbData(Base):
    """倒垂线数据表"""
    __tablename__ = "inverted_plumb_data"

    id = Column(Integer, primary_key=True, index=True)
    point_code = Column(String, ForeignKey("monitor_points.point_code"), index=True, comment="测点编号")
    left_right_value = Column(Float, comment="左右岸值")
    up_down_value = Column(Float, comment="上下游值")
    time = Column(DateTime, default=datetime.now, comment="监测时间")
    
    point = relationship("MonitorPoint", back_populates="inverted_plumb_data")

class StaticLevelData(Base):
    """静力水准数据表"""
    __tablename__ = "static_level_data"

    id = Column(Integer, primary_key=True, index=True)
    point_code = Column(String, ForeignKey("monitor_points.point_code"), index=True, comment="测点编号")
    value = Column(Float, comment="沉降值")
    time = Column(DateTime, default=datetime.now, comment="监测时间")
    
    point = relationship("MonitorPoint", back_populates="static_level_data")

class TensionLineData(Base):
    """引张线数据表"""
    __tablename__ = "tension_line_data"

    id = Column(Integer, primary_key=True, index=True)
    point_code = Column(String, ForeignKey("monitor_points.point_code"), index=True, comment="测点编号")
    value = Column(Float, comment="位移值")
    time = Column(DateTime, default=datetime.now, comment="监测时间")
    
    point = relationship("MonitorPoint", back_populates="tension_line_data")

class WaterLevelData(Base):
    """水位数据表"""
    __tablename__ = "water_level_data"

    id = Column(Integer, primary_key=True, index=True)
    point_code = Column(String, ForeignKey("monitor_points.point_code"), index=True, comment="测点编号")
    value = Column(Float, comment="水位值")
    time = Column(DateTime, default=datetime.now, comment="监测时间")
    
    point = relationship("MonitorPoint", back_populates="water_level_data")