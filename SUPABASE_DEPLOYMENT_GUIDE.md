# Supabase 배포 가이드

## 🎯 현재 상태
- ✅ PostgreSQL 로컬 데이터베이스 설정 완료
- ✅ 모든 테이블 스키마 생성 완료 (Alembic 마이그레이션)
- ✅ 애플리케이션 정상 작동 확인 (healthy 상태)
- ✅ Celery 워커 실행 중
- ✅ Redis 연결 정상

## 📋 다음 단계: 실제 Supabase 프로젝트 배포

### 1단계: Supabase 프로젝트 생성
1. [Supabase 대시보드](https://supabase.com/dashboard)에 로그인
2. "New Project" 클릭
3. 프로젝트 정보 입력:
   - **Name**: `reddit-content-platform`
   - **Database Password**: 강력한 비밀번호 생성
   - **Region**: 가장 가까운 지역 선택 (예: Northeast Asia - Seoul)

### 2단계: 데이터베이스 스키마 적용
프로젝트 생성 후 SQL Editor에서 다음 마이그레이션 파일을 실행:

```sql
-- supabase/migrations/20240101000000_initial_schema.sql 내용 복사하여 실행
```

### 3단계: 환경 변수 업데이트
프로젝트 생성 후 Settings > API에서 다음 정보를 복사:

```bash
# .env 파일 업데이트
SUPABASE_URL=https://your-project-ref.supabase.co
SUPABASE_ANON_KEY=your-anon-key
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key

# 데이터베이스 URL 업데이트 (Settings > Database > Connection string)
DATABASE_URL=postgresql://postgres:[YOUR-PASSWORD]@db.your-project-ref.supabase.co:5432/postgres
```

### 4단계: Row Level Security (RLS) 정책 설정
SQL Editor에서 다음 정책들을 적용:

```sql
-- RLS 활성화
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE keywords ENABLE ROW LEVEL SECURITY;
-- ... (나머지 테이블들)

-- 정책 생성
CREATE POLICY "Users can view own profile" ON users FOR SELECT USING (auth.uid()::text = id::text);
-- ... (나머지 정책들)
```

### 5단계: 프론트엔드 배포 준비

#### 관리자 대시보드 (Vercel 배포)
```bash
cd admin-dashboard
# 환경 변수 설정
echo "VITE_API_BASE_URL=https://your-api-domain.com" > .env.production
echo "VITE_SUPABASE_URL=https://your-project-ref.supabase.co" >> .env.production
echo "VITE_SUPABASE_ANON_KEY=your-anon-key" >> .env.production

# Vercel 배포
npx vercel --prod
```

#### 블로그 사이트 (Vercel 배포)
```bash
cd blog-site
# 환경 변수 설정
echo "NEXT_PUBLIC_API_BASE_URL=https://your-api-domain.com" > .env.production
echo "NEXT_PUBLIC_SUPABASE_URL=https://your-project-ref.supabase.co" >> .env.production

# Vercel 배포
npx vercel --prod
```

### 6단계: 백엔드 API 배포 (Railway)

```bash
# Railway 배포
railway login
railway init
railway add postgresql
railway add redis

# 환경 변수 설정
railway variables set DATABASE_URL=postgresql://postgres:[PASSWORD]@db.your-project-ref.supabase.co:5432/postgres
railway variables set SUPABASE_URL=https://your-project-ref.supabase.co
railway variables set SUPABASE_ANON_KEY=your-anon-key
railway variables set SUPABASE_SERVICE_ROLE_KEY=your-service-role-key

# 배포
railway up
```

### 7단계: 도메인 및 CORS 설정
1. **API 도메인**: Railway에서 제공하는 도메인 또는 커스텀 도메인 설정
2. **CORS 설정**: 프론트엔드 도메인들을 CORS_ORIGINS에 추가
3. **Supabase Auth**: 허용된 리디렉션 URL에 프론트엔드 도메인 추가

### 8단계: 모니터링 및 로깅 설정
1. **Prometheus 메트릭**: Grafana 대시보드 설정
2. **로그 모니터링**: 구조화된 로그 확인
3. **알림 설정**: 시스템 오류 시 알림 구성

## 🔧 현재 로컬 개발 환경
- **Database**: PostgreSQL (localhost:5432)
- **Redis**: localhost:6379
- **API**: http://localhost:8000
- **Admin Dashboard**: http://localhost:5173
- **Blog Site**: http://localhost:3000

## 📝 배포 체크리스트
- [ ] Supabase 프로젝트 생성
- [ ] 데이터베이스 스키마 적용
- [ ] RLS 정책 설정
- [ ] 환경 변수 업데이트
- [ ] 백엔드 API 배포
- [ ] 관리자 대시보드 배포
- [ ] 블로그 사이트 배포
- [ ] 도메인 및 CORS 설정
- [ ] 모니터링 설정
- [ ] 최종 테스트

## 🚀 배포 후 확인사항
1. 모든 API 엔드포인트 정상 작동
2. 인증 플로우 테스트
3. 크롤링 기능 테스트
4. 트렌드 분석 기능 테스트
5. 블로그 컨텐츠 생성 테스트
6. 관리자 대시보드 기능 테스트
7. 공개 블로그 사이트 기능 테스트