"""
Backtesting Page - 백테스팅

전략 백테스팅 및 성과 비교

Author: AI Assistant
Created: 2025-11-22
"""

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from app.backtesting.backtest_engine import BacktestEngine
from app.backtesting.strategies import (
    MovingAverageStrategy,
    FearGreedStrategy,
    CombinedSignalStrategy
)


def generate_sample_data(days: int = 252) -> pd.DataFrame:
    """
    Generate sample data for backtesting demo

    Args:
        days: Number of days

    Returns:
        DataFrame with price and indicator data
    """
    dates = pd.date_range(end=datetime.now(), periods=days, freq='D')

    # Generate realistic price data
    np.random.seed(42)
    returns = np.random.randn(days) * 0.02 + 0.0003
    price = 100 * np.exp(np.cumsum(returns))

    df = pd.DataFrame({
        'close': price,
        'ma_20': pd.Series(price).rolling(20).mean(),
        'ma_60': pd.Series(price).rolling(60).mean(),
        'fear_greed': 50 + 25 * np.sin(np.arange(days) / 10) + np.random.randn(days) * 10,
        'fed_rate': 5.5 + np.random.randn(days) * 0.1,
        'kr_rate': 3.5 + np.random.randn(days) * 0.1
    }, index=dates)

    # Clip fear_greed to 0-100
    df['fear_greed'] = df['fear_greed'].clip(0, 100)

    return df.dropna()


def display_metrics(result: dict, title: str):
    """Display performance metrics"""
    metrics = result['metrics']

    st.markdown(f"### {title}")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "총 수익률",
            f"{metrics['total_return_pct']:+.2f}%",
            help="전체 기간 수익률"
        )
        st.metric(
            "CAGR",
            f"{metrics['cagr_pct']:.2f}%",
            help="연환산 수익률"
        )

    with col2:
        st.metric(
            "최대 낙폭 (MDD)",
            f"{metrics['max_drawdown_pct']:.2f}%",
            help="최대 손실폭"
        )
        st.metric(
            "변동성",
            f"{metrics['volatility_pct']:.2f}%",
            help="연환산 변동성"
        )

    with col3:
        st.metric(
            "샤프 비율",
            f"{metrics['sharpe_ratio']:.3f}",
            help="위험 조정 수익률"
        )
        st.metric(
            "소르티노 비율",
            f"{metrics['sortino_ratio']:.3f}",
            help="하방 위험만 고려"
        )

    with col4:
        st.metric(
            "승률",
            f"{metrics['win_rate'] * 100:.1f}%",
            help="승리 거래 비율"
        )
        st.metric(
            "손익비",
            f"{metrics['profit_factor']:.2f}",
            help=">1.0이면 수익"
        )


def display_benchmark_comparison(result: dict, benchmark: dict, engine: BacktestEngine):
    """Display benchmark comparison"""
    comparison = engine.compare_to_benchmark(result, benchmark)

    st.markdown("### 벤치마크 대비 성과")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "Alpha (초과 수익)",
            f"{comparison['alpha_pct']:+.2f}%",
            help="벤치마크 대비 초과 수익률"
        )

    with col2:
        st.metric(
            "Beta (시장 민감도)",
            f"{comparison['beta']:.3f}",
            help="1.0 = 시장과 동일"
        )

    with col3:
        st.metric(
            "초과 수익률",
            f"{comparison['excess_return_pct']:+.2f}%",
            help="전략 - 벤치마크"
        )

    with col4:
        outperformance = "✅ 우수" if comparison['excess_return_pct'] > 0 else "❌ 미달"
        st.metric(
            "벤치마크 대비",
            outperformance
        )


def plot_equity_curves(results: dict, benchmark: dict, engine: BacktestEngine):
    """Plot equity curves for all strategies"""
    fig = go.Figure()

    # Benchmark
    benchmark_equity = benchmark['equity_curve']
    fig.add_trace(go.Scatter(
        x=benchmark_equity.index,
        y=benchmark_equity.values,
        mode='lines',
        name='Buy & Hold (벤치마크)',
        line=dict(color='gray', width=2, dash='dash')
    ))

    # Strategies
    colors = ['#2ecc71', '#3498db', '#e74c3c']
    for i, (strategy_name, result) in enumerate(results.items()):
        equity = result['equity_curve']

        fig.add_trace(go.Scatter(
            x=equity.index,
            y=equity.values,
            mode='lines',
            name=strategy_name,
            line=dict(color=colors[i % len(colors)], width=2)
        ))

    fig.update_layout(
        title="전략별 자산 곡선 비교",
        xaxis_title="날짜",
        yaxis_title="자산 가치",
        height=500,
        hovermode='x unified',
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )

    st.plotly_chart(fig, use_container_width=True)


