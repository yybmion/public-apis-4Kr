"""
FRED (Federal Reserve Economic Data) API Collector
Stock Intelligence System

FRED provides 800,000+ economic time series data from 108 sources.
API Documentation: https://fred.stlouisfed.org/docs/api/

Required package: pip install fredapi
"""

import asyncio
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import pandas as pd

from app.collectors.base import BaseCollector, CollectionError
from app.config import settings


class FredCollector(BaseCollector):
    """
    FRED (Federal Reserve Economic Data) API Collector

    Collects US macroeconomic indicators from FRED database.

    Features:
    - 800,000+ economic time series
    - Official Federal Reserve data
    - Free API with rate limit: 120 requests/minute

    Required:
    - FRED_API_KEY environment variable
    """

    # Major Economic Indicators
    # Categories: Interest Rates, Employment, Inflation, GDP, Housing, Financial
    INDICATORS = {
        # Interest Rates
        'federal_funds_rate': {
            'series_id': 'FEDFUNDS',
            'name': '연방기금금리 (Federal Funds Rate)',
            'category': 'interest_rates',
            'unit': 'percent',
            'frequency': 'monthly'
        },
        'treasury_10y': {
            'series_id': 'DGS10',
            'name': '10년 국채금리 (10-Year Treasury)',
            'category': 'interest_rates',
            'unit': 'percent',
            'frequency': 'daily'
        },
        'treasury_2y': {
            'series_id': 'DGS2',
            'name': '2년 국채금리 (2-Year Treasury)',
            'category': 'interest_rates',
            'unit': 'percent',
            'frequency': 'daily'
        },
        'treasury_3m': {
            'series_id': 'DTB3',
            'name': '3개월 국채금리 (3-Month Treasury)',
            'category': 'interest_rates',
            'unit': 'percent',
            'frequency': 'daily'
        },

        # Employment
        'unemployment_rate': {
            'series_id': 'UNRATE',
            'name': '실업률 (Unemployment Rate)',
            'category': 'employment',
            'unit': 'percent',
            'frequency': 'monthly'
        },
        'nonfarm_payrolls': {
            'series_id': 'PAYEMS',
            'name': '비농업 고용 (Nonfarm Payrolls)',
            'category': 'employment',
            'unit': 'thousands',
            'frequency': 'monthly'
        },
        'initial_claims': {
            'series_id': 'ICSA',
            'name': '신규 실업수당 청구 (Initial Claims)',
            'category': 'employment',
            'unit': 'thousands',
            'frequency': 'weekly'
        },

        # Inflation
        'cpi': {
            'series_id': 'CPIAUCSL',
            'name': '소비자물가지수 (CPI)',
            'category': 'inflation',
            'unit': 'index',
            'frequency': 'monthly'
        },
        'core_cpi': {
            'series_id': 'CPILFESL',
            'name': '근원 CPI (Core CPI)',
            'category': 'inflation',
            'unit': 'index',
            'frequency': 'monthly'
        },
        'pce': {
            'series_id': 'PCE',
            'name': '개인소비지출 (PCE)',
            'category': 'inflation',
            'unit': 'billions',
            'frequency': 'monthly'
        },
        'core_pce': {
            'series_id': 'PCEPILFE',
            'name': '근원 PCE (Core PCE)',
            'category': 'inflation',
            'unit': 'index',
            'frequency': 'monthly'
        },

        # GDP and Economic Growth
        'gdp': {
            'series_id': 'GDP',
            'name': 'GDP',
            'category': 'gdp',
            'unit': 'billions',
            'frequency': 'quarterly'
        },
        'gdp_growth': {
            'series_id': 'A191RL1Q225SBEA',
            'name': 'GDP 성장률 (GDP Growth Rate)',
            'category': 'gdp',
            'unit': 'percent',
            'frequency': 'quarterly'
        },
        'industrial_production': {
            'series_id': 'INDPRO',
            'name': '산업생산지수 (Industrial Production)',
            'category': 'gdp',
            'unit': 'index',
            'frequency': 'monthly'
        },
        'retail_sales': {
            'series_id': 'RSXFS',
            'name': '소매판매 (Retail Sales)',
            'category': 'gdp',
            'unit': 'millions',
            'frequency': 'monthly'
        },

        # Housing
        'housing_starts': {
            'series_id': 'HOUST',
            'name': '주택착공 (Housing Starts)',
            'category': 'housing',
            'unit': 'thousands',
            'frequency': 'monthly'
        },
        'existing_home_sales': {
            'series_id': 'EXHOSLUSM495S',
            'name': '기존주택판매 (Existing Home Sales)',
            'category': 'housing',
            'unit': 'millions',
            'frequency': 'monthly'
        },
        'case_shiller': {
            'series_id': 'CSUSHPISA',
            'name': 'Case-Shiller 주택가격지수',
            'category': 'housing',
            'unit': 'index',
            'frequency': 'monthly'
        },

        # Financial Markets
        'sp500': {
            'series_id': 'SP500',
            'name': 'S&P 500',
            'category': 'financial',
            'unit': 'index',
            'frequency': 'daily'
        },
        'vix': {
            'series_id': 'VIXCLS',
            'name': 'VIX 변동성지수 (VIX)',
            'category': 'financial',
            'unit': 'index',
            'frequency': 'daily'
        },
        'm2': {
            'series_id': 'M2SL',
            'name': 'M2 통화량 (M2 Money Supply)',
            'category': 'financial',
            'unit': 'billions',
            'frequency': 'weekly'
        },

        # Consumer Confidence
        'consumer_sentiment': {
            'series_id': 'UMCSENT',
            'name': '소비자심리지수 (Consumer Sentiment)',
            'category': 'sentiment',
            'unit': 'index',
            'frequency': 'monthly'
        }
    }

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize FRED collector

        Args:
            api_key: FRED API key (defaults to settings.FRED_API_KEY)
        """
        super().__init__(api_key or settings.FRED_API_KEY)
        self.fred_client = None

        if not self.api_key:
            self.log_warning("FRED API key not configured")

    def _init_fred_client(self):
        """Initialize FRED API client"""
        if self.fred_client is None:
            try:
                from fredapi import Fred
                self.fred_client = Fred(api_key=self.api_key)
                self.log_info("FRED API client initialized")
            except ImportError:
                raise CollectionError(
                    "fredapi library not installed. Install with: pip install fredapi",
                    source="FRED"
                )
            except Exception as e:
                raise CollectionError(
                    f"Failed to initialize FRED client: {str(e)}",
                    source="FRED"
                )

    async def collect(self,
                     indicator: str = None,
                     series_id: str = None,
                     start_date: str = None,
                     end_date: str = None,
                     **kwargs) -> Dict[str, Any]:
        """
        Collect data from FRED API

        Args:
            indicator: Indicator name from INDICATORS dict
            series_id: FRED series ID (if not using indicator)
            start_date: Start date (YYYY-MM-DD) - defaults to 5 years ago
            end_date: End date (YYYY-MM-DD) - defaults to today

        Returns:
            Dict containing time series data

        Raises:
            CollectionError: If collection fails
        """
        if not self.api_key:
            raise CollectionError("FRED API key not configured", source="FRED")

        # Initialize client
        self._init_fred_client()

        # Determine series ID
        if indicator:
            if indicator not in self.INDICATORS:
                raise CollectionError(
                    f"Unknown indicator: {indicator}. "
                    f"Available: {', '.join(self.INDICATORS.keys())}",
                    source="FRED"
                )
            series_info = self.INDICATORS[indicator]
            series_id = series_info['series_id']
        elif not series_id:
            raise CollectionError(
                "Must provide either 'indicator' or 'series_id'",
                source="FRED"
            )

        # Set date range (default: last 5 years)
        if not end_date:
            end_date = datetime.now().strftime('%Y-%m-%d')
        if not start_date:
            start_date = (datetime.now() - timedelta(days=365*5)).strftime('%Y-%m-%d')

        try:
            # Fetch data (fredapi is synchronous, so we run in executor)
            loop = asyncio.get_event_loop()
            series = await loop.run_in_executor(
                None,
                lambda: self.fred_client.get_series(
                    series_id,
                    observation_start=start_date,
                    observation_end=end_date
                )
            )

            if series is None or series.empty:
                raise CollectionError(
                    f"No data returned for series {series_id}",
                    source="FRED"
                )

            # Convert to dict format
            data_points = []
            for date, value in series.items():
                if pd.notna(value):  # Skip NaN values
                    data_points.append({
                        'date': date.strftime('%Y-%m-%d'),
                        'value': float(value)
                    })

            result = {
                'series_id': series_id,
                'indicator': indicator,
                'start_date': start_date,
                'end_date': end_date,
                'data_points': data_points,
                'count': len(data_points)
            }

            # Add indicator metadata if available
            if indicator and indicator in self.INDICATORS:
                result['metadata'] = self.INDICATORS[indicator]

            self.log_info(
                f"Collected {len(data_points)} data points for {series_id}",
                indicator=indicator,
                series_id=series_id
            )

            return result

        except Exception as e:
            raise CollectionError(
                f"Failed to fetch FRED data: {str(e)}",
                source="FRED",
                details={'series_id': series_id, 'indicator': indicator}
            )

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

    async def get_yield_curve(self) -> Dict[str, Any]:
        """
        Get current yield curve data (3M, 2Y, 10Y)

        Returns:
            Dict with yield curve data and spread analysis
        """
        self._init_fred_client()

        loop = asyncio.get_event_loop()

        # Fetch latest values for each maturity
        t3m = await loop.run_in_executor(
            None,
            lambda: self.fred_client.get_series_latest_release('DTB3')
        )
        t2y = await loop.run_in_executor(
            None,
            lambda: self.fred_client.get_series_latest_release('DGS2')
        )
        t10y = await loop.run_in_executor(
            None,
            lambda: self.fred_client.get_series_latest_release('DGS10')
        )

        # Get latest non-null values
        t3m_value = float(t3m.dropna().iloc[-1]) if not t3m.dropna().empty else None
        t2y_value = float(t2y.dropna().iloc[-1]) if not t2y.dropna().empty else None
        t10y_value = float(t10y.dropna().iloc[-1]) if not t10y.dropna().empty else None

        # Calculate spreads
        spread_10y_2y = None
        spread_10y_3m = None
        is_inverted = False

        if t10y_value is not None and t2y_value is not None:
            spread_10y_2y = round(t10y_value - t2y_value, 2)
            is_inverted = spread_10y_2y < 0

        if t10y_value is not None and t3m_value is not None:
            spread_10y_3m = round(t10y_value - t3m_value, 2)

        return {
            'yields': {
                'treasury_3m': t3m_value,
                'treasury_2y': t2y_value,
                'treasury_10y': t10y_value
            },
            'spreads': {
                '10y_2y': spread_10y_2y,
                '10y_3m': spread_10y_3m
            },
            'yield_curve_inverted': is_inverted,
            'recession_signal': is_inverted,  # Inverted yield curve = recession signal
            'date': datetime.now().strftime('%Y-%m-%d')
        }

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
            'series_id': data['series_id'],
            'value': latest['value'],
            'date': latest['date'],
            'metadata': data.get('metadata', {})
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
        required_fields = ['series_id', 'data_points']
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


# Convenience function for quick access
async def get_fred_indicator(indicator: str,
                             start_date: str = None,
                             end_date: str = None) -> Dict[str, Any]:
    """
    Quick function to get FRED indicator data

    Args:
        indicator: Indicator name from FredCollector.INDICATORS
        start_date: Start date (YYYY-MM-DD)
        end_date: End date (YYYY-MM-DD)

    Returns:
        Dict with indicator data
    """
    collector = FredCollector()
    return await collector.safe_collect(
        indicator=indicator,
        start_date=start_date,
        end_date=end_date
    )
