"""
Fear & Greed Index Collector
Stock Intelligence System

CNN Fear & Greed Index measures market sentiment (0-100)
- 0-25: Extreme Fear
- 25-45: Fear
- 45-55: Neutral
- 55-75: Greed
- 75-100: Extreme Greed

Source: CNN Business
Unofficial API endpoint
"""

import aiohttp
from typing import Dict, Any, Optional, List
from datetime import datetime

from app.collectors.base import BaseCollector, CollectionError


class FearGreedCollector(BaseCollector):
    """
    CNN Fear & Greed Index Collector

    Collects market sentiment index (0-100) from CNN.

    Features:
    - Real-time market sentiment
    - Historical data available
    - No API key required (unofficial endpoint)

    Index Interpretation:
    - 0-25: Extreme Fear (좋은 매수 기회)
    - 25-45: Fear (조심스러운 매수)
    - 45-55: Neutral (관망)
    - 55-75: Greed (조심스러운 매도 고려)
    - 75-100: Extreme Greed (매도 고려)
    """

    API_URL = "https://production.dataviz.cnn.io/index/fearandgreed/graphdata"

    def __init__(self):
        """Initialize Fear & Greed collector"""
        super().__init__(api_key=None)  # No API key needed

    @staticmethod
    def _classify_sentiment(score: float) -> str:
        """
        Classify sentiment based on score

        Args:
            score: Fear & Greed score (0-100)

        Returns:
            Sentiment label
        """
        if score <= 25:
            return "Extreme Fear"
        elif score <= 45:
            return "Fear"
        elif score <= 55:
            return "Neutral"
        elif score <= 75:
            return "Greed"
        else:
            return "Extreme Greed"

    @staticmethod
    def _get_investment_signal(score: float) -> Dict[str, str]:
        """
        Get investment signal based on score

        Args:
            score: Fear & Greed score

        Returns:
            Dict with signal and description
        """
        if score <= 25:
            return {
                'signal': 'STRONG_BUY',
                'description': '극단적 공포 - 역발상 매수 기회',
                'action': '적극 매수 고려'
            }
        elif score <= 35:
            return {
                'signal': 'BUY',
                'description': '공포 - 매수 기회',
                'action': '분할 매수 고려'
            }
        elif score <= 45:
            return {
                'signal': 'WEAK_BUY',
                'description': '약한 공포 - 조심스러운 매수',
                'action': '소량 매수 가능'
            }
        elif score <= 55:
            return {
                'signal': 'HOLD',
                'description': '중립 - 관망',
                'action': '현재 포지션 유지'
            }
        elif score <= 65:
            return {
                'signal': 'WEAK_SELL',
                'description': '약한 탐욕 - 주의',
                'action': '일부 차익 실현 고려'
            }
        elif score <= 75:
            return {
                'signal': 'SELL',
                'description': '탐욕 - 조정 가능성',
                'action': '분할 매도 고려'
            }
        else:
            return {
                'signal': 'STRONG_SELL',
                'description': '극단적 탐욕 - 고점 경고',
                'action': '적극 매도 고려'
            }

    async def collect(self, **kwargs) -> Dict[str, Any]:
        """
        Collect current Fear & Greed Index

        Returns:
            Dict containing fear & greed data

        Raises:
            CollectionError: If collection fails
        """
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    self.API_URL,
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    if response.status != 200:
                        raise CollectionError(
                            f"Fear & Greed API returned status {response.status}",
                            source="FearGreed"
                        )

                    data = await response.json()

                    # Extract current value
                    current = data.get('fear_and_greed', {})
                    score = current.get('score', 0)

                    if score is None or score == 0:
                        raise CollectionError(
                            "No score data available",
                            source="FearGreed"
                        )

                    score = round(float(score), 2)
                    rating = self._classify_sentiment(score)
                    signal = self._get_investment_signal(score)

                    result = {
                        'score': score,
                        'rating': rating,
                        'signal': signal,
                        'previous_close': current.get('previous_close'),
                        'previous_1_week': current.get('previous_1_week'),
                        'previous_1_month': current.get('previous_1_month'),
                        'previous_1_year': current.get('previous_1_year'),
                        'timestamp': datetime.now().isoformat()
                    }

                    # Calculate trends
                    trends = {}
                    if result['previous_close'] is not None:
                        trends['daily_change'] = round(score - result['previous_close'], 2)
                    if result['previous_1_week'] is not None:
                        trends['weekly_change'] = round(score - result['previous_1_week'], 2)
                    if result['previous_1_month'] is not None:
                        trends['monthly_change'] = round(score - result['previous_1_month'], 2)

                    result['trends'] = trends

                    self.log_info(
                        f"Fear & Greed Index collected: {score} ({rating})",
                        score=score,
                        rating=rating
                    )

                    return result

        except aiohttp.ClientError as e:
            raise CollectionError(
                f"HTTP error fetching Fear & Greed data: {str(e)}",
                source="FearGreed"
            )
        except Exception as e:
            raise CollectionError(
                f"Failed to fetch Fear & Greed data: {str(e)}",
                source="FearGreed"
            )

    async def collect_historical(self) -> Dict[str, Any]:
        """
        Collect historical Fear & Greed data

        Returns:
            Dict with historical data points
        """
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    self.API_URL,
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    if response.status != 200:
                        raise CollectionError(
                            f"API returned status {response.status}",
                            source="FearGreed"
                        )

                    data = await response.json()

                    # Extract historical data
                    historical = data.get('fear_and_greed_historical', {}).get('data', [])

                    if not historical:
                        raise CollectionError(
                            "No historical data available",
                            source="FearGreed"
                        )

                    data_points = []
                    for item in historical:
                        timestamp = item.get('x', 0) / 1000  # Convert from milliseconds
                        score = item.get('y', 0)
                        rating = item.get('rating', '')

                        data_points.append({
                            'date': datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d'),
                            'score': round(float(score), 2),
                            'rating': rating
                        })

                    # Sort by date
                    data_points.sort(key=lambda x: x['date'])

                    result = {
                        'data_points': data_points,
                        'count': len(data_points),
                        'latest': data_points[-1] if data_points else None,
                        'timestamp': datetime.now().isoformat()
                    }

                    self.log_info(
                        f"Collected {len(data_points)} historical data points",
                        count=len(data_points)
                    )

                    return result

        except Exception as e:
            raise CollectionError(
                f"Failed to fetch historical data: {str(e)}",
                source="FearGreed"
            )

    async def get_trend_analysis(self, days: int = 30) -> Dict[str, Any]:
        """
        Analyze Fear & Greed trends over specified period

        Args:
            days: Number of days to analyze

        Returns:
            Dict with trend analysis
        """
        historical = await self.collect_historical()
        data_points = historical['data_points']

        if not data_points:
            return {'error': 'No data available'}

        # Get recent data
        recent_data = data_points[-days:] if len(data_points) >= days else data_points

        # Calculate statistics
        scores = [p['score'] for p in recent_data]
        avg_score = sum(scores) / len(scores)

        # Count sentiment distribution
        sentiment_dist = {
            'Extreme Fear': 0,
            'Fear': 0,
            'Neutral': 0,
            'Greed': 0,
            'Extreme Greed': 0
        }

        for point in recent_data:
            sentiment = self._classify_sentiment(point['score'])
            sentiment_dist[sentiment] = sentiment_dist.get(sentiment, 0) + 1

        # Determine trend
        if len(recent_data) >= 2:
            first_score = recent_data[0]['score']
            last_score = recent_data[-1]['score']
            trend_direction = "increasing" if last_score > first_score else "decreasing"
            trend_magnitude = abs(last_score - first_score)
        else:
            trend_direction = "stable"
            trend_magnitude = 0

        return {
            'period_days': days,
            'average_score': round(avg_score, 2),
            'average_sentiment': self._classify_sentiment(avg_score),
            'current_score': recent_data[-1]['score'],
            'current_sentiment': recent_data[-1]['rating'],
            'trend_direction': trend_direction,
            'trend_magnitude': round(trend_magnitude, 2),
            'sentiment_distribution': sentiment_dist,
            'extreme_fear_days': sentiment_dist['Extreme Fear'],
            'extreme_greed_days': sentiment_dist['Extreme Greed'],
            'analysis_date': datetime.now().isoformat()
        }

    def validate_data(self, data: Dict) -> bool:
        """
        Validate collected data

        Args:
            data: Data to validate

        Returns:
            True if valid, False otherwise
        """
        # Check required fields
        if 'score' not in data or 'rating' not in data:
            return False

        # Check score range
        score = data['score']
        if not isinstance(score, (int, float)):
            return False

        if not (0 <= score <= 100):
            return False

        # Check rating is valid
        valid_ratings = ['Extreme Fear', 'Fear', 'Neutral', 'Greed', 'Extreme Greed']
        if data['rating'] not in valid_ratings:
            return False

        return True


# Convenience function
async def get_fear_greed_index() -> Dict[str, Any]:
    """
    Quick function to get current Fear & Greed Index

    Returns:
        Dict with fear & greed data
    """
    collector = FearGreedCollector()
    return await collector.safe_collect()
