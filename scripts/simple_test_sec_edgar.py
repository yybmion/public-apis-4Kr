#!/usr/bin/env python3
"""
Simple Test: SEC EDGAR API Collector
Uses only standard library + aiohttp
No API key required!
"""

import asyncio
import sys

try:
    import aiohttp
except ImportError:
    print("❌ aiohttp library not found. Installing...")
    import subprocess
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'aiohttp'])
    import aiohttp


async def test_sec_edgar():
    """Test SEC EDGAR API - No API key needed!"""

    print("=" * 80)
    print("  🧪 Testing SEC EDGAR API Collector")
    print("  (No API key required - FREE official US government data!)")
    print("=" * 80)
    print()

    # Test 1: Get company tickers
    print("📊 Test 1: Fetching company ticker list...")
    ticker_url = "https://www.sec.gov/files/company_tickers.json"

    headers = {
        "User-Agent": "Stock-Intelligence-System support@example.com",
        "Accept": "application/json"
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(ticker_url, headers=headers, timeout=30) as response:
                if response.status == 200:
                    tickers = await response.json()
                    print(f"✅ Successfully fetched {len(tickers)} company tickers\n")

                    # Show a few examples
                    print("   Sample companies:")
                    for i, (key, company) in enumerate(list(tickers.items())[:5]):
                        ticker = company.get('ticker', 'N/A')
                        name = company.get('title', 'N/A')
                        cik = company.get('cik_str', 'N/A')
                        print(f"      {ticker:6s} - {name[:40]:40s} (CIK: {cik})")

                    print()

                    # Find Apple
                    apple_cik = None
                    for company in tickers.values():
                        if company.get('ticker') == 'AAPL':
                            apple_cik = str(company.get('cik_str')).zfill(10)
                            print(f"   📍 Found Apple Inc.: CIK = {apple_cik}")
                            break

                    if not apple_cik:
                        print("   ❌ Could not find Apple in ticker list")
                        return False

                else:
                    print(f"❌ HTTP Error: {response.status}")
                    return False

        print()

        # Test 2: Get Apple's company submissions
        print("📊 Test 2: Fetching Apple's SEC filings...")
        submissions_url = f"https://data.sec.gov/submissions/CIK{apple_cik}.json"

        await asyncio.sleep(0.1)  # Rate limiting

        async with aiohttp.ClientSession() as session:
            async with session.get(submissions_url, headers=headers, timeout=30) as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ Successfully fetched company submissions\n")

                    print(f"   Company Name: {data.get('name')}")
                    print(f"   CIK: {data.get('cik')}")
                    print(f"   SIC: {data.get('sic')} - {data.get('sicDescription')}")
                    print()

                    # Filings
                    if 'filings' in data and 'recent' in data['filings']:
                        recent = data['filings']['recent']
                        total_filings = len(recent.get('accessionNumber', []))
                        print(f"   Total Recent Filings: {total_filings}")

                        # Find latest 10-K
                        forms = recent.get('form', [])
                        dates = recent.get('filingDate', [])
                        acc_nums = recent.get('accessionNumber', [])

                        for i, form in enumerate(forms):
                            if form == '10-K':
                                print(f"\n   Latest 10-K Filing:")
                                print(f"      Date: {dates[i]}")
                                print(f"      Accession: {acc_nums[i]}")
                                break

                else:
                    print(f"❌ HTTP Error: {response.status}")
                    return False

        print()

        # Test 3: Get Apple's financial facts
        print("📊 Test 3: Fetching Apple's financial facts (XBRL data)...")
        facts_url = f"https://data.sec.gov/api/xbrl/companyfacts/CIK{apple_cik}.json"

        await asyncio.sleep(0.1)  # Rate limiting

        async with aiohttp.ClientSession() as session:
            async with session.get(facts_url, headers=headers, timeout=30) as response:
                if response.status == 200:
                    facts_data = await response.json()
                    print(f"✅ Successfully fetched financial facts\n")

                    if 'facts' in facts_data:
                        facts = facts_data['facts']

                        print(f"   Available Taxonomies: {list(facts.keys())}")

                        if 'us-gaap' in facts:
                            us_gaap = facts['us-gaap']
                            print(f"   US-GAAP Concepts: {len(us_gaap)}")

                            # Show Revenue if available
                            revenue_concepts = ['Revenues', 'Revenue', 'RevenueFromContractWithCustomerExcludingAssessedTax']
                            for concept in revenue_concepts:
                                if concept in us_gaap:
                                    revenue_data = us_gaap[concept]
                                    if 'units' in revenue_data and 'USD' in revenue_data['units']:
                                        usd_data = revenue_data['units']['USD']
                                        if usd_data:
                                            latest = usd_data[-1]
                                            value = latest.get('val', 0)
                                            date = latest.get('end', 'N/A')
                                            print(f"\n   Latest Revenue ({concept}):")
                                            print(f"      Value: ${value:,}")
                                            print(f"      Date: {date}")
                                            break
                                    break

                else:
                    print(f"❌ HTTP Error: {response.status}")
                    return False

        print()
        print("=" * 80)
        print("✅ All tests PASSED! SEC EDGAR API collector is working!")
        print("=" * 80)
        print()
        print("📝 What this means:")
        print("   • You can access official US company financial data for FREE")
        print("   • No API key needed - public government data")
        print("   • Access to ALL SEC filings (10-K, 10-Q, 8-K, etc.)")
        print("   • Structured financial data (Revenue, Assets, etc.)")
        print("   • Historical data available going back years")
        print()
        print("💡 Data Available:")
        print("   • Company Information: Name, CIK, SIC code, address")
        print("   • Annual Reports (10-K): Comprehensive yearly financials")
        print("   • Quarterly Reports (10-Q): Quarterly financial updates")
        print("   • Current Reports (8-K): Material event disclosures")
        print("   • Institutional Holdings (13F): What big investors own")
        print("   • Financial Facts: Revenue, Assets, Liabilities, EPS, etc.")
        print()
        print("🔧 Usage Examples:")
        print("   • Track revenue growth trends")
        print("   • Analyze balance sheet strength")
        print("   • Monitor institutional investor activity")
        print("   • Get real-time filing notifications")
        print()

        return True

    except asyncio.TimeoutError:
        print("❌ Connection timeout - SEC server might be slow")
        print("   Try again in a few minutes")
        return False
    except aiohttp.ClientError as e:
        print(f"❌ Network error: {str(e)}")
        print("   Check your internet connection")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    success = await test_sec_edgar()

    if success:
        print("🎉 Next steps:")
        print()
        print("   1️⃣  SEC EDGAR API works perfectly!")
        print("       Ready to integrate into your system")
        print()
        print("   2️⃣  Create database tables for SEC data")
        print("       Run migration script to set up tables")
        print()
        print("   3️⃣  Start collecting data")
        print("       • Company information")
        print("       • SEC filings (10-K, 10-Q, 8-K)")
        print("       • Financial facts (XBRL)")
        print("       • Institutional holdings (13F)")
        print()
        print("   4️⃣  Build analysis features")
        print("       • Revenue growth analysis")
        print("       • Balance sheet health scoring")
        print("       • Institutional ownership tracking")
        print()
    else:
        print("⚠️  Test failed.")
        print()
        print("Troubleshooting:")
        print("   • Check internet connection")
        print("   • Try again in a few minutes")
        print("   • SEC server might be temporarily unavailable")
        print("   • Verify no firewall/proxy is blocking SEC API")

    return success


if __name__ == "__main__":
    result = asyncio.run(main())
    sys.exit(0 if result else 1)
