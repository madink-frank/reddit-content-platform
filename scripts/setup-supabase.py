#!/usr/bin/env python3
"""
Supabase 설정 자동화 스크립트
수동으로 생성한 Supabase 프로젝트의 정보를 입력받아 환경 설정을 자동화합니다.
"""

import os
import sys
from pathlib import Path

def setup_supabase_env():
    """Supabase 환경 설정을 대화형으로 생성합니다."""
    
    print("🚀 Supabase 환경 설정 도우미")
    print("=" * 50)
    
    # 사용자 입력 받기
    project_url = input("Supabase Project URL을 입력하세요 (https://xxx.supabase.co): ").strip()
    anon_key = input("Supabase Anon Key를 입력하세요: ").strip()
    service_key = input("Supabase Service Role Key를 입력하세요: ").strip()
    db_password = input("데이터베이스 비밀번호를 입력하세요: ").strip()
    
    # Redis 설정 (선택사항)
    use_redis = input("Upstash Redis를 사용하시겠습니까? (y/n): ").strip().lower()
    redis_url = ""
    if use_redis == 'y':
        redis_url = input("Upstash Redis URL을 입력하세요: ").strip()
    else:
        redis_url = "redis://localhost:6379"
    
    # Reddit API 설정
    reddit_client_id = input("Reddit Client ID를 입력하세요 (선택사항): ").strip() or "demo_client_id"
    reddit_client_secret = input("Reddit Client Secret을 입력하세요 (선택사항): ").strip() or "demo_client_secret"
    
    # JWT Secret 생성
    import secrets
    jwt_secret = secrets.token_urlsafe(32)
    
    # 프로젝트 참조 추출
    project_ref = project_url.replace("https://", "").replace(".supabase.co", "")
    
    # 데이터베이스 URL 생성
    database_url = f"postgresql://postgres:{db_password}@db.{project_ref}.supabase.co:5432/postgres"
    
    # 환경 파일 생성
    env_content = f"""# Supabase 프로덕션 환경 설정
# 자동 생성됨: {project_ref}

# Supabase 설정
SUPABASE_URL={project_url}
SUPABASE_ANON_KEY={anon_key}
SUPABASE_SERVICE_ROLE_KEY={service_key}

# 데이터베이스 (Supabase PostgreSQL)
DATABASE_URL={database_url}

# Redis
REDIS_URL={redis_url}

# Reddit API
REDDIT_CLIENT_ID={reddit_client_id}
REDDIT_CLIENT_SECRET={reddit_client_secret}
REDDIT_REDIRECT_URI={project_url}/api/v1/auth/callback

# JWT 설정
JWT_SECRET_KEY={jwt_secret}
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=15
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7

# 애플리케이션 설정
PROJECT_NAME=Reddit Content Platform
VERSION=1.0.0
API_V1_STR=/api/v1
ENVIRONMENT=production

# CORS 설정 (나중에 실제 도메인으로 교체)
CORS_ORIGINS=["https://your-admin-dashboard.vercel.app", "https://your-blog-site.vercel.app"]

# Reddit API 설정
REDDIT_USER_AGENT=RedditContentPlatform/1.0

# 서버리스 환경 설정
SERVERLESS=true
DISABLE_CELERY=true
"""

    # 파일 저장
    env_file = Path(".env.production")
    with open(env_file, "w") as f:
        f.write(env_content)
    
    print(f"\n✅ 환경 설정 파일이 생성되었습니다: {env_file}")
    
    # Vercel 환경 변수 설정 명령어 생성
    vercel_commands = f"""
# Vercel 환경 변수 설정 명령어들:
vercel env add SUPABASE_URL production
# 값: {project_url}

vercel env add SUPABASE_ANON_KEY production  
# 값: {anon_key}

vercel env add SUPABASE_SERVICE_ROLE_KEY production
# 값: {service_key}

vercel env add DATABASE_URL production
# 값: {database_url}

vercel env add REDIS_URL production
# 값: {redis_url}

vercel env add JWT_SECRET_KEY production
# 값: {jwt_secret}

vercel env add REDDIT_CLIENT_ID production
# 값: {reddit_client_id}

vercel env add REDDIT_CLIENT_SECRET production
# 값: {reddit_client_secret}
"""
    
    with open("vercel-env-setup.txt", "w") as f:
        f.write(vercel_commands)
    
    print("✅ Vercel 환경 변수 설정 명령어가 생성되었습니다: vercel-env-setup.txt")
    
    # 다음 단계 안내
    print("\n🎯 다음 단계:")
    print("1. Supabase SQL Editor에서 스키마 적용:")
    print("   - supabase/migrations/20240101000000_initial_schema.sql 실행")
    print("2. Vercel 배포:")
    print("   - vercel --prod")
    print("3. 환경 변수 설정:")
    print("   - vercel-env-setup.txt 파일의 명령어들 실행")
    
    return True

if __name__ == "__main__":
    try:
        setup_supabase_env()
    except KeyboardInterrupt:
        print("\n❌ 설정이 취소되었습니다.")
        sys.exit(1)
    except Exception as e:
        print(f"❌ 오류가 발생했습니다: {e}")
        sys.exit(1)