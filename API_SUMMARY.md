# API 및 데이터 소스 완전 가이드

**Stock Intelligence System에서 사용하는 모든 API 및 데이터 소스입니다.**

---

## 📊 한눈에 보기

### 필수 데이터 수집 API (5개) ⭐

| API | 용도 | API 키 | 회원가입 | 비용 | Rate Limit |
|-----|------|-------|---------|------|-----------|
| **KIS API** | 한국 주식 실시간 시세 | ✅ App Key + Secret | ✅ (증권계좌 필요) | 무료 | 초당 20회 |
| **DART API** | 한국 기업 전자공시 | ✅ API Key | ✅ | 무료 | 무제한 |
| **ECOS API** | 한국 경제 지표 | ✅ API Key | ✅ (본인인증) | 무료 | 100/day |
| **FRED API** | 미국 경제 지표 | ✅ API Key | ✅ | 무료 | 120/min |
| **BigKinds API** | 한국 뉴스 | ✅ API Key | ✅ | 무료 | - |

### API 키 불필요 (5개) ✨

| 데이터 소스 | 용도 | 회원가입 | 비용 |
|-----------|------|---------|------|
| **Yahoo Finance** | 글로벌 주식 시세 | ❌ | 무료 |
| **Fear & Greed** | CNN 지수 | ❌ | 무료 |
| **SEC EDGAR** | 미국 기업 재무 | ❌ | 무료 |
| **Tradestie** | Reddit WSB | ❌ | 무료 |
| **StockTwits** | 소셜 감성 | ❌ | 무료 |

### AI 기능 API (6개) - 선택 🤖

| API | 용도 | API 키 | 비용 | 월 한도 |
|-----|------|--------|------|--------|
| **Upstage** | 문서 OCR/AI | ✅ | 무료 tier | 300회 |
| **CLOVA Studio** | 네이버 LLM | ✅ | 무료 tier | 100회 |
| **Claude** | Anthropic LLM | ✅ | 유료 | $5 credit |
| **GPT-4** | OpenAI LLM | ✅ | 유료 | $5 credit |
| **Gemini** | Google LLM | ✅ | 무료 tier | 60/min |
| **Grok** | xAI LLM | ✅ | 유료 | - |

### 알림 API (3개) - 선택 📢

| API | 용도 | API 키 | 비용 |
|-----|------|--------|------|
| **Telegram** | 실시간 알림 | ✅ Bot Token | 무료 |
| **Kakao Talk** | 카톡 알림 | ✅ REST API Key | 무료 |
| **Gmail SMTP** | 이메일 | ✅ App Password | 무료 |

---

## 🎯 실제 필요한 설정

### 옵션 1: 최소 설정 (AI 없이)

**필수 API (5개):**
```bash
KIS_APP_KEY=                # 한국투자증권
KIS_APP_SECRET=             # 한국투자증권
DART_API_KEY=               # 금융감독원
ECOS_API_KEY=               # 한국은행
FRED_API_KEY=               # 미국 연준
BIGKINDS_API_KEY=           # 뉴스
```

**작동 기능:**
- ✅ 모든 핵심 기능 (데이터 수집, 분석, 신호, 백테스팅, Dashboard)
- ❌ AI 분석
- ❌ 알림

**소요 시간:** 1-2시간

---

### 옵션 2: 알림 추가

최소 설정 + 알림 API 1개 이상 추가

**추천 (가장 쉬움):**
```bash
TELEGRAM_BOT_TOKEN=         # 5분 소요
TELEGRAM_CHAT_ID=
```

**또는:**
```bash
SMTP_USERNAME=              # Gmail 앱 비밀번호
SMTP_PASSWORD=
EMAIL_TO=
```

**작동 기능:**
- ✅ 모든 핵심 기능
- ✅ 실시간 투자 알림
- ❌ AI 분석

**소요 시간:** +15분

---

### 옵션 3: AI 기능 추가

최소 설정 + AI API 1개 이상 추가

