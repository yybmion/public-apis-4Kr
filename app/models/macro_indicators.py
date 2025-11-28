"""
Macroeconomic Indicators Models
Stock Intelligence System
"""

from sqlalchemy import Column, Integer, String, Float, Date, DateTime, JSON, Index
from sqlalchemy.sql import func
from app.database.session import Base


class MacroIndicator(Base):
    """
    Macroeconomic Indicator Time Series Data

    Stores data from FRED, ECOS, and other economic data sources
    """
    __tablename__ = "macro_indicators"

    id = Column(Integer, primary_key=True, index=True)

    # Source Information
    source = Column(String(50), nullable=False, index=True)  # 'FRED', 'ECOS', etc.
    indicator_code = Column(String(100), nullable=False, index=True)  # Series ID or indicator name
    indicator_name = Column(String(200))  # Human-readable name
    category = Column(String(50), index=True)  # 'interest_rates', 'employment', etc.

    # Data Point
    date = Column(Date, nullable=False, index=True)  # Data date
    value = Column(Float, nullable=False)  # Indicator value

    # Metadata
    unit = Column(String(50))  # 'percent', 'billions', 'index', etc.
    frequency = Column(String(10))  # 'D', 'W', 'M', 'Q', 'A'
    country = Column(String(10), index=True)  # 'US', 'KR', etc.

    # Additional Data
    metadata = Column(JSON)  # Additional metadata from source

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Composite indexes for efficient queries
    __table_args__ = (
        Index('idx_source_indicator_date', 'source', 'indicator_code', 'date'),
        Index('idx_category_country_date', 'category', 'country', 'date'),
        Index('idx_source_category', 'source', 'category'),
    )

    def __repr__(self):
        return f"<MacroIndicator {self.source}:{self.indicator_code} {self.date} = {self.value}>"


class YieldCurve(Base):
    """
    Yield Curve Data

    Stores yield curve data and spread calculations
    """
    __tablename__ = "yield_curves"

    id = Column(Integer, primary_key=True, index=True)

    # Date
    date = Column(Date, nullable=False, index=True, unique=True)
    country = Column(String(10), nullable=False, default='US')  # 'US', 'KR'

    # Yields by Maturity (in percent)
    yield_3m = Column(Float)  # 3-month
    yield_6m = Column(Float)  # 6-month
    yield_1y = Column(Float)  # 1-year
    yield_2y = Column(Float)  # 2-year
    yield_5y = Column(Float)  # 5-year
    yield_10y = Column(Float)  # 10-year
    yield_30y = Column(Float)  # 30-year

    # Spreads (in basis points)
    spread_10y_2y = Column(Float)  # 10Y-2Y spread
    spread_10y_3m = Column(Float)  # 10Y-3M spread
    spread_2y_3m = Column(Float)  # 2Y-3M spread

    # Inversion Signals
    is_inverted_10y_2y = Column(Integer, default=0)  # Boolean: 10Y-2Y inverted
    is_inverted_10y_3m = Column(Integer, default=0)  # Boolean: 10Y-3M inverted
    recession_signal = Column(Integer, default=0)  # Boolean: Any inversion detected

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    __table_args__ = (
        Index('idx_country_date', 'country', 'date'),
        Index('idx_recession_signal', 'recession_signal', 'date'),
    )

    def __repr__(self):
        return f"<YieldCurve {self.date} 10Y={self.yield_10y} 2Y={self.yield_2y}>"


class EconomicSnapshot(Base):
    """
    Daily Economic Snapshot

    Stores key economic indicators for quick access
    """
    __tablename__ = "economic_snapshots"

    id = Column(Integer, primary_key=True, index=True)

    # Date and Country
    date = Column(Date, nullable=False, index=True)
    country = Column(String(10), nullable=False, index=True)  # 'US', 'KR', 'GLOBAL'

    # US Indicators
    us_federal_funds_rate = Column(Float)
    us_treasury_10y = Column(Float)
    us_unemployment_rate = Column(Float)
    us_cpi = Column(Float)
    us_gdp_growth = Column(Float)

    # Korean Indicators
    kr_base_rate = Column(Float)
    kr_treasury_10y = Column(Float)
    kr_unemployment_rate = Column(Float)
    kr_cpi = Column(Float)
    kr_gdp_growth = Column(Float)
    kr_usd_krw = Column(Float)  # Exchange rate

    # Composite Indicators
    yield_curve_us_inverted = Column(Integer, default=0)
    yield_curve_kr_inverted = Column(Integer, default=0)

    # Metadata
    data_sources = Column(JSON)  # List of data sources used
    completeness_score = Column(Float)  # Percentage of indicators available

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    __table_args__ = (
        Index('idx_country_date_unique', 'country', 'date', unique=True),
    )

    def __repr__(self):
        return f"<EconomicSnapshot {self.country} {self.date}>"
