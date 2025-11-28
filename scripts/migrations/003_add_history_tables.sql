-- Migration 003: Add History Tables
-- 히스토리 데이터 저장용 테이블 추가
--
-- Tables:
-- 1. market_data_history - 일일 시장 데이터
-- 2. signal_history - 투자 신호 히스토리
-- 3. fear_greed_history - Fear & Greed Index 히스토리
-- 4. economic_data_history - 경제 지표 히스토리
-- 5. backtest_history - 백테스팅 결과 히스토리
--
-- Author: AI Assistant
-- Created: 2025-11-22

-- ==============================================================================
-- 1. Market Data History Table
-- ==============================================================================

CREATE TABLE IF NOT EXISTS market_data_history (
    id SERIAL PRIMARY KEY,

    -- Date
    date TIMESTAMP NOT NULL,

    -- US Markets - S&P 500
    sp500_close FLOAT,
    sp500_open FLOAT,
    sp500_high FLOAT,
    sp500_low FLOAT,
    sp500_volume FLOAT,
    sp500_change_pct FLOAT,

    -- US Markets - NASDAQ
    nasdaq_close FLOAT,
    nasdaq_open FLOAT,
    nasdaq_high FLOAT,
    nasdaq_low FLOAT,
    nasdaq_volume FLOAT,
    nasdaq_change_pct FLOAT,

    -- KR Markets - KOSPI
    kospi_close FLOAT,
    kospi_open FLOAT,
    kospi_high FLOAT,
    kospi_low FLOAT,
    kospi_volume FLOAT,
    kospi_change_pct FLOAT,

    -- KR Markets - KOSDAQ
    kosdaq_close FLOAT,
    kosdaq_open FLOAT,
    kosdaq_high FLOAT,
    kosdaq_low FLOAT,
    kosdaq_volume FLOAT,
    kosdaq_change_pct FLOAT,

    -- Moving Averages
    sp500_ma_20 FLOAT,
    sp500_ma_60 FLOAT,
    sp500_ma_200 FLOAT,

    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

-- Indexes for market_data_history
CREATE INDEX idx_market_date ON market_data_history(date);
CREATE INDEX idx_market_created_at ON market_data_history(created_at);
CREATE UNIQUE INDEX idx_market_date_unique ON market_data_history(date);

COMMENT ON TABLE market_data_history IS '일일 시장 데이터 히스토리';
COMMENT ON COLUMN market_data_history.date IS '데이터 날짜';
COMMENT ON COLUMN market_data_history.sp500_close IS 'S&P 500 종가';
COMMENT ON COLUMN market_data_history.nasdaq_close IS 'NASDAQ 종가';
COMMENT ON COLUMN market_data_history.kospi_close IS 'KOSPI 종가';
COMMENT ON COLUMN market_data_history.kosdaq_close IS 'KOSDAQ 종가';


-- ==============================================================================
-- 2. Signal History Table
-- ==============================================================================

CREATE TABLE IF NOT EXISTS signal_history (
    id SERIAL PRIMARY KEY,

    -- Date
    date TIMESTAMP NOT NULL,

    -- Signal
    signal VARCHAR(20) NOT NULL,
    confidence FLOAT NOT NULL,
    score FLOAT,

    -- Breakdown
    market_correlation_score FLOAT,
    economic_score FLOAT,
    fear_greed_score FLOAT,
    yield_curve_score FLOAT,

    -- Action Plan
    action VARCHAR(200),
    timeframe VARCHAR(50),
    target_allocation TEXT,

    -- Risk Management
    stop_loss_pct FLOAT,
    take_profit_pct FLOAT,

    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

-- Indexes for signal_history
CREATE INDEX idx_signal_date ON signal_history(date);
CREATE INDEX idx_signal_signal ON signal_history(signal);
CREATE INDEX idx_signal_created_at ON signal_history(created_at);

COMMENT ON TABLE signal_history IS '투자 신호 히스토리';
COMMENT ON COLUMN signal_history.signal IS '투자 신호 (STRONG_BUY, BUY, HOLD, SELL, STRONG_SELL)';
COMMENT ON COLUMN signal_history.confidence IS '신뢰도 (%)';
COMMENT ON COLUMN signal_history.target_allocation IS '목표 자산 배분 (JSON)';


-- ==============================================================================
-- 3. Fear & Greed History Table
-- ==============================================================================

CREATE TABLE IF NOT EXISTS fear_greed_history (
    id SERIAL PRIMARY KEY,

    -- Date
    date TIMESTAMP NOT NULL,

    -- Fear & Greed Index
    score FLOAT NOT NULL,
    rating VARCHAR(20),

    -- Components
    market_momentum FLOAT,
    stock_price_strength FLOAT,
    stock_price_breadth FLOAT,
    put_call_ratio FLOAT,
    market_volatility FLOAT,
    safe_haven_demand FLOAT,
    junk_bond_demand FLOAT,

    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

-- Indexes for fear_greed_history
CREATE INDEX idx_fear_greed_date ON fear_greed_history(date);
CREATE INDEX idx_fear_greed_score ON fear_greed_history(score);
CREATE INDEX idx_fear_greed_created_at ON fear_greed_history(created_at);
CREATE UNIQUE INDEX idx_fear_greed_date_unique ON fear_greed_history(date);

COMMENT ON TABLE fear_greed_history IS 'Fear & Greed Index 히스토리';
COMMENT ON COLUMN fear_greed_history.score IS 'Fear & Greed 점수 (0-100)';
COMMENT ON COLUMN fear_greed_history.rating IS '등급 (Extreme Fear, Fear, Neutral, Greed, Extreme Greed)';


-- ==============================================================================
-- 4. Economic Data History Table
-- ==============================================================================

CREATE TABLE IF NOT EXISTS economic_data_history (
    id SERIAL PRIMARY KEY,

    -- Date
    date TIMESTAMP NOT NULL,

    -- Interest Rates
    us_fed_rate FLOAT,
    kr_base_rate FLOAT,
    interest_rate_spread FLOAT,

    -- Treasury Yields
    treasury_3m FLOAT,
    treasury_2y FLOAT,
    treasury_5y FLOAT,
    treasury_10y FLOAT,
    treasury_30y FLOAT,

    -- Yield Curve Spreads
    spread_10y_2y FLOAT,
    spread_10y_3m FLOAT,

    -- Yield Curve Analysis
    yield_curve_inverted BOOLEAN,
    recession_signal BOOLEAN,
    recession_probability FLOAT,

    -- Exchange Rates
    usd_krw FLOAT,
    usd_jpy FLOAT,
    eur_usd FLOAT,

    -- Inflation
    us_cpi FLOAT,
    kr_cpi FLOAT,

    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

-- Indexes for economic_data_history
CREATE INDEX idx_economic_date ON economic_data_history(date);
CREATE INDEX idx_economic_fed_rate ON economic_data_history(us_fed_rate);
CREATE INDEX idx_economic_spread ON economic_data_history(spread_10y_2y);
CREATE INDEX idx_economic_created_at ON economic_data_history(created_at);
CREATE UNIQUE INDEX idx_economic_date_unique ON economic_data_history(date);

COMMENT ON TABLE economic_data_history IS '경제 지표 히스토리';
COMMENT ON COLUMN economic_data_history.us_fed_rate IS '미국 기준금리 (%)';
COMMENT ON COLUMN economic_data_history.kr_base_rate IS '한국 기준금리 (%)';
COMMENT ON COLUMN economic_data_history.spread_10y_2y IS '10Y-2Y Spread (%p)';


-- ==============================================================================
-- 5. Backtest History Table
-- ==============================================================================

CREATE TABLE IF NOT EXISTS backtest_history (
    id SERIAL PRIMARY KEY,

    -- Backtest Info
    strategy_name VARCHAR(100) NOT NULL,
    start_date TIMESTAMP NOT NULL,
    end_date TIMESTAMP NOT NULL,

    -- Parameters
    initial_capital FLOAT NOT NULL,
    commission FLOAT,
    slippage FLOAT,
    risk_free_rate FLOAT,

    -- Performance Metrics
    final_value FLOAT,
    total_return_pct FLOAT,
    cagr_pct FLOAT,
    max_drawdown_pct FLOAT,
    volatility_pct FLOAT,
    sharpe_ratio FLOAT,
    sortino_ratio FLOAT,

    -- Trading Stats
    total_trades INTEGER,
    winning_trades INTEGER,
    losing_trades INTEGER,
    win_rate FLOAT,
    profit_factor FLOAT,
    avg_win FLOAT,
    avg_loss FLOAT,

    -- Benchmark Comparison
    benchmark_return_pct FLOAT,
    alpha_pct FLOAT,
    beta FLOAT,

    -- Detailed Results (JSON)
    equity_curve TEXT,
    trades TEXT,

    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

-- Indexes for backtest_history
CREATE INDEX idx_backtest_strategy ON backtest_history(strategy_name);
CREATE INDEX idx_backtest_start_date ON backtest_history(start_date);
CREATE INDEX idx_backtest_end_date ON backtest_history(end_date);
CREATE INDEX idx_backtest_created_at ON backtest_history(created_at);

COMMENT ON TABLE backtest_history IS '백테스팅 결과 히스토리';
COMMENT ON COLUMN backtest_history.strategy_name IS '전략 이름';
COMMENT ON COLUMN backtest_history.cagr_pct IS '연환산 수익률 (%)';
COMMENT ON COLUMN backtest_history.sharpe_ratio IS '샤프 비율';


-- ==============================================================================
-- Sample Queries
-- ==============================================================================

-- Get latest market data
-- SELECT * FROM market_data_history
-- ORDER BY date DESC
-- LIMIT 10;

-- Get signal changes (when signal differs from previous day)
-- SELECT
--     date,
--     signal,
--     confidence,
--     LAG(signal) OVER (ORDER BY date) as prev_signal
-- FROM signal_history
-- ORDER BY date DESC
-- LIMIT 20;

-- Get extreme fear/greed periods
-- SELECT
--     date,
--     score,
--     rating
-- FROM fear_greed_history
-- WHERE score < 25 OR score > 75
-- ORDER BY date DESC;

-- Get recession signals
-- SELECT
--     date,
--     spread_10y_2y,
--     recession_signal,
--     recession_probability
-- FROM economic_data_history
-- WHERE recession_signal = TRUE
-- ORDER BY date DESC;

-- Get best performing backtests
-- SELECT
--     strategy_name,
--     start_date,
--     end_date,
--     cagr_pct,
--     sharpe_ratio,
--     max_drawdown_pct
-- FROM backtest_history
-- ORDER BY sharpe_ratio DESC
-- LIMIT 10;

-- ==============================================================================
-- Rollback (if needed)
-- ==============================================================================

-- DROP TABLE IF EXISTS market_data_history CASCADE;
-- DROP TABLE IF EXISTS signal_history CASCADE;
-- DROP TABLE IF EXISTS fear_greed_history CASCADE;
-- DROP TABLE IF EXISTS economic_data_history CASCADE;
-- DROP TABLE IF EXISTS backtest_history CASCADE;
