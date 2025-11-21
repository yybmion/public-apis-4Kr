"""
Technical Analyzer - Calculate Technical Indicators
Stock Intelligence System
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta

try:
    import ta
    from ta.trend import SMAIndicator, EMAIndicator, MACD
    from ta.momentum import RSIIndicator, StochasticOscillator
    from ta.volatility import BollingerBands, AverageTrueRange
    from ta.volume import OnBalanceVolumeIndicator
except ImportError:
    ta = None

from app.utils.logger import analyzer_logger, LoggerMixin


class TechnicalAnalyzer(LoggerMixin):
    """
    Calculate technical indicators for stock analysis

    Indicators:
    - Moving Averages (SMA, EMA)
    - RSI (Relative Strength Index)
    - MACD (Moving Average Convergence Divergence)
    - Bollinger Bands
    - Stochastic Oscillator
    - ATR (Average True Range)
    - OBV (On Balance Volume)
    """

    def __init__(self):
        super().__init__()
        if ta is None:
            self.log_warning("ta library not installed. Some indicators may not work.")

    def calculate_all_indicators(
        self,
        df: pd.DataFrame,
        close_col: str = 'close',
        high_col: str = 'high',
        low_col: str = 'low',
        volume_col: str = 'volume'
    ) -> pd.DataFrame:
        """
        Calculate all technical indicators

        Args:
            df: DataFrame with OHLCV data
            close_col: Column name for close price
            high_col: Column name for high price
            low_col: Column name for low price
            volume_col: Column name for volume

        Returns:
            DataFrame with all indicators added
        """
        df = df.copy()

        # Moving Averages
        df = self.calculate_moving_averages(df, close_col)

        # RSI
        df = self.calculate_rsi(df, close_col)

        # MACD
        df = self.calculate_macd(df, close_col)

        # Bollinger Bands
        df = self.calculate_bollinger_bands(df, close_col)

        # Stochastic
        df = self.calculate_stochastic(df, high_col, low_col, close_col)

        # ATR
        df = self.calculate_atr(df, high_col, low_col, close_col)

        # OBV
        if volume_col in df.columns:
            df = self.calculate_obv(df, close_col, volume_col)

        # Volatility
        df = self.calculate_volatility(df, close_col)

        self.log_info(f"Calculated all indicators for {len(df)} rows")

        return df

    def calculate_moving_averages(
        self,
        df: pd.DataFrame,
        close_col: str = 'close',
        periods: List[int] = [5, 20, 60, 120, 200]
    ) -> pd.DataFrame:
        """Calculate Simple Moving Averages"""
        df = df.copy()

        for period in periods:
            if len(df) >= period:
                df[f'ma_{period}'] = df[close_col].rolling(window=period).mean()
                df[f'ema_{period}'] = df[close_col].ewm(span=period, adjust=False).mean()

        return df

    def calculate_rsi(
        self,
        df: pd.DataFrame,
        close_col: str = 'close',
        period: int = 14
    ) -> pd.DataFrame:
        """Calculate Relative Strength Index"""
        df = df.copy()

        if ta and len(df) >= period:
            rsi_indicator = RSIIndicator(close=df[close_col], window=period)
            df['rsi'] = rsi_indicator.rsi()
        else:
            # Manual calculation
            delta = df[close_col].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
            rs = gain / loss
            df['rsi'] = 100 - (100 / (1 + rs))

        return df

    def calculate_macd(
        self,
        df: pd.DataFrame,
        close_col: str = 'close',
        fast: int = 12,
        slow: int = 26,
        signal: int = 9
    ) -> pd.DataFrame:
        """Calculate MACD"""
        df = df.copy()

        if ta and len(df) >= slow:
            macd_indicator = MACD(
                close=df[close_col],
                window_fast=fast,
                window_slow=slow,
                window_sign=signal
            )
            df['macd'] = macd_indicator.macd()
            df['macd_signal'] = macd_indicator.macd_signal()
            df['macd_diff'] = macd_indicator.macd_diff()
        else:
            # Manual calculation
            ema_fast = df[close_col].ewm(span=fast, adjust=False).mean()
            ema_slow = df[close_col].ewm(span=slow, adjust=False).mean()
            df['macd'] = ema_fast - ema_slow
            df['macd_signal'] = df['macd'].ewm(span=signal, adjust=False).mean()
            df['macd_diff'] = df['macd'] - df['macd_signal']

        return df

    def calculate_bollinger_bands(
        self,
        df: pd.DataFrame,
        close_col: str = 'close',
        period: int = 20,
        std_dev: float = 2.0
    ) -> pd.DataFrame:
        """Calculate Bollinger Bands"""
        df = df.copy()

        if ta and len(df) >= period:
            bb_indicator = BollingerBands(
                close=df[close_col],
                window=period,
                window_dev=std_dev
            )
            df['bb_upper'] = bb_indicator.bollinger_hband()
            df['bb_middle'] = bb_indicator.bollinger_mavg()
            df['bb_lower'] = bb_indicator.bollinger_lband()
            df['bb_width'] = bb_indicator.bollinger_wband()
        else:
            # Manual calculation
            df['bb_middle'] = df[close_col].rolling(window=period).mean()
            std = df[close_col].rolling(window=period).std()
            df['bb_upper'] = df['bb_middle'] + (std_dev * std)
            df['bb_lower'] = df['bb_middle'] - (std_dev * std)
            df['bb_width'] = (df['bb_upper'] - df['bb_lower']) / df['bb_middle']

        return df

    def calculate_stochastic(
        self,
        df: pd.DataFrame,
        high_col: str = 'high',
        low_col: str = 'low',
        close_col: str = 'close',
        period: int = 14,
        smooth: int = 3
    ) -> pd.DataFrame:
        """Calculate Stochastic Oscillator"""
        df = df.copy()

        if ta and len(df) >= period:
            stoch_indicator = StochasticOscillator(
                high=df[high_col],
                low=df[low_col],
                close=df[close_col],
                window=period,
                smooth_window=smooth
            )
            df['stoch_k'] = stoch_indicator.stoch()
            df['stoch_d'] = stoch_indicator.stoch_signal()
        else:
            # Manual calculation
            low_min = df[low_col].rolling(window=period).min()
            high_max = df[high_col].rolling(window=period).max()
            df['stoch_k'] = 100 * (df[close_col] - low_min) / (high_max - low_min)
            df['stoch_d'] = df['stoch_k'].rolling(window=smooth).mean()

        return df

    def calculate_atr(
        self,
        df: pd.DataFrame,
        high_col: str = 'high',
        low_col: str = 'low',
        close_col: str = 'close',
        period: int = 14
    ) -> pd.DataFrame:
        """Calculate Average True Range"""
        df = df.copy()

        if ta and len(df) >= period:
            atr_indicator = AverageTrueRange(
                high=df[high_col],
                low=df[low_col],
                close=df[close_col],
                window=period
            )
            df['atr'] = atr_indicator.average_true_range()
        else:
            # Manual calculation
            high_low = df[high_col] - df[low_col]
            high_close = np.abs(df[high_col] - df[close_col].shift())
            low_close = np.abs(df[low_col] - df[close_col].shift())

            true_range = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
            df['atr'] = true_range.rolling(window=period).mean()

        return df

    def calculate_obv(
        self,
        df: pd.DataFrame,
        close_col: str = 'close',
        volume_col: str = 'volume'
    ) -> pd.DataFrame:
        """Calculate On Balance Volume"""
        df = df.copy()

        if ta:
            obv_indicator = OnBalanceVolumeIndicator(
                close=df[close_col],
                volume=df[volume_col]
            )
            df['obv'] = obv_indicator.on_balance_volume()
        else:
            # Manual calculation
            obv = [0]
            for i in range(1, len(df)):
                if df[close_col].iloc[i] > df[close_col].iloc[i-1]:
                    obv.append(obv[-1] + df[volume_col].iloc[i])
                elif df[close_col].iloc[i] < df[close_col].iloc[i-1]:
                    obv.append(obv[-1] - df[volume_col].iloc[i])
                else:
                    obv.append(obv[-1])
            df['obv'] = obv

        return df

    def calculate_volatility(
        self,
        df: pd.DataFrame,
        close_col: str = 'close',
        periods: List[int] = [10, 20, 30]
    ) -> pd.DataFrame:
        """Calculate historical volatility"""
        df = df.copy()

        returns = df[close_col].pct_change()

        for period in periods:
            if len(df) >= period:
                df[f'volatility_{period}d'] = returns.rolling(window=period).std() * np.sqrt(252) * 100

        return df

    def detect_patterns(self, df: pd.DataFrame) -> Dict[str, bool]:
        """
        Detect chart patterns

        Returns:
            Dictionary of pattern names and detection results
        """
        patterns = {
            'golden_cross': False,
            'dead_cross': False,
            'rsi_oversold': False,
            'rsi_overbought': False,
            'macd_bullish': False,
            'macd_bearish': False,
            'bb_squeeze': False,
            'above_ma_20': False,
            'above_ma_60': False
        }

        if len(df) < 2:
            return patterns

        latest = df.iloc[-1]
        prev = df.iloc[-2]

        # Golden Cross / Dead Cross
        if 'ma_5' in df.columns and 'ma_20' in df.columns:
            if latest['ma_5'] > latest['ma_20'] and prev['ma_5'] <= prev['ma_20']:
                patterns['golden_cross'] = True
            elif latest['ma_5'] < latest['ma_20'] and prev['ma_5'] >= prev['ma_20']:
                patterns['dead_cross'] = True

            patterns['above_ma_20'] = latest['close'] > latest['ma_20']

        if 'ma_60' in df.columns:
            patterns['above_ma_60'] = latest['close'] > latest['ma_60']

        # RSI
        if 'rsi' in df.columns:
            patterns['rsi_oversold'] = latest['rsi'] < 30
            patterns['rsi_overbought'] = latest['rsi'] > 70

        # MACD
        if 'macd' in df.columns and 'macd_signal' in df.columns:
            if latest['macd'] > latest['macd_signal'] and prev['macd'] <= prev['macd_signal']:
                patterns['macd_bullish'] = True
            elif latest['macd'] < latest['macd_signal'] and prev['macd'] >= prev['macd_signal']:
                patterns['macd_bearish'] = True

        # Bollinger Bands Squeeze
        if 'bb_width' in df.columns:
            bb_width_ma = df['bb_width'].rolling(window=20).mean().iloc[-1]
            if latest['bb_width'] < bb_width_ma * 0.5:
                patterns['bb_squeeze'] = True

        return patterns

    def calculate_trend_strength(self, df: pd.DataFrame) -> Dict[str, float]:
        """
        Calculate trend strength metrics

        Returns:
            Dictionary with trend strength indicators
        """
        if len(df) < 20:
            return {'trend_score': 0, 'trend_direction': 'neutral'}

        latest = df.iloc[-1]

        score = 0

        # MA alignment
        if 'ma_5' in df.columns and 'ma_20' in df.columns and 'ma_60' in df.columns:
            if latest['ma_5'] > latest['ma_20'] > latest['ma_60']:
                score += 30  # Strong uptrend
            elif latest['ma_5'] < latest['ma_20'] < latest['ma_60']:
                score -= 30  # Strong downtrend

        # Price vs MA
        if 'ma_20' in df.columns:
            if latest['close'] > latest['ma_20']:
                score += 20
            else:
                score -= 20

        # MACD
        if 'macd_diff' in df.columns:
            if latest['macd_diff'] > 0:
                score += 15
            else:
                score -= 15

        # RSI
        if 'rsi' in df.columns:
            if latest['rsi'] > 50:
                score += 15
            else:
                score -= 15

        # Volume trend
        if 'obv' in df.columns and len(df) >= 10:
            obv_slope = (df['obv'].iloc[-1] - df['obv'].iloc[-10]) / 10
            if obv_slope > 0:
                score += 20
            else:
                score -= 20

        # Normalize to -100 to 100
        score = max(-100, min(100, score))

        if score > 30:
            direction = 'strong_uptrend'
        elif score > 10:
            direction = 'uptrend'
        elif score > -10:
            direction = 'neutral'
        elif score > -30:
            direction = 'downtrend'
        else:
            direction = 'strong_downtrend'

        return {
            'trend_score': score,
            'trend_direction': direction
        }
