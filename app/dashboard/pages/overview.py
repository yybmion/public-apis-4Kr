"""
Overview Page - 전체 시장 현황

시장 현황, 투자 신호, 주요 지표를 한눈에 표시

Author: AI Assistant
Created: 2025-11-22
"""

import streamlit as st
import asyncio
from datetime import datetime
from app.scheduler.collection_jobs import CollectionJobs
from app.scheduler.analysis_jobs import AnalysisJobs


def get_signal_color(signal: str) -> str:
    """Get CSS class for signal"""
    signal_map = {
        'STRONG_BUY': 'signal-strong-buy',
        'BUY': 'signal-buy',
        'HOLD': 'signal-hold',
        'SELL': 'signal-sell',
        'STRONG_SELL': 'signal-strong-sell'
    }
    return signal_map.get(signal, 'signal-hold')


def get_signal_emoji(signal: str) -> str:
    """Get emoji for signal"""
    signal_map = {
        'STRONG_BUY': '🚀',
        'BUY': '📈',
        'WEAK_BUY': '↗️',
        'HOLD': '➡️',
        'WEAK_SELL': '↘️',
        'SELL': '📉',
        'STRONG_SELL': '⚠️'
    }
    return signal_map.get(signal, '➡️')


async def load_data():
    """Load latest data and analysis"""
    try:
        # Initialize jobs
        collection_jobs = CollectionJobs()
        analysis_jobs = AnalysisJobs()

        # Collect data
        with st.spinner('데이터 수집 중...'):
            fear_greed = await collection_jobs.collect_fear_greed()
            fred = await collection_jobs.collect_fred_data()
            ecos = await collection_jobs.collect_ecos_data()

            collection_results = {
                'fear_greed': fear_greed,
                'fred': fred,
                'ecos': ecos
            }

        # Generate signal
        with st.spinner('투자 신호 분석 중...'):
            signal_result = await analysis_jobs.generate_investment_signal(collection_results)

        # Generate briefing
        briefing_result = await analysis_jobs.generate_daily_briefing(
            collection_results,
            signal_result
        )

        return {
            'collection': collection_results,
            'signal': signal_result,
            'briefing': briefing_result
        }

    except Exception as e:
        st.error(f"데이터 로드 실패: {str(e)}")
        return None


