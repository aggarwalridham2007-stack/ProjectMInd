# ProjectMind

**AI-Powered Scientific Research Intelligence Platform**

> Transform unstructured scientific literature into an interactive knowledge network capable of reasoning across multiple research papers.

## Overview

ProjectMind is an enterprise-grade AI platform designed to help researchers, students, universities, research labs, and R&D organizations understand, compare, analyze, and discover knowledge from multiple scientific research papers.

**Not a chatbot. Not a paper summarizer. Not a standard RAG application.**

An AI research analyst platform that extracts structured scientific knowledge, identifies relationships, detects contradictions, evaluates evidence quality, and discovers unexplored research opportunities.

## Project Status

🚀 **Foundation Phase** - Monorepo infrastructure, clean architecture, and base application setup.

## Tech Stack

### Frontend
- React 18
- TypeScript
- Vite
- TailwindCSS
- React Router
- Zustand
- Axios

### Backend
- FastAPI
- Python 3.12
- SQLAlchemy
- Alembic
- Pydantic v2
- JWT Authentication
- Async Support

### Databases
- PostgreSQL
- Neo4j
- ChromaDB

### Infrastructure
- Docker & Docker Compose
- GitHub Actions
- Environment Configuration

## Quick Start

### Prerequisites
- Docker & Docker Compose
- Node.js 18+ (for local frontend development)
- Python 3.12+ (for local backend development)

### Using Docker Compose

```bash
# Clone repository
git clone https://github.com/aggarwalridham2007-stack/ProjectMind.git
cd ProjectMind

# Setup environment
cp .env.example .env

# Start services
docker-compose up --build

# Access
Frontend: http://localhost:5173
Backend: http://localhost:8000
API Docs: http://localhost:8000/docs
```

### Health Checks

```bash
# Backend health
curl http://localhost:8000/health

# Frontend (via browser)
http://localhost:5173
```

## Project Structure

```
ProjectMind/
├── frontend/                 # React Application
│   ├── src/
│   │   ├── api/            # API clients
│   │   ├── components/     # React components
│   │   ├── pages/          # Page components
│   │   ├── store/          # Zustand stores
│   │   ├── styles/         # Global styles
│   │   ├── types/          # TypeScript types
│   │   ├── utils/          # Utilities
│   │   └── App.tsx
│   ├── public/
│   ├── vite.config.ts
│   ├── tsconfig.json
│   ├── tailwind.config.js
│   └── package.json
│
├── backend/                  # FastAPI Application
│   ├── app/
│   │   ├── api/            # API routes
│   │   ├── core/           # Configuration, security
│   │   ├── db/             # Database
│   │   ├── models/         # SQLAlchemy models
│   │   ├── schemas/        # Pydantic schemas
│   │   ├── services/       # Business logic
│   │   ├── dependencies/   # DI container
│   │   ├── middleware/     # Custom middleware
│   │   └── main.py         # Entry point
│   ├── migrations/         # Alembic migrations
│   ├── tests/              # pytest tests
│   ├── requirements.txt
│   ├── pyproject.toml
│   ├── alembic.ini
│   └── Dockerfile
│
├── docker-compose.yml
├── .env.example
├── .gitignore
└── README.md
```

## Documentation

- [Backend Setup](./backend/README.md)
- [Frontend Setup](./frontend/README.md)
- [Architecture](./docs/ARCHITECTURE.md)
- [API Documentation](./backend/docs/API.md)

## Development

### Backend Development

```bash
cd backend

# Install dependencies
pip install -r requirements.txt

# Run migrations
alembic upgrade head

# Start development server
uvicorn app.main:app --reload

# Run tests
pytest
```

### Frontend Development

```bash
cd frontend

# Install dependencies
npm install

# Start dev server
npm run dev

# Run tests
npm run test

# Build
npm run build
```

## CI/CD

GitHub Actions workflows handle:
- Linting & formatting
- Unit & integration tests
- Security scanning
- Build verification
- Deployment

See `.github/workflows/` for configuration.

## License

MIT

## Contact

Built with ❤️ as an enterprise-grade AI research platform.

---

**ProjectMind** - Where Science Meets Intelligence
