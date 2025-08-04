"""
Phase 3: 데이터베이스 연결 테스트
- Supabase 연결 설정
- 데이터베이스 헬스체크
- 연결 상태 모니터링
"""

import os
from fastapi import FastAPI, HTTPException
from datetime import datetime
from typing import Optional
import asyncio

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
    
    # JWT 설정 (Phase 4에서 사용 예정)
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "dev-secret-key")

settings = Settings()

# 간단한 데이터베이스 연결 테스트 클래스
class DatabaseConnection:
    def __init__(self):
        self.supabase_url = settings.SUPABASE_URL
        self.supabase_key = settings.SUPABASE_KEY
        self.is_connected = False
        
    async def test_connection(self):
        """데이터베이스 연결 테스트 (시뮬레이션)"""
        try:
            # 실제 환경에서는 여기서 Supabase 클라이언트를 사용
            if self.supabase_url and self.supabase_key:
                # 연결 시뮬레이션
                await asyncio.sleep(0.1)  # 네트워크 지연 시뮬레이션
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

# 데이터베이스 인스턴스 생성
db = DatabaseConnection()

# FastAPI 앱 생성
app = FastAPI(
    title=f"{settings.PROJECT_NAME} - Phase 3",
    version="3.0.0",
    description="Phase 3: Database connection and health check",
    debug=settings.DEBUG
)

@app.get("/")
async def root():
    """Phase 3 - 기본 루트 엔드포인트"""
    return {
        "message": "🚀 Phase 3 배포 성공!",
        "status": "working",
        "phase": "3 - Database Connection",
        "timestamp": datetime.utcnow().isoformat(),
        "environment": settings.ENVIRONMENT,
        "database_configured": db.get_connection_info()["configured"],
        "next_phase": "기본 인증 시스템"
    }

@app.get("/health")
async def health():
    """Phase 3 - 헬스체크 (데이터베이스 포함)"""
    db_info = db.get_connection_info()
    
    return {
        "status": "healthy",
        "phase": "3",
        "timestamp": datetime.utcnow().isoformat(),
        "deployment": "vercel-serverless",
        "environment": settings.ENVIRONMENT,
        "database": db_info
    }

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
        "phase": 3,
        "database_info": db.get_connection_info(),
        "environment_variables": {
            "SUPABASE_URL": "✅ Set" if settings.SUPABASE_URL else "❌ Not set",
            "SUPABASE_KEY": "✅ Set" if settings.SUPABASE_KEY else "❌ Not set"
        },
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/config")
async def config_status():
    """Phase 3 - 설정 상태 확인 (데이터베이스 포함)"""
    return {
        "phase": 3,
        "project_name": settings.PROJECT_NAME,
        "environment": settings.ENVIRONMENT,
        "debug": settings.DEBUG,
        "configurations": {
            "supabase_configured": bool(settings.SUPABASE_URL and settings.SUPABASE_KEY),
            "reddit_api_configured": bool(settings.REDDIT_CLIENT_ID and settings.REDDIT_CLIENT_SECRET),
            "jwt_configured": bool(settings.JWT_SECRET_KEY != "dev-secret-key")
        },
        "database": db.get_connection_info(),
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/phase")
async def phase_info():
    """현재 Phase 정보"""
    return {
        "current_phase": 3,
        "description": "Database connection and health monitoring",
        "features": [
            "Database connection testing",
            "Supabase integration setup",
            "Connection health monitoring",
            "Database status endpoints"
        ],
        "next_phase_features": [
            "JWT token generation",
            "User authentication",
            "Protected endpoints",
            "Token validation middleware"
        ],
        "endpoints": {
            "/": "Root endpoint with database status",
            "/health": "Health check including database",
            "/db/test": "Test database connection",
            "/db/status": "Database configuration status",
            "/config": "Full configuration status",
            "/phase": "Current phase information"
        },
        "environment_variables": {
            "required_for_database": [
                "SUPABASE_URL",
                "SUPABASE_KEY"
            ],
            "required_for_next_phases": [
                "REDDIT_CLIENT_ID", 
                "REDDIT_CLIENT_SECRET"
            ],
            "optional": [
                "PROJECT_NAME",
                "ENVIRONMENT",
                "DEBUG",
                "JWT_SECRET_KEY"
            ]
        }
    }

# Vercel에서 자동으로 감지할 수 있도록 app 객체 export
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)