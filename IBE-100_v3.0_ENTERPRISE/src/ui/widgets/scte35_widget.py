"""
Enhanced SCTE-35 Widget
Complete marker generation interface
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QScrollArea,
    QLabel, QSpinBox, QComboBox, QGroupBox, QPushButton,
    QTimeEdit, QCheckBox, QMessageBox
)
from PyQt6.QtCore import Qt, QTime, pyqtSignal
from pathlib import Path

from src.models.scte35_marker import SCTE35Marker, CueType


class SCTE35Widget(QWidget):
    """Enhanced SCTE-35 marker generation widget"""
    
    marker_generated = pyqtSignal(SCTE35Marker)
    
    def __init__(self, scte35_service):
        super().__init__()
        self.scte35_service = scte35_service
        self.setup_ui()
        self._update_directory_display()
        # Initialize auto-increment state
        if hasattr(self, 'auto_increment') and self.auto_increment.isChecked():
            self._on_auto_increment_toggled(True)
    
    def setup_ui(self):
        """Setup user interface"""
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_widget = QWidget()
        layout = QVBoxLayout(scroll_widget)
        
        # Title
        title = QLabel("🎬 Generate SCTE-35 Marker")
        title.setStyleSheet("font-size: 20px; font-weight: bold; color: #4CAF50; padding: 10px;")
        layout.addWidget(title)
        
        # Profile Directory Info
        self.directory_label = QLabel()
        self.directory_label.setStyleSheet("font-size: 11px; color: #888; padding: 5px; font-style: italic;")
        self.directory_label.setWordWrap(True)
        layout.addWidget(self.directory_label)
        
        # Marker Configuration
        config_group = QGroupBox("Marker Configuration")
        config_layout = QVBoxLayout()
        
        # Event ID
        event_id_layout = QHBoxLayout()
        event_id_layout.addWidget(QLabel("Event ID:"))
        event_id_layout.addStretch()
        self.event_id = QSpinBox()
        self.event_id.setRange(10000, 99999)
        self.event_id.setValue(10023)
        self.event_id.setMinimumWidth(150)
        event_id_layout.addWidget(self.event_id)
        
        # Auto Increment Checkbox
        self.auto_increment = QCheckBox("Auto Increment")
        self.auto_increment.setChecked(True)
        self.auto_increment.toggled.connect(self._on_auto_increment_toggled)
        event_id_layout.addWidget(self.auto_increment)
        event_id_layout.addStretch()
        
        config_layout.addLayout(event_id_layout)
        
        # Cue Type
        cue_type_layout = QHBoxLayout()
        cue_type_layout.addWidget(QLabel("Cue Type:"))
        cue_type_layout.addStretch()
        self.cue_type = QComboBox()
        self.cue_type.addItems([ct.value for ct in CueType])
        self.cue_type.setCurrentText(CueType.PREROLL.value)
        self.cue_type.setMinimumWidth(200)
        cue_type_layout.addWidget(self.cue_type)
        config_layout.addLayout(cue_type_layout)
        
        # Pre-roll Duration
        preroll_layout = QHBoxLayout()
        preroll_layout.addWidget(QLabel("Pre-roll Duration (seconds) [Min: 4.0 recommended]:"))
        preroll_layout.addStretch()
        self.preroll_duration = QSpinBox()
        self.preroll_duration.setRange(0, 10)
        self.preroll_duration.setValue(4)  # Industry standard minimum: 4.0 seconds
        self.preroll_duration.setMinimumWidth(150)
        preroll_layout.addWidget(self.preroll_duration)
        config_layout.addLayout(preroll_layout)
        
        # Ad Duration
        ad_duration_layout = QHBoxLayout()
        ad_duration_layout.addWidget(QLabel("Ad Duration (seconds):"))
        ad_duration_layout.addStretch()
        self.ad_duration = QSpinBox()
        self.ad_duration.setRange(1, 3600)
        self.ad_duration.setValue(600)
        self.ad_duration.setMinimumWidth(150)
        ad_duration_layout.addWidget(self.ad_duration)
        config_layout.addLayout(ad_duration_layout)
        
        config_group.setLayout(config_layout)
        layout.addWidget(config_group)
        
        # Scheduling Options
        schedule_group = QGroupBox("Scheduling Options")
        schedule_layout = QVBoxLayout()
        
        self.immediate_cue = QCheckBox("Trigger Cue Immediately (No Schedule)")
        self.immediate_cue.setChecked(True)
        self.immediate_cue.toggled.connect(self._on_immediate_toggled)
        schedule_layout.addWidget(self.immediate_cue)
        
        schedule_time_layout = QHBoxLayout()
        schedule_time_layout.addWidget(QLabel("Schedule Time (HH:MM:SS):"))
        schedule_time_layout.addStretch()
        self.schedule_time = QTimeEdit()
        self.schedule_time.setDisplayFormat("HH:mm:ss")
        self.schedule_time.setTime(QTime.currentTime())
        self.schedule_time.setMinimumWidth(150)
        self.schedule_time.setEnabled(False)
        schedule_time_layout.addWidget(self.schedule_time)
        schedule_layout.addLayout(schedule_time_layout)
        
        schedule_group.setLayout(schedule_layout)
        layout.addWidget(schedule_group)
        
        # Generate Buttons
        button_layout = QHBoxLayout()
        
        self.generate_btn = QPushButton("🎯 Generate Marker")
        self.generate_btn.setStyleSheet("""
            QPushButton { 
                background-color: #4CAF50; 
                color: white; 
                font-weight: bold; 
                padding: 12px; 
                font-size: 14px;
                border-radius: 8px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        self.generate_btn.clicked.connect(self._generate_marker)
        button_layout.addWidget(self.generate_btn)
        
        self.generate_pair_btn = QPushButton("🎬 Generate CUE Pair")
        self.generate_pair_btn.setStyleSheet("""
            QPushButton { 
                background-color: #2196F3; 
                color: white; 
                font-weight: bold; 
                padding: 12px; 
                font-size: 14px;
                border-radius: 8px;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
        """)
        self.generate_pair_btn.setToolTip("Generate CUE-OUT and CUE-IN with sequential event IDs")
        self.generate_pair_btn.clicked.connect(self._generate_cue_pair)
        button_layout.addWidget(self.generate_pair_btn)
        
        layout.addLayout(button_layout)
        
        layout.addStretch()
        scroll.setWidget(scroll_widget)
        
        main_layout = QVBoxLayout(self)
        main_layout.addWidget(scroll)
    
    def _on_immediate_toggled(self, checked: bool):
        """Handle immediate cue toggle"""
        self.schedule_time.setEnabled(not checked)
    
    def _on_auto_increment_toggled(self, checked: bool):
        """Handle auto-increment toggle"""
        self.event_id.setEnabled(not checked)
        if checked:
            # Update to next available ID
            next_id = self.scte35_service.get_next_event_id()
            self.event_id.setValue(next_id)
    
    def _update_directory_display(self):
        """Update directory display"""
        if self.scte35_service:
            profile_name = getattr(self.scte35_service, 'profile_name', 'default')
            markers_dir = self.scte35_service.markers_dir
            self.directory_label.setText(f"📁 Markers Directory: {markers_dir} | Profile: {profile_name}")
    
    def update_profile(self, profile_name: str):
        """Update when profile changes"""
        self._update_directory_display()
    
    def _generate_marker(self):
        """Generate SCTE-35 marker"""
        try:
            auto_inc = self.auto_increment.isChecked()
            event_id = self.event_id.value() if not auto_inc else None
            
            cue_type = CueType(self.cue_type.currentText())
            preroll = self.preroll_duration.value()
            ad_duration = self.ad_duration.value()
            immediate = self.immediate_cue.isChecked()
            schedule_time = None if immediate else self.schedule_time.time().toString("HH:mm:ss")
            
            # If PREROLL is selected, generate sequence (CUE-OUT, CUE-IN, CUE-CRASH)
            if cue_type == CueType.PREROLL:
                cue_out, cue_in, cue_crash = self.scte35_service.generate_preroll_sequence(
                    base_event_id=event_id,
                    preroll_seconds=preroll,
                    ad_duration_seconds=ad_duration,
                    immediate=immediate,
                    auto_increment=auto_inc,
                    include_crash=True
                )
                
                # Update UI with next available ID
                if auto_inc:
                    next_id = self.scte35_service.get_next_event_id()
                    self.event_id.setValue(next_id)
                
                # Emit all markers
                self.marker_generated.emit(cue_out)
                self.marker_generated.emit(cue_in)
                if cue_crash:
                    self.marker_generated.emit(cue_crash)
                
                QMessageBox.information(
                    self, "Success",
                    f"Preroll sequence generated successfully!\n\n"
                    f"CUE-OUT:\n"
                    f"  File: {cue_out.xml_path.name}\n"
                    f"  Event ID: {cue_out.event_id}\n\n"
                    f"CUE-IN:\n"
                    f"  File: {cue_in.xml_path.name}\n"
                    f"  Event ID: {cue_in.event_id}\n\n"
                    f"CUE-CRASH:\n"
                    f"  File: {cue_crash.xml_path.name}\n"
                    f"  Event ID: {cue_crash.event_id}\n\n"
                    f"Ad Duration: {ad_duration} seconds"
                )
            else:
                # Generate single marker for other types
                marker = self.scte35_service.generate_marker(
                    event_id=event_id,
                    cue_type=cue_type,
                    preroll_seconds=preroll,
                    ad_duration_seconds=ad_duration,
                    schedule_time=schedule_time,
                    immediate=immediate,
                    auto_increment=auto_inc
                )
                
                # Update UI with new event ID if auto-increment was used
                if auto_inc:
                    self.event_id.setValue(marker.event_id)
                
                self.marker_generated.emit(marker)
                QMessageBox.information(
                    self, "Success",
                    f"Marker generated successfully!\n\n"
                    f"File: {marker.xml_path.name}\n"
                    f"Event ID: {marker.event_id}\n"
                    f"Cue Type: {cue_type.value}"
                )
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to generate marker:\n{str(e)}")
    
    def _generate_cue_pair(self):
        """Generate CUE-OUT and CUE-IN pair with sequential event IDs"""
        try:
            auto_inc = self.auto_increment.isChecked()
            base_event_id = self.event_id.value() if not auto_inc else None
            
            ad_duration = self.ad_duration.value()
            immediate = self.immediate_cue.isChecked()
            
            cue_out, cue_in = self.scte35_service.generate_cue_pair(
                base_event_id=base_event_id,
                ad_duration_seconds=ad_duration,
                immediate=immediate,
                auto_increment=auto_inc
            )
            
            # Update UI with next available ID
            if auto_inc:
                next_id = self.scte35_service.get_next_event_id()
                self.event_id.setValue(next_id)
            
            self.marker_generated.emit(cue_out)
            self.marker_generated.emit(cue_in)
            
            QMessageBox.information(
                self, "Success",
                f"CUE pair generated successfully!\n\n"
                f"CUE-OUT:\n"
                f"  File: {cue_out.xml_path.name}\n"
                f"  Event ID: {cue_out.event_id}\n\n"
                f"CUE-IN:\n"
                f"  File: {cue_in.xml_path.name}\n"
                f"  Event ID: {cue_in.event_id}\n\n"
                f"Ad Duration: {ad_duration} seconds"
            )
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to generate CUE pair:\n{str(e)}")

