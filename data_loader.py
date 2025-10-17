"""
Data Loader for Historical Market Data

Supports multiple data sources:
- CSV files
- cTrader API historical data
- MetaTrader exports
- Yahoo Finance (via yfinance)
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Optional, List
import os


class DataLoader:
    """
    Load and preprocess historical OHLC data for backtesting
    """

    @staticmethod
    def load_csv(
        filepath: str,
        date_column: str = 'timestamp',
        date_format: Optional[str] = None
    ) -> pd.DataFrame:
        """
        Load OHLC data from CSV file

        Expected columns: timestamp, open, high, low, close, volume (optional)

        Args:
            filepath: Path to CSV file
            date_column: Name of date/timestamp column
            date_format: Date format string (auto-detected if None)

        Returns:
            DataFrame with datetime index and OHLC columns
        """
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Data file not found: {filepath}")

        # Read CSV
        df = pd.read_csv(filepath)

        # Parse dates
        if date_format:
            df[date_column] = pd.to_datetime(df[date_column], format=date_format)
        else:
            df[date_column] = pd.to_datetime(df[date_column])

        # Set index
        df.set_index(date_column, inplace=True)
        df.sort_index(inplace=True)

        # Standardize column names
        column_mapping = {
            'Open': 'open',
            'High': 'high',
            'Low': 'low',
            'Close': 'close',
            'Volume': 'volume'
        }
        df.rename(columns=column_mapping, inplace=True)

        # Ensure required columns exist
        required_columns = ['open', 'high', 'low', 'close']
        missing_columns = [col for col in required_columns if col not in df.columns]

        if missing_columns:
            raise ValueError(f"Missing required columns: {missing_columns}")

        return df[['open', 'high', 'low', 'close'] + (['volume'] if 'volume' in df.columns else [])]

    @staticmethod
    def load_mt5_export(filepath: str) -> pd.DataFrame:
        """
        Load data from MetaTrader 5 export format

        MT5 CSV format: Date, Time, Open, High, Low, Close, Volume

        Args:
            filepath: Path to MT5 CSV export

        Returns:
            DataFrame with datetime index
        """
        df = pd.read_csv(filepath)

        # Combine Date and Time columns
        df['timestamp'] = pd.to_datetime(df['Date'] + ' ' + df['Time'])

        # Set index and select columns
        df.set_index('timestamp', inplace=True)
        df = df[['Open', 'High', 'Low', 'Close', 'Volume']].copy()

        # Rename columns
        df.columns = ['open', 'high', 'low', 'close', 'volume']

        return df

    @staticmethod
    def generate_sample_data(
        symbol: str,
        start_date: str,
        end_date: str,
        timeframe: str = '5min',
        base_price: float = 1.1000
    ) -> pd.DataFrame:
        """
        Generate sample/synthetic OHLC data for testing

        Args:
            symbol: Symbol name
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            timeframe: Timeframe ('1min', '5min', '15min', '1H', '1D')
            base_price: Starting price

        Returns:
            DataFrame with synthetic OHLC data
        """
        # Create date range
        dates = pd.date_range(start=start_date, end=end_date, freq=timeframe)

        # Generate random price movements
        np.random.seed(42)
        n = len(dates)

        # Generate returns
        returns = np.random.normal(0, 0.0001, n)  # Small returns for forex

        # Generate prices
        close_prices = base_price * np.exp(np.cumsum(returns))

        # Generate OHLC from close prices
        data = []
        for i, price in enumerate(close_prices):
            # Add some randomness to create realistic OHLC
            volatility = abs(np.random.normal(0, 0.0002))

            high = price + abs(np.random.normal(0, volatility))
            low = price - abs(np.random.normal(0, volatility))
            open_price = low + (high - low) * np.random.random()

            # Ensure OHLC logic
            high = max(high, open_price, price)
            low = min(low, open_price, price)

            data.append({
                'open': open_price,
                'high': high,
                'low': low,
                'close': price,
                'volume': int(np.random.uniform(1000, 10000))
            })

        df = pd.DataFrame(data, index=dates)
        df.index.name = 'timestamp'

        print(f"Generated {len(df)} bars of sample data for {symbol}")
        print(f"Period: {df.index[0]} to {df.index[-1]}")

        return df

    @staticmethod
    def resample_data(df: pd.DataFrame, timeframe: str) -> pd.DataFrame:
        """
        Resample OHLC data to different timeframe

        Args:
            df: OHLC DataFrame
            timeframe: Target timeframe ('5min', '15min', '1H', '4H', '1D')

        Returns:
            Resampled DataFrame
        """
        resampled = df.resample(timeframe).agg({
            'open': 'first',
            'high': 'max',
            'low': 'min',
            'close': 'last',
            'volume': 'sum' if 'volume' in df.columns else lambda x: 0
        })

        # Drop NaN rows (incomplete periods)
        resampled.dropna(inplace=True)

        return resampled

    @staticmethod
    def clean_data(df: pd.DataFrame, remove_weekends: bool = True) -> pd.DataFrame:
        """
        Clean and validate OHLC data

        Args:
            df: OHLC DataFrame
            remove_weekends: Remove weekend data (for forex)

        Returns:
            Cleaned DataFrame
        """
        # Remove duplicates
        df = df[~df.index.duplicated(keep='first')]

        # Remove rows with missing values
        df.dropna(inplace=True)

        # Validate OHLC logic (high >= low, etc.)
        invalid_rows = (
            (df['high'] < df['low']) |
            (df['high'] < df['open']) |
            (df['high'] < df['close']) |
            (df['low'] > df['open']) |
            (df['low'] > df['close'])
        )

        if invalid_rows.any():
            print(f"Warning: Removed {invalid_rows.sum()} rows with invalid OHLC data")
            df = df[~invalid_rows]

        # Remove weekends (forex markets closed)
        if remove_weekends:
            df = df[df.index.dayofweek < 5]  # 0=Monday, 4=Friday

        # Remove zero or negative prices
        price_cols = ['open', 'high', 'low', 'close']
        valid_prices = (df[price_cols] > 0).all(axis=1)
        df = df[valid_prices]

        return df

    @staticmethod
    def add_time_features(df: pd.DataFrame) -> pd.DataFrame:
        """
        Add time-based features to DataFrame

        Args:
            df: OHLC DataFrame with datetime index

        Returns:
            DataFrame with added time features
        """
        df = df.copy()

        df['hour'] = df.index.hour
        df['day_of_week'] = df.index.dayofweek
        df['day'] = df.index.day
        df['month'] = df.index.month
        df['year'] = df.index.year

        # Trading sessions
        df['is_asian_session'] = (df['hour'] >= 0) & (df['hour'] < 8)
        df['is_london_session'] = (df['hour'] >= 8) & (df['hour'] < 16)
        df['is_ny_session'] = (df['hour'] >= 13) & (df['hour'] < 22)

        return df

    @staticmethod
    def save_to_csv(df: pd.DataFrame, filepath: str):
        """
        Save DataFrame to CSV

        Args:
            df: DataFrame to save
            filepath: Output file path
        """
        df.to_csv(filepath)
        print(f"Data saved to: {filepath}")


class YahooFinanceLoader:
    """
    Load data from Yahoo Finance (for stocks/indices)

    Note: Requires yfinance package: pip install yfinance
    """

    @staticmethod
    def download(
        ticker: str,
        start_date: str,
        end_date: str,
        interval: str = '5m'
    ) -> pd.DataFrame:
        """
        Download data from Yahoo Finance

        Args:
            ticker: Ticker symbol (e.g., 'EURUSD=X' for forex)
            start_date: Start date
            end_date: End date
            interval: Data interval ('1m', '5m', '15m', '1h', '1d')

        Returns:
            OHLC DataFrame
        """
        try:
            import yfinance as yf
        except ImportError:
            raise ImportError(
                "yfinance not installed. Install with: pip install yfinance"
            )

        print(f"Downloading {ticker} data from Yahoo Finance...")

        df = yf.download(
            ticker,
            start=start_date,
            end=end_date,
            interval=interval,
            progress=False,
            auto_adjust=True
        )

        if df.empty:
            raise ValueError(f"No data returned for {ticker}")

        # Handle MultiIndex columns (if multiple tickers)
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)

        # Standardize column names
        df.columns = [str(col).lower() for col in df.columns]
        df.index.name = 'timestamp'

        # Convert timezone-aware index to timezone-naive (UTC)
        if df.index.tz is not None:
            df.index = df.index.tz_convert('UTC').tz_localize(None)

        print(f"Downloaded {len(df)} bars")

        # Ensure we have the required columns
        required_cols = ['open', 'high', 'low', 'close']
        available_cols = [col for col in required_cols if col in df.columns]

        if not all(col in df.columns for col in required_cols):
            raise ValueError(f"Missing required columns. Available: {list(df.columns)}")

        result_cols = available_cols + (['volume'] if 'volume' in df.columns else [])
        return df[result_cols]


# Example usage and helper functions
def prepare_backtest_data(
    symbol: str,
    start_date: str = "2023-01-01",
    end_date: str = "2024-01-01",
    timeframe: str = "5min",
    use_sample: bool = True
) -> pd.DataFrame:
    """
    Prepare data for backtesting

    Args:
        symbol: Trading symbol
        start_date: Start date
        end_date: End date
        timeframe: Data timeframe
        use_sample: Use generated sample data if True

    Returns:
        Clean OHLC DataFrame ready for backtesting
    """
    if use_sample:
        # Generate sample data
        df = DataLoader.generate_sample_data(
            symbol, start_date, end_date, timeframe
        )
    else:
        # Try to load from file
        filename = f"data/{symbol}_{timeframe}.csv"
        if os.path.exists(filename):
            df = DataLoader.load_csv(filename)
        else:
            raise FileNotFoundError(
                f"Data file not found: {filename}\n"
                "Set use_sample=True to generate sample data"
            )

    # Clean data
    df = DataLoader.clean_data(df)

    # Add time features
    df = DataLoader.add_time_features(df)

    return df


if __name__ == "__main__":
    # Example: Generate and save sample data
    print("Generating sample data for EURUSD...")

    df = DataLoader.generate_sample_data(
        symbol="EURUSD",
        start_date="2023-01-01",
        end_date="2024-01-01",
        timeframe="5min",
        base_price=1.1000
    )

    # Clean and add features
    df = DataLoader.clean_data(df)
    df = DataLoader.add_time_features(df)

    # Save to file
    os.makedirs("data", exist_ok=True)
    DataLoader.save_to_csv(df, "data/EURUSD_5min.csv")

    print("\nData summary:")
    print(df.info())
    print("\nFirst few rows:")
    print(df.head())
