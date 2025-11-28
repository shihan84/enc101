"""
Enhanced Monitoring Widget
Real-time monitoring with multiple tabs
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QTabWidget, QTextEdit, QLabel,
    QLineEdit, QPushButton, QSpinBox, QHBoxLayout, QSplitter,
    QGroupBox, QScrollArea
)
from PyQt6.QtCore import QTimer, Qt, pyqtSignal
from PyQt6.QtGui import QFont
from datetime import datetime
import psutil
from .scte35_monitor_widget import SCTE35MonitorWidget


class MonitoringWidget(QWidget):
    """Enhanced monitoring widget with multiple views"""
    
    # Signal for thread-safe console updates
    _console_message = pyqtSignal(str)
    
    def __init__(self, monitoring_service, stream_service=None, 
                 scte35_monitor_service=None, telegram_service=None,
                 stream_analyzer_service=None, bitrate_monitor_service=None,
                 profile_service=None):
        super().__init__()
        self.monitoring_service = monitoring_service
        self.stream_service = stream_service
        self.scte35_monitor_service = scte35_monitor_service
        self.telegram_service = telegram_service
        self.stream_analyzer_service = stream_analyzer_service
        self.bitrate_monitor_service = bitrate_monitor_service
        self.profile_service = profile_service  # For profile-specific settings
        
        # Flag to track if UI is ready
        self._ui_ready = False
        
        # Cache for metrics to avoid unnecessary updates
        self._cached_metrics_text = ""
        self._cached_status_text = ""
        
        # Connect signal for thread-safe updates
        self._console_message.connect(self._safe_append_console)
        
        self.setup_ui()
        self._ui_ready = True  # Mark UI as ready after setup
        self.setup_timers()
    
    def _safe_append_console(self, message: str):
        """Thread-safe method to append to console (called from signal)"""
        try:
            if not hasattr(self, 'console') or not self.console:
                return
            
            # Performance optimization: Limit console buffer size
            max_lines = 1000
            if self.console.document().blockCount() > max_lines:
                # Remove oldest lines
                cursor = self.console.textCursor()
                cursor.movePosition(cursor.MoveOperation.Start)
                for _ in range(100):  # Remove 100 lines at a time
                    cursor.movePosition(cursor.MoveOperation.Down, cursor.MoveMode.KeepAnchor)
                cursor.removeSelectedText()
            
            self.console.append(message)
            
            # Auto-scroll to bottom (only if user is at bottom)
            scrollbar = self.console.verticalScrollBar()
            if scrollbar and scrollbar.value() >= scrollbar.maximum() - 50:  # Near bottom
                scrollbar.setValue(scrollbar.maximum())
        except Exception:
            pass  # Fail silently
    
    def setup_ui(self):
        """Setup user interface - redesigned to reduce congestion"""
        layout = QVBoxLayout(self)
        layout.setSpacing(5)
        layout.setContentsMargins(5, 5, 5, 5)
        
        # Use splitter for better organization
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Left Panel - Basic Monitoring (Compact)
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(0, 0, 0, 0)
        
        # Basic Monitoring Tabs
        basic_tabs = QTabWidget()
        basic_tabs.setStyleSheet("""
            QTabWidget::pane { border: 1px solid #444; background-color: #2a2a2a; }
            QTabBar::tab { background-color: #3a3a3a; color: white; padding: 6px 12px; font-size: 10px; }
            QTabBar::tab:selected { background-color: #2196F3; }
        """)
        
        # Console
        self.console = QTextEdit()
        self.console.setReadOnly(True)
        self.console.setFont(QFont("Courier", 9))
        self.console.setStyleSheet("background-color: #1e1e1e; color: #00ff00; padding: 8px;")
        basic_tabs.addTab(self.console, "📺 Console")
        
        # System Metrics with Scroll
        metrics_scroll = QScrollArea()
        metrics_scroll.setWidgetResizable(True)
        metrics_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        metrics_scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: #1e1e1e;
            }
        """)
        self.metrics_label = QLabel()
        self.metrics_label.setFont(QFont("Courier", 9))
        self.metrics_label.setStyleSheet("background-color: #1e1e1e; color: #ffffff; padding: 8px;")
        self.metrics_label.setWordWrap(True)
        metrics_scroll.setWidget(self.metrics_label)
        basic_tabs.addTab(metrics_scroll, "⚡ Metrics")
        
        # Stream Status
        self.stream_status = QTextEdit()
        self.stream_status.setReadOnly(True)
        self.stream_status.setFont(QFont("Courier", 9))
        self.stream_status.setStyleSheet("background-color: #1e1e1e; color: #4CAF50; padding: 8px;")
        basic_tabs.addTab(self.stream_status, "📡 Status")
        
        left_layout.addWidget(basic_tabs)
        splitter.addWidget(left_panel)
        splitter.setStretchFactor(0, 0)
        splitter.setSizes([400, 900])
        
        # Right Panel - Advanced Monitoring
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(0, 0, 0, 0)
        
        # Advanced Monitoring Tabs
        advanced_tabs = QTabWidget()
        advanced_tabs.setStyleSheet("""
            QTabWidget::pane { border: 1px solid #444; background-color: #2a2a2a; }
            QTabBar::tab { background-color: #3a3a3a; color: white; padding: 8px 16px; }
            QTabBar::tab:selected { background-color: #2196F3; }
        """)
        
        # SCTE-35 Monitor
        if self.scte35_monitor_service:
            telegram_service = getattr(self, 'telegram_service', None)
            self.scte35_monitor_widget = SCTE35MonitorWidget(
                self.scte35_monitor_service,
                telegram_service,
                self.profile_service  # Pass profile service for saving settings
            )
            advanced_tabs.addTab(self.scte35_monitor_widget, "🎬 SCTE-35")
        else:
            self.scte35_monitor_widget = None
        
        # Stream Quality and Bitrate Monitor tabs removed - not needed for now
        
        right_layout.addWidget(advanced_tabs)
        splitter.addWidget(right_panel)
        splitter.setStretchFactor(1, 1)
        
        layout.addWidget(splitter)
    
    def setup_timers(self):
        """Setup update timers with optimized intervals"""
        # Metrics timer - update every 1.5 seconds (smoother)
        self.metrics_timer = QTimer()
        self.metrics_timer.setSingleShot(False)
        self.metrics_timer.timeout.connect(self._update_metrics)
        # Store delay timer to prevent garbage collection
        self._metrics_delay_timer = QTimer()
        self._metrics_delay_timer.setSingleShot(True)
        self._metrics_delay_timer.timeout.connect(self._start_metrics_timer)
        self._metrics_delay_timer.start(500)  # Start metrics timer after 500ms delay
        
        # Stream status timer - update every 3 seconds (less frequent)
        self.status_timer = QTimer()
        self.status_timer.setSingleShot(False)
        self.status_timer.timeout.connect(self._update_stream_status)
        # Store delay timer to prevent garbage collection
        self._status_delay_timer = QTimer()
        self._status_delay_timer.setSingleShot(True)
        self._status_delay_timer.timeout.connect(self._start_status_timer)
        self._status_delay_timer.start(500)
    
    def _start_metrics_timer(self):
        """Start metrics timer safely"""
        if self._ui_ready and hasattr(self, 'metrics_timer'):
            try:
                self.metrics_timer.start(1500)
            except Exception:
                pass  # Fail silently if timer can't start
    
    def _start_status_timer(self):
        """Start status timer safely"""
        if self._ui_ready and hasattr(self, 'status_timer'):
            try:
                self.status_timer.start(3000)
            except Exception:
                pass  # Fail silently if timer can't start
    
    def _update_metrics(self):
        """Update system metrics - optimized with caching"""
        try:
            # Check if UI is ready
            if not self._ui_ready:
                return
            
            # Check if metrics_label exists
            if not hasattr(self, 'metrics_label') or not self.metrics_label:
                return
            
            # Check if monitoring service is available
            if not self.monitoring_service:
                error_text = "Monitoring service not available"
                if error_text != self._cached_metrics_text:
                    try:
                        self.metrics_label.setText(error_text)
                        self._cached_metrics_text = error_text
                    except Exception:
                        pass  # Fail silently if label doesn't exist
                return
            
            metrics = self.monitoring_service.get_system_metrics()
            if not metrics:
                return
            
            cpu = metrics.get('cpu', {}).get('percent', 0)
            memory = metrics.get('memory', {})
            disk = metrics.get('disk', {})
            
            metrics_text = f"""
═══════════════════════════════════════════════════
           SYSTEM METRICS (Real-time)
═══════════════════════════════════════════════════

CPU Usage:      {cpu:.1f}%

Memory Usage:   {memory.get('percent', 0):.1f}%
                Used: {memory.get('used_gb', 0):.2f} GB / {memory.get('total_gb', 0):.2f} GB

Disk Usage:     {disk.get('percent', 0):.1f}%
                Used: {disk.get('used_gb', 0):.2f} GB / {disk.get('total_gb', 0):.2f} GB

═══════════════════════════════════════════════════
"""
            # Only update if text changed (performance optimization)
            if metrics_text != self._cached_metrics_text:
                self.metrics_label.setText(metrics_text)
                self._cached_metrics_text = metrics_text
        except AttributeError as e:
            # Handle case where attributes don't exist yet
            error_text = f"Metrics not ready: {str(e)}"
            if hasattr(self, 'metrics_label') and self.metrics_label:
                if error_text != self._cached_metrics_text:
                    self.metrics_label.setText(error_text)
                    self._cached_metrics_text = error_text
        except Exception as e:
            error_text = f"Error updating metrics: {e}"
            if hasattr(self, 'metrics_label') and self.metrics_label:
                if error_text != self._cached_metrics_text:
                    self.metrics_label.setText(error_text)
                    self._cached_metrics_text = error_text
    
    def _update_stream_status(self):
        """Update stream status - optimized with caching"""
        try:
            if not self.stream_service:
                return
            
            session = self.stream_service.get_current_session()
            if not session:
                status_text = "No active stream session"
                if status_text != self._cached_status_text:
                    self.stream_status.setText(status_text)
                    self._cached_status_text = status_text
                return
            
            # Calculate runtime
            runtime_str = "N/A"
            if session.start_time:
                if session.stop_time:
                    runtime = session.stop_time - session.start_time
                else:
                    runtime = datetime.now() - session.start_time
                hours, remainder = divmod(int(runtime.total_seconds()), 3600)
                minutes, seconds = divmod(remainder, 60)
                if hours > 0:
                    runtime_str = f"{hours}h {minutes}m {seconds}s"
                elif minutes > 0:
                    runtime_str = f"{minutes}m {seconds}s"
                else:
                    runtime_str = f"{seconds}s"
            
            # Calculate packets per second (if running)
            pps_str = "0"
            if session.status == "running" and session.start_time:
                runtime_seconds = (datetime.now() - session.start_time).total_seconds()
                if runtime_seconds > 0:
                    pps = session.packets_processed / runtime_seconds
                    pps_str = f"{pps:.1f}"
            
            status_text = f"""
═══════════════════════════════════════════════════
          STREAM SESSION STATUS
═══════════════════════════════════════════════════

Session ID:     {session.session_id[:8]}...
Status:         {session.status.upper()}

Start Time:     {session.start_time.strftime('%Y-%m-%d %H:%M:%S') if session.start_time else 'N/A'}
Stop Time:      {session.stop_time.strftime('%Y-%m-%d %H:%M:%S') if session.stop_time else 'Running...'}
Runtime:        {runtime_str}

═══════════════════════════════════════════════════
              REAL-TIME METRICS
═══════════════════════════════════════════════════

  Packets:      {session.packets_processed:,}
  Packets/sec: {pps_str}
  Errors:       {session.errors_count}

═══════════════════════════════════════════════════
"""
            # Only update if text changed (performance optimization)
            if status_text != self._cached_status_text:
                self.stream_status.setText(status_text)
                self._cached_status_text = status_text
        except Exception as e:
            error_text = f"Error updating stream status: {e}"
            if error_text != self._cached_status_text:
                self.stream_status.setText(error_text)
                self._cached_status_text = error_text
    
    def append(self, message: str):
        """Append message to console - thread-safe with signals"""
        # Use signal for thread-safe UI updates (called from background threads)
        try:
            self._console_message.emit(message)
        except Exception:
            # Fallback: try direct call if signal fails (shouldn't happen)
            try:
                if hasattr(self, 'console') and self.console:
                    self.console.append(message)
            except Exception:
                pass  # Fail silently

