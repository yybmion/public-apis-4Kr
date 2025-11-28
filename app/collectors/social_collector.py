"""
Social Media Data Collectors
소셜 미디어 데이터 수집기

- Tradestie API: WallStreetBets Top 50 주식
- StockTwits API: 종목별 투자자 감성
"""

import aiohttp
import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime
from sqlalchemy.orm import Session

from app.utils.logger import LoggerMixin
from app.models.social_media import SocialMediaMention


class TradestieCollector(LoggerMixin):
    """
    Tradestie API Collector

    WallStreetBets에서 가장 많이 언급된 종목 Top 50 수집
    API: https://tradestie.com/api/v1/apps/reddit
    Rate Limit: 20 requests/minute
    Cost: FREE
    """

    def __init__(self):
        super().__init__()
        self.base_url = "https://tradestie.com/api/v1/apps/reddit"
        self.source = "wallstreetbets"
        self.platform = "reddit"

    async def collect(self) -> List[Dict[str, Any]]:
        """
        WallStreetBets Top 50 주식 수집

        Returns:
            List of stock mentions with sentiment
        """
        try:
            self.logger.info("Collecting WallStreetBets trending stocks from Tradestie API...")

            async with aiohttp.ClientSession() as session:
                async with session.get(self.base_url, timeout=30) as response:
                    if response.status == 200:
                        data = await response.json()

                        self.logger.info(f"Successfully collected {len(data)} stocks from WSB")

                        # 데이터 파싱
                        mentions = []
                        for idx, item in enumerate(data):
                            mention = {
                                'source': self.source,
                                'platform': self.platform,
                                'ticker': item.get('ticker'),
                                'mention_count': item.get('no_of_comments', 0),
                                'rank': idx + 1,
                                'sentiment': item.get('sentiment', 'NEUTRAL').upper(),
                                'sentiment_score': item.get('sentiment_score', 0.0),
                                'raw_data': item,
                                'data_date': datetime.now()
                            }
                            mentions.append(mention)

                        return mentions
                    else:
                        self.logger.error(f"Tradestie API error: HTTP {response.status}")
                        return []

        except asyncio.TimeoutError:
            self.logger.error("Tradestie API request timeout")
            return []
        except Exception as e:
            self.logger.error(f"Error collecting from Tradestie: {str(e)}", exc_info=True)
            return []

    async def safe_collect(self) -> List[Dict[str, Any]]:
        """안전한 수집 (에러 시 빈 리스트 반환)"""
        try:
            return await self.collect()
        except Exception as e:
            self.logger.error(f"Safe collect error: {str(e)}")
            return []

    def save_to_database(self, mentions: List[Dict[str, Any]], db: Session) -> int:
        """
        수집된 데이터를 데이터베이스에 저장

        Args:
            mentions: 수집된 멘션 리스트
            db: Database session

        Returns:
            저장된 레코드 수
        """
        try:
            saved_count = 0

            for mention_data in mentions:
                # 중복 체크 (같은 날짜, 같은 소스, 같은 티커)
                existing = db.query(SocialMediaMention).filter(
                    SocialMediaMention.source == mention_data['source'],
                    SocialMediaMention.ticker == mention_data['ticker'],
                    SocialMediaMention.data_date >= datetime.now().replace(hour=0, minute=0, second=0)
                ).first()

                if existing:
                    # 업데이트
                    existing.mention_count = mention_data['mention_count']
                    existing.rank = mention_data['rank']
                    existing.sentiment = mention_data['sentiment']
                    existing.sentiment_score = mention_data['sentiment_score']
                    existing.raw_data = mention_data['raw_data']
                else:
                    # 새로 생성
                    mention = SocialMediaMention(**mention_data)
                    db.add(mention)

                saved_count += 1

            db.commit()
            self.logger.info(f"Saved {saved_count} WSB mentions to database")
            return saved_count

        except Exception as e:
            self.logger.error(f"Error saving to database: {str(e)}")
            db.rollback()
            return 0


