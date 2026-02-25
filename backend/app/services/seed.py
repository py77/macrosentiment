"""Seed the indicators table with all ~40 macro indicators."""
import asyncio
import logging
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))

from sqlalchemy import select
from app.database import async_session
from app.models.indicator import Indicator

logger = logging.getLogger(__name__)

INDICATORS = [
    # Interest Rates & Yield Curve
    {"series_id": "DFF", "name": "Fed Funds Rate", "category": "rates", "source": "fred", "weight": 1.0, "higher_is_bullish": False, "unit": "%", "description": "Federal Funds Effective Rate"},
    {"series_id": "DGS2", "name": "2-Year Treasury Yield", "category": "rates", "source": "fred", "weight": 0.8, "higher_is_bullish": False, "unit": "%", "description": "Market-Set Short-Term Rate"},
    {"series_id": "DGS10", "name": "10-Year Treasury Yield", "category": "rates", "source": "fred", "weight": 1.0, "higher_is_bullish": False, "unit": "%", "description": "Benchmark Long-Term Rate"},
    {"series_id": "2S10S", "name": "2s10s Spread", "category": "rates", "source": "computed", "weight": 0.9, "higher_is_bullish": True, "unit": "bps", "description": "Yield Curve Spread (DGS10 - DGS2)"},
    {"series_id": "DFII10", "name": "10-Year Real Rate (TIPS)", "category": "rates", "source": "fred", "weight": 0.7, "higher_is_bullish": False, "unit": "%", "description": "10-Year Treasury Inflation-Indexed"},
    {"series_id": "T5YIE", "name": "5-Year Breakeven Inflation", "category": "rates", "source": "fred", "weight": 0.8, "higher_is_bullish": False, "unit": "%", "description": "Market Inflation Expectations"},

    # Inflation
    {"series_id": "CPIAUCSL", "name": "CPI All Urban (YoY)", "category": "inflation", "source": "fred", "weight": 1.0, "higher_is_bullish": False, "unit": "index", "description": "Consumer Price Index for All Urban Consumers"},
    {"series_id": "CPILFESL", "name": "Core CPI (ex Food/Energy)", "category": "inflation", "source": "fred", "weight": 1.0, "higher_is_bullish": False, "unit": "index", "description": "CPI Less Food and Energy"},
    {"series_id": "PCEPI", "name": "PCE Price Index", "category": "inflation", "source": "fred", "weight": 0.9, "higher_is_bullish": False, "unit": "index", "description": "Personal Consumption Expenditures Price Index"},
    {"series_id": "PCEPILFE", "name": "Core PCE Price Index", "category": "inflation", "source": "fred", "weight": 1.0, "higher_is_bullish": False, "unit": "index", "description": "PCE Excluding Food and Energy (Fed's preferred measure)"},

    # Growth & Activity
    {"series_id": "A191RL1Q225SBEA", "name": "Real GDP Growth (QoQ)", "category": "growth", "source": "fred", "weight": 1.0, "higher_is_bullish": True, "unit": "%", "description": "Real GDP Quarterly Change, Annualized"},
    {"series_id": "INDPRO", "name": "Industrial Production Index", "category": "growth", "source": "fred", "weight": 0.9, "higher_is_bullish": True, "unit": "index", "description": "Industrial Production: Total Index"},
    {"series_id": "USSLIND", "name": "Leading Economic Index", "category": "growth", "source": "fred", "weight": 0.8, "higher_is_bullish": True, "unit": "index", "description": "Conference Board Leading Economic Indicators (discontinued)"},

    # Labor
    {"series_id": "UNRATE", "name": "Unemployment Rate", "category": "labor", "source": "fred", "weight": 1.0, "higher_is_bullish": False, "unit": "%", "description": "Civilian Unemployment Rate"},
    {"series_id": "ICSA", "name": "Initial Jobless Claims", "category": "labor", "source": "fred", "weight": 0.9, "higher_is_bullish": False, "unit": "thousands", "description": "Initial Claims for Unemployment Insurance"},
    {"series_id": "PAYEMS", "name": "Nonfarm Payrolls", "category": "labor", "source": "fred", "weight": 1.0, "higher_is_bullish": True, "unit": "thousands", "description": "Total Nonfarm Payroll Employment"},

    # Market Sentiment
    {"series_id": "VIX", "name": "VIX Volatility Index", "category": "sentiment", "source": "ibkr", "weight": 1.0, "higher_is_bullish": False, "unit": "index", "description": "CBOE Volatility Index (Fear Gauge)"},

    # Credit
    {"series_id": "BAMLH0A0HYM2", "name": "HY OAS Spread", "category": "credit", "source": "fred", "weight": 1.0, "higher_is_bullish": False, "unit": "bps", "description": "ICE BofA US High Yield OAS"},
    {"series_id": "BAMLC0A4CBBB", "name": "IG BBB Spread", "category": "credit", "source": "fred", "weight": 0.8, "higher_is_bullish": False, "unit": "bps", "description": "ICE BofA BBB US Corporate OAS"},
    {"series_id": "NFCI", "name": "Financial Conditions Index", "category": "credit", "source": "fred", "weight": 0.9, "higher_is_bullish": False, "unit": "index", "description": "Chicago Fed National Financial Conditions Index (positive = tighter)"},

    # Liquidity
    {"series_id": "WALCL", "name": "Fed Balance Sheet", "category": "liquidity", "source": "fred", "weight": 1.0, "higher_is_bullish": True, "unit": "$M", "description": "Federal Reserve Total Assets"},
    {"series_id": "M2SL", "name": "M2 Money Supply", "category": "liquidity", "source": "fred", "weight": 0.9, "higher_is_bullish": True, "unit": "$B", "description": "M2 Money Stock"},
    {"series_id": "RRPONTSYD", "name": "Reverse Repo Outstanding", "category": "liquidity", "source": "fred", "weight": 0.7, "higher_is_bullish": False, "unit": "$B", "description": "Overnight Reverse Repurchase Agreements"},

    # Global / Cross-Asset (IBKR)
    {"series_id": "DX", "name": "US Dollar Index (DXY)", "category": "global", "source": "ibkr", "weight": 0.8, "higher_is_bullish": False, "unit": "index", "description": "ICE US Dollar Index"},
    {"series_id": "GC", "name": "Gold (Front Month)", "category": "global", "source": "ibkr", "weight": 0.7, "higher_is_bullish": False, "unit": "$/oz", "description": "COMEX Gold Continuous Contract"},
    {"series_id": "CL", "name": "WTI Crude Oil (Front Month)", "category": "global", "source": "ibkr", "weight": 0.8, "higher_is_bullish": True, "unit": "$/bbl", "description": "NYMEX WTI Crude Oil Continuous"},
    {"series_id": "HG", "name": "Copper (Front Month)", "category": "global", "source": "ibkr", "weight": 0.7, "higher_is_bullish": True, "unit": "$/lb", "description": "COMEX Copper Continuous (Dr. Copper)"},

    # Equity Market (IBKR)
    {"series_id": "SPX", "name": "S&P 500 Index", "category": "equity", "source": "ibkr", "weight": 1.0, "higher_is_bullish": True, "unit": "index", "description": "S&P 500 Large Cap Index"},
    {"series_id": "SPX_VS_200D", "name": "S&P 500 vs 200d MA", "category": "equity", "source": "computed", "weight": 0.8, "higher_is_bullish": True, "unit": "%", "description": "S&P 500 distance from 200-day moving average"},

]


async def seed_indicators():
    """Insert or update all indicator definitions."""
    async with async_session() as db:
        for ind_data in INDICATORS:
            result = await db.execute(
                select(Indicator).where(Indicator.series_id == ind_data["series_id"])
            )
            existing = result.scalar_one_or_none()

            if existing:
                for key, value in ind_data.items():
                    setattr(existing, key, value)
            else:
                db.add(Indicator(**ind_data))

        await db.commit()
        logger.info(f"Seeded {len(INDICATORS)} indicators")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(seed_indicators())
