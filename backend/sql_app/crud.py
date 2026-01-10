from sqlalchemy.orm import Session
from typing import List, Optional
from . import models, schemas, auth

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
