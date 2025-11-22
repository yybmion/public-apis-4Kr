"""
Alert Manager - Centralized Alert Management

통합 알림 관리 시스템

Features:
- Telegram 및 Email 통합 관리
- 알림 설정 관리
- 알림 히스토리 추적
- 중복 알림 방지

Author: AI Assistant
Created: 2025-11-22
"""

import os
import asyncio
from typing import Dict, Any, Optional, List, Set
from datetime import datetime, timedelta
import logging
import json

from app.alerts.telegram_bot import TelegramBot
from app.alerts.email_notifier import EmailNotifier

# Setup logging
logger = logging.getLogger(__name__)


class AlertConfig:
    """Alert configuration settings"""

    def __init__(self):
        """Initialize alert configuration from environment"""
        # Channels
        self.telegram_enabled = os.getenv('ALERT_TELEGRAM_ENABLED', 'true').lower() == 'true'
        self.email_enabled = os.getenv('ALERT_EMAIL_ENABLED', 'true').lower() == 'true'

        # Thresholds
        self.extreme_fear_threshold = float(os.getenv('ALERT_EXTREME_FEAR', '25'))
        self.extreme_greed_threshold = float(os.getenv('ALERT_EXTREME_GREED', '75'))
        self.signal_change_alert = os.getenv('ALERT_SIGNAL_CHANGE', 'true').lower() == 'true'

        # Schedules
        self.daily_briefing_time = os.getenv('ALERT_DAILY_TIME', '09:00')
        self.weekly_report_day = int(os.getenv('ALERT_WEEKLY_DAY', '0'))  # Monday

        # Rate limiting
        self.min_alert_interval_minutes = int(os.getenv('ALERT_MIN_INTERVAL', '60'))

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'telegram_enabled': self.telegram_enabled,
            'email_enabled': self.email_enabled,
            'extreme_fear_threshold': self.extreme_fear_threshold,
            'extreme_greed_threshold': self.extreme_greed_threshold,
            'signal_change_alert': self.signal_change_alert,
            'daily_briefing_time': self.daily_briefing_time,
            'weekly_report_day': self.weekly_report_day,
            'min_alert_interval_minutes': self.min_alert_interval_minutes
        }


