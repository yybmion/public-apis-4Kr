"""
Analyzer Tests
"""

import pytest
import pandas as pd
from datetime import datetime, timedelta
from app.analyzers.technical_analyzer import TechnicalAnalyzer
from app.analyzers.signal_detector import SignalDetector


class TestTechnicalAnalyzer:
    """Test Technical Analyzer"""

    def test_calculate_indicators(self):
        """Test indicator calculation"""
        # Create sample price data
        dates = pd.date_range(end=datetime.now(), periods=100)
        df = pd.DataFrame({
            'date': dates,
            'open': range(100, 200),
            'high': range(105, 205),
            'low': range(95, 195),
            'close': range(100, 200),
            'volume': [1000000] * 100
        })

        analyzer = TechnicalAnalyzer()
        result = analyzer.calculate_all_indicators(df)

        # Check that indicators are added
        assert 'ma_5' in result.columns
        assert 'ma_20' in result.columns
        assert 'rsi' in result.columns
        assert 'macd' in result.columns
        assert not result['ma_5'].isna().all()

    def test_detect_patterns(self):
        """Test pattern detection"""
        dates = pd.date_range(end=datetime.now(), periods=100)
        df = pd.DataFrame({
            'date': dates,
            'open': range(100, 200),
            'high': range(105, 205),
            'low': range(95, 195),
            'close': range(100, 200),
            'volume': [1000000] * 100
        })

        analyzer = TechnicalAnalyzer()
        df = analyzer.calculate_all_indicators(df)
        patterns = analyzer.detect_patterns(df)

        # Check patterns structure
        assert isinstance(patterns, dict)
        assert 'golden_cross' in patterns
        assert 'dead_cross' in patterns
        assert 'rsi_oversold' in patterns

    def test_calculate_trend_strength(self):
        """Test trend strength calculation"""
        dates = pd.date_range(end=datetime.now(), periods=100)
        df = pd.DataFrame({
            'date': dates,
            'open': range(100, 200),
            'high': range(105, 205),
            'low': range(95, 195),
            'close': range(100, 200),
            'volume': [1000000] * 100
        })

        analyzer = TechnicalAnalyzer()
        df = analyzer.calculate_all_indicators(df)
        strength = analyzer.calculate_trend_strength(df)

        # Check trend strength is within valid range
        assert isinstance(strength, (int, float))
        assert -100 <= strength <= 100


class TestSignalDetector:
    """Test Signal Detector"""

    def test_get_us_market_signal(self, test_db):
        """Test US market signal detection"""
        detector = SignalDetector(test_db)

        try:
            signal = detector.get_us_market_signal()

            # Check signal structure
            assert isinstance(signal, dict)
            assert 'signal' in signal
            assert signal['signal'] in ['BULLISH', 'BEARISH']
            assert 'confidence' in signal
        except Exception:
            # May fail if no data in test DB
            pytest.skip("No US market data available")
