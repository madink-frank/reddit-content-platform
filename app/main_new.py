"""
완전히 새로운 Phase 1 앱 - 기존 파일과 완전히 독립적
"""

from fastapi import FastAPI
from datetime import datetime

# 완전히 새로운 FastAPI 앱
app = FastAPI(
    title="Reddit Platform - Phase 1 NEW",
    version="1.0.0",
    description="완전히 새로운 Phase 1 앱"
)

@app.get("/")
async def root():
    return {
        "message": "🚀 NEW Phase 1 성공!",
        "status": "working",
        "phase": "1-NEW",
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "phase": "1-NEW",
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/test")
async def test():
    return {
        "message": "테스트 성공",
        "new_app": True,
        "timestamp": datetime.utcnow().isoformat()
    }