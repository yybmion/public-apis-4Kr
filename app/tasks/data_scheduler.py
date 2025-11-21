"""
Data Collection Scheduler
Stock Intelligence System

Schedule automated data collection:
- Market open (09:00): Collect US market data
- Market hours (09:00-15:30): Real-time price updates every 10 seconds
- Market close (16:00): Daily summary and backtesting
- Evening (18:00): News collection and sentiment analysis
"""

import asyncio
from datetime import datetime, time
from typing import List, Optional
import pytz
from sqlalchemy.orm import Session

from app.database.session import SessionLocal
from app.collectors.kis_collector import KISCollector
from app.collectors.yahoo_collector import YahooCollector
from app.collectors.dart_collector import DARTCollector
from app.models.stock import Stock, StockPrice, USIndex
from app.analyzers.technical_analyzer import TechnicalAnalyzer
from app.config import settings, is_market_hours
from app.utils.logger import LoggerMixin


class DataScheduler(LoggerMixin):
    """
    Schedule and execute data collection tasks
    """

    def __init__(self):
        super().__init__()
        self.kis_collector = KISCollector()
        self.yahoo_collector = YahooCollector()
        self.dart_collector = DARTCollector()
        self.technical_analyzer = TechnicalAnalyzer()
        self.kst = pytz.timezone('Asia/Seoul')

    async def collect_us_market_data(self):
        """Collect US market indices"""
        self.log_info("Collecting US market data...")

        try:
            results = await self.yahoo_collector.collect_all_indices()

            with SessionLocal() as db:
                for data in results:
                    # Save to database
                    us_index = USIndex(
                        symbol=data['symbol'],
                        name=data['name'],
                        close=data['close'],
                        change_rate=data.get('change_rate', 0),
                        ma_20=data.get('ma_20'),
                        ma_60=data.get('ma_60'),
                        above_ma=data.get('above_ma'),
                        date=datetime.strptime(data['date'], '%Y-%m-%d').date()
                    )

                    # Check if already exists
                    existing = db.query(USIndex).filter(
                        USIndex.symbol == us_index.symbol,
                        USIndex.date == us_index.date
                    ).first()

                    if existing:
                        # Update
                        existing.close = us_index.close
                        existing.change_rate = us_index.change_rate
                        existing.ma_20 = us_index.ma_20
                        existing.ma_60 = us_index.ma_60
                        existing.above_ma = us_index.above_ma
                    else:
                        db.add(us_index)

                db.commit()

            self.log_info(f"Collected {len(results)} US indices")
            return results

        except Exception as e:
            self.log_error(f"Failed to collect US market data: {str(e)}")
            return []

    async def collect_stock_prices(self, stock_codes: Optional[List[str]] = None):
        """
        Collect real-time stock prices

        Args:
            stock_codes: List of stock codes to collect. If None, collect all.
        """
        self.log_info("Collecting stock prices...")

        with SessionLocal() as db:
            if stock_codes is None:
                # Get all active stocks
                stocks = db.query(Stock).limit(100).all()  # Limit for testing
                stock_codes = [stock.code for stock in stocks]

            collected = 0
            failed = 0

            for stock_code in stock_codes:
                try:
                    data = await self.kis_collector.collect(stock_code=stock_code)

                    if data:
                        # Save to database
                        stock_price = StockPrice(
                            stock_code=stock_code,
                            date=datetime.strptime(data['date'], '%Y-%m-%d').date(),
                            open=data['open'],
                            high=data['high'],
                            low=data['low'],
                            close=data['current_price'],
                            volume=data['volume'],
                            trading_value=data.get('trading_value'),
                            change_rate=data['change_rate'],
                            source='KIS_API',
                            verified=True
                        )

                        # Check if already exists
                        existing = db.query(StockPrice).filter(
                            StockPrice.stock_code == stock_code,
                            StockPrice.date == stock_price.date
                        ).first()

                        if existing:
                            # Update
                            existing.close = stock_price.close
                            existing.high = max(existing.high, stock_price.high)
                            existing.low = min(existing.low, stock_price.low)
                            existing.volume = stock_price.volume
                            existing.change_rate = stock_price.change_rate
                        else:
                            db.add(stock_price)

                        collected += 1

                    # Rate limiting
                    await asyncio.sleep(0.1)

                except Exception as e:
                    self.log_error(f"Failed to collect {stock_code}: {str(e)}")
                    failed += 1
                    continue

            db.commit()

        self.log_info(f"Collected {collected} stocks, {failed} failed")

    async def calculate_indicators_for_all(self):
        """Calculate technical indicators for all stocks"""
        self.log_info("Calculating technical indicators...")

        with SessionLocal() as db:
            stocks = db.query(Stock).all()

            for stock in stocks:
                try:
                    # Get price history
                    prices = (
                        db.query(StockPrice)
                        .filter(StockPrice.stock_code == stock.code)
                        .order_by(StockPrice.date.desc())
                        .limit(200)
                        .all()
                    )

                    if len(prices) < 20:
                        continue

                    # Convert to DataFrame
                    import pandas as pd
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

                    # Calculate indicators
                    df = self.technical_analyzer.calculate_all_indicators(df)

                    # TODO: Save indicators to database or cache

                    self.log_info(f"Calculated indicators for {stock.code}")

                except Exception as e:
                    self.log_error(f"Failed to calculate indicators for {stock.code}: {str(e)}")
                    continue

    async def morning_routine(self):
        """
        Morning routine at market open (09:00 KST)
        - Collect US market data from previous day
        - Generate market outlook
        """
        self.log_info("Running morning routine...")

        # Collect US data
        await self.collect_us_market_data()

        # TODO: Generate daily market outlook
        # TODO: Send morning briefing

        self.log_info("Morning routine complete")

    async def realtime_collection_loop(self):
        """
        Real-time collection during market hours
        Collect every 10 seconds during 09:00-15:30 KST
        """
        self.log_info("Starting real-time collection loop...")

        while True:
            now = datetime.now(self.kst)

            # Check if market is open
            if is_market_hours():
                try:
                    # Collect data
                    await self.collect_stock_prices()

                    # Wait 10 seconds
                    await asyncio.sleep(settings.REALTIME_COLLECTION_INTERVAL)

                except Exception as e:
                    self.log_error(f"Error in realtime collection: {str(e)}")
                    await asyncio.sleep(60)  # Wait 1 minute on error
            else:
                # Market closed, wait until next market open
                self.log_info("Market closed, waiting...")
                await asyncio.sleep(300)  # Check every 5 minutes

    async def evening_routine(self):
        """
        Evening routine at 18:00 KST
        - Collect news
        - Perform sentiment analysis
        - Send daily summary
        """
        self.log_info("Running evening routine...")

        # TODO: Collect news
        # TODO: Sentiment analysis
        # TODO: Send daily summary

        self.log_info("Evening routine complete")

    async def run_scheduler(self):
        """
        Main scheduler loop

        Schedules:
        - 09:00: Morning routine
        - 09:00-15:30: Real-time collection
        - 16:00: Daily summary
        - 18:00: Evening routine
        """
        self.log_info("Data scheduler started")

        while True:
            now = datetime.now(self.kst)
            current_time = now.time()

            # Morning routine (09:00)
            if current_time.hour == 9 and current_time.minute == 0:
                await self.morning_routine()

            # Real-time collection (market hours)
            elif is_market_hours():
                await self.collect_stock_prices()
                await asyncio.sleep(settings.REALTIME_COLLECTION_INTERVAL)

            # Daily summary (16:00)
            elif current_time.hour == 16 and current_time.minute == 0:
                self.log_info("Running daily summary...")
                await self.calculate_indicators_for_all()

            # Evening routine (18:00)
            elif current_time.hour == 18 and current_time.minute == 0:
                await self.evening_routine()

            # Sleep for 1 minute
            await asyncio.sleep(60)


# Standalone execution
if __name__ == "__main__":
    scheduler = DataScheduler()
    asyncio.run(scheduler.run_scheduler())
