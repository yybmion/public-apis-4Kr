# API 및 데이터 소스 요약

## 📊 데이터 소스 한눈에 보기

| 데이터 소스 | 필수 여부 | API 키 필요 | 회원가입 | 비용 | Rate Limit | 수집 데이터 |
|------------|---------|-----------|---------|------|-----------|-----------|
| **FRED API** | ✅ 필수 | ✅ 필요 | ✅ 필요 | 무료 | 120 req/min | 미국 경제 지표 (금리, 국채 수익률) |
| **ECOS API** | ✅ 필수 | ✅ 필요 | ✅ 필요 (본인인증) | 무료 | 100 req/day | 한국 경제 지표 (기준금리, 환율, CPI) |
| **Fear & Greed** | ✅ 필수 | ❌ 불필요 | ❌ 불필요 | 무료 | 무제한 | CNN Fear & Greed Index |
| **Yahoo Finance** | ✅ 필수 | ❌ 불필요 | ❌ 불필요 | 무료 | ~2000 req/hour | S&P 500, NASDAQ, KOSPI, KOSDAQ |
| **SEC EDGAR** | ⚠️ 선택 | ❌ 불필요 (User-Agent만) | ❌ 불필요 | 무료 | 10 req/sec | 미국 기업 재무제표 (10-K, 10-Q) |
| **Telegram Bot** | ⚠️ 선택 | ✅ 필요 (Bot Token) | ✅ 필요 | 무료 | 무제한 | 실시간 투자 알림 |
| **Gmail SMTP** | ⚠️ 선택 | ✅ 필요 (App Password) | ✅ 필요 | 무료 | 500/day | 일일/주간 이메일 리포트 |

---

## ✅ 필수 데이터 소스 (4개)

시스템 기본 작동에 필요한 데이터 소스입니다.

### 1. FRED API (필수, API 키 필요) 🔑

**수집 데이터:**
- 미국 기준금리 (FEDFUNDS)
- 국채 수익률 (DGS3MO, DGS2, DGS5, DGS10, DGS30)
- 실업률 (UNRATE)
- GDP (GDP)
- 소비자물가지수 (CPIAUCSL)

**회원가입:**
1. https://fred.stlouisfed.org/ 접속
2. "My Account" → "Create Account"
3. 이메일 인증
4. "API Keys" → "Request API Key"
5. API 키 복사

**환경 변수:**
```bash
FRED_API_KEY=your_fred_api_key_here
```

**Rate Limit:** 120 requests/minute

---

### 2. ECOS API (필수, API 키 필요) 🔑

**수집 데이터:**
- 한국 기준금리
- 환율 (USD/KRW, JPY/KRW, EUR/KRW)
- 소비자물가지수 (CPI)
- GDP 성장률

**회원가입:**
1. https://ecos.bok.or.kr/ 접속
2. 회원가입 (본인인증 필수: 휴대폰 또는 아이핀)
3. 로그인 → "OpenAPI" → "인증키 신청/관리"
4. "인증키 신청" 클릭
5. 용도 입력 (예: "개인 프로젝트")
6. 인증키 복사

**환경 변수:**
```bash
ECOS_API_KEY=your_ecos_api_key_here
```

**Rate Limit:** 100 requests/day

**주의:** 일일 한도가 100회로 제한적이므로 효율적으로 사용해야 함

---

### 3. Fear & Greed Index (필수, API 키 불필요) ✨

**수집 데이터:**
- Fear & Greed Index 점수 (0-100)
- 등급 (Extreme Fear, Fear, Neutral, Greed, Extreme Greed)
- 7가지 구성요소 (모멘텀, 강도, VIX 등)

**회원가입:** 불필요

**API 엔드포인트:**
```
https://production.dataviz.cnn.io/index/fearandgreed/graphdata
```

**환경 변수:** 불필요

**Rate Limit:** 무제한

**구현 파일:** `app/collectors/fear_greed_collector.py`

**코드 예시:**
```python
import requests

url = "https://production.dataviz.cnn.io/index/fearandgreed/graphdata"
response = requests.get(url)
data = response.json()
score = data['fear_and_greed']['score']
```

---

### 4. Yahoo Finance (필수, API 키 불필요) ✨

**수집 데이터:**
- S&P 500 (^GSPC)
- NASDAQ Composite (^IXIC)
- KOSPI (^KS11)
- KOSDAQ (^KQ11)
- 개별 주식 (AAPL, TSLA 등)

**회원가입:** 불필요

**Python 라이브러리:** `yfinance`

**환경 변수:** 불필요

**Rate Limit:** ~2000 requests/hour (비공식)

