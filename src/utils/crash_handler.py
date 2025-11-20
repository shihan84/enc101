"""
Crash Detection and Alert Handler
Handles application crashes and sends Telegram alerts
"""

import sys
import traceback
import threading
import atexit
from datetime import datetime
from pathlib import Path
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from ..services.telegram_service import TelegramService


class CrashHandler:
    """Handles application crashes and sends alerts"""
    
    def __init__(self, telegram_service: Optional['TelegramService'] = None):
        self.telegram_service = telegram_service
        self.crash_log_path = Path("logs/crashes")
        self.crash_log_path.mkdir(parents=True, exist_ok=True)
        self._crash_reported = False
        
        # Setup handlers
        self._setup_exception_handlers()
        self._setup_atexit_handler()
    
    def set_telegram_service(self, telegram_service: 'TelegramService'):
        """Set Telegram service for crash alerts"""
        self.telegram_service = telegram_service
    
    def _setup_exception_handlers(self):
        """Setup global exception handlers"""
        # Handle uncaught exceptions
        sys.excepthook = self._handle_exception
        
        # Handle thread exceptions (if available)
        if hasattr(threading, 'excepthook'):
            threading.excepthook = self._handle_thread_exception
    
    def _setup_atexit_handler(self):
        """Setup atexit handler for graceful shutdown detection"""
        atexit.register(self._handle_exit)
    
    def _handle_exception(self, exc_type, exc_value, exc_traceback):
        """Handle uncaught exceptions"""
        if exc_type == KeyboardInterrupt:
            # User-initiated shutdown, don't treat as crash
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return
        
        # Log crash
        crash_info = self._log_crash(exc_type, exc_value, exc_traceback)
        
        # Send Telegram alert
        if not self._crash_reported:
            self._send_crash_alert(crash_info)
            self._crash_reported = True
        
        # Call original exception handler
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
    
    def _handle_thread_exception(self, args):
        """Handle exceptions in threads"""
        exc_type, exc_value, exc_traceback, thread = args
        
        if exc_type == KeyboardInterrupt:
            return
        
        # Log crash
        crash_info = self._log_crash(exc_type, exc_value, exc_traceback, thread=thread)
        
        # Send Telegram alert
        if not self._crash_reported:
            self._send_crash_alert(crash_info)
            self._crash_reported = True
    
    def _log_crash(self, exc_type, exc_value, exc_traceback, thread=None) -> dict:
        """Log crash information to file"""
        timestamp = datetime.now()
        crash_file = self.crash_log_path / f"crash_{timestamp.strftime('%Y%m%d_%H%M%S')}.log"
        
        crash_info = {
            'timestamp': timestamp.isoformat(),
            'exception_type': exc_type.__name__,
            'exception_message': str(exc_value),
            'thread': thread.name if thread else 'Main',
            'traceback': ''.join(traceback.format_exception(exc_type, exc_value, exc_traceback))
        }
        
        try:
            with open(crash_file, 'w', encoding='utf-8') as f:
                f.write("=" * 80 + "\n")
                f.write(f"CRASH REPORT - {timestamp.strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write("=" * 80 + "\n\n")
                f.write(f"Exception Type: {exc_type.__name__}\n")
                f.write(f"Exception Message: {exc_value}\n")
                f.write(f"Thread: {crash_info['thread']}\n")
                f.write(f"\nTraceback:\n")
                f.write(crash_info['traceback'])
                f.write("\n" + "=" * 80 + "\n")
        except Exception as e:
            print(f"[ERROR] Failed to write crash log: {e}")
        
        return crash_info
    
    def _send_crash_alert(self, crash_info: dict):
        """Send crash alert via Telegram"""
        if not self.telegram_service or not self.telegram_service.enabled:
            return
        
        try:
            # Build crash message
            message = f"🚨 <b>Application Crash Detected</b>\n\n"
            message += f"<b>Exception:</b> {crash_info['exception_type']}\n"
            message += f"<b>Message:</b> {crash_info['exception_message']}\n"
            message += f"<b>Thread:</b> {crash_info['thread']}\n"
            message += f"<b>Time:</b> {crash_info['timestamp']}\n\n"
            
            # Add traceback (truncated if too long)
            traceback_text = crash_info['traceback']
            if len(traceback_text) > 1000:
                traceback_text = traceback_text[:1000] + "\n... (truncated)"
            
            message += f"<b>Traceback:</b>\n<code>{traceback_text}</code>"
            
            # Send in a separate thread to avoid blocking
            def send_alert():
                try:
                    self.telegram_service.send_message(message, disable_notification=False)
                except Exception:
                    pass  # Fail silently if Telegram fails
            
            thread = threading.Thread(target=send_alert, daemon=True)
            thread.start()
            
        except Exception:
            pass  # Fail silently if alert sending fails
    
    def _handle_exit(self):
        """Handle application exit"""
        # Check if this is an unexpected exit
        # (atexit is called for both normal and abnormal exits)
        # We can't easily distinguish, so we'll send a closure notification
        # if Telegram is enabled and we haven't already reported a crash
        if self.telegram_service and self.telegram_service.enabled and not self._crash_reported:
            try:
                # Send closure notification
                message = f"⚠️ <b>Application Closed</b>\n\n"
                message += f"<b>Time:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                message += f"<b>Status:</b> Application terminated"
                
                def send_alert():
                    try:
                        self.telegram_service.send_message(message, disable_notification=True)
                    except Exception:
                        pass
                
                thread = threading.Thread(target=send_alert, daemon=True)
                thread.start()
                thread.join(timeout=2)  # Wait up to 2 seconds
            except Exception:
                pass
    
    def report_graceful_shutdown(self):
        """Report graceful shutdown (prevents closure alert)"""
        self._crash_reported = True
        if self.telegram_service and self.telegram_service.enabled:
            try:
                message = f"✅ <b>Application Shutdown</b>\n\n"
                message += f"<b>Time:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                message += f"<b>Status:</b> Graceful shutdown"
                
                def send_alert():
                    try:
                        self.telegram_service.send_message(message, disable_notification=True)
                    except Exception:
                        pass
                
                thread = threading.Thread(target=send_alert, daemon=True)
                thread.start()
            except Exception:
                pass

