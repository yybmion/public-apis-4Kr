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
from app.models.llm_analysis import LLMAnalysis, LLMConsensus, LLMPerformance
from app.models.social_media import SocialMediaMention
from app.collectors.kis_collector import KISCollector
from app.collectors.yahoo_collector import YahooCollector
from app.collectors.dart_collector import DARTCollector
from app.collectors.news_collector import NewsCollector, SentimentAnalyzer
from app.collectors.social_collector import TradestieCollector, StockTwitsCollector, collect_all_social_data
from app.analyzers.technical_analyzer import TechnicalAnalyzer
from app.analyzers.signal_detector import SignalDetector
from app.analyzers.backtest_engine import BacktestEngine, SP500MAStrategy, GoldenCrossStrategy
from app.analyzers.chart_ocr import ChartOCRAnalyzer, MockChartAnalyzer
from app.recommenders.beginner_recommender import BeginnerRecommender
from app.recommenders.sector_analyzer import SectorAnalyzer
from app.llm.orchestrator import LLMOrchestrator
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


class LLMAnalyzeRequest(BaseModel):
    stock_code: str
    stock_name: str
    analysis_type: str = "combined_signal"  # 'news_risk', 'combined_signal', 'explanation'
    technical_data: Optional[Dict] = None
    fundamental_data: Optional[Dict] = None
    us_market_data: Optional[Dict] = None
    news_data: Optional[Dict] = None


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


# ==================== LLM Multi-Agent Endpoints ====================

@app.post("/api/v1/llm/analyze-multi")
async def analyze_with_multi_llm(request: LLMAnalyzeRequest, db: Session = Depends(get_db)):
    """
    Analyze stock with multiple LLM agents in parallel

    Args:
        request: Analysis request with stock data
        db: Database session

    Returns:
        Multi-agent consensus analysis
    """
    try:
        orchestrator = LLMOrchestrator(db)

        result = await orchestrator.analyze_multi_agent(
            stock_code=request.stock_code,
            stock_name=request.stock_name,
            technical_data=request.technical_data,
            fundamental_data=request.fundamental_data,
            us_market_data=request.us_market_data,
            news_data=request.news_data,
            analysis_type=request.analysis_type
        )

        return {
            "status": "success",
            "data": result
        }

    except Exception as e:
        api_logger.error(f"Error in multi-LLM analysis for {request.stock_code}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/llm/consensus/{stock_code}")