**추천 (무료):**
```bash
UPSTAGE_API_KEY=            # 월 300회 무료
```

**또는 (한국어):**
```bash
CLOVA_API_KEY=              # 월 100회 무료
CLOVA_API_GATEWAY=
```

**작동 기능:**
- ✅ 모든 핵심 기능
- ✅ AI 문서 분석
- ✅ AI 투자 분석

**소요 시간:** +30분

---

## 📝 API별 발급 가이드

### 1. KIS API (한국투자증권) ⭐ 필수

**URL:** https://apiportal.koreainvestment.com/

**발급 절차:**
1. 한국투자증권 증권계좌 개설 (필수)
2. KIS Developers 사이트 접속
3. 로그인 → "API 신청"
4. App Key 및 App Secret 발급

**주의:**
- 증권계좌 없으면 사용 불가
- 실전/모의 투자 API 구분

---

### 2. DART API (금융감독원) ⭐ 필수

**URL:** https://opendart.fss.or.kr/

**발급 절차:**
1. 회원가입 (이메일 인증)
2. "오픈API" → "인증키 신청"
3. API Key 즉시 발급

**소요 시간:** 5분

---

### 3. ECOS API (한국은행) ⭐ 필수

**URL:** https://ecos.bok.or.kr/

**발급 절차:**
1. 회원가입 (본인인증 필수: 휴대폰 또는 아이핀)
2. "OpenAPI" → "인증키 신청/관리"
3. 용도 입력 후 발급

**주의:**
- 본인인증 필수
- 일일 한도 100회

**소요 시간:** 15분

---

### 4. FRED API (미국 연준) ⭐ 필수

**URL:** https://fred.stlouisfed.org/

**발급 절차:**
1. "My Account" → "Create Account"
2. 이메일 인증
3. "API Keys" → "Request API Key"

**소요 시간:** 5분

---

### 5. BigKinds API (뉴스) ⭐ 필수

**URL:** https://www.bigkinds.or.kr/

**발급 절차:**
1. 회원가입 (이메일 인증)
2. "Open API" → "API 키 발급"

**소요 시간:** 5분

---

### 6. Telegram Bot 📢 선택

**발급 절차:**
1. Telegram 앱에서 @BotFather 검색
2. `/newbot` 명령어
3. Bot Token 복사
4. @userinfobot에서 Chat ID 확인

**소요 시간:** 5분

---

### 7-12. AI APIs 🤖 선택

**Upstage:** https://www.upstage.ai/ (무료 tier 300회/월)
**CLOVA:** https://www.ncloud.com/product/aiService/clovaStudio (무료 tier 100회/월)
**Claude:** https://console.anthropic.com/ ($5 무료 크레딧)
**GPT-4:** https://platform.openai.com/ ($5 무료 크레딧)
**Gemini:** https://ai.google.dev/ (무료 tier)
**Grok:** https://x.ai/ (유료)

---

## 💰 비용 요약

**핵심 기능 (무료):**
- KIS, DART, ECOS, FRED, BigKinds
- Yahoo, Fear&Greed, SEC EDGAR, Tradestie, StockTwits
- Telegram, Gmail

**AI 무료 Tier:**
- Upstage (월 300회)
- CLOVA (월 100회)
- Gemini (분당 60회)

**AI 유료 (선택):**
- Claude, GPT-4 (각 $5 무료 크레딧 후 과금)
- Grok (가격 확인 필요)

**총 비용: 0원** (핵심 기능 + AI 무료 tier 사용 시)

---

## 📋 .env 파일 템플릿

### 최소 설정

```bash
# ============================================
# Database (필수)
# ============================================
DATABASE_URL=postgresql://user:password@localhost:5432/stock_intelligence

# ============================================
# 필수 데이터 수집 API (5개)
# ============================================

# 1. 한국투자증권 KIS
KIS_APP_KEY=your_kis_app_key_here
KIS_APP_SECRET=your_kis_app_secret_here

# 2. DART (금융감독원)
DART_API_KEY=your_dart_api_key_here

# 3. ECOS (한국은행)
ECOS_API_KEY=your_ecos_api_key_here

# 4. FRED (미국 연준)
FRED_API_KEY=your_fred_api_key_here

# 5. BigKinds (뉴스)
BIGKINDS_API_KEY=your_bigkinds_api_key_here

# ============================================
# Logging (필수)
# ============================================
LOG_DIR=logs
LOG_LEVEL=INFO
```

