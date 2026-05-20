# Agent Guidance: Cross-Media Recommendation Engine

## Developer Commands

### Backend (FastAPI)
- **Setup**: `cd backend && python -m venv venv && source venv/bin/activate && pip install -r requirements.txt`
- **Run**: `uvicorn main:app --reload` (from `backend/` with venv active)
- **Migrations**: 
  - Init: `alembic init alembic`
  - Generate: `alembic revision --autogenerate -m "message"`
  - Apply: `alembic upgrade head`
- **Health Check**: `GET http://localhost:8000/health`
- **API Docs**: `http://localhost:8000/docs`

### Frontend (Flutter)
- **Setup**: `cd frontend && flutter pub get`
- **Run**: `flutter run -d chrome`
- **Build**: `flutter build web`

## Architecture
- **Stack**: FastAPI (Backend) $\rightarrow$ Flutter (Frontend).
- **Layered Architecture**: Presentation $\rightarrow$ Application $\rightarrow$ Data Access $\rightarrow$ Data Storage.
- **Bounded Services**: Recommendation, Economy, Community.

## Database & State
- **PostgreSQL (Neon.tech)**: Uses `pgvector` for embeddings.
- **MongoDB (Atlas)**: Used for forum threads and nested comments (via Motor).
- **Embeddings**: `sentence-transformers/all-MiniLM-L6-v2` (384 dimensions).
- **Caching**: In-memory numpy matrix for recommendation search to avoid frequent DB hits.
- **Auth**: JWT (`python-jose`, `passlib`).

## Key Conventions
- **Environment**: Use `backend/.env` for secrets. NEVER commit `.env`.
- **Primary Keys**: Use UUIDs for all database primary keys.
- **Async**: Use `async/await` throughout the backend.
- **CORS**: If Flutter cannot connect, ensure `CORSMiddleware` is configured in `main.py`.

## Deployment
- **Backend**: Render.com (Web Service).
- **Frontend**: Firebase Hosting.
- **Keep-Alive**: `cron-job.org` pings `/health` every 14 minutes to prevent Render sleep.
