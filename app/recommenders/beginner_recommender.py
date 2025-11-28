"""
Beginner Recommender - Stock Recommendation for Beginners
Stock Intelligence System
"""

from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from datetime import datetime, timedelta

from app.models.stock import Stock, StockPrice, Financial, Recommendation
from app.utils.logger import LoggerMixin


class BeginnerRecommender(LoggerMixin):
    """
    Recommend stocks suitable for beginner investors

    Criteria:
    - Large market cap (stability)
    - Low volatility
    - Good fundamentals (ROE, dividend)
    - High liquidity
    - Low debt ratio
    """

    # Risk level thresholds
    RISK_THRESHOLDS = {
        'LOW': {
            'market_cap_min': 10_000_000_000_000,  # 10 trillion KRW
            'volatility_max': 1.5,
            'debt_ratio_max': 150,
            'dividend_min': 2.0,
            'trading_value_min': 50_000_000_000,  # 50 billion KRW
        },
        'MEDIUM': {
            'market_cap_min': 3_000_000_000_000,  # 3 trillion KRW
            'volatility_max': 2.5,
            'debt_ratio_max': 200,
            'dividend_min': 1.0,
            'trading_value_min': 20_000_000_000,  # 20 billion KRW
        },
        'HIGH': {
            'market_cap_min': 1_000_000_000_000,  # 1 trillion KRW
            'volatility_max': 4.0,
            'debt_ratio_max': 300,
            'dividend_min': 0,
            'trading_value_min': 10_000_000_000,  # 10 billion KRW
        }
    }

    def __init__(self, db: Session):
        super().__init__()
        self.db = db

    def filter_stocks(
        self,
        risk_level: str = 'LOW',
        sector: Optional[str] = None,
        market: Optional[str] = None,
        min_score: int = 60
    ) -> List[Stock]:
        """
        Filter stocks based on beginner-friendly criteria

        Args:
            risk_level: LOW, MEDIUM, or HIGH
            sector: Optional sector filter
            market: Optional market filter (KOSPI/KOSDAQ)
            min_score: Minimum beginner suitability score

        Returns:
            List of filtered stocks
        """
        thresholds = self.RISK_THRESHOLDS.get(risk_level, self.RISK_THRESHOLDS['LOW'])

        # Build query
        query = self.db.query(Stock).join(StockPrice).join(Financial)

        # Basic filters
        query = query.filter(
            Stock.market_cap >= thresholds['market_cap_min'],
            Financial.debt_ratio <= thresholds['debt_ratio_max'],
            Financial.roe >= 10,  # At least 10% ROE
        )

        # Optional filters
        if sector:
            query = query.filter(Stock.sector == sector)

        if market:
            query = query.filter(Stock.market == market)

        # Get latest price data
        thirty_days_ago = datetime.now() - timedelta(days=30)
        query = query.filter(StockPrice.date >= thirty_days_ago)

        # Execute query
        stocks = query.distinct().all()

        self.log_info(f"Filtered {len(stocks)} stocks for risk level {risk_level}")

        return stocks

    def calculate_score(
        self,
        stock: Stock,
        latest_price: StockPrice,
        latest_financial: Financial
    ) -> int:
        """
        Calculate beginner suitability score (0-100)

        Scoring formula:
        - Market Cap (30 points)
        - Volatility (20 points)
        - ROE (20 points)
        - Dividend Yield (15 points)
        - Foreign Ownership (15 points)

        Args:
            stock: Stock instance
            latest_price: Latest price data
            latest_financial: Latest financial data

        Returns:
            Score between 0 and 100
        """
        score = 0

        # 1. Market Cap (30 points)
        if stock.market_cap:
            market_cap_trillion = stock.market_cap / 1_000_000_000_000
            if market_cap_trillion >= 50:
                score += 30
            elif market_cap_trillion >= 20:
                score += 25
            elif market_cap_trillion >= 10:
                score += 20
            elif market_cap_trillion >= 5:
                score += 15
            else:
                score += 10

        # 2. Volatility (20 points) - Lower is better
        # Assuming volatility is calculated as 20-day standard deviation
        # For now, use a placeholder
        # In real implementation, calculate from price history
        volatility = 2.0  # Placeholder
        if volatility < 1.0:
            score += 20
        elif volatility < 1.5:
            score += 15
        elif volatility < 2.0:
            score += 10
        elif volatility < 2.5:
            score += 5

        # 3. ROE (20 points)
        if latest_financial.roe:
            roe = float(latest_financial.roe)
            if roe >= 20:
                score += 20
            elif roe >= 15:
                score += 15
            elif roe >= 10:
                score += 10
            elif roe >= 5:
                score += 5

        # 4. Dividend Yield (15 points)
        if latest_financial.dividend_yield:
            div_yield = float(latest_financial.dividend_yield)
            if div_yield >= 4.0:
                score += 15
            elif div_yield >= 3.0:
                score += 12
            elif div_yield >= 2.0:
                score += 9
            elif div_yield >= 1.0:
                score += 6

        # 5. Foreign Ownership (15 points) - Higher institutional trust
        if latest_price.foreign_ownership:
            foreign = float(latest_price.foreign_ownership)
            if foreign >= 40:
                score += 15
            elif foreign >= 30:
                score += 12
            elif foreign >= 20:
                score += 9
            elif foreign >= 10:
                score += 6

        return min(100, score)

    def generate_reasons(
        self,
        stock: Stock,
        score: int,
        latest_price: StockPrice,
        latest_financial: Financial
    ) -> List[str]:
        """
        Generate reasons why this stock is recommended

        Args:
            stock: Stock instance
            score: Calculated score
            latest_price: Latest price data
            latest_financial: Latest financial data

        Returns:
            List of reason strings
        """
        reasons = []

        # Market Cap
        if stock.market_cap:
            market_cap_trillion = stock.market_cap / 1_000_000_000_000
            if market_cap_trillion >= 10:
                reasons.append(f"시가총액 {market_cap_trillion:.1f}조원 대형 안정주")

        # ROE
        if latest_financial.roe and latest_financial.roe >= 15:
            reasons.append(f"ROE {latest_financial.roe:.1f}% 우수한 수익성")

        # Dividend
        if latest_financial.dividend_yield and latest_financial.dividend_yield >= 2:
            reasons.append(f"배당수익률 {latest_financial.dividend_yield:.1f}% 안정적 배당")

        # Foreign Ownership
        if latest_price.foreign_ownership and latest_price.foreign_ownership >= 30:
            reasons.append(f"외국인 보유 {latest_price.foreign_ownership:.1f}% 기관 신뢰 높음")

        # Debt Ratio
        if latest_financial.debt_ratio and latest_financial.debt_ratio <= 100:
            reasons.append(f"부채비율 {latest_financial.debt_ratio:.1f}% 재무 안정")

        # Sector
        if stock.sector:
            reasons.append(f"{stock.sector} 섹터의 대표 종목")

        # If no specific reasons, add generic one
        if not reasons:
            reasons.append("초보자에게 적합한 종목")

        # Return top 3 reasons
        return reasons[:3]

    def recommend(
        self,
        risk_level: str = 'LOW',
        sector: Optional[str] = None,
        market: Optional[str] = None,
        limit: int = 10,
        save_to_db: bool = True
    ) -> List[Dict]:
        """
        Generate stock recommendations for beginners

        Args:
            risk_level: Investment risk level
            sector: Optional sector filter
            market: Optional market filter
            limit: Maximum number of recommendations
            save_to_db: Whether to save recommendations to database

        Returns:
            List of recommendation dictionaries
        """
        # Filter stocks
        filtered_stocks = self.filter_stocks(risk_level, sector, market)

        if not filtered_stocks:
            self.log_warning(f"No stocks found for risk level {risk_level}")
            return []

        recommendations = []

        for stock in filtered_stocks:
            try:
                # Get latest price
                latest_price = (
                    self.db.query(StockPrice)
                    .filter(StockPrice.stock_code == stock.code)
                    .order_by(StockPrice.date.desc())
                    .first()
                )

                # Get latest financial
                latest_financial = (
                    self.db.query(Financial)
                    .filter(Financial.stock_code == stock.code)
                    .order_by(Financial.year.desc())
                    .first()
                )

                if not latest_price or not latest_financial:
                    continue

                # Calculate score
                score = self.calculate_score(stock, latest_price, latest_financial)

                # Generate reasons
                reasons = self.generate_reasons(stock, score, latest_price, latest_financial)

                # Create recommendation
                rec = {
                    'stock_code': stock.code,
                    'stock_name': stock.name,
                    'market': stock.market,
                    'sector': stock.sector,
                    'current_price': latest_price.close,
                    'market_cap': stock.market_cap,
                    'score': score,
                    'risk_level': risk_level,
                    'reasons': reasons,
                    'per': float(latest_financial.per) if latest_financial.per else None,
                    'pbr': float(latest_financial.pbr) if latest_financial.pbr else None,
                    'roe': float(latest_financial.roe) if latest_financial.roe else None,
                    'dividend_yield': float(latest_financial.dividend_yield) if latest_financial.dividend_yield else None,
                    'debt_ratio': float(latest_financial.debt_ratio) if latest_financial.debt_ratio else None,
                    'foreign_ownership': float(latest_price.foreign_ownership) if latest_price.foreign_ownership else None,
                }

                recommendations.append(rec)

            except Exception as e:
                self.log_error(f"Failed to process {stock.code}: {str(e)}")
                continue

        # Sort by score (descending)
        recommendations.sort(key=lambda x: x['score'], reverse=True)

        # Limit results
        top_recommendations = recommendations[:limit]

        # Save to database
        if save_to_db:
            self._save_recommendations(top_recommendations)

        self.log_info(f"Generated {len(top_recommendations)} recommendations")

        return top_recommendations

    def _save_recommendations(self, recommendations: List[Dict]):
        """Save recommendations to database"""
        try:
            # Delete old recommendations (older than 7 days)
            seven_days_ago = datetime.now() - timedelta(days=7)
            self.db.query(Recommendation).filter(
                Recommendation.created_at < seven_days_ago
            ).delete()

            # Save new recommendations
            for rec in recommendations:
                db_rec = Recommendation(
                    stock_code=rec['stock_code'],
                    score=rec['score'],
                    risk_level=rec['risk_level'],
                    reasons=rec['reasons'],
                    expected_return_1m=None,  # TODO: Calculate expected return
                    max_drawdown=None,  # TODO: Calculate max drawdown
                    us_correlation=0.85,  # Fixed correlation coefficient
                    us_signal=None,  # TODO: Get US signal
                    valid_until=datetime.now().date() + timedelta(days=7)
                )
                self.db.add(db_rec)

            self.db.commit()
            self.log_info(f"Saved {len(recommendations)} recommendations to database")

        except Exception as e:
            self.db.rollback()
            self.log_error(f"Failed to save recommendations: {str(e)}")

    def analyze_user_profile(self, answers: Dict[str, any]) -> Dict[str, any]:
        """
        Analyze user investment profile based on questionnaire

        Args:
            answers: Dictionary of question answers

        Returns:
            User profile with risk level and preferences
        """
        risk_score = 0

        # Question 1: Investment amount
        amount = answers.get('investment_amount', 0)
        if amount < 5_000_000:
            risk_score += 1
        elif amount < 10_000_000:
            risk_score += 2
        else:
            risk_score += 3

        # Question 2: Investment period
        period = answers.get('investment_period', 'short')
        if period == 'short':  # < 1 year
            risk_score += 1
        elif period == 'medium':  # 1-3 years
            risk_score += 2
        else:  # > 3 years
            risk_score += 3

        # Question 3: Loss tolerance
        loss_tolerance = answers.get('loss_tolerance', 'low')
        if loss_tolerance == 'low':
            risk_score += 1
        elif loss_tolerance == 'medium':
            risk_score += 2
        else:
            risk_score += 3

        # Question 4: Investment experience
        experience = answers.get('experience', 'none')
        if experience == 'none':
            risk_score += 1
        elif experience == 'some':
            risk_score += 2
        else:
            risk_score += 3

        # Question 5: Investment goal
        goal = answers.get('goal', 'preservation')
        if goal == 'preservation':
            risk_score += 1
        elif goal == 'income':
            risk_score += 2
        else:  # growth
            risk_score += 3

        # Determine risk level
        if risk_score <= 7:
            risk_level = 'LOW'
        elif risk_score <= 11:
            risk_level = 'MEDIUM'
        else:
            risk_level = 'HIGH'

        # Sector preferences
        sector_prefs = self._determine_sector_preferences(answers)

        return {
            'risk_score': risk_score,
            'risk_level': risk_level,
            'investment_amount': amount,
            'investment_period': period,
            'loss_tolerance': loss_tolerance,
            'experience': experience,
            'goal': goal,
            'preferred_sectors': sector_prefs,
            'recommendation': self._get_risk_level_recommendation(risk_level)
        }

    def _determine_sector_preferences(self, answers: Dict) -> List[str]:
        """Determine preferred sectors based on user profile"""
        goal = answers.get('goal', 'preservation')
        period = answers.get('investment_period', 'short')

        if goal == 'preservation':
            return ['금융', '통신', '유틸리티']
        elif goal == 'income':
            return ['금융', 'REIT', '통신']
        else:  # growth
            if period == 'long':
                return ['IT/반도체', '바이오', '신재생에너지']
            else:
                return ['IT/반도체', '자동차', '화학']

    def _get_risk_level_recommendation(self, risk_level: str) -> str:
        """Get recommendation text for risk level"""
        recommendations = {
            'LOW': "안정적인 대형주 중심으로 투자하시는 것을 추천합니다. 배당주와 우량주에 집중하세요.",
            'MEDIUM': "중대형주와 성장주를 균형있게 투자하시는 것을 추천합니다. 적절한 위험 관리가 필요합니다.",
            'HIGH': "성장 가능성이 높은 종목에 투자할 수 있습니다. 다만 변동성이 클 수 있으니 주의하세요."
        }
        return recommendations.get(risk_level, recommendations['LOW'])
