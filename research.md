# Macrosentiment Dashboard — Indicator Reference

## Data Sources

| Source | Method | Coverage |
|--------|--------|----------|
| **FRED API** | Async HTTP via `httpx` — free API key from fred.stlouisfed.org | 21 economic series, 3-year backfill |
| **IBKR Gateway** | `ib_insync` via ThreadPoolExecutor on localhost:4001, client_id 78 | 6 market contracts, 1-year daily bars + live snapshots |
| **Computed** | Derived in `data_fetcher._compute_derived()` from raw data | 2 synthetic indicators |

---

## CREDIT & CONDITIONS

Category z-score is the weighted average of its indicators' z-scores (flipped for `higher_is_bullish: false`). Negative z-score here = spreads below historical average = calm credit markets = **bullish**.

### HY OAS Spread

- **Source:** FRED series `BAMLH0A0HYM2`
- **What it is:** ICE BofA US High Yield Option-Adjusted Spread. The extra yield (in percentage points) investors demand to hold junk-rated corporate bonds over equivalent-maturity US Treasuries.
- **How to read it:** Lower = investors are comfortable taking credit risk = bullish for risk assets. When this spikes (e.g., 8%+ in 2020), it signals credit stress and potential contagion.
- **Unit:** percentage points (displayed as %)
- **Weight:** 1.0 | **Higher is bullish:** No

### Financial Conditions Index (NFCI)

- **Source:** FRED series `NFCI`
- **What it is:** Chicago Fed National Financial Conditions Index. A weekly composite of 105 financial indicators covering money markets, debt/equity markets, and the banking system.
- **How to read it:** Zero = average conditions. Positive = tighter than average (bearish). Negative = looser than average (bullish). At -0.57, financial conditions are accommodative.
- **Unit:** index (standard deviations from average)
- **Weight:** 0.9 | **Higher is bullish:** No

### IG BBB Spread

- **Source:** FRED series `BAMLC0A4CBBB`
- **What it is:** ICE BofA BBB US Corporate Option-Adjusted Spread. The credit spread on investment-grade BBB-rated bonds — the lowest tier before junk.
- **How to read it:** This is the "canary" tier — when BBB spreads widen, it means the market is pricing in downgrade risk. Lower = healthy credit conditions.
- **Unit:** percentage points
- **Weight:** 0.8 | **Higher is bullish:** No

---

## EQUITY MARKET

### S&P 500 Index

- **Source:** IBKR `Index("SPX", "CBOE")` — 1-year daily historical bars via `reqHistoricalData`
- **What it is:** The S&P 500 large-cap US equity index. The most-watched benchmark for US stock market performance.
- **How to read it:** The raw price level. The z-score tells you how the current level compares to the 1-year distribution. Snapshot may show 0.0 when market is closed (filtered out — last historical close is used instead).
- **Unit:** index points
- **Weight:** 1.0 | **Higher is bullish:** Yes

### S&P 500 vs 200-Day Moving Average

- **Source:** Computed from SPX historical bars — `(SPX / 200d MA - 1) * 100`
- **What it is:** The percentage distance of the S&P 500 from its 200-day simple moving average. A classic trend-following signal.
- **How to read it:** Positive = above the 200d MA (uptrend). Negative = below (downtrend). At +5.32%, the market is moderately above trend. Extreme readings (>10% or <-10%) suggest overextension.
- **Unit:** percentage
- **Weight:** 0.8 | **Higher is bullish:** Yes

---

## GLOBAL / CROSS-ASSET

### US Dollar Index (DXY)

- **Source:** IBKR `ContFuture("DX", "NYBOT")` — continuous front-month DX future
- **What it is:** ICE US Dollar Index, measuring the dollar against a basket of 6 major currencies (EUR 57.6%, JPY 13.6%, GBP 11.9%, CAD 9.1%, SEK 4.2%, CHF 3.6%).
- **How to read it:** A stronger dollar tightens global financial conditions (most commodities and EM debt priced in USD). Lower DXY = easier global conditions = bullish for risk. The z-score is inverted since `higher_is_bullish: false`.
- **Unit:** index
- **Weight:** 0.8 | **Higher is bullish:** No

### WTI Crude Oil (Front Month)

