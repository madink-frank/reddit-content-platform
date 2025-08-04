"""
Phase 4: 기본 인증 시스템
- JWT 토큰 생성/검증
- 보호된 엔드포인트
- 토큰 검증 미들웨어
"""

import os
import jwt
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from datetime import datetime, timedelta
from typing import Optional
import asyncio
from pydantic import BaseModel

# 기본 설정 클래스
class Settings:
    PROJECT_NAME: str = os.getenv("PROJECT_NAME", "Reddit Content Platform")
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "production")
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"
    
    # 데이터베이스 설정
    SUPABASE_URL: str = os.getenv("SUPABASE_URL", "")
    SUPABASE_KEY: str = os.getenv("SUPABASE_KEY", "")
    
    # Reddit API 설정 (Phase 6에서 사용 예정)
    REDDIT_CLIENT_ID: str = os.getenv("REDDIT_CLIENT_ID", "")
    REDDIT_CLIENT_SECRET: str = os.getenv("REDDIT_CLIENT_SECRET", "")
    
    # JWT 설정
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "dev-secret-key-phase4")
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_HOURS: int = 24

settings = Settings()

# Pydantic 모델
class LoginRequest(BaseModel):
    username: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    expires_in: int

# JWT 인증 클래스
class JWTAuth:
    def __init__(self):
        self.secret_key = settings.JWT_SECRET_KEY
        self.algorithm = settings.JWT_ALGORITHM
        self.expiration_hours = settings.JWT_EXPIRATION_HOURS
        
    def create_token(self, user_data: dict) -> str:
        """JWT 토큰 생성"""
        payload = {
            "user_id": user_data.get("user_id"),
            "username": user_data.get("username"),
            "exp": datetime.utcnow() + timedelta(hours=self.expiration_hours),
            "iat": datetime.utcnow(),
            "iss": "reddit-content-platform"
        }
        
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
    
    def verify_token(self, token: str) -> dict:
        """JWT 토큰 검증"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
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
    
    def authenticate_user(self, username: str, password: str) -> Optional[dict]:
        """사용자 인증 (시뮬레이션)"""
        # 실제 환경에서는 데이터베이스에서 사용자 정보를 확인
        demo_users = {
            "admin": "admin123",
            "user": "user123",
            "demo": "demo123"
        }
        
        if username in demo_users and demo_users[username] == password:
            return {
                "user_id": f"user_{username}",
                "username": username,
                "role": "admin" if username == "admin" else "user"
            }
        return None

# 데이터베이스 연결 클래스 (Phase 3에서 가져옴)
class DatabaseConnection:
    def __init__(self):
        self.supabase_url = settings.SUPABASE_URL
        self.supabase_key = settings.SUPABASE_KEY
        self.is_connected = False
        
    async def test_connection(self):
        """데이터베이스 연결 테스트 (시뮬레이션)"""
        try:
            if self.supabase_url and self.supabase_key:
                await asyncio.sleep(0.1)
                self.is_connected = True
                return {
                    "status": "connected",
                    "url": self.supabase_url[:50] + "..." if len(self.supabase_url) > 50 else self.supabase_url,
                    "timestamp": datetime.utcnow().isoformat()
                }
            else:
                return {
                    "status": "not_configured",
                    "message": "SUPABASE_URL or SUPABASE_KEY not set",
                    "timestamp": datetime.utcnow().isoformat()
                }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    def get_connection_info(self):
        """연결 정보 반환"""
        return {
            "configured": bool(self.supabase_url and self.supabase_key),
            "connected": self.is_connected,
            "url_configured": bool(self.supabase_url),
            "key_configured": bool(self.supabase_key)
        }

# 인스턴스 생성
db = DatabaseConnection()
jwt_auth = JWTAuth()
security = HTTPBearer()

# FastAPI 앱 생성
app = FastAPI(
    title=f"{settings.PROJECT_NAME} - Phase 4",
    version="4.0.0",
    description="Phase 4: JWT Authentication and protected endpoints",
    debug=settings.DEBUG
)

# 의존성: 현재 사용자 가져오기
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """토큰에서 현재 사용자 정보 추출"""
    token = credentials.credentials
    payload = jwt_auth.verify_token(token)
    return payload

@app.get("/")
async def root():
    """Phase 4 - 기본 루트 엔드포인트"""
    return {
        "message": "🚀 Phase 4 배포 성공!",
        "status": "working",
        "phase": "4 - JWT Authentication",
        "timestamp": datetime.utcnow().isoformat(),
        "environment": settings.ENVIRONMENT,
        "features": {
            "database_configured": db.get_connection_info()["configured"],
            "jwt_configured": bool(settings.JWT_SECRET_KEY != "dev-secret-key"),
            "authentication": "enabled"
        },
        "next_phase": "키워드 관리 API"
    }

@app.get("/health")
async def health():
    """Phase 4 - 헬스체크 (인증 시스템 포함)"""
    db_info = db.get_connection_info()
    
    return {
        "status": "healthy",
        "phase": "4",
        "timestamp": datetime.utcnow().isoformat(),
        "deployment": "vercel-serverless",
        "environment": settings.ENVIRONMENT,
        "database": db_info,
        "authentication": {
            "jwt_configured": bool(settings.JWT_SECRET_KEY),
            "algorithm": settings.JWT_ALGORITHM,
            "token_expiration_hours": settings.JWT_EXPIRATION_HOURS
        }
    }

@app.post("/auth/login", response_model=TokenResponse)
async def login(login_data: LoginRequest):
    """사용자 로그인 및 토큰 발급"""
    user = jwt_auth.authenticate_user(login_data.username, login_data.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password"
        )
    
    token = jwt_auth.create_token(user)
    
    return TokenResponse(
        access_token=token,
        token_type="bearer",
        expires_in=settings.JWT_EXPIRATION_HOURS * 3600
    )

@app.get("/auth/me")
async def get_current_user_info(current_user: dict = Depends(get_current_user)):
    """현재 로그인한 사용자 정보"""
    return {
        "user_id": current_user.get("user_id"),
        "username": current_user.get("username"),
        "token_issued_at": datetime.fromtimestamp(current_user.get("iat")).isoformat(),
        "token_expires_at": datetime.fromtimestamp(current_user.get("exp")).isoformat(),
        "issuer": current_user.get("iss")
    }

@app.get("/auth/protected")
async def protected_endpoint(current_user: dict = Depends(get_current_user)):
    """보호된 엔드포인트 예제"""
    return {
        "message": f"Hello {current_user.get('username')}! This is a protected endpoint.",
        "user_id": current_user.get("user_id"),
        "access_time": datetime.utcnow().isoformat(),
        "phase": "4"
    }

@app.get("/auth/demo-users")
async def get_demo_users():
    """데모 사용자 목록 (개발용)"""
    return {
        "demo_users": [
            {"username": "admin", "password": "admin123", "role": "admin"},
            {"username": "user", "password": "user123", "role": "user"},
            {"username": "demo", "password": "demo123", "role": "user"}
        ],
        "note": "Use these credentials to test the authentication system",
        "login_endpoint": "/auth/login"
    }

# Phase 3 엔드포인트들 (데이터베이스)
@app.get("/db/test")
async def test_database():
    """데이터베이스 연결 테스트"""
    result = await db.test_connection()
    
    if result["status"] == "error":
        raise HTTPException(status_code=500, detail=result)
    elif result["status"] == "not_configured":
        raise HTTPException(status_code=503, detail=result)
    
    return result

@app.get("/db/status")
async def database_status():
    """데이터베이스 상태 확인"""
    return {
        "phase": 4,
        "database_info": db.get_connection_info(),
        "environment_variables": {
            "SUPABASE_URL": "✅ Set" if settings.SUPABASE_URL else "❌ Not set",
            "SUPABASE_KEY": "✅ Set" if settings.SUPABASE_KEY else "❌ Not set"
        },
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/config")
async def config_status():
    """Phase 4 - 설정 상태 확인 (인증 포함)"""
    return {
        "phase": 4,
        "project_name": settings.PROJECT_NAME,
        "environment": settings.ENVIRONMENT,
        "debug": settings.DEBUG,
        "configurations": {
            "supabase_configured": bool(settings.SUPABASE_URL and settings.SUPABASE_KEY),
            "reddit_api_configured": bool(settings.REDDIT_CLIENT_ID and settings.REDDIT_CLIENT_SECRET),
            "jwt_configured": bool(settings.JWT_SECRET_KEY != "dev-secret-key")
        },
        "database": db.get_connection_info(),
        "authentication": {
            "jwt_secret_configured": bool(settings.JWT_SECRET_KEY),
            "algorithm": settings.JWT_ALGORITHM,
            "expiration_hours": settings.JWT_EXPIRATION_HOURS
        },
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/phase")
async def phase_info():
    """현재 Phase 정보"""
    return {
        "current_phase": 4,
        "description": "JWT Authentication and protected endpoints",
        "features": [
            "JWT token generation and validation",
            "User authentication system",
            "Protected endpoints with middleware",
            "Token-based access control"
        ],
        "next_phase_features": [
            "Keyword CRUD operations",
            "Data validation and storage",
            "Keyword management endpoints",
            "Search and filtering capabilities"
        ],
        "endpoints": {
            "public": {
                "/": "Root endpoint with authentication status",
                "/health": "Health check including auth system",
                "/auth/login": "User login and token generation",
                "/auth/demo-users": "Demo users for testing",
                "/db/test": "Database connection test",
                "/db/status": "Database status",
                "/config": "Configuration status",
                "/phase": "Phase information"
            },
            "protected": {
                "/auth/me": "Current user information",
                "/auth/protected": "Protected endpoint example"
            }
        },
        "authentication": {
            "type": "JWT Bearer Token",
            "algorithm": settings.JWT_ALGORITHM,
            "expiration": f"{settings.JWT_EXPIRATION_HOURS} hours",
            "demo_users": ["admin", "user", "demo"]
        }
    }

# Vercel에서 자동으로 감지할 수 있도록 app 객체 export
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)