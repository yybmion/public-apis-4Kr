# Phase 1 설치 및 테스트 가이드

Phase 1에서 추가된 거시경제 데이터 수집기(FRED, ECOS, Fear & Greed Index)를 설정하고 테스트하는 가이드입니다.

---

## 📋 목차

1. [API 키 발급](#1-api-키-발급)
2. [환경 변수 설정](#2-환경-변수-설정)
3. [패키지 설치](#3-패키지-설치)
4. [데이터베이스 마이그레이션](#4-데이터베이스-마이그레이션)
5. [데이터 수집 테스트](#5-데이터-수집-테스트)
6. [문제 해결](#6-문제-해결)

---

## 1. API 키 발급

### 1.1 FRED API Key (필수)

**FRED (Federal Reserve Economic Data)**는 미국 연방준비은행의 공식 경제 데이터 API입니다.

#### 발급 방법:

1. **FRED 웹사이트 접속**
   - https://fred.stlouisfed.org/

2. **계정 생성**
   - 우측 상단 "My Account" → "Create Account" 클릭
   - 이메일, 비밀번호 입력하여 무료 계정 생성

3. **API Key 요청**
   - 로그인 후 https://fredaccount.stlouisfed.org/apikeys 접속
   - "Request API Key" 버튼 클릭
   - 간단한 정보 입력 (이름, 이메일, 사용 목적)

4. **API Key 확인**
   - 즉시 발급됨 (예: `abcd1234efgh5678ijkl9012mnop3456`)
   - 이메일로도 전송됨

**제한 사항**:
- ✅ **무료**
- ✅ **120 requests/minute**
- ✅ **800,000+ 경제 지표 접근 가능**

**공식 문서**:
- https://fred.stlouisfed.org/docs/api/fred/

---

### 1.2 ECOS API Key (필수)

**ECOS (Economic Statistics System)**는 한국은행의 공식 경제통계 API입니다.

#### 발급 방법:

1. **ECOS 웹사이트 접속**
   - https://ecos.bok.or.kr/

2. **API 신청**
   - 상단 메뉴 "Open API" → "인증키 신청/조회" 클릭
   - 또는 직접 접속: https://ecos.bok.or.kr/api/#/

3. **신청서 작성**
   - 이름, 이메일, 전화번호 입력
   - 이용 목적: "연구/학습" 또는 "개인 프로젝트"
   - 약관 동의

4. **인증키 발급**
   - 즉시 발급됨 (예: `SAMPLE_KEY_1234567890`)
   - 신청 페이지에서 바로 확인 가능

**제한 사항**:
- ✅ **무료**
- ✅ **1일 10,000회 호출 가능**
- ✅ **100,000+ 한국 경제 지표 접근 가능**

**공식 문서**:
- https://ecos.bok.or.kr/api/#/UserGuide

---

### 1.3 Fear & Greed Index (API Key 불필요)

**CNN Fear & Greed Index**는 API 키 없이 사용 가능한 공개 엔드포인트입니다.

- ✅ **무료**
- ✅ **API 키 불필요**
- ✅ **일일 시장 심리 데이터**

**데이터 소스**:
- https://production.dataviz.cnn.io/index/fearandgreed/graphdata

---

## 2. 환경 변수 설정

### 2.1 `.env` 파일 수정

프로젝트 루트 디렉토리의 `.env` 파일에 API 키를 추가합니다:

```bash
# 1. .env 파일 열기
cd /home/user/public-apis-4Kr
nano .env
```

### 2.2 API 키 추가

`.env` 파일에 다음 라인을 추가하세요:

```bash
# =============================================================================
# Phase 1: Macroeconomic Data APIs
# =============================================================================

# FRED API (Federal Reserve Economic Data)
# Get your key at: https://fredaccount.stlouisfed.org/apikeys
FRED_API_KEY=your_fred_api_key_here

# ECOS API (Bank of Korea Economic Statistics)
# Get your key at: https://ecos.bok.or.kr/api/#/
ECOS_API_KEY=your_ecos_api_key_here

# Fear & Greed Index (No API key required)
# Public endpoint - no configuration needed
```

**예시**:
```bash
FRED_API_KEY=abcd1234efgh5678ijkl9012mnop3456
ECOS_API_KEY=SAMPLE_KEY_1234567890ABCDEF
```

---

## 3. 패키지 설치

Phase 1에 필요한 Python 패키지를 설치합니다.

### 3.1 Python 환경 확인

```bash
python --version  # Python 3.10+ 필요
```

### 3.2 패키지 설치

```bash
# 프로젝트 루트 디렉토리에서 실행
cd /home/user/public-apis-4Kr

# 필수 패키지 설치
pip install fredapi==0.5.1
pip install aiohttp==3.9.1
pip install pandas
pip install pydantic
pip install pydantic-settings

# 또는 requirements.txt 전체 설치
pip install -r requirements.txt
```

### 3.3 설치 확인

```bash
python -c "import fredapi; print('fredapi version:', fredapi.__version__)"
python -c "import aiohttp; print('aiohttp installed successfully')"
```

---

## 4. 데이터베이스 마이그레이션

Phase 1에서 추가된 6개 테이블을 생성합니다.

### 4.1 PostgreSQL 연결 확인

```bash
# DATABASE_URL 환경 변수 확인
echo $DATABASE_URL
```

### 4.2 마이그레이션 실행

**방법 1: psql 직접 실행** (권장)

```bash
# PostgreSQL에 연결
psql $DATABASE_URL

# 마이그레이션 스크립트 실행
\i /home/user/public-apis-4Kr/scripts/migrations/001_add_phase1_tables.sql

# 테이블 생성 확인
SELECT table_name FROM information_schema.tables
WHERE table_schema = 'public' AND table_name IN (
  'macro_indicators', 'yield_curves', 'economic_snapshots',
  'fear_greed_index', 'market_sentiments', 'sentiment_history'
);

# 종료
\q
```

**방법 2: Python 스크립트 실행**

```bash
cd /home/user/public-apis-4Kr
python scripts/run_migration.py
```

### 4.3 생성된 테이블 확인

다음 6개 테이블이 생성되어야 합니다:

1. ✅ `macro_indicators` - FRED/ECOS 시계열 데이터
2. ✅ `yield_curves` - 수익률 곡선 및 경기 침체 신호
3. ✅ `economic_snapshots` - 일일 경제 스냅샷
4. ✅ `fear_greed_index` - Fear & Greed Index
5. ✅ `market_sentiments` - 통합 시장 심리
6. ✅ `sentiment_history` - 심리 지표 이력

---

## 5. 데이터 수집 테스트

각 수집기를 개별적으로 테스트합니다.

### 5.1 FRED API 수집기 테스트

```bash
cd /home/user/public-apis-4Kr

# Federal Funds Rate 수집 테스트
python -m pytest tests/test_fred_collector.py::TestFredCollector::test_collect_real_data -v

# Yield Curve 계산 테스트
python -m pytest tests/test_fred_collector.py::TestFredCollector::test_yield_curve -v
```

**예상 결과**:
```
✅ FRED API 연결 성공
✅ Federal Funds Rate 데이터 수집 완료
✅ Yield Curve 계산 완료
✅ Recession Signal 탐지 완료
```

### 5.2 ECOS API 수집기 테스트

```bash
# 한국 기준금리 수집 테스트
python -m pytest tests/test_ecos_collector.py::TestEcosCollector::test_collect_real_data -v

# 경제 스냅샷 생성 테스트
python -m pytest tests/test_ecos_collector.py::TestEcosCollector::test_economic_snapshot -v
```

**예상 결과**:
```
✅ ECOS API 연결 성공
✅ 한국 기준금리 데이터 수집 완료
✅ USD/KRW 환율 데이터 수집 완료
✅ 경제 스냅샷 생성 완료
```

### 5.3 Fear & Greed Index 수집기 테스트

```bash
# Fear & Greed Index 수집 테스트
python -m pytest tests/test_fear_greed_collector.py::TestFearGreedCollector::test_collect_real_data -v

# 투자 신호 생성 테스트
python -m pytest tests/test_fear_greed_collector.py::TestFearGreedCollector::test_investment_signal -v
```

**예상 결과**:
```
✅ Fear & Greed Index API 연결 성공
✅ 현재 점수: 45.5 (Neutral)
✅ 투자 신호: HOLD
✅ 30일 추세 분석 완료
```

### 5.4 통합 테스트

모든 수집기를 한번에 테스트:

```bash
python -m pytest tests/test_integration_collectors.py -v
```

---

## 6. 문제 해결

### 6.1 FRED API 오류

**오류**: `fredapi.exceptions.InvalidApiKey`

**해결책**:
1. `.env` 파일에서 `FRED_API_KEY` 확인
2. API 키가 올바른지 확인 (32자리 영숫자)
3. https://fredaccount.stlouisfed.org/apikeys 에서 키 재확인

---

**오류**: `Rate limit exceeded`

**해결책**:
- FRED는 분당 120회 제한
- 코드에 `time.sleep(0.5)` 추가하여 호출 간격 조정

---

### 6.2 ECOS API 오류

**오류**: `Authentication failed`

**해결책**:
1. `.env` 파일에서 `ECOS_API_KEY` 확인
2. https://ecos.bok.or.kr/api/#/ 에서 키 재발급
3. 키 발급 후 5분 대기 (활성화 시간)

---

**오류**: `No data available`

**해결책**:
- 일부 지표는 월별/분기별 업데이트
- 최근 날짜 대신 1개월 전 날짜로 시도
- 공식 문서에서 업데이트 주기 확인

---

### 6.3 Fear & Greed Index 오류

**오류**: `Connection timeout`

**해결책**:
- CNN 서버가 일시적으로 응답 안 할 수 있음
- 1분 후 재시도
- VPN 사용 시 비활성화

---

**오류**: `Invalid JSON response`

**해결책**:
- CNN이 API 구조를 변경했을 수 있음
- `fear_greed_collector.py`의 파싱 로직 확인
- GitHub Issues에 보고

---

### 6.4 데이터베이스 오류

**오류**: `relation "macro_indicators" does not exist`

**해결책**:
1. 마이그레이션이 실행되지 않음
2. 4.2 단계 다시 실행
3. `\dt` 명령어로 테이블 목록 확인

---

**오류**: `duplicate key value violates unique constraint`

**해결책**:
- 같은 날짜의 데이터를 중복 삽입하려 함
- `ON CONFLICT DO UPDATE` 사용
- 또는 기존 데이터 삭제 후 재수집

---

## 7. 다음 단계

Phase 1 테스트가 완료되면:

1. **자동화 설정**
   - 매일 자동으로 데이터 수집 (cron job 또는 AWS Lambda)

2. **대시보드 구현**
   - Streamlit으로 경제 지표 시각화
   - Yield Curve 그래프
   - Fear & Greed Index 히스토리

3. **알림 시스템**
   - 경기 침체 신호 발생 시 알림
   - 극단적 공포/탐욕 시 알림

4. **Phase 2 진행**
   - 추가 데이터 소스 통합 (Whale Wisdom, SEC EDGAR 등)

---

## 📞 지원

문제가 발생하면:
1. GitHub Issues에 보고
2. PHASE1_INTEGRATION_SUMMARY.md 참조
3. 공식 API 문서 확인

---

**마지막 업데이트**: 2025-11-22
**작성자**: AI Assistant
