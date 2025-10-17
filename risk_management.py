"""
Risk Management System for London Breakout Strategy
"""
import numpy as np
from typing import Dict, Optional, List, Tuple
from dataclasses import dataclass, field
from datetime import datetime, date

import config


@dataclass
class Position:
    """Represents an open position"""
    symbol: str
    side: str  # "LONG" or "SHORT"
    entry_price: float
    stop_loss: float
    take_profit: float
    size_lots: float
    entry_time: datetime
    position_id: Optional[str] = None

    @property
    def risk_pips(self) -> float:
        """Calculate risk in pips"""
        return abs(self.entry_price - self.stop_loss) * 10000

    @property
    def current_risk_amount(self) -> float:
        """Calculate current risk in account currency"""
        # Assuming 1 pip = $10 per standard lot for simplicity
        # In production, use actual pip value calculation
        pip_value = 10.0 * self.size_lots
        return self.risk_pips * pip_value

    def calculate_pnl(self, current_price: float) -> float:
        """
        Calculate current P&L in pips

        Args:
            current_price: Current market price

        Returns:
            P&L in pips (positive = profit, negative = loss)
        """
        if self.side == "LONG":
            return (current_price - self.entry_price) * 10000
        else:  # SHORT
            return (self.entry_price - current_price) * 10000

    def is_stop_hit(self, current_price: float) -> bool:
        """Check if stop-loss is hit"""
        if self.side == "LONG":
            return current_price <= self.stop_loss
        else:  # SHORT
            return current_price >= self.stop_loss

    def is_target_hit(self, current_price: float) -> bool:
        """Check if take-profit is hit"""
        if self.side == "LONG":
            return current_price >= self.take_profit
        else:  # SHORT
            return current_price <= self.take_profit


@dataclass
class Trade:
    """Completed trade record"""
    symbol: str
    side: str
    entry_price: float
    exit_price: float
    stop_loss: float
    take_profit: float
    size_lots: float
    entry_time: datetime
    exit_time: datetime
    pnl_pips: float
    pnl_amount: float
    exit_reason: str  # "TP", "SL", "TIME", "MANUAL"
    commission: float = 0.0

    @property
    def net_pnl(self) -> float:
        """Net P&L after commission"""
        return self.pnl_amount - self.commission

    @property
    def duration_minutes(self) -> float:
        """Trade duration in minutes"""
        return (self.exit_time - self.entry_time).total_seconds() / 60

    @property
    def was_winner(self) -> bool:
        """Check if trade was profitable"""
        return self.net_pnl > 0


