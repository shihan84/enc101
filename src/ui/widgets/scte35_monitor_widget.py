"""
SCTE-35 Monitoring Widget
Real-time SCTE-35 event detection and display
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QTextEdit,
    QGroupBox, QLineEdit, QSpinBox, QFormLayout, QScrollArea
)
from PyQt6.QtCore import QTimer, Qt, pyqtSignal
from PyQt6.QtGui import QFont, QColor
from datetime import datetime
from typing import Optional
from src.services.scte35_monitor_service import SCTE35MonitorService, SCTE35Event
from src.services.telegram_service import TelegramService


class SCTE35MonitorWidget(QWidget):
    """Widget for SCTE-35 event monitoring"""
    
    event_detected = pyqtSignal(object)  # Emits SCTE35Event
    
    def __init__(self, monitor_service: Optional[SCTE35MonitorService] = None, 
                 telegram_service: Optional[TelegramService] = None,
                 profile_service=None):
        super().__init__()
        self.monitor_service = monitor_service
        self.telegram_service = telegram_service
        self.profile_service = profile_service  # For saving profile-specific settings
        self.current_profile_name: Optional[str] = None  # Track current profile
        self.setup_ui()
        self.setup_timers()
        
        # Connect to service if available
        if self.monitor_service:
            self.monitor_service.register_event_callback(self._on_event_detected)
            # Set Telegram service if available
            if self.telegram_service:
                self.monitor_service.set_telegram_service(self.telegram_service)
    
    def set_current_profile(self, profile_name: str):
        """Set current profile name and load its Telegram settings"""
        self.current_profile_name = profile_name
        if self.profile_service:
            telegram_settings = self.profile_service.get_telegram_settings(profile_name)
            self._load_telegram_settings(telegram_settings)
    
    def _load_telegram_settings(self, settings: dict):
        """Load Telegram settings into UI"""
        if settings:
            if hasattr(self, 'telegram_token') and settings.get('telegram_bot_token'):
                self.telegram_token.setText(settings.get('telegram_bot_token', ''))
            if hasattr(self, 'telegram_chat_id') and settings.get('telegram_chat_id'):
                self.telegram_chat_id.setText(settings.get('telegram_chat_id', ''))
            if hasattr(self, 'telegram_enable_checkbox'):
                self.telegram_enable_checkbox.setChecked(settings.get('telegram_enabled', False))
    
    def setup_ui(self):
        """Setup user interface with scroll area"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(5, 5, 5, 5)
        main_layout.setSpacing(5)
        
        # Create scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
        """)
        
        # Content widget
        content_widget = QWidget()
        layout = QVBoxLayout(content_widget)
        layout.setSpacing(8)
        layout.setContentsMargins(5, 5, 5, 5)
        
        # Control Panel
        control_group = QGroupBox("🎬 SCTE-35 Monitoring Control")
        control_group.setStyleSheet("""
            QGroupBox {
                border: 2px solid rgba(148, 163, 184, 0.2);
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 15px;
                font-weight: 600;
            }
        """)
        control_layout = QFormLayout()
        
        # Input source
        self.input_source = QLineEdit()
        self.input_source.setPlaceholderText("Enter stream URL (HLS, SRT, UDP, etc.)")
        self.input_source.setStyleSheet("padding: 5px;")
        control_layout.addRow("Input Source:", self.input_source)
        
        # SCTE-35 PID
        self.scte35_pid = QSpinBox()
        self.scte35_pid.setRange(0, 8191)
        self.scte35_pid.setValue(500)
        self.scte35_pid.setStyleSheet("padding: 5px;")
        control_layout.addRow("SCTE-35 PID:", self.scte35_pid)
        
        # Control buttons
        button_layout = QHBoxLayout()
        
        self.start_btn = QPushButton("▶️ Start Monitoring")
        self.start_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                font-weight: bold;
                padding: 8px 15px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:disabled {
                background-color: #666;
            }
        """)
        self.start_btn.clicked.connect(self._start_monitoring)
        button_layout.addWidget(self.start_btn)
        
        self.stop_btn = QPushButton("⏹️ Stop")
        self.stop_btn.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
                font-weight: bold;
                padding: 8px 15px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #da190b;
            }
            QPushButton:disabled {
                background-color: #666;
            }
        """)
        self.stop_btn.setEnabled(False)
        self.stop_btn.clicked.connect(self._stop_monitoring)
        button_layout.addWidget(self.stop_btn)
        
        self.clear_btn = QPushButton("🗑️ Clear Events")
        self.clear_btn.setStyleSheet("""
            QPushButton {
                background-color: #FF9800;
                color: white;
                font-weight: bold;
                padding: 8px 15px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #F57C00;
            }
        """)
        self.clear_btn.clicked.connect(self._clear_events)
        button_layout.addWidget(self.clear_btn)
        
        button_layout.addStretch()
        control_layout.addRow("", button_layout)
        control_group.setLayout(control_layout)
        layout.addWidget(control_group)
        
        # Telegram Notification Panel
        telegram_group = QGroupBox("📱 Telegram Notifications")
        telegram_group.setStyleSheet("""
            QGroupBox {
                border: 2px solid rgba(148, 163, 184, 0.2);
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 15px;
                font-weight: 600;
            }
        """)
        telegram_layout = QFormLayout()
        
        # Bot Token
        self.telegram_token = QLineEdit()
        self.telegram_token.setPlaceholderText("Enter Telegram Bot Token")
        self.telegram_token.setEchoMode(QLineEdit.EchoMode.Password)
        self.telegram_token.setStyleSheet("padding: 5px;")
        if self.telegram_service and self.telegram_service.bot_token:
            self.telegram_token.setText(self.telegram_service.bot_token)
        telegram_layout.addRow("Bot Token:", self.telegram_token)
        
        # Chat ID
        self.telegram_chat_id = QLineEdit()
        self.telegram_chat_id.setPlaceholderText("Enter Chat ID")
        self.telegram_chat_id.setStyleSheet("padding: 5px;")
        if self.telegram_service and self.telegram_service.chat_id:
            self.telegram_chat_id.setText(self.telegram_service.chat_id)
        telegram_layout.addRow("Chat ID:", self.telegram_chat_id)
        
        # Telegram buttons
        telegram_btn_layout = QHBoxLayout()
        
        self.telegram_test_btn = QPushButton("🔍 Test Connection")
        self.telegram_test_btn.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                font-weight: bold;
                padding: 8px 15px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
        """)
        self.telegram_test_btn.clicked.connect(self._test_telegram)
        telegram_btn_layout.addWidget(self.telegram_test_btn)
        
        self.telegram_save_btn = QPushButton("💾 Save Config")
        self.telegram_save_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                font-weight: bold;
                padding: 8px 15px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        self.telegram_save_btn.clicked.connect(self._save_telegram_config)
        telegram_btn_layout.addWidget(self.telegram_save_btn)
        
        # Enable/Disable notifications
        self.telegram_enable_checkbox = QPushButton("🔔 Enable Notifications")
        self.telegram_enable_checkbox.setCheckable(True)
        self.telegram_enable_checkbox.setChecked(True)
        self.telegram_enable_checkbox.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                font-weight: bold;
                padding: 8px 15px;
                border-radius: 5px;
            }
            QPushButton:checked {
                background-color: #4CAF50;
            }
            QPushButton:!checked {
                background-color: #666;
            }
        """)
        self.telegram_enable_checkbox.clicked.connect(self._toggle_telegram_notifications)
        telegram_btn_layout.addWidget(self.telegram_enable_checkbox)
        
        telegram_btn_layout.addStretch()
        telegram_layout.addRow("", telegram_btn_layout)
        
        # Status label
        self.telegram_status_label = QLabel("Status: Not configured")
        self.telegram_status_label.setStyleSheet("color: #888; font-size: 12px;")
        telegram_layout.addRow("", self.telegram_status_label)
        
        telegram_group.setLayout(telegram_layout)
        layout.addWidget(telegram_group)
        
        # Statistics Panel
        stats_group = QGroupBox("📊 Statistics")
        stats_group.setStyleSheet("""
            QGroupBox {
                border: 2px solid rgba(148, 163, 184, 0.2);
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 15px;
                font-weight: 600;
            }
        """)
        stats_layout = QHBoxLayout()
        
        self.total_events_label = QLabel("Total Events: 0")
        self.total_events_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #4CAF50;")
        stats_layout.addWidget(self.total_events_label)
        
        self.events_per_min_label = QLabel("Events/min: 0")
        self.events_per_min_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #2196F3;")
        stats_layout.addWidget(self.events_per_min_label)
        
        self.last_event_label = QLabel("Last Event: None")
        self.last_event_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #FF9800;")
        stats_layout.addWidget(self.last_event_label)
        
        stats_layout.addStretch()
        stats_group.setLayout(stats_layout)
        layout.addWidget(stats_group)
        
        # Events Table
        events_group = QGroupBox("📋 Detected Events")
        events_group.setStyleSheet("""
            QGroupBox {
                border: 2px solid rgba(148, 163, 184, 0.2);
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 15px;
                font-weight: 600;
            }
        """)
        events_layout = QVBoxLayout()
        
        self.events_table = QTableWidget()
        self.events_table.setColumnCount(6)
        self.events_table.setHorizontalHeaderLabels([
            "Time", "Event ID", "Cue Type", "PTS", "Duration", "Status"
        ])
        self.events_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.events_table.setAlternatingRowColors(True)
        self.events_table.setStyleSheet("""
            QTableWidget {
                background-color: #1e1e1e;
                color: #ffffff;
                gridline-color: #444;
            }
            QTableWidget::item {
                padding: 5px;
            }
            QHeaderView::section {
                background-color: #2a2a2a;
                color: #ffffff;
                padding: 8px;
                font-weight: bold;
                border: 1px solid #444;
            }
        """)
        self.events_table.setMaximumHeight(250)
        self.events_table.setMinimumHeight(200)
        events_layout.addWidget(self.events_table)
        
        events_group.setLayout(events_layout)
        layout.addWidget(events_group)
        
        # Log Console
        log_group = QGroupBox("📺 Monitor Log")
        log_group.setStyleSheet("""
            QGroupBox {
                border: 2px solid rgba(148, 163, 184, 0.2);
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 15px;
                font-weight: 600;
            }
        """)
        log_layout = QVBoxLayout()
        
        self.log_console = QTextEdit()
        self.log_console.setReadOnly(True)
        self.log_console.setFont(QFont("Courier", 9))
        self.log_console.setMaximumHeight(150)
        self.log_console.setMinimumHeight(100)
        self.log_console.setStyleSheet("""
            QTextEdit {
                background-color: #1e1e1e;
                color: #00ff00;
                padding: 8px;
                border: 1px solid #444;
                font-size: 9px;
            }
        """)
        log_layout.addWidget(self.log_console)
        
        log_group.setLayout(log_layout)
        layout.addWidget(log_group)
        
        # Set scroll widget
        scroll.setWidget(content_widget)
        main_layout.addWidget(scroll)
    
    def setup_timers(self):
        """Setup update timers"""
        # Update statistics every 2 seconds
        self.stats_timer = QTimer()
        self.stats_timer.timeout.connect(self._update_statistics)
        self.stats_timer.start(2000)
    
    def _start_monitoring(self):
        """Start SCTE-35 monitoring"""
        if not self.monitor_service:
            self.log_console.append("[ERROR] Monitor service not available")
            return
        
        input_source = self.input_source.text().strip()
        if not input_source:
            self.log_console.append("[ERROR] Please enter an input source")
            return
        
        scte35_pid = self.scte35_pid.value()
        
        success = self.monitor_service.start_monitoring(
            input_source,
            scte35_pid,
            output_callback=self.log_console.append
        )
        
        if success:
            self.start_btn.setEnabled(False)
            self.stop_btn.setEnabled(True)
            self.input_source.setEnabled(False)
            self.scte35_pid.setEnabled(False)
        else:
            self.log_console.append("[ERROR] Failed to start monitoring")
    
    def _stop_monitoring(self):
        """Stop SCTE-35 monitoring"""
        if self.monitor_service:
            self.monitor_service.stop_monitoring()
            self.log_console.append("[INFO] Monitoring stopped")
        
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.input_source.setEnabled(True)
        self.scte35_pid.setEnabled(True)
    
    def _clear_events(self):
        """Clear event history"""
        if self.monitor_service:
            self.monitor_service.clear_events()
        self.events_table.setRowCount(0)
        self.log_console.append("[INFO] Event history cleared")
    
    def _on_event_detected(self, event: SCTE35Event):
        """Handle detected SCTE-35 event"""
        # Emit signal
        self.event_detected.emit(event)
        
        # Add to table
        row = self.events_table.rowCount()
        self.events_table.insertRow(row)
        
        # Time
        time_str = event.timestamp.strftime("%H:%M:%S")
        self.events_table.setItem(row, 0, QTableWidgetItem(time_str))
        
        # Event ID
        event_id_str = str(event.event_id) if event.event_id else "N/A"
        self.events_table.setItem(row, 1, QTableWidgetItem(event_id_str))
        
        # Cue Type
        cue_type_str = event.cue_type or "Unknown"
        self.events_table.setItem(row, 2, QTableWidgetItem(cue_type_str))
        
        # PTS
        pts_str = str(event.pts_time) if event.pts_time else "N/A"
        self.events_table.setItem(row, 3, QTableWidgetItem(pts_str))
        
        # Duration
        duration_str = str(event.break_duration) if event.break_duration else "N/A"
        self.events_table.setItem(row, 4, QTableWidgetItem(duration_str))
        
        # Status
        status = "Out of Network" if event.out_of_network else "In Network"
        status_item = QTableWidgetItem(status)
        if event.out_of_network:
            status_item.setForeground(QColor("#f44336"))
        else:
            status_item.setForeground(QColor("#4CAF50"))
        self.events_table.setItem(row, 5, status_item)
        
        # Scroll to bottom
        self.events_table.scrollToBottom()
        
        # Limit rows
        if self.events_table.rowCount() > 1000:
            self.events_table.removeRow(0)
    
    def _update_statistics(self):
        """Update statistics display"""
        if not self.monitor_service:
            return
        
        stats = self.monitor_service.get_statistics()
        
        self.total_events_label.setText(f"Total Events: {stats.get('total_events', 0)}")
        self.events_per_min_label.setText(f"Events/min: {stats.get('events_per_minute', 0)}")
        
        last_event_time = stats.get('last_event_time')
        if last_event_time:
            if isinstance(last_event_time, datetime):
                time_str = last_event_time.strftime("%H:%M:%S")
            else:
                time_str = str(last_event_time)
            self.last_event_label.setText(f"Last Event: {time_str}")
        else:
            self.last_event_label.setText("Last Event: None")
    
    def append_log(self, message: str):
        """Append message to log console"""
        self.log_console.append(message)
        # Auto-scroll
        scrollbar = self.log_console.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
    
    def _test_telegram(self):
        """Test Telegram connection"""
        if not self.telegram_service:
            self.log_console.append("[ERROR] Telegram service not available")
            return
        
        bot_token = self.telegram_token.text().strip()
        chat_id = self.telegram_chat_id.text().strip()
        
        if not bot_token or not chat_id:
            self.log_console.append("[ERROR] Please enter bot token and chat ID")
            self.telegram_status_label.setText("Status: ❌ Missing token/chat ID")
            self.telegram_status_label.setStyleSheet("color: #f44336; font-size: 12px;")
            return
        
        # Configure service
        self.telegram_service.configure(bot_token, chat_id)
        
        # Test connection
        self.log_console.append("[INFO] Testing Telegram connection...")
        if self.telegram_service.test_connection():
            self.log_console.append("[SUCCESS] Telegram connection successful!")
            self.telegram_status_label.setText("Status: ✅ Connected")
            self.telegram_status_label.setStyleSheet("color: #4CAF50; font-size: 12px;")
            
            # Send test message
            self.telegram_service.send_message("✅ <b>IBE-100 Enterprise</b>\n\nTelegram notifications are now active!")
        else:
            self.log_console.append("[ERROR] Telegram connection failed. Check token and chat ID.")
            self.telegram_status_label.setText("Status: ❌ Connection failed")
            self.telegram_status_label.setStyleSheet("color: #f44336; font-size: 12px;")
    
    def _save_telegram_config(self):
        """Save Telegram configuration to current profile"""
        if not self.telegram_service:
            self.log_console.append("[ERROR] Telegram service not available")
            return
        
        bot_token = self.telegram_token.text().strip()
        chat_id = self.telegram_chat_id.text().strip()
        
        if not bot_token or not chat_id:
            self.log_console.append("[ERROR] Please enter bot token and chat ID")
            return
        
        # Configure service
        self.telegram_service.configure(bot_token, chat_id)
        
        # Update monitor service
        if self.monitor_service:
            self.monitor_service.set_telegram_service(self.telegram_service)
        
        # Save to current profile if profile service is available
        if self.profile_service and self.current_profile_name:
            enabled = self.telegram_enable_checkbox.isChecked() if hasattr(self, 'telegram_enable_checkbox') else True
            success = self.profile_service.save_telegram_settings(
                self.current_profile_name,
                bot_token,
                chat_id,
                enabled=enabled,
                notify_scte35=True,
                notify_errors=True
            )
            if success:
                self.log_console.append(f"[INFO] Telegram configuration saved to profile: {self.current_profile_name}")
            else:
                self.log_console.append("[WARNING] Failed to save Telegram settings to profile")
        else:
            if not self.current_profile_name:
                self.log_console.append("[WARNING] No profile selected. Please load a profile first to save Telegram settings.")
            else:
                self.log_console.append("[INFO] Telegram configuration saved (profile service not available)")
        
        self.telegram_status_label.setText("Status: 💾 Configuration saved")
        self.telegram_status_label.setStyleSheet("color: #2196F3; font-size: 12px;")
    
    def _toggle_telegram_notifications(self, checked: bool):
        """Toggle Telegram notifications"""
        if self.monitor_service:
            self.monitor_service.enable_telegram_notifications(checked)
        
        if checked:
            self.log_console.append("[INFO] Telegram notifications enabled")
            self.telegram_enable_checkbox.setText("🔔 Enable Notifications")
        else:
            self.log_console.append("[INFO] Telegram notifications disabled")
            self.telegram_enable_checkbox.setText("🔕 Disable Notifications")

