"""
Economic Indicator Analyzer

경제 지표 분석 및 투자 영향 평가

분석 항목:
- 금리 (미국 Fed, 한국 기준금리)
- 환율 (USD/KRW)
- 인플레이션
- GDP 성장률
- 수익률 곡선 (Yield Curve)

Author: AI Assistant
Created: 2025-11-22
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
from enum import Enum


class InterestRateTrend(str, Enum):
    """Interest rate trend"""
    RISING = "RISING"          # 상승 중
    FALLING = "FALLING"        # 하락 중
    STABLE = "STABLE"          # 안정적
    PEAK = "PEAK"              # 정점 도달
    BOTTOM = "BOTTOM"          # 바닥 도달


class EconomicAnalyzer:
    """
    경제 지표 분석기

    Features:
    - 금리 분석 및 영향 평가
    - 환율 분석
    - 수익률 곡선 분석 (경기 침체 예측)
    - 섹터별 영향 분석
    """

    # 금리별 수혜/악영향 섹터
    RATE_SENSITIVE_SECTORS = {
        'rising_rates': {
            'beneficiaries': ['은행', '보험', '증권'],
            'victims': ['건설', '부동산', '유틸리티']
        },
        'falling_rates': {
            'beneficiaries': ['건설', '부동산', '자동차'],
            'victims': ['은행', '보험']
        }
    }

    # 환율 민감 섹터
    EXCHANGE_RATE_SECTORS = {
        'krw_weakening': {  # 원화 약세 (달러 강세)
            'beneficiaries': ['수출주 (반도체, 자동차, 화학)'],
            'victims': ['수입주 (항공, 유통)']
        },
        'krw_strengthening': {  # 원화 강세 (달러 약세)
            'beneficiaries': ['수입주 (항공, 유통)', '내수주'],
            'victims': ['수출주']
        }
    }

    def __init__(self):
        """Initialize Economic Analyzer"""
        pass

    def analyze_interest_rates(
        self,
        us_fed_rate: float,
        kr_base_rate: float,
        fed_rate_history: Optional[List[float]] = None,
        kr_rate_history: Optional[List[float]] = None
    ) -> Dict[str, Any]:
        """
        금리 분석 및 투자 영향 평가

        Args:
            us_fed_rate: 미국 연준 기준금리 (%)
            kr_base_rate: 한국 기준금리 (%)
            fed_rate_history: 미국 금리 이력 (최근 순)
            kr_rate_history: 한국 금리 이력 (최근 순)

        Returns:
            금리 분석 결과
        """
        analysis = {
            'current_rates': {
                'us_fed_rate': us_fed_rate,
                'kr_base_rate': kr_base_rate,
                'spread': us_fed_rate - kr_base_rate
            },
            'trends': {},
            'impact': {
                'beneficiary_sectors': [],
                'victim_sectors': []
            },
            'investment_strategy': {},
            'warnings': []
        }

        # 1. 금리 추세 분석
        if fed_rate_history and len(fed_rate_history) >= 2:
            fed_trend = self._analyze_rate_trend(fed_rate_history)
            analysis['trends']['us_fed'] = fed_trend
        else:
            analysis['trends']['us_fed'] = InterestRateTrend.STABLE

        if kr_rate_history and len(kr_rate_history) >= 2:
            kr_trend = self._analyze_rate_trend(kr_rate_history)
            analysis['trends']['kr_base'] = kr_trend
        else:
            analysis['trends']['kr_base'] = InterestRateTrend.STABLE

        # 2. 금리 수준 평가
        if us_fed_rate > 5.0:
            analysis['warnings'].append(
                "⚠️  미국 고금리 (5% 이상) → 글로벌 유동성 축소"
            )
            analysis['impact']['victim_sectors'].extend(
                self.RATE_SENSITIVE_SECTORS['rising_rates']['victims']
            )
        elif us_fed_rate < 2.0:
            analysis['warnings'].append(
                "💡 미국 저금리 (2% 미만) → 유동성 풍부, 위험자산 선호"
            )
            analysis['impact']['beneficiary_sectors'].extend(
                self.RATE_SENSITIVE_SECTORS['falling_rates']['beneficiaries']
            )

        # 3. 미국-한국 금리 차이 분석
        spread = us_fed_rate - kr_base_rate

        if spread > 2.0:
            analysis['warnings'].append(
                f"⚠️  미국 금리가 한국보다 {spread:.1f}%p 높음 → 원화 약세 압력"
            )
            analysis['investment_strategy']['currency'] = "달러 자산 비중 확대"
            analysis['investment_strategy']['sectors'] = [
                "수출주 (반도체, 자동차)"
            ]
        elif spread < -1.0:
            analysis['warnings'].append(
                f"💡 한국 금리가 미국보다 {abs(spread):.1f}%p 높음 → 원화 강세 가능"
            )
            analysis['investment_strategy']['currency'] = "원화 자산 비중 확대"
            analysis['investment_strategy']['sectors'] = [
                "내수주, 수입 기업"
            ]
        else:
            analysis['warnings'].append(
                f"✓ 금리 차이 적정 범위 ({spread:+.1f}%p)"
            )

        # 4. 투자 전략 수립
        us_trend = analysis['trends']['us_fed']

        if us_trend == InterestRateTrend.RISING:
            analysis['investment_strategy']['general'] = (
                "금리 상승기 → 은행주 매수, 건설/부동산 매도"
            )
            analysis['impact']['beneficiary_sectors'].extend(
                self.RATE_SENSITIVE_SECTORS['rising_rates']['beneficiaries']
            )
        elif us_trend == InterestRateTrend.FALLING:
            analysis['investment_strategy']['general'] = (
                "금리 하락기 → 건설/부동산 매수, 은행주 매도"
            )
            analysis['impact']['beneficiary_sectors'].extend(
                self.RATE_SENSITIVE_SECTORS['falling_rates']['beneficiaries']
            )
        elif us_trend == InterestRateTrend.PEAK:
            analysis['investment_strategy']['general'] = (
                "금리 정점 → 경기 순환 섹터 매수 시점"
            )
            analysis['warnings'].append(
                "💡 금리 고점 도달 → 조만간 인하 가능성"
            )

        # 중복 제거
        analysis['impact']['beneficiary_sectors'] = list(set(
            analysis['impact']['beneficiary_sectors']
        ))
        analysis['impact']['victim_sectors'] = list(set(
            analysis['impact']['victim_sectors']
        ))

        return analysis

    def analyze_yield_curve(
        self,
        treasury_2y: float,
        treasury_10y: float,
        treasury_30y: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        수익률 곡선 분석 (경기 침체 예측)

        Args:
            treasury_2y: 2년물 국채 수익률 (%)
            treasury_10y: 10년물 국채 수익률 (%)
            treasury_30y: 30년물 국채 수익률 (%)

        Returns:
            수익률 곡선 분석 결과
        """
        spread_10y_2y = treasury_10y - treasury_2y

        analysis = {
            'yields': {
                '2y': treasury_2y,
                '10y': treasury_10y,
                '30y': treasury_30y
            },
            'spreads': {
                '10y_2y': spread_10y_2y
            },
            'yield_curve_shape': '',
            'recession_signal': False,
            'recession_probability': 0.0,
            'investment_strategy': '',
            'warnings': []
        }

        # 수익률 곡선 역전 분석
        if spread_10y_2y < -0.5:
            analysis['yield_curve_shape'] = '강한 역전 (Inverted)'
            analysis['recession_signal'] = True
            analysis['recession_probability'] = min(80.0, abs(spread_10y_2y) * 40)
            analysis['warnings'].append(
                f"⚠️  수익률 곡선 강한 역전 ({spread_10y_2y:.2f}%p)"
            )
            analysis['warnings'].append(
                "⚠️  6-18개월 내 경기 침체 가능성 높음"
            )
            analysis['investment_strategy'] = (
                "방어적 포트폴리오 구성: 채권, 금, 방어주 비중 확대"
            )
        elif spread_10y_2y < 0:
            analysis['yield_curve_shape'] = '약한 역전 (Slightly Inverted)'
            analysis['recession_signal'] = True
            analysis['recession_probability'] = 40.0
            analysis['warnings'].append(
                f"⚠️  수익률 곡선 역전 ({spread_10y_2y:.2f}%p)"
            )
            analysis['investment_strategy'] = (
                "경계 모드: 현금 비중 확대, 변동성 대비"
            )
        elif spread_10y_2y < 0.5:
            analysis['yield_curve_shape'] = '평탄화 (Flat)'
            analysis['recession_probability'] = 20.0
            analysis['warnings'].append(
                f"💡 수익률 곡선 평탄화 ({spread_10y_2y:.2f}%p)"
            )
            analysis['investment_strategy'] = (
                "주의 모드: 과도한 위험 자산 노출 자제"
            )
        else:
            analysis['yield_curve_shape'] = '정상 (Normal/Steep)'
            analysis['recession_probability'] = 10.0
            analysis['warnings'].append(
                f"✓ 수익률 곡선 정상 ({spread_10y_2y:.2f}%p)"
            )
            analysis['investment_strategy'] = (
                "공격적 포트폴리오: 성장주, 경기 민감주 투자"
            )

        return analysis

    def analyze_exchange_rate(
        self,
        usd_krw: float,
        usd_krw_history: Optional[List[float]] = None
    ) -> Dict[str, Any]:
        """
        환율 분석 및 섹터 영향

        Args:
            usd_krw: USD/KRW 환율
            usd_krw_history: 환율 이력 (최근 순)

        Returns:
            환율 분석 결과
        """
        analysis = {
            'current_rate': usd_krw,
            'trend': '',
            'strength': '',
            'impact': {
                'beneficiary_sectors': [],
                'victim_sectors': []
            },
            'warnings': []
        }

        # 환율 수준 평가
        if usd_krw > 1400:
            analysis['strength'] = '원화 약세 (Strong)'
            analysis['warnings'].append(
                f"⚠️  원화 약세 심화 ({usd_krw:.0f}원)"
            )
            analysis['impact']['beneficiary_sectors'] = self.EXCHANGE_RATE_SECTORS['krw_weakening']['beneficiaries']
            analysis['impact']['victim_sectors'] = self.EXCHANGE_RATE_SECTORS['krw_weakening']['victims']
        elif usd_krw < 1100:
            analysis['strength'] = '원화 강세 (Strong)'
            analysis['warnings'].append(
                f"💡 원화 강세 ({usd_krw:.0f}원)"
            )
            analysis['impact']['beneficiary_sectors'] = self.EXCHANGE_RATE_SECTORS['krw_strengthening']['beneficiaries']
            analysis['impact']['victim_sectors'] = self.EXCHANGE_RATE_SECTORS['krw_strengthening']['victims']
        else:
            analysis['strength'] = '적정 수준'
            analysis['warnings'].append(
                f"✓ 환율 적정 수준 ({usd_krw:.0f}원)"
            )

        # 추세 분석
        if usd_krw_history and len(usd_krw_history) >= 2:
            recent_avg = sum(usd_krw_history[:5]) / 5 if len(usd_krw_history) >= 5 else usd_krw_history[0]
            older_avg = sum(usd_krw_history[5:10]) / 5 if len(usd_krw_history) >= 10 else recent_avg

            if recent_avg > older_avg * 1.02:
                analysis['trend'] = '상승 (원화 약세)'
            elif recent_avg < older_avg * 0.98:
                analysis['trend'] = '하락 (원화 강세)'
            else:
                analysis['trend'] = '안정'

        return analysis

    def _analyze_rate_trend(self, rate_history: List[float]) -> InterestRateTrend:
        """
        금리 추세 분석 (내부 메서드)

        Args:
            rate_history: 금리 이력 (최근 순서)

        Returns:
            금리 추세
        """
        if len(rate_history) < 2:
            return InterestRateTrend.STABLE

        recent = rate_history[0]
        previous = rate_history[1]

        # 최근 3개 데이터로 추세 확인
        if len(rate_history) >= 3:
            trend_data = rate_history[:3]

            # 모두 상승
            if all(trend_data[i] > trend_data[i + 1] for i in range(len(trend_data) - 1)):
                # 상승 폭이 줄어들면 Peak
                if (trend_data[0] - trend_data[1]) < (trend_data[1] - trend_data[2]) * 0.5:
                    return InterestRateTrend.PEAK
                return InterestRateTrend.RISING

            # 모두 하락
            if all(trend_data[i] < trend_data[i + 1] for i in range(len(trend_data) - 1)):
                # 하락 폭이 줄어들면 Bottom
                if (trend_data[1] - trend_data[0]) < (trend_data[2] - trend_data[1]) * 0.5:
                    return InterestRateTrend.BOTTOM
                return InterestRateTrend.FALLING

        # 2개 데이터로만 판단
        if recent > previous:
            return InterestRateTrend.RISING
        elif recent < previous:
            return InterestRateTrend.FALLING
        else:
            return InterestRateTrend.STABLE

    def generate_economic_summary(
        self,
        fred_data: Dict[str, Any],
        ecos_data: Dict[str, Any],
        fear_greed_score: float
    ) -> Dict[str, Any]:
        """
        경제 지표 종합 요약

        Args:
            fred_data: FRED 데이터 (금리, 수익률 곡선 등)
            ecos_data: ECOS 데이터 (한국 경제 지표)
            fear_greed_score: Fear & Greed Index

        Returns:
            경제 지표 종합 요약
        """
        summary = {
            'overall_economic_condition': '',
            'market_phase': '',
            'recommended_asset_allocation': {},
            'key_insights': [],
            'risks': [],
            'opportunities': []
        }

        # 금리 분석
        if 'fed_rate' in fred_data and 'base_rate' in ecos_data:
            rate_analysis = self.analyze_interest_rates(
                fred_data['fed_rate'],
                ecos_data['base_rate']
            )
            summary['key_insights'].extend(rate_analysis['warnings'])

        # 수익률 곡선 분석
        if 'yield_curve' in fred_data:
            yc = fred_data['yield_curve']
            if yc.get('recession_signal'):
                summary['risks'].append(
                    "경기 침체 신호 - 방어적 포지션 권장"
                )
                summary['overall_economic_condition'] = '경기 침체 우려'
                summary['market_phase'] = 'Late Cycle / Recession'
            else:
                summary['overall_economic_condition'] = '경기 확장'
                summary['market_phase'] = 'Early / Mid Cycle'

        # Fear & Greed 반영
        if fear_greed_score < 25:
            summary['opportunities'].append(
                "극단적 공포 - 역발상 매수 기회"
            )
        elif fear_greed_score > 75:
            summary['risks'].append(
                "극단적 탐욕 - 고점 경계 필요"
            )

        # 자산 배분 권장
        if summary['market_phase'] == 'Early / Mid Cycle':
            summary['recommended_asset_allocation'] = {
                '주식': '60-70%',
                '채권': '20-30%',
                '현금': '10%'
            }
        elif summary['market_phase'] == 'Late Cycle / Recession':
            summary['recommended_asset_allocation'] = {
                '주식': '30-40%',
                '채권': '40-50%',
                '현금': '20-30%'
            }
        else:
            summary['recommended_asset_allocation'] = {
                '주식': '50%',
                '채권': '30%',
                '현금': '20%'
            }

        return summary
