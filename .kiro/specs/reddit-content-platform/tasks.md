# Implementation Plan

- [x] 1. 프로젝트 기본 구조 및 의존성 설정
  - FastAPI 프로젝트 구조 생성 및 기본 설정 파일 구성
  - requirements.txt에 필요한 패키지 추가 (FastAPI, Celery, SQLAlchemy, Redis, etc.)
  - Docker 설정 및 docker-compose.yml 구성
  - 환경 변수 설정 (.env 파일 및 설정 클래스)
  - _Requirements: 8.1, 8.2_

- [x] 2. 데이터베이스 모델 및 마이그레이션 설정
  - SQLAlchemy 모델 클래스 구현 (User, Keyword, Post, Comment, Metric, ProcessLog, BlogContent)
  - Alembic 마이그레이션 스크립트 생성
  - 데이터베이스 연결 및 세션 관리 유틸리티 구현
  - 모델 간 관계 설정 및 제약 조건 정의
  - _Requirements: 2.1, 4.1, 5.2_

- [x] 3. 인증 시스템 구현
  - OAuth2 인증 플로우 구현
  - JWT 토큰 생성 및 검증 로직 구현
  - 리프레시 토큰 메커니즘 구현
  - 인증 미들웨어 및 의존성 주입 설정
  - 인증 관련 API 엔드포인트 구현 (/auth/login, /auth/refresh, /auth/logout)
  - _Requirements: 1.1, 1.2, 1.3, 1.4_

- [x] 4. 키워드 관리 API 구현
  - 키워드 CRUD 서비스 로직 구현
  - 키워드 관련 API 엔드포인트 구현 (POST, GET, PUT, DELETE /keywords)
  - 키워드 중복 검증 로직 구현
  - 사용자별 키워드 필터링 구현
  - Pydantic 스키마 정의 (KeywordCreate, KeywordResponse, KeywordUpdate)
  - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5_

- [x] 5. Redis 캐시 및 세션 관리 구현
  - Redis 연결 설정 및 연결 풀 구성
  - 캐시 매니저 클래스 구현 (get, set, delete, expire)
  - 세션 관리 유틸리티 구현
  - 캐시 키 네이밍 컨벤션 정의
  - _Requirements: 3.4, 5.3, 5.4_

- [x] 6. Celery 작업 큐 설정 및 기본 태스크 구현
  - Celery 앱 설정 및 RabbitMQ 연결 구성
  - 기본 Celery 태스크 데코레이터 및 설정
  - 태스크 상태 추적 및 결과 저장 메커니즘
  - 태스크 재시도 정책 및 오류 처리 구현
  - _Requirements: 3.1, 3.3, 8.4_

- [x] 7. Reddit API 클라이언트 구현
  - Reddit API 인증 및 클라이언트 설정
  - 포스트 검색 및 데이터 수집 함수 구현
  - 댓글 수집 함수 구현
  - API 레이트 리미트 처리 및 재시도 로직
  - Reddit 데이터 파싱 및 정규화 함수
  - _Requirements: 3.1, 3.2, 3.5_

- [x] 8. 크롤링 백그라운드 태스크 구현
  - 키워드별 Reddit 포스트 크롤링 Celery 태스크
  - 크롤링된 데이터 데이터베이스 저장 로직
  - 크롤링 상태 추적 및 로그 기록
  - 크롤링 스케줄링 API 엔드포인트 구현
  - 크롤링 상태 조회 API 구현
  - _Requirements: 3.1, 3.2, 3.4_

- [x] 9. 포스트 조회 API 구현
  - 포스트 목록 조회 API (페이지네이션 포함)
  - 키워드별 포스트 필터링 기능
  - 포스트 상세 조회 API (댓글 포함)
  - 검색 및 정렬 기능 구현
  - _Requirements: 4.1, 4.2, 4.3, 4.4_

- [x] 10. TF-IDF 트렌드 분석 엔진 구현
  - TF-IDF 알고리즘 구현 (scikit-learn 활용)
  - 키워드 중요도 계산 함수
  - 트렌드 메트릭 계산 로직 (engagement score, trend velocity)
  - 트렌드 분석 Celery 태스크 구현
  - _Requirements: 5.1, 5.2_

