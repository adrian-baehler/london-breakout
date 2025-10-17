"""
London Breakout Trading Strategy Implementation
"""
import pandas as pd
import numpy as np
from datetime import datetime, time, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

import config


class SignalType(Enum):
    """Trading signal types"""
    NONE = 0
    LONG = 1
    SHORT = -1


class PositionSide(Enum):
    """Position side"""
    LONG = 1
    SHORT = -1


@dataclass
class AsianRange:
    """Asian session price range"""
    high: float
    low: float
    timestamp: datetime

    @property
    def range_pips(self) -> float:
        """Calculate range in pips (assuming 4-digit quote)"""
        return (self.high - self.low) * 10000

    @property
    def midpoint(self) -> float:
        """Range midpoint"""
        return (self.high + self.low) / 2

    def is_valid(self) -> bool:
        """Check if range is valid for trading"""
        range_pips = self.range_pips
        return config.MIN_RANGE_PIPS <= range_pips <= config.MAX_RANGE_PIPS


@dataclass
class TradeSignal:
    """Trade signal with entry and exit levels"""
    signal_type: SignalType
    timestamp: datetime
    entry_price: float
    stop_loss: float
    take_profit: float
    asian_range: AsianRange

    @property
    def risk_pips(self) -> float:
        """Calculate risk in pips"""
        return abs(self.entry_price - self.stop_loss) * 10000

    @property
    def reward_pips(self) -> float:
        """Calculate reward in pips"""
        return abs(self.take_profit - self.entry_price) * 10000

    @property
    def risk_reward_ratio(self) -> float:
        """Calculate risk-reward ratio"""
        if self.risk_pips == 0:
            return 0
        return self.reward_pips / self.risk_pips


