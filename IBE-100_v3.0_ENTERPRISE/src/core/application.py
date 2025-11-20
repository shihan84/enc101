"""
Main Application Framework
Manages application lifecycle, dependency injection, and service coordination
"""

import sys
import signal
from pathlib import Path
from typing import Optional
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QObject, pyqtSignal

from .config import ConfigManager
from .logger import get_logger
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..utils.crash_handler import CrashHandler


class Application(QObject):
    """Main application framework"""
    
    # Signals
    initialized = pyqtSignal()
    shutdown_requested = pyqtSignal()
    
    def __init__(self, config_path: Path = None):
        super().__init__()
        
        # Initialize core components
        self.config_manager = ConfigManager(config_path)
        self.config = self.config_manager.get_config()
        
        # Setup logging
        log_dir = Path(self.config.log_dir)
        self.logger = get_logger("IBE100", log_dir)
        
        self.logger.info(f"Initializing {self.config.app_name} v{self.config.app_version}")
        
        # Application state
        self._qt_app: Optional[QApplication] = None
        self._services = {}
        self._running = False
        self._crash_handler: Optional['CrashHandler'] = None
        
        # Setup signal handlers
        self._setup_signal_handlers()
    
    def _setup_signal_handlers(self):
        """Setup signal handlers for graceful shutdown"""
        if sys.platform != 'win32':
            signal.signal(signal.SIGINT, self._signal_handler)
            signal.signal(signal.SIGTERM, self._signal_handler)
    
    def set_crash_handler(self, crash_handler: 'CrashHandler'):
        """Set crash handler for application"""
        self._crash_handler = crash_handler
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        self.logger.info(f"Received signal {signum}, shutting down...")
        # Report graceful shutdown
        if self._crash_handler:
            self._crash_handler.report_graceful_shutdown()
        self.shutdown()
    
    def register_service(self, name: str, service: object):
        """Register a service"""
        self._services[name] = service
        self.logger.debug(f"Registered service: {name}")
    
    def get_service(self, name: str) -> Optional[object]:
        """Get a registered service"""
        return self._services.get(name)
    
    def initialize_qt(self):
        """Initialize Qt application"""
        from PyQt6.QtGui import QIcon
        from pathlib import Path
        
        if not self._qt_app:
            self._qt_app = QApplication(sys.argv)
            self._qt_app.setApplicationName(self.config.app_name)
            self._qt_app.setApplicationVersion(self.config.app_version)
            
            # Set application icon for taskbar (Windows)
            # Handle both development and PyInstaller bundled modes
            icon_path = None
            if getattr(sys, 'frozen', False):
                # PyInstaller bundled mode
                base_path = Path(sys._MEIPASS)
                icon_path = base_path / "logo.ico"
            else:
                # Development mode
                icon_path = Path("logo.ico")
            
            if icon_path and icon_path.exists():
                self._qt_app.setWindowIcon(QIcon(str(icon_path)))
                self.logger.info(f"Application icon set: {icon_path}")
            else:
                self.logger.warning(f"Icon not found: {icon_path}")
            
            self.logger.info("Qt application initialized")
        return self._qt_app
    
    def run(self):
        """Run the application"""
        if self._running:
            self.logger.warning("Application is already running")
            return
        
        self._running = True
        self.logger.info("Starting application...")
        
        # Initialize Qt if not already done
        if not self._qt_app:
            self.initialize_qt()
        
        # Emit initialized signal
        self.initialized.emit()
        
        # Run Qt event loop
        try:
            exit_code = self._qt_app.exec()
            self.logger.info(f"Application exited with code {exit_code}")
            # Report graceful shutdown
            if self._crash_handler:
                self._crash_handler.report_graceful_shutdown()
            return exit_code
        except Exception as e:
            self.logger.error(f"Application error: {e}", exc_info=True)
            # Crash handler will send alert automatically
            return 1
        finally:
            self._running = False
    
    def shutdown(self):
        """Shutdown the application"""
        if not self._running:
            return
        
        self.logger.info("Shutting down application...")
        self.shutdown_requested.emit()
        
        # Report graceful shutdown
        if self._crash_handler:
            self._crash_handler.report_graceful_shutdown()
        
        # Shutdown services
        for name, service in self._services.items():
            try:
                if hasattr(service, 'shutdown'):
                    service.shutdown()
                self.logger.debug(f"Shutdown service: {name}")
            except Exception as e:
                self.logger.error(f"Error shutting down service {name}: {e}")
        
        # Quit Qt application
        if self._qt_app:
            self._qt_app.quit()
        
        self._running = False
        self.logger.info("Application shutdown complete")
    
    @property
    def qt_app(self) -> Optional[QApplication]:
        """Get Qt application instance"""
        return self._qt_app
    
    @property
    def is_running(self) -> bool:
        """Check if application is running"""
        return self._running

