"""
FastAPI Main Application
Stock Intelligence System
"""

from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from app.config import settings, validate_config
from app.database.session import get_db, init_db
from app.models.stock import Stock, StockPrice, USIndex
from app.collectors.kis_collector import KISCollector
from app.collectors.yahoo_collector import YahooCollector
from app.collectors.dart_collector import DARTCollector
from app.utils.logger import api_logger


# Initialize FastAPI app
app = FastAPI(
    title="Stock Intelligence System API",
    description="한국 주식 자동매매 지원 시스템 API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify allowed origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    """
    Run on application startup
    """
    api_logger.info("Starting Stock Intelligence System API")

    # Validate configuration
    try:
        if settings.APP_ENV == "production":
            validate_config()
        api_logger.info("Configuration validated successfully")
    except ValueError as e:
        api_logger.error(f"Configuration validation failed: {str(e)}")
        if settings.APP_ENV == "production":
            raise

    # Initialize database
    try:
        init_db()
        api_logger.info("Database initialized successfully")
    except Exception as e:
        api_logger.error(f"Database initialization failed: {str(e)}")


@app.on_event("shutdown")
async def shutdown_event():
    """
    Run on application shutdown
    """
    api_logger.info("Shutting down Stock Intelligence System API")


# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0",
        "environment": settings.APP_ENV
    }


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Stock Intelligence System API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }


# ==================== Stock Endpoints ====================

@app.get("/api/v1/stocks")
async def list_stocks(
    skip: int = 0,
    limit: int = 100,
    market: Optional[str] = None,
    sector: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    List all stocks

    Args:
        skip: Number of records to skip
        limit: Maximum number of records to return
        market: Filter by market (KOSPI/KOSDAQ)
        sector: Filter by sector
        db: Database session

    Returns:
        List of stocks
    """
    query = db.query(Stock)

    if market:
        query = query.filter(Stock.market == market)

    if sector:
        query = query.filter(Stock.sector == sector)

    stocks = query.offset(skip).limit(limit).all()

    return {
        "status": "success",
        "data": {
            "stocks": [
                {
                    "code": stock.code,
                    "name": stock.name,
                    "market": stock.market,
                    "sector": stock.sector,
                    "market_cap": stock.market_cap
                }
                for stock in stocks
            ],
            "total": query.count(),
            "skip": skip,
            "limit": limit
        }
    }


@app.get("/api/v1/stocks/{stock_code}")
async def get_stock(
    stock_code: str,
    include_prices: bool = False,
    db: Session = Depends(get_db)
):
    """
    Get stock details

    Args:
        stock_code: Stock code (6 digits)
        include_prices: Include price history
        db: Database session

    Returns:
        Stock details
    """
    stock = db.query(Stock).filter(Stock.code == stock_code).first()

    if not stock:
        raise HTTPException(status_code=404, detail=f"Stock {stock_code} not found")

    data = {
        "code": stock.code,
        "name": stock.name,
        "market": stock.market,
        "sector": stock.sector,
        "market_cap": stock.market_cap,
        "description": stock.description
    }

    if include_prices:
        # Get latest 30 days of prices
        prices = (
            db.query(StockPrice)
            .filter(StockPrice.stock_code == stock_code)
            .order_by(StockPrice.date.desc())
            .limit(30)
            .all()
        )

        data["prices"] = [
            {
                "date": price.date.isoformat(),
                "open": price.open,
                "high": price.high,
                "low": price.low,
                "close": price.close,
                "volume": price.volume
            }
            for price in prices
        ]

    return {
        "status": "success",
        "data": data
    }


@app.post("/api/v1/stocks/{stock_code}/collect")
async def collect_stock_data(
    stock_code: str,
    db: Session = Depends(get_db)
):
    """
    Collect real-time data for a stock

    Args:
        stock_code: Stock code (6 digits)
        db: Database session

    Returns:
        Collected data
    """
    try:
        # Initialize collector
        collector = KISCollector()

        # Collect data
        data = await collector.safe_collect(stock_code=stock_code)

        if not data:
            raise HTTPException(
                status_code=500,
                detail="Failed to collect stock data"
            )

        api_logger.info(f"Collected data for {stock_code}")

        return {
            "status": "success",
            "data": data
        }

    except Exception as e:
        api_logger.error(f"Error collecting data for {stock_code}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== US Market Endpoints ====================

@app.get("/api/v1/market/us")
async def get_us_markets(db: Session = Depends(get_db)):
    """
    Get US market indices

    Returns:
        US market data
    """
    # Get latest data for each index
    indices = ['SP500', 'NASDAQ', 'DOW']
    data = []

    for index_name in indices:
        # Get symbol for this index
        collector = YahooCollector()
        symbol = collector.INDICES.get(index_name, {}).get('symbol')

        if not symbol:
            continue

        # Get latest record from database
        latest = (
            db.query(USIndex)
            .filter(USIndex.symbol == symbol)
            .order_by(USIndex.date.desc())
            .first()
        )

        if latest:
            data.append({
                "symbol": latest.symbol,
                "name": latest.name,
                "close": float(latest.close),
                "change_rate": float(latest.change_rate) if latest.change_rate else 0,
                "ma_20": float(latest.ma_20) if latest.ma_20 else None,
                "above_ma": latest.above_ma,
                "signal": "BULLISH" if latest.above_ma else "BEARISH",
                "date": latest.date.isoformat()
            })

    return {
        "status": "success",
        "data": {
            "indices": data,
            "timestamp": datetime.now().isoformat()
        }
    }


@app.post("/api/v1/market/us/collect")
async def collect_us_markets(db: Session = Depends(get_db)):
    """
    Collect US market data

    Returns:
        Collected data
    """
    try:
        collector = YahooCollector()
        results = await collector.collect_all_indices()

        api_logger.info(f"Collected data for {len(results)} US indices")

        return {
            "status": "success",
            "data": {
                "collected": len(results),
                "results": results
            }
        }

    except Exception as e:
        api_logger.error(f"Error collecting US market data: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== Market Overview Endpoint ====================

@app.get("/api/v1/market/overview")
async def get_market_overview(db: Session = Depends(get_db)):
    """
    Get overall market overview

    Returns:
        Market overview data
    """
    # Get US market signal
    sp500 = (
        db.query(USIndex)
        .filter(USIndex.symbol == '^GSPC')
        .order_by(USIndex.date.desc())
        .first()
    )

    us_signal = "NEUTRAL"
    if sp500:
        us_signal = "BULLISH" if sp500.above_ma else "BEARISH"

    # Count stocks by market
    kospi_count = db.query(Stock).filter(Stock.market == 'KOSPI').count()
    kosdaq_count = db.query(Stock).filter(Stock.market == 'KOSDAQ').count()

    return {
        "status": "success",
        "data": {
            "kospi": {
                "total_stocks": kospi_count
            },
            "kosdaq": {
                "total_stocks": kosdaq_count
            },
            "us_markets": {
                "sp500_signal": us_signal,
                "sp500_close": float(sp500.close) if sp500 else None,
                "sp500_ma_20": float(sp500.ma_20) if sp500 and sp500.ma_20 else None
            },
            "timestamp": datetime.now().isoformat()
        }
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower()
    )
