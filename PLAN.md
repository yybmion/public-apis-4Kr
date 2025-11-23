# 프로젝트 계획서 (PLAN)
## 한국 주식 자동매매 지원 시스템

**프로젝트명**: Stock Intelligence System (SIS)
**버전**: 2.2
**작성일**: 2025-11-21
**최종 업데이트**: 2025-11-23
**기간**: 3개월 (12주)

> **📌 API 준비 필수!**
>
> 프로젝트 시작 전 **19개 API/데이터 소스** 확인 필요:
> - **필수 데이터 API (5개)**: KIS, DART, ECOS, FRED, BigKinds
> - **API 키 불필요 (5개)**: Yahoo Finance, Fear & Greed, SEC EDGAR, Tradestie, StockTwits
> - **선택 AI API (6개)**: Upstage, CLOVA Studio, Claude, GPT-4, Gemini, Grok
> - **선택 알림 API (3개)**: Telegram, Kakao Talk, Gmail SMTP
>
> **상세 가이드**: **`API_SUMMARY.md`** 참조 (발급 방법, 소요 시간, 비용 등)

---

## 📋 목차

1. [프로젝트 개요](#1-프로젝트-개요)
2. [3개월 상세 일정](#2-3개월-상세-일정)
3. [주차별 세부 계획](#3-주차별-세부-계획)
4. [리소스 계획](#4-리소스-계획)
5. [리스크 관리](#5-리스크-관리)
6. [품질 관리](#6-품질-관리)
7. [커뮤니케이션 계획](#7-커뮤니케이션-계획)

---

## 1. 프로젝트 개요

### 1.1 목표

**핵심 목표**:
- 초보 투자자를 위한 **신뢰할 수 있는** 데이터 기반 주식 투자 지원 시스템 구축
- 미국-한국 증시 상관성 (0.85) 활용한 **과학적** 투자 전략 제공
- **백테스팅으로 검증된** 전략만 제공하여 신뢰성 확보

**성공 기준**:
| 지표 | 목표값 | 측정 시점 |
|------|--------|----------|
| MVP 완성 | 100% | 1개월차 말 |
| 백테스팅 샤프 비율 | > 1.0 | 2개월차 말 |
| 추천 종목 승률 | > 60% | 모의투자 3주 후 |
| 시스템 가용성 | > 99% | 3개월차 |
| 사용자 만족도 | > 4.0/5.0 | 베타 테스트 종료 |

### 1.2 범위 (Scope)

**포함 (In Scope)**:
- ✅ 한국 주식 (KOSPI/KOSDAQ) 데이터 수집
- ✅ 미국 지수 (S&P 500, 나스닥, 다우존스) 연동
- ✅ 초보자 맞춤 종목 추천 시스템
- ✅ 차트 이미지 분석 (OCR + AI)
- ✅ 백테스팅 시스템
- ✅ 웹 대시보드 (Streamlit)
- ✅ 카카오톡 알림

**제외 (Out of Scope)**:
- ❌ 실제 자동매매 실행 (법적 이슈)
- ❌ 모바일 앱 개발
- ❌ 미국 주식 직접 매매
- ❌ 암호화폐 트레이딩
- ❌ 소셜 커뮤니티 기능

---

## 2. 3개월 상세 일정

### 2.1 마일스톤 타임라인

```
Week 1-4: Phase 1 (MVP 구축)
┌─────────────────────────────────────────────────────────┐
│ Week 1-2: 데이터 수집 인프라                              │
│ - KIS API, DART, Yahoo Finance 연동                     │
│ - PostgreSQL DB 구축                                    │
│ - 일일 자동 수집 스크립트                                │
│                                                         │
│ Week 3: 기술적 지표 계산                                  │
│ - 이동평균선, RSI, MACD 계산                             │
│ - S&P 500 신호 생성                                     │
│                                                         │
│ Week 4: 기본 대시보드                                     │
│ - Streamlit 메인 페이지                                 │
│ - 시장 현황 표시                                         │
│ - 종목 검색 및 상세 정보                                 │
└─────────────────────────────────────────────────────────┘
                          ↓
                    [1차 리뷰]
                          ↓

Week 5-8: Phase 2 (핵심 기능) ✅ 완료
┌─────────────────────────────────────────────────────────┐
│ Week 5-6: 초보자 추천 시스템 ✅                           │
│ - 투자 성향 분석 설문 ✅                                 │
│ - 종목 필터링 알고리즘 ✅                                │
│ - 초보자 적합도 점수 계산 ✅                             │
│ - 섹터 가이드 작성 ✅                                    │
│                                                         │
│ Week 7: 백테스팅 시스템 ✅                               │
│ - Backtrader 프레임워크 구축 ✅                         │
│ - S&P 500 이평선 전략 백테스트 (2018-2023) ✅          │
│ - 골든크로스 전략 검증 ✅                                │
│ - 결과 시각화 및 리포트 ✅                               │
│                                                         │
│ Week 8: Multi-LLM 분석 시스템 & 소셜 미디어 수집 ✅      │
│ - Supabase (PostgreSQL) 데이터베이스 통합 ✅            │
│ - 4-Agent LLM 시스템 구현 (Claude, GPT-4, Gemini, Grok) ✅│
│ - 병렬 분석 및 합의 메커니즘 (투표 기반) ✅              │
│ - 성능 추적 및 로깅 시스템 ✅                            │
│ - Multi-LLM API 엔드포인트 5개 구현 ✅                   │
│ - 소셜 미디어 수집 시스템 (WallStreetBets + StockTwits) ✅│
│ - 소셜 미디어 데이터 모델 및 수집기 구현 ✅              │
│ - 소셜 미디어 API 엔드포인트 4개 구현 ✅                 │
│ - SNS 크롤링 연구 및 실행 가능성 검증 완료 ✅           │
└─────────────────────────────────────────────────────────┘
                          ↓
                    [2차 리뷰 + 중간 발표]
                          ↓

Week 9-12: Phase 3 (완성 및 배포)
┌─────────────────────────────────────────────────────────┐
│ Week 9-10: 뉴스 감성 분석 & 알림                          │
│ - 빅카인즈 API 연동                                      │
│ - 한국어 감성 분석 모델 (BERT)                           │
│ - 뉴스 신뢰도 평가 시스템                                │
│ - 카카오톡 메시지 API 연동                               │
│                                                         │
│ Week 11: AWS 배포 & 모의투자                             │
│ - EC2 인스턴스 설정 및 배포                              │
│ - Lambda + CloudWatch 스케줄링                          │
│ - 모의투자 3주 실전 테스트 시작                          │
│                                                         │
│ Week 12: 최종 테스트 & 문서화                             │
│ - 버그 수정 및 성능 최적화                               │
│ - 사용자 가이드 작성                                     │
│ - 최종 발표 준비                                         │
└─────────────────────────────────────────────────────────┘
                          ↓
                    [최종 리뷰 + 발표]
```

### 2.2 Gantt Chart

| 작업 | W1 | W2 | W3 | W4 | W5 | W6 | W7 | W8 | W9 | W10 | W11 | W12 |
|------|----|----|----|----|----|----|----|----|----|----|-----|-----|
| **Phase 1: MVP** |
| KIS API 연동 | ██ | ██ |  |  |  |  |  |  |  |  |  |  |
| DB 구축 | ██ | ██ |  |  |  |  |  |  |  |  |  |  |
| 기술 지표 |  |  | ██ |  |  |  |  |  |  |  |  |  |
| 대시보드 |  |  |  | ██ |  |  |  |  |  |  |  |  |
| **Phase 2: 핵심** |
| 추천 시스템 |  |  |  |  | ██ | ██ |  |  |  |  |  |  |
| 백테스팅 |  |  |  |  |  |  | ██ |  |  |  |  |  |
| 차트 분석 |  |  |  |  |  |  |  | ██ |  |  |  |  |
| **Phase 3: 완성** |
| 뉴스 분석 |  |  |  |  |  |  |  |  | ██ | ██ |  |  |
| 알림 시스템 |  |  |  |  |  |  |  |  | ██ | ██ |  |  |
| AWS 배포 |  |  |  |  |  |  |  |  |  |  | ██ |  |
| 모의투자 |  |  |  |  |  |  |  |  |  |  | ██ | ██ |
| 테스트/문서화 |  |  |  |  |  |  |  |  |  |  | ░░ | ██ |

※ ██: 집중 작업, ░░: 병행 작업

---

## 3. 주차별 세부 계획

### Week 1-2: 데이터 수집 인프라 구축

#### 목표
- 한국 주식 실시간 시세 수집 시스템 구축
- 미국 지수 연동
- PostgreSQL 데이터베이스 설계 및 구축

#### 세부 작업

**Day 1-2: 환경 설정**
```bash
# 작업 리스트
- [ ] GitHub 리포지토리 생성
- [ ] Python 가상 환경 설정 (Python 3.10+)
- [ ] 필수 라이브러리 설치
- [ ] 프로젝트 디렉토리 구조 생성
- [ ] .env 파일 설정

# 명령어
git clone https://github.com/your-repo/stock-intelligence-system.git
cd stock-intelligence-system
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

**Day 3-5: 한국투자증권 KIS API 연동**
```python
# 작업 리스트
- [ ] KIS Developers 계좌 개설
- [ ] API Key 발급 (App Key, App Secret)
- [ ] OAuth 토큰 발급 코드 작성
- [ ] 실시간 시세 조회 API 연동
- [ ] 일봉 데이터 조회 API 연동
- [ ] 단위 테스트 작성

# 테스트
python -m pytest tests/test_collectors/test_kis_collector.py
```

**Day 6-8: PostgreSQL DB 구축**
```sql
-- 작업 리스트
- [ ] PostgreSQL 15 설치 (로컬 또는 Docker)
- [ ] 데이터베이스 생성 (stockdb)
- [ ] 테이블 스키마 작성 (stocks, stock_prices, financials 등)
- [ ] 인덱스 생성
- [ ] SQLAlchemy ORM 모델 작성
- [ ] DB 마이그레이션 스크립트

-- 실행
psql -U postgres
CREATE DATABASE stockdb;
\c stockdb
\i scripts/init_db.sql
```

**Day 9-10: 미국 지수 데이터 연동**
```python
# 작업 리스트
- [ ] yfinance 라이브러리로 S&P 500 데이터 수집
- [ ] 20일/60일 이동평균선 계산
- [ ] us_indices 테이블에 저장
- [ ] 데이터 검증 로직 작성

# 테스트
python scripts/test_yahoo_collector.py
```

**Day 11-14: 자동 수집 스크립트**
```python
# 작업 리스트
- [ ] 일일 데이터 수집 스크립트 (daily_collector.py)
- [ ] 실시간 수집 스크립트 (realtime_collector.py)
- [ ] 에러 핸들링 및 재시도 로직
- [ ] 로깅 시스템 구축
- [ ] cron 또는 스케줄러 설정

# 실행 (장중 10초마다)
python scripts/realtime_collector.py --interval 10
```

#### 산출물
- ✅ KIS API 연동 코드 (`app/collectors/kis_collector.py`)
- ✅ DB 스키마 (`scripts/init_db.sql`)
- ✅ 데이터 수집 스크립트 (`scripts/daily_collector.py`)
- ✅ 단위 테스트 (`tests/test_collectors/`)

#### 리스크 및 대응
| 리스크 | 대응 방안 |
|--------|----------|
| KIS API 연동 실패 | 공식 문서 + 커뮤니티 (GitHub Issues) 참고 |
| DB 설계 오류 | ERD 검토 + 멘토 리뷰 |
| 데이터 수집 지연 | 비동기 처리 (asyncio) 적용 |

---

### Week 3: 기술적 지표 계산

#### 목표
- 모든 종목에 대한 기술적 지표 계산
- S&P 500 이동평균선 신호 생성

#### 세부 작업

**Day 15-17: 기술 지표 라이브러리**
```python
# 작업 리스트
- [ ] TA-Lib 또는 ta 라이브러리 설치
- [ ] 이동평균선 (5, 20, 60, 120일) 계산
- [ ] RSI (14일) 계산
- [ ] MACD 계산
- [ ] 볼린저 밴드 계산
- [ ] 변동성 (20일 표준편차) 계산
- [ ] technical_analyzer.py 작성

# 실행
python scripts/calculate_indicators.py --all
```

**Day 18-19: S&P 500 신호 생성**
```python
# 작업 리스트
- [ ] S&P 500 > MA(20) → BULLISH
- [ ] S&P 500 < MA(20) → BEARISH
- [ ] 신호 이력 DB 저장
- [ ] 신호 변경 시 알림 로직

# 테스트
assert sp500_signal("2023-06-15") == "BULLISH"
```

**Day 20-21: 매매 신호 탐지**
```python
# 작업 리스트
- [ ] 골든크로스/데드크로스 탐지
- [ ] RSI 과매수/과매도 탐지
- [ ] MACD 크로스 탐지
- [ ] 신호 종합 점수 계산

# 결과 예시
{
  "golden_cross": True,
  "rsi_oversold": False,
  "macd_bullish": True,
  "score": 75
}
```

#### 산출물
- ✅ 기술 지표 계산 모듈 (`app/analyzers/technical_analyzer.py`)
- ✅ 신호 탐지 모듈 (`app/analyzers/signal_detector.py`)
- ✅ 일일 신호 리포트

---

### Week 4: 기본 대시보드 구축

#### 목표
- Streamlit으로 웹 대시보드 MVP 완성
- 시장 현황, 종목 검색, 상세 정보 표시

#### 세부 작업

**Day 22-24: Streamlit 설정**
```python
# 작업 리스트
- [ ] Streamlit 설치 및 기본 구조
- [ ] 메인 페이지 레이아웃
- [ ] 사이드바 메뉴
- [ ] FastAPI 연동 (HTTP 요청)

# 실행
streamlit run dashboard/app.py
```

**Day 25-26: 시장 현황 페이지**
```python
# 작업 리스트
- [ ] KOSPI/KOSDAQ 지수 표시
- [ ] S&P 500 지수 및 신호 표시
- [ ] 실시간 갱신 (30초마다)
- [ ] Plotly 차트 연동

# 화면 구성
┌─────────────────────────────────────┐
│ 📊 시장 현황                         │
├─────────────────────────────────────┤
│ KOSPI: 2,530 (+1.2%) ↗️              │
│ S&P 500: 4,550 (-1.3%) ↘️ [BEARISH] │
│                                     │
│ [차트]                               │
└─────────────────────────────────────┘
```

**Day 27-28: 종목 검색 및 상세**
```python
# 작업 리스트
- [ ] 종목 검색 (코드 또는 이름)
- [ ] 현재가, 차트, 재무 정보 표시
- [ ] 기술 지표 표시
- [ ] 캔들스틱 차트 (Plotly)

# 사용자 플로우
종목 검색 → 상세 페이지 → 차트/지표 확인
```

#### 산출물
- ✅ Streamlit 대시보드 (`dashboard/app.py`)
- ✅ 시장 현황 페이지 (`dashboard/pages/01_market_overview.py`)
- ✅ 종목 상세 페이지 (`dashboard/pages/03_stock_detail.py`)

---

### Week 5-6: 초보자 추천 시스템

#### 목표
- 투자 성향 분석 및 맞춤 종목 추천
- 섹터별 가이드 제공

#### 세부 작업

**Day 29-31: 투자 성향 분석**
```python
# 작업 리스트
- [ ] 5문항 설문지 UI (Streamlit)
- [ ] 성향 분석 알고리즘 (risk_level, preferred_sector)
- [ ] 결과 시각화 (레이더 차트)

# 설문 예시
1. 투자 금액: 500만원 미만 / 500~1,000만원 / ...
2. 투자 기간: 단기 / 중기 / 장기
3. 손실 허용도: 불안함 / 견딜 수 있음 / 기회로 봄
...
```

**Day 32-35: 종목 필터링 알고리즘**
```python
# 작업 리스트
- [ ] 필터 조건 정의 (시가총액, 거래대금, 부채비율 등)
- [ ] 리스크 수준별 필터링
- [ ] BeginnerRecommender 클래스 작성
- [ ] filter_stocks() 메서드 구현

# 필터 예시
if risk_level == "LOW":
    query = query.filter(
        market_cap >= 10_trillion,
        volatility_20d < 1.5,
        dividend_yield >= 2.0
    )
```

**Day 36-38: 점수 계산 및 추천**
```python
# 작업 리스트
- [ ] 초보자 적합도 점수 알고리즘 (0-100)
- [ ] 추천 이유 생성 로직
- [ ] 상위 10~20개 추천
- [ ] DB에 추천 결과 저장

# 점수 구성
score = (시가총액 30점) + (변동성 20점) +
        (ROE 20점) + (배당 15점) + (외국인 보유 15점)
```

**Day 39-42: 섹터 가이드**
```markdown
# 작업 리스트
- [ ] 10개 주요 섹터 분류
- [ ] 섹터별 특징 설명 (초등학생 수준)
- [ ] 현재 트렌드 분석 (경제 지표 기반)
- [ ] 대표 종목 3개 선정
- [ ] Streamlit 페이지 작성

# 섹터 예시
## IT/반도체
- 특징: 한국의 강점 산업, 고성장
- 리스크: MEDIUM
- 대표 종목: 삼성전자, SK하이닉스, NAVER
- 관련 지표: 필라델피아 반도체 지수
```

#### 산출물
- ✅ 추천 엔진 (`app/recommenders/beginner_recommender.py`)
- ✅ 섹터 분석기 (`app/recommenders/sector_analyzer.py`)
- ✅ 추천 페이지 (`dashboard/pages/02_recommendations.py`)

---

### Week 7: 백테스팅 시스템

#### 목표
- Backtrader로 전략 검증 시스템 구축
- S&P 500 이평선 전략 백테스트 (2018-2023)

#### 세부 작업

**Day 43-45: Backtrader 프레임워크**
```python
# 작업 리스트
- [ ] Backtrader 설치 및 기본 구조
- [ ] SP500MAStrategy 클래스 작성
- [ ] 데이터 피드 설정 (OHLCV)
- [ ] 수수료 및 슬리피지 설정

# 전략 코드
class SP500MAStrategy(bt.Strategy):
    params = (('ma_period', 20),)

    def next(self):
        if self.sp500_close > self.sp500_ma:
            self.buy()  # 매수
        else:
            self.close()  # 매도
```

**Day 46-47: 백테스트 실행**
```python
# 작업 리스트
- [ ] 2018-2023년 데이터 준비
- [ ] 백테스트 실행
- [ ] 성과 지표 계산 (CAGR, MDD, Sharpe)
- [ ] 결과 시각화 (equity curve)

# 실행
python scripts/run_backtest.py \
  --strategy SP500MAStrategy \
  --start 2018-01-01 \
  --end 2023-12-31 \
  --capital 10000000
```

**Day 48-49: 결과 분석 및 리포트**
```python
# 작업 리스트
- [ ] 백테스트 결과 DB 저장
- [ ] 벤치마크(코스피) 대비 비교
- [ ] 월별/연도별 수익률 분석
- [ ] PDF 리포트 생성

# 목표 결과
- CAGR: > 10%
- Sharpe Ratio: > 1.0
- MDD: < -20%
```

#### 산출물
- ✅ 백테스트 엔진 (`app/analyzers/backtest_engine.py`)
- ✅ 백테스트 결과 (`reports/backtest_sp500_ma.pdf`)
- ✅ 백테스트 API (`/api/v1/backtest/results`)

---

### Week 8: 차트 이미지 분석

#### 목표
- Upstage OCR로 차트에서 데이터 추출
- CLOVA AI로 패턴 분석

#### 세부 작업

**Day 50-52: Upstage Document AI**
```python
# 작업 리스트
- [ ] Upstage API Key 발급
- [ ] 이미지 업로드 API 작성
- [ ] OCR 결과 파싱 (가격, 지표 추출)
- [ ] 정확도 검증 (수동 테스트 10건)

# API 호출
response = upstage.ocr(image_path)
current_price = extract_price(response.text)
```

**Day 53-54: CLOVA Studio AI 분석**
```python
# 작업 리스트
- [ ] CLOVA Studio API Key 발급
- [ ] 차트 분석 프롬프트 작성
- [ ] 응답 파싱 (추세, 지지/저항선 등)
- [ ] 신뢰도 점수 계산

# 프롬프트 예시
"이 차트에서 현재 추세는 상승인가요, 하락인가요?
지지선과 저항선의 가격대를 알려주세요."
```

**Day 55-56: UI 통합**
```python
# 작업 리스트
- [ ] Streamlit 파일 업로드 위젯
- [ ] 분석 버튼 및 로딩 스피너
- [ ] 결과 표시 (OCR + AI 분석)
- [ ] 차트 페이지 작성

# 사용자 플로우
이미지 업로드 → 분석 버튼 → 결과 표시 (5초 이내)
```

#### 산출물
- ✅ 차트 OCR 모듈 (`app/analyzers/chart_ocr.py`)
- ✅ 차트 분석 페이지 (`dashboard/pages/04_chart_analysis.py`)
- ✅ 월 300건 무료 한도 관리 로직

---

### Week 9-10: 뉴스 감성 분석 & 알림

#### 목표
- 뉴스 수집 및 감성 분석 시스템 구축
- 카카오톡 알림 연동

#### 세부 작업

**Day 57-60: 뉴스 수집**
```python
# 작업 리스트
- [ ] 빅카인즈 API 연동
- [ ] 종목별 뉴스 검색 (최근 7일)
- [ ] 뉴스 출처 분류 (Tier 1/2/3)
- [ ] stock_news 테이블 저장

# 신뢰도 평가
tier1 = ['연합뉴스', '한국경제', '매일경제']
tier2 = ['파이낸셜뉴스', '이데일리']
tier3 = ['블로그', '커뮤니티']
```

**Day 61-64: 감성 분석**
```python
# 작업 리스트
- [ ] Transformers 라이브러리 설치
- [ ] 한국어 BERT 모델 로드 (beomi/kcbert-base)
- [ ] 감성 점수 계산 (-1.0 ~ +1.0)
- [ ] 종목별 감성 집계

# 모델 사용
from transformers import pipeline
sentiment = pipeline("sentiment-analysis", model="beomi/kcbert-base")
result = sentiment("삼성전자 실적 호조")
# {'label': 'positive', 'score': 0.95}
```

**Day 65-68: 카카오톡 알림**
```python
# 작업 리스트
- [ ] 카카오 개발자 계정 및 앱 등록
- [ ] REST API Key 발급
- [ ] 나에게 보내기 테스트
- [ ] 알림 유형 정의 (목표가, 급등/락, 공시, 손절매)
- [ ] KakaoNotifier 클래스 작성

# 알림 전송
notifier.send_alert(
    alert_type='target_price',
    stock_name='삼성전자',
    message='목표가 76,000원 도달!'
)
```

**Day 69-70: 알림 트리거 설정**
```python
# 작업 리스트
- [ ] 목표가 모니터링 (10초마다)
- [ ] 급등/락 탐지 (5% 이상 변동)
- [ ] 중요 공시 모니터링
- [ ] S&P 500 신호 변경 알림
- [ ] 사용자별 알림 설정 DB

# 트리거 예시
if current_price >= target_price:
    send_alert('target_price', ...)
```

#### 산출물
- ✅ 뉴스 수집기 (`app/collectors/news_collector.py`)
- ✅ 감성 분석기 (`app/analyzers/sentiment_analyzer.py`)
- ✅ 알림 시스템 (`app/utils/notification.py`)

---

### Week 11: AWS 배포 & 모의투자

#### 목표
- AWS EC2에 시스템 배포
- 모의투자 계좌로 실전 테스트 시작

#### 세부 작업

**Day 71-73: AWS 인프라 설정**
```bash
# 작업 리스트
- [ ] AWS 계정 생성
- [ ] EC2 인스턴스 생성 (t2.micro)
- [ ] RDS PostgreSQL 인스턴스 생성 (db.t3.micro)
- [ ] ElastiCache Redis 생성
- [ ] S3 버킷 생성 (차트 이미지 저장)
- [ ] IAM 역할 및 보안 그룹 설정

# EC2 생성
aws ec2 run-instances \
  --image-id ami-0c55b159cbfafe1f0 \
  --instance-type t2.micro \
  --key-name my-key-pair
```

**Day 74-75: 코드 배포**
```bash
# 작업 리스트
- [ ] GitHub Actions CI/CD 파이프라인 작성
- [ ] Docker 이미지 빌드 및 ECR 푸시
- [ ] EC2에 Docker 설치 및 실행
- [ ] 환경 변수 설정 (.env)
- [ ] Nginx 리버스 프록시 설정
- [ ] SSL 인증서 (Let's Encrypt)

# 배포 명령
git push origin main  # GitHub Actions 자동 배포
```

**Day 76-77: Lambda 스케줄링**
```python
# 작업 리스트
- [ ] Lambda 함수 작성 (일일 데이터 수집)
- [ ] CloudWatch Events 규칙 생성
  - 09:00: 미국 시장 분석
  - 09:00-15:30: 실시간 수집 (10초마다)
  - 16:00: 백테스팅
  - 18:00: 뉴스 분석
- [ ] Lambda IAM 역할 설정
- [ ] 테스트 실행

# CloudWatch 규칙 예시
cron(0 0 * * ? *)  # 매일 09:00 KST
```

**Day 78-84: 모의투자 실전 테스트**
```python
# 작업 리스트
- [ ] KIS 모의투자 계좌 개설
- [ ] 초기 자본 1,000만원 설정
- [ ] 추천 종목 TOP 5 매수
- [ ] 일일 포트폴리오 추적
- [ ] 수익률, MDD 기록
- [ ] 문제점 발견 시 즉시 수정

# 모의투자 기록 (Week 11-12)
Day 1: 삼성전자 10주, KB금융 5주 매수
Day 2: 수익률 +1.2%
...
Day 21: 최종 수익률 +8.5%, MDD -3.2%
```

#### 산출물
- ✅ AWS 인프라 (EC2, RDS, Lambda)
- ✅ CI/CD 파이프라인 (`.github/workflows/deploy.yml`)
- ✅ 모의투자 일지 (`reports/mock_trading_log.xlsx`)

---

### Week 12: 최종 테스트 & 문서화

#### 목표
- 버그 수정 및 성능 최적화
- 사용자 가이드 및 발표 자료 작성

#### 세부 작업

**Day 85-87: 통합 테스트**
```python
# 작업 리스트
- [ ] End-to-End 테스트 (사용자 시나리오)
- [ ] 부하 테스트 (동시 사용자 100명)
- [ ] API 응답 시간 측정 (목표: < 1초)
- [ ] 메모리 누수 확인
- [ ] 에러 로그 검토 및 수정

# 테스트 도구
- Locust (부하 테스트)
- pytest (단위/통합 테스트)
```

**Day 88-89: 성능 최적화**
```python
# 작업 리스트
- [ ] DB 쿼리 최적화 (인덱스 추가)
- [ ] Redis 캐싱 전략 (TTL 설정)
- [ ] API 응답 압축 (gzip)
- [ ] 이미지 최적화 (압축, CDN)
- [ ] 불필요한 로그 제거

# 최적화 예시
# Before: 2.5초
# After: 0.8초 (캐싱 + 인덱스)
```

**Day 90-91: 문서화**
```markdown
# 작업 리스트
- [ ] README.md 업데이트
- [ ] BEGINNER_GUIDE.md 작성 (초보자용)
- [ ] API 문서 (Swagger/OpenAPI)
- [ ] 설치 가이드
- [ ] 운영 매뉴얼
- [ ] FAQ

# 문서 구성
1. 시작하기 (5분 안에 실행)
2. 기능 설명 (스크린샷 포함)
3. 트러블슈팅
4. FAQ
```

**Day 92-93: 발표 자료 준비**
```markdown
# 작업 리스트
- [ ] 프레젠테이션 슬라이드 (PPT)
- [ ] 데모 시나리오 작성
- [ ] 백테스팅 결과 차트
- [ ] 모의투자 성과 정리
- [ ] 시연 영상 촬영 (3분)

# 발표 구성
1. 문제 정의 (초보 투자자의 어려움)
2. 솔루션 (SIS 시스템)
3. 핵심 기술 (미국-한국 연관성, 백테스팅)
4. 시연 (라이브 데모)
5. 성과 (모의투자 결과)
6. 향후 계획
```

**Day 94: 최종 점검**
```bash
# 작업 리스트
- [ ] 모든 기능 테스트 (체크리스트)
- [ ] 문서 오타 확인
- [ ] GitHub 리포지토리 정리
- [ ] 발표 리허설
- [ ] 백업 (DB, 코드)
```

#### 산출물
- ✅ 사용자 가이드 (`BEGINNER_GUIDE.md`)
- ✅ API 문서 (`docs/api.md`)
- ✅ 발표 자료 (`presentation/SIS_Final.pptx`)
- ✅ 시연 영상 (`demo/system_demo.mp4`)

---

## 4. 리소스 계획

### 4.1 인력 계획

| 역할 | 인원 | 주요 업무 | 시간 투입 |
|------|------|----------|----------|
| **Full-stack Developer** | 1명 | 전체 시스템 개발 | 주 40시간 (3개월) |
| **멘토 (선택)** | 1명 | 코드 리뷰, 기술 자문 | 주 2시간 |

### 4.2 비용 계획

#### 월별 비용 (무료 티어 최대 활용)

| 항목 | 1개월 | 2개월 | 3개월 | 비고 |
|------|-------|-------|-------|------|
| **AWS EC2** | 0원 | 0원 | 0원 | t2.micro 1년 무료 |
| **AWS RDS** | 0원 | 0원 | 0원 | db.t3.micro 1년 무료 |
| **AWS Lambda** | 0원 | 0원 | 0원 | 월 100만 요청 무료 |
| **S3** | 0원 | 0원 | 0원 | 5GB 무료 |
| **Upstage API** | 0원 | 0원 | 0원 | 월 300건 무료 |
| **CLOVA Studio** | 0원 | 15,000원 | 15,000원 | 체험판 → 유료 |
| **도메인 (선택)** | 15,000원 | 0원 | 0원 | 연 15,000원 |
| **총계** | **15,000원** | **15,000원** | **15,000원** | **45,000원** |

#### 4~6개월 예상 비용 (무료 티어 종료 후)
- EC2: 월 10,000원
- RDS: 월 15,000원
- 총: **월 40,000원**

### 4.3 API 사용량 관리

> **📌 전체 API 목록 및 상세 정보**: **`API_SUMMARY.md`** 참조

**필수 데이터 수집 API (5개):**

| API | 무료 한도 | Rate Limit | 특이사항 |
|-----|----------|-----------|----------|
| **KIS API** | 무제한 | 초당 20회 | 증권계좌 필수 |
| **DART API** | 무제한 | 무제한 | 회원가입만 필요 |
| **ECOS API** | 100회/day | - | 본인인증 필수 |
| **FRED API** | 무제한 | 120회/min | 이메일 인증 |
| **BigKinds API** | - | - | 회원가입 필요 |

**선택 AI API (주요):**

| API | 무료 한도 | 예상 사용량 | 대응 방안 |
|-----|----------|-----------|----------|
| Upstage OCR | 월 300건 | 월 200건 | 1일 10건 제한 |
| CLOVA Studio | 월 100회 | 월 100건 | 무료 한도 내 사용 |
| Gemini | 60회/min | 적정 | 무료 tier 활용 |

---

## 5. 리스크 관리

### 5.1 리스크 매트릭스

| 리스크 | 영향도 | 확률 | 점수 | 우선순위 |
|--------|-------|------|------|---------|
| KIS API 정책 변경 | High | Medium | 8 | 1순위 |
| 백테스팅 과최적화 | High | Medium | 8 | 1순위 |
| AWS 비용 초과 | Medium | Low | 4 | 3순위 |
| 일정 지연 | Medium | Medium | 6 | 2순위 |
| 데이터 정확도 이슈 | High | Low | 6 | 2순위 |

### 5.2 리스크별 대응 계획

#### 1순위: KIS API 정책 변경
**대응**:
- 백업 API 준비 (키움증권, LS증권)
- 데이터 로컬 캐싱 (1주일치)
- API 커뮤니티 모니터링

#### 1순위: 백테스팅 과최적화
**대응**:
- Walk-forward 검증
- Out-of-sample 테스트 (30%)
- 보수적 파라미터 선택

#### 2순위: 일정 지연
**대응**:
- 주차별 버퍼 1일 확보
- 우선순위 낮은 기능 Phase 4로 연기
- 일일 진행률 체크

#### 3순위: AWS 비용 초과
**대응**:
- 일일 비용 모니터링
- 알림 설정 ($10 초과 시)
- Lambda로 EC2 자동 중지 (장외 시간)

---

## 6. 품질 관리

### 6.1 코드 품질

**코딩 표준**:
- PEP 8 준수
- Type Hints 사용
- Docstring 작성 (Google Style)

**코드 리뷰**:
- Pull Request 필수
- 자동화된 테스트 통과 필수
- 주 1회 멘토 리뷰

### 6.2 테스트 전략

| 테스트 유형 | 커버리지 목표 | 도구 |
|-----------|-------------|------|
| 단위 테스트 | 80% | pytest |
| 통합 테스트 | 주요 플로우 | pytest |
| E2E 테스트 | 5개 시나리오 | Selenium (선택) |
| 부하 테스트 | 100명 동시 | Locust |

### 6.3 데이터 품질

**검증 항목**:
- [ ] 주가 데이터 교차 검증 (오차 < 1%)
- [ ] 재무제표 DART 공식 출처 확인
- [ ] 이동평균선 계산 검증 (수동 계산과 비교)
- [ ] 백테스팅 결과 재현성 확인

---

## 7. 커뮤니케이션 계획

### 7.1 정기 회의

| 회의 | 주기 | 참석자 | 목적 |
|------|------|-------|------|
| 주간 리뷰 | 매주 금요일 | 개발자 + 멘토 | 진행률, 이슈 |
| 마일스톤 리뷰 | Phase 종료 시 | 전체 | 결과물 검토 |
| 일일 스탠드업 (선택) | 매일 10분 | 개발자 | 오늘 할 일, 블로커 |

### 7.2 문서화

**필수 문서**:
- ✅ README.md (프로젝트 소개)
- ✅ PRD.md (제품 요구사항)
- ✅ LLD.md (기술 설계)
- ✅ PLAN.md (프로젝트 계획)
- ✅ BEGINNER_GUIDE.md (초보자 가이드)

**선택 문서**:
- 주간 진행 리포트
- 이슈 트래킹 (GitHub Issues)
- 회의록

### 7.3 협업 도구

| 도구 | 용도 |
|------|------|
| GitHub | 코드 관리, 이슈 트래킹 |
| Notion/Confluence | 문서 공유 |
| Slack/Discord | 커뮤니케이션 |
| Google Meet | 화상 회의 |

---

## 8. 최종 체크리스트

### 8.1 Phase 1 완료 기준 (1개월)
- [ ] KIS API 연동 완료 (100개 이상 종목 데이터 수집)
- [ ] PostgreSQL DB 구축 (5개 테이블)
- [ ] 기술 지표 계산 (MA, RSI, MACD)
- [ ] S&P 500 신호 생성
- [ ] 기본 대시보드 (시장 현황, 종목 상세)

### 8.2 Phase 2 완료 기준 (2개월)
- [ ] 초보자 추천 시스템 (TOP 10 종목)
- [ ] 백테스팅 결과 (Sharpe > 1.0)
- [ ] 차트 이미지 분석 (OCR + AI)
- [ ] 섹터 가이드 (10개 섹터)

### 8.3 Phase 3 완료 기준 (3개월)
- [ ] 뉴스 감성 분석 (한국어 BERT)
- [ ] 카카오톡 알림 (5가지 유형)
- [ ] AWS 배포 (EC2 + RDS)
- [ ] 모의투자 완료 (3주, 수익률 기록)
- [ ] 문서화 완료 (5개 문서)
- [ ] 발표 준비 완료

### 8.4 최종 성공 기준
- [ ] 백테스팅 CAGR > 10%
- [ ] 백테스팅 MDD < -20%
- [ ] 모의투자 승률 > 60%
- [ ] API 응답 시간 < 1초
- [ ] 시스템 가용성 > 99%
- [ ] 사용자 가이드 작성 완료

---

## 9. 향후 계획 (Phase 4+)

### 9.1 단기 (3~6개월)
- [ ] 미국 주식 데이터 추가
- [ ] 포트폴리오 백테스팅 시뮬레이터
- [ ] 모바일 반응형 개선
- [ ] 사용자 피드백 반영

### 9.2 중기 (6~12개월)
- [ ] 실제 자동매매 연동 (증권사 승인 필요)
- [ ] 커뮤니티 기능 (투자 아이디어 공유)
- [ ] AI 예측 모델 고도화 (LSTM)
- [ ] 유료 서비스 전환 검토

### 9.3 장기 (12개월+)
- [ ] 모바일 앱 출시 (React Native)
- [ ] 해외 진출 (영어 버전)
- [ ] B2B 서비스 (증권사 제휴)

---

## 변경 이력

| 버전 | 날짜 | 변경 내용 | 작성자 |
|------|------|-----------|--------|
| 1.0 | 2025-11-21 | 초안 작성 | AI Assistant |
| 2.0 | 2025-11-22 | Phase 2 완료 상태 반영 (Multi-LLM 시스템) | AI Assistant |
|  |  | Week 8 완료 항목 업데이트 | |
| 2.1 | 2025-11-22 | 소셜 미디어 수집 시스템 추가 | AI Assistant |
|  |  | Week 8에 WallStreetBets + StockTwits 구현 반영 | |
|  |  | SNS 크롤링 연구 완료 표시 | |
| 2.2 | 2025-11-23 | API 요구사항 명확화 및 API_SUMMARY.md 참조 추가 | AI Assistant |
|  |  | - 19개 API/데이터 소스 목록 명시 (5개 필수 + 14개 선택) | |
|  |  | - API 준비 필수 안내 추가 | |
|  |  | - API 사용량 관리 섹션 업데이트 | |
|  |  | - API_SUMMARY.md 상호 참조 추가 | |
