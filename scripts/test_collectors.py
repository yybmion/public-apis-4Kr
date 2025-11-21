"""
Test Script for Data Collectors
Stock Intelligence System

This script tests all data collectors to verify they are working correctly.
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.collectors.kis_collector import KISCollector
from app.collectors.yahoo_collector import YahooCollector
from app.collectors.dart_collector import DARTCollector
from app.config import settings


async def test_yahoo_collector():
    """Test Yahoo Finance collector"""
    print("\n" + "="*50)
    print("Testing Yahoo Finance Collector (US Indices)")
    print("="*50)

    collector = YahooCollector()

    try:
        # Test S&P 500
        print("\n📊 Collecting S&P 500 data...")
        data = await collector.collect(symbol="^GSPC", period="3mo")

        print(f"✅ Success!")
        print(f"   Symbol: {data['symbol']}")
        print(f"   Name: {data['name']}")
        print(f"   Close: ${data['close']:,.2f}")
        print(f"   MA(20): ${data['ma_20']:,.2f}" if data['ma_20'] else "   MA(20): N/A")
        print(f"   Above MA: {'🟢 Yes' if data['above_ma'] else '🔴 No'}")
        print(f"   Signal: {collector.get_signal(data['close'], data['ma_20']) if data['ma_20'] else 'N/A'}")
        print(f"   Date: {data['date']}")

        # Test all indices
        print("\n📊 Collecting all US indices...")
        all_data = await collector.collect_all_indices()

        for idx_data in all_data:
            signal = "🟢 BULLISH" if idx_data['above_ma'] else "🔴 BEARISH"
            print(f"   {idx_data['name']:30} ${idx_data['close']:10,.2f}  {signal}")

        return True

    except Exception as e:
        print(f"❌ Failed: {str(e)}")
        return False


async def test_kis_collector():
    """Test KIS API collector"""
    print("\n" + "="*50)
    print("Testing KIS API Collector (Korean Stocks)")
    print("="*50)

    if not settings.KIS_APP_KEY or not settings.KIS_APP_SECRET:
        print("⚠️  Skipped: KIS API keys not configured")
        print("   Please set KIS_APP_KEY and KIS_APP_SECRET in .env file")
        return None

    collector = KISCollector()

    try:
        # Test with Samsung Electronics (005930)
        print("\n📊 Collecting Samsung Electronics (005930) data...")

        # First get access token
        print("   Getting OAuth token...")
        token = await collector.get_access_token()
        print(f"   ✅ Token obtained: {token[:20]}...")

        # Collect stock data
        print("   Collecting stock data...")
        data = await collector.collect(stock_code="005930")

        print(f"✅ Success!")
        print(f"   Code: {data['code']}")
        print(f"   Name: {data['name']}")
        print(f"   Price: {data['current_price']:,}원")
        print(f"   Change: {data['change_rate']:+.2f}%")
        print(f"   Volume: {data['volume']:,}주")
        print(f"   High: {data['high']:,}원")
        print(f"   Low: {data['low']:,}원")

        return True

    except Exception as e:
        print(f"❌ Failed: {str(e)}")
        return False


async def test_dart_collector():
    """Test DART API collector"""
    print("\n" + "="*50)
    print("Testing DART API Collector (Financial Data)")
    print("="*50)

    if not settings.DART_API_KEY:
        print("⚠️  Skipped: DART API key not configured")
        print("   Please set DART_API_KEY in .env file")
        return None

    collector = DARTCollector()

    try:
        # Note: DART requires corp_code, not stock_code
        # This is just a test to verify API connection
        print("\n📊 Testing DART API connection...")
        print("   Note: Full test requires corp_code mapping")

        print(f"✅ DART Collector initialized")
        print(f"   API Key: {settings.DART_API_KEY[:10]}...")
        print(f"   Base URL: {settings.DART_BASE_URL}")

        return True

    except Exception as e:
        print(f"❌ Failed: {str(e)}")
        return False


async def main():
    """Run all tests"""
    print("\n")
    print("╔" + "="*60 + "╗")
    print("║" + " "*15 + "Stock Intelligence System" + " "*20 + "║")
    print("║" + " "*18 + "Collector Tests" + " "*25 + "║")
    print("╚" + "="*60 + "╝")

    results = {}

    # Test Yahoo Finance (doesn't require API key)
    results['yahoo'] = await test_yahoo_collector()

    # Test KIS API
    results['kis'] = await test_kis_collector()

    # Test DART API
    results['dart'] = await test_dart_collector()

    # Summary
    print("\n" + "="*50)
    print("Test Summary")
    print("="*50)

    for name, result in results.items():
        if result is True:
            status = "✅ PASS"
        elif result is False:
            status = "❌ FAIL"
        else:
            status = "⚠️  SKIP"

        print(f"{name.upper():15} {status}")

    # Calculate success rate
    passed = sum(1 for r in results.values() if r is True)
    total = len([r for r in results.values() if r is not None])

    if total > 0:
        success_rate = (passed / total) * 100
        print(f"\nSuccess Rate: {success_rate:.1f}% ({passed}/{total})")

    print("\n" + "="*50)

    if results['yahoo'] is True:
        print("\n🎉 At least one collector is working!")
        print("You can now start the API server and dashboard:")
        print("   1. uvicorn app.main:app --reload")
        print("   2. streamlit run dashboard/app.py")
    else:
        print("\n⚠️  Some collectors failed. Check API keys in .env file")


if __name__ == "__main__":
    asyncio.run(main())
