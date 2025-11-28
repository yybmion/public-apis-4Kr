"""
Analysis Jobs

자동화된 분석 작업

Schedule:
- Market Analysis: 매일 09:30 (한국 장 시작 직후)
- Daily Briefing: 매일 09:00, 15:40 (개장 전, 마감 후)
- Signal Generation: 매일 08:30 (개장 전)

Author: AI Assistant
Created: 2025-11-22
"""

import asyncio
from typing import Dict, Any, Optional
from datetime import datetime
import logging

from app.analyzers.market_correlation_analyzer import MarketCorrelationAnalyzer
from app.analyzers.economic_analyzer import EconomicAnalyzer
from app.analyzers.signal_generator import SignalGenerator

# Logger setup
logger = logging.getLogger(__name__)


class AnalysisJobs:
    """
    분석 작업 관리자

    Features:
    - 시장 상관관계 분석
    - 경제 지표 분석
    - 투자 신호 생성
    - 일일 브리핑 생성
    """

    def __init__(self):
        """Initialize Analysis Jobs"""
        self.market_analyzer = MarketCorrelationAnalyzer()
        self.economic_analyzer = EconomicAnalyzer()
        self.signal_generator = SignalGenerator()
        self.latest_signal = None

    async def analyze_market_correlation(
        self,
        collection_results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        시장 상관관계 분석

        Args:
            collection_results: 데이터 수집 결과

        Returns:
            분석 결과
        """
        logger.info("📊 시장 상관관계 분석 시작...")

        try:
            # Extract data
            fear_greed_data = collection_results.get('fear_greed', {})
            fear_greed_score = fear_greed_data.get('data', {}).get('score', 50.0)

            # Mock S&P 500 and NASDAQ data (실제로는 Yahoo Finance 등에서 수집)
            # TODO: Integrate with Yahoo Finance collector
            sp500_data = {
                'close': 4550.50,
                'ma20': 4530.00,
                'ma60': 4480.00,
                'change_pct': -1.2
            }

            nasdaq_data = {
                'close': 14200.30,
                'change_pct': -0.8
            }

            # Analyze
            analysis = self.market_analyzer.analyze_combined_signals(
                sp500_data,
                nasdaq_data,
                fear_greed_score
            )

            logger.info(
                f"✅ 시장 분석 완료: Signal={analysis['final_signal']}, "
                f"Agreement={analysis['agreement_level'] * 100:.0f}%"
            )

            return {
                'success': True,
                'analysis': analysis,
                'timestamp': datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"❌ 시장 분석 예외: {str(e)}")
            return {'success': False, 'error': str(e)}

    async def analyze_economic_indicators(
        self,
        collection_results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        경제 지표 분석

        Args:
            collection_results: 데이터 수집 결과

        Returns:
            분석 결과
        """
        logger.info("📈 경제 지표 분석 시작...")

        try:
            # Extract FRED data
            fred_data = collection_results.get('fred', {})
            if not fred_data.get('success'):
                logger.warning("⚠️  FRED 데이터 없음 - 경제 분석 제한적")
                return {'success': False, 'error': 'No FRED data'}

            # Extract ECOS data
            ecos_data = collection_results.get('ecos', {})
            if not ecos_data.get('success'):
                logger.warning("⚠️  ECOS 데이터 없음 - 경제 분석 제한적")
                return {'success': False, 'error': 'No ECOS data'}

            # Get rates
            us_fed_rate = fred_data.get('fed_rate', {}).get('latest_value', 5.25)
            kr_base_rate = ecos_data.get('base_rate', {}).get('latest_value', 3.50)

            # Analyze interest rates
            rate_analysis = self.economic_analyzer.analyze_interest_rates(
                us_fed_rate,
                kr_base_rate
            )

            # Analyze yield curve
            yc_data = fred_data.get('yield_curve', {})
            yc_analysis = None

            if yc_data.get('yields'):
                yields = yc_data['yields']
                if '2y' in yields and '10y' in yields:
                    yc_analysis = self.economic_analyzer.analyze_yield_curve(
                        yields['2y'],
                        yields['10y']
                    )

            logger.info(
                f"✅ 경제 분석 완료: "
                f"Fed={us_fed_rate:.2f}%, KR={kr_base_rate:.2f}%, "
                f"Spread={us_fed_rate - kr_base_rate:+.2f}%p"
            )

            return {
                'success': True,
                'rate_analysis': rate_analysis,
                'yield_curve_analysis': yc_analysis,
                'timestamp': datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"❌ 경제 분석 예외: {str(e)}")
            return {'success': False, 'error': str(e)}

    async def generate_investment_signal(
        self,
        collection_results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        투자 신호 생성

        Args:
            collection_results: 데이터 수집 결과

        Returns:
            투자 신호
        """
        logger.info("🎯 투자 신호 생성 시작...")

        try:
            # Extract data
            fear_greed_data = collection_results.get('fear_greed', {})
            fear_greed_score = fear_greed_data.get('data', {}).get('score', 50.0)

            fred_data = collection_results.get('fred', {})
            ecos_data = collection_results.get('ecos', {})

            # Mock market data (TODO: integrate with Yahoo Finance)
            sp500_data = {
                'close': 4550.50,
                'ma20': 4530.00,
                'ma60': 4480.00,
                'change_pct': -1.2
            }

            nasdaq_data = {
                'close': 14200.30,
                'change_pct': -0.8
            }

            # Get economic data
            fed_rate = fred_data.get('fed_rate', {}).get('latest_value', 5.25)
            kr_base_rate = ecos_data.get('base_rate', {}).get('latest_value', 3.50)

            # Mock exchange rate (TODO: integrate with ECOS)
            usd_krw = 1330.50

            # Yield curve data
            yield_curve_data = None
            yc = fred_data.get('yield_curve', {})
            if yc.get('yields'):
                yields = yc['yields']
                if '2y' in yields and '10y' in yields:
                    yield_curve_data = {
                        '2y': yields['2y'],
                        '10y': yields['10y']
                    }

            # Generate comprehensive signal
            signal = self.signal_generator.generate_comprehensive_signal(
                sp500_data,
                nasdaq_data,
                fear_greed_score,
                fed_rate,
                kr_base_rate,
                usd_krw,
                yield_curve_data
            )

            logger.info(
                f"✅ 투자 신호 생성 완료: "
                f"Signal={signal['signal']}, "
                f"Confidence={signal['confidence']:.0f}%"
            )

            # Store latest signal
            self.latest_signal = signal

            return {
                'success': True,
                'signal': signal,
                'timestamp': datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"❌ 신호 생성 예외: {str(e)}")
            return {'success': False, 'error': str(e)}

    async def generate_daily_briefing(
        self,
        collection_results: Dict[str, Any],
        signal_results: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        일일 브리핑 생성

        Args:
            collection_results: 데이터 수집 결과
            signal_results: 투자 신호 결과 (optional)

        Returns:
            브리핑 텍스트
        """
        logger.info("📰 일일 브리핑 생성 시작...")

        try:
            # Get signal
            if signal_results and signal_results.get('success'):
                signal = signal_results['signal']
            elif self.latest_signal:
                signal = self.latest_signal
            else:
                logger.warning("⚠️  투자 신호 없음 - 브리핑 제한적")
                return {'success': False, 'error': 'No signal data'}

            # Mock market changes (TODO: integrate with real data)
            sp500_change = -1.2
            kospi_change = -0.8

            # Generate briefing
            briefing = self.signal_generator.generate_daily_briefing(
                signal,
                sp500_change,
                kospi_change
            )

            logger.info("✅ 일일 브리핑 생성 완료")

            return {
                'success': True,
                'briefing': briefing,
                'signal': signal['signal'],
                'confidence': signal['confidence'],
                'timestamp': datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"❌ 브리핑 생성 예외: {str(e)}")
            return {'success': False, 'error': str(e)}

    async def run_full_analysis(
        self,
        collection_results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        전체 분석 실행 (상관관계 + 경제 + 신호 + 브리핑)

        Args:
            collection_results: 데이터 수집 결과

        Returns:
            전체 분석 결과
        """
        logger.info("=" * 80)
        logger.info("🔍 전체 분석 시작")
        logger.info("=" * 80)

        start_time = datetime.now()

        # Run analyses
        market_analysis = await self.analyze_market_correlation(collection_results)
        economic_analysis = await self.analyze_economic_indicators(collection_results)
        signal = await self.generate_investment_signal(collection_results)
        briefing = await self.generate_daily_briefing(collection_results, signal)

        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()

        # Summary
        successful = sum(1 for r in [market_analysis, economic_analysis, signal, briefing] if r.get('success'))
        total = 4

        logger.info("=" * 80)
        logger.info(f"✅ 전체 분석 완료: {successful}/{total} 성공 (소요시간: {duration:.1f}초)")
        logger.info("=" * 80)

        # Print briefing if available
        if briefing.get('success'):
            print(briefing['briefing'])

        return {
            'success': successful > 0,
            'results': {
                'market_analysis': market_analysis,
                'economic_analysis': economic_analysis,
                'investment_signal': signal,
                'daily_briefing': briefing
            },
            'summary': {
                'successful': successful,
                'total': total,
                'duration_seconds': duration
            },
            'timestamp': end_time.isoformat()
        }

    def get_latest_signal(self) -> Optional[Dict[str, Any]]:
        """
        최근 투자 신호 반환

        Returns:
            최근 투자 신호
        """
        return self.latest_signal
