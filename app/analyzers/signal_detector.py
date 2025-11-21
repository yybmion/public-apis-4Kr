"""
Signal Detector - Generate Trading Signals
Stock Intelligence System
"""

import pandas as pd
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from sqlalchemy.orm import Session

from app.models.stock import USIndex
from app.analyzers.technical_analyzer import TechnicalAnalyzer
from app.utils.logger import LoggerMixin


class SignalDetector(LoggerMixin):
    """
    Detect trading signals based on technical analysis and US market

    Signals:
    - US Market Signal (S&P 500 vs MA20)
    - Golden Cross / Dead Cross
    - RSI Oversold / Overbought
    - MACD Crossover
    - Bollinger Bands Breakout
    """

    def __init__(self, db: Optional[Session] = None):
        super().__init__()
        self.db = db
        self.analyzer = TechnicalAnalyzer()

    def get_us_market_signal(self) -> Dict[str, any]:
        """
        Get S&P 500 signal based on 20-day MA

        Returns:
            Dict with signal and details
        """
        if not self.db:
            self.log_warning("Database session not provided")
            return {'signal': 'NEUTRAL', 'confidence': 0}

        # Get latest S&P 500 data
        sp500 = (
            self.db.query(USIndex)
            .filter(USIndex.symbol == '^GSPC')
            .order_by(USIndex.date.desc())
            .first()
        )

        if not sp500 or not sp500.ma_20:
            self.log_warning("S&P 500 data not available")
            return {'signal': 'NEUTRAL', 'confidence': 0}

        # Calculate signal
        close = float(sp500.close)
        ma_20 = float(sp500.ma_20)
        diff_pct = ((close - ma_20) / ma_20) * 100

        if close > ma_20:
            signal = 'BULLISH'
            confidence = min(100, 50 + abs(diff_pct) * 10)
        else:
            signal = 'BEARISH'
            confidence = min(100, 50 + abs(diff_pct) * 10)

        return {
            'signal': signal,
            'confidence': confidence,
            'close': close,
            'ma_20': ma_20,
            'diff_pct': diff_pct,
            'date': sp500.date.isoformat(),
            'recommendation': self._get_recommendation(signal, confidence)
        }

    def _get_recommendation(self, signal: str, confidence: float) -> str:
        """Get investment recommendation based on signal"""
        if signal == 'BULLISH':
            if confidence > 70:
                return "한국 주식 적극 매수 포지션"
            elif confidence > 50:
                return "한국 주식 매수 포지션 유지"
            else:
                return "한국 주식 관망"
        else:  # BEARISH
            if confidence > 70:
                return "한국 주식 현금 비중 확대 (방어 전략)"
            elif confidence > 50:
                return "한국 주식 신중한 접근 필요"
            else:
                return "한국 주식 중립"

    def detect_stock_signals(
        self,
        df: pd.DataFrame,
        stock_code: str,
        stock_name: str
    ) -> Dict[str, any]:
        """
        Detect all trading signals for a stock

        Args:
            df: DataFrame with OHLCV and indicators
            stock_code: Stock code
            stock_name: Stock name

        Returns:
            Dict with all detected signals
        """
        if len(df) < 20:
            return {
                'stock_code': stock_code,
                'stock_name': stock_name,
                'signals': [],
                'score': 0,
                'action': 'HOLD'
            }

        # Calculate indicators if not present
        if 'rsi' not in df.columns:
            df = self.analyzer.calculate_all_indicators(df)

        # Detect patterns
        patterns = self.analyzer.detect_patterns(df)

        # Calculate trend strength
        trend = self.analyzer.calculate_trend_strength(df)

        # Collect signals
        signals = []
        score = 0

        latest = df.iloc[-1]

        # Golden Cross (강력한 매수 신호)
        if patterns['golden_cross']:
            signals.append({
                'type': 'GOLDEN_CROSS',
                'description': '골든크로스 발생 (단기 이평선이 장기 이평선 돌파)',
                'action': 'BUY',
                'strength': 'STRONG',
                'score': 25
            })
            score += 25

        # Dead Cross (강력한 매도 신호)
        if patterns['dead_cross']:
            signals.append({
                'type': 'DEAD_CROSS',
                'description': '데드크로스 발생 (단기 이평선이 장기 이평선 하향 돌파)',
                'action': 'SELL',
                'strength': 'STRONG',
                'score': -25
            })
            score -= 25

        # RSI Oversold (매수 신호)
        if patterns['rsi_oversold']:
            signals.append({
                'type': 'RSI_OVERSOLD',
                'description': f'RSI 과매도 구간 ({latest["rsi"]:.1f})',
                'action': 'BUY',
                'strength': 'MEDIUM',
                'score': 15
            })
            score += 15

        # RSI Overbought (매도 신호)
        if patterns['rsi_overbought']:
            signals.append({
                'type': 'RSI_OVERBOUGHT',
                'description': f'RSI 과매수 구간 ({latest["rsi"]:.1f})',
                'action': 'SELL',
                'strength': 'MEDIUM',
                'score': -15
            })
            score -= 15

        # MACD Bullish Crossover
        if patterns['macd_bullish']:
            signals.append({
                'type': 'MACD_BULLISH',
                'description': 'MACD 상향 돌파',
                'action': 'BUY',
                'strength': 'MEDIUM',
                'score': 15
            })
            score += 15

        # MACD Bearish Crossover
        if patterns['macd_bearish']:
            signals.append({
                'type': 'MACD_BEARISH',
                'description': 'MACD 하향 돌파',
                'action': 'SELL',
                'strength': 'MEDIUM',
                'score': -15
            })
            score -= 15

        # Price above MA20 (약한 매수 신호)
        if patterns['above_ma_20']:
            signals.append({
                'type': 'ABOVE_MA20',
                'description': '20일 이동평균선 위에 위치',
                'action': 'BUY',
                'strength': 'WEAK',
                'score': 10
            })
            score += 10

        # Price above MA60 (약한 매수 신호)
        if patterns['above_ma_60']:
            signals.append({
                'type': 'ABOVE_MA60',
                'description': '60일 이동평균선 위에 위치',
                'action': 'BUY',
                'strength': 'WEAK',
                'score': 5
            })
            score += 5

        # Bollinger Bands Squeeze (변동성 축소 후 확대 예상)
        if patterns['bb_squeeze']:
            signals.append({
                'type': 'BB_SQUEEZE',
                'description': '볼린저 밴드 수축 (큰 변동성 임박)',
                'action': 'WATCH',
                'strength': 'INFO',
                'score': 0
            })

        # Add trend info
        signals.append({
            'type': 'TREND',
            'description': f'추세: {self._translate_trend(trend["trend_direction"])} (점수: {trend["trend_score"]})',
            'action': 'INFO',
            'strength': 'INFO',
            'score': trend['trend_score'] // 5
        })
        score += trend['trend_score'] // 5

        # Determine final action
        if score > 30:
            action = 'STRONG_BUY'
        elif score > 10:
            action = 'BUY'
        elif score > -10:
            action = 'HOLD'
        elif score > -30:
            action = 'SELL'
        else:
            action = 'STRONG_SELL'

        return {
            'stock_code': stock_code,
            'stock_name': stock_name,
            'signals': signals,
            'total_signals': len(signals),
            'score': score,
            'action': action,
            'trend': trend,
            'patterns': patterns,
            'latest_price': float(latest['close']),
            'rsi': float(latest.get('rsi', 0)) if 'rsi' in latest else None,
            'macd': float(latest.get('macd', 0)) if 'macd' in latest else None,
            'timestamp': datetime.now().isoformat()
        }

    def _translate_trend(self, direction: str) -> str:
        """Translate trend direction to Korean"""
        translations = {
            'strong_uptrend': '강한 상승 추세',
            'uptrend': '상승 추세',
            'neutral': '중립',
            'downtrend': '하락 추세',
            'strong_downtrend': '강한 하락 추세'
        }
        return translations.get(direction, direction)

    def generate_combined_signal(
        self,
        stock_signals: Dict[str, any],
        us_signal: Optional[Dict[str, any]] = None
    ) -> Dict[str, any]:
        """
        Combine stock signals with US market signal

        US-Korea correlation: 0.85
        If S&P 500 is bullish, boost Korean stock buy signals
        If S&P 500 is bearish, reduce Korean stock buy signals
        """
        if us_signal is None:
            us_signal = self.get_us_market_signal()

        stock_score = stock_signals['score']
        stock_action = stock_signals['action']

        # Adjust score based on US market
        if us_signal['signal'] == 'BULLISH':
            # Boost buy signals
            adjusted_score = stock_score + (us_signal['confidence'] * 0.3)
            us_impact = 'positive'
        elif us_signal['signal'] == 'BEARISH':
            # Reduce buy signals / boost sell signals
            adjusted_score = stock_score - (us_signal['confidence'] * 0.3)
            us_impact = 'negative'
        else:
            adjusted_score = stock_score
            us_impact = 'neutral'

        # Determine final action
        if adjusted_score > 40:
            final_action = 'STRONG_BUY'
        elif adjusted_score > 15:
            final_action = 'BUY'
        elif adjusted_score > -15:
            final_action = 'HOLD'
        elif adjusted_score > -40:
            final_action = 'SELL'
        else:
            final_action = 'STRONG_SELL'

        return {
            **stock_signals,
            'us_market_signal': us_signal['signal'],
            'us_market_confidence': us_signal['confidence'],
            'us_impact': us_impact,
            'original_score': stock_score,
            'adjusted_score': adjusted_score,
            'original_action': stock_action,
            'final_action': final_action,
            'recommendation': self._generate_recommendation(
                stock_signals,
                us_signal,
                final_action
            )
        }

    def _generate_recommendation(
        self,
        stock_signals: Dict,
        us_signal: Dict,
        final_action: str
    ) -> str:
        """Generate human-readable recommendation"""
        stock_name = stock_signals['stock_name']

        recommendations = {
            'STRONG_BUY': f"🟢 {stock_name} 적극 매수 추천",
            'BUY': f"🟢 {stock_name} 매수 고려",
            'HOLD': f"⚪ {stock_name} 보유 유지",
            'SELL': f"🔴 {stock_name} 매도 고려",
            'STRONG_SELL': f"🔴 {stock_name} 적극 매도 추천"
        }

        base_rec = recommendations.get(final_action, f"{stock_name} 관망")

        # Add US market context
        if us_signal['signal'] == 'BULLISH':
            context = "\n📊 미국 증시 상승 추세로 한국 증시에 긍정적"
        elif us_signal['signal'] == 'BEARISH':
            context = "\n📊 미국 증시 하락 추세로 한국 증시에 부정적"
        else:
            context = ""

        # Add key signals
        key_signals = [s for s in stock_signals['signals'] if s['strength'] in ['STRONG', 'MEDIUM']]
        if key_signals:
            signal_text = "\n\n주요 신호:\n" + "\n".join([f"• {s['description']}" for s in key_signals[:3]])
        else:
            signal_text = ""

        return base_rec + context + signal_text

    def scan_market(
        self,
        stock_data_list: List[Tuple[str, str, pd.DataFrame]],
        top_n: int = 10
    ) -> List[Dict]:
        """
        Scan multiple stocks and return top opportunities

        Args:
            stock_data_list: List of (code, name, dataframe) tuples
            top_n: Number of top stocks to return

        Returns:
            List of top stock signals sorted by score
        """
        all_signals = []

        us_signal = self.get_us_market_signal()

        for stock_code, stock_name, df in stock_data_list:
            try:
                stock_signals = self.detect_stock_signals(df, stock_code, stock_name)
                combined = self.generate_combined_signal(stock_signals, us_signal)
                all_signals.append(combined)
            except Exception as e:
                self.log_error(f"Failed to analyze {stock_code}: {str(e)}")
                continue

        # Sort by adjusted score
        all_signals.sort(key=lambda x: x['adjusted_score'], reverse=True)

        # Return top N
        return all_signals[:top_n]
