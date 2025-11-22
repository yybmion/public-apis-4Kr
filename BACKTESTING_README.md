# 백테스팅 모듈 사용 가이드

## 📋 개요

과거 데이터로 투자 전략을 검증하고 성과를 측정하는 백테스팅 모듈입니다.

## 🎯 주요 기능

### 1. 성과 지표 계산
- **수익률**: 총 수익률, 연환산 수익률 (CAGR)
- **리스크**: 최대 낙폭 (MDD), 변동성
- **위험조정 수익률**: 샤프 비율, 소르티노 비율
- **거래 통계**: 승률, 손익비, 평균 승/패

### 2. 백테스팅 엔진
- 과거 데이터로 전략 실행
- 포지션 관리 (매수/매도)
- 거래 비용 반영 (수수료, 슬리피지)
- Buy & Hold 벤치마크 비교

### 3. 투자 전략
- **Moving Average Strategy**: 이동평균선 전략 (골든크로스/데드크로스)
- **Fear & Greed Strategy**: 역발상 전략
- **Combined Signal Strategy**: 통합 신호 전략

### 4. 시각화
- 자산 곡선 차트 (Plotly)
- 매수/매도 포인트 표시
- 벤치마크 대비 비교

## 📊 성과 지표

### 수익률 지표
```python
- Total Return: 총 수익률 (%)
- CAGR: 연환산 수익률 (%)
- Excess Return: 벤치마크 대비 초과 수익률
```

### 리스크 지표
```python
- Max Drawdown (MDD): 최대 낙폭 (%)
- Volatility: 변동성 (연환산, %)
- MDD Duration: 최대 낙폭 기간 (일)
```

### 위험조정 수익률
```python
- Sharpe Ratio: 샤프 비율 (>1.0 우수)
- Sortino Ratio: 소르티노 비율 (하방 위험만 고려)
- Alpha: 초과 수익률 (벤치마크 대비)
- Beta: 시장 민감도
```

### 거래 통계
```python
- Win Rate: 승률 (%)
- Profit Factor: 손익비 (>1.0 수익)
- Average Win: 평균 승리 금액
- Average Loss: 평균 손실 금액
```

## 🚀 사용 방법

### 1. 기본 사용법

```python
from app.backtesting.backtest_engine import BacktestEngine
from app.backtesting.strategies import MovingAverageStrategy
import pandas as pd

# 데이터 준비 (과거 가격 데이터)
data = pd.DataFrame({
    'close': [100, 102, 101, 105, 107, ...],
    'ma_20': [98, 99, 100, 101, 102, ...],
    'ma_60': [95, 96, 97, 98, 99, ...]
}, index=pd.date_range('2023-01-01', periods=252))

# 전략 생성
strategy = MovingAverageStrategy()

# 백테스팅 엔진 초기화
engine = BacktestEngine(
    initial_capital=10000000,  # 초기 자본 (1천만원)
    commission=0.0015,         # 거래 수수료 (0.15%)
    slippage=0.001             # 슬리피지 (0.1%)
)

# 백테스팅 실행
result = engine.run(data, strategy.generate_signal)

# 결과 출력
print(engine.generate_report(result, "MA Strategy"))
```

### 2. 벤치마크 비교

```python
# Buy & Hold 벤치마크
benchmark = engine.run_buy_and_hold(data)

# 비교
comparison = engine.compare_to_benchmark(result, benchmark)

print(f"Alpha: {comparison['alpha_pct']:+.2f}%")
print(f"Excess Return: {comparison['excess_return_pct']:+.2f}%")
```

### 3. 시각화

```python
# 자산 곡선 차트
fig = engine.plot_equity_curve(result, benchmark)

# HTML 저장
fig.write_html('backtest_result.html')

# 또는 Streamlit에서 표시
import streamlit as st
st.plotly_chart(fig)
```

### 4. 성과 지표 접근

```python
# 결과에서 지표 추출
metrics = result['metrics']

print(f"CAGR: {metrics['cagr_pct']:.2f}%")
print(f"MDD: {metrics['max_drawdown_pct']:.2f}%")
print(f"Sharpe: {metrics['sharpe_ratio']:.3f}")
print(f"Win Rate: {metrics['win_rate'] * 100:.1f}%")
```

