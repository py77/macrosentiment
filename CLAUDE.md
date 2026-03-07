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

## Environment Variables (.env)

```
FRED_API_KEY=<your key from fred.stlouisfed.org>
IBKR_HOST=host.docker.internal    # Docker->host for IBKR Gateway
IBKR_PORT=4001
IBKR_CLIENT_ID=78
DATABASE_URL=postgresql+asyncpg://postgres:postgres@db:5432/macrosentiment  # set by docker-compose
CORS_ORIGINS=https://frontend-tau-peach-83.vercel.app,https://frontend-py77s-projects.vercel.app  # Vercel frontend domains only
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

# View backend logs
docker compose logs -f backend

# Rebuild after dependency changes
docker compose up -d --build

# Database shell
docker compose exec db psql -U postgres macrosentiment

# Health check
curl http://localhost:8002/health

# Start Cloudflare tunnel + auto-deploy to Vercel (one command)
bash start-tunnel.sh
```

## Vercel Deployment

- **Frontend URL:** https://frontend-tau-peach-83.vercel.app
- **Vercel project:** py77s-projects/frontend (rootDirectory="frontend")
- **Deploy from repo root**, not `frontend/` — Vercel's rootDirectory setting handles it
- `.vercel/project.json` must exist at both repo root and `frontend/.vercel/`

### Cloudflare Tunnel (quick tunnel)

The backend runs locally (needs IBKR Gateway on localhost:4001). A Cloudflare quick tunnel exposes it to the internet so the Vercel-hosted frontend can reach it.

**`bash start-tunnel.sh`** handles everything automatically:
1. Starts cloudflared and captures the new tunnel URL
2. Updates Vercel's `VITE_API_URL` env var
3. Triggers a fresh `vercel --prod` deploy
4. Tails cloudflared logs (Ctrl+C to stop)

**Important notes:**
- Quick tunnel URL changes every restart — the script handles this
- `VITE_API_URL` is a build-time variable — `vercel redeploy` won't pick up changes, need `vercel --prod`
- `CORS_ORIGINS` should only contain Vercel frontend domains, not tunnel URLs (the browser Origin header is the frontend domain, not the tunnel)
- `client.ts` auto-clears stale localStorage when `VITE_API_URL` changes between builds
- Future: a named Cloudflare tunnel with a permanent URL eliminates redeployment (see comments in `start-tunnel.sh`)

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

## API Endpoints

```
GET  /health                         — Health check
GET  /api/dashboard                  — Full dashboard payload
GET  /api/indicators                 — All indicators with latest values
GET  /api/indicators/{id}/history    — Time-series for one indicator
GET  /api/regime/current             — Current regime + scores
GET  /api/regime/history             — Regime timeline
POST /api/fetch/trigger              — Manual data refresh
GET  /api/fetch/status               — Last fetch times per source
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
- Regime quadrant labels use Recharts `ReferenceArea` `label` prop (SVG-native) — never use HTML overlay divs on charts (blocks tooltips)
- Frontend-only changes deploy with `npx vercel --prod` from repo root — no tunnel restart needed

## Gotchas

- **IBKR threading:** ib_insync needs nest_asyncio which can't patch uvloop. The IBKR client runs in a ThreadPoolExecutor with an explicit SelectorEventLoop — do not use asyncio.new_event_loop() (creates uvloop under uvicorn).
- **ContFuture vs Future:** Use ContFuture (not Future) for commodities/DX — auto-rolls to front month, no expiry needed.
- **SPX snapshot 0.0:** Index snapshots return 0.0 when market is closed. The client filters price != 0.
- **Docker->IBKR:** Backend connects to IBKR Gateway via host.docker.internal (set in .env as IBKR_HOST).
- **Computed indicators:** 2S10S (DGS10-DGS2 in bps) and SPX_VS_200D (% from 200d MA) are derived in data_fetcher.py:_compute_derived().
- **CORS vs tunnel URLs:** Do not add tunnel URLs to CORS_ORIGINS. The Origin header comes from the Vercel frontend domain, not the tunnel. Only Vercel domains belong in CORS.
- **docker compose restart vs up:** `restart` does NOT re-read `.env`. Always use `docker compose up -d` after `.env` changes.
