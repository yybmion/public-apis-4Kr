# LLD: 한국 주식 자동매매 지원 시스템
## Low-Level Design Document

**문서 버전**: 2.0
**작성일**: 2025-11-21
**최종 업데이트**: 2025-11-22
**프로젝트명**: Stock Intelligence System (SIS)

---

## 📋 문서 개요

이 문서는 주식 투자 지원 시스템의 **저수준 설계**를 정의합니다.
실제 구현 가능한 코드 레벨의 설계, API 명세, 데이터베이스 스키마, 클래스 다이어그램 등을 포함합니다.

---

## 목차

1. [시스템 아키텍처](#1-시스템-아키텍처)
2. [데이터베이스 설계](#2-데이터베이스-설계)
3. [API 설계](#3-api-설계)
4. [클래스 다이어그램](#4-클래스-다이어그램)
5. [데이터 플로우](#5-데이터-플로우)
6. [모듈별 상세 설계](#6-모듈별-상세-설계)
7. [배포 아키텍처](#7-배포-아키텍처)

---

## 1. 시스템 아키텍처

### 1.1 전체 아키텍처 다이어그램

```
┌─────────────────────────────────────────────────────────────┐
│                         Frontend Layer                       │
│                    (Streamlit Web Dashboard)                 │
└─────────────────────────────────────────────────────────────┘
                              │ HTTPS
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                       API Gateway Layer                      │
│                         (FastAPI)                            │
├─────────────────────────────────────────────────────────────┤
│  GET  /api/v1/stocks/{code}          # 종목 정보           │
│  GET  /api/v1/recommendations         # 추천 종목          │
│  POST /api/v1/chart/analyze           # 차트 분석          │
│  GET  /api/v1/market/overview         # 시장 현황          │
│  POST /api/v1/llm/analyze-multi       # Multi-LLM 분석     │
│  POST /api/v1/llm/analyze-signal/{code} # LLM 종합 분석   │
└─────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        ↓                     ↓                     ↓
┌────────────────┐  ┌────────────────┐  ┌────────────────┐
│ Data Collector │  │ Analysis       │  │ Recommendation │
│ Service        │  │ Service        │  │ Engine         │
├────────────────┤  ├────────────────┤  ├────────────────┤
│ • KIS API      │  │ • Technical    │  │ • Filtering    │
│ • DART API     │  │   Indicators   │  │ • Scoring      │
│ • Yahoo Finance│  │ • Backtest     │  │ • Ranking      │
│ • ECOS API     │  │ • Chart OCR    │  │                │
│ • News API     │  │ • Sentiment    │  │                │
└────────────────┘  └────────────────┘  └────────────────┘
        │                     │                     │
        └─────────────────────┼─────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                   Multi-LLM Analysis Layer                   │
│                    (LLM Orchestrator)                        │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐       │
│  │ Claude  │  │  GPT-4  │  │ Gemini  │  │  Grok   │       │
│  │ Sonnet 4│  │ Turbo   │  │  Pro    │  │   2     │       │
│  └─────────┘  └─────────┘  └─────────┘  └─────────┘       │
│       ↓            ↓            ↓            ↓              │
│  ┌─────────────────────────────────────────────────┐       │
│  │         Consensus Voting Mechanism              │       │
│  │  • BUY/SELL/HOLD 투표                           │       │
│  │  • 신뢰도 가중 평균                             │       │
│  │  • 동의 수준 계산                               │       │
│  └─────────────────────────────────────────────────┘       │
└─────────────────────────────────────────────────────────────┘
        │                     │                     │
        └─────────────────────┼─────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                     Data Access Layer                        │
│                    (SQLAlchemy ORM)                          │
└─────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        ↓                     ↓                     ↓
┌────────────────┐  ┌────────────────┐  ┌────────────────┐
│   Supabase     │  │     Redis      │  │   AWS S3       │
│  (PostgreSQL)  │  │   (Cache)      │  │  (차트 이미지)  │
│  • 주가/종목   │  │                │  │                │
│  • LLM분석기록 │  │                │  │                │
│  • 합의결과    │  │                │  │                │
└────────────────┘  └────────────────┘  └────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                   Background Jobs Layer                      │
│                (AWS Lambda + CloudWatch)                     │
├─────────────────────────────────────────────────────────────┤
│  • 09:00: 미국 시장 분석 리포트 생성                          │
│  • 09:00-15:30: 10초마다 실시간 시세 수집                    │
│  • 16:00: 일일 백테스팅 실행                                 │
│  • 18:00: 뉴스 감성 분석                                     │
│  • 매시 정각: 경제 지표 업데이트                             │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                    Notification Layer                        │
│                 (카카오톡 메시지 API)                         │
└─────────────────────────────────────────────────────────────┘
```

### 1.2 기술 스택

| Layer | Technology | Version |
|-------|-----------|---------|
| **Frontend** | Streamlit | 1.28+ |
| **API Server** | FastAPI | 0.104+ |
| **Database** | Supabase (PostgreSQL) | 15+ |
| **Cache** | Redis | 7+ |
| **ORM** | SQLAlchemy | 2.0+ |
| **LLM - Agent 1** | Anthropic Claude Sonnet 4 | latest |
| **LLM - Agent 2** | OpenAI GPT-4 Turbo | gpt-4-turbo |
| **LLM - Agent 3** | Google Gemini Pro | latest |
| **LLM - Agent 4** | xAI Grok 2 | grok-2 |
| **Task Queue** | AWS Lambda | - |
| **Storage** | AWS S3 | - |
| **Monitoring** | CloudWatch | - |

### 1.3 디렉토리 구조

```
stock-intelligence-system/
├── app/
│   ├── __init__.py
│   ├── main.py                    # FastAPI 앱 엔트리포인트
│   ├── config.py                  # 설정 관리
│   ├── dependencies.py            # DI 컨테이너
│   │
│   ├── api/                       # API 라우터
│   │   ├── __init__.py
│   │   ├── v1/
│   │   │   ├── __init__.py
│   │   │   ├── stocks.py
│   │   │   ├── recommendations.py
│   │   │   ├── market.py
│   │   │   └── chart_analysis.py
│   │
│   ├── collectors/                # 데이터 수집기
│   │   ├── __init__.py
│   │   ├── base.py               # 추상 클래스
│   │   ├── kis_collector.py      # 한국투자증권 API
│   │   ├── dart_collector.py     # 전자공시
│   │   ├── yahoo_collector.py    # Yahoo Finance
│   │   ├── ecos_collector.py     # 한국은행
│   │   └── news_collector.py     # 뉴스 수집
│   │
│   ├── analyzers/                 # 분석기
│   │   ├── __init__.py
│   │   ├── technical_analyzer.py  # 기술적 분석
│   │   ├── chart_ocr.py          # 차트 OCR
│   │   ├── sentiment_analyzer.py  # 감성 분석
│   │   └── backtest_engine.py    # 백테스팅
│   │
│   ├── recommenders/              # 추천 엔진
│   │   ├── __init__.py
│   │   ├── beginner_recommender.py
│   │   ├── sector_analyzer.py
│   │   └── scoring.py
│   │
│   ├── llm/                       # Multi-LLM 분석 시스템
│   │   ├── __init__.py
│   │   ├── orchestrator.py        # LLM 조정자 (투표 메커니즘)
│   │   └── agents/                # LLM 에이전트
│   │       ├── __init__.py
│   │       ├── base_agent.py      # 추상 기본 클래스
│   │       ├── claude_agent.py    # Claude Sonnet 4
│   │       ├── gpt4_agent.py      # GPT-4 Turbo
│   │       ├── gemini_agent.py    # Gemini Pro
│   │       └── grok_agent.py      # Grok 2
│   │
│   ├── models/                    # 데이터 모델
│   │   ├── __init__.py
│   │   ├── stock.py
│   │   ├── price.py
│   │   ├── financial.py
│   │   ├── user.py
│   │   └── llm_analysis.py        # LLM 분석 추적 모델
│   │
│   ├── schemas/                   # Pydantic 스키마
│   │   ├── __init__.py
│   │   ├── stock.py
│   │   ├── recommendation.py
│   │   └── market.py
│   │
│   ├── database/                  # DB 관련
│   │   ├── __init__.py
│   │   ├── session.py
│   │   └── base.py
│   │
│   ├── utils/                     # 유틸리티
│   │   ├── __init__.py
│   │   ├── logger.py
│   │   ├── cache.py
│   │   └── validators.py
│   │
│   └── tasks/                     # 백그라운드 작업
│       ├── __init__.py
│       ├── daily_tasks.py
│       └── realtime_tasks.py
│
├── dashboard/                     # Streamlit 대시보드
│   ├── app.py
│   ├── pages/
│   │   ├── 01_market_overview.py
│   │   ├── 02_recommendations.py
│   │   ├── 03_stock_detail.py
│   │   └── 04_chart_analysis.py
│   └── components/
│       ├── charts.py
│       └── widgets.py
│
├── tests/                         # 테스트
│   ├── test_collectors/
│   ├── test_analyzers/
│   └── test_recommenders/
│
├── scripts/                       # 유틸리티 스크립트
│   ├── init_db.py
│   ├── seed_data.py
│   └── backfill_historical.py
│
├── docker/
│   ├── Dockerfile
│   └── docker-compose.yml
│
├── requirements.txt
├── .env.example
└── README.md
```

---

## 2. 데이터베이스 설계

### 2.1 ERD (Entity-Relationship Diagram)

```
┌─────────────────┐
│     stocks      │
├─────────────────┤
│ PK code         │───┐
│    name         │   │
│    market       │   │ 1:N
│    sector       │   │
│    market_cap   │   │
│    created_at   │   │
└─────────────────┘   │
                      │
        ┌─────────────┴────────────────────┬──────────────┐
        │                                  │              │
        ↓                                  ↓              ↓
┌──────────────────┐          ┌─────────────────────┐   ┌──────────────────┐
│  stock_prices    │          │    financials       │   │  stock_news      │
├──────────────────┤          ├─────────────────────┤   ├──────────────────┤
│ PK id            │          │ PK id               │   │ PK id            │
│ FK stock_code    │          │ FK stock_code       │   │ FK stock_code    │
│    date          │          │    year             │   │    title         │
│    open          │          │    quarter          │   │    content       │
│    high          │          │    revenue          │   │    source        │
│    low           │          │    operating_profit │   │    sentiment     │
│    close         │          │    net_income       │   │    published_at  │
│    volume        │          │    total_assets     │   │    created_at    │
│    source        │          │    per              │   └──────────────────┘
│    verified      │          │    pbr              │
│    created_at    │          │    roe              │
└──────────────────┘          │    source           │
                              │    verified         │
                              │    created_at       │
                              └─────────────────────┘

┌─────────────────────┐       ┌──────────────────────┐
│   us_indices        │       │   economic_indices   │
├─────────────────────┤       ├──────────────────────┤
│ PK id               │       │ PK id                │
│    symbol           │       │    indicator_name    │
│    name             │       │    country           │
│    close            │       │    value             │
│    change_rate      │       │    unit              │
│    ma_20            │       │    date              │
│    ma_60            │       │    source            │
│    date             │       │    created_at        │
│    created_at       │       └──────────────────────┘
└─────────────────────┘

┌──────────────────────┐      ┌──────────────────────┐
│   recommendations    │      │   backtest_results   │
├──────────────────────┤      ├──────────────────────┤
│ PK id                │      │ PK id                │
│ FK stock_code        │      │    strategy_name     │
│    score             │      │    start_date        │
│    risk_level        │      │    end_date          │
│    reasons           │      │    total_return      │
│    expected_return   │      │    cagr              │
│    max_drawdown      │      │    mdd               │
│    us_signal         │      │    sharpe_ratio      │
│    created_at        │      │    win_rate          │
└──────────────────────┘      │    created_at        │
                              └──────────────────────┘

┌─────────────────────────────────── LLM Analysis Tables ────────────────────────────────┐

┌──────────────────────┐      ┌──────────────────────┐      ┌──────────────────────┐
│   llm_analyses       │      │   llm_consensus      │      │  llm_performance     │
├──────────────────────┤      ├──────────────────────┤      ├──────────────────────┤
│ PK id                │      │ PK id                │      │ PK id                │
│ FK stock_code        │  ┌───│ FK stock_code        │      │    llm_model         │
│    stock_name        │  │   │    analysis_type     │      │    total_requests    │
│    analysis_type     │  │   │    claude_analysis_id├──┐   │    total_tokens      │
│    llm_model         │◄─┘   │    gpt4_analysis_id  │  │   │    total_cost        │
│    model_version     │  ┌───│    gemini_analysis_id│  │   │    avg_latency_ms    │
│    input_data (JSON) │  │┌──│    grok_analysis_id  │  │   │    success_rate      │
│    llm_response      │  ││  │    buy_votes         │  │   │    accuracy          │
│    parsed_result     │  ││  │    sell_votes        │  │   │    buy_count         │
│    decision          │  ││  │    hold_votes        │  │   │    sell_count        │
│    confidence        │  ││  │    consensus_decision│  │   │    hold_count        │
│    tokens_used       │  ││  │    consensus_conf    │  │   │    last_used_at      │
│    cost              │  ││  │    agreement_level   │  │   │    updated_at        │
│    latency_ms        │  ││  │    avg_confidence    │  │   └──────────────────────┘
│    success           │  ││  │    recommendation    │  │
│    created_at        │  ││  │    created_at        │  │
└──────────────────────┘  ││  └──────────────────────┘  │
        │  │  │  │        ││                            │
        └──┴──┴──┴────────┴┴────────────────────────────┘
         Claude GPT4 Gemini Grok (4-way relationship)

┌──────────────────────────┐
│  data_collection_logs    │
├──────────────────────────┤
│ PK id                    │
│    collector_type        │  -- 'kis', 'yahoo', 'dart', 'news', 'social'
│    action                │
│    target_code           │
│    success               │
│    records_collected     │
│    duration_ms           │
│    error_message         │
│    metadata (JSON)       │
│    created_at            │
└──────────────────────────┘

┌────────────────────────── Social Media Tables ─────────────────────────────┐

┌──────────────────────────┐      ┌──────────────────────────┐
│ social_media_mentions    │      │ social_influencer_posts  │
├──────────────────────────┤      ├──────────────────────────┤
│ PK id                    │      │ PK id                    │
│    source                │      │    username              │
│    platform              │      │    platform              │
│    ticker                │      │    post_id (unique)      │
│    stock_code            │      │    post_url              │
│    mention_count         │      │    post_text             │
│    rank                  │      │    mentioned_tickers     │
│    sentiment             │      │    sentiment             │
│    sentiment_score       │      │    sentiment_score       │
│    bullish_ratio         │      │    like_count            │
│    impact_score          │      │    retweet_count         │
│    comment_count         │      │    reply_count           │
│    upvote_count          │      │    impact_score          │
│    raw_data (JSON)       │      │    posted_at             │
│    data_date             │      │    collected_at          │
│    collected_at          │      │    created_at            │
│    created_at            │      └──────────────────────────┘
└──────────────────────────┘
  Source: WallStreetBets, StockTwits
  실시간 투자자 감성 추적
```

### 2.2 테이블 상세 스키마

#### 2.2.1 stocks (종목 기본 정보)

```sql
CREATE TABLE stocks (
    code VARCHAR(10) PRIMARY KEY,        -- 종목코드 (예: '005930')
    name VARCHAR(100) NOT NULL,          -- 종목명 (예: '삼성전자')
    market VARCHAR(10),                  -- 시장 ('KOSPI', 'KOSDAQ')
    sector VARCHAR(50),                  -- 섹터
    market_cap BIGINT,                   -- 시가총액 (원)
    description TEXT,                    -- 회사 설명
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),

    INDEX idx_sector (sector),
    INDEX idx_market_cap (market_cap DESC)
);
```

#### 2.2.2 stock_prices (주가 데이터)

```sql
CREATE TABLE stock_prices (
    id SERIAL PRIMARY KEY,
    stock_code VARCHAR(10) NOT NULL,
    date DATE NOT NULL,
    open INTEGER NOT NULL,               -- 시가
    high INTEGER NOT NULL,               -- 고가
    low INTEGER NOT NULL,                -- 저가
    close INTEGER NOT NULL,              -- 종가
    volume BIGINT,                       -- 거래량
    trading_value BIGINT,                -- 거래대금
    change_rate DECIMAL(5,2),            -- 등락률
    foreign_ownership DECIMAL(5,2),      -- 외국인 보유 비율
    source VARCHAR(50),                  -- 데이터 출처
    verified BOOLEAN DEFAULT FALSE,      -- 검증 여부
    created_at TIMESTAMP DEFAULT NOW(),

    FOREIGN KEY (stock_code) REFERENCES stocks(code),
    UNIQUE (stock_code, date),
    INDEX idx_stock_date (stock_code, date DESC)
);
```

#### 2.2.3 financials (재무제표)

```sql
CREATE TABLE financials (
    id SERIAL PRIMARY KEY,
    stock_code VARCHAR(10) NOT NULL,
    year INTEGER NOT NULL,
    quarter INTEGER,                     -- 1, 2, 3, 4 (연간은 NULL)
    revenue BIGINT,                      -- 매출액
    operating_profit BIGINT,             -- 영업이익
    net_income BIGINT,                   -- 당기순이익
    total_assets BIGINT,                 -- 총자산
    total_liabilities BIGINT,            -- 총부채
    equity BIGINT,                       -- 자본
    per DECIMAL(10,2),                   -- PER
    pbr DECIMAL(10,2),                   -- PBR
    roe DECIMAL(5,2),                    -- ROE (%)
    debt_ratio DECIMAL(5,2),             -- 부채비율 (%)
    dividend_yield DECIMAL(5,2),         -- 배당수익률 (%)
    source VARCHAR(50) DEFAULT 'DART',
    verified BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),

    FOREIGN KEY (stock_code) REFERENCES stocks(code),
    UNIQUE (stock_code, year, quarter),
    INDEX idx_stock_year (stock_code, year DESC)
);
```

#### 2.2.4 us_indices (미국 지수)

```sql
CREATE TABLE us_indices (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(10) NOT NULL,         -- '^GSPC', '^IXIC', '^DJI'
    name VARCHAR(50),                    -- 'S&P 500', 'NASDAQ', 'Dow Jones'
    close DECIMAL(10,2) NOT NULL,
    change_rate DECIMAL(5,2),
    ma_20 DECIMAL(10,2),                 -- 20일 이동평균선
    ma_60 DECIMAL(10,2),                 -- 60일 이동평균선
    above_ma BOOLEAN,                    -- 이평선 위 여부
    date DATE NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),

    UNIQUE (symbol, date),
    INDEX idx_symbol_date (symbol, date DESC)
);
```

#### 2.2.5 economic_indicators (경제 지표)

```sql
CREATE TABLE economic_indicators (
    id SERIAL PRIMARY KEY,
    indicator_name VARCHAR(50) NOT NULL,  -- 'base_rate', 'usd_krw', 'cpi'
    country VARCHAR(10),                  -- 'KR', 'US'
    value DECIMAL(10,4) NOT NULL,
    unit VARCHAR(20),                     -- '%', '원', 'points'
    date DATE NOT NULL,
    source VARCHAR(50),                   -- 'ECOS', 'FRED'
    created_at TIMESTAMP DEFAULT NOW(),

    UNIQUE (indicator_name, country, date),
    INDEX idx_indicator_date (indicator_name, date DESC)
);
```

#### 2.2.6 stock_news (뉴스)

```sql
CREATE TABLE stock_news (
    id SERIAL PRIMARY KEY,
    stock_code VARCHAR(10),
    title VARCHAR(500) NOT NULL,
    content TEXT,
    source VARCHAR(100),                 -- '한국경제', '연합뉴스'
    source_tier INTEGER,                 -- 1, 2, 3 (신뢰도)
    url VARCHAR(500),
    sentiment_score DECIMAL(3,2),        -- -1.0 ~ +1.0
    sentiment_label VARCHAR(20),         -- 'positive', 'negative', 'neutral'
    published_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW(),

    FOREIGN KEY (stock_code) REFERENCES stocks(code),
    INDEX idx_stock_published (stock_code, published_at DESC),
    INDEX idx_published (published_at DESC)
);
```

#### 2.2.7 recommendations (추천 종목)

```sql
CREATE TABLE recommendations (
    id SERIAL PRIMARY KEY,
    stock_code VARCHAR(10) NOT NULL,
    score INTEGER NOT NULL,              -- 0~100 (초보자 적합도)
    risk_level VARCHAR(10),              -- 'LOW', 'MEDIUM', 'HIGH'
    reasons JSONB,                       -- ['이유1', '이유2', '이유3']
    expected_return_1m DECIMAL(5,2),     -- 1개월 예상 수익률
    max_drawdown DECIMAL(5,2),           -- 예상 최대 낙폭
    us_correlation DECIMAL(3,2),         -- S&P 500 상관계수
    us_signal VARCHAR(10),               -- 'BULLISH', 'BEARISH'
    valid_until DATE,                    -- 추천 유효 기한
    created_at TIMESTAMP DEFAULT NOW(),

    FOREIGN KEY (stock_code) REFERENCES stocks(code),
    INDEX idx_score (score DESC),
    INDEX idx_created (created_at DESC)
);
```

#### 2.2.8 backtest_results (백테스트 결과)

```sql
CREATE TABLE backtest_results (
    id SERIAL PRIMARY KEY,
    strategy_name VARCHAR(100) NOT NULL,
    description TEXT,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    initial_capital BIGINT,
    final_capital BIGINT,
    total_return DECIMAL(10,2),          -- 총 수익률 (%)
    cagr DECIMAL(5,2),                   -- 연평균 수익률
    mdd DECIMAL(5,2),                    -- 최대 낙폭
    sharpe_ratio DECIMAL(5,2),           -- 샤프 비율
    win_rate DECIMAL(5,2),               -- 승률 (%)
    total_trades INTEGER,                -- 총 거래 횟수
    parameters JSONB,                    -- 전략 파라미터
    created_at TIMESTAMP DEFAULT NOW(),

    INDEX idx_strategy (strategy_name),
    INDEX idx_sharpe (sharpe_ratio DESC)
);
```

#### 2.2.9 llm_analyses (LLM 분석 기록)

```sql
CREATE TABLE llm_analyses (
    id SERIAL PRIMARY KEY,
    stock_code VARCHAR(10) NOT NULL,
    stock_name VARCHAR(100),
    analysis_type VARCHAR(50),          -- 'news_risk', 'combined_signal', 'explanation'
    llm_model VARCHAR(50) NOT NULL,     -- 'claude', 'gpt4', 'gemini', 'grok'
    model_version VARCHAR(50),

    input_data JSONB,                   -- 입력 데이터
    llm_response TEXT,                  -- 원본 LLM 응답
    parsed_result JSONB,                -- 파싱된 결과

    decision VARCHAR(20),               -- 'BUY', 'SELL', 'HOLD'
    confidence DECIMAL(5,2),            -- 신뢰도 (0-100)

    tokens_used INTEGER,                -- 토큰 사용량
    cost DECIMAL(10,6),                 -- 비용 (USD)
    latency_ms INTEGER,                 -- 응답 시간 (ms)

    success BOOLEAN DEFAULT TRUE,
    error_message TEXT,
    created_at TIMESTAMP DEFAULT NOW(),

    INDEX idx_stock_code (stock_code),
    INDEX idx_llm_model (llm_model),
    INDEX idx_created_at (created_at DESC),
    FOREIGN KEY (stock_code) REFERENCES stocks(code)
);
```

#### 2.2.10 llm_consensus (LLM 합의 결과)

```sql
CREATE TABLE llm_consensus (
    id SERIAL PRIMARY KEY,
    stock_code VARCHAR(10) NOT NULL,
    stock_name VARCHAR(100),
    analysis_type VARCHAR(50),

    claude_analysis_id INTEGER,         -- FK to llm_analyses
    gpt4_analysis_id INTEGER,
    gemini_analysis_id INTEGER,
    grok_analysis_id INTEGER,

    buy_votes INTEGER DEFAULT 0,
    sell_votes INTEGER DEFAULT 0,
    hold_votes INTEGER DEFAULT 0,

    consensus_decision VARCHAR(20),     -- 'BUY', 'SELL', 'HOLD', 'NO_CONSENSUS'
    consensus_confidence DECIMAL(5,2),  -- 0-100
    agreement_level DECIMAL(3,2),       -- 0-1 (동의 비율)

    avg_confidence DECIMAL(5,2),
    total_cost DECIMAL(10,6),
    total_latency_ms INTEGER,

    recommendation TEXT,
    created_at TIMESTAMP DEFAULT NOW(),

    INDEX idx_stock_code (stock_code),
    INDEX idx_created_at (created_at DESC),
    FOREIGN KEY (stock_code) REFERENCES stocks(code),
    FOREIGN KEY (claude_analysis_id) REFERENCES llm_analyses(id),
    FOREIGN KEY (gpt4_analysis_id) REFERENCES llm_analyses(id),
    FOREIGN KEY (gemini_analysis_id) REFERENCES llm_analyses(id),
    FOREIGN KEY (grok_analysis_id) REFERENCES llm_analyses(id)
);
```

#### 2.2.11 llm_performance (LLM 성능 지표)

```sql
CREATE TABLE llm_performance (
    id SERIAL PRIMARY KEY,
    llm_model VARCHAR(50) UNIQUE NOT NULL,  -- 'claude', 'gpt4', 'gemini', 'grok'

    total_requests INTEGER DEFAULT 0,
    total_tokens INTEGER DEFAULT 0,
    total_cost DECIMAL(10,4) DEFAULT 0.0,

    avg_latency_ms DECIMAL(8,2),
    success_rate DECIMAL(5,4),          -- 0-1

    correct_predictions INTEGER DEFAULT 0,
    total_predictions INTEGER DEFAULT 0,
    accuracy DECIMAL(5,4),              -- 0-1 (실제 결과와 비교 시)

    buy_count INTEGER DEFAULT 0,
    sell_count INTEGER DEFAULT 0,
    hold_count INTEGER DEFAULT 0,

    last_used_at TIMESTAMP,
    updated_at TIMESTAMP DEFAULT NOW(),

    INDEX idx_accuracy (accuracy DESC)
);
```

#### 2.2.12 data_collection_logs (데이터 수집 로그)

```sql
CREATE TABLE data_collection_logs (
    id SERIAL PRIMARY KEY,
    collector_type VARCHAR(50) NOT NULL,  -- 'kis', 'yahoo', 'dart', 'news'
    action VARCHAR(100),
    target_code VARCHAR(20),
    target_name VARCHAR(100),

    success BOOLEAN DEFAULT TRUE,
    records_collected INTEGER DEFAULT 0,
    error_message TEXT,

    metadata JSONB,
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    duration_ms INTEGER,
    created_at TIMESTAMP DEFAULT NOW(),

    INDEX idx_collector_type (collector_type),
    INDEX idx_target_code (target_code),
    INDEX idx_created_at (created_at DESC)
);
```

#### 2.2.13 social_media_mentions (소셜 미디어 종목 멘션)

```sql
CREATE TABLE social_media_mentions (
    id SERIAL PRIMARY KEY,

    -- 소스 정보
    source VARCHAR(50) NOT NULL,        -- 'wallstreetbets', 'stocktwits'
    platform VARCHAR(50),               -- 'reddit', 'twitter', 'stocktwits'

    -- 종목 정보
    ticker VARCHAR(20) NOT NULL,        -- 주식 티커 ('TSLA', 'AAPL', etc.)
    stock_code VARCHAR(10),             -- 한국 종목 코드 (매핑용)

    -- 멘션 데이터
    mention_count INTEGER DEFAULT 1,
    rank INTEGER,                       -- 순위 (1 = 가장 많이 언급됨)

    -- 감성 분석
    sentiment VARCHAR(20),              -- 'BULLISH', 'BEARISH', 'NEUTRAL'
    sentiment_score DECIMAL(5,2),       -- -1.0 ~ 1.0
    bullish_ratio DECIMAL(5,2),         -- 0.0 ~ 1.0 (긍정 비율)

    -- 영향력 지표
    impact_score DECIMAL(10,2),
    comment_count INTEGER,
    upvote_count INTEGER,

    -- 원본 데이터
    raw_data JSONB,

    -- 메타데이터
    data_date TIMESTAMP WITH TIME ZONE,
    collected_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    INDEX idx_source (source),
    INDEX idx_ticker (ticker),
    INDEX idx_rank (rank ASC),
    INDEX idx_data_date (data_date DESC),
    INDEX idx_created_at (created_at DESC)
);
```

#### 2.2.14 social_influencer_posts (인플루언서 포스트)

```sql
CREATE TABLE social_influencer_posts (
    id SERIAL PRIMARY KEY,

    -- 인플루언서 정보
    username VARCHAR(100) NOT NULL,     -- 'elonmusk', 'WarrenBuffett', etc.
    platform VARCHAR(50) NOT NULL,      -- 'twitter', 'reddit'

    -- 포스트 정보
    post_id VARCHAR(100) UNIQUE,        -- 원본 포스트 ID
    post_url VARCHAR(500),
    post_text TEXT,

    -- 언급된 종목
    mentioned_tickers JSONB,            -- ['TSLA', 'DOGE', ...]

    -- 감성 분석
    sentiment VARCHAR(20),              -- 'POSITIVE', 'NEGATIVE', 'NEUTRAL'
    sentiment_score DECIMAL(5,2),

    -- 영향력 지표
    like_count INTEGER DEFAULT 0,
    retweet_count INTEGER DEFAULT 0,
    reply_count INTEGER DEFAULT 0,
    impact_score DECIMAL(10,2),

    -- 메타데이터
    posted_at TIMESTAMP WITH TIME ZONE,
    collected_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    INDEX idx_username (username),
    INDEX idx_platform (platform),
    INDEX idx_posted_at (posted_at DESC),
    INDEX idx_created_at (created_at DESC)
);
```

### 2.3 인덱스 전략

| 테이블 | 인덱스 | 이유 |
|--------|--------|------|
| stock_prices | (stock_code, date DESC) | 종목별 최신 가격 조회 |
| financials | (stock_code, year DESC) | 종목별 최신 재무제표 |
| stock_news | (published_at DESC) | 최신 뉴스 조회 |
| recommendations | (score DESC) | 추천 종목 정렬 |

---

## 3. API 설계

### 3.1 RESTful API 명세

**Base URL**: `https://api.stockintel.com/v1`

#### 3.1.1 시장 현황 API

**GET /market/overview**

응답 예시:
```json
{
  "status": "success",
  "data": {
    "kospi": {
      "index": 2530.50,
      "change": 30.20,
      "change_rate": 1.21,
      "volume": 450000000
    },
    "kosdaq": {
      "index": 850.20,
      "change": -4.30,
      "change_rate": -0.50
    },
    "us_markets": {
      "sp500": {
        "close": 4550.30,
        "change_rate": -1.3,
        "above_ma_20": false,
        "signal": "BEARISH"
      },
      "nasdaq": {
        "close": 14200.30,
        "change_rate": -0.8
      }
    },
    "timestamp": "2025-11-21T15:30:00+09:00"
  }
}
```

#### 3.1.2 종목 조회 API

**GET /stocks/{code}**

Path Parameters:
- `code`: 종목코드 (예: '005930')

Query Parameters:
- `include_financials`: boolean (default: false)
- `include_news`: boolean (default: false)

응답 예시:
```json
{
  "status": "success",
  "data": {
    "code": "005930",
    "name": "삼성전자",
    "sector": "IT/반도체",
    "market": "KOSPI",
    "current_price": 75000,
    "change_rate": 2.5,
    "market_cap": 445000000000000,
    "volume": 15234567,
    "price_52w_high": 86000,
    "price_52w_low": 60000,
    "foreign_ownership": 52.3,
    "technical_indicators": {
      "ma_5": 74800,
      "ma_20": 73500,
      "ma_60": 71000,
      "rsi_14": 65,
      "macd": 120,
      "macd_signal": 100
    },
    "financials": {
      "per": 15.2,
      "pbr": 1.8,
      "roe": 12.5,
      "debt_ratio": 45,
      "dividend_yield": 2.5
    },
    "data_sources": {
      "price": "KIS_API",
      "financials": "DART",
      "verified": true
    },
    "timestamp": "2025-11-21T15:30:00+09:00"
  }
}
```

#### 3.1.3 추천 종목 API

**GET /recommendations**

Query Parameters:
- `risk_level`: 'LOW' | 'MEDIUM' | 'HIGH' (optional)
- `sector`: string (optional)
- `min_score`: integer (0-100, default: 60)
- `limit`: integer (default: 10)

응답 예시:
```json
{
  "status": "success",
  "data": {
    "recommendations": [
      {
        "stock": {
          "code": "005930",
          "name": "삼성전자",
          "current_price": 75000,
          "sector": "IT/반도체"
        },
        "score": 85,
        "risk_level": "LOW",
        "reasons": [
          "시가총액 445조원으로 국내 최대 대형주",
          "외국인 보유 비율 52%로 기관의 신뢰 높음",
          "연간 배당수익률 2.5%로 안정적 배당"
        ],
        "expected_return_1m": 3.5,
        "max_drawdown": -8.0,
        "us_correlation": 0.78,
        "us_signal": "BULLISH"
      }
    ],
    "total": 15,
    "us_market_status": {
      "sp500_signal": "BULLISH",
      "recommendation": "한국 주식 매수 포지션 유지"
    },
    "generated_at": "2025-11-21T09:00:00+09:00"
  }
}
```

#### 3.1.4 차트 이미지 분석 API

**POST /chart/analyze**

Request:
```json
{
  "image": "base64_encoded_image_data",
  "analysis_type": "full"  // 'ocr_only', 'pattern_only', 'full'
}
```

응답 예시:
```json
{
  "status": "success",
  "data": {
    "ocr_result": {
      "current_price": 75000,
      "ma_5": 74800,
      "ma_20": 73500,
      "ma_60": 71000,
      "rsi": 65,
      "volume": 15234567,
      "confidence": 0.92
    },
    "ai_analysis": {
      "trend": "상승",
      "confidence": 0.85,
      "support_line": 74000,
      "resistance_line": 76000,
      "golden_cross": true,
      "recommendation": "매수 관망 (저항선 돌파 시 매수)",
      "risk_level": "MEDIUM",
      "explanation": "현재 5일 이동평균선이 20일선을 상향 돌파하여 골든크로스가 발생했습니다. 거래량도 평균 대비 150% 증가하여 매수세가 강합니다. 다만 저항선 76,000원을 돌파하는지 확인이 필요합니다."
    },
    "processing_time_ms": 3200,
    "credits_used": 1
  }
}
```

#### 3.1.5 백테스트 결과 조회 API

**GET /backtest/results**

Query Parameters:
- `strategy_name`: string (optional)
- `min_sharpe_ratio`: float (optional)
- `limit`: integer (default: 10)

응답 예시:
```json
{
  "status": "success",
  "data": {
    "results": [
      {
        "strategy_name": "SP500_MA_20_Strategy",
        "description": "S&P 500 20일 이동평균선 기반 한국 주식 매매",
        "period": {
          "start": "2018-01-01",
          "end": "2023-12-31"
        },
        "performance": {
          "total_return": 285.5,
          "cagr": 12.3,
          "mdd": -15.2,
          "sharpe_ratio": 1.8,
          "win_rate": 58,
          "total_trades": 47
        },
        "benchmark": {
          "name": "KOSPI",
          "total_return": 120.0,
          "mdd": -35.0
        },
        "parameters": {
          "ma_period": 20,
          "threshold": 0
        },
        "created_at": "2025-11-21T00:00:00+09:00"
      }
    ]
  }
}
```

#### 3.1.6 Multi-LLM 분석 API

**POST /llm/analyze-signal/{code}**

종목 코드로 Multi-LLM 종합 분석 실행 (데이터 자동 수집 + 4-Agent 병렬 분석)

Path Parameters:
- `code`: 종목코드 (예: '005930')

응답 예시:
```json
{
  "status": "success",
  "data": {
    "consensus_id": 123,
    "stock_code": "005930",
    "stock_name": "삼성전자",
    "analysis_type": "combined_signal",
    "individual_results": {
      "claude": {
        "success": true,
        "decision": "BUY",
        "confidence": 85.5,
        "tokens_used": 1250,
        "cost": 0.0125,
        "latency_ms": 1420
      },
      "gpt4": {
        "success": true,
        "decision": "BUY",
        "confidence": 78.2,
        "tokens_used": 980,
        "cost": 0.0196,
        "latency_ms": 1150
      },
      "gemini": {
        "success": true,
        "decision": "HOLD",
        "confidence": 62.0,
        "tokens_used": 1100,
        "cost": 0.0033,
        "latency_ms": 980
      },
      "grok": {
        "success": true,
        "decision": "BUY",
        "confidence": 72.8,
        "tokens_used": 1050,
        "cost": 0.0105,
        "latency_ms": 1230
      }
    },
    "consensus": {
      "decision": "BUY",
      "confidence": 78.6,
      "agreement_level": 0.75,
      "strength": "STRONG",
      "votes": {
        "buy": 3,
        "sell": 0,
        "hold": 1
      },
      "successful_models": 4,
      "total_models": 4
    },
    "total_duration_ms": 1520,
    "timestamp": "2025-11-22T10:30:00+09:00"
  }
}
```

**GET /llm/consensus/{code}**

종목의 LLM 합의 결과 이력 조회

Query Parameters:
- `limit`: 조회 개수 (default: 10)
- `analysis_type`: 분석 유형 필터 (옵션)

**GET /llm/performance**

LLM 모델별 성능 지표 조회

Query Parameters:
- `model_name`: 특정 모델 필터 (claude, gpt4, gemini, grok) - 옵션

응답 예시:
```json
{
  "status": "success",
  "data": {
    "models": [
      {
        "model": "claude",
        "total_requests": 1250,
        "total_tokens": 1563000,
        "total_cost": 15.63,
        "avg_latency_ms": 1345.2,
        "success_rate": 99.2,
        "accuracy": 67.5,
        "decisions": {
          "buy": 520,
          "sell": 380,
          "hold": 350
        },
        "last_used": "2025-11-22T10:30:00+09:00"
      },
      {
        "model": "gpt4",
        "total_requests": 1250,
        "total_tokens": 1225000,
        "total_cost": 24.50,
        "avg_latency_ms": 1180.5,
        "success_rate": 98.8,
        "accuracy": 65.2,
        "decisions": {
          "buy": 490,
          "sell": 420,
          "hold": 340
        }
      }
    ],
    "total_models": 4
  }
}
```

**GET /llm/history/{code}**

종목의 LLM 분석 이력 조회

Query Parameters:
- `limit`: 조회 개수 (default: 20)
- `model_name`: 모델 필터 (옵션)

#### 3.1.7 소셜 미디어 분석 API

**POST /social/collect**

소셜 미디어 데이터 수집 (WallStreetBets + StockTwits)

응답 예시:
```json
{
  "status": "success",
  "data": {
    "wallstreetbets_mentions": 50,
    "stocktwits_mentions": 20,
    "total_collected": 70,
    "timestamp": "2025-11-22T10:00:00+09:00"
  }
}
```

**GET /social/wallstreetbets/trending**

WallStreetBets 트렌딩 주식 조회

Query Parameters:
- `limit`: 조회 개수 (default: 20)

응답 예시:
```json
{
  "status": "success",
  "data": {
    "trending_stocks": [
      {
        "rank": 1,
        "ticker": "NVDA",
        "mention_count": 1250,
        "sentiment": "BULLISH",
        "sentiment_score": 0.75,
        "data_date": "2025-11-22T00:00:00+09:00"
      },
      {
        "rank": 2,
        "ticker": "TSLA",
        "mention_count": 980,
        "sentiment": "BULLISH",
        "sentiment_score": 0.62,
        "data_date": "2025-11-22T00:00:00+09:00"
      }
    ],
    "total": 20,
    "source": "r/wallstreetbets",
    "timestamp": "2025-11-22T10:00:00+09:00"
  }
}
```

**GET /social/stocktwits/{ticker}**

특정 종목의 StockTwits 투자자 감성 조회

Path Parameters:
- `ticker`: 주식 티커 (예: 'TSLA', 'AAPL')

응답 예시:
```json
{
  "status": "success",
  "data": {
    "ticker": "TSLA",
    "sentiment": "BULLISH",
    "sentiment_score": 0.45,
    "bullish_ratio": 0.725,
    "mention_count": 345,
    "sentiment_breakdown": {
      "bullish": 250,
      "bearish": 95,
      "neutral": 0
    },
    "data_date": "2025-11-22T10:00:00+09:00",
    "collected_at": "2025-11-22T10:15:30+09:00"
  }
}
```

**GET /social/trending-combined**

통합 소셜 미디어 트렌드 (WSB + StockTwits)

Query Parameters:
- `limit`: 조회 개수 (default: 30)

응답 예시:
```json
{
  "status": "success",
  "data": {
    "trending_stocks": [
      {
        "ticker": "NVDA",
        "wsb_rank": 1,
        "wsb_mentions": 1250,
        "wsb_sentiment": "BULLISH",
        "stocktwits_sentiment": "BULLISH",
        "stocktwits_bullish_ratio": 0.78,
        "combined_score": 1328.0
      }
    ],
    "total": 30,
    "sources": ["wallstreetbets", "stocktwits"],
    "timestamp": "2025-11-22T10:00:00+09:00"
  }
}
```

### 3.2 에러 응답 형식

```json
{
  "status": "error",
  "error": {
    "code": "STOCK_NOT_FOUND",
    "message": "종목을 찾을 수 없습니다.",
    "details": {
      "stock_code": "999999"
    }
  },
  "timestamp": "2025-11-21T15:30:00+09:00"
}
```

**에러 코드 정의**:
| 코드 | HTTP Status | 설명 |
|------|-------------|------|
| STOCK_NOT_FOUND | 404 | 종목이 존재하지 않음 |
| API_RATE_LIMIT | 429 | API 호출 한도 초과 |
| INVALID_PARAMETER | 400 | 잘못된 요청 파라미터 |
| DATA_VERIFICATION_FAILED | 422 | 데이터 검증 실패 |
| EXTERNAL_API_ERROR | 502 | 외부 API 오류 |
| INTERNAL_ERROR | 500 | 내부 서버 오류 |

---

## 4. 클래스 다이어그램

### 4.1 데이터 수집기 (Collectors)

```python
# collectors/base.py
from abc import ABC, abstractmethod
from typing import Dict, Any

class BaseCollector(ABC):
    """모든 데이터 수집기의 추상 클래스"""

    def __init__(self, api_key: str = None):
        self.api_key = api_key

    @abstractmethod
    async def collect(self, **kwargs) -> Dict[str, Any]:
        """데이터 수집 메서드"""
        pass

    @abstractmethod
    def validate_data(self, data: Dict) -> bool:
        """데이터 검증"""
        pass

    def add_metadata(self, data: Dict) -> Dict:
        """데이터에 메타데이터 추가"""
        return {
            **data,
            "source": self.__class__.__name__,
            "collected_at": datetime.now().isoformat(),
            "verified": self.validate_data(data)
        }
```

```python
# collectors/kis_collector.py
import requests
from .base import BaseCollector

class KISCollector(BaseCollector):
    """한국투자증권 API 데이터 수집기"""

    def __init__(self, app_key: str, app_secret: str):
        super().__init__()
        self.app_key = app_key
        self.app_secret = app_secret
        self.base_url = "https://openapi.koreainvestment.com:9443"
        self.access_token = None

    async def get_access_token(self) -> str:
        """OAuth 토큰 발급"""
        url = f"{self.base_url}/oauth2/tokenP"
        data = {
            "grant_type": "client_credentials",
            "appkey": self.app_key,
            "appsecret": self.app_secret
        }
        response = requests.post(url, json=data)
        response.raise_for_status()
        self.access_token = response.json()['access_token']
        return self.access_token

    async def collect(self, stock_code: str) -> Dict[str, Any]:
        """실시간 주식 시세 조회"""
        if not self.access_token:
            await self.get_access_token()

        url = f"{self.base_url}/uapi/domestic-stock/v1/quotations/inquire-price"
        headers = {
            "authorization": f"Bearer {self.access_token}",
            "appkey": self.app_key,
            "appsecret": self.app_secret,
            "tr_id": "FHKST01010100"
        }
        params = {
            "FID_COND_MRKT_DIV_CODE": "J",
            "FID_INPUT_ISCD": stock_code
        }

        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()['output']

        # 데이터 정규화
        normalized = {
            'code': stock_code,
            'name': data['hts_kor_isnm'],
            'current_price': int(data['stck_prpr']),
            'open': int(data['stck_oprc']),
            'high': int(data['stck_hgpr']),
            'low': int(data['stck_lwpr']),
            'volume': int(data['acml_vol']),
            'change_rate': float(data['prdy_ctrt']),
        }

        return self.add_metadata(normalized)

    def validate_data(self, data: Dict) -> bool:
        """데이터 유효성 검증"""
        required_fields = ['code', 'name', 'current_price', 'volume']
        return all(field in data for field in required_fields)
```

```python
# collectors/yahoo_collector.py
import yfinance as yf
from .base import BaseCollector

class YahooCollector(BaseCollector):
    """Yahoo Finance 미국 지수 수집기"""

    async def collect(self, symbol: str = "^GSPC") -> Dict[str, Any]:
        """S&P 500 데이터 조회"""
        ticker = yf.Ticker(symbol)
        hist = ticker.history(period="3mo")  # 최근 3개월

        latest = hist.iloc[-1]
        ma_20 = hist['Close'].rolling(window=20).mean().iloc[-1]
        ma_60 = hist['Close'].rolling(window=60).mean().iloc[-1]

        data = {
            'symbol': symbol,
            'close': float(latest['Close']),
            'volume': int(latest['Volume']),
            'ma_20': float(ma_20),
            'ma_60': float(ma_60),
            'above_ma': latest['Close'] > ma_20,
            'date': latest.name.strftime('%Y-%m-%d')
        }

        return self.add_metadata(data)

    def validate_data(self, data: Dict) -> bool:
        return 'close' in data and data['close'] > 0
```

### 4.2 분석기 (Analyzers)

```python
# analyzers/technical_analyzer.py
import pandas as pd
import ta

class TechnicalAnalyzer:
    """기술적 지표 계산"""

    def calculate_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        모든 기술적 지표 계산

        Args:
            df: OHLCV 데이터프레임 (columns: open, high, low, close, volume)

        Returns:
            지표가 추가된 데이터프레임
        """
        # 이동평균선
        df['ma_5'] = df['close'].rolling(window=5).mean()
        df['ma_20'] = df['close'].rolling(window=20).mean()
        df['ma_60'] = df['close'].rolling(window=60).mean()
        df['ma_120'] = df['close'].rolling(window=120).mean()

        # RSI
        df['rsi'] = ta.momentum.RSIIndicator(df['close'], window=14).rsi()

        # MACD
        macd = ta.trend.MACD(df['close'])
        df['macd'] = macd.macd()
        df['macd_signal'] = macd.macd_signal()
        df['macd_diff'] = macd.macd_diff()

        # 볼린저 밴드
        bollinger = ta.volatility.BollingerBands(df['close'])
        df['bb_upper'] = bollinger.bollinger_hband()
        df['bb_middle'] = bollinger.bollinger_mavg()
        df['bb_lower'] = bollinger.bollinger_lband()

        # 변동성 (표준편차)
        df['volatility_20d'] = df['close'].pct_change().rolling(20).std() * 100

        return df

    def detect_signals(self, df: pd.DataFrame) -> Dict[str, Any]:
        """매매 신호 탐지"""
        latest = df.iloc[-1]
        prev = df.iloc[-2]

        signals = {
            'golden_cross': False,
            'dead_cross': False,
            'rsi_oversold': False,
            'rsi_overbought': False,
            'above_ma_20': False,
            'macd_bullish': False
        }

        # 골든크로스/데드크로스
        if latest['ma_5'] > latest['ma_20'] and prev['ma_5'] <= prev['ma_20']:
            signals['golden_cross'] = True
        elif latest['ma_5'] < latest['ma_20'] and prev['ma_5'] >= prev['ma_20']:
            signals['dead_cross'] = True

        # RSI
        if latest['rsi'] < 30:
            signals['rsi_oversold'] = True
        elif latest['rsi'] > 70:
            signals['rsi_overbought'] = True

        # 이평선 위
        signals['above_ma_20'] = latest['close'] > latest['ma_20']

        # MACD
        if latest['macd'] > latest['macd_signal']:
            signals['macd_bullish'] = True

        return signals
```

### 4.3 추천 엔진 (Recommenders)

```python
# recommenders/beginner_recommender.py
from typing import List
from sqlalchemy.orm import Session
from models import Stock, StockPrice, Financial
from schemas import RecommendationResponse

class BeginnerRecommender:
    """초보자 맞춤 종목 추천 엔진"""

    def __init__(self, db: Session):
        self.db = db

    def filter_stocks(
        self,
        risk_level: str = "LOW"
    ) -> List[Stock]:
        """종목 필터링"""

        query = self.db.query(Stock).join(StockPrice).join(Financial)

        # 기본 필터링
        query = query.filter(
            Stock.market_cap >= 1_000_000_000_000,  # 1조 이상
            StockPrice.trading_value >= 10_000_000_000,  # 일평균 거래대금 100억 이상
            Financial.debt_ratio <= 200,  # 부채비율 200% 이하
            Financial.roe >= 10,  # ROE 10% 이상
            StockPrice.foreign_ownership >= 20  # 외국인 보유 20% 이상
        )

        # 리스크 수준별 추가 필터링
        if risk_level == "LOW":
            query = query.filter(
                Stock.market_cap >= 10_000_000_000_000,  # 10조 이상
                Financial.dividend_yield >= 2.0  # 배당 2% 이상
            )

        return query.all()

    def calculate_score(self, stock: Stock) -> int:
        """초보자 적합도 점수 계산 (0-100)"""
        score = 0

        # 시가총액 (30점)
        if stock.market_cap > 10_000_000_000_000:
            score += 30
        elif stock.market_cap > 5_000_000_000_000:
            score += 20
        else:
            score += 10

        # 변동성 (20점)
        if stock.latest_price.volatility_20d < 1.5:
            score += 20
        elif stock.latest_price.volatility_20d < 2.5:
            score += 10

        # ROE (20점)
        if stock.latest_financial.roe > 15:
            score += 20
        elif stock.latest_financial.roe > 10:
            score += 10

        # 배당수익률 (15점)
        if stock.latest_financial.dividend_yield > 3:
            score += 15
        elif stock.latest_financial.dividend_yield > 2:
            score += 10

        # 외국인 보유 (15점)
        if stock.latest_price.foreign_ownership > 30:
            score += 15
        elif stock.latest_price.foreign_ownership > 20:
            score += 10

        return min(score, 100)

    def generate_reasons(self, stock: Stock, score: int) -> List[str]:
        """추천 이유 생성"""
        reasons = []

        # 시가총액
        market_cap_trillion = stock.market_cap / 1_000_000_000_000
        if market_cap_trillion >= 10:
            reasons.append(f"시가총액 {market_cap_trillion:.0f}조원으로 초대형 안정주")

        # 외국인 보유
        if stock.latest_price.foreign_ownership > 30:
            reasons.append(f"외국인 보유 비율 {stock.latest_price.foreign_ownership:.1f}%로 기관 신뢰 높음")

        # 배당
        if stock.latest_financial.dividend_yield > 2:
            reasons.append(f"연간 배당수익률 {stock.latest_financial.dividend_yield:.1f}%로 안정적 배당")

        # ROE
        if stock.latest_financial.roe > 15:
            reasons.append(f"ROE {stock.latest_financial.roe:.1f}%로 우수한 자기자본이익률")

        # 섹터
        reasons.append(f"{stock.sector} 섹터의 대표주")

        return reasons[:3]  # 상위 3개만

    async def recommend(
        self,
        risk_level: str = "LOW",
        limit: int = 10
    ) -> List[RecommendationResponse]:
        """추천 종목 생성"""

        # 1. 필터링
        filtered_stocks = self.filter_stocks(risk_level)

        # 2. 점수 계산
        recommendations = []
        for stock in filtered_stocks:
            score = self.calculate_score(stock)
            reasons = self.generate_reasons(stock, score)

            recommendations.append({
                'stock': stock,
                'score': score,
                'reasons': reasons,
                'risk_level': risk_level
            })

        # 3. 점수 순 정렬
        recommendations.sort(key=lambda x: x['score'], reverse=True)

        return recommendations[:limit]
```

---

## 5. 데이터 플로우

### 5.1 실시간 주가 수집 플로우

```
09:00 (장 시작)
    ↓
[AWS Lambda] 실시간 수집 시작
    ↓
[KISCollector.collect()] ← API 호출 (10초마다)
    ↓
[Redis Cache] 임시 저장 (TTL: 30초)
    ↓
[DataValidator] 데이터 검증
    ↓
    ├─ 검증 성공 → [PostgreSQL] 저장
    └─ 검증 실패 → [CloudWatch Logs] 에러 기록
                  → [Slack/Email] 알림
```

### 5.2 추천 종목 생성 플로우

```
매일 09:00
    ↓
[AWS Lambda] 추천 종목 생성 트리거
    ↓
┌────────────────────┐
│ BeginnerRecommender│
├────────────────────┤
│ 1. filter_stocks() │ ← PostgreSQL (stocks, prices, financials)
│ 2. calculate_score()│
│ 3. generate_reasons()│
└────────────────────┘
    ↓
[US Market Analyzer]
    ↓
    ├─ S&P 500 > MA_20 → signal = BULLISH
    └─ S&P 500 < MA_20 → signal = BEARISH
    ↓
[Recommendations Table] 저장
    ↓
[Redis Cache] 캐싱 (TTL: 24시간)
    ↓
[FastAPI] /api/v1/recommendations 응답 준비
```

### 5.3 차트 이미지 분석 플로우

```
[User] 차트 이미지 업로드
    ↓
[FastAPI] POST /api/v1/chart/analyze
    ↓
[S3] 이미지 업로드 (임시)
    ↓
    ┌────────────────┬────────────────┐
    ↓                ↓                ↓
[Upstage OCR]  [CLOVA AI]   [OpenCV]
텍스트 추출      패턴 분석     캔들 탐지
    ↓                ↓                ↓
    └────────────────┴────────────────┘
                      ↓
            [결과 통합 및 검증]
                      ↓
            [PostgreSQL] 로그 저장
                      ↓
            [FastAPI] 응답 반환
                      ↓
            [S3] 이미지 삭제 (24시간 후)
```

---

## 6. 모듈별 상세 설계

### 6.1 백테스팅 엔진

```python
# analyzers/backtest_engine.py
import backtrader as bt
from typing import Dict, Any

class SP500MAStrategy(bt.Strategy):
    """S&P 500 이동평균선 전략"""

    params = (
        ('ma_period', 20),
    )

    def __init__(self):
        # S&P 500 데이터
        self.sp500_ma = bt.indicators.SMA(
            self.datas[1].close,
            period=self.params.ma_period
        )

        # 매매 신호
        self.signal = self.datas[1].close > self.sp500_ma

    def next(self):
        # S&P 500이 이평선 위 → 매수
        if self.signal[0] and not self.position:
            self.buy()

        # S&P 500이 이평선 아래 → 매도
        elif not self.signal[0] and self.position:
            self.close()


class BacktestEngine:
    """백테스팅 엔진"""

    def run(
        self,
        strategy_class: type,
        stock_data: pd.DataFrame,
        us_data: pd.DataFrame,
        initial_cash: float = 10_000_000
    ) -> Dict[str, Any]:
        """
        백테스팅 실행

        Args:
            strategy_class: 전략 클래스
            stock_data: 한국 주식 데이터
            us_data: 미국 지수 데이터
            initial_cash: 초기 자본

        Returns:
            백테스팅 결과
        """
        cerebro = bt.Cerebro()

        # 전략 추가
        cerebro.addstrategy(strategy_class)

        # 데이터 추가
        data_kr = bt.feeds.PandasData(dataname=stock_data)
        data_us = bt.feeds.PandasData(dataname=us_data)

        cerebro.adddata(data_kr)
        cerebro.adddata(data_us)

        # 초기 설정
        cerebro.broker.setcash(initial_cash)
        cerebro.broker.setcommission(commission=0.0025)  # 수수료 0.25%

        # 분석기 추가
        cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='sharpe')
        cerebro.addanalyzer(bt.analyzers.DrawDown, _name='drawdown')
        cerebro.addanalyzer(bt.analyzers.Returns, _name='returns')
        cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name='trades')

        # 실행
        results = cerebro.run()
        strat = results[0]

        # 결과 추출
        final_value = cerebro.broker.getvalue()
        total_return = ((final_value - initial_cash) / initial_cash) * 100

        return {
            'initial_capital': initial_cash,
            'final_capital': final_value,
            'total_return': total_return,
            'sharpe_ratio': strat.analyzers.sharpe.get_analysis().get('sharperatio', 0),
            'max_drawdown': strat.analyzers.drawdown.get_analysis()['max']['drawdown'],
            'total_trades': strat.analyzers.trades.get_analysis()['total']['total'],
            'win_rate': self._calculate_win_rate(strat.analyzers.trades.get_analysis())
        }

    def _calculate_win_rate(self, trade_analysis: Dict) -> float:
        """승률 계산"""
        won = trade_analysis['won']['total']
        total = trade_analysis['total']['total']
        return (won / total * 100) if total > 0 else 0
```

### 6.2 알림 시스템

```python
# utils/notification.py
import requests
import json
from typing import Dict

class KakaoNotifier:
    """카카오톡 알림"""

    def __init__(self, access_token: str):
        self.access_token = access_token
        self.base_url = "https://kapi.kakao.com"

    def send_alert(
        self,
        alert_type: str,
        stock_name: str,
        message: str,
        data: Dict = None
    ):
        """알림 전송"""

        # 알림 템플릿
        templates = {
            'target_price': f"🎯 목표가 도달\n\n{stock_name}\n{message}",
            'surge': f"📈 급등 알림\n\n{stock_name}\n{message}",
            'plunge': f"📉 급락 알림\n\n{stock_name}\n{message}",
            'disclosure': f"📢 중요 공시\n\n{stock_name}\n{message}",
            'us_signal': f"🇺🇸 미국 시장 신호\n\n{message}",
            'stop_loss': f"⛔ 손절매 실행\n\n{stock_name}\n{message}"
        }

        text = templates.get(alert_type, message)

        url = f"{self.base_url}/v2/api/talk/memo/default/send"
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/x-www-form-urlencoded"
        }

        template = {
            "object_type": "text",
            "text": text,
            "link": {
                "web_url": "https://finance.naver.com",
                "mobile_web_url": "https://finance.naver.com"
            }
        }

        if data:
            template["button_title"] = "자세히 보기"

        payload = {
            "template_object": json.dumps(template)
        }

        response = requests.post(url, headers=headers, data=payload)
        return response.status_code == 200
```

---

## 7. 배포 아키텍처

### 7.1 AWS 인프라 구성

```
┌──────────────────────────────────────────────────────┐
│                    Internet                          │
└──────────────────────────────────────────────────────┘
                          │
                          ↓
┌──────────────────────────────────────────────────────┐
│              Route 53 (DNS)                          │
│           stockintel.com                             │
└──────────────────────────────────────────────────────┘
                          │
                          ↓
┌──────────────────────────────────────────────────────┐
│     CloudFront (CDN) + WAF                           │
│     - HTTPS 인증서 (ACM)                              │
│     - DDoS 방어                                       │
└──────────────────────────────────────────────────────┘
                          │
        ┌─────────────────┼─────────────────┐
        ↓                 ↓                 ↓
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│ Application  │  │   API        │  │  Static      │
│ Load Balancer│  │   Gateway    │  │  Assets      │
└──────────────┘  └──────────────┘  └──────────────┘
        │                 │                 │
        ↓                 ↓                 ↓
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│ EC2 Instance │  │ FastAPI      │  │     S3       │
│ (Streamlit)  │  │ (Container)  │  │ (Images)     │
│  t2.micro    │  │  ECS Fargate │  │              │
└──────────────┘  └──────────────┘  └──────────────┘
                          │
        ┌─────────────────┼─────────────────┐
        ↓                 ↓                 ↓
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│ RDS          │  │ ElastiCache  │  │  Lambda      │
│ PostgreSQL   │  │ (Redis)      │  │ Functions    │
│  db.t3.micro │  │              │  │              │
└──────────────┘  └──────────────┘  └──────────────┘
```

### 7.2 Docker 구성

**docker-compose.yml**:
```yaml
version: '3.8'

services:
  api:
    build: ./app
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:pass@db:5432/stockdb
      - REDIS_URL=redis://cache:6379/0
      - KIS_APP_KEY=${KIS_APP_KEY}
      - KIS_APP_SECRET=${KIS_APP_SECRET}
    depends_on:
      - db
      - cache

  dashboard:
    build: ./dashboard
    ports:
      - "8501:8501"
    environment:
      - API_URL=http://api:8000
    depends_on:
      - api

  db:
    image: postgres:15-alpine
    volumes:
      - postgres_data:/var/lib/postgresql/data
    environment:
      - POSTGRES_USER=stockuser
      - POSTGRES_PASSWORD=stockpass
      - POSTGRES_DB=stockdb

  cache:
    image: redis:7-alpine
    ports:
      - "6379:6379"

volumes:
  postgres_data:
```

### 7.3 CI/CD 파이프라인

```yaml
# .github/workflows/deploy.yml
name: Deploy to AWS

on:
  push:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run tests
        run: |
          pip install -r requirements.txt
          pytest tests/

  deploy:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v2
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: ap-northeast-2

      - name: Login to Amazon ECR
        run: |
          aws ecr get-login-password --region ap-northeast-2 | \
          docker login --username AWS --password-stdin ${{ secrets.ECR_REGISTRY }}

      - name: Build and push Docker image
        run: |
          docker build -t stock-api:latest .
          docker tag stock-api:latest ${{ secrets.ECR_REGISTRY }}/stock-api:latest
          docker push ${{ secrets.ECR_REGISTRY }}/stock-api:latest

      - name: Deploy to ECS
        run: |
          aws ecs update-service --cluster stock-cluster \
            --service stock-api-service --force-new-deployment
```

---

## 8. 모니터링 및 로깅

### 8.1 로깅 전략

```python
# utils/logger.py
import logging
from pythonjsonlogger import jsonlogger

def setup_logger(name: str):
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    handler = logging.StreamHandler()
    formatter = jsonlogger.JsonFormatter(
        '%(asctime)s %(name)s %(levelname)s %(message)s'
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    return logger

# 사용 예시
logger = setup_logger('stock_api')
logger.info('Data collected', extra={
    'stock_code': '005930',
    'source': 'KIS_API',
    'latency_ms': 150
})
```

### 8.2 성능 메트릭

**CloudWatch 메트릭**:
- API 응답 시간 (p50, p95, p99)
- 데이터 수집 성공률
- 데이터 검증 실패율
- DB 쿼리 시간
- 외부 API 에러율

---

## 9. 보안 설계

### 9.1 API Key 관리

```python
# config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Database
    DATABASE_URL: str

    # External APIs
    KIS_APP_KEY: str
    KIS_APP_SECRET: str
    UPSTAGE_API_KEY: str
    CLOVA_API_KEY: str

    # AWS
    AWS_ACCESS_KEY_ID: str
    AWS_SECRET_ACCESS_KEY: str
    AWS_REGION: str = "ap-northeast-2"

    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
```

### 9.2 데이터 암호화

```python
# utils/crypto.py
from cryptography.fernet import Fernet

class DataEncryptor:
    def __init__(self, key: str):
        self.cipher = Fernet(key.encode())

    def encrypt(self, data: str) -> str:
        return self.cipher.encrypt(data.encode()).decode()

    def decrypt(self, encrypted: str) -> str:
        return self.cipher.decrypt(encrypted.encode()).decode()
```

---

## 10. 테스트 전략

### 10.1 단위 테스트

```python
# tests/test_collectors/test_kis_collector.py
import pytest
from app.collectors.kis_collector import KISCollector

@pytest.fixture
def kis_collector():
    return KISCollector(app_key="test_key", app_secret="test_secret")

@pytest.mark.asyncio
async def test_collect_stock_data(kis_collector, mock_kis_api):
    # Given
    stock_code = "005930"

    # When
    result = await kis_collector.collect(stock_code)

    # Then
    assert result['code'] == stock_code
    assert 'current_price' in result
    assert result['verified'] is True
```

### 10.2 통합 테스트

```python
# tests/test_integration/test_recommendation_flow.py
import pytest
from app.main import app
from fastapi.testclient import TestClient

client = TestClient(app)

def test_get_recommendations():
    # Given
    params = {
        "risk_level": "LOW",
        "limit": 10
    }

    # When
    response = client.get("/api/v1/recommendations", params=params)

    # Then
    assert response.status_code == 200
    data = response.json()
    assert len(data['data']['recommendations']) <= 10
    assert data['data']['recommendations'][0]['score'] > 60
```

---

## 변경 이력

| 버전 | 날짜 | 변경 내용 | 작성자 |
|------|------|-----------|--------|
| 1.0 | 2025-11-21 | 초안 작성 | AI Assistant |
| 2.0 | 2025-11-22 | Supabase 통합 및 Multi-LLM 분석 시스템 추가 | AI Assistant |
|  |  | - Supabase (PostgreSQL) 데이터베이스 통합 | |
|  |  | - Multi-LLM 레이어 추가 (Claude, GPT-4, Gemini, Grok) | |
|  |  | - LLM 분석 추적 테이블 4개 추가 (llm_analyses, llm_consensus, llm_performance, data_collection_logs) | |
|  |  | - Multi-LLM API 엔드포인트 5개 추가 | |
|  |  | - 투표 기반 합의 메커니즘 설계 | |
| 2.1 | 2025-11-22 | 소셜 미디어 데이터 수집 시스템 추가 | AI Assistant |
|  |  | - WallStreetBets 트렌딩 주식 수집 (Tradestie API) | |
|  |  | - StockTwits 종목별 투자자 감성 분석 | |
|  |  | - 소셜 미디어 테이블 2개 추가 (social_media_mentions, social_influencer_posts) | |
|  |  | - 소셜 미디어 API 엔드포인트 4개 추가 | |
|  |  | - 무료 API 기반 실시간 감성 추적 시스템 구현 | |