class AlertManager:
    """
    Centralized Alert Manager

    Manages both Telegram and Email alerts with:
    - Configuration management
    - Alert history tracking
    - Duplicate prevention
    - Rate limiting
    """

    def __init__(self, config: Optional[AlertConfig] = None):
        """
        Initialize Alert Manager

        Args:
            config: Alert configuration (or default)
        """
        self.config = config or AlertConfig()
        self.telegram = TelegramBot() if self.config.telegram_enabled else None
        self.email = EmailNotifier() if self.config.email_enabled else None

        # Alert history for duplicate prevention
        self.alert_history: Dict[str, datetime] = {}
        self.signal_history: List[Dict[str, Any]] = []

        logger.info("Alert Manager initialized")
        logger.info(f"Telegram enabled: {self.config.telegram_enabled}")
        logger.info(f"Email enabled: {self.config.email_enabled}")

    async def send_investment_signal(
        self,
        signal_data: Dict[str, Any],
        force: bool = False
    ) -> Dict[str, bool]:
        """
        Send investment signal alert

        Args:
            signal_data: Signal data from SignalGenerator
            force: Force send (ignore rate limiting)

        Returns:
            Dictionary with channel statuses
        """
        # Check rate limiting
        if not force and not self._should_send_alert('investment_signal'):
            logger.info("Investment signal alert skipped (rate limited)")
            return {'telegram': False, 'email': False}

        results = {}

        # Send to Telegram
        if self.telegram:
            try:
                results['telegram'] = await self.telegram.send_investment_signal(signal_data)
            except Exception as e:
                logger.error(f"Failed to send Telegram signal: {str(e)}")
                results['telegram'] = False
        else:
            results['telegram'] = False

        # Send to Email (less frequently - only on signal changes)
        if self.email and self.config.signal_change_alert:
            try:
                # Email sends daily report instead of individual signals
                results['email'] = False  # Will be sent in daily report
            except Exception as e:
                logger.error(f"Failed to send Email signal: {str(e)}")
                results['email'] = False
        else:
            results['email'] = False

        # Update history
        self._record_alert('investment_signal')
        self._record_signal(signal_data)

        return results

    async def send_daily_briefing(
        self,
        briefing: str,
        signal_data: Optional[Dict[str, Any]] = None,
        market_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, bool]:
        """
        Send daily briefing

        Args:
            briefing: Daily briefing text
            signal_data: Optional signal data
            market_data: Optional market data

        Returns:
            Dictionary with channel statuses
        """
        results = {}

        # Send to Telegram
        if self.telegram:
            try:
                results['telegram'] = await self.telegram.send_daily_briefing(briefing, signal_data)
            except Exception as e:
                logger.error(f"Failed to send Telegram briefing: {str(e)}")
                results['telegram'] = False
        else:
            results['telegram'] = False

        # Send to Email (full report)
        if self.email and signal_data and market_data:
            try:
                results['email'] = self.email.send_daily_report(signal_data, market_data, briefing)
            except Exception as e:
                logger.error(f"Failed to send Email report: {str(e)}")
                results['email'] = False
        else:
            results['email'] = False

        self._record_alert('daily_briefing')
        return results

    async def send_extreme_market_alert(
        self,
        fear_greed_score: float,
        market_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, bool]:
        """
        Send alert for extreme market conditions

        Args:
            fear_greed_score: Fear & Greed Index score
            market_data: Optional market data

        Returns:
            Dictionary with channel statuses
        """
        # Check if extreme
        is_extreme_fear = fear_greed_score <= self.config.extreme_fear_threshold
        is_extreme_greed = fear_greed_score >= self.config.extreme_greed_threshold

        if not (is_extreme_fear or is_extreme_greed):
            return {'telegram': False, 'email': False}

        # Check rate limiting (prevent spam)
        if not self._should_send_alert(f'extreme_market_{fear_greed_score:.0f}', min_interval=180):
            logger.info("Extreme market alert skipped (rate limited)")
            return {'telegram': False, 'email': False}

        results = {}

        # Send to Telegram
        if self.telegram:
            try:
                results['telegram'] = await self.telegram.send_extreme_market_alert(
                    fear_greed_score, market_data or {}
                )
            except Exception as e:
                logger.error(f"Failed to send Telegram extreme alert: {str(e)}")
                results['telegram'] = False
        else:
            results['telegram'] = False

        # Send to Email
        if self.email and market_data:
            try:
                results['email'] = self.email.send_extreme_market_alert(fear_greed_score, market_data)
            except Exception as e:
                logger.error(f"Failed to send Email extreme alert: {str(e)}")
                results['email'] = False
        else:
            results['email'] = False

        self._record_alert(f'extreme_market_{fear_greed_score:.0f}')
        return results

    async def send_signal_change_alert(
        self,
        old_signal: str,
        new_signal: str,
        confidence: float,
        reason: str = ""
    ) -> Dict[str, bool]:
        """
        Send alert when signal changes

        Args:
            old_signal: Previous signal
            new_signal: New signal
            confidence: Confidence level
            reason: Reason for change

        Returns:
            Dictionary with channel statuses
        """
        if not self.config.signal_change_alert:
            return {'telegram': False, 'email': False}

        # Check if meaningful change
        if old_signal == new_signal:
            return {'telegram': False, 'email': False}

        results = {}

        # Send to Telegram
        if self.telegram:
            try:
                results['telegram'] = await self.telegram.send_signal_change_alert(
                    old_signal, new_signal, confidence
                )
            except Exception as e:
                logger.error(f"Failed to send Telegram change alert: {str(e)}")
                results['telegram'] = False
        else:
            results['telegram'] = False

        # Send to Email
        if self.email:
            try:
                results['email'] = self.email.send_signal_change_alert(
                    old_signal, new_signal, confidence, reason
                )
            except Exception as e:
                logger.error(f"Failed to send Email change alert: {str(e)}")
                results['email'] = False
        else:
            results['email'] = False

        self._record_alert('signal_change')
        return results

    async def send_economic_alert(
        self,
        alert_type: str,
        data: Dict[str, Any]
    ) -> Dict[str, bool]:
        """
        Send economic indicator alert

        Args:
            alert_type: Alert type (rate_hike, yield_curve_inversion, etc.)
            data: Alert data

        Returns:
            Dictionary with channel statuses
        """
        # Check rate limiting
        if not self._should_send_alert(f'economic_{alert_type}', min_interval=1440):  # 24 hours
            logger.info(f"Economic alert {alert_type} skipped (rate limited)")
            return {'telegram': False, 'email': False}

        results = {}

        # Send to Telegram
        if self.telegram:
            try:
                results['telegram'] = await self.telegram.send_economic_alert(alert_type, data)
            except Exception as e:
                logger.error(f"Failed to send Telegram economic alert: {str(e)}")
                results['telegram'] = False
        else:
            results['telegram'] = False

        # Email doesn't have separate economic alerts (included in daily report)
        results['email'] = False

        self._record_alert(f'economic_{alert_type}')
        return results

    async def send_weekly_report(
        self,
        performance_data: Dict[str, Any],
        signals_history: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, bool]:
        """
        Send weekly performance report

        Args:
            performance_data: Weekly performance metrics
            signals_history: Optional signal history (uses internal if not provided)

        Returns:
            Dictionary with channel statuses
        """
        results = {}

        # Use internal signal history if not provided
        if signals_history is None:
            signals_history = self.signal_history[-7:]  # Last 7 signals

        # Weekly report primarily via Email
        if self.email:
            try:
                results['email'] = self.email.send_weekly_report(performance_data, signals_history)
            except Exception as e:
                logger.error(f"Failed to send Email weekly report: {str(e)}")
                results['email'] = False
        else:
            results['email'] = False

        # Telegram gets a summary
        if self.telegram:
            try:
                summary = self._generate_weekly_summary(performance_data)
                results['telegram'] = await self.telegram.send_custom_alert(
                    "주간 성과 리포트",
                    summary,
                    "📈"
                )
            except Exception as e:
                logger.error(f"Failed to send Telegram weekly summary: {str(e)}")
                results['telegram'] = False
        else:
            results['telegram'] = False

        self._record_alert('weekly_report')
        return results

    async def send_custom_alert(
        self,
        title: str,
        message: str,
        channels: Optional[List[str]] = None
    ) -> Dict[str, bool]:
        """
        Send custom alert

        Args:
            title: Alert title
            message: Alert message
            channels: Channels to send to (['telegram', 'email'] or None for all)

        Returns:
            Dictionary with channel statuses
        """
        results = {}

        # Determine channels
        send_telegram = (channels is None or 'telegram' in channels) and self.telegram
        send_email = (channels is None or 'email' in channels) and self.email

        # Send to Telegram
        if send_telegram:
            try:
                results['telegram'] = await self.telegram.send_custom_alert(title, message)
            except Exception as e:
                logger.error(f"Failed to send Telegram custom alert: {str(e)}")
                results['telegram'] = False
        else:
            results['telegram'] = False

        # Send to Email
        if send_email:
            try:
                results['email'] = self.email.send_email(title, message)
            except Exception as e:
                logger.error(f"Failed to send Email custom alert: {str(e)}")
                results['email'] = False
        else:
            results['email'] = False

        return results

    async def test_all_channels(self) -> Dict[str, bool]:
        """
        Test all alert channels

        Returns:
            Dictionary with channel test results
        """
        results = {}

        # Test Telegram
        if self.telegram:
            try:
                results['telegram'] = await self.telegram.test_connection()
            except Exception as e:
                logger.error(f"Telegram test failed: {str(e)}")
                results['telegram'] = False
        else:
            results['telegram'] = False

        # Test Email
        if self.email:
            try:
                results['email'] = self.email.test_connection()
            except Exception as e:
                logger.error(f"Email test failed: {str(e)}")
                results['email'] = False
        else:
            results['email'] = False

        return results

    def get_signal_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get recent signal history

        Args:
            limit: Maximum number of signals to return

        Returns:
            List of recent signals
        """
        return self.signal_history[-limit:]

    def get_alert_history(self) -> Dict[str, datetime]:
        """
        Get alert history

        Returns:
            Dictionary of alert types and last send times
        """
        return self.alert_history.copy()

    def clear_history(self):
        """Clear all history"""
        self.alert_history.clear()
        self.signal_history.clear()
        logger.info("Alert history cleared")

    # Private methods

    def _should_send_alert(
        self,
        alert_key: str,
        min_interval: Optional[int] = None
    ) -> bool:
        """
        Check if alert should be sent (rate limiting)

        Args:
            alert_key: Alert identifier
            min_interval: Minimum interval in minutes (or use config default)

        Returns:
            True if alert should be sent
        """
        if alert_key not in self.alert_history:
            return True

        last_sent = self.alert_history[alert_key]
        interval = min_interval or self.config.min_alert_interval_minutes
        elapsed = (datetime.now() - last_sent).total_seconds() / 60

        return elapsed >= interval

    def _record_alert(self, alert_key: str):
        """Record alert in history"""
        self.alert_history[alert_key] = datetime.now()

    def _record_signal(self, signal_data: Dict[str, Any]):
        """Record signal in history"""
        self.signal_history.append({
            'date': datetime.now().strftime('%Y-%m-%d %H:%M'),
            'signal': signal_data.get('signal', 'UNKNOWN'),
            'confidence': signal_data.get('confidence', 0),
            'score': signal_data.get('score', 0)
        })

        # Keep only last 100 signals
        if len(self.signal_history) > 100:
            self.signal_history = self.signal_history[-100:]

    def _generate_weekly_summary(self, performance_data: Dict[str, Any]) -> str:
        """Generate weekly summary text"""
        return f"""
주간 성과:
• 총 수익률: {performance_data.get('total_return_pct', 0):+.2f}%
• 최대 낙폭: {performance_data.get('max_drawdown_pct', 0):.2f}%
• 승률: {performance_data.get('win_rate', 0) * 100:.1f}%

자세한 내용은 이메일 리포트를 확인하세요.
        """.strip()


# Singleton instance
_alert_manager: Optional[AlertManager] = None


def get_alert_manager() -> AlertManager:
    """
    Get singleton Alert Manager instance

    Returns:
        AlertManager instance
    """
    global _alert_manager
    if _alert_manager is None:
        _alert_manager = AlertManager()
    return _alert_manager
