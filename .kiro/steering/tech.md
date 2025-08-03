# Technology Stack

## Backend
- **Framework**: FastAPI with Python 3.12+
- **Database**: PostgreSQL (production) / SQLite (development)
- **ORM**: SQLAlchemy with Alembic migrations
- **Cache/Message Broker**: Redis
- **Background Tasks**: Celery with Redis broker
- **Authentication**: JWT tokens with Reddit OAuth2
- **API Client**: HTTPX for async HTTP requests, PRAW for Reddit API
- **Monitoring**: Prometheus metrics with optional Grafana
- **Testing**: pytest with coverage reporting

## Frontend (Admin Dashboard)
- **Framework**: React 19 with TypeScript
- **Build Tool**: Vite
- **Styling**: Tailwind CSS v4
- **State Management**: Zustand
- **Data Fetching**: TanStack Query (React Query)
- **UI Components**: Headless UI, Heroicons, Lucide React
- **Charts**: Chart.js with react-chartjs-2
- **Testing**: Vitest with Testing Library

## Infrastructure
- **Containerization**: Docker with docker-compose
- **Development**: Local SQLite + Redis
- **Production**: PostgreSQL + Redis cluster
- **Deployment**: Railway (configured), supports Vercel/Netlify for frontend

## Common Commands

### Development Setup
```bash
# Backend setup
python3 -m venv .venv
source .venv/bin/activate  # or .venv/bin/activate.fish
pip install -r requirements.txt

# Start development server
./scripts/dev-start.sh
# or manually: uvicorn app.main:app --reload

# Database migrations
alembic upgrade head
alembic revision --autogenerate -m "description"

# Start Celery worker
celery -A app.core.celery_app worker --loglevel=info
celery -A app.core.celery_app beat --loglevel=info
```

### Frontend Setup
```bash
cd admin-dashboard
npm install
npm run dev          # Development server
npm run build        # Production build
npm run lint         # ESLint
npm run format       # Prettier
npm run test         # Vitest tests
```

### Docker Development
```bash
docker-compose up -d              # Start all services
docker-compose up -d --build      # Rebuild and start
docker-compose logs -f api        # View API logs
docker-compose down               # Stop all services
```

### Testing
```bash
# Backend tests
pytest                           # Run all tests
pytest -v --cov=app            # With coverage
pytest -m unit                 # Unit tests only
pytest -m integration          # Integration tests only

# Frontend tests
cd admin-dashboard
npm run test                    # Interactive mode
npm run test:run               # Single run
npm run test:coverage          # With coverage
```

## Code Quality Tools
- **Backend**: Black (formatting), isort (imports), flake8 (linting)
- **Frontend**: ESLint, Prettier, TypeScript strict mode
- **Git Hooks**: Husky with lint-staged for pre-commit checks