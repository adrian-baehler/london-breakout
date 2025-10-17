"""
Backtesting Engine for London Breakout Strategy
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import matplotlib.pyplot as plt
import seaborn as sns

from strategy import LondonBreakoutStrategy, SignalType, TradeSignal
from risk_management import RiskManager, Position, Trade
import config


class BacktestEngine:
    """
    Backtesting engine for London Breakout Strategy

    Features:
    - Realistic trade execution with slippage and commission
    - Position management with stop-loss and take-profit
    - Comprehensive performance metrics
    - Equity curve and drawdown tracking
    - Visual performance reports
    """

    def __init__(self, symbol: str, initial_capital: float = None):
        self.symbol = symbol
        self.initial_capital = initial_capital or config.INITIAL_CAPITAL

        self.strategy = LondonBreakoutStrategy(symbol)
        self.risk_manager = RiskManager(self.initial_capital)

        self.equity_curve: List[float] = []
        self.dates: List[datetime] = []

    def run(
        self,
        df: pd.DataFrame,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> Dict:
        """
        Run backtest on historical data

        Args:
            df: OHLC dataframe with datetime index
            start_date: Start date for backtest (YYYY-MM-DD)
            end_date: End date for backtest (YYYY-MM-DD)

        Returns:
            Dictionary with backtest results
        """
        # Filter date range
        if start_date:
            df = df[df.index >= start_date]
        if end_date:
            df = df[df.index <= end_date]

        if df.empty:
            raise ValueError("No data available for backtest period")

        print(f"Starting backtest for {self.symbol}")
        print(f"Period: {df.index[0]} to {df.index[-1]}")
        print(f"Initial capital: ${self.initial_capital:,.2f}")
        print("-" * 60)

        # Iterate through bars
        for current_time, bar in df.iterrows():
            self._process_bar(df, current_time, bar)

        # Close any remaining open positions at end
        for position in self.risk_manager.open_positions.copy():
            last_price = df.iloc[-1]['close']
            self.risk_manager.close_position(
                position, last_price, df.index[-1], "END"
            )

        # Generate results
        results = self._generate_results(df)

        print("\n" + "=" * 60)
        print("BACKTEST COMPLETED")
        print("=" * 60)
        self._print_results(results)

        return results

    def _process_bar(self, df: pd.DataFrame, current_time: datetime, bar: pd.Series):
        """Process a single bar"""
        # Update equity curve
        self.equity_curve.append(self.risk_manager.current_equity)
        self.dates.append(current_time)

        # Check open positions for exit conditions
        for position in self.risk_manager.open_positions.copy():
            exit_price = None
            exit_reason = None

            # Check stop-loss (use low/high to be realistic)
            if position.side == "LONG":
                if bar['low'] <= position.stop_loss:
                    exit_price = position.stop_loss
                    exit_reason = "SL"
                elif bar['high'] >= position.take_profit:
                    exit_price = position.take_profit
                    exit_reason = "TP"
            else:  # SHORT
                if bar['high'] >= position.stop_loss:
                    exit_price = position.stop_loss
                    exit_reason = "SL"
                elif bar['low'] <= position.take_profit:
                    exit_price = position.take_profit
                    exit_reason = "TP"

            # Check time-based exit
            if exit_price is None and self.strategy.should_exit_time_based(current_time):
                exit_price = bar['close']
                exit_reason = "TIME"

            # Update trailing stop
            if exit_price is None:
                self.risk_manager.update_trailing_stop(position, bar['close'])

            # Close position if exit triggered
            if exit_price is not None:
                self.risk_manager.close_position(
                    position, exit_price, current_time, exit_reason
                )

        # Generate new signals if no position open for this symbol
        open_symbols = [p.symbol for p in self.risk_manager.open_positions]
        if self.symbol not in open_symbols:
            signal = self.strategy.generate_signal(df, current_time)

            if signal is not None:
                self._execute_signal(signal, current_time)

    def _execute_signal(self, signal: TradeSignal, current_time: datetime):
        """Execute a trading signal"""
        # Determine position side
        side = "LONG" if signal.signal_type == SignalType.LONG else "SHORT"

        # Open position
        position = self.risk_manager.open_position(
            symbol=self.symbol,
            side=side,
            entry_price=signal.entry_price,
            stop_loss=signal.stop_loss,
            take_profit=signal.take_profit,
            entry_time=current_time
        )

        if position:
            print(f"{current_time} | {side} | Entry: {signal.entry_price:.5f} | "
                  f"SL: {signal.stop_loss:.5f} | TP: {signal.take_profit:.5f} | "
                  f"Size: {position.size_lots} lots")

    def _generate_results(self, df: pd.DataFrame) -> Dict:
        """Generate comprehensive backtest results"""
        stats = self.risk_manager.get_statistics()

        # Calculate additional metrics
        equity_series = pd.Series(self.equity_curve, index=self.dates)

        # Drawdown calculation
        running_max = equity_series.expanding().max()
        drawdown = (equity_series - running_max) / running_max * 100
        max_drawdown = drawdown.min()

        # Sharpe ratio (annualized)
        returns = equity_series.pct_change().dropna()
        if len(returns) > 0:
            sharpe_ratio = np.sqrt(252) * (returns.mean() / returns.std()) if returns.std() > 0 else 0
        else:
            sharpe_ratio = 0

        # Sortino ratio
        negative_returns = returns[returns < 0]
        if len(negative_returns) > 0 and negative_returns.std() > 0:
            sortino_ratio = np.sqrt(252) * (returns.mean() / negative_returns.std())
        else:
            sortino_ratio = 0

        # Calculate consecutive wins/losses
        consecutive_wins, consecutive_losses = self._calculate_consecutive_trades()

        # Compile results
        results = {
            **stats,
            "max_drawdown": max_drawdown,
            "max_drawdown_amount": equity_series.min() - running_max[equity_series.idxmin()],
            "sharpe_ratio": sharpe_ratio,
            "sortino_ratio": sortino_ratio,
            "max_consecutive_wins": consecutive_wins,
            "max_consecutive_losses": consecutive_losses,
            "total_days": (df.index[-1] - df.index[0]).days,
            "equity_curve": equity_series,
            "trades": self.risk_manager.closed_trades
        }

        return results

    def _calculate_consecutive_trades(self) -> tuple:
        """Calculate max consecutive wins and losses"""
        if not self.risk_manager.closed_trades:
            return 0, 0

        max_wins = 0
        max_losses = 0
        current_wins = 0
        current_losses = 0

        for trade in self.risk_manager.closed_trades:
            if trade.was_winner:
                current_wins += 1
                current_losses = 0
                max_wins = max(max_wins, current_wins)
            else:
                current_losses += 1
                current_wins = 0
                max_losses = max(max_losses, current_losses)

        return max_wins, max_losses

    def _print_results(self, results: Dict):
        """Print formatted backtest results"""
        print(f"\nTotal Trades: {results['total_trades']}")
        print(f"Winners: {results['winners']} | Losers: {results['losers']}")
        print(f"Win Rate: {results['win_rate']:.2f}%")
        print(f"\nProfit Factor: {results['profit_factor']:.2f}")
        print(f"Average Win: ${results['average_win']:.2f}")
        print(f"Average Loss: ${results['average_loss']:.2f}")
        print(f"Largest Win: ${results['largest_win']:.2f}")
        print(f"Largest Loss: ${results['largest_loss']:.2f}")
        print(f"\nTotal P&L: ${results['total_pnl']:.2f} ({results['total_pnl_percent']:.2f}%)")
        print(f"Final Equity: ${results['current_equity']:.2f}")
        print(f"Return: {results['return_percent']:.2f}%")
        print(f"\nMax Drawdown: {results['max_drawdown']:.2f}%")
        print(f"Sharpe Ratio: {results['sharpe_ratio']:.2f}")
        print(f"Sortino Ratio: {results['sortino_ratio']:.2f}")
        print(f"\nMax Consecutive Wins: {results['max_consecutive_wins']}")
        print(f"Max Consecutive Losses: {results['max_consecutive_losses']}")

    def plot_results(self, results: Dict, save_path: Optional[str] = None):
        """
        Generate visual performance report

        Args:
            results: Backtest results dictionary
            save_path: Path to save plot (if None, displays plot)
        """
        fig, axes = plt.subplots(3, 2, figsize=(15, 12))
        fig.suptitle(f'London Breakout Strategy - {self.symbol}', fontsize=16)

        # 1. Equity Curve
        equity_curve = results['equity_curve']
        axes[0, 0].plot(equity_curve.index, equity_curve.values, linewidth=2)
        axes[0, 0].axhline(y=self.initial_capital, color='r', linestyle='--', alpha=0.5)
        axes[0, 0].set_title('Equity Curve')
        axes[0, 0].set_ylabel('Equity ($)')
        axes[0, 0].grid(True, alpha=0.3)

        # 2. Drawdown
        running_max = equity_curve.expanding().max()
        drawdown = (equity_curve - running_max) / running_max * 100
        axes[0, 1].fill_between(drawdown.index, drawdown.values, 0, alpha=0.3, color='red')
        axes[0, 1].set_title('Drawdown')
        axes[0, 1].set_ylabel('Drawdown (%)')
        axes[0, 1].grid(True, alpha=0.3)

        # 3. Trade Distribution
        trades = results['trades']
        pnls = [t.net_pnl for t in trades]
        colors = ['green' if pnl > 0 else 'red' for pnl in pnls]
        axes[1, 0].bar(range(len(pnls)), pnls, color=colors, alpha=0.6)
        axes[1, 0].axhline(y=0, color='black', linestyle='-', linewidth=0.5)
        axes[1, 0].set_title('Individual Trade P&L')
        axes[1, 0].set_xlabel('Trade Number')
        axes[1, 0].set_ylabel('P&L ($)')
        axes[1, 0].grid(True, alpha=0.3)

        # 4. P&L Distribution
        axes[1, 1].hist(pnls, bins=30, edgecolor='black', alpha=0.7)
        axes[1, 1].axvline(x=0, color='red', linestyle='--', linewidth=2)
        axes[1, 1].set_title('P&L Distribution')
        axes[1, 1].set_xlabel('P&L ($)')
        axes[1, 1].set_ylabel('Frequency')
        axes[1, 1].grid(True, alpha=0.3)

        # 5. Cumulative P&L
        cumulative_pnl = np.cumsum(pnls)
        axes[2, 0].plot(cumulative_pnl, linewidth=2)
        axes[2, 0].axhline(y=0, color='r', linestyle='--', alpha=0.5)
        axes[2, 0].set_title('Cumulative P&L')
        axes[2, 0].set_xlabel('Trade Number')
        axes[2, 0].set_ylabel('Cumulative P&L ($)')
        axes[2, 0].grid(True, alpha=0.3)

        # 6. Performance Metrics
        axes[2, 1].axis('off')
        metrics_text = f"""
        Performance Summary
        {'='*30}
        Total Trades: {results['total_trades']}
        Win Rate: {results['win_rate']:.2f}%
        Profit Factor: {results['profit_factor']:.2f}

        Total Return: {results['return_percent']:.2f}%
        Max Drawdown: {results['max_drawdown']:.2f}%

        Sharpe Ratio: {results['sharpe_ratio']:.2f}
        Sortino Ratio: {results['sortino_ratio']:.2f}

        Average Win: ${results['average_win']:.2f}
        Average Loss: ${results['average_loss']:.2f}

        Final Equity: ${results['current_equity']:.2f}
        """
        axes[2, 1].text(0.1, 0.5, metrics_text, fontsize=11, family='monospace',
                        verticalalignment='center')

        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"\nPlot saved to: {save_path}")
        else:
            plt.show()

    def export_trades(self, filepath: str):
        """
        Export trade log to CSV

        Args:
            filepath: Path to save CSV file
        """
        if not self.risk_manager.closed_trades:
            print("No trades to export")
            return

        trades_data = []
        for trade in self.risk_manager.closed_trades:
            trades_data.append({
                'symbol': trade.symbol,
                'side': trade.side,
                'entry_time': trade.entry_time,
                'exit_time': trade.exit_time,
                'entry_price': trade.entry_price,
                'exit_price': trade.exit_price,
                'stop_loss': trade.stop_loss,
                'take_profit': trade.take_profit,
                'size_lots': trade.size_lots,
                'pnl_pips': trade.pnl_pips,
                'pnl_amount': trade.pnl_amount,
                'commission': trade.commission,
                'net_pnl': trade.net_pnl,
                'exit_reason': trade.exit_reason,
                'duration_minutes': trade.duration_minutes
            })

        df = pd.DataFrame(trades_data)
        df.to_csv(filepath, index=False)
        print(f"Trades exported to: {filepath}")


def quick_backtest(symbol: str, data_file: str, plot: bool = True) -> Dict:
    """
    Quick backtest helper function

    Args:
        symbol: Trading symbol
        data_file: Path to OHLC CSV file
        plot: Whether to display plots

    Returns:
        Backtest results dictionary
    """
    # Load data
    df = pd.read_csv(data_file, parse_dates=['timestamp'], index_col='timestamp')

    # Run backtest
    engine = BacktestEngine(symbol)
    results = engine.run(df, config.BACKTEST_START_DATE, config.BACKTEST_END_DATE)

    # Plot results
    if plot:
        engine.plot_results(results)

    # Export trades
    if config.SAVE_TRADE_LOG:
        engine.export_trades(config.TRADE_LOG_FILE)

    return results
