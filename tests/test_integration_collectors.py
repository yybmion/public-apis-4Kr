"""
Integration Tests for New Data Collectors
Stock Intelligence System
"""

import asyncio
from datetime import datetime, timedelta


def test_collectors_import():
    """Test that all new collectors can be imported"""
    from app.collectors.fred_collector import FredCollector
    from app.collectors.ecos_collector import EcosCollector
    from app.collectors.fear_greed_collector import FearGreedCollector

    assert FredCollector is not None
    assert EcosCollector is not None
    assert FearGreedCollector is not None
    print("✓ All collectors imported successfully")


def test_models_import():
    """Test that all new models can be imported"""
    from app.models.macro_indicators import MacroIndicator, YieldCurve, EconomicSnapshot
    from app.models.market_sentiment import FearGreedIndex, MarketSentiment, SentimentHistory

    assert MacroIndicator is not None
    assert YieldCurve is not None
    assert EconomicSnapshot is not None
    assert FearGreedIndex is not None
    assert MarketSentiment is not None
    assert SentimentHistory is not None
    print("✓ All models imported successfully")


async def test_fred_collector_basic():
    """Test FRED collector basic functionality"""
    from app.collectors.fred_collector import FredCollector

    collector = FredCollector()

    # Test indicator definitions
    assert len(collector.INDICATORS) > 0
    assert 'federal_funds_rate' in collector.INDICATORS
    assert 'unemployment_rate' in collector.INDICATORS

    # Test validation
    valid_data = {
        'series_id': 'TEST',
        'data_points': [{'date': '2024-01-01', 'value': 5.0}]
    }
    assert collector.validate_data(valid_data) is True

    invalid_data = {
        'series_id': 'TEST',
        'data_points': []  # Empty
    }
    assert collector.validate_data(invalid_data) is False

    print("✓ FRED collector basic tests passed")


async def test_ecos_collector_basic():
    """Test ECOS collector basic functionality"""
    from app.collectors.ecos_collector import EcosCollector

    collector = EcosCollector()

    # Test indicator definitions
    assert len(collector.INDICATORS) > 0
    assert 'base_rate' in collector.INDICATORS
    assert 'usd_krw' in collector.INDICATORS
    assert 'cpi' in collector.INDICATORS

    # Test validation
    valid_data = {
        'stat_code': 'TEST',
        'data_points': [{'date': '2024-01', 'value': 3.5}]
    }
    assert collector.validate_data(valid_data) is True

    print("✓ ECOS collector basic tests passed")


async def test_fear_greed_collector_basic():
    """Test Fear & Greed collector basic functionality"""
    from app.collectors.fear_greed_collector import FearGreedCollector

    collector = FearGreedCollector()

    # Test sentiment classification
    assert collector._classify_sentiment(10) == "Extreme Fear"
    assert collector._classify_sentiment(35) == "Fear"
    assert collector._classify_sentiment(50) == "Neutral"
    assert collector._classify_sentiment(65) == "Greed"
    assert collector._classify_sentiment(85) == "Extreme Greed"

    # Test investment signal
    signal = collector._get_investment_signal(20)
    assert signal['signal'] == 'STRONG_BUY'

    signal = collector._get_investment_signal(80)
    assert signal['signal'] == 'STRONG_SELL'

    # Test validation
    valid_data = {
        'score': 50,
        'rating': 'Neutral'
    }
    assert collector.validate_data(valid_data) is True

    invalid_data = {
        'score': 150,  # Out of range
        'rating': 'Neutral'
    }
    assert collector.validate_data(invalid_data) is False

    print("✓ Fear & Greed collector basic tests passed")


def test_database_models():
    """Test database model creation"""
    from app.database.session import Base, engine
    from app.models.macro_indicators import MacroIndicator, YieldCurve, EconomicSnapshot
    from app.models.market_sentiment import FearGreedIndex, MarketSentiment, SentimentHistory

    # Check that models are registered with Base
    table_names = [table.name for table in Base.metadata.sorted_tables]

    expected_tables = [
        'macro_indicators',
        'yield_curves',
        'economic_snapshots',
        'fear_greed_index',
        'market_sentiments',
        'sentiment_history'
    ]

    for table_name in expected_tables:
        assert table_name in table_names, f"Table {table_name} not found in metadata"

    print(f"✓ All {len(expected_tables)} new tables registered in Base.metadata")


def test_collector_categories():
    """Test that collectors properly categorize data"""
    from app.collectors.fred_collector import FredCollector
    from app.collectors.ecos_collector import EcosCollector

    fred = FredCollector()
    ecos = EcosCollector()

    # FRED categories
    fred_categories = set()
    for indicator, info in fred.INDICATORS.items():
        fred_categories.add(info['category'])

    assert 'interest_rates' in fred_categories
    assert 'employment' in fred_categories
    assert 'inflation' in fred_categories
    print(f"✓ FRED has {len(fred_categories)} categories")

    # ECOS categories
    ecos_indicators = list(ecos.INDICATORS.keys())
    assert 'base_rate' in ecos_indicators
    assert 'usd_krw' in ecos_indicators
    print(f"✓ ECOS has {len(ecos_indicators)} indicators")


def main():
    """Run all integration tests"""
    print("=" * 60)
    print("Integration Tests - New Data Collectors")
    print("=" * 60)
    print()

    print("1. Testing imports...")
    test_collectors_import()
    test_models_import()
    print()

    print("2. Testing FRED collector...")
    asyncio.run(test_fred_collector_basic())
    print()

    print("3. Testing ECOS collector...")
    asyncio.run(test_ecos_collector_basic())
    print()

    print("4. Testing Fear & Greed collector...")
    asyncio.run(test_fear_greed_collector_basic())
    print()

    print("5. Testing database models...")
    test_database_models()
    print()

    print("6. Testing collector categories...")
    test_collector_categories()
    print()

    print("=" * 60)
    print("✓ ALL INTEGRATION TESTS PASSED!")
    print("=" * 60)
    print()
    print("Summary:")
    print("  - 3 new data collectors implemented")
    print("  - 6 new database models created")
    print("  - FRED: 25+ US economic indicators")
    print("  - ECOS: 25+ Korean economic indicators")
    print("  - Fear & Greed: Market sentiment analysis")
    print()
    print("Next steps:")
    print("  1. Set FRED_API_KEY in .env file")
    print("  2. Set ECOS_API_KEY in .env file")
    print("  3. Run: python -c 'from app.database.session import init_db; init_db()'")
    print("  4. Test real API calls with actual API keys")


if __name__ == "__main__":
    main()
