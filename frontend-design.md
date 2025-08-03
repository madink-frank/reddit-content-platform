# Reddit Content Platform - Frontend Design Document

## Overview

Reddit Content Platform의 프론트엔드는 사용자가 키워드를 관리하고, 크롤링된 데이터를 분석하며, AI 기반 콘텐츠를 생성할 수 있는 직관적이고 반응형 웹 애플리케이션입니다. 현대적인 React 기반 SPA(Single Page Application)로 구현되며, 실시간 데이터 업데이트와 풍부한 시각화 기능을 제공합니다.

## Design Principles

### 1. 사용자 중심 설계 (User-Centric Design)
- 직관적인 네비게이션과 명확한 정보 계층구조
- 최소한의 클릭으로 원하는 기능에 접근
- 사용자 피드백을 통한 지속적인 UX 개선

### 2. 반응형 디자인 (Responsive Design)
- 모바일, 태블릿, 데스크톱 모든 디바이스 지원
- Progressive Web App (PWA) 기능 제공
- 터치 친화적인 인터페이스

### 3. 실시간성 (Real-time Updates)
- WebSocket을 통한 실시간 크롤링 상태 업데이트
- 실시간 트렌드 데이터 시각화
- 즉시 반영되는 사용자 액션

### 4. 접근성 (Accessibility)
- WCAG 2.1 AA 준수
- 키보드 네비게이션 지원
- 스크린 리더 호환성

## Technology Stack

### Core Framework
- **React 18** - 컴포넌트 기반 UI 라이브러리
- **TypeScript** - 타입 안전성과 개발 생산성
- **Vite** - 빠른 개발 서버와 빌드 도구

### State Management
- **Zustand** - 경량 상태 관리 라이브러리
- **React Query (TanStack Query)** - 서버 상태 관리 및 캐싱

### Routing
- **React Router v6** - 클라이언트 사이드 라우팅

### UI Components & Styling
- **Tailwind CSS** - 유틸리티 기반 CSS 프레임워크
- **Headless UI** - 접근성을 고려한 컴포넌트 라이브러리
- **Heroicons** - 일관된 아이콘 시스템

### Data Visualization
- **Chart.js + React-Chartjs-2** - 차트 및 그래프
- **D3.js** - 복잡한 데이터 시각화
- **React-Table** - 고성능 테이블 컴포넌트

### Real-time Communication
- **Socket.IO Client** - WebSocket 통신
- **Server-Sent Events** - 실시간 업데이트

### Development Tools
- **ESLint + Prettier** - 코드 품질 및 포맷팅
- **Husky + lint-staged** - Git hooks
- **Storybook** - 컴포넌트 개발 및 문서화

### Testing
- **Vitest** - 단위 테스트
- **Testing Library** - 컴포넌트 테스트
- **Playwright** - E2E 테스트

### Deployment
- **Vercel** - 프론트엔드 호스팅 및 배포
- **Docker** - 컨테이너화 (선택적)

## Architecture

### Component Architecture

```
src/
├── components/           # 재사용 가능한 UI 컴포넌트
│   ├── ui/              # 기본 UI 컴포넌트 (Button, Input, Modal 등)
│   ├── layout/          # 레이아웃 컴포넌트 (Header, Sidebar, Footer)
│   ├── charts/          # 차트 및 시각화 컴포넌트
│   └── forms/           # 폼 관련 컴포넌트
├── pages/               # 페이지 컴포넌트
│   ├── auth/           # 인증 관련 페이지
│   ├── dashboard/      # 대시보드
│   ├── keywords/       # 키워드 관리
│   ├── posts/          # 포스트 조회
│   ├── analytics/      # 분석 및 통계
│   └── content/        # 콘텐츠 생성
├── hooks/               # 커스텀 React hooks
├── services/            # API 서비스 레이어
├── stores/              # 상태 관리 (Zustand)
├── types/               # TypeScript 타입 정의
├── utils/               # 유틸리티 함수
└── constants/           # 상수 정의
```

### State Management Architecture

