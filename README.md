# London Breakout Trading Strategy

A complete Python implementation of the London Breakout day trading strategy with risk management, backtesting, and cTrader API integration.

![Alt text](https://github.com/adrian-baehler/london-breakout/blob/main/backtest_results.png)


## Strategy Overview

The London Breakout strategy capitalizes on the increased volatility and liquidity at the opening of the London trading session (08:00 GMT). The strategy:

1. **Identifies the Asian session range** (00:00 - 07:00 GMT)
2. **Waits for London open** (08:00 GMT)
3. **Enters on breakout** above or below the Asian range
4. **Sets stop-loss** at the opposite side of the range
5. **Targets 2:1 risk-reward ratio** (configurable)

### Key Features

- Comprehensive risk management (position sizing, daily loss limits)
- Advanced backtesting engine with performance metrics
- cTrader API integration for live trading
- Trend filtering and false breakout protection
- Trailing stop-loss functionality
- Detailed performance analytics and reporting

## Installation

### Option 1: Using DevContainer (Recommended)

The easiest way to get started with all dependencies pre-configured:

**Prerequisites:**
- [Docker Desktop](https://www.docker.com/products/docker-desktop)
- [VS Code](https://code.visualstudio.com/)
- [Dev Containers extension](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers)

**Steps:**
1. Open the project folder in VS Code
2. Press `F1` and select "Dev Containers: Reopen in Container"
3. Wait for container to build (first time: ~5-10 minutes)
4. Everything is ready to use!

The DevContainer includes:
- Python 3.11 with all dependencies
- TA-Lib pre-compiled
- Jupyter Lab
- VS Code extensions
- Automated setup

See [.devcontainer/README.md](.devcontainer/README.md) for more details.

### Option 2: Local Installation

#### 1. Clone or Download

```bash
cd /path/to/londonbreakout
```

#### 2. Create Virtual Environment (Recommended)

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

#### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

**Note:** TA-Lib requires the C library to be installed first:
- **Linux:** `sudo apt-get install ta-lib`
- **macOS:** `brew install ta-lib`
- **Windows:** Download from [TA-Lib releases](https://github.com/mrjbq7/ta-lib#dependencies)

#### 4. Install cTrader OpenAPI (Optional - for live trading)

```bash
pip install git+https://github.com/spotware/OpenApiPy.git
```

## Quick Start

### Run a Backtest

```bash
python run_backtest.py
```

This will:
- Generate sample EURUSD data (or load from CSV)
- Run the strategy backtest
- Display performance metrics
- Generate charts (saved as `backtest_results.png`)
- Export trade log to `trades.csv`

### Generate Sample Data

```bash
python data_loader.py
```

Creates sample 5-minute EURUSD data in `data/EURUSD_5min.csv`

### Optimize Parameters

```bash
python optimize.py
```

Runs grid search optimization to find optimal parameters.

## Configuration

Edit `config.py` to customize strategy parameters:

### Strategy Parameters

```python
# Asian session range detection
ASIAN_SESSION_START = time(0, 0)   # 00:00 UTC
ASIAN_SESSION_END = time(7, 0)     # 07:00 UTC

# London session timing
LONDON_OPEN = time(8, 0)           # 08:00 GMT
TRADING_WINDOW_HOURS = 2           # Trade within first 2 hours

# Breakout detection
BREAKOUT_BUFFER_PIPS = 2           # Buffer to avoid false breakouts
MIN_RANGE_PIPS = 15                # Minimum range size
MAX_RANGE_PIPS = 100               # Maximum range size
```

### Risk Management

```python
# Position sizing
RISK_PER_TRADE_PERCENT = 1.0       # Risk 1% per trade
POSITION_SIZE_PER_100 = 0.01       # 0.01 lots per $100

# Risk-reward
RISK_REWARD_RATIO = 2.0            # Target 2:1 R:R
MIN_RISK_REWARD = 1.5              # Minimum acceptable R:R

# Limits
MAX_DAILY_LOSS_PERCENT = 3.0       # Max 3% daily loss
MAX_OPEN_POSITIONS = 3             # Max concurrent positions
```

### Trading Pairs

```python
TRADING_PAIRS = [
    "EURUSD",
    "GBPUSD",
    "EURGBP",
    "USDJPY",
    "GBPJPY",
    "EURJPY"
]
```

## Live Trading with cTrader

### 1. Get cTrader Credentials

1. Visit [cTrader Open API](https://openapi.ctrader.com/)
2. Create an application to get:
   - Client ID
   - Client Secret
   - Access Token
   - Account ID

### 2. Configure Credentials

Copy `.env.example` to `.env` and fill in your credentials:

```bash
cp .env.example .env
```

Edit `.env`:

```
CTRADER_CLIENT_ID=your_client_id
CTRADER_CLIENT_SECRET=your_client_secret
CTRADER_ACCESS_TOKEN=your_access_token
CTRADER_ACCOUNT_ID=your_account_id
USE_DEMO=True
```

### 3. Run Live Trading (Template)

```python
from ctrader_api import CTraderClient, LiveTrader

# Create and connect client
client = CTraderClient()
client.connect()

# Initialize live trader
trader = LiveTrader("EURUSD", client)
trader.start()

# ... implement your main trading loop ...

# Stop and disconnect
trader.stop()
client.disconnect()
```

**IMPORTANT:** The live trading module is a framework/template. You need to implement the main trading loop and proper error handling before using with real money.

## Project Structure

```
londonbreakout/
├── config.py              # Configuration and parameters
├── strategy.py            # Core London Breakout strategy logic
├── risk_management.py     # Risk management system
├── backtest.py            # Backtesting engine
├── data_loader.py         # Data loading and preprocessing
├── ctrader_api.py         # cTrader API integration
├── run_backtest.py        # Backtest execution script
├── optimize.py            # Parameter optimization
├── requirements.txt       # Python dependencies
├── .env.example           # Example environment variables
└── README.md              # This file
```

## Usage Examples

### Custom Backtest

```python
from data_loader import DataLoader
from backtest import BacktestEngine

# Load your data
df = DataLoader.load_csv('data/EURUSD_5min.csv')

# Run backtest
engine = BacktestEngine("EURUSD", initial_capital=10000)
results = engine.run(df, start_date="2023-01-01", end_date="2024-01-01")

# Plot results
engine.plot_results(results)

# Export trades
engine.export_trades("my_trades.csv")
```

### Generate Signals Only

```python
from strategy import LondonBreakoutStrategy
import pandas as pd

# Load data
df = pd.read_csv('data/EURUSD_5min.csv', parse_dates=['timestamp'], index_col='timestamp')

# Create strategy
strategy = LondonBreakoutStrategy("EURUSD")

# Generate signal for specific time
signal = strategy.generate_signal(df, datetime(2023, 6, 15, 8, 30))

if signal:
    print(f"Signal: {signal.signal_type}")
    print(f"Entry: {signal.entry_price}")
    print(f"Stop Loss: {signal.stop_loss}")
    print(f"Take Profit: {signal.take_profit}")
```

### Custom Risk Management

```python
from risk_management import RiskManager

# Initialize with capital
risk_mgr = RiskManager(initial_capital=10000)

# Calculate position size
position_size = risk_mgr.calculate_position_size(
    entry_price=1.1000,
    stop_loss=1.0950,
    risk_percent=1.0  # Risk 1%
)

print(f"Position size: {position_size} lots")
```

## Performance Metrics

The backtest engine provides comprehensive metrics:

- **Total Trades** - Number of completed trades
- **Win Rate** - Percentage of winning trades
- **Profit Factor** - Gross profit / gross loss
- **Total Return** - Overall return percentage
- **Max Drawdown** - Maximum equity drawdown
- **Sharpe Ratio** - Risk-adjusted return (annualized)
- **Sortino Ratio** - Downside risk-adjusted return
- **Average Win/Loss** - Average profit/loss per trade
- **Consecutive Wins/Losses** - Longest winning/losing streaks

## Risk Disclaimer

**IMPORTANT:** This software is for educational and research purposes only.

- Trading forex carries substantial risk of loss
- Past performance does not guarantee future results
- Always test strategies on demo accounts first
- Never risk more than you can afford to lose
- This code is provided "as is" without warranty

**Use at your own risk. The authors are not responsible for any financial losses.**

## Contributing

Contributions are welcome! Areas for improvement:

- Additional entry/exit filters
- More data source integrations
- Machine learning signal enhancement
- Advanced order types
- Telegram/email notifications
- Web dashboard for monitoring

## License

MIT License - see LICENSE file for details

## Support

For issues, questions, or contributions:
- Open an issue on GitHub
- Review the code documentation
- Check cTrader API documentation: https://help.ctrader.com/open-api/

## Acknowledgments

- Strategy concept based on classic London Breakout methodology
- cTrader OpenAPI by Spotware Systems
- Built with pandas, numpy, matplotlib, and other open-source tools

## Version History

- **v1.0.0** (2025) - Initial release
  - Core strategy implementation
  - Backtesting engine
  - Risk management system
  - cTrader API integration
  - Parameter optimization

---

**Happy Trading!** Remember to always backtest thoroughly and start with a demo account.
