"""
News & Sentiment Analysis Page
Stock Intelligence System
"""

import streamlit as st
import requests
import pandas as pd
from datetime import datetime, timedelta

# Page configuration
st.set_page_config(
    page_title="뉴스 & 감성 분석 - Stock Intelligence System",
    page_icon="📰",
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


def get_stock_news(stock_code, days=7):
    """Get stock news"""
    try:
        params = {"days": days}
        response = requests.get(f"{API_URL}/api/v1/news/{stock_code}", params=params)
        if response.status_code == 200:
            return response.json()['data']
        return None
    except Exception as e:
        st.error(f"뉴스 조회 오류: {str(e)}")
        return None


def get_sentiment_analysis(stock_code, days=7):
    """Get sentiment analysis"""
    try:
        params = {"days": days}
        response = requests.get(f"{API_URL}/api/v1/sentiment/{stock_code}", params=params)
        if response.status_code == 200:
            return response.json()['data']
        return None
    except Exception as e:
        st.error(f"감성 분석 오류: {str(e)}")
        return None


def display_sentiment_badge(sentiment):
    """Display sentiment badge"""
    colors = {
        'positive': '#4CAF50',
        'negative': '#FF5252',
        'neutral': '#FF9800'
    }

    labels = {
        'positive': '긍정',
        'negative': '부정',
        'neutral': '중립'
    }

    color = colors.get(sentiment, '#757575')
    label = labels.get(sentiment, sentiment)

    return f"<span style='background-color:{color}; color:white; padding:5px 12px; border-radius:5px; font-weight:bold;'>{label}</span>"


def get_source_tier_badge(tier):
    """Get source tier badge"""
    colors = {
        1: '#2196F3',
        2: '#4CAF50',
        3: '#FFC107'
    }

    labels = {
        1: '신뢰도 1급',
        2: '신뢰도 2급',
        3: '신뢰도 3급'
    }

    color = colors.get(tier, '#9E9E9E')
    label = labels.get(tier, f'Tier {tier}')

    return f"<span style='background-color:{color}; color:white; padding:3px 8px; border-radius:3px; font-size:12px;'>{label}</span>"


# ==================== Main Page ====================

st.title("📰 뉴스 & 감성 분석")
st.markdown("### AI 기반 종목 뉴스 감성 분석")

# Check API status
if not check_api_health():
    st.error("⚠️ API 서버에 연결할 수 없습니다.")
    st.stop()

# Tabs
tab1, tab2 = st.tabs(["종목 뉴스", "감성 분석"])

# ==================== Tab 1: Stock News ====================

with tab1:
    st.header("📰 종목별 뉴스")
    st.markdown("주요 언론사의 종목 관련 뉴스를 수집하고 AI로 감성을 분석합니다.")

    # Input section
    col1, col2 = st.columns([3, 1])

    with col1:
        stock_code = st.text_input(
            "종목코드 입력 (6자리)",
            placeholder="예: 005930",
            help="뉴스를 조회할 종목의 6자리 코드를 입력하세요."
        )

    with col2:
        days = st.selectbox(
            "조회 기간",
            options=[3, 7, 14, 30],
            index=1,
            format_func=lambda x: f"최근 {x}일"
        )

    if st.button("뉴스 조회", type="primary"):
        if not stock_code or len(stock_code) != 6:
            st.error("올바른 6자리 종목코드를 입력하세요.")
        else:
            with st.spinner(f"{stock_code} 뉴스 수집 중... (시간이 걸릴 수 있습니다)"):
                news_data = get_stock_news(stock_code, days)

                if news_data:
                    st.success(f"✅ {news_data['stock_name']} 뉴스 {news_data['total']}건 조회")

                    # Data source indicator
                    if news_data.get('source') == 'fresh_collection':
                        st.info("🔄 실시간 수집된 최신 뉴스입니다.")
                    else:
                        st.info("💾 데이터베이스에서 조회한 뉴스입니다.")

                    st.divider()

                    # Display articles
                    if news_data['articles']:
                        for i, article in enumerate(news_data['articles'], 1):
                            with st.expander(f"{i}. {article['title']}", expanded=(i <= 3)):
                                # Article metadata
                                col1, col2, col3 = st.columns(3)

                                with col1:
                                    sentiment = article.get('sentiment_label', 'neutral')
                                    st.markdown(f"**감성:** {display_sentiment_badge(sentiment)}", unsafe_allow_html=True)

                                with col2:
                                    score = article.get('sentiment_score', 0.0)
                                    st.write(f"**신뢰도:** {score:.2f}")

                                with col3:
                                    tier = article.get('source_tier', 3)
                                    st.markdown(f"**출처등급:** {get_source_tier_badge(tier)}", unsafe_allow_html=True)

                                # Article details
                                st.markdown("---")
                                st.write(f"**출처:** {article.get('source', 'N/A')}")

                                if article.get('published_at'):
                                    pub_date = article['published_at']
                                    st.write(f"**발행일:** {pub_date}")

                                if article.get('content'):
                                    st.markdown("**내용:**")
                                    content = article['content']
                                    if len(content) > 500:
                                        st.write(content[:500] + "...")
                                    else:
                                        st.write(content)

                                if article.get('url'):
                                    st.markdown(f"[원문 보기]({article['url']})")

                    else:
                        st.warning("조회된 뉴스가 없습니다.")

                    # Summary statistics
                    if news_data['articles']:
                        st.divider()
                        st.subheader("뉴스 통계")

                        articles = news_data['articles']

                        # Count by sentiment
                        positive = len([a for a in articles if a.get('sentiment_label') == 'positive'])
                        negative = len([a for a in articles if a.get('sentiment_label') == 'negative'])
                        neutral = len([a for a in articles if a.get('sentiment_label') == 'neutral'])

                        col1, col2, col3, col4 = st.columns(4)

                        with col1:
                            st.metric("전체 기사", f"{len(articles)}건")

                        with col2:
                            st.markdown(
                                f"<div style='background-color:#4CAF50; padding:10px; border-radius:5px; text-align:center;'>"
                                f"<span style='color:white;'>긍정<br><strong style='font-size:24px;'>{positive}</strong>건</span>"
                                f"</div>",
                                unsafe_allow_html=True
                            )

                        with col3:
                            st.markdown(
                                f"<div style='background-color:#FF5252; padding:10px; border-radius:5px; text-align:center;'>"
                                f"<span style='color:white;'>부정<br><strong style='font-size:24px;'>{negative}</strong>건</span>"
                                f"</div>",
                                unsafe_allow_html=True
                            )

                        with col4:
                            st.markdown(
                                f"<div style='background-color:#FF9800; padding:10px; border-radius:5px; text-align:center;'>"
                                f"<span style='color:white;'>중립<br><strong style='font-size:24px;'>{neutral}</strong>건</span>"
                                f"</div>",
                                unsafe_allow_html=True
                            )

                        # Source tier distribution
                        st.subheader("출처 등급 분포")

                        tier_1 = len([a for a in articles if a.get('source_tier') == 1])
                        tier_2 = len([a for a in articles if a.get('source_tier') == 2])
                        tier_3 = len([a for a in articles if a.get('source_tier') == 3])

                        col1, col2, col3 = st.columns(3)

                        with col1:
                            st.metric("1급 언론사", f"{tier_1}건")
                        with col2:
                            st.metric("2급 언론사", f"{tier_2}건")
                        with col3:
                            st.metric("3급 언론사", f"{tier_3}건")

                else:
                    st.error("뉴스를 가져올 수 없습니다.")

    # Info section
    st.divider()
    st.subheader("📌 뉴스 출처 신뢰도 등급")
    st.markdown(
        """
        **1급 언론사 (가중치 1.0)**: 연합뉴스, 한국경제, 매일경제, 서울경제, 파이낸셜뉴스
        - 공신력 있는 주요 경제 언론사
        - 검증된 정보와 깊이 있는 분석 제공

        **2급 언론사 (가중치 0.7)**: 뉴스1, 뉴시스, 이데일리, 머니투데이, 아시아경제
        - 신뢰할 수 있는 경제 전문 매체
        - 빠른 속보와 시장 동향 보도

        **3급 언론사 (가중치 0.5)**: 기타 언론사
        - 참고용 정보 제공
        - 다양한 관점 확인 가능
        """
    )

# ==================== Tab 2: Sentiment Analysis ====================

with tab2:
    st.header("💭 감성 분석")
    st.markdown("Korean BERT 모델을 활용한 뉴스 감성 종합 분석")

    # Input section
    col1, col2 = st.columns([3, 1])

    with col1:
        stock_code_sentiment = st.text_input(
            "종목코드 입력 (6자리)",
            placeholder="예: 005930",
            key="sentiment_stock_code",
            help="감성 분석을 수행할 종목의 6자리 코드를 입력하세요."
        )

    with col2:
        days_sentiment = st.selectbox(
            "분석 기간",
            options=[3, 7, 14, 30],
            index=1,
            format_func=lambda x: f"최근 {x}일",
            key="sentiment_days"
        )

    if st.button("감성 분석 실행", type="primary"):
        if not stock_code_sentiment or len(stock_code_sentiment) != 6:
            st.error("올바른 6자리 종목코드를 입력하세요.")
        else:
            with st.spinner(f"{stock_code_sentiment} 감성 분석 중..."):
                sentiment_data = get_sentiment_analysis(stock_code_sentiment, days_sentiment)

                if sentiment_data:
                    st.success(f"✅ {sentiment_data['stock_name']} 감성 분석 완료")

                    sentiment = sentiment_data['sentiment']

                    # Overall sentiment
                    overall = sentiment['overall_sentiment']
                    avg_score = sentiment['average_score']

                    # Large sentiment indicator
                    if overall == 'positive':
                        color = '#4CAF50'
                        emoji = '😊'
                        message = '긍정적인 시장 분위기'
                    elif overall == 'negative':
                        color = '#FF5252'
                        emoji = '😟'
                        message = '부정적인 시장 분위기'
                    else:
                        color = '#FF9800'
                        emoji = '😐'
                        message = '중립적인 시장 분위기'

                    st.markdown(
                        f"<div style='background-color:{color}; padding:40px; border-radius:15px; text-align:center; margin:20px 0;'>"
                        f"<span style='color:white; font-size:48px;'>{emoji}</span><br>"
                        f"<span style='color:white; font-size:32px; font-weight:bold;'>{overall.upper()}</span><br>"
                        f"<span style='color:white; font-size:18px;'>{message}</span>"
                        f"</div>",
                        unsafe_allow_html=True
                    )

                    st.divider()

                    # Sentiment metrics
                    st.subheader("감성 지표")

                    col1, col2, col3, col4 = st.columns(4)

                    with col1:
                        st.metric("평균 감성 점수", f"{avg_score:.2f}")

                    with col2:
                        positive_count = sentiment['positive_count']
                        st.metric("긍정 기사", f"{positive_count}건", delta=None if positive_count == 0 else "+")

                    with col3:
                        negative_count = sentiment['negative_count']
                        st.metric("부정 기사", f"{negative_count}건", delta=None if negative_count == 0 else "-")

                    with col4:
                        neutral_count = sentiment['neutral_count']
                        st.metric("중립 기사", f"{neutral_count}건")

                    st.divider()

                    # Sentiment distribution
                    st.subheader("감성 분포")

                    total = sentiment['total_articles']

                    if total > 0:
                        pos_pct = (positive_count / total) * 100
                        neg_pct = (negative_count / total) * 100
                        neu_pct = (neutral_count / total) * 100

                        # Create simple bar chart using columns
                        st.markdown("**비율:**")

                        col1, col2, col3 = st.columns(3)

                        with col1:
                            st.markdown(
                                f"<div style='background-color:#4CAF50; height:200px; border-radius:10px; display:flex; align-items:center; justify-content:center; flex-direction:column;'>"
                                f"<span style='color:white; font-size:36px; font-weight:bold;'>{pos_pct:.1f}%</span>"
                                f"<span style='color:white; font-size:18px;'>긍정</span>"
                                f"</div>",
                                unsafe_allow_html=True
                            )

                        with col2:
                            st.markdown(
                                f"<div style='background-color:#FF5252; height:200px; border-radius:10px; display:flex; align-items:center; justify-content:center; flex-direction:column;'>"
                                f"<span style='color:white; font-size:36px; font-weight:bold;'>{neg_pct:.1f}%</span>"
                                f"<span style='color:white; font-size:18px;'>부정</span>"
                                f"</div>",
                                unsafe_allow_html=True
                            )

                        with col3:
                            st.markdown(
                                f"<div style='background-color:#FF9800; height:200px; border-radius:10px; display:flex; align-items:center; justify-content:center; flex-direction:column;'>"
                                f"<span style='color:white; font-size:36px; font-weight:bold;'>{neu_pct:.1f}%</span>"
                                f"<span style='color:white; font-size:18px;'>중립</span>"
                                f"</div>",
                                unsafe_allow_html=True
                            )

                    st.divider()

                    # Investment recommendation based on sentiment
                    st.subheader("💡 감성 기반 투자 의견")

                    if overall == 'positive' and avg_score > 0.6:
                        st.success(
                            """
                            **🟢 긍정적 시그널**

                            언론 보도가 긍정적이고 시장 분위기가 좋습니다.

                            **제안:**
                            - 긍정적 모멘텀 활용 가능
                            - 단, 과열 여부 확인 필요
                            - 기술적 지표와 병행 분석 권장
                            """
                        )
                    elif overall == 'positive':
                        st.info(
                            """
                            **🟢 약한 긍정**

                            다소 긍정적인 뉴스가 많습니다.

                            **제안:**
                            - 신중한 진입 고려
                            - 추가 정보 확인 후 판단
                            """
                        )
                    elif overall == 'negative' and avg_score < -0.6:
                        st.error(
                            """
                            **🔴 강한 부정 시그널**

                            언론 보도가 매우 부정적입니다.

                            **제안:**
                            - 신규 진입 보류 권장
                            - 보유 중이라면 손절 검토
                            - 회복 시그널까지 관망
                            """
                        )
                    elif overall == 'negative':
                        st.warning(
                            """
                            **🔴 약한 부정**

                            다소 부정적인 뉴스가 많습니다.

                            **제안:**
                            - 단기적 약세 가능성
                            - 저가 매수 기회 탐색 가능
                            - 펀더멘털 확인 필수
                            """
                        )
                    else:
                        st.info(
                            """
                            **🟡 중립**

                            특별한 방향성이 없습니다.

                            **제안:**
                            - 기다리며 관찰
                            - 다른 지표 중심 판단
                            - 뉴스 변화 모니터링
                            """
                        )

                    # Additional context
                    if sentiment.get('weighted_score'):
                        st.divider()
                        st.subheader("📊 가중 점수")
                        st.write(f"출처 신뢰도를 반영한 가중 점수: **{sentiment['weighted_score']:.2f}**")
                        st.caption("1급 언론사의 보도에 더 높은 가중치를 부여한 점수입니다.")

                else:
                    st.error("감성 분석을 수행할 수 없습니다.")

    # Info section
    st.divider()
    st.subheader("🤖 AI 감성 분석 모델")
    st.markdown(
        """
        **사용 모델:** Korean BERT (beomi/kcbert-base)

        **분석 방식:**
        1. **1차 분석**: BERT 모델을 통한 AI 감성 분석
        2. **2차 분석**: 키워드 기반 보완 분석 (모델 unavailable 시)
        3. **가중 평균**: 언론사 신뢰도를 반영한 종합 점수 산출

        **긍정 키워드**: 상승, 급등, 호실적, 최대, 기대, 성장, 개선, 호조
        **부정 키워드**: 하락, 급락, 악화, 손실, 부진, 감소, 우려, 위기

        **활용 시 유의사항:**
        - 감성 분석은 참고 지표이며, 투자 결정의 유일한 근거가 되어서는 안 됩니다
        - 기술적 분석, 재무 분석 등 다른 지표와 종합적으로 판단하세요
        - 단기적인 뉴스 감성보다 중장기 트렌드를 중시하세요
        """
    )

# Footer
st.divider()
st.markdown(
    """
    <div style='text-align: center; color: gray; padding: 20px;'>
        📰 BigKinds API + Korean BERT 감성 분석 | 3단계 언론사 신뢰도 시스템
    </div>
    """,
    unsafe_allow_html=True
)
