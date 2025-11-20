"""
Stream Quality Analysis Widget
Real-time stream quality monitoring and metrics display
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QTextEdit,
    QGroupBox, QLineEdit, QSpinBox, QFormLayout, QFrame, QScrollArea
)
from PyQt6.QtCore import QTimer, Qt, pyqtSignal
from PyQt6.QtGui import QFont, QColor
from datetime import datetime
from typing import Optional
from src.services.stream_analyzer_service import StreamAnalyzerService, StreamMetrics, ComplianceReport


class QualityMetricCard(QFrame):
    """Card widget for displaying quality metrics"""
    
    def __init__(self, title: str, value: str = "N/A", color: str = "#4CAF50"):
        super().__init__()
        self.title = title
        self.value = value
        self.color = color
        self.setup_ui()
    
    def setup_ui(self):
        """Setup metric card UI"""
        self.setStyleSheet(f"""
            QFrame {{
                background-color: #2a2a2a;
                border: 2px solid {self.color};
                border-radius: 8px;
                padding: 10px;
            }}
        """)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(5)
        
        title_label = QLabel(self.title)
        title_label.setStyleSheet("color: #888; font-size: 11px;")
        layout.addWidget(title_label)
        
        self.value_label = QLabel(self.value)
        self.value_label.setObjectName("value_label")
        self.value_label.setStyleSheet(f"color: {self.color}; font-size: 24px; font-weight: bold;")
        layout.addWidget(self.value_label)
        
        layout.addStretch()
    
    def update_value(self, value: str):
        """Update metric value"""
        value_label = self.findChild(QLabel, "value_label")
        if value_label:
            value_label.setText(value)


class StreamQualityWidget(QWidget):
    """Widget for stream quality analysis"""
    
    metrics_updated = pyqtSignal(object)  # Emits StreamMetrics
    compliance_changed = pyqtSignal(object)  # Emits ComplianceReport
    
    def __init__(self, analyzer_service: Optional[StreamAnalyzerService] = None):
        super().__init__()
        self.analyzer_service = analyzer_service
        self.setup_ui()
        self.setup_timers()
        
        # Connect to service if available
        if self.analyzer_service:
            self.analyzer_service.register_metrics_callback(self._on_metrics_updated)
            self.analyzer_service.register_compliance_callback(self._on_compliance_changed)
    
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
        control_group = QGroupBox("📊 Stream Quality Analysis Control")
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
        
        # Analysis interval
        self.interval = QSpinBox()
        self.interval.setRange(1, 60)
        self.interval.setValue(5)
        self.interval.setSuffix(" seconds")
        self.interval.setStyleSheet("padding: 5px;")
        control_layout.addRow("Analysis Interval:", self.interval)
        
        # Control buttons
        button_layout = QHBoxLayout()
        
        self.start_btn = QPushButton("▶️ Start Analysis")
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
        self.start_btn.clicked.connect(self._start_analysis)
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
        self.stop_btn.clicked.connect(self._stop_analysis)
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
        
        # Quality Metrics Row - Compact
        metrics_row = QHBoxLayout()
        metrics_row.setSpacing(10)
        
        self.bitrate_card = QualityMetricCard("Bitrate", "0.00", "#3b82f6")
        self.bitrate_card.setFixedHeight(90)
        self.bitrate_card.setMinimumWidth(140)
        metrics_row.addWidget(self.bitrate_card)
        
        self.packets_card = QualityMetricCard("Packets/sec", "0", "#f59e0b")
        self.packets_card.setFixedHeight(90)
        self.packets_card.setMinimumWidth(140)
        metrics_row.addWidget(self.packets_card)
        
        self.errors_card = QualityMetricCard("Continuity Errors", "0", "#ef4444")
        self.errors_card.setFixedHeight(90)
        self.errors_card.setMinimumWidth(140)
        metrics_row.addWidget(self.errors_card)
        
        self.pcr_card = QualityMetricCard("PCR Jitter", "0.0", "#8b5cf6")
        self.pcr_card.setFixedHeight(90)
        self.pcr_card.setMinimumWidth(140)
        metrics_row.addWidget(self.pcr_card)
        
        metrics_row.addStretch()
        layout.addLayout(metrics_row)
        
        # Compliance Status
        compliance_group = QGroupBox("✅ ETSI TR 101 290 Compliance")
        compliance_group.setStyleSheet("""
            QGroupBox {
                border: 2px solid rgba(148, 163, 184, 0.2);
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 15px;
                font-weight: 600;
            }
        """)
        compliance_layout = QHBoxLayout()
        
        self.compliance_status = QLabel("Status: Not Analyzed")
        self.compliance_status.setStyleSheet("font-size: 14px; font-weight: bold; color: #888;")
        compliance_layout.addWidget(self.compliance_status)
        
        self.priority1_label = QLabel("Priority 1: 0")
        self.priority1_label.setStyleSheet("color: #ef4444; font-weight: bold;")
        compliance_layout.addWidget(self.priority1_label)
        
        self.priority2_label = QLabel("Priority 2: 0")
        self.priority2_label.setStyleSheet("color: #f59e0b; font-weight: bold;")
        compliance_layout.addWidget(self.priority2_label)
        
        self.priority3_label = QLabel("Priority 3: 0")
        self.priority3_label.setStyleSheet("color: #3b82f6; font-weight: bold;")
        compliance_layout.addWidget(self.priority3_label)
        
        compliance_layout.addStretch()
        compliance_group.setLayout(compliance_layout)
        layout.addWidget(compliance_group)
        
        # Metrics History Table
        history_group = QGroupBox("📋 Metrics History")
        history_group.setStyleSheet("""
            QGroupBox {
                border: 2px solid rgba(148, 163, 184, 0.2);
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 15px;
                font-weight: 600;
            }
        """)
        history_layout = QVBoxLayout()
        
        self.metrics_table = QTableWidget()
        self.metrics_table.setColumnCount(6)
        self.metrics_table.setHorizontalHeaderLabels([
            "Time", "Bitrate (Mbps)", "Packets/sec", "Continuity Errors", "PCR Errors", "PCR Jitter"
        ])
        self.metrics_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.metrics_table.setAlternatingRowColors(True)
        self.metrics_table.setMaximumHeight(180)
        self.metrics_table.setMinimumHeight(150)
        self.metrics_table.setStyleSheet("""
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
        history_layout.addWidget(self.metrics_table)
        
        history_group.setLayout(history_layout)
        layout.addWidget(history_group)
        
        # Analysis Log
        log_group = QGroupBox("📺 Analysis Log")
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
    
    def _start_analysis(self):
        """Start stream quality analysis"""
        if not self.analyzer_service:
            self.log_console.append("[ERROR] Analyzer service not available")
            return
        
        input_source = self.input_source.text().strip()
        if not input_source:
            self.log_console.append("[ERROR] Please enter an input source")
            return
        
        interval = self.interval.value()
        
        success = self.analyzer_service.start_analysis(
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
            self.log_console.append("[ERROR] Failed to start analysis")
    
    def _stop_analysis(self):
        """Stop stream quality analysis"""
        if self.analyzer_service:
            self.analyzer_service.stop_analysis()
            self.log_console.append("[INFO] Analysis stopped")
        
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.input_source.setEnabled(True)
        self.interval.setEnabled(True)
    
    def _clear_history(self):
        """Clear metrics history"""
        if self.analyzer_service:
            self.analyzer_service.clear_history()
        self.metrics_table.setRowCount(0)
        self.log_console.append("[INFO] Metrics history cleared")
    
    def _on_metrics_updated(self, metrics: StreamMetrics):
        """Handle metrics update"""
        self.metrics_updated.emit(metrics)
        
        # Add to table
        row = self.metrics_table.rowCount()
        self.metrics_table.insertRow(row)
        
        # Time
        time_str = metrics.timestamp.strftime("%H:%M:%S")
        self.metrics_table.setItem(row, 0, QTableWidgetItem(time_str))
        
        # Bitrate
        self.metrics_table.setItem(row, 1, QTableWidgetItem(f"{metrics.bitrate:.2f}"))
        
        # Packets/sec
        self.metrics_table.setItem(row, 2, QTableWidgetItem(str(metrics.packets_per_second)))
        
        # Continuity errors
        error_item = QTableWidgetItem(str(metrics.continuity_errors))
        if metrics.continuity_errors > 0:
            error_item.setForeground(QColor("#ef4444"))
        self.metrics_table.setItem(row, 3, error_item)
        
        # PCR errors
        self.metrics_table.setItem(row, 4, QTableWidgetItem(str(metrics.pcr_errors)))
        
        # PCR jitter
        self.metrics_table.setItem(row, 5, QTableWidgetItem(f"{metrics.pcr_jitter:.2f}"))
        
        # Scroll to bottom
        self.metrics_table.scrollToBottom()
        
        # Limit rows
        if self.metrics_table.rowCount() > 1000:
            self.metrics_table.removeRow(0)
    
    def _on_compliance_changed(self, report: ComplianceReport):
        """Handle compliance report update"""
        self.compliance_changed.emit(report)
        
        if report.compliant:
            self.compliance_status.setText("Status: ✅ Compliant")
            self.compliance_status.setStyleSheet("font-size: 14px; font-weight: bold; color: #4CAF50;")
        else:
            self.compliance_status.setText("Status: ❌ Non-Compliant")
            self.compliance_status.setStyleSheet("font-size: 14px; font-weight: bold; color: #ef4444;")
        
        self.priority1_label.setText(f"Priority 1: {report.priority_1_errors}")
        self.priority2_label.setText(f"Priority 2: {report.priority_2_errors}")
        self.priority3_label.setText(f"Priority 3: {report.priority_3_errors}")
    
    def _update_display(self):
        """Update metrics display"""
        if not self.analyzer_service:
            return
        
        metrics = self.analyzer_service.get_current_metrics()
        if metrics:
            self.bitrate_card.update_value(f"{metrics.bitrate:.2f}")
            self.packets_card.update_value(str(metrics.packets_per_second))
            self.errors_card.update_value(str(metrics.continuity_errors))
            self.pcr_card.update_value(f"{metrics.pcr_jitter:.1f}")
        
        # Update compliance
        report = self.analyzer_service.get_compliance_report()
        if report:
            self._on_compliance_changed(report)
    
    def append_log(self, message: str):
        """Append message to log console"""
        self.log_console.append(message)
        scrollbar = self.log_console.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