class LondonBreakoutStrategy:
    """
    London Breakout Strategy Implementation

    Strategy Rules:
    1. Identify Asian session range (00:00 - 07:00 UTC)
    2. Wait for London open (08:00 UTC)
    3. Enter on breakout above/below Asian range
    4. Stop-loss at opposite side of range
    5. Take-profit at 2x risk (configurable)
    """

    def __init__(self, symbol: str):
        self.symbol = symbol
        self.current_range: Optional[AsianRange] = None
        self.last_signal_date: Optional[datetime] = None

    def identify_asian_range(self, df: pd.DataFrame, target_date: datetime) -> Optional[AsianRange]:
        """
        Identify the Asian session price range for a given date

        Args:
            df: OHLC dataframe with datetime index
            target_date: Date to find Asian range for

        Returns:
            AsianRange object or None if not found
        """
        # Filter data for Asian session on target date
        asian_start = datetime.combine(target_date.date(), config.ASIAN_SESSION_START)
        asian_end = datetime.combine(target_date.date(), config.ASIAN_SESSION_END)

        # Get data within Asian session
        mask = (df.index >= asian_start) & (df.index < asian_end)
        asian_data = df[mask]

        if asian_data.empty:
            return None

        # Calculate high and low of Asian session
        high = asian_data['high'].max()
        low = asian_data['low'].min()

        asian_range = AsianRange(
            high=high,
            low=low,
            timestamp=asian_end
        )

        return asian_range if asian_range.is_valid() else None

    def calculate_trend_direction(self, df: pd.DataFrame, timestamp: datetime) -> int:
        """
        Calculate trend direction using EMA

        Args:
            df: OHLC dataframe with datetime index
            timestamp: Current timestamp

        Returns:
            1 for uptrend, -1 for downtrend, 0 for no trend
        """
        if not config.USE_TREND_FILTER:
            return 0

        # Get data up to current timestamp
        historical = df[df.index <= timestamp].copy()

        if len(historical) < config.TREND_EMA_PERIOD:
            return 0

        # Calculate EMA
        ema = historical['close'].ewm(span=config.TREND_EMA_PERIOD, adjust=False).mean()
        current_price = historical['close'].iloc[-1]
        current_ema = ema.iloc[-1]

        if current_price > current_ema:
            return 1  # Uptrend
        elif current_price < current_ema:
            return -1  # Downtrend
        else:
            return 0

    def check_breakout(self, current_bar: pd.Series, asian_range: AsianRange) -> SignalType:
        """
        Check if current bar breaks out of Asian range

        Args:
            current_bar: Current OHLC bar
            asian_range: Asian session range

        Returns:
            SignalType (LONG, SHORT, or NONE)
        """
        breakout_buffer = config.BREAKOUT_BUFFER_PIPS / 10000

        # Check for bullish breakout (close above high + buffer)
        if current_bar['close'] > asian_range.high + breakout_buffer:
            return SignalType.LONG

        # Check for bearish breakout (close below low - buffer)
        elif current_bar['close'] < asian_range.low - breakout_buffer:
            return SignalType.SHORT

        return SignalType.NONE

    def calculate_position_levels(
        self,
        signal_type: SignalType,
        entry_price: float,
        asian_range: AsianRange
    ) -> Tuple[float, float]:
        """
        Calculate stop-loss and take-profit levels

        Args:
            signal_type: LONG or SHORT
            entry_price: Entry price
            asian_range: Asian range for stop-loss calculation

        Returns:
            Tuple of (stop_loss, take_profit)
        """
        if signal_type == SignalType.LONG:
            # Long position: stop at Asian low
            stop_loss = asian_range.low
            risk = entry_price - stop_loss
            take_profit = entry_price + (risk * config.RISK_REWARD_RATIO)

        elif signal_type == SignalType.SHORT:
            # Short position: stop at Asian high
            stop_loss = asian_range.high
            risk = stop_loss - entry_price
            take_profit = entry_price - (risk * config.RISK_REWARD_RATIO)

        else:
            return 0.0, 0.0

        return stop_loss, take_profit

    def generate_signal(
        self,
        df: pd.DataFrame,
        current_time: datetime
    ) -> Optional[TradeSignal]:
        """
        Generate trading signal for current timestamp

        Args:
            df: OHLC dataframe with datetime index
            current_time: Current timestamp to evaluate

        Returns:
            TradeSignal object or None
        """
        # Only one signal per day
        if self.last_signal_date == current_time.date():
            return None

        # Check if we're in London trading window
        current_hour = current_time.time()
        london_open = config.LONDON_OPEN
        london_window_end = (
            datetime.combine(current_time.date(), london_open) +
            timedelta(hours=config.TRADING_WINDOW_HOURS)
        ).time()

        if not (london_open <= current_hour <= london_window_end):
            return None

        # Get or identify Asian range for current date
        if self.current_range is None or self.current_range.timestamp.date() != current_time.date():
            self.current_range = self.identify_asian_range(df, current_time)

        if self.current_range is None:
            return None

        # Get current bar
        current_bar = df.loc[current_time] if current_time in df.index else None
        if current_bar is None:
            return None

        # Check for breakout
        signal_type = self.check_breakout(current_bar, self.current_range)

        if signal_type == SignalType.NONE:
            return None

        # Apply trend filter if enabled
        if config.TRADE_WITH_TREND_ONLY:
            trend = self.calculate_trend_direction(df, current_time)

            # Skip if signal against trend
            if (signal_type == SignalType.LONG and trend == -1) or \
               (signal_type == SignalType.SHORT and trend == 1):
                return None

        # Calculate entry, stop-loss, and take-profit
        entry_price = current_bar['close']
        stop_loss, take_profit = self.calculate_position_levels(
            signal_type, entry_price, self.current_range
        )

        # Create trade signal
        trade_signal = TradeSignal(
            signal_type=signal_type,
            timestamp=current_time,
            entry_price=entry_price,
            stop_loss=stop_loss,
            take_profit=take_profit,
            asian_range=self.current_range
        )

        # Validate risk-reward ratio
        if trade_signal.risk_reward_ratio < config.MIN_RISK_REWARD:
            return None

        # Mark that we generated a signal today
        self.last_signal_date = current_time.date()

        return trade_signal

    def should_exit_time_based(self, current_time: datetime) -> bool:
        """
        Check if position should be exited based on time

        Args:
            current_time: Current timestamp

        Returns:
            True if should exit
        """
        if not config.USE_TIME_EXIT:
            return False

        # Exit before London close
        exit_time = (
            datetime.combine(current_time.date(), config.LONDON_CLOSE) -
            timedelta(minutes=config.EXIT_BEFORE_CLOSE_MINUTES)
        )

        return current_time >= exit_time

    def reset(self):
        """Reset strategy state"""
        self.current_range = None
        self.last_signal_date = None


class TradingSession:
    """Helper class to manage trading sessions"""

    @staticmethod
    def is_asian_session(dt: datetime) -> bool:
        """Check if timestamp is in Asian session"""
        t = dt.time()
        return config.ASIAN_SESSION_START <= t < config.ASIAN_SESSION_END

    @staticmethod
    def is_london_session(dt: datetime) -> bool:
        """Check if timestamp is in London session"""
        t = dt.time()
        return config.LONDON_OPEN <= t < config.LONDON_CLOSE

    @staticmethod
    def is_trading_window(dt: datetime) -> bool:
        """Check if timestamp is in London trading window"""
        t = dt.time()
        london_window_end = (
            datetime.combine(dt.date(), config.LONDON_OPEN) +
            timedelta(hours=config.TRADING_WINDOW_HOURS)
        ).time()
        return config.LONDON_OPEN <= t <= london_window_end
