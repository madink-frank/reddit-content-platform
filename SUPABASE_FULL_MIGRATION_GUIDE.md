# 🚀 Supabase 올인원 마이그레이션 가이드

## 현재 아키텍처 vs Supabase 아키텍처

### 현재 구조
```
FastAPI (Python) → PostgreSQL + Redis + Celery
├── 백엔드 API 서버 (Railway/Vercel 필요)
├── 데이터베이스 (PostgreSQL)
├── 캐시/메시지 브로커 (Redis)
└── 백그라운드 작업 (Celery Workers)
```

### Supabase 올인원 구조
```
Supabase Edge Functions (Deno/TypeScript) → Supabase Services
├── Edge Functions (서버리스 API)
├── Database (PostgreSQL)
├── Auth (내장 인증)
├── Storage (파일 저장)
└── Realtime (실시간 구독)
```

## 🔄 마이그레이션 옵션

### 옵션 1: 하이브리드 접근 (권장)
**Supabase + 최소한의 외부 서비스**

```yaml
Services:
  - Supabase: Database + Auth + Storage
  - Vercel: FastAPI 서버리스 함수
  - Upstash: Redis (서버리스)
  - 프론트엔드: Vercel/Netlify
```

**장점**: 기존 코드 재사용, 빠른 배포
**단점**: 여전히 여러 서비스 필요

### 옵션 2: 완전 Supabase 전환 (대규모 리팩토링)
**모든 로직을 Edge Functions로 이전**

```yaml
Services:
  - Supabase: Database + Auth + Edge Functions
  - 프론트엔드: Vercel/Netlify
```

**장점**: 단일 플랫폼, 완전 서버리스
**단점**: 전체 코드 재작성 필요 (Python → TypeScript/Deno)

### 옵션 3: Supabase + 외부 백엔드 (현재 최적)
**데이터베이스만 Supabase 사용**

```yaml
Services:
  - Supabase: Database + Auth
  - Railway/Render: FastAPI 백엔드
  - Upstash: Redis
  - 프론트엔드: Vercel
```

**장점**: 기존 코드 유지, Supabase DB 활용
**단점**: 여러 서비스 관리

## 🛠️ 각 옵션별 구현 방법

### 옵션 1: 하이브리드 (권장)

#### 1단계: Supabase 프로젝트 설정
```bash
# 수동 작업 필요
1. https://supabase.com/dashboard 접속
2. 새 프로젝트 생성: "reddit-content-platform"
3. 데이터베이스 비밀번호 설정
4. 지역 선택 (Seoul)
```

#### 2단계: 데이터베이스 마이그레이션
```sql
-- Supabase SQL Editor에서 실행
-- supabase/migrations/20240101000000_initial_schema.sql 내용 복사
```

#### 3단계: Vercel 서버리스 함수로 FastAPI 배포
```python
# vercel.json 설정
{
  "functions": {
    "app/main.py": {
      "runtime": "python3.9"
    }
  },
  "routes": [
    { "src": "/(.*)", "dest": "/app/main.py" }
  ]
}
```

#### 4단계: Upstash Redis 설정
```bash
# 수동 작업
1. https://upstash.com 가입
2. Redis 데이터베이스 생성
3. 연결 URL 복사
```

#### 5단계: 환경 변수 설정
```bash
# Vercel 환경 변수
DATABASE_URL=postgresql://postgres:[PASSWORD]@db.xxx.supabase.co:5432/postgres
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_ANON_KEY=xxx
REDIS_URL=redis://xxx.upstash.io:6379
```

### 옵션 2: 완전 Supabase 전환