def plot_drawdown_comparison(results: dict):
    """Plot drawdown comparison"""
    fig = go.Figure()

    colors = ['#2ecc71', '#3498db', '#e74c3c']
    for i, (strategy_name, result) in enumerate(results.items()):
        metrics = result['metrics']
        drawdown = metrics['drawdown_series']

        fig.add_trace(go.Scatter(
            x=drawdown.index,
            y=drawdown.values * 100,  # Convert to percentage
            mode='lines',
            name=strategy_name,
            line=dict(color=colors[i % len(colors)], width=2),
            fill='tozeroy'
        ))

    fig.update_layout(
        title="전략별 낙폭 비교",
        xaxis_title="날짜",
        yaxis_title="낙폭 (%)",
        height=400,
        hovermode='x unified'
    )

    st.plotly_chart(fig, use_container_width=True)


def plot_metrics_comparison(results: dict):
    """Plot metrics comparison radar chart"""
    strategies = list(results.keys())

    # Normalize metrics for radar chart (0-100 scale)
    metrics_data = {
        'CAGR': [],
        'Sharpe Ratio': [],
        'Win Rate': [],
        'Profit Factor': [],
        'Recovery': []  # Inverse of MDD
    }

    for strategy_name in strategies:
        metrics = results[strategy_name]['metrics']

        # Normalize each metric to 0-100 scale
        cagr = min(max(metrics['cagr_pct'], -20), 40)  # -20% to 40%
        cagr_norm = ((cagr + 20) / 60) * 100

        sharpe = min(max(metrics['sharpe_ratio'], -1), 3)  # -1 to 3
        sharpe_norm = ((sharpe + 1) / 4) * 100

        win_rate_norm = metrics['win_rate'] * 100

        profit_factor = min(max(metrics['profit_factor'], 0), 3)  # 0 to 3
        profit_norm = (profit_factor / 3) * 100

        # Recovery (inverse of MDD)
        mdd = abs(metrics['max_drawdown_pct'])
        recovery_norm = max(0, (30 - mdd) / 30 * 100)  # 0-30% MDD

        metrics_data['CAGR'].append(cagr_norm)
        metrics_data['Sharpe Ratio'].append(sharpe_norm)
        metrics_data['Win Rate'].append(win_rate_norm)
        metrics_data['Profit Factor'].append(profit_norm)
        metrics_data['Recovery'].append(recovery_norm)

    fig = go.Figure()

    colors = ['#2ecc71', '#3498db', '#e74c3c']
    for i, strategy_name in enumerate(strategies):
        values = [
            metrics_data['CAGR'][i],
            metrics_data['Sharpe Ratio'][i],
            metrics_data['Win Rate'][i],
            metrics_data['Profit Factor'][i],
            metrics_data['Recovery'][i]
        ]

        fig.add_trace(go.Scatterpolar(
            r=values + [values[0]],  # Close the polygon
            theta=list(metrics_data.keys()) + [list(metrics_data.keys())[0]],
            fill='toself',
            name=strategy_name,
            line=dict(color=colors[i % len(colors)])
        ))

    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100]
            )
        ),
        title="전략별 성과 지표 비교",
        height=500
    )

    st.plotly_chart(fig, use_container_width=True)