**코드 예시:**
```python
import yfinance as yf

# S&P 500
sp500 = yf.Ticker("^GSPC")
data = sp500.history(period="1d")
close_price = data['Close'].iloc[-1]

# KOSPI
kospi = yf.Ticker("^KS11")
data = kospi.history(period="1d")
```

---

## ⚠️ 선택 데이터 소스 (3개)

추가 기능을 위한 선택사항입니다.

### 5. SEC EDGAR API (선택, User-Agent만 필요)

**용도:** 미국 상장 기업 재무제표 분석

**수집 데이터:**
- 10-K (연간 보고서)
- 10-Q (분기 보고서)
- 재무제표 (XBRL)
- 기관 투자자 보유 현황

**회원가입:** 불필요

**요구사항:** User-Agent 헤더에 이메일 포함

**환경 변수:**
```bash
SEC_USER_AGENT="Stock-Intelligence-System your-email@example.com"
```

**Rate Limit:** 10 requests/second

**필수 여부:**
- ❌ 미국 기업 분석이 필요 없으면 **생략 가능**
- ✅ 미국 기업 재무제표가 필요하면 **사용**

**구현 상태:** Phase 2에서 완전 구현됨 (4개 테이블, 수집기, 테스트)

---

### 6. Telegram Bot (선택, Bot Token 필요) 🔑

**용도:** 실시간 투자 알림

**알림 종류:**
- 투자 신호 변경 (STRONG_BUY → BUY 등)
- 일일 시장 브리핑 (오전 09:00, 오후 15:40)
- 극단적 시장 상황 (Fear & Greed < 25 또는 > 75)
- 경제 지표 변화 (금리 인상/인하, 수익률 곡선 역전)

**Bot 생성:**
1. Telegram 앱 설치
2. @BotFather 검색
3. `/newbot` 명령어
4. Bot 이름 및 Username 설정
5. Bot Token 복사

**Chat ID 확인:**
1. @userinfobot 검색
2. `/start` 명령어
3. Chat ID 복사

**환경 변수:**
```bash
TELEGRAM_BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
TELEGRAM_CHAT_ID=123456789
ALERT_TELEGRAM_ENABLED=true
```

**필수 여부:**
- ❌ 알림이 필요 없으면 **생략 가능**
- ✅ 실시간 알림을 받고 싶으면 **사용**

---

### 7. Gmail SMTP (선택, App Password 필요) 🔑

**용도:** 이메일 알림 및 리포트

**발송 내용:**
- 일일 투자 리포트 (HTML 포맷)
- 주간 성과 리포트
- 중요 신호 변경 알림
- 극단적 시장 상황 알림

**App Password 생성:**
1. Gmail 계정 로그인
2. Google 계정 관리 → 보안
3. 2단계 인증 활성화 (필수)
4. "앱 비밀번호" → "메일" 선택
5. 16자리 비밀번호 생성

**환경 변수:**
```bash
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your_app_password_here
EMAIL_FROM=your-email@gmail.com
EMAIL_TO=recipient@example.com
ALERT_EMAIL_ENABLED=true
```

**대안:** Naver Mail, Daum Mail 등도 사용 가능

**필수 여부:**
- ❌ 이메일 알림이 필요 없으면 **생략 가능**
- ✅ 상세한 리포트를 이메일로 받고 싶으면 **사용**

---

## 🚀 최소 설정 (핵심 기능만)

**핵심 투자 시스템만 사용하려면 (알림 없이):**

### 필수 설정:
1. ✅ FRED API 키 (미국 경제 지표)
2. ✅ ECOS API 키 (한국 경제 지표)
3. ✅ Fear & Greed (API 키 불필요)
4. ✅ Yahoo Finance (API 키 불필요)

### .env 파일 (최소):
```bash
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/stock_intelligence

# API Keys (필수)
FRED_API_KEY=your_fred_api_key_here
ECOS_API_KEY=your_ecos_api_key_here

# Logging
LOG_DIR=logs
LOG_LEVEL=INFO
```

**이것만 설정하면 작동하는 기능:**
- ✅ 데이터 수집 (시장, 경제, Fear & Greed)
- ✅ 투자 신호 생성
- ✅ 백테스팅
- ✅ Dashboard 확인
- ✅ 로그 확인
- ❌ 알림 (Telegram, Email) - 비활성화

---

## 🎯 완전 설정 (모든 기능 사용)

**모든 기능을 사용하려면:**

### 필수 설정:
1. ✅ FRED API 키
2. ✅ ECOS API 키
3. ✅ Fear & Greed
4. ✅ Yahoo Finance