### 완전 설정 (AI + 알림 포함)

```bash
# ... 최소 설정 + 아래 추가 ...

# ============================================
# AI APIs (선택)
# ============================================
UPSTAGE_API_KEY=your_upstage_key
CLOVA_API_KEY=your_clova_key
CLOVA_API_GATEWAY=your_clova_gateway
ANTHROPIC_API_KEY=your_anthropic_key
OPENAI_API_KEY=your_openai_key
GOOGLE_API_KEY=your_google_key
XAI_API_KEY=your_xai_key

# ============================================
# 알림 (선택)
# ============================================

# Telegram
TELEGRAM_BOT_TOKEN=your_telegram_token
TELEGRAM_CHAT_ID=your_chat_id

# Kakao
KAKAO_REST_API_KEY=your_kakao_key

# Gmail
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your_email@gmail.com
SMTP_PASSWORD=your_app_password
EMAIL_FROM=your_email@gmail.com
EMAIL_TO=recipient@example.com

# ============================================
# AWS (선택)
# ============================================
AWS_ACCESS_KEY_ID=your_aws_key
AWS_SECRET_ACCESS_KEY=your_aws_secret
S3_BUCKET_NAME=your_bucket

# ============================================
# Supabase (선택 - PostgreSQL 호스팅)
# ============================================
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key
SUPABASE_DB_URL=your_supabase_db_url
```

---

## ✅ 체크리스트

### 필수 준비 (1-2시간)

- [ ] **KIS API** - 증권계좌 + API 발급 (30분)
- [ ] **DART API** - 회원가입 + API 발급 (5분)
- [ ] **ECOS API** - 본인인증 + API 발급 (15분)
- [ ] **FRED API** - 회원가입 + API 발급 (5분)
- [ ] **BigKinds API** - 회원가입 + API 발급 (5분)
- [ ] **PostgreSQL** - 설치 및 DB 생성 (15분)
- [ ] **.env 파일** - 작성 (10분)

### 선택 준비 (+30분)

- [ ] **Telegram Bot** - Bot 생성 (5분)
- [ ] **Upstage** 또는 **CLOVA** - AI API (10분)
- [ ] **Gmail SMTP** - 앱 비밀번호 (5분)

---

## 🚨 주의사항

### KIS API
- **증권계좌 필수** - 계좌 없으면 사용 불가
- 실전/모의 투자 API 구분
- OAuth 토큰 자동 갱신 (코드 구현됨)

### ECOS API
- **본인인증 필수** (휴대폰 또는 아이핀)
- **일일 한도 100회** - 효율적 사용 필요
- 한도 초과 시 다음 날 00:00 초기화

### BigKinds API
- 뉴스 검색어 최적화 필요
- API 사용량 모니터링

### AI APIs
- 무료 한도 확인
- 초과 시 과금 발생
- 비용 모니터링 필수

---

## 🔧 문제 해결

### Q: KIS API가 작동하지 않아요
**A:**
- 증권계좌 개설 확인
- App Key/Secret 재확인
- 실전/모의 설정 확인

### Q: ECOS API 한도 초과
**A:**
- 일일 100회 제한
- 다음 날 00:00 초기화
- 캐싱 활용 필요

### Q: BigKinds API 오류
**A:**
- API 키 재확인
- 뉴스 검색어 확인
- Rate limit 확인

---

## 📞 더 알아보기

자세한 설정 가이드는 **DEPLOYMENT_GUIDE.md**를 참조하세요.

**최종 업데이트:** 2025-11-22
**버전:** 2.0.0
