"""
Telegram Bot for Investment Alerts

텔레그램 봇을 통한 실시간 투자 알림

Features:
- 일일 투자 신호 전송
- 시장 변화 알림 (극단적 공포/탐욕)
- 경제 지표 업데이트
- 맞춤형 알림 설정

Author: AI Assistant
Created: 2025-11-22
"""

import os
import asyncio
from typing import Dict, Any, Optional, List
from datetime import datetime
import logging

try:
    import telegram
    from telegram import Bot
    from telegram.error import TelegramError
except ImportError:
    telegram = None
    Bot = None
    TelegramError = Exception

# Setup logging
logger = logging.getLogger(__name__)


class TelegramBot:
    """
    Telegram Bot for sending investment alerts

    Environment Variables:
        TELEGRAM_BOT_TOKEN: Bot token from @BotFather
        TELEGRAM_CHAT_ID: Your chat ID (get from @userinfobot)
    """

    def __init__(
        self,
        bot_token: Optional[str] = None,
        chat_id: Optional[str] = None
    ):
        """
        Initialize Telegram Bot

        Args:
            bot_token: Telegram bot token (or from env)
            chat_id: Chat ID to send messages (or from env)
        """
        if telegram is None:
            logger.warning("python-telegram-bot not installed. Install with: pip install python-telegram-bot")
            self.bot = None
            self.chat_id = None
            return

        self.bot_token = bot_token or os.getenv('TELEGRAM_BOT_TOKEN')
        self.chat_id = chat_id or os.getenv('TELEGRAM_CHAT_ID')

        if not self.bot_token:
            logger.warning("TELEGRAM_BOT_TOKEN not set. Telegram alerts disabled.")
            self.bot = None
        else:
            self.bot = Bot(token=self.bot_token)

        if not self.chat_id:
            logger.warning("TELEGRAM_CHAT_ID not set. Cannot send messages.")

    async def send_message(
        self,
        message: str,
        parse_mode: str = 'Markdown'
    ) -> bool:
        """
        Send a message to Telegram

        Args:
            message: Message text (supports Markdown)
            parse_mode: 'Markdown' or 'HTML'

        Returns:
            Success status
        """
        if not self.bot or not self.chat_id:
            logger.warning("Telegram bot not configured. Message not sent.")
            return False

        try:
            await self.bot.send_message(
                chat_id=self.chat_id,
                text=message,
                parse_mode=parse_mode
            )
            logger.info(f"Telegram message sent to {self.chat_id}")
            return True

        except TelegramError as e:
            logger.error(f"Failed to send Telegram message: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error sending Telegram message: {str(e)}")
            return False

    async def send_investment_signal(
        self,
        signal_data: Dict[str, Any]
    ) -> bool:
        """
        Send investment signal alert

        Args:
            signal_data: Signal data from SignalGenerator

        Returns:
            Success status
        """
        signal = signal_data.get('signal', 'UNKNOWN')
        confidence = signal_data.get('confidence', 0)
        score = signal_data.get('score', 0)
        action_plan = signal_data.get('action_plan', {})

        # Create message
        message = f"""
🎯 **투자 신호 업데이트**

📊 **신호**: {self._format_signal(signal)}
💡 **신뢰도**: {confidence:.0f}%
⭐ **점수**: {score:.1f}/10

💼 **추천 액션**
{action_plan.get('action', 'N/A')}

⏰ **시간대**: {action_plan.get('timeframe', 'N/A')}

🎯 **목표 자산 배분**
{self._format_allocation(action_plan.get('target_allocation', {}))}

---
⏰ 시간: {datetime.now().strftime('%Y-%m-%d %H:%M')}
        """.strip()

        return await self.send_message(message)

    async def send_daily_briefing(
        self,
        briefing: str,
        signal_data: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Send daily market briefing

        Args:
            briefing: Daily briefing text
            signal_data: Optional signal data

        Returns:
            Success status
        """
        message = f"""
📰 **일일 시장 브리핑**

{briefing}

---
⏰ {datetime.now().strftime('%Y-%m-%d %H:%M')}
        """.strip()

        # Add signal if provided
        if signal_data:
            signal = signal_data.get('signal', 'UNKNOWN')
            confidence = signal_data.get('confidence', 0)
            message += f"\n\n🎯 **현재 신호**: {self._format_signal(signal)} (신뢰도 {confidence:.0f}%)"

        return await self.send_message(message)

    async def send_extreme_market_alert(
        self,
        fear_greed_score: float,
        market_data: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Send alert for extreme market conditions

        Args:
            fear_greed_score: Fear & Greed Index score
            market_data: Additional market data

        Returns:
            Success status
        """
        if fear_greed_score >= 75:
            emoji = "🔥"
            status = "**극단적 탐욕 (Extreme Greed)**"
            action = "⚠️ 조정 가능성 주의! 포지션 축소 고려"
        elif fear_greed_score <= 25:
            emoji = "❄️"
            status = "**극단적 공포 (Extreme Fear)**"
            action = "💡 매수 기회! 역발상 전략 고려"
        else:
            # Not extreme - no alert
            return False

        message = f"""
{emoji} **시장 알림: 극단적 심리 상태**

📊 Fear & Greed Index: **{fear_greed_score:.0f}**
{status}

{action}

---
⏰ {datetime.now().strftime('%Y-%m-%d %H:%M')}
        """.strip()

        # Add market data if provided
        if market_data:
            sp500_change = market_data.get('sp500_change_pct', 0)
            nasdaq_change = market_data.get('nasdaq_change_pct', 0)

            message += f"\n\n📈 **미국 시장**"
            message += f"\nS&P 500: {sp500_change:+.2f}%"
            message += f"\nNASDAQ: {nasdaq_change:+.2f}%"

        return await self.send_message(message)

    async def send_economic_alert(
        self,
        alert_type: str,
        data: Dict[str, Any]
    ) -> bool:
        """
        Send economic indicator alert

        Args:
            alert_type: Alert type (rate_hike, yield_curve_inversion, etc.)
            data: Alert data

        Returns:
            Success status
        """
        if alert_type == 'rate_hike':
            emoji = "📈"
            title = "금리 인상 감지"
            message = f"""
{emoji} **{title}**

🇺🇸 미국 기준금리: {data.get('fed_rate', 'N/A')}%
🇰🇷 한국 기준금리: {data.get('kr_rate', 'N/A')}%
📊 금리 차이: {data.get('spread', 'N/A')}%p

{data.get('impact', '')}
            """.strip()

        elif alert_type == 'yield_curve_inversion':
            emoji = "⚠️"
            title = "수익률 곡선 역전 (Recession Signal)"
            message = f"""
{emoji} **{title}**

📊 10Y-2Y Spread: {data.get('spread_10y_2y', 'N/A')}%p
📉 경기 침체 확률: {data.get('recession_probability', 0):.0f}%

⚠️ 경기 침체 가능성 증가 - 포트폴리오 재검토 권장
            """.strip()

        elif alert_type == 'rate_cut':
            emoji = "📉"
            title = "금리 인하 감지"
            message = f"""
{emoji} **{title}**

🇺🇸 미국 기준금리: {data.get('fed_rate', 'N/A')}%
🇰🇷 한국 기준금리: {data.get('kr_rate', 'N/A')}%

💡 성장주 수혜 예상
            """.strip()
        else:
            # Unknown alert type
            return False

        message += f"\n\n---\n⏰ {datetime.now().strftime('%Y-%m-%d %H:%M')}"

        return await self.send_message(message)

    async def send_signal_change_alert(
        self,
        old_signal: str,
        new_signal: str,
        confidence: float
    ) -> bool:
        """
        Send alert when investment signal changes

        Args:
            old_signal: Previous signal
            new_signal: New signal
            confidence: New signal confidence

        Returns:
            Success status
        """
        message = f"""
🔔 **투자 신호 변경**

{self._format_signal(old_signal)} → {self._format_signal(new_signal)}

💡 **신뢰도**: {confidence:.0f}%

---
⏰ {datetime.now().strftime('%Y-%m-%d %H:%M')}
        """.strip()

        return await self.send_message(message)

    async def send_custom_alert(
        self,
        title: str,
        message: str,
        emoji: str = "📢"
    ) -> bool:
        """
        Send custom alert

        Args:
            title: Alert title
            message: Alert message
            emoji: Emoji prefix

        Returns:
            Success status
        """
        formatted_message = f"""
{emoji} **{title}**

{message}

---
⏰ {datetime.now().strftime('%Y-%m-%d %H:%M')}
        """.strip()

        return await self.send_message(formatted_message)

    def _format_signal(self, signal: str) -> str:
        """Format signal with emoji"""
        signal_emojis = {
            'STRONG_BUY': '🟢🟢 강한 매수',
            'BUY': '🟢 매수',
            'WEAK_BUY': '🟡 약한 매수',
            'HOLD': '⚪ 관망',
            'WEAK_SELL': '🟠 약한 매도',
            'SELL': '🔴 매도',
            'STRONG_SELL': '🔴🔴 강한 매도'
        }
        return signal_emojis.get(signal, signal)

    def _format_allocation(self, allocation: Dict[str, str]) -> str:
        """Format asset allocation"""
        if not allocation:
            return "N/A"

        lines = []
        for asset, percent in allocation.items():
            lines.append(f"  • {asset}: {percent}")

        return "\n".join(lines)

    async def test_connection(self) -> bool:
        """
        Test Telegram bot connection

        Returns:
            Success status
        """
        if not self.bot:
            logger.error("Telegram bot not initialized")
            return False

        try:
            me = await self.bot.get_me()
            logger.info(f"Telegram bot connected: @{me.username}")

            # Send test message
            test_message = f"""
✅ **Telegram Bot 연결 성공**

봇 이름: {me.first_name}
사용자명: @{me.username}

시간: {datetime.now().strftime('%Y-%m-%d %H:%M')}
            """.strip()

            return await self.send_message(test_message)

        except TelegramError as e:
            logger.error(f"Telegram connection test failed: {str(e)}")
            return False


# Convenience function
async def send_telegram_alert(
    message: str,
    bot_token: Optional[str] = None,
    chat_id: Optional[str] = None
) -> bool:
    """
    Quick function to send a Telegram alert

    Args:
        message: Message to send
        bot_token: Bot token (or from env)
        chat_id: Chat ID (or from env)

    Returns:
        Success status
    """
    bot = TelegramBot(bot_token, chat_id)
    return await bot.send_message(message)
