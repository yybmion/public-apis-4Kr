"""
Example Usage Scripts
Stock Intelligence System

Demonstrates how to use the main features of the system
"""

import asyncio
import sys
from pathlib import Path
import pandas as pd

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.database.session import SessionLocal
from app.analyzers.technical_analyzer import TechnicalAnalyzer
from app.analyzers.signal_detector import SignalDetector
from app.analyzers.backtest_engine import BacktestEngine, SP500MAStrategy
from app.recommenders.beginner_recommender import BeginnerRecommender
from app.recommenders.sector_analyzer import SectorAnalyzer
from app.collectors.yahoo_collector import YahooCollector
from app.utils.notification import MockNotifier


def print_section(title):
    """Print section header"""
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70 + "\n")


async def example_technical_analysis():
    """Example: Calculate technical indicators"""
    print_section("Example 1: Technical Analysis")

    # Create sample data
    dates = pd.date_range('2023-01-01', periods=100, freq='D')
    prices = 50000 + (pd.Series(range(100)) * 100) + (pd.Series(range(100)) ** 1.5) * 10

    df = pd.DataFrame({
        'date': dates,
        'open': prices * 0.99,
        'high': prices * 1.02,
        'low': prices * 0.98,
        'close': prices,
        'volume': 1000000 + (pd.Series(range(100)) * 10000)
    })

    # Calculate indicators
    analyzer = TechnicalAnalyzer()
    df_with_indicators = analyzer.calculate_all_indicators(df)

    # Show latest values
    latest = df_with_indicators.iloc[-1]

    print(f"Latest Close: {latest['close']:,.0f}원")
    print(f"MA(5):  {latest.get('ma_5', 0):,.0f}원")
    print(f"MA(20): {latest.get('ma_20', 0):,.0f}원")
    print(f"RSI:    {latest.get('rsi', 0):.2f}")
    print(f"MACD:   {latest.get('macd', 0):.2f}")

    # Detect patterns
    patterns = analyzer.detect_patterns(df_with_indicators)
    print("\n패턴 탐지:")
    for pattern, detected in patterns.items():
        if detected:
            print(f"  ✓ {pattern}")

    # Calculate trend
    trend = analyzer.calculate_trend_strength(df_with_indicators)
    print(f"\n추세 점수: {trend['trend_score']}")
    print(f"추세 방향: {trend['trend_direction']}")


async def example_signal_detection():
    """Example: Detect trading signals"""
    print_section("Example 2: Signal Detection")

    # Create sample data
    dates = pd.date_range('2023-01-01', periods=100, freq='D')
    prices = 70000 + (pd.Series(range(100)) * 50)

    df = pd.DataFrame({
        'date': dates,
        'open': prices * 0.99,
        'high': prices * 1.01,
        'low': prices * 0.99,
        'close': prices,
        'volume': 1000000
    })

    # Detect signals
    detector = SignalDetector()
    signals = detector.detect_stock_signals(df, "005930", "삼성전자")

    print(f"종목: {signals['stock_name']} ({signals['stock_code']})")
    print(f"최종 액션: {signals['action']}")
    print(f"점수: {signals['score']}")
    print(f"\n감지된 신호 ({signals['total_signals']}개):")

    for signal in signals['signals'][:5]:  # Show top 5
        print(f"  • {signal['description']}")


async def example_backtest():
    """Example: Run backtest"""
    print_section("Example 3: Backtesting")

    # Create sample Korean stock data
    dates = pd.date_range('2020-01-01', periods=500, freq='D')
    kr_prices = 60000 + pd.Series(range(500)) * 20 + (pd.Series(range(500)) ** 1.2) * 2

    kr_data = pd.DataFrame({
        'date': dates,
        'open': kr_prices * 0.99,
        'high': kr_prices * 1.02,
        'low': kr_prices * 0.98,
        'close': kr_prices,
        'volume': 1000000
    })

    # Create sample US data (S&P 500)
    us_prices = 4000 + pd.Series(range(500)) * 1.5 + (pd.Series(range(500)) ** 1.1) * 0.5

    us_data = pd.DataFrame({
        'date': dates,
        'open': us_prices * 0.99,
        'high': us_prices * 1.01,
        'low': us_prices * 0.99,
        'close': us_prices,
        'volume': 100000000
    })

    # Run backtest
    engine = BacktestEngine()

    print("S&P 500 MA(20) 전략 백테스트 실행 중...")
    result = engine.run_backtest(
        strategy_class=SP500MAStrategy,
        stock_data=kr_data,
        us_data=us_data,
        initial_cash=10_000_000,
        ma_period=20
    )

    # Print report
    print(engine.format_backtest_report(result))