#### Edge Functions 예제
```typescript
// supabase/functions/keywords/index.ts
import { serve } from "https://deno.land/std@0.168.0/http/server.ts"
import { createClient } from 'https://esm.sh/@supabase/supabase-js@2'

serve(async (req) => {
  const supabase = createClient(
    Deno.env.get('SUPABASE_URL') ?? '',
    Deno.env.get('SUPABASE_ANON_KEY') ?? ''
  )

  if (req.method === 'POST') {
    const { keyword } = await req.json()
    
    const { data, error } = await supabase
      .from('keywords')
      .insert({ keyword, user_id: 'user-id' })
    
    return new Response(JSON.stringify({ data, error }), {
      headers: { 'Content-Type': 'application/json' }
    })
  }
})
```

#### 백그라운드 작업 대체
```typescript
// supabase/functions/crawl-reddit/index.ts
import { serve } from "https://deno.land/std@0.168.0/http/server.ts"

serve(async (req) => {
  // Reddit API 호출
  const response = await fetch('https://www.reddit.com/r/python.json')
  const data = await response.json()
  
  // Supabase에 저장
  const supabase = createClient(...)
  await supabase.from('posts').insert(processedData)
  
  return new Response('OK')
})
```

## 📋 수동 작업이 필요한 부분

### 1. Supabase 프로젝트 생성 (필수)
```bash
수동 작업:
1. https://supabase.com/dashboard 접속
2. GitHub/Google 계정으로 로그인
3. "New Project" 클릭
4. 프로젝트 정보 입력:
   - Name: reddit-content-platform
   - Database Password: 강력한 비밀번호
   - Region: Northeast Asia (Seoul)
5. 프로젝트 생성 대기 (2-3분)
```

### 2. 데이터베이스 스키마 적용 (필수)
```bash
수동 작업:
1. Supabase Dashboard → SQL Editor
2. 새 쿼리 생성
3. supabase/migrations/20240101000000_initial_schema.sql 내용 복사
4. 실행 (Run)
```

### 3. API 키 및 URL 복사 (필수)
```bash
수동 작업:
1. Settings → API
2. 다음 정보 복사:
   - Project URL
   - anon/public key
   - service_role/secret key
```

### 4. 외부 서비스 설정 (옵션에 따라)
```bash
Upstash Redis (옵션 1):
1. https://upstash.com 가입
2. Redis 데이터베이스 생성
3. 연결 정보 복사

Vercel 배포 (옵션 1):
1. GitHub 연동
2. 프로젝트 import
3. 환경 변수 설정
```

## 🚀 권장 마이그레이션 단계

### 단계 1: 데이터베이스 마이그레이션 (즉시 가능)
```bash
1. Supabase 프로젝트 생성
2. 스키마 적용
3. 로컬 환경에서 Supabase DB 연결 테스트
```

### 단계 2: 인증 시스템 전환 (선택사항)
```bash
1. Supabase Auth 설정
2. Reddit OAuth 연동
3. 기존 JWT 로직을 Supabase Auth로 교체
```

### 단계 3: 백엔드 배포 (하이브리드)
```bash
1. Vercel에 FastAPI 배포
2. Upstash Redis 연결
3. 환경 변수 설정
```

### 단계 4: 프론트엔드 배포
```bash
1. 관리자 대시보드 → Vercel
2. 블로그 사이트 → Vercel/Netlify
3. Supabase 연결 설정
```

## 💡 즉시 시작할 수 있는 작업

현재 바로 시작할 수 있는 것:

1. **Supabase 프로젝트 생성** (5분)
2. **데이터베이스 스키마 적용** (5분)
3. **로컬 환경에서 Supabase 연결 테스트** (10분)

이 작업들을 완료하면 나머지는 점진적으로 진행할 수 있습니다.

## 🎯 결론

**권장사항**: 옵션 1 (하이브리드)
- 기존 코드 재사용 가능
- 빠른 배포 가능
- 점진적 마이그레이션 가능
- Supabase의 장점 활용

**완전 전환**은 시간이 많이 걸리므로, 먼저 하이브리드로 시작하고 나중에 필요시 Edge Functions로 전환하는 것이 현실적입니다.