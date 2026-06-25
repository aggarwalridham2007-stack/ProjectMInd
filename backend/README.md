# ProjectMind Backend

FastAPI-based backend for ProjectMind - AI-Powered Scientific Research Intelligence Platform.

## Architecture

Follows Clean Architecture with the following layers:

```
app/
├── api/              # API routes (Controller layer)
├── core/             # Configuration, security, constants
├── domain/           # Domain entities and interfaces
├── application/      # Application services and use cases
├── infrastructure/   # External services, repositories
├── dependencies/     # Dependency injection container
├── middleware/       # Custom middleware
├── shared/           # Shared utilities and constants
└── main.py           # Application factory
```

## Core Concepts

### Service Registry
Centralized service container for dependency injection.

### Event Bus
Asynchronous event-driven architecture support.

### Repository Pattern
Abstraction for data access.

### Application Factory
Lazy initialization and configuration management.

## Development

```bash
# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env

# Run migrations
alembic upgrade head

# Start development server
uvicorn app.main:app --reload

# Run tests
pytest

# Lint
black app tests
isort app tests
flake8 app tests
mypy app
```

## API Documentation

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Health Check

```bash
curl http://localhost:8000/health
```

## Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app

# Run specific test
pytest tests/test_health.py
```
