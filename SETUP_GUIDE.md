# Stock Intelligence System - Setup Guide

한국 주식 자동매매 지원 시스템 설치 및 실행 가이드

## 목차
1. [시스템 요구사항](#시스템-요구사항)
2. [환경 설정](#환경-설정)
3. [실행 방법](#실행-방법)
4. [API 사용법](#api-사용법)
5. [문제 해결](#문제-해결)

---

## 시스템 요구사항

### 필수 요구사항
- **Python**: 3.10 이상
- **PostgreSQL**: 15 이상
- **Redis**: 7 이상 (선택사항, 캐싱용)
- **Docker** (선택사항, 컨테이너 실행용)

### 권장 사양
- RAM: 최소 4GB (8GB 권장)
- Disk: 최소 10GB 여유 공간

---

## 환경 설정

### 1. 프로젝트 클론
```bash
git clone <repository-url>
cd public-apis-4Kr
```

### 2. Python 가상환경 생성
```bash
python -m venv venv

# macOS/Linux
source venv/bin/activate

# Windows
venv\Scripts\activate
```

### 3. 의존성 패키지 설치
```bash
pip install -r requirements.txt
```

### 4. 환경 변수 설정
```bash
# .env.example을 .env로 복사
cp .env.example .env

# .env 파일을 편집기로 열어 API 키 입력
nano .env  # 또는 vim .env
```

#### 필수 API 키 발급

1. **한국투자증권 KIS API**
   - https://apiportal.koreainvestment.com
   - 회원가입 후 APP KEY, APP SECRET 발급
   - .env 파일에 입력:
     ```
     KIS_APP_KEY=your_kis_app_key_here
     KIS_APP_SECRET=your_kis_app_secret_here
     ```

2. **DART API** (재무제표용)
   - https://opendart.fss.or.kr
   - API 인증키 신청
   - .env 파일에 입력:
     ```
     DART_API_KEY=your_dart_api_key_here
     ```

3. **한국은행 ECOS API** (경제지표용)
   - https://ecos.bok.or.kr
   - 인증키 신청
   - .env 파일에 입력:
     ```
     ECOS_API_KEY=your_ecos_api_key_here
     ```

### 5. 데이터베이스 초기화

#### Option A: Local PostgreSQL 사용
```bash
# PostgreSQL 설치 (macOS)
brew install postgresql@15

# PostgreSQL 시작
brew services start postgresql@15

# 데이터베이스 생성
psql -U postgres
CREATE DATABASE stockdb;
CREATE USER stockuser WITH PASSWORD 'stockpass';
GRANT ALL PRIVILEGES ON DATABASE stockdb TO stockuser;
\q

# 테이블 생성
psql -U stockuser -d stockdb -f scripts/init_db.sql
```

#### Option B: Docker 사용 (권장)
```bash
cd docker
docker-compose up -d db cache
```

---

## 실행 방법

### Method 1: Docker Compose (가장 쉬움)

모든 서비스를 한 번에 실행:
```bash
cd docker
docker-compose up -d

# 로그 확인
docker-compose logs -f

# 중지
docker-compose down
```

서비스 접속:
- **API 문서**: http://localhost:8000/docs
- **대시보드**: http://localhost:8501
- **PostgreSQL**: localhost:5432
- **Redis**: localhost:6379

### Method 2: 로컬 실행

#### 1. API 서버 실행
```bash
# 터미널 1
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### 2. 대시보드 실행
```bash
# 터미널 2
streamlit run dashboard/app.py
```

#### 3. 브라우저에서 접속
- API 문서: http://localhost:8000/docs
- 대시보드: http://localhost:8501

---

## API 사용법

### Health Check
```bash
curl http://localhost:8000/health
```

### 종목 목록 조회
```bash
curl http://localhost:8000/api/v1/stocks?limit=10
```

### 특정 종목 조회
```bash
# 삼성전자 (005930)
curl http://localhost:8000/api/v1/stocks/005930
```

### 실시간 데이터 수집
```bash
# 삼성전자 데이터 수집
curl -X POST http://localhost:8000/api/v1/stocks/005930/collect
```

### 미국 시장 데이터 수집
```bash
curl -X POST http://localhost:8000/api/v1/market/us/collect
```

### 시장 현황 조회
```bash
curl http://localhost:8000/api/v1/market/overview
```

---

## 데이터 수집 테스트

### 1. KIS API 테스트
```bash
python -m pytest tests/test_collectors/test_kis_collector.py -v
```

### 2. Yahoo Finance 테스트
```bash
python -c "
from app.collectors.yahoo_collector import YahooCollector
import asyncio

async def test():
    collector = YahooCollector()
    data = await collector.collect(symbol='^GSPC')
    print(f'S&P 500: {data[\"close\"]}')
    print(f'Signal: {data[\"above_ma\"]}')

asyncio.run(test())
"
```

### 3. 전체 시스템 테스트
```bash
# 미국 시장 데이터 수집
curl -X POST http://localhost:8000/api/v1/market/us/collect

# 결과 확인
curl http://localhost:8000/api/v1/market/us
```

---

## 주요 기능

### ✅ 현재 구현된 기능 (Week 1-2)

- [x] 프로젝트 구조 생성
- [x] 데이터베이스 스키마 설계
- [x] KIS API 연동 (한국 주식 시세)
- [x] Yahoo Finance 연동 (미국 지수)
- [x] DART API 연동 (재무제표)
- [x] FastAPI 백엔드 서버
- [x] Streamlit 대시보드
- [x] Docker 컨테이너 지원
- [x] 설정 관리 시스템
- [x] 로깅 시스템

### 🚧 다음 구현 예정 (Week 3-4)

- [ ] 기술적 지표 계산 (MA, RSI, MACD)
- [ ] S&P 500 신호 생성 시스템
- [ ] 실시간 차트 시각화
- [ ] 종목 검색 기능
- [ ] 알림 시스템

---

## 문제 해결

### 1. API 키 오류
```
Error: KIS_APP_KEY is required
```
**해결**: .env 파일에 올바른 API 키를 입력했는지 확인

### 2. 데이터베이스 연결 실패
```
Error: could not connect to server
```
**해결**:
```bash
# PostgreSQL이 실행 중인지 확인
brew services list  # macOS
sudo systemctl status postgresql  # Linux

# Docker 사용 시
docker-compose ps
```

### 3. 포트 충돌
```
Error: Address already in use
```
**해결**:
```bash
# 포트 사용 중인 프로세스 확인
lsof -i :8000  # API
lsof -i :8501  # Dashboard

# 프로세스 종료
kill -9 <PID>
```

### 4. Python 패키지 설치 오류
```
Error: Failed building wheel for XXX
```
**해결**:
```bash
# 시스템 의존성 설치
# macOS
brew install postgresql

# Ubuntu/Debian
sudo apt-get install python3-dev libpq-dev

# 패키지 재설치
pip install --upgrade pip
pip install -r requirements.txt
```

---

## 개발 팀 연락처

문제가 지속되면 이슈를 등록해주세요:
- GitHub Issues: [프로젝트 이슈 페이지]

---

## 라이선스

이 프로젝트는 MIT 라이선스를 따릅니다.
