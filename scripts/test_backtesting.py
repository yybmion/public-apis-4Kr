#!/usr/bin/env python3
"""
Backtesting Test Script

백테스팅 모듈 테스트

Usage:
    python scripts/test_backtesting.py
"""

import sys
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime, timedelta

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.backtesting.backtest_engine import BacktestEngine
from app.backtesting.strategies import (
    MovingAverageStrategy,
    FearGreedStrategy,
    CombinedSignalStrategy
)


def print_section(title: str):
    """Print section header"""
    print(f"\n{'=' * 80}")
    print(f"  {title}")
    print(f"{'=' * 80}\n")


def print_success(msg: str):
    """Print success message"""
    print(f"✅ {msg}")


def generate_sample_data(days: int = 252) -> pd.DataFrame:
    """
    Generate sample market data for testing

    Args:
        days: Number of days (default: 252 = 1 year)

    Returns:
        Sample data DataFrame
    """
    print("📊 샘플 데이터 생성 중...")

    # Generate dates
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    dates = pd.date_range(start=start_date, end=end_date, freq='D')

    # Generate price data (random walk with trend)
    np.random.seed(42)

    # Base price with upward trend
    trend = np.linspace(100, 120, len(dates))
    noise = np.random.randn(len(dates)) * 2
    prices = trend + noise.cumsum() * 0.5

    # Ensure positive prices
    prices = np.maximum(prices, 50)

    # Calculate moving averages
    price_series = pd.Series(prices, index=dates)
    ma_20 = price_series.rolling(window=20).mean()
    ma_60 = price_series.rolling(window=60).mean()

    # Generate Fear & Greed (oscillating between 20-80)
    fear_greed = 50 + 25 * np.sin(np.arange(len(dates)) / 20) + np.random.randn(len(dates)) * 5
    fear_greed = np.clip(fear_greed, 0, 100)

    # Generate interest rates
    fed_rate = 5.25 + np.random.randn(len(dates)) * 0.1
    kr_rate = 3.50 + np.random.randn(len(dates)) * 0.1

    # Create DataFrame
    data = pd.DataFrame({
        'close': prices,
        'ma_20': ma_20,
        'ma_60': ma_60,
        'fear_greed': fear_greed,
        'fed_rate': fed_rate,
        'kr_rate': kr_rate
    }, index=dates)

    # Fill NaN values for MA
    data['ma_20'].fillna(method='bfill', inplace=True)
    data['ma_60'].fillna(method='bfill', inplace=True)

    print_success(f"샘플 데이터 생성 완료: {len(data)}일")
    print(f"   기간: {data.index[0].strftime('%Y-%m-%d')} ~ {data.index[-1].strftime('%Y-%m-%d')}")
    print(f"   시작 가격: ${data['close'].iloc[0]:.2f}")
    print(f"   종료 가격: ${data['close'].iloc[-1]:.2f}")
    print()

    return data


def test_moving_average_strategy():
    """Test Moving Average Strategy"""
    print_section("TEST 1: Moving Average Strategy")

    # Generate data
    data = generate_sample_data(days=252)

    # Create strategy
    strategy = MovingAverageStrategy()

    # Create backtest engine
    engine = BacktestEngine(
        initial_capital=10000000,  # 1천만원
        commission=0.0015,
        slippage=0.001
    )

    print("🚀 백테스팅 실행 중...")

    # Run backtest
    result = engine.run(data, strategy.generate_signal)

    print_success("백테스팅 완료!\n")

    # Print report
    report = engine.generate_report(result, "Moving Average Strategy")
    print(report)

    # Compare to buy & hold
    print("📊 Buy & Hold 벤치마크 계산 중...")
    benchmark = engine.run_buy_and_hold(data)

    comparison = engine.compare_to_benchmark(result, benchmark)

    print(f"\n📈 벤치마크 대비 성과:")
    print(f"   Alpha (초과 수익률): {comparison['alpha_pct']:+.2f}%")
    print(f"   Beta: {comparison['beta']:.3f}")
    print(f"   Excess Return: {comparison['excess_return_pct']:+.2f}%")

    return result, benchmark


def test_fear_greed_strategy():
    """Test Fear & Greed Strategy"""
    print_section("TEST 2: Fear & Greed Strategy")

    # Generate data
    data = generate_sample_data(days=252)

    # Create strategy
    strategy = FearGreedStrategy()

    # Create backtest engine
    engine = BacktestEngine(initial_capital=10000000)

    print("🚀 백테스팅 실행 중...")

    # Run backtest
    result = engine.run(data, strategy.generate_signal)

    print_success("백테스팅 완료!\n")

    # Print report
    report = engine.generate_report(result, "Fear & Greed Strategy")
    print(report)

    return result