```typescript
// 전역 상태 구조
interface AppState {
  auth: AuthState;
  keywords: KeywordState;
  posts: PostState;
  analytics: AnalyticsState;
  content: ContentState;
  ui: UIState;
}

interface AuthState {
  user: User | null;
  isAuthenticated: boolean;
  tokens: TokenPair | null;
  isLoading: boolean;
}

interface KeywordState {
  keywords: Keyword[];
  selectedKeywords: string[];
  isLoading: boolean;
  error: string | null;
}
```

## User Interface Design

### Design System

#### Color Palette
```css
:root {
  /* Primary Colors */
  --color-primary-50: #eff6ff;
  --color-primary-500: #3b82f6;
  --color-primary-600: #2563eb;
  --color-primary-700: #1d4ed8;
  
  /* Secondary Colors */
  --color-secondary-50: #f8fafc;
  --color-secondary-500: #64748b;
  --color-secondary-600: #475569;
  
  /* Success/Error/Warning */
  --color-success: #10b981;
  --color-error: #ef4444;
  --color-warning: #f59e0b;
  
  /* Neutral Colors */
  --color-gray-50: #f9fafb;
  --color-gray-100: #f3f4f6;
  --color-gray-900: #111827;
}
```

#### Typography
```css
/* Font Stack */
font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;

/* Type Scale */
--text-xs: 0.75rem;    /* 12px */
--text-sm: 0.875rem;   /* 14px */
--text-base: 1rem;     /* 16px */
--text-lg: 1.125rem;   /* 18px */
--text-xl: 1.25rem;    /* 20px */
--text-2xl: 1.5rem;    /* 24px */
--text-3xl: 1.875rem;  /* 30px */
--text-4xl: 2.25rem;   /* 36px */
```

#### Spacing System
```css
/* Spacing Scale (Tailwind-based) */
--space-1: 0.25rem;   /* 4px */
--space-2: 0.5rem;    /* 8px */
--space-4: 1rem;      /* 16px */
--space-6: 1.5rem;    /* 24px */
--space-8: 2rem;      /* 32px */
--space-12: 3rem;     /* 48px */
--space-16: 4rem;     /* 64px */
```

### Layout Structure

#### Main Layout
```
┌─────────────────────────────────────────────────────────┐
│                    Header/Navigation                     │
├─────────────────────────────────────────────────────────┤
│          │                                              │
│          │                                              │
│ Sidebar  │              Main Content                    │
│          │                                              │
│          │                                              │
├─────────────────────────────────────────────────────────┤
│                       Footer                            │
└─────────────────────────────────────────────────────────┘
```

#### Responsive Breakpoints
```css
/* Mobile First Approach */
--breakpoint-sm: 640px;   /* Small devices */
--breakpoint-md: 768px;   /* Medium devices */
--breakpoint-lg: 1024px;  /* Large devices */
--breakpoint-xl: 1280px;  /* Extra large devices */
--breakpoint-2xl: 1536px; /* 2X large devices */
```

## Page Specifications

### 1. Authentication Pages

#### Login Page (`/login`)
**목적**: Reddit OAuth2를 통한 사용자 인증

**구성 요소**:
- Reddit 로그인 버튼
- 로딩 상태 표시
- 에러 메시지 표시
- 서비스 소개 섹션

**기능**:
- Reddit OAuth2 인증 플로우
- JWT 토큰 저장
- 자동 리다이렉트 (인증 후 대시보드로)

#### Callback Page (`/auth/callback`)
**목적**: OAuth2 콜백 처리

**구성 요소**:
- 로딩 스피너
- 인증 처리 상태 메시지

**기능**:
- Authorization code 처리
- 토큰 교환 및 저장
- 사용자 정보 가져오기

### 2. Dashboard (`/dashboard`)

**목적**: 전체 시스템 현황을 한눈에 파악

