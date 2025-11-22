"""
Email Notifier for Investment Alerts

이메일을 통한 투자 알림 및 리포트 전송

Features:
- 일일 투자 리포트
- 주간 성과 리포트
- 중요 신호 변경 알림
- HTML 포맷 이메일

Author: AI Assistant
Created: 2025-11-22
"""

import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, Any, Optional, List
from datetime import datetime
import logging

# Setup logging
logger = logging.getLogger(__name__)


class EmailNotifier:
    """
    Email Notifier for sending investment reports

    Environment Variables:
        SMTP_SERVER: SMTP server (e.g., smtp.gmail.com)
        SMTP_PORT: SMTP port (e.g., 587)
        SMTP_USERNAME: SMTP username (email)
        SMTP_PASSWORD: SMTP password (app password for Gmail)
        EMAIL_FROM: From email address
        EMAIL_TO: To email address(es) (comma-separated)
    """

    def __init__(
        self,
        smtp_server: Optional[str] = None,
        smtp_port: Optional[int] = None,
        username: Optional[str] = None,
        password: Optional[str] = None,
        from_email: Optional[str] = None,
        to_emails: Optional[List[str]] = None
    ):
        """
        Initialize Email Notifier

        Args:
            smtp_server: SMTP server address
            smtp_port: SMTP port
            username: SMTP username
            password: SMTP password
            from_email: From email address
            to_emails: List of recipient emails
        """
        self.smtp_server = smtp_server or os.getenv('SMTP_SERVER', 'smtp.gmail.com')
        self.smtp_port = smtp_port or int(os.getenv('SMTP_PORT', '587'))
        self.username = username or os.getenv('SMTP_USERNAME')
        self.password = password or os.getenv('SMTP_PASSWORD')
        self.from_email = from_email or os.getenv('EMAIL_FROM', self.username)

        to_emails_str = os.getenv('EMAIL_TO', '')
        self.to_emails = to_emails or [e.strip() for e in to_emails_str.split(',') if e.strip()]

        if not all([self.username, self.password]):
            logger.warning("SMTP credentials not set. Email alerts disabled.")
            self.enabled = False
        else:
            self.enabled = True

        if not self.to_emails:
            logger.warning("EMAIL_TO not set. Cannot send emails.")
            self.enabled = False

    def send_email(
        self,
        subject: str,
        body_text: str,
        body_html: Optional[str] = None
    ) -> bool:
        """
        Send an email

        Args:
            subject: Email subject
            body_text: Plain text body
            body_html: Optional HTML body

        Returns:
            Success status
        """
        if not self.enabled:
            logger.warning("Email notifier not configured. Email not sent.")
            return False

        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = self.from_email
            msg['To'] = ', '.join(self.to_emails)

            # Attach plain text
            part1 = MIMEText(body_text, 'plain', 'utf-8')
            msg.attach(part1)

            # Attach HTML if provided
            if body_html:
                part2 = MIMEText(body_html, 'html', 'utf-8')
                msg.attach(part2)

            # Send email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.username, self.password)
                server.send_message(msg)

            logger.info(f"Email sent to {', '.join(self.to_emails)}: {subject}")
            return True

        except smtplib.SMTPException as e:
            logger.error(f"SMTP error sending email: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error sending email: {str(e)}")
            return False

    def send_daily_report(
        self,
        signal_data: Dict[str, Any],
        market_data: Dict[str, Any],
        briefing: str
    ) -> bool:
        """
        Send daily investment report

        Args:
            signal_data: Investment signal data
            market_data: Market data
            briefing: Daily briefing text

        Returns:
            Success status
        """
        subject = f"📊 일일 투자 리포트 - {datetime.now().strftime('%Y-%m-%d')}"

        # Plain text version
        body_text = f"""
일일 투자 리포트
{datetime.now().strftime('%Y년 %m월 %d일')}

=== 투자 신호 ===
신호: {signal_data.get('signal', 'N/A')}
신뢰도: {signal_data.get('confidence', 0):.0f}%
점수: {signal_data.get('score', 0):.1f}/10

추천 액션: {signal_data.get('action_plan', {}).get('action', 'N/A')}

=== 시장 현황 ===
{briefing}

=== 목표 자산 배분 ===
{self._format_allocation_text(signal_data.get('action_plan', {}).get('target_allocation', {}))}

---
Stock Intelligence System
        """.strip()

        # HTML version
        body_html = self._generate_daily_report_html(signal_data, market_data, briefing)

        return self.send_email(subject, body_text, body_html)

    def send_weekly_report(
        self,
        performance_data: Dict[str, Any],
        signals_history: List[Dict[str, Any]]
    ) -> bool:
        """
        Send weekly performance report

        Args:
            performance_data: Weekly performance metrics
            signals_history: Signal history for the week

        Returns:
            Success status
        """
        subject = f"📈 주간 투자 리포트 - {datetime.now().strftime('%Y-%m-%d')}"

        # Plain text version
        body_text = f"""
주간 투자 리포트
{datetime.now().strftime('%Y년 %m월 %d일')}

=== 주간 성과 ===
총 수익률: {performance_data.get('total_return_pct', 0):+.2f}%
최대 낙폭: {performance_data.get('max_drawdown_pct', 0):.2f}%
승률: {performance_data.get('win_rate', 0) * 100:.1f}%

=== 신호 변경 내역 ===
이번 주 신호 변경 횟수: {len(signals_history)}

{self._format_signals_history_text(signals_history)}

---
Stock Intelligence System
        """.strip()

        # HTML version
        body_html = self._generate_weekly_report_html(performance_data, signals_history)

        return self.send_email(subject, body_text, body_html)

    def send_signal_change_alert(
        self,
        old_signal: str,
        new_signal: str,
        confidence: float,
        reason: str = ""
    ) -> bool:
        """
        Send alert for signal change

        Args:
            old_signal: Previous signal
            new_signal: New signal
            confidence: Confidence level
            reason: Reason for change

        Returns:
            Success status
        """
        subject = f"🔔 투자 신호 변경: {old_signal} → {new_signal}"

        body_text = f"""
투자 신호 변경 알림

이전 신호: {old_signal}
새 신호: {new_signal}
신뢰도: {confidence:.0f}%

{reason}

시간: {datetime.now().strftime('%Y-%m-%d %H:%M')}

---
Stock Intelligence System
        """.strip()

        body_html = f"""
<html>
<body style="font-family: Arial, sans-serif; line-height: 1.6;">
    <h2 style="color: #2c3e50;">🔔 투자 신호 변경 알림</h2>
    <p><strong>이전 신호:</strong> {old_signal}</p>
    <p><strong>새 신호:</strong> <span style="color: #e74c3c; font-size: 1.2em;">{new_signal}</span></p>
    <p><strong>신뢰도:</strong> {confidence:.0f}%</p>
    {f'<p>{reason}</p>' if reason else ''}
    <hr>
    <p style="color: #7f8c8d; font-size: 0.9em;">
        시간: {datetime.now().strftime('%Y-%m-%d %H:%M')}<br>
        Stock Intelligence System
    </p>
</body>
</html>
        """.strip()

        return self.send_email(subject, body_text, body_html)

    def send_extreme_market_alert(
        self,
        fear_greed_score: float,
        market_data: Dict[str, Any]
    ) -> bool:
        """
        Send alert for extreme market conditions

        Args:
            fear_greed_score: Fear & Greed Index score
            market_data: Market data

        Returns:
            Success status
        """
        if fear_greed_score >= 75:
            status = "극단적 탐욕 (Extreme Greed)"
            emoji = "🔥"
        elif fear_greed_score <= 25:
            status = "극단적 공포 (Extreme Fear)"
            emoji = "❄️"
        else:
            return False

        subject = f"{emoji} 시장 알림: {status}"

        body_text = f"""
시장 심리 극단 알림

Fear & Greed Index: {fear_greed_score:.0f}
상태: {status}

미국 시장:
- S&P 500: {market_data.get('sp500_change_pct', 0):+.2f}%
- NASDAQ: {market_data.get('nasdaq_change_pct', 0):+.2f}%

시간: {datetime.now().strftime('%Y-%m-%d %H:%M')}

---
Stock Intelligence System
        """.strip()

        body_html = f"""
<html>
<body style="font-family: Arial, sans-serif; line-height: 1.6;">
    <h2 style="color: #e74c3c;">{emoji} 시장 심리 극단 알림</h2>
    <p><strong>Fear & Greed Index:</strong> <span style="font-size: 1.5em; color: #e74c3c;">{fear_greed_score:.0f}</span></p>
    <p><strong>상태:</strong> {status}</p>
    <h3>미국 시장</h3>
    <ul>
        <li>S&P 500: {market_data.get('sp500_change_pct', 0):+.2f}%</li>
        <li>NASDAQ: {market_data.get('nasdaq_change_pct', 0):+.2f}%</li>
    </ul>
    <hr>
    <p style="color: #7f8c8d; font-size: 0.9em;">
        시간: {datetime.now().strftime('%Y-%m-%d %H:%M')}<br>
        Stock Intelligence System
    </p>
</body>
</html>
        """.strip()

        return self.send_email(subject, body_text, body_html)

    def test_connection(self) -> bool:
        """
        Test email connection

        Returns:
            Success status
        """
        if not self.enabled:
            logger.error("Email notifier not configured")
            return False

        subject = "✅ Email Notifier 테스트"
        body_text = f"""
Email Notifier 연결 성공

SMTP 서버: {self.smtp_server}:{self.smtp_port}
발신자: {self.from_email}
수신자: {', '.join(self.to_emails)}

시간: {datetime.now().strftime('%Y-%m-%d %H:%M')}

---
Stock Intelligence System
        """.strip()

        return self.send_email(subject, body_text)

    # HTML generation helpers

    def _generate_daily_report_html(
        self,
        signal_data: Dict[str, Any],
        market_data: Dict[str, Any],
        briefing: str
    ) -> str:
        """Generate HTML for daily report"""
        signal = signal_data.get('signal', 'N/A')
        confidence = signal_data.get('confidence', 0)
        score = signal_data.get('score', 0)
        action_plan = signal_data.get('action_plan', {})

        # Signal color
        signal_color = self._get_signal_color(signal)

        html = f"""
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        h2 {{ color: #2c3e50; }}
        .signal-box {{ background-color: {signal_color}; color: white; padding: 15px; border-radius: 5px; margin: 10px 0; }}
        .metric {{ display: inline-block; margin: 10px 20px 10px 0; }}
        .allocation {{ background-color: #ecf0f1; padding: 15px; border-radius: 5px; margin: 10px 0; }}
        .footer {{ color: #7f8c8d; font-size: 0.9em; margin-top: 20px; padding-top: 10px; border-top: 1px solid #bdc3c7; }}
    </style>
</head>
<body>
    <h2>📊 일일 투자 리포트</h2>
    <p>{datetime.now().strftime('%Y년 %m월 %d일')}</p>

    <div class="signal-box">
        <h3 style="margin: 0 0 10px 0;">투자 신호</h3>
        <div class="metric"><strong>신호:</strong> {signal}</div>
        <div class="metric"><strong>신뢰도:</strong> {confidence:.0f}%</div>
        <div class="metric"><strong>점수:</strong> {score:.1f}/10</div>
    </div>

    <h3>추천 액션</h3>
    <p>{action_plan.get('action', 'N/A')}</p>
    <p><strong>시간대:</strong> {action_plan.get('timeframe', 'N/A')}</p>

    <h3>시장 현황</h3>
    <p style="white-space: pre-line;">{briefing}</p>

    <div class="allocation">
        <h3>목표 자산 배분</h3>
        {self._format_allocation_html(action_plan.get('target_allocation', {}))}
    </div>

    <div class="footer">
        Stock Intelligence System<br>
        Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}
    </div>
</body>
</html>
        """.strip()

        return html

    def _generate_weekly_report_html(
        self,
        performance_data: Dict[str, Any],
        signals_history: List[Dict[str, Any]]
    ) -> str:
        """Generate HTML for weekly report"""
        html = f"""
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        h2 {{ color: #2c3e50; }}
        .metric-box {{ background-color: #3498db; color: white; padding: 15px; border-radius: 5px; margin: 10px 0; }}
        .metric {{ display: inline-block; margin: 10px 20px 10px 0; }}
        table {{ border-collapse: collapse; width: 100%; margin: 10px 0; }}
        th, td {{ border: 1px solid #bdc3c7; padding: 8px; text-align: left; }}
        th {{ background-color: #34495e; color: white; }}
        .footer {{ color: #7f8c8d; font-size: 0.9em; margin-top: 20px; padding-top: 10px; border-top: 1px solid #bdc3c7; }}
    </style>
</head>
<body>
    <h2>📈 주간 투자 리포트</h2>
    <p>{datetime.now().strftime('%Y년 %m월 %d일')}</p>

    <div class="metric-box">
        <h3 style="margin: 0 0 10px 0;">주간 성과</h3>
        <div class="metric"><strong>총 수익률:</strong> {performance_data.get('total_return_pct', 0):+.2f}%</div>
        <div class="metric"><strong>최대 낙폭:</strong> {performance_data.get('max_drawdown_pct', 0):.2f}%</div>
        <div class="metric"><strong>승률:</strong> {performance_data.get('win_rate', 0) * 100:.1f}%</div>
    </div>

    <h3>신호 변경 내역</h3>
    <p>이번 주 신호 변경 횟수: {len(signals_history)}</p>

    {self._format_signals_history_html(signals_history)}

    <div class="footer">
        Stock Intelligence System<br>
        Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}
    </div>
</body>
</html>
        """.strip()

        return html

    def _get_signal_color(self, signal: str) -> str:
        """Get color for signal"""
        colors = {
            'STRONG_BUY': '#27ae60',
            'BUY': '#2ecc71',
            'WEAK_BUY': '#f39c12',
            'HOLD': '#95a5a6',
            'WEAK_SELL': '#e67e22',
            'SELL': '#e74c3c',
            'STRONG_SELL': '#c0392b'
        }
        return colors.get(signal, '#95a5a6')

    def _format_allocation_text(self, allocation: Dict[str, str]) -> str:
        """Format allocation for plain text"""
        if not allocation:
            return "N/A"
        return "\n".join([f"- {asset}: {percent}" for asset, percent in allocation.items()])

    def _format_allocation_html(self, allocation: Dict[str, str]) -> str:
        """Format allocation for HTML"""
        if not allocation:
            return "<p>N/A</p>"
        items = "".join([f"<li>{asset}: {percent}</li>" for asset, percent in allocation.items()])
        return f"<ul>{items}</ul>"

    def _format_signals_history_text(self, signals: List[Dict[str, Any]]) -> str:
        """Format signals history for plain text"""
        if not signals:
            return "변경 없음"
        lines = []
        for sig in signals:
            lines.append(f"- {sig.get('date', 'N/A')}: {sig.get('signal', 'N/A')} (신뢰도 {sig.get('confidence', 0):.0f}%)")
        return "\n".join(lines)

    def _format_signals_history_html(self, signals: List[Dict[str, Any]]) -> str:
        """Format signals history for HTML"""
        if not signals:
            return "<p>변경 없음</p>"

        rows = ""
        for sig in signals:
            rows += f"""
            <tr>
                <td>{sig.get('date', 'N/A')}</td>
                <td>{sig.get('signal', 'N/A')}</td>
                <td>{sig.get('confidence', 0):.0f}%</td>
            </tr>
            """

        return f"""
        <table>
            <thead>
                <tr>
                    <th>날짜</th>
                    <th>신호</th>
                    <th>신뢰도</th>
                </tr>
            </thead>
            <tbody>
                {rows}
            </tbody>
        </table>
        """


# Convenience function
def send_email_alert(
    subject: str,
    message: str,
    html_message: Optional[str] = None
) -> bool:
    """
    Quick function to send an email alert

    Args:
        subject: Email subject
        message: Plain text message
        html_message: Optional HTML message

    Returns:
        Success status
    """
    notifier = EmailNotifier()
    return notifier.send_email(subject, message, html_message)
