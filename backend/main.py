from fastapi import FastAPI, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from fastapi.middleware.cors import CORSMiddleware
from sql_app import models, schemas, database, crud, auth
from datetime import datetime, timedelta

# 创建数据库表
models.Base.metadata.create_all(bind=database.engine)

app = FastAPI(title="智慧水利监测平台 API")

# 配置 CORS (允许前端 Vue 访问)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应改为前端具体地址
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
def read_root():
    return {
        "message": "智慧水利监测平台 API",
        "version": "1.0.0",
        "docs": "/docs",
        "endpoints": {
            "points": "/points/",
            "measurements": "/measurements/{point_code}",
            "inverted_plumb": "/inverted-plumb/{point_code}",
            "static_level": "/static-level/{point_code}",
            "tension_line": "/tension-line/{point_code}",
            "water_level": "/water-level/{point_code}",
            "auth": "/auth/login",
            "docs": "/docs"
        }
    }

# 1. 获取所有测点 (用于 Cesium 打点) [cite: 21]
@app.get("/points/", response_model=list[schemas.MonitorPointOut])
def read_points(current_user: models.User = Depends(auth.get_current_active_user), db: Session = Depends(get_db)):
    points = db.query(models.MonitorPoint).all()
    return points

# 2. 获取指定测点的历史数据 (用于 ECharts 折线图) [cite: 20]
@app.get("/measurements/{point_code}", response_model=list[schemas.MeasurementOut])
def read_measurements(point_code: str, current_user: models.User = Depends(auth.get_current_active_user), db: Session = Depends(get_db)):
    data = db.query(models.Measurement).filter(
        models.Measurement.point_code == point_code
    ).order_by(models.Measurement.time).all()
    return data

# 3. 动态添加监测数据 (对应指导书具体任务 [cite: 22])
@app.post("/measurements/", response_model=schemas.MeasurementOut)
def create_measurement(item: schemas.MeasurementCreate, current_user: models.User = Depends(auth.get_current_admin_user), db: Session = Depends(get_db)):
    point = db.query(models.MonitorPoint).filter(models.MonitorPoint.point_code == item.point_code).first()
    if not point:
        raise HTTPException(status_code=404, detail="测点不存在")
    
    db_item = models.Measurement(
        point_code=item.point_code,
        value=item.value,
        time=item.time or datetime.now(),
        measurement_type=item.measurement_type
    )
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

@app.get("/points/{point_code}", response_model=schemas.MonitorPointDetail)
def read_point_detail(point_code: str, current_user: models.User = Depends(auth.get_current_active_user), db: Session = Depends(get_db)):
    point = db.query(models.MonitorPoint).filter(models.MonitorPoint.point_code == point_code).first()
    if not point:
        raise HTTPException(status_code=404, detail="测点不存在")
    
    latest_measurement = db.query(models.Measurement).filter(
        models.Measurement.point_code == point_code
    ).order_by(models.Measurement.time.desc()).first()
    
    data_count = db.query(models.Measurement).filter(
        models.Measurement.point_code == point_code
    ).count()
    
    return schemas.MonitorPointDetail(
        point_code=point.point_code,
        point_name=point.point_name,
        longitude=point.longitude,
        latitude=point.latitude,
        height=point.height,
        device_type=point.device_type,
        latest_value=latest_measurement.value if latest_measurement else None,
        latest_time=latest_measurement.time if latest_measurement else None,
        data_count=data_count
    )







@app.get("/measurements/{point_code}/stats", response_model=schemas.MeasurementStats)
def get_measurement_stats(point_code: str, current_user: models.User = Depends(auth.get_current_active_user), db: Session = Depends(get_db)):
    stats = db.query(
        func.max(models.Measurement.value).label('max_value'),
        func.min(models.Measurement.value).label('min_value'),
        func.avg(models.Measurement.value).label('avg_value'),
        func.count(models.Measurement.id).label('count'),
        func.max(models.Measurement.time).label('latest_time'),
        func.min(models.Measurement.time).label('earliest_time')
    ).filter(models.Measurement.point_code == point_code).first()
    
    if not stats or stats.count == 0:
        raise HTTPException(status_code=404, detail="测点无数据")
    
    return schemas.MeasurementStats(
        point_code=point_code,
        max_value=stats.max_value,
        min_value=stats.min_value,
        avg_value=stats.avg_value,
        count=stats.count,
        latest_time=stats.latest_time,
        earliest_time=stats.earliest_time
    )

