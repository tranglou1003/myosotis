## Myosotis (FastAPI + PostgreSQL)

This repository provides a production-ready FastAPI backend skeleton with PostgreSQL, Alembic migrations, JWT authentication, and a modular service architecture. It includes Docker support, testing setup, and static assets mounting for features such as MMSE assessment media.

### Key Features
- FastAPI application with structured modules (APIs, services, models, schemas)
- PostgreSQL (>= 14) with SQLAlchemy ORM
- Alembic for schema migrations
- JWT-based login/register, authorization guards
- User CRUD: Get Me, Update Me
- Pagination utilities
- Centralized exception handling and logging
- Pytest configuration for unit tests
- Dockerized development workflow
- Static files served at `/static`

## Project Structure

```txt
.
├── alembic/                 # Alembic migrations and env
│   └── versions/            # Auto/generated migration files
├── app/
│   ├── api/                 # API route modules (v1, v2)
│   ├── core/                # Settings, database, router, security
│   ├── db/                  # DB session helpers and seed data
│   ├── middleware/          # Custom middlewares
│   ├── models/              # SQLAlchemy models (alembic-aware)
│   ├── schemas/             # Pydantic schemas
│   ├── services/            # Business logic and DB operations
│   └── main.py              # FastAPI app factory and bootstrapping
├── static/                  # Media assets (images, audio, video)
├── docker-compose.yml       # Local dev stack (Postgres, app)
├── Dockerfile               # App image definition
├── alembic.ini              # Alembic configuration
├── logging.ini              # Logging configuration
├── pytest.ini               # Pytest config
├── requirements.txt         # Python dependencies
└── README.md
```

## Getting Started

### Prerequisites
- Python 3.10+
- Docker and Docker Compose

### Environment Variables
Create a `.env` file in the project root. Typical variables include (names may vary based on `app/core/config.py`):

```env
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=seadev
DATABASE_URL=postgresql+psycopg2://postgres:postgres@db:5432/seadev
API_PREFIX=/api
PROJECT_NAME=SeaDev Backend
DEBUG=true
BACKEND_CORS_ORIGINS=[*]
KEYCLOAK_CLIENT_ID=your-client-id
LOGGING_CONFIG_FILE=logging.ini
SEA_LION_API_KEY=YOUR_API_KEY
```

### Run with Docker
The repository ships with a ready-to-use `docker-compose.yml`:

```bash
docker compose up -d --build
```

Services provided:
- `db`: PostgreSQL 16, exposed on host port 5678
- `alembic`: Applies migrations automatically on startup
- `app`: FastAPI server on port 8777 with auto-reload

Once started, the API is available at:
- Swagger UI: http://localhost:8777/docs
- ReDoc: http://localhost:8777/re-docs
- OpenAPI JSON: http://localhost:8777/api/openapi.json (or `${API_PREFIX}/openapi.json`)

Static files (if `./static` exists) are served under `/static`, e.g. http://localhost:8777/static/

### Run Locally (without Docker)
```bash
python -m venv .venv
. .venv/bin/activate  # Windows: .venv\\Scripts\\activate
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8777 --reload
```

Ensure your local PostgreSQL is running and `DATABASE_URL` points to it.

## Database Migrations (Alembic)

This project uses Alembic for schema migrations. Common commands:

```bash
# Create a new revision (autogenerate based on SQLAlchemy models)
alembic revision --autogenerate -m "your message"

# Upgrade to the latest
alembic upgrade head

# Downgrade one step
alembic downgrade -1
```

Migrations run automatically in Docker via the `alembic` service before the app starts.

## Testing

```bash
pytest -q
```

Add tests under the `test/` directory. The project includes fixtures and basic test examples.

## Notable Modules

- `app/core/config.py`: Loads environment variables and settings
- `app/core/router.py`: Aggregates API routers and prefixes
- `app/utils/exception_handler.py`: Unified error handling
- `app/services/*`: Business logic and DB operations
- `app/models/*`: SQLAlchemy models synchronized with Alembic

## API Overview

The app includes sample routes for:
- Authentication (JWT): login/register
- User management (CRUD, Get Me, Update Me)
- MMSE Assessment endpoints and supporting media
- Chat, story, media, and other demo services

Explore all routes via Swagger UI at `/docs`.

## Deployment Notes

- Configure `LOGGING_CONFIG_FILE` for production-grade logging.
- Set `DEBUG=false` in production.
- Ensure `BACKEND_CORS_ORIGINS` matches allowed frontends.
- Use a managed PostgreSQL instance and secure secrets in your environment.

## License

This project is provided as-is. Add your preferred license terms here.

## Contact Information

Myosotis Team

📧 Email: ncminhhieu127@gmail.com  
🌐 Website: https://seadev-1.ript.vn/  
📍 Address: Ha Noi City, Vietnam
