#!/usr/bin/env python3
"""
Run London Breakout Strategy Backtest

This script demonstrates how to run a backtest of the London Breakout strategy.
"""
import os
import sys
from datetime import datetime

from data_loader import prepare_backtest_data, YahooFinanceLoader, DataLoader
from backtest import BacktestEngine
import config


def main():
    """Run backtest"""
    print("=" * 70)
    print("LONDON BREAKOUT STRATEGY BACKTESTER")
    print("=" * 70)
    print()

    # Configuration
    symbol = "EURUSD"
    yahoo_ticker = "EURUSD=X"  # Yahoo Finance format for forex
    start_date = config.BACKTEST_START_DATE or "2023-01-01"
    end_date = config.BACKTEST_END_DATE or "2024-01-01"
    initial_capital = config.INITIAL_CAPITAL

    print(f"Symbol: {symbol}")
    print(f"Period: {start_date} to {end_date}")
    print(f"Initial Capital: ${initial_capital:,.2f}")
    print(f"Data Source: Yahoo Finance (with fallback)")
    print()

    # Try to download data from Yahoo Finance
    print("Attempting to download from Yahoo Finance...")
    print("Note: Yahoo Finance has limitations:")
    print("  - 5m data: last 60 days only")
    print("  - 1h data: last 730 days only")
    print("  - 1d data: many years available")
    print()

    data_loaded = False

    # Try 1-hour data (last 720 days to stay within Yahoo's 730-day limit)
    try:
        from datetime import datetime as dt, timedelta
        recent_start = (dt.now() - timedelta(days=720)).strftime("%Y-%m-%d")
        recent_end = dt.now().strftime("%Y-%m-%d")

        print(f"Trying 1h data: {recent_start} to {recent_end} (720 days)...")
        df = YahooFinanceLoader.download(
            ticker=yahoo_ticker,
            start_date=recent_start,
            end_date=recent_end,
            interval="1h"
        )

        df = DataLoader.clean_data(df)
        df = DataLoader.add_time_features(df)

        print(f"✓ Successfully loaded {len(df)} bars from Yahoo Finance!")
        print(f"  Date range: {df.index[0]} to {df.index[-1]}")
        data_loaded = True
        print()
    except Exception as e:
        print(f"✗ 1-hour data failed: {str(e)[:100]}...")
        print()

    # Fallback to sample data
    if not data_loaded:
        print("Yahoo Finance unavailable - using generated sample data...")
        print("(For real backtesting, use CSV data from your broker)")
        print()
        df = prepare_backtest_data(
            symbol=symbol,
            start_date=start_date,
            end_date=end_date,
            timeframe="5min",
            use_sample=True
        )
        print(f"✓ Generated {len(df)} sample bars")
        print()

    # Create backtest engine
    engine = BacktestEngine(symbol, initial_capital)

    # Run backtest with actual data date range
    actual_start = df.index[0].strftime("%Y-%m-%d")
    actual_end = df.index[-1].strftime("%Y-%m-%d")

    print("Running backtest...")
    print("-" * 70)
    results = engine.run(df, actual_start, actual_end)

    # Plot results
    print("\nGenerating performance charts...")
    engine.plot_results(results, save_path="backtest_results.png")

    # Export trades
    if config.SAVE_TRADE_LOG:
        print("Exporting trade log...")
        engine.export_trades("trades.csv")

    print("\nBacktest completed successfully!")
    print(f"Results saved to: backtest_results.png")
    if config.SAVE_TRADE_LOG:
        print(f"Trade log saved to: trades.csv")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nBacktest interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
