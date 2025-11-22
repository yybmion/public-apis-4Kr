#!/usr/bin/env python3
"""
Simple Test: Fear & Greed Index
Uses only standard library + requests (usually pre-installed)
No API key required!
"""

import json
try:
    import requests
except ImportError:
    print("❌ requests library not found. Installing...")
    import subprocess
    subprocess.check_call(['pip', 'install', 'requests'])
    import requests


def test_fear_greed_index():
    """Test CNN Fear & Greed Index - No API key needed!"""

    print("=" * 80)
    print("  🧪 Testing Fear & Greed Index Collector")
    print("  (No API key required - FREE!)")
    print("=" * 80)
    print()

    url = "https://production.dataviz.cnn.io/index/fearandgreed/graphdata"

    try:
        print("📡 Connecting to CNN Fear & Greed Index...")

        response = requests.get(url, timeout=10)

        if response.status_code == 200:
            data = response.json()

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
                print(f"📈 Historical Data: {len(history)} data points available")

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

                # Trend analysis
                if len(scores) >= 10:
                    recent_avg = sum(scores[:10]) / 10
                    older_avg = sum(scores[10:20]) / 10 if len(scores) >= 20 else avg_score

                    if recent_avg < older_avg - 5:
                        trend = "📉 Decreasing (공포 증가 중)"
                    elif recent_avg > older_avg + 5:
                        trend = "📈 Increasing (탐욕 증가 중)"
                    else:
                        trend = "➡️  Stable (안정적)"

                    print(f"   Trend: {trend}")
                print()

            print("=" * 80)
            print("✅ Test PASSED! Fear & Greed Index collector is working!")
            print("=" * 80)
            print()
            print("📝 What this means:")
            print("   • You can collect market sentiment data for FREE")
            print("   • No API key needed - works immediately")
            print("   • Data updates daily from CNN")
            print("   • Perfect for contrarian investment strategies")
            print()
            print("💡 Usage examples:")
            print("   • When score < 25: Consider buying (market panic)")
            print("   • When score > 75: Consider selling (market euphoria)")
            print("   • Track trends to identify market turning points")
            print()

            return True
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            print(f"   Response: {response.text[:200]}")
            return False

    except requests.exceptions.Timeout:
        print("❌ Connection timeout - CNN server might be slow")
        print("   Try again in a few minutes")
        return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Network error: {str(e)}")
        print("   Check your internet connection")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def main():
    success = test_fear_greed_index()

    if success:
        print("🎉 Next steps:")
        print()
        print("   1️⃣  Fear & Greed Index works perfectly!")
        print("       Ready to use in your system")
        print()
        print("   2️⃣  Want 800,000+ economic indicators?")
        print("       Get free API keys for:")
        print("       • FRED (US economic data)")
        print("       • ECOS (Korean economic data)")
        print("       See: PHASE1_SETUP_GUIDE.md")
        print()
        print("   3️⃣  Or proceed to Phase 2:")
        print("       • SEC EDGAR (official US financial data)")
        print("       • Institutional holdings")
        print("       • More data sources")
        print()
    else:
        print("⚠️  Test failed.")
        print()
        print("Troubleshooting:")
        print("   • Check internet connection")
        print("   • Try again in a few minutes")
        print("   • CNN server might be temporarily unavailable")

    return success


if __name__ == "__main__":
    result = main()
    exit(0 if result else 1)
