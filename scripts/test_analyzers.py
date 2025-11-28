#!/usr/bin/env python3
"""
Analysis Modules Test Script

분석 모듈 테스트:
- Market Correlation Analyzer (미국-한국 상관관계)
- Economic Analyzer (경제 지표)
- Signal Generator (투자 신호)

Usage:
    python scripts/test_analyzers.py
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.analyzers.market_correlation_analyzer import MarketCorrelationAnalyzer
from app.analyzers.economic_analyzer import EconomicAnalyzer
from app.analyzers.signal_generator import SignalGenerator


def print_section(title: str):
    """Print section header"""
    print(f"\n{'=' * 80}")
    print(f"  {title}")
    print(f"{'=' * 80}\n")


def print_success(msg: str):
    """Print success message"""
    print(f"✅ {msg}")


def print_info(msg: str):
    """Print info message"""
    print(f"ℹ️  {msg}")


def test_market_correlation_analyzer():
    """Test Market Correlation Analyzer"""
    print_section("TEST 1: Market Correlation Analyzer")

    analyzer = MarketCorrelationAnalyzer()
    print_success("MarketCorrelationAnalyzer 초기화 완료\n")

    # Test data (예시)
    sp500_data = {
        'close': 4550.50,
        'ma20': 4530.00,
        'ma60': 4480.00,
        'change_pct': -1.2
    }

    nasdaq_data = {
        'close': 14200.30,
        'change_pct': -0.8
    }

    fear_greed_score = 35.5  # Fear 상태

    # Test 1: S&P 500 Signal
    print("📊 Test 1-1: S&P 500 분석")
    sp500_analysis = analyzer.analyze_sp500_signal(
        sp500_data['close'],
        sp500_data['ma20'],
        sp500_data['ma60'],
        sp500_data['change_pct']
    )

    print(f"  Signal: {sp500_analysis['signal']}")
    print(f"  Confidence: {sp500_analysis['confidence']:.1f}%")
    print(f"  Expected KOSPI Change: {sp500_analysis['expected_kospi_change']:+.2f}%")
    print(f"  Risk Level: {sp500_analysis['risk_level']}\n")

    print("  Reasoning:")
    for reason in sp500_analysis['reasoning']:
        print(f"    • {reason}")

    # Test 2: NASDAQ Signal
    print("\n📊 Test 1-2: NASDAQ 분석")
    nasdaq_analysis = analyzer.analyze_nasdaq_tech_signal(
        nasdaq_data['close'],
        nasdaq_data['change_pct']
    )

    print(f"  Signal: {nasdaq_analysis['signal']}")
    print(f"  Expected KOSDAQ Change: {nasdaq_analysis['expected_kosdaq_change']:+.2f}%\n")

    # Test 3: Combined Signals
    print("📊 Test 1-3: 종합 신호 분석")
    combined = analyzer.analyze_combined_signals(
        sp500_data,
        nasdaq_data,
        fear_greed_score
    )

    print(f"  Final Signal: {combined['final_signal']}")
    print(f"  Agreement Level: {combined['agreement_level'] * 100:.0f}%")
    print(f"  Market Direction: {combined['expected_market_direction']}\n")

    print_success("Market Correlation Analyzer 테스트 완료!\n")


def test_economic_analyzer():
    """Test Economic Analyzer"""
    print_section("TEST 2: Economic Analyzer")

    analyzer = EconomicAnalyzer()
    print_success("EconomicAnalyzer 초기화 완료\n")

    # Test data
    us_fed_rate = 5.25
    kr_base_rate = 3.50
    fed_rate_history = [5.25, 5.00, 4.75, 4.50, 4.25]
    kr_rate_history = [3.50, 3.50, 3.25, 3.00, 2.75]

    # Test 1: Interest Rate Analysis
    print("📊 Test 2-1: 금리 분석")
    rate_analysis = analyzer.analyze_interest_rates(
        us_fed_rate,
        kr_base_rate,
        fed_rate_history,
        kr_rate_history
    )

    print(f"  US Fed Rate: {rate_analysis['current_rates']['us_fed_rate']:.2f}%")
    print(f"  KR Base Rate: {rate_analysis['current_rates']['kr_base_rate']:.2f}%")
    print(f"  Spread: {rate_analysis['current_rates']['spread']:+.2f}%p\n")

    print(f"  US Trend: {rate_analysis['trends']['us_fed']}")
    print(f"  KR Trend: {rate_analysis['trends']['kr_base']}\n")

    print("  Warnings:")
    for warning in rate_analysis['warnings']:
        print(f"    {warning}")

    print("\n  Beneficiary Sectors:")
    for sector in rate_analysis['impact']['beneficiary_sectors']:
        print(f"    • {sector}")

    # Test 2: Yield Curve Analysis
    print("\n📊 Test 2-2: 수익률 곡선 분석")
    yc_analysis = analyzer.analyze_yield_curve(
        treasury_2y=4.85,
        treasury_10y=4.55  # 역전!
    )

    print(f"  Yield Curve Shape: {yc_analysis['yield_curve_shape']}")
    print(f"  Recession Signal: {yc_analysis['recession_signal']}")
    print(f"  Recession Probability: {yc_analysis['recession_probability']:.0f}%")
    print(f"  10Y-2Y Spread: {yc_analysis['spreads']['10y_2y']:+.2f}%p\n")

    print(f"  Investment Strategy:")
    print(f"    {yc_analysis['investment_strategy']}\n")

    # Test 3: Exchange Rate Analysis
    print("📊 Test 2-3: 환율 분석")
    fx_analysis = analyzer.analyze_exchange_rate(
        usd_krw=1330.50,
        usd_krw_history=[1330.50, 1325.00, 1320.00, 1315.00, 1310.00]
    )

    print(f"  USD/KRW: {fx_analysis['current_rate']:.2f}원")
    print(f"  Strength: {fx_analysis['strength']}")
    print(f"  Trend: {fx_analysis['trend']}\n")

    print("  Warnings:")
    for warning in fx_analysis['warnings']:
        print(f"    {warning}")

    print_success("Economic Analyzer 테스트 완료!\n")


def test_signal_generator():
    """Test Signal Generator"""
    print_section("TEST 3: Signal Generator")

    generator = SignalGenerator()
    print_success("SignalGenerator 초기화 완료\n")

    # Test data
    sp500_data = {
        'close': 4550.50,
        'ma20': 4530.00,
        'ma60': 4480.00,
        'change_pct': -1.2
    }

    nasdaq_data = {
        'close': 14200.30,
        'change_pct': -0.8
    }

    fear_greed_score = 35.5  # Fear
    fed_rate = 5.25
    kr_base_rate = 3.50
    usd_krw = 1330.50

    yield_curve_data = {
        '2y': 4.85,
        '10y': 4.55  # 역전
    }

    # Test: Comprehensive Signal Generation
    print("📊 Test 3-1: 종합 투자 신호 생성")
    signal = generator.generate_comprehensive_signal(
        sp500_data,
        nasdaq_data,
        fear_greed_score,
        fed_rate,
        kr_base_rate,
        usd_krw,
        yield_curve_data
    )

    print(f"  Final Signal: {signal['signal']}")
    print(f"  Score: {signal['score']:.1f}")
    print(f"  Confidence: {signal['confidence']:.0f}%\n")

    print("  Signal Breakdown:")
    for key, value in signal['breakdown'].items():
        if value:
            print(f"    • {key}: {value}")

    print("\n  Action Plan:")
    print(f"    Action: {signal['action_plan']['action']}")
    print(f"    Timeframe: {signal['action_plan']['timeframe']}\n")

    print("  Target Allocation:")
    for asset, allocation in signal['action_plan']['target_allocation'].items():
        print(f"    • {asset}: {allocation}")

    if signal['action_plan']['specific_sectors']:
        print("\n  Specific Sectors:")
        for sector in signal['action_plan']['specific_sectors'][:5]:
            print(f"    • {sector}")

    print("\n  Risk Management:")
    for risk in signal['action_plan']['risk_management'][:3]:
        print(f"    • {risk}")

    # Test: Daily Briefing
    print("\n📊 Test 3-2: 일일 브리핑 생성")
    briefing = generator.generate_daily_briefing(
        signal,
        sp500_change=-1.2,
        kospi_change=-0.8
    )

    print(briefing)

    print_success("Signal Generator 테스트 완료!\n")


def main():
    """Main test runner"""
    print_section("Analysis Modules Test Suite")
    print("분석 모듈 테스트를 시작합니다.\n")
    print("테스트 모듈:")
    print("  1. MarketCorrelationAnalyzer - 미국-한국 상관관계 분석")
    print("  2. EconomicAnalyzer - 경제 지표 분석")
    print("  3. SignalGenerator - 종합 투자 신호 생성")
    print()

    try:
        # Test 1: Market Correlation Analyzer
        test_market_correlation_analyzer()

        # Test 2: Economic Analyzer
        test_economic_analyzer()

        # Test 3: Signal Generator
        test_signal_generator()

        # Final Summary
        print_section("최종 결과")
        print_success("✨ 모든 분석 모듈 테스트 통과!")
        print()
        print("🎉 분석 모듈 구현 완료!")
        print()
        print("사용 가능한 기능:")
        print("  1. 미국-한국 시장 상관관계 분석")
        print("  2. S&P 500/NASDAQ 기반 한국 시장 예측")
        print("  3. 금리/환율/수익률 곡선 분석")
        print("  4. 섹터별 영향 분석")
        print("  5. 종합 투자 신호 생성")
        print("  6. 일일 브리핑 자동 생성")
        print()
        print("다음 단계:")
        print("  1. 데이터 수집 자동화 (스케줄러)")
        print("  2. 대시보드 구축 (Streamlit)")
        print("  3. 알림 시스템 (텔레그램/이메일)")
        print()

        return True

    except Exception as e:
        print(f"\n❌ 테스트 실패: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