- **Source:** IBKR `ContFuture("CL", "NYMEX")` — continuous front-month WTI crude future
- **What it is:** West Texas Intermediate crude oil, the US benchmark for oil prices.
- **How to read it:** Higher oil generally signals economic demand (bullish for growth), though extreme spikes can become a tax on consumers. The model treats higher as bullish because it correlates with global economic activity.
- **Unit:** $/barrel
- **Weight:** 0.8 | **Higher is bullish:** Yes

### Copper (Front Month)

- **Source:** IBKR `ContFuture("HG", "COMEX")` — continuous front-month copper future
- **What it is:** COMEX copper, often called "Dr. Copper" because its price is considered a barometer of global industrial health (used in construction, electronics, manufacturing).
- **How to read it:** Rising copper = rising industrial demand = bullish macro signal. Copper is more sensitive to China/EM growth than oil.
- **Unit:** $/lb
- **Weight:** 0.7 | **Higher is bullish:** Yes

### Gold (Front Month)

- **Source:** IBKR `ContFuture("GC", "COMEX")` — continuous front-month gold future
- **What it is:** COMEX gold. A safe-haven asset and inflation hedge.
- **How to read it:** Rising gold can signal inflation fears, geopolitical risk, or loss of confidence in fiat currencies. The model treats higher gold as bearish for macro sentiment (`higher_is_bullish: false`) since it often rises during stress.
- **Unit:** $/oz
- **Weight:** 0.7 | **Higher is bullish:** No
- **Note:** Fetched and stored but not always displayed in the top-3 card view (lower weight than DX, CL).

---

## GROWTH & ACTIVITY

### Real GDP Growth (QoQ)

- **Source:** FRED series `A191RL1Q225SBEA`
- **What it is:** Real Gross Domestic Product, quarterly percent change at a seasonally adjusted annual rate. The broadest measure of economic output.
- **How to read it:** Positive = economy expanding. The annualized rate means a 1.4% reading implies the economy would grow 1.4% if that quarter's pace continued for a full year. Released with a ~1 month lag.
- **Unit:** annualized %
- **Weight:** 1.0 | **Higher is bullish:** Yes
- **Note:** Only ~7 quarterly data points in 3 years — too few for z-score computation (requires 10+ observations).

### Industrial Production Index

- **Source:** FRED series `INDPRO`
- **What it is:** Total Industrial Production Index (2017=100). Measures real output from manufacturing, mining, and utilities.
- **How to read it:** Above 100 = production above 2017 levels. Monthly frequency makes it more timely than GDP. A z-score of +1.88 means production is well above the 3-year average.
- **Unit:** index (2017=100)
- **Weight:** 0.9 | **Higher is bullish:** Yes

### Leading Economic Index

- **Source:** FRED series `USSLIND`
- **What it is:** Conference Board Leading Economic Indicators Index. A composite of 10 forward-looking indicators (claims, building permits, stock prices, etc.).
- **How to read it:** **DISCONTINUED** — the Conference Board stopped publishing this series. Returns no data from FRED. Shows "--" on the dashboard.
- **Unit:** index
- **Weight:** 0.8 | **Higher is bullish:** Yes

---

## INFLATION

Category signal is **bearish** when inflation z-scores are positive (above average) because `higher_is_bullish: false` — rising inflation tightens monetary policy and hurts asset valuations.

### CPI All Urban (YoY)

- **Source:** FRED series `CPIAUCSL`
- **What it is:** Consumer Price Index for All Urban Consumers: All Items. The headline inflation measure. This is the **index level** (1982-84=100), not the year-over-year percentage change.
- **How to read it:** The raw level (326.59) means prices are 3.27x the 1982-84 baseline. The z-score compares the current level to the 3-year distribution. Higher = more inflation = bearish. Monthly frequency, released ~2 weeks after month-end.
- **Unit:** index (1982-84=100)
- **Weight:** 1.0 | **Higher is bullish:** No

### Core CPI (ex Food/Energy)

- **Source:** FRED series `CPILFESL`
- **What it is:** CPI Less Food and Energy. Strips out volatile food and energy prices to reveal the underlying inflation trend.
- **How to read it:** The Fed and markets focus heavily on core measures because they're more persistent. At 332.79, core CPI is above headline — food/energy have been deflationary relative to services recently.
- **Unit:** index (1982-84=100)
- **Weight:** 1.0 | **Higher is bullish:** No

### Core PCE Price Index

