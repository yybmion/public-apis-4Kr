"""
Sector Analysis Page
Stock Intelligence System
"""

import streamlit as st
import requests
import pandas as pd

# Page configuration
st.set_page_config(
    page_title="섹터 분석 - Stock Intelligence System",
    page_icon="🏭",
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


def get_all_sectors():
    """Get all sectors"""
    try:
        response = requests.get(f"{API_URL}/api/v1/sectors")
        if response.status_code == 200:
            return response.json()['data']['sectors']
        return []
    except Exception as e:
        st.error(f"섹터 조회 오류: {str(e)}")
        return []


def get_beginner_friendly_sectors():
    """Get beginner-friendly sectors"""
    try:
        response = requests.get(f"{API_URL}/api/v1/sectors/beginner-friendly")
        if response.status_code == 200:
            return response.json()['data']['sectors']
        return []
    except Exception as e:
        st.error(f"섹터 조회 오류: {str(e)}")
        return []


def get_sector_details(sector_name):
    """Get sector details"""
    try:
        # URL encode sector name
        import urllib.parse
        encoded_sector = urllib.parse.quote(sector_name)

        response = requests.get(f"{API_URL}/api/v1/sectors/{encoded_sector}")
        if response.status_code == 200:
            return response.json()['data']
        return None
    except Exception as e:
        st.error(f"섹터 상세 조회 오류: {str(e)}")
        return None


def display_risk_badge(risk_level):
    """Display risk level badge"""
    colors = {
        'LOW': '#4CAF50',
        'MEDIUM': '#FF9800',
        'HIGH': '#FF5252'
    }

    labels = {
        'LOW': '저위험',
        'MEDIUM': '중위험',
        'HIGH': '고위험'
    }

    color = colors.get(risk_level, '#757575')
    label = labels.get(risk_level, risk_level)

    return f"<span style='background-color:{color}; color:white; padding:5px 10px; border-radius:5px; font-weight:bold;'>{label}</span>"


# ==================== Main Page ====================

st.title("🏭 섹터 분석")
st.markdown("### 업종별 특성과 투자 전략")

# Check API status
if not check_api_health():
    st.error("⚠️ API 서버에 연결할 수 없습니다.")
    st.stop()

# Tabs
tab1, tab2, tab3 = st.tabs(["전체 섹터", "초보자 추천 섹터", "섹터 상세 분석"])

# ==================== Tab 1: All Sectors ====================

with tab1:
    st.header("📊 전체 섹터 현황")

    if st.button("전체 섹터 조회", type="primary"):
        with st.spinner("섹터 정보 조회 중..."):
            sectors = get_all_sectors()

            if sectors:
                st.success(f"✅ {len(sectors)}개 섹터 조회 완료")

                # Display sectors in grid
                cols = st.columns(3)

                for i, sector in enumerate(sectors):
                    with cols[i % 3]:
                        with st.container():
                            # Sector card
                            st.markdown(
                                f"<div style='border:2px solid #e0e0e0; padding:20px; border-radius:10px; margin:10px 0;'>"
                                f"<h3>{sector['emoji']} {sector['name']}</h3>"
                                f"<p>{sector['description']}</p>"
                                f"<p>위험도: {display_risk_badge(sector['risk_level'])}</p>"
                                f"</div>",
                                unsafe_allow_html=True
                            )

                # Summary statistics
                st.divider()
                st.subheader("섹터 분포")

                col1, col2, col3 = st.columns(3)

                with col1:
                    low_risk = len([s for s in sectors if s['risk_level'] == 'LOW'])
                    st.metric("저위험 섹터", f"{low_risk}개")

                with col2:
                    medium_risk = len([s for s in sectors if s['risk_level'] == 'MEDIUM'])
                    st.metric("중위험 섹터", f"{medium_risk}개")

                with col3:
                    high_risk = len([s for s in sectors if s['risk_level'] == 'HIGH'])
                    st.metric("고위험 섹터", f"{high_risk}개")

            else:
                st.info("섹터 정보가 없습니다.")

# ==================== Tab 2: Beginner-Friendly Sectors ====================

with tab2:
    st.header("🌟 초보자 추천 섹터")
    st.markdown("투자 입문자에게 적합한 안정적이고 이해하기 쉬운 섹터")

    if st.button("추천 섹터 조회", type="primary", key="beginner_button"):
        with st.spinner("추천 섹터 조회 중..."):
            sectors = get_beginner_friendly_sectors()

            if sectors:
                st.success(f"✅ {len(sectors)}개 초보자 추천 섹터")

                for sector in sectors:
                    with st.expander(f"{sector['emoji']} {sector['name']}", expanded=True):
                        st.markdown(f"**설명:** {sector['description']}")

                        col1, col2 = st.columns(2)

                        with col1:
                            st.markdown("**주요 특징:**")
                            for char in sector.get('characteristics', []):
                                st.write(f"• {char}")

                        with col2:
                            st.markdown("**리스크 요인:**")
                            for risk in sector.get('risks', []):
                                st.write(f"• {risk}")

                        st.markdown(f"**위험도:** {display_risk_badge(sector['risk_level'])}", unsafe_allow_html=True)

                        st.markdown("**대표 종목:**")
                        st.write(", ".join(sector.get('representative_stocks', [])))

                        st.markdown("**추천 대상:**")
                        st.write(", ".join(sector.get('recommended_for', [])))

                st.divider()

                # Investment tips
                st.subheader("💡 초보자를 위한 섹터 투자 팁")
                st.markdown(
                    """
                    1. **분산 투자**: 여러 섹터에 나누어 투자하여 리스크를 분산하세요.
                    2. **이해 우선**: 내가 이해할 수 있는 산업부터 시작하세요.
                    3. **시장 리더**: 각 섹터의 대표 기업(시가총액 상위)부터 연구하세요.
                    4. **장기 관점**: 섹터별로 적절한 투자 기간을 설정하세요.
                    5. **뉴스 모니터링**: 해당 섹터의 주요 뉴스를 꾸준히 확인하세요.
                    """
                )

            else:
                st.info("추천 섹터 정보가 없습니다.")

# ==================== Tab 3: Sector Details ====================

with tab3:
    st.header("🔍 섹터 상세 분석")

    # Sector selection
    sector_name = st.selectbox(
        "분석할 섹터 선택",
        options=[
            "IT/반도체",
            "금융",
            "자동차",
            "화학",
            "바이오/헬스케어",
            "에너지",
            "소비재",
            "통신",
            "건설",
            "유통"
        ],
        help="상세 정보를 확인할 섹터를 선택하세요."
    )

    if st.button("섹터 상세 조회", type="primary", key="detail_button"):
        with st.spinner(f"{sector_name} 섹터 분석 중..."):
            details = get_sector_details(sector_name)

            if details:
                info = details['info']

                # Header
                st.markdown(
                    f"<div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding:30px; border-radius:15px; margin-bottom:20px;'>"
                    f"<h1 style='color:white; margin:0;'>{info['emoji']} {info['name']}</h1>"
                    f"<p style='color:white; font-size:18px; margin:10px 0 0 0;'>{info['description']}</p>"
                    f"</div>",
                    unsafe_allow_html=True
                )

                # Risk level
                col1, col2 = st.columns([1, 3])

                with col1:
                    st.markdown("**위험도:**")
                    st.markdown(display_risk_badge(info['risk_level']), unsafe_allow_html=True)

                with col2:
                    st.markdown("**추천 대상:**")
                    st.write(", ".join(info.get('recommended_for', [])))

                st.divider()

                # Characteristics and Risks
                col1, col2 = st.columns(2)

                with col1:
                    st.subheader("✨ 주요 특징")
                    for char in info.get('characteristics', []):
                        st.success(f"✓ {char}")

                with col2:
                    st.subheader("⚠️ 리스크 요인")
                    for risk in info.get('risks', []):
                        st.warning(f"⚠ {risk}")

                st.divider()

                # Key factors
                if 'key_factors' in info:
                    st.subheader("📌 주요 관심 지표")
                    factors = info['key_factors']

                    cols = st.columns(len(factors))
                    for i, factor in enumerate(factors):
                        with cols[i]:
                            st.info(factor)

                st.divider()

                # Representative stocks
                st.subheader("🏢 대표 종목")

                if 'stocks' in details and details['stocks']:
                    # Convert to DataFrame
                    df = pd.DataFrame(details['stocks'])

                    # Format market cap
                    df['market_cap_trillion'] = (df['market_cap'] / 1_000_000_000_000).round(2)

                    # Display table
                    st.dataframe(
                        df[['code', 'name', 'market', 'market_cap_trillion']],
                        column_config={
                            "code": "종목코드",
                            "name": "종목명",
                            "market": "시장",
                            "market_cap_trillion": st.column_config.NumberColumn(
                                "시가총액 (조원)",
                                format="%.2f"
                            )
                        },
                        hide_index=True,
                        use_container_width=True
                    )

                    # Statistics
                    col1, col2, col3 = st.columns(3)

                    with col1:
                        st.metric("종목 수", f"{len(df)}개")

                    with col2:
                        avg_cap = df['market_cap'].mean() / 1_000_000_000_000
                        st.metric("평균 시가총액", f"{avg_cap:.2f}조원")

                    with col3:
                        total_cap = df['market_cap'].sum() / 1_000_000_000_000
                        st.metric("총 시가총액", f"{total_cap:.2f}조원")

                else:
                    st.write(", ".join(info.get('representative_stocks', [])))

                st.divider()

                # Investment guide
                if 'guide' in details:
                    st.subheader("📖 투자 가이드")
                    st.markdown(details['guide'])

                # Additional resources
                st.divider()
                st.subheader("📚 추가 학습 자료")

                sector_resources = {
                    "IT/반도체": [
                        "• 반도체 수급 사이클 이해하기",
                        "• 메모리 vs 시스템 반도체 차이",
                        "• 삼성전자, SK하이닉스 실적 리포트 읽기"
                    ],
                    "금융": [
                        "• 금리와 은행 수익성의 관계",
                        "• 대손충당금과 건전성 지표",
                        "• ROE, PBR 등 금융업 핵심 지표"
                    ],
                    "자동차": [
                        "• 전기차 시장 동향 파악하기",
                        "• 자동차 부품 공급망 이해",
                        "• 미국/유럽/중국 시장 분석"
                    ],
                    "바이오/헬스케어": [
                        "• 신약 개발 단계별 이해",
                        "• 임상시험 결과 해석하기",
                        "• 파이프라인과 특허 만료 체크"
                    ]
                }

                resources = sector_resources.get(sector_name, [
                    "• 업종 리포트 정기 확인",
                    "• 관련 뉴스 모니터링",
                    "• 대표 기업 IR 자료 학습"
                ])

                for resource in resources:
                    st.write(resource)

            else:
                st.error("섹터 정보를 가져올 수 없습니다.")

# Footer
st.divider()
st.markdown(
    """
    <div style='text-align: center; color: gray; padding: 20px;'>
        🏭 10개 주요 섹터 가이드 | 초보자를 위한 업종별 투자 전략
    </div>
    """,
    unsafe_allow_html=True
)
