# Macrosentiment

Macro-economic sentiment dashboard that tracks ~40 indicators across 9 categories, classifies the current market regime, and produces a composite sentiment score from -100 to +100.

## Overview

The dashboard continuously monitors growth and inflation momentum across the economy, then classifies the environment into one of four market regimes:

| Regime | Growth | Inflation | Implication |
|---|---|---|---|
| **Goldilocks** | ↑ | ↓ | Risk-on equities |
| **Reflation** | ↑ | ↑ | Commodities, cyclicals |
| **Deflation** | ↓ | ↓ | Bonds, quality |
| **Stagflation** | ↓ | ↑ | Defensive, cash, gold |

Scores are derived from z-scores computed over a 3-year lookback window, weighted by category, and scaled to the -100 → +100 composite.

## Tech Stack

- **Backend:** FastAPI (Python 3.12), SQLAlchemy async, PostgreSQL
- **Frontend:** React 19, TypeScript, Vite, Tailwind CSS, TanStack Query, Recharts
- **Deployment:** Docker Compose (3 services: `db`, `backend`, `frontend`)
- **Fonts/Theme:** JetBrains Mono, Catppuccin dark

## Data Sources

| Source | Indicators |
|---|---|
| [FRED API](https://fred.stlouisfed.org) | Interest rates, inflation, GDP, labor, credit spreads, liquidity |
| IBKR Gateway | VIX, DXY, Gold, Oil, Copper, S&P 500 |
| Manual entry | AAII sentiment, forward P/E |
| Computed | 2s10s yield curve spread, SPX vs 200-day MA |

## Quick Start

### Prerequisites

- Docker & Docker Compose
- FRED API key (free at [fred.stlouisfed.org](https://fred.stlouisfed.org/docs/api/api_key.html))
- Interactive Brokers Gateway running on port 4001 (for market data; FRED-only mode still works)

### Setup

```bash
# 1. Clone the repo
git clone https://github.com/py77/macrosentiment.git
cd macrosentiment

# 2. Create your .env file
cat > .env << 'EOF'
FRED_API_KEY=your_fred_api_key_here
IBKR_HOST=host.docker.internal
IBKR_PORT=4001
IBKR_CLIENT_ID=78
EOF

# 3. Start all services
docker compose up -d

# 4. Trigger the initial data fetch
curl -X POST http://localhost:8002/api/fetch/trigger

# 5. Open the dashboard
open http://localhost:3002
```

The backend runs Alembic migrations and seeds the indicators table on first start.

## API Endpoints

```
GET  /health                        Health check
GET  /api/dashboard                 Full dashboard payload
GET  /api/indicators                All indicators with latest values
GET  /api/indicators/{id}/history   Time-series for one indicator
GET  /api/regime/current            Current regime + scores
GET  /api/regime/history            Regime timeline
POST /api/fetch/trigger             Manual data refresh
GET  /api/fetch/status              Last fetch times per source
POST /api/indicators/manual         Submit manual indicator values
```

## Configuration

| Variable | Default | Description |
|---|---|---|
| `FRED_API_KEY` | — | Required for FRED data |
| `IBKR_HOST` | `host.docker.internal` | IBKR Gateway host |
| `IBKR_PORT` | `4001` | IBKR Gateway port |
| `IBKR_CLIENT_ID` | `78` | IBKR client ID |
| `DATABASE_URL` | set by compose | PostgreSQL connection string |
| `CORS_ORIGINS` | — | Additional allowed origins (comma-separated) |

## Project Structure

```
macrosentiment/
├── backend/
│   └── app/
│       ├── main.py          FastAPI app, lifespan, CORS, routers
│       ├── config.py        Pydantic Settings
│       ├── database.py      Async SQLAlchemy engine + session
│       ├── models/          ORM models (indicator, value, regime, fetch_log)
│       ├── schemas/         Pydantic response models
│       ├── services/        FRED, IBKR, processor, regime, scoring, data_fetcher
│       ├── tasks/           APScheduler (23:00 UTC daily + 13:30 UTC weekdays)
│       └── api/             Route handlers
├── frontend/
│   └── src/
│       ├── api/             Axios client + API functions
│       ├── hooks/           TanStack Query hooks
│       ├── types/           TypeScript interfaces
│       ├── components/      RegimeQuadrant, CompositeGauge, CategoryCard, etc.
│       └── pages/           DashboardPage
└── docker-compose.yml
```

## Useful Commands

```bash
# View backend logs
docker compose logs -f backend

# Run a migration
docker compose exec backend alembic upgrade head

# Rebuild after dependency changes
docker compose up -d --build

# Database shell
docker compose exec db psql -U postgres macrosentiment

# Re-seed indicators table
docker compose exec backend python -m app.services.seed
```

## License

MIT