@app.get("/measurements/{point_code}/range", response_model=list[schemas.MeasurementOut])
def get_measurements_by_range(
    point_code: str,
    start_time: datetime = Query(..., description="开始时间"),
    end_time: datetime = Query(..., description="结束时间"),
    current_user: models.User = Depends(auth.get_current_active_user),
    db: Session = Depends(get_db)
):
    point = db.query(models.MonitorPoint).filter(
        models.MonitorPoint.point_code == point_code
    ).first()
    
    device_type = point.device_type if point else None
    
    data = db.query(models.Measurement).filter(
        models.Measurement.point_code == point_code,
        models.Measurement.time >= start_time,
        models.Measurement.time <= end_time
    ).order_by(models.Measurement.time).all()
    
    result = []
    for item in data:
        result.append(schemas.MeasurementOut(
            id=item.id,
            point_code=item.point_code,
            value=item.value,
            time=item.time,
            device_type=device_type
        ))
    
    return result

@app.post("/measurements/batch", response_model=list[schemas.MeasurementOut])
def create_measurements_batch(batch: schemas.MeasurementBatch, current_user: models.User = Depends(auth.get_current_admin_user), db: Session = Depends(get_db)):
    result = []
    for item in batch.measurements:
        point = db.query(models.MonitorPoint).filter(
            models.MonitorPoint.point_code == item.point_code
        ).first()
        if not point:
            continue
        
        db_item = models.Measurement(
            point_code=item.point_code,
            value=item.value,
            time=item.time or datetime.now(),
            measurement_type=item.measurement_type
        )
        db.add(db_item)
        result.append(db_item)
    
    db.commit()
    for item in result:
        db.refresh(item)
    
    return result

@app.get("/measurements/latest", response_model=list[schemas.MeasurementLatest])
def get_all_latest_measurements(current_user: models.User = Depends(auth.get_current_active_user), db: Session = Depends(get_db)):
    subquery = db.query(
        models.Measurement.point_code,
        func.max(models.Measurement.time).label('max_time')
    ).group_by(models.Measurement.point_code).subquery()
    
    latest_data = db.query(models.Measurement).join(
        subquery,
        (models.Measurement.point_code == subquery.c.point_code) &
        (models.Measurement.time == subquery.c.max_time)
    ).all()
    
    result = []
    for measurement in latest_data:
        point = db.query(models.MonitorPoint).filter(
            models.MonitorPoint.point_code == measurement.point_code
        ).first()
        result.append(schemas.MeasurementLatest(
            point_code=measurement.point_code,
            point_name=point.point_name if point else measurement.point_code,
            value=measurement.value,
            time=measurement.time
        ))
    
    return result

@app.get("/measurements/{point_code}/latest", response_model=schemas.MeasurementLatest)
def get_latest_measurement(point_code: str, current_user: models.User = Depends(auth.get_current_active_user), db: Session = Depends(get_db)):
    measurement = db.query(models.Measurement).filter(
        models.Measurement.point_code == point_code
    ).order_by(models.Measurement.time.desc()).first()
    
    if not measurement:
        raise HTTPException(status_code=404, detail="测点无数据")
    
    point = db.query(models.MonitorPoint).filter(
        models.MonitorPoint.point_code == point_code
    ).first()
    
    return schemas.MeasurementLatest(
        point_code=measurement.point_code,
        point_name=point.point_name if point else measurement.point_code,
        value=measurement.value,
        time=measurement.time
    )

