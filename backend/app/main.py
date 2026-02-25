import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    from app.tasks.scheduler import start_scheduler, stop_scheduler
    start_scheduler()
    logger.info("Macrosentiment backend started")
    yield
    stop_scheduler()
    logger.info("Macrosentiment backend stopped")


app = FastAPI(title="Macrosentiment", version="1.0.0", lifespan=lifespan)

from app.config import settings

_cors_origins = ["http://localhost:3002", "http://localhost:5173"]
if settings.cors_origins:
    _cors_origins.extend(o.strip() for o in settings.cors_origins.split(",") if o.strip())

app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from app.api import dashboard, indicators, regime, fetch

app.include_router(dashboard.router, prefix="/api", tags=["dashboard"])
app.include_router(indicators.router, prefix="/api", tags=["indicators"])
app.include_router(regime.router, prefix="/api", tags=["regime"])
app.include_router(fetch.router, prefix="/api", tags=["fetch"])


@app.get("/health")
async def health():
    return {"status": "ok"}
