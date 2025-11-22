"""
Economic Indicators Page - 경제 지표

경제 지표 상세 정보

Author: AI Assistant
Created: 2025-11-22
"""

import streamlit as st
import asyncio
from app.scheduler.collection_jobs import CollectionJobs
from app.analyzers.economic_analyzer import EconomicAnalyzer


async def load_economic_data():
    """Load economic data"""
    try:
        collection_jobs = CollectionJobs()

        fred = await collection_jobs.collect_fred_data()
        ecos = await collection_jobs.collect_ecos_data()

        return {'fred': fred, 'ecos': ecos}

    except Exception as e:
        st.error(f"데이터 로드 실패: {str(e)}")
        return None


def show():
    """Show economic indicators page"""
    st.title("📈 경제 지표")

    # Load data
    data = asyncio.run(load_economic_data())

    if not data:
        st.warning("경제 데이터를 불러올 수 없습니다.")
        return

    fred_data = data.get('fred', {})
    ecos_data = data.get('ecos', {})

    # Interest Rates
    st.markdown("### 💰 금리")

    col1, col2, col3 = st.columns(3)

    # US Fed Rate
    if fred_data.get('success'):
        fed_rate_data = fred_data['fed_rate']
        fed_rate = fed_rate_data['latest_value']
        fed_date = fed_rate_data['latest_date']

        with col1:
            st.metric(
                label="🇺🇸 미국 기준금리 (Fed Rate)",
                value=f"{fed_rate:.2f}%",
                help=f"최근 업데이트: {fed_date}"
            )

    # KR Base Rate
    if ecos_data.get('success'):
        base_rate_data = ecos_data['base_rate']
        base_rate = base_rate_data['latest_value']
        base_date = base_rate_data['latest_date']

        with col2:
            st.metric(
                label="🇰🇷 한국 기준금리",
                value=f"{base_rate:.2f}%",
                help=f"최근 업데이트: {base_date}"
            )

    # Rate Spread
    if fred_data.get('success') and ecos_data.get('success'):
        spread = fed_rate - base_rate

        with col3:
            st.metric(
                label="📊 금리 차이",
                value=f"{spread:+.2f}%p",
                delta=None
            )

            if spread > 2.5:
                st.error("⚠️ 높은 금리 차 - 원화 약세 압력")
            elif spread < 1.0:
                st.success("💡 낮은 금리 차 - 원화 강세 가능")
            else:
                st.info("✓ 적정 범위")

    st.markdown("---")

    # Yield Curve
    if fred_data.get('success') and 'yield_curve' in fred_data:
        yc = fred_data['yield_curve']

        st.markdown("### 📊 수익률 곡선")

        col1, col2, col3 = st.columns(3)

        yields = yc.get('yields', {})

        with col1:
            if '2y' in yields:
                st.metric("2년물 국채", f"{yields['2y']:.3f}%")

        with col2:
            if '10y' in yields:
                st.metric("10년물 국채", f"{yields['10y']:.3f}%")

        with col3:
            spread_10y_2y = yc.get('spreads', {}).get('10y_2y', 0)
            st.metric("10Y-2Y Spread", f"{spread_10y_2y:+.3f}%p")

        # Recession Signal
        if yc.get('recession_signal'):
            st.error("⚠️ **경기 침체 신호 (Recession Signal)**")
            st.write(f"확률: {yc.get('recession_probability', 0):.0f}%")
        else:
            st.success("✓ 수익률 곡선 정상")

        st.markdown("---")

    # Economic Analysis
    if fred_data.get('success') and ecos_data.get('success'):
        analyzer = EconomicAnalyzer()

        st.markdown("### 🔍 경제 분석")

        # Interest Rate Analysis
        rate_analysis = analyzer.analyze_interest_rates(
            fred_rate,
            base_rate
        )

        st.markdown("#### 금리 영향 분석")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("**수혜 섹터**")
            for sector in rate_analysis['impact']['beneficiary_sectors']:
                st.success(f"✓ {sector}")

        with col2:
            st.markdown("**악영향 섹터**")
            for sector in rate_analysis['impact']['victim_sectors']:
                st.warning(f"⚠️ {sector}")

        # Warnings
        if rate_analysis.get('warnings'):
            st.markdown("#### ⚠️ 주의사항")
            for warning in rate_analysis['warnings']:
                st.write(warning)

        # Investment Strategy
        if rate_analysis.get('investment_strategy'):
            strategy = rate_analysis['investment_strategy']

            st.markdown("#### 💡 투자 전략")
            if 'general' in strategy:
                st.info(strategy['general'])
            if 'sectors' in strategy:
                st.write("추천 섹터:", ', '.join(strategy['sectors']))