def show():
    """Show backtesting page"""
    st.title("📊 백테스팅")

    st.markdown("""
    투자 전략의 과거 성과를 시뮬레이션하고 비교합니다.
    """)

    # Sidebar - Parameters
    st.sidebar.markdown("## 백테스팅 설정")

    # Initial capital
    initial_capital = st.sidebar.number_input(
        "초기 자본 (원)",
        min_value=1000000,
        max_value=1000000000,
        value=10000000,
        step=1000000,
        help="백테스팅 시작 자본"
    )

    # Commission
    commission = st.sidebar.number_input(
        "거래 수수료 (%)",
        min_value=0.0,
        max_value=1.0,
        value=0.15,
        step=0.01,
        help="한국: 0.15%, 미국: 0.01%"
    ) / 100

    # Slippage
    slippage = st.sidebar.number_input(
        "슬리피지 (%)",
        min_value=0.0,
        max_value=1.0,
        value=0.1,
        step=0.05,
        help="가격 변동으로 인한 손실"
    ) / 100

    # Risk-free rate
    risk_free_rate = st.sidebar.number_input(
        "무위험 수익률 (%)",
        min_value=0.0,
        max_value=10.0,
        value=3.0,
        step=0.1,
        help="국고채 수익률"
    ) / 100

    # Backtest period
    period_days = st.sidebar.selectbox(
        "백테스팅 기간",
        [252, 504, 756, 1260],
        index=0,
        format_func=lambda x: f"{x//252}년 ({x}일)"
    )

    # Strategy selection
    st.sidebar.markdown("## 전략 선택")

    run_ma = st.sidebar.checkbox("Moving Average Strategy", value=True)
    run_fg = st.sidebar.checkbox("Fear & Greed Strategy", value=True)
    run_combined = st.sidebar.checkbox("Combined Signal Strategy", value=True)

    # Run backtest button
    run_backtest = st.sidebar.button("🚀 백테스팅 실행", type="primary")

    # Main content
    if run_backtest:
        if not any([run_ma, run_fg, run_combined]):
            st.warning("⚠️ 최소 하나의 전략을 선택해주세요.")
            return

        with st.spinner("백테스팅 실행 중..."):
            # Generate sample data
            data = generate_sample_data(days=period_days)

            # Initialize engine
            engine = BacktestEngine(
                initial_capital=initial_capital,
                commission=commission,
                slippage=slippage,
                risk_free_rate=risk_free_rate
            )

            # Run benchmark
            benchmark = engine.run_buy_and_hold(data)

            # Run selected strategies
            results = {}

            if run_ma:
                with st.spinner("Moving Average Strategy 실행 중..."):
                    strategy = MovingAverageStrategy()
                    result = engine.run(data, strategy.generate_signal)
                    results['Moving Average'] = result

            if run_fg:
                with st.spinner("Fear & Greed Strategy 실행 중..."):
                    strategy = FearGreedStrategy()
                    result = engine.run(data, strategy.generate_signal)
                    results['Fear & Greed'] = result

            if run_combined:
                with st.spinner("Combined Signal Strategy 실행 중..."):
                    strategy = CombinedSignalStrategy()
                    result = engine.run(data, strategy.generate_signal)
                    results['Combined Signal'] = result

        st.success("✅ 백테스팅 완료!")

        # Display results
        st.markdown("---")

        # Equity curves
        st.markdown("## 📈 자산 곡선")
        plot_equity_curves(results, benchmark, engine)

        st.markdown("---")

        # Metrics comparison
        st.markdown("## 📊 성과 지표 비교")

        # Create comparison table
        comparison_data = {
            '전략': [],
            'CAGR (%)': [],
            'MDD (%)': [],
            'Sharpe': [],
            'Sortino': [],
            '승률 (%)': [],
            '손익비': [],
            'Alpha (%)': []
        }

        for strategy_name, result in results.items():
            metrics = result['metrics']
            comparison = engine.compare_to_benchmark(result, benchmark)

            comparison_data['전략'].append(strategy_name)
            comparison_data['CAGR (%)'].append(f"{metrics['cagr_pct']:.2f}")
            comparison_data['MDD (%)'].append(f"{metrics['max_drawdown_pct']:.2f}")
            comparison_data['Sharpe'].append(f"{metrics['sharpe_ratio']:.3f}")
            comparison_data['Sortino'].append(f"{metrics['sortino_ratio']:.3f}")
            comparison_data['승률 (%)'].append(f"{metrics['win_rate'] * 100:.1f}")
            comparison_data['손익비'].append(f"{metrics['profit_factor']:.2f}")
            comparison_data['Alpha (%)'].append(f"{comparison['alpha_pct']:+.2f}")

        # Add benchmark
        bench_metrics = benchmark['metrics']
        comparison_data['전략'].append('Buy & Hold (벤치마크)')
        comparison_data['CAGR (%)'].append(f"{bench_metrics['cagr_pct']:.2f}")
        comparison_data['MDD (%)'].append(f"{bench_metrics['max_drawdown_pct']:.2f}")
        comparison_data['Sharpe'].append(f"{bench_metrics['sharpe_ratio']:.3f}")
        comparison_data['Sortino'].append(f"{bench_metrics['sortino_ratio']:.3f}")
        comparison_data['승률 (%)'].append(f"{bench_metrics['win_rate'] * 100:.1f}")
        comparison_data['손익비'].append(f"{bench_metrics['profit_factor']:.2f}")
        comparison_data['Alpha (%)'].append("0.00")

        df_comparison = pd.DataFrame(comparison_data)
        st.dataframe(df_comparison, use_container_width=True, hide_index=True)

        st.markdown("---")

        # Radar chart
        plot_metrics_comparison(results)

        st.markdown("---")

        # Drawdown comparison
        st.markdown("## 📉 낙폭 비교")
        plot_drawdown_comparison(results)

        st.markdown("---")

        # Individual strategy details
        st.markdown("## 📋 전략별 상세 성과")

        for strategy_name, result in results.items():
            with st.expander(f"🔍 {strategy_name} 상세", expanded=False):
                display_metrics(result, strategy_name)

                st.markdown("---")

                display_benchmark_comparison(result, benchmark, engine)

                st.markdown("---")

                # Trade history
                trades = result.get('trades', [])
                if trades:
                    st.markdown("### 거래 내역")

                    trade_data = {
                        '날짜': [t['date'].strftime('%Y-%m-%d') for t in trades],
                        '유형': [t['type'] for t in trades],
                        '가격': [f"{t['price']:.2f}" for t in trades],
                        '수량': [f"{t['shares']:.2f}" for t in trades],
                        '금액': [f"{t['amount']:,.0f}" for t in trades]
                    }

                    # Add profit if available
                    if 'profit' in trades[0]:
                        trade_data['손익'] = [f"{t.get('profit', 0):+,.0f}" for t in trades]

                    df_trades = pd.DataFrame(trade_data)
                    st.dataframe(df_trades, use_container_width=True, hide_index=True)
                else:
                    st.info("거래 내역이 없습니다.")

    else:
        # Show instructions
        st.info("👈 왼쪽 사이드바에서 설정을 조정하고 '백테스팅 실행' 버튼을 클릭하세요.")

        st.markdown("### 💡 사용 방법")

        st.markdown("""
        1. **초기 자본**: 백테스팅 시작 자본을 설정합니다 (기본값: 1,000만원)
        2. **거래 수수료**: 한국 시장은 0.15%, 미국 시장은 0.01% 권장
        3. **슬리피지**: 가격 변동으로 인한 손실 (0.1% 권장)
        4. **백테스팅 기간**: 1년(252일)부터 5년(1260일)까지 선택
        5. **전략 선택**: 테스트할 전략을 선택합니다
        6. **실행**: 백테스팅 실행 버튼 클릭
        """)

        st.markdown("### 📊 전략 설명")

        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown("#### Moving Average")
            st.markdown("""
            이동평균선 기반 전략
            - 골든크로스: 강한 매수
            - 데드크로스: 강한 매도
            - 20일선 > 60일선: 매수
            """)

        with col2:
            st.markdown("#### Fear & Greed")
            st.markdown("""
            역발상 전략
            - 극단적 공포 (<25): 매수
            - 극단적 탐욕 (>75): 매도
            - 시장 심리 반대 포지션
            """)

        with col3:
            st.markdown("#### Combined Signal")
            st.markdown("""
            통합 신호 전략
            - Moving Average: 40%
            - Fear & Greed: 30%
            - Interest Rate: 30%
            - 가중 평균 신호
            """)

        st.markdown("---")

        st.markdown("### 📈 성과 지표 해석")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("""
            **수익률 지표**
            - **CAGR**: 연환산 수익률 (>20% 우수)
            - **Alpha**: 벤치마크 대비 초과 수익률
            - **총 수익률**: 전체 기간 수익률
            """)

        with col2:
            st.markdown("""
            **리스크 지표**
            - **MDD**: 최대 낙폭 (<10% 우수)
            - **Sharpe Ratio**: 샤프 비율 (>1.0 우수)
            - **Sortino Ratio**: 하방 위험만 고려
            """)

        st.markdown("""
        **거래 통계**
        - **승률**: 승리 거래 비율 (>60% 우수)
        - **손익비**: Profit Factor (>2.0 우수)
        - **평균 승/패**: 거래당 평균 수익/손실
        """)
