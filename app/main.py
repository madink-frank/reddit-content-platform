"""
Phase 1: 완전히 독립적인 minimal FastAPI 앱
- 외부 의존성 없음
- import 체인 없음
- 기본 엔드포인트만 제공
"""

from fastapi import FastAPI
from datetime import datetime

# 완전히 독립적인 FastAPI 앱 생성
app = FastAPI(
    title="Reddit Content Platform - Phase 1",
    version="1.0.0",
    description="Phase 1: Minimal deployment test"
)

@app.get("/")
async def root():
    """Phase 1 - 기본 루트 엔드포인트"""
    return {
        "message": "🎉 Phase 1 배포 성공! (v2)",
        "status": "working",
        "phase": "1 - Minimal App",
        "timestamp": datetime.utcnow().isoformat(),
        "next_phase": "환경 변수 및 설정 추가"
    }

@app.get("/health")
async def health():
    """Phase 1 - 헬스체크"""
    return {
        "status": "healthy",
        "phase": "1",
        "timestamp": datetime.utcnow().isoformat(),
        "deployment": "vercel-serverless"
    }

@app.get("/phase")
async def phase_info():
    """현재 Phase 정보"""
    return {
        "current_phase": 1,
        "description": "Minimal FastAPI app with zero dependencies",
        "features": [
            "Basic endpoints",
            "Health check",
            "JSON responses"
        ],
        "next_phase_features": [
            "Environment variables",
            "Configuration management",
            "Database connection test"
        ]
    }

# Vercel에서 자동으로 감지할 수 있도록 app 객체 export
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)