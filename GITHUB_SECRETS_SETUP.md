# GitHub Secrets 설정 가이드

이 가이드는 Reddit Content Platform의 CI/CD 파이프라인에 필요한 GitHub Secrets를 설정하는 방법을 설명합니다.

## 📋 필요한 Secrets 목록

### 🔐 필수 Production Secrets

| Secret Name | 설명 | 예시 값 |
|-------------|------|---------|
| `DATABASE_URL` | 프로덕션 데이터베이스 연결 문자열 | `postgresql://user:pass@host:5432/db` |
| `REDIS_URL` | Redis 서버 연결 문자열 | `redis://host:6379` |
| `JWT_SECRET_KEY` | JWT 토큰 서명용 비밀키 | `생성된-안전한-키` |
| `REDDIT_CLIENT_ID` | Reddit API 클라이언트 ID | `your_reddit_client_id` |
| `REDDIT_CLIENT_SECRET` | Reddit API 클라이언트 시크릿 | `your_reddit_client_secret` |

### 📊 모니터링 Secrets

| Secret Name | 설명 | 예시 값 |
|-------------|------|---------|
| `GRAFANA_PASSWORD` | Grafana 관리자 비밀번호 | `secure_password` |
| `GRAFANA_SECRET_KEY` | Grafana 세션 암호화 키 | `생성된-그라파나-키` |

### 🚀 배포 Secrets (선택사항)

| Secret Name | 설명 | 예시 값 |
|-------------|------|---------|
| `RAILWAY_TOKEN` | Railway CLI 토큰 | `railway_token_here` |

## 🛠️ 단계별 설정 방법

### 1단계: GitHub Repository Settings 접근

1. **GitHub 저장소 페이지로 이동**
   ```
   https://github.com/your-username/your-repository
   ```

2. **Settings 탭 클릭**
   - 저장소 상단 메뉴바에서 "Settings" 클릭

3. **Secrets 메뉴 접근**
   - 왼쪽 사이드바에서 "Secrets and variables" 클릭
   - "Actions" 서브메뉴 선택

### 2단계: Reddit API 자격증명 생성

Reddit API 자격증명이 없는 경우:

1. **Reddit Apps 페이지 방문**
   ```
   https://www.reddit.com/prefs/apps
   ```

2. **새 앱 생성**
   - "Create App" 또는 "Create Another App" 버튼 클릭

3. **앱 정보 입력**
   ```
   Name: Reddit Content Platform
   App type: web app (선택)
   Description: Content crawling and analysis platform
   About URL: (비워둬도 됨)
   Redirect URI: http://localhost:8000/auth/callback
   ```

4. **자격증명 확인**
   - **Client ID**: 앱 이름 바로 아래 표시되는 문자열
   - **Client Secret**: "secret" 라벨 옆의 문자열

### 3단계: 보안 키 생성

안전한 키들을 생성하려면 제공된 스크립트를 사용:

```bash
python scripts/generate-secrets.py
```

이 스크립트는 다음을 생성합니다:
- JWT Secret Key
- Grafana 비밀번호 및 Secret Key
- 데이터베이스/Redis URL 템플릿

### 4단계: GitHub Secrets 추가

각 secret을 개별적으로 추가:

#### 4.1 JWT Secret Key 추가
```
Name: JWT_SECRET_KEY
Value: [generate-secrets.py에서 생성된 JWT 키]
```

#### 4.2 Database URL 추가
```
Name: DATABASE_URL
Value: postgresql://username:password@host:port/database_name
```

**실제 값 예시:**
```
postgresql://reddit_user:secure_password@db.example.com:5432/reddit_platform
```

#### 4.3 Redis URL 추가
```
Name: REDIS_URL
Value: redis://host:port
```

**실제 값 예시:**
```
redis://redis.example.com:6379
```

#### 4.4 Reddit API 자격증명 추가
```
Name: REDDIT_CLIENT_ID
Value: [Reddit에서 생성한 Client ID]

Name: REDDIT_CLIENT_SECRET
Value: [Reddit에서 생성한 Client Secret]
```

