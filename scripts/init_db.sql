-- Stock Intelligence System Database Schema
-- Version: 1.0
-- Date: 2025-11-21

-- Drop existing tables if they exist
DROP TABLE IF EXISTS backtest_results CASCADE;
DROP TABLE IF EXISTS recommendations CASCADE;
DROP TABLE IF EXISTS stock_news CASCADE;
DROP TABLE IF EXISTS economic_indicators CASCADE;
DROP TABLE IF EXISTS us_indices CASCADE;
DROP TABLE IF EXISTS financials CASCADE;
DROP TABLE IF EXISTS stock_prices CASCADE;
DROP TABLE IF EXISTS stocks CASCADE;

-- 1. stocks (종목 기본 정보)
CREATE TABLE stocks (
    code VARCHAR(10) PRIMARY KEY,              -- 종목코드 (예: '005930')
    name VARCHAR(100) NOT NULL,                -- 종목명 (예: '삼성전자')
    market VARCHAR(10),                        -- 시장 ('KOSPI', 'KOSDAQ')
    sector VARCHAR(50),                        -- 섹터
    market_cap BIGINT,                         -- 시가총액 (원)
    description TEXT,                          -- 회사 설명
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_stocks_sector ON stocks(sector);
CREATE INDEX idx_stocks_market_cap ON stocks(market_cap DESC);

-- 2. stock_prices (주가 데이터)
CREATE TABLE stock_prices (
    id SERIAL PRIMARY KEY,
    stock_code VARCHAR(10) NOT NULL,
    date DATE NOT NULL,
    open INTEGER NOT NULL,                     -- 시가
    high INTEGER NOT NULL,                     -- 고가
    low INTEGER NOT NULL,                      -- 저가
    close INTEGER NOT NULL,                    -- 종가
    volume BIGINT,                             -- 거래량
    trading_value BIGINT,                      -- 거래대금
    change_rate DECIMAL(5,2),                  -- 등락률
    foreign_ownership DECIMAL(5,2),            -- 외국인 보유 비율
    source VARCHAR(50),                        -- 데이터 출처
    verified BOOLEAN DEFAULT FALSE,            -- 검증 여부
    created_at TIMESTAMP DEFAULT NOW(),

    FOREIGN KEY (stock_code) REFERENCES stocks(code) ON DELETE CASCADE,
    UNIQUE (stock_code, date)
);

CREATE INDEX idx_stock_prices_stock_date ON stock_prices(stock_code, date DESC);
CREATE INDEX idx_stock_prices_date ON stock_prices(date DESC);

-- 3. financials (재무제표)
CREATE TABLE financials (
    id SERIAL PRIMARY KEY,
    stock_code VARCHAR(10) NOT NULL,
    year INTEGER NOT NULL,
    quarter INTEGER,                           -- 1, 2, 3, 4 (연간은 NULL)
    revenue BIGINT,                            -- 매출액
    operating_profit BIGINT,                   -- 영업이익
    net_income BIGINT,                         -- 당기순이익
    total_assets BIGINT,                       -- 총자산
    total_liabilities BIGINT,                  -- 총부채
    equity BIGINT,                             -- 자본
    per DECIMAL(10,2),                         -- PER
    pbr DECIMAL(10,2),                         -- PBR
    roe DECIMAL(5,2),                          -- ROE (%)
    debt_ratio DECIMAL(5,2),                   -- 부채비율 (%)
    dividend_yield DECIMAL(5,2),               -- 배당수익률 (%)
    source VARCHAR(50) DEFAULT 'DART',
    verified BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),

    FOREIGN KEY (stock_code) REFERENCES stocks(code) ON DELETE CASCADE,
    UNIQUE (stock_code, year, quarter)
);

CREATE INDEX idx_financials_stock_year ON financials(stock_code, year DESC);

-- 4. us_indices (미국 지수)
CREATE TABLE us_indices (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(10) NOT NULL,               -- '^GSPC', '^IXIC', '^DJI'
    name VARCHAR(50),                          -- 'S&P 500', 'NASDAQ', 'Dow Jones'
    close DECIMAL(10,2) NOT NULL,
    change_rate DECIMAL(5,2),
    ma_20 DECIMAL(10,2),                       -- 20일 이동평균선
    ma_60 DECIMAL(10,2),                       -- 60일 이동평균선
    above_ma BOOLEAN,                          -- 이평선 위 여부
    date DATE NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),

    UNIQUE (symbol, date)
);

CREATE INDEX idx_us_indices_symbol_date ON us_indices(symbol, date DESC);

-- 5. economic_indicators (경제 지표)
CREATE TABLE economic_indicators (
    id SERIAL PRIMARY KEY,
    indicator_name VARCHAR(50) NOT NULL,       -- 'base_rate', 'usd_krw', 'cpi'
    country VARCHAR(10),                       -- 'KR', 'US'
    value DECIMAL(10,4) NOT NULL,
    unit VARCHAR(20),                          -- '%', '원', 'points'
    date DATE NOT NULL,
    source VARCHAR(50),                        -- 'ECOS', 'FRED'
    created_at TIMESTAMP DEFAULT NOW(),

    UNIQUE (indicator_name, country, date)
);

