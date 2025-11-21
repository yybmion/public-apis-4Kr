"""
Notification System - Kakao Talk Notifications
Stock Intelligence System
"""

import requests
import json
from typing import Dict, Optional
from datetime import datetime

from app.config import settings
from app.utils.logger import LoggerMixin


class KakaoNotifier(LoggerMixin):
    """
    Send notifications via Kakao Talk

    Notification types:
    - Target price reached
    - Surge/Plunge alert
    - Important disclosure
    - US market signal change
    - Stop loss trigger
    """

    def __init__(self, access_token: Optional[str] = None):
        super().__init__()
        self.access_token = access_token or settings.KAKAO_ACCESS_TOKEN
        self.base_url = settings.KAKAO_BASE_URL

        if not self.access_token:
            self.log_warning("Kakao access token not configured")

    def send_alert(
        self,
        alert_type: str,
        stock_name: str,
        message: str,
        data: Optional[Dict] = None
    ) -> bool:
        """
        Send alert notification

        Args:
            alert_type: Type of alert (target_price, surge, etc.)
            stock_name: Stock name
            message: Alert message
            data: Additional data

        Returns:
            True if successful
        """
        if not self.access_token:
            self.log_error("Cannot send notification without access token")
            return False

        # Get template for alert type
        text = self._get_template(alert_type, stock_name, message, data)

        return self._send_message(text)

    def _get_template(
        self,
        alert_type: str,
        stock_name: str,
        message: str,
        data: Optional[Dict]
    ) -> str:
        """Get message template for alert type"""

        templates = {
            'target_price': f"""
🎯 목표가 도달 알림

{stock_name}
{message}

현재가: {data.get('current_price', 0):,}원
목표가: {data.get('target_price', 0):,}원
달성률: {data.get('achievement', 0):.1f}%

시간: {datetime.now().strftime('%Y-%m-%d %H:%M')}
            """,

            'surge': f"""
📈 급등 알림

{stock_name}
{message}

현재가: {data.get('current_price', 0):,}원
상승률: +{data.get('change_rate', 0):.2f}%
거래량: {data.get('volume', 0):,}주

⚠️ 변동성이 큰 상황입니다. 신중하게 판단하세요.

시간: {datetime.now().strftime('%Y-%m-%d %H:%M')}
            """,

            'plunge': f"""
📉 급락 알림

{stock_name}
{message}

현재가: {data.get('current_price', 0):,}원
하락률: {data.get('change_rate', 0):.2f}%
거래량: {data.get('volume', 0):,}주

⚠️ 손절매 여부를 검토하세요.

시간: {datetime.now().strftime('%Y-%m-%d %H:%M')}
            """,

            'disclosure': f"""
📢 중요 공시 알림

{stock_name}
{message}

공시 제목: {data.get('title', 'N/A')}
공시 시간: {data.get('published_at', 'N/A')}

💡 공시 내용을 확인하고 투자 전략을 재검토하세요.
            """,

            'us_signal': f"""
🇺🇸 미국 시장 신호 변경

{message}

S&P 500: {data.get('sp500_close', 0):,.2f}
MA(20): {data.get('sp500_ma', 0):,.2f}
신호: {data.get('signal', 'N/A')}

💡 한국 주식시장에 {data.get('impact', '영향을')} 줄 수 있습니다.
{data.get('recommendation', '')}

시간: {datetime.now().strftime('%Y-%m-%d %H:%M')}
            """,

            'stop_loss': f"""
⛔ 손절매 실행 알림

{stock_name}
{message}

현재가: {data.get('current_price', 0):,}원
매수가: {data.get('buy_price', 0):,}원
손실률: {data.get('loss_rate', 0):.2f}%

자동으로 손절매가 실행되었습니다.

시간: {datetime.now().strftime('%Y-%m-%d %H:%M')}
            """,

            'recommendation': f"""
💡 종목 추천 알림

{stock_name}
{message}

현재가: {data.get('current_price', 0):,}원
추천 이유:
{self._format_reasons(data.get('reasons', []))}

적합도 점수: {data.get('score', 0)}/100

시간: {datetime.now().strftime('%Y-%m-%d %H:%M')}
            """
        }

        return templates.get(alert_type, f"{stock_name}\n{message}")

    def _format_reasons(self, reasons: list) -> str:
        """Format reasons as bullet points"""
        if not reasons:
            return ""
        return "\n".join([f"• {reason}" for reason in reasons])

    def _send_message(self, text: str) -> bool:
        """
        Send message via Kakao Talk API

        Args:
            text: Message text

        Returns:
            True if successful
        """
        try:
            url = f"{self.base_url}/v2/api/talk/memo/default/send"

            headers = {
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/x-www-form-urlencoded"
            }

            template = {
                "object_type": "text",
                "text": text,
                "link": {
                    "web_url": "https://finance.naver.com",
                    "mobile_web_url": "https://finance.naver.com"
                },
                "button_title": "자세히 보기"
            }

            payload = {
                "template_object": json.dumps(template)
            }

            response = requests.post(url, headers=headers, data=payload)

            if response.status_code == 200:
                self.log_info("Notification sent successfully")
                return True
            else:
                self.log_error(f"Failed to send notification: {response.status_code} - {response.text}")
                return False

        except Exception as e:
            self.log_error(f"Error sending notification: {str(e)}")
            return False

    def send_target_price_alert(
        self,
        stock_name: str,
        current_price: int,
        target_price: int
    ) -> bool:
        """Send target price reached alert"""
        achievement = (current_price / target_price) * 100

        return self.send_alert(
            alert_type='target_price',
            stock_name=stock_name,
            message=f"목표가 {target_price:,}원에 도달했습니다!",
            data={
                'current_price': current_price,
                'target_price': target_price,
                'achievement': achievement
            }
        )

    def send_surge_alert(
        self,
        stock_name: str,
        current_price: int,
        change_rate: float,
        volume: int
    ) -> bool:
        """Send surge alert"""
        return self.send_alert(
            alert_type='surge',
            stock_name=stock_name,
            message=f"{abs(change_rate):.2f}% 급등이 발생했습니다!",
            data={
                'current_price': current_price,
                'change_rate': change_rate,
                'volume': volume
            }
        )

    def send_plunge_alert(
        self,
        stock_name: str,
        current_price: int,
        change_rate: float,
        volume: int
    ) -> bool:
        """Send plunge alert"""
        return self.send_alert(
            alert_type='plunge',
            stock_name=stock_name,
            message=f"{abs(change_rate):.2f}% 급락이 발생했습니다!",
            data={
                'current_price': current_price,
                'change_rate': change_rate,
                'volume': volume
            }
        )

    def send_us_signal_alert(
        self,
        signal: str,
        sp500_close: float,
        sp500_ma: float,
        recommendation: str
    ) -> bool:
        """Send US market signal change alert"""
        impact = "긍정적인 영향을" if signal == "BULLISH" else "부정적인 영향을"

        return self.send_alert(
            alert_type='us_signal',
            stock_name="미국 시장 신호",
            message=f"S&P 500 신호가 {signal}로 변경되었습니다.",
            data={
                'signal': signal,
                'sp500_close': sp500_close,
                'sp500_ma': sp500_ma,
                'impact': impact,
                'recommendation': recommendation
            }
        )

    def send_recommendation_alert(
        self,
        stock_name: str,
        current_price: int,
        score: int,
        reasons: list
    ) -> bool:
        """Send stock recommendation alert"""
        return self.send_alert(
            alert_type='recommendation',
            stock_name=stock_name,
            message="이 종목이 회원님께 추천됩니다.",
            data={
                'current_price': current_price,
                'score': score,
                'reasons': reasons
            }
        )


