"""
Configuration file for London Breakout Trading Strategy
"""
from typing import List
from datetime import time

# ==================== STRATEGY PARAMETERS ====================

# Asian session range detection (before London open)
ASIAN_SESSION_START = time(0, 0)  # 00:00 UTC (Tokyo open)
ASIAN_SESSION_END = time(7, 0)    # 07:00 UTC (before London)

# London session timing
LONDON_OPEN = time(8, 0)          # 08:00 GMT/UTC
LONDON_CLOSE = time(16, 0)        # 16:00 GMT/UTC

# Trading window (how long after London open to look for breakouts)
TRADING_WINDOW_HOURS = 2          # Trade within first 2 hours

# Breakout detection
BREAKOUT_BUFFER_PIPS = 2          # Buffer to avoid false breakouts
MIN_RANGE_PIPS = 15               # Minimum range size to consider valid
MAX_RANGE_PIPS = 100              # Maximum range size (avoid extreme volatility)

# ==================== RISK MANAGEMENT ====================

# Position sizing
RISK_PER_TRADE_PERCENT = 1.0      # Risk 1% of account per trade
POSITION_SIZE_PER_100 = 0.01      # 0.01 lots per $100 capital

# Risk-reward ratios
RISK_REWARD_RATIO = 2.0           # Target 2:1 (can use 3.0 for 3:1)
MIN_RISK_REWARD = 1.5             # Minimum acceptable R:R

# Stop-loss and take-profit
STOP_LOSS_METHOD = "range"        # "range" (opposite side) or "atr" (ATR-based)
ATR_PERIOD = 14                   # If using ATR method
ATR_MULTIPLIER = 1.5              # ATR multiplier for stops

# Maximum risk limits
MAX_DAILY_LOSS_PERCENT = 3.0      # Max 3% daily loss
MAX_OPEN_POSITIONS = 3            # Maximum concurrent positions
MAX_POSITION_SIZE_LOTS = 1.0      # Maximum lot size per trade

# ==================== TRADING PAIRS ====================

# Recommended pairs for London Breakout
TRADING_PAIRS: List[str] = [
    "EURUSD",
    "GBPUSD",
    "EURGBP",
    "USDJPY",
    "GBPJPY",
    "EURJPY"
]

# ==================== FILTERS & CONFIRMATION ====================

# Trend filter
USE_TREND_FILTER = True
TREND_EMA_PERIOD = 200            # EMA for trend direction
TRADE_WITH_TREND_ONLY = True      # Only trade in trend direction

# Volume filter (if available)
USE_VOLUME_FILTER = False
MIN_VOLUME_MULTIPLIER = 1.2       # Breakout volume should be 1.2x average

# False breakout filter
USE_CANDLE_CONFIRMATION = True    # Wait for candle close confirmation
CONFIRMATION_TIMEFRAME = "5m"     # Timeframe for confirmation

# ==================== BACKTESTING ====================

# Backtest settings
INITIAL_CAPITAL = 10000           # Starting capital for backtest
COMMISSION_PER_LOT = 7.0          # Commission per lot (round trip)
SPREAD_PIPS = 1.5                 # Average spread in pips

# Date range (None = use all available data)
BACKTEST_START_DATE = "2023-01-01"
BACKTEST_END_DATE = None          # None = up to latest data

# ==================== CTRADER API ====================

# cTrader connection settings
CTRADER_HOST = "demo.ctraderapi.com"  # demo or live server
CTRADER_PORT = 5035                    # Port for API connection
CLIENT_ID = ""                         # Your client ID (from cTrader)
CLIENT_SECRET = ""                     # Your client secret
ACCESS_TOKEN = ""                      # OAuth access token
ACCOUNT_ID = ""                        # Trading account ID

# API settings
USE_DEMO = True                        # Use demo account (set False for live)
RECONNECT_ATTEMPTS = 5                 # Number of reconnection attempts
HEARTBEAT_INTERVAL = 30                # Heartbeat interval in seconds

# ==================== LOGGING & OUTPUT ====================

# Logging configuration
LOG_LEVEL = "INFO"                # DEBUG, INFO, WARNING, ERROR
LOG_TO_FILE = True
LOG_FILE = "londonbreakout.log"

# Trade logging
SAVE_TRADE_LOG = True
TRADE_LOG_FILE = "trades.csv"

# Performance reporting
GENERATE_REPORT = True
REPORT_FILE = "performance_report.html"

# ==================== ADVANCED SETTINGS ====================

# Time-based exit
USE_TIME_EXIT = True
EXIT_BEFORE_CLOSE_MINUTES = 30    # Exit positions 30min before London close

# Trailing stop
USE_TRAILING_STOP = True
TRAILING_STOP_ACTIVATION_RR = 1.0  # Activate after 1:1 R:R reached
TRAILING_STOP_DISTANCE_PIPS = 10   # Trail by 10 pips

# Partial profit taking
USE_PARTIAL_TAKE_PROFIT = False
PARTIAL_TP_PERCENT = 50            # Close 50% at first target
PARTIAL_TP_RR = 1.0                # First target at 1:1 R:R

# ==================== NOTIFICATIONS ====================

# Alert settings
ENABLE_NOTIFICATIONS = False
NOTIFICATION_EMAIL = ""
SEND_TRADE_ALERTS = True
SEND_DAILY_SUMMARY = True
