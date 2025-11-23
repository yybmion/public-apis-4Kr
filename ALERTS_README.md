# 알림 시스템 사용 가이드

## 📋 개요

Telegram과 Email을 통한 실시간 투자 알림 시스템입니다.

## 🎯 주요 기능

### 1. Telegram Bot 알림
- **실시간 투자 신호**: 신호 변경 시 즉시 알림
- **일일 브리핑**: 매일 시장 요약 및 투자 전략
- **극단적 시장 알림**: Fear & Greed 극단 (< 25 또는 > 75)
- **경제 지표 알림**: 금리 변화, 수익률 곡선 역전

### 2. Email 알림
- **일일 투자 리포트**: HTML 포맷 상세 리포트
- **주간 성과 리포트**: 주간 수익률 및 신호 변경 내역
- **중요 신호 변경**: 투자 신호 변경 시 이메일 발송
- **극단적 시장 상황**: Fear & Greed 극단 알림

### 3. Alert Manager
- **중앙 집중식 관리**: 모든 알림을 단일 인터페이스로 관리
- **중복 방지**: Rate limiting으로 스팸 방지
- **히스토리 추적**: 알림 및 신호 히스토리 기록
- **설정 관리**: 알림 임계값 및 채널 설정

## 🚀 설정 방법

### 1. Telegram Bot 설정

