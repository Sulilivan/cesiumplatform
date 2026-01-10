from sqlalchemy.orm import Session
from typing import List, Optional
from . import models, schemas, auth
from datetime import datetime

def get_user(db: Session, user_id: int) -> Optional[models.User]:
    return db.query(models.User).filter(models.User.id == user_id).first()

def get_user_by_username(db: Session, username: str) -> Optional[models.User]:
    return db.query(models.User).filter(models.User.username == username).first()

def get_user_by_email(db: Session, email: str) -> Optional[models.User]:
    return db.query(models.User).filter(models.User.email == email).first()

def get_users(db: Session, skip: int = 0, limit: int = 100) -> List[models.User]:
    return db.query(models.User).offset(skip).limit(limit).all()

def create_user(db: Session, user: schemas.UserCreate) -> models.User:
    hashed_password = auth.get_password_hash(user.password)
    db_user = models.User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password,
        role=user.role
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def update_user(db: Session, user_id: int, user_update: dict) -> Optional[models.User]:
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if db_user:
        for key, value in user_update.items():
            if key == "password":
                value = auth.get_password_hash(value)
            setattr(db_user, key, value)
        db.commit()
        db.refresh(db_user)
    return db_user

def delete_user(db: Session, user_id: int) -> bool:
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if db_user:
        db.delete(db_user)
        db.commit()
        return True
    return False

def get_points(db: Session, skip: int = 0, limit: int = 100) -> List[models.MonitorPoint]:
    return db.query(models.MonitorPoint).offset(skip).limit(limit).all()

def get_point_by_code(db: Session, point_code: str) -> Optional[models.MonitorPoint]:
    return db.query(models.MonitorPoint).filter(models.MonitorPoint.point_code == point_code).first()

def create_point(db: Session, point: schemas.PointCreate) -> models.MonitorPoint:
    db_point = models.MonitorPoint(**point.model_dump())
    db.add(db_point)
    db.commit()
    db.refresh(db_point)
    return db_point

def get_measurements(db: Session, point_code: str, skip: int = 0, limit: int = 100) -> List[models.Measurement]:
    return db.query(models.Measurement).filter(models.Measurement.point_code == point_code).order_by(models.Measurement.time.desc()).offset(skip).limit(limit).all()

def create_measurement(db: Session, measurement: schemas.MeasurementCreate) -> models.Measurement:
    db_measurement = models.Measurement(**measurement.model_dump())
    db.add(db_measurement)
    db.commit()
    db.refresh(db_measurement)
    return db_measurement

def get_latest_measurement(db: Session, point_code: str) -> Optional[models.Measurement]:
    return db.query(models.Measurement).filter(models.Measurement.point_code == point_code).order_by(models.Measurement.time.desc()).first()

def get_all_latest_measurements(db: Session) -> List[dict]:
    from sqlalchemy import func
    subquery = db.query(
        models.Measurement.point_code,
        func.max(models.Measurement.time).label('max_time')
    ).group_by(models.Measurement.point_code).subquery()
    
    latest = db.query(models.Measurement).join(
        subquery,
        (models.Measurement.point_code == subquery.c.point_code) &
        (models.Measurement.time == subquery.c.max_time)
    ).all()
    
    result = []
    for m in latest:
        point = db.query(models.MonitorPoint).filter(models.MonitorPoint.point_code == m.point_code).first()
        if point:
            result.append({
                'point_code': m.point_code,
                'point_name': point.point_name,
                'value': m.value,
                'time': m.time,
                'device_type': point.device_type
            })
    return result

def get_inverted_plumb_data(db: Session, point_code: str, skip: int = 0, limit: int = 100) -> List[models.InvertedPlumbData]:
    return db.query(models.InvertedPlumbData).filter(
        models.InvertedPlumbData.point_code == point_code
    ).order_by(models.InvertedPlumbData.time.desc()).offset(skip).limit(limit).all()

def create_inverted_plumb_data(db: Session, data: schemas.InvertedPlumbDataCreate) -> models.InvertedPlumbData:
    db_data = models.InvertedPlumbData(
        point_code=data.point_code,
        left_right_value=data.left_right_value,
        up_down_value=data.up_down_value,
        time=data.time or datetime.now()
    )
    db.add(db_data)
    db.commit()
    db.refresh(db_data)
    return db_data

def get_latest_inverted_plumb(db: Session, point_code: str) -> Optional[models.InvertedPlumbData]:
    return db.query(models.InvertedPlumbData).filter(
        models.InvertedPlumbData.point_code == point_code
    ).order_by(models.InvertedPlumbData.time.desc()).first()

def get_static_level_data(db: Session, point_code: str, skip: int = 0, limit: int = 100) -> List[models.StaticLevelData]:
    return db.query(models.StaticLevelData).filter(
        models.StaticLevelData.point_code == point_code
    ).order_by(models.StaticLevelData.time.desc()).offset(skip).limit(limit).all()

def create_static_level_data(db: Session, data: schemas.StaticLevelDataCreate) -> models.StaticLevelData:
    db_data = models.StaticLevelData(
        point_code=data.point_code,
        value=data.value,
        time=data.time or datetime.now()
    )
    db.add(db_data)
    db.commit()
    db.refresh(db_data)
    return db_data

def get_latest_static_level(db: Session, point_code: str) -> Optional[models.StaticLevelData]:
    return db.query(models.StaticLevelData).filter(
        models.StaticLevelData.point_code == point_code
    ).order_by(models.StaticLevelData.time.desc()).first()

def get_tension_line_data(db: Session, point_code: str, skip: int = 0, limit: int = 100) -> List[models.TensionLineData]:
    return db.query(models.TensionLineData).filter(
        models.TensionLineData.point_code == point_code
    ).order_by(models.TensionLineData.time.desc()).offset(skip).limit(limit).all()

def create_tension_line_data(db: Session, data: schemas.TensionLineDataCreate) -> models.TensionLineData:
    db_data = models.TensionLineData(
        point_code=data.point_code,
        value=data.value,
        time=data.time or datetime.now()
    )
    db.add(db_data)
    db.commit()
    db.refresh(db_data)
    return db_data

def get_latest_tension_line(db: Session, point_code: str) -> Optional[models.TensionLineData]:
    return db.query(models.TensionLineData).filter(
        models.TensionLineData.point_code == point_code
    ).order_by(models.TensionLineData.time.desc()).first()

def get_water_level_data(db: Session, point_code: str, skip: int = 0, limit: int = 100) -> List[models.WaterLevelData]:
    return db.query(models.WaterLevelData).filter(
        models.WaterLevelData.point_code == point_code
    ).order_by(models.WaterLevelData.time.desc()).offset(skip).limit(limit).all()

def create_water_level_data(db: Session, data: schemas.WaterLevelDataCreate) -> models.WaterLevelData:
    db_data = models.WaterLevelData(
        point_code=data.point_code,
        value=data.value,
        time=data.time or datetime.now()
    )
    db.add(db_data)
    db.commit()
    db.refresh(db_data)
    return db_data

def get_latest_water_level(db: Session, point_code: str) -> Optional[models.WaterLevelData]:
    return db.query(models.WaterLevelData).filter(
        models.WaterLevelData.point_code == point_code
    ).order_by(models.WaterLevelData.time.desc()).first()