def example_recommendations():
    """Example: Generate stock recommendations"""
    print_section("Example 4: Stock Recommendations")

    with SessionLocal() as db:
        recommender = BeginnerRecommender(db)

        # Analyze user profile
        print("투자자 프로필 분석:")
        user_answers = {
            'investment_amount': 5_000_000,
            'investment_period': 'long',
            'loss_tolerance': 'low',
            'experience': 'none',
            'goal': 'preservation'
        }

        profile = recommender.analyze_user_profile(user_answers)
        print(f"  위험도: {profile['risk_level']}")
        print(f"  추천 섹터: {', '.join(profile['preferred_sectors'])}")
        print(f"  조언: {profile['recommendation']}")

        # Get recommendations
        print("\n종목 추천 (상위 5개):")
        recommendations = recommender.recommend(
            risk_level=profile['risk_level'],
            limit=5,
            save_to_db=False
        )

        if recommendations:
            for i, rec in enumerate(recommendations, 1):
                print(f"\n{i}. {rec['stock_name']} ({rec['stock_code']})")
                print(f"   점수: {rec['score']}/100")
                print(f"   이유:")
                for reason in rec['reasons']:
                    print(f"     • {reason}")
        else:
            print("  (종목 데이터가 없습니다)")


def example_sector_analysis():
    """Example: Sector analysis"""
    print_section("Example 5: Sector Analysis")

    with SessionLocal() as db:
        analyzer = SectorAnalyzer(db)

        # Get all sectors
        sectors = analyzer.get_all_sectors()

        print(f"전체 섹터: {len(sectors)}개\n")

        # Show beginner-friendly sectors
        beginner_sectors = analyzer.get_beginner_friendly_sectors()
        print("초보자 추천 섹터:")
        for sector in beginner_sectors:
            info = analyzer.get_sector_info(sector)
            print(f"  {info['emoji']} {info['name']} - {info['description']}")

        # Get sector guide
        print("\n" + "="*70)
        guide = analyzer.format_sector_guide('IT/반도체')
        print(guide)


async def example_notification():
    """Example: Send notifications"""
    print_section("Example 6: Notifications")

    # Use mock notifier (doesn't actually send)
    notifier = MockNotifier()

    print("예제 알림 전송:")

    # Target price alert
    notifier.send_target_price_alert(
        stock_name="삼성전자",
        current_price=75000,
        target_price=75000
    )

    # Surge alert
    notifier.send_surge_alert(
        stock_name="SK하이닉스",
        current_price=120000,
        change_rate=7.5,
        volume=5000000
    )

    # US signal alert
    notifier.send_us_signal_alert(
        signal="BULLISH",
        sp500_close=4550.0,
        sp500_ma=4480.0,
        recommendation="한국 주식 매수 포지션 유지"
    )

    print("\n✓ 모든 알림이 성공적으로 전송되었습니다 (모의 전송)")


async def example_us_market_data():
    """Example: Collect US market data"""
    print_section("Example 7: US Market Data Collection")

    collector = YahooCollector()

    print("S&P 500 데이터 수집 중...")
    data = await collector.collect(symbol="^GSPC", period="3mo")

    print(f"\n지수: {data['name']}")
    print(f"심볼: {data['symbol']}")
    print(f"종가: ${data['close']:,.2f}")
    print(f"MA(20): ${data['ma_20']:,.2f}" if data['ma_20'] else "MA(20): N/A")
    print(f"MA 위: {'예' if data['above_ma'] else '아니오'}")
    print(f"신호: {'🟢 BULLISH' if data['above_ma'] else '🔴 BEARISH'}")

    # Get signal
    signal = collector.get_signal(data['close'], data['ma_20']) if data['ma_20'] else 'NEUTRAL'
    print(f"\n매매 신호: {signal}")

    if signal == 'BULLISH':
        print("💡 한국 주식 매수 포지션 유지를 권장합니다.")
    elif signal == 'BEARISH':
        print("💡 한국 주식 신중한 접근이 필요합니다.")


async def main():
    """Run all examples"""
    print("\n" + "╔" + "="*68 + "╗")
    print("║" + " "*15 + "Stock Intelligence System Examples" + " "*19 + "║")
    print("╚" + "="*68 + "╝")

    try:
        # Example 1: Technical Analysis
        await example_technical_analysis()

        # Example 2: Signal Detection
        await example_signal_detection()

        # Example 3: Backtesting
        await example_backtest()

        # Example 4: Recommendations
        example_recommendations()

        # Example 5: Sector Analysis
        example_sector_analysis()

        # Example 6: Notifications
        await example_notification()

        # Example 7: US Market Data
        await example_us_market_data()

        print("\n" + "="*70)
        print("  ✅ 모든 예제 실행 완료!")
        print("="*70)

    except Exception as e:
        print(f"\n❌ 오류 발생: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
