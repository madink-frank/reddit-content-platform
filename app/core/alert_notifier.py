"""
Alert notification system for critical errors.
"""

import json
import smtplib
import asyncio
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, Any, Optional, List
import httpx

from app.core.config import settings
from app.core.logging import get_logger, ErrorCategory


logger = get_logger(__name__)


class AlertNotifier:
    """
    Alert notification system for critical errors.
    Supports Slack, email, and webhook notifications.
    """
    
    def __init__(self):
        """Initialize the alert notifier."""
        self.environment = settings.ENVIRONMENT
        self.service_name = settings.PROJECT_NAME
        
        # Configure notification channels
        self.slack_enabled = bool(settings.ALERT_SLACK_WEBHOOK)
        self.email_enabled = settings.ALERT_EMAIL_ENABLED and settings.SMTP_HOST and settings.ADMIN_EMAIL
        self.webhook_enabled = bool(settings.ALERT_WEBHOOK_URL)
    
    async def notify(self, message: str, error_category: str, 
                    alert_level: str, details: Dict[str, Any] = None) -> bool:
        """
        Send alert notification to configured channels.
        
        Args:
            message: Alert message
            error_category: Error category (e.g., "database", "system")
            alert_level: Alert level (e.g., "high", "critical")
            details: Additional alert details
        
        Returns:
            bool: True if notification was sent successfully
        """
        if not self._should_send_alert(error_category, alert_level):
            return False
        
        # Prepare alert data
        alert_data = self._prepare_alert_data(message, error_category, alert_level, details)
        
        # Send notifications in parallel
        tasks = []
        
        if self.slack_enabled:
            tasks.append(self._send_slack_notification(alert_data))
        
        if self.email_enabled:
            tasks.append(self._send_email_notification(alert_data))
        
        if self.webhook_enabled:
            tasks.append(self._send_webhook_notification(alert_data))
        
        # Wait for all notifications to complete
        if tasks:
            results = await asyncio.gather(*tasks, return_exceptions=True)
            return any(result is True for result in results)
        
        return False
    
    def _should_send_alert(self, error_category: str, alert_level: str) -> bool:
        """
        Determine if an alert should be sent based on category and level.
        
        Args:
            error_category: Error category
            alert_level: Alert level
        
        Returns:
            bool: True if alert should be sent
        """
        # Always send critical alerts
        if alert_level in ["critical", "high"]:
            return True
        
        # Send medium alerts only in production
        if alert_level == "medium" and self.environment == "production":
            return True
        
        # Send low alerts only for specific categories in production
        if (alert_level == "low" and self.environment == "production" and 
            error_category in ["authentication", "database", "system"]):
            return True
        
        return False
    
    def _prepare_alert_data(self, message: str, error_category: str,
                           alert_level: str, details: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Prepare alert data for notification.
        
        Args:
            message: Alert message
            error_category: Error category
            alert_level: Alert level
            details: Additional alert details
        
        Returns:
            Dict: Alert data
        """
        alert_data = {
            "service": self.service_name,
            "environment": self.environment,
            "message": message,
            "error_category": error_category,
            "alert_level": alert_level,
            "details": details or {}
        }
        
        return alert_data
    
    async def _send_slack_notification(self, alert_data: Dict[str, Any]) -> bool:
        """
        Send notification to Slack.
        
        Args:
            alert_data: Alert data
        
        Returns:
            bool: True if notification was sent successfully
        """
        if not settings.ALERT_SLACK_WEBHOOK:
            return False
        
        try:
            # Format Slack message
            color = self._get_alert_color(alert_data["alert_level"])
            
            slack_message = {
                "attachments": [
                    {
                        "color": color,
                        "title": f"[{alert_data['environment'].upper()}] {alert_data['error_category'].upper()} Alert",
                        "text": alert_data["message"],
                        "fields": [
                            {
                                "title": "Service",
                                "value": alert_data["service"],
                                "short": True
                            },
                            {
                                "title": "Category",
                                "value": alert_data["error_category"],
                                "short": True
                            },
                            {
                                "title": "Level",
                                "value": alert_data["alert_level"],
                                "short": True
                            }
                        ],
                        "footer": "Reddit Content Platform Monitoring"
                    }
                ]
            }
            
            # Add details if available
            if alert_data["details"]:
                detail_fields = []
                for key, value in alert_data["details"].items():
                    if key not in ["traceback", "stack_trace"]:
                        detail_fields.append({
                            "title": key,
                            "value": str(value)[:100],
                            "short": True
                        })
                
                if detail_fields:
                    slack_message["attachments"][0]["fields"].extend(detail_fields)
            
            # Send to Slack
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    settings.ALERT_SLACK_WEBHOOK,
                    json=slack_message,
                    timeout=5.0
                )
                
                if response.status_code == 200:
                    logger.info(
                        "Slack alert notification sent",
                        operation="alert_notification",
                        channel="slack",
                        status="success"
                    )
                    return True
                else:
                    logger.warning(
                        f"Failed to send Slack alert: {response.status_code}",
                        operation="alert_notification",
                        channel="slack",
                        status="failed",
                        status_code=response.status_code,
                        response=response.text[:200]
                    )
                    return False
                    
        except Exception as e:
            logger.error(
                f"Error sending Slack alert: {str(e)}",
                operation="alert_notification",
                channel="slack",
                status="error",
                error=str(e),
                exc_info=True
            )
            return False
    
    async def _send_email_notification(self, alert_data: Dict[str, Any]) -> bool:
        """
        Send notification via email.
        
        Args:
            alert_data: Alert data
        
        Returns:
            bool: True if notification was sent successfully
        """
        if not (settings.ALERT_EMAIL_ENABLED and settings.SMTP_HOST and settings.ADMIN_EMAIL):
            return False
        
        try:
            # Create email message
            msg = MIMEMultipart()
            msg["Subject"] = f"[{alert_data['environment'].upper()}] {alert_data['error_category'].upper()} Alert: {alert_data['message'][:50]}"
            msg["From"] = settings.SMTP_USER or "alerts@redditcontentplatform.com"
            msg["To"] = settings.ADMIN_EMAIL
            
            # Format email body
            body = f"""
            <html>
            <body>
                <h2>{alert_data['message']}</h2>
                <p><strong>Service:</strong> {alert_data['service']}</p>
                <p><strong>Environment:</strong> {alert_data['environment']}</p>
                <p><strong>Category:</strong> {alert_data['error_category']}</p>
                <p><strong>Level:</strong> {alert_data['alert_level']}</p>
                
                <h3>Details:</h3>
                <ul>
            """
            
            # Add details if available
            if alert_data["details"]:
                for key, value in alert_data["details"].items():
                    if key not in ["traceback", "stack_trace"]:
                        body += f"<li><strong>{key}:</strong> {str(value)[:200]}</li>\n"
            
            body += """
                </ul>
            </body>
            </html>
            """
            
            msg.attach(MIMEText(body, "html"))
            
            # Send email in a separate thread to avoid blocking
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None, 
                self._send_email_sync, 
                msg, 
                settings.SMTP_HOST, 
                settings.SMTP_PORT, 
                settings.SMTP_USER, 
                settings.SMTP_PASSWORD
            )
            
            if result:
                logger.info(
                    "Email alert notification sent",
                    operation="alert_notification",
                    channel="email",
                    status="success",
                    recipient=settings.ADMIN_EMAIL
                )
            else:
                logger.warning(
                    "Failed to send email alert",
                    operation="alert_notification",
                    channel="email",
                    status="failed"
                )
            
            return result
            
        except Exception as e:
            logger.error(
                f"Error sending email alert: {str(e)}",
                operation="alert_notification",
                channel="email",
                status="error",
                error=str(e),
                exc_info=True
            )
            return False
    
    def _send_email_sync(self, msg, host, port, user, password) -> bool:
        """
        Send email synchronously (to be run in executor).
        
        Args:
            msg: Email message
            host: SMTP host
            port: SMTP port
            user: SMTP username
            password: SMTP password
        
        Returns:
            bool: True if email was sent successfully
        """
        try:
            server = smtplib.SMTP(host, port)
            server.starttls()
            
            if user and password:
                server.login(user, password)
            
            server.send_message(msg)
            server.quit()
            return True
        except Exception:
            return False
    
    async def _send_webhook_notification(self, alert_data: Dict[str, Any]) -> bool:
        """
        Send notification to webhook.
        
        Args:
            alert_data: Alert data
        
        Returns:
            bool: True if notification was sent successfully
        """
        if not settings.ALERT_WEBHOOK_URL:
            return False
        
        try:
            # Send to webhook
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    settings.ALERT_WEBHOOK_URL,
                    json=alert_data,
                    timeout=5.0
                )
                
                if response.status_code in [200, 201, 202]:
                    logger.info(
                        "Webhook alert notification sent",
                        operation="alert_notification",
                        channel="webhook",
                        status="success"
                    )
                    return True
                else:
                    logger.warning(
                        f"Failed to send webhook alert: {response.status_code}",
                        operation="alert_notification",
                        channel="webhook",
                        status="failed",
                        status_code=response.status_code,
                        response=response.text[:200]
                    )
                    return False
                    
        except Exception as e:
            logger.error(
                f"Error sending webhook alert: {str(e)}",
                operation="alert_notification",
                channel="webhook",
                status="error",
                error=str(e),
                exc_info=True
            )
            return False
    
    def _get_alert_color(self, alert_level: str) -> str:
        """
        Get color for alert level.
        
        Args:
            alert_level: Alert level
        
        Returns:
            str: Color hex code
        """
        colors = {
            "critical": "#FF0000",  # Red
            "high": "#FFA500",      # Orange
            "medium": "#FFFF00",    # Yellow
            "low": "#00FF00"        # Green
        }
        
        return colors.get(alert_level.lower(), "#808080")  # Default to gray


# Global alert notifier instance
alert_notifier = AlertNotifier()


async def send_alert(message: str, error_category: str = ErrorCategory.UNKNOWN.value,
                    alert_level: str = "medium", details: Dict[str, Any] = None) -> bool:
    """
    Send alert notification.
    
    Args:
        message: Alert message
        error_category: Error category
        alert_level: Alert level
        details: Additional alert details
    
    Returns:
        bool: True if notification was sent successfully
    """
    return await alert_notifier.notify(message, error_category, alert_level, details)