CREATE INDEX idx_economic_indicators_name_date ON economic_indicators(indicator_name, date DESC);

-- 6. stock_news (뉴스)
CREATE TABLE stock_news (
    id SERIAL PRIMARY KEY,
    stock_code VARCHAR(10),
    title VARCHAR(500) NOT NULL,
    content TEXT,
    source VARCHAR(100),                       -- '한국경제', '연합뉴스'
    source_tier INTEGER,                       -- 1, 2, 3 (신뢰도)
    url VARCHAR(500),
    sentiment_score DECIMAL(3,2),              -- -1.0 ~ +1.0
    sentiment_label VARCHAR(20),               -- 'positive', 'negative', 'neutral'
    published_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW(),

    FOREIGN KEY (stock_code) REFERENCES stocks(code) ON DELETE CASCADE
);

CREATE INDEX idx_stock_news_stock_published ON stock_news(stock_code, published_at DESC);
CREATE INDEX idx_stock_news_published ON stock_news(published_at DESC);

-- 7. recommendations (추천 종목)
CREATE TABLE recommendations (
    id SERIAL PRIMARY KEY,
    stock_code VARCHAR(10) NOT NULL,
    score INTEGER NOT NULL,                    -- 0~100 (초보자 적합도)
    risk_level VARCHAR(10),                    -- 'LOW', 'MEDIUM', 'HIGH'
    reasons JSONB,                             -- ['이유1', '이유2', '이유3']
    expected_return_1m DECIMAL(5,2),           -- 1개월 예상 수익률
    max_drawdown DECIMAL(5,2),                 -- 예상 최대 낙폭
    us_correlation DECIMAL(3,2),               -- S&P 500 상관계수
    us_signal VARCHAR(10),                     -- 'BULLISH', 'BEARISH'
    valid_until DATE,                          -- 추천 유효 기한
    created_at TIMESTAMP DEFAULT NOW(),

    FOREIGN KEY (stock_code) REFERENCES stocks(code) ON DELETE CASCADE
);

CREATE INDEX idx_recommendations_score ON recommendations(score DESC);
CREATE INDEX idx_recommendations_created ON recommendations(created_at DESC);

-- 8. backtest_results (백테스트 결과)
CREATE TABLE backtest_results (
    id SERIAL PRIMARY KEY,
    strategy_name VARCHAR(100) NOT NULL,
    description TEXT,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    initial_capital BIGINT,
    final_capital BIGINT,
    total_return DECIMAL(10,2),                -- 총 수익률 (%)
    cagr DECIMAL(5,2),                         -- 연평균 수익률
    mdd DECIMAL(5,2),                          -- 최대 낙폭
    sharpe_ratio DECIMAL(5,2),                 -- 샤프 비율
    win_rate DECIMAL(5,2),                     -- 승률 (%)
    total_trades INTEGER,                      -- 총 거래 횟수
    parameters JSONB,                          -- 전략 파라미터
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_backtest_results_strategy ON backtest_results(strategy_name);
CREATE INDEX idx_backtest_results_sharpe ON backtest_results(sharpe_ratio DESC);

-- Insert sample data for testing (optional)
-- KOSPI 대형주 샘플
INSERT INTO stocks (code, name, market, sector, market_cap) VALUES
('005930', '삼성전자', 'KOSPI', 'IT/반도체', 445000000000000),
('000660', 'SK하이닉스', 'KOSPI', 'IT/반도체', 95000000000000),
('035720', '카카오', 'KOSPI', 'IT/인터넷', 25000000000000),
('051910', 'LG화학', 'KOSPI', '화학', 48000000000000),
('006400', '삼성SDI', 'KOSPI', '전기전자', 42000000000000),
('035420', 'NAVER', 'KOSPI', 'IT/인터넷', 35000000000000),
('028260', '삼성물산', 'KOSPI', '건설', 28000000000000),
('105560', 'KB금융', 'KOSPI', '금융', 24000000000000),
('055550', '신한지주', 'KOSPI', '금융', 22000000000000),
('012330', '현대모비스', 'KOSPI', '자동차', 26000000000000)
ON CONFLICT (code) DO NOTHING;

COMMENT ON TABLE stocks IS '종목 기본 정보';
COMMENT ON TABLE stock_prices IS '일별 주가 데이터';
COMMENT ON TABLE financials IS '재무제표 정보';
COMMENT ON TABLE us_indices IS '미국 주요 지수';
COMMENT ON TABLE economic_indicators IS '경제 지표';
COMMENT ON TABLE stock_news IS '종목별 뉴스';
COMMENT ON TABLE recommendations IS '추천 종목';
COMMENT ON TABLE backtest_results IS '백테스팅 결과';