### 선택 설정:
5. ⚠️ SEC EDGAR (미국 기업 재무제표 필요 시)
6. ⚠️ Telegram Bot (실시간 알림 원하면)
7. ⚠️ Gmail SMTP (이메일 리포트 원하면)

### .env 파일 (완전):
```bash
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/stock_intelligence

# API Keys (필수)
FRED_API_KEY=your_fred_api_key_here
ECOS_API_KEY=your_ecos_api_key_here

# SEC EDGAR (선택)
SEC_USER_AGENT="Stock-Intelligence-System your-email@example.com"

# Telegram (선택)
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
TELEGRAM_CHAT_ID=your_telegram_chat_id_here
ALERT_TELEGRAM_ENABLED=true

# Email (선택)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your_app_password_here
EMAIL_FROM=your-email@gmail.com
EMAIL_TO=recipient@example.com
ALERT_EMAIL_ENABLED=true

# Logging
LOG_DIR=logs
LOG_LEVEL=INFO
```

---

## 📝 체크리스트

### 최소 설정 (핵심 기능만)
- [ ] FRED API 키 발급
- [ ] ECOS API 키 발급
- [ ] PostgreSQL 설치 및 데이터베이스 생성
- [ ] .env 파일 생성 (최소 설정)
- [ ] `pip install -r requirements.txt`
- [ ] Migration 실행
- [ ] 테스트 실행

**소요 시간:** 약 30분

### 완전 설정 (모든 기능)
최소 설정 + 아래 항목:
- [ ] Telegram Bot 생성 및 Token 발급 (+5분)
- [ ] Chat ID 확인 (+2분)
- [ ] Gmail App Password 생성 (+5분)
- [ ] SEC EDGAR User-Agent 설정 (+1분)
- [ ] 알림 테스트 (`python scripts/test_alerts.py`)

**소요 시간:** 약 45분

---

## 🤔 어떤 설정을 선택할까?

### 1. 학습 및 개발 단계
**추천:** 최소 설정
- FRED + ECOS만 설정
- 알림 없이 Dashboard에서 확인
- 빠른 시작 가능

### 2. 개인 투자용
**추천:** 완전 설정 (Telegram 포함)
- FRED + ECOS + Telegram
- 실시간 알림으로 신호 놓치지 않음
- 이메일은 선택사항

### 3. 프로덕션/공유용
**추천:** 완전 설정 (모두 포함)
- 모든 API 설정
- Telegram + Email 모두 활성화
- 로그 모니터링 활성화

---

## 💰 비용 요약

**모든 서비스 무료!**

| 서비스 | 월 비용 | 제한사항 |
|--------|---------|---------|
| FRED API | 무료 | 120 req/min |
| ECOS API | 무료 | 100 req/day |
| Fear & Greed | 무료 | 무제한 |
| Yahoo Finance | 무료 | ~2000 req/hour |
| SEC EDGAR | 무료 | 10 req/sec |
| Telegram | 무료 | 무제한 |
| Gmail SMTP | 무료 | 500 emails/day |

**총 비용: 0원**

---

## 🔧 설정 우선순위

1. **1순위 (필수):**
   - ✅ FRED API 키
   - ✅ ECOS API 키
   - ✅ PostgreSQL 데이터베이스

2. **2순위 (강력 추천):**
   - ⭐ Telegram Bot (실시간 알림)

3. **3순위 (있으면 좋음):**
   - 📧 Gmail SMTP (이메일 리포트)

4. **4순위 (선택사항):**
   - 📊 SEC EDGAR (미국 기업 분석 시)

---

## 📞 문제 해결

### Q: FRED API 키가 작동하지 않아요
**A:**
- API 키가 올바른지 확인
- Rate limit (120/min) 초과 여부 확인
- 테스트: `python -c "from fredapi import Fred; import os; from dotenv import load_dotenv; load_dotenv(); fred = Fred(api_key=os.getenv('FRED_API_KEY')); print(fred.get_series_latest_release('FEDFUNDS'))"`

### Q: ECOS API 인증 실패
**A:**
- 인증키 재발급 (한국은행 ECOS 사이트)
- 일일 한도 (100회) 확인
- 본인인증 완료 여부 확인

### Q: Telegram Bot이 메시지를 못 받아요
**A:**
- Bot과 대화 시작 (`/start` 전송)
- Chat ID 재확인 (@userinfobot)
- Bot Token 확인

### Q: Gmail 로그인 실패
**A:**
- 앱 비밀번호 사용 (실제 비밀번호 X)
- 2단계 인증 활성화 확인
- SMTP 포트 확인 (587)

---

**작성일:** 2025-11-22
**버전:** 1.0.0
