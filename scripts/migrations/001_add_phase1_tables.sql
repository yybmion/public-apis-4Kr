-- Phase 1 Database Migration: Add Macroeconomic Data Tables
-- Created: 2025-11-22
-- Description: Adds 6 new tables for FRED, ECOS, and Fear & Greed Index data

-- ============================================================
-- TABLE 1: macro_indicators (거시경제 지표)
-- ============================================================
CREATE TABLE IF NOT EXISTS macro_indicators (
    id SERIAL PRIMARY KEY,

    -- 데이터 소스
    source VARCHAR(50) NOT NULL,        -- 'FRED', 'ECOS', etc.
    indicator_code VARCHAR(50) NOT NULL, -- 'FEDFUNDS', 'base_rate', etc.
    indicator_name VARCHAR(200),        -- Human-readable name

    -- 카테고리
    category VARCHAR(50),               -- 'interest_rates', 'employment', 'inflation', etc.
    country VARCHAR(10),                -- 'US', 'KR'

    -- 시계열 데이터
    date DATE NOT NULL,
    value DECIMAL(20,6) NOT NULL,
    unit VARCHAR(20),                   -- 'percent', 'KRW', 'index', etc.
    frequency VARCHAR(10),              -- 'D' (daily), 'M' (monthly), 'Q' (quarterly), 'A' (annual)

    -- 메타데이터
    metadata JSONB,                     -- 추가 정보 (JSON)
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),

    UNIQUE (source, indicator_code, date)
);

CREATE INDEX IF NOT EXISTS idx_macro_source_indicator_date
    ON macro_indicators(source, indicator_code, date DESC);
CREATE INDEX IF NOT EXISTS idx_macro_category_country_date
    ON macro_indicators(category, country, date DESC);
CREATE INDEX IF NOT EXISTS idx_macro_source_category
    ON macro_indicators(source, category);

COMMENT ON TABLE macro_indicators IS 'Time series data from FRED (800K+ US indicators) and ECOS (100K+ Korean indicators)';

-- ============================================================
-- TABLE 2: yield_curves (수익률 곡선)
-- ============================================================
CREATE TABLE IF NOT EXISTS yield_curves (
    id SERIAL PRIMARY KEY,

    -- 날짜 및 국가
    date DATE NOT NULL,
    country VARCHAR(10) NOT NULL,       -- 'US', 'KR'

    -- Yield 데이터 (단위: %)
    yield_3m DECIMAL(10,6),             -- 3개월
    yield_6m DECIMAL(10,6),             -- 6개월
    yield_1y DECIMAL(10,6),             -- 1년
    yield_2y DECIMAL(10,6),             -- 2년
    yield_3y DECIMAL(10,6),             -- 3년
    yield_5y DECIMAL(10,6),             -- 5년
    yield_7y DECIMAL(10,6),             -- 7년
    yield_10y DECIMAL(10,6),            -- 10년
    yield_20y DECIMAL(10,6),            -- 20년
    yield_30y DECIMAL(10,6),            -- 30년

    -- 스프레드 (basis points)
    spread_10y_2y DECIMAL(10,2),        -- 10Y - 2Y spread
    spread_10y_3m DECIMAL(10,2),        -- 10Y - 3M spread
    spread_2y_3m DECIMAL(10,2),         -- 2Y - 3M spread

    -- 경기 침체 신호
    is_inverted_10y_2y BOOLEAN,         -- 10Y < 2Y (주요 경기 침체 신호)
    is_inverted_10y_3m BOOLEAN,         -- 10Y < 3M
    recession_signal BOOLEAN,           -- 종합 경기 침체 신호

    -- 메타데이터
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),

    UNIQUE (date, country)
);

CREATE INDEX IF NOT EXISTS idx_yield_date_country
    ON yield_curves(date DESC, country);
CREATE INDEX IF NOT EXISTS idx_yield_recession_signal
    ON yield_curves(recession_signal, date DESC);

COMMENT ON TABLE yield_curves IS 'Yield curve data with automatic recession signal detection';

