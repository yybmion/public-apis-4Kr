"""
Analysis Charts Page - 분석 차트

시각화 및 추세 분석

Author: AI Assistant
Created: 2025-11-22
"""

import streamlit as st


def show():
    """Show charts page"""
    st.title("📉 분석 차트")

    st.info("📊 **차트 페이지 개발 중**")

    st.markdown("""
    ### 향후 추가될 차트:

    1. **시장 상관관계 차트**
       - S&P 500 vs KOSPI 상관관계
       - NASDAQ vs KOSDAQ 상관관계

    2. **경제 지표 추세**
       - 금리 추이 (미국/한국)
       - 수익률 곡선 변화
       - Fear & Greed Index 30일 추이

    3. **투자 신호 히스토리**
       - 신호 변화 추적
       - 신뢰도 변화
       - 백테스팅 결과

    4. **섹터 분석**
       - 섹터별 수익률
       - 섹터 로테이션

    5. **포트폴리오 추적**
       - 자산 배분 변화
       - 수익률 추적
       - MDD (최대 낙폭)

    ---

    현재는 **Overview** 페이지와 **투자 신호** 페이지에서 주요 정보를 확인할 수 있습니다.
    """)

    # Placeholder charts
    import plotly.graph_objects as go
    import numpy as np

    st.markdown("### 📊 데모 차트 (예시)")

    # Example: Fear & Greed trend
    st.markdown("#### Fear & Greed Index 추이 (30일)")

    # Generate sample data
    days = np.arange(30)
    scores = 50 + 20 * np.sin(days / 5) + np.random.randn(30) * 5

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=days,
        y=scores,
        mode='lines+markers',
        name='Fear & Greed Score',
        line=dict(color='#1f77b4', width=2)
    ))

    # Add zones
    fig.add_hrect(y0=0, y1=25, fillcolor="red", opacity=0.1, line_width=0)
    fig.add_hrect(y0=25, y1=45, fillcolor="orange", opacity=0.1, line_width=0)
    fig.add_hrect(y0=45, y1=55, fillcolor="yellow", opacity=0.1, line_width=0)
    fig.add_hrect(y0=55, y1=75, fillcolor="lightgreen", opacity=0.1, line_width=0)
    fig.add_hrect(y0=75, y1=100, fillcolor="green", opacity=0.1, line_width=0)

    fig.update_layout(
        title="Fear & Greed Index (Sample Data)",
        xaxis_title="Days",
        yaxis_title="Score",
        height=400,
        yaxis_range=[0, 100]
    )

    st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")
    st.info("💡 실제 데이터 시각화는 데이터베이스 통합 후 활성화됩니다.")