- [x] 11. 트렌드 데이터 캐싱 및 API 구현
  - 트렌드 메트릭 Redis 캐싱 로직
  - 트렌드 데이터 조회 API 구현
  - 캐시 만료 및 갱신 메커니즘
  - 트렌드 히스토리 추적 기능
  - _Requirements: 5.2, 5.3, 5.4_

- [x] 12. 마크다운 컨텐츠 생성 엔진 구현
  - 블로그 포스트 템플릿 시스템 구현
  - 트렌드 데이터 기반 컨텐츠 생성 로직
  - 마크다운 형식 변환 및 검증
  - 컨텐츠 생성 Celery 태스크 구현
  - _Requirements: 6.1, 6.2, 6.3_

- [x] 13. 컨텐츠 관리 API 구현
  - 생성된 컨텐츠 저장 및 조회 API
  - 컨텐츠 목록 및 상세 조회 기능
  - 컨텐츠 수정 및 삭제 기능
  - 컨텐츠 생성 상태 추적 API
  - _Requirements: 6.2, 6.4_

- [x] 14. 블로그 사이트용 API 엔드포인트 구현
  - 공개 블로그 포스트 조회 API (인증 불필요)
  - 카테고리별 포스트 필터링 API
  - 포스트 검색 API (제목, 내용, 태그)
  - RSS 피드 생성 API
  - 사이트맵 생성 API
  - _Requirements: 8.1, 8.2, 8.3, 8.4_

- [x] 15. Prometheus 메트릭 수집 구현
  - FastAPI 메트릭 미들웨어 구현
  - 비즈니스 메트릭 수집 (API 응답시간, 크롤링 성공률 등)
  - Celery 태스크 메트릭 수집
  - 커스텀 메트릭 정의 및 수집
  - _Requirements: 9.1, 9.3_

- [x] 16. 구조화된 로깅 시스템 구현
  - JSON 형식 로그 포맷터 구현
  - 요청 ID 추적 및 상관관계 로깅
  - 오류 로그 분류 및 알림 시스템
  - 로그 레벨별 설정 및 필터링
  - _Requirements: 9.4, 9.5_

- [x] 17. API 문서화 및 Swagger 설정
  - FastAPI 자동 문서화 설정
  - API 스키마 및 예제 정의
  - Postman 컬렉션 생성 및 환경 설정
  - API 버전 관리 구현
  - _Requirements: 모든 API 관련 요구사항_

- [x] 18. 헬스체크 및 모니터링 엔드포인트 구현
  - 서비스 상태 확인 API (/health)
  - 데이터베이스 연결 상태 체크
  - Redis 연결 상태 체크
  - 외부 서비스 의존성 체크
  - _Requirements: 9.1, 9.2_

- [x] 19. 단위 테스트 구현
  - 인증 서비스 단위 테스트
  - 키워드 관리 서비스 테스트
  - 크롤링 로직 테스트 (모킹 포함)
  - 트렌드 분석 알고리즘 테스트
  - 컨텐츠 생성 로직 테스트
  - _Requirements: 모든 핵심 비즈니스 로직_

- [x] 20. 통합 테스트 구현
  - API 엔드포인트 통합 테스트
  - 데이터베이스 트랜잭션 테스트
  - Celery 태스크 통합 테스트
  - 외부 API 모킹 테스트
  - _Requirements: 모든 API 및 워크플로우_

- [x] 21. Docker 컨테이너화 및 배포 설정
  - 프로덕션용 Dockerfile 최적화
  - docker-compose 프로덕션 설정
  - 환경별 설정 분리 (dev, staging, prod)
  - 컨테이너 헬스체크 설정
  - _Requirements: 9.1, 9.2_

- [x] 22. GitHub Actions CI/CD 파이프라인 구현
  - 코드 린팅 및 포맷팅 체크
  - 자동 테스트 실행 워크플로우
  - 도커 이미지 빌드 및 푸시
  - 배포 자동화 스크립트
  - _Requirements: 9.1, 9.2_

- [x] 23. 성능 최적화 및 부하 테스트
  - 데이터베이스 쿼리 최적화
  - Redis 캐싱 전략 최적화
  - API 응답 시간 개선
  - Locust를 사용한 부하 테스트 스크립트 작성
  - _Requirements: 9.3_

## 관리자 대시보드 (Admin Dashboard)

