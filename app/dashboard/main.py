"""
Stock Intelligence System - Streamlit Dashboard

실시간 시장 분석 및 투자 신호 대시보드

Pages:
1. 📊 개요 (Overview) - 전체 시장 현황
2. 🎯 투자 신호 - 매수/매도 신호 및 액션 플랜
3. 📈 경제 지표 - 금리, 환율, 수익률 곡선
4. 📉 분석 차트 - 시각화 및 추세
5. ⚙️  설정 - 스케줄러 제어

Author: AI Assistant
Created: 2025-11-22
"""

import streamlit as st
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Page configuration
st.set_page_config(
    page_title="Stock Intelligence System",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        padding: 1rem;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        border-radius: 0.5rem;
        padding: 1rem;
        margin: 0.5rem 0;
    }
    .signal-strong-buy {
        color: #00C853;
        font-weight: bold;
        font-size: 1.5rem;
    }
    .signal-buy {
        color: #64DD17;
        font-weight: bold;
        font-size: 1.5rem;
    }
    .signal-hold {
        color: #FFC107;
        font-weight: bold;
        font-size: 1.5rem;
    }
    .signal-sell {
        color: #FF6D00;
        font-weight: bold;
        font-size: 1.5rem;
    }
    .signal-strong-sell {
        color: #D50000;
        font-weight: bold;
        font-size: 1.5rem;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown('<div class="main-header">📊 Stock Intelligence System</div>', unsafe_allow_html=True)
st.markdown("---")

# Sidebar
st.sidebar.title("📑 메뉴")

# Navigation
page = st.sidebar.radio(
    "페이지 선택",
    [
        "📊 개요",
        "🎯 투자 신호",
        "📈 경제 지표",
        "📉 분석 차트",
        "⚙️ 설정"
    ]
)

# Main content
if page == "📊 개요":
    from app.dashboard.pages import overview
    overview.show()

elif page == "🎯 투자 신호":
    from app.dashboard.pages import signals
    signals.show()

elif page == "📈 경제 지표":
    from app.dashboard.pages import economic
    economic.show()

elif page == "📉 분석 차트":
    from app.dashboard.pages import charts
    charts.show()

elif page == "⚙️ 설정":
    from app.dashboard.pages import settings
    settings.show()

# Footer
st.sidebar.markdown("---")
st.sidebar.markdown("### 📚 정보")
st.sidebar.info("""
**Stock Intelligence System**

데이터 기반 투자 의사결정 지원 시스템

- 실시간 시장 분석
- 자동 투자 신호 생성
- 경제 지표 모니터링
- 백테스팅 및 검증

v1.0.0
""")

# Debug info (only in development)
if st.sidebar.checkbox("디버그 정보 표시"):
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🔧 디버그")
    st.sidebar.write(f"Python: {sys.version}")
    st.sidebar.write(f"Streamlit: {st.__version__}")
