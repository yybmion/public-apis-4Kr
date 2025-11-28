"""
Data Collection Jobs

자동화된 데이터 수집 작업

Schedule:
- Fear & Greed: 매일 06:00 (미국 장 마감 후)
- FRED: 매일 07:00 (미국 경제 지표)
- ECOS: 매일 09:00 (한국 경제 지표)
- SEC EDGAR: 매주 월요일 08:00 (주간 업데이트)

Author: AI Assistant
Created: 2025-11-22
"""

import asyncio
from typing import Dict, Any, Optional
from datetime import datetime
import logging

from app.collectors.fear_greed_collector import FearGreedCollector
from app.collectors.fred_collector import FredCollector
from app.collectors.ecos_collector import EcosCollector
from app.collectors.sec_edgar_collector import SECEdgarCollector
from app.config import Settings

# Logger setup
logger = logging.getLogger(__name__)


class CollectionJobs:
    """
    데이터 수집 작업 관리자

    Features:
    - 비동기 데이터 수집
    - 오류 처리 및 재시도
    - 수집 결과 로깅
    """

    def __init__(self, settings: Optional[Settings] = None):
        """
        Initialize Collection Jobs

        Args:
            settings: Application settings
        """
        self.settings = settings or Settings()
        self.results = {}

    async def collect_fear_greed(self) -> Dict[str, Any]:
        """
        Fear & Greed Index 수집

        Schedule: 매일 06:00 (미국 장 마감 후)

        Returns:
            수집 결과
        """
        logger.info("🎯 Fear & Greed Index 수집 시작...")

        try:
            collector = FearGreedCollector()
            result = await collector.collect()

            if result.get('success'):
                data = result['data']
                logger.info(
                    f"✅ Fear & Greed 수집 완료: "
                    f"Score={data['score']:.1f}, Rating={data['rating']}"
                )

                self.results['fear_greed'] = {
                    'success': True,
                    'data': data,
                    'timestamp': datetime.now().isoformat()
                }

                return self.results['fear_greed']
            else:
                logger.error(f"❌ Fear & Greed 수집 실패: {result.get('error')}")
                return {'success': False, 'error': result.get('error')}

        except Exception as e:
            logger.error(f"❌ Fear & Greed 수집 예외: {str(e)}")
            return {'success': False, 'error': str(e)}

    async def collect_fred_data(self) -> Dict[str, Any]:
        """
        FRED 경제 지표 수집

        Schedule: 매일 07:00
        Indicators:
        - Federal Funds Rate
        - 10-Year Treasury
        - 2-Year Treasury
        - Yield Curve

        Returns:
            수집 결과
        """
        logger.info("📊 FRED 경제 지표 수집 시작...")

        if not self.settings.FRED_API_KEY or self.settings.FRED_API_KEY == "your_fred_api_key_here":
            logger.warning("⚠️  FRED API 키가 설정되지 않았습니다.")
            return {'success': False, 'error': 'API key not configured', 'skipped': True}

        try:
            collector = FredCollector(api_key=self.settings.FRED_API_KEY)

            # Federal Funds Rate
            fed_rate_result = await collector.collect(indicator='federal_funds_rate')

            if not fed_rate_result.get('success'):
                logger.error(f"❌ Fed Rate 수집 실패: {fed_rate_result.get('error')}")
                return fed_rate_result

            # Yield Curve
            yc_result = await collector.get_yield_curve()

            if yc_result.get('success'):
                logger.info(
                    f"✅ FRED 데이터 수집 완료: "
                    f"Fed Rate={fed_rate_result['data']['latest_value']:.2f}%, "
                    f"10Y-2Y={yc_result['data']['spreads'].get('10y_2y', 0):.3f}%"
                )

                self.results['fred'] = {
                    'success': True,
                    'fed_rate': fed_rate_result['data'],
                    'yield_curve': yc_result['data'],
                    'timestamp': datetime.now().isoformat()
                }

                return self.results['fred']
            else:
                logger.error(f"❌ Yield Curve 수집 실패: {yc_result.get('error')}")
                return yc_result

        except Exception as e:
            logger.error(f"❌ FRED 수집 예외: {str(e)}")
            return {'success': False, 'error': str(e)}

    async def collect_ecos_data(self) -> Dict[str, Any]:
        """
        ECOS 한국 경제 지표 수집

        Schedule: 매일 09:00
        Indicators:
        - Base Rate (기준금리)
        - USD/KRW Exchange Rate
        - Economic Snapshot

        Returns:
            수집 결과
        """
        logger.info("🇰🇷 ECOS 경제 지표 수집 시작...")

        if not self.settings.ECOS_API_KEY or self.settings.ECOS_API_KEY == "your_ecos_api_key_here":
            logger.warning("⚠️  ECOS API 키가 설정되지 않았습니다.")
            return {'success': False, 'error': 'API key not configured', 'skipped': True}

        try:
            collector = EcosCollector(api_key=self.settings.ECOS_API_KEY)

            # Base Rate
            base_rate_result = await collector.collect(indicator='base_rate')

            if not base_rate_result.get('success'):
                logger.error(f"❌ 기준금리 수집 실패: {base_rate_result.get('error')}")
                return base_rate_result

            # Economic Snapshot
            snapshot_result = await collector.get_economic_snapshot()

            if snapshot_result.get('success'):
                logger.info(
                    f"✅ ECOS 데이터 수집 완료: "
                    f"기준금리={base_rate_result['data']['latest_value']:.2f}%"
                )

                self.results['ecos'] = {
                    'success': True,
                    'base_rate': base_rate_result['data'],
                    'snapshot': snapshot_result['data'],
                    'timestamp': datetime.now().isoformat()
                }

                return self.results['ecos']
            else:
                logger.error(f"❌ Economic Snapshot 수집 실패: {snapshot_result.get('error')}")
                return snapshot_result

        except Exception as e:
            logger.error(f"❌ ECOS 수집 예외: {str(e)}")
            return {'success': False, 'error': str(e)}

    async def collect_sec_edgar_data(self, tickers: list = None) -> Dict[str, Any]:
        """
        SEC EDGAR 데이터 수집

        Schedule: 매주 월요일 08:00
        Default Tickers: AAPL, TSLA, MSFT, GOOGL, AMZN

        Args:
            tickers: 수집할 티커 리스트

        Returns:
            수집 결과
        """
        logger.info("🏢 SEC EDGAR 데이터 수집 시작...")

        if tickers is None:
            tickers = ['AAPL', 'TSLA', 'MSFT', 'GOOGL', 'AMZN']

        try:
            collector = SECEdgarCollector()
            results = []

            for ticker in tickers:
                logger.info(f"  📄 {ticker} 데이터 수집 중...")

                # Get latest 10-K
                result = await collector.get_latest_10k(ticker)

                if result.get('success'):
                    results.append({
                        'ticker': ticker,
                        'success': True,
                        'data': result['data']
                    })
                    logger.info(f"  ✅ {ticker} 수집 완료")
                else:
                    results.append({
                        'ticker': ticker,
                        'success': False,
                        'error': result.get('error')
                    })
                    logger.error(f"  ❌ {ticker} 수집 실패: {result.get('error')}")

                # Rate limiting
                await asyncio.sleep(0.15)  # 10 req/sec limit

            successful = sum(1 for r in results if r['success'])
            logger.info(f"✅ SEC EDGAR 수집 완료: {successful}/{len(tickers)} 성공")

            self.results['sec_edgar'] = {
                'success': True,
                'results': results,
                'successful_count': successful,
                'total_count': len(tickers),
                'timestamp': datetime.now().isoformat()
            }

            return self.results['sec_edgar']

        except Exception as e:
            logger.error(f"❌ SEC EDGAR 수집 예외: {str(e)}")
            return {'success': False, 'error': str(e)}

    async def collect_all_daily(self) -> Dict[str, Any]:
        """
        일일 전체 데이터 수집 (Fear & Greed, FRED, ECOS)

        Returns:
            전체 수집 결과
        """
        logger.info("=" * 80)
        logger.info("📅 일일 데이터 수집 시작")
        logger.info("=" * 80)

        start_time = datetime.now()

        # Collect all data
        fear_greed = await self.collect_fear_greed()
        fred = await self.collect_fred_data()
        ecos = await self.collect_ecos_data()

        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()

        # Summary
        successful = sum(1 for r in [fear_greed, fred, ecos] if r.get('success'))
        total = 3

        logger.info("=" * 80)
        logger.info(f"📊 일일 수집 완료: {successful}/{total} 성공 (소요시간: {duration:.1f}초)")
        logger.info("=" * 80)

        return {
            'success': successful > 0,
            'results': {
                'fear_greed': fear_greed,
                'fred': fred,
                'ecos': ecos
            },
            'summary': {
                'successful': successful,
                'total': total,
                'duration_seconds': duration
            },
            'timestamp': end_time.isoformat()
        }

    def get_latest_results(self) -> Dict[str, Any]:
        """
        최근 수집 결과 반환

        Returns:
            최근 수집 결과
        """
        return self.results
