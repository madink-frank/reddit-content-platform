#!/usr/bin/env python3
"""
GitHub Secrets 생성 도우미 스크립트
Usage: python scripts/generate-secrets.py
"""

import secrets
import string
import base64
import os
from urllib.parse import quote

def generate_jwt_secret(length=64):
    """안전한 JWT secret key 생성"""
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
    return ''.join(secrets.choice(alphabet) for _ in range(length))

def generate_grafana_secret(length=32):
    """Grafana secret key 생성"""
    return secrets.token_urlsafe(length)

def generate_database_url_template():
    """Database URL 템플릿 생성"""
    return {
        "postgresql": "postgresql://username:password@host:port/database_name",
        "sqlite": "sqlite:///./app.db",
        "mysql": "mysql://username:password@host:port/database_name"
    }

def generate_redis_url_template():
    """Redis URL 템플릿 생성"""
    return {
        "local": "redis://localhost:6379",
        "remote": "redis://username:password@host:port",
        "cluster": "redis://host1:6379,host2:6379,host3:6379"
    }

def main():
    print("🔐 GitHub Secrets 생성 도우미")
    print("=" * 50)
    
    # JWT Secret Key
    jwt_secret = generate_jwt_secret()
    print(f"\n📝 JWT_SECRET_KEY:")
    print(f"   {jwt_secret}")
    
    # Grafana Secrets
    grafana_password = secrets.token_urlsafe(16)
    grafana_secret = generate_grafana_secret()
    print(f"\n📊 GRAFANA_PASSWORD:")
    print(f"   {grafana_password}")
    print(f"\n📊 GRAFANA_SECRET_KEY:")
    print(f"   {grafana_secret}")
    
    # Database URL Templates
    print(f"\n🗄️  DATABASE_URL 템플릿:")
    db_templates = generate_database_url_template()
    for db_type, url in db_templates.items():
        print(f"   {db_type}: {url}")
    
    # Redis URL Templates
    print(f"\n🔴 REDIS_URL 템플릿:")
    redis_templates = generate_redis_url_template()
    for redis_type, url in redis_templates.items():
        print(f"   {redis_type}: {url}")
    
    # Reddit API 안내
    print(f"\n🤖 Reddit API 자격증명:")
    print(f"   1. https://www.reddit.com/prefs/apps 방문")
    print(f"   2. 'Create App' 클릭")
    print(f"   3. App type: 'web app' 선택")
    print(f"   4. Redirect URI: http://localhost:8000/auth/callback")
    print(f"   5. REDDIT_CLIENT_ID와 REDDIT_CLIENT_SECRET 복사")
    
    # 환경별 설정 안내
    print(f"\n🌍 환경별 설정:")
    print(f"   Development: .env 파일 사용")
    print(f"   Staging: GitHub Secrets + .env.staging")
    print(f"   Production: GitHub Secrets + .env.production")
    
    # GitHub Secrets 설정 안내
    print(f"\n⚙️  GitHub Secrets 설정 방법:")
    print(f"   1. GitHub 저장소 → Settings")
    print(f"   2. Secrets and variables → Actions")
    print(f"   3. New repository secret 클릭")
    print(f"   4. 위의 값들을 하나씩 추가")
    
    # 보안 주의사항
    print(f"\n⚠️  보안 주의사항:")
    print(f"   - 이 값들을 코드에 직접 포함하지 마세요")
    print(f"   - .env 파일을 git에 커밋하지 마세요")
    print(f"   - 정기적으로 secret key들을 교체하세요")
    print(f"   - 프로덕션과 개발 환경의 키를 분리하세요")

if __name__ == "__main__":
    main()