@app.post("/alerts/check", response_model=list[schemas.AlertInfo])
def check_alerts(configs: list[schemas.AlertConfig], db: Session = Depends(get_db)):
    alerts = []
    
    for config in configs:
        if not config.alert_enabled:
            continue
        
        latest = db.query(models.Measurement).filter(
            models.Measurement.point_code == config.point_code
        ).order_by(models.Measurement.time.desc()).first()
        
        if not latest:
            continue
        
        point = db.query(models.MonitorPoint).filter(
            models.MonitorPoint.point_code == config.point_code
        ).first()
        
        if config.max_value is not None and latest.value > config.max_value:
            alerts.append(schemas.AlertInfo(
                point_code=config.point_code,
                point_name=point.point_name if point else config.point_code,
                current_value=latest.value,
                alert_type="超过上限",
                threshold=config.max_value,
                time=latest.time
            ))
        
        if config.min_value is not None and latest.value < config.min_value:
            alerts.append(schemas.AlertInfo(
                point_code=config.point_code,
                point_name=point.point_name if point else config.point_code,
                current_value=latest.value,
                alert_type="低于下限",
                threshold=config.min_value,
                time=latest.time
            ))
    
    return alerts

@app.get("/measurements/{point_code}/compare", response_model=schemas.MeasurementCompare)
def compare_measurements(
    point_code: str, 
    current_time: datetime = Query(None, description="当前监测时间"),
    previous_time: datetime = Query(None, description="对比监测时间"),
    current_user: models.User = Depends(auth.get_current_active_user),
    db: Session = Depends(get_db)
):
    query = db.query(models.Measurement).filter(
        models.Measurement.point_code == point_code
    )
    
    if current_time:
        current = query.filter(models.Measurement.time <= current_time).order_by(
            models.Measurement.time.desc()
        ).first()
    else:
        current = query.order_by(models.Measurement.time.desc()).first()
    
    if not current:
        raise HTTPException(status_code=404, detail="未找到当前监测数据")
    
    if previous_time:
        previous = query.filter(models.Measurement.time <= previous_time).order_by(
            models.Measurement.time.desc()
        ).first()
    else:
        previous = query.filter(models.Measurement.time < current.time).order_by(
            models.Measurement.time.desc()
        ).first()
    
    if not previous:
        raise HTTPException(status_code=404, detail="未找到对比监测数据")
    
    change_value = current.value - previous.value
    change_percent = (change_value / previous.value * 100) if previous.value != 0 else 0
    
    point = db.query(models.MonitorPoint).filter(
        models.MonitorPoint.point_code == point_code
    ).first()
    
    return schemas.MeasurementCompare(
        point_code=point_code,
        point_name=point.point_name if point else point_code,
        current_value=current.value,
        previous_value=previous.value,
        change_value=change_value,
        change_percent=change_percent,
        time=current.time
    )

@app.post("/auth/register", response_model=schemas.UserResponse)
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_username(db, username=user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="用户名已存在")
    
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="邮箱已被注册")
    
    return crud.create_user(db=db, user=user)