def test_combined_strategy():
    """Test Combined Signal Strategy"""
    print_section("TEST 3: Combined Signal Strategy")

    # Generate data
    data = generate_sample_data(days=252)

    # Create strategy
    strategy = CombinedSignalStrategy()

    # Create backtest engine
    engine = BacktestEngine(initial_capital=10000000)

    print("🚀 백테스팅 실행 중...")

    # Run backtest
    result = engine.run(data, strategy.generate_signal)

    print_success("백테스팅 완료!\n")

    # Print report
    report = engine.generate_report(result, "Combined Signal Strategy")
    print(report)

    # Compare to buy & hold
    benchmark = engine.run_buy_and_hold(data)
    comparison = engine.compare_to_benchmark(result, benchmark)

    print(f"\n📈 벤치마크 대비 성과:")
    print(f"   Strategy CAGR: {comparison['strategy']['cagr_pct']:.2f}%")
    print(f"   Benchmark CAGR: {comparison['benchmark']['cagr_pct']:.2f}%")
    print(f"   Alpha: {comparison['alpha_pct']:+.2f}%")
    print(f"   Beta: {comparison['beta']:.3f}")

    print(f"\n   Strategy MDD: {comparison['strategy']['max_drawdown_pct']:.2f}%")
    print(f"   Benchmark MDD: {comparison['benchmark']['max_drawdown_pct']:.2f}%")

    print(f"\n   Strategy Sharpe: {comparison['strategy']['sharpe_ratio']:.3f}")
    print(f"   Benchmark Sharpe: {comparison['benchmark']['sharpe_ratio']:.3f}")

    return result, benchmark


def test_visualization():
    """Test visualization"""
    print_section("TEST 4: Visualization")

    try:
        import plotly

        print("📊 차트 생성 중...")

        # Generate data
        data = generate_sample_data(days=252)

        # Run strategy
        strategy = CombinedSignalStrategy()
        engine = BacktestEngine(initial_capital=10000000)

        result = engine.run(data, strategy.generate_signal)
        benchmark = engine.run_buy_and_hold(data)

        # Create chart
        fig = engine.plot_equity_curve(result, benchmark)

        if fig:
            # Save to HTML
            output_file = project_root / 'backtest_result.html'
            fig.write_html(str(output_file))

            print_success(f"차트 저장 완료: {output_file}")
            print(f"   브라우저에서 열어보세요!")
        else:
            print("⚠️  차트 생성 실패")

    except ImportError:
        print("⚠️  Plotly가 설치되지 않았습니다.")
        print("   설치: pip install plotly")


def main():
    """Main test runner"""
    print_section("Backtesting Module Test Suite")
    print("백테스팅 모듈 테스트를 시작합니다.\n")
    print("테스트 시나리오:")
    print("  1. Moving Average Strategy (이동평균선 전략)")
    print("  2. Fear & Greed Strategy (역발상 전략)")
    print("  3. Combined Signal Strategy (통합 신호 전략)")
    print("  4. Visualization (시각화)")
    print()

    try:
        # Test 1: MA Strategy
        ma_result, ma_benchmark = test_moving_average_strategy()

        # Test 2: Fear & Greed Strategy
        fg_result = test_fear_greed_strategy()

        # Test 3: Combined Strategy
        combined_result, combined_benchmark = test_combined_strategy()

        # Test 4: Visualization
        test_visualization()

        # Final Summary
        print_section("최종 결과")
        print_success("✨ 모든 테스트 통과!")
        print()
        print("🎉 백테스팅 모듈 구현 완료!")
        print()
        print("사용 가능한 기능:")
        print("  1. 과거 데이터 백테스팅")
        print("  2. 성과 지표 계산 (수익률, MDD, 샤프)")
        print("  3. 전략 비교 (벤치마크 대비)")
        print("  4. 거래 통계 (승률, 손익비)")
        print("  5. 자산 곡선 시각화")
        print()
        print("다음 단계:")
        print("  1. 실제 데이터로 백테스팅")
        print("  2. 전략 파라미터 최적화")
        print("  3. 대시보드에 통합")
        print("  4. 알림 시스템 구현")
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
