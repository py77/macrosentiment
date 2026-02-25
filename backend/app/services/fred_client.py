import asyncio
import logging
from datetime import date, timedelta

import httpx

from app.config import settings

logger = logging.getLogger(__name__)

FRED_BASE_URL = "https://api.stlouisfed.org/fred"

# All FRED series we track
FRED_SERIES = {
    # Interest Rates & Yield Curve
    "DFF": {"name": "Fed Funds Rate", "category": "rates"},
    "DGS2": {"name": "2-Year Treasury", "category": "rates"},
    "DGS10": {"name": "10-Year Treasury", "category": "rates"},
    "DFII10": {"name": "10-Year Real Rate (TIPS)", "category": "rates"},
    "T5YIE": {"name": "5-Year Breakeven Inflation", "category": "rates"},
    # Inflation
    "CPIAUCSL": {"name": "CPI All Urban YoY", "category": "inflation"},
    "CPILFESL": {"name": "Core CPI (ex Food/Energy)", "category": "inflation"},
    "PCEPI": {"name": "PCE Price Index", "category": "inflation"},
    "PCEPILFE": {"name": "Core PCE Price Index", "category": "inflation"},
    # Growth & Activity
    "A191RL1Q225SBEA": {"name": "Real GDP Growth (QoQ)", "category": "growth"},
    "INDPRO": {"name": "Industrial Production Index", "category": "growth"},
    "USSLIND": {"name": "Leading Economic Index", "category": "growth"},
    # Labor
    "UNRATE": {"name": "Unemployment Rate", "category": "labor"},
    "ICSA": {"name": "Initial Jobless Claims", "category": "labor"},
    "PAYEMS": {"name": "Nonfarm Payrolls", "category": "labor"},
    # Credit
    "BAMLH0A0HYM2": {"name": "HY OAS Spread", "category": "credit"},
    "BAMLC0A4CBBB": {"name": "IG BBB Spread", "category": "credit"},
    "NFCI": {"name": "Financial Conditions Index", "category": "credit"},
    # Liquidity
    "WALCL": {"name": "Fed Balance Sheet", "category": "liquidity"},
    "M2SL": {"name": "M2 Money Supply", "category": "liquidity"},
    "RRPONTSYD": {"name": "Reverse Repo Outstanding", "category": "liquidity"},
}


class FredClient:
    def __init__(self):
        self.api_key = settings.fred_api_key
        self._client: httpx.AsyncClient | None = None

    async def _get_client(self) -> httpx.AsyncClient:
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(timeout=30.0)
        return self._client

    async def close(self):
        if self._client and not self._client.is_closed:
            await self._client.aclose()

    async def fetch_series(
        self,
        series_id: str,
        start_date: date | None = None,
        end_date: date | None = None,
    ) -> list[dict]:
        """Fetch observations for a FRED series."""
        if not self.api_key:
            logger.warning("FRED_API_KEY not set, skipping fetch")
            return []

        client = await self._get_client()
        params = {
            "series_id": series_id,
            "api_key": self.api_key,
            "file_type": "json",
            "sort_order": "asc",
        }
        if start_date:
            params["observation_start"] = start_date.isoformat()
        if end_date:
            params["observation_end"] = end_date.isoformat()

        try:
            resp = await client.get(f"{FRED_BASE_URL}/series/observations", params=params)
            resp.raise_for_status()
            data = resp.json()
            observations = []
            for obs in data.get("observations", []):
                if obs["value"] != ".":
                    observations.append({
                        "date": date.fromisoformat(obs["date"]),
                        "value": float(obs["value"]),
                    })
            return observations
        except httpx.HTTPStatusError as e:
            logger.error(f"FRED API error for {series_id}: {e.response.status_code}")
            return []
        except Exception as e:
            logger.error(f"FRED fetch error for {series_id}: {e}")
            return []

    async def fetch_all_series(
        self,
        start_date: date | None = None,
        end_date: date | None = None,
    ) -> dict[str, list[dict]]:
        """Fetch all configured FRED series with rate limiting."""
        results = {}
        series_list = list(FRED_SERIES.keys())

        # FRED rate limit: ~120 requests/minute — batch with small delays
        for i, series_id in enumerate(series_list):
            logger.info(f"Fetching FRED series {series_id} ({i+1}/{len(series_list)})")
            results[series_id] = await self.fetch_series(series_id, start_date, end_date)
            if (i + 1) % 10 == 0:
                await asyncio.sleep(1.0)  # Rate limit pause
            else:
                await asyncio.sleep(0.2)

        return results


fred_client = FredClient()
