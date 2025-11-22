"""
SEC EDGAR API Collector

Collects official financial data from the U.S. Securities and Exchange Commission (SEC).

Official Documentation:
- https://www.sec.gov/edgar/sec-api-documentation
- https://www.sec.gov/developer

Data Sources:
- Company filings (10-K, 10-Q, 8-K, etc.)
- Financial facts (XBRL data)
- Company information

Rate Limit: 10 requests per second
Authentication: User-Agent header required (no API key)

Author: AI Assistant
Created: 2025-11-22
"""

import asyncio
import aiohttp
from typing import Dict, Any, List, Optional
from datetime import datetime
import time


class SECEdgarCollector:
    """
    SEC EDGAR API Collector

    Collects data from the U.S. Securities and Exchange Commission's EDGAR database.

    Features:
    - Company ticker to CIK lookup
    - Company filings retrieval (10-K, 10-Q, etc.)
    - Financial facts extraction (XBRL data)
    - No API key required (User-Agent only)

    Rate Limit: 10 requests per second (enforced automatically)
    """

    BASE_URL = "https://data.sec.gov"
    COMPANY_TICKERS_URL = "https://www.sec.gov/files/company_tickers.json"

    # User-Agent is REQUIRED by SEC
    # Format: Name Email
    USER_AGENT = "Stock-Intelligence-System support@example.com"

    def __init__(self, user_agent: Optional[str] = None):
        """
        Initialize SEC EDGAR Collector

        Args:
            user_agent: Custom User-Agent string (Name Email format required by SEC)
                       If not provided, uses default.
        """
        self.user_agent = user_agent or self.USER_AGENT
        self.last_request_time = 0
        self.min_request_interval = 0.1  # 10 requests per second = 0.1s interval

        # Cache for company tickers
        self._company_tickers_cache: Optional[Dict] = None
        self._cache_timestamp: Optional[float] = None
        self._cache_ttl = 86400  # 24 hours

    async def _rate_limit(self):
        """Enforce rate limit of 10 requests per second"""
        current_time = time.time()
        time_since_last_request = current_time - self.last_request_time

        if time_since_last_request < self.min_request_interval:
            await asyncio.sleep(self.min_request_interval - time_since_last_request)

        self.last_request_time = time.time()

    async def _make_request(
        self,
        url: str,
        headers: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Make HTTP request to SEC API with rate limiting

        Args:
            url: API endpoint URL
            headers: Optional additional headers

        Returns:
            API response as dictionary
        """
        await self._rate_limit()

        default_headers = {
            "User-Agent": self.user_agent,
            "Accept": "application/json"
        }

        if headers:
            default_headers.update(headers)

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    url,
                    headers=default_headers,
                    timeout=30
                ) as response:
                    response.raise_for_status()
                    data = await response.json()

                    return {
                        'success': True,
                        'data': data,
                        'source': 'SEC_EDGAR',
                        'url': url,
                        'timestamp': datetime.now().isoformat()
                    }

        except aiohttp.ClientError as e:
            return {
                'success': False,
                'error': str(e),
                'error_type': 'network_error',
                'source': 'SEC_EDGAR',
                'url': url,
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'error_type': 'unknown_error',
                'source': 'SEC_EDGAR',
                'url': url,
                'timestamp': datetime.now().isoformat()
            }

    async def get_company_tickers(self, force_refresh: bool = False) -> Dict[str, Any]:
        """
        Get mapping of all company tickers to CIK numbers

        CIK (Central Index Key) is SEC's unique identifier for companies.
        This endpoint provides ticker -> CIK mapping for all companies.

        Args:
            force_refresh: Force refresh cache even if not expired

        Returns:
            Dictionary with ticker -> company info mapping

        Example:
            {
                "0": {
                    "cik_str": 320193,
                    "ticker": "AAPL",
                    "title": "Apple Inc."
                },
                ...
            }
        """
        # Check cache
        current_time = time.time()
        if (not force_refresh and
            self._company_tickers_cache and
            self._cache_timestamp and
            (current_time - self._cache_timestamp) < self._cache_ttl):

            return {
                'success': True,
                'data': self._company_tickers_cache,
                'source': 'SEC_EDGAR',
                'cached': True,
                'timestamp': datetime.now().isoformat()
            }

        # Fetch fresh data
        result = await self._make_request(self.COMPANY_TICKERS_URL)

        if result['success']:
            self._company_tickers_cache = result['data']
            self._cache_timestamp = current_time

        return result

    async def ticker_to_cik(self, ticker: str) -> Optional[str]:
        """
        Convert stock ticker to CIK number

        Args:
            ticker: Stock ticker symbol (e.g., 'AAPL', 'TSLA')

        Returns:
            10-digit CIK string, or None if not found

        Example:
            'AAPL' -> '0000320193'
        """
        tickers_result = await self.get_company_tickers()

        if not tickers_result['success']:
            return None

        tickers_data = tickers_result['data']
        ticker_upper = ticker.upper()

        # Search through all companies
        for company in tickers_data.values():
            if company.get('ticker') == ticker_upper:
                cik = company.get('cik_str')
                # Pad to 10 digits
                return str(cik).zfill(10)

        return None

    async def get_company_submissions(
        self,
        cik: str
    ) -> Dict[str, Any]:
        """
        Get all SEC submissions for a company

        Args:
            cik: 10-digit CIK number (e.g., '0000320193' for Apple)

        Returns:
            Company information and list of all filings

        Example:
            {
                "name": "Apple Inc.",
                "filings": {
                    "recent": {
                        "accessionNumber": [...],
                        "filingDate": [...],
                        "form": ["10-K", "10-Q", ...]
                    }
                }
            }
        """
        # Ensure CIK is 10 digits
        cik_padded = str(cik).zfill(10)
        url = f"{self.BASE_URL}/submissions/CIK{cik_padded}.json"

        return await self._make_request(url)

    async def get_company_facts(
        self,
        cik: str
    ) -> Dict[str, Any]:
        """
        Get XBRL financial facts for a company

        This returns structured financial data (revenue, assets, etc.)
        from XBRL-formatted filings.

        Args:
            cik: 10-digit CIK number

        Returns:
            Company financial facts with historical data

        Example:
            {
                "facts": {
                    "us-gaap": {
                        "Revenue": {
                            "units": {
                                "USD": [
                                    {"end": "2023-09-30", "val": 383285000000, ...}
                                ]
                            }
                        }
                    }
                }
            }
        """
        cik_padded = str(cik).zfill(10)
        url = f"{self.BASE_URL}/api/xbrl/companyfacts/CIK{cik_padded}.json"

        return await self._make_request(url)

    async def get_filings_by_form(
        self,
        ticker: str,
        form_type: str = "10-K",
        limit: int = 10
    ) -> Dict[str, Any]:
        """
        Get specific form filings for a company by ticker

        Args:
            ticker: Stock ticker symbol (e.g., 'AAPL')
            form_type: Filing form type (e.g., '10-K', '10-Q', '8-K')
            limit: Maximum number of filings to return

        Returns:
            List of filings matching the form type

        Common Form Types:
            - 10-K: Annual report
            - 10-Q: Quarterly report
            - 8-K: Current report (material events)
            - DEF 14A: Proxy statement
            - 13F-HR: Institutional investment manager holdings
        """
        # Get CIK from ticker
        cik = await self.ticker_to_cik(ticker)

        if not cik:
            return {
                'success': False,
                'error': f'Ticker {ticker} not found',
                'error_type': 'ticker_not_found',
                'timestamp': datetime.now().isoformat()
            }

        # Get all submissions
        submissions_result = await self.get_company_submissions(cik)

        if not submissions_result['success']:
            return submissions_result

        submissions = submissions_result['data']
        recent_filings = submissions.get('filings', {}).get('recent', {})

        # Filter by form type
        filtered_filings = []

        if 'form' in recent_filings:
            forms = recent_filings['form']
            accession_numbers = recent_filings.get('accessionNumber', [])
            filing_dates = recent_filings.get('filingDate', [])
            primary_documents = recent_filings.get('primaryDocument', [])

            for i, form in enumerate(forms):
                if form == form_type:
                    filing = {
                        'form': form,
                        'filing_date': filing_dates[i] if i < len(filing_dates) else None,
                        'accession_number': accession_numbers[i] if i < len(accession_numbers) else None,
                        'primary_document': primary_documents[i] if i < len(primary_documents) else None,
                        'cik': cik
                    }

                    # Construct document URL
                    if filing['accession_number'] and filing['primary_document']:
                        acc_no_clean = filing['accession_number'].replace('-', '')
                        filing['document_url'] = (
                            f"https://www.sec.gov/Archives/edgar/data/"
                            f"{cik}/{acc_no_clean}/{filing['primary_document']}"
                        )

                    filtered_filings.append(filing)

                    if len(filtered_filings) >= limit:
                        break

        return {
            'success': True,
            'data': {
                'ticker': ticker,
                'cik': cik,
                'company_name': submissions.get('name'),
                'form_type': form_type,
                'filings': filtered_filings,
                'total_found': len(filtered_filings)
            },
            'source': 'SEC_EDGAR',
            'timestamp': datetime.now().isoformat()
        }

    async def get_latest_10k(self, ticker: str) -> Dict[str, Any]:
        """
        Get the latest 10-K (annual report) for a company

        Args:
            ticker: Stock ticker symbol

        Returns:
            Latest 10-K filing information
        """
        result = await self.get_filings_by_form(ticker, "10-K", limit=1)

        if result['success'] and result['data']['filings']:
            latest_filing = result['data']['filings'][0]
            result['data']['latest_filing'] = latest_filing

        return result

    async def get_latest_10q(self, ticker: str) -> Dict[str, Any]:
        """
        Get the latest 10-Q (quarterly report) for a company

        Args:
            ticker: Stock ticker symbol

        Returns:
            Latest 10-Q filing information
        """
        result = await self.get_filings_by_form(ticker, "10-Q", limit=1)

        if result['success'] and result['data']['filings']:
            latest_filing = result['data']['filings'][0]
            result['data']['latest_filing'] = latest_filing

        return result

    def validate_data(self, data: Dict) -> bool:
        """
        Validate collected data

        Args:
            data: Data dictionary to validate

        Returns:
            True if valid, False otherwise
        """
        if not isinstance(data, dict):
            return False

        return data.get('success', False)


# Example usage
async def main():
    """Example usage of SEC EDGAR Collector"""
    collector = SECEdgarCollector()

    # Example 1: Get company tickers
    print("Fetching company tickers...")
    tickers = await collector.get_company_tickers()
    if tickers['success']:
        print(f"✓ Found {len(tickers['data'])} companies")

    # Example 2: Get Apple's latest 10-K
    print("\nFetching Apple's latest 10-K...")
    apple_10k = await collector.get_latest_10k("AAPL")
    if apple_10k['success']:
        filing = apple_10k['data']['latest_filing']
        print(f"✓ Latest 10-K: {filing['filing_date']}")
        print(f"  Document: {filing.get('document_url', 'N/A')}")

    # Example 3: Get Tesla's financial facts
    print("\nFetching Tesla's CIK...")
    tesla_cik = await collector.ticker_to_cik("TSLA")
    if tesla_cik:
        print(f"✓ Tesla CIK: {tesla_cik}")

        print("Fetching Tesla's financial facts...")
        facts = await collector.get_company_facts(tesla_cik)
        if facts['success']:
            print(f"✓ Financial facts retrieved")


if __name__ == "__main__":
    asyncio.run(main())
