# MACROSENTIMENT

Macro-economic sentiment assessment tool tracking ~40 indicators across 9 categories, classifying the current market regime (Goldilocks/Reflation/Deflation/Stagflation), and providing a composite sentiment score (-100 to +100).

## Architecture

- **Backend:** FastAPI (Python 3.12) + SQLAlchemy async + PostgreSQL
- **Frontend:** React 19 + TypeScript + Vite + Tailwind + TanStack Query + Recharts
- **Deployment:** Docker Compose (3 services: db, backend, frontend)
- **Ports:** Backend :8002, Frontend :3002 (avoids conflict with portfolio on 8000/3000)

## Quick Start

```bash
docker compose up -d
# Backend runs migrations on first start, then:
# POST http://localhost:8002/api/fetch/trigger  — triggers initial data fetch
# Open http://localhost:3002 — dashboard
```

## Data Sources

- **FRED API** — interest rates, inflation, GDP, labor, credit spreads, liquidity (requires `FRED_API_KEY` in .env)
- **IBKR Gateway** — VIX, DXY, Gold, Oil, Copper, S&P 500 (port 4001, client_id 78, readonly)
- **Manual entry** — AAII sentiment, forward P/E via `POST /api/indicators/manual`

## Key Commands

```bash
# Run Alembic migration
docker compose exec backend alembic upgrade head

# Seed indicators table
docker compose exec backend python -m app.services.seed

# Manual data fetch
curl -X POST http://localhost:8002/api/fetch/trigger
```

## Project Structure

```
backend/app/
  main.py          — FastAPI app with lifespan, CORS, routers
  config.py        — Pydantic Settings (.env loading)
  database.py      — SQLAlchemy async engine + session
  models/          — ORM models (indicator, indicator_value, regime, fetch_log)
  schemas/         — Pydantic response models
  services/        — Business logic (FRED, IBKR, processor, regime, scoring, data_fetcher)
  tasks/           — APScheduler (daily 23:00 UTC + morning 13:30 UTC)
  api/             — Route handlers (dashboard, indicators, regime, fetch)

frontend/src/
  api/             — Axios client + API functions
  hooks/           — TanStack Query hooks
  types/           — TypeScript interfaces
  components/      — RegimeQuadrant, CompositeGauge, CategoryCard, IndicatorTable, etc.
  pages/           — DashboardPage (single-page layout)
```

## Regime Classification

Growth/inflation momentum scores (-1 to +1) → 4 quadrants:
- **Goldilocks** (growth↑ inflation↓): risk-on equities
- **Reflation** (growth↑ inflation↑): commodities, cyclicals
- **Deflation** (growth↓ inflation↓): bonds, quality
- **Stagflation** (growth↓ inflation↑): defensive, cash, gold

## Conventions

- Terminal aesthetic: Catppuccin dark, JetBrains Mono, monospace
- All market data via IBKR Gateway (no yfinance)
- IBKR client_id: 78 (avoids conflict with equityreport's 77)
- Z-scores computed over 3-year lookback window
- Composite score scaled -100 to +100 via category-weighted z-scores
