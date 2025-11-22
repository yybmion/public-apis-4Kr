"""
Settings Page - 설정

스케줄러 제어 및 시스템 설정

Author: AI Assistant
Created: 2025-11-22
"""

import streamlit as st


def show():
    """Show settings page"""
    st.title("⚙️ 설정")

    st.markdown("### 📅 스케줄러 설정")

    st.info("💡 **스케줄러 제어 기능 개발 중**")

    st.markdown("""
    ### 향후 추가될 기능:

    1. **스케줄러 제어**
       - 스케줄러 시작/중지
       - 스케줄러 상태 확인
       - 작업 목록 표시

    2. **즉시 실행**
       - 데이터 수집 즉시 실행
       - 분석 즉시 실행
       - 브리핑 생성

    3. **스케줄 관리**
       - 스케줄 시간 변경
       - 작업 활성화/비활성화

    4. **API 키 관리**
       - FRED API 키
       - ECOS API 키
       - 기타 API 키

    5. **알림 설정**
       - 텔레그램 알림
       - 이메일 알림
       - 신호 변화 알림

    ---

    현재는 `scripts/run_scheduler.py`를 사용하여 스케줄러를 실행하세요.
    """)

    st.markdown("---")

    st.markdown("### 📊 시스템 정보")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### 데이터 수집기")
        st.write("✅ Fear & Greed Index")
        st.write("✅ FRED API")
        st.write("✅ ECOS API")
        st.write("✅ SEC EDGAR API")

    with col2:
        st.markdown("#### 분석 모듈")
        st.write("✅ 시장 상관관계 분석")
        st.write("✅ 경제 지표 분석")
        st.write("✅ 투자 신호 생성")
        st.write("✅ 일일 브리핑")

    st.markdown("---")

    st.markdown("### 📚 사용 가이드")

    with st.expander("스케줄러 실행 방법"):
        st.code("""
# 스케줄러 실행
python scripts/run_scheduler.py --init

# 테스트 모드
python scripts/test_scheduler.py --mode instant
        """, language="bash")

    with st.expander("대시보드 실행 방법"):
        st.code("""
# 대시보드 실행
streamlit run app/dashboard/main.py

# 또는
python scripts/run_dashboard.py
        """, language="bash")

    with st.expander("API 키 설정"):
        st.markdown("""
`.env` 파일을 생성하고 다음 내용을 추가하세요:

```bash
# FRED API (optional)
FRED_API_KEY=your_fred_api_key_here

# ECOS API (optional)
ECOS_API_KEY=your_ecos_api_key_here
```

**API 키 발급:**
- FRED: https://fredaccount.stlouisfed.org/apikeys
- ECOS: https://ecos.bok.or.kr/api/

**참고**: Fear & Greed Index와 SEC EDGAR는 API 키가 필요없습니다.
        """)

    st.markdown("---")

    st.markdown("### 🔧 고급 설정")

    st.warning("⚠️ 고급 설정은 다음 버전에서 제공됩니다.")

    # Placeholder for future settings
    if st.checkbox("고급 설정 표시 (비활성)"):
        st.text_input("FRED API Key", type="password", disabled=True)
        st.text_input("ECOS API Key", type="password", disabled=True)
        st.selectbox("로그 레벨", ["INFO", "DEBUG", "WARNING"], disabled=True)
        st.number_input("데이터 갱신 주기 (초)", value=3600, disabled=True)
