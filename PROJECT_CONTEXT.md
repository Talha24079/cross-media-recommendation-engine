# Project Context: Cross-Media Recommendation Engine

This document provides a comprehensive overview of the **Cross-Media Recommendation Engine** backend, intended to give another AI assistant full context for continued development or integration with the Flutter frontend.

## 🚀 Project Overview
A gamified, AI-powered platform that provides cross-media recommendations (movies, books, games, etc.) based on semantic similarity. It features a reputation-based economy, automated user factions based on taste clusters, and community interaction tools.

## 🛠 Tech Stack
- **Framework**: FastAPI (Python 3.14+)
- **Primary Database**: PostgreSQL + `pgvector` (for semantic search & user taste vectors)
- **Secondary Database**: MongoDB (for high-volume community threads & comments)
- **AI Models**: `sentence-transformers` (`all-MiniLM-L6-v2`) for 384-dim embeddings
- **Task Scheduling**: `APScheduler` (for daily faction clustering)
- **Auth**: JWT (OAuth2 with Password Flow), `passlib` (bcrypt), `python-jose`
- **Frontend (Planned)**: Flutter (Phase 7)

## 📁 Project Structure
```text
backend/
├── core/               # App configuration, security, database engines
├── models/             # SQLAlchemy (Postgres) and Mongo models
├── schemas/            # Pydantic validation schemas (strictly hardened)
├── routers/            # API endpoints (auth, recommendation, economy, community)
├── services/           # Core business logic (recommendation, economy, factions)
├── main.py             # App entry point, lifespan, middleware
├── requirements.txt    # Project dependencies
└── venv/               # Python virtual environment
test.py                 # Comprehensive E2E integration test suite
```

## ✅ Implemented Features (Phases 1-6.5)

### 1. Recommendation Engine (Phase 4)
- Uses `all-MiniLM-L6-v2` to generate 384-dimensional embeddings for media items.
- Implements **Write-Through Caching**: An in-memory NumPy matrix is kept in sync with the Postgres database for lightning-fast similarity search.
- **pgvector** is used for persistent storage and HNSW indexing.

### 2. Gamified Economy (Phase 5)
- **Reputation Points**: Users earn points through participation.
- **ACID Transactions**: All point mutations are atomic and logged in a `central_ledger`.
- **Bounties**: Users can stake points to create bounties for recommendations; other users can resolve and win them.
- **Daily Streak**: Automated point rewards for daily logins.

### 3. Auto-Factions & Taste Profiling (Phase 6)
- **Taste Vectors**: Users build a 384-dim taste vector based on interactions with media.
- **K-Means Clustering**: A background job runs every 24 hours to cluster users into one of 5 named factions based on their taste profiles.
- **Community Interaction**: Interaction endpoints update user taste profiles dynamically.

### 4. Production Hardening & Security (Phase 6.5)
- **Input Validation**: Strict Pydantic Field constraints (regex, length limits, value ranges).
- **SQLi Protection**: All route parameters are type-validated (e.g., `uuid.UUID`, `ObjectId`).
- **CORS**: Configured to allow frontend integration.
- **Duplicate Detection**: AI-powered check to prevent duplicate media submissions (>90% similarity).
- **Points Generation**: Automated rewards for media contribution (+5), threads (+3), comments (+2), and interactions (+1).

## 🛡 Security Note
- **JWT Auth**: Most endpoints (Economy, Community, Media Add) are protected by `get_current_user`.
- **Ownership Check**: Only bounty creators can resolve their own bounties.

## 🏃 How to Run
1. **Environment**: Ensure a `.env` file exists in `backend/` with `DATABASE_URL`, `MONGODB_URL`, and `SECRET_KEY`.
2. **Postgres**: Enable `pgvector` extension: `CREATE EXTENSION IF NOT EXISTS vector;`.
3. **Run Server**: 
   ```bash
   cd backend
   venv/bin/python -m uvicorn main.py:app --reload
   ```
4. **Test**: Run the integration suite from the root:
   ```bash
   backend/venv/bin/python test.py
   ```

## 🛠 Recently Completed: Production Hardening Sprint (Phase 6.5)
We just finished a comprehensive security and robustness "lockdown" of the backend to ensure it is 100% ready for frontend integration.

- **Hardened Validation**: Every Pydantic schema now has strict constraints (min/max lengths, regex for usernames, digit requirement for passwords).
- **SQLi Protection**: Upgraded all route parameters (`bounty_id`, `thread_id`, etc.) from `str` to `uuid.UUID` or `ObjectId` to prevent injection attacks.
- **Automated Points Engine**: Wired the `economy_service` into the `routers`. Users now automatically earn points for media add, threads, comments, and interactions, with all transactions recorded in the `CentralLedger`.
- **AI Content Moderation**: Implemented a check in `add_media_item` that uses the recommendation engine to find existing items with >90% similarity, blocking duplicates with a `409 Conflict`.
- **Global Error Handling**: Added a global exception handler in `core/exceptions.py` to ensure the API returns clean JSON instead of raw tracebacks during internal errors.
- **`GET /auth/me`**: Added the core profile endpoint required for the frontend dashboard.
- **Integration Testing**: Developed `test.py` which runs a 16-step E2E suite. **All tests currently pass.**

## 🎯 Next Steps: Phase 7 (Flutter Frontend)
The backend is stable and hardened. The next developer should focus on:
1. Connecting the Flutter app to the REST endpoints.
2. Implementing the "My Faction" dashboard.
3. Building the semantic search UI.
4. Handling the gamified point displays and bounty interactions.