-- ============================================================
-- TABLE 3: economic_snapshots (경제 스냅샷)
-- ============================================================
CREATE TABLE IF NOT EXISTS economic_snapshots (
    id SERIAL PRIMARY KEY,

    -- 날짜 및 국가
    date DATE NOT NULL UNIQUE,
    country VARCHAR(10) DEFAULT 'GLOBAL',

    -- 미국 주요 지표
    us_federal_funds_rate DECIMAL(10,4),
    us_treasury_10y DECIMAL(10,4),
    us_treasury_2y DECIMAL(10,4),
    us_unemployment_rate DECIMAL(10,4),
    us_cpi DECIMAL(10,4),
    us_gdp_growth DECIMAL(10,4),
    us_sp500 DECIMAL(10,2),
    us_vix DECIMAL(10,2),

    -- 한국 주요 지표
    kr_base_rate DECIMAL(10,4),
    kr_usd_krw DECIMAL(10,2),
    kr_cpi DECIMAL(10,4),
    kr_unemployment_rate DECIMAL(10,4),
    kr_export BIGINT,                   -- 수출 (백만 달러)
    kr_import BIGINT,                   -- 수입 (백만 달러)

    -- Yield Curve 상태
    yield_curve_us_inverted BOOLEAN,
    yield_curve_kr_inverted BOOLEAN,

    -- 스냅샷 완성도
    completeness_score INTEGER,         -- 0-100 (수집된 지표 비율)

    -- 메타데이터
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_snapshot_date
    ON economic_snapshots(date DESC);
CREATE INDEX IF NOT EXISTS idx_snapshot_completeness
    ON economic_snapshots(completeness_score DESC);

COMMENT ON TABLE economic_snapshots IS 'Daily snapshot of key US and Korean economic indicators';

-- ============================================================
-- TABLE 4: fear_greed_index (공포 탐욕 지수)
-- ============================================================
CREATE TABLE IF NOT EXISTS fear_greed_index (
    id SERIAL PRIMARY KEY,

    -- 날짜 (unique)
    date DATE NOT NULL UNIQUE,

    -- Fear & Greed 점수
    score DECIMAL(5,2) NOT NULL,        -- 0-100
    rating VARCHAR(20) NOT NULL,        -- 'Extreme Fear', 'Fear', 'Neutral', 'Greed', 'Extreme Greed'

    -- 투자 신호
    signal VARCHAR(20),                 -- 'STRONG_BUY', 'BUY', 'WEAK_BUY', 'HOLD', 'WEAK_SELL', 'SELL', 'STRONG_SELL'
    signal_description TEXT,            -- 신호 설명 (한글)

    -- 이전 값 (비교용)
    previous_close DECIMAL(5,2),        -- 전일 종가
    previous_1_week DECIMAL(5,2),       -- 1주 전
    previous_1_month DECIMAL(5,2),      -- 1개월 전
    previous_1_year DECIMAL(5,2),       -- 1년 전

    -- 변화량
    daily_change DECIMAL(5,2),          -- 일일 변화
    weekly_change DECIMAL(5,2),         -- 주간 변화
    monthly_change DECIMAL(5,2),        -- 월간 변화

    -- 메타데이터
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_fear_greed_date
    ON fear_greed_index(date DESC);
CREATE INDEX IF NOT EXISTS idx_fear_greed_rating
    ON fear_greed_index(rating);
CREATE INDEX IF NOT EXISTS idx_fear_greed_signal
    ON fear_greed_index(signal);

COMMENT ON TABLE fear_greed_index IS 'CNN Fear & Greed Index with contrarian investment signals';

-- ============================================================
-- TABLE 5: market_sentiments (시장 심리 종합)
-- ============================================================
CREATE TABLE IF NOT EXISTS market_sentiments (
    id SERIAL PRIMARY KEY,

    -- 날짜
    date DATE NOT NULL UNIQUE,

    -- Fear & Greed Index
    fear_greed_score DECIMAL(5,2),
    fear_greed_rating VARCHAR(20),

    -- VIX (변동성 지수)
    vix_value DECIMAL(10,2),
    vix_level VARCHAR(20),              -- 'LOW', 'MEDIUM', 'HIGH', 'EXTREME'

    -- Put/Call Ratio
    put_call_ratio DECIMAL(10,4),

    -- 종합 심리 지표
    overall_sentiment_score DECIMAL(5,2), -- 0-100 (종합 점수)
    overall_sentiment_rating VARCHAR(20), -- 'EXTREME_FEAR', 'FEAR', 'NEUTRAL', 'GREED', 'EXTREME_GREED'

    -- 투자 신호
    composite_signal VARCHAR(20),       -- 'STRONG_BUY', 'BUY', 'HOLD', 'SELL', 'STRONG_SELL'
    market_regime VARCHAR(20),          -- 'Bull', 'Bear', 'Sideways', 'Volatile'

    -- 역발상 신호
    extreme_fear_alert BOOLEAN,         -- 극단적 공포 (역발상 매수 기회)
    extreme_greed_alert BOOLEAN,        -- 극단적 탐욕 (역발상 매도 고려)

    -- 메타데이터
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_sentiment_date
    ON market_sentiments(date DESC);
CREATE INDEX IF NOT EXISTS idx_sentiment_composite_signal
    ON market_sentiments(composite_signal);
CREATE INDEX IF NOT EXISTS idx_sentiment_extreme_alerts
    ON market_sentiments(extreme_fear_alert, extreme_greed_alert);

COMMENT ON TABLE market_sentiments IS 'Aggregated market sentiment from multiple sources';

-- ============================================================
-- TABLE 6: sentiment_history (심리 지표 이력)
-- ============================================================
CREATE TABLE IF NOT EXISTS sentiment_history (
    id SERIAL PRIMARY KEY,

    -- 기간 정의
    period_type VARCHAR(20) NOT NULL,   -- 'daily', 'weekly', 'monthly', 'yearly'
    period_start DATE NOT NULL,
    period_end DATE NOT NULL,

    -- Fear & Greed 통계
    avg_fear_greed DECIMAL(5,2),
    min_fear_greed DECIMAL(5,2),
    max_fear_greed DECIMAL(5,2),
    std_fear_greed DECIMAL(5,2),        -- 표준편차 (변동성)

    -- 기간별 일수
    extreme_fear_days INTEGER,          -- 극단적 공포 일수
    fear_days INTEGER,
    neutral_days INTEGER,
    greed_days INTEGER,
    extreme_greed_days INTEGER,

    -- 추세 분석
    trend_direction VARCHAR(20),        -- 'increasing', 'decreasing', 'stable'
    trend_strength DECIMAL(5,2),        -- 0-100 (추세 강도)

    -- 메타데이터
    created_at TIMESTAMP DEFAULT NOW(),

    UNIQUE (period_type, period_start, period_end)
);

CREATE INDEX IF NOT EXISTS idx_sentiment_history_period
    ON sentiment_history(period_type, period_start DESC);

COMMENT ON TABLE sentiment_history IS 'Historical sentiment analysis by period';

-- ============================================================
-- Verification Query
-- ============================================================
-- Run this to verify all tables were created successfully:
-- SELECT table_name FROM information_schema.tables
-- WHERE table_schema = 'public' AND table_name IN (
--   'macro_indicators', 'yield_curves', 'economic_snapshots',
--   'fear_greed_index', 'market_sentiments', 'sentiment_history'
-- );
