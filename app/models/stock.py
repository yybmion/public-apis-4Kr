"""
SQLAlchemy Models for Stock Data
Stock Intelligence System
"""

from sqlalchemy import Column, String, BigInteger, Text, TIMESTAMP, Index, Integer, Date, Boolean, DECIMAL, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime

from app.database.session import Base


class Stock(Base):
    """종목 기본 정보"""
    __tablename__ = "stocks"

    code = Column(String(10), primary_key=True, comment="종목코드")
    name = Column(String(100), nullable=False, comment="종목명")
    market = Column(String(10), comment="시장 (KOSPI/KOSDAQ)")
    sector = Column(String(50), comment="섹터")
    market_cap = Column(BigInteger, comment="시가총액 (원)")
    description = Column(Text, comment="회사 설명")
    created_at = Column(TIMESTAMP, default=func.now())
    updated_at = Column(TIMESTAMP, default=func.now(), onupdate=func.now())

    # Relationships
    prices = relationship("StockPrice", back_populates="stock", cascade="all, delete-orphan")
    financials = relationship("Financial", back_populates="stock", cascade="all, delete-orphan")
    news = relationship("StockNews", back_populates="stock", cascade="all, delete-orphan")
    recommendations = relationship("Recommendation", back_populates="stock", cascade="all, delete-orphan")

    __table_args__ = (
        Index('idx_stocks_sector', 'sector'),
        Index('idx_stocks_market_cap', market_cap.desc()),
    )

    def __repr__(self):
        return f"<Stock(code={self.code}, name={self.name})>"


class StockPrice(Base):
    """주가 데이터"""
    __tablename__ = "stock_prices"

    id = Column(Integer, primary_key=True, autoincrement=True)
    stock_code = Column(String(10), ForeignKey('stocks.code', ondelete='CASCADE'), nullable=False)
    date = Column(Date, nullable=False)
    open = Column(Integer, nullable=False, comment="시가")
    high = Column(Integer, nullable=False, comment="고가")
    low = Column(Integer, nullable=False, comment="저가")
    close = Column(Integer, nullable=False, comment="종가")
    volume = Column(BigInteger, comment="거래량")
    trading_value = Column(BigInteger, comment="거래대금")
    change_rate = Column(DECIMAL(5, 2), comment="등락률")
    foreign_ownership = Column(DECIMAL(5, 2), comment="외국인 보유 비율")
    source = Column(String(50), comment="데이터 출처")
    verified = Column(Boolean, default=False, comment="검증 여부")
    created_at = Column(TIMESTAMP, default=func.now())

    # Relationship
    stock = relationship("Stock", back_populates="prices")

    __table_args__ = (
        Index('idx_stock_prices_stock_date', 'stock_code', date.desc()),
        Index('idx_stock_prices_date', date.desc()),
        {'schema': None, 'extend_existing': True}
    )

    def __repr__(self):
        return f"<StockPrice(stock={self.stock_code}, date={self.date}, close={self.close})>"


class Financial(Base):
    """재무제표"""
    __tablename__ = "financials"

    id = Column(Integer, primary_key=True, autoincrement=True)
    stock_code = Column(String(10), ForeignKey('stocks.code', ondelete='CASCADE'), nullable=False)
    year = Column(Integer, nullable=False)
    quarter = Column(Integer, comment="1, 2, 3, 4 (연간은 NULL)")
    revenue = Column(BigInteger, comment="매출액")
    operating_profit = Column(BigInteger, comment="영업이익")
    net_income = Column(BigInteger, comment="당기순이익")
    total_assets = Column(BigInteger, comment="총자산")
    total_liabilities = Column(BigInteger, comment="총부채")
    equity = Column(BigInteger, comment="자본")
    per = Column(DECIMAL(10, 2), comment="PER")
    pbr = Column(DECIMAL(10, 2), comment="PBR")
    roe = Column(DECIMAL(5, 2), comment="ROE (%)")
    debt_ratio = Column(DECIMAL(5, 2), comment="부채비율 (%)")
    dividend_yield = Column(DECIMAL(5, 2), comment="배당수익률 (%)")
    source = Column(String(50), default='DART')
    verified = Column(Boolean, default=True)
    created_at = Column(TIMESTAMP, default=func.now())

    # Relationship
    stock = relationship("Stock", back_populates="financials")

    __table_args__ = (
        Index('idx_financials_stock_year', 'stock_code', year.desc()),
    )

    def __repr__(self):
        return f"<Financial(stock={self.stock_code}, year={self.year}, quarter={self.quarter})>"


