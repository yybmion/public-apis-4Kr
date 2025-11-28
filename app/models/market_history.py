"""
Market History Data Models

시장 데이터 히스토리 저장용 모델

Tables:
1. market_data_history - 일일 시장 데이터 (S&P 500, NASDAQ, KOSPI, KOSDAQ)
2. signal_history - 투자 신호 히스토리
3. fear_greed_history - Fear & Greed Index 히스토리
4. economic_data_history - 경제 지표 히스토리 (금리, 환율 등)

Author: AI Assistant
Created: 2025-11-22
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, Text, Index, Boolean
from sqlalchemy.sql import func
from app.models.base import Base


class MarketDataHistory(Base):
    """
    일일 시장 데이터 히스토리

    S&P 500, NASDAQ, KOSPI, KOSDAQ 등의 일일 데이터
    """
    __tablename__ = "market_data_history"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)

    # Date
    date = Column(DateTime, nullable=False, index=True, comment="데이터 날짜")

    # US Markets
    sp500_close = Column(Float, comment="S&P 500 종가")
    sp500_open = Column(Float, comment="S&P 500 시가")
    sp500_high = Column(Float, comment="S&P 500 고가")
    sp500_low = Column(Float, comment="S&P 500 저가")
    sp500_volume = Column(Float, comment="S&P 500 거래량")
    sp500_change_pct = Column(Float, comment="S&P 500 변동률 (%)")

    nasdaq_close = Column(Float, comment="NASDAQ 종가")
    nasdaq_open = Column(Float, comment="NASDAQ 시가")
    nasdaq_high = Column(Float, comment="NASDAQ 고가")
    nasdaq_low = Column(Float, comment="NASDAQ 저가")
    nasdaq_volume = Column(Float, comment="NASDAQ 거래량")
    nasdaq_change_pct = Column(Float, comment="NASDAQ 변동률 (%)")

    # KR Markets
    kospi_close = Column(Float, comment="KOSPI 종가")
    kospi_open = Column(Float, comment="KOSPI 시가")
    kospi_high = Column(Float, comment="KOSPI 고가")
    kospi_low = Column(Float, comment="KOSPI 저가")
    kospi_volume = Column(Float, comment="KOSPI 거래량")
    kospi_change_pct = Column(Float, comment="KOSPI 변동률 (%)")

    kosdaq_close = Column(Float, comment="KOSDAQ 종가")
    kosdaq_open = Column(Float, comment="KOSDAQ 시가")
    kosdaq_high = Column(Float, comment="KOSDAQ 고가")
    kosdaq_low = Column(Float, comment="KOSDAQ 저가")
    kosdaq_volume = Column(Float, comment="KOSDAQ 거래량")
    kosdaq_change_pct = Column(Float, comment="KOSDAQ 변동률 (%)")

    # Moving Averages (calculated)
    sp500_ma_20 = Column(Float, comment="S&P 500 20일 이동평균")
    sp500_ma_60 = Column(Float, comment="S&P 500 60일 이동평균")
    sp500_ma_200 = Column(Float, comment="S&P 500 200일 이동평균")

    # Metadata
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)

    __table_args__ = (
        Index('idx_market_date', 'date'),
        Index('idx_market_created_at', 'created_at'),
    )


class SignalHistory(Base):
    """
    투자 신호 히스토리

    일일 투자 신호 및 액션 플랜 기록
    """
    __tablename__ = "signal_history"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)

    # Date
    date = Column(DateTime, nullable=False, index=True, comment="신호 생성 날짜")

    # Signal
    signal = Column(String(20), nullable=False, comment="투자 신호 (STRONG_BUY, BUY, HOLD, SELL, STRONG_SELL)")
    confidence = Column(Float, nullable=False, comment="신뢰도 (%)")
    score = Column(Float, comment="신호 점수 (0-10)")

    # Breakdown
    market_correlation_score = Column(Float, comment="시장 상관관계 점수")
    economic_score = Column(Float, comment="경제 지표 점수")
    fear_greed_score = Column(Float, comment="Fear & Greed 점수")
    yield_curve_score = Column(Float, comment="수익률 곡선 점수")

    # Action Plan
    action = Column(String(200), comment="추천 액션")
    timeframe = Column(String(50), comment="시간대")

    # Target Allocation (JSON string)
    target_allocation = Column(Text, comment="목표 자산 배분 (JSON)")

    # Risk Management
    stop_loss_pct = Column(Float, comment="손절 라인 (%)")
    take_profit_pct = Column(Float, comment="익절 라인 (%)")

    # Metadata
    created_at = Column(DateTime, server_default=func.now(), nullable=False)

    __table_args__ = (
        Index('idx_signal_date', 'date'),
        Index('idx_signal_signal', 'signal'),
        Index('idx_signal_created_at', 'created_at'),
    )


class FearGreedHistory(Base):
    """
    Fear & Greed Index 히스토리

    CNN Fear & Greed Index 일일 데이터
    """
    __tablename__ = "fear_greed_history"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)

    # Date
    date = Column(DateTime, nullable=False, index=True, comment="데이터 날짜")

    # Fear & Greed Index
    score = Column(Float, nullable=False, comment="Fear & Greed 점수 (0-100)")
    rating = Column(String(20), comment="등급 (Extreme Fear, Fear, Neutral, Greed, Extreme Greed)")

    # Components (if available)
    market_momentum = Column(Float, comment="시장 모멘텀")
    stock_price_strength = Column(Float, comment="주가 강도")
    stock_price_breadth = Column(Float, comment="주가 폭")
    put_call_ratio = Column(Float, comment="Put/Call 비율")
    market_volatility = Column(Float, comment="시장 변동성 (VIX)")
    safe_haven_demand = Column(Float, comment="안전 자산 수요")
    junk_bond_demand = Column(Float, comment="정크본드 수요")

    # Metadata
    created_at = Column(DateTime, server_default=func.now(), nullable=False)

    __table_args__ = (
        Index('idx_fear_greed_date', 'date'),
        Index('idx_fear_greed_score', 'score'),
        Index('idx_fear_greed_created_at', 'created_at'),
    )


class EconomicDataHistory(Base):
    """
    경제 지표 히스토리

    금리, 환율, 수익률 곡선 등 경제 지표 일일 데이터
    """
    __tablename__ = "economic_data_history"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)

    # Date
    date = Column(DateTime, nullable=False, index=True, comment="데이터 날짜")

    # Interest Rates
    us_fed_rate = Column(Float, comment="미국 기준금리 (%)")
    kr_base_rate = Column(Float, comment="한국 기준금리 (%)")
    interest_rate_spread = Column(Float, comment="금리 차 (%p)")

    # Treasury Yields
    treasury_3m = Column(Float, comment="3개월물 국채 수익률 (%)")
    treasury_2y = Column(Float, comment="2년물 국채 수익률 (%)")
    treasury_5y = Column(Float, comment="5년물 국채 수익률 (%)")
    treasury_10y = Column(Float, comment="10년물 국채 수익률 (%)")
    treasury_30y = Column(Float, comment="30년물 국채 수익률 (%)")

    # Yield Curve Spreads
    spread_10y_2y = Column(Float, comment="10Y-2Y Spread (%p)")
    spread_10y_3m = Column(Float, comment="10Y-3M Spread (%p)")

    # Yield Curve Analysis
    yield_curve_inverted = Column(Boolean, comment="수익률 곡선 역전 여부")
    recession_signal = Column(Boolean, comment="경기 침체 신호")
    recession_probability = Column(Float, comment="경기 침체 확률 (%)")

    # Exchange Rates
    usd_krw = Column(Float, comment="USD/KRW 환율")
    usd_jpy = Column(Float, comment="USD/JPY 환율")
    eur_usd = Column(Float, comment="EUR/USD 환율")

    # Inflation
    us_cpi = Column(Float, comment="미국 CPI (%)")
    kr_cpi = Column(Float, comment="한국 CPI (%)")

    # Metadata
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)

    __table_args__ = (
        Index('idx_economic_date', 'date'),
        Index('idx_economic_fed_rate', 'us_fed_rate'),
        Index('idx_economic_spread', 'spread_10y_2y'),
        Index('idx_economic_created_at', 'created_at'),
    )


class BacktestHistory(Base):
    """
    백테스팅 히스토리

    백테스팅 실행 결과 저장
    """
    __tablename__ = "backtest_history"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)

    # Backtest Info
    strategy_name = Column(String(100), nullable=False, comment="전략 이름")
    start_date = Column(DateTime, nullable=False, comment="백테스팅 시작일")
    end_date = Column(DateTime, nullable=False, comment="백테스팅 종료일")

    # Parameters
    initial_capital = Column(Float, nullable=False, comment="초기 자본")
    commission = Column(Float, comment="거래 수수료 (%)")
    slippage = Column(Float, comment="슬리피지 (%)")
    risk_free_rate = Column(Float, comment="무위험 수익률 (%)")

    # Performance Metrics
    final_value = Column(Float, comment="최종 자산")
    total_return_pct = Column(Float, comment="총 수익률 (%)")
    cagr_pct = Column(Float, comment="연환산 수익률 (%)")
    max_drawdown_pct = Column(Float, comment="최대 낙폭 (%)")
    volatility_pct = Column(Float, comment="변동성 (%)")

    sharpe_ratio = Column(Float, comment="샤프 비율")
    sortino_ratio = Column(Float, comment="소르티노 비율")

    # Trading Stats
    total_trades = Column(Integer, comment="총 거래 수")
    winning_trades = Column(Integer, comment="승리 거래 수")
    losing_trades = Column(Integer, comment="패배 거래 수")
    win_rate = Column(Float, comment="승률")
    profit_factor = Column(Float, comment="손익비")

    avg_win = Column(Float, comment="평균 승리 금액")
    avg_loss = Column(Float, comment="평균 손실 금액")

    # Benchmark Comparison
    benchmark_return_pct = Column(Float, comment="벤치마크 수익률 (%)")
    alpha_pct = Column(Float, comment="Alpha (%)")
    beta = Column(Float, comment="Beta")

    # Detailed Results (JSON)
    equity_curve = Column(Text, comment="자산 곡선 (JSON)")
    trades = Column(Text, comment="거래 내역 (JSON)")

    # Metadata
    created_at = Column(DateTime, server_default=func.now(), nullable=False)

    __table_args__ = (
        Index('idx_backtest_strategy', 'strategy_name'),
        Index('idx_backtest_dates', 'start_date', 'end_date'),
        Index('idx_backtest_created_at', 'created_at'),
    )
