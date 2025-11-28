"""
Pytest Configuration and Fixtures
"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database.session import Base
from app.models.stock import Stock, StockPrice, USIndex


@pytest.fixture(scope="session")
def test_db_engine():
    """Create test database engine"""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    return engine


@pytest.fixture(scope="function")
def test_db(test_db_engine):
    """Create test database session"""
    TestingSessionLocal = sessionmaker(bind=test_db_engine)
    session = TestingSessionLocal()

    # Add sample data
    sample_stock = Stock(
        code="005930",
        name="삼성전자",
        market="KOSPI",
        sector="IT/반도체",
        market_cap=400_000_000_000_000
    )
    session.add(sample_stock)

    sample_us_index = USIndex(
        symbol="^GSPC",
        name="S&P 500",
        close=4500.0,
        ma_20=4450.0,
        above_ma=True
    )
    session.add(sample_us_index)

    session.commit()

    yield session

    session.close()