- **Source:** FRED series `PCEPILFE`
- **What it is:** Personal Consumption Expenditures Price Index Excluding Food and Energy (2017=100). **The Federal Reserve's preferred inflation measure.**
- **How to read it:** Differs from CPI in weighting methodology (substitution effects, healthcare weighting). The Fed targets 2% annual growth in this index. At 127.92 (2017=100), prices are up ~28% since 2017. Released ~1 month after month-end.
- **Unit:** index (2017=100)
- **Weight:** 1.0 | **Higher is bullish:** No

### Additional inflation indicators (not in top-3 display)

- **PCE Price Index** (`PCEPI`) — headline PCE including food/energy. Weight 0.9.
- **5-Year Breakeven Inflation** (`T5YIE`) — market-implied inflation expectations derived from TIPS vs nominal Treasury spread. Weight 0.8. This is forward-looking (what the bond market expects), while CPI/PCE are backward-looking.

---

## LABOR MARKET

### Nonfarm Payrolls

- **Source:** FRED series `PAYEMS`
- **What it is:** Total Nonfarm Payroll Employment, in thousands. The headline number from the monthly jobs report (BLS Employment Situation).
- **How to read it:** 158,627 thousand = 158.6 million jobs. The z-score (+1.20) reflects the level relative to 3-year history. Rising payrolls = expanding economy. This is the single most market-moving economic release.
- **Unit:** thousands of persons
- **Weight:** 1.0 | **Higher is bullish:** Yes

### Unemployment Rate

- **Source:** FRED series `UNRATE`
- **What it is:** Civilian Unemployment Rate (U-3). Percentage of the labor force that is jobless and actively seeking work.
- **How to read it:** 4.3% is slightly above recent lows (3.4% in early 2023). z=+0.75 means it's above the 3-year average — mildly bearish since `higher_is_bullish: false`. However, 4.3% is still historically low.
- **Unit:** percentage
- **Weight:** 1.0 | **Higher is bullish:** No

### Initial Jobless Claims

- **Source:** FRED series `ICSA`
- **What it is:** Weekly Initial Claims for Unemployment Insurance. The most timely labor market indicator — released every Thursday for the prior week.
- **How to read it:** 206,000 new filings is very low (z=-1.50). Lower claims = fewer layoffs = bullish. The -23,000 change shows a significant weekly drop. This is the first indicator to spike at the onset of recessions.
- **Unit:** number of claims
- **Weight:** 0.9 | **Higher is bullish:** No

---

## LIQUIDITY

### Fed Balance Sheet

- **Source:** FRED series `WALCL`
- **What it is:** Federal Reserve Total Assets, in millions of dollars. Updated weekly (Wednesday).
- **How to read it:** $6.61 trillion, down from a peak of ~$8.9T. The -$8,987M weekly change reflects ongoing Quantitative Tightening (balance sheet runoff). z=-0.93 = below 3-year average = bearish for liquidity, but the pace of decline has slowed.
- **Unit:** millions of dollars
- **Weight:** 1.0 | **Higher is bullish:** Yes

### M2 Money Supply

- **Source:** FRED series `M2SL`
- **What it is:** M2 Money Stock, in billions. Includes cash, checking deposits, savings, money market funds, and small time deposits. The broadest commonly tracked money aggregate.
- **How to read it:** $22,442B. z=+1.63 = well above 3-year average. M2 contracted in 2022-23 (unprecedented) but has resumed growth. Expanding money supply = more liquidity = bullish.
- **Unit:** billions of dollars
- **Weight:** 0.9 | **Higher is bullish:** Yes

### Reverse Repo Outstanding

- **Source:** FRED series `RRPONTSYD`
- **What it is:** Overnight Reverse Repurchase Agreements. Cash parked at the Fed by money market funds overnight.
- **How to read it:** $0.92B — essentially zero (was $2.5T in mid-2023). When RRP drains, that cash flows into the financial system (buying T-bills, bank deposits). z=-1.23 = very low = bullish for liquidity. The massive RRP drain has been a stealth liquidity injection.
- **Unit:** billions of dollars
- **Weight:** 0.7 | **Higher is bullish:** No

---

## RATES & YIELD CURVE

### 10-Year Treasury Yield

- **Source:** FRED series `DGS10`
- **What it is:** Market Yield on US Treasury Securities at 10-Year Constant Maturity. The benchmark long-term risk-free rate.
- **How to read it:** 4.03% — below recent peaks (~5% in Oct 2023). z=-1.04 = below 3-year average = bullish (lower rates ease financial conditions, support equity valuations). Drives mortgage rates, corporate borrowing costs, and equity discount rates.
- **Unit:** percentage
- **Weight:** 1.0 | **Higher is bullish:** No

