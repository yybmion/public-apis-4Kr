"""
KIS (한국투자증권) API Collector
Stock Intelligence System
"""

import requests
import aiohttp
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
import hashlib
import json

from app.collectors.base import BaseCollector, CollectionError
from app.config import settings


class KISCollector(BaseCollector):
    """
    한국투자증권 KIS Developers API 데이터 수집기

    Features:
    - OAuth 2.0 토큰 관리
    - 실시간 주식 시세 조회
    - 일봉 데이터 조회
    - 종목 기본 정보 조회
    """

    def __init__(self, app_key: Optional[str] = None, app_secret: Optional[str] = None):
        """
        Initialize KIS collector

        Args:
            app_key: KIS API App Key (defaults to settings)
            app_secret: KIS API App Secret (defaults to settings)
        """
        super().__init__()
        self.app_key = app_key or settings.KIS_APP_KEY
        self.app_secret = app_secret or settings.KIS_APP_SECRET
        self.base_url = settings.KIS_BASE_URL
        self.access_token = None
        self.token_expires_at = None

    async def get_access_token(self) -> str:
        """
        Get OAuth 2.0 access token

        Returns:
            Access token string

        Raises:
            CollectionError: If token request fails
        """
        # Check if we have a valid token
        if self.access_token and self.token_expires_at:
            if datetime.now() < self.token_expires_at:
                return self.access_token

        # Request new token
        url = f"{self.base_url}/oauth2/tokenP"
        data = {
            "grant_type": "client_credentials",
            "appkey": self.app_key,
            "appsecret": self.app_secret
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=data) as response:
                    if response.status != 200:
                        raise CollectionError(
                            f"Token request failed with status {response.status}",
                            source="KIS_API"
                        )

                    result = await response.json()
                    self.access_token = result['access_token']
                    # Token expires in 24 hours, refresh 1 hour before
                    self.token_expires_at = datetime.now() + timedelta(hours=23)

                    self.log_info("Access token obtained successfully")
                    return self.access_token

        except Exception as e:
            raise CollectionError(f"Failed to get access token: {str(e)}", source="KIS_API")

    async def collect(self, stock_code: str, **kwargs) -> Dict[str, Any]:
        """
        Collect real-time stock price data

        Args:
            stock_code: 종목코드 (예: '005930')
            **kwargs: Additional parameters

        Returns:
            Dict containing stock price data

        Raises:
            CollectionError: If collection fails
        """
        # Ensure we have a valid token
        token = await self.get_access_token()

        url = f"{self.base_url}/uapi/domestic-stock/v1/quotations/inquire-price"

        headers = {
            "content-type": "application/json; charset=utf-8",
            "authorization": f"Bearer {token}",
            "appkey": self.app_key,
            "appsecret": self.app_secret,
            "tr_id": "FHKST01010100"  # 국내주식 현재가 시세
        }

        params = {
            "FID_COND_MRKT_DIV_CODE": "J",  # 시장 구분 (J: 주식)
            "FID_INPUT_ISCD": stock_code
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers, params=params) as response:
                    if response.status != 200:
                        raise CollectionError(
                            f"API request failed with status {response.status}",
                            source="KIS_API",
                            details={"stock_code": stock_code}
                        )

                    result = await response.json()

                    if result['rt_cd'] != '0':
                        raise CollectionError(
                            f"API returned error: {result.get('msg1', 'Unknown error')}",
                            source="KIS_API",
                            details={"stock_code": stock_code}
                        )

                    output = result['output']

                    # Normalize data
                    normalized = {
                        'code': stock_code,
                        'name': output.get('hts_kor_isnm', ''),
                        'current_price': int(output.get('stck_prpr', 0)),
                        'open': int(output.get('stck_oprc', 0)),
                        'high': int(output.get('stck_hgpr', 0)),
                        'low': int(output.get('stck_lwpr', 0)),
                        'volume': int(output.get('acml_vol', 0)),
                        'trading_value': int(output.get('acml_tr_pbmn', 0)),
                        'change_rate': float(output.get('prdy_ctrt', 0)),
                        'market_cap': int(output.get('hts_avls', 0)) if output.get('hts_avls') else None,
                        'per': float(output.get('per', 0)) if output.get('per') else None,
                        'date': datetime.now().date().isoformat()
                    }

                    return normalized

        except aiohttp.ClientError as e:
            raise CollectionError(
                f"HTTP request failed: {str(e)}",
                source="KIS_API",
                details={"stock_code": stock_code}
            )
        except Exception as e:
            raise CollectionError(
                f"Unexpected error: {str(e)}",
                source="KIS_API",
                details={"stock_code": stock_code}
            )

    async def collect_daily_ohlcv(
        self,
        stock_code: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        period: str = "D"
    ) -> Dict[str, Any]:
        """
        Collect daily OHLCV data

        Args:
            stock_code: 종목코드
            start_date: 시작일 (YYYYMMDD)
            end_date: 종료일 (YYYYMMDD)
            period: 기간 구분 (D: 일, W: 주, M: 월)

        Returns:
            Dict containing daily OHLCV data
        """
        token = await self.get_access_token()

        url = f"{self.base_url}/uapi/domestic-stock/v1/quotations/inquire-daily-price"

        headers = {
            "content-type": "application/json; charset=utf-8",
            "authorization": f"Bearer {token}",
            "appkey": self.app_key,
            "appsecret": self.app_secret,
            "tr_id": "FHKST01010400"  # 국내주식 기간별시세(일/주/월/년)
        }

        # Default to last 30 days if not specified
        if not end_date:
            end_date = datetime.now().strftime("%Y%m%d")
        if not start_date:
            start_date = (datetime.now() - timedelta(days=30)).strftime("%Y%m%d")

        params = {
            "FID_COND_MRKT_DIV_CODE": "J",
            "FID_INPUT_ISCD": stock_code,
            "FID_PERIOD_DIV_CODE": period,
            "FID_ORG_ADJ_PRC": "0",  # 수정주가 여부 (0: 미사용)
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers, params=params) as response:
                    if response.status != 200:
                        raise CollectionError(
                            f"Daily OHLCV request failed with status {response.status}",
                            source="KIS_API"
                        )

                    result = await response.json()

                    if result['rt_cd'] != '0':
                        raise CollectionError(
                            f"API returned error: {result.get('msg1', 'Unknown error')}",
                            source="KIS_API"
                        )

                    # Parse output
                    output_list = result.get('output', [])
                    daily_data = []

                    for item in output_list:
                        daily_data.append({
                            'date': item.get('stck_bsop_date', ''),
                            'open': int(item.get('stck_oprc', 0)),
                            'high': int(item.get('stck_hgpr', 0)),
                            'low': int(item.get('stck_lwpr', 0)),
                            'close': int(item.get('stck_clpr', 0)),
                            'volume': int(item.get('acml_vol', 0)),
                            'trading_value': int(item.get('acml_tr_pbmn', 0)),
                        })

                    return {
                        'stock_code': stock_code,
                        'period': period,
                        'data': daily_data
                    }

        except Exception as e:
            raise CollectionError(
                f"Failed to collect daily OHLCV: {str(e)}",
                source="KIS_API",
                details={"stock_code": stock_code}
            )

    def validate_data(self, data: Dict) -> bool:
        """
        Validate collected data

        Args:
            data: Data to validate

        Returns:
            True if valid, False otherwise
        """
        required_fields = ['code', 'name', 'current_price', 'volume']

        # Check all required fields exist
        if not all(field in data for field in required_fields):
            return False

        # Check price and volume are positive
        if data.get('current_price', 0) <= 0:
            return False

        if data.get('volume', 0) < 0:
            return False

        # Check code format (should be 6 digits)
        if not data.get('code', '').isdigit() or len(data.get('code', '')) != 6:
            return False

        return True
