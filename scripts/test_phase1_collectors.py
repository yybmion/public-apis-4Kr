#!/usr/bin/env python3
"""
Phase 1 Data Collectors Test Script

Tests all three Phase 1 collectors:
1. FRED API Collector (requires API key)
2. ECOS API Collector (requires API key)
3. Fear & Greed Index Collector (no API key required)

Usage:
    python scripts/test_phase1_collectors.py
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.collectors.fred_collector import FredCollector
from app.collectors.ecos_collector import EcosCollector
from app.collectors.fear_greed_collector import FearGreedCollector
from app.config import Settings


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


def print_data(label: str, value):
    """Print data in a formatted way"""
    print(f"   {label}: {value}")


async def test_fear_greed_collector():
    """Test Fear & Greed Index Collector (No API key required)"""
    print_section("TEST 1: Fear & Greed Index Collector")

    try:
        collector = FearGreedCollector()
        print_success("Fear & Greed Index Collector initialized")

        # Test current data collection
        print("\n📊 Collecting current Fear & Greed Index...")
        result = await collector.collect()

        if result.get('success'):
            data = result['data']
            print_success("Data collection successful!")
            print_data("Score", f"{data['score']:.2f} / 100")
            print_data("Rating", data['rating'])
            print_data("Signal", data['signal']['signal'])
            print_data("Description", data['signal']['description'])
            print_data("Date", data['timestamp'])

            # Test trend analysis
            print("\n📈 Analyzing 30-day trend...")
            trend = await collector.get_trend_analysis(days=30)

            if trend.get('success'):
                trend_data = trend['data']
                print_success("Trend analysis successful!")
                print_data("Average Score", f"{trend_data['average_score']:.2f}")
                print_data("Trend Direction", trend_data['trend_direction'])
                print_data("Extreme Fear Days", trend_data['extreme_fear_days'])
                print_data("Extreme Greed Days", trend_data['extreme_greed_days'])
            else:
                print_error(f"Trend analysis failed: {trend.get('error')}")
        else:
            print_error(f"Data collection failed: {result.get('error')}")

        return True

    except Exception as e:
        print_error(f"Fear & Greed Index test failed: {str(e)}")
        return False


async def test_fred_collector(api_key: str):
    """Test FRED API Collector (requires API key)"""
    print_section("TEST 2: FRED API Collector")

    if not api_key or api_key == "your_fred_api_key_here":
        print_warning("FRED_API_KEY not configured in .env file")
        print_warning("Skipping FRED API test")
        print_warning("To enable: Get API key from https://fredaccount.stlouisfed.org/apikeys")
        return False

    try:
        collector = FredCollector(api_key=api_key)
        print_success("FRED Collector initialized")

        # Test single indicator
        print("\n📊 Collecting Federal Funds Rate...")
        result = await collector.collect(indicator='federal_funds_rate')

        if result.get('success'):
            data = result['data']
            print_success("Data collection successful!")
            print_data("Indicator", data['indicator_name'])
            print_data("Latest Value", f"{data['latest_value']:.2f}%")
            print_data("Latest Date", data['latest_date'])
            print_data("Data Points", len(data['data']))
        else:
            print_error(f"Data collection failed: {result.get('error')}")
            return False

        # Test yield curve
        print("\n📈 Calculating Yield Curve...")
        yield_result = await collector.get_yield_curve()

        if yield_result.get('success'):
            yc_data = yield_result['data']
            print_success("Yield curve calculation successful!")
            print_data("10Y Treasury", f"{yc_data['yields'].get('treasury_10y', 0):.3f}%")
            print_data("2Y Treasury", f"{yc_data['yields'].get('treasury_2y', 0):.3f}%")
            print_data("10Y-2Y Spread", f"{yc_data['spreads'].get('10y_2y', 0):.3f}%")
            print_data("Yield Curve Inverted", yc_data['yield_curve_inverted'])
            print_data("Recession Signal", yc_data['recession_signal'])
        else:
            print_error(f"Yield curve calculation failed: {yield_result.get('error')}")
            return False

        return True

    except Exception as e:
        print_error(f"FRED API test failed: {str(e)}")
        return False


async def test_ecos_collector(api_key: str):
    """Test ECOS API Collector (requires API key)"""
    print_section("TEST 3: ECOS API Collector")

    if not api_key or api_key == "your_ecos_api_key_here":
        print_warning("ECOS_API_KEY not configured in .env file")
        print_warning("Skipping ECOS API test")
        print_warning("To enable: Get API key from https://ecos.bok.or.kr/api/")
        return False

    try:
        collector = EcosCollector(api_key=api_key)
        print_success("ECOS Collector initialized")

        # Test single indicator
        print("\n📊 Collecting Korean Base Rate...")
        result = await collector.collect(indicator='base_rate')

        if result.get('success'):
            data = result['data']
            print_success("Data collection successful!")
            print_data("Indicator", data['indicator_name'])
            print_data("Latest Value", f"{data['latest_value']:.2f}%")
            print_data("Latest Date", data['latest_date'])
            print_data("Data Points", len(data['data']))
        else:
            print_error(f"Data collection failed: {result.get('error')}")
            return False

        # Test economic snapshot
        print("\n📈 Generating Economic Snapshot...")
        snapshot = await collector.get_economic_snapshot()

        if snapshot.get('success'):
            snap_data = snapshot['data']
            print_success("Economic snapshot generated!")
            print_data("Base Rate", f"{snap_data.get('base_rate', {}).get('value', 0):.2f}%")
            print_data("USD/KRW", f"{snap_data.get('usd_krw', {}).get('value', 0):.2f}")
            print_data("CPI", f"{snap_data.get('cpi', {}).get('value', 0):.2f}")
            print_data("Total Indicators", len(snap_data))
        else:
            print_error(f"Economic snapshot failed: {snapshot.get('error')}")
            return False

        return True

    except Exception as e:
        print_error(f"ECOS API test failed: {str(e)}")
        return False


async def main():
    """Main test runner"""
    print_section("Phase 1 Data Collectors Test Suite")
    print("This script tests all three Phase 1 data collectors:\n")
    print("1. Fear & Greed Index (No API key required)")
    print("2. FRED API (Requires API key)")
    print("3. ECOS API (Requires API key)")
    print("\nMake sure you have configured your .env file with API keys.")
    print("See PHASE1_SETUP_GUIDE.md for detailed instructions.\n")

    # Load configuration
    try:
        settings = Settings()
        fred_api_key = settings.FRED_API_KEY
        ecos_api_key = settings.ECOS_API_KEY
    except Exception as e:
        print_error(f"Failed to load configuration: {str(e)}")
        print_warning("Make sure .env file exists with required API keys")
        fred_api_key = ""
        ecos_api_key = ""

    # Run tests
    results = {
        'fear_greed': False,
        'fred': False,
        'ecos': False
    }

    # Test 1: Fear & Greed (always runs - no API key needed)
    results['fear_greed'] = await test_fear_greed_collector()

    # Test 2: FRED (only if API key configured)
    results['fred'] = await test_fred_collector(fred_api_key)

    # Test 3: ECOS (only if API key configured)
    results['ecos'] = await test_ecos_collector(ecos_api_key)

    # Print summary
    print_section("Test Summary")

    total_tests = 3
    passed_tests = sum(results.values())

    print(f"\n📊 Results: {passed_tests}/{total_tests} tests passed\n")

    if results['fear_greed']:
        print_success("Fear & Greed Index: PASSED")
    else:
        print_error("Fear & Greed Index: FAILED")

    if results['fred']:
        print_success("FRED API: PASSED")
    elif fred_api_key and fred_api_key != "your_fred_api_key_here":
        print_error("FRED API: FAILED")
    else:
        print_warning("FRED API: SKIPPED (No API key)")

    if results['ecos']:
        print_success("ECOS API: PASSED")
    elif ecos_api_key and ecos_api_key != "your_ecos_api_key_here":
        print_error("ECOS API: FAILED")
    else:
        print_warning("ECOS API: SKIPPED (No API key)")

    print("\n" + "=" * 80)

    # Next steps
    if passed_tests == total_tests:
        print("\n🎉 All tests passed! You're ready to use Phase 1 collectors.")
        print("\nNext steps:")
        print("1. Set up database migration (see PHASE1_SETUP_GUIDE.md)")
        print("2. Configure automated data collection")
        print("3. Build dashboard for visualization")
    elif passed_tests > 0:
        print("\n⚠️  Some tests passed. Configure missing API keys to enable all collectors.")
        print("\nSee PHASE1_SETUP_GUIDE.md for API key setup instructions:")
        if not results['fred']:
            print("  - FRED API Key: https://fredaccount.stlouisfed.org/apikeys")
        if not results['ecos']:
            print("  - ECOS API Key: https://ecos.bok.or.kr/api/")
    else:
        print("\n❌ No tests passed. Please check your configuration and try again.")
        print("\nSee PHASE1_SETUP_GUIDE.md for troubleshooting.")

    print()

    return passed_tests == total_tests


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
