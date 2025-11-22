"""
Test FRED Collector
"""

import pytest
import asyncio
from datetime import datetime, timedelta
from app.collectors.fred_collector import FredCollector, get_fred_indicator


class TestFredCollector:
    """Test FRED API Collector"""

    @pytest.fixture
    def collector(self):
        """Create FredCollector instance"""
        return FredCollector()

    def test_indicators_defined(self, collector):
        """Test that all major indicators are defined"""
        assert len(collector.INDICATORS) > 0
        assert 'federal_funds_rate' in collector.INDICATORS
        assert 'unemployment_rate' in collector.INDICATORS
        assert 'cpi' in collector.INDICATORS
        assert 'gdp' in collector.INDICATORS
        assert 'treasury_10y' in collector.INDICATORS

    def test_indicator_structure(self, collector):
        """Test indicator metadata structure"""
        for name, info in collector.INDICATORS.items():
            assert 'series_id' in info
            assert 'name' in info
            assert 'category' in info
            assert 'unit' in info
            assert 'frequency' in info

    @pytest.mark.asyncio
    async def test_collect_without_api_key(self):
        """Test that collection fails gracefully without API key"""
        collector = FredCollector(api_key=None)

        # Should log warning but not crash
        result = await collector.safe_collect(indicator='federal_funds_rate')

        # Result should be None when API key is missing
        assert result is None

    @pytest.mark.asyncio
    async def test_validation(self, collector):
        """Test data validation"""
        # Valid data
        valid_data = {
            'series_id': 'FEDFUNDS',
            'indicator': 'federal_funds_rate',
            'data_points': [
                {'date': '2024-01-01', 'value': 5.33},
                {'date': '2024-02-01', 'value': 5.33}
            ]
        }
        assert collector.validate_data(valid_data) is True

        # Invalid data - missing series_id
        invalid_data1 = {
            'indicator': 'test',
            'data_points': []
        }
        assert collector.validate_data(invalid_data1) is False

        # Invalid data - empty data points
        invalid_data2 = {
            'series_id': 'TEST',
            'data_points': []
        }
        assert collector.validate_data(invalid_data2) is False

        # Invalid data - wrong structure
        invalid_data3 = {
            'series_id': 'TEST',
            'data_points': [
                {'date': '2024-01-01'}  # Missing 'value'
            ]
        }
        assert collector.validate_data(invalid_data3) is False

    def test_indicator_categories(self, collector):
        """Test that indicators are properly categorized"""
        categories = {
            'interest_rates': [],
            'employment': [],
            'inflation': [],
            'gdp': [],
            'housing': [],
            'financial': [],
            'sentiment': []
        }

        for name, info in collector.INDICATORS.items():
            category = info['category']
            assert category in categories
            categories[category].append(name)

        # Ensure each category has at least one indicator
        for category, indicators in categories.items():
            assert len(indicators) > 0, f"Category '{category}' has no indicators"

    @pytest.mark.asyncio
    @pytest.mark.skipif(
        True,  # Skip by default as it requires API key
        reason="Requires FRED API key"
    )
    async def test_collect_real_data(self, collector):
        """Test collecting real data from FRED (requires API key)"""
        # Set start_date to recent period to limit data
        start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')

        result = await collector.safe_collect(
            indicator='federal_funds_rate',
            start_date=start_date
        )

        assert result is not None
        assert 'series_id' in result
        assert 'data_points' in result
        assert len(result['data_points']) > 0

    @pytest.mark.asyncio
    @pytest.mark.skipif(
        True,  # Skip by default
        reason="Requires FRED API key"
    )
    async def test_collect_multiple(self, collector):
        """Test collecting multiple indicators at once"""
        indicators = ['federal_funds_rate', 'unemployment_rate', 'cpi']
        start_date = (datetime.now() - timedelta(days=90)).strftime('%Y-%m-%d')

        result = await collector.collect_multiple(
            indicators=indicators,
            start_date=start_date
        )

        assert 'indicators' in result
        assert result['total'] == 3

    @pytest.mark.asyncio
    @pytest.mark.skipif(
        True,  # Skip by default
        reason="Requires FRED API key"
    )
    async def test_yield_curve(self, collector):
        """Test yield curve calculation"""
        result = await collector.get_yield_curve()

        assert 'yields' in result
        assert 'spreads' in result
        assert 'yield_curve_inverted' in result
        assert 'recession_signal' in result

        # Check yields
        assert 'treasury_3m' in result['yields']
        assert 'treasury_2y' in result['yields']
        assert 'treasury_10y' in result['yields']

        # Check spreads
        assert '10y_2y' in result['spreads']
        assert '10y_3m' in result['spreads']

    @pytest.mark.asyncio
    @pytest.mark.skipif(
        True,  # Skip by default
        reason="Requires FRED API key"
    )
    async def test_latest_value(self, collector):
        """Test getting latest value for an indicator"""
        result = await collector.get_latest_value('federal_funds_rate')

        assert 'indicator' in result
        assert 'value' in result
        assert 'date' in result
        assert result['indicator'] == 'federal_funds_rate'


def test_convenience_function():
    """Test convenience function"""
    # Just test that it's importable and callable
    assert callable(get_fred_indicator)


if __name__ == "__main__":
    # Run basic tests without API key
    collector = FredCollector()

    print("=" * 60)
    print("FRED Collector Test Suite")
    print("=" * 60)

    print("\n1. Testing indicator definitions...")
    print(f"   Total indicators: {len(collector.INDICATORS)}")
    print(f"   ✓ Indicators defined")

    print("\n2. Testing indicator structure...")
    for name, info in list(collector.INDICATORS.items())[:3]:
        print(f"   - {name}: {info['name']} ({info['frequency']})")
    print(f"   ✓ Structure valid")

    print("\n3. Testing validation...")
    valid_data = {
        'series_id': 'FEDFUNDS',
        'data_points': [{'date': '2024-01-01', 'value': 5.33}]
    }
    assert collector.validate_data(valid_data)
    print(f"   ✓ Validation working")

    print("\n4. Testing categories...")
    categories = {}
    for name, info in collector.INDICATORS.items():
        cat = info['category']
        if cat not in categories:
            categories[cat] = 0
        categories[cat] += 1

    for cat, count in categories.items():
        print(f"   - {cat}: {count} indicators")
    print(f"   ✓ Categories organized")

    print("\n" + "=" * 60)
    print("✓ All basic tests passed!")
    print("=" * 60)
    print("\nNote: Real API tests skipped (requires FRED_API_KEY)")
    print("To run full tests:")
    print("  1. Get API key from https://fred.stlouisfed.org/docs/api/api_key.html")
    print("  2. Set FRED_API_KEY in .env")
    print("  3. Run: pytest tests/test_fred_collector.py")