class USIndex(Base):
    """미국 지수"""
    __tablename__ = "us_indices"

    id = Column(Integer, primary_key=True, autoincrement=True)
    symbol = Column(String(10), nullable=False, comment="^GSPC, ^IXIC, ^DJI")
    name = Column(String(50), comment="S&P 500, NASDAQ, Dow Jones")
    close = Column(DECIMAL(10, 2), nullable=False)
    change_rate = Column(DECIMAL(5, 2))
    ma_20 = Column(DECIMAL(10, 2), comment="20일 이동평균선")
    ma_60 = Column(DECIMAL(10, 2), comment="60일 이동평균선")
    above_ma = Column(Boolean, comment="이평선 위 여부")
    date = Column(Date, nullable=False)
    created_at = Column(TIMESTAMP, default=func.now())

    __table_args__ = (
        Index('idx_us_indices_symbol_date', 'symbol', date.desc()),
    )

    def __repr__(self):
        return f"<USIndex(symbol={self.symbol}, date={self.date}, close={self.close})>"


class EconomicIndicator(Base):
    """경제 지표"""
    __tablename__ = "economic_indicators"

    id = Column(Integer, primary_key=True, autoincrement=True)
    indicator_name = Column(String(50), nullable=False, comment="base_rate, usd_krw, cpi")
    country = Column(String(10), comment="KR, US")
    value = Column(DECIMAL(10, 4), nullable=False)
    unit = Column(String(20), comment="%, 원, points")
    date = Column(Date, nullable=False)
    source = Column(String(50), comment="ECOS, FRED")
    created_at = Column(TIMESTAMP, default=func.now())

    __table_args__ = (
        Index('idx_economic_indicators_name_date', 'indicator_name', date.desc()),
    )

    def __repr__(self):
        return f"<EconomicIndicator(name={self.indicator_name}, value={self.value})>"


class StockNews(Base):
    """종목 뉴스"""
    __tablename__ = "stock_news"

    id = Column(Integer, primary_key=True, autoincrement=True)
    stock_code = Column(String(10), ForeignKey('stocks.code', ondelete='CASCADE'))
    title = Column(String(500), nullable=False)
    content = Column(Text)
    source = Column(String(100), comment="한국경제, 연합뉴스")
    source_tier = Column(Integer, comment="1, 2, 3 (신뢰도)")
    url = Column(String(500))
    sentiment_score = Column(DECIMAL(3, 2), comment="-1.0 ~ +1.0")
    sentiment_label = Column(String(20), comment="positive, negative, neutral")
    published_at = Column(TIMESTAMP)
    created_at = Column(TIMESTAMP, default=func.now())

    # Relationship
    stock = relationship("Stock", back_populates="news")

    __table_args__ = (
        Index('idx_stock_news_stock_published', 'stock_code', published_at.desc()),
        Index('idx_stock_news_published', published_at.desc()),
    )

    def __repr__(self):
        return f"<StockNews(stock={self.stock_code}, title={self.title[:30]})>"


class Recommendation(Base):
    """추천 종목"""
    __tablename__ = "recommendations"

    id = Column(Integer, primary_key=True, autoincrement=True)
    stock_code = Column(String(10), ForeignKey('stocks.code', ondelete='CASCADE'), nullable=False)
    score = Column(Integer, nullable=False, comment="0~100 (초보자 적합도)")
    risk_level = Column(String(10), comment="LOW, MEDIUM, HIGH")
    reasons = Column(JSONB, comment="추천 이유 리스트")
    expected_return_1m = Column(DECIMAL(5, 2), comment="1개월 예상 수익률")
    max_drawdown = Column(DECIMAL(5, 2), comment="예상 최대 낙폭")
    us_correlation = Column(DECIMAL(3, 2), comment="S&P 500 상관계수")
    us_signal = Column(String(10), comment="BULLISH, BEARISH")
    valid_until = Column(Date, comment="추천 유효 기한")
    created_at = Column(TIMESTAMP, default=func.now())

    # Relationship
    stock = relationship("Stock", back_populates="recommendations")

    __table_args__ = (
        Index('idx_recommendations_score', score.desc()),
        Index('idx_recommendations_created', created_at.desc()),
    )

    def __repr__(self):
        return f"<Recommendation(stock={self.stock_code}, score={self.score})>"


class BacktestResult(Base):
    """백테스트 결과"""
    __tablename__ = "backtest_results"

    id = Column(Integer, primary_key=True, autoincrement=True)
    strategy_name = Column(String(100), nullable=False)
    description = Column(Text)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    initial_capital = Column(BigInteger)
    final_capital = Column(BigInteger)
    total_return = Column(DECIMAL(10, 2), comment="총 수익률 (%)")
    cagr = Column(DECIMAL(5, 2), comment="연평균 수익률")
    mdd = Column(DECIMAL(5, 2), comment="최대 낙폭")
    sharpe_ratio = Column(DECIMAL(5, 2), comment="샤프 비율")
    win_rate = Column(DECIMAL(5, 2), comment="승률 (%)")
    total_trades = Column(Integer, comment="총 거래 횟수")
    parameters = Column(JSONB, comment="전략 파라미터")
    created_at = Column(TIMESTAMP, default=func.now())

    __table_args__ = (
        Index('idx_backtest_results_strategy', 'strategy_name'),
        Index('idx_backtest_results_sharpe', sharpe_ratio.desc()),
    )

    def __repr__(self):
        return f"<BacktestResult(strategy={self.strategy_name}, sharpe={self.sharpe_ratio})>"
