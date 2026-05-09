# cross-media-recommendation-engine

# Project Setup Guide for New Team Members

Welcome to the Cross-Media Recommendation Engine! This guide will walk you through setting up the project locally.

---

## Prerequisites

- Python 3.11+ (3.14 tested in CI)
- PostgreSQL 13+ (or use Neon.tech free tier)
- MongoDB Atlas (or local MongoDB instance)
- Git

---

## Quick Start (recommended)

1. Clone the repository and change into project root:

```bash
git clone <repository-url>
cd cross-media-recommendation-engine
```

2. Copy `.env.example` to create your local `.env` and edit values:

```bash
cd backend
cp .env.example .env
# Edit .env with real credentials
```

3. Create and activate the virtual environment, then install dependencies:

```bash
# from backend/
python -m venv venv
source venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

4. Run the test suite:

```bash
PYTHONPATH=. venv/bin/pytest -q
```

5. Run the app locally:

```bash
venv/bin/uvicorn main:app --reload
# Open http://localhost:8000/docs
```

---

## Detailed Notes

- The repository does NOT include `.env` (secrets) or `venv/`. Use `.env.example` as the template and create your own `venv`.
- Tests are hermetic and do not require live databases due to fixtures, but integration runs against real DBs may be needed for end-to-end verification.
- Coverage floor is enforced at 90% (see `backend/pytest.ini`).

---

## Database Setup (Neon/Postgres)

If you prefer managed Neon/Postgres:
1. Sign up at https://neon.tech
2. Create a project and copy the connection string
3. Put the connection string into `DATABASE_URL` in `backend/.env`

## MongoDB Atlas

1. Sign up at https://mongodb.com/cloud/atlas
2. Create an M0 cluster
3. Add a DB user and network access per Atlas UI
4. Paste the connection string into `MONGODB_URL` in `backend/.env`

---

## Useful Commands

- Run tests: `PYTHONPATH=. venv/bin/pytest -q`
- Run coverage: `PYTHONPATH=. venv/bin/pytest --cov=. --cov-report=term-missing`
- Linting/format: (not included; use `black`/`ruff` if desired)

---

## Support

If you get stuck, open an issue on the repo or ping the team. Include test output and exact commands you ran.

---

Happy hacking! 🚀
