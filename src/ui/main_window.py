"""
Enterprise Main Window
Modern UI with enterprise service integration
"""

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QTabWidget,
    QPushButton, QLabel, QMessageBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap, QIcon
from pathlib import Path
from typing import Optional

from ..core import Application as AppFramework
from ..models.stream_config import StreamConfig
from .widgets import StreamConfigWidget, SCTE35Widget, MonitoringWidget, DashboardWidget, EPGEditorWidget
from .themes import apply_modern_theme


class MainWindow(QMainWindow):
    """Enterprise Main Window"""
    
    def __init__(self, app_framework: AppFramework):
        super().__init__()
        self.app = app_framework
        self.logger = self.app.logger
        
        # Get services
        self.stream_service = self.app.get_service("stream")
        self.scte35_service = self.app.get_service("scte35")
        self.profile_service = self.app.get_service("profile")
        self.monitoring_service = self.app.get_service("monitoring")
        
        # State
        self.current_config: Optional[StreamConfig] = None
        self.current_marker = None
        self.current_profile_name: Optional[str] = None  # Track current profile
        
        self.setup_ui()
        self.setup_connections()
        self._update_marker_indicator()  # Initialize marker indicator
        
        self.logger.info("Main window initialized")
    
    def setup_ui(self):
        """Setup user interface"""
        config = self.app.config
        self.setWindowTitle(f"{config.app_name} v{config.app_version}")
        self.setMinimumSize(config.window_width, config.window_height)
        
        # Set window icon (also set on QApplication for taskbar)
        # Handle both development and PyInstaller bundled modes
        import sys
        if getattr(sys, 'frozen', False):
            # PyInstaller bundled mode
            base_path = Path(sys._MEIPASS)
            icon_path = base_path / "logo.ico"
        else:
            # Development mode
            icon_path = Path("logo.ico")
        
        if icon_path.exists():
            self.setWindowIcon(QIcon(str(icon_path)))
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # Header
        header_layout = QHBoxLayout()
        logo_label = QLabel()
        logo_path = Path("logo.png")
        if logo_path.exists():
            pixmap = QPixmap(str(logo_path))
            scaled = pixmap.scaled(50, 50, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            logo_label.setPixmap(scaled)
        else:
            logo_label.setText("🏠")
            logo_label.setStyleSheet("font-size: 40px;")
        
        title_label = QLabel("Broadcast Encoder 110")
        title_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #4CAF50;")
        
        header_layout.addWidget(logo_label)
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        main_layout.addLayout(header_layout)
        
        # Tabs
        self.tab_widget = QTabWidget()
        self.tab_widget.setStyleSheet("""
            QTabWidget::pane { border: 1px solid #444; background-color: #2a2a2a; }
            QTabBar::tab { background-color: #3a3a3a; color: white; padding: 10px 20px; }
            QTabBar::tab:selected { background-color: #4CAF50; }
        """)
        
        # Dashboard tab
        self.dashboard_widget = DashboardWidget(self.app)
        # Set quick action callbacks
        self.dashboard_widget.set_quick_action_callbacks(
            start_callback=self._quick_start_stream,
            marker_callback=self._quick_generate_marker,
            logs_callback=self._view_logs
        )
        self.tab_widget.addTab(self.dashboard_widget, "📊 Dashboard")
        
        # Configuration tab
        self.config_widget = StreamConfigWidget(self.profile_service, self.stream_service)
        self.config_widget.profile_loaded.connect(self._on_profile_loaded)
        self.tab_widget.addTab(self.config_widget, "⚙️ Configuration")
        
        # SCTE-35 tab
        self.scte35_widget = SCTE35Widget(self.scte35_service)
        self.scte35_widget.marker_generated.connect(self._on_marker_generated)
        self.tab_widget.addTab(self.scte35_widget, "🎬 SCTE-35")
        
        # Track current profile
        self.current_profile_name: Optional[str] = None
        
        # EPG Editor tab
        epg_service = self.app.get_service("epg")
        self.epg_widget = EPGEditorWidget(epg_service)
        self.epg_widget.epg_generated.connect(self._on_epg_generated)
        self.tab_widget.addTab(self.epg_widget, "📺 EPG Editor")
        
        # Monitoring tab
        scte35_monitor_service = self.app.get_service("scte35_monitor")
        telegram_service = self.app.get_service("telegram")
        stream_analyzer_service = self.app.get_service("stream_analyzer")
        bitrate_monitor_service = self.app.get_service("bitrate_monitor")
        self.monitoring_widget = MonitoringWidget(
            self.monitoring_service, 
            self.stream_service,
            scte35_monitor_service,
            telegram_service,
            stream_analyzer_service,
            bitrate_monitor_service
        )
        self.tab_widget.addTab(self.monitoring_widget, "📺 Monitoring")
        
        main_layout.addWidget(self.tab_widget)
        
        # Control buttons
        control_layout = QHBoxLayout()
        
        self.start_btn = QPushButton("▶️ Start Processing")
        self.start_btn.setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold; padding: 10px;")
        control_layout.addWidget(self.start_btn)
        
        self.stop_btn = QPushButton("⏹️ Stop")
        self.stop_btn.setStyleSheet("background-color: #f44336; color: white; font-weight: bold; padding: 10px;")
        self.stop_btn.setEnabled(False)
        control_layout.addWidget(self.stop_btn)
        
        # Current marker indicator
        self.marker_indicator = QLabel("📌 No marker selected")
        self.marker_indicator.setStyleSheet("color: #888; font-size: 11px; padding: 5px; font-style: italic;")
        control_layout.addWidget(self.marker_indicator)
        
        main_layout.addLayout(control_layout)
        
        # Footer
        footer = QLabel(f"© 2024 Broadcast Encoder 110 | v{config.app_version}")
        footer.setStyleSheet("color: #888; font-size: 10px; padding: 5px;")
        main_layout.addWidget(footer)
        
        # Apply modern theme
        apply_modern_theme(self.app.qt_app)
        self._apply_theme()
    
    def _on_marker_generated(self, marker):
        """Handle marker generation - automatically replaces old marker"""
        old_marker = self.current_marker
        self.current_marker = marker
        
        if old_marker:
            self.monitoring_widget.append(f"[INFO] Old marker replaced: {old_marker.xml_path.name}")
            self.monitoring_widget.append(f"[INFO] Old marker will NOT be used in stream")
        
        self.monitoring_widget.append(f"[SUCCESS] New marker generated: {marker.xml_path.name}")
        self.monitoring_widget.append(f"[INFO] This marker will be used for next stream start")
        
        # Update marker indicator
        self._update_marker_indicator()
    
    def _update_marker_indicator(self):
        """Update the marker indicator in the UI"""
        if self.current_marker:
            self.marker_indicator.setText(f"📌 Active: {self.current_marker.xml_path.name}")
            self.marker_indicator.setStyleSheet("color: #4CAF50; font-size: 11px; padding: 5px; font-weight: bold;")
        else:
            self.marker_indicator.setText("📌 No marker selected")
            self.marker_indicator.setStyleSheet("color: #888; font-size: 11px; padding: 5px; font-style: italic;")
    
    def _on_epg_generated(self, eit_path):
        """Handle EPG/EIT generation"""
        self.monitoring_widget.append(f"[SUCCESS] Generated EIT file: {eit_path.name}")
    
    def _on_profile_loaded(self, profile_name: str):
        """Handle profile loaded - update services to use profile-specific settings"""
        if profile_name != self.current_profile_name:
            self.current_profile_name = profile_name
            # Update SCTE-35 service to use profile-specific directory
            if self.scte35_service:
                self.scte35_service.set_profile(profile_name)
                self.logger.info(f"SCTE-35 service switched to profile: {profile_name}")
                self.monitoring_widget.append(f"[INFO] SCTE-35 markers directory: {self.scte35_service.markers_dir}")
                # Update SCTE-35 widget display
                if hasattr(self, 'scte35_widget'):
                    self.scte35_widget.update_profile(profile_name)
            
            # Load profile-specific Telegram settings
            if self.profile_service:
                telegram_settings = self.profile_service.get_telegram_settings(profile_name)
                if telegram_settings and telegram_settings.get('telegram_bot_token'):
                    # Update Telegram service with profile-specific settings
                    telegram_service = self.app.get_service("telegram")
                    if telegram_service:
                        telegram_service.configure(
                            telegram_settings.get('telegram_bot_token', ''),
                            telegram_settings.get('telegram_chat_id', '')
                        )
                        self.logger.info(f"Loaded Telegram settings for profile: {profile_name}")
                        self.monitoring_widget.append(f"[INFO] Telegram settings loaded for profile: {profile_name}")
                        
                        # Update monitoring widget with new Telegram service and profile
                        if hasattr(self, 'monitoring_widget') and hasattr(self.monitoring_widget, 'scte35_monitor_widget'):
                            if self.monitoring_widget.scte35_monitor_widget:
                                self.monitoring_widget.scte35_monitor_widget.telegram_service = telegram_service
                                self.monitoring_widget.scte35_monitor_widget.set_current_profile(profile_name)
    
    def _apply_theme(self):
        """Apply enterprise theme"""
        self.setStyleSheet("""
            QMainWindow {
                background-color: #1a1a1a;
            }
            QWidget {
                color: #ffffff;
                background-color: #2a2a2a;
            }
            QLineEdit, QSpinBox, QComboBox {
                color: #000000;
                background-color: #ffffff;
                border: 2px solid #555;
                border-radius: 4px;
                padding: 5px;
            }
            QGroupBox {
                border: 2px solid #444;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
                font-weight: bold;
            }
        """)
    
    def setup_connections(self):
        """Setup signal connections"""
        self.start_btn.clicked.connect(self._start_stream)
        self.stop_btn.clicked.connect(self._stop_stream)
    
    def _start_stream(self):
        """Start stream processing"""
        try:
            # Get configuration from widget
            config = self.config_widget.get_config()
            
            # Validate configuration
            if not config.input_url or not config.input_url.strip():
                QMessageBox.warning(self, "Configuration Error", "Please enter an input stream URL")
                return
            
            if config.output_type.value == "SRT" and (not config.output_srt or not config.output_srt.strip()):
                QMessageBox.warning(self, "Configuration Error", "Please enter an SRT destination")
                return
            
            # Confirm marker selection
            if self.current_marker:
                reply = QMessageBox.question(
                    self, "Confirm Marker Selection",
                    f"📌 Marker to be used in stream:\n\n"
                    f"   {self.current_marker.xml_path.name}\n\n"
                    f"⚠️ Only this marker will be used.\n"
                    f"Old markers will NOT be included.\n\n"
                    f"Continue with stream start?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                    QMessageBox.StandardButton.Yes
                )
                if reply != QMessageBox.StandardButton.Yes:
                    return
            else:
                reply = QMessageBox.question(
                    self, "No Marker Selected",
                    "⚠️ No SCTE-35 marker is currently selected.\n\n"
                    "The stream will start WITHOUT SCTE-35 markers.\n\n"
                    "Do you want to:\n"
                    "• Continue without marker\n"
                    "• Cancel and generate a marker first",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                    QMessageBox.StandardButton.No
                )
                if reply != QMessageBox.StandardButton.Yes:
                    return
            
            # Start stream
            session = self.stream_service.start_stream(
                config,
                self.current_marker,
                output_callback=self.monitoring_widget.append
            )
            
            self.current_config = config
            self.start_btn.setEnabled(False)
            self.stop_btn.setEnabled(True)
            self.monitoring_widget.append(f"[INFO] Stream started: {session.session_id}")
            self.monitoring_widget.append(f"[INFO] Input: {config.input_type.value} - {config.input_url}")
            self.monitoring_widget.append(f"[INFO] Output: {config.output_type.value} - {config.output_srt if config.output_type.value == 'SRT' else 'N/A'}")
            if self.current_marker:
                self.monitoring_widget.append(f"[INFO] Using marker: {self.current_marker.xml_path.name}")
            
        except Exception as e:
            self.logger.error(f"Failed to start stream: {e}", exc_info=True)
            QMessageBox.critical(self, "Error", f"Failed to start stream:\n{str(e)}")
            self.start_btn.setEnabled(True)
            self.stop_btn.setEnabled(False)
    
    def _stop_stream(self):
        """Stop stream processing"""
        self.stream_service.stop_stream()
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.monitoring_widget.append("[INFO] Stream stopped")
    
    def _quick_start_stream(self):
        """Quick start stream from dashboard"""
        # Switch to configuration tab
        self.tab_widget.setCurrentIndex(1)  # Configuration tab
        # Trigger start if config is ready
        if self.current_config:
            self._start_stream()
        else:
            QMessageBox.information(
                self, "Configuration Required",
                "Please configure your stream settings first, then click Start Processing."
            )
    
    def _quick_generate_marker(self):
        """Quick generate marker from dashboard"""
        # Switch to SCTE-35 tab
        self.tab_widget.setCurrentIndex(2)  # SCTE-35 tab
        QMessageBox.information(
            self, "Generate Marker",
            "Configure your marker settings and click Generate."
        )
    
    def _view_logs(self):
        """View application logs"""
        import subprocess
        import os
        
        logs_dir = Path("logs")
        if logs_dir.exists():
            # Open logs directory in file explorer
            if os.name == 'nt':  # Windows
                os.startfile(str(logs_dir.absolute()))
            else:
                subprocess.Popen(['xdg-open', str(logs_dir.absolute())])
        else:
            QMessageBox.information(self, "Logs", "Logs directory not found.")