def show():
    """Show overview page"""
    st.title("📊 시장 개요")

    # Refresh button
    col1, col2, col3 = st.columns([1, 1, 4])
    with col1:
        if st.button("🔄 새로고침", use_container_width=True):
            st.rerun()

    with col2:
        st.write(f"🕐 업데이트: {datetime.now().strftime('%H:%M:%S')}")

    st.markdown("---")

    # Load data
    data = asyncio.run(load_data())

    if not data:
        st.warning("데이터를 불러올 수 없습니다. 스케줄러가 실행 중인지 확인하세요.")
        return

    collection = data.get('collection', {})
    signal_data = data.get('signal', {})
    briefing_data = data.get('briefing', {})

    # Row 1: Main Signal
    if signal_data and signal_data.get('success'):
        signal = signal_data['signal']

        st.markdown("### 🎯 현재 투자 신호")

        col1, col2, col3 = st.columns([2, 2, 2])

        with col1:
            signal_value = signal['signal']
            signal_emoji = get_signal_emoji(signal_value)
            signal_class = get_signal_color(signal_value)

            st.markdown(f"""
            <div class="metric-card">
                <h2 style="text-align: center;">{signal_emoji}</h2>
                <p style="text-align: center; font-size: 1.2rem;">투자 신호</p>
                <h1 style="text-align: center;" class="{signal_class}">{signal_value}</h1>
            </div>
            """, unsafe_allow_html=True)

        with col2:
            confidence = signal['confidence']
            confidence_color = "#00C853" if confidence >= 70 else "#FFC107" if confidence >= 50 else "#FF6D00"

            st.markdown(f"""
            <div class="metric-card">
                <h2 style="text-align: center;">📊</h2>
                <p style="text-align: center; font-size: 1.2rem;">신뢰도</p>
                <h1 style="text-align: center; color: {confidence_color};">{confidence:.0f}%</h1>
            </div>
            """, unsafe_allow_html=True)

        with col3:
            action = signal['action_plan']['action']
            timeframe = signal['action_plan']['timeframe']

            st.markdown(f"""
            <div class="metric-card">
                <h2 style="text-align: center;">💡</h2>
                <p style="text-align: center; font-size: 1.2rem;">추천 액션</p>
                <h3 style="text-align: center;">{action}</h3>
                <p style="text-align: center; color: #666;">{timeframe}</p>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("---")

    # Row 2: Market Data
    st.markdown("### 📈 시장 데이터")

    col1, col2, col3 = st.columns(3)

    # Fear & Greed
    if collection.get('fear_greed', {}).get('success'):
        fg_data = collection['fear_greed']['data']
        score = fg_data['score']
        rating = fg_data['rating']

        with col1:
            score_color = "#D50000" if score < 25 or score > 75 else "#00C853" if 40 <= score <= 60 else "#FFC107"

            st.metric(
                label="😨 Fear & Greed Index",
                value=f"{score:.1f}",
                delta=rating
            )

            st.progress(score / 100)

            signal_type = fg_data['signal']['signal']
            st.info(f"신호: {signal_type}")

    # FRED - US Fed Rate
    if collection.get('fred', {}).get('success'):
        fred_data = collection['fred']
        fed_rate = fred_data['fed_rate']['latest_value']

        with col2:
            st.metric(
                label="🇺🇸 미국 기준금리",
                value=f"{fed_rate:.2f}%",
                delta=None
            )

            # Yield Curve
            yc = fred_data.get('yield_curve', {})
            if yc:
                spread = yc.get('spreads', {}).get('10y_2y', 0)
                recession = yc.get('recession_signal', False)

                spread_color = "🔴" if recession else "🟢"
                st.write(f"{spread_color} 10Y-2Y Spread: {spread:+.3f}%")

                if recession:
                    st.warning("⚠️ 경기 침체 신호")

    # ECOS - KR Base Rate
    if collection.get('ecos', {}).get('success'):
        ecos_data = collection['ecos']
        base_rate = ecos_data['base_rate']['latest_value']

        with col3:
            st.metric(
                label="🇰🇷 한국 기준금리",
                value=f"{base_rate:.2f}%",
                delta=None
            )

            # Rate spread
            if collection.get('fred', {}).get('success'):
                spread = fed_rate - base_rate
                st.write(f"금리 차: {spread:+.2f}%p")

                if spread > 2.0:
                    st.warning("⚠️ 원화 약세 압력")
                elif spread < 1.0:
                    st.info("💡 원화 강세 가능")

    st.markdown("---")

    # Row 3: Asset Allocation
    if signal_data and signal_data.get('success'):
        signal = signal_data['signal']
        allocation = signal['action_plan']['target_allocation']

        st.markdown("### 💼 권장 자산 배분")

        cols = st.columns(len(allocation))
        for i, (asset, percent) in enumerate(allocation.items()):
            with cols[i]:
                st.metric(
                    label=asset,
                    value=percent
                )

        st.markdown("---")

    # Row 4: Recommended Sectors
    if signal_data and signal_data.get('success'):
        signal = signal_data['signal']
        sectors = signal['action_plan']['specific_sectors']

        if sectors:
            st.markdown("### 🎯 추천 섹터")

            cols = st.columns(min(len(sectors), 4))
            for i, sector in enumerate(sectors[:4]):
                with cols[i]:
                    st.info(f"📊 {sector}")

            st.markdown("---")

    # Row 5: Daily Briefing
    if briefing_data and briefing_data.get('success'):
        st.markdown("### 📰 일일 브리핑")

        st.code(briefing_data['briefing'], language=None)

    # Sidebar - Quick Stats
    with st.sidebar:
        st.markdown("---")
        st.markdown("### 📊 빠른 통계")

        if collection.get('fear_greed', {}).get('success'):
            fg = collection['fear_greed']['data']
            st.metric("Fear & Greed", f"{fg['score']:.0f}", fg['rating'])

        if signal_data and signal_data.get('success'):
            sig = signal_data['signal']
            st.metric("투자 신호", sig['signal'])
            st.metric("신뢰도", f"{sig['confidence']:.0f}%")
