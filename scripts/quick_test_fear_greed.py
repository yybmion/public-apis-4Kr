#!/usr/bin/env python3
"""
Quick Test: Fear & Greed Index Collector
No API key required - works immediately!
"""

import asyncio
import aiohttp
from datetime import datetime


async def test_fear_greed_index():
    """Test CNN Fear & Greed Index - No API key needed!"""

    print("=" * 80)
    print("  🧪 Testing Fear & Greed Index Collector")
    print("  (No API key required - FREE!)")
    print("=" * 80)
    print()

    url = "https://production.dataviz.cnn.io/index/fearandgreed/graphdata"

    try:
        print("📡 Connecting to CNN Fear & Greed Index...")

        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=10) as response:
                if response.status == 200:
                    data = await response.json()

                    print("✅ Connection successful!\n")

                    # Parse current score
                    current_score = data['fear_and_greed']['score']
                    current_rating = data['fear_and_greed']['rating']

                    print(f"📊 Current Fear & Greed Index")
                    print(f"   Score: {current_score:.2f} / 100")
                    print(f"   Rating: {current_rating}")
                    print()

                    # Determine signal
                    score = float(current_score)
                    if score <= 25:
                        signal = "STRONG_BUY 🟢"
                        description = "극단적 공포 - 역발상 매수 기회!"
                    elif score <= 45:
                        signal = "BUY 🟢"
                        description = "공포 - 매수 고려"
                    elif score <= 55:
                        signal = "HOLD 🟡"
                        description = "중립 - 관망"
                    elif score <= 75:
                        signal = "SELL 🔴"
                        description = "탐욕 - 매도 고려"
                    else:
                        signal = "STRONG_SELL 🔴"
                        description = "극단적 탐욕 - 적극 매도 고려"

                    print(f"💡 투자 신호: {signal}")
                    print(f"   {description}")
                    print()

                    # Historical data
                    if 'fear_and_greed_historical' in data:
                        history = data['fear_and_greed_historical']['data']
                        print(f"📈 Historical Data: {len(history)} data points")

                        if len(history) >= 2:
                            yesterday = history[0]
                            last_week = history[6] if len(history) > 6 else history[-1]

                            yesterday_score = float(yesterday['score'])
                            last_week_score = float(last_week['score'])

                            daily_change = score - yesterday_score
                            weekly_change = score - last_week_score

                            print(f"   Daily change: {daily_change:+.2f}")
                            print(f"   Weekly change: {weekly_change:+.2f}")
                            print()

                    # Calculate 30-day average
                    if 'fear_and_greed_historical' in data:
                        history = data['fear_and_greed_historical']['data'][:30]
                        scores = [float(d['score']) for d in history]
                        avg_score = sum(scores) / len(scores)

                        extreme_fear_days = sum(1 for s in scores if s <= 25)
                        extreme_greed_days = sum(1 for s in scores if s >= 75)

                        print(f"📊 30-Day Analysis")
                        print(f"   Average score: {avg_score:.2f}")
                        print(f"   Extreme fear days: {extreme_fear_days}")
                        print(f"   Extreme greed days: {extreme_greed_days}")
                        print()

                    print("=" * 80)
                    print("✅ Test PASSED! Fear & Greed Index collector is working!")
                    print("=" * 80)
                    print()
                    print("📝 What this means:")
                    print("   - You can collect market sentiment data for FREE")
                    print("   - No API key needed")
                    print("   - Data updates daily")
                    print("   - Can be used for contrarian investment strategies")
                    print()

                    return True
                else:
                    print(f"❌ HTTP Error: {response.status}")
                    return False

    except asyncio.TimeoutError:
        print("❌ Connection timeout - CNN server might be slow")
        print("   Try again in a few minutes")
        return False
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False


async def main():
    success = await test_fear_greed_index()

    if success:
        print("\n🎉 Next steps:")
        print("   1. This collector works without any setup!")
        print("   2. Ready to integrate into your system")
        print("   3. Can start collecting data immediately")
        print()
        print("   To get FRED & ECOS data (800K+ economic indicators):")
        print("   - Follow PHASE1_SETUP_GUIDE.md")
        print("   - Get free API keys (takes 5 minutes)")
        print()
    else:
        print("\n⚠️  Test failed. Please check your internet connection.")

    return success


if __name__ == "__main__":
    result = asyncio.run(main())
    exit(0 if result else 1)