**구성 요소**:
```
┌─────────────────────────────────────────────────────────┐
│                    Welcome Message                      │
├─────────────────┬─────────────────┬─────────────────────┤
│   Active        │   Total Posts   │   Trending          │
│   Keywords      │   Collected     │   Keywords          │
│   Card          │   Card          │   Card              │
├─────────────────┴─────────────────┴─────────────────────┤
│                Recent Activity Feed                     │
├─────────────────────────────────────────────────────────┤
│              Quick Actions Section                      │
│  [Add Keyword] [Start Crawling] [Generate Content]     │
├─────────────────────────────────────────────────────────┤
│                Trending Topics Chart                    │
└─────────────────────────────────────────────────────────┘
```

**기능**:
- 실시간 통계 카드
- 최근 활동 피드
- 빠른 액션 버튼
- 트렌딩 토픽 시각화

### 3. Keywords Management (`/keywords`)

**목적**: 키워드 등록, 수정, 삭제 및 관리

**구성 요소**:
```
┌─────────────────────────────────────────────────────────┐
│  [+ Add Keyword]                    [Search] [Filter]   │
├─────────────────────────────────────────────────────────┤
│ ┌─────────────────────────────────────────────────────┐ │
│ │ Keyword: "AI Technology"                            │ │
│ │ Description: AI and machine learning trends         │ │
│ │ Posts: 1,234 | Last Updated: 2 hours ago          │ │
│ │ Status: ● Active    [Edit] [Delete] [View Posts]   │ │
│ └─────────────────────────────────────────────────────┘ │
│ ┌─────────────────────────────────────────────────────┐ │
│ │ Keyword: "Cryptocurrency"                           │ │
│ │ Description: Crypto market and blockchain news      │ │
│ │ Posts: 856 | Last Updated: 1 hour ago             │ │
│ │ Status: ● Active    [Edit] [Delete] [View Posts]   │ │
│ └─────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────┘
```

**기능**:
- 키워드 CRUD 작업
- 실시간 검색 및 필터링
- 키워드별 통계 표시
- 벌크 액션 (일괄 삭제, 활성화/비활성화)

### 4. Posts Explorer (`/posts`)

**목적**: 수집된 Reddit 포스트 탐색 및 검색

**구성 요소**:
```
┌─────────────────────────────────────────────────────────┐
│ Search: [________________] [🔍] Filters: [▼] Sort: [▼]  │
├─────────────────────────────────────────────────────────┤
│ ┌─────────────────────────────────────────────────────┐ │
│ │ 🔥 r/technology • 2 hours ago • 1.2k upvotes       │ │
│ │ "Revolutionary AI breakthrough changes everything"   │ │
│ │ This new AI model can generate code, write essays.. │ │
│ │ 💬 234 comments | 🏷️ AI Technology | [View Full]    │ │
│ └─────────────────────────────────────────────────────┘ │
│ ┌─────────────────────────────────────────────────────┐ │
│ │ 📈 r/investing • 4 hours ago • 856 upvotes         │ │
│ │ "Crypto market shows signs of recovery"             │ │
│ │ After weeks of decline, major cryptocurrencies...   │ │
│ │ 💬 156 comments | 🏷️ Cryptocurrency | [View Full]   │ │
│ └─────────────────────────────────────────────────────┘ │
├─────────────────────────────────────────────────────────┤
│              [Previous] Page 1 of 45 [Next]            │
└─────────────────────────────────────────────────────────┘
```

**기능**:
- 고급 검색 및 필터링
- 정렬 옵션 (날짜, 인기도, 댓글 수)
- 무한 스크롤 또는 페이지네이션
- 포스트 상세 모달
- 즐겨찾기 및 태그 기능

### 5. Analytics Dashboard (`/analytics`)

**목적**: 트렌드 분석 및 통계 시각화

