"""
Phase 2: 환경 변수 및 설정 관리 (루트 레벨)
- 환경 변수 읽기
- 기본 설정 클래스
- 설정 상태 확인 엔드포인트
"""

import os
from fastapi import FastAPI
from datetime import datetime
from typing import Optional

# 기본 설정 클래스
class Settings:
    PROJECT_NAME: str = os.getenv("PROJECT_NAME", "Reddit Content Platform")
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "production")
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"
    
    # 데이터베이스 설정 (Phase 3에서 사용 예정)
    SUPABASE_URL: str = os.getenv("SUPABASE_URL", "")
    SUPABASE_KEY: str = os.getenv("SUPABASE_KEY", "")
    
    # Reddit API 설정 (Phase 6에서 사용 예정)
    REDDIT_CLIENT_ID: str = os.getenv("REDDIT_CLIENT_ID", "")
    REDDIT_CLIENT_SECRET: str = os.getenv("REDDIT_CLIENT_SECRET", "")
    
    # JWT 설정 (Phase 4에서 사용 예정)
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "dev-secret-key")

settings = Settings()

# FastAPI 앱 생성
app = FastAPI(
    title=f"{settings.PROJECT_NAME} - Phase 2",
    version="2.0.0",
    description="Phase 2: Environment variables and configuration management",
    debug=settings.DEBUG
)

@app.get("/")
async def root():
    """Phase 2 - 기본 루트 엔드포인트"""
    return {
        "message": "🚀 Phase 2 배포 성공! (ROOT LEVEL)",
        "status": "working",
        "phase": "2 - Configuration Management",
        "timestamp": datetime.utcnow().isoformat(),
        "environment": settings.ENVIRONMENT,
        "next_phase": "데이터베이스 연결 테스트"
    }

@app.get("/health")
async def health():
    """Phase 2 - 헬스체크"""
    return {
        "status": "healthy",
        "phase": "2",
        "timestamp": datetime.utcnow().isoformat(),
        "deployment": "vercel-serverless",
        "environment": settings.ENVIRONMENT
    }

@app.get("/config")
async def config_status():
    """Phase 2 - 설정 상태 확인"""
    return {
        "phase": 2,
        "project_name": settings.PROJECT_NAME,
        "environment": settings.ENVIRONMENT,
        "debug": settings.DEBUG,
        "configurations": {
            "supabase_configured": bool(settings.SUPABASE_URL),
            "reddit_api_configured": bool(settings.REDDIT_CLIENT_ID and settings.REDDIT_CLIENT_SECRET),
            "jwt_configured": bool(settings.JWT_SECRET_KEY != "dev-secret-key")
        },
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/phase")
async def phase_info():
    """현재 Phase 정보"""
    return {
        "current_phase": 2,
        "description": "Environment variables and configuration management",
        "features": [
            "Environment variable reading",
            "Configuration class",
            "Settings validation",
            "Configuration status endpoint"
        ],
        "next_phase_features": [
            "Database connection",
            "Supabase integration",
            "Connection health check"
        ],
        "environment_variables": {
            "required_for_next_phases": [
                "SUPABASE_URL",
                "SUPABASE_KEY",
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