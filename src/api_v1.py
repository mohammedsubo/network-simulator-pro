"""
API v1 with JWT Authentication
Quick implementation for production readiness
"""

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime, timedelta
from typing import Optional
import jwt
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Security
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Security scheme
security = HTTPBearer()

# Models
class UserLogin(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class User(BaseModel):
    username: str
    role: str = "viewer"  # admin, viewer

# Simple user database (replace with real DB)
USERS_DB = {
    "admin": {"password": "admin123", "role": "admin"},
    "demo": {"password": "demo123", "role": "viewer"}
}

# Create API v1 router
from fastapi import APIRouter
api_v1 = APIRouter(prefix="/api/v1")

# JWT Functions
def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials"
            )
        return {"username": username, "role": payload.get("role")}
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired"
        )
    except jwt.JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )

def require_admin(user: dict = Depends(verify_token)):
    if user["role"] != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return user

# Auth Endpoints
@api_v1.post("/auth/login", response_model=Token)
async def login(user_login: UserLogin):
    """Login to get access token"""
    user = USERS_DB.get(user_login.username)
    if not user or user["password"] != user_login.password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password"
        )
    
    access_token = create_access_token(
        data={"sub": user_login.username, "role": user["role"]}
    )
    return {"access_token": access_token}

@api_v1.get("/auth/me")
async def get_current_user(user: dict = Depends(verify_token)):
    """Get current user info"""
    return user

# Protected Endpoints (from original API)
@api_v1.get("/status")
async def get_status(user: dict = Depends(verify_token)):
    """Get simulator status (protected)"""
    # Original get_status code here
    return {
        "status": "running",
        "user": user["username"],
        "role": user["role"]
    }

@api_v1.post("/devices")
async def add_devices(request: dict, user: dict = Depends(verify_token)):
    """Add devices (protected)"""
    # Original add_devices code
    return {"message": f"Devices added by {user['username']}"}

@api_v1.delete("/devices/{device_id}")
async def remove_device(device_id: str, user: dict = Depends(require_admin)):
    """Remove device (admin only)"""
    return {"message": f"Device {device_id} removed by admin {user['username']}"}

@api_v1.post("/reset")
async def reset_simulation(user: dict = Depends(require_admin)):
    """Reset simulation (admin only)"""
    return {"message": "Simulation reset by admin"}

# Public Endpoints
@api_v1.get("/health")
async def health_check():
    """Health check (public)"""
    return {"status": "healthy", "version": "v1"}

# Rate Limiting
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)

# Apply rate limiting to login
@api_v1.post("/auth/login-limited")
@limiter.limit("5/minute")
async def login_with_rate_limit(request, user_login: UserLogin):
    return await login(user_login)

# Main App
app = FastAPI(
    title="5G Network Simulator API",
    version="1.0.0",
    docs_url="/api/v1/docs",
    redoc_url="/api/v1/redoc"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount API v1
app.include_router(api_v1)

# Add rate limit error handler
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Redirect root to docs
@app.get("/")
async def root():
    return {"message": "API v1 available at /api/v1", "docs": "/api/v1/docs"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)