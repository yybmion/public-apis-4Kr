"""
FastAPI Main Application
Stock Intelligence System
"""

from fastapi import FastAPI, Depends, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Optional, Dict
from datetime import datetime, timedelta
from pydantic import BaseModel
import pandas as pd
import tempfile
import os

from app.config import settings, validate_config
from app.database.session import get_db, init_db
from app.models.stock import Stock, StockPrice, USIndex, Recommendation, BacktestResult, StockNews
from app.collectors.kis_collector import KISCollector
from app.collectors.yahoo_collector import YahooCollector
from app.collectors.dart_collector import DARTCollector
from app.collectors.news_collector import NewsCollector, SentimentAnalyzer
from app.analyzers.technical_analyzer import TechnicalAnalyzer
from app.analyzers.signal_detector import SignalDetector
from app.analyzers.backtest_engine import BacktestEngine, SP500MAStrategy, GoldenCrossStrategy
from app.analyzers.chart_ocr import ChartOCRAnalyzer, MockChartAnalyzer
from app.recommenders.beginner_recommender import BeginnerRecommender
from app.recommenders.sector_analyzer import SectorAnalyzer
from app.utils.logger import api_logger


# Pydantic models for request/response
class UserProfileRequest(BaseModel):
    investment_amount: int
    investment_period: str  # 'short', 'medium', 'long'
    loss_tolerance: str  # 'low', 'medium', 'high'
    experience: str  # 'none', 'beginner', 'intermediate'
    goal: str  # 'preservation', 'income', 'growth'


class BacktestRequest(BaseModel):
    stock_code: str
    strategy: str  # 'sp500_ma', 'golden_cross'
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    initial_cash: int = 10_000_000
    ma_period: Optional[int] = 20
    fast_period: Optional[int] = 5
    slow_period: Optional[int] = 20


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


# ==================== Recommendation Endpoints ====================

@app.post("/api/v1/recommendations/analyze-profile")
async def analyze_user_profile(request: UserProfileRequest, db: Session = Depends(get_db)):
    """
    Analyze user profile and determine risk level

    Args:
        request: User profile questionnaire answers
        db: Database session

    Returns:
        Risk profile and investment recommendations
    """
    try:
        recommender = BeginnerRecommender(db)

        profile = recommender.analyze_user_profile({
            'investment_amount': request.investment_amount,
            'investment_period': request.investment_period,
            'loss_tolerance': request.loss_tolerance,
            'experience': request.experience,
            'goal': request.goal
        })

        return {
            "status": "success",
            "data": profile
        }

    except Exception as e:
        api_logger.error(f"Error analyzing user profile: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/recommendations")
async def get_recommendations(
    risk_level: Optional[str] = None,
    limit: int = 10,
    save_to_db: bool = False,
    db: Session = Depends(get_db)
):
    """
    Get stock recommendations for beginners

    Args:
        risk_level: Filter by risk level (LOW, MEDIUM, HIGH)
        limit: Maximum number of recommendations
        save_to_db: Save recommendations to database
        db: Database session

    Returns:
        List of recommended stocks with scores and reasons
    """
    try:
        recommender = BeginnerRecommender(db)

        recommendations = recommender.recommend(
            risk_level=risk_level,
            limit=limit,
            save_to_db=save_to_db
        )

        return {
            "status": "success",
            "data": {
                "recommendations": recommendations,
                "total": len(recommendations),
                "risk_level": risk_level or "ALL"
            }
        }

    except Exception as e:
        api_logger.error(f"Error getting recommendations: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/recommendations/history")
