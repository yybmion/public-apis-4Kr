"""
Backtest Engine

백테스팅 실행 엔진

과거 데이터로 투자 전략을 검증하고 성과를 측정

Author: AI Assistant
Created: 2025-11-22
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime, timedelta
from enum import Enum

from app.backtesting.performance_metrics import PerformanceMetrics


class SignalType(str, Enum):
    """Signal types"""
    STRONG_BUY = "STRONG_BUY"
    BUY = "BUY"
    WEAK_BUY = "WEAK_BUY"
    HOLD = "HOLD"
    WEAK_SELL = "WEAK_SELL"
    SELL = "SELL"
    STRONG_SELL = "STRONG_SELL"


class BacktestEngine:
    """
    백테스팅 엔진

    Features:
    - 과거 데이터로 전략 실행
    - 포지션 관리 (매수/매도)
    - 거래 비용 반영
    - 성과 지표 계산
    - 리스크 관리
    """

    def __init__(
        self,
        initial_capital: float = 10000000,  # 1천만원
        commission: float = 0.0015,  # 0.15% (한국 주식 거래 수수료)
        slippage: float = 0.001,  # 0.1% (슬리피지)
        risk_free_rate: float = 0.03  # 3% (무위험 수익률)
    ):
        """
        Initialize Backtest Engine

        Args:
            initial_capital: 초기 자본
            commission: 거래 수수료 (비율)
            slippage: 슬리피지 (비율)
            risk_free_rate: 무위험 수익률
        """
        self.initial_capital = initial_capital
        self.commission = commission
        self.slippage = slippage
        self.risk_free_rate = risk_free_rate

        # Performance calculator
        self.performance = PerformanceMetrics(risk_free_rate=risk_free_rate)

        # Backtest results
        self.equity_curve = None
        self.trades = []
        self.positions = []

    def _calculate_signal_weight(self, signal: str) -> float:
        """
        신호별 포지션 비중 계산

        Args:
            signal: 투자 신호

        Returns:
            포지션 비중 (0.0 ~ 1.0)
        """
        signal_weights = {
            SignalType.STRONG_BUY: 1.0,      # 100%
            SignalType.BUY: 0.7,              # 70%
            SignalType.WEAK_BUY: 0.4,         # 40%
            SignalType.HOLD: 0.0,             # 0% (기존 유지)
            SignalType.WEAK_SELL: -0.4,       # -40% (40% 매도)
            SignalType.SELL: -0.7,            # -70% (70% 매도)
            SignalType.STRONG_SELL: -1.0      # -100% (전량 매도)
        }

        return signal_weights.get(signal, 0.0)

    def run(
        self,
        data: pd.DataFrame,
        strategy_func: Callable[[pd.Series], str]
    ) -> Dict[str, Any]:
        """
        백테스트 실행

        Args:
            data: 가격 데이터
                  index: 날짜
                  columns: ['close', 'sp500', 'nasdaq', 'fear_greed', ...]
            strategy_func: 전략 함수
                           입력: 데이터 row (pd.Series)
                           출력: 신호 (str)

        Returns:
            백테스트 결과
        """
        # Initialize
        cash = self.initial_capital
        shares = 0.0
        equity_values = []
        dates = []

        self.trades = []
        self.positions = []

        # Run backtest
        for date, row in data.iterrows():
            # Get signal from strategy
            signal = strategy_func(row)

            # Current price
            price = row['close']

            # Calculate target position weight
            target_weight = self._calculate_signal_weight(signal)

            # Current position value
            position_value = shares * price
            total_value = cash + position_value

            # Target position value
            target_position_value = total_value * abs(target_weight)

            # Calculate trade
            if target_weight > 0:  # Buy signal
                # Buy more shares
                target_shares = target_position_value / price

                if target_shares > shares:
                    # Buy
                    shares_to_buy = target_shares - shares
                    cost = shares_to_buy * price * (1 + self.commission + self.slippage)

                    if cost <= cash:
                        # Execute buy
                        cash -= cost
                        shares += shares_to_buy

                        # Record trade
                        self.trades.append({
                            'date': date,
                            'type': 'BUY',
                            'signal': signal,
                            'price': price,
                            'shares': shares_to_buy,
                            'cost': cost
                        })

            elif target_weight < 0:  # Sell signal
                # Sell shares
                target_shares = shares * (1 + target_weight)  # target_weight is negative

                if target_shares < shares:
                    # Sell
                    shares_to_sell = shares - target_shares
                    proceeds = shares_to_sell * price * (1 - self.commission - self.slippage)

                    # Execute sell
                    cash += proceeds
                    shares -= shares_to_sell

                    # Record trade
                    self.trades.append({
                        'date': date,
                        'type': 'SELL',
                        'signal': signal,
                        'price': price,
                        'shares': shares_to_sell,
                        'proceeds': proceeds
                    })

            # HOLD: do nothing

            # Calculate equity
            position_value = shares * price
            total_equity = cash + position_value

            equity_values.append(total_equity)
            dates.append(date)

            # Record position
            self.positions.append({
                'date': date,
                'cash': cash,
                'shares': shares,
                'price': price,
                'position_value': position_value,
                'total_equity': total_equity,
                'signal': signal
            })

        # Create equity curve
        self.equity_curve = pd.Series(equity_values, index=dates)

        # Calculate performance metrics
        metrics = self.performance.calculate_all_metrics(
            self.equity_curve,
            self._calculate_trade_profits()
        )

        return {
            'metrics': metrics,
            'equity_curve': self.equity_curve,
            'trades': self.trades,
            'positions': self.positions
        }

    def run_buy_and_hold(
        self,
        data: pd.DataFrame
    ) -> Dict[str, Any]:
        """
        Buy & Hold 벤치마크 실행

        Args:
            data: 가격 데이터

        Returns:
            벤치마크 결과
        """
        # Buy at first day
        first_price = data.iloc[0]['close']
        shares = self.initial_capital / (first_price * (1 + self.commission))

        # Calculate equity curve
        equity_values = shares * data['close'] * (1 - self.commission)
        equity_curve = pd.Series(equity_values.values, index=data.index)

        # Calculate metrics
        metrics = self.performance.calculate_all_metrics(equity_curve)

        return {
            'metrics': metrics,
            'equity_curve': equity_curve
        }

    def _calculate_trade_profits(self) -> List[Dict[str, Any]]:
        """
        Calculate profit for each trade pair (buy -> sell)

        Returns:
            List of trade profits
        """
        trade_profits = []

        # Match buy and sell trades
        open_positions = []

        for trade in self.trades:
            if trade['type'] == 'BUY':
                open_positions.append(trade)
            elif trade['type'] == 'SELL' and open_positions:
                # Match with earliest buy (FIFO)
                buy_trade = open_positions.pop(0)

                # Calculate profit
                buy_price = buy_trade['price']
                sell_price = trade['price']
                shares = min(buy_trade['shares'], trade['shares'])

                profit = (sell_price - buy_price) * shares
                profit -= buy_trade['cost'] * (shares / buy_trade['shares'])  # Buy costs
                profit -= trade['proceeds'] * (shares / trade['shares']) * (self.commission + self.slippage)  # Sell costs

                trade_profits.append({
                    'buy_date': buy_trade['date'],
                    'sell_date': trade['date'],
                    'buy_price': buy_price,
                    'sell_price': sell_price,
                    'shares': shares,
                    'profit': profit,
                    'return': (sell_price - buy_price) / buy_price
                })

        return trade_profits

    def compare_to_benchmark(
        self,
        strategy_result: Dict[str, Any],
        benchmark_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        벤치마크 대비 성과 비교

        Args:
            strategy_result: 전략 결과
            benchmark_result: 벤치마크 결과

        Returns:
            비교 결과
        """
        comparison = self.performance.compare_to_benchmark(
            strategy_result['equity_curve'],
            benchmark_result['equity_curve']
        )

        return comparison

    def generate_report(
        self,
        result: Dict[str, Any],
        strategy_name: str = "Strategy"
    ) -> str:
        """
        백테스트 리포트 생성

        Args:
            result: 백테스트 결과
            strategy_name: 전략 이름

        Returns:
            리포트 텍스트
        """
        return self.performance.generate_report(
            result['metrics'],
            strategy_name
        )

    def plot_equity_curve(
        self,
        strategy_result: Dict[str, Any],
        benchmark_result: Optional[Dict[str, Any]] = None
    ):
        """
        자산 곡선 시각화 (Plotly)

        Args:
            strategy_result: 전략 결과
            benchmark_result: 벤치마크 결과 (optional)
        """
        try:
            import plotly.graph_objects as go

            fig = go.Figure()

            # Strategy
            fig.add_trace(go.Scatter(
                x=strategy_result['equity_curve'].index,
                y=strategy_result['equity_curve'].values,
                mode='lines',
                name='Strategy',
                line=dict(color='#1f77b4', width=2)
            ))

            # Benchmark
            if benchmark_result:
                fig.add_trace(go.Scatter(
                    x=benchmark_result['equity_curve'].index,
                    y=benchmark_result['equity_curve'].values,
                    mode='lines',
                    name='Buy & Hold',
                    line=dict(color='#ff7f0e', width=2, dash='dash')
                ))

            # Add trades (markers)
            buy_trades = [t for t in strategy_result['trades'] if t['type'] == 'BUY']
            sell_trades = [t for t in strategy_result['trades'] if t['type'] == 'SELL']

            if buy_trades:
                buy_dates = [t['date'] for t in buy_trades]
                buy_values = [strategy_result['equity_curve'].loc[t['date']] for t in buy_trades]

                fig.add_trace(go.Scatter(
                    x=buy_dates,
                    y=buy_values,
                    mode='markers',
                    name='Buy',
                    marker=dict(color='green', size=10, symbol='triangle-up')
                ))

            if sell_trades:
                sell_dates = [t['date'] for t in sell_trades]
                sell_values = [strategy_result['equity_curve'].loc[t['date']] for t in sell_trades]

                fig.add_trace(go.Scatter(
                    x=sell_dates,
                    y=sell_values,
                    mode='markers',
                    name='Sell',
                    marker=dict(color='red', size=10, symbol='triangle-down')
                ))

            fig.update_layout(
                title="백테스팅 자산 곡선",
                xaxis_title="날짜",
                yaxis_title="자산 (원)",
                height=600,
                hovermode='x unified'
            )

            return fig

        except ImportError:
            print("Plotly not installed. Install with: pip install plotly")
            return None