**구성 요소**:
```
┌─────────────────────────────────────────────────────────┐
│ Time Range: [Last 7 days ▼] Keywords: [All ▼]         │
├─────────────────────────────────────────────────────────┤
│ ┌─────────────────────┐ ┌─────────────────────────────┐ │
│ │   Trending Topics   │ │      Keyword Performance    │ │
│ │                     │ │                             │ │
│ │   📊 Line Chart     │ │     📊 Bar Chart            │ │
│ │                     │ │                             │ │
│ └─────────────────────┘ └─────────────────────────────┘ │
├─────────────────────────────────────────────────────────┤
│ ┌─────────────────────┐ ┌─────────────────────────────┐ │
│ │   Subreddit         │ │      Sentiment Analysis     │ │
│ │   Distribution      │ │                             │ │
│ │   🥧 Pie Chart      │ │     📊 Sentiment Chart      │ │
│ │                     │ │                             │ │
│ └─────────────────────┘ └─────────────────────────────┘ │
├─────────────────────────────────────────────────────────┤
│                Top Performing Posts                     │
│ [Table with sortable columns: Title, Score, Comments]   │
└─────────────────────────────────────────────────────────┘
```

**기능**:
- 인터랙티브 차트 및 그래프
- 시간 범위 선택
- 키워드별 필터링
- 데이터 내보내기 (CSV, PDF)
- 실시간 데이터 업데이트

### 6. Content Generation (`/content`)

**목적**: AI 기반 콘텐츠 생성 및 관리

**구성 요소**:
```
┌─────────────────────────────────────────────────────────┐
│                  Content Generation                     │
├─────────────────────────────────────────────────────────┤
│ Content Type: [Blog Post ▼]                           │
│ Keywords: [Select keywords...] [AI Technology] [×]      │
│ Template: [Tech Blog Template ▼]                       │
│ Custom Prompt: [Optional custom instructions...]       │
│                                                         │
│ [Generate Content] [Save as Draft]                     │
├─────────────────────────────────────────────────────────┤
│                Generated Content Preview                │
│ ┌─────────────────────────────────────────────────────┐ │
│ │ # The Future of AI Technology                       │ │
│ │                                                     │ │
│ │ Based on recent Reddit discussions, AI technology   │ │
│ │ is experiencing unprecedented growth...              │ │
│ │                                                     │ │
│ │ [Edit] [Copy] [Download] [Publish]                 │ │
│ └─────────────────────────────────────────────────────┘ │
├─────────────────────────────────────────────────────────┤
│                Previous Content                         │
│ [List of previously generated content with actions]     │
└─────────────────────────────────────────────────────────┘
```

**기능**:
- 다양한 콘텐츠 타입 선택
- 키워드 기반 콘텐츠 생성
- 템플릿 시스템
- 실시간 미리보기
- 콘텐츠 편집 및 저장
- 생성 히스토리 관리

### 7. Crawling Status (`/crawling`)

**목적**: 크롤링 작업 모니터링 및 제어

**구성 요소**:
```
┌─────────────────────────────────────────────────────────┐
│ Crawling Status: ● Running | Last Update: 2 min ago    │
├─────────────────────────────────────────────────────────┤
│ ┌─────────────────────────────────────────────────────┐ │
│ │ Current Job: "AI Technology" keyword crawling       │ │
│ │ Progress: ████████████░░░░ 75% (750/1000 posts)    │ │
│ │ ETA: 5 minutes | [Pause] [Stop]                    │ │
│ └─────────────────────────────────────────────────────┘ │
├─────────────────────────────────────────────────────────┤
│                    Job Queue                           │
│ 1. ⏳ "Cryptocurrency" - Waiting                       │
│ 2. ⏳ "Machine Learning" - Waiting                     │
│ 3. ⏳ "Web Development" - Waiting                      │
│                                                         │
│ [Add New Job] [Clear Queue]                            │
├─────────────────────────────────────────────────────────┤
│                  Recent Jobs History                    │
│ ✅ "AI Technology" - Completed (1,234 posts) - 1h ago  │
│ ✅ "Blockchain" - Completed (856 posts) - 3h ago       │
│ ❌ "NFT" - Failed (Rate limit exceeded) - 5h ago       │
└─────────────────────────────────────────────────────────┘
```

**기능**:
- 실시간 크롤링 상태 모니터링
- 진행률 표시 및 ETA 계산
- 작업 큐 관리
- 크롤링 제어 (시작, 일시정지, 중지)
- 작업 히스토리 및 로그

