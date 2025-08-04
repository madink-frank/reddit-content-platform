# 🚀 점진적 배포 문제 해결 계획

## 📋 현재 상황
- **문제**: `app/main.py`가 복잡한 import 체인으로 인해 `ModuleNotFoundError: No module named 'praw'` 발생
- **원인**: 전체 애플리케이션을 한번에 배포하려고 해서 의존성 문제 발생
- **해결책**: 점진적으로 기능을 추가하면서 각 단계별로 배포 테스트

## 🎯 Phase별 배포 계획

### Phase 1: 기본 인프라 확인 ✅ (진행 중)
**목표**: 가장 기본적인 FastAPI 앱이 Vercel에서 작동하는지 확인

**파일**: `app/main_minimal_v1.py`
**기능**:
- ✅ 기본 FastAPI 앱
- ✅ 루트 엔드포인트 (`/`)
- ✅ 헬스체크 엔드포인트 (`/health`)
- ✅ Phase 정보 엔드포인트 (`/phase`)

**성공 기준**: 
- 500 에러 없이 배포 성공
- 모든 엔드포인트에서 200 응답

### Phase 2: 환경 변수 및 설정 관리
**목표**: 환경 변수 읽기 및 기본 설정 클래스 추가

**파일**: `app/main_minimal_v2.py`
**추가 기능**:
- 환경 변수 읽기 (`os.getenv`)
- 기본 설정 클래스
- 설정 상태 확인 엔드포인트 (`/config`)

### Phase 3: 데이터베이스 연결 테스트
**목표**: Supabase 연결 설정 및 연결 테스트

**파일**: `app/main_minimal_v3.py`
**추가 기능**:
- Supabase 연결 설정
- 데이터베이스 헬스체크 엔드포인트
- 연결 상태 모니터링

### Phase 4: 기본 인증 시스템
**목표**: JWT 토큰 생성/검증 기능 추가

**파일**: `app/main_minimal_v4.py`
**추가 기능**:
- JWT 토큰 생성
- 토큰 검증 미들웨어
- 보호된 엔드포인트 예제

### Phase 5: 키워드 관리 API
**목표**: 기본 CRUD 엔드포인트 추가

**파일**: `app/main_minimal_v5.py`
**추가 기능**:
- 키워드 CRUD 엔드포인트
- 데이터 검증
- 에러 처리

### Phase 6: Reddit API 연동
**목표**: Reddit API 클라이언트 추가

**파일**: `app/main_minimal_v6.py`
**추가 기능**:
- Reddit API 클라이언트
- 기본 크롤링 기능
- API 상태 모니터링

### Phase 7: 전체 기능 통합
**목표**: 모든 기능을 통합한 완전한 애플리케이션

**파일**: `app/main.py` (기존 파일 수정)
**기능**: 모든 Phase의 기능 통합

## 🔧 각 Phase별 구현 전략

### Phase 1 구현 (현재)
```python
# app/main_minimal_v1.py
from fastapi import FastAPI
from datetime import datetime

app = FastAPI(title="Reddit Content Platform - Phase 1")

@app.get("/")
async def root():
    return {"message": "Phase 1 배포 성공!", "phase": 1}
```

### Phase 2 구현 예시
```python
# app/main_minimal_v2.py
import os
from fastapi import FastAPI
from datetime import datetime

class Settings:
    PROJECT_NAME: str = os.getenv("PROJECT_NAME", "Reddit Content Platform")
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "production")
    SUPABASE_URL: str = os.getenv("SUPABASE_URL", "")

settings = Settings()
app = FastAPI(title=f"{settings.PROJECT_NAME} - Phase 2")

@app.get("/config")
async def config_status():
    return {
        "environment": settings.ENVIRONMENT,
        "supabase_configured": bool(settings.SUPABASE_URL),
        "phase": 2
    }
```

## 📊 성공 지표

각 Phase의 성공 기준:
1. **배포 성공**: Vercel에서 빌드 오류 없이 배포
2. **엔드포인트 응답**: 모든 엔드포인트에서 200 OK 응답
3. **기능 작동**: 해당 Phase의 모든 기능이 정상 작동
4. **이전 기능 유지**: 이전 Phase의 기능이 영향받지 않음

## 🔄 배포 프로세스

각 Phase마다:
1. **로컬 테스트**: 기능이 로컬에서 작동하는지 확인
2. **파일 생성**: 해당 Phase의 minimal 앱 파일 생성
3. **vercel.json 업데이트**: 새로운 파일을 가리키도록 설정
4. **배포 및 테스트**: GitHub 푸시 → Vercel 자동 배포 → 테스트
5. **문제 해결**: 문제 발생 시 이전 Phase로 롤백 후 수정

## 🚨 롤백 계획

문제 발생 시:
1. **즉시 롤백**: `vercel.json`을 이전 Phase 파일로 변경
2. **문제 분석**: 로그 확인 및 원인 파악
3. **수정 후 재배포**: 문제 해결 후 다시 배포

---

**현재 진행 상황**: Phase 1 - 기본 인프라 확인 중 🚧

**다음 단계**: Phase 1 배포 성공 확인 → Phase 2 환경 변수 추가