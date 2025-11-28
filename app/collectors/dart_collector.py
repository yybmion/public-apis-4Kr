"""
DART (전자공시시스템) API Collector
Stock Intelligence System
"""

import aiohttp
import xml.etree.ElementTree as ET
from typing import Dict, Any, Optional, List
from datetime import datetime

from app.collectors.base import BaseCollector, CollectionError
from app.config import settings


class DARTCollector(BaseCollector):
    """
    DART (Data Analysis, Retrieval and Transfer System) API 수집기

    Features:
    - 기업개황 조회
    - 재무제표 조회 (포괄손익계산서, 재무상태표)
    - 배당 정보 조회
    - 주요공시 조회
    """

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize DART collector

        Args:
            api_key: DART API Key (defaults to settings)
        """
        super().__init__(api_key)
        self.api_key = api_key or settings.DART_API_KEY
        self.base_url = settings.DART_BASE_URL

    async def collect(self, corp_code: str, **kwargs) -> Dict[str, Any]:
        """
        Collect company basic information

        Args:
            corp_code: 고유번호 (8자리)
            **kwargs: Additional parameters

        Returns:
            Dict containing company information
        """
        url = f"{self.base_url}/company.json"
        params = {
            "crtfc_key": self.api_key,
            "corp_code": corp_code
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    if response.status != 200:
                        raise CollectionError(
                            f"DART API request failed with status {response.status}",
                            source="DART_API"
                        )

                    result = await response.json()

                    if result.get('status') != '000':
                        raise CollectionError(
                            f"DART API error: {result.get('message', 'Unknown error')}",
                            source="DART_API"
                        )

                    return result

        except Exception as e:
            raise CollectionError(
                f"Failed to collect DART data: {str(e)}",
                source="DART_API",
                details={"corp_code": corp_code}
            )

    async def collect_financials(
        self,
        corp_code: str,
        bsns_year: str,
        reprt_code: str = "11011"
    ) -> Dict[str, Any]:
        """
        Collect financial statements

        Args:
            corp_code: 고유번호
            bsns_year: 사업연도 (YYYY)
            reprt_code: 보고서 코드
                - 11011: 사업보고서
                - 11012: 반기보고서
                - 11013: 1분기보고서
                - 11014: 3분기보고서

        Returns:
            Dict containing financial data
        """
        # 단일회사 전체 재무제표
        url = f"{self.base_url}/fnlttSinglAcntAll.json"
        params = {
            "crtfc_key": self.api_key,
            "corp_code": corp_code,
            "bsns_year": bsns_year,
            "reprt_code": reprt_code,
            "fs_div": "CFS"  # CFS: 연결재무제표, OFS: 개별재무제표
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    if response.status != 200:
                        raise CollectionError(
                            f"Financial data request failed with status {response.status}",
                            source="DART_API"
                        )

                    result = await response.json()

                    if result.get('status') != '000':
                        raise CollectionError(
                            f"DART API error: {result.get('message', 'Unknown error')}",
                            source="DART_API"
                        )

                    # Parse financial data
                    financial_data = self._parse_financials(result.get('list', []))

                    return {
                        'corp_code': corp_code,
                        'year': bsns_year,
                        'report_type': reprt_code,
                        'financials': financial_data
                    }

        except Exception as e:
            raise CollectionError(
                f"Failed to collect financial data: {str(e)}",
                source="DART_API",
                details={"corp_code": corp_code, "year": bsns_year}
            )

    def _parse_financials(self, data_list: List[Dict]) -> Dict[str, Any]:
        """
        Parse financial statement data

        Args:
            data_list: Raw financial data from DART

        Returns:
            Parsed financial metrics
        """
        financials = {
            'revenue': None,              # 매출액
            'operating_profit': None,     # 영업이익
            'net_income': None,           # 당기순이익
            'total_assets': None,         # 총자산
            'total_liabilities': None,    # 총부채
            'equity': None,               # 자본총계
        }

        # Account name mapping (Korean to key)
        account_mapping = {
            '매출액': 'revenue',
            '영업이익': 'operating_profit',
            '당기순이익': 'net_income',
            '자산총계': 'total_assets',
            '부채총계': 'total_liabilities',
            '자본총계': 'equity',
        }

        for item in data_list:
            account_nm = item.get('account_nm', '')

            for korean_name, key in account_mapping.items():
                if korean_name in account_nm:
                    # Get current period amount
                    amount_str = item.get('thstrm_amount', '0')
                    # Remove commas and convert to integer
                    amount = int(amount_str.replace(',', '')) if amount_str else 0
                    financials[key] = amount
                    break

        # Calculate financial ratios
        if financials['total_assets'] and financials['equity']:
            financials['debt_ratio'] = (
                (financials['total_liabilities'] / financials['equity']) * 100
                if financials['equity'] > 0 else None
            )

        if financials['equity'] and financials['net_income']:
            financials['roe'] = (
                (financials['net_income'] / financials['equity']) * 100
                if financials['equity'] > 0 else None
            )

        return financials

    async def collect_disclosures(
        self,
        corp_code: str,
        bgn_de: Optional[str] = None,
        end_de: Optional[str] = None,
        page_count: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Collect company disclosures

        Args:
            corp_code: 고유번호
            bgn_de: 시작일 (YYYYMMDD)
            end_de: 종료일 (YYYYMMDD)
            page_count: 페이지당 건수

        Returns:
            List of disclosure data
        """
        url = f"{self.base_url}/list.json"

        # Default to last 30 days
        if not end_de:
            end_de = datetime.now().strftime("%Y%m%d")
        if not bgn_de:
            from datetime import timedelta
            bgn_de = (datetime.now() - timedelta(days=30)).strftime("%Y%m%d")

        params = {
            "crtfc_key": self.api_key,
            "corp_code": corp_code,
            "bgn_de": bgn_de,
            "end_de": end_de,
            "page_count": page_count
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    if response.status != 200:
                        raise CollectionError(
                            f"Disclosure request failed with status {response.status}",
                            source="DART_API"
                        )

                    result = await response.json()

                    if result.get('status') != '000':
                        # No data is acceptable
                        if result.get('status') == '013':
                            return []

                        raise CollectionError(
                            f"DART API error: {result.get('message', 'Unknown error')}",
                            source="DART_API"
                        )

                    disclosures = result.get('list', [])

                    self.log_info(
                        f"Collected {len(disclosures)} disclosures for {corp_code}"
                    )

                    return disclosures

        except Exception as e:
            raise CollectionError(
                f"Failed to collect disclosures: {str(e)}",
                source="DART_API",
                details={"corp_code": corp_code}
            )

    async def get_corp_code(self, stock_code: str) -> Optional[str]:
        """
        Convert stock code to DART corp_code

        Note: This requires the CORPCODE.xml file from DART
        which contains mappings of stock codes to corp codes.

        Args:
            stock_code: 종목코드 (6자리)

        Returns:
            Corp code (8자리) or None if not found
        """
        # TODO: Implement corp code lookup
        # This requires downloading and parsing CORPCODE.xml from DART
        # For now, return None and log warning

        self.log_warning(
            f"Corp code lookup not implemented for stock code {stock_code}"
        )
        return None

    def validate_data(self, data: Dict) -> bool:
        """
        Validate collected data

        Args:
            data: Data to validate

        Returns:
            True if valid, False otherwise
        """
        # Basic validation - check if data exists and has status
        if not data:
            return False

        # For company data
        if 'corp_name' in data:
            return bool(data.get('corp_name'))

        # For financial data
        if 'financials' in data:
            financials = data.get('financials', {})
            # At least one financial metric should exist
            return any(financials.values())

        return True