# Mock notifier for testing
class MockNotifier(LoggerMixin):
    """Mock notifier for testing without actual API calls"""

    def send_alert(self, alert_type: str, stock_name: str, message: str, data: Optional[Dict] = None) -> bool:
        self.log_info(f"[MOCK] Alert sent - Type: {alert_type}, Stock: {stock_name}, Message: {message}")
        return True

    def send_target_price_alert(self, stock_name: str, current_price: int, target_price: int) -> bool:
        return self.send_alert('target_price', stock_name, f"Target {target_price} reached at {current_price}")

    def send_surge_alert(self, stock_name: str, current_price: int, change_rate: float, volume: int) -> bool:
        return self.send_alert('surge', stock_name, f"Surge {change_rate}%")

    def send_plunge_alert(self, stock_name: str, current_price: int, change_rate: float, volume: int) -> bool:
        return self.send_alert('plunge', stock_name, f"Plunge {change_rate}%")

    def send_us_signal_alert(self, signal: str, sp500_close: float, sp500_ma: float, recommendation: str) -> bool:
        return self.send_alert('us_signal', "US Market", f"Signal changed to {signal}")

    def send_recommendation_alert(self, stock_name: str, current_price: int, score: int, reasons: list) -> bool:
        return self.send_alert('recommendation', stock_name, f"Recommended with score {score}")
