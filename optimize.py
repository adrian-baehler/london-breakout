#!/usr/bin/env python3
"""
Parameter Optimization for London Breakout Strategy

This script helps find optimal strategy parameters through grid search.
"""
import pandas as pd
import numpy as np
from typing import Dict, List
import itertools
from concurrent.futures import ProcessPoolExecutor
import warnings
warnings.filterwarnings('ignore')

from data_loader import prepare_backtest_data
from backtest import BacktestEngine
import config


class StrategyOptimizer:
    """
    Optimize strategy parameters using grid search
    """

    def __init__(self, symbol: str, df: pd.DataFrame):
        self.symbol = symbol
        self.df = df
        self.results: List[Dict] = []

    def optimize(
        self,
        param_grid: Dict[str, List],
        metric: str = "sharpe_ratio",
        max_workers: int = 4
    ) -> pd.DataFrame:
        """
        Run parameter optimization

        Args:
            param_grid: Dictionary of parameters to test
            metric: Metric to optimize ("sharpe_ratio", "return_percent", "profit_factor")
            max_workers: Number of parallel workers

        Returns:
            DataFrame with results sorted by metric
        """
        # Generate parameter combinations
        param_names = list(param_grid.keys())
        param_values = list(param_grid.values())
        param_combinations = list(itertools.product(*param_values))

        print(f"Testing {len(param_combinations)} parameter combinations...")
        print(f"Parameters: {param_names}")
        print()

        # Run backtests
        for i, params in enumerate(param_combinations, 1):
            param_dict = dict(zip(param_names, params))

            print(f"[{i}/{len(param_combinations)}] Testing: {param_dict}")

            # Temporarily update config
            original_config = self._save_config(param_names)
            self._update_config(param_dict)

            try:
                # Run backtest
                engine = BacktestEngine(self.symbol, config.INITIAL_CAPITAL)
                results = engine.run(self.df)

                # Store results
                result_row = {
                    **param_dict,
                    'total_trades': results['total_trades'],
                    'win_rate': results['win_rate'],
                    'profit_factor': results['profit_factor'],
                    'return_percent': results['return_percent'],
                    'max_drawdown': results['max_drawdown'],
                    'sharpe_ratio': results['sharpe_ratio'],
                    'sortino_ratio': results['sortino_ratio']
                }
                self.results.append(result_row)

            except Exception as e:
                print(f"Error: {e}")
                continue

            finally:
                # Restore config
                self._restore_config(original_config)

        # Convert to DataFrame and sort
        results_df = pd.DataFrame(self.results)
        results_df = results_df.sort_values(metric, ascending=False)

        print("\n" + "=" * 70)
        print("OPTIMIZATION COMPLETED")
        print("=" * 70)
        print(f"\nTop 5 parameter sets by {metric}:")
        print(results_df.head())

        return results_df

    def _save_config(self, param_names: List[str]) -> Dict:
        """Save current config values"""
        return {name: getattr(config, name) for name in param_names}

    def _update_config(self, params: Dict):
        """Update config with new parameters"""
        for name, value in params.items():
            setattr(config, name, value)

    def _restore_config(self, original_config: Dict):
        """Restore original config values"""
        for name, value in original_config.items():
            setattr(config, name, value)


def main():
    """Run optimization"""
    print("=" * 70)
    print("LONDON BREAKOUT STRATEGY OPTIMIZER")
    print("=" * 70)
    print()

    # Load data
    symbol = "EURUSD"
    df = prepare_backtest_data(
        symbol=symbol,
        start_date="2023-01-01",
        end_date="2024-01-01",
        use_sample=True
    )

    # Define parameter grid
    param_grid = {
        'RISK_REWARD_RATIO': [1.5, 2.0, 2.5, 3.0],
        'BREAKOUT_BUFFER_PIPS': [1, 2, 3, 5],
        'MIN_RANGE_PIPS': [10, 15, 20, 25],
        'TRADING_WINDOW_HOURS': [1, 2, 3, 4]
    }

    # Run optimization
    optimizer = StrategyOptimizer(symbol, df)
    results_df = optimizer.optimize(
        param_grid=param_grid,
        metric="sharpe_ratio"
    )

    # Save results
    results_df.to_csv("optimization_results.csv", index=False)
    print(f"\nResults saved to: optimization_results.csv")


if __name__ == "__main__":
    main()
