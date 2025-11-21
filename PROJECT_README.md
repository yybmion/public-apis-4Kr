# 📈 Stock Intelligence System (SIS)

한국 주식 자동매매 지원 시스템

> **과학적 데이터 기반**의 초보 투자자를 위한 주식 투자 지원 플랫폼

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red.svg)](https://streamlit.io/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15+-blue.svg)](https://www.postgresql.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## 🎯 프로젝트 개요

Stock Intelligence System (SIS)은 **한국 주식 시장**에서 투자하는 초보자들을 위한 데이터 기반 투자 지원 시스템입니다.

### 핵심 특징

- 🇺🇸 **미-한 시장 연동**: S&P 500과 KOSPI의 **0.85 상관계수**를 활용한 과학적 매매 신호
- 📊 **공식 데이터만 사용**: 한국투자증권(KIS), DART, 한국은행 등 **신뢰할 수 있는 공식 API**만 활용
- 🧪 **백테스팅 검증**: 모든 전략은 5년 이상의 **백테스팅으로 검증** (Sharpe Ratio > 1.0 목표)
- 🎓 **초보자 친화적**: 복잡한 금융 용어를 쉽게 설명하고, 위험도별 맞춤 추천 제공
- 💰 **저비용 운영**: AWS 무료 티어 활용으로 **월 15,000원 이하** 운영 가능

---

## 🏗️ 시스템 아키텍처

```
┌─────────────────────────────────────────────────────────┐
│              Streamlit Web Dashboard                     │
│          (초보자 친화적 UI, 실시간 차트)                   │
└─────────────────────────────────────────────────────────┘
                          │ HTTP
                          ↓
┌─────────────────────────────────────────────────────────┐
│                  FastAPI Backend                         │
│    - RESTful API                                         │
│    - 데이터 수집 스케줄링                                  │
│    - 추천 알고리즘 엔진                                    │
└─────────────────────────────────────────────────────────┘
                          │
        ┌─────────────────┼─────────────────┐
        ↓                 ↓                 ↓
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│ KIS API      │  │ Yahoo        │  │ DART API     │
│ (한국 주식)   │  │ Finance      │  │ (재무제표)    │
│              │  │ (미국 지수)   │  │              │
└──────────────┘  └──────────────┘  └──────────────┘
                          │
        ┌─────────────────┼─────────────────┐
        ↓                 ↓                 ↓
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│ PostgreSQL   │  │ Redis        │  │ AWS S3       │
│ (메인 DB)     │  │ (캐시)        │  │ (차트 이미지) │
└──────────────┘  └──────────────┘  └──────────────┘
```

---

## ✨ 주요 기능

### Phase 1: MVP (Week 1-4) ✅

- [x] **데이터 수집 인프라**
  - 한국투자증권 KIS API 연동
  - Yahoo Finance 미국 지수 연동
  - DART 재무제표 API 연동
  - PostgreSQL 데이터베이스 구축

- [x] **웹 인터페이스**
  - FastAPI RESTful API 서버
  - Streamlit 대시보드
  - Docker 컨테이너화
  - 실시간 시장 현황 표시

### Phase 2: 핵심 기능 (Week 5-8) 🚧

- [ ] **투자 추천 시스템**
  - 초보자 성향 분석 (5문항 설문)
  - 초보자 적합도 점수 (0-100)
  - 위험도별 종목 필터링 (LOW/MEDIUM/HIGH)
  - 섹터별 가이드

- [ ] **백테스팅 엔진**
  - Backtrader 프레임워크 구축
  - S&P 500 이평선 전략 (2018-2023)
  - 성과 지표 (CAGR, MDD, Sharpe)

- [ ] **차트 이미지 분석**
  - Upstage OCR로 데이터 추출
  - CLOVA AI로 패턴 분석

### Phase 3: 완성 및 배포 (Week 9-12) 📋

- [ ] **뉴스 감성 분석**
  - 빅카인즈 API 연동
  - 한국어 BERT 감성 분석
  - 뉴스 신뢰도 평가

- [ ] **알림 시스템**
  - 카카오톡 메시지 API
  - 목표가, 급등락, 공시, 손절매 알림

- [ ] **AWS 배포**
  - EC2, RDS, Lambda
  - CI/CD 파이프라인
  - 모의투자 실전 테스트 (3주)

---

## 🚀 빠른 시작

### 1. Prerequisites

- Python 3.10+
- Docker & Docker Compose (권장)
- PostgreSQL 15+ (또는 Docker)

### 2. 설치

```bash
# 레포지토리 클론
git clone <repository-url>
cd public-apis-4Kr

# 환경 변수 설정
cp .env.example .env
# .env 파일을 열어 API 키 입력

# Docker Compose로 실행 (가장 쉬움)
cd docker
docker-compose up -d
```

### 3. API 키 발급

다음 API 키들을 발급받아 `.env` 파일에 입력하세요:

1. **한국투자증권 KIS API** (필수)
   - https://apiportal.koreainvestment.com
   - 무료 모의투자 계좌 지원

2. **DART API** (필수)
   - https://opendart.fss.or.kr
   - 재무제표 데이터용

3. **한국은행 ECOS API** (선택)
   - https://ecos.bok.or.kr
   - 경제 지표용

### 4. 접속

- **API 문서**: http://localhost:8000/docs
- **대시보드**: http://localhost:8501

자세한 설치 가이드는 [SETUP_GUIDE.md](./SETUP_GUIDE.md)를 참조하세요.

---

## 📊 데이터 소스

모든 데이터는 **공식 출처**에서만 수집합니다:

| 데이터 종류 | API | 출처 | 신뢰도 |
|------------|-----|------|-------|
| 한국 주식 시세 | 한국투자증권 KIS | 공식 증권사 API | ⭐⭐⭐⭐⭐ |
| 재무제표 | DART | 금융감독원 | ⭐⭐⭐⭐⭐ |
| 미국 지수 | Yahoo Finance | 야후 파이낸스 | ⭐⭐⭐⭐ |
| 경제 지표 | ECOS | 한국은행 | ⭐⭐⭐⭐⭐ |
| 뉴스 | 빅카인즈 | 한국언론진흥재단 | ⭐⭐⭐⭐ |

---

## 💡 핵심 전략: 미-한 시장 연동

### 이론적 배경

**S&P 500과 KOSPI의 상관계수는 약 0.85**로 매우 높은 상관관계를 보입니다.

> "미국 증시가 상승하면, 다음 날 한국 증시도 상승할 확률이 높다"

### 실전 적용

```python
if SP500 > MA(20):
    signal = "BULLISH"  # 한국 주식 매수
else:
    signal = "BEARISH"  # 한국 주식 관망 또는 매도
```

### 백테스팅 목표 성과

| 지표 | 목표 | 벤치마크 (KOSPI) |
|------|------|------------------|
| CAGR | > 10% | ~8% |
| MDD | < -20% | -35% |
| Sharpe Ratio | > 1.0 | ~0.5 |
| 승률 | > 60% | - |

---

## 📁 프로젝트 구조

```
public-apis-4Kr/
├── app/                          # FastAPI 백엔드
│   ├── collectors/               # 데이터 수집기
│   │   ├── kis_collector.py     # 한국투자증권 API
│   │   ├── yahoo_collector.py   # Yahoo Finance
│   │   └── dart_collector.py    # DART API
│   ├── analyzers/                # 분석 엔진
│   ├── recommenders/             # 추천 시스템
│   ├── models/                   # DB 모델
│   └── main.py                   # FastAPI 앱
│
├── dashboard/                    # Streamlit 대시보드
│   ├── app.py                    # 메인 대시보드
│   └── pages/                    # 멀티페이지
│
├── scripts/                      # 유틸리티 스크립트
│   ├── init_db.sql              # DB 초기화
│   └── test_collectors.py       # 수집기 테스트
│
├── docker/                       # Docker 설정
│   ├── docker-compose.yml
│   ├── Dockerfile.api
│   └── Dockerfile.dashboard
│
├── docs/                         # 문서
│   ├── PRD.md                   # 제품 요구사항
│   ├── LLD.md                   # 기술 설계
│   ├── PLAN.md                  # 프로젝트 계획
│   └── BEGINNER_GUIDE.md        # 초보자 가이드
│
├── requirements.txt              # Python 의존성
├── .env.example                  # 환경 변수 예시
├── SETUP_GUIDE.md               # 설치 가이드
└── PROJECT_README.md            # 이 파일
```

---

## 🧪 테스트

### 데이터 수집기 테스트

```bash
# 모든 수집기 테스트
python scripts/test_collectors.py
```

### API 테스트

```bash
# API 서버 시작
uvicorn app.main:app --reload

# 다른 터미널에서
curl http://localhost:8000/health
curl http://localhost:8000/api/v1/market/overview
```

---

## 📚 문서

- [PRD.md](./PRD.md) - 제품 요구사항 문서
- [LLD.md](./LLD.md) - 저수준 설계 문서
- [PLAN.md](./PLAN.md) - 3개월 프로젝트 계획
- [BEGINNER_GUIDE.md](./BEGINNER_GUIDE.md) - 초보자를 위한 가이드
- [SETUP_GUIDE.md](./SETUP_GUIDE.md) - 설치 및 실행 가이드

---

## 💰 비용

### 개발/테스트 단계 (월)

| 항목 | 비용 |
|------|------|
| AWS EC2 (t2.micro) | 무료 (1년) |
| AWS RDS (db.t3.micro) | 무료 (1년) |
| AWS Lambda | 무료 (100만 요청) |
| CLOVA Studio | 15,000원 |
| **총계** | **~15,000원/월** |

### 프로덕션 (무료 티어 종료 후)

- 월 약 40,000원 예상

---

## 🛠️ 기술 스택

### Backend
- **Framework**: FastAPI 0.104+
- **Database**: PostgreSQL 15+
- **Cache**: Redis 7+
- **ORM**: SQLAlchemy 2.0+

### Frontend
- **Framework**: Streamlit 1.28+
- **Charts**: Plotly

### Data Collection
- **Korean Stocks**: 한국투자증권 KIS API
- **US Markets**: yfinance
- **Financials**: DART Open API
- **Economic Data**: 한국은행 ECOS API

### Analysis
- **Backtesting**: Backtrader
- **Technical Analysis**: TA-Lib, pandas-ta
- **AI/ML**: Transformers (BERT), OpenCV

### Infrastructure
- **Container**: Docker, Docker Compose
- **Cloud**: AWS (EC2, RDS, Lambda, S3)
- **CI/CD**: GitHub Actions

---

## 🗓️ 개발 로드맵

### ✅ 완료 (Week 1-2)

- [x] 프로젝트 구조 설계
- [x] 데이터베이스 스키마 구축
- [x] KIS API 연동
- [x] Yahoo Finance 연동
- [x] DART API 연동
- [x] FastAPI 백엔드
- [x] Streamlit 대시보드
- [x] Docker 컨테이너화

### 🚧 진행 중 (Week 3-4)

- [ ] 기술적 지표 계산 (MA, RSI, MACD)
- [ ] S&P 500 신호 생성
- [ ] 실시간 차트 시각화
- [ ] 종목 검색 및 상세 페이지

### 📋 예정 (Week 5-12)

- [ ] 초보자 추천 시스템
- [ ] 백테스팅 엔진
- [ ] 차트 이미지 분석
- [ ] 뉴스 감성 분석
- [ ] 카카오톡 알림
- [ ] AWS 배포
- [ ] 모의투자 테스트

---

## 👥 기여 방법

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📝 라이선스

이 프로젝트는 MIT 라이선스를 따릅니다. 자세한 내용은 [LICENSE](LICENSE) 파일을 참조하세요.

---

## 🙏 감사의 글

이 프로젝트는 다음 오픈소스 프로젝트들의 도움을 받았습니다:

- [FastAPI](https://fastapi.tiangolo.com/)
- [Streamlit](https://streamlit.io/)
- [yfinance](https://github.com/ranaroussi/yfinance)
- [Backtrader](https://www.backtrader.com/)
- [PostgreSQL](https://www.postgresql.org/)

---

## 📧 문의

프로젝트에 대한 질문이나 제안사항이 있으시면 이슈를 등록해주세요.

---

**⚠️ 면책 조항**

이 시스템은 교육 및 연구 목적으로 개발되었습니다. 실제 투자 결정은 사용자의 책임이며, 시스템의 추천을 맹목적으로 따르지 마세요. 주식 투자는 원금 손실의 위험이 있습니다.
