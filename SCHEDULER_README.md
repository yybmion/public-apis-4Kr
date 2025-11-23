# 자동화 스케줄러 사용 가이드

## 📋 개요

Stock Intelligence System의 자동화 스케줄러는 데이터 수집, 분석, 신호 생성을 자동으로 실행합니다.

## ⏰ 스케줄

| 시간 | 작업 | 설명 |
|------|------|------|
| **06:00** | Fear & Greed Index 수집 | 미국 장 마감 후 시장 심리 지표 |
| **07:00** | FRED 경제 지표 수집 | 미국 금리, 수익률 곡선 등 |
| **08:30** | 투자 신호 생성 | 수집된 데이터 기반 매수/매도 신호 |
| **09:00** | ECOS + 개장 전 브리핑 | 한국 경제 지표 + 일일 브리핑 |
| **09:30** | 전체 분석 실행 | 시장 상관관계 + 경제 분석 |
| **15:40** | 마감 후 브리핑 | 장 마감 후 일일 브리핑 |
| **월 08:00** | SEC EDGAR 주간 업데이트 | 미국 기업 재무 데이터 (매주 월요일) |

## 🚀 사용 방법

### 1. 의존성 설치

```bash
pip install -r requirements.txt
```

주요 패키지:
- `apscheduler==3.10.4` - 스케줄링
- `aiohttp==3.9.1` - 비동기 HTTP
- `fredapi==0.5.1` - FRED API

### 2. 환경 변수 설정

`.env` 파일을 생성하고 API 키를 설정하세요:

```bash
# FRED API (필수는 아님)
FRED_API_KEY=your_fred_api_key_here

# ECOS API (필수는 아님)
ECOS_API_KEY=your_ecos_api_key_here

# Fear & Greed Index는 API 키 불필요
# SEC EDGAR는 API 키 불필요
```

**API 키 발급:**
- FRED: https://fredaccount.stlouisfed.org/apikeys
- ECOS: https://ecos.bok.or.kr/api/

### 3. 스케줄러 실행

#### 옵션 1: 일반 실행

```bash
python scripts/run_scheduler.py
```

#### 옵션 2: 초기 데이터 수집 후 실행

```bash
python scripts/run_scheduler.py --init
```

첫 실행 시 `--init` 옵션을 사용하면 즉시 데이터를 수집합니다.

#### 옵션 3: 백그라운드 실행 (Linux/Mac)

```bash
nohup python scripts/run_scheduler.py --init > scheduler.log 2>&1 &
```

#### 옵션 4: systemd 서비스 (Linux)

`/etc/systemd/system/stock-scheduler.service` 생성:

```ini
[Unit]
Description=Stock Intelligence System Scheduler
After=network.target

[Service]
Type=simple
User=your_user
WorkingDirectory=/path/to/public-apis-4Kr
ExecStart=/usr/bin/python3 /path/to/public-apis-4Kr/scripts/run_scheduler.py --init
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

서비스 시작:

```bash
sudo systemctl enable stock-scheduler
sudo systemctl start stock-scheduler
sudo systemctl status stock-scheduler
```

로그 확인:

```bash
sudo journalctl -u stock-scheduler -f
```

### 4. 종료

**스케줄러 종료:**

```bash
Ctrl+C
```

스케줄러는 안전하게 종료됩니다 (진행 중인 작업 완료 후).

## 🧪 테스트

### 즉시 실행 테스트

```bash
python scripts/test_scheduler.py --mode instant
```

모든 작업을 즉시 실행하여 테스트합니다.

### 짧은 간격 테스트 (10초)

```bash
python scripts/test_scheduler.py --mode schedule
```

10초마다 작업을 실행하여 스케줄링을 테스트합니다.

### 실제 스케줄 테스트

```bash
python scripts/test_scheduler.py --mode daemon
```

실제 스케줄 시간에 맞춰 작업을 실행합니다.

## 📊 수집되는 데이터

### 1. Fear & Greed Index
- **출처**: CNN Fear & Greed Index
- **주기**: 매일
- **API 키**: 불필요
- **데이터**: 시장 심리 점수 (0-100)

### 2. FRED 경제 지표
- **출처**: Federal Reserve Economic Data
- **주기**: 매일
- **API 키**: 필요 (무료)
- **데이터**:
  - Federal Funds Rate (기준금리)
  - 10-Year Treasury Yield (10년물 국채 수익률)
  - 2-Year Treasury Yield (2년물 국채 수익률)
  - Yield Curve (수익률 곡선)

### 3. ECOS 경제 지표
- **출처**: 한국은행 경제통계시스템
- **주기**: 매일
- **API 키**: 필요 (무료)
- **데이터**:
  - 한국 기준금리
  - USD/KRW 환율
  - 경제 스냅샷

### 4. SEC EDGAR
- **출처**: U.S. Securities and Exchange Commission
- **주기**: 매주 월요일
- **API 키**: 불필요
- **데이터**:
  - 10-K, 10-Q 공시
  - XBRL 재무 데이터
  - 기관 투자자 보유 현황 (13F)

## 🎯 생성되는 분석 결과

### 1. 시장 상관관계 분석
- S&P 500 → KOSPI 예측 (상관계수 0.85)
- NASDAQ → KOSDAQ 예측 (상관계수 0.81)
- 이동평균선 기반 매수/매도 신호

### 2. 경제 지표 분석
- 금리 분석 (미국-한국 금리 차)
- 수익률 곡선 분석 (경기 침체 예측)
- 환율 분석 (원화 강세/약세)

### 3. 투자 신호
- **7단계 신호**: STRONG_BUY, BUY, WEAK_BUY, HOLD, WEAK_SELL, SELL, STRONG_SELL
- **신뢰도**: 0-100%
- **액션 플랜**: 자산 배분, 추천 섹터, 리스크 관리

### 4. 일일 브리핑
- 시장 현황 요약
- 투자 신호 및 근거
- 추천 액션 및 섹터
- 리스크 관리 전략

## 📁 파일 구조

```
app/
└── scheduler/
    ├── __init__.py
    ├── collection_jobs.py    # 데이터 수집 작업
    ├── analysis_jobs.py      # 분석 작업
    └── scheduler.py          # 스케줄러 메인

