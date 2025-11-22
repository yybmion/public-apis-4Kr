"""
Investment Signal Generator

여러 분석 결과를 종합하여 최종 투자 신호 생성

통합 분석:
- 미국-한국 시장 상관관계
- 경제 지표
- 시장 심리 (Fear & Greed)
- SEC 기관 투자자 동향

Author: AI Assistant
Created: 2025-11-22
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
from enum import Enum

from app.analyzers.market_correlation_analyzer import (
    MarketCorrelationAnalyzer,
    MarketSignal
)
from app.analyzers.economic_analyzer import EconomicAnalyzer


class InvestmentSignal(str, Enum):
    """Investment signal types"""
    STRONG_BUY = "STRONG_BUY"      # 강력 매수
    BUY = "BUY"                     # 매수
    WEAK_BUY = "WEAK_BUY"          # 약한 매수
    HOLD = "HOLD"                   # 보유
    WEAK_SELL = "WEAK_SELL"        # 약한 매도
    SELL = "SELL"                   # 매도
    STRONG_SELL = "STRONG_SELL"    # 강력 매도


class SignalGenerator:
    """
    투자 신호 생성기

    Features:
    - 다중 신호 통합 (시장, 경제, 심리)
    - 신뢰도 기반 가중치 적용
    - 리스크/리워드 분석
    - 구체적 액션 플랜 생성
    """

    def __init__(self):
        """Initialize Signal Generator"""
        self.market_analyzer = MarketCorrelationAnalyzer()
        self.economic_analyzer = EconomicAnalyzer()

        # 신호별 점수
        self.SIGNAL_SCORES = {
            InvestmentSignal.STRONG_BUY: 10,
            InvestmentSignal.BUY: 7,
            InvestmentSignal.WEAK_BUY: 4,
            InvestmentSignal.HOLD: 0,
            InvestmentSignal.WEAK_SELL: -4,
            InvestmentSignal.SELL: -7,
            InvestmentSignal.STRONG_SELL: -10
        }

    def generate_comprehensive_signal(
        self,
        sp500_data: Dict[str, float],
        nasdaq_data: Dict[str, float],
        fear_greed_score: float,
        fed_rate: float,
        kr_base_rate: float,
        usd_krw: float,
        yield_curve_data: Optional[Dict[str, float]] = None
    ) -> Dict[str, Any]:
        """
        종합 투자 신호 생성

        Args:
            sp500_data: S&P 500 데이터
            nasdaq_data: NASDAQ 데이터
            fear_greed_score: Fear & Greed Index (0-100)
            fed_rate: 미국 기준금리
            kr_base_rate: 한국 기준금리
            usd_krw: USD/KRW 환율
            yield_curve_data: 수익률 곡선 데이터 (optional)

        Returns:
            종합 투자 신호 및 전략
        """
        signals = []
        weights = []

        # 1. 시장 상관관계 분석 (가중치: 40%)
        market_analysis = self.market_analyzer.analyze_combined_signals(
            sp500_data,
            nasdaq_data,
            fear_greed_score
        )
        signals.append(market_analysis['final_signal'])
        weights.append(0.40)

        # 2. 경제 지표 분석 (가중치: 30%)
        rate_analysis = self.economic_analyzer.analyze_interest_rates(
            fed_rate,
            kr_base_rate
        )

        # 금리 상승 → 매도, 하락 → 매수
        rate_spread = fed_rate - kr_base_rate
        if rate_spread > 2.5:
            signals.append(MarketSignal.SELL)  # 높은 금리 차 → 위험
        elif rate_spread < 1.0:
            signals.append(MarketSignal.BUY)   # 낮은 금리 차 → 기회
        else:
            signals.append(MarketSignal.HOLD)
        weights.append(0.30)

        # 3. Fear & Greed 역발상 신호 (가중치: 20%)
        if fear_greed_score < 20:
            signals.append(MarketSignal.STRONG_BUY)  # 극단적 공포
        elif fear_greed_score < 40:
            signals.append(MarketSignal.BUY)
        elif fear_greed_score < 60:
            signals.append(MarketSignal.HOLD)
        elif fear_greed_score < 80:
            signals.append(MarketSignal.SELL)
        else:
            signals.append(MarketSignal.STRONG_SELL)  # 극단적 탐욕
        weights.append(0.20)

        # 4. 수익률 곡선 (가중치: 10%)
        if yield_curve_data:
            yc_analysis = self.economic_analyzer.analyze_yield_curve(
                yield_curve_data['2y'],
                yield_curve_data['10y']
            )

            if yc_analysis['recession_signal']:
                signals.append(MarketSignal.SELL)  # 경기 침체 신호
            else:
                signals.append(MarketSignal.BUY)   # 정상
            weights.append(0.10)

        # 가중 평균 점수 계산
        total_score = sum(
            self.SIGNAL_SCORES[sig] * weight
            for sig, weight in zip(signals, weights)
        )

        # 점수를 신호로 변환
        if total_score >= 7:
            final_signal = InvestmentSignal.STRONG_BUY
        elif total_score >= 4:
            final_signal = InvestmentSignal.BUY
        elif total_score >= 2:
            final_signal = InvestmentSignal.WEAK_BUY
        elif total_score >= -2:
            final_signal = InvestmentSignal.HOLD
        elif total_score >= -4:
            final_signal = InvestmentSignal.WEAK_SELL
        elif total_score >= -7:
            final_signal = InvestmentSignal.SELL
        else:
            final_signal = InvestmentSignal.STRONG_SELL

        # 신뢰도 계산 (신호 일치도)
        signal_agreement = len([s for s in signals if 'BUY' in str(s)]) / len(signals) if 'BUY' in str(final_signal) else \
                          len([s for s in signals if 'SELL' in str(s)]) / len(signals) if 'SELL' in str(final_signal) else \
                          len([s for s in signals if s == MarketSignal.HOLD]) / len(signals)

        # 구체적 액션 플랜 생성
        action_plan = self._generate_action_plan(
            final_signal,
            market_analysis,
            rate_analysis,
            fear_greed_score
        )

        return {
            'signal': final_signal,
            'score': total_score,
            'confidence': signal_agreement * 100,
            'breakdown': {
                'market_correlation': market_analysis['final_signal'],
                'economic_indicators': signals[1],
                'fear_greed': signals[2],
                'yield_curve': signals[3] if len(signals) > 3 else None
            },
            'action_plan': action_plan,
            'market_analysis': market_analysis,
            'rate_analysis': rate_analysis,
            'timestamp': datetime.now().isoformat()
        }

    def _generate_action_plan(
        self,
        signal: InvestmentSignal,
        market_analysis: Dict[str, Any],
        rate_analysis: Dict[str, Any],
        fear_greed_score: float
    ) -> Dict[str, Any]:
        """
        구체적 액션 플랜 생성

        Args:
            signal: 최종 투자 신호
            market_analysis: 시장 분석 결과
            rate_analysis: 금리 분석 결과
            fear_greed_score: Fear & Greed 점수

        Returns:
            액션 플랜
        """
        plan = {
            'action': '',
            'target_allocation': {},
            'specific_sectors': [],
            'risk_management': [],
            'timeframe': '',
            'stop_loss': None,
            'take_profit': None
        }

        if signal in [InvestmentSignal.STRONG_BUY, InvestmentSignal.BUY]:
            plan['action'] = '매수 포지션 확대'
            plan['target_allocation'] = {
                '주식': '70-80%',
                '채권': '10-20%',
                '현금': '10%'
            }
            plan['timeframe'] = '중장기 (3-12개월)'

            # 추천 섹터
            if market_analysis['sp500_analysis']['signal'] in [MarketSignal.BUY, MarketSignal.STRONG_BUY]:
                plan['specific_sectors'] = market_analysis['sp500_analysis']['sectors_to_watch']

            # 리스크 관리
            plan['risk_management'] = [
                f"분할 매수: 3-4회 나눠서 진입",
                f"손절 라인: -10% 이하 시 재평가",
                f"Fear & Greed가 80 이상 시 부분 매도 고려"
            ]

            # 스톱로스
            if signal == InvestmentSignal.STRONG_BUY:
                plan['stop_loss'] = -15  # -15%
                plan['take_profit'] = +30  # +30%
            else:
                plan['stop_loss'] = -10
                plan['take_profit'] = +20

        elif signal == InvestmentSignal.WEAK_BUY:
            plan['action'] = '소량 매수 또는 관망'
            plan['target_allocation'] = {
                '주식': '50-60%',
                '채권': '30-35%',
                '현금': '10-15%'
            }
            plan['timeframe'] = '단기-중기 (1-6개월)'
            plan['risk_management'] = [
                "소량 매수로 시작",
                "신호 강화 시 추가 매수",
                "손절 라인: -7%"
            ]

        elif signal == InvestmentSignal.HOLD:
            plan['action'] = '현재 포지션 유지'
            plan['target_allocation'] = {
                '주식': '40-50%',
                '채권': '30-40%',
                '현금': '20%'
            }
            plan['timeframe'] = '관망'
            plan['risk_management'] = [
                "불필요한 거래 자제",
                "시장 방향성 확인 후 재진입",
                "변동성 대비 현금 비중 유지"
            ]

        elif signal in [InvestmentSignal.WEAK_SELL, InvestmentSignal.SELL, InvestmentSignal.STRONG_SELL]:
            plan['action'] = '보유 비중 축소 또는 매도'
            plan['target_allocation'] = {
                '주식': '20-30%',
                '채권': '40-50%',
                '현금': '30-40%'
            }
            plan['timeframe'] = '즉시'
            plan['risk_management'] = [
                "수익 실현: 수익 종목부터 청산",
                "손절: 손실 종목도 정리",
                "현금 확보 후 재진입 기회 대기"
            ]

            if signal == InvestmentSignal.STRONG_SELL:
                plan['risk_management'].append(
                    "⚠️  주식 비중 20% 이하로 축소 권장"
                )

        # 경제 지표 기반 추가 조언
        if rate_analysis['impact']['beneficiary_sectors']:
            plan['specific_sectors'].extend(
                rate_analysis['impact']['beneficiary_sectors']
            )

        # 중복 제거
        plan['specific_sectors'] = list(set(plan['specific_sectors']))

        return plan

    def generate_daily_briefing(
        self,
        comprehensive_signal: Dict[str, Any],
        sp500_change: float,
        kospi_change: Optional[float] = None
    ) -> str:
        """
        일일 브리핑 생성 (텍스트 리포트)

        Args:
            comprehensive_signal: 종합 신호 결과
            sp500_change: S&P 500 변동률 (%)
            kospi_change: KOSPI 변동률 (%) (optional)

        Returns:
            일일 브리핑 텍스트
        """
        signal = comprehensive_signal['signal']
        confidence = comprehensive_signal['confidence']
        action = comprehensive_signal['action_plan']['action']

        briefing = f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  📊 일일 투자 브리핑
  {datetime.now().strftime('%Y년 %m월 %d일')}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🎯 최종 투자 신호: {signal} (신뢰도: {confidence:.0f}%)

📈 시장 상황:
  • S&P 500: {sp500_change:+.2f}%
"""

        if kospi_change is not None:
            briefing += f"  • KOSPI: {kospi_change:+.2f}%\n"

        briefing += f"""
💡 추천 액션: {action}

🎯 포트폴리오 구성:
"""
        for asset, allocation in comprehensive_signal['action_plan']['target_allocation'].items():
            briefing += f"  • {asset}: {allocation}\n"

        if comprehensive_signal['action_plan']['specific_sectors']:
            briefing += f"\n📊 주목 섹터:\n"
            for sector in comprehensive_signal['action_plan']['specific_sectors'][:5]:
                briefing += f"  • {sector}\n"

        briefing += f"\n⚠️  리스크 관리:\n"
        for risk in comprehensive_signal['action_plan']['risk_management'][:3]:
            briefing += f"  • {risk}\n"

        briefing += "\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"

        return briefing
