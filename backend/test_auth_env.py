from passlib.context import CryptContext
from jose import jwt
from datetime import datetime, timedelta

# Test Passlib
try:
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    hash_val = pwd_context.hash("test")
    print(f"Hash success: {hash_val[:10]}...")
    verify = pwd_context.verify("test", hash_val)
    print(f"Verify success: {verify}")
except Exception as e:
    print(f"Passlib Error: {e}")

# Test JWT
try:
    secret = "secret"
    algo = "HS256"
    data = {"sub": "test"}
    token = jwt.encode(data, secret, algorithm=algo)
    print(f"JWT Encode success: {token[:10]}...")
    decoded = jwt.decode(token, secret, algorithms=[algo])
    print(f"JWT Decode success: {decoded}")
except Exception as e:
    print(f"JWT Error: {e}")