@app.post("/auth/login", response_model=schemas.Token)
def login(user_credentials: schemas.UserLogin, db: Session = Depends(get_db)):
    user = auth.authenticate_user(db, user_credentials.username, user_credentials.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth.create_access_token(
        data={"sub": user.username, "role": user.role}, expires_delta=access_token_expires
    )
    return schemas.Token(
        access_token=access_token,
        token_type="bearer",
        user=schemas.UserResponse(
            id=user.id,
            username=user.username,
            email=user.email,
            role=user.role,
            is_active=user.is_active,
            created_at=user.created_at
        )
    )

@app.get("/auth/me", response_model=schemas.UserResponse)
def read_users_me(current_user: models.User = Depends(auth.get_current_active_user)):
    return schemas.UserResponse(
        id=current_user.id,
        username=current_user.username,
        email=current_user.email,
        role=current_user.role,
        is_active=current_user.is_active,
        created_at=current_user.created_at
    )

@app.get("/auth/users", response_model=list[schemas.UserResponse])
def read_users(
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(auth.get_current_admin_user),
    db: Session = Depends(get_db)
):
    users = crud.get_users(db, skip=skip, limit=limit)
    return [
        schemas.UserResponse(
            id=user.id,
            username=user.username,
            email=user.email,
            role=user.role,
            is_active=user.is_active,
            created_at=user.created_at
        )
        for user in users
    ]

@app.put("/auth/users/{user_id}", response_model=schemas.UserResponse)
def update_user(
    user_id: int,
    user_update: dict,
    current_user: models.User = Depends(auth.get_current_admin_user),
    db: Session = Depends(get_db)
):
    db_user = crud.update_user(db, user_id=user_id, user_update=user_update)
    if db_user is None:
        raise HTTPException(status_code=404, detail="用户不存在")
    return schemas.UserResponse(
        id=db_user.id,
        username=db_user.username,
        email=db_user.email,
        role=db_user.role,
        is_active=db_user.is_active,
        created_at=db_user.created_at
    )

@app.delete("/auth/users/{user_id}")
def delete_user(
    user_id: int,
    current_user: models.User = Depends(auth.get_current_admin_user),
    db: Session = Depends(get_db)
):
    success = crud.delete_user(db, user_id=user_id)
    if not success:
        raise HTTPException(status_code=404, detail="用户不存在")
    return {"message": "用户删除成功"}

@app.post("/auth/users", response_model=schemas.UserResponse)
def create_user(
    user: schemas.UserCreate,
    current_user: models.User = Depends(auth.get_current_admin_user),
    db: Session = Depends(get_db)
):
    db_user = crud.get_user_by_username(db, username=user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="用户名已存在")
    return crud.create_user(db=db, user=user)

@app.post("/points/", response_model=schemas.MonitorPointOut)
def create_point(
    point: schemas.PointCreate,
    current_user: models.User = Depends(auth.get_current_admin_user),
    db: Session = Depends(get_db)
):
    db_point = crud.get_point_by_code(db, point_code=point.point_code)
    if db_point:
        raise HTTPException(status_code=400, detail="测点编号已存在")
    return crud.create_point(db=db, point=point)

@app.put("/points/{point_code}", response_model=schemas.MonitorPointOut)
def update_point(
    point_code: str,
    point_update: schemas.PointUpdate,
    current_user: models.User = Depends(auth.get_current_admin_user),
    db: Session = Depends(get_db)
):
    # 简单的验证，如果包含bind_model_id，也允许修改
    db_point = crud.update_point(db, point_code=point_code, point_update=point_update.model_dump(exclude_unset=True))
    if not db_point:
        raise HTTPException(status_code=404, detail="测点不存在")
    return db_point

@app.delete("/points/{point_code}")
def delete_point(
    point_code: str,
    current_user: models.User = Depends(auth.get_current_admin_user),
    db: Session = Depends(get_db)
):
    success = crud.delete_point(db, point_code=point_code)
    if not success:
        raise HTTPException(status_code=404, detail="测点不存在")
    return {"message": "测点删除成功"}

@app.get("/inverted-plumb/{point_code}", response_model=list[schemas.InvertedPlumbDataOut])
def read_inverted_plumb_data(
    point_code: str,
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(auth.get_current_active_user),
    db: Session = Depends(get_db)
):
    return crud.get_inverted_plumb_data(db, point_code, skip, limit)

@app.post("/inverted-plumb/", response_model=schemas.InvertedPlumbDataOut)
def create_inverted_plumb_data(
    data: schemas.InvertedPlumbDataCreate,
    current_user: models.User = Depends(auth.get_current_admin_user),
    db: Session = Depends(get_db)
):
    point = db.query(models.MonitorPoint).filter(models.MonitorPoint.point_code == data.point_code).first()
    if not point:
        raise HTTPException(status_code=404, detail="测点不存在")
    return crud.create_inverted_plumb_data(db, data)

@app.get("/inverted-plumb/{point_code}/latest", response_model=schemas.InvertedPlumbDataOut)
def read_latest_inverted_plumb(
    point_code: str,
    current_user: models.User = Depends(auth.get_current_active_user),
    db: Session = Depends(get_db)
):
    data = crud.get_latest_inverted_plumb(db, point_code)
    if not data:
        raise HTTPException(status_code=404, detail="测点无数据")
    return data

@app.get("/static-level/{point_code}", response_model=list[schemas.StaticLevelDataOut])
def read_static_level_data(
    point_code: str,
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(auth.get_current_active_user),
    db: Session = Depends(get_db)
):
    return crud.get_static_level_data(db, point_code, skip, limit)

@app.post("/static-level/", response_model=schemas.StaticLevelDataOut)
def create_static_level_data(
    data: schemas.StaticLevelDataCreate,
    current_user: models.User = Depends(auth.get_current_admin_user),
    db: Session = Depends(get_db)
):
    point = db.query(models.MonitorPoint).filter(models.MonitorPoint.point_code == data.point_code).first()
    if not point:
        raise HTTPException(status_code=404, detail="测点不存在")
    return crud.create_static_level_data(db, data)

@app.get("/static-level/{point_code}/latest", response_model=schemas.StaticLevelDataOut)
def read_latest_static_level(
    point_code: str,
    current_user: models.User = Depends(auth.get_current_active_user),
    db: Session = Depends(get_db)
):
    data = crud.get_latest_static_level(db, point_code)
    if not data:
        raise HTTPException(status_code=404, detail="测点无数据")
    return data

@app.get("/tension-line/{point_code}", response_model=list[schemas.TensionLineDataOut])
def read_tension_line_data(
    point_code: str,
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(auth.get_current_active_user),
    db: Session = Depends(get_db)
):
    return crud.get_tension_line_data(db, point_code, skip, limit)

@app.post("/tension-line/", response_model=schemas.TensionLineDataOut)
def create_tension_line_data(
    data: schemas.TensionLineDataCreate,
    current_user: models.User = Depends(auth.get_current_admin_user),
    db: Session = Depends(get_db)
):
    point = db.query(models.MonitorPoint).filter(models.MonitorPoint.point_code == data.point_code).first()
    if not point:
        raise HTTPException(status_code=404, detail="测点不存在")
    return crud.create_tension_line_data(db, data)

@app.get("/tension-line/{point_code}/latest", response_model=schemas.TensionLineDataOut)
def read_latest_tension_line(
    point_code: str,
    current_user: models.User = Depends(auth.get_current_active_user),
    db: Session = Depends(get_db)
):
    data = crud.get_latest_tension_line(db, point_code)
    if not data:
        raise HTTPException(status_code=404, detail="测点无数据")
    return data

@app.get("/water-level/{point_code}", response_model=list[schemas.WaterLevelDataOut])
def read_water_level_data(
    point_code: str,
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(auth.get_current_active_user),
    db: Session = Depends(get_db)
):
    return crud.get_water_level_data(db, point_code, skip, limit)

@app.post("/water-level/", response_model=schemas.WaterLevelDataOut)
def create_water_level_data(
    data: schemas.WaterLevelDataCreate,
    current_user: models.User = Depends(auth.get_current_admin_user),
    db: Session = Depends(get_db)
):
    point = db.query(models.MonitorPoint).filter(models.MonitorPoint.point_code == data.point_code).first()
    if not point:
        raise HTTPException(status_code=404, detail="测点不存在")
    return crud.create_water_level_data(db, data)

@app.get("/water-level/{point_code}/latest", response_model=schemas.WaterLevelDataOut)
def read_latest_water_level(
    point_code: str,
    current_user: models.User = Depends(auth.get_current_active_user),
    db: Session = Depends(get_db)
):
    data = crud.get_latest_water_level(db, point_code)
    if not data:
        raise HTTPException(status_code=404, detail="测点无数据")
    return data