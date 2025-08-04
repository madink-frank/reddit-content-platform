# 🔧 Vercel 배포 문제 해결

## 문제 원인
1. **복잡한 미들웨어**: 서버리스 환경에서 지원하지 않는 기능들
2. **누락된 모듈**: import 오류로 인한 애플리케이션 시작 실패
3. **백그라운드 태스크**: Celery 등 서버리스에서 작동하지 않는 기능

## 해결 방법

### 1. 간단한 메인 파일 사용
`app/main_simple.py` 파일을 생성하여 기본적인 FastAPI 앱만 실행

### 2. Vercel 설정 파일 생성
`vercel.json` 파일로 배포 설정 최적화

### 3. 최소 의존성 파일
`requirements_minimal.txt`로 필수 패키지만 설치

## 🚀 배포 단계

### 1단계: 파일 업데이트
다음 파일들이 생성/수정되었습니다:
- ✅ `app/main_simple.py` - 간단한 FastAPI 앱
- ✅ `vercel.json` - Vercel 배포 설정
- ✅ `requirements_minimal.txt` - 최소 의존성

### 2단계: GitHub에 푸시
```bash
git add .
git commit -m "Fix: Simplify app for Vercel deployment"
git push origin main
```

### 3단계: Vercel에서 재배포
1. Vercel 대시보드에서 프로젝트 선택
2. **Settings** → **General** → **Build & Output Settings**
3. **Framework Preset**: Other
4. **Build Command**: 비워두기
5. **Output Directory**: 비워두기
6. **Install Command**: `pip install -r requirements_minimal.txt`

### 4단계: 환경 변수 재확인
다음 환경 변수들이 설정되어 있는지 확인:

```
SUPABASE_URL=https://kyseetrtvhvddkdlcsbm.supabase.co
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imt5c2VldHJ0dmh2ZGRrZGxjc2JtIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTQyMDA1MjAsImV4cCI6MjA2OTc3NjUyMH0.UUUa2iJJIRJPPR1w5DBV6QiVr24WqBOcpbpUTh2Ae6M
DATABASE_URL=postgresql://postgres:Madink1234!@db.kyseetrtvhvddkdlcsbm.supabase.co:5432/postgres
JWT_SECRET_KEY=8vN2pQ7mK9xR4tY6wE3rT5uI8oP1aS2dF7gH0jK3lM9nB6vC4xZ1qW5eR8tY2uI7
PROJECT_NAME=Reddit Content Platform
API_V1_STR=/api/v1
ENVIRONMENT=production
```

### 5단계: 재배포 트리거
1. **Deployments** 탭으로 이동
2. **Redeploy** 버튼 클릭
3. **Use existing Build Cache** 체크 해제
4. **Redeploy** 클릭

## 🧪 테스트 엔드포인트

배포 성공 후 다음 엔드포인트들을 테스트:

1. **기본 상태**: `https://your-app.vercel.app/`
2. **헬스체크**: `https://your-app.vercel.app/health`
3. **API 헬스체크**: `https://your-app.vercel.app/api/v1/health/basic`
4. **Supabase 연결**: `https://your-app.vercel.app/api/v1/health/supabase`
5. **API 문서**: `https://your-app.vercel.app/docs`

## 📋 성공 확인 체크리스트

- [ ] 기본 엔드포인트 응답 (200 OK)
- [ ] 헬스체크 통과
- [ ] API 문서 접근 가능
- [ ] Supabase 연결 확인
- [ ] 500 에러 해결

## 🔄 다음 단계

배포가 성공하면:
1. **기능 점진적 추가**: 복잡한 기능들을 하나씩 추가
2. **모니터링 설정**: 로그 및 메트릭 확인
3. **프론트엔드 연동**: 관리자 대시보드 배포
4. **실제 Reddit API 연동**: 테스트 후 실제 키 설정