## Component Specifications

### Core UI Components

#### Button Component
```typescript
interface ButtonProps {
  variant: 'primary' | 'secondary' | 'outline' | 'ghost' | 'danger';
  size: 'sm' | 'md' | 'lg';
  loading?: boolean;
  disabled?: boolean;
  icon?: React.ReactNode;
  children: React.ReactNode;
  onClick?: () => void;
}
```

#### Input Component
```typescript
interface InputProps {
  type: 'text' | 'email' | 'password' | 'search' | 'number';
  placeholder?: string;
  value: string;
  onChange: (value: string) => void;
  error?: string;
  disabled?: boolean;
  icon?: React.ReactNode;
  label?: string;
}
```

#### Modal Component
```typescript
interface ModalProps {
  isOpen: boolean;
  onClose: () => void;
  title: string;
  size: 'sm' | 'md' | 'lg' | 'xl';
  children: React.ReactNode;
  footer?: React.ReactNode;
}
```

### Data Display Components

#### DataTable Component
```typescript
interface DataTableProps<T> {
  data: T[];
  columns: Column<T>[];
  loading?: boolean;
  pagination?: PaginationConfig;
  sorting?: SortingConfig;
  filtering?: FilteringConfig;
  selection?: SelectionConfig;
}
```

#### Chart Components
```typescript
interface LineChartProps {
  data: ChartData[];
  xAxis: string;
  yAxis: string;
  title?: string;
  height?: number;
  interactive?: boolean;
}

interface BarChartProps {
  data: ChartData[];
  xAxis: string;
  yAxis: string;
  title?: string;
  horizontal?: boolean;
}
```

### Form Components

#### KeywordForm Component
```typescript
interface KeywordFormProps {
  initialData?: Keyword;
  onSubmit: (data: KeywordFormData) => void;
  onCancel: () => void;
  loading?: boolean;
}
```

#### ContentGenerationForm Component
```typescript
interface ContentGenerationFormProps {
  keywords: Keyword[];
  templates: Template[];
  onGenerate: (config: GenerationConfig) => void;
  loading?: boolean;
}
```

## API Integration

### Service Layer Architecture

```typescript
// API Client 설정
class ApiClient {
  private baseURL: string;
  private token: string | null;

  constructor(baseURL: string) {
    this.baseURL = baseURL;
    this.token = localStorage.getItem('access_token');
  }

  async request<T>(endpoint: string, options?: RequestOptions): Promise<T> {
    // HTTP 요청 로직
    // 토큰 자동 갱신
    // 에러 처리
  }
}

// 서비스 클래스들
class AuthService {
  async login(code: string, state: string): Promise<TokenResponse> {}
  async refresh(): Promise<TokenResponse> {}
  async logout(): Promise<void> {}
}

class KeywordService {
  async getKeywords(): Promise<Keyword[]> {}
  async createKeyword(data: KeywordCreate): Promise<Keyword> {}
  async updateKeyword(id: number, data: KeywordUpdate): Promise<Keyword> {}
  async deleteKeyword(id: number): Promise<void> {}
}

class PostService {
  async getPosts(params: PostSearchParams): Promise<PostResponse> {}
  async getPost(id: number): Promise<Post> {}
  async searchPosts(query: string): Promise<PostResponse> {}
}
```

### React Query Integration

```typescript
// Custom hooks for API calls
export const useKeywords = () => {
  return useQuery({
    queryKey: ['keywords'],
    queryFn: () => keywordService.getKeywords(),
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
};

export const useCreateKeyword = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (data: KeywordCreate) => keywordService.createKeyword(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['keywords'] });
    },
  });
};

export const usePosts = (params: PostSearchParams) => {
  return useInfiniteQuery({
    queryKey: ['posts', params],
    queryFn: ({ pageParam = 1 }) => 
      postService.getPosts({ ...params, page: pageParam }),
    getNextPageParam: (lastPage) => lastPage.nextPage,
  });
};
```

## Real-time Features

### WebSocket Integration