#### 4.5 Grafana 설정 추가
```
Name: GRAFANA_PASSWORD
Value: [generate-secrets.py에서 생성된 비밀번호]

Name: GRAFANA_SECRET_KEY
Value: [generate-secrets.py에서 생성된 Secret Key]
```

### 5단계: Railway 배포 설정 (선택사항)

Railway를 사용하는 경우:

1. **Railway CLI 토큰 생성**
   ```bash
   railway login
   railway whoami --token
   ```

2. **GitHub Secret 추가**
   ```
   Name: RAILWAY_TOKEN
   Value: [Railway CLI 토큰]
   ```

## 🔍 설정 확인 방법

### 로컬에서 확인

1. **환경 변수 테스트**
   ```bash
   # .env 파일 생성 (로컬 개발용)
   cp .env.example .env
   # .env 파일을 편집하여 실제 값 입력
   ```

2. **연결 테스트**
   ```bash
   # 데이터베이스 연결 테스트
   python -c "from app.core.database import engine; print('DB OK')"
   
   # Redis 연결 테스트
   python -c "from app.core.redis_client import redis_client; print('Redis OK')"
   ```

### GitHub Actions에서 확인

1. **테스트 PR 생성**
   - 작은 변경사항으로 Pull Request 생성
   - CI 파이프라인이 성공적으로 실행되는지 확인

2. **로그 확인**
   - GitHub Actions 탭에서 워크플로우 실행 로그 확인
   - 환경 변수 관련 오류가 없는지 확인

## ⚠️ 보안 주의사항

### 🔒 Secret 관리 원칙

1. **절대 코드에 포함하지 마세요**
   ```python
   # ❌ 잘못된 예시
   JWT_SECRET = "my-secret-key"
   
   # ✅ 올바른 예시
   JWT_SECRET = os.getenv("JWT_SECRET_KEY")
   ```

2. **환경별 분리**
   - 개발: `.env` 파일 (git에 커밋하지 않음)
   - 스테이징: GitHub Secrets
   - 프로덕션: GitHub Secrets (다른 값 사용)

3. **정기적 교체**
   - JWT Secret: 3-6개월마다
   - API Keys: 필요시
   - 데이터베이스 비밀번호: 정기적으로

### 🛡️ 추가 보안 설정

1. **GitHub Repository 보안**
   - Repository를 Private으로 설정
   - Branch protection rules 활성화
   - Required reviews 설정

2. **환경별 접근 제어**
   - Production environment에 approval 필요 설정
   - Staging environment 자동 배포 허용

## 🚨 문제 해결

### 일반적인 오류들

#### 1. Database 연결 실패
```
Error: could not connect to server
```

**해결방법:**
- DATABASE_URL 형식 확인
- 호스트/포트 접근 가능성 확인
- 사용자 권한 확인

#### 2. Redis 연결 실패
```
Error: Connection refused
```

**해결방법:**
- REDIS_URL 형식 확인
- Redis 서버 상태 확인
- 방화벽 설정 확인

#### 3. Reddit API 인증 실패
```
Error: 401 Unauthorized
```

**해결방법:**
- REDDIT_CLIENT_ID/SECRET 확인
- Reddit 앱 설정 확인
- Rate limit 확인

#### 4. JWT 토큰 오류
```
Error: Invalid token
```

**해결방법:**
- JWT_SECRET_KEY 일관성 확인
- 키 길이 및 복잡성 확인

### 디버깅 명령어

```bash
# GitHub Actions 로그에서 환경 변수 확인 (민감한 정보는 마스킹됨)
echo "DATABASE_URL is set: ${{ secrets.DATABASE_URL != '' }}"

# 로컬에서 환경 변수 확인
python -c "import os; print('JWT_SECRET_KEY:', bool(os.getenv('JWT_SECRET_KEY')))"
```

## 📞 지원

문제가 발생하면:

1. **GitHub Actions 로그 확인**
   - Actions 탭에서 실패한 워크플로우 로그 검토

2. **환경 변수 검증**
   - 모든 필수 secrets가 설정되었는지 확인

3. **연결 테스트**
   - 로컬에서 동일한 설정으로 테스트

4. **문서 참조**
   - [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) 참조
   - GitHub Actions 공식 문서 참조