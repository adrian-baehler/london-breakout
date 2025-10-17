#!/usr/bin/env python3
"""
Test Yahoo Finance data download
"""
from data_loader import YahooFinanceLoader, DataLoader
from datetime import datetime, timedelta

print("=" * 70)
print("YAHOO FINANCE DATA TEST")
print("=" * 70)
print()

# Test 1: Recent 5-minute data (last 30 days)
print("Test 1: Recent 5-minute data (last 30 days)")
print("-" * 70)
end_date = datetime.now()
start_date = end_date - timedelta(days=30)

print(f"Ticker: EURUSD=X")
print(f"Period: {start_date.date()} to {end_date.date()}")
print(f"Interval: 5m")
print()

try:
    df = YahooFinanceLoader.download(
        ticker="EURUSD=X",
        start_date=start_date.strftime("%Y-%m-%d"),
        end_date=end_date.strftime("%Y-%m-%d"),
        interval="5m"
    )
    print(f"✓ Success! Downloaded {len(df)} bars")
    print(f"\nDate range: {df.index[0]} to {df.index[-1]}")
    print(f"\nSample data:")
    print(df.head())
    print()
except Exception as e:
    print(f"✗ Failed: {e}")
    print()

# Test 2: Hourly data (longer history)
print("\n" + "=" * 70)
print("Test 2: Hourly data (1 year history)")
print("-" * 70)
print(f"Ticker: EURUSD=X")
print(f"Period: 2023-01-01 to 2024-01-01")
print(f"Interval: 1h")
print()

try:
    df = YahooFinanceLoader.download(
        ticker="EURUSD=X",
        start_date="2023-01-01",
        end_date="2024-01-01",
        interval="1h"
    )
    print(f"✓ Success! Downloaded {len(df)} bars")
    print(f"\nDate range: {df.index[0]} to {df.index[-1]}")
    print(f"\nSample data:")
    print(df.head())

    # Clean and prepare
    print("\nCleaning data...")
    df = DataLoader.clean_data(df)
    df = DataLoader.add_time_features(df)
    print(f"✓ After cleaning: {len(df)} bars")
    print()
except Exception as e:
    print(f"✗ Failed: {e}")
    print()

# Test 3: Daily data (full history)
print("\n" + "=" * 70)
print("Test 3: Daily data (multi-year history)")
print("-" * 70)
print(f"Ticker: EURUSD=X")
print(f"Period: 2020-01-01 to 2024-01-01")
print(f"Interval: 1d")
print()

try:
    df = YahooFinanceLoader.download(
        ticker="EURUSD=X",
        start_date="2020-01-01",
        end_date="2024-01-01",
        interval="1d"
    )
    print(f"✓ Success! Downloaded {len(df)} bars")
    print(f"\nDate range: {df.index[0]} to {df.index[-1]}")
    print(f"\nStatistics:")
    print(df[['close']].describe())
    print()
except Exception as e:
    print(f"✗ Failed: {e}")
    print()

print("=" * 70)
print("SUMMARY")
print("=" * 70)
print("""
Yahoo Finance Limitations:
- 5-minute data: Only last 60 days available
- 1-hour data: ~2 years history
- Daily data: Many years available

Recommendation for London Breakout:
- Use 1-hour interval (1h) for backtesting
- Or use sample data for testing
- Or get real 5-minute data from broker/CSV

Next Steps:
1. Update config.py dates to last 30 days for 5m data
2. OR use 1h interval instead of 5m
3. OR use CSV data from broker
""")
