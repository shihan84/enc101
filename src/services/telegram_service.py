"""
Telegram Notification Service
Sends alerts and notifications via Telegram Bot API
"""

import requests
import json
from typing import Optional, Dict, List
from datetime import datetime
from ..core.logger import get_logger
from ..utils.exceptions import SCTE35Error


class TelegramService:
    """Service for sending Telegram notifications"""
    
    BASE_URL = "https://api.telegram.org/bot"
    
    def __init__(self, bot_token: str = "", chat_id: str = ""):
        self.logger = get_logger("TelegramService")
        self.bot_token = bot_token
        self.chat_id = chat_id
        self.enabled = bool(bot_token and chat_id)
        
        if self.enabled:
            self.logger.info("Telegram service initialized")
        else:
            self.logger.info("Telegram service initialized (disabled - no token/chat_id)")
    
    def configure(self, bot_token: str, chat_id: str):
        """Configure Telegram service"""
        self.bot_token = bot_token
        self.chat_id = chat_id
        self.enabled = bool(bot_token and chat_id)
        
        if self.enabled:
            self.logger.info("Telegram service configured")
        else:
            self.logger.warning("Telegram service disabled - missing token or chat_id")
    
    def test_connection(self) -> bool:
        """Test Telegram bot connection"""
        if not self.enabled:
            return False
        
        try:
            url = f"{self.BASE_URL}{self.bot_token}/getMe"
            response = requests.get(url, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('ok'):
                    bot_info = data.get('result', {})
                    self.logger.info(f"Telegram bot connected: @{bot_info.get('username', 'Unknown')}")
                    return True
            
            self.logger.error(f"Telegram connection failed: {response.text}")
            return False
            
        except Exception as e:
            self.logger.error(f"Telegram connection test error: {e}")
            return False
    
    def send_message(
        self,
        text: str,
        parse_mode: str = "HTML",
        disable_notification: bool = False
    ) -> bool:
        """
        Send a text message to Telegram
        
        Args:
            text: Message text
            parse_mode: HTML or Markdown
            disable_notification: Silent notification
        
        Returns:
            True if sent successfully
        """
        if not self.enabled:
            return False
        
        try:
            url = f"{self.BASE_URL}{self.bot_token}/sendMessage"
            
            payload = {
                'chat_id': self.chat_id,
                'text': text,
                'parse_mode': parse_mode,
                'disable_notification': disable_notification
            }
            
            response = requests.post(url, json=payload, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('ok'):
                    self.logger.debug("Telegram message sent successfully")
                    return True
                else:
                    self.logger.error(f"Telegram API error: {data.get('description', 'Unknown')}")
                    return False
            else:
                self.logger.error(f"Telegram HTTP error: {response.status_code} - {response.text}")
                return False
                
        except requests.exceptions.Timeout:
            self.logger.error("Telegram request timeout")
            return False
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Telegram request error: {e}")
            return False
        except Exception as e:
            self.logger.error(f"Telegram send error: {e}", exc_info=True)
            return False
    
    def send_scte35_alert(
        self,
        event_id: Optional[int] = None,
        cue_type: Optional[str] = None,
        pts_time: Optional[int] = None,
        break_duration: Optional[int] = None,
        out_of_network: Optional[bool] = None,
        source: Optional[str] = None
    ) -> bool:
        """
        Send SCTE-35 event alert to Telegram
        
        Args:
            event_id: SCTE-35 event ID
            cue_type: Event type (CUE-OUT, CUE-IN, etc.)
            pts_time: Presentation Time Stamp
            break_duration: Break duration in 90kHz units
            out_of_network: Network status
            source: Stream source
        
        Returns:
            True if sent successfully
        """
        if not self.enabled:
            return False
        
        # Build alert message
        emoji = "🎬"
        if cue_type:
            if "CUE-OUT" in cue_type.upper():
                emoji = "📺"
            elif "CUE-IN" in cue_type.upper():
                emoji = "▶️"
            elif "PREROLL" in cue_type.upper():
                emoji = "🎯"
        
        message = f"{emoji} <b>SCTE-35 Event Detected</b>\n\n"
        
        if cue_type:
            message += f"<b>Type:</b> {cue_type}\n"
        
        if event_id:
            message += f"<b>Event ID:</b> {event_id}\n"
        
        if pts_time:
            pts_seconds = pts_time / 90000  # Convert to seconds
            message += f"<b>PTS:</b> {pts_time} ({pts_seconds:.2f}s)\n"
        
        if break_duration:
            duration_seconds = break_duration / 90000  # Convert to seconds
            message += f"<b>Duration:</b> {duration_seconds:.1f}s\n"
        
        if out_of_network is not None:
            network_status = "Out of Network" if out_of_network else "In Network"
            status_emoji = "🔴" if out_of_network else "🟢"
            message += f"<b>Status:</b> {status_emoji} {network_status}\n"
        
        if source:
            message += f"<b>Source:</b> {source}\n"
        
        message += f"\n<i>Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</i>"
        
        return self.send_message(message, disable_notification=False)
    
    def send_error_alert(
        self,
        error_type: str,
        error_message: str,
        source: Optional[str] = None
    ) -> bool:
        """
        Send error alert to Telegram
        
        Args:
            error_type: Type of error
            error_message: Error message
            source: Source of error
        
        Returns:
            True if sent successfully
        """
        if not self.enabled:
            return False
        
        message = f"⚠️ <b>Error Alert</b>\n\n"
        message += f"<b>Type:</b> {error_type}\n"
        message += f"<b>Message:</b> {error_message}\n"
        
        if source:
            message += f"<b>Source:</b> {source}\n"
        
        message += f"\n<i>Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</i>"
        
        return self.send_message(message, disable_notification=False)
    
    def send_status_update(
        self,
        status: str,
        details: Optional[str] = None
    ) -> bool:
        """
        Send status update to Telegram
        
        Args:
            status: Status message
            details: Additional details
        
        Returns:
            True if sent successfully
        """
        if not self.enabled:
            return False
        
        message = f"ℹ️ <b>Status Update</b>\n\n"
        message += f"<b>Status:</b> {status}\n"
        
        if details:
            message += f"<b>Details:</b> {details}\n"
        
        message += f"\n<i>Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</i>"
        
        return self.send_message(message, disable_notification=True)
    
    def send_monitoring_started(self, source: str, pid: int) -> bool:
        """Send notification when monitoring starts"""
        message = f"🔍 <b>SCTE-35 Monitoring Started</b>\n\n"
        message += f"<b>Source:</b> {source}\n"
        message += f"<b>SCTE-35 PID:</b> {pid}\n"
        message += f"\n<i>Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</i>"
        return self.send_message(message)
    
    def send_monitoring_stopped(self) -> bool:
        """Send notification when monitoring stops"""
        message = f"⏹️ <b>SCTE-35 Monitoring Stopped</b>\n\n"
        message += f"<i>Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</i>"
        return self.send_message(message, disable_notification=True)
    
    def send_crash_alert(
        self,
        exception_type: str,
        exception_message: str,
        traceback_text: str,
        thread: str = "Main"
    ) -> bool:
        """
        Send crash alert to Telegram
        
        Args:
            exception_type: Type of exception
            exception_message: Exception message
            traceback_text: Traceback text
            thread: Thread where crash occurred
        
        Returns:
            True if sent successfully
        """
        if not self.enabled:
            return False
        
        message = f"🚨 <b>Application Crash</b>\n\n"
        message += f"<b>Exception:</b> {exception_type}\n"
        message += f"<b>Message:</b> {exception_message}\n"
        message += f"<b>Thread:</b> {thread}\n"
        message += f"<b>Time:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        
        # Truncate traceback if too long
        if len(traceback_text) > 1500:
            traceback_text = traceback_text[:1500] + "\n... (truncated)"
        
        message += f"<b>Traceback:</b>\n<code>{traceback_text}</code>"
        
        return self.send_message(message, disable_notification=False)
    
    def send_statistics(
        self,
        total_events: int,
        events_per_minute: int,
        events_by_type: Dict[str, int]
    ) -> bool:
        """
        Send monitoring statistics
        
        Args:
            total_events: Total events detected
            events_per_minute: Events per minute rate
            events_by_type: Events breakdown by type
        
        Returns:
            True if sent successfully
        """
        if not self.enabled:
            return False
        
        message = f"📊 <b>SCTE-35 Statistics</b>\n\n"
        message += f"<b>Total Events:</b> {total_events}\n"
        message += f"<b>Events/Min:</b> {events_per_minute}\n\n"
        
        if events_by_type:
            message += "<b>By Type:</b>\n"
            for event_type, count in events_by_type.items():
                message += f"  • {event_type}: {count}\n"
        
        message += f"\n<i>Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</i>"
        
        return self.send_message(message, disable_notification=True)