```typescript
// WebSocket 서비스
class WebSocketService {
  private socket: Socket;

  constructor() {
    this.socket = io(process.env.VITE_WS_URL);
    this.setupEventListeners();
  }

  private setupEventListeners() {
    this.socket.on('crawling_status', (data) => {
      // 크롤링 상태 업데이트
    });

    this.socket.on('new_post', (data) => {
      // 새 포스트 알림
    });

    this.socket.on('analytics_update', (data) => {
      // 분석 데이터 업데이트
    });
  }

  subscribeToCrawlingUpdates(keywordId: number) {
    this.socket.emit('subscribe_crawling', { keywordId });
  }
}

// React Hook
export const useWebSocket = () => {
  const [socket] = useState(() => new WebSocketService());
  
  useEffect(() => {
    return () => socket.disconnect();
  }, []);

  return socket;
};
```

### Server-Sent Events

```typescript
// SSE Hook for real-time updates
export const useServerSentEvents = (endpoint: string) => {
  const [data, setData] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    const eventSource = new EventSource(`${API_BASE_URL}${endpoint}`);

    eventSource.onmessage = (event) => {
      setData(JSON.parse(event.data));
    };

    eventSource.onerror = (error) => {
      setError(error);
    };

    return () => eventSource.close();
  }, [endpoint]);

  return { data, error };
};
```

## Performance Optimization

### Code Splitting

```typescript
// Lazy loading for pages
const Dashboard = lazy(() => import('../pages/Dashboard'));
const Keywords = lazy(() => import('../pages/Keywords'));
const Posts = lazy(() => import('../pages/Posts'));
const Analytics = lazy(() => import('../pages/Analytics'));
const Content = lazy(() => import('../pages/Content'));

// Route configuration
const routes = [
  {
    path: '/dashboard',
    element: (
      <Suspense fallback={<PageLoader />}>
        <Dashboard />
      </Suspense>
    ),
  },
  // ... other routes
];
```

### Memoization

```typescript
// Component memoization
const PostCard = memo(({ post }: { post: Post }) => {
  return (
    <div className="post-card">
      {/* Post content */}
    </div>
  );
});

// Hook memoization
const useFilteredPosts = (posts: Post[], filters: FilterConfig) => {
  return useMemo(() => {
    return posts.filter(post => {
      // Filtering logic
    });
  }, [posts, filters]);
};
```

### Virtual Scrolling

```typescript
// Virtual list for large datasets
import { FixedSizeList as List } from 'react-window';

const PostList = ({ posts }: { posts: Post[] }) => {
  const Row = ({ index, style }: { index: number; style: CSSProperties }) => (
    <div style={style}>
      <PostCard post={posts[index]} />
    </div>
  );

  return (
    <List
      height={600}
      itemCount={posts.length}
      itemSize={120}
      width="100%"
    >
      {Row}
    </List>
  );
};
```

## Testing Strategy

### Unit Testing

```typescript
// Component testing
describe('KeywordForm', () => {
  it('should submit form with valid data', async () => {
    const mockSubmit = vi.fn();
    render(<KeywordForm onSubmit={mockSubmit} />);
    
    await user.type(screen.getByLabelText(/keyword/i), 'AI Technology');
    await user.click(screen.getByRole('button', { name: /submit/i }));
    
    expect(mockSubmit).toHaveBeenCalledWith({
      keyword: 'AI Technology',
    });
  });
});

// Hook testing
describe('useKeywords', () => {
  it('should fetch keywords successfully', async () => {
    const { result } = renderHook(() => useKeywords());
    
    await waitFor(() => {
      expect(result.current.isSuccess).toBe(true);
    });
    
    expect(result.current.data).toHaveLength(3);
  });
});
```

### Integration Testing

