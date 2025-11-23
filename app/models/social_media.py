"""
Social Media Mentions Model
SNS에서 언급된 종목 추적
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, Text, JSON, Boolean
from sqlalchemy.sql import func
from app.database.session import Base


class SocialMediaMention(Base):
    """
    소셜 미디어 종목 멘션 추적

    WallStreetBets, StockTwits 등에서 언급된 종목 및 감성
    """
    __tablename__ = "social_media_mentions"

    id = Column(Integer, primary_key=True, index=True)

    # 소스 정보
    source = Column(String(50), nullable=False, index=True)  # 'wallstreetbets', 'stocktwits'
    platform = Column(String(50))  # 'reddit', 'twitter'

    # 종목 정보
    ticker = Column(String(20), nullable=False, index=True)  # 종목 티커 (예: 'TSLA', 'AAPL')
    stock_code = Column(String(10))  # 한국 종목 코드 (매핑용)

    # 멘션 데이터
    mention_count = Column(Integer, default=1)  # 멘션 횟수
    rank = Column(Integer)  # 순위 (1위 = 가장 많이 언급됨)

    # 감성 분석
    sentiment = Column(String(20))  # 'BULLISH', 'BEARISH', 'NEUTRAL'
    sentiment_score = Column(Float)  # -1.0 ~ 1.0
    bullish_ratio = Column(Float)  # 0.0 ~ 1.0 (긍정 비율)

    # 영향력 지표
    impact_score = Column(Float)  # 영향력 점수
    comment_count = Column(Integer)  # 댓글 수
    upvote_count = Column(Integer)  # 추천 수

    # 원본 데이터
    raw_data = Column(JSON)  # API 응답 원본

    # 메타데이터
    data_date = Column(DateTime(timezone=True))  # 데이터 기준일
    collected_at = Column(DateTime(timezone=True), server_default=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)

    # 인덱스
    def __repr__(self):
        return f"<SocialMediaMention(source={self.source}, ticker={self.ticker}, sentiment={self.sentiment})>"


class SocialInfluencerPost(Base):
    """
    영향력 있는 인물의 소셜 미디어 포스트

    일론 머스크, 워렌 버핏 등의 발언 추적 (향후 확장용)
    """
    __tablename__ = "social_influencer_posts"

    id = Column(Integer, primary_key=True, index=True)

    # 인플루언서 정보
    username = Column(String(100), nullable=False, index=True)  # 'elonmusk', 'WarrenBuffett'
    platform = Column(String(50), nullable=False)  # 'twitter', 'reddit'

    # 포스트 정보
    post_id = Column(String(100), unique=True)  # 원본 포스트 ID
    post_url = Column(String(500))
    post_text = Column(Text)

    # 언급된 종목
    mentioned_tickers = Column(JSON)  # ['TSLA', 'DOGE', ...]

    # 감성 분석
    sentiment = Column(String(20))  # 'POSITIVE', 'NEGATIVE', 'NEUTRAL'
    sentiment_score = Column(Float)

    # 영향력 지표
    like_count = Column(Integer, default=0)
    retweet_count = Column(Integer, default=0)
    reply_count = Column(Integer, default=0)
    impact_score = Column(Float)  # 계산된 영향력 점수

    # 메타데이터
    posted_at = Column(DateTime(timezone=True))
    collected_at = Column(DateTime(timezone=True), server_default=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)

    def __repr__(self):
        return f"<SocialInfluencerPost(username={self.username}, sentiment={self.sentiment})>"
