"""
Backtest Engine - Strategy Backtesting with Backtrader
Stock Intelligence System
"""

import backtrader as bt
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from sqlalchemy.orm import Session

from app.models.stock import BacktestResult
from app.utils.logger import LoggerMixin


class SP500MAStrategy(bt.Strategy):
    """
    S&P 500 Moving Average Strategy

    Strategy:
    - Buy Korean stocks when S&P 500 > MA(20)
    - Sell/Hold cash when S&P 500 < MA(20)

    This leverages the 0.85 correlation between S&P 500 and KOSPI
    """

    params = (
        ('ma_period', 20),
        ('printlog', False),
    )

    def __init__(self):
        # Keep reference to the US market data (data1)
        self.us_close = self.datas[1].close

        # Calculate MA on US market
        self.us_ma = bt.indicators.SimpleMovingAverage(
            self.us_close,
            period=self.params.ma_period
        )

        # Track signals
        self.signal = self.us_close > self.us_ma

        # Track orders
        self.order = None

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            return

        if order.status in [order.Completed]:
            if order.isbuy():
                self.log(f'BUY EXECUTED, Price: {order.executed.price:.2f}')
            elif order.issell():
                self.log(f'SELL EXECUTED, Price: {order.executed.price:.2f}')

        self.order = None

    def notify_trade(self, trade):
        if not trade.isclosed:
            return

        self.log(f'TRADE PROFIT, GROSS: {trade.pnl:.2f}, NET: {trade.pnlcomm:.2f}')

    def next(self):
        # Check if we have an order pending
        if self.order:
            return

        # Check if we are in the market
        if not self.position:
            # Buy signal: S&P 500 > MA(20)
            if self.signal[0]:
                self.log(f'BUY CREATE, SP500: {self.us_close[0]:.2f}, MA: {self.us_ma[0]:.2f}')
                self.order = self.buy()
        else:
            # Sell signal: S&P 500 < MA(20)
            if not self.signal[0]:
                self.log(f'SELL CREATE, SP500: {self.us_close[0]:.2f}, MA: {self.us_ma[0]:.2f}')
                self.order = self.sell()

    def log(self, txt, dt=None):
        if self.params.printlog:
            dt = dt or self.datas[0].datetime.date(0)
            print(f'{dt.isoformat()} {txt}')


class GoldenCrossStrategy(bt.Strategy):
    """
    Golden Cross Strategy

    Buy when MA(5) crosses above MA(20) (Golden Cross)
    Sell when MA(5) crosses below MA(20) (Dead Cross)
    """

    params = (
        ('fast_period', 5),
        ('slow_period', 20),
        ('printlog', False),
    )

    def __init__(self):
        self.fast_ma = bt.indicators.SimpleMovingAverage(
            self.data.close,
            period=self.params.fast_period
        )
        self.slow_ma = bt.indicators.SimpleMovingAverage(
            self.data.close,
            period=self.params.slow_period
        )

        # Crossover signal
        self.crossover = bt.indicators.CrossOver(self.fast_ma, self.slow_ma)

        self.order = None

    def notify_order(self, order):
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log(f'BUY EXECUTED, Price: {order.executed.price:.2f}')
            elif order.issell():
                self.log(f'SELL EXECUTED, Price: {order.executed.price:.2f}')
        self.order = None

    def next(self):
        if self.order:
            return

        if not self.position:
            # Golden Cross
            if self.crossover > 0:
                self.log(f'GOLDEN CROSS - BUY')
                self.order = self.buy()
        else:
            # Dead Cross
            if self.crossover < 0:
                self.log(f'DEAD CROSS - SELL')
                self.order = self.sell()

    def log(self, txt, dt=None):
        if self.params.printlog:
            dt = dt or self.data.datetime.date(0)
            print(f'{dt.isoformat()} {txt}')


