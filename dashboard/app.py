"""
Streamlit Dashboard
Stock Intelligence System
"""

import streamlit as st
import requests
import pandas as pd
from datetime import datetime
import plotly.graph_objects as go

# Page configuration
st.set_page_config(
    page_title="Stock Intelligence System",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
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


def get_market_overview():
    """Get market overview data"""
    try:
        response = requests.get(f"{API_URL}/api/v1/market/overview")
        if response.status_code == 200:
            return response.json()['data']
        return None
    except Exception as e:
        st.error(f"Error fetching market overview: {str(e)}")
        return None


def get_us_markets():
    """Get US market data"""
    try:
        response = requests.get(f"{API_URL}/api/v1/market/us")
        if response.status_code == 200:
            return response.json()['data']['indices']
        return []
    except Exception as e:
        st.error(f"Error fetching US markets: {str(e)}")
        return []


def get_stocks(market=None, limit=20):
    """Get stock list"""
    try:
        params = {"limit": limit}
        if market:
            params["market"] = market

        response = requests.get(f"{API_URL}/api/v1/stocks", params=params)
        if response.status_code == 200:
            return response.json()['data']['stocks']
        return []
    except Exception as e:
        st.error(f"Error fetching stocks: {str(e)}")
        return []


def collect_us_market_data():
    """Trigger US market data collection"""
    try:
        response = requests.post(f"{API_URL}/api/v1/market/us/collect")
        if response.status_code == 200:
            return response.json()
        return None
    except Exception as e:
        st.error(f"Error collecting US market data: {str(e)}")
        return None


# ==================== Main Dashboard ====================

st.title("📈 Stock Intelligence System")
st.markdown("### 한국 주식 자동매매 지원 시스템")

# Check API status
if not check_api_health():
    st.error("⚠️ API 서버에 연결할 수 없습니다. API 서버가 실행 중인지 확인하세요.")
    st.code("uvicorn app.main:app --reload", language="bash")
    st.stop()

st.success("✅ API 서버 연결됨")

# Sidebar
st.sidebar.title("메뉴")
page = st.sidebar.radio(
    "페이지 선택",
    ["시장 현황", "종목 조회", "미국 시장", "데이터 수집"]
)

# ==================== Page: 시장 현황 ====================

if page == "시장 현황":
    st.header("📊 시장 현황")

    # Get market overview
    overview = get_market_overview()

    if overview:
        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric(
                label="KOSPI 상장 종목",
                value=f"{overview['kospi']['total_stocks']:,}개"
            )

        with col2:
            st.metric(
                label="KOSDAQ 상장 종목",
                value=f"{overview['kosdaq']['total_stocks']:,}개"
            )

        with col3:
            signal = overview['us_markets']['sp500_signal']
            signal_emoji = "🟢" if signal == "BULLISH" else "🔴"
            st.metric(
                label="S&P 500 신호",
                value=f"{signal_emoji} {signal}"
            )

        # US Market Details
        st.subheader("미국 시장 정보")
        us_markets = get_us_markets()

        if us_markets:
            for index in us_markets:
                col1, col2, col3, col4 = st.columns(4)

                with col1:
                    st.write(f"**{index['name']}**")

                with col2:
                    change_color = "green" if index['change_rate'] >= 0 else "red"
                    st.markdown(
                        f"<span style='color:{change_color}; font-size:20px;'>"
                        f"{index['close']:,.2f} ({index['change_rate']:+.2f}%)"
                        f"</span>",
                        unsafe_allow_html=True
                    )

                with col3:
                    if index['ma_20']:
                        st.write(f"MA(20): {index['ma_20']:,.2f}")

                with col4:
                    signal_emoji = "🟢" if index['signal'] == "BULLISH" else "🔴"
                    st.write(f"{signal_emoji} {index['signal']}")

                st.divider()

# ==================== Page: 종목 조회 ====================

elif page == "종목 조회":
    st.header("🔍 종목 조회")

    # Market filter
    market_filter = st.selectbox(
        "시장 선택",
        ["전체", "KOSPI", "KOSDAQ"]
    )

    market = None if market_filter == "전체" else market_filter

    # Get stocks
    stocks = get_stocks(market=market, limit=50)

    if stocks:
        # Convert to DataFrame
        df = pd.DataFrame(stocks)

        # Format market cap
        df['market_cap_trillion'] = (df['market_cap'] / 1_000_000_000_000).round(2)

        # Display table
        st.dataframe(
            df[['code', 'name', 'market', 'sector', 'market_cap_trillion']],
            column_config={
                "code": "종목코드",
                "name": "종목명",
                "market": "시장",
                "sector": "섹터",
                "market_cap_trillion": st.column_config.NumberColumn(
                    "시가총액 (조원)",
                    format="%.2f"
                )
            },
            hide_index=True,
            use_container_width=True
        )

        # Statistics
        st.subheader("통계")
        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("총 종목 수", f"{len(df):,}개")

        with col2:
            avg_market_cap = df['market_cap'].mean() / 1_000_000_000_000
            st.metric("평균 시가총액", f"{avg_market_cap:.2f}조원")

        with col3:
            total_market_cap = df['market_cap'].sum() / 1_000_000_000_000
            st.metric("총 시가총액", f"{total_market_cap:.2f}조원")

    else:
        st.info("종목 데이터가 없습니다. 데이터를 먼저 수집해주세요.")

# ==================== Page: 미국 시장 ====================

elif page == "미국 시장":
    st.header("🇺🇸 미국 시장")

    us_markets = get_us_markets()

    if us_markets:
        for index in us_markets:
            st.subheader(f"{index['name']} ({index['symbol']})")

            col1, col2, col3, col4 = st.columns(4)

            with col1:
                st.metric(
                    "현재가",
                    f"{index['close']:,.2f}",
                    f"{index['change_rate']:+.2f}%"
                )

            with col2:
                if index['ma_20']:
                    st.metric("MA(20)", f"{index['ma_20']:,.2f}")

            with col3:
                signal_color = "green" if index['signal'] == "BULLISH" else "red"
                st.markdown(
                    f"<div style='background-color:{signal_color}; padding:10px; border-radius:5px; text-align:center;'>"
                    f"<span style='color:white; font-size:20px;'>{index['signal']}</span>"
                    f"</div>",
                    unsafe_allow_html=True
                )

            with col4:
                st.write(f"**업데이트:** {index['date']}")

            st.divider()

        # Trading recommendation
        st.subheader("투자 권장 사항")

        sp500_data = next((idx for idx in us_markets if idx['symbol'] == '^GSPC'), None)

        if sp500_data:
            if sp500_data['signal'] == "BULLISH":
                st.success(
                    "✅ **매수 포지션 유지**\n\n"
                    "S&P 500이 20일 이동평균선 위에 있습니다. "
                    "한국 주식 시장과의 상관성(0.85)을 고려할 때, "
                    "한국 주식 매수 포지션을 유지하는 것이 좋습니다."
                )
            else:
                st.warning(
                    "⚠️ **신중한 접근 필요**\n\n"
                    "S&P 500이 20일 이동평균선 아래에 있습니다. "
                    "한국 주식 시장도 조정을 받을 가능성이 있으니 "
                    "현금 비중을 늘리거나 방어적 종목에 투자하세요."
                )

    else:
        st.info("미국 시장 데이터가 없습니다. 데이터를 수집해주세요.")

# ==================== Page: 데이터 수집 ====================

elif page == "데이터 수집":
    st.header("🔄 데이터 수집")

    st.markdown(
        """
        이 페이지에서 외부 API로부터 데이터를 수집할 수 있습니다.
        """
    )

    # US Market Data Collection
    st.subheader("미국 시장 데이터")

    if st.button("미국 시장 데이터 수집", type="primary"):
        with st.spinner("데이터 수집 중..."):
            result = collect_us_market_data()

            if result and result.get('status') == 'success':
                st.success(f"✅ {result['data']['collected']}개 지수 데이터 수집 완료!")

                # Display collected data
                for idx in result['data']['results']:
                    st.write(f"- {idx['name']}: {idx['close']:,.2f}")
            else:
                st.error("❌ 데이터 수집 실패")

    st.divider()

    # Stock Data Collection
    st.subheader("한국 주식 데이터")

    stock_code = st.text_input(
        "종목코드 입력 (6자리)",
        placeholder="예: 005930"
    )

    if st.button("종목 데이터 수집"):
        if not stock_code or len(stock_code) != 6:
            st.error("올바른 6자리 종목코드를 입력하세요.")
        else:
            with st.spinner(f"{stock_code} 데이터 수집 중..."):
                try:
                    response = requests.post(f"{API_URL}/api/v1/stocks/{stock_code}/collect")

                    if response.status_code == 200:
                        data = response.json()['data']
                        st.success(f"✅ {data.get('name', stock_code)} 데이터 수집 완료!")

                        # Display collected data
                        col1, col2, col3 = st.columns(3)

                        with col1:
                            st.metric("현재가", f"{data['current_price']:,}원")

                        with col2:
                            st.metric("거래량", f"{data['volume']:,}주")

                        with col3:
                            st.metric("등락률", f"{data['change_rate']:+.2f}%")

                    else:
                        st.error(f"❌ 데이터 수집 실패: {response.text}")

                except Exception as e:
                    st.error(f"❌ 오류 발생: {str(e)}")

# Footer
st.divider()
st.markdown(
    """
    <div style='text-align: center; color: gray; padding: 20px;'>
        Stock Intelligence System v1.0 | Built with ❤️ using FastAPI & Streamlit
    </div>
    """,
    unsafe_allow_html=True
)
