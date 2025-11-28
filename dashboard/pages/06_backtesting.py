"""
Backtesting Page
Stock Intelligence System
"""

import streamlit as st
import requests
import pandas as pd
from datetime import datetime, timedelta

# Page configuration
st.set_page_config(
    page_title="백테스팅 - Stock Intelligence System",
    page_icon="📊",
    layout="wide"
)

# API configuration
API_URL = "http://localhost:8000"


def check_api_health():
    """Check if API is running"""
    try:
        response = requests.get(f"{API_URL}/health", timeout=2)
        return response.status_code == 200
    except:
        return False


def run_backtest(config):
    """Run backtest"""
    try:
        response = requests.post(f"{API_URL}/api/v1/backtest/run", json=config)
        if response.status_code == 200:
            return response.json()['data']
        else:
            st.error(f"백테스트 실행 실패: {response.text}")
            return None
    except Exception as e:
        st.error(f"백테스트 오류: {str(e)}")
        return None


def get_backtest_results(limit=50, strategy=None):
    """Get backtest results"""
    try:
        params = {"limit": limit}
        if strategy:
            params["strategy"] = strategy

        response = requests.get(f"{API_URL}/api/v1/backtest/results", params=params)
        if response.status_code == 200:
            return response.json()['data']['results']
        return []
    except Exception as e:
        st.error(f"결과 조회 오류: {str(e)}")
        return []


def format_performance_metrics(result):
    """Format performance metrics for display"""
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        total_return = result['total_return']
        return_color = 'green' if total_return > 0 else 'red'
        st.markdown(
            f"<div style='background-color:{return_color}; padding:15px; border-radius:8px; text-align:center;'>"
            f"<span style='color:white; font-size:14px;'>총 수익률</span><br>"
            f"<span style='color:white; font-size:24px; font-weight:bold;'>{total_return:+.2f}%</span>"
            f"</div>",
            unsafe_allow_html=True
        )

    with col2:
        cagr = result['cagr']
        cagr_color = 'green' if cagr > 10 else 'orange' if cagr > 5 else 'red'
        st.markdown(
            f"<div style='background-color:{cagr_color}; padding:15px; border-radius:8px; text-align:center;'>"
            f"<span style='color:white; font-size:14px;'>연평균 수익률 (CAGR)</span><br>"
            f"<span style='color:white; font-size:24px; font-weight:bold;'>{cagr:.2f}%</span>"
            f"</div>",
            unsafe_allow_html=True
        )

    with col3:
        mdd = result['max_drawdown']
        mdd_color = 'green' if abs(mdd) < 15 else 'orange' if abs(mdd) < 25 else 'red'
        st.markdown(
            f"<div style='background-color:{mdd_color}; padding:15px; border-radius:8px; text-align:center;'>"
            f"<span style='color:white; font-size:14px;'>최대 낙폭 (MDD)</span><br>"
            f"<span style='color:white; font-size:24px; font-weight:bold;'>{mdd:.2f}%</span>"
            f"</div>",
            unsafe_allow_html=True
        )

    with col4:
        sharpe = result['sharpe_ratio']
        sharpe_color = 'green' if sharpe > 1.5 else 'orange' if sharpe > 1.0 else 'red'
        st.markdown(
            f"<div style='background-color:{sharpe_color}; padding:15px; border-radius:8px; text-align:center;'>"
            f"<span style='color:white; font-size:14px;'>샤프 비율</span><br>"
            f"<span style='color:white; font-size:24px; font-weight:bold;'>{sharpe:.2f}</span>"
            f"</div>",
            unsafe_allow_html=True
        )


# ==================== Main Page ====================

st.title("📊 백테스팅")
st.markdown("### 투자 전략 성과 검증")

# Check API status
if not check_api_health():
    st.error("⚠️ API 서버에 연결할 수 없습니다.")
    st.stop()

# Tabs
tab1, tab2 = st.tabs(["백테스트 실행", "결과 이력"])

# ==================== Tab 1: Run Backtest ====================

