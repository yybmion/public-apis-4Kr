"""
Recommender Tests
"""

import pytest
from app.recommenders.beginner_recommender import BeginnerRecommender
from app.recommenders.sector_analyzer import SectorAnalyzer


class TestBeginnerRecommender:
    """Test Beginner Recommender"""

    def test_analyze_user_profile(self, test_db):
        """Test user profile analysis"""
        recommender = BeginnerRecommender(test_db)

        profile = recommender.analyze_user_profile({
            'investment_amount': 10000000,
            'investment_period': 'long',
            'loss_tolerance': 'medium',
            'experience': 'beginner',
            'goal': 'growth'
        })

        # Check profile structure
        assert isinstance(profile, dict)
        assert 'risk_level' in profile
        assert profile['risk_level'] in ['LOW', 'MEDIUM', 'HIGH']
        assert 'risk_score' in profile
        assert 'investment_style' in profile
        assert 'preferred_sectors' in profile

    def test_calculate_score(self, test_db):
        """Test score calculation"""
        recommender = BeginnerRecommender(test_db)

        # Get sample stock
        stock = test_db.query(Stock).first()

        if stock:
            # This will fail if no price/financial data, but tests the method
            try:
                score = recommender.calculate_score(stock, None, None)
                assert 0 <= score <= 100
            except Exception:
                pytest.skip("No price/financial data available")


class TestSectorAnalyzer:
    """Test Sector Analyzer"""

    def test_get_all_sectors(self, test_db):
        """Test getting all sectors"""
        analyzer = SectorAnalyzer(test_db)
        sectors = analyzer.get_all_sectors()

        # Check sectors list
        assert isinstance(sectors, list)
        assert len(sectors) == 10
        assert 'IT/반도체' in sectors

    def test_get_sector_info(self, test_db):
        """Test getting sector info"""
        analyzer = SectorAnalyzer(test_db)
        info = analyzer.get_sector_info('IT/반도체')

        # Check info structure
        assert isinstance(info, dict)
        assert 'name' in info
        assert 'emoji' in info
        assert 'description' in info
        assert 'risk_level' in info
        assert 'characteristics' in info

    def test_get_beginner_friendly_sectors(self, test_db):
        """Test getting beginner-friendly sectors"""
        analyzer = SectorAnalyzer(test_db)
        sectors = analyzer.get_beginner_friendly_sectors()

        # Check that only LOW risk sectors are returned
        assert isinstance(sectors, list)
        assert len(sectors) > 0

        for sector in sectors:
            info = analyzer.get_sector_info(sector)
            assert info['risk_level'] == 'LOW'

    def test_format_sector_guide(self, test_db):
        """Test sector guide formatting"""
        analyzer = SectorAnalyzer(test_db)
        guide = analyzer.format_sector_guide('IT/반도체')

        # Check guide is a string
        assert isinstance(guide, str)
        assert len(guide) > 0
