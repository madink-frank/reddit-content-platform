# GitHub 저장소 설정 가이드

## 1. GitHub에서 새 저장소 생성

1. **GitHub 웹사이트 접속**: https://github.com
2. **로그인** 후 우상단의 **"+"** 버튼 클릭
3. **"New repository"** 선택
4. **저장소 설정**:
   - Repository name: `reddit-content-platform` (또는 원하는 이름)
   - Description: `Reddit Content Platform with Supabase Integration`
   - **Public** 또는 **Private** 선택
   - **Initialize this repository with:** 모두 체크 해제 (이미 로컬에 코드가 있으므로)
5. **"Create repository"** 클릭

## 2. 로컬 저장소를 GitHub에 연결

새 저장소가 생성되면 GitHub에서 제공하는 명령어를 사용하세요:

```bash
# GitHub 저장소를 원격 저장소로 추가
git remote add origin https://github.com/[YOUR-USERNAME]/[REPOSITORY-NAME].git

# 기본 브랜치를 main으로 설정
git branch -M main

# 코드를 GitHub에 업로드
git push -u origin main
```

## 3. 예시 (실제 사용자명과 저장소명으로 변경하세요)

```bash
# 예시: madink-frank 사용자의 reddit-content-platform 저장소
git remote add origin https://github.com/madink-frank/reddit-content-platform.git
git branch -M main
git push -u origin main
```

## 4. 업로드 완료 후 확인사항

✅ **포함된 주요 파일들**:
- `app/` - FastAPI 백엔드 코드
- `admin-dashboard/` - React 프론트엔드 코드
- `supabase/` - 데이터베이스 마이그레이션
- `vercel.json` - Vercel 배포 설정
- `railway.toml` - Railway 배포 설정
- `docker-compose.yml` - Docker 설정
- `requirements.txt` - Python 의존성
- 각종 테스트 파일들
- 배포 가이드 문서들

## 5. Vercel 배포 시 GitHub 저장소 선택

GitHub 저장소가 생성되면:

1. **Vercel 대시보드** (https://vercel.com/dashboard) 접속
2. **"Add New"** → **"Project"** 클릭
3. **"Import Git Repository"** 섹션에서 방금 생성한 저장소 선택
4. **"Import"** 클릭
5. 환경 변수 설정 (`vercel-env-commands.txt` 참조)
6. **"Deploy"** 클릭

## 6. 환경 변수 설정

Vercel 프로젝트 설정에서 다음 환경 변수들을 추가하세요:

```
SUPABASE_URL=https://kyseetrtvhvddkdlcsbm.supabase.co
SUPABASE_ANON_KEY=[키 값]
SUPABASE_SERVICE_ROLE_KEY=[키 값]
DATABASE_URL=[데이터베이스 URL]
JWT_SECRET_KEY=[JWT 키]
ENVIRONMENT=production
SERVERLESS=true
DISABLE_CELERY=true
```

## 7. 배포 완료!

모든 설정이 완료되면 Vercel이 자동으로 배포를 시작합니다.
배포 URL을 통해 애플리케이션에 접근할 수 있습니다.

---

**참고**: 저장소명과 사용자명은 실제 GitHub 계정에 맞게 변경하세요.