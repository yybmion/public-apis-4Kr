"""
ECOS (Economic Statistics System) API Collector
Stock Intelligence System

Bank of Korea Economic Statistics System
API Documentation: https://ecos.bok.or.kr/api/

Required: ECOS_API_KEY from Bank of Korea
"""

import asyncio
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import aiohttp

from app.collectors.base import BaseCollector, CollectionError
from app.config import settings


class EcosCollector(BaseCollector):
    """
    ECOS (한국은행 경제통계시스템) API Collector

    Collects Korean macroeconomic indicators from Bank of Korea.

    Features:
    - 100,000+ economic statistics
    - Official Bank of Korea data
    - Free API

    Required:
    - ECOS_API_KEY environment variable
    """

    BASE_URL = "https://ecos.bok.or.kr/api/StatisticSearch"

    # Major Korean Economic Indicators
    # Format: (통계표코드, 항목코드1, 항목코드2, 항목코드3)
    INDICATORS = {
        # Interest Rates (금리)
        'base_rate': {
            'stat_code': '722Y001',
            'item_code1': 'AA11',
            'item_code2': None,
            'item_code3': None,
            'name': '한국은행 기준금리',
            'unit': 'percent',
            'frequency': 'D'  # Daily
        },
        'call_rate': {
            'stat_code': '817Y002',
            'item_code1': '010101000',
            'item_code2': None,
            'item_code3': None,
            'name': '콜금리',
            'unit': 'percent',
            'frequency': 'D'
        },
        'cd_91d': {
            'stat_code': '817Y002',
            'item_code1': '010502000',
            'item_code2': None,
            'item_code3': None,
            'name': 'CD금리 91일',
            'unit': 'percent',
            'frequency': 'D'
        },
        'treasury_3y': {
            'stat_code': '817Y002',
            'item_code1': '010200000',
            'item_code2': None,
            'item_code3': None,
            'name': '국고채 3년',
            'unit': 'percent',
            'frequency': 'D'
        },
        'treasury_10y': {
            'stat_code': '817Y002',
            'item_code1': '010210000',
            'item_code2': None,
            'item_code3': None,
            'name': '국고채 10년',
            'unit': 'percent',
            'frequency': 'D'
        },

        # Money Supply (통화)
        'm1': {
            'stat_code': '101Y002',
            'item_code1': 'BBFA00',
            'item_code2': None,
            'item_code3': None,
            'name': 'M1 통화량',
            'unit': '억원',
            'frequency': 'M'  # Monthly
        },
        'm2': {
            'stat_code': '101Y003',
            'item_code1': 'BBGA00',
            'item_code2': None,
            'item_code3': None,
            'name': 'M2 통화량',
            'unit': '억원',
            'frequency': 'M'
        },
        'lf': {
            'stat_code': '101Y004',
            'item_code1': 'BBHA00',
            'item_code2': None,
            'item_code3': None,
            'name': 'Lf 통화량 (광의유동성)',
            'unit': '억원',
            'frequency': 'M'
        },

        # GDP (경제성장)
        'gdp_growth': {
            'stat_code': '200Y002',
            'item_code1': '10101',
            'item_code2': None,
            'item_code3': None,
            'name': 'GDP 성장률 (전기대비)',
            'unit': 'percent',
            'frequency': 'Q'  # Quarterly
        },
        'gdp_annual_growth': {
            'stat_code': '200Y002',
            'item_code1': '10201',
            'item_code2': None,
            'item_code3': None,
            'name': 'GDP 성장률 (전년동기대비)',
            'unit': 'percent',
            'frequency': 'Q'
        },

        # Inflation (물가)
        'cpi': {
            'stat_code': '901Y009',
            'item_code1': '0',
            'item_code2': None,
            'item_code3': None,
            'name': '소비자물가지수',
            'unit': 'index',
            'frequency': 'M'
        },
        'cpi_core': {
            'stat_code': '901Y009',
            'item_code1': 'C',
            'item_code2': None,
            'item_code3': None,
            'name': '근원 소비자물가지수',
            'unit': 'index',
            'frequency': 'M'
        },
        'ppi': {
            'stat_code': '404Y014',
            'item_code1': '*AA',
            'item_code2': None,
            'item_code3': None,
            'name': '생산자물가지수',
            'unit': 'index',
            'frequency': 'M'
        },

        # Employment (고용)
        'unemployment_rate': {
            'stat_code': '901Y027',
            'item_code1': 'I41C',
            'item_code2': None,
            'item_code3': None,
            'name': '실업률',
            'unit': 'percent',
            'frequency': 'M'
        },
        'employment_rate': {
            'stat_code': '901Y027',
            'item_code1': 'I41B',
            'item_code2': None,
            'item_code3': None,
            'name': '고용률',
            'unit': 'percent',
            'frequency': 'M'
        },

        # Trade (무역)
        'export': {
            'stat_code': '403Y003',
            'item_code1': '*AA',
            'item_code2': None,
            'item_code3': None,
            'name': '수출액 (통관기준)',
            'unit': '백만달러',
            'frequency': 'M'
        },
        'import': {
            'stat_code': '403Y003',
            'item_code1': '*AB',
            'item_code2': None,
            'item_code3': None,
            'name': '수입액 (통관기준)',
            'unit': '백만달러',
            'frequency': 'M'
        },
        'trade_balance': {
            'stat_code': '403Y003',
            'item_code1': '*AC',
            'item_code2': None,
            'item_code3': None,
            'name': '무역수지',
            'unit': '백만달러',
            'frequency': 'M'
        },

        # Exchange Rate (환율)
        'usd_krw': {
            'stat_code': '731Y001',
            'item_code1': '0000001',
            'item_code2': None,
            'item_code3': None,
            'name': '원/달러 환율',
            'unit': 'KRW/USD',
            'frequency': 'D'
        },
        'eur_krw': {
            'stat_code': '731Y001',
            'item_code1': '0000003',
            'item_code2': None,
            'item_code3': None,
            'name': '원/유로 환율',
            'unit': 'KRW/EUR',
            'frequency': 'D'
        },
        'jpy_krw': {
            'stat_code': '731Y001',
            'item_code1': '0000002',
            'item_code2': None,
            'item_code3': None,
            'name': '원/100엔 환율',
            'unit': 'KRW/100JPY',
            'frequency': 'D'
        },

        # Business Survey Index (기업경기실사지수)
        'bsi_manufacturing': {
            'stat_code': '512Y007',
            'item_code1': 'BBMA',
            'item_code2': None,
            'item_code3': None,
            'name': 'BSI 제조업 업황 실적',
            'unit': 'index',
            'frequency': 'M'
        },
        'csi': {
            'stat_code': '511Y002',
            'item_code1': '99990',
            'item_code2': None,
            'item_code3': None,
            'name': '소비자심리지수 (CSI)',
            'unit': 'index',
            'frequency': 'M'
        }
    }

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize ECOS collector

        Args:
            api_key: ECOS API key (defaults to settings.ECOS_API_KEY)
        """
        super().__init__(api_key or settings.ECOS_API_KEY)
        self.base_url = settings.ECOS_BASE_URL

        if not self.api_key:
            self.log_warning("ECOS API key not configured")

    async def collect(self,
                     indicator: str = None,
                     stat_code: str = None,
                     item_code1: str = None,
                     start_date: str = None,
                     end_date: str = None,
                     frequency: str = 'M',
                     **kwargs) -> Dict[str, Any]:
        """
        Collect data from ECOS API

        Args:
            indicator: Indicator name from INDICATORS dict
            stat_code: ECOS stat code (if not using indicator)
            item_code1: Item code 1
            start_date: Start date (YYYYMM or YYYYMMDD)
            end_date: End date (YYYYMM or YYYYMMDD)
            frequency: D (daily), M (monthly), Q (quarterly), A (annual)

        Returns:
            Dict containing time series data

        Raises:
            CollectionError: If collection fails
        """
        if not self.api_key:
            raise CollectionError("ECOS API key not configured", source="ECOS")

        # Determine stat code and item codes
        indicator_info = None
        if indicator:
            if indicator not in self.INDICATORS:
                raise CollectionError(
                    f"Unknown indicator: {indicator}. "
                    f"Available: {', '.join(self.INDICATORS.keys())}",
                    source="ECOS"
                )
            indicator_info = self.INDICATORS[indicator]
            stat_code = indicator_info['stat_code']
            item_code1 = indicator_info['item_code1']
            frequency = indicator_info.get('frequency', frequency)

        if not stat_code or not item_code1:
            raise CollectionError(
                "Must provide either 'indicator' or 'stat_code' + 'item_code1'",
                source="ECOS"
            )

        # Set date range
        if not end_date:
            end_date = datetime.now().strftime('%Y%m')
        if not start_date:
            # Default to 5 years ago for monthly/quarterly, 1 year for daily
            if frequency == 'D':
                start_date = (datetime.now() - timedelta(days=365)).strftime('%Y%m%d')
                if len(end_date) == 6:  # Convert to YYYYMMDD if YYYYMM
                    end_date = end_date + '31'
            else:
                start_date = (datetime.now() - timedelta(days=365*5)).strftime('%Y%m')

        # Build URL
        url_parts = [
            self.base_url,
            self.api_key,
            'json',
            'kr',
            '1',
            '10000',  # Max count
            stat_code,
            frequency,
            start_date,
            end_date,
            item_code1
        ]

        # Add optional item codes
        if indicator_info:
            if indicator_info.get('item_code2'):
                url_parts.append(indicator_info['item_code2'])
            if indicator_info.get('item_code3'):
                url_parts.append(indicator_info['item_code3'])

        url = '/'.join(str(p) for p in url_parts)

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=30)) as response:
                    if response.status != 200:
                        raise CollectionError(
                            f"ECOS API returned status {response.status}",
                            source="ECOS"
                        )

                    data = await response.json()

                    # Check for API errors
                    if 'RESULT' in data:
                        error_msg = data['RESULT'].get('MESSAGE', 'Unknown error')
                        raise CollectionError(
                            f"ECOS API error: {error_msg}",
                            source="ECOS",
                            details={'stat_code': stat_code, 'item_code1': item_code1}
                        )

                    if 'StatisticSearch' not in data:
                        raise CollectionError(
                            "No data returned from ECOS API",
                            source="ECOS",
                            details={'stat_code': stat_code}
                        )

                    rows = data['StatisticSearch']['row']

                    # Parse data points
                    data_points = []
                    for row in rows:
                        try:
                            value = float(row['DATA_VALUE'])
                            time_str = row['TIME']

                            # Format date based on frequency
                            if frequency == 'D' and len(time_str) == 8:
                                date = f"{time_str[:4]}-{time_str[4:6]}-{time_str[6:8]}"
                            elif frequency in ['M', 'Q'] and len(time_str) == 6:
                                date = f"{time_str[:4]}-{time_str[4:6]}"
                            elif frequency == 'A' and len(time_str) == 4:
                                date = f"{time_str}"
                            else:
                                date = time_str

                            data_points.append({
                                'date': date,
                                'value': value
                            })
                        except (ValueError, KeyError) as e:
                            self.log_warning(f"Failed to parse row: {e}", row=row)
                            continue

                    result = {
                        'indicator': indicator,
                        'stat_code': stat_code,
                        'item_code1': item_code1,
                        'frequency': frequency,
                        'start_date': start_date,
                        'end_date': end_date,
                        'data_points': data_points,
                        'count': len(data_points)
                    }

                    # Add metadata if available
                    if rows and len(rows) > 0:
                        result['metadata'] = {
                            'stat_name': rows[0].get('STAT_NAME', ''),
                            'item_name': rows[0].get('ITEM_NAME1', ''),
                            'unit_name': rows[0].get('UNIT_NAME', '')
                        }

                    if indicator_info:
                        result['indicator_info'] = indicator_info

                    self.log_info(
                        f"Collected {len(data_points)} data points from ECOS",
                        indicator=indicator,
                        stat_code=stat_code
                    )

                    return result

        except aiohttp.ClientError as e:
            raise CollectionError(
                f"HTTP error fetching ECOS data: {str(e)}",
                source="ECOS",
                details={'stat_code': stat_code}
            )
        except Exception as e:
            raise CollectionError(
                f"Failed to fetch ECOS data: {str(e)}",
                source="ECOS",
                details={'stat_code': stat_code, 'indicator': indicator}
            )

    async def get_latest_value(self, indicator: str) -> Dict[str, Any]:
        """
        Get latest value for a specific indicator

        Args:
            indicator: Indicator name

        Returns:
            Dict with latest value and date
        """
        data = await self.collect(indicator=indicator)

        if not data['data_points']:
            return {
                'indicator': indicator,
                'value': None,
                'date': None,
                'error': 'No data available'
            }

        latest = data['data_points'][-1]

        return {
            'indicator': indicator,
            'stat_code': data['stat_code'],
            'value': latest['value'],
            'date': latest['date'],
            'metadata': data.get('metadata', {}),
            'unit': data.get('indicator_info', {}).get('unit', '')
        }

    async def collect_multiple(self,
                               indicators: List[str],
                               start_date: str = None,
                               end_date: str = None) -> Dict[str, Any]:
        """
        Collect multiple indicators at once

        Args:
            indicators: List of indicator names
            start_date: Start date
            end_date: End date

        Returns:
            Dict with results for each indicator
        """
        results = {}

        for indicator in indicators:
            try:
                data = await self.collect(
                    indicator=indicator,
                    start_date=start_date,
                    end_date=end_date
                )
                results[indicator] = data
            except CollectionError as e:
                self.log_error(f"Failed to collect {indicator}: {str(e)}")
                results[indicator] = {'error': str(e)}

        return {
            'indicators': results,
            'total': len(indicators),
            'successful': sum(1 for r in results.values() if 'error' not in r),
            'failed': sum(1 for r in results.values() if 'error' in r)
        }

    async def get_economic_snapshot(self) -> Dict[str, Any]:
        """
        Get snapshot of key Korean economic indicators

        Returns:
            Dict with current economic indicators
        """
        key_indicators = [
            'base_rate',
            'usd_krw',
            'cpi',
            'unemployment_rate',
            'export',
            'import'
        ]

        snapshot = {}
        for indicator in key_indicators:
            try:
                latest = await self.get_latest_value(indicator)
                snapshot[indicator] = latest
            except Exception as e:
                self.log_error(f"Failed to get {indicator}: {str(e)}")
                snapshot[indicator] = {'error': str(e)}

        return {
            'snapshot': snapshot,
            'timestamp': datetime.now().isoformat()
        }

    def validate_data(self, data: Dict) -> bool:
        """
        Validate collected data

        Args:
            data: Data to validate

        Returns:
            True if valid, False otherwise
        """
        # Check required fields
        required_fields = ['stat_code', 'data_points']
        if not all(field in data for field in required_fields):
            return False

        # Check data points structure
        if not isinstance(data['data_points'], list):
            return False

        # Check at least one data point exists
        if len(data['data_points']) == 0:
            return False

        # Validate data point structure
        for point in data['data_points'][:5]:  # Check first 5
            if not isinstance(point, dict):
                return False
            if 'date' not in point or 'value' not in point:
                return False
            if not isinstance(point['value'], (int, float)):
                return False

        return True


# Convenience function
async def get_ecos_indicator(indicator: str,
                             start_date: str = None,
                             end_date: str = None) -> Dict[str, Any]:
    """
    Quick function to get ECOS indicator data

    Args:
        indicator: Indicator name from EcosCollector.INDICATORS
        start_date: Start date (YYYYMM)
        end_date: End date (YYYYMM)

    Returns:
        Dict with indicator data
    """
    collector = EcosCollector()
    return await collector.safe_collect(
        indicator=indicator,
        start_date=start_date,
        end_date=end_date
    )
