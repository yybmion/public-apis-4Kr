"""
Trading Signals Page
Stock Intelligence System
"""

import streamlit as st
import requests
import pandas as pd

# Page configuration
st.set_page_config(
    page_title="매매 신호 - Stock Intelligence System",
    page_icon="🔔",
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


def get_us_market_signal():
    """Get US market signal"""
    try:
        response = requests.get(f"{API_URL}/api/v1/signals/us-market")
        if response.status_code == 200:
            return response.json()['data']
        return None
    except Exception as e:
        st.error(f"미국 시장 신호 조회 오류: {str(e)}")
        return None


def get_stock_signals(stock_code):
    """Get stock signals"""
    try:
        response = requests.get(f"{API_URL}/api/v1/signals/{stock_code}")
        if response.status_code == 200:
            return response.json()['data']
        return None
    except Exception as e:
        st.error(f"종목 신호 조회 오류: {str(e)}")
        return None


def get_combined_signal(stock_code):
    """Get combined signal"""
    try:
        response = requests.get(f"{API_URL}/api/v1/signals/{stock_code}/combined")
        if response.status_code == 200:
            return response.json()['data']
        return None
    except Exception as e:
        st.error(f"통합 신호 조회 오류: {str(e)}")
        return None


def display_action_badge(action):
    """Display action badge with color"""
    colors = {
        'STRONG_BUY': '#00C853',
        'BUY': '#4CAF50',
        'HOLD': '#FF9800',
        'SELL': '#FF5252',
        'STRONG_SELL': '#D50000'
    }

    labels = {
        'STRONG_BUY': '강력 매수',
        'BUY': '매수',
        'HOLD': '보유',
        'SELL': '매도',
        'STRONG_SELL': '강력 매도'
    }

    color = colors.get(action, '#757575')
    label = labels.get(action, action)

    st.markdown(
        f"<div style='background-color:{color}; padding:20px; border-radius:10px; text-align:center;'>"
        f"<span style='color:white; font-size:28px; font-weight:bold;'>{label}</span>"
        f"</div>",
        unsafe_allow_html=True
    )


# ==================== Main Page ====================

st.title("🔔 매매 신호")
st.markdown("### 기술적 분석 기반 자동 신호 감지")

# Check API status
if not check_api_health():
    st.error("⚠️ API 서버에 연결할 수 없습니다.")
    st.stop()

# Tabs
tab1, tab2, tab3 = st.tabs(["미국 시장 신호", "종목 신호", "통합 신호"])

# ==================== Tab 1: US Market Signal ====================

with tab1:
    st.header("🇺🇸 미국 시장 신호")
    st.markdown("S&P 500 지수와 20일 이동평균선 비교를 통한 시장 방향성 분석")

    if st.button("미국 시장 신호 조회", type="primary"):
        with st.spinner("신호 분석 중..."):
            signal = get_us_market_signal()

            if signal:
                st.success("✅ 신호 분석 완료")

                # Main signal
                col1, col2 = st.columns([1, 2])

                with col1:
                    signal_type = signal['signal']
                    signal_color = '#4CAF50' if signal_type == 'BULLISH' else '#FF5252'

                    st.markdown(
                        f"<div style='background-color:{signal_color}; padding:30px; border-radius:10px; text-align:center;'>"
                        f"<span style='color:white; font-size:36px; font-weight:bold;'>{signal_type}</span>"
                        f"</div>",
                        unsafe_allow_html=True
                    )

                with col2:
                    st.metric("신호 확신도", f"{signal['confidence']:.1f}%")
                    st.metric("S&P 500 종가", f"${signal['sp500_close']:,.2f}")
                    st.metric("MA(20)", f"${signal['sp500_ma']:,.2f}")

                st.divider()

                # Analysis details
                st.subheader("분석 상세")
                col1, col2 = st.columns(2)

                with col1:
                    st.write(f"**이격도:** {signal['ma_diff_pct']:+.2f}%")
                    st.write(f"**갱신 시간:** {signal['date']}")

                with col2:
                    st.write(f"**추세:** {signal['trend']}")
                    st.write(f"**변동성:** {signal.get('volatility', 'N/A')}")

                st.divider()

                # Korean market impact
                st.subheader("한국 시장 영향")

                if signal_type == 'BULLISH':
                    st.success(
                        """
                        **✅ 긍정적 영향 예상**

                        S&P 500이 20일 이동평균선 위에 있습니다.
                        한국-미국 주식시장 상관계수 0.85를 고려할 때,
                        한국 시장도 긍정적인 흐름을 보일 가능성이 높습니다.

                        **권장 조치:**
                        - 한국 주식 매수 포지션 유지
                        - 성장주 중심 포트폴리오 구성
                        - 외국인 매수 우위 종목 주목
                        """
                    )
                else:
                    st.warning(
                        """
                        **⚠️ 부정적 영향 예상**

                        S&P 500이 20일 이동평균선 아래에 있습니다.
                        한국 시장도 조정을 받을 가능성이 있습니다.

                        **권장 조치:**
                        - 현금 비중 확대 고려
                        - 방어주(배당주, 필수소비재) 중심 전환
                        - 손절매 라인 재점검
                        """
                    )

                # Historical context
                if 'historical_accuracy' in signal:
                    st.divider()
                    st.subheader("신호 신뢰도")
                    st.write(f"과거 정확도: {signal['historical_accuracy']}%")

# ==================== Tab 2: Stock Signals ====================

with tab2:
    st.header("📈 종목별 매매 신호")
    st.markdown("개별 종목의 기술적 지표 분석 및 패턴 인식")

    stock_code = st.text_input(
        "종목코드 입력 (6자리)",
        placeholder="예: 005930",
        help="신호를 조회할 종목의 6자리 코드를 입력하세요."
    )

    if st.button("종목 신호 조회", type="primary"):
        if not stock_code or len(stock_code) != 6:
            st.error("올바른 6자리 종목코드를 입력하세요.")
        else:
            with st.spinner(f"{stock_code} 신호 분석 중..."):
                signals = get_stock_signals(stock_code)

                if signals:
                    st.success(f"✅ {signals['stock_name']} 신호 분석 완료")

                    # Main action
                    col1, col2, col3 = st.columns([2, 1, 1])

                    with col1:
                        display_action_badge(signals['action'])

                    with col2:
                        st.metric("신호 점수", f"{signals['score']}/100")

                    with col3:
                        st.metric("감지된 신호", f"{signals['total_signals']}개")

                    st.divider()

                    # Detected signals
                    st.subheader("감지된 신호")

                    if signals['signals']:
                        for i, sig in enumerate(signals['signals'], 1):
                            signal_type = sig['type']
                            description = sig['description']
                            strength = sig['strength']

                            # Signal color based on type
                            if 'BUY' in signal_type or '매수' in description:
                                color = '#4CAF50'
                                emoji = '🟢'
                            elif 'SELL' in signal_type or '매도' in description:
                                color = '#FF5252'
                                emoji = '🔴'
                            else:
                                color = '#FF9800'
                                emoji = '🟡'

                            st.markdown(
                                f"<div style='background-color:{color}; padding:10px; margin:5px 0; border-radius:5px;'>"
                                f"<span style='color:white;'>{emoji} <strong>{i}.</strong> {description} "
                                f"(강도: {strength})</span>"
                                f"</div>",
                                unsafe_allow_html=True
                            )
                    else:
                        st.info("현재 감지된 신호가 없습니다.")

                    st.divider()

                    # Technical indicators
                    if 'indicators' in signals:
                        st.subheader("기술적 지표")
                        indicators = signals['indicators']

                        col1, col2, col3, col4 = st.columns(4)

                        with col1:
                            st.metric("RSI", f"{indicators.get('rsi', 0):.1f}")
                        with col2:
                            st.metric("MACD", f"{indicators.get('macd', 0):.2f}")
                        with col3:
                            st.metric("볼린저 밴드 위치", indicators.get('bb_position', 'N/A'))
                        with col4:
                            st.metric("거래량 비율", f"{indicators.get('volume_ratio', 1.0):.2f}x")

                    # Pattern details
                    if 'patterns' in signals:
                        st.subheader("차트 패턴")
                        patterns = signals['patterns']

                        for pattern, detected in patterns.items():
                            if detected:
                                st.write(f"✓ {pattern}")

# ==================== Tab 3: Combined Signal ====================

with tab3:
    st.header("🎯 통합 신호")
    st.markdown("미국 시장 신호 + 개별 종목 신호를 결합한 최종 투자 판단")

    stock_code_combined = st.text_input(
        "종목코드 입력 (6자리)",
        placeholder="예: 005930",
        key="combined_stock_code",
        help="통합 신호를 조회할 종목의 6자리 코드를 입력하세요."
    )

    if st.button("통합 신호 조회", type="primary"):
        if not stock_code_combined or len(stock_code_combined) != 6:
            st.error("올바른 6자리 종목코드를 입력하세요.")
        else:
            with st.spinner(f"{stock_code_combined} 통합 신호 분석 중..."):
                combined = get_combined_signal(stock_code_combined)

                if combined:
                    st.success(f"✅ {combined['stock_name']} 통합 신호 분석 완료")

                    # Final action
                    col1, col2 = st.columns([2, 1])

                    with col1:
                        display_action_badge(combined['final_action'])

                    with col2:
                        st.metric("최종 점수", f"{combined['final_score']}/100")

                    st.divider()

                    # Component signals
                    st.subheader("구성 신호")

                    col1, col2 = st.columns(2)

                    with col1:
                        st.markdown("**📈 종목 신호**")
                        stock_action = combined['stock_signal']['action']
                        stock_score = combined['stock_signal']['score']

                        st.write(f"행동: {stock_action}")
                        st.write(f"점수: {stock_score}/100")
                        st.write(f"신호 수: {combined['stock_signal']['total_signals']}개")

                    with col2:
                        st.markdown("**🇺🇸 미국 시장 신호**")
                        us_signal_type = combined['us_signal']['signal']
                        us_confidence = combined['us_signal']['confidence']

                        st.write(f"신호: {us_signal_type}")
                        st.write(f"확신도: {us_confidence:.1f}%")

                    st.divider()

                    # Analysis
                    st.subheader("종합 분석")

                    analysis_text = combined.get('analysis', '')
                    if analysis_text:
                        st.info(analysis_text)

                    # Signal adjustment
                    st.subheader("신호 조정")

                    adjustment = combined.get('adjustment', 0)
                    if adjustment > 0:
                        st.success(f"✅ 미국 시장 호조로 점수 {adjustment:+.1f}점 상승")
                    elif adjustment < 0:
                        st.warning(f"⚠️ 미국 시장 부진으로 점수 {adjustment:.1f}점 하락")
                    else:
                        st.info("미국 시장의 영향이 중립적입니다.")

                    st.divider()

                    # Recommendation
                    st.subheader("투자 권장 사항")

                    final_action = combined['final_action']

                    if final_action == 'STRONG_BUY':
                        st.success(
                            """
                            **🟢 강력 매수 추천**

                            종목 자체의 기술적 지표와 미국 시장 환경이 모두 긍정적입니다.

                            - 분할 매수 전략 활용
                            - 목표가 설정 후 진입
                            - 리스크 관리 철저히
                            """
                        )
                    elif final_action == 'BUY':
                        st.success(
                            """
                            **🟢 매수 고려**

                            전반적으로 긍정적인 신호가 포착되었습니다.

                            - 소량 포지션 진입 고려
                            - 추가 매수 타이밍 준비
                            - 손절매 라인 미리 설정
                            """
                        )
                    elif final_action == 'HOLD':
                        st.info(
                            """
                            **🟡 보유 유지**

                            명확한 방향성이 없는 상황입니다.

                            - 기존 포지션 유지
                            - 추가 매수/매도 관망
                            - 신호 변화 모니터링
                            """
                        )
                    elif final_action == 'SELL':
                        st.warning(
                            """
                            **🔴 매도 고려**

                            부정적인 신호가 감지되었습니다.

                            - 단계적 매도 검토
                            - 수익 실현 또는 손실 제한
                            - 다른 종목으로 전환 고려
                            """
                        )
                    elif final_action == 'STRONG_SELL':
                        st.error(
                            """
                            **🔴 강력 매도 추천**

                            종목과 시장 환경이 모두 부정적입니다.

                            - 즉시 매도 권장
                            - 손실 최소화 우선
                            - 현금 비중 확대
                            """
                        )

# Footer
st.divider()
st.markdown(
    """
    <div style='text-align: center; color: gray; padding: 20px;'>
        🔔 15+ 기술적 지표 기반 자동 신호 감지 | 미국-한국 상관관계 0.85 반영
    </div>
    """,
    unsafe_allow_html=True
)