### Fed Funds Rate

- **Source:** FRED series `DFF`
- **What it is:** Federal Funds Effective Rate. The overnight rate banks charge each other, directly controlled by the Federal Reserve through its target range.
- **How to read it:** 3.64% — down from 5.33% peak, reflecting Fed rate cuts. z=-1.63 = well below 3-year average. This is the anchor for all short-term rates. Lower = easier monetary policy = bullish.
- **Unit:** percentage
- **Weight:** 1.0 | **Higher is bullish:** No

### 2s10s Spread

- **Source:** Computed as `(DGS10 - DGS2) * 100` (converted to basis points)
- **What it is:** The spread between the 10-year and 2-year Treasury yields. The most-watched yield curve indicator.
- **How to read it:** +60 bps = normal upward-sloping curve (longer maturity = higher yield). When negative (inverted), it's the most reliable recession predictor — the curve was inverted from mid-2022 through 2024. z=+1.03 = above 3-year average = bullish (curve has normalized).
- **Unit:** basis points (1 bp = 0.01%)
- **Weight:** 0.9 | **Higher is bullish:** Yes

### Additional rate indicators (not in top-3 display)

- **2-Year Treasury Yield** (`DGS2`) — short-end of the curve, most sensitive to Fed policy expectations. Weight 0.8.
- **10-Year Real Rate (TIPS)** (`DFII10`) — inflation-adjusted 10Y yield. Weight 0.7.
- **5-Year Breakeven Inflation** (`T5YIE`) — also appears in inflation calculations. Weight 0.8.

---

## MARKET SENTIMENT

### VIX Volatility Index

- **Source:** IBKR `Index("VIX", "CBOE")` — snapshot + 1-year daily historical bars
- **What it is:** CBOE Volatility Index. Derived from S&P 500 option prices, representing the market's expectation of 30-day forward volatility. Often called the "fear gauge."
- **How to read it:** 19.53 is near the long-term average (~20). z=+0.08 = essentially neutral. Below 15 = complacency (potential for complacent sell-off). Above 25 = elevated fear. Above 35 = panic. The -0.02 change is negligible.
- **Unit:** index (annualized implied volatility in %)
- **Weight:** 1.0 | **Higher is bullish:** No

---

## Regime Classification

The dashboard classifies the macro environment into one of four regimes based on growth and inflation momentum:

| | Inflation Falling | Inflation Rising |
|---|---|---|
| **Growth Rising** | **GOLDILOCKS** — risk-on equities | **REFLATION** — commodities, cyclicals |
| **Growth Falling** | **DEFLATION** — bonds, quality | **STAGFLATION** — defensive, cash, gold |

**Current regime: REFLATION** (growth +0.60, inflation +0.74)

## Composite Score

**+15.25** on a scale of -100 to +100. Weighted sum across all categories:

| Category | Weight | Rationale |
|----------|--------|-----------|
| Growth | 30% | Dominant driver of equity returns |
| Inflation | 15% | Direction matters for policy trajectory |
| Rates | 15% | Directly affects discount rates and borrowing |
| Credit | 15% | Early warning system for financial stress |
| Sentiment | 10% | Contrarian signal at extremes |
| Liquidity | 10% | Backdrop for asset price support |
| Equity | 5% | Partially reflexive — low weight to avoid circularity |

## Data Freshness

| Source | Frequency | Typical Lag |
|--------|-----------|-------------|
| FRED daily series (DFF, DGS2, DGS10, DFII10, T5YIE, spreads) | Daily | 1 business day |
| FRED weekly series (ICSA, WALCL, NFCI, RRPONTSYD) | Weekly | 1-4 days |
| FRED monthly series (CPI, PCE, UNRATE, PAYEMS, INDPRO, M2) | Monthly | 2-4 weeks |
| FRED quarterly series (GDP) | Quarterly | 1-3 months |
| IBKR snapshots (SPX, VIX, DX, GC, CL, HG) | Real-time when market open | None (delayed-frozen fallback) |
| IBKR historical bars | Daily | 1 business day |
| Computed (2S10S, SPX_VS_200D) | Derived after each fetch | Same as inputs |

Scheduled fetches run at **23:00 UTC** (evening) and **13:30 UTC** (morning, weekdays). Manual trigger available via `POST /api/fetch/trigger`.