```typescript
// API integration testing
describe('Keyword Management Flow', () => {
  it('should create, edit, and delete keyword', async () => {
    render(<KeywordManagement />);
    
    // Create keyword
    await user.click(screen.getByText(/add keyword/i));
    await user.type(screen.getByLabelText(/keyword/i), 'Test Keyword');
    await user.click(screen.getByText(/save/i));
    
    // Verify creation
    expect(await screen.findByText('Test Keyword')).toBeInTheDocument();
    
    // Edit keyword
    await user.click(screen.getByText(/edit/i));
    await user.clear(screen.getByLabelText(/keyword/i));
    await user.type(screen.getByLabelText(/keyword/i), 'Updated Keyword');
    await user.click(screen.getByText(/save/i));
    
    // Verify update
    expect(await screen.findByText('Updated Keyword')).toBeInTheDocument();
    
    // Delete keyword
    await user.click(screen.getByText(/delete/i));
    await user.click(screen.getByText(/confirm/i));
    
    // Verify deletion
    expect(screen.queryByText('Updated Keyword')).not.toBeInTheDocument();
  });
});
```

### E2E Testing

```typescript
// Playwright E2E tests
test('complete user workflow', async ({ page }) => {
  // Login
  await page.goto('/login');
  await page.click('[data-testid="reddit-login"]');
  await page.waitForURL('/dashboard');
  
  // Add keyword
  await page.goto('/keywords');
  await page.click('[data-testid="add-keyword"]');
  await page.fill('[data-testid="keyword-input"]', 'AI Technology');
  await page.click('[data-testid="save-keyword"]');
  
  // Start crawling
  await page.goto('/crawling');
  await page.click('[data-testid="start-crawling"]');
  
  // Wait for crawling to complete
  await page.waitForSelector('[data-testid="crawling-complete"]');
  
  // View results
  await page.goto('/posts');
  await expect(page.locator('[data-testid="post-item"]')).toHaveCount.greaterThan(0);
  
  // Generate content
  await page.goto('/content');
  await page.selectOption('[data-testid="content-type"]', 'blog');
  await page.click('[data-testid="generate-content"]');
  
  // Verify content generation
  await expect(page.locator('[data-testid="generated-content"]')).toBeVisible();
});
```

## Deployment Configuration

### Vercel Configuration

```json
// vercel.json
{
  "framework": "vite",
  "buildCommand": "npm run build",
  "outputDirectory": "dist",
  "installCommand": "npm install",
  "devCommand": "npm run dev",
  "env": {
    "VITE_API_URL": "@api-url",
    "VITE_WS_URL": "@ws-url"
  },
  "build": {
    "env": {
      "VITE_API_URL": "https://your-api-domain.railway.app",
      "VITE_WS_URL": "wss://your-api-domain.railway.app"
    }
  },
  "rewrites": [
    {
      "source": "/((?!api/.*).*)",
      "destination": "/index.html"
    }
  ]
}
```

### Environment Configuration

```typescript
// env.d.ts
interface ImportMetaEnv {
  readonly VITE_API_URL: string;
  readonly VITE_WS_URL: string;
  readonly VITE_REDDIT_CLIENT_ID: string;
  readonly VITE_APP_NAME: string;
  readonly VITE_APP_VERSION: string;
}

// config.ts
export const config = {
  apiUrl: import.meta.env.VITE_API_URL || 'http://localhost:8000',
  wsUrl: import.meta.env.VITE_WS_URL || 'ws://localhost:8000',
  redditClientId: import.meta.env.VITE_REDDIT_CLIENT_ID,
  appName: import.meta.env.VITE_APP_NAME || 'Reddit Content Platform',
  appVersion: import.meta.env.VITE_APP_VERSION || '1.0.0',
};
```

### Docker Configuration (Optional)

```dockerfile
# Dockerfile
FROM node:18-alpine as builder

WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production

COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/nginx.conf

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

## Security Considerations

### Authentication & Authorization

```typescript
// Token management
class TokenManager {
  private static readonly ACCESS_TOKEN_KEY = 'access_token';
  private static readonly REFRESH_TOKEN_KEY = 'refresh_token';

  static setTokens(tokens: TokenPair) {
    localStorage.setItem(this.ACCESS_TOKEN_KEY, tokens.accessToken);
    localStorage.setItem(this.REFRESH_TOKEN_KEY, tokens.refreshToken);
  }

