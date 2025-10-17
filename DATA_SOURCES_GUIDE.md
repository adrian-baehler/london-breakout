# Backtest Data Sources Guide

## Where Does the Backtest Data Come From?

The London Breakout strategy supports **multiple data sources** for backtesting. Here's everything you need to know:

---

## Current Default Setup

### By Default: **Sample/Synthetic Data** 🎲

**File:** `run_backtest.py` (line 41)
```python
use_sample=True  # Currently using generated sample data
```

**What This Means:**
- The backtest generates **synthetic OHLC data** on-the-fly
- No real market data is used by default
- Perfect for **testing** and **learning** the strategy
- Data is generated using realistic random walk with forex-like volatility

### How Sample Data is Generated

**Location:** `data_loader.py` - `generate_sample_data()` method (lines 104-165)

**Process:**
1. Creates date range for specified period (e.g., 2023-01-01 to 2024-01-01)
2. Generates 5-minute bars (configurable)
3. Uses random walk with small returns (mean=0, std=0.0001)
4. Creates realistic OHLC bars from close prices
5. Adds random volume data
6. Seeds random generator (seed=42) for reproducibility

**Characteristics:**
- Base price: 1.1000 (configurable)
- Timeframe: 5 minutes (configurable)
- Volatility: Forex-realistic (0.02% per bar)
- Reproducible: Same seed = same data every time

---

## Available Data Sources

The system supports **5 different data sources**:

### 1. ✅ Generated Sample Data (Default)

**Use Case:** Testing, learning, development

**Pros:**
- ✅ No setup required
- ✅ Works immediately
- ✅ Reproducible results
- ✅ Free
- ✅ Any date range
- ✅ Any symbol

**Cons:**
- ❌ Not real market data
- ❌ Doesn't capture real market behavior
- ❌ Results not reliable for live trading

**How to Use:**
```python
# In run_backtest.py
df = prepare_backtest_data(
    symbol="EURUSD",
    start_date="2023-01-01",
    end_date="2024-01-01",
    timeframe="5min",
    use_sample=True  # ← Uses generated data
)
```

---

### 2. 📄 CSV Files (Your Own Data)

**Use Case:** Using data you already have

**Pros:**
- ✅ Real market data
- ✅ Reliable results
- ✅ Any format (with some setup)
- ✅ Offline - no internet needed

**Cons:**
- ❌ Need to acquire data first
- ❌ Storage requirements
- ❌ Need to update periodically

**How to Use:**

**Step 1:** Get OHLC data in CSV format with columns:
- `timestamp` (or `date`)
- `open`, `high`, `low`, `close`
- `volume` (optional)

**Step 2:** Place file in `data/` folder:
```bash
data/EURUSD_5min.csv
```

**Step 3:** Update run_backtest.py:
```python
df = prepare_backtest_data(
    symbol="EURUSD",
    start_date="2023-01-01",
    end_date="2024-01-01",
    timeframe="5min",
    use_sample=False  # ← Uses CSV file
)
```

**CSV Format Example:**
```csv
timestamp,open,high,low,close,volume
2023-01-01 00:00:00,1.1000,1.1005,1.0995,1.1002,5000
2023-01-01 00:05:00,1.1002,1.1010,1.1000,1.1008,6500
...
```

**Custom CSV Loading:**
```python
from data_loader import DataLoader

df = DataLoader.load_csv(
    filepath="path/to/your/data.csv",
    date_column="timestamp",  # Your date column name
    date_format="%Y-%m-%d %H:%M:%S"  # Optional
)
```

---

### 3. 📊 MetaTrader 5 (MT5) Export

**Use Case:** If you use MetaTrader 5

**Pros:**
- ✅ Easy export from MT5
- ✅ Real broker data
- ✅ High quality
- ✅ Built-in support

**Cons:**
- ❌ Requires MT5 account
- ❌ Manual export process
- ❌ Limited history (broker-dependent)

**How to Export from MT5:**

1. Open MT5
2. Open chart for your symbol
3. Set timeframe (M5 for 5-min)
4. Right-click chart → "Export Data"
5. Save as CSV

**How to Use:**
```python
from data_loader import DataLoader

df = DataLoader.load_mt5_export("path/to/mt5_export.csv")
```

**MT5 Format:**
```csv
Date,Time,Open,High,Low,Close,Volume
2023-01-01,00:00,1.1000,1.1005,1.0995,1.1002,5000
```

---

### 4. 📈 Yahoo Finance (For Forex/Stocks)

**Use Case:** Quick access to free historical data

**Pros:**
- ✅ Free
- ✅ Automated download
- ✅ No registration
- ✅ Major forex pairs available

**Cons:**
- ❌ Limited forex coverage
- ❌ Requires internet
- ❌ Rate limits
- ❌ Lower quality than broker data

**How to Use:**

**Step 1:** Install yfinance:
```bash
pip install yfinance
```

**Step 2:** Download data:
```python
from data_loader import YahooFinanceLoader

df = YahooFinanceLoader.download(
    ticker="EURUSD=X",  # Forex format: PAIR=X
    start_date="2023-01-01",
    end_date="2024-01-01",
    interval="5m"  # 1m, 5m, 15m, 1h, 1d
)
```

**Available Forex Pairs:**
- EURUSD=X
- GBPUSD=X
- USDJPY=X
- AUDUSD=X
- etc.

---

### 5. 🔌 cTrader API (Live Data)

**Use Case:** If you're using cTrader for live trading

**Pros:**
- ✅ Real-time data
- ✅ Same as live trading
- ✅ Highest quality
- ✅ Direct from broker