- [x] 24. React 관리자 대시보드 프로젝트 설정
  - React + TypeScript + Vite 프로젝트 초기화
  - Tailwind CSS 및 UI 컴포넌트 라이브러리 설정 (Headless UI, Heroicons)
  - ESLint, Prettier 코드 품질 도구 설정
  - 환경 변수 및 API 베이스 URL 설정
  - _Requirements: 7.1_

- [x] 25. 관리자 인증 및 라우팅 시스템 구현
  - React Router 설정 및 보호된 라우트 구현
  - OAuth2 로그인 플로우 프론트엔드 구현
  - JWT 토큰 관리 (localStorage/sessionStorage)
  - 자동 토큰 갱신 및 로그아웃 처리
  - 인증 컨텍스트 및 훅 구현
  - _Requirements: 1.1, 1.2, 1.3, 7.1_

- [x] 26. 관리자 API 클라이언트 및 상태 관리 구현
  - Axios 기반 API 클라이언트 구현
  - TanStack Query를 사용한 서버 상태 관리
  - API 요청 인터셉터 (토큰 자동 첨부, 오류 처리)
  - 로딩 상태 및 오류 상태 관리
  - Zustand를 사용한 클라이언트 상태 관리
  - _Requirements: 7.2_

- [x] 27. 키워드 관리 UI 구현
  - 키워드 목록 표시 컴포넌트
  - 키워드 추가/수정/삭제 폼 구현
  - 키워드 검색 및 필터링 기능
  - 키워드별 상태 표시 (활성/비활성)
  - 실시간 키워드 유효성 검증
  - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5, 7.2_

- [x] 28. 크롤링 관리 대시보드 구현
  - 크롤링 작업 시작/중지 컨트롤
  - 크롤링 상태 실시간 모니터링
  - 크롤링 진행률 및 결과 표시
  - 크롤링 히스토리 및 로그 조회
  - 크롤링 스케줄 설정 UI
  - _Requirements: 3.1, 3.4, 7.3_

- [x] 29. 수집된 포스트 조회 UI 구현
  - 포스트 목록 테이블 (페이지네이션 포함)
  - 포스트 상세 모달 또는 페이지
  - 키워드별 포스트 필터링
  - 포스트 검색 및 정렬 기능
  - 포스트 메타데이터 표시 (점수, 댓글 수 등)
  - _Requirements: 4.1, 4.2, 4.3, 7.2_

- [x] 30. 트렌드 분석 시각화 구현
  - Chart.js를 사용한 트렌드 차트
  - 키워드별 트렌드 비교 그래프
  - TF-IDF 점수 시각화
  - 트렌드 메트릭 대시보드
  - 실시간 트렌드 업데이트
  - _Requirements: 5.1, 5.3, 7.3_

- [x] 31. 컨텐츠 생성 및 관리 UI 구현
  - 컨텐츠 생성 트리거 버튼 및 설정
  - 생성된 블로그 포스트 목록 및 미리보기
  - 마크다운 에디터 및 실시간 프리뷰
  - 컨텐츠 템플릿 선택 및 커스터마이징
  - 컨텐츠 수정 및 삭제 기능
  - _Requirements: 6.1, 6.2, 6.3, 7.4_

- [x] 32. 시스템 모니터링 대시보드 구현
  - 시스템 상태 및 헬스체크 표시
  - API 응답 시간 및 오류율 차트
  - 크롤링 성공률 및 성능 메트릭
  - 알림 및 경고 표시
  - 실시간 시스템 상태 업데이트
  - _Requirements: 9.1, 9.3, 7.3_

- [x] 33. 관리자 설정 및 프로필 관리 구현
  - 사용자 프로필 정보 표시 및 수정
  - 알림 설정 및 환경 설정
  - 테마 설정 (다크/라이트 모드)
  - 시스템 설정 관리
  - 계정 연동 상태 표시
  - _Requirements: 1.1, 7.1_

- [x] 34. 관리자 대시보드 반응형 디자인 구현
  - 모바일 친화적 레이아웃 구현
  - 터치 인터페이스 최적화
  - 반응형 테이블 및 차트
  - 모바일 네비게이션 메뉴
  - 성능 최적화 (코드 스플리팅, 레이지 로딩)
  - _Requirements: 7.1_

## 공개 블로그 사이트 (Public Blog Site)