#### Step 1: Bot 생성
1. Telegram에서 [@BotFather](https://t.me/BotFather) 검색
2. `/newbot` 명령어로 새 봇 생성
3. 봇 이름 및 사용자명 설정
4. **Bot Token** 받기 (예: `1234567890:ABCdefGHIjklMNOpqrsTUVwxyz`)

#### Step 2: Chat ID 확인
1. Telegram에서 [@userinfobot](https://t.me/userinfobot) 검색
2. `/start` 명령어 실행
3. **Chat ID** 확인 (예: `123456789`)

#### Step 3: 환경 변수 설정
```bash
export TELEGRAM_BOT_TOKEN="1234567890:ABCdefGHIjklMNOpqrsTUVwxyz"
export TELEGRAM_CHAT_ID="123456789"
```

또는 `.env` 파일에 추가:
```bash
TELEGRAM_BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
TELEGRAM_CHAT_ID=123456789
```

### 2. Email 설정

#### Gmail 사용 시 (권장)

**Step 1: App Password 생성**
1. Google 계정 > 보안 > 2단계 인증 활성화
2. 보안 > 앱 비밀번호 > "메일" 선택
3. **앱 비밀번호** 생성 (16자리, 예: `abcd efgh ijkl mnop`)

**Step 2: 환경 변수 설정**
```bash
export SMTP_SERVER="smtp.gmail.com"
export SMTP_PORT="587"
export SMTP_USERNAME="your-email@gmail.com"
export SMTP_PASSWORD="abcd efgh ijkl mnop"  # App password
export EMAIL_FROM="your-email@gmail.com"
export EMAIL_TO="recipient@example.com"
```

또는 `.env` 파일:
```bash
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=abcdefghijklmnop
EMAIL_FROM=your-email@gmail.com
EMAIL_TO=recipient@example.com
```

#### 기타 SMTP 서버

**Naver Mail:**
```bash
SMTP_SERVER=smtp.naver.com
SMTP_PORT=587
```

**Daum Mail:**
```bash
SMTP_SERVER=smtp.daum.net
SMTP_PORT=465
```

### 3. 알림 설정

환경 변수로 알림 동작 커스터마이징:

```bash
# 알림 채널 활성화/비활성화
export ALERT_TELEGRAM_ENABLED="true"
export ALERT_EMAIL_ENABLED="true"

# 극단 시장 임계값
export ALERT_EXTREME_FEAR="25"    # Fear & Greed < 25 시 알림
export ALERT_EXTREME_GREED="75"   # Fear & Greed > 75 시 알림

# 신호 변경 알림
export ALERT_SIGNAL_CHANGE="true"

# 일일 브리핑 시간
export ALERT_DAILY_TIME="09:00"

# 주간 리포트 요일 (0=월요일)
export ALERT_WEEKLY_DAY="0"

# Rate limiting (분 단위)
export ALERT_MIN_INTERVAL="60"
```

## 💻 사용 방법

### 1. 기본 사용법

```python
import asyncio
from app.alerts.alert_manager import get_alert_manager

async def main():
    # Alert Manager 가져오기
    manager = get_alert_manager()

    # 투자 신호 전송
    signal_data = {
        'signal': 'BUY',
        'confidence': 75.0,
        'score': 7.2,
        'action_plan': {
            'action': '점진적 매수 전략',
            'timeframe': '1-2주',
            'target_allocation': {
                '주식': '60%',
                '채권': '30%',
                '현금': '10%'
            }
        }
    }

    await manager.send_investment_signal(signal_data)

asyncio.run(main())
```

### 2. 일일 브리핑 전송

```python
from app.alerts.alert_manager import get_alert_manager

async def send_daily_briefing():
    manager = get_alert_manager()

    briefing = """
    📊 미국 시장: S&P 500 +0.85%, NASDAQ +1.20%
    💡 주요 이슈: Fed 금리 동결 결정
    📈 한국 시장 전망: 긍정적 영향 예상
    """

    signal_data = {
        'signal': 'BUY',
        'confidence': 75.0
    }

    market_data = {
        'sp500_change_pct': 0.85,
        'nasdaq_change_pct': 1.20
    }

    await manager.send_daily_briefing(briefing, signal_data, market_data)

asyncio.run(send_daily_briefing())
```

### 3. 극단 시장 알림

```python
from app.alerts.alert_manager import get_alert_manager

async def check_extreme_market():
    manager = get_alert_manager()

    fear_greed_score = 20  # 극단적 공포

    market_data = {
        'sp500_change_pct': -2.5,
        'nasdaq_change_pct': -3.2
    }

    # Fear & Greed < 25 시 자동으로 알림 전송
    await manager.send_extreme_market_alert(fear_greed_score, market_data)

asyncio.run(check_extreme_market())
```

### 4. 신호 변경 알림

```python
from app.alerts.alert_manager import get_alert_manager

async def notify_signal_change():
    manager = get_alert_manager()

    await manager.send_signal_change_alert(
        old_signal='HOLD',
        new_signal='BUY',
        confidence=72.0,
        reason='S&P 500 골든크로스 발생'
    )

asyncio.run(notify_signal_change())
```

### 5. 주간 리포트 전송

```python
from app.alerts.alert_manager import get_alert_manager

async def send_weekly_report():
    manager = get_alert_manager()

    performance_data = {
        'total_return_pct': 3.5,
        'max_drawdown_pct': -2.1,
        'win_rate': 0.625
    }

    signals_history = [
        {'date': '2025-11-18', 'signal': 'HOLD', 'confidence': 65},
        {'date': '2025-11-19', 'signal': 'BUY', 'confidence': 72},
    ]

    await manager.send_weekly_report(performance_data, signals_history)

asyncio.run(send_weekly_report())
```

### 6. 사용자 정의 알림

```python
from app.alerts.alert_manager import get_alert_manager

async def send_custom():
    manager = get_alert_manager()

    await manager.send_custom_alert(
        title="중요 알림",
        message="사용자 정의 메시지",
        channels=['telegram', 'email']  # 또는 ['telegram'] 또는 ['email']
    )

asyncio.run(send_custom())
```

## 🧪 테스트

### 알림 시스템 테스트 실행

```bash
python scripts/test_alerts.py
```

테스트 내용:
1. Telegram 및 Email 연결 테스트
2. 투자 신호 알림
3. 일일 브리핑
4. 극단 시장 알림 (공포/탐욕)
5. 신호 변경 알림
6. 경제 지표 알림 (금리 인상, 수익률 곡선 역전)
7. 주간 리포트
8. 사용자 정의 알림
9. 알림 히스토리 확인

### 개별 채널 테스트

**Telegram만 테스트:**
```python
from app.alerts.telegram_bot import TelegramBot

async def test_telegram():
    bot = TelegramBot()
    success = await bot.test_connection()
    print(f"Telegram: {'✅' if success else '❌'}")

asyncio.run(test_telegram())
```

**Email만 테스트:**
```python
from app.alerts.email_notifier import EmailNotifier

def test_email():
    notifier = EmailNotifier()
    success = notifier.test_connection()
    print(f"Email: {'✅' if success else '❌'}")

test_email()
```

## 📊 스케줄러 통합

스케줄러에서 자동으로 알림 전송:

```python
from app.scheduler.scheduler import StockDataScheduler

scheduler = StockDataScheduler()

# 스케줄러가 자동으로:
# - 06:00 Fear & Greed 수집
# - 07:00 FRED 데이터 수집
# - 08:30 투자 신호 생성 → Telegram 알림
# - 09:00 일일 브리핑 생성 → Telegram + Email 알림
# - 15:40 오후 브리핑 → Telegram 알림
# - 주간 월요일 08:00 주간 리포트 → Email 알림

scheduler.start()
```

## 🔧 고급 기능

### 1. Alert Manager 커스터마이징

```python
from app.alerts.alert_manager import AlertManager, AlertConfig

# 사용자 정의 설정
config = AlertConfig()
config.extreme_fear_threshold = 20  # 더 극단적인 공포만 알림
config.extreme_greed_threshold = 80
config.min_alert_interval_minutes = 120  # 2시간마다만

manager = AlertManager(config)
```

### 2. 히스토리 관리

```python
from app.alerts.alert_manager import get_alert_manager

manager = get_alert_manager()

# 최근 신호 히스토리 확인
signals = manager.get_signal_history(limit=10)
for sig in signals:
    print(f"{sig['date']}: {sig['signal']} ({sig['confidence']:.0f}%)")

# 알림 히스토리 확인
alerts = manager.get_alert_history()
for alert_type, last_sent in alerts.items():
    print(f"{alert_type}: {last_sent}")

# 히스토리 초기화
manager.clear_history()
```

### 3. Rate Limiting 커스터마이징

특정 알림의 최소 간격 설정:

```python
# 극단 시장 알림은 3시간(180분)마다만
await manager.send_extreme_market_alert(
    fear_greed_score=20,
    market_data=data
)
# 내부적으로 min_interval=180 사용

# 경제 알림은 24시간(1440분)마다만
await manager.send_economic_alert(
    alert_type='rate_hike',
    data=rate_data
)
# 내부적으로 min_interval=1440 사용
```

### 4. 조건부 알림

```python
from app.alerts.alert_manager import get_alert_manager

async def conditional_alert(signal_data, prev_signal):
    manager = get_alert_manager()

    current_signal = signal_data['signal']

    # 신호가 변경된 경우에만 알림
    if current_signal != prev_signal:
        await manager.send_signal_change_alert(
            old_signal=prev_signal,
            new_signal=current_signal,
            confidence=signal_data['confidence']
        )

    # 강한 매수/매도 신호에만 추가 알림
    if current_signal in ['STRONG_BUY', 'STRONG_SELL']:
        await manager.send_custom_alert(
            title=f"⚠️ 강한 신호: {current_signal}",
            message="즉시 포트폴리오 재조정을 고려하세요."
        )
```

## 📝 Telegram 메시지 포맷

Telegram은 Markdown 포맷을 지원합니다:

```python
message = """
**굵게**
*기울임*
`코드`
[링크](https://example.com)

• 목록 1
• 목록 2
"""

await bot.send_message(message, parse_mode='Markdown')
```

## 🔐 보안 주의사항

### 1. 환경 변수 보호
- `.env` 파일을 `.gitignore`에 추가
- Bot Token 및 SMTP Password 노출 금지
- 프로덕션 환경에서는 secrets manager 사용

### 2. Telegram Bot 보안
- Bot Token을 공개 저장소에 커밋하지 말 것
- Chat ID를 확인하여 허가된 사용자만 알림 수신

### 3. Email 보안
- App Password 사용 (실제 비밀번호 X)
- 2단계 인증 활성화
- SMTP over TLS/SSL 사용

## 🐛 문제 해결

### Telegram 알림이 안 옴

**확인 사항:**
1. `TELEGRAM_BOT_TOKEN`이 올바르게 설정되었는지
2. `TELEGRAM_CHAT_ID`가 올바른지
3. Bot과 대화를 시작했는지 (Bot에게 `/start` 전송)
4. 네트워크 연결 확인

**테스트:**
```bash
python scripts/test_alerts.py
```

### Email 알림이 안 옴

**확인 사항:**
1. Gmail App Password를 사용하는지 (실제 비밀번호 X)
2. 2단계 인증이 활성화되었는지
3. SMTP 포트가 올바른지 (Gmail: 587)
4. 방화벽에서 SMTP 포트가 차단되지 않았는지

**Gmail SMTP 오류:**
```
SMTPAuthenticationError: Username and Password not accepted
```
→ App Password를 사용하세요 (구글 계정 > 보안 > 앱 비밀번호)

### Rate Limiting으로 알림이 스킵됨

**확인:**
```python
manager = get_alert_manager()
history = manager.get_alert_history()
print(history)  # 마지막 알림 전송 시간 확인
```

**강제 전송:**
```python
await manager.send_investment_signal(signal_data, force=True)
```

## 📚 API 레퍼런스

### AlertManager

**메서드:**
- `send_investment_signal(signal_data, force=False)`: 투자 신호 전송
- `send_daily_briefing(briefing, signal_data, market_data)`: 일일 브리핑
- `send_extreme_market_alert(fear_greed_score, market_data)`: 극단 시장 알림
- `send_signal_change_alert(old, new, confidence, reason)`: 신호 변경 알림
- `send_economic_alert(alert_type, data)`: 경제 지표 알림
- `send_weekly_report(performance_data, signals_history)`: 주간 리포트
- `send_custom_alert(title, message, channels)`: 사용자 정의 알림
- `test_all_channels()`: 모든 채널 테스트
- `get_signal_history(limit)`: 신호 히스토리 조회
- `get_alert_history()`: 알림 히스토리 조회
- `clear_history()`: 히스토리 초기화

### TelegramBot

**메서드:**
- `send_message(message, parse_mode='Markdown')`: 메시지 전송
- `send_investment_signal(signal_data)`: 투자 신호 전송
- `send_daily_briefing(briefing, signal_data)`: 일일 브리핑
- `send_extreme_market_alert(fear_greed_score, market_data)`: 극단 알림
- `send_signal_change_alert(old, new, confidence)`: 신호 변경
- `send_economic_alert(alert_type, data)`: 경제 알림
- `send_custom_alert(title, message, emoji)`: 사용자 정의
- `test_connection()`: 연결 테스트

### EmailNotifier

**메서드:**
- `send_email(subject, body_text, body_html)`: 이메일 전송
- `send_daily_report(signal_data, market_data, briefing)`: 일일 리포트
- `send_weekly_report(performance_data, signals_history)`: 주간 리포트
- `send_signal_change_alert(old, new, confidence, reason)`: 신호 변경
- `send_extreme_market_alert(fear_greed_score, market_data)`: 극단 알림
- `test_connection()`: 연결 테스트

## 🔄 업데이트

알림 시스템을 업데이트하려면:

```bash
git pull origin main
```

새로운 알림 타입 추가 시 `app/alerts/`에 기능을 추가하세요.

## 📞 지원

문제 발생 시:
1. `scripts/test_alerts.py` 실행
2. 로그 확인
3. 환경 변수 재확인
4. GitHub Issues에 문의
