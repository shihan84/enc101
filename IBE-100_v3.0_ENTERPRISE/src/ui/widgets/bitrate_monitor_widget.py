"""
Bitrate Monitor Widget
Real-time bitrate monitoring with charts and alerts
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QGroupBox, QLineEdit, QSpinBox, QFormLayout, QFrame,
    QDoubleSpinBox, QTextEdit, QScrollArea
)
from PyQt6.QtCore import QTimer, Qt, pyqtSignal
from PyQt6.QtGui import QFont, QColor
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional
from src.services.bitrate_monitor_service import BitrateMonitorService, BitratePoint


class BitrateCard(QFrame):
    """Card for displaying bitrate"""
    
    def __init__(self, title: str, value: str = "0.00", unit: str = "Mbps", color: str = "#3b82f6"):
        super().__init__()
        self.title = title
        self.value = value
        self.unit = unit
        self.color = color
        self.setup_ui()
    
    def setup_ui(self):
        """Setup card UI"""
        self.setStyleSheet(f"""
            QFrame {{
                background-color: #2a2a2a;
                border: 2px solid {self.color};
                border-radius: 8px;
                padding: 15px;
            }}
        """)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(5)
        
        title_label = QLabel(self.title)
        title_label.setStyleSheet("color: #888; font-size: 12px;")
        layout.addWidget(title_label)
        
        value_layout = QHBoxLayout()
        self.value_label = QLabel(self.value)
        self.value_label.setObjectName("value_label")
        self.value_label.setStyleSheet(f"color: {self.color}; font-size: 32px; font-weight: bold;")
        value_layout.addWidget(self.value_label)
        
        unit_label = QLabel(self.unit)
        unit_label.setStyleSheet("color: #888; font-size: 14px; padding-top: 8px;")
        value_layout.addWidget(unit_label)
        value_layout.addStretch()
        
        layout.addLayout(value_layout)
        layout.addStretch()
    
    def update_value(self, value: str):
        """Update value"""
        value_label = self.findChild(QLabel, "value_label")
        if value_label:
            value_label.setText(value)


class BitrateMonitorWidget(QWidget):
    """Widget for bitrate monitoring"""
    
    threshold_alert = pyqtSignal(str, float)  # Emits (alert_type, bitrate)
    
    def __init__(self, monitor_service: Optional[BitrateMonitorService] = None):
        super().__init__()
        self.monitor_service = monitor_service
        self.setup_ui()
        self.setup_timers()
        
        # Connect to service if available
        if self.monitor_service:
            self.monitor_service.register_alert_callback(self._on_alert)
    
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
        control_group = QGroupBox("📈 Bitrate Monitoring Control")
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
        
        # Monitoring interval
        self.interval = QSpinBox()
        self.interval.setRange(1, 60)
        self.interval.setValue(5)
        self.interval.setSuffix(" seconds")
        self.interval.setStyleSheet("padding: 5px;")
        control_layout.addRow("Interval:", self.interval)
        
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
        
        self.clear_btn = QPushButton("🗑️ Clear History")
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
        self.clear_btn.clicked.connect(self._clear_history)
        button_layout.addWidget(self.clear_btn)
        
        button_layout.addStretch()
        control_layout.addRow("", button_layout)
        control_group.setLayout(control_layout)
        layout.addWidget(control_group)
        
        # Bitrate Cards Row - Compact
        bitrate_row = QHBoxLayout()
        bitrate_row.setSpacing(10)
        
        self.current_bitrate_card = BitrateCard("Current Bitrate", "0.00", "Mbps", "#3b82f6")
        self.current_bitrate_card.setFixedHeight(100)
        self.current_bitrate_card.setMinimumWidth(160)
        bitrate_row.addWidget(self.current_bitrate_card)
        
        self.avg_bitrate_card = BitrateCard("Average", "0.00", "Mbps", "#10b981")
        self.avg_bitrate_card.setFixedHeight(100)
        self.avg_bitrate_card.setMinimumWidth(160)
        bitrate_row.addWidget(self.avg_bitrate_card)
        
        self.min_bitrate_card = BitrateCard("Minimum", "0.00", "Mbps", "#f59e0b")
        self.min_bitrate_card.setFixedHeight(100)
        self.min_bitrate_card.setMinimumWidth(160)
        bitrate_row.addWidget(self.min_bitrate_card)
        
        self.max_bitrate_card = BitrateCard("Maximum", "0.00", "Mbps", "#ef4444")
        self.max_bitrate_card.setFixedHeight(100)
        self.max_bitrate_card.setMinimumWidth(160)
        bitrate_row.addWidget(self.max_bitrate_card)
        
        bitrate_row.addStretch()
        layout.addLayout(bitrate_row)
        
        # Threshold Settings
        threshold_group = QGroupBox("⚠️ Alert Thresholds")
        threshold_group.setStyleSheet("""
            QGroupBox {
                border: 2px solid rgba(148, 163, 184, 0.2);
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 15px;
                font-weight: 600;
            }
        """)
        threshold_layout = QFormLayout()
        
        self.min_threshold = QDoubleSpinBox()
        self.min_threshold.setRange(0, 1000)
        self.min_threshold.setValue(0)
        self.min_threshold.setSuffix(" Mbps")
        self.min_threshold.setStyleSheet("padding: 5px;")
        threshold_layout.addRow("Minimum Threshold:", self.min_threshold)
        
        self.max_threshold = QDoubleSpinBox()
        self.max_threshold.setRange(0, 1000)
        self.max_threshold.setValue(0)
        self.max_threshold.setSuffix(" Mbps")
        self.max_threshold.setStyleSheet("padding: 5px;")
        threshold_layout.addRow("Maximum Threshold:", self.max_threshold)
        
        threshold_btn = QPushButton("💾 Set Thresholds")
        threshold_btn.setStyleSheet("""
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
        threshold_btn.clicked.connect(self._set_thresholds)
        threshold_layout.addRow("", threshold_btn)
        
        threshold_group.setLayout(threshold_layout)
        layout.addWidget(threshold_group)
        
        # Statistics
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
        
        self.samples_label = QLabel("Samples: 0")
        self.samples_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #4CAF50;")
        stats_layout.addWidget(self.samples_label)
        
        self.export_btn = QPushButton("📥 Export Report")
        self.export_btn.setStyleSheet("""
            QPushButton {
                background-color: #8b5cf6;
                color: white;
                font-weight: bold;
                padding: 8px 15px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #7c3aed;
            }
        """)
        self.export_btn.clicked.connect(self._export_report)
        stats_layout.addWidget(self.export_btn)
        
        stats_layout.addStretch()
        stats_group.setLayout(stats_layout)
        layout.addWidget(stats_group)
        
        # Monitor Log
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
        self.log_console.setMaximumHeight(120)
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
        # Update display every 2 seconds
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self._update_display)
        self.update_timer.start(2000)
    
    def _start_monitoring(self):
        """Start bitrate monitoring"""
        if not self.monitor_service:
            self.log_console.append("[ERROR] Monitor service not available")
            return
        
        input_source = self.input_source.text().strip()
        if not input_source:
            self.log_console.append("[ERROR] Please enter an input source")
            return
        
        interval = self.interval.value()
        
        success = self.monitor_service.start_monitoring(
            input_source,
            interval,
            output_callback=self.log_console.append
        )
        
        if success:
            self.start_btn.setEnabled(False)
            self.stop_btn.setEnabled(True)
            self.input_source.setEnabled(False)
            self.interval.setEnabled(False)
        else:
            self.log_console.append("[ERROR] Failed to start monitoring")
    
    def _stop_monitoring(self):
        """Stop bitrate monitoring"""
        if self.monitor_service:
            self.monitor_service.stop_monitoring()
            self.log_console.append("[INFO] Monitoring stopped")
        
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.input_source.setEnabled(True)
        self.interval.setEnabled(True)
    
    def _clear_history(self):
        """Clear bitrate history"""
        if self.monitor_service:
            self.monitor_service.clear_history()
        self.log_console.append("[INFO] Bitrate history cleared")
    
    def _set_thresholds(self):
        """Set bitrate thresholds"""
        if not self.monitor_service:
            return
        
        min_br = self.min_threshold.value() if self.min_threshold.value() > 0 else None
        max_br = self.max_threshold.value() if self.max_threshold.value() > 0 else None
        
        self.monitor_service.set_thresholds(min_br, max_br)
        self.log_console.append(f"[INFO] Thresholds set: min={min_br}, max={max_br}")
    
    def _on_alert(self, alert_type: str, bitrate: float):
        """Handle bitrate alert"""
        self.threshold_alert.emit(alert_type, bitrate)
        self.log_console.append(f"[ALERT] {alert_type}: Bitrate = {bitrate:.2f} Mbps")
    
    def _update_display(self):
        """Update bitrate display"""
        if not self.monitor_service:
            return
        
        # Update current bitrate
        current = self.monitor_service.get_current_bitrate()
        self.current_bitrate_card.update_value(f"{current:.2f}")
        
        # Update statistics
        stats = self.monitor_service.get_statistics()
        self.avg_bitrate_card.update_value(f"{stats.get('average_bitrate', 0):.2f}")
        self.min_bitrate_card.update_value(f"{stats.get('min_bitrate', 0):.2f}")
        self.max_bitrate_card.update_value(f"{stats.get('max_bitrate', 0):.2f}")
        self.samples_label.setText(f"Samples: {stats.get('total_samples', 0)}")
    
    def _export_report(self):
        """Export bitrate report"""
        if not self.monitor_service:
            return
        
        try:
            report = self.monitor_service.export_report("csv")
            report_path = Path("reports") / f"bitrate_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            report_path.parent.mkdir(exist_ok=True)
            report_path.write_text(report, encoding='utf-8')
            self.log_console.append(f"[SUCCESS] Report exported: {report_path}")
        except Exception as e:
            self.log_console.append(f"[ERROR] Failed to export report: {e}")
    
    def append_log(self, message: str):
        """Append message to log"""
        self.log_console.append(message)
        scrollbar = self.log_console.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

