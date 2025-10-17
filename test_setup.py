#!/usr/bin/env python3
"""
Test Setup and Validation Script

Run this script to verify your installation and test the basic functionality.
"""
import sys


def test_imports():
    """Test if all required packages are importable"""
    print("Testing package imports...")

    required_packages = [
        ('numpy', 'NumPy'),
        ('pandas', 'Pandas'),
        ('matplotlib', 'Matplotlib'),
        ('seaborn', 'Seaborn')
    ]

    optional_packages = [
        ('pandas_ta', 'Pandas-TA'),
        ('backtrader', 'Backtrader'),
    ]

    all_good = True

    # Test required packages
    for package, name in required_packages:
        try:
            __import__(package)
            print(f"  ✓ {name} - OK")
        except ImportError:
            print(f"  ✗ {name} - MISSING (required)")
            all_good = False

    # Test optional packages
    for package, name in optional_packages:
        try:
            __import__(package)
            print(f"  ✓ {name} - OK")
        except ImportError:
            print(f"  ⚠ {name} - Not installed (optional)")

    # Test cTrader API
    try:
        from OpenApiPy import Client
        print(f"  ✓ OpenApiPy (cTrader API) - OK")
    except ImportError:
        print(f"  ⚠ OpenApiPy - Not installed (only needed for live trading)")

    return all_good


def test_modules():
    """Test if project modules load correctly"""
    print("\nTesting project modules...")

    modules = [
        'config',
        'strategy',
        'risk_management',
        'backtest',
        'data_loader',
        'ctrader_api'
    ]

    all_good = True

    for module in modules:
        try:
            __import__(module)
            print(f"  ✓ {module}.py - OK")
        except ImportError as e:
            print(f"  ✗ {module}.py - ERROR: {e}")
            all_good = False
        except Exception as e:
            print(f"  ⚠ {module}.py - WARNING: {e}")

    return all_good


def test_data_generation():
    """Test sample data generation"""
    print("\nTesting data generation...")

    try:
        from data_loader import DataLoader

        df = DataLoader.generate_sample_data(
            symbol="EURUSD",
            start_date="2024-01-01",
            end_date="2024-01-02",
            timeframe="5min"
        )

        print(f"  ✓ Generated {len(df)} bars")
        print(f"  ✓ Columns: {list(df.columns)}")
        print(f"  ✓ Date range: {df.index[0]} to {df.index[-1]}")

        return True
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return False


def test_strategy():
    """Test strategy signal generation"""
    print("\nTesting strategy logic...")

    try:
        from strategy import LondonBreakoutStrategy
        from data_loader import DataLoader
        from datetime import datetime

        # Generate sample data
        df = DataLoader.generate_sample_data(
            symbol="EURUSD",
            start_date="2024-01-01",
            end_date="2024-01-02",
            timeframe="5min"
        )

        # Create strategy
        strategy = LondonBreakoutStrategy("EURUSD")

        # Try to generate a signal
        test_time = datetime(2024, 1, 1, 8, 30)  # London session
        signal = strategy.generate_signal(df, test_time)

        print(f"  ✓ Strategy initialized")
        print(f"  ✓ Signal generation works (signal: {signal is not None})")

        return True
    except Exception as e:
        print(f"  ✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_risk_management():
    """Test risk management calculations"""
    print("\nTesting risk management...")

    try:
        from risk_management import RiskManager

        # Create risk manager
        rm = RiskManager(initial_capital=10000)

        # Test position sizing
        position_size = rm.calculate_position_size(
            entry_price=1.1000,
            stop_loss=1.0950,
            risk_percent=1.0
        )

        print(f"  ✓ Risk manager initialized (capital: $10,000)")
        print(f"  ✓ Position sizing works (size: {position_size} lots)")

        # Test position opening
        position = rm.open_position(
            symbol="EURUSD",
            side="LONG",
            entry_price=1.1000,
            stop_loss=1.0950,
            take_profit=1.1100,
            entry_time=None
        )

        if position:
            print(f"  ✓ Position management works")
        else:
            print(f"  ⚠ Position not opened (check risk limits)")

        return True
    except Exception as e:
        print(f"  ✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_mini_backtest():
    """Run a mini backtest"""
    print("\nRunning mini backtest...")

    try:
        from data_loader import DataLoader
        from backtest import BacktestEngine

        # Generate small dataset
        df = DataLoader.generate_sample_data(
            symbol="EURUSD",
            start_date="2024-01-01",
            end_date="2024-01-07",  # Just 1 week
            timeframe="5min"
        )

        # Run backtest
        engine = BacktestEngine("EURUSD", initial_capital=10000)
        results = engine.run(df, verbose=False)

        print(f"  ✓ Backtest completed")
        print(f"  ✓ Total trades: {results['total_trades']}")
        print(f"  ✓ Win rate: {results['win_rate']:.2f}%")
        print(f"  ✓ Final equity: ${results['current_equity']:.2f}")

        return True
    except Exception as e:
        print(f"  ✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests"""
    print("=" * 70)
    print("LONDON BREAKOUT STRATEGY - SETUP VALIDATION")
    print("=" * 70)
    print()

    results = {
        'imports': test_imports(),
        'modules': test_modules(),
        'data': test_data_generation(),
        'strategy': test_strategy(),
        'risk': test_risk_management(),
        'backtest': test_mini_backtest()
    }

    print("\n" + "=" * 70)
    print("TEST RESULTS")
    print("=" * 70)

    for test_name, passed in results.items():
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{test_name.upper()}: {status}")

    all_passed = all(results.values())

    print()
    if all_passed:
        print("✓ All tests passed! Your setup is ready.")
        print("\nNext steps:")
        print("  1. Run: python run_backtest.py")
        print("  2. Check out QUICKSTART.md for more examples")
        print("  3. Read README.md for full documentation")
    else:
        print("✗ Some tests failed. Please check the errors above.")
        print("\nTroubleshooting:")
        print("  1. Make sure all requirements are installed:")
        print("     pip install -r requirements.txt")
        print("  2. Check that Python version is 3.8+")
        print("  3. Review the error messages for specific issues")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