with tab1:
    st.header("🚀 백테스트 실행")

    st.markdown(
        """
        투자 전략의 과거 성과를 시뮬레이션하여 검증합니다.

        **제공 전략:**
        - **S&P 500 MA 전략**: S&P 500이 20일 이동평균선 위에 있을 때 한국 주식 매수
        - **골든크로스 전략**: 5일 이동평균선이 20일 이동평균선을 상향 돌파할 때 매수
        """
    )

    with st.form("backtest_form"):
        col1, col2 = st.columns(2)

        with col1:
            stock_code = st.text_input(
                "종목코드 (6자리)",
                placeholder="예: 005930",
                help="백테스트할 종목의 6자리 코드를 입력하세요."
            )

            strategy = st.selectbox(
                "전략 선택",
                options=["sp500_ma", "golden_cross"],
                format_func=lambda x: {
                    "sp500_ma": "S&P 500 MA(20) 전략",
                    "golden_cross": "골든크로스 전략"
                }[x],
                help="테스트할 투자 전략을 선택하세요."
            )

            initial_cash = st.number_input(
                "초기 자본 (원)",
                min_value=1_000_000,
                max_value=1_000_000_000,
                value=10_000_000,
                step=1_000_000,
                help="백테스트를 시작할 초기 자본금을 입력하세요."
            )

        with col2:
            # Date range
            end_date = st.date_input(
                "종료일",
                value=datetime.now(),
                help="백테스트 종료 날짜"
            )

            start_date = st.date_input(
                "시작일",
                value=end_date - timedelta(days=365),
                help="백테스트 시작 날짜"
            )

            # Strategy-specific parameters
            if strategy == "sp500_ma":
                ma_period = st.slider(
                    "이동평균 기간",
                    min_value=5,
                    max_value=60,
                    value=20,
                    help="S&P 500의 이동평균선 기간을 선택하세요."
                )
            else:
                col_a, col_b = st.columns(2)
                with col_a:
                    fast_period = st.slider("단기 MA", 5, 20, 5)
                with col_b:
                    slow_period = st.slider("장기 MA", 10, 60, 20)

        submitted = st.form_submit_button("백테스트 실행", type="primary", use_container_width=True)

        if submitted:
            if not stock_code or len(stock_code) != 6:
                st.error("올바른 6자리 종목코드를 입력하세요.")
            else:
                with st.spinner(f"{stock_code} 백테스트 실행 중... (수 분이 걸릴 수 있습니다)"):
                    config = {
                        "stock_code": stock_code,
                        "strategy": strategy,
                        "start_date": start_date.strftime('%Y-%m-%d'),
                        "end_date": end_date.strftime('%Y-%m-%d'),
                        "initial_cash": initial_cash
                    }

                    if strategy == "sp500_ma":
                        config["ma_period"] = ma_period
                    else:
                        config["fast_period"] = fast_period
                        config["slow_period"] = slow_period

                    result = run_backtest(config)

                    if result:
                        st.success(f"✅ 백테스트 완료!")

                        # Display strategy info
                        st.subheader("전략 정보")
                        col1, col2, col3 = st.columns(3)

                        with col1:
                            st.write(f"**전략:** {result['strategy_name']}")
                        with col2:
                            st.write(f"**종목:** {stock_code}")
                        with col3:
                            st.write(f"**기간:** {result['start_date']} ~ {result['end_date']}")

                        st.divider()

                        # Performance metrics
                        st.subheader("성과 지표")
                        format_performance_metrics(result)

                        st.divider()

                        # Capital and trading
                        st.subheader("자본 변화")
                        col1, col2, col3 = st.columns(3)

                        with col1:
                            st.metric("초기 자본", f"{result['initial_capital']:,.0f}원")
                        with col2:
                            profit = result['final_capital'] - result['initial_capital']
                            st.metric(
                                "최종 자본",
                                f"{result['final_capital']:,.0f}원",
                                f"{profit:+,.0f}원"
                            )
                        with col3:
                            st.metric("손익", f"{profit:+,.0f}원", f"{result['total_return']:+.2f}%")

                        st.divider()

                        # Trading statistics
                        st.subheader("거래 통계")
                        col1, col2 = st.columns(2)

                        with col1:
                            st.metric("총 거래 횟수", f"{result['total_trades']}회")
                        with col2:
                            st.metric("승률", f"{result['win_rate']:.1f}%")

                        st.divider()

                        # Assessment
                        st.subheader("종합 평가")

                        assessments = []

                        # Return assessment
                        if result['cagr'] > 15:
                            assessments.append("✅ 우수한 수익률")
                        elif result['cagr'] > 10:
                            assessments.append("✅ 양호한 수익률")
                        elif result['cagr'] > 5:
                            assessments.append("⚠️ 평균적인 수익률")
                        else:
                            assessments.append("❌ 낮은 수익률")

                        # Risk assessment
                        if abs(result['max_drawdown']) < 15:
                            assessments.append("✅ 낮은 리스크 (MDD < 15%)")
                        elif abs(result['max_drawdown']) < 25:
                            assessments.append("⚠️ 중간 리스크 (MDD 15-25%)")
                        else:
                            assessments.append("❌ 높은 리스크 (MDD > 25%)")

                        # Sharpe assessment
                        if result['sharpe_ratio'] > 1.5:
                            assessments.append("✅ 우수한 위험 대비 수익")
                        elif result['sharpe_ratio'] > 1.0:
                            assessments.append("✅ 양호한 위험 대비 수익")
                        elif result['sharpe_ratio'] > 0.5:
                            assessments.append("⚠️ 보통의 위험 대비 수익")
                        else:
                            assessments.append("❌ 낮은 위험 대비 수익")

                        for assessment in assessments:
                            st.write(assessment)