class StockTwitsCollector(LoggerMixin):
    """
    StockTwits API Collector

    주식 전용 소셜 네트워크에서 종목별 투자자 감성 수집
    API: https://api.stocktwits.com/api/2/streams/symbol/{symbol}.json
    Rate Limit: Public API (제한적)
    Cost: FREE
    """

    def __init__(self):
        super().__init__()
        self.base_url = "https://api.stocktwits.com/api/2/streams/symbol"
        self.source = "stocktwits"
        self.platform = "stocktwits"

    async def collect_symbol(self, symbol: str) -> Optional[Dict[str, Any]]:
        """
        특정 종목의 StockTwits 데이터 수집

        Args:
            symbol: 주식 티커 (예: 'TSLA', 'AAPL')

        Returns:
            종목 멘션 및 감성 데이터
        """
        try:
            url = f"{self.base_url}/{symbol}.json"

            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=30) as response:
                    if response.status == 200:
                        data = await response.json()

                        messages = data.get('messages', [])

                        if not messages:
                            return None

                        # 감성 분석
                        sentiment_counts = {'bullish': 0, 'bearish': 0, 'neutral': 0}

                        for msg in messages:
                            entities = msg.get('entities', {})
                            if 'sentiment' in entities:
                                sentiment = entities['sentiment'].get('basic', 'neutral')
                                sentiment_counts[sentiment] = sentiment_counts.get(sentiment, 0) + 1
                            else:
                                sentiment_counts['neutral'] += 1

                        total = sum(sentiment_counts.values())

                        if total > 0:
                            bullish_ratio = sentiment_counts['bullish'] / total
                            bearish_ratio = sentiment_counts['bearish'] / total

                            # 전체 감성 결정
                            if bullish_ratio > 0.6:
                                overall_sentiment = 'BULLISH'
                            elif bearish_ratio > 0.6:
                                overall_sentiment = 'BEARISH'
                            else:
                                overall_sentiment = 'NEUTRAL'

                            # 감성 점수 계산 (-1 ~ 1)
                            sentiment_score = bullish_ratio - bearish_ratio

                            return {
                                'source': self.source,
                                'platform': self.platform,
                                'ticker': symbol,
                                'mention_count': total,
                                'sentiment': overall_sentiment,
                                'sentiment_score': sentiment_score,
                                'bullish_ratio': bullish_ratio,
                                'raw_data': {
                                    'sentiment_breakdown': sentiment_counts,
                                    'total_messages': total
                                },
                                'data_date': datetime.now()
                            }

                        return None

                    elif response.status == 404:
                        self.logger.warning(f"Symbol {symbol} not found on StockTwits")
                        return None
                    else:
                        self.logger.error(f"StockTwits API error for {symbol}: HTTP {response.status}")
                        return None

        except asyncio.TimeoutError:
            self.logger.error(f"StockTwits API timeout for {symbol}")
            return None
        except Exception as e:
            self.logger.error(f"Error collecting StockTwits for {symbol}: {str(e)}")
            return None

    async def collect_multiple(self, symbols: List[str]) -> List[Dict[str, Any]]:
        """
        여러 종목의 데이터를 병렬로 수집

        Args:
            symbols: 주식 티커 리스트

        Returns:
            수집된 멘션 리스트
        """
        self.logger.info(f"Collecting StockTwits data for {len(symbols)} symbols...")

        tasks = [self.collect_symbol(symbol) for symbol in symbols]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # 성공한 결과만 필터링
        mentions = [
            result for result in results
            if result is not None and not isinstance(result, Exception)
        ]

        self.logger.info(f"Successfully collected {len(mentions)}/{len(symbols)} symbols from StockTwits")

        return mentions

    def save_to_database(self, mentions: List[Dict[str, Any]], db: Session) -> int:
        """데이터베이스에 저장"""
        try:
            saved_count = 0

            for mention_data in mentions:
                # 중복 체크
                existing = db.query(SocialMediaMention).filter(
                    SocialMediaMention.source == mention_data['source'],
                    SocialMediaMention.ticker == mention_data['ticker'],
                    SocialMediaMention.data_date >= datetime.now().replace(hour=0, minute=0, second=0)
                ).first()

                if existing:
                    # 업데이트
                    for key, value in mention_data.items():
                        if key != 'source' and key != 'ticker':
                            setattr(existing, key, value)
                else:
                    # 새로 생성
                    mention = SocialMediaMention(**mention_data)
                    db.add(mention)

                saved_count += 1

            db.commit()
            self.logger.info(f"Saved {saved_count} StockTwits mentions to database")
            return saved_count

        except Exception as e:
            self.logger.error(f"Error saving to database: {str(e)}")
            db.rollback()
            return 0


# 편의 함수
async def collect_all_social_data(db: Session) -> Dict[str, int]:
    """
    모든 소셜 미디어 데이터 수집

    Returns:
        각 소스별 수집된 레코드 수
    """
    results = {}

    # 1. WallStreetBets Top 50
    tradestie = TradestieCollector()
    wsb_mentions = await tradestie.collect()
    wsb_count = tradestie.save_to_database(wsb_mentions, db)
    results['wallstreetbets'] = wsb_count

    # 2. StockTwits (WSB에서 언급된 상위 종목만)
    if wsb_mentions:
        top_tickers = [m['ticker'] for m in wsb_mentions[:20]]  # 상위 20개만

        stocktwits = StockTwitsCollector()
        st_mentions = await stocktwits.collect_multiple(top_tickers)
        st_count = stocktwits.save_to_database(st_mentions, db)
        results['stocktwits'] = st_count

    return results
