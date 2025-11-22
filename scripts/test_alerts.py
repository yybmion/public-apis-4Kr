"""
Test Alert System

알림 시스템 테스트

Tests:
1. Telegram Bot connection
2. Email connection
3. Investment signal alerts
4. Daily briefing
5. Extreme market alerts
6. Signal change alerts
7. Economic alerts

Author: AI Assistant
Created: 2025-11-22
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.alerts.alert_manager import AlertManager, get_alert_manager


async def test_connections():
    """Test all alert channel connections"""
    print("\n" + "=" * 80)
    print("  Alert System Connection Test")
    print("=" * 80)

    manager = get_alert_manager()

    print("\n1. Testing connections...")
    results = await manager.test_all_channels()

    print(f"\n   Telegram: {'✅ Connected' if results['telegram'] else '❌ Failed'}")
    print(f"   Email:    {'✅ Connected' if results['email'] else '❌ Failed'}")

    return all(results.values())


async def test_investment_signal():
    """Test investment signal alert"""
    print("\n" + "=" * 80)
    print("  Investment Signal Alert Test")
    print("=" * 80)

    manager = get_alert_manager()

    # Sample signal data
    signal_data = {
        'signal': 'BUY',
        'confidence': 75.5,
        'score': 7.2,
        'action_plan': {
            'action': '점진적 매수 (DCA 전략)',
            'timeframe': '1-2주',
            'target_allocation': {
                '주식': '60%',
                '채권': '30%',
                '현금': '10%'
            }
        }
    }

    print("\n2. Sending investment signal alert...")
    results = await manager.send_investment_signal(signal_data)

    print(f"\n   Telegram: {'✅ Sent' if results['telegram'] else '❌ Failed'}")
    print(f"   Email:    {'✅ Sent' if results['email'] else '⚠️ Skipped (sent in daily report)'}")

    return True


async def test_daily_briefing():
    """Test daily briefing"""
    print("\n" + "=" * 80)
    print("  Daily Briefing Test")
    print("=" * 80)

    manager = get_alert_manager()

    # Sample briefing
    briefing = """
📊 미국 시장:
- S&P 500: +0.85% (상승 마감)
- NASDAQ: +1.20% (기술주 강세)

💡 주요 이슈:
- Fed 금리 동결 결정
- 빅테크 실적 호조