class RiskManager:
    """
    Risk Management System

    Responsibilities:
    - Position sizing based on account equity and risk percentage
    - Track open positions and daily P&L
    - Enforce maximum risk limits
    - Calculate optimal lot size for each trade
    """

    def __init__(self, initial_capital: float):
        self.initial_capital = initial_capital
        self.current_equity = initial_capital
        self.open_positions: List[Position] = []
        self.closed_trades: List[Trade] = []
        self.daily_pnl: Dict[date, float] = {}

    @property
    def total_pnl(self) -> float:
        """Calculate total P&L from closed trades"""
        return sum(trade.net_pnl for trade in self.closed_trades)

    @property
    def open_risk(self) -> float:
        """Calculate total risk from open positions"""
        return sum(pos.current_risk_amount for pos in self.open_positions)

    @property
    def win_rate(self) -> float:
        """Calculate win rate percentage"""
        if not self.closed_trades:
            return 0.0
        winners = sum(1 for trade in self.closed_trades if trade.was_winner)
        return (winners / len(self.closed_trades)) * 100

    @property
    def average_win(self) -> float:
        """Calculate average winning trade"""
        winners = [t.net_pnl for t in self.closed_trades if t.was_winner]
        return np.mean(winners) if winners else 0.0

    @property
    def average_loss(self) -> float:
        """Calculate average losing trade"""
        losers = [t.net_pnl for t in self.closed_trades if not t.was_winner]
        return np.mean(losers) if losers else 0.0

    @property
    def profit_factor(self) -> float:
        """Calculate profit factor (gross profit / gross loss)"""
        gross_profit = sum(t.net_pnl for t in self.closed_trades if t.was_winner)
        gross_loss = abs(sum(t.net_pnl for t in self.closed_trades if not t.was_winner))

        if gross_loss == 0:
            return float('inf') if gross_profit > 0 else 0.0

        return gross_profit / gross_loss

    def calculate_position_size(
        self,
        entry_price: float,
        stop_loss: float,
        risk_percent: Optional[float] = None
    ) -> float:
        """
        Calculate position size in lots based on risk

        Args:
            entry_price: Planned entry price
            stop_loss: Stop-loss price
            risk_percent: Risk percentage (uses config default if None)

        Returns:
            Position size in lots
        """
        if risk_percent is None:
            risk_percent = config.RISK_PER_TRADE_PERCENT

        # Calculate risk in account currency
        risk_amount = self.current_equity * (risk_percent / 100)

        # Calculate risk in pips
        risk_pips = abs(entry_price - stop_loss) * 10000

        if risk_pips == 0:
            return 0.0

        # Calculate position size
        # Assuming 1 pip = $10 per standard lot (simplified)
        # In production, calculate actual pip value based on pair
        pip_value_per_lot = 10.0
        position_size = risk_amount / (risk_pips * pip_value_per_lot)

        # Apply limits
        position_size = min(position_size, config.MAX_POSITION_SIZE_LOTS)

        # Apply simple rule: 0.01 lots per $100
        simple_size = (self.current_equity / 100) * config.POSITION_SIZE_PER_100
        position_size = min(position_size, simple_size)

        # Round to 2 decimal places
        return round(position_size, 2)

    def can_open_position(self, risk_amount: float, current_date: date) -> Tuple[bool, str]:
        """
        Check if new position can be opened based on risk limits

        Args:
            risk_amount: Risk amount for new position
            current_date: Current trading date

        Returns:
            Tuple of (can_open: bool, reason: str)
        """
        # Check maximum open positions
        if len(self.open_positions) >= config.MAX_OPEN_POSITIONS:
            return False, f"Maximum open positions reached ({config.MAX_OPEN_POSITIONS})"

        # Check daily loss limit
        if current_date in self.daily_pnl:
            daily_loss_percent = (self.daily_pnl[current_date] / self.current_equity) * 100

            if daily_loss_percent <= -config.MAX_DAILY_LOSS_PERCENT:
                return False, f"Daily loss limit reached ({config.MAX_DAILY_LOSS_PERCENT}%)"

        # Check if new position would exceed max risk
        total_risk_after = self.open_risk + risk_amount
        max_allowed_risk = self.current_equity * (config.RISK_PER_TRADE_PERCENT * config.MAX_OPEN_POSITIONS / 100)

        if total_risk_after > max_allowed_risk:
            return False, "Total risk exposure too high"

        return True, "OK"

    def open_position(
        self,
        symbol: str,
        side: str,
        entry_price: float,
        stop_loss: float,
        take_profit: float,
        entry_time: datetime,
        size_lots: Optional[float] = None
    ) -> Optional[Position]:
        """
        Open a new position

        Args:
            symbol: Trading symbol
            side: "LONG" or "SHORT"
            entry_price: Entry price
            stop_loss: Stop-loss price
            take_profit: Take-profit price
            entry_time: Entry timestamp
            size_lots: Position size (auto-calculated if None)

        Returns:
            Position object or None if cannot open
        """
        # Calculate position size if not provided
        if size_lots is None:
            size_lots = self.calculate_position_size(entry_price, stop_loss)

        if size_lots == 0:
            return None

        # Create position
        position = Position(
            symbol=symbol,
            side=side,
            entry_price=entry_price,
            stop_loss=stop_loss,
            take_profit=take_profit,
            size_lots=size_lots,
            entry_time=entry_time,
            position_id=f"{symbol}_{entry_time.strftime('%Y%m%d_%H%M%S')}"
        )

        # Check if can open
        can_open, reason = self.can_open_position(
            position.current_risk_amount,
            entry_time.date()
        )

        if not can_open:
            print(f"Cannot open position: {reason}")
            return None

        # Add to open positions
        self.open_positions.append(position)
        return position

    def close_position(
        self,
        position: Position,
        exit_price: float,
        exit_time: datetime,
        exit_reason: str
    ) -> Trade:
        """
        Close an open position

        Args:
            position: Position to close
            exit_price: Exit price
            exit_time: Exit timestamp
            exit_reason: Reason for exit

        Returns:
            Trade object
        """
        # Calculate P&L
        if position.side == "LONG":
            pnl_pips = (exit_price - position.entry_price) * 10000
        else:  # SHORT
            pnl_pips = (position.entry_price - exit_price) * 10000

        # Calculate P&L in account currency
        pip_value = 10.0 * position.size_lots
        pnl_amount = pnl_pips * pip_value

        # Calculate commission
        commission = config.COMMISSION_PER_LOT * position.size_lots

        # Create trade record
        trade = Trade(
            symbol=position.symbol,
            side=position.side,
            entry_price=position.entry_price,
            exit_price=exit_price,
            stop_loss=position.stop_loss,
            take_profit=position.take_profit,
            size_lots=position.size_lots,
            entry_time=position.entry_time,
            exit_time=exit_time,
            pnl_pips=pnl_pips,
            pnl_amount=pnl_amount,
            exit_reason=exit_reason,
            commission=commission
        )

        # Update equity
        self.current_equity += trade.net_pnl

        # Update daily P&L
        trade_date = exit_time.date()
        if trade_date not in self.daily_pnl:
            self.daily_pnl[trade_date] = 0.0
        self.daily_pnl[trade_date] += trade.net_pnl

        # Remove from open positions
        self.open_positions.remove(position)

        # Add to closed trades
        self.closed_trades.append(trade)

        return trade

    def update_trailing_stop(self, position: Position, current_price: float) -> bool:
        """
        Update trailing stop-loss if applicable

        Args:
            position: Position to update
            current_price: Current market price

        Returns:
            True if stop was updated
        """
        if not config.USE_TRAILING_STOP:
            return False

        # Check if position is in profit enough to activate trailing stop
        pnl_pips = position.calculate_pnl(current_price)
        activation_pips = position.risk_pips * config.TRAILING_STOP_ACTIVATION_RR

        if pnl_pips < activation_pips:
            return False

        # Calculate new stop-loss
        trail_distance = config.TRAILING_STOP_DISTANCE_PIPS / 10000

        if position.side == "LONG":
            new_stop = current_price - trail_distance
            if new_stop > position.stop_loss:
                position.stop_loss = new_stop
                return True
        else:  # SHORT
            new_stop = current_price + trail_distance
            if new_stop < position.stop_loss:
                position.stop_loss = new_stop
                return True

        return False

    def get_statistics(self) -> Dict:
        """
        Get comprehensive trading statistics

        Returns:
            Dictionary with performance metrics
        """
        if not self.closed_trades:
            return {
                "total_trades": 0,
                "win_rate": 0.0,
                "total_pnl": 0.0,
                "profit_factor": 0.0
            }

        winners = [t for t in self.closed_trades if t.was_winner]
        losers = [t for t in self.closed_trades if not t.was_winner]

        return {
            "total_trades": len(self.closed_trades),
            "winners": len(winners),
            "losers": len(losers),
            "win_rate": self.win_rate,
            "total_pnl": self.total_pnl,
            "total_pnl_percent": (self.total_pnl / self.initial_capital) * 100,
            "profit_factor": self.profit_factor,
            "average_win": self.average_win,
            "average_loss": self.average_loss,
            "largest_win": max((t.net_pnl for t in winners), default=0),
            "largest_loss": min((t.net_pnl for t in losers), default=0),
            "average_trade": np.mean([t.net_pnl for t in self.closed_trades]),
            "current_equity": self.current_equity,
            "return_percent": ((self.current_equity - self.initial_capital) / self.initial_capital) * 100
        }

    def reset(self):
        """Reset risk manager to initial state"""
        self.current_equity = self.initial_capital
        self.open_positions = []
        self.closed_trades = []
        self.daily_pnl = {}
