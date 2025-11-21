"""
Yahoo Finance Collector for US Indices
Stock Intelligence System
"""

import yfinance as yf
import pandas as pd
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta

from app.collectors.base import BaseCollector, CollectionError


class YahooCollector(BaseCollector):
    """
    Yahoo Finance 미국 지수 데이터 수집기

    Collects data for:
    - S&P 500 (^GSPC)
    - NASDAQ (^IXIC)
    - Dow Jones (^DJI)
    """

    # Symbol mapping
    INDICES = {
        'SP500': {
            'symbol': '^GSPC',
            'name': 'S&P 500'
        },
        'NASDAQ': {
            'symbol': '^IXIC',
            'name': 'NASDAQ Composite'
        },
        'DOW': {
            'symbol': '^DJI',
            'name': 'Dow Jones Industrial Average'
        }
    }

    def __init__(self):
        """Initialize Yahoo Finance collector"""
        super().__init__()

    async def collect(self, symbol: str = "^GSPC", period: str = "3mo", **kwargs) -> Dict[str, Any]:
        """
        Collect US index data

        Args:
            symbol: Index symbol (default: ^GSPC for S&P 500)
            period: Data period (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)
            **kwargs: Additional parameters

        Returns:
            Dict containing index data with moving averages

        Raises:
            CollectionError: If collection fails
        """
        try:
            # Download data
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period=period)

            if hist.empty:
                raise CollectionError(
                    f"No data returned for symbol {symbol}",
                    source="YahooFinance",
                    details={"symbol": symbol}
                )

            # Get latest data
            latest = hist.iloc[-1]
            latest_date = hist.index[-1]

            # Calculate moving averages
            ma_20 = hist['Close'].rolling(window=20).mean().iloc[-1]
            ma_60 = hist['Close'].rolling(window=60).mean().iloc[-1]

            # Calculate change rate
            if len(hist) > 1:
                prev_close = hist.iloc[-2]['Close']
                change_rate = ((latest['Close'] - prev_close) / prev_close) * 100
            else:
                change_rate = 0.0

            # Get index name
            index_name = None
            for key, info in self.INDICES.items():
                if info['symbol'] == symbol:
                    index_name = info['name']
                    break

            if not index_name:
                index_name = symbol

            # Normalize data
            normalized = {
                'symbol': symbol,
                'name': index_name,
                'close': float(latest['Close']),
                'high': float(latest['High']),
                'low': float(latest['Low']),
                'open': float(latest['Open']),
                'volume': int(latest['Volume']),
                'ma_20': float(ma_20) if not pd.isna(ma_20) else None,
                'ma_60': float(ma_60) if not pd.isna(ma_60) else None,
                'above_ma': bool(latest['Close'] > ma_20) if not pd.isna(ma_20) else None,
                'change_rate': float(change_rate),
                'date': latest_date.strftime('%Y-%m-%d')
            }

            self.log_info(
                f"Collected data for {symbol}",
                close=normalized['close'],
                above_ma=normalized['above_ma']
            )

            return normalized

        except Exception as e:
            raise CollectionError(
                f"Failed to collect Yahoo Finance data: {str(e)}",
                source="YahooFinance",
                details={"symbol": symbol}
            )

    async def collect_all_indices(self, period: str = "3mo") -> List[Dict[str, Any]]:
        """
        Collect data for all major US indices

        Args:
            period: Data period

        Returns:
            List of dictionaries containing data for each index
        """
        results = []

        for key, info in self.INDICES.items():
            try:
                data = await self.collect(symbol=info['symbol'], period=period)
                results.append(data)
                self.log_info(f"Collected {info['name']}")
            except CollectionError as e:
                self.log_error(f"Failed to collect {info['name']}: {str(e)}")
                continue

        return results

    async def collect_historical(
        self,
        symbol: str = "^GSPC",
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Collect historical data for backtesting

        Args:
            symbol: Index symbol
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)

        Returns:
            Dict containing historical OHLCV data
        """
        try:
            # Set default dates if not provided
            if not end_date:
                end_date = datetime.now().strftime('%Y-%m-%d')
            if not start_date:
                start_date = (datetime.now() - timedelta(days=365*5)).strftime('%Y-%m-%d')

            ticker = yf.Ticker(symbol)
            hist = ticker.history(start=start_date, end=end_date)

            if hist.empty:
                raise CollectionError(
                    f"No historical data for {symbol}",
                    source="YahooFinance"
                )

            # Calculate moving averages
            hist['MA_20'] = hist['Close'].rolling(window=20).mean()
            hist['MA_60'] = hist['Close'].rolling(window=60).mean()

            # Convert to list of dicts
            data_list = []
            for date, row in hist.iterrows():
                data_list.append({
                    'date': date.strftime('%Y-%m-%d'),
                    'open': float(row['Open']),
                    'high': float(row['High']),
                    'low': float(row['Low']),
                    'close': float(row['Close']),
                    'volume': int(row['Volume']),
                    'ma_20': float(row['MA_20']) if not pd.isna(row['MA_20']) else None,
                    'ma_60': float(row['MA_60']) if not pd.isna(row['MA_60']) else None,
                })

            return {
                'symbol': symbol,
                'start_date': start_date,
                'end_date': end_date,
                'data': data_list,
                'total_records': len(data_list)
            }

        except Exception as e:
            raise CollectionError(
                f"Failed to collect historical data: {str(e)}",
                source="YahooFinance",
                details={"symbol": symbol}
            )

    def get_signal(self, close: float, ma_20: float) -> str:
        """
        Generate market signal based on price vs MA

        Args:
            close: Current close price
            ma_20: 20-day moving average

        Returns:
            'BULLISH' or 'BEARISH'
        """
        return 'BULLISH' if close > ma_20 else 'BEARISH'

    def validate_data(self, data: Dict) -> bool:
        """
        Validate collected data

        Args:
            data: Data to validate

        Returns:
            True if valid, False otherwise
        """
        required_fields = ['symbol', 'close', 'date']

        # Check required fields
        if not all(field in data for field in required_fields):
            return False

        # Check close price is positive
        if data.get('close', 0) <= 0:
            return False

        # Check symbol format
        if not data.get('symbol'):
            return False

        return True