📈 한국 시장 전망:
- 미국 증시 호조로 긍정적 영향 예상
- KOSPI 상승 개장 전망
    """.strip()

    signal_data = {
        'signal': 'BUY',
        'confidence': 75.0
    }

    market_data = {
        'sp500_change_pct': 0.85,
        'nasdaq_change_pct': 1.20
    }

    print("\n3. Sending daily briefing...")
    results = await manager.send_daily_briefing(briefing, signal_data, market_data)

    print(f"\n   Telegram: {'✅ Sent' if results['telegram'] else '❌ Failed'}")
    print(f"   Email:    {'✅ Sent' if results['email'] else '❌ Failed'}")

    return True


async def test_extreme_market_alert():
    """Test extreme market alert"""
    print("\n" + "=" * 80)
    print("  Extreme Market Alert Test")
    print("=" * 80)

    manager = get_alert_manager()

    # Test extreme fear
    print("\n4a. Testing extreme fear alert (score=20)...")
    fear_data = {
        'sp500_change_pct': -2.5,
        'nasdaq_change_pct': -3.2
    }

    results = await manager.send_extreme_market_alert(20, fear_data)
    print(f"   Telegram: {'✅ Sent' if results['telegram'] else '❌ Failed'}")
    print(f"   Email:    {'✅ Sent' if results['email'] else '❌ Failed'}")

    # Wait a bit
    await asyncio.sleep(2)

    # Test extreme greed
    print("\n4b. Testing extreme greed alert (score=80)...")
    greed_data = {
        'sp500_change_pct': 1.8,
        'nasdaq_change_pct': 2.5
    }

    results = await manager.send_extreme_market_alert(80, greed_data)
    print(f"   Telegram: {'✅ Sent' if results['telegram'] else '❌ Failed'}")
    print(f"   Email:    {'✅ Sent' if results['email'] else '❌ Failed'}")

    return True


async def test_signal_change_alert():
    """Test signal change alert"""
    print("\n" + "=" * 80)
    print("  Signal Change Alert Test")
    print("=" * 80)

    manager = get_alert_manager()

    print("\n5. Sending signal change alert...")
    results = await manager.send_signal_change_alert(
        old_signal='HOLD',
        new_signal='BUY',
        confidence=72.0,
        reason='S&P 500 골든크로스 발생 및 Fear & Greed 지수 개선'
    )

    print(f"\n   Telegram: {'✅ Sent' if results['telegram'] else '❌ Failed'}")
    print(f"   Email:    {'✅ Sent' if results['email'] else '❌ Failed'}")

    return True


async def test_economic_alert():
    """Test economic alert"""
    print("\n" + "=" * 80)
    print("  Economic Alert Test")
    print("=" * 80)

    manager = get_alert_manager()

    # Test rate hike alert
    print("\n6a. Testing rate hike alert...")
    rate_hike_data = {
        'fed_rate': 5.50,
        'kr_rate': 3.50,
        'spread': 2.00,
        'impact': '⚠️ 높은 금리 차 - 원화 약세 압력 지속'
    }

    results = await manager.send_economic_alert('rate_hike', rate_hike_data)
    print(f"   Telegram: {'✅ Sent' if results['telegram'] else '❌ Failed'}")
    print(f"   Email:    {'✅ Sent (included in daily)' if results['email'] else '⚠️ Skipped'}")

    await asyncio.sleep(2)

    # Test yield curve inversion
    print("\n6b. Testing yield curve inversion alert...")
    yc_data = {
        'spread_10y_2y': -0.35,
        'recession_probability': 65
    }

    results = await manager.send_economic_alert('yield_curve_inversion', yc_data)
    print(f"   Telegram: {'✅ Sent' if results['telegram'] else '❌ Failed'}")
    print(f"   Email:    {'✅ Sent (included in daily)' if results['email'] else '⚠️ Skipped'}")

    return True


async def test_weekly_report():
    """Test weekly report"""
    print("\n" + "=" * 80)
    print("  Weekly Report Test")
    print("=" * 80)

    manager = get_alert_manager()

    # Sample performance data
    performance_data = {
        'total_return_pct': 3.5,
        'max_drawdown_pct': -2.1,
        'win_rate': 0.625
    }

    # Sample signals history
    signals_history = [
        {'date': '2025-11-18', 'signal': 'HOLD', 'confidence': 65},
        {'date': '2025-11-19', 'signal': 'BUY', 'confidence': 72},
        {'date': '2025-11-20', 'signal': 'BUY', 'confidence': 75},
        {'date': '2025-11-21', 'signal': 'STRONG_BUY', 'confidence': 82},
    ]

    print("\n7. Sending weekly report...")
    results = await manager.send_weekly_report(performance_data, signals_history)

    print(f"\n   Telegram: {'✅ Sent (summary)' if results['telegram'] else '❌ Failed'}")
    print(f"   Email:    {'✅ Sent (full report)' if results['email'] else '❌ Failed'}")

    return True


async def test_custom_alert():
    """Test custom alert"""
    print("\n" + "=" * 80)
    print("  Custom Alert Test")
    print("=" * 80)

    manager = get_alert_manager()

    print("\n8. Sending custom alert...")
    results = await manager.send_custom_alert(
        title="테스트 알림",
        message="이것은 사용자 정의 알림 메시지입니다.",
        channels=['telegram', 'email']
    )

    print(f"\n   Telegram: {'✅ Sent' if results['telegram'] else '❌ Failed'}")
    print(f"   Email:    {'✅ Sent' if results['email'] else '❌ Failed'}")

    return True


async def test_alert_history():
    """Test alert history"""
    print("\n" + "=" * 80)
    print("  Alert History Test")
    print("=" * 80)

    manager = get_alert_manager()

    print("\n9. Checking alert history...")

    # Get signal history
    signal_history = manager.get_signal_history(limit=5)
    print(f"\n   Recent signals: {len(signal_history)} recorded")

    for sig in signal_history:
        print(f"   - {sig['date']}: {sig['signal']} (신뢰도: {sig['confidence']:.0f}%)")

    # Get alert history
    alert_history = manager.get_alert_history()
    print(f"\n   Alert types sent: {len(alert_history)}")

    for alert_type, last_sent in alert_history.items():
        print(f"   - {alert_type}: {last_sent.strftime('%Y-%m-%d %H:%M')}")

    return True


async def main():
    """Run all tests"""
    print("\n" + "=" * 80)
    print("  🔔 Alert System Test Suite")
    print("=" * 80)
    print("\n⚠️  Make sure you have configured the following environment variables:")
    print("   - TELEGRAM_BOT_TOKEN (from @BotFather)")
    print("   - TELEGRAM_CHAT_ID (from @userinfobot)")
    print("   - SMTP_USERNAME (email address)")
    print("   - SMTP_PASSWORD (app password)")
    print("   - EMAIL_TO (recipient email)")

    input("\nPress Enter to continue...")

    try:
        # Run tests
        await test_connections()
        await asyncio.sleep(2)

        await test_investment_signal()
        await asyncio.sleep(2)

        await test_daily_briefing()
        await asyncio.sleep(2)

        await test_extreme_market_alert()
        await asyncio.sleep(2)

        await test_signal_change_alert()
        await asyncio.sleep(2)

        await test_economic_alert()
        await asyncio.sleep(2)

        await test_weekly_report()
        await asyncio.sleep(2)

        await test_custom_alert()
        await asyncio.sleep(2)

        await test_alert_history()

        # Summary
        print("\n" + "=" * 80)
        print("  ✅ All tests completed!")
        print("=" * 80)
        print("\nCheck your Telegram and Email to verify all alerts were received.")

    except KeyboardInterrupt:
        print("\n\n⚠️  Tests interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Error during tests: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    asyncio.run(main())