**Cons:**
- ❌ Requires cTrader account
- ❌ API credentials needed
- ❌ More complex setup

**How to Use:**
See `ctrader_api.py` for implementation details.

---

## Recommended Data Sources by Use Case

### 🎓 Learning the Strategy
**Use:** Sample Data
- Quick setup
- Reproducible
- Free

### 🧪 Testing Strategy Logic
**Use:** Sample Data or Yahoo Finance
- Quick iteration
- No data management

### 📊 Serious Backtesting
**Use:** CSV Files or MT5 Export
- Real market data
- Reliable results
- Proper validation

### 🚀 Pre-Live Testing
**Use:** cTrader API or Broker Data
- Same as live environment
- Account for real spreads/slippage

---

## How to Switch Data Sources

### Quick Switch: Change One Line

**In `run_backtest.py` line 41:**

```python
# Use generated sample data
use_sample=True

# OR use real CSV data
use_sample=False
```

### Custom Data Loading

**Option 1: Load Your CSV**
```python
from data_loader import DataLoader

df = DataLoader.load_csv("path/to/data.csv")
df = DataLoader.clean_data(df)
df = DataLoader.add_time_features(df)

engine = BacktestEngine("EURUSD", 10000)
results = engine.run(df)
```

**Option 2: Yahoo Finance**
```python
from data_loader import YahooFinanceLoader, DataLoader

df = YahooFinanceLoader.download("EURUSD=X", "2023-01-01", "2024-01-01", "5m")
df = DataLoader.clean_data(df)
df = DataLoader.add_time_features(df)

engine = BacktestEngine("EURUSD", 10000)
results = engine.run(df)
```

**Option 3: MT5 Export**
```python
from data_loader import DataLoader

df = DataLoader.load_mt5_export("mt5_data.csv")
df = DataLoader.clean_data(df)
df = DataLoader.add_time_features(df)

engine = BacktestEngine("EURUSD", 10000)
results = engine.run(df)
```

---

## Data Requirements

### Minimum Requirements

**Columns:**
- `timestamp` (datetime index)
- `open` (float)
- `high` (float)
- `low` (float)
- `close` (float)

**Optional:**
- `volume` (int)

**Timeframe:**
- Recommended: 5 minutes
- Supported: 1min, 5min, 15min, 1H, 4H, 1D

**Period:**
- Minimum: 1 month (for meaningful results)
- Recommended: 1+ years
- Ideal: 2-3 years for robust testing

---

## Data Quality Checks

The `DataLoader.clean_data()` method automatically:

✅ Removes duplicates
✅ Removes missing values
✅ Validates OHLC logic (high >= low, etc.)
✅ Removes weekends (forex closed)
✅ Removes zero/negative prices
✅ Flags and removes invalid bars

---

## Getting Real Historical Data

### Free Sources

1. **Yahoo Finance**
   - Automated via yfinance
   - Major pairs only
   - Limited history for intraday

2. **Dukascopy**
   - https://www.dukascopy.com/swiss/english/marketwatch/historical/
   - High quality tick data
   - Manual download

3. **HistData**
   - http://www.histdata.com/
   - M1 bars for major pairs
   - Free registration

### Paid Sources

1. **TrueFX**
   - Institutional-grade tick data
   - ~$50-200/month

2. **Kibot**
   - High-quality intraday data
   - ~$30-100/month

3. **Your Broker**
   - Often the best source
   - Same data as live trading
   - Usually free for clients

---

## Example: Complete Workflow with Real Data

### 1. Get Data from Dukascopy
```bash
# Download from https://www.dukascopy.com/swiss/english/marketwatch/historical/
# Select: EURUSD, M5, 2023-01-01 to 2024-01-01
# Format: CSV
```

### 2. Place in Project
```bash
mkdir -p data
mv ~/Downloads/EURUSD_M5_2023.csv data/EURUSD_5min.csv
```

### 3. Update run_backtest.py
```python
# Change line 41
use_sample=False  # Now uses real data!
```

### 4. Run Backtest
```bash
python run_backtest.py
```

### 5. Analyze Results
```bash
# Check results
open backtest_results.png
open trades.csv
```

---

## FAQ

**Q: Can I use the sample data for live trading decisions?**
A: No! Sample data is synthetic and doesn't represent real market behavior.

**Q: What's the best timeframe?**
A: 5 minutes is ideal for London Breakout. Lower timeframes (1min) need more data.

**Q: How much historical data do I need?**
A: Minimum 1 year, ideally 2-3 years for robust backtesting.

**Q: Does the strategy work with daily data?**
A: No, London Breakout is an intraday strategy requiring intraday data.

**Q: Can I use stock data?**
A: The strategy is designed for forex, but you can adapt it for stocks.

**Q: Where do I get cTrader historical data?**
A: Via the cTrader OpenAPI - see `ctrader_api.py` for implementation.

---

## Summary

| Data Source | Setup | Quality | Cost | Best For |
|-------------|-------|---------|------|----------|
| **Sample Data** | None | Low | Free | Testing/Learning |
| **CSV Files** | Easy | High | Free* | Serious Backtesting |
| **MT5 Export** | Easy | High | Free | MT5 Users |
| **Yahoo Finance** | Medium | Medium | Free | Quick Testing |
| **cTrader API** | Complex | Highest | Free | Live Trading Prep |

*Cost of acquiring data varies

---

**Current Setup:** Using **sample data** by default
**To Use Real Data:** Change `use_sample=False` in `run_backtest.py` and place CSV in `data/` folder

**Recommendation:** Start with sample data to learn, then switch to real data for actual strategy validation.