- [x] 35. Next.js 블로그 사이트 프로젝트 설정
  - Next.js + TypeScript 프로젝트 초기화
  - Tailwind CSS v4 설정 및 디자인 시스템 구축
  - SEO 최적화 설정 (메타 태그, 구조화된 데이터)
  - 환경 변수 및 API 연결 설정
  - _Requirements: 8.1_

- [x] 36. 블로그 레이아웃 및 네비게이션 구현
  - 반응형 블로그 레이아웃 구현
  - 헤더, 푸터, 사이드바 컴포넌트
  - 카테고리 네비게이션 메뉴
  - 검색 바 및 필터링 UI
  - 다크/라이트 모드 토글
  - _Requirements: 8.1, 8.5_

- [x] 37. 블로그 포스트 목록 페이지 구현
  - 포스트 카드 컴포넌트 (제목, 요약, 썸네일, 메타데이터)
  - 페이지네이션 또는 무한 스크롤
  - 카테고리별 필터링
  - 태그별 필터링
  - 최신순/인기순 정렬
  - _Requirements: 8.1, 8.3_

- [x] 38. 블로그 포스트 상세 페이지 구현
  - 마크다운 렌더링 (MDX 또는 react-markdown)
  - 코드 하이라이팅 (Prism.js 또는 highlight.js)
  - 목차 (Table of Contents) 자동 생성
  - 소셜 공유 버튼
  - 관련 포스트 추천
  - _Requirements: 8.2_

- [x] 39. 검색 및 필터링 기능 구현
  - 전체 텍스트 검색 (제목, 내용, 태그)
  - 실시간 검색 결과 표시
  - 검색 결과 하이라이팅
  - 고급 필터 (날짜 범위, 카테고리, 태그)
  - 검색 히스토리 및 인기 검색어
  - _Requirements: 8.4_

- [x] 40. SEO 및 성능 최적화 구현
  - 메타 태그 동적 생성
  - Open Graph 및 Twitter Card 설정
  - 구조화된 데이터 (JSON-LD) 추가
  - 사이트맵 자동 생성
  - RSS 피드 생성
  - 이미지 최적화 및 레이지 로딩
  - _Requirements: 8.1, 8.5_

- [x] 41. 블로그 사이트 API 연동 구현
  - Next.js API Routes를 통한 백엔드 연동
  - ISR (Incremental Static Regeneration) 설정
  - 캐싱 전략 구현
  - 오류 처리 및 폴백 페이지
  - 로딩 상태 및 스켈레톤 UI
  - _Requirements: 8.1, 8.2_

- [x] 42. 블로그 사이트 추가 기능 구현
  - 댓글 시스템 (선택사항)
  - 뉴스레터 구독 폼
  - 소셜 미디어 연동
  - 방문자 통계 (Google Analytics)
  - 접근성 개선 (ARIA, 키보드 네비게이션)
  - _Requirements: 8.5_

## 공통 프론트엔드 작업

- [x] 43. 프론트엔드 테스트 구현
  - Jest 및 React Testing Library 설정 (관리자 대시보드)
  - Vitest 설정 (블로그 사이트)
  - 컴포넌트 단위 테스트
  - API 통신 모킹 테스트
  - E2E 테스트 (Playwright)
  - 접근성 테스트 및 개선
  - _Requirements: 코드 품질 보장_

- [x] 44. 프론트엔드 빌드 및 배포 설정
  - 관리자 대시보드 Vite 프로덕션 빌드 최적화
  - 블로그 사이트 Next.js 빌드 최적화
  - 정적 파일 압축 및 캐싱 설정
  - 환경별 빌드 설정 (dev, staging, prod)
  - GitHub Actions 프론트엔드 배포 파이프라인
  - CDN 설정 및 성능 최적화
  - _Requirements: 9.1, 9.2_

- [x] 45. 최종 통합 테스트 및 문서화
  - 전체 워크플로우 엔드투엔드 테스트
  - API 문서 최종 검토 및 업데이트
  - 관리자 대시보드 사용자 가이드 작성
  - 블로그 사이트 사용자 가이드 작성
  - 배포 가이드 및 운영 매뉴얼 작성
  - 모니터링 대시보드 설정 및 알림 구성
  - _Requirements: 모든 요구사항 통합 검증_