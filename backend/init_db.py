from sql_app import database, models, crud, schemas, auth

def init_db():
    db = database.SessionLocal()
    try:
        database.Base.metadata.create_all(bind=database.engine)
        print("数据库表创建成功")
        
        admin_user = crud.get_user_by_username(db, username="admin")
        if not admin_user:
            admin_create = schemas.UserCreate(
                username="admin",
                email="admin@example.com",
                password="admin123",
                role="admin"
            )
            admin = crud.create_user(db, admin_create)
            print(f"管理员账号创建成功: {admin.username} (密码: admin123)")
        else:
            print("管理员账号已存在")
        
        test_user = crud.get_user_by_username(db, username="user")
        if not test_user:
            user_create = schemas.UserCreate(
                username="user",
                email="user@example.com",
                password="user123",
                role="user"
            )
            user = crud.create_user(db, user_create)
            print(f"测试用户账号创建成功: {user.username} (密码: user123)")
        else:
            print("测试用户账号已存在")
    finally:
        db.close()

if __name__ == "__main__":
    init_db()
