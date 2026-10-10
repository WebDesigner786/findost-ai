# FinDost AI — Production FastAPI Backend

Production-grade, asynchronous-ready financial operations backend for **FinDost AI**, designed for Pakistani students, households, micro-entrepreneurs (Kiryana SMEs), and enterprises.

Built with **FastAPI**, **SQLAlchemy 2.0 Core/ORM**, and **Pydantic v2**. Prepared for direct integration with **Supabase PostgreSQL** or standalone local SQLite execution.

---

## 1. Architectural Highlights

- **Strict `NUMERIC(14,2)` Handling for PKR**:
  - All financial amounts in the database use `Numeric(14, 2)` (supporting up to 999 Billion PKR with 2 exact decimal places).
  - Python business logic relies strictly on `Decimal` arithmetic and integer paisa strings (`1 PKR = 100 Paisa`), eliminating IEEE-754 binary floating-point drift.
- **Zero Hardcoded Credentials**:
  - Environment variables loaded securely via Pydantic `BaseSettings`.
  - Database URL normalization handles standard `postgresql://` and Supabase connection poolers.
- **Robust Error-Handling Middleware**:
  - Uniform, typed JSON error responses across all routes:
    ```json
    {
      "error": {
        "code": "VALIDATION_ERROR | NOT_FOUND | DATABASE_ERROR",
        "message": "Human readable message",
        "details": null
      }
    }
    ```
  - Never leaks raw credentials or database connection strings.
- **Supabase Connection Pooling Best Practices**:
  - Configured with `pool_size=10`, `max_overflow=20`, `pool_timeout=30`, and `pool_pre_ping=True` to survive serverless connection drops and PgBouncer transaction pooling.

---

## 2. Directory Structure

```text
backend/
├── app/
│   ├── config.py             # Pydantic BaseSettings environment loader
│   ├── database.py           # SQLAlchemy 2.0 Engine, pooling & sessionmaker
│   ├── main.py               # FastAPI entry point, lifespan, error handlers & CORS
│   ├── middleware/
│   │   ├── cors.py           # CORS setup for frontend origins
│   │   └── error_handler.py  # Global error interceptor
│   ├── models/               # SQLAlchemy Models with NUMERIC(14,2)
│   │   ├── base.py           # Timestamp mixin (created_at, updated_at)
│   │   ├── workspace.py      # Workspaces (student, household, sme, enterprise)
│   │   ├── document.py       # Uploaded invoices, receipts & source references
│   │   ├── transaction.py    # Ledger transactions with audit history
│   │   ├── udhaar.py         # Customer receivables & khata leaves
│   │   ├── forecast.py       # 90-day cash flow projections & P10/P90 points
│   │   ├── anomaly.py        # Price spikes, duplicates, overdue debt signals
│   │   └── recommendation.py # Evidence-backed recommendations
│   ├── routers/
│   │   ├── health.py         # /api/health (database ping & dialect inspection)
│   │   ├── workspaces.py     # /api/workspaces & /api/workspaces/{id}/dashboard
│   │   ├── transactions.py   # /api/workspaces/{id}/transactions & /api/transactions/{id}
│   │   ├── udhaar.py         # /api/workspaces/{id}/udhaar & /api/udhaar/{id}/settlements
│   │   ├── scenarios.py      # /api/workspaces/{id}/scenarios (shock testing)
│   │   ├── reports.py        # /api/workspaces/{id}/reports (evidence & tax preview)
│   │   ├── documents.py      # /api/documents/upload (PDF, JPG, CSV, XLSX)
│   │   └── seed.py           # /api/seed (idempotent DB seed)
│   ├── schemas/              # Pydantic v2 validation models
│   │   ├── common.py         # Money ({ currency: "PKR", amountPaisa: str }) & Decimal converters
│   │   ├── dashboard.py      # DashboardData & KPIs
│   │   ├── transaction.py    # Transaction & batch import schemas
│   │   ├── udhaar.py         # Udhaar & FIFO settlement schemas
│   │   ├── scenario.py       # Shocks & recovery levers schemas
│   │   └── report.py         # Grounded recommendations & tax preview schemas
│   └── services/
│       ├── calculator.py     # Exact Decimal run rate, runway & forecast engine
│       └── seed_data.py      # Seed data for 4 Pakistani personas
├── scripts/
│   └── init_db.py            # CLI script to create tables and seed database
├── tests/
│   └── test_api.py           # Pytest suite testing exact math & endpoints
├── .env.example
├── pyproject.toml
└── requirements.txt
```

---

## 3. Quick Start

### 1. Set Up Python Virtual Environment

```bash
cd backend
python -m venv venv

# Windows:
venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

pip install -r requirements.txt
```

### 2. Configure Environment

Copy `.env.example` to `.env`:

```bash
copy .env.example .env
```

To connect directly to **Supabase PostgreSQL**, set `DATABASE_URL` in your `.env`:

```env
DATABASE_URL=postgresql://postgres:[YOUR-PASSWORD]@db.[PROJECT-REF].supabase.co:5432/postgres
```

*(If `DATABASE_URL` is left as default, it automatically uses SQLite at `sqlite:///./findost_local.db` for zero-configuration offline runs).*

### 3. Initialize & Seed Database

```bash
python scripts/init_db.py
```

### 4. Run Development Server

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

- **Interactive Swagger Docs**: `http://localhost:8000/docs`
- **ReDoc API Reference**: `http://localhost:8000/redoc`
- **Health Check**: `http://localhost:8000/api/health`

---

## 4. Run Test Suite

```bash
pytest tests/ -v
```
