# 🚀 배포 준비 가이드

Stock Intelligence System 프로덕션 배포를 위한 완전한 준비 가이드입니다.

## 📋 목차

1. [필수 API 키 및 회원가입](#1-필수-api-키-및-회원가입)
2. [환경 변수 설정](#2-환경-변수-설정)
3. [데이터베이스 설정](#3-데이터베이스-설정)
4. [의존성 설치](#4-의존성-설치)
5. [로그 디렉토리 설정](#5-로그-디렉토리-설정)
6. [초기 데이터 수집](#6-초기-데이터-수집)
7. [스케줄러 설정](#7-스케줄러-설정)
8. [알림 시스템 설정](#8-알림-시스템-설정)
9. [테스트 체크리스트](#9-테스트-체크리스트)
10. [프로덕션 실행](#10-프로덕션-실행)

---

## 1. 필수 API 키 및 회원가입

### 1.1 FRED API (필수)

**서비스**: 미국 연방준비제도 경제 데이터
**비용**: 무료
**Rate Limit**: 120 requests/minute

**회원가입 및 API 키 발급:**

1. https://fred.stlouisfed.org/ 접속
2. 우측 상단 "My Account" → "Create Account" 클릭
3. 이메일, 비밀번호 설정
4. 이메일 인증 완료
5. 로그인 후 "My Account" → "API Keys" 이동
6. "Request API Key" 클릭
7. API Key 복사 (예: `abcd1234efgh5678ijkl9012mnop3456`)

**데이터 수집 항목:**
- 미국 기준금리 (FEDFUNDS)
- 국채 수익률 (DGS3MO, DGS2, DGS10, DGS30)
- 실업률, GDP 등

**필수 환경 변수:**
```bash
FRED_API_KEY=abcd1234efgh5678ijkl9012mnop3456
```

---

### 1.2 한국은행 ECOS API (필수)

**서비스**: 한국 경제 통계
**비용**: 무료
**Rate Limit**: 100 requests/day

**회원가입 및 API 키 발급:**

1. https://ecos.bok.or.kr/ 접속
2. 우측 상단 "로그인" → "회원가입" 클릭
3. 본인인증 (휴대폰 인증 또는 아이핀)
4. 회원정보 입력 및 약관 동의
5. 로그인 후 "OpenAPI" → "인증키 신청/관리" 이동
6. "인증키 신청" 클릭
7. 용도: "개인 프로젝트" 입력
8. 인증키 발급 및 복사 (예: `ABC123XYZ456DEF789GHI012JKL345MN`)

**데이터 수집 항목:**
- 한국 기준금리
- 환율 (USD/KRW)
- 소비자물가지수 (CPI)

**필수 환경 변수:**
```bash
ECOS_API_KEY=ABC123XYZ456DEF789GHI012JKL345MN
```

---

### 1.3 Fear & Greed Index (셀레니움 필요 없음)

**서비스**: CNN Fear & Greed Index
**비용**: 무료
**API 키**: 불필요

**데이터 수집 방법:**
- CNN 웹사이트에서 HTML 파싱
- 또는 공개 API 엔드포인트 사용
- **셀레니움 불필요** (requests 라이브러리만으로 수집 가능)

**URL:**
```
https://production.dataviz.cnn.io/index/fearandgreed/graphdata
```

**추가 설정 불필요**

---

### 1.4 Yahoo Finance (API 키 불필요)

**서비스**: 주식 시장 데이터
**비용**: 무료
**API 키**: 불필요

**데이터 수집 방법:**
- `yfinance` Python 라이브러리 사용
- 공개 API (회원가입 불필요)

**수집 데이터:**
- S&P 500 (^GSPC)
- NASDAQ (^IXIC)
- KOSPI (^KS11)
- KOSDAQ (^KQ11)

**추가 설정 불필요**

---

### 1.5 Telegram Bot (선택 사항)

**서비스**: 실시간 투자 알림
**비용**: 무료
**필수 여부**: 선택 (알림 기능 사용 시 필수)

**Bot 생성 및 토큰 발급:**

1. Telegram 앱 설치 및 계정 생성
2. Telegram에서 `@BotFather` 검색
3. `/newbot` 명령어 전송
4. Bot 이름 입력 (예: `Stock Intelligence Bot`)
5. Bot Username 입력 (예: `stock_intelligence_bot`)
6. Bot Token 복사 (예: `1234567890:ABCdefGHIjklMNOpqrsTUVwxyz`)
7. `/setdescription` 명령어로 Bot 설명 설정 (선택)

**Chat ID 확인:**

1. Telegram에서 `@userinfobot` 검색
2. `/start` 명령어 전송
3. Chat ID 복사 (예: `123456789`)

**또는 직접 확인:**

1. 생성한 Bot과 대화 시작 (`/start` 전송)
2. 브라우저에서 접속:
   ```
   https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates
   ```
3. `chat.id` 값 복사

**필수 환경 변수:**
```bash
TELEGRAM_BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
TELEGRAM_CHAT_ID=123456789
```

---

### 1.6 Email (SMTP) (선택 사항)

**서비스**: 이메일 알림 (Gmail 권장)
**비용**: 무료
**필수 여부**: 선택 (알림 기능 사용 시 필수)

#### Gmail 사용 시 (권장)

**App Password 생성:**

1. Gmail 계정 로그인
2. Google 계정 관리 (https://myaccount.google.com/) 이동
3. "보안" 메뉴 선택
4. "2단계 인증" 활성화 (필수)
   - 전화번호 등록
   - 인증 코드 입력
5. "보안" → "앱 비밀번호" 선택
6. "앱 선택" → "메일" 선택
7. "기기 선택" → "기타" 선택 → "Stock Intelligence" 입력
8. "생성" 클릭
9. 16자리 앱 비밀번호 복사 (예: `abcd efgh ijkl mnop`)
   - 공백 제거 후 사용: `abcdefghijklmnop`

**필수 환경 변수:**
```bash
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=abcdefghijklmnop
EMAIL_FROM=your-email@gmail.com
EMAIL_TO=recipient@example.com
```

#### Naver Mail 사용 시

```bash
SMTP_SERVER=smtp.naver.com
SMTP_PORT=587
SMTP_USERNAME=your-id@naver.com
SMTP_PASSWORD=your-password
```

**주의**: Naver는 앱 비밀번호가 아닌 실제 비밀번호 사용

---

### 1.7 SEC EDGAR (API 키 불필요)

**서비스**: 미국 기업 재무 데이터
**비용**: 무료
**API 키**: 불필요

**요구사항:**
- User-Agent 헤더 필수
  ```
  User-Agent: Stock-Intelligence-System your-email@example.com
  ```
- Rate Limit: 10 requests/second

**필수 환경 변수:**
```bash
SEC_USER_AGENT="Stock-Intelligence-System your-email@example.com"
```

---

## 2. 환경 변수 설정

### 2.1 `.env` 파일 생성

프로젝트 루트에 `.env` 파일 생성:

```bash
# 프로젝트 루트
cd /path/to/stock-intelligence-system

# .env 파일 생성
touch .env
chmod 600 .env  # 권한 설정 (본인만 읽기/쓰기)
```

### 2.2 `.env` 파일 내용

```bash
# ==============================================================================
# Database
# ==============================================================================
DATABASE_URL=postgresql://user:password@localhost:5432/stock_intelligence

# ==============================================================================
# API Keys
# ==============================================================================

# FRED API (필수)
FRED_API_KEY=your_fred_api_key_here

# ECOS API (필수)
ECOS_API_KEY=your_ecos_api_key_here

# SEC EDGAR (필수)
SEC_USER_AGENT=Stock-Intelligence-System your-email@example.com

# ==============================================================================
# Alerts (선택)
# ==============================================================================

# Telegram
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
TELEGRAM_CHAT_ID=your_telegram_chat_id_here
ALERT_TELEGRAM_ENABLED=true

# Email (Gmail)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your_app_password_here
EMAIL_FROM=your-email@gmail.com
EMAIL_TO=recipient@example.com
ALERT_EMAIL_ENABLED=true

# Alert Settings
ALERT_EXTREME_FEAR=25
ALERT_EXTREME_GREED=75
ALERT_SIGNAL_CHANGE=true
ALERT_MIN_INTERVAL=60

# ==============================================================================
# Logging
# ==============================================================================
LOG_DIR=logs
LOG_LEVEL=INFO

# ==============================================================================
# Scheduler
# ==============================================================================
SCHEDULER_TIMEZONE=Asia/Seoul

# ==============================================================================
# Security (선택)
# ==============================================================================
# Sentry DSN (오류 추적)
# SENTRY_DSN=your_sentry_dsn_here

# ==============================================================================
# Application
# ==============================================================================
ENVIRONMENT=production
DEBUG=false
```

### 2.3 환경 변수 로드 확인

```bash
python -c "
from dotenv import load_dotenv
import os

load_dotenv()

print('FRED_API_KEY:', 'OK' if os.getenv('FRED_API_KEY') else 'MISSING')
print('ECOS_API_KEY:', 'OK' if os.getenv('ECOS_API_KEY') else 'MISSING')
print('DATABASE_URL:', 'OK' if os.getenv('DATABASE_URL') else 'MISSING')
"
```

---

## 3. 데이터베이스 설정

### 3.1 PostgreSQL 설치

#### Ubuntu/Debian:
```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
```

#### macOS (Homebrew):
```bash
brew install postgresql@14
brew services start postgresql@14
```

#### Windows:
1. https://www.postgresql.org/download/windows/
2. 인스톨러 다운로드 및 실행
3. 비밀번호 설정 (기억 필수)

### 3.2 데이터베이스 생성

```bash
# PostgreSQL 접속
sudo -u postgres psql

# 데이터베이스 생성
CREATE DATABASE stock_intelligence;

# 사용자 생성 (선택)
CREATE USER stock_user WITH PASSWORD 'secure_password';

# 권한 부여
GRANT ALL PRIVILEGES ON DATABASE stock_intelligence TO stock_user;

# 종료
\q
```

### 3.3 Migration 실행

```bash
# 프로젝트 루트에서
cd /path/to/stock-intelligence-system

# Migration 파일 확인
ls scripts/migrations/

# Migration 실행 (순서대로)
psql -U stock_user -d stock_intelligence -f scripts/migrations/001_add_fear_greed_table.sql
psql -U stock_user -d stock_intelligence -f scripts/migrations/002_add_sec_edgar_tables.sql
psql -U stock_user -d stock_intelligence -f scripts/migrations/003_add_history_tables.sql
```

**또는 한 번에:**
```bash
for file in scripts/migrations/*.sql; do
    echo "Running $file..."
    psql -U stock_user -d stock_intelligence -f "$file"
done
```

### 3.4 테이블 확인

```bash
psql -U stock_user -d stock_intelligence

# 테이블 목록
\dt

# 예상 테이블:
# - fear_greed_index
# - sec_companies
# - sec_filings
# - sec_financial_facts
# - sec_institutional_holdings
# - market_data_history
# - signal_history
# - fear_greed_history
# - economic_data_history
# - backtest_history

# 종료
\q
```

---

## 4. 의존성 설치

### 4.1 Python 버전 확인

```bash
python --version
# Python 3.8 이상 필요
```

### 4.2 가상환경 생성 (권장)

```bash
# 가상환경 생성
python -m venv venv

# 가상환경 활성화
# Linux/macOS:
source venv/bin/activate

# Windows:
venv\Scripts\activate
```

### 4.3 패키지 설치

```bash
# requirements.txt 설치
pip install -r requirements.txt

# 설치 확인
pip list | grep -E "streamlit|sqlalchemy|pandas|fredapi"
```

**주요 패키지:**
- streamlit==1.28.2
- sqlalchemy==2.0.23
- pandas==2.1.3
- fredapi==0.5.1
- yfinance==0.2.32
- apscheduler==3.10.4
- python-telegram-bot==20.7

---

## 5. 로그 디렉토리 설정

### 5.1 로그 디렉토리 생성

```bash
# 프로젝트 루트에서
mkdir -p logs
chmod 755 logs
```

### 5.2 로그 파일 확인

로그 시스템이 자동으로 생성하는 파일:
- `logs/stock_intelligence.log` - 전체 로그
- `logs/errors.log` - 오류 로그만

### 5.3 로그 로테이션 설정 (선택)

로그 파일이 자동으로 로테이션됩니다:
- 파일 크기 제한: 10 MB
- 백업 개수: 10개 (전체), 5개 (오류)

---

## 6. 초기 데이터 수집

### 6.1 수동 데이터 수집 테스트

각 데이터 소스별로 수집 테스트:

```bash
# Fear & Greed Index
python -c "
from app.collectors.fear_greed_collector import FearGreedCollector
import asyncio

async def test():
    collector = FearGreedCollector()
    data = await collector.collect()
    print(f'Fear & Greed Score: {data.get(\"score\")}')

asyncio.run(test())
"

# FRED API
python -c "
from fredapi import Fred
import os
from dotenv import load_dotenv

load_dotenv()
fred = Fred(api_key=os.getenv('FRED_API_KEY'))
rate = fred.get_series_latest_release('FEDFUNDS')
print(f'US Fed Rate: {rate.iloc[-1]}%')
"

# Yahoo Finance
python -c "
import yfinance as yf
sp500 = yf.Ticker('^GSPC')
data = sp500.history(period='1d')
print(f'S&P 500: {data[\"Close\"].iloc[-1]:.2f}')
"
```

### 6.2 초기 히스토리 데이터 수집

**1년치 과거 데이터 수집** (백테스팅용):

```bash
# 스크립트 작성
cat > scripts/collect_historical_data.py << 'EOF'
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
from app.database.history_db import get_history_db

db = get_history_db()

# 1년치 데이터
end_date = datetime.now()
start_date = end_date - timedelta(days=365)

print("Collecting historical market data...")

# S&P 500
sp500 = yf.Ticker("^GSPC")
df_sp500 = sp500.history(start=start_date, end=end_date)

# NASDAQ
nasdaq = yf.Ticker("^IXIC")
df_nasdaq = nasdaq.history(start=start_date, end=end_date)

# KOSPI
kospi = yf.Ticker("^KS11")
df_kospi = kospi.history(start=start_date, end=end_date)

# Save to database
for date in df_sp500.index:
    market_data = {
        'sp500': {
            'close': df_sp500.loc[date, 'Close'],
            'open': df_sp500.loc[date, 'Open'],
            'high': df_sp500.loc[date, 'High'],
            'low': df_sp500.loc[date, 'Low'],
            'volume': df_sp500.loc[date, 'Volume']
        },
        'nasdaq': {
            'close': df_nasdaq.loc[date, 'Close'] if date in df_nasdaq.index else None
        },
        'kospi': {
            'close': df_kospi.loc[date, 'Close'] if date in df_kospi.index else None
        }
    }

    db.save_market_data(market_data, date=date.to_pydatetime())

print(f"✅ Collected {len(df_sp500)} days of market data")
EOF

# 실행
python scripts/collect_historical_data.py
```

---

## 7. 스케줄러 설정

### 7.1 스케줄러 테스트

```bash
# 스케줄러 테스트 실행 (1분간)
timeout 60 python scripts/run_scheduler.py
```

### 7.2 systemd 서비스 설정 (Linux)

**서비스 파일 생성:**

```bash
sudo nano /etc/systemd/system/stock-intelligence-scheduler.service
```

**내용:**

```ini
[Unit]
Description=Stock Intelligence Scheduler
After=network.target postgresql.service

[Service]
Type=simple
User=your_username
WorkingDirectory=/path/to/stock-intelligence-system
Environment="PATH=/path/to/stock-intelligence-system/venv/bin"
EnvironmentFile=/path/to/stock-intelligence-system/.env
ExecStart=/path/to/stock-intelligence-system/venv/bin/python scripts/run_scheduler.py
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**서비스 활성화:**

```bash
# 서비스 리로드
sudo systemctl daemon-reload

# 서비스 시작
sudo systemctl start stock-intelligence-scheduler

# 서비스 상태 확인
sudo systemctl status stock-intelligence-scheduler

# 부팅 시 자동 시작
sudo systemctl enable stock-intelligence-scheduler

# 로그 확인
sudo journalctl -u stock-intelligence-scheduler -f
```

### 7.3 스케줄 확인

스케줄러가 다음 시간에 실행됩니다 (KST):

- **06:00** - Fear & Greed Index 수집
- **07:00** - FRED 데이터 수집
- **08:30** - 투자 신호 생성 → Telegram 알림
- **09:00** - ECOS 데이터 수집 + 일일 브리핑 → Telegram + Email
- **09:30** - 전체 분석 실행
- **15:40** - 오후 브리핑 → Telegram
- **월요일 08:00** - SEC EDGAR 주간 데이터 수집

---

## 8. 알림 시스템 설정

### 8.1 Telegram Bot 테스트

```bash
python scripts/test_alerts.py
```

**확인사항:**
- Telegram으로 테스트 메시지 수신
- Email로 테스트 메시지 수신

### 8.2 알림 설정 커스터마이징

`.env` 파일에서 설정 조정:

```bash
# 극단 시장 임계값
ALERT_EXTREME_FEAR=25        # 25 이하에서 알림
ALERT_EXTREME_GREED=75       # 75 이상에서 알림

# 신호 변경 알림
ALERT_SIGNAL_CHANGE=true     # 투자 신호 변경 시 알림

# Rate limiting (분 단위)
ALERT_MIN_INTERVAL=60        # 같은 알림은 60분에 1번만
```

---

## 9. 테스트 체크리스트

### 9.1 API 연결 테스트

```bash
# FRED
python -c "from fredapi import Fred; import os; from dotenv import load_dotenv; load_dotenv(); fred = Fred(api_key=os.getenv('FRED_API_KEY')); print('FRED:', fred.get_series_latest_release('FEDFUNDS').iloc[-1])"

# ECOS
# (ECOS API 테스트 스크립트 실행 필요)

# Yahoo Finance
python -c "import yfinance as yf; print('Yahoo:', yf.Ticker('^GSPC').history(period='1d')['Close'].iloc[-1])"
```

### 9.2 데이터베이스 테스트

```bash
python scripts/test_history_db.py
```

### 9.3 백테스팅 테스트

```bash
python scripts/test_backtesting.py
```

### 9.4 알림 테스트

```bash
python scripts/test_alerts.py
```

### 9.5 Dashboard 테스트

```bash
streamlit run app/dashboard/main.py
```

브라우저에서 http://localhost:8501 접속하여 모든 페이지 확인:
- ✅ 개요
- ✅ 투자 신호
- ✅ 경제 지표
- ✅ 분석 차트
- ✅ 백테스팅
- ✅ 로그
- ✅ 설정

---

## 10. 프로덕션 실행

### 10.1 스케줄러 시작

```bash
# Foreground (테스트용)
python scripts/run_scheduler.py

# Background (프로덕션)
nohup python scripts/run_scheduler.py > scheduler.log 2>&1 &

# systemd (권장)
sudo systemctl start stock-intelligence-scheduler
```

### 10.2 Dashboard 시작

```bash
# Development
streamlit run app/dashboard/main.py

# Production (포트 지정)
streamlit run app/dashboard/main.py --server.port 8501 --server.address 0.0.0.0

# Background
nohup streamlit run app/dashboard/main.py --server.port 8501 --server.address 0.0.0.0 > dashboard.log 2>&1 &
```

### 10.3 프로세스 확인

```bash
# 실행 중인 프로세스 확인
ps aux | grep -E "scheduler|streamlit"

# 포트 확인
lsof -i :8501
```

### 10.4 로그 모니터링

```bash
# 실시간 로그 확인
tail -f logs/stock_intelligence.log

# 오류 로그 확인
tail -f logs/errors.log

# systemd 로그 (스케줄러)
sudo journalctl -u stock-intelligence-scheduler -f
```

---

## 📝 체크리스트 요약

프로덕션 배포 전 확인사항:

### API 키 (필수)
- [ ] FRED API 키 발급 및 설정
- [ ] ECOS API 키 발급 및 설정
- [ ] SEC User-Agent 설정

### API 키 (선택)
- [ ] Telegram Bot Token 및 Chat ID 설정
- [ ] Gmail App Password 설정
- [ ] Email 수신자 설정

### 데이터베이스
- [ ] PostgreSQL 설치 및 실행
- [ ] 데이터베이스 생성
- [ ] Migration 실행 (3개 파일)
- [ ] 테이블 생성 확인

### 환경 설정
- [ ] .env 파일 생성 및 권한 설정
- [ ] 환경 변수 로드 확인
- [ ] 로그 디렉토리 생성

### 의존성
- [ ] Python 3.8+ 설치
- [ ] 가상환경 생성
- [ ] requirements.txt 설치

### 테스트
- [ ] API 연결 테스트 (FRED, ECOS, Yahoo)
- [ ] 데이터베이스 테스트
- [ ] 백테스팅 테스트
- [ ] 알림 테스트
- [ ] Dashboard 테스트

### 초기 데이터
- [ ] 1년치 히스토리 데이터 수집
- [ ] Fear & Greed 초기 데이터 수집

### 프로덕션
- [ ] 스케줄러 실행 (systemd 권장)
- [ ] Dashboard 실행
- [ ] 로그 모니터링 설정
- [ ] 백업 설정 (선택)

---

## 🚨 문제 해결

### API 오류

**FRED API 오류 (400 Bad Request):**
- API 키 확인: 올바른 키인지 재확인
- Rate limit 확인: 120 requests/minute 초과 시 대기

**ECOS API 오류 (인증 실패):**
- 인증키 재발급: 한국은행 ECOS 사이트에서 재발급
- 일일 한도 확인: 100 requests/day

### 데이터베이스 오류

**Connection refused:**
```bash
sudo systemctl start postgresql
```

**권한 오류:**
```bash
GRANT ALL PRIVILEGES ON DATABASE stock_intelligence TO stock_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO stock_user;
```

### Telegram 알림 오류

**Bot not receiving messages:**
- Bot과 대화 시작: `/start` 명령어 전송
- Chat ID 재확인: @userinfobot으로 확인

### Email 알림 오류

**SMTPAuthenticationError:**
- Gmail: 앱 비밀번호 사용 (실제 비밀번호 X)
- 2단계 인증 확인: 필수 활성화

---

## 📞 지원

문제 발생 시:
1. `logs/errors.log` 확인
2. Dashboard → 로그 페이지에서 오류 확인
3. GitHub Issues에 문의

---

**업데이트**: 2025-11-22
**버전**: 1.0.0