## 📈 투자 전략

### 1. Moving Average Strategy

이동평균선 기반 전략:

```python
from app.backtesting.strategies import MovingAverageStrategy

strategy = MovingAverageStrategy(
    short_window=20,  # 단기 이동평균 (일)
    long_window=60    # 장기 이동평균 (일)
)

# 신호 규칙:
# - 골든크로스 (20일선이 60일선 상향돌파): STRONG_BUY
# - 20일선 > 60일선 & 가격 > 20일선: BUY
# - 데드크로스 (20일선이 60일선 하향돌파): STRONG_SELL
# - 20일선 < 60일선 & 가격 < 20일선: SELL
```

### 2. Fear & Greed Strategy

역발상 전략 (Fear & Greed Index 기반):

```python
from app.backtesting.strategies import FearGreedStrategy

strategy = FearGreedStrategy()

# 신호 규칙:
# - Fear & Greed < 25 (극단적 공포): STRONG_BUY
# - Fear & Greed < 40 (공포): BUY
# - 40 <= Fear & Greed <= 60 (중립): HOLD
# - Fear & Greed > 75 (극단적 탐욕): STRONG_SELL
# - Fear & Greed > 60 (탐욕): SELL
```

### 3. Combined Signal Strategy

통합 신호 전략 (다중 지표 가중 평균):

```python
from app.backtesting.strategies import CombinedSignalStrategy

strategy = CombinedSignalStrategy()

# 가중치:
# - Moving Average: 40%
# - Fear & Greed: 30%
# - Interest Rate Spread: 30%
```

### 4. 커스텀 전략

직접 전략을 만들 수 있습니다:

```python
def my_custom_strategy(row: pd.Series) -> str:
    """
    커스텀 전략

    Args:
        row: 데이터 행 (close, ma_20, fear_greed 등)

    Returns:
        신호: STRONG_BUY, BUY, HOLD, SELL, STRONG_SELL
    """
    close = row['close']
    ma_20 = row['ma_20']
    fear_greed = row['fear_greed']

    # 예: MA > 현재가 AND 극단적 공포
    if close > ma_20 and fear_greed < 25:
        return "STRONG_BUY"
    elif close < ma_20 and fear_greed > 75:
        return "STRONG_SELL"
    else:
        return "HOLD"

# 사용
result = engine.run(data, my_custom_strategy)
```

## 🧪 테스트

### 백테스팅 테스트 실행

```bash
python scripts/test_backtesting.py
```

테스트 내용:
1. Moving Average Strategy 백테스팅
2. Fear & Greed Strategy 백테스팅
3. Combined Signal Strategy 백테스팅
4. 시각화 (HTML 파일 생성)

### 샘플 데이터 생성

테스트 스크립트는 자동으로 샘플 데이터를 생성합니다 (252일 = 1년).

실제 데이터 사용 시:
```python
# Yahoo Finance에서 데이터 가져오기
import yfinance as yf

# KOSPI ETF 예시
ticker = yf.Ticker("069500.KS")  # KODEX 200
data = ticker.history(period="1y")

# 필요한 컬럼 추가 (MA, Fear & Greed 등)
data['ma_20'] = data['Close'].rolling(20).mean()
data['ma_60'] = data['Close'].rolling(60).mean()
```

## 📊 결과 해석

### 좋은 전략의 기준

| 지표 | 우수 | 양호 | 보통 | 개선 필요 |
|------|------|------|------|----------|
| **CAGR** | >20% | 10-20% | 5-10% | <5% |
| **Sharpe Ratio** | >2.0 | 1.0-2.0 | 0.5-1.0 | <0.5 |
| **MDD** | <10% | 10-20% | 20-30% | >30% |
| **Win Rate** | >60% | 50-60% | 40-50% | <40% |
| **Profit Factor** | >2.0 | 1.5-2.0 | 1.0-1.5 | <1.0 |

### Alpha & Beta 해석

**Alpha (초과 수익률)**:
- Alpha > 0: 벤치마크 대비 초과 수익
- Alpha < 0: 벤치마크 미달

**Beta (시장 민감도)**:
- Beta = 1: 시장과 동일한 움직임
- Beta > 1: 시장보다 변동성 크다
- Beta < 1: 시장보다 변동성 작다

