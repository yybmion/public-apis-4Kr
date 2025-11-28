"""
Sector Analyzer - Analyze and Recommend by Sector
Stock Intelligence System
"""

from typing import Dict, List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.stock import Stock, StockPrice
from app.utils.logger import LoggerMixin


class SectorAnalyzer(LoggerMixin):
    """
    Analyze sectors and provide sector-specific guidance
    """

    # Sector information for beginners
    SECTOR_INFO = {
        'IT/반도체': {
            'emoji': '⚡',
            'name': 'IT/반도체',
            'description': '정보기술 및 반도체 산업',
            'characteristics': [
                '한국의 강점 산업 (삼성, SK하이닉스)',
                '고성장 가능성',
                '글로벌 경쟁력 보유'
            ],
            'risks': [
                '경기 민감도 높음',
                '기술 변화 빠름',
                '반도체 업황 사이클 존재'
            ],
            'risk_level': 'MEDIUM',
            'recommended_for': ['성장형', '중장기 투자자'],
            'key_factors': ['반도체 가격', '글로벌 IT 수요', '달러 환율'],
            'representative_stocks': ['삼성전자', 'SK하이닉스', 'NAVER', '카카오']
        },
        '금융': {
            'emoji': '🏦',
            'name': '금융',
            'description': '은행, 증권, 보험',
            'characteristics': [
                '안정적인 배당',
                '경기 회복기에 수혜',
                '대형주 위주로 안정성'
            ],
            'risks': [
                '금리 변동에 민감',
                '부실 채권 리스크',
                '규제 리스크'
            ],
            'risk_level': 'LOW',
            'recommended_for': ['안정형', '배당 투자자'],
            'key_factors': ['기준금리', '대출 성장률', '부동산 시장'],
            'representative_stocks': ['KB금융', '신한지주', '하나금융지주']
        },
        '자동차': {
            'emoji': '🚗',
            'name': '자동차',
            'description': '자동차 제조 및 부품',
            'characteristics': [
                '수출 중심 산업',
                '전기차 전환 진행 중',
                '대형 제조업'
            ],
            'risks': [
                '원자재 가격 변동',
                '환율 리스크',
                '글로벌 경쟁 심화'
            ],
            'risk_level': 'MEDIUM',
            'recommended_for': ['성장형', '장기 투자자'],
            'key_factors': ['글로벌 자동차 판매', '전기차 보급률', '환율'],
            'representative_stocks': ['현대차', '기아', '현대모비스']
        },
        '화학': {
            'emoji': '🧪',
            'name': '화학',
            'description': '정유, 화학, 소재',
            'characteristics': [
                '경기 선행 지표',
                '원자재 기반 산업',
                '수출 비중 높음'
            ],
            'risks': [
                '유가 변동',
                '중국 경기에 민감',
                '환경 규제'
            ],
            'risk_level': 'MEDIUM',
            'recommended_for': ['경기 회복기 투자자'],
            'key_factors': ['유가', '중국 경기', '글로벌 수요'],
            'representative_stocks': ['LG화학', 'SK이노베이션', '롯데케미칼']
        },
        '바이오/헬스케어': {
            'emoji': '💊',
            'name': '바이오/헬스케어',
            'description': '제약, 바이오, 의료기기',
            'characteristics': [
                '고성장 산업',
                '고령화 수혜',
                '연구개발 중심'
            ],
            'risks': [
                '임상 실패 리스크',
                '높은 변동성',
                '규제 리스크'
            ],
            'risk_level': 'HIGH',
            'recommended_for': ['공격형', '장기 투자자'],
            'key_factors': ['신약 개발', '임상 결과', '글로벌 보건 이슈'],
            'representative_stocks': ['삼성바이오로직스', '셀트리온', 'SK바이오팜']
        },
        '에너지': {
            'emoji': '⚡',
            'name': '에너지',
            'description': '전력, 신재생에너지',
            'characteristics': [
                '필수 유틸리티',
                '안정적 수익',
                '신재생에너지 성장'
            ],
            'risks': [
                '규제 산업',
                '초기 투자 큰 편',
                '정책 변화에 민감'
            ],
            'risk_level': 'LOW',
            'recommended_for': ['안정형', '배당 투자자'],
            'key_factors': ['전력 수요', '신재생에너지 정책', '탄소중립'],
            'representative_stocks': ['한국전력', 'SK E&S', 'OCI']
        },
        '소비재': {
            'emoji': '🛍️',
            'name': '소비재',
            'description': '식품, 의류, 생활용품',
            'characteristics': [
                '경기 방어주',
                '브랜드 파워 중요',
                '안정적 수요'
            ],
            'risks': [
                '성장성 제한적',
                '경쟁 치열',
                '원자재 가격 영향'
            ],
            'risk_level': 'LOW',
            'recommended_for': ['안정형', '초보자'],
            'key_factors': ['소비 심리', '원자재 가격', '트렌드 변화'],
            'representative_stocks': ['CJ제일제당', '오리온', 'LG생활건강']
        },
        '통신': {
            'emoji': '📡',
            'name': '통신',
            'description': '이동통신, 인터넷',
            'characteristics': [
                '과점 시장',
                '안정적 현금흐름',
                '높은 배당'
            ],
            'risks': [
                '성장 둔화',
                '경쟁 심화',
                '규제 리스크'
            ],
            'risk_level': 'LOW',
            'recommended_for': ['안정형', '배당 투자자'],
            'key_factors': ['5G 가입자', '데이터 사용량', '규제'],
            'representative_stocks': ['SK텔레콤', 'KT', 'LG유플러스']
        },
        '건설': {
            'emoji': '🏗️',
            'name': '건설',
            'description': '건설, 플랜트',
            'characteristics': [
                '경기 민감',
                '수주 기반 매출',
                '해외 사업 비중'
            ],
            'risks': [
                '부동산 정책 영향',
                '공사 지연 리스크',
                '수주 변동성'
            ],
            'risk_level': 'MEDIUM',
            'recommended_for': ['경기 회복기 투자자'],
            'key_factors': ['부동산 시장', '정부 발주', '해외 수주'],
            'representative_stocks': ['삼성물산', '현대건설', '대우건설']
        },
        '유통': {
            'emoji': '🏪',
            'name': '유통',
            'description': '백화점, 마트, 이커머스',
            'characteristics': [
                '소비 트렌드 반영',
                '온라인 전환 가속',
                '경기 민감'
            ],
            'risks': [
                '경쟁 심화',
                '마진율 하락',
                '소비 심리 영향'
            ],
            'risk_level': 'MEDIUM',
            'recommended_for': ['성장형', '트렌드 투자자'],
            'key_factors': ['소비 심리', '온라인 쇼핑 증가', '경쟁'],
            'representative_stocks': ['신세계', '롯데쇼핑', '쿠팡']
        }
    }

    def __init__(self, db: Session):
        super().__init__()
        self.db = db

    def get_sector_info(self, sector: str) -> Optional[Dict]:
        """Get detailed information about a sector"""
        return self.SECTOR_INFO.get(sector)

    def get_all_sectors(self) -> List[Dict]:
        """Get information about all sectors"""
        return list(self.SECTOR_INFO.values())

    def get_sector_performance(self, sector: str, days: int = 30) -> Dict:
        """
        Calculate sector performance metrics

        Args:
            sector: Sector name
            days: Number of days to analyze

        Returns:
            Performance metrics
        """
        # Get all stocks in sector
        stocks = self.db.query(Stock).filter(Stock.sector == sector).all()

        if not stocks:
            return {
                'sector': sector,
                'stock_count': 0,
                'avg_return': 0,
                'avg_volume_change': 0
            }

        total_return = 0
        valid_stocks = 0

        for stock in stocks:
            # Get price data for the period
            prices = (
                self.db.query(StockPrice)
                .filter(StockPrice.stock_code == stock.code)
                .order_by(StockPrice.date.desc())
                .limit(days)
                .all()
            )

            if len(prices) >= 2:
                latest = prices[0].close
                oldest = prices[-1].close
                stock_return = ((latest - oldest) / oldest) * 100
                total_return += stock_return
                valid_stocks += 1

        avg_return = total_return / valid_stocks if valid_stocks > 0 else 0

        return {
            'sector': sector,
            'stock_count': len(stocks),
            'avg_return': avg_return,
            'valid_stocks': valid_stocks
        }

    def recommend_sector(
        self,
        risk_level: str = 'LOW',
        investment_goal: str = 'preservation'
    ) -> List[Dict]:
        """
        Recommend sectors based on user profile

        Args:
            risk_level: User's risk tolerance
            investment_goal: preservation, income, or growth

        Returns:
            List of recommended sectors
        """
        recommendations = []

        for sector_name, sector_info in self.SECTOR_INFO.items():
            # Calculate match score
            match_score = 0

            # Risk level match
            if sector_info['risk_level'] == risk_level:
                match_score += 50
            elif (risk_level == 'LOW' and sector_info['risk_level'] == 'MEDIUM') or \
                 (risk_level == 'HIGH' and sector_info['risk_level'] == 'MEDIUM'):
                match_score += 25

            # Investment goal match
            if investment_goal == 'preservation' and sector_info['risk_level'] == 'LOW':
                match_score += 30
            elif investment_goal == 'income' and sector_info['risk_level'] in ['LOW', 'MEDIUM']:
                match_score += 30
            elif investment_goal == 'growth' and sector_info['risk_level'] in ['MEDIUM', 'HIGH']:
                match_score += 30

            # Get performance
            performance = self.get_sector_performance(sector_name)

            recommendations.append({
                **sector_info,
                'match_score': match_score,
                'performance': performance
            })

        # Sort by match score
        recommendations.sort(key=lambda x: x['match_score'], reverse=True)

        return recommendations

    def get_sector_comparison(self) -> List[Dict]:
        """
        Get comparison of all sectors

        Returns:
            List of sectors with performance metrics
        """
        comparison = []

        for sector_name, sector_info in self.SECTOR_INFO.items():
            # Get stock count
            stock_count = self.db.query(Stock).filter(Stock.sector == sector_name).count()

            # Get performance
            performance = self.get_sector_performance(sector_name)

            comparison.append({
                'sector': sector_name,
                'emoji': sector_info['emoji'],
                'risk_level': sector_info['risk_level'],
                'stock_count': stock_count,
                'avg_return_30d': performance.get('avg_return', 0),
                'description': sector_info['description']
            })

        return comparison

    def get_beginner_friendly_sectors(self) -> List[str]:
        """Get list of sectors suitable for beginners"""
        beginner_sectors = []

        for sector_name, sector_info in self.SECTOR_INFO.items():
            if sector_info['risk_level'] == 'LOW':
                beginner_sectors.append(sector_name)

        return beginner_sectors

    def format_sector_guide(self, sector: str) -> str:
        """
        Format sector information as a beginner-friendly guide

        Args:
            sector: Sector name

        Returns:
            Formatted guide text
        """
        info = self.get_sector_info(sector)

        if not info:
            return f"'{sector}' 섹터 정보를 찾을 수 없습니다."

        guide = f"""
{info['emoji']} **{info['name']}**

📝 **설명**
{info['description']}

✅ **장점**
"""
        for char in info['characteristics']:
            guide += f"• {char}\n"

        guide += f"""
⚠️ **리스크**
"""
        for risk in info['risks']:
            guide += f"• {risk}\n"

        guide += f"""
📊 **위험도**: {info['risk_level']}

👥 **추천 대상**
"""
        for rec in info['recommended_for']:
            guide += f"• {rec}\n"

        guide += f"""
🔍 **주요 체크 포인트**
"""
        for factor in info['key_factors']:
            guide += f"• {factor}\n"

        guide += f"""
🏢 **대표 종목**
"""
        for stock in info['representative_stocks']:
            guide += f"• {stock}\n"

        return guide