  static getAccessToken(): string | null {
    return localStorage.getItem(this.ACCESS_TOKEN_KEY);
  }

  static clearTokens() {
    localStorage.removeItem(this.ACCESS_TOKEN_KEY);
    localStorage.removeItem(this.REFRESH_TOKEN_KEY);
  }

  static isTokenExpired(token: string): boolean {
    try {
      const payload = JSON.parse(atob(token.split('.')[1]));
      return payload.exp * 1000 < Date.now();
    } catch {
      return true;
    }
  }
}

// Protected route component
const ProtectedRoute = ({ children }: { children: React.ReactNode }) => {
  const { isAuthenticated, isLoading } = useAuth();

  if (isLoading) {
    return <PageLoader />;
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  return <>{children}</>;
};
```

### Input Validation & Sanitization

```typescript
// Input sanitization
import DOMPurify from 'dompurify';

const sanitizeInput = (input: string): string => {
  return DOMPurify.sanitize(input, { ALLOWED_TAGS: [] });
};

// Form validation
const keywordSchema = z.object({
  keyword: z.string()
    .min(1, 'Keyword is required')
    .max(100, 'Keyword must be less than 100 characters')
    .regex(/^[a-zA-Z0-9\s-_]+$/, 'Invalid characters in keyword'),
  description: z.string()
    .max(500, 'Description must be less than 500 characters')
    .optional(),
});
```

### Content Security Policy

```html
<!-- index.html -->
<meta http-equiv="Content-Security-Policy" 
      content="default-src 'self'; 
               script-src 'self' 'unsafe-inline'; 
               style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; 
               font-src 'self' https://fonts.gstatic.com; 
               img-src 'self' data: https:; 
               connect-src 'self' https://your-api-domain.railway.app wss://your-api-domain.railway.app;">
```

## Accessibility Features

### ARIA Labels and Roles

```typescript
// Accessible components
const Button = ({ children, ...props }: ButtonProps) => {
  return (
    <button
      role="button"
      aria-label={props['aria-label']}
      aria-describedby={props['aria-describedby']}
      {...props}
    >
      {children}
    </button>
  );
};

const Modal = ({ isOpen, onClose, title, children }: ModalProps) => {
  return (
    <div
      role="dialog"
      aria-modal="true"
      aria-labelledby="modal-title"
      aria-hidden={!isOpen}
    >
      <h2 id="modal-title">{title}</h2>
      {children}
    </div>
  );
};
```

### Keyboard Navigation

```typescript
// Keyboard navigation hook
const useKeyboardNavigation = (items: any[], onSelect: (item: any) => void) => {
  const [selectedIndex, setSelectedIndex] = useState(0);

  useEffect(() => {
    const handleKeyDown = (event: KeyboardEvent) => {
      switch (event.key) {
        case 'ArrowDown':
          event.preventDefault();
          setSelectedIndex(prev => Math.min(prev + 1, items.length - 1));
          break;
        case 'ArrowUp':
          event.preventDefault();
          setSelectedIndex(prev => Math.max(prev - 1, 0));
          break;
        case 'Enter':
          event.preventDefault();
          onSelect(items[selectedIndex]);
          break;
      }
    };

    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, [items, selectedIndex, onSelect]);

  return selectedIndex;
};
```

### Screen Reader Support

```typescript
// Screen reader announcements
const useScreenReader = () => {
  const announce = (message: string, priority: 'polite' | 'assertive' = 'polite') => {
    const announcement = document.createElement('div');
    announcement.setAttribute('aria-live', priority);
    announcement.setAttribute('aria-atomic', 'true');
    announcement.className = 'sr-only';
    announcement.textContent = message;
    
    document.body.appendChild(announcement);
    
    setTimeout(() => {
      document.body.removeChild(announcement);
    }, 1000);
  };

  return { announce };
};
```

이 프론트엔드 설계 문서는 Reddit Content Platform의 사용자 인터페이스를 위한 포괄적인 가이드를 제공합니다. 다음 단계로 실제 구현을 시작할 준비가 되었습니다.