"""
Test History Database

히스토리 DB 테스트

Tests:
1. Market data save/load
2. Signal history save/load
3. Fear & Greed history save/load
4. Economic data save/load
5. Backtest results save/load

Author: AI Assistant
Created: 2025-11-22
"""

import sys
from pathlib import Path
from datetime import datetime, timedelta
import pandas as pd

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.database.history_db import get_history_db


def test_market_data():
    """Test market data save/load"""
    print("\n" + "=" * 80)
    print("  Market Data Test")
    print("=" * 80)

    db = get_history_db()

    # Sample market data
    data = {
        'sp500': {
            'close': 4500.50,
            'open': 4480.00,
            'high': 4520.00,
            'low': 4470.00,
            'volume': 3500000000,
            'change_pct': 0.45,
            'ma_20': 4450.00,
            'ma_60': 4400.00,
            'ma_200': 4350.00
        },
        'nasdaq': {
            'close': 14000.00,
            'change_pct': 0.75
        },
        'kospi': {
            'close': 2600.00,
            'change_pct': 0.30
        }
    }

    print("\n1. Saving market data...")
    success = db.save_market_data(data)
    print(f"   {'✅ Saved' if success else '❌ Failed'}")

    print("\n2. Loading market data (last 5 days)...")
    df = db.get_market_data(days=5)

    if df is not None and not df.empty:
        print(f"   ✅ Loaded {len(df)} records")
        print(f"\n   Latest data:")
        print(df.tail())
    else:
        print(f"   ❌ No data found")


def test_signal_history():
    """Test signal history save/load"""
    print("\n" + "=" * 80)
    print("  Signal History Test")
    print("=" * 80)

    db = get_history_db()

    # Sample signal
    signal_data = {
        'signal': 'BUY',
        'confidence': 75.5,
        'score': 7.2,
        'breakdown': {
            'market_correlation': 8.0,
            'economic_indicators': 7.0,
            'fear_greed': 6.5,
            'yield_curve': 7.5
        },
        'action_plan': {
            'action': '점진적 매수',
            'timeframe': '1-2주',
            'target_allocation': {
                '주식': '60%',
                '채권': '30%',
                '현금': '10%'
            },
            'stop_loss': -5.0,
            'take_profit': 15.0
        }
    }

    print("\n3. Saving signal...")
    success = db.save_signal(signal_data)
    print(f"   {'✅ Saved' if success else '❌ Failed'}")

    print("\n4. Loading signal history (last 10 days)...")
    history = db.get_signal_history(days=10)

    if history:
        print(f"   ✅ Loaded {len(history)} signals")
        for sig in history[:3]:
            print(f"   - {sig['date']}: {sig['signal']} (신뢰도 {sig['confidence']:.0f}%)")
    else:
        print(f"   ❌ No signals found")


def test_fear_greed_history():
    """Test Fear & Greed history save/load"""
    print("\n" + "=" * 80)
    print("  Fear & Greed History Test")
    print("=" * 80)

    db = get_history_db()

    # Sample Fear & Greed data
    data = {
        'score': 65.0,
        'rating': 'Greed',
        'market_momentum': 70.0,
        'stock_price_strength': 65.0,
        'market_volatility': 55.0
    }

    print("\n5. Saving Fear & Greed data...")
    success = db.save_fear_greed(data)
    print(f"   {'✅ Saved' if success else '❌ Failed'}")

    print("\n6. Loading Fear & Greed history (last 7 days)...")
    df = db.get_fear_greed_history(days=7)

    if df is not None and not df.empty:
        print(f"   ✅ Loaded {len(df)} records")
        print(f"\n   Recent data:")
        print(df.tail())
    else:
        print(f"   ❌ No data found")


def test_economic_data():
    """Test economic data save/load"""
    print("\n" + "=" * 80)
    print("  Economic Data Test")
    print("=" * 80)

    db = get_history_db()

    # Sample economic data
    data = {
        'us_fed_rate': 5.50,
        'kr_base_rate': 3.50,
        'interest_rate_spread': 2.00,
        'treasury_2y': 4.80,
        'treasury_10y': 4.50,
        'spread_10y_2y': -0.30,
        'yield_curve_inverted': True,
        'recession_signal': True,
        'recession_probability': 65.0,
        'usd_krw': 1320.50
    }

    print("\n7. Saving economic data...")
    success = db.save_economic_data(data)
    print(f"   {'✅ Saved' if success else '❌ Failed'}")


def test_backtest_save():
    """Test backtest save"""
    print("\n" + "=" * 80)
    print("  Backtest History Test")
    print("=" * 80)

    db = get_history_db()

    # Sample backtest result
    backtest_data = {
        'strategy_name': 'Moving Average Strategy',
        'start_date': datetime.now() - timedelta(days=252),
        'end_date': datetime.now(),
        'initial_capital': 10000000,
        'commission': 0.0015,
        'slippage': 0.001,
        'risk_free_rate': 0.03,
        'metrics': {
            'final_value': 11500000,
            'total_return_pct': 15.0,
            'cagr_pct': 15.2,
            'max_drawdown_pct': -12.5,
            'volatility_pct': 18.0,
            'sharpe_ratio': 1.25,
            'sortino_ratio': 1.85,
            'total_trades': 24,
            'winning_trades': 15,
            'losing_trades': 9,
            'win_rate': 0.625,
            'profit_factor': 2.34,
            'avg_win': 150000,
            'avg_loss': -80000
        },
        'benchmark_return_pct': 12.0,
        'alpha_pct': 3.0,
        'beta': 1.05,
        'equity_curve': [10000000, 10500000, 11000000, 11500000],
        'trades': [
            {'date': '2025-01-15', 'type': 'BUY', 'price': 100.0, 'shares': 100}
        ]
    }

    print("\n8. Saving backtest result...")
    success = db.save_backtest(backtest_data)
    print(f"   {'✅ Saved' if success else '❌ Failed'}")


def main():
    """Run all tests"""
    print("\n" + "=" * 80)
    print("  🗄️  History Database Test Suite")
    print("=" * 80)
    print("\n⚠️  Make sure PostgreSQL is running and DATABASE_URL is set.")
    print("   Example: export DATABASE_URL='postgresql://user:password@localhost:5432/stock_intelligence'")

    input("\nPress Enter to continue...")

    try:
        # Run tests
        test_market_data()
        test_signal_history()
        test_fear_greed_history()
        test_economic_data()
        test_backtest_save()

        # Summary
        print("\n" + "=" * 80)
        print("  ✅ All tests completed!")
        print("=" * 80)
        print("\nCheck your database to verify the data was saved correctly.")
        print("\nSample queries:")
        print("  SELECT * FROM market_data_history ORDER BY date DESC LIMIT 5;")
        print("  SELECT * FROM signal_history ORDER BY date DESC LIMIT 10;")
        print("  SELECT * FROM fear_greed_history ORDER BY date DESC LIMIT 7;")
        print("  SELECT * FROM backtest_history ORDER BY created_at DESC LIMIT 5;")

    except KeyboardInterrupt:
        print("\n\n⚠️  Tests interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Error during tests: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