async def get_llm_consensus(
    stock_code: str,
    limit: int = 10,
    analysis_type: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Get LLM consensus results for a stock

    Args:
        stock_code: Stock code (6 digits)
        limit: Maximum number of records
        analysis_type: Filter by analysis type
        db: Database session

    Returns:
        Consensus results
    """
    try:
        query = db.query(LLMConsensus).filter(LLMConsensus.stock_code == stock_code)

        if analysis_type:
            query = query.filter(LLMConsensus.analysis_type == analysis_type)

        results = query.order_by(LLMConsensus.created_at.desc()).limit(limit).all()

        return {
            "status": "success",
            "data": {
                "stock_code": stock_code,
                "consensus_results": [
                    {
                        "id": r.id,
                        "analysis_type": r.analysis_type,
                        "consensus_decision": r.consensus_decision,
                        "consensus_confidence": r.consensus_confidence,
                        "agreement_level": r.agreement_level,
                        "votes": {
                            "buy": r.buy_votes,
                            "sell": r.sell_votes,
                            "hold": r.hold_votes
                        },
                        "recommendation": r.recommendation,
                        "created_at": r.created_at.isoformat()
                    }
                    for r in results
                ],
                "total": len(results)
            }
        }

    except Exception as e:
        api_logger.error(f"Error getting consensus for {stock_code}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/llm/performance")
async def get_llm_performance(
    model_name: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Get LLM model performance metrics

    Args:
        model_name: Specific model name (claude, gpt4, gemini, grok) or None for all
        db: Database session

    Returns:
        Performance metrics
    """
    try:
        orchestrator = LLMOrchestrator(db)
        performance = orchestrator.get_model_performance(model_name)

        return {
            "status": "success",
            "data": performance
        }

    except Exception as e:
        api_logger.error(f"Error getting LLM performance: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/llm/history/{stock_code}")
async def get_llm_analysis_history(
    stock_code: str,
    limit: int = 20,
    model_name: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Get LLM analysis history for a stock

    Args:
        stock_code: Stock code (6 digits)
        limit: Maximum number of records
        model_name: Filter by model name
        db: Database session

    Returns:
        Analysis history
    """
    try:
        query = db.query(LLMAnalysis).filter(LLMAnalysis.stock_code == stock_code)

        if model_name:
            query = query.filter(LLMAnalysis.llm_model == model_name)

        results = query.order_by(LLMAnalysis.created_at.desc()).limit(limit).all()

        return {
            "status": "success",
            "data": {
                "stock_code": stock_code,
                "analyses": [
                    {
                        "id": r.id,
                        "llm_model": r.llm_model,
                        "analysis_type": r.analysis_type,
                        "decision": r.decision,
                        "confidence": r.confidence,
                        "tokens_used": r.tokens_used,
                        "cost": r.cost,
                        "latency_ms": r.latency_ms,
                        "success": r.success,
                        "created_at": r.created_at.isoformat()
                    }
                    for r in results
                ],
                "total": len(results)
            }
        }

    except Exception as e:
        api_logger.error(f"Error getting LLM history for {stock_code}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/llm/analyze-signal/{stock_code}")
async def analyze_stock_signal_with_llm(
    stock_code: str,
    db: Session = Depends(get_db)
):
    """
    Comprehensive stock analysis with multi-LLM consensus

    Collects all necessary data and runs multi-agent analysis

    Args:
        stock_code: Stock code (6 digits)
        db: Database session

    Returns:
        Complete analysis with LLM consensus
    """
    try:
        # Get stock info
        stock = db.query(Stock).filter(Stock.code == stock_code).first()
        if not stock:
            raise HTTPException(status_code=404, detail=f"Stock {stock_code} not found")

        # Collect technical data
        prices = (
            db.query(StockPrice)
            .filter(StockPrice.stock_code == stock_code)
            .order_by(StockPrice.date.desc())
            .limit(100)
            .all()
        )

        if len(prices) < 20:
            raise HTTPException(status_code=400, detail="Insufficient price data")

        price_df = pd.DataFrame([
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

        # Calculate technical indicators
        analyzer = TechnicalAnalyzer()
        technical_data = analyzer.calculate_all_indicators(price_df)

        # Get US market data
        sp500 = (
            db.query(USIndex)
            .filter(USIndex.symbol == '^GSPC')
            .order_by(USIndex.date.desc())
            .first()
        )

        us_market_data = {
            "sp500_close": float(sp500.close) if sp500 else None,
            "sp500_ma_20": float(sp500.ma_20) if sp500 and sp500.ma_20 else None,
            "sp500_above_ma": sp500.above_ma if sp500 else None,
            "signal": "BULLISH" if sp500 and sp500.above_ma else "BEARISH"
        } if sp500 else None

        # Get fundamental data (if available)
        fundamental_data = {
            "market_cap": stock.market_cap,
            "sector": stock.sector,
            "market": stock.market
        }

        # Get news data
        start_date = datetime.now() - timedelta(days=7)
        news = (
            db.query(StockNews)
            .filter(
                StockNews.stock_code == stock_code,
                StockNews.published_at >= start_date
            )
            .order_by(StockNews.published_at.desc())
            .limit(20)
            .all()
        )

        news_data = {
            "articles": [
                {
                    "title": n.title,
                    "sentiment_label": n.sentiment_label,
                    "sentiment_score": n.sentiment_score,
                    "published_at": n.published_at.isoformat() if n.published_at else None
                }
                for n in news
            ],
            "total": len(news)
        } if news else None

        # Run multi-LLM analysis
        orchestrator = LLMOrchestrator(db)
        result = await orchestrator.analyze_multi_agent(
            stock_code=stock_code,
            stock_name=stock.name,
            technical_data=technical_data,
            fundamental_data=fundamental_data,
            us_market_data=us_market_data,
            news_data=news_data,
            analysis_type="combined_signal"
        )

        return {
            "status": "success",
            "data": result
        }

    except HTTPException:
        raise
    except Exception as e:
        api_logger.error(f"Error analyzing {stock_code} with LLM: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== Social Media Endpoints ====================

@app.post("/api/v1/social/collect")
async def collect_social_media_data(db: Session = Depends(get_db)):
    """
    소셜 미디어 데이터 수집 (WallStreetBets + StockTwits)

    Returns:
        수집된 데이터 통계
    """
    try:
        api_logger.info("Starting social media data collection...")

        # 모든 소셜 데이터 수집
        results = await collect_all_social_data(db)

        return {
            "status": "success",
            "data": {
                "wallstreetbets_mentions": results.get('wallstreetbets', 0),
                "stocktwits_mentions": results.get('stocktwits', 0),
                "total_collected": sum(results.values()),
                "timestamp": datetime.now().isoformat()
            }
        }

    except Exception as e:
        api_logger.error(f"Error collecting social media data: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/social/wallstreetbets/trending")
async def get_wsb_trending(
    limit: int = 20,
    db: Session = Depends(get_db)
):
    """
    WallStreetBets 트렌딩 주식 조회

    Args:
        limit: 조회 개수 (default: 20)
        db: Database session

    Returns:
        트렌딩 주식 리스트 (멘션 많은 순)
    """
    try:
        # 오늘 수집된 WSB 데이터 조회
        today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)

        trending = (
            db.query(SocialMediaMention)
            .filter(
                SocialMediaMention.source == 'wallstreetbets',
                SocialMediaMention.data_date >= today_start
            )
            .order_by(SocialMediaMention.rank.asc())
            .limit(limit)
            .all()
        )

        if not trending:
            # 데이터가 없으면 수집 실행
            api_logger.info("No WSB data found, collecting now...")
            collector = TradestieCollector()
            mentions = await collector.collect()
            collector.save_to_database(mentions, db)

            # 다시 조회
            trending = (
                db.query(SocialMediaMention)
                .filter(
                    SocialMediaMention.source == 'wallstreetbets',
                    SocialMediaMention.data_date >= today_start
                )
                .order_by(SocialMediaMention.rank.asc())
                .limit(limit)
                .all()
            )

        return {
            "status": "success",
            "data": {
                "trending_stocks": [
                    {
                        "rank": t.rank,
                        "ticker": t.ticker,
                        "mention_count": t.mention_count,
                        "sentiment": t.sentiment,
                        "sentiment_score": t.sentiment_score,
                        "data_date": t.data_date.isoformat() if t.data_date else None
                    }
                    for t in trending
                ],
                "total": len(trending),
                "source": "r/wallstreetbets",
                "timestamp": datetime.now().isoformat()
            }
        }

    except Exception as e:
        api_logger.error(f"Error getting WSB trending: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/social/stocktwits/{ticker}")
async def get_stocktwits_sentiment(
    ticker: str,
    db: Session = Depends(get_db)
):
    """
    특정 종목의 StockTwits 감성 조회

    Args:
        ticker: 주식 티커 (예: 'TSLA', 'AAPL')
        db: Database session

    Returns:
        종목별 투자자 감성
    """
    try:
        ticker = ticker.upper()

        # DB에서 최신 데이터 조회 (오늘)
        today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)

        sentiment_data = (
            db.query(SocialMediaMention)
            .filter(
                SocialMediaMention.source == 'stocktwits',
                SocialMediaMention.ticker == ticker,
                SocialMediaMention.data_date >= today_start
            )
            .order_by(SocialMediaMention.collected_at.desc())
            .first()
        )

        if not sentiment_data:
            # 데이터가 없으면 실시간 수집
            api_logger.info(f"No StockTwits data for {ticker}, collecting now...")
            collector = StockTwitsCollector()
            mention = await collector.collect_symbol(ticker)

            if mention:
                collector.save_to_database([mention], db)
                sentiment_data = (
                    db.query(SocialMediaMention)
                    .filter(
                        SocialMediaMention.source == 'stocktwits',
                        SocialMediaMention.ticker == ticker
                    )
                    .order_by(SocialMediaMention.collected_at.desc())
                    .first()
                )

        if not sentiment_data:
            return {
                "status": "success",
                "data": {
                    "ticker": ticker,
                    "sentiment": "NO_DATA",
                    "message": f"No StockTwits data available for {ticker}"
                }
            }

        return {
            "status": "success",
            "data": {
                "ticker": ticker,
                "sentiment": sentiment_data.sentiment,
                "sentiment_score": sentiment_data.sentiment_score,
                "bullish_ratio": sentiment_data.bullish_ratio,
                "mention_count": sentiment_data.mention_count,
                "sentiment_breakdown": sentiment_data.raw_data.get('sentiment_breakdown', {}),
                "data_date": sentiment_data.data_date.isoformat() if sentiment_data.data_date else None,
                "collected_at": sentiment_data.collected_at.isoformat()
            }
        }

    except Exception as e:
        api_logger.error(f"Error getting StockTwits sentiment for {ticker}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/social/trending-combined")
async def get_combined_social_trends(
    limit: int = 30,
    db: Session = Depends(get_db)
):
    """
    통합 소셜 미디어 트렌드 (WSB + StockTwits)

    Args:
        limit: 조회 개수
        db: Database session

    Returns:
        통합 트렌드 데이터
    """
    try:
        today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)

        # WSB + StockTwits 데이터 모두 조회
        all_mentions = (
            db.query(SocialMediaMention)
            .filter(SocialMediaMention.data_date >= today_start)
            .all()
        )

        # 티커별로 그룹화
        ticker_data = {}
        for mention in all_mentions:
            ticker = mention.ticker
            if ticker not in ticker_data:
                ticker_data[ticker] = {
                    'ticker': ticker,
                    'wsb_rank': None,
                    'wsb_mentions': 0,
                    'wsb_sentiment': None,
                    'stocktwits_sentiment': None,
                    'stocktwits_bullish_ratio': None,
                    'combined_score': 0
                }

            if mention.source == 'wallstreetbets':
                ticker_data[ticker]['wsb_rank'] = mention.rank
                ticker_data[ticker]['wsb_mentions'] = mention.mention_count
                ticker_data[ticker]['wsb_sentiment'] = mention.sentiment
                ticker_data[ticker]['combined_score'] += mention.mention_count * 1.0
            elif mention.source == 'stocktwits':
                ticker_data[ticker]['stocktwits_sentiment'] = mention.sentiment
                ticker_data[ticker]['stocktwits_bullish_ratio'] = mention.bullish_ratio
                ticker_data[ticker]['combined_score'] += (mention.bullish_ratio or 0.5) * 100

        # 점수 기준 정렬
        sorted_data = sorted(
            ticker_data.values(),
            key=lambda x: x['combined_score'],
            reverse=True
        )[:limit]

        return {
            "status": "success",
            "data": {
                "trending_stocks": sorted_data,
                "total": len(sorted_data),
                "sources": ["wallstreetbets", "stocktwits"],
                "timestamp": datetime.now().isoformat()
            }
        }

    except Exception as e:
        api_logger.error(f"Error getting combined social trends: {str(e)}")
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