# ==================== Tab 2: Results History ====================

with tab2:
    st.header("📚 백테스트 결과 이력")

    col1, col2 = st.columns([3, 1])

    with col1:
        history_limit = st.slider("표시할 결과 수", min_value=10, max_value=100, value=50)

    with col2:
        strategy_filter = st.selectbox(
            "전략 필터",
            options=[None, "SP500MAStrategy", "GoldenCrossStrategy"],
            format_func=lambda x: "전체" if x is None else x
        )

    if st.button("이력 조회"):
        with st.spinner("이력 조회 중..."):
            results = get_backtest_results(limit=history_limit, strategy=strategy_filter)

            if results:
                st.success(f"✅ {len(results)}개 백테스트 결과 조회")

                # Convert to DataFrame
                df = pd.DataFrame(results)

                # Display summary table
                st.dataframe(
                    df[[
                        'created_at', 'strategy_name', 'start_date', 'end_date',
                        'total_return', 'cagr', 'mdd', 'sharpe_ratio'
                    ]],
                    column_config={
                        "created_at": "실행 시간",
                        "strategy_name": "전략",
                        "start_date": "시작일",
                        "end_date": "종료일",
                        "total_return": st.column_config.NumberColumn("총 수익률 (%)", format="%.2f"),
                        "cagr": st.column_config.NumberColumn("CAGR (%)", format="%.2f"),
                        "mdd": st.column_config.NumberColumn("MDD (%)", format="%.2f"),
                        "sharpe_ratio": st.column_config.NumberColumn("샤프 비율", format="%.2f")
                    },
                    hide_index=True,
                    use_container_width=True
                )

                # Statistics
                st.subheader("통계")
                col1, col2, col3, col4 = st.columns(4)

                with col1:
                    st.metric("총 백테스트 수", f"{len(df)}회")

                with col2:
                    avg_return = df['total_return'].mean()
                    st.metric("평균 수익률", f"{avg_return:.2f}%")

                with col3:
                    avg_sharpe = df['sharpe_ratio'].mean()
                    st.metric("평균 샤프 비율", f"{avg_sharpe:.2f}")

                with col4:
                    profitable = len(df[df['total_return'] > 0])
                    success_rate = (profitable / len(df)) * 100
                    st.metric("수익 전략 비율", f"{success_rate:.1f}%")

                # Best strategy
                if len(df) > 0:
                    st.subheader("최고 성과 전략")
                    best = df.loc[df['sharpe_ratio'].idxmax()]

                    col1, col2, col3 = st.columns(3)

                    with col1:
                        st.write(f"**전략:** {best['strategy_name']}")
                        st.write(f"**기간:** {best['start_date']} ~ {best['end_date']}")

                    with col2:
                        st.metric("총 수익률", f"{best['total_return']:.2f}%")
                        st.metric("CAGR", f"{best['cagr']:.2f}%")

                    with col3:
                        st.metric("MDD", f"{best['mdd']:.2f}%")
                        st.metric("샤프 비율", f"{best['sharpe_ratio']:.2f}")

            else:
                st.info("백테스트 결과 이력이 없습니다.")

# Footer
st.divider()
st.markdown(
    """
    <div style='text-align: center; color: gray; padding: 20px;'>
        📊 Backtrader 기반 전략 백테스팅 | 목표 샤프 비율 > 1.0
    </div>
    """,
    unsafe_allow_html=True
)
