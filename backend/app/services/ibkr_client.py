import asyncio
import logging
import math
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone

from app.config import settings

logger = logging.getLogger(__name__)

# IBKR contracts for macro indicators
IBKR_CONTRACTS = {
    "SPX": {"type": "Index", "symbol": "SPX", "exchange": "CBOE", "category": "equity"},
    "VIX": {"type": "Index", "symbol": "VIX", "exchange": "CBOE", "category": "sentiment"},
    "DX": {"type": "ContFuture", "symbol": "DX", "exchange": "NYBOT", "category": "global"},
    "GC": {"type": "ContFuture", "symbol": "GC", "exchange": "COMEX", "category": "global"},
    "CL": {"type": "ContFuture", "symbol": "CL", "exchange": "NYMEX", "category": "global"},
    "HG": {"type": "ContFuture", "symbol": "HG", "exchange": "COMEX", "category": "global"},
}

_executor = ThreadPoolExecutor(max_workers=1)


def _make_contract(key: str):
    """Create an ib_insync contract object from config."""
    from ib_insync import ContFuture, Index
    cfg = IBKR_CONTRACTS[key]
    if cfg["type"] == "Index":
        return Index(cfg["symbol"], cfg["exchange"])
    elif cfg["type"] == "ContFuture":
        return ContFuture(cfg["symbol"], exchange=cfg["exchange"])
    raise ValueError(f"Unknown contract type: {cfg['type']}")


def _run_ibkr_sync() -> dict:
    """Run all IBKR fetches synchronously in a dedicated thread with its own event loop."""
    # Create a standard asyncio event loop (not uvloop) for this thread.
    # nest_asyncio (used by ib_insync) can't patch uvloop.
    loop = asyncio.SelectorEventLoop()
    asyncio.set_event_loop(loop)

    import nest_asyncio
    nest_asyncio.apply(loop)

    from ib_insync import IB

    ib = IB()
    host = settings.ibkr_host
    port = settings.ibkr_port
    client_id = settings.ibkr_client_id
    timeout = settings.ibkr_timeout_sec

    # Connect with retries
    for attempt in range(3):
        try:
            ib.connect(host, port, clientId=client_id, timeout=timeout, readonly=True)
            logger.info(f"Connected to IBKR on attempt {attempt + 1}")
            break
        except Exception as e:
            wait = 2 ** attempt
            logger.warning(f"IBKR connection attempt {attempt + 1} failed: {e}. Retrying in {wait}s...")
            time.sleep(wait)
    else:
        raise ConnectionError("Failed to connect to IBKR Gateway after retries")

    try:
        ib.reqMarketDataType(4)  # Delayed-frozen fallback

        results = {"snapshots": {}, "historical": {}}

        for key in IBKR_CONTRACTS:
            try:
                contract = _make_contract(key)
                qualified = ib.qualifyContracts(contract)
                if not qualified:
                    logger.warning(f"Could not qualify contract for {key}")
                    continue

                # Snapshot
                ticker = ib.reqMktData(contract, snapshot=True)
                ib.sleep(3)

                price = ticker.marketPrice()
                if math.isnan(price):
                    price = ticker.close
                if not math.isnan(price) and price != 0:
                    results["snapshots"][key] = {
                        "symbol": key,
                        "price": round(price, 4),
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                    }
                else:
                    logger.warning(f"No price data for {key}")

                ib.cancelMktData(contract)
                ib.sleep(0.5)

            except Exception as e:
                logger.error(f"IBKR snapshot error for {key}: {e}")

        # Historical bars
        for key in IBKR_CONTRACTS:
            try:
                contract = _make_contract(key)
                ib.qualifyContracts(contract)

                what_to_show = "TRADES"

                bars = ib.reqHistoricalData(
                    contract,
                    endDateTime="",
                    durationStr="1 Y",
                    barSizeSetting="1 day",
                    whatToShow=what_to_show,
                    useRTH=True,
                    formatDate=1,
                )
                ib.sleep(1)

                if bars:
                    results["historical"][key] = [
                        {"date": b.date, "value": b.close}
                        for b in bars
                    ]
                    logger.info(f"IBKR historical {key}: {len(bars)} bars")

                ib.sleep(2)  # Pacing between requests
            except Exception as e:
                logger.error(f"IBKR historical error for {key}: {e}")

        return results

    finally:
        ib.disconnect()
        logger.info("Disconnected from IBKR")


async def fetch_ibkr_all() -> dict:
    """Run IBKR fetches in a thread to avoid event loop conflicts."""
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(_executor, _run_ibkr_sync)
