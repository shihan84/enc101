#!/usr/bin/env python3
"""
IBE-210 v2.2.3 Enterprise - Main Entry Point
Enterprise-grade broadcast encoder with bundled TSDuck support
"""

import sys
import os
from pathlib import Path

# Add src to path - handle both development and PyInstaller bundled modes
if getattr(sys, 'frozen', False):
    # PyInstaller bundled mode - src is in the bundle
    base_path = Path(sys._MEIPASS)
    # Add both base path and src subdirectory to path
    sys.path.insert(0, str(base_path))
    src_path = base_path / "src"
    if src_path.exists():
        sys.path.insert(0, str(src_path))
    # Also add parent directory in case src is at root level
    sys.path.insert(0, str(base_path.parent))
else:
    # Development mode
    project_root = Path(__file__).parent
    sys.path.insert(0, str(project_root))
    sys.path.insert(0, str(project_root / "src"))

# Set UTF-8 encoding for Windows
os.system('chcp 65001 >nul 2>&1')

from src.core import Application, ConfigManager, get_logger
# Direct imports to avoid PyInstaller issues with __init__.py
from src.services.tsduck_service import TSDuckService
from src.services.stream_service import StreamService
from src.services.scte35_service import SCTE35Service
from src.services.scte35_monitor_service import SCTE35MonitorService
from src.services.dynamic_marker_service import DynamicMarkerService
from src.services.telegram_service import TelegramService
from src.services.monitoring_service import MonitoringService
from src.services.profile_service import ProfileService
from src.services.stream_analyzer_service import StreamAnalyzerService
from src.services.bitrate_monitor_service import BitrateMonitorService
from src.services.epg_service import EPGService
from src.database import Database, SessionRepository
from src.api import APIServer, setup_routes
from src.ui.main_window import MainWindow
from src.utils.crash_handler import CrashHandler


def main():
    """Main application entry point"""
    # Initialize crash handler early (before services) to catch startup crashes
    telegram_service = None
    crash_handler = None
    
    try:
        # Initialize application framework
        app_framework = Application()
        qt_app = app_framework.initialize_qt()
        
        # Performance optimizations for Qt (PyQt6 compatible)
        # Note: High DPI support is enabled by default in PyQt6
        # Window context help button is disabled via stylesheet
        
        logger = get_logger("Main")
        logger.info("=" * 60)
        logger.info("IBE-210 v2.2.4 Enterprise Starting...")
        logger.info("=" * 60)
        
        # Initialize services
        config = app_framework.config
        
        # TSDuck service
        tsduck_service = TSDuckService(config.tsduck_path or None)
        if not tsduck_service.verify_installation():
            logger.warning("TSDuck installation not verified. Some features may not work.")
        
        # Database
        database = Database()
        session_repo = SessionRepository(database)
        app_framework.register_service("database", database)
        app_framework.register_service("session_repo", session_repo)
        
        # Register services
        app_framework.register_service("tsduck", tsduck_service)
        # Telegram Service (initialize early for crash alerts and stream notifications)
        telegram_service = TelegramService(
            bot_token=config.telegram_bot_token if config.telegram_enabled else "",
            chat_id=config.telegram_chat_id if config.telegram_enabled else ""
        )
        app_framework.register_service("telegram", telegram_service)
        
        # SCTE-35 Service
        scte35_service = SCTE35Service()
        app_framework.register_service("scte35", scte35_service)
        
        # Dynamic Marker Service (for 24/7 streaming with incrementing event IDs)
        dynamic_marker_service = DynamicMarkerService(scte35_service)
        app_framework.register_service("dynamic_marker", dynamic_marker_service)
        
        # Stream Service (with dynamic marker support)
        stream_service = StreamService(
            tsduck_service=tsduck_service,
            telegram_service=telegram_service,
            dynamic_marker_service=dynamic_marker_service
        )
        app_framework.register_service("stream", stream_service)
        
        # Crash Handler (with Telegram integration) - setup early
        crash_handler = CrashHandler(telegram_service)
        app_framework.set_crash_handler(crash_handler)
        
        # SCTE-35 Monitor Service (requires TSDuck service)
        scte35_monitor_service = SCTE35MonitorService(tsduck_service, telegram_service)
        app_framework.register_service("scte35_monitor", scte35_monitor_service)
        
        app_framework.register_service("monitoring", MonitoringService())
        app_framework.register_service("profile", ProfileService())
        
        # Stream Analysis Services (with Telegram integration)
        stream_analyzer = StreamAnalyzerService(tsduck_service, telegram_service)
        app_framework.register_service("stream_analyzer", stream_analyzer)
        
        bitrate_monitor = BitrateMonitorService(tsduck_service, telegram_service)
        app_framework.register_service("bitrate_monitor", bitrate_monitor)
        
        # EPG Service
        epg_service = EPGService()
        app_framework.register_service("epg", epg_service)
        
        # Backup Manager (for automated backups)
        from src.utils.backup_manager import BackupManager
        backup_manager = BackupManager(max_backups=10)
        app_framework.register_service("backup", backup_manager)
        logger.info("Backup manager initialized")
        
        # API Server (if enabled)
        if config.api_enabled:
            api_server = APIServer(config.api_host, config.api_port)
            setup_routes(api_server, app_framework)
            api_server.start()
            app_framework.register_service("api", api_server)
            logger.info(f"API server started on http://{config.api_host}:{config.api_port}")
        
        logger.info("Services initialized")
        
        # Create and show main window
        main_window = MainWindow(app_framework)
        main_window.show()
        
        logger.info("Application ready")
        
        # Run application
        exit_code = app_framework.run()
        
        logger.info("Application shutting down...")
        return exit_code
        
    except KeyboardInterrupt:
        # User-initiated shutdown
        if crash_handler:
            crash_handler.report_graceful_shutdown()
        return 0
    except Exception as e:
        # Startup crash - try to send alert
        error_msg = f"Failed to start application: {e}"
        print(f"[FATAL ERROR] {error_msg}")
        import traceback
        traceback_text = ''.join(traceback.format_exception(type(e), e, e.__traceback__))
        traceback.print_exc()
        
        # Try to send crash alert if Telegram is available
        if telegram_service and telegram_service.enabled:
            try:
                telegram_service.send_crash_alert(
                    exception_type=type(e).__name__,
                    exception_message=str(e),
                    traceback_text=traceback_text,
                    thread="Main"
                )
            except Exception:
                pass  # Fail silently if alert fails
        
        return 1


if __name__ == "__main__":
    sys.exit(main())