### 리포트 예시

```
================================================================================
  Combined Signal Strategy - 백테스팅 성과 리포트
================================================================================

📅 기간: 2023-01-01 ~ 2023-12-31 (365일)

💰 수익률:
   초기 자산: $10,000,000.00
   최종 자산: $11,500,000.00
   총 수익률: +15.00%
   연환산 수익률 (CAGR): +15.23%

📉 리스크:
   최대 낙폭 (MDD): -12.50%
   MDD 기간: 45일
   변동성 (연환산): 18.50%

📊 위험조정 수익률:
   샤프 비율: 1.250
   소르티노 비율: 1.850

💼 거래 통계:
   총 거래 수: 24
   승리: 15 | 패배: 9
   승률: 62.5%
   평균 승리: $150,000.00
   평균 손실: $80,000.00
   손익비 (Profit Factor): 2.34

================================================================================
```

## ⚙️ 파라미터 튜닝

### 전략 파라미터

Moving Average Strategy:
```python
strategy = MovingAverageStrategy(
    short_window=20,  # 10, 15, 20, 25 등 테스트
    long_window=60    # 50, 60, 100, 200 등 테스트
)
```

### 백테스팅 파라미터

```python
engine = BacktestEngine(
    initial_capital=10000000,  # 초기 자본
    commission=0.0015,         # 한국: 0.15%, 미국: 0.001%
    slippage=0.001,            # 0.1% ~ 0.5%
    risk_free_rate=0.03        # 3% (국고채 수익률)
)
```

## 🔧 고급 기능

### 1. 거래 내역 분석

```python
# 개별 거래 확인
for trade in result['trades']:
    print(f"{trade['date']}: {trade['type']} {trade['shares']:.2f} @ ${trade['price']:.2f}")

# 수익 거래만 필터
winning_trades = [t for t in result['trades'] if t.get('profit', 0) > 0]
print(f"승리 거래 수: {len(winning_trades)}")
```

### 2. 월별 수익률 분석

```python
import pandas as pd

# 월별 수익률 계산
equity = result['equity_curve']
monthly_returns = equity.resample('M').last().pct_change()

print("월별 수익률:")
for date, ret in monthly_returns.items():
    print(f"{date.strftime('%Y-%m')}: {ret * 100:+.2f}%")
```

### 3. 드로다운 기간 분석

```python
metrics = result['metrics']

print(f"최대 낙폭 기간:")
print(f"  고점: {metrics['peak_date']}")
print(f"  저점: {metrics['trough_date']}")
print(f"  회복: {metrics['recovery_date']}")
print(f"  기간: {metrics['max_drawdown_duration']}일")
```

## 📝 주의사항

### 1. 백테스팅 함정 (Pitfalls)

- **Overfitting (과적합)**: 과거 데이터에만 최적화된 전략
- **Look-ahead Bias**: 미래 정보 사용
- **Survivorship Bias**: 상장폐지 종목 제외
- **데이터 품질**: 잘못된 데이터로 인한 왜곡

### 2. 실전 적용 시 고려사항

- 백테스팅 결과 ≠ 미래 수익률 보장
- 슬리피지, 수수료를 충분히 반영
- 시장 환경 변화 고려
- 리스크 관리 필수

### 3. 권장사항

- 다양한 기간에서 테스트 (1년, 3년, 5년)
- 여러 시장 환경에서 검증 (상승장, 하락장, 횡보장)
- Out-of-sample 테스트 (미래 데이터로 재검증)
- Walk-forward 분석

## 📚 참고 자료

- Sharpe Ratio: https://en.wikipedia.org/wiki/Sharpe_ratio
- Maximum Drawdown: https://en.wikipedia.org/wiki/Drawdown_(economics)
- Backtesting Best Practices: https://www.quantstart.com/articles/Backtesting-Systematic-Trading-Strategies-in-Python-Considerations-and-Open-Source-Frameworks

## 🔄 업데이트

백테스팅 모듈을 업데이트하려면:

```bash
git pull origin main
```

새로운 전략 추가 시 `app/backtesting/strategies.py`에 클래스를 추가하세요.
