"""
Investment Signals Page - 투자 신호 상세

투자 신호 상세 정보 및 액션 플랜

Author: AI Assistant
Created: 2025-11-22
"""

import streamlit as st
import asyncio
from app.scheduler.collection_jobs import CollectionJobs
from app.scheduler.analysis_jobs import AnalysisJobs


async def load_signal():
    """Load investment signal"""
    try:
        collection_jobs = CollectionJobs()
        analysis_jobs = AnalysisJobs()

        # Collect data
        fear_greed = await collection_jobs.collect_fear_greed()
        fred = await collection_jobs.collect_fred_data()
        ecos = await collection_jobs.collect_ecos_data()

        collection_results = {
            'fear_greed': fear_greed,
            'fred': fred,
            'ecos': ecos
        }

        # Generate signal
        signal_result = await analysis_jobs.generate_investment_signal(collection_results)

        return signal_result

    except Exception as e:
        st.error(f"신호 로드 실패: {str(e)}")
        return None


def show():
    """Show signals page"""
    st.title("🎯 투자 신호")

    # Load signal
    signal_data = asyncio.run(load_signal())

    if not signal_data or not signal_data.get('success'):
        st.warning("투자 신호를 불러올 수 없습니다.")
        return

    signal = signal_data['signal']

    # Main Signal
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### 최종 신호")
        st.markdown(f"## {signal['signal']}")
        st.markdown(f"**신뢰도**: {signal['confidence']:.0f}%")
        st.markdown(f"**점수**: {signal['score']:.1f} / 10")

    with col2:
        st.markdown("### 액션")
        action = signal['action_plan']['action']
        timeframe = signal['action_plan']['timeframe']

        st.info(f"**{action}**")
        st.write(f"기간: {timeframe}")

    st.markdown("---")

    # Signal Breakdown
    st.markdown("### 📊 신호 분석")

    breakdown = signal['breakdown']

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("시장 상관관계", str(breakdown.get('market_correlation', 'N/A')))

    with col2:
        st.metric("경제 지표", str(breakdown.get('economic_indicators', 'N/A')))

    with col3:
        st.metric("Fear & Greed", str(breakdown.get('fear_greed', 'N/A')))

    with col4:
        yc = breakdown.get('yield_curve')
        st.metric("수익률 곡선", str(yc) if yc else 'N/A')

    st.markdown("---")

    # Target Allocation
    st.markdown("### 💼 목표 자산 배분")

    allocation = signal['action_plan']['target_allocation']

    for asset, percent in allocation.items():
        st.write(f"**{asset}**: {percent}")

    st.markdown("---")

    # Recommended Sectors
    sectors = signal['action_plan']['specific_sectors']

    if sectors:
        st.markdown("### 🎯 추천 섹터")
        for sector in sectors:
            st.write(f"• {sector}")

        st.markdown("---")

    # Risk Management
    st.markdown("### ⚠️ 리스크 관리")

    risks = signal['action_plan']['risk_management']

    for risk in risks:
        st.write(f"• {risk}")

    # Stop Loss & Take Profit
    stop_loss = signal['action_plan'].get('stop_loss')
    take_profit = signal['action_plan'].get('take_profit')

    if stop_loss or take_profit:
        st.markdown("---")
        col1, col2 = st.columns(2)

        with col1:
            if stop_loss:
                st.error(f"🛑 손절라인: {stop_loss}%")

        with col2:
            if take_profit:
                st.success(f"✅ 익절라인: +{take_profit}%")
