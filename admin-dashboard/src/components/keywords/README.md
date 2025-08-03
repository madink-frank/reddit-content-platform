# Keyword Management UI Components

This directory contains the implementation of the keyword management UI components for task 27.

## Components

### KeywordList
- **Location**: `KeywordList.tsx`
- **Purpose**: Displays a list of keywords with search, filtering, and management capabilities
- **Features**:
  - Search functionality with real-time filtering
  - Filter by status (all/active/inactive)
  - Toggle keyword active/inactive status
  - Edit and delete keywords
  - Empty state handling
  - Loading state handling
  - Responsive design

### KeywordForm
- **Location**: `KeywordForm.tsx`
- **Purpose**: Modal form for creating and editing keywords
- **Features**:
  - Create new keywords
  - Edit existing keywords
  - Real-time validation
  - Character restrictions (letters, numbers, spaces, hyphens, underscores)
  - Length validation (2-100 characters)
  - Active/inactive status toggle (for editing)
  - Loading states
  - Error handling

### KeywordsPage
- **Location**: `../pages/KeywordsPage.tsx`
- **Purpose**: Main page component that integrates the keyword management components
- **Features**:
  - State management for search and filters
  - Modal state management
  - Error handling
  - Integration with React Query hooks

## Key Features Implemented

✅ **키워드 목록 표시 컴포넌트** - KeywordList component displays all keywords in a clean, organized list

✅ **키워드 추가/수정/삭제 폼 구현** - KeywordForm handles create, update operations with proper validation

✅ **키워드 검색 및 필터링 기능** - Real-time search and status-based filtering

✅ **키워드별 상태 표시 (활성/비활성)** - Visual status indicators and toggle switches

✅ **실시간 키워드 유효성 검증** - Real-time validation with user-friendly error messages

## Requirements Satisfied

- **2.1**: Keyword creation and storage
- **2.2**: Keyword listing and retrieval
- **2.3**: Keyword updates and modifications
- **2.4**: Keyword deletion
- **2.5**: Keyword validation and duplicate prevention
- **7.2**: Admin dashboard interface for keyword management

## Usage

```tsx
import { KeywordsPage } from '../pages/KeywordsPage';

// The KeywordsPage component handles all keyword management functionality
<KeywordsPage />
```

## Testing

The components are fully tested with:
- Unit tests for individual components
- Integration tests for user interactions
- Validation tests for form inputs
- Loading and error state tests

Run tests with:
```bash
npm run test -- src/test/keywords.test.tsx --run
```

## Dependencies

- React 19
- TypeScript
- Tailwind CSS
- Headless UI (for Switch component)
- Heroicons (for icons)
- TanStack Query (for data fetching)
- Zustand (for state management)

## Accessibility

- Proper ARIA labels and roles
- Keyboard navigation support
- Screen reader friendly
- Focus management
- Color contrast compliance