class BacktestEngine(LoggerMixin):
    """
    Backtesting engine using Backtrader
    """

    def __init__(self, db: Optional[Session] = None):
        super().__init__()
        self.db = db

    def run_backtest(
        self,
        strategy_class: type,
        stock_data: pd.DataFrame,
        us_data: Optional[pd.DataFrame] = None,
        initial_cash: float = 10_000_000,
        commission: float = 0.0025,
        **strategy_params
    ) -> Dict[str, any]:
        """
        Run backtest for a strategy

        Args:
            strategy_class: Strategy class to test
            stock_data: Korean stock OHLCV data
            us_data: US index data (for SP500MAStrategy)
            initial_cash: Initial capital in KRW
            commission: Commission rate (0.0025 = 0.25%)
            **strategy_params: Additional strategy parameters

        Returns:
            Backtest results dictionary
        """
        # Initialize Cerebro
        cerebro = bt.Cerebro()

        # Add strategy
        cerebro.addstrategy(strategy_class, **strategy_params)

        # Prepare data
        stock_data = stock_data.copy()
        if 'date' in stock_data.columns:
            stock_data.set_index('date', inplace=True)
        stock_data.index = pd.to_datetime(stock_data.index)

        # Add Korean stock data
        data_kr = bt.feeds.PandasData(
            dataname=stock_data,
            datetime=None,
            open='open',
            high='high',
            low='low',
            close='close',
            volume='volume',
            openinterest=-1
        )
        cerebro.adddata(data_kr)

        # Add US data if provided (for SP500MAStrategy)
        if us_data is not None:
            us_data = us_data.copy()
            if 'date' in us_data.columns:
                us_data.set_index('date', inplace=True)
            us_data.index = pd.to_datetime(us_data.index)

            data_us = bt.feeds.PandasData(
                dataname=us_data,
                datetime=None,
                open='open',
                high='high',
                low='low',
                close='close',
                volume='volume',
                openinterest=-1
            )
            cerebro.adddata(data_us)

        # Set broker parameters
        cerebro.broker.setcash(initial_cash)
        cerebro.broker.setcommission(commission=commission)

        # Add analyzers
        cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='sharpe', riskfreerate=0.03)
        cerebro.addanalyzer(bt.analyzers.DrawDown, _name='drawdown')
        cerebro.addanalyzer(bt.analyzers.Returns, _name='returns')
        cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name='trades')

        # Run backtest
        self.log_info(f"Starting backtest with initial capital: {initial_cash:,.0f} KRW")
        initial_value = cerebro.broker.getvalue()

        results = cerebro.run()
        strat = results[0]

        final_value = cerebro.broker.getvalue()
        total_return = ((final_value - initial_value) / initial_value) * 100

        # Extract analyzer results
        sharpe = strat.analyzers.sharpe.get_analysis()
        drawdown = strat.analyzers.drawdown.get_analysis()
        returns = strat.analyzers.returns.get_analysis()
        trades = strat.analyzers.trades.get_analysis()

        # Calculate metrics
        sharpe_ratio = sharpe.get('sharperatio', 0)
        if sharpe_ratio is None:
            sharpe_ratio = 0

        max_drawdown = drawdown.get('max', {}).get('drawdown', 0)

        # Calculate CAGR
        start_date = stock_data.index[0]
        end_date = stock_data.index[-1]
        years = (end_date - start_date).days / 365.25
        cagr = (((final_value / initial_value) ** (1 / years)) - 1) * 100 if years > 0 else 0

        # Calculate win rate
        total_trades = trades.get('total', {}).get('total', 0)
        won_trades = trades.get('won', {}).get('total', 0)
        win_rate = (won_trades / total_trades * 100) if total_trades > 0 else 0

        result = {
            'strategy_name': strategy_class.__name__,
            'start_date': start_date.strftime('%Y-%m-%d'),
            'end_date': end_date.strftime('%Y-%m-%d'),
            'initial_capital': initial_cash,
            'final_capital': final_value,
            'total_return': total_return,
            'cagr': cagr,
            'max_drawdown': max_drawdown,
            'sharpe_ratio': sharpe_ratio,
            'total_trades': total_trades,
            'win_rate': win_rate,
            'commission': commission
        }

        self.log_info(
            f"Backtest complete - Return: {total_return:.2f}%, "
            f"Sharpe: {sharpe_ratio:.2f}, MDD: {max_drawdown:.2f}%"
        )

        return result

    def run_sp500_strategy_backtest(
        self,
        stock_code: str,
        stock_data: pd.DataFrame,
        us_data: pd.DataFrame,
        initial_cash: float = 10_000_000,
        ma_period: int = 20
    ) -> Dict[str, any]:
        """
        Run S&P 500 MA strategy backtest

        Args:
            stock_code: Korean stock code
            stock_data: Korean stock OHLCV data
            us_data: S&P 500 OHLCV data
            initial_cash: Initial capital
            ma_period: Moving average period

        Returns:
            Backtest results
        """
        result = self.run_backtest(
            strategy_class=SP500MAStrategy,
            stock_data=stock_data,
            us_data=us_data,
            initial_cash=initial_cash,
            ma_period=ma_period
        )

        result['stock_code'] = stock_code
        result['strategy_description'] = f'S&P 500 MA({ma_period}) Strategy'

        # Save to database
        if self.db:
            self._save_backtest_result(result)

        return result

    def run_golden_cross_backtest(
        self,
        stock_code: str,
        stock_data: pd.DataFrame,
        initial_cash: float = 10_000_000,
        fast_period: int = 5,
        slow_period: int = 20
    ) -> Dict[str, any]:
        """
        Run Golden Cross strategy backtest

        Args:
            stock_code: Stock code
            stock_data: Stock OHLCV data
            initial_cash: Initial capital
            fast_period: Fast MA period
            slow_period: Slow MA period

        Returns:
            Backtest results
        """
        result = self.run_backtest(
            strategy_class=GoldenCrossStrategy,
            stock_data=stock_data,
            initial_cash=initial_cash,
            fast_period=fast_period,
            slow_period=slow_period
        )

        result['stock_code'] = stock_code
        result['strategy_description'] = f'Golden Cross MA({fast_period}/{slow_period}) Strategy'

        # Save to database
        if self.db:
            self._save_backtest_result(result)

        return result

    def compare_strategies(
        self,
        stock_code: str,
        stock_data: pd.DataFrame,
        us_data: pd.DataFrame,
        benchmark_data: Optional[pd.DataFrame] = None
    ) -> Dict[str, any]:
        """
        Compare multiple strategies

        Args:
            stock_code: Stock code
            stock_data: Stock data
            us_data: US market data
            benchmark_data: Benchmark (KOSPI) data

        Returns:
            Comparison results
        """
        strategies = []

        # S&P 500 MA Strategy
        sp500_result = self.run_sp500_strategy_backtest(
            stock_code,
            stock_data,
            us_data
        )
        strategies.append(sp500_result)

        # Golden Cross Strategy
        gc_result = self.run_golden_cross_backtest(
            stock_code,
            stock_data
        )
        strategies.append(gc_result)

        # Calculate benchmark performance if provided
        benchmark_return = 0
        if benchmark_data is not None:
            initial = benchmark_data['close'].iloc[0]
            final = benchmark_data['close'].iloc[-1]
            benchmark_return = ((final - initial) / initial) * 100

        # Find best strategy
        best_strategy = max(strategies, key=lambda x: x['sharpe_ratio'])

        return {
            'stock_code': stock_code,
            'strategies': strategies,
            'benchmark_return': benchmark_return,
            'best_strategy': best_strategy['strategy_name'],
            'comparison_date': datetime.now().isoformat()
        }

    def _save_backtest_result(self, result: Dict):
        """Save backtest result to database"""
        try:
            db_result = BacktestResult(
                strategy_name=result['strategy_name'],
                description=result.get('strategy_description', ''),
                start_date=datetime.strptime(result['start_date'], '%Y-%m-%d').date(),
                end_date=datetime.strptime(result['end_date'], '%Y-%m-%d').date(),
                initial_capital=int(result['initial_capital']),
                final_capital=int(result['final_capital']),
                total_return=result['total_return'],
                cagr=result['cagr'],
                mdd=result['max_drawdown'],
                sharpe_ratio=result['sharpe_ratio'],
                win_rate=result['win_rate'],
                total_trades=result['total_trades'],
                parameters={
                    'stock_code': result.get('stock_code'),
                    'commission': result.get('commission', 0.0025)
                }
            )

            self.db.add(db_result)
            self.db.commit()

            self.log_info(f"Saved backtest result to database")

        except Exception as e:
            self.db.rollback()
            self.log_error(f"Failed to save backtest result: {str(e)}")

    def format_backtest_report(self, result: Dict) -> str:
        """Format backtest result as a report"""
        report = f"""
╔══════════════════════════════════════════════════════════════╗
║                    BACKTEST REPORT                            ║
╚══════════════════════════════════════════════════════════════╝

📊 Strategy: {result['strategy_name']}
🏷️  Stock: {result.get('stock_code', 'N/A')}

📅 Period: {result['start_date']} ~ {result['end_date']}

💰 Performance:
   Initial Capital:  {result['initial_capital']:>15,.0f} KRW
   Final Capital:    {result['final_capital']:>15,.0f} KRW
   Total Return:     {result['total_return']:>15.2f} %
   CAGR:            {result['cagr']:>15.2f} %

📈 Risk Metrics:
   Max Drawdown:    {result['max_drawdown']:>15.2f} %
   Sharpe Ratio:    {result['sharpe_ratio']:>15.2f}

📊 Trading:
   Total Trades:    {result['total_trades']:>15}
   Win Rate:        {result['win_rate']:>15.2f} %

╔══════════════════════════════════════════════════════════════╗
║ Assessment                                                    ║
╚══════════════════════════════════════════════════════════════╝
"""

        # Performance assessment
        if result['cagr'] > 15:
            report += "✅ Excellent return\n"
        elif result['cagr'] > 10:
            report += "✅ Good return\n"
        elif result['cagr'] > 5:
            report += "⚠️  Average return\n"
        else:
            report += "❌ Poor return\n"

        # Risk assessment
        if abs(result['max_drawdown']) < 15:
            report += "✅ Low risk (MDD < 15%)\n"
        elif abs(result['max_drawdown']) < 25:
            report += "⚠️  Medium risk (MDD 15-25%)\n"
        else:
            report += "❌ High risk (MDD > 25%)\n"

        # Sharpe assessment
        if result['sharpe_ratio'] > 1.5:
            report += "✅ Excellent risk-adjusted return\n"
        elif result['sharpe_ratio'] > 1.0:
            report += "✅ Good risk-adjusted return\n"
        elif result['sharpe_ratio'] > 0.5:
            report += "⚠️  Fair risk-adjusted return\n"
        else:
            report += "❌ Poor risk-adjusted return\n"

        return report
