#!/usr/bin/env python3
"""
SEC EDGAR API Collector Test Script

Tests the SEC EDGAR API collector for:
- Company ticker to CIK lookup
- Company submissions (filings)
- Financial facts (XBRL data)
- 10-K and 10-Q filings

No API key required - SEC EDGAR is a free public API!

Usage:
    python scripts/test_sec_edgar.py
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.collectors.sec_edgar_collector import SECEdgarCollector


def print_section(title: str):
    """Print a section header"""
    print(f"\n{'=' * 80}")
    print(f"  {title}")
    print(f"{'=' * 80}\n")


def print_success(message: str):
    """Print success message"""
    print(f"✅ {message}")


def print_error(message: str):
    """Print error message"""
    print(f"❌ {message}")


def print_warning(message: str):
    """Print warning message"""
    print(f"⚠️  {message}")


def print_data(label: str, value, indent: int = 1):
    """Print data in a formatted way"""
    indent_str = "   " * indent
    print(f"{indent_str}{label}: {value}")


async def test_ticker_to_cik():
    """Test ticker to CIK conversion"""
    print_section("TEST 1: Ticker to CIK Conversion")

    collector = SECEdgarCollector()

    test_tickers = ["AAPL", "TSLA", "MSFT", "GOOGL"]

    print("Testing ticker to CIK conversion for major tech companies...\n")

    results = {}
    for ticker in test_tickers:
        print(f"📊 Looking up CIK for {ticker}...")
        cik = await collector.ticker_to_cik(ticker)

        if cik:
            results[ticker] = cik
            print_success(f"{ticker} -> CIK: {cik}")
        else:
            print_error(f"Could not find CIK for {ticker}")

    print(f"\n✅ Successfully converted {len(results)}/{len(test_tickers)} tickers to CIK")

    return results


async def test_company_submissions(cik: str, ticker: str):
    """Test company submissions retrieval"""
    print_section(f"TEST 2: Company Submissions ({ticker})")

    collector = SECEdgarCollector()

    print(f"📡 Fetching SEC submissions for {ticker} (CIK: {cik})...")

    result = await collector.get_company_submissions(cik)

    if result.get('success'):
        data = result['data']
        print_success(f"Successfully retrieved submissions for {ticker}\n")

        # Company information
        print("🏢 Company Information:")
        print_data("Name", data.get('name'))
        print_data("CIK", data.get('cik'))
        print_data("SIC", data.get('sic'))
        print_data("SIC Description", data.get('sicDescription'))

        # Filing statistics
        if 'filings' in data and 'recent' in data['filings']:
            recent = data['filings']['recent']
            total_filings = len(recent.get('accessionNumber', []))

            print(f"\n📄 Filing Statistics:")
            print_data("Total Recent Filings", total_filings)

            # Count by form type
            if 'form' in recent:
                form_counts = {}
                for form in recent['form']:
                    form_counts[form] = form_counts.get(form, 0) + 1

                print_data("Form Types", len(form_counts))

                # Show top 5 form types
                top_forms = sorted(form_counts.items(), key=lambda x: x[1], reverse=True)[:5]
                print("\n   Top 5 Form Types:")
                for form, count in top_forms:
                    print_data(f"{form}", f"{count} filings", indent=2)

        return True
    else:
        print_error(f"Failed to retrieve submissions: {result.get('error')}")
        return False


async def test_company_facts(cik: str, ticker: str):
    """Test company financial facts retrieval"""
    print_section(f"TEST 3: Company Financial Facts ({ticker})")

    collector = SECEdgarCollector()

    print(f"📊 Fetching financial facts for {ticker} (CIK: {cik})...")

    result = await collector.get_company_facts(cik)

    if result.get('success'):
        data = result['data']
        print_success(f"Successfully retrieved financial facts for {ticker}\n")

        # Parse facts
        if 'facts' in data:
            facts = data['facts']

            print("📈 Financial Data Available:")

            # Count taxonomies
            print_data("Taxonomies", list(facts.keys()))

            # US-GAAP facts
            if 'us-gaap' in facts:
                us_gaap = facts['us-gaap']
                print_data("US-GAAP Concepts", len(us_gaap))

                # Show important concepts if available
                important_concepts = [
                    'Revenue', 'Revenues', 'RevenueFromContractWithCustomerExcludingAssessedTax',
                    'Assets', 'AssetsCurrent',
                    'Liabilities', 'LiabilitiesCurrent',
                    'NetIncomeLoss',
                    'EarningsPerShareBasic',
                    'StockholdersEquity'
                ]

                available_concepts = []
                for concept in important_concepts:
                    if concept in us_gaap:
                        available_concepts.append(concept)

                if available_concepts:
                    print("\n   Key Financial Concepts Available:")
                    for concept in available_concepts[:10]:  # Show first 10
                        # Get latest value
                        concept_data = us_gaap[concept]
                        if 'units' in concept_data:
                            for unit, values in concept_data['units'].items():
                                if values:
                                    latest = values[-1]
                                    value = latest.get('val', 'N/A')
                                    date = latest.get('end', 'N/A')
                                    print_data(concept, f"{value:,} {unit} (as of {date})", indent=2)
                                    break
                                break

        return True
    else:
        print_error(f"Failed to retrieve financial facts: {result.get('error')}")
        return False


async def test_10k_filing(ticker: str):
    """Test 10-K filing retrieval"""
    print_section(f"TEST 4: Latest 10-K Filing ({ticker})")

    collector = SECEdgarCollector()

    print(f"📄 Fetching latest 10-K (annual report) for {ticker}...")

    result = await collector.get_latest_10k(ticker)

    if result.get('success'):
        data = result['data']
        print_success(f"Successfully retrieved latest 10-K for {ticker}\n")

        print("📊 10-K Filing Information:")
        print_data("Company", data.get('company_name'))
        print_data("CIK", data.get('cik'))
        print_data("Total 10-K Filings Found", data.get('total_found'))

        if 'latest_filing' in data:
            filing = data['latest_filing']
            print("\n📄 Latest 10-K Details:")
            print_data("Filing Date", filing.get('filing_date'))
            print_data("Accession Number", filing.get('accession_number'))
            print_data("Primary Document", filing.get('primary_document'))

            if 'document_url' in filing:
                print_data("Document URL", filing['document_url'])
                print("\n   💡 You can download this document directly from the URL above")

        return True
    else:
        print_error(f"Failed to retrieve 10-K: {result.get('error')}")
        return False


async def test_10q_filing(ticker: str):
    """Test 10-Q filing retrieval"""
    print_section(f"TEST 5: Latest 10-Q Filing ({ticker})")

    collector = SECEdgarCollector()

    print(f"📄 Fetching latest 10-Q (quarterly report) for {ticker}...")

    result = await collector.get_latest_10q(ticker)

    if result.get('success'):
        data = result['data']
        print_success(f"Successfully retrieved latest 10-Q for {ticker}\n")

        print("📊 10-Q Filing Information:")
        print_data("Company", data.get('company_name'))
        print_data("Total 10-Q Filings Found", data.get('total_found'))

        if 'latest_filing' in data:
            filing = data['latest_filing']
            print("\n📄 Latest 10-Q Details:")
            print_data("Filing Date", filing.get('filing_date'))
            print_data("Accession Number", filing.get('accession_number'))
            print_data("Primary Document", filing.get('primary_document'))

            if 'document_url' in filing:
                print_data("Document URL", filing['document_url'])

        return True
    else:
        print_error(f"Failed to retrieve 10-Q: {result.get('error')}")
        return False


async def test_multiple_filings(ticker: str):
    """Test retrieving multiple filings"""
    print_section(f"TEST 6: Multiple Filings ({ticker})")

    collector = SECEdgarCollector()

    print(f"📄 Fetching last 5 10-K filings for {ticker}...")

    result = await collector.get_filings_by_form(ticker, "10-K", limit=5)

    if result.get('success'):
        data = result['data']
        filings = data.get('filings', [])

        print_success(f"Successfully retrieved {len(filings)} 10-K filings\n")

        print("📊 Recent 10-K Filings:")
        for i, filing in enumerate(filings, 1):
            print(f"\n   {i}. {filing.get('filing_date')}")
            print_data("Accession Number", filing.get('accession_number'), indent=2)
            print_data("Document", filing.get('primary_document'), indent=2)

        return True
    else:
        print_error(f"Failed to retrieve filings: {result.get('error')}")
        return False


async def main():
    """Main test runner"""
    print_section("SEC EDGAR API Collector Test Suite")
    print("This script tests the SEC EDGAR API collector functionality.\n")
    print("✓ No API key required - SEC EDGAR is free and public!")
    print("✓ Rate limited to 10 requests per second (enforced automatically)")
    print("✓ Data source: U.S. Securities and Exchange Commission\n")

    # Track test results
    results = {
        'ticker_to_cik': False,
        'submissions': False,
        'facts': False,
        '10k': False,
        '10q': False,
        'multiple_filings': False
    }

    # Test 1: Ticker to CIK conversion
    cik_mapping = await test_ticker_to_cik()
    results['ticker_to_cik'] = len(cik_mapping) > 0

    if not cik_mapping:
        print_error("\nCannot continue tests - ticker to CIK conversion failed")
        print_section("Test Summary")
        print_error("0/6 tests passed")
        return False

    # Use Apple (AAPL) for remaining tests
    test_ticker = "AAPL"
    test_cik = cik_mapping.get(test_ticker)

    if not test_cik:
        print_error(f"\nCannot continue tests - no CIK found for {test_ticker}")
        return False

    # Test 2: Company submissions
    results['submissions'] = await test_company_submissions(test_cik, test_ticker)

    # Test 3: Company financial facts
    results['facts'] = await test_company_facts(test_cik, test_ticker)

    # Test 4: Latest 10-K
    results['10k'] = await test_10k_filing(test_ticker)

    # Test 5: Latest 10-Q
    results['10q'] = await test_10q_filing(test_ticker)

    # Test 6: Multiple filings
    results['multiple_filings'] = await test_multiple_filings(test_ticker)

    # Print summary
    print_section("Test Summary")

    passed_tests = sum(results.values())
    total_tests = len(results)

    print(f"\n📊 Results: {passed_tests}/{total_tests} tests passed\n")

    for test_name, passed in results.items():
        test_label = test_name.replace('_', ' ').title()
        if passed:
            print_success(f"{test_label}: PASSED")
        else:
            print_error(f"{test_label}: FAILED")

    print("\n" + "=" * 80)

    # Next steps
    if passed_tests == total_tests:
        print("\n🎉 All tests passed! SEC EDGAR collector is working perfectly.")
        print("\n📝 What this means:")
        print("   • You can access official US company financial data")
        print("   • No API key needed - completely free")
        print("   • Rate limited to 10 req/sec automatically")
        print("   • Access to 10-K, 10-Q, 8-K, and all other SEC filings")
        print("   • Structured XBRL financial data available")
        print("\n💡 Available Data:")
        print("   • Company Information: CIK, ticker, SIC code, address")
        print("   • Filings: 10-K (annual), 10-Q (quarterly), 8-K (events)")
        print("   • Financial Facts: Revenue, Assets, Liabilities, EPS, etc.")
        print("   • Institutional Holdings: 13F-HR filings")
        print("\n🔧 Next Steps:")
        print("   1. Create database migration for SEC tables")
        print("   2. Integrate collector into main data pipeline")
        print("   3. Set up automated data collection schedule")
        print("   4. Build dashboard for SEC data visualization")
    elif passed_tests > 0:
        print("\n⚠️  Some tests passed. Check errors above for details.")
    else:
        print("\n❌ All tests failed. Troubleshooting:")
        print("   • Check internet connection")
        print("   • Verify SEC API is accessible (https://data.sec.gov)")
        print("   • Try again in a few minutes")
        print("   • Check if proxy/firewall is blocking SEC API")

    print()

    return passed_tests == total_tests


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