async def get_recommendation_history(
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """
    Get recommendation history from database

    Args:
        limit: Maximum number of records
        db: Database session

    Returns:
        Historical recommendations
    """
    try:
        recommendations = (
            db.query(Recommendation)
            .order_by(Recommendation.created_at.desc())
            .limit(limit)
            .all()
        )

        return {
            "status": "success",
            "data": {
                "recommendations": [
                    {
                        "stock_code": rec.stock_code,
                        "stock_name": rec.stock_name,
                        "score": rec.score,
                        "reasons": rec.reasons,
                        "risk_level": rec.risk_level,
                        "created_at": rec.created_at.isoformat()
                    }
                    for rec in recommendations
                ],
                "total": len(recommendations)
            }
        }

    except Exception as e:
        api_logger.error(f"Error getting recommendation history: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== Signal Detection Endpoints ====================

@app.get("/api/v1/signals/us-market")
async def get_us_market_signal(db: Session = Depends(get_db)):
    """
    Get US market signal based on S&P 500 vs MA(20)

    Returns:
        US market signal and recommendation
    """
    try:
        detector = SignalDetector(db)
        signal = detector.get_us_market_signal()

        return {
            "status": "success",
            "data": signal
        }

    except Exception as e:
        api_logger.error(f"Error getting US market signal: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/signals/{stock_code}")
async def detect_stock_signals(stock_code: str, db: Session = Depends(get_db)):
    """
    Detect trading signals for a specific stock

    Args:
        stock_code: Stock code (6 digits)
        db: Database session

    Returns:
        Trading signals and recommended action
    """
    try:
        # Get stock info
        stock = db.query(Stock).filter(Stock.code == stock_code).first()
        if not stock:
            raise HTTPException(status_code=404, detail=f"Stock {stock_code} not found")

        # Get price history
        prices = (
            db.query(StockPrice)
            .filter(StockPrice.stock_code == stock_code)
            .order_by(StockPrice.date.desc())
            .limit(100)
            .all()
        )

        if len(prices) < 20:
            raise HTTPException(status_code=400, detail="Insufficient price data")

        # Convert to DataFrame
        df = pd.DataFrame([
            {
                'date': p.date,
                'open': p.open,
                'high': p.high,
                'low': p.low,
                'close': p.close,
                'volume': p.volume
            }
            for p in reversed(prices)
        ])

        # Detect signals
        detector = SignalDetector(db)
        signals = detector.detect_stock_signals(df, stock_code, stock.name)

        return {
            "status": "success",
            "data": signals
        }

    except HTTPException:
        raise
    except Exception as e:
        api_logger.error(f"Error detecting signals for {stock_code}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/signals/{stock_code}/combined")
async def get_combined_signal(stock_code: str, db: Session = Depends(get_db)):
    """
    Get combined signal (US market + Korean stock)

    Args:
        stock_code: Stock code (6 digits)
        db: Database session

    Returns:
        Combined trading signal with action
    """
    try:
        # Get stock info
        stock = db.query(Stock).filter(Stock.code == stock_code).first()
        if not stock:
            raise HTTPException(status_code=404, detail=f"Stock {stock_code} not found")

        # Get price history
        prices = (
            db.query(StockPrice)
            .filter(StockPrice.stock_code == stock_code)
            .order_by(StockPrice.date.desc())
            .limit(100)
            .all()
        )

        if len(prices) < 20:
            raise HTTPException(status_code=400, detail="Insufficient price data")

        # Convert to DataFrame
        df = pd.DataFrame([
            {
                'date': p.date,
                'open': p.open,
                'high': p.high,
                'low': p.low,
                'close': p.close,
                'volume': p.volume
            }
            for p in reversed(prices)
        ])

        # Get combined signal
        detector = SignalDetector(db)
        stock_signals = detector.detect_stock_signals(df, stock_code, stock.name)
        us_signal = detector.get_us_market_signal()
        combined = detector.generate_combined_signal(stock_signals, us_signal)

        return {
            "status": "success",
            "data": combined
        }

    except HTTPException:
        raise
    except Exception as e:
        api_logger.error(f"Error getting combined signal for {stock_code}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== Backtesting Endpoints ====================

@app.post("/api/v1/backtest/run")
async def run_backtest(request: BacktestRequest, db: Session = Depends(get_db)):
    """
    Run backtesting for a stock with specified strategy

    Args:
        request: Backtest configuration
        db: Database session

    Returns:
        Backtest results with performance metrics
    """
    try:
        # Get stock data
        end_date = datetime.strptime(request.end_date, '%Y-%m-%d').date() if request.end_date else datetime.now().date()
        start_date = datetime.strptime(request.start_date, '%Y-%m-%d').date() if request.start_date else (end_date - timedelta(days=365))

        prices = (
            db.query(StockPrice)
            .filter(
                StockPrice.stock_code == request.stock_code,
                StockPrice.date >= start_date,
                StockPrice.date <= end_date
            )
            .order_by(StockPrice.date)
            .all()
        )

        if len(prices) < 60:
            raise HTTPException(status_code=400, detail="Insufficient historical data (need at least 60 days)")

        # Convert to DataFrame
        stock_df = pd.DataFrame([
            {
                'date': p.date,
                'open': p.open,
                'high': p.high,
                'low': p.low,
                'close': p.close,
                'volume': p.volume
            }
            for p in prices
        ])

        # Get US data if using SP500 strategy
        us_df = None
        if request.strategy == 'sp500_ma':
            us_prices = (
                db.query(USIndex)
                .filter(
                    USIndex.symbol == '^GSPC',
                    USIndex.date >= start_date,
                    USIndex.date <= end_date
                )
                .order_by(USIndex.date)
                .all()
            )

            if len(us_prices) < 60:
                raise HTTPException(status_code=400, detail="Insufficient US market data")

            us_df = pd.DataFrame([
                {
                    'date': p.date,
                    'open': float(p.close) * 0.99,  # Approximate
                    'high': float(p.close) * 1.01,
                    'low': float(p.close) * 0.99,
                    'close': float(p.close),
                    'volume': 1000000
                }
                for p in us_prices
            ])

        # Run backtest
        engine = BacktestEngine(db)

        if request.strategy == 'sp500_ma':
            result = engine.run_sp500_strategy_backtest(
                stock_code=request.stock_code,
                stock_data=stock_df,
                us_data=us_df,
                initial_cash=request.initial_cash,
                ma_period=request.ma_period
            )
        elif request.strategy == 'golden_cross':
            result = engine.run_golden_cross_backtest(
                stock_code=request.stock_code,
                stock_data=stock_df,
                initial_cash=request.initial_cash,
                fast_period=request.fast_period,
                slow_period=request.slow_period
            )
        else:
            raise HTTPException(status_code=400, detail=f"Unknown strategy: {request.strategy}")

        return {
            "status": "success",
            "data": result
        }

    except HTTPException:
        raise
    except Exception as e:
        api_logger.error(f"Error running backtest: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/backtest/results")
async def get_backtest_results(
    limit: int = 50,
    strategy: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Get historical backtest results

    Args:
        limit: Maximum number of records
        strategy: Filter by strategy name
        db: Database session

    Returns:
        Historical backtest results
    """
    try:
        query = db.query(BacktestResult).order_by(BacktestResult.created_at.desc())

        if strategy:
            query = query.filter(BacktestResult.strategy_name == strategy)

        results = query.limit(limit).all()

        return {
            "status": "success",
            "data": {
                "results": [
                    {
                        "id": r.id,
                        "strategy_name": r.strategy_name,
                        "description": r.description,
                        "start_date": r.start_date.isoformat(),
                        "end_date": r.end_date.isoformat(),
                        "initial_capital": r.initial_capital,
                        "final_capital": r.final_capital,
                        "total_return": r.total_return,
                        "cagr": r.cagr,
                        "mdd": r.mdd,
                        "sharpe_ratio": r.sharpe_ratio,
                        "win_rate": r.win_rate,
                        "total_trades": r.total_trades,
                        "created_at": r.created_at.isoformat()
                    }
                    for r in results
                ],
                "total": len(results)
            }
        }

    except Exception as e:
        api_logger.error(f"Error getting backtest results: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== Sector Analysis Endpoints ====================

@app.get("/api/v1/sectors")
async def get_all_sectors(db: Session = Depends(get_db)):
    """
    Get all available sectors

    Returns:
        List of sectors with information
    """
    try:
        analyzer = SectorAnalyzer(db)
        sectors = analyzer.get_all_sectors()

        sector_info = []
        for sector in sectors:
            info = analyzer.get_sector_info(sector)
            sector_info.append(info)

        return {
            "status": "success",
            "data": {
                "sectors": sector_info,
                "total": len(sector_info)
            }
        }

    except Exception as e:
        api_logger.error(f"Error getting sectors: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/sectors/beginner-friendly")
async def get_beginner_friendly_sectors(db: Session = Depends(get_db)):
    """
    Get beginner-friendly sectors

    Returns:
        List of recommended sectors for beginners
    """
    try:
        analyzer = SectorAnalyzer(db)
        sectors = analyzer.get_beginner_friendly_sectors()

        sector_info = []
        for sector in sectors:
            info = analyzer.get_sector_info(sector)
            sector_info.append(info)

        return {
            "status": "success",
            "data": {
                "sectors": sector_info,
                "total": len(sector_info)
            }
        }

    except Exception as e:
        api_logger.error(f"Error getting beginner-friendly sectors: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/sectors/{sector_name}")
async def get_sector_details(sector_name: str, db: Session = Depends(get_db)):
    """
    Get detailed information about a sector

    Args:
        sector_name: Sector name (e.g., 'IT/반도체')
        db: Database session

    Returns:
        Detailed sector information
    """
    try:
        analyzer = SectorAnalyzer(db)

        # Get sector info
        info = analyzer.get_sector_info(sector_name)
        if not info:
            raise HTTPException(status_code=404, detail=f"Sector {sector_name} not found")

        # Get sector guide
        guide = analyzer.format_sector_guide(sector_name)

        # Get stocks in sector
        stocks = (
            db.query(Stock)
            .filter(Stock.sector == sector_name)
            .order_by(Stock.market_cap.desc())
            .limit(20)
            .all()
        )

        return {
            "status": "success",
            "data": {
                "info": info,
                "guide": guide,
                "stocks": [
                    {
                        "code": s.code,
                        "name": s.name,
                        "market": s.market,
                        "market_cap": s.market_cap
                    }
                    for s in stocks
                ]
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        api_logger.error(f"Error getting sector details for {sector_name}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== Chart OCR Endpoints ====================

@app.post("/api/v1/chart/analyze")
async def analyze_chart_image(
    file: UploadFile = File(...),
    extract_indicators: bool = True
):
    """
    Analyze stock chart image using OCR

    Args:
        file: Chart image file (PNG, JPG, etc.)
        extract_indicators: Extract technical indicators

    Returns:
        Extracted chart data and analysis
    """
    try:
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as tmp:
            content = await file.read()
            tmp.write(content)
            tmp_path = tmp.name

        try:
            # Try to use real OCR analyzer
            if settings.UPSTAGE_API_KEY:
                analyzer = ChartOCRAnalyzer()
            else:
                api_logger.warning("Upstage API key not configured, using mock analyzer")
                analyzer = MockChartAnalyzer()

            # Analyze chart
            result = analyzer.analyze_chart(tmp_path, extract_indicators=extract_indicators)

            return {
                "status": "success",
                "data": result
            }

        finally:
            # Clean up temp file
            if os.path.exists(tmp_path):
                os.remove(tmp_path)

    except Exception as e:
        api_logger.error(f"Error analyzing chart image: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== News & Sentiment Endpoints ====================

@app.get("/api/v1/news/{stock_code}")
async def get_stock_news(
    stock_code: str,
    days: int = 7,
    db: Session = Depends(get_db)
):
    """
    Get news articles for a stock

    Args:
        stock_code: Stock code (6 digits)
        days: Number of days to look back
        db: Database session

    Returns:
        News articles with sentiment
    """
    try:
        # Get stock name
        stock = db.query(Stock).filter(Stock.code == stock_code).first()
        if not stock:
            raise HTTPException(status_code=404, detail=f"Stock {stock_code} not found")

        # Get news from database
        start_date = datetime.now() - timedelta(days=days)
        news = (
            db.query(StockNews)
            .filter(
                StockNews.stock_code == stock_code,
                StockNews.published_at >= start_date
            )
            .order_by(StockNews.published_at.desc())
            .all()
        )

        # If no news in database, collect new
        if not news:
            collector = NewsCollector()
            end_date = datetime.now().strftime('%Y-%m-%d')
            start_date_str = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')

            data = await collector.collect(
                keyword=stock.name,
                start_date=start_date_str,
                end_date=end_date
            )

            # Analyze sentiment
            analyzer = SentimentAnalyzer()
            articles = analyzer.analyze_articles(data['articles'])

            # Save to database
            collector.save_to_database(articles, stock_code, db)

            return {
                "status": "success",
                "data": {
                    "stock_code": stock_code,
                    "stock_name": stock.name,
                    "articles": articles,
                    "total": len(articles),
                    "source": "fresh_collection"
                }
            }

        # Return news from database
        return {
            "status": "success",
            "data": {
                "stock_code": stock_code,
                "stock_name": stock.name,
                "articles": [
                    {
                        "title": n.title,
                        "content": n.content,
                        "source": n.source,
                        "source_tier": n.source_tier,
                        "url": n.url,
                        "published_at": n.published_at.isoformat() if n.published_at else None,
                        "sentiment_label": n.sentiment_label,
                        "sentiment_score": n.sentiment_score
                    }
                    for n in news
                ],
                "total": len(news),
                "source": "database"
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        api_logger.error(f"Error getting news for {stock_code}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/sentiment/{stock_code}")
async def get_sentiment_analysis(
    stock_code: str,
    days: int = 7,
    db: Session = Depends(get_db)
):
    """
    Get aggregated sentiment analysis for a stock

    Args:
        stock_code: Stock code (6 digits)
        days: Number of days to analyze
        db: Database session

    Returns:
        Aggregated sentiment metrics
    """
    try:
        # Get stock name
        stock = db.query(Stock).filter(Stock.code == stock_code).first()
        if not stock:
            raise HTTPException(status_code=404, detail=f"Stock {stock_code} not found")

        # Get news
        start_date = datetime.now() - timedelta(days=days)
        news = (
            db.query(StockNews)
            .filter(
                StockNews.stock_code == stock_code,
                StockNews.published_at >= start_date
            )
            .all()
        )

        if not news:
            return {
                "status": "success",
                "data": {
                    "stock_code": stock_code,
                    "stock_name": stock.name,
                    "sentiment": {
                        "overall_sentiment": "neutral",
                        "average_score": 0.0,
                        "positive_count": 0,
                        "negative_count": 0,
                        "neutral_count": 0,
                        "total_articles": 0
                    },
                    "message": "No news articles available"
                }
            }

        # Convert to list of dicts
        articles = [
            {
                "sentiment_label": n.sentiment_label or "neutral",
                "sentiment_score": n.sentiment_score or 0.0,
                "source_tier": n.source_tier
            }
            for n in news
        ]

        # Aggregate sentiment
        analyzer = SentimentAnalyzer()
        aggregated = analyzer.aggregate_sentiment(articles, weight_by_tier=True)

        return {
            "status": "success",
            "data": {
                "stock_code": stock_code,
                "stock_name": stock.name,
                "period_days": days,
                "sentiment": aggregated
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        api_logger.error(f"Error getting sentiment for {stock_code}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower()
    )
