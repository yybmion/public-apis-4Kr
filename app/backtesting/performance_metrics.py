"""
Performance Metrics Calculator

백테스팅 성과 지표 계산

지표:
- 총 수익률 (Total Return)
- 연환산 수익률 (CAGR)
- 샤프 비율 (Sharpe Ratio)
- 최대 낙폭 (Maximum Drawdown, MDD)
- 승률 (Win Rate)
- 손익비 (Profit Factor)
- 변동성 (Volatility)

Author: AI Assistant
Created: 2025-11-22
"""

import numpy as np
import pandas as pd
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta


class PerformanceMetrics:
    """
    백테스팅 성과 지표 계산기

    Features:
    - 수익률 계산 (총/연환산)
    - 리스크 지표 (MDD, 변동성, 샤프)
    - 거래 통계 (승률, 손익비)
    - 벤치마크 대비 성과
    """

    def __init__(self, risk_free_rate: float = 0.03):
        """
        Initialize Performance Metrics Calculator

        Args:
            risk_free_rate: 무위험 수익률 (연환산, 기본값 3%)
        """
        self.risk_free_rate = risk_free_rate

    def calculate_returns(
        self,
        equity_curve: pd.Series
    ) -> Dict[str, float]:
        """
        수익률 계산

        Args:
            equity_curve: 자산 곡선 (시계열)

        Returns:
            수익률 지표
        """
        if len(equity_curve) < 2:
            return {
                'total_return': 0.0,
                'cagr': 0.0
            }

        # Total Return
        initial_value = equity_curve.iloc[0]
        final_value = equity_curve.iloc[-1]
        total_return = (final_value - initial_value) / initial_value

        # CAGR (Compound Annual Growth Rate)
        days = (equity_curve.index[-1] - equity_curve.index[0]).days
        years = days / 365.25

        if years > 0:
            cagr = (final_value / initial_value) ** (1 / years) - 1
        else:
            cagr = 0.0

        return {
            'total_return': total_return,
            'cagr': cagr
        }

    def calculate_max_drawdown(
        self,
        equity_curve: pd.Series
    ) -> Dict[str, Any]:
        """
        최대 낙폭 (MDD) 계산

        Args:
            equity_curve: 자산 곡선

        Returns:
            MDD 정보
        """
        if len(equity_curve) < 2:
            return {
                'max_drawdown': 0.0,
                'max_drawdown_pct': 0.0,
                'max_drawdown_duration': 0
            }

        # Running maximum
        running_max = equity_curve.expanding().max()

        # Drawdown
        drawdown = equity_curve - running_max
        drawdown_pct = drawdown / running_max

        # Maximum Drawdown
        max_dd = drawdown.min()
        max_dd_pct = drawdown_pct.min()

        # MDD Duration (days in drawdown)
        max_dd_idx = drawdown.idxmin()

        # Find when peak occurred before MDD
        peak_idx = running_max.loc[:max_dd_idx].idxmax()

        # Find recovery point
        recovery_idx = None
        peak_value = equity_curve.loc[peak_idx]

        for idx in equity_curve.loc[max_dd_idx:].index:
            if equity_curve.loc[idx] >= peak_value:
                recovery_idx = idx
                break

        # Calculate duration
        if recovery_idx is not None:
            duration = (recovery_idx - peak_idx).days
        else:
            duration = (equity_curve.index[-1] - peak_idx).days

        return {
            'max_drawdown': max_dd,
            'max_drawdown_pct': max_dd_pct,
            'max_drawdown_duration': duration,
            'peak_date': peak_idx,
            'trough_date': max_dd_idx,
            'recovery_date': recovery_idx
        }

    def calculate_sharpe_ratio(
        self,
        returns: pd.Series,
        periods_per_year: int = 252
    ) -> float:
        """
        샤프 비율 계산

        Args:
            returns: 수익률 시계열 (일간)
            periods_per_year: 연간 거래일 수 (기본값 252)

        Returns:
            샤프 비율
        """
        if len(returns) < 2:
            return 0.0

        # Average return
        mean_return = returns.mean()

        # Volatility
        std_return = returns.std()

        if std_return == 0:
            return 0.0

        # Daily risk-free rate
        daily_rf = (1 + self.risk_free_rate) ** (1 / periods_per_year) - 1

        # Sharpe Ratio (annualized)
        sharpe = (mean_return - daily_rf) / std_return * np.sqrt(periods_per_year)

        return sharpe

    def calculate_sortino_ratio(
        self,
        returns: pd.Series,
        periods_per_year: int = 252
    ) -> float:
        """
        소르티노 비율 계산 (하방 위험만 고려)

        Args:
            returns: 수익률 시계열
            periods_per_year: 연간 거래일 수

        Returns:
            소르티노 비율
        """
        if len(returns) < 2:
            return 0.0

        # Average return
        mean_return = returns.mean()

        # Downside deviation (only negative returns)
        downside_returns = returns[returns < 0]

        if len(downside_returns) == 0:
            return np.inf

        downside_std = downside_returns.std()

        if downside_std == 0:
            return 0.0

        # Daily risk-free rate
        daily_rf = (1 + self.risk_free_rate) ** (1 / periods_per_year) - 1

        # Sortino Ratio (annualized)
        sortino = (mean_return - daily_rf) / downside_std * np.sqrt(periods_per_year)

        return sortino

    def calculate_volatility(
        self,
        returns: pd.Series,
        periods_per_year: int = 252
    ) -> float:
        """
        변동성 계산 (연환산)

        Args:
            returns: 수익률 시계열
            periods_per_year: 연간 거래일 수

        Returns:
            연환산 변동성
        """
        if len(returns) < 2:
            return 0.0

        # Annualized volatility
        volatility = returns.std() * np.sqrt(periods_per_year)

        return volatility

    def calculate_win_rate(
        self,
        trades: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        승률 및 거래 통계 계산

        Args:
            trades: 거래 리스트
                [{'return': 0.05, 'profit': 500}, ...]

        Returns:
            거래 통계
        """
        if not trades:
            return {
                'total_trades': 0,
                'winning_trades': 0,
                'losing_trades': 0,
                'win_rate': 0.0,
                'avg_win': 0.0,
                'avg_loss': 0.0,
                'profit_factor': 0.0
            }

        total_trades = len(trades)

        # Separate winning and losing trades
        winning_trades = [t for t in trades if t.get('profit', t.get('return', 0)) > 0]
        losing_trades = [t for t in trades if t.get('profit', t.get('return', 0)) < 0]

        # Win rate
        win_rate = len(winning_trades) / total_trades if total_trades > 0 else 0.0

        # Average win/loss
        avg_win = np.mean([t.get('profit', t.get('return', 0)) for t in winning_trades]) if winning_trades else 0.0
        avg_loss = np.mean([abs(t.get('profit', t.get('return', 0))) for t in losing_trades]) if losing_trades else 0.0

        # Profit Factor
        total_profit = sum([t.get('profit', t.get('return', 0)) for t in winning_trades])
        total_loss = abs(sum([t.get('profit', t.get('return', 0)) for t in losing_trades]))

        profit_factor = total_profit / total_loss if total_loss > 0 else 0.0

        return {
            'total_trades': total_trades,
            'winning_trades': len(winning_trades),
            'losing_trades': len(losing_trades),
            'win_rate': win_rate,
            'avg_win': avg_win,
            'avg_loss': avg_loss,
            'profit_factor': profit_factor,
            'total_profit': total_profit,
            'total_loss': total_loss
        }

    def calculate_all_metrics(
        self,
        equity_curve: pd.Series,
        trades: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        전체 성과 지표 계산

        Args:
            equity_curve: 자산 곡선
            trades: 거래 리스트 (optional)

        Returns:
            전체 성과 지표
        """
        # Returns
        returns_metrics = self.calculate_returns(equity_curve)

        # Daily returns
        daily_returns = equity_curve.pct_change().dropna()

        # Max Drawdown
        mdd_metrics = self.calculate_max_drawdown(equity_curve)

        # Sharpe Ratio
        sharpe = self.calculate_sharpe_ratio(daily_returns)

        # Sortino Ratio
        sortino = self.calculate_sortino_ratio(daily_returns)

        # Volatility
        volatility = self.calculate_volatility(daily_returns)

        # Trade statistics
        trade_stats = {}
        if trades:
            trade_stats = self.calculate_win_rate(trades)

        # Combine all metrics
        all_metrics = {
            # Returns
            'total_return': returns_metrics['total_return'],
            'total_return_pct': returns_metrics['total_return'] * 100,
            'cagr': returns_metrics['cagr'],
            'cagr_pct': returns_metrics['cagr'] * 100,

            # Risk
            'max_drawdown': mdd_metrics['max_drawdown'],
            'max_drawdown_pct': mdd_metrics['max_drawdown_pct'] * 100,
            'max_drawdown_duration': mdd_metrics['max_drawdown_duration'],
            'volatility': volatility,
            'volatility_pct': volatility * 100,

            # Risk-adjusted
            'sharpe_ratio': sharpe,
            'sortino_ratio': sortino,

            # Dates
            'start_date': equity_curve.index[0],
            'end_date': equity_curve.index[-1],
            'total_days': (equity_curve.index[-1] - equity_curve.index[0]).days,

            # Values
            'initial_value': equity_curve.iloc[0],
            'final_value': equity_curve.iloc[-1],
        }

        # Add trade statistics if available
        if trades:
            all_metrics.update(trade_stats)

        return all_metrics

    def compare_to_benchmark(
        self,
        strategy_equity: pd.Series,
        benchmark_equity: pd.Series
    ) -> Dict[str, Any]:
        """
        벤치마크 대비 성과 비교

        Args:
            strategy_equity: 전략 자산 곡선
            benchmark_equity: 벤치마크 자산 곡선

        Returns:
            비교 지표
        """
        # Calculate metrics for both
        strategy_metrics = self.calculate_all_metrics(strategy_equity)
        benchmark_metrics = self.calculate_all_metrics(benchmark_equity)

        # Alpha (excess return)
        alpha = strategy_metrics['cagr'] - benchmark_metrics['cagr']

        # Beta (correlation-based)
        strategy_returns = strategy_equity.pct_change().dropna()
        benchmark_returns = benchmark_equity.pct_change().dropna()

        # Align indices
        aligned = pd.concat([strategy_returns, benchmark_returns], axis=1, join='inner')
        aligned.columns = ['strategy', 'benchmark']

        if len(aligned) > 1:
            covariance = aligned.cov().iloc[0, 1]
            benchmark_variance = aligned['benchmark'].var()
            beta = covariance / benchmark_variance if benchmark_variance > 0 else 0.0
        else:
            beta = 0.0

        return {
            'strategy': strategy_metrics,
            'benchmark': benchmark_metrics,
            'alpha': alpha,
            'alpha_pct': alpha * 100,
            'beta': beta,
            'excess_return': strategy_metrics['total_return'] - benchmark_metrics['total_return'],
            'excess_return_pct': (strategy_metrics['total_return'] - benchmark_metrics['total_return']) * 100
        }

    def generate_report(
        self,
        metrics: Dict[str, Any],
        strategy_name: str = "Strategy"
    ) -> str:
        """
        성과 리포트 생성 (텍스트)

        Args:
            metrics: 성과 지표
            strategy_name: 전략 이름

        Returns:
            리포트 텍스트
        """
        report = f"""
{'=' * 80}
  {strategy_name} - 백테스팅 성과 리포트
{'=' * 80}

📅 기간: {metrics['start_date'].strftime('%Y-%m-%d')} ~ {metrics['end_date'].strftime('%Y-%m-%d')} ({metrics['total_days']}일)

💰 수익률:
   초기 자산: ${metrics['initial_value']:,.2f}
   최종 자산: ${metrics['final_value']:,.2f}
   총 수익률: {metrics['total_return_pct']:+.2f}%
   연환산 수익률 (CAGR): {metrics['cagr_pct']:+.2f}%

📉 리스크:
   최대 낙폭 (MDD): {metrics['max_drawdown_pct']:+.2f}%
   MDD 기간: {metrics['max_drawdown_duration']}일
   변동성 (연환산): {metrics['volatility_pct']:.2f}%

📊 위험조정 수익률:
   샤프 비율: {metrics['sharpe_ratio']:.3f}
   소르티노 비율: {metrics['sortino_ratio']:.3f}
"""

        # Add trade statistics if available
        if 'total_trades' in metrics and metrics['total_trades'] > 0:
            report += f"""
💼 거래 통계:
   총 거래 수: {metrics['total_trades']}
   승리: {metrics['winning_trades']} | 패배: {metrics['losing_trades']}
   승률: {metrics['win_rate'] * 100:.1f}%
   평균 승리: ${metrics['avg_win']:,.2f}
   평균 손실: ${metrics['avg_loss']:,.2f}
   손익비 (Profit Factor): {metrics['profit_factor']:.2f}
"""

        report += f"\n{'=' * 80}\n"

        return report
