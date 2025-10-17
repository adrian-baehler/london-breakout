# Quick Start Guide

Get up and running with the London Breakout strategy in 5 minutes!

## Step 1: Install Dependencies

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install packages
pip install numpy pandas matplotlib seaborn
pip install pandas-ta backtrader python-dotenv

# Optional: TA-Lib (for advanced indicators)
# pip install ta-lib  # Requires TA-Lib C library
```

## Step 2: Run Your First Backtest

```bash
python run_backtest.py
```

This will:
- Generate sample EURUSD data for 2023
- Run the London Breakout strategy
- Print performance metrics
- Save results chart to `backtest_results.png`
- Export trade log to `trades.csv`

## Step 3: Review Results

Open `backtest_results.png` to see:
- Equity curve
- Drawdown chart
- Trade distribution
- P&L histogram
- Performance summary

Check `trades.csv` for detailed trade-by-trade analysis.

## Step 4: Customize Strategy (Optional)

Edit `config.py` to adjust parameters:

```python
# Try different risk-reward ratios
RISK_REWARD_RATIO = 3.0  # Change from 2.0 to 3.0

# Adjust breakout buffer
BREAKOUT_BUFFER_PIPS = 3  # Change from 2 to 3

# Change trading window
TRADING_WINDOW_HOURS = 3  # Change from 2 to 3
```

Re-run the backtest to see how changes affect performance.

## Step 5: Optimize Parameters

Find the best parameters for your data:

```bash
python optimize.py
```

This tests multiple parameter combinations and saves results to `optimization_results.csv`.

## Next Steps

### Use Your Own Data

1. Get historical forex data (MT5 export, CSV, etc.)
2. Place in `data/` folder
3. Update `run_backtest.py`:

```python
df = prepare_backtest_data(
    symbol="EURUSD",
    start_date="2023-01-01",
    end_date="2024-01-01",
    use_sample=False  # Use real data
)
```

### Connect to cTrader (Live Trading)

1. Get credentials from https://openapi.ctrader.com/
2. Copy `.env.example` to `.env`
3. Fill in your credentials
4. Install OpenAPI: `pip install git+https://github.com/spotware/OpenApiPy.git`
5. See `ctrader_api.py` for implementation

**WARNING:** Always test on demo account first!

## Common Issues

### "TA-Lib not found"

TA-Lib is optional. If you see this warning, you can either:
- Install TA-Lib C library + Python wrapper
- Comment out TA-Lib in `requirements.txt` (pandas-ta can be used instead)

### "No module named OpenApiPy"

This is normal if you haven't installed cTrader API. Only needed for live trading.

```bash
pip install git+https://github.com/spotware/OpenApiPy.git
```

### "No data available"

Make sure you have data in the correct format:
- Columns: timestamp, open, high, low, close
- CSV format with headers
- Or use `use_sample=True` to generate test data

## Example Output

```
LONDON BREAKOUT STRATEGY BACKTESTER
======================================================================

Symbol: EURUSD
Period: 2023-01-01 to 2024-01-01
Initial Capital: $10,000.00

Loading market data...
Loaded 52560 bars

Running backtest...
----------------------------------------------------------------------
2023-01-02 08:15:00 | LONG | Entry: 1.10250 | SL: 1.10100 | TP: 1.10550 | Size: 0.05 lots
2023-01-03 08:20:00 | SHORT | Entry: 1.10180 | SL: 1.10320 | TP: 1.09900 | Size: 0.05 lots
...

======================================================================
BACKTEST COMPLETED
======================================================================

Total Trades: 156
Winners: 109 | Losers: 47
Win Rate: 69.87%

Profit Factor: 2.14
Average Win: $82.50
Average Loss: -$41.20

Total P&L: $4,125.30 (41.25%)
Final Equity: $14,125.30
Return: 41.25%

Max Drawdown: -8.34%
Sharpe Ratio: 1.82
Sortino Ratio: 2.45
```

## Tips for Success

1. **Start Simple** - Use default parameters first
2. **Test Thoroughly** - Backtest on multiple years of data
3. **Understand Drawdowns** - Know your max loss tolerance
4. **Paper Trade** - Test on demo before going live
5. **Keep Records** - Save all backtest results for comparison
6. **Risk Management** - Never risk more than 1-2% per trade
7. **Be Patient** - The strategy doesn't trade every day

## Resources

- **Strategy Documentation:** See README.md
- **cTrader API Docs:** https://help.ctrader.com/open-api/
- **Python Docs:** https://docs.python.org/3/
- **Pandas Guide:** https://pandas.pydata.org/docs/

## Need Help?

- Check the code comments - they're extensive
- Review the example scripts
- Read the full README.md
- Test with sample data first

Happy trading! Remember: Always test strategies thoroughly before risking real money.
