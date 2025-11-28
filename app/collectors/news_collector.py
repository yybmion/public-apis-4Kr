"""
News Collector - Collect and Analyze Stock News
Stock Intelligence System
"""

import requests
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from app.models.stock import StockNews
from app.collectors.base import BaseCollector, CollectionError
from app.config import settings
from app.utils.logger import LoggerMixin


class NewsCollector(BaseCollector):
    """
    Collect news from BigKinds API (한국언론진흥재단)

    News sources are tiered by reliability:
    - Tier 1: 연합뉴스, 한국경제, 매일경제, 서울경제
    - Tier 2: 파이낸셜뉴스, 이데일리, 헤럴드경제
    - Tier 3: 기타 언론사
    """

    # News source reliability tiers
    SOURCE_TIERS = {
        '연합뉴스': 1,
        '한국경제': 1,
        '매일경제': 1,
        '서울경제': 1,
        '파이낸셜뉴스': 2,
        '이데일리': 2,
        '헤럴드경제': 2,
        '아시아경제': 2,
        '뉴스1': 2,
    }

    def __init__(self, api_key: Optional[str] = None):
        super().__init__(api_key)
        self.api_key = api_key or settings.BIGKINDS_API_KEY
        self.base_url = settings.BIGKINDS_BASE_URL

        if not self.api_key:
            self.log_warning("BigKinds API key not configured")

    async def collect(
        self,
        keyword: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        **kwargs
    ) -> Dict[str, any]:
        """
        Collect news articles for a keyword

        Args:
            keyword: Search keyword (e.g., stock name)
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)

        Returns:
            Dictionary with news articles
        """
        if not self.api_key:
            raise CollectionError("BigKinds API key not configured", source="BigKinds")

        # Default to last 7 days
        if not end_date:
            end_date = datetime.now().strftime('%Y-%m-%d')
        if not start_date:
            start_date = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')

        try:
            # Note: BigKinds API is complex and requires specific authentication
            # This is a simplified implementation
            # In production, you would need to implement full BigKinds API protocol

            self.log_info(f"Collecting news for '{keyword}' from {start_date} to {end_date}")

            # For now, return mock data
            # Real implementation would call BigKinds API
            articles = self._mock_news_collection(keyword, start_date, end_date)

            return {
                'keyword': keyword,
                'start_date': start_date,
                'end_date': end_date,
                'articles': articles,
                'total': len(articles)
            }

        except Exception as e:
            raise CollectionError(
                f"Failed to collect news: {str(e)}",
                source="BigKinds",
                details={'keyword': keyword}
            )

    def _mock_news_collection(
        self,
        keyword: str,
        start_date: str,
        end_date: str
    ) -> List[Dict]:
        """Mock news collection for testing"""
        self.log_warning("Using mock news data (BigKinds API not fully implemented)")

        # Generate mock news articles
        mock_articles = [
            {
                'title': f'{keyword} 주가 상승세 지속',
                'content': f'{keyword}가 최근 실적 개선에 힘입어 주가 상승세를 이어가고 있다.',
                'source': '한국경제',
                'url': 'https://example.com/news/1',
                'published_at': datetime.now() - timedelta(days=1),
            },
            {
                'title': f'{keyword} 신규 사업 진출 발표',
                'content': f'{keyword}가 새로운 사업 영역에 진출한다고 발표했다.',
                'source': '연합뉴스',
                'url': 'https://example.com/news/2',
                'published_at': datetime.now() - timedelta(days=2),
            },
            {
                'title': f'{keyword} 분기 실적 호조',
                'content': f'{keyword}의 이번 분기 실적이 시장 예상을 상회했다.',
                'source': '매일경제',
                'url': 'https://example.com/news/3',
                'published_at': datetime.now() - timedelta(days=3),
            },
        ]

        return mock_articles

    def get_source_tier(self, source: str) -> int:
        """
        Get reliability tier for news source

        Args:
            source: News source name

        Returns:
            Tier level (1-3, lower is better)
        """
        return self.SOURCE_TIERS.get(source, 3)

    def filter_by_tier(
        self,
        articles: List[Dict],
        max_tier: int = 2
    ) -> List[Dict]:
        """
        Filter articles by source tier

        Args:
            articles: List of articles
            max_tier: Maximum tier to include

        Returns:
            Filtered articles
        """
        filtered = []

        for article in articles:
            source = article.get('source', '')
            tier = self.get_source_tier(source)

            if tier <= max_tier:
                article['source_tier'] = tier
                filtered.append(article)

        self.log_info(f"Filtered {len(filtered)}/{len(articles)} articles (tier <= {max_tier})")

        return filtered

    def save_to_database(
        self,
        articles: List[Dict],
        stock_code: Optional[str],
        db: Session
    ):
        """
        Save news articles to database

        Args:
            articles: List of articles
            stock_code: Associated stock code
            db: Database session
        """
        try:
            for article in articles:
                news = StockNews(
                    stock_code=stock_code,
                    title=article['title'],
                    content=article.get('content'),
                    source=article['source'],
                    source_tier=self.get_source_tier(article['source']),
                    url=article.get('url'),
                    published_at=article['published_at']
                )

                # Check if already exists
                existing = db.query(StockNews).filter(
                    StockNews.title == news.title,
                    StockNews.published_at == news.published_at
                ).first()

                if not existing:
                    db.add(news)

            db.commit()
            self.log_info(f"Saved {len(articles)} news articles to database")

        except Exception as e:
            db.rollback()
            self.log_error(f"Failed to save news to database: {str(e)}")

    def validate_data(self, data: Dict) -> bool:
        """Validate collected news data"""
        if not data:
            return False

        required_fields = ['keyword', 'articles']
        if not all(field in data for field in required_fields):
            return False

        articles = data.get('articles', [])
        if not isinstance(articles, list):
            return False

        # Check each article has required fields
        for article in articles:
            if not all(field in article for field in ['title', 'source']):
                return False

        return True


