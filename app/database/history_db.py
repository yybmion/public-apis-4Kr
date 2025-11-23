"""
History Database Helper

히스토리 데이터 저장 및 조회 헬퍼

Functions:
- save_market_data: 시장 데이터 저장
- save_signal: 투자 신호 저장
- save_fear_greed: Fear & Greed 저장
- save_economic_data: 경제 지표 저장
- save_backtest: 백테스팅 결과 저장

Author: AI Assistant
Created: 2025-11-22
"""

import os
import json
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import IntegrityError
import logging
import pandas as pd

from app.models.market_history import (
    MarketDataHistory,
    SignalHistory,
    FearGreedHistory,
    EconomicDataHistory,
    BacktestHistory
)

# Setup logging
logger = logging.getLogger(__name__)


class HistoryDB:
    """History Database Helper"""

    def __init__(self, database_url: Optional[str] = None):
        """
        Initialize History DB

        Args:
            database_url: Database URL (or from env)
        """
        self.database_url = database_url or os.getenv(
            'DATABASE_URL',
            'postgresql://user:password@localhost:5432/stock_intelligence'
        )

        try:
            self.engine = create_engine(self.database_url)
            self.SessionLocal = sessionmaker(bind=self.engine)
            self.enabled = True
            logger.info("History DB initialized")
        except Exception as e:
            logger.error(f"Failed to initialize History DB: {str(e)}")
            self.enabled = False

    def get_session(self) -> Optional[Session]:
        """Get database session"""
        if not self.enabled:
            return None
        return self.SessionLocal()

    # Market Data

    def save_market_data(self, data: Dict[str, Any], date: Optional[datetime] = None) -> bool:
        """
        Save market data

        Args:
            data: Market data dictionary
            date: Data date (default: now)

        Returns:
            Success status
        """
        if not self.enabled:
            logger.warning("History DB not enabled")
            return False

        session = self.get_session()
        if not session:
            return False

        try:
            market_data = MarketDataHistory(
                date=date or datetime.now(),
                sp500_close=data.get('sp500', {}).get('close'),
                sp500_open=data.get('sp500', {}).get('open'),
                sp500_high=data.get('sp500', {}).get('high'),
                sp500_low=data.get('sp500', {}).get('low'),
                sp500_volume=data.get('sp500', {}).get('volume'),
                sp500_change_pct=data.get('sp500', {}).get('change_pct'),
                nasdaq_close=data.get('nasdaq', {}).get('close'),
                nasdaq_open=data.get('nasdaq', {}).get('open'),
                nasdaq_high=data.get('nasdaq', {}).get('high'),
                nasdaq_low=data.get('nasdaq', {}).get('low'),
                nasdaq_volume=data.get('nasdaq', {}).get('volume'),
                nasdaq_change_pct=data.get('nasdaq', {}).get('change_pct'),
                kospi_close=data.get('kospi', {}).get('close'),
                kospi_open=data.get('kospi', {}).get('open'),
                kospi_high=data.get('kospi', {}).get('high'),
                kospi_low=data.get('kospi', {}).get('low'),
                kospi_volume=data.get('kospi', {}).get('volume'),
                kospi_change_pct=data.get('kospi', {}).get('change_pct'),
                kosdaq_close=data.get('kosdaq', {}).get('close'),
                kosdaq_open=data.get('kosdaq', {}).get('open'),
                kosdaq_high=data.get('kosdaq', {}).get('high'),
                kosdaq_low=data.get('kosdaq', {}).get('low'),
                kosdaq_volume=data.get('kosdaq', {}).get('volume'),
                kosdaq_change_pct=data.get('kosdaq', {}).get('change_pct'),
                sp500_ma_20=data.get('sp500', {}).get('ma_20'),
                sp500_ma_60=data.get('sp500', {}).get('ma_60'),
                sp500_ma_200=data.get('sp500', {}).get('ma_200')
            )

            session.add(market_data)
            session.commit()
            logger.info(f"Market data saved for {date or datetime.now()}")
            return True

        except IntegrityError:
            session.rollback()
            logger.warning(f"Market data already exists for {date or datetime.now()}")
            return False
        except Exception as e:
            session.rollback()
            logger.error(f"Failed to save market data: {str(e)}")
            return False
        finally:
            session.close()

    def get_market_data(self, days: int = 252) -> Optional[pd.DataFrame]:
        """
        Get recent market data as DataFrame

        Args:
            days: Number of days

        Returns:
            DataFrame with market data
        """
        if not self.enabled:
            return None

        session = self.get_session()
        if not session:
            return None

        try:
            cutoff_date = datetime.now() - timedelta(days=days)

            records = session.query(MarketDataHistory).filter(
                MarketDataHistory.date >= cutoff_date
            ).order_by(MarketDataHistory.date.asc()).all()

            if not records:
                return None

            # Convert to DataFrame
            data = []
            for record in records:
                data.append({
                    'date': record.date,
                    'sp500_close': record.sp500_close,
                    'sp500_ma_20': record.sp500_ma_20,
                    'sp500_ma_60': record.sp500_ma_60,
                    'nasdaq_close': record.nasdaq_close,
                    'kospi_close': record.kospi_close,
                    'kosdaq_close': record.kosdaq_close
                })

            df = pd.DataFrame(data)
            df.set_index('date', inplace=True)
            return df

        except Exception as e:
            logger.error(f"Failed to get market data: {str(e)}")
            return None
        finally:
            session.close()

    # Signal History

    def save_signal(self, signal_data: Dict[str, Any], date: Optional[datetime] = None) -> bool:
        """
        Save investment signal

        Args:
            signal_data: Signal data from SignalGenerator
            date: Signal date (default: now)

        Returns:
            Success status
        """
        if not self.enabled:
            logger.warning("History DB not enabled")
            return False

        session = self.get_session()
        if not session:
            return False

        try:
            breakdown = signal_data.get('breakdown', {})
            action_plan = signal_data.get('action_plan', {})

            signal = SignalHistory(
                date=date or datetime.now(),
                signal=signal_data.get('signal'),
                confidence=signal_data.get('confidence'),
                score=signal_data.get('score'),
                market_correlation_score=breakdown.get('market_correlation'),
                economic_score=breakdown.get('economic_indicators'),
                fear_greed_score=breakdown.get('fear_greed'),
                yield_curve_score=breakdown.get('yield_curve'),
                action=action_plan.get('action'),
                timeframe=action_plan.get('timeframe'),
                target_allocation=json.dumps(action_plan.get('target_allocation', {})),
                stop_loss_pct=action_plan.get('stop_loss'),
                take_profit_pct=action_plan.get('take_profit')
            )

            session.add(signal)
            session.commit()
            logger.info(f"Signal saved: {signal_data.get('signal')}")
            return True

        except Exception as e:
            session.rollback()
            logger.error(f"Failed to save signal: {str(e)}")
            return False
        finally:
            session.close()

    def get_signal_history(self, days: int = 30) -> List[Dict[str, Any]]:
        """
        Get recent signal history

        Args:
            days: Number of days

        Returns:
            List of signal records
        """
        if not self.enabled:
            return []

        session = self.get_session()
        if not session:
            return []

        try:
            cutoff_date = datetime.now() - timedelta(days=days)

            records = session.query(SignalHistory).filter(
                SignalHistory.date >= cutoff_date
            ).order_by(SignalHistory.date.desc()).all()

            return [
                {
                    'date': record.date.strftime('%Y-%m-%d'),
                    'signal': record.signal,
                    'confidence': record.confidence,
                    'score': record.score
                }
                for record in records
            ]

        except Exception as e:
            logger.error(f"Failed to get signal history: {str(e)}")
            return []
        finally:
            session.close()

    # Fear & Greed History

    def save_fear_greed(self, data: Dict[str, Any], date: Optional[datetime] = None) -> bool:
        """
        Save Fear & Greed Index

        Args:
            data: Fear & Greed data
            date: Data date (default: now)

        Returns:
            Success status
        """
        if not self.enabled:
            logger.warning("History DB not enabled")
            return False

        session = self.get_session()
        if not session:
            return False

        try:
            fear_greed = FearGreedHistory(
                date=date or datetime.now(),
                score=data.get('score'),
                rating=data.get('rating'),
                market_momentum=data.get('market_momentum'),
                stock_price_strength=data.get('stock_price_strength'),
                stock_price_breadth=data.get('stock_price_breadth'),
                put_call_ratio=data.get('put_call_ratio'),
                market_volatility=data.get('market_volatility'),
                safe_haven_demand=data.get('safe_haven_demand'),
                junk_bond_demand=data.get('junk_bond_demand')
            )

            session.add(fear_greed)
            session.commit()
            logger.info(f"Fear & Greed saved: {data.get('score')}")
            return True

        except IntegrityError:
            session.rollback()
            logger.warning(f"Fear & Greed already exists for {date or datetime.now()}")
            return False
        except Exception as e:
            session.rollback()
            logger.error(f"Failed to save Fear & Greed: {str(e)}")
            return False
        finally:
            session.close()

    def get_fear_greed_history(self, days: int = 30) -> Optional[pd.DataFrame]:
        """
        Get Fear & Greed history as DataFrame

        Args:
            days: Number of days

        Returns:
            DataFrame with Fear & Greed data
        """
        if not self.enabled:
            return None

        session = self.get_session()
        if not session:
            return None

        try:
            cutoff_date = datetime.now() - timedelta(days=days)

            records = session.query(FearGreedHistory).filter(
                FearGreedHistory.date >= cutoff_date
            ).order_by(FearGreedHistory.date.asc()).all()

            if not records:
                return None

            data = [
                {
                    'date': record.date,
                    'score': record.score,
                    'rating': record.rating
                }
                for record in records
            ]

            df = pd.DataFrame(data)
            df.set_index('date', inplace=True)
            return df

        except Exception as e:
            logger.error(f"Failed to get Fear & Greed history: {str(e)}")
            return None
        finally:
            session.close()

    # Economic Data History

    def save_economic_data(self, data: Dict[str, Any], date: Optional[datetime] = None) -> bool:
        """
        Save economic data

        Args:
            data: Economic data
            date: Data date (default: now)

        Returns:
            Success status
        """
        if not self.enabled:
            logger.warning("History DB not enabled")
            return False

        session = self.get_session()
        if not session:
            return False

        try:
            economic = EconomicDataHistory(
                date=date or datetime.now(),
                us_fed_rate=data.get('us_fed_rate'),
                kr_base_rate=data.get('kr_base_rate'),
                interest_rate_spread=data.get('interest_rate_spread'),
                treasury_3m=data.get('treasury_3m'),
                treasury_2y=data.get('treasury_2y'),
                treasury_5y=data.get('treasury_5y'),
                treasury_10y=data.get('treasury_10y'),
                treasury_30y=data.get('treasury_30y'),
                spread_10y_2y=data.get('spread_10y_2y'),
                spread_10y_3m=data.get('spread_10y_3m'),
                yield_curve_inverted=data.get('yield_curve_inverted'),
                recession_signal=data.get('recession_signal'),
                recession_probability=data.get('recession_probability'),
                usd_krw=data.get('usd_krw'),
                usd_jpy=data.get('usd_jpy'),
                eur_usd=data.get('eur_usd'),
                us_cpi=data.get('us_cpi'),
                kr_cpi=data.get('kr_cpi')
            )

            session.add(economic)
            session.commit()
            logger.info(f"Economic data saved for {date or datetime.now()}")
            return True

        except IntegrityError:
            session.rollback()
            logger.warning(f"Economic data already exists for {date or datetime.now()}")
            return False
        except Exception as e:
            session.rollback()
            logger.error(f"Failed to save economic data: {str(e)}")
            return False
        finally:
            session.close()

    # Backtest History

    def save_backtest(self, backtest_data: Dict[str, Any]) -> bool:
        """
        Save backtest result

        Args:
            backtest_data: Backtest result data

        Returns:
            Success status
        """
        if not self.enabled:
            logger.warning("History DB not enabled")
            return False

        session = self.get_session()
        if not session:
            return False

        try:
            metrics = backtest_data.get('metrics', {})

            backtest = BacktestHistory(
                strategy_name=backtest_data.get('strategy_name'),
                start_date=backtest_data.get('start_date'),
                end_date=backtest_data.get('end_date'),
                initial_capital=backtest_data.get('initial_capital'),
                commission=backtest_data.get('commission'),
                slippage=backtest_data.get('slippage'),
                risk_free_rate=backtest_data.get('risk_free_rate'),
                final_value=metrics.get('final_value'),
                total_return_pct=metrics.get('total_return_pct'),
                cagr_pct=metrics.get('cagr_pct'),
                max_drawdown_pct=metrics.get('max_drawdown_pct'),
                volatility_pct=metrics.get('volatility_pct'),
                sharpe_ratio=metrics.get('sharpe_ratio'),
                sortino_ratio=metrics.get('sortino_ratio'),
                total_trades=metrics.get('total_trades'),
                winning_trades=metrics.get('winning_trades'),
                losing_trades=metrics.get('losing_trades'),
                win_rate=metrics.get('win_rate'),
                profit_factor=metrics.get('profit_factor'),
                avg_win=metrics.get('avg_win'),
                avg_loss=metrics.get('avg_loss'),
                benchmark_return_pct=backtest_data.get('benchmark_return_pct'),
                alpha_pct=backtest_data.get('alpha_pct'),
                beta=backtest_data.get('beta'),
                equity_curve=json.dumps(backtest_data.get('equity_curve', [])),
                trades=json.dumps(backtest_data.get('trades', []))
            )

            session.add(backtest)
            session.commit()
            logger.info(f"Backtest saved: {backtest_data.get('strategy_name')}")
            return True

        except Exception as e:
            session.rollback()
            logger.error(f"Failed to save backtest: {str(e)}")
            return False
        finally:
            session.close()


# Singleton instance
_history_db: Optional[HistoryDB] = None


def get_history_db() -> HistoryDB:
    """
    Get singleton History DB instance

    Returns:
        HistoryDB instance
    """
    global _history_db
    if _history_db is None:
        _history_db = HistoryDB()
    return _history_db
