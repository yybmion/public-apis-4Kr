"""
Stock Recommendations Page
Stock Intelligence System
"""

import streamlit as st
import requests
import pandas as pd

# Page configuration
st.set_page_config(
    page_title="종목 추천 - Stock Intelligence System",
    page_icon="💡",
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


def analyze_user_profile(profile_data):
    """Analyze user profile"""
    try:
        response = requests.post(
            f"{API_URL}/api/v1/recommendations/analyze-profile",
            json=profile_data
        )
        if response.status_code == 200:
            return response.json()['data']
        return None
    except Exception as e:
        st.error(f"프로필 분석 오류: {str(e)}")
        return None


def get_recommendations(risk_level=None, limit=10):
    """Get stock recommendations"""
    try:
        params = {"limit": limit}
        if risk_level:
            params["risk_level"] = risk_level

        response = requests.get(f"{API_URL}/api/v1/recommendations", params=params)
        if response.status_code == 200:
            return response.json()['data']['recommendations']
        return []
    except Exception as e:
        st.error(f"추천 종목 조회 오류: {str(e)}")
        return []


def get_recommendation_history(limit=50):
    """Get recommendation history"""
    try:
        params = {"limit": limit}
        response = requests.get(f"{API_URL}/api/v1/recommendations/history", params=params)
        if response.status_code == 200:
            return response.json()['data']['recommendations']
        return []
    except Exception as e:
        st.error(f"추천 이력 조회 오류: {str(e)}")
        return []


# ==================== Main Page ====================

st.title("💡 종목 추천")
st.markdown("### 초보 투자자를 위한 맞춤형 종목 추천")

# Check API status
if not check_api_health():
    st.error("⚠️ API 서버에 연결할 수 없습니다.")
    st.stop()

# Tabs
tab1, tab2, tab3 = st.tabs(["프로필 분석", "추천 종목", "추천 이력"])

# ==================== Tab 1: Profile Analysis ====================

with tab1:
    st.header("📋 투자자 프로필 분석")
    st.markdown("5가지 질문에 답하여 당신에게 맞는 투자 전략을 찾아보세요.")

    with st.form("profile_form"):
        col1, col2 = st.columns(2)

        with col1:
            investment_amount = st.number_input(
                "1. 투자 가능 금액 (원)",
                min_value=1_000_000,
                max_value=1_000_000_000,
                value=5_000_000,
                step=1_000_000,
                help="투자할 수 있는 총 금액을 입력하세요."
            )

            investment_period = st.selectbox(
                "2. 투자 기간",
                options=["short", "medium", "long"],
                format_func=lambda x: {
                    "short": "단기 (1년 이하)",
                    "medium": "중기 (1~3년)",
                    "long": "장기 (3년 이상)"
                }[x],
                help="투자 자금을 묶어둘 수 있는 기간을 선택하세요."
            )

            loss_tolerance = st.selectbox(
                "3. 손실 허용 범위",
                options=["low", "medium", "high"],
                format_func=lambda x: {
                    "low": "낮음 (5% 이하)",
                    "medium": "보통 (10% 이하)",
                    "high": "높음 (20% 이하)"
                }[x],
                help="얼마까지 손실을 감당할 수 있나요?"
            )

        with col2:
            experience = st.selectbox(
                "4. 투자 경험",
                options=["none", "beginner", "intermediate"],
                format_func=lambda x: {
                    "none": "없음 (처음)",
                    "beginner": "초보 (1년 미만)",
                    "intermediate": "중급 (1년 이상)"
                }[x],
                help="주식 투자 경험이 얼마나 되나요?"
            )

            goal = st.selectbox(
                "5. 투자 목표",
                options=["preservation", "income", "growth"],
                format_func=lambda x: {
                    "preservation": "원금 보존 (안정적)",
                    "income": "배당 수익 (정기 수입)",
                    "growth": "자본 이득 (큰 수익)"
                }[x],
                help="투자를 통해 달성하고 싶은 목표는 무엇인가요?"
            )

        submitted = st.form_submit_button("프로필 분석하기", type="primary", use_container_width=True)

        if submitted:
            with st.spinner("프로필 분석 중..."):
                profile_data = {
                    "investment_amount": investment_amount,
                    "investment_period": investment_period,
                    "loss_tolerance": loss_tolerance,
                    "experience": experience,
                    "goal": goal
                }

                result = analyze_user_profile(profile_data)

                if result:
                    st.success("✅ 프로필 분석 완료!")

                    # Display results
                    col1, col2, col3 = st.columns(3)

                    with col1:
                        risk_level = result['risk_level']
                        risk_color = {
                            'LOW': 'green',
                            'MEDIUM': 'orange',
                            'HIGH': 'red'
                        }.get(risk_level, 'gray')

                        st.markdown(
                            f"<div style='background-color:{risk_color}; padding:20px; border-radius:10px; text-align:center;'>"
                            f"<span style='color:white; font-size:24px; font-weight:bold;'>위험도: {risk_level}</span>"
                            f"</div>",
                            unsafe_allow_html=True
                        )

                    with col2:
                        st.metric("위험 점수", f"{result['risk_score']}/15")

                    with col3:
                        st.metric("투자 금액", f"{investment_amount:,}원")

                    st.divider()

                    # Preferred sectors
                    st.subheader("추천 섹터")
                    st.write(", ".join(result['preferred_sectors']))

                    # Investment style
                    st.subheader("투자 스타일")
                    st.write(result['investment_style'])

                    # Recommendation
                    st.subheader("맞춤 조언")
                    st.info(result['recommendation'])

                    # Portfolio allocation
                    if 'allocation' in result:
                        st.subheader("포트폴리오 배분")
                        col1, col2, col3 = st.columns(3)

                        with col1:
                            st.metric("주식 비중", f"{result['allocation']['stocks']}%")
                        with col2:
                            st.metric("채권 비중", f"{result['allocation']['bonds']}%")
                        with col3:
                            st.metric("현금 비중", f"{result['allocation']['cash']}%")

# ==================== Tab 2: Recommendations ====================

with tab2:
    st.header("📈 추천 종목")

    col1, col2 = st.columns([3, 1])

    with col1:
        st.markdown("초보 투자자에게 적합한 종목을 선별하여 추천합니다.")

    with col2:
        risk_filter = st.selectbox(
            "위험도 필터",
            options=[None, "LOW", "MEDIUM", "HIGH"],
            format_func=lambda x: "전체" if x is None else x
        )

    limit = st.slider("표시할 종목 수", min_value=5, max_value=50, value=10)

    if st.button("추천 종목 조회", type="primary"):
        with st.spinner("추천 종목 분석 중..."):
            recommendations = get_recommendations(risk_level=risk_filter, limit=limit)

            if recommendations:
                st.success(f"✅ {len(recommendations)}개 종목 추천")

                for i, rec in enumerate(recommendations, 1):
                    with st.expander(f"{i}. {rec['stock_name']} ({rec['stock_code']}) - 점수: {rec['score']}/100"):
                        col1, col2, col3 = st.columns(3)

                        with col1:
                            st.metric("적합도 점수", f"{rec['score']}/100")

                        with col2:
                            risk_color = {
                                'LOW': 'green',
                                'MEDIUM': 'orange',
                                'HIGH': 'red'
                            }.get(rec['risk_level'], 'gray')

                            st.markdown(
                                f"<div style='background-color:{risk_color}; padding:10px; border-radius:5px; text-align:center;'>"
                                f"<span style='color:white;'>위험도: {rec['risk_level']}</span>"
                                f"</div>",
                                unsafe_allow_html=True
                            )

                        with col3:
                            st.metric("현재가", f"{rec['current_price']:,}원")

                        st.subheader("추천 이유")
                        for reason in rec['reasons']:
                            st.write(f"• {reason}")

                        if 'financial_strength' in rec:
                            st.subheader("재무 강점")
                            st.write(rec['financial_strength'])

            else:
                st.warning("추천 가능한 종목이 없습니다. 종목 데이터를 먼저 수집해주세요.")

# ==================== Tab 3: Recommendation History ====================

with tab3:
    st.header("📚 추천 이력")

    history_limit = st.slider("표시할 이력 수", min_value=10, max_value=100, value=50)

    if st.button("이력 조회"):
        with st.spinner("이력 조회 중..."):
            history = get_recommendation_history(limit=history_limit)

            if history:
                # Convert to DataFrame
                df = pd.DataFrame(history)

                # Display table
                st.dataframe(
                    df[['created_at', 'stock_name', 'stock_code', 'score', 'risk_level']],
                    column_config={
                        "created_at": "추천 시간",
                        "stock_name": "종목명",
                        "stock_code": "종목코드",
                        "score": "점수",
                        "risk_level": "위험도"
                    },
                    hide_index=True,
                    use_container_width=True
                )

                # Statistics
                st.subheader("통계")
                col1, col2, col3, col4 = st.columns(4)

                with col1:
                    st.metric("총 추천 횟수", f"{len(df):,}회")

                with col2:
                    avg_score = df['score'].mean()
                    st.metric("평균 점수", f"{avg_score:.1f}/100")

                with col3:
                    low_risk_count = len(df[df['risk_level'] == 'LOW'])
                    st.metric("저위험 종목", f"{low_risk_count}개")

                with col4:
                    unique_stocks = df['stock_code'].nunique()
                    st.metric("고유 종목 수", f"{unique_stocks}개")

            else:
                st.info("추천 이력이 없습니다.")

# Footer
st.divider()
st.markdown(
    """
    <div style='text-align: center; color: gray; padding: 20px;'>
        💡 초보 투자자 맞춤형 추천 시스템 | 0-100점 적합도 스코어링
    </div>
    """,
    unsafe_allow_html=True
)