class SentimentAnalyzer(LoggerMixin):
    """
    Analyze sentiment of news articles using Korean BERT

    Uses beomi/kcbert-base or similar Korean language model
    """

    def __init__(self):
        super().__init__()
        self.model = None
        self.tokenizer = None

        # Try to load model
        self._load_model()

    def _load_model(self):
        """Load Korean BERT model for sentiment analysis"""
        try:
            from transformers import AutoTokenizer, AutoModelForSequenceClassification
            import torch

            model_name = "beomi/kcbert-base"

            self.log_info(f"Loading Korean BERT model: {model_name}")

            # Note: This requires transformers and torch to be installed
            # In production, you would want to cache this model
            self.tokenizer = AutoTokenizer.from_pretrained(model_name)
            self.model = AutoModelForSequenceClassification.from_pretrained(model_name)

            self.log_info("Korean BERT model loaded successfully")

        except ImportError:
            self.log_warning("transformers or torch not installed, using simple sentiment")
            self.model = None
        except Exception as e:
            self.log_warning(f"Failed to load BERT model: {str(e)}, using simple sentiment")
            self.model = None

    def analyze(self, text: str) -> Dict[str, any]:
        """
        Analyze sentiment of text

        Args:
            text: Text to analyze

        Returns:
            Dictionary with sentiment label and score
        """
        if self.model is None:
            # Fallback to simple keyword-based sentiment
            return self._simple_sentiment(text)

        try:
            import torch

            # Tokenize
            inputs = self.tokenizer(
                text,
                return_tensors="pt",
                truncation=True,
                max_length=512,
                padding=True
            )

            # Get prediction
            with torch.no_grad():
                outputs = self.model(**inputs)
                predictions = torch.nn.functional.softmax(outputs.logits, dim=-1)

            # Get sentiment
            scores = predictions[0].tolist()

            # Assuming binary classification: [negative, positive]
            negative_score = scores[0]
            positive_score = scores[1]

            if positive_score > negative_score:
                sentiment = 'positive'
                confidence = positive_score
            else:
                sentiment = 'negative'
                confidence = negative_score

            # Convert to -1 to +1 scale
            sentiment_score = (positive_score - negative_score)

            return {
                'sentiment': sentiment,
                'score': sentiment_score,
                'confidence': confidence,
                'positive': positive_score,
                'negative': negative_score
            }

        except Exception as e:
            self.log_error(f"BERT sentiment analysis failed: {str(e)}")
            return self._simple_sentiment(text)

    def _simple_sentiment(self, text: str) -> Dict[str, any]:
        """
        Simple keyword-based sentiment analysis (fallback)

        Args:
            text: Text to analyze

        Returns:
            Sentiment dictionary
        """
        positive_keywords = [
            '상승', '호조', '성장', '개선', '증가', '확대', '강세', '긍정',
            '호재', '수익', '매수', '추천', '기대', '성공', '혁신'
        ]

        negative_keywords = [
            '하락', '부진', '감소', '축소', '약세', '부정', '악재', '손실',
            '매도', '우려', '실패', '리스크', '위험', '하향', '조정'
        ]

        positive_count = sum(1 for keyword in positive_keywords if keyword in text)
        negative_count = sum(1 for keyword in negative_keywords if keyword in text)

        total = positive_count + negative_count

        if total == 0:
            return {
                'sentiment': 'neutral',
                'score': 0.0,
                'confidence': 0.5,
                'method': 'keyword'
            }

        positive_ratio = positive_count / total
        negative_ratio = negative_count / total

        if positive_ratio > negative_ratio:
            sentiment = 'positive'
            score = positive_ratio - negative_ratio
        elif negative_ratio > positive_ratio:
            sentiment = 'negative'
            score = -(negative_ratio - positive_ratio)
        else:
            sentiment = 'neutral'
            score = 0.0

        return {
            'sentiment': sentiment,
            'score': score,
            'confidence': abs(score),
            'positive_keywords': positive_count,
            'negative_keywords': negative_count,
            'method': 'keyword'
        }

    def analyze_articles(
        self,
        articles: List[Dict]
    ) -> List[Dict]:
        """
        Analyze sentiment for multiple articles

        Args:
            articles: List of articles with title and content

        Returns:
            Articles with sentiment added
        """
        for article in articles:
            # Combine title and content
            text = article.get('title', '') + ' ' + article.get('content', '')

            # Analyze sentiment
            sentiment_result = self.analyze(text)

            # Add to article
            article['sentiment_label'] = sentiment_result['sentiment']
            article['sentiment_score'] = sentiment_result['score']
            article['sentiment_confidence'] = sentiment_result.get('confidence', 0)

        self.log_info(f"Analyzed sentiment for {len(articles)} articles")

        return articles

    def aggregate_sentiment(
        self,
        articles: List[Dict],
        weight_by_tier: bool = True
    ) -> Dict[str, any]:
        """
        Aggregate sentiment across multiple articles

        Args:
            articles: List of articles with sentiment
            weight_by_tier: Weight by source reliability tier

        Returns:
            Aggregated sentiment
        """
        if not articles:
            return {
                'overall_sentiment': 'neutral',
                'average_score': 0.0,
                'positive_count': 0,
                'negative_count': 0,
                'neutral_count': 0
            }

        scores = []
        weights = []

        positive_count = 0
        negative_count = 0
        neutral_count = 0

        for article in articles:
            score = article.get('sentiment_score', 0)
            scores.append(score)

            # Weight by tier (tier 1 = 3x, tier 2 = 2x, tier 3 = 1x)
            if weight_by_tier:
                tier = article.get('source_tier', 3)
                weight = 4 - tier  # tier 1 = 3, tier 2 = 2, tier 3 = 1
            else:
                weight = 1

            weights.append(weight)

            # Count sentiment types
            sentiment = article.get('sentiment_label', 'neutral')
            if sentiment == 'positive':
                positive_count += 1
            elif sentiment == 'negative':
                negative_count += 1
            else:
                neutral_count += 1

        # Calculate weighted average
        total_weight = sum(weights)
        if total_weight > 0:
            weighted_score = sum(s * w for s, w in zip(scores, weights)) / total_weight
        else:
            weighted_score = 0.0

        # Determine overall sentiment
        if weighted_score > 0.1:
            overall = 'positive'
        elif weighted_score < -0.1:
            overall = 'negative'
        else:
            overall = 'neutral'

        return {
            'overall_sentiment': overall,
            'average_score': weighted_score,
            'positive_count': positive_count,
            'negative_count': negative_count,
            'neutral_count': neutral_count,
            'total_articles': len(articles)
        }