scripts/
├── run_scheduler.py          # 프로덕션 실행
└── test_scheduler.py         # 테스트 스크립트
```

## 🔧 커스터마이징

### 스케줄 변경

`app/scheduler/scheduler.py`의 `_configure_scheduler()` 메서드에서 스케줄을 변경할 수 있습니다:

```python
# 예: Fear & Greed를 매일 18:00에 수집
self.scheduler.add_job(
    self.job_collect_fear_greed,
    CronTrigger(hour=18, minute=0),  # 18:00으로 변경
    id='fear_greed_collection',
    name='Fear & Greed Index 수집'
)
```

### 수집 종목 변경

SEC EDGAR 수집 종목을 변경하려면:

```python
# app/scheduler/collection_jobs.py
async def collect_sec_edgar_data(self, tickers: list = None):
    if tickers is None:
        tickers = ['AAPL', 'TSLA', 'MSFT', 'GOOGL', 'AMZN']  # 여기를 수정
```

## ⚠️  주의사항

### 1. API 키 없이 실행 가능
- Fear & Greed Index: API 키 불필요
- SEC EDGAR: API 키 불필요
- FRED/ECOS: API 키가 없으면 해당 작업은 스킵됨

### 2. Rate Limit
- SEC EDGAR: 10 requests/second (자동 제한)
- FRED: 120 requests/minute (자동 제한)
- ECOS: 100 requests/day (수동 관리 필요)

### 3. 네트워크
- 외부 API 접근이 필요합니다
- 방화벽/프록시 설정 확인

### 4. 타임존
- 모든 시간은 시스템 로컬 타임존 기준
- 한국 시간(KST) 기준으로 설정되어 있음

## 📝 로그

스케줄러 실행 로그는 표준 출력으로 출력됩니다:

```
2025-11-22 06:00:00 - INFO - 🎯 [JOB] Fear & Greed Index 수집 시작
2025-11-22 06:00:02 - INFO - ✅ Fear & Greed 수집 완료: Score=35.5, Rating=Fear
```

로그 파일로 저장하려면:

```bash
python scripts/run_scheduler.py > scheduler.log 2>&1
```

## 🆘 문제 해결

### Q1: "ModuleNotFoundError: No module named 'apscheduler'"

```bash
pip install apscheduler==3.10.4
```

### Q2: "API key not configured"

`.env` 파일에 API 키를 설정하세요. 또는 API 키 없이 실행 가능한 수집기만 사용하세요 (Fear & Greed, SEC EDGAR).

### Q3: 스케줄러가 실행되지 않음

- Python 버전 확인: 3.8 이상 필요
- 의존성 설치 확인: `pip install -r requirements.txt`
- 로그 확인

### Q4: 데이터가 수집되지 않음

- 인터넷 연결 확인
- API 키 유효성 확인
- 방화벽/프록시 설정 확인

## 📚 참고 자료

- APScheduler 문서: https://apscheduler.readthedocs.io/
- FRED API: https://fred.stlouisfed.org/docs/api/
- ECOS API: https://ecos.bok.or.kr/api/
- SEC EDGAR: https://www.sec.gov/edgar

## 🔄 업데이트

스케줄러를 업데이트하려면:

```bash
git pull origin main
pip install -r requirements.txt --upgrade
```

서비스 재시작 (systemd 사용 시):

```bash
sudo systemctl restart stock-scheduler
```
