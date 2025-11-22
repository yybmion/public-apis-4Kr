"""
Investment Strategies

백테스팅용 투자 전략 예제

Strategies:
1. Moving Average Strategy (이동평균선 전략)
2. Fear & Greed Strategy (역발상 전략)
3. Combined Signal Strategy (통합 신호 전략)

Author: AI Assistant
Created: 2025-11-22
"""

import pandas as pd
from typing import Dict, Any


class MovingAverageStrategy:
    """
    이동평균선 전략

    Rules:
    - 20일선 > 60일선: BUY
    - 20일선 < 60일선: SELL
    - 골든크로스: STRONG_BUY
    - 데드크로스: STRONG_SELL
    """

    def __init__(self, short_window: int = 20, long_window: int = 60):
        """
        Initialize MA Strategy

        Args:
            short_window: 단기 이동평균 (기본값 20일)
            long_window: 장기 이동평균 (기본값 60일)
        """
        self.short_window = short_window
        self.long_window = long_window
        self.prev_short_ma = None
        self.prev_long_ma = None

    def generate_signal(self, row: pd.Series) -> str:
        """
        Generate trading signal

        Args:
            row: Data row with 'close', 'ma_20', 'ma_60'

        Returns:
            Signal: STRONG_BUY, BUY, HOLD, SELL, STRONG_SELL
        """
        close = row.get('close', 0)
        short_ma = row.get(f'ma_{self.short_window}', row.get('ma_20', close))
        long_ma = row.get(f'ma_{self.long_window}', row.get('ma_60', close))

        # Golden Cross (단기선이 장기선을 상향돌파)
        if self.prev_short_ma and self.prev_long_ma:
            if self.prev_short_ma <= self.prev_long_ma and short_ma > long_ma:
                signal = "STRONG_BUY"
            # Death Cross (단기선이 장기선을 하향돌파)
            elif self.prev_short_ma >= self.prev_long_ma and short_ma < long_ma:
                signal = "STRONG_SELL"
            # Above MA
            elif short_ma > long_ma and close > short_ma:
                signal = "BUY"
            # Below MA
            elif short_ma < long_ma and close < short_ma:
                signal = "SELL"
            else:
                signal = "HOLD"
        else:
            # First iteration
            if short_ma > long_ma:
                signal = "BUY"
            elif short_ma < long_ma:
                signal = "SELL"
            else:
                signal = "HOLD"

        # Update previous values
        self.prev_short_ma = short_ma
        self.prev_long_ma = long_ma

        return signal


class FearGreedStrategy:
    """
    Fear & Greed 역발상 전략

    Rules:
    - Fear & Greed < 25 (극단적 공포): STRONG_BUY
    - Fear & Greed < 40 (공포): BUY
    - 40 <= Fear & Greed <= 60 (중립): HOLD
    - Fear & Greed > 75 (극단적 탐욕): STRONG_SELL
    - Fear & Greed > 60 (탐욕): SELL
    """

    def generate_signal(self, row: pd.Series) -> str:
        """
        Generate trading signal based on Fear & Greed

        Args:
            row: Data row with 'fear_greed'

        Returns:
            Signal
        """
        fear_greed = row.get('fear_greed', 50)

        if fear_greed < 25:
            return "STRONG_BUY"
        elif fear_greed < 40:
            return "BUY"
        elif fear_greed > 75:
            return "STRONG_SELL"
        elif fear_greed > 60:
            return "SELL"
        else:
            return "HOLD"


class CombinedSignalStrategy:
    """
    통합 신호 전략

    Combines:
    - Moving Average
    - Fear & Greed
    - Interest Rate Spread

    Weighted average of signals
    """

    def __init__(self):
        """Initialize Combined Strategy"""
        self.ma_strategy = MovingAverageStrategy()

    def generate_signal(self, row: pd.Series) -> str:
        """
        Generate combined signal

        Args:
            row: Data row with multiple indicators

        Returns:
            Combined signal
        """
        signals = []
        weights = []

        # 1. Moving Average (40% weight)
        if 'ma_20' in row and 'ma_60' in row:
            ma_signal = self.ma_strategy.generate_signal(row)
            signals.append(ma_signal)
            weights.append(0.4)

        # 2. Fear & Greed (30% weight)
        if 'fear_greed' in row:
            fg_strategy = FearGreedStrategy()
            fg_signal = fg_strategy.generate_signal(row)
            signals.append(fg_signal)
            weights.append(0.3)

        # 3. Interest Rate Spread (30% weight)
        if 'fed_rate' in row and 'kr_rate' in row:
            fed_rate = row['fed_rate']
            kr_rate = row['kr_rate']
            spread = fed_rate - kr_rate

            # High spread → Sell (원화 약세 우려)
            if spread > 2.5:
                signals.append("SELL")
            elif spread > 2.0:
                signals.append("WEAK_SELL")
            elif spread < 1.0:
                signals.append("BUY")
            else:
                signals.append("HOLD")

            weights.append(0.3)

        # Calculate weighted signal
        if not signals:
            return "HOLD"

        # Convert signals to scores
        signal_scores = {
            'STRONG_BUY': 2,
            'BUY': 1,
            'WEAK_BUY': 0.5,
            'HOLD': 0,
            'WEAK_SELL': -0.5,
            'SELL': -1,
            'STRONG_SELL': -2
        }

        # Weighted average
        total_score = sum(
            signal_scores.get(sig, 0) * weight
            for sig, weight in zip(signals, weights)
        )

        # Normalize weights
        total_weight = sum(weights)
        if total_weight > 0:
            avg_score = total_score / total_weight
        else:
            avg_score = 0

        # Convert back to signal
        if avg_score >= 1.5:
            return "STRONG_BUY"
        elif avg_score >= 0.5:
            return "BUY"
        elif avg_score >= 0.25:
            return "WEAK_BUY"
        elif avg_score >= -0.25:
            return "HOLD"
        elif avg_score >= -0.5:
            return "WEAK_SELL"
        elif avg_score >= -1.5:
            return "SELL"
        else:
            return "STRONG_SELL"


def create_strategy(strategy_name: str):
    """
    Create strategy instance by name

    Args:
        strategy_name: Strategy name
            - 'ma': Moving Average
            - 'fear_greed': Fear & Greed
            - 'combined': Combined Signal

    Returns:
        Strategy instance
    """
    strategies = {
        'ma': MovingAverageStrategy(),
        'fear_greed': FearGreedStrategy(),
        'combined': CombinedSignalStrategy()
    }

    strategy = strategies.get(strategy_name)

    if not strategy:
        raise ValueError(f"Unknown strategy: {strategy_name}")

    return strategy
