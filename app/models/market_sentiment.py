"""
Market Sentiment Models
Stock Intelligence System
"""

from sqlalchemy import Column, Integer, String, Float, Date, DateTime, JSON, Text, Index
from sqlalchemy.sql import func
from app.database.session import Base


class FearGreedIndex(Base):
    """
    Fear & Greed Index Data

    Stores CNN Fear & Greed Index (market sentiment indicator)
    """
    __tablename__ = "fear_greed_index"

    id = Column(Integer, primary_key=True, index=True)

    # Date
    date = Column(Date, nullable=False, index=True, unique=True)

    # Fear & Greed Score (0-100)
    score = Column(Float, nullable=False)  # 0 = Extreme Fear, 100 = Extreme Greed
    rating = Column(String(20), nullable=False)  # 'Extreme Fear', 'Fear', 'Neutral', 'Greed', 'Extreme Greed'

    # Investment Signal
    signal = Column(String(20))  # 'STRONG_BUY', 'BUY', 'HOLD', 'SELL', 'STRONG_SELL'
    signal_description = Column(Text)

    # Historical Comparisons
    previous_close = Column(Float)  # Previous day
    previous_1_week = Column(Float)  # 1 week ago
    previous_1_month = Column(Float)  # 1 month ago
    previous_1_year = Column(Float)  # 1 year ago

    # Trend Analysis
    daily_change = Column(Float)  # Change from previous day
    weekly_change = Column(Float)  # Change from 1 week ago
    monthly_change = Column(Float)  # Change from 1 month ago

    # Metadata
    data_source = Column(String(50), default='CNN')
    raw_data = Column(JSON)  # Original data from API

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    __table_args__ = (
        Index('idx_date_score', 'date', 'score'),
        Index('idx_rating', 'rating'),
        Index('idx_signal', 'signal'),
    )

    def __repr__(self):
        return f"<FearGreedIndex {self.date}: {self.score} ({self.rating})>"


class MarketSentiment(Base):
    """
    Aggregated Market Sentiment

    Combines multiple sentiment indicators for comprehensive market view
    """
    __tablename__ = "market_sentiments"

    id = Column(Integer, primary_key=True, index=True)

    # Date
    date = Column(Date, nullable=False, index=True, unique=True)

    # Fear & Greed
    fear_greed_score = Column(Float)  # 0-100
    fear_greed_rating = Column(String(20))

    # VIX (Volatility Index)
    vix_value = Column(Float)  # CBOE Volatility Index
    vix_rating = Column(String(20))  # 'Low', 'Medium', 'High', 'Extreme'

    # Put/Call Ratio
    put_call_ratio = Column(Float)
    put_call_signal = Column(String(20))  # 'Bullish', 'Bearish', 'Neutral'

    # Market Breadth
    advance_decline_ratio = Column(Float)  # Advancing stocks / Declining stocks
    new_highs_lows_ratio = Column(Float)  # New highs / New lows

    # Social Media Sentiment (from existing social_media table)
    reddit_sentiment_score = Column(Float)  # Aggregated from WallStreetBets
    twitter_sentiment_score = Column(Float)  # If available

    # Composite Scores
    overall_sentiment_score = Column(Float)  # Weighted average of all indicators
    overall_sentiment_rating = Column(String(20))  # 'Extreme Fear' to 'Extreme Greed'
    composite_signal = Column(String(20))  # 'STRONG_BUY', 'BUY', 'HOLD', 'SELL', 'STRONG_SELL'

    # Market Regime Classification
    market_regime = Column(String(20))  # 'Bull', 'Bear', 'Sideways', 'Volatile'
    regime_confidence = Column(Float)  # 0-1

    # Contrarian Signals
    extreme_fear_alert = Column(Integer, default=0)  # Boolean: Buying opportunity
    extreme_greed_alert = Column(Integer, default=0)  # Boolean: Selling opportunity

    # Metadata
    indicators_count = Column(Integer)  # Number of indicators used
    data_quality_score = Column(Float)  # 0-1, based on data availability

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    __table_args__ = (
        Index('idx_overall_sentiment', 'overall_sentiment_rating'),
        Index('idx_composite_signal', 'composite_signal'),
        Index('idx_market_regime', 'market_regime'),
        Index('idx_extreme_alerts', 'extreme_fear_alert', 'extreme_greed_alert'),
    )

    def __repr__(self):
        return f"<MarketSentiment {self.date}: {self.overall_sentiment_rating} ({self.composite_signal})>"


class SentimentHistory(Base):
    """
    Sentiment History for Trend Analysis

    Stores aggregated sentiment statistics by period
    """
    __tablename__ = "sentiment_history"

    id = Column(Integer, primary_key=True, index=True)

    # Period
    period_type = Column(String(10), nullable=False)  # 'daily', 'weekly', 'monthly'
    period_start = Column(Date, nullable=False, index=True)
    period_end = Column(Date, nullable=False)

    # Aggregated Statistics
    avg_fear_greed = Column(Float)
    min_fear_greed = Column(Float)
    max_fear_greed = Column(Float)
    std_fear_greed = Column(Float)  # Standard deviation

    avg_vix = Column(Float)
    max_vix = Column(Float)

    # Sentiment Distribution (% of days in each category)
    extreme_fear_days = Column(Integer, default=0)
    fear_days = Column(Integer, default=0)
    neutral_days = Column(Integer, default=0)
    greed_days = Column(Integer, default=0)
    extreme_greed_days = Column(Integer, default=0)

    # Trend Indicators
    trend_direction = Column(String(20))  # 'increasing', 'decreasing', 'stable'
    trend_strength = Column(Float)  # 0-1

    # Market Events
    notable_events = Column(JSON)  # List of significant sentiment events

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        Index('idx_period_type_start', 'period_type', 'period_start'),
    )

    def __repr__(self):
        return f"<SentimentHistory {self.period_type} {self.period_start}>"
