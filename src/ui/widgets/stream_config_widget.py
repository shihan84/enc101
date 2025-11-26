"""
Enhanced Stream Configuration Widget
Complete configuration interface with all settings
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QScrollArea,
    QLabel, QLineEdit, QSpinBox, QComboBox, QGroupBox,
    QCheckBox, QPushButton, QMessageBox, QInputDialog
)
from PyQt6.QtCore import pyqtSignal
from typing import Optional

from src.models.stream_config import StreamConfig, InputType, OutputType
from src.services.profile_service import ProfileService
from src.services.stream_service import StreamService


class StreamConfigWidget(QWidget):
    """Enhanced stream configuration widget"""
    
    config_changed = pyqtSignal(StreamConfig)
    profile_loaded = pyqtSignal(str)  # Emits profile name when profile is loaded
    
    def __init__(self, profile_service: ProfileService, stream_service: 'StreamService' = None):
        super().__init__()
        self.profile_service = profile_service
        self.stream_service = stream_service
        self.setup_ui()
        self._setup_profile_management()
    
    def setup_ui(self):
        """Setup user interface"""
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_widget = QWidget()
        layout = QVBoxLayout(scroll_widget)
        
        # Profile Management
        profile_group = QGroupBox("Profile Management")
        profile_layout = QVBoxLayout()
        
        profile_select_layout = QHBoxLayout()
        profile_select_layout.addWidget(QLabel("Profile:"))
        self.profile_combo = QComboBox()
        self.profile_combo.setEditable(True)
        self.profile_combo.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)
        self.profile_combo.lineEdit().setPlaceholderText("Type profile name or select existing...")
        self._refresh_profiles()
        profile_select_layout.addWidget(self.profile_combo, 1)
        
        self.load_profile_btn = QPushButton("Load")
        self.load_profile_btn.clicked.connect(self._load_profile)
        profile_select_layout.addWidget(self.load_profile_btn)
        
        self.save_profile_btn = QPushButton("Save")
        self.save_profile_btn.clicked.connect(self._save_profile)
        profile_select_layout.addWidget(self.save_profile_btn)
        
        self.delete_profile_btn = QPushButton("Delete")
        self.delete_profile_btn.clicked.connect(self._delete_profile)
        profile_select_layout.addWidget(self.delete_profile_btn)
        
        profile_layout.addLayout(profile_select_layout)
        profile_group.setLayout(profile_layout)
        layout.addWidget(profile_group)
        
        # Input Configuration
        input_group = QGroupBox("Input Stream")
        input_layout = QVBoxLayout()
        
        self.input_type = QComboBox()
        self.input_type.addItems([it.value for it in InputType])
        self.input_type.setCurrentText(InputType.HLS.value)
        input_layout.addWidget(QLabel("Input Type:"))
        input_layout.addWidget(self.input_type)
        
        self.input_url = QLineEdit()
        self.input_url.setPlaceholderText("Enter stream URL (e.g., https://cdn.example.com/stream/index.m3u8)")
        self.input_url.setText("https://cdn.itassist.one/BREAKING/NEWS/index.m3u8")
        input_layout.addWidget(QLabel("Stream URL/Address:"))
        input_layout.addWidget(self.input_url)
        
        input_group.setLayout(input_layout)
        layout.addWidget(input_group)
        
        # Output Configuration
        output_group = QGroupBox("Output Streams")
        output_layout = QVBoxLayout()
        
        self.output_type = QComboBox()
        self.output_type.addItems([ot.value for ot in OutputType])
        self.output_type.setCurrentText(OutputType.SRT.value)
        self.output_type.currentTextChanged.connect(self._on_output_type_changed)
        output_layout.addWidget(QLabel("Output Type:"))
        output_layout.addWidget(self.output_type)
        
        # SRT Output
        self.output_srt = QLineEdit()
        self.output_srt.setPlaceholderText("Enter SRT destination (e.g., cdn.example.com:8888)")
        self.output_srt.setText("cdn.itassist.one:8888")
        self.output_srt_label = QLabel("SRT Destination:")
        output_layout.addWidget(self.output_srt_label)
        output_layout.addWidget(self.output_srt)
        
        # HLS Output
        self.output_hls = QLineEdit()
        self.output_hls.setPlaceholderText("Enter HLS output directory")
        self.output_hls.setText("output/hls")
        self.output_hls_label = QLabel("HLS Output Directory:")
        self.output_hls_label.setVisible(False)
        self.output_hls.setVisible(False)
        output_layout.addWidget(self.output_hls_label)
        output_layout.addWidget(self.output_hls)
        
        # DASH Output
        self.output_dash = QLineEdit()
        self.output_dash.setPlaceholderText("Enter DASH output directory")
        self.output_dash.setText("output/dash")
        self.output_dash_label = QLabel("DASH Output Directory:")
        self.output_dash_label.setVisible(False)
        self.output_dash.setVisible(False)
        output_layout.addWidget(self.output_dash_label)
        output_layout.addWidget(self.output_dash)
        
        output_group.setLayout(output_layout)
        layout.addWidget(output_group)
        
        # Service Configuration
        service_group = QGroupBox("Service Configuration")
        service_layout = QVBoxLayout()
        
        self.service_name = QLineEdit()
        self.service_name.setText("SCTE-35 Stream")
        service_layout.addWidget(QLabel("Service Name:"))
        service_layout.addWidget(self.service_name)
        
        self.provider_name = QLineEdit()
        self.provider_name.setText("ITAssist")
        service_layout.addWidget(QLabel("Provider Name:"))
        service_layout.addWidget(self.provider_name)
        
        self.service_id = QSpinBox()
        self.service_id.setRange(1, 65535)
        self.service_id.setValue(1)
        service_layout.addWidget(QLabel("Service ID:"))
        service_layout.addWidget(self.service_id)
        
        service_group.setLayout(service_layout)
        layout.addWidget(service_group)
        
        # PID Configuration
        pid_group = QGroupBox("PID Configuration")
        pid_layout = QVBoxLayout()
        
        self.vpid = QSpinBox()
        self.vpid.setRange(32, 8190)
        self.vpid.setValue(256)
        pid_layout.addWidget(QLabel("Video PID:"))
        pid_layout.addWidget(self.vpid)
        
        self.apid = QSpinBox()
        self.apid.setRange(32, 8190)
        self.apid.setValue(257)
        pid_layout.addWidget(QLabel("Audio PID:"))
        pid_layout.addWidget(self.apid)
        
        self.scte35_pid = QSpinBox()
        self.scte35_pid.setRange(32, 8190)
        self.scte35_pid.setValue(500)
        pid_layout.addWidget(QLabel("SCTE-35 PID:"))
        pid_layout.addWidget(self.scte35_pid)
        
        pid_group.setLayout(pid_layout)
        layout.addWidget(pid_group)
        
        # SRT Configuration
        srt_group = QGroupBox("SRT Configuration")
        srt_layout = QVBoxLayout()
        
        self.stream_id = QLineEdit()
        self.stream_id.setText("#!::r=scte/scte,m=publish")
        self.stream_id.setPlaceholderText("Enter Stream ID for SRT")
        srt_layout.addWidget(QLabel("Stream ID:"))
        srt_layout.addWidget(self.stream_id)
        
        self.latency = QSpinBox()
        self.latency.setRange(100, 10000)
        self.latency.setValue(2000)
        self.latency.setSuffix(" ms")
        srt_layout.addWidget(QLabel("Latency:"))
        srt_layout.addWidget(self.latency)
        
        # Test SRT Connection button
        test_srt_btn = QPushButton("🔍 Test SRT Connection")
        test_srt_btn.setStyleSheet("background-color: #2196F3; color: white; padding: 8px;")
        test_srt_btn.clicked.connect(self._test_srt_connection)
        srt_layout.addWidget(test_srt_btn)
        
        srt_group.setLayout(srt_layout)
        layout.addWidget(srt_group)
        
        # HLS/DASH Settings
        hls_dash_group = QGroupBox("HLS/DASH Output Settings")
        hls_dash_layout = QVBoxLayout()
        
        self.enable_cors = QCheckBox("Enable CORS Headers")
        self.enable_cors.setChecked(True)
        hls_dash_layout.addWidget(self.enable_cors)
        
        self.segment_duration = QSpinBox()
        self.segment_duration.setRange(2, 30)
        self.segment_duration.setValue(6)
        self.segment_duration.setSuffix(" seconds")
        hls_dash_layout.addWidget(QLabel("Segment Duration:"))
        hls_dash_layout.addWidget(self.segment_duration)
        
        self.playlist_window = QSpinBox()
        self.playlist_window.setRange(3, 20)
        self.playlist_window.setValue(5)
        hls_dash_layout.addWidget(QLabel("Playlist Window Size:"))
        hls_dash_layout.addWidget(self.playlist_window)
        
        hls_dash_group.setLayout(hls_dash_layout)
        layout.addWidget(hls_dash_group)
        
        # SCTE-35 Injection Settings
        injection_group = QGroupBox("SCTE-35 Injection Settings")
        injection_layout = QVBoxLayout()
        
        self.start_delay = QSpinBox()
        self.start_delay.setRange(0, 10000)
        self.start_delay.setValue(2000)
        self.start_delay.setSuffix(" ms")
        injection_layout.addWidget(QLabel("Start Delay:"))
        injection_layout.addWidget(self.start_delay)
        
        self.inject_count = QSpinBox()
        self.inject_count.setRange(1, 100000)  # Increased from 1000 to 100000 for long streams
        self.inject_count.setValue(1)
        injection_layout.addWidget(QLabel("Inject Count:"))
        injection_layout.addWidget(self.inject_count)
        
        self.inject_interval = QSpinBox()
        self.inject_interval.setRange(100, 60000)
        self.inject_interval.setValue(1000)
        self.inject_interval.setSuffix(" ms")
        injection_layout.addWidget(QLabel("Inject Interval:"))
        injection_layout.addWidget(self.inject_interval)
        
        injection_group.setLayout(injection_layout)
        layout.addWidget(injection_group)
        
        layout.addStretch()
        scroll.setWidget(scroll_widget)
        
        main_layout = QVBoxLayout(self)
        main_layout.addWidget(scroll)
    
    def _setup_profile_management(self):
        """Setup profile management"""
        pass
    
    def _refresh_profiles(self):
        """Refresh profile list"""
        self.profile_combo.clear()
        profiles = self.profile_service.get_profile_names()
        if profiles:
            self.profile_combo.addItems(profiles)
    
    def _load_profile(self):
        """Load selected profile"""
        profile_name = self.profile_combo.currentText().strip()
        if not profile_name:
            return
        
        profile = self.profile_service.get_profile(profile_name)
        if not profile:
            QMessageBox.warning(self, "Error", f"Profile '{profile_name}' not found")
            return
        
        if profile.config:
            self._apply_config(profile.config)
            # Emit signal to notify profile change
            self.profile_loaded.emit(profile_name)
            QMessageBox.information(self, "Success", f"Profile '{profile_name}' loaded")
    
    def _test_srt_connection(self):
        """Test SRT connection"""
        if not self.stream_service:
            QMessageBox.warning(self, "Error", "Stream service not available")
            return
        
        # Get SRT configuration
        output_type = self.output_type.currentText()
        if output_type != OutputType.SRT.value:
            QMessageBox.warning(self, "Error", "Please select SRT as output type first")
            return
        
        server = self.output_srt.text().strip()
        if not server:
            QMessageBox.warning(self, "Error", "Please enter SRT destination (server:port)")
            return
        
        stream_id = self.stream_id.text().strip() if hasattr(self, 'stream_id') else ""
        
        # Show testing message
        QMessageBox.information(self, "Testing", f"Testing SRT connection to {server}...\n\nThis may take a few seconds.")
        
        # Test connection
        success, message = self.stream_service.test_srt_connection(server, stream_id if stream_id else None)
        
        if success:
            QMessageBox.information(self, "Success", f"✅ {message}\n\nSRT connection is working correctly!")
        else:
            QMessageBox.warning(
                self, "Connection Failed", 
                f"❌ {message}\n\n"
                f"Troubleshooting Tips:\n"
                f"1. Check Stream ID format - try without '#!::' prefix\n"
                f"2. Try leaving Stream ID empty\n"
                f"3. Verify server address and port are correct\n"
                f"4. Ensure server is accepting connections\n"
                f"5. Check firewall/network settings"
            )
    
    def _save_profile(self):
        """Save current configuration as profile"""
        profile_name = self.profile_combo.currentText().strip()
        if not profile_name:
            name, ok = QInputDialog.getText(self, "Save Profile", "Profile Name:")
            if not ok or not name.strip():
                return
            profile_name = name.strip()
        
        desc, ok = QInputDialog.getText(self, "Save Profile", "Description (optional):")
        if not ok:
            desc = ""
        
        from src.models.profile import Profile
        config = self.get_config()
        profile = Profile(name=profile_name, description=desc, config=config)
        
        if self.profile_service.save_profile(profile):
            self._refresh_profiles()
            self.profile_combo.setCurrentText(profile_name)
            QMessageBox.information(self, "Success", f"Profile '{profile_name}' saved")
        else:
            QMessageBox.warning(self, "Error", "Failed to save profile")
    
    def _delete_profile(self):
        """Delete selected profile"""
        profile_name = self.profile_combo.currentText().strip()
        if not profile_name:
            return
        
        reply = QMessageBox.question(
            self, "Delete Profile",
            f"Are you sure you want to delete profile '{profile_name}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            if self.profile_service.delete_profile(profile_name):
                self._refresh_profiles()
                QMessageBox.information(self, "Success", f"Profile '{profile_name}' deleted")
            else:
                QMessageBox.warning(self, "Error", "Failed to delete profile")
    
    def _on_output_type_changed(self, text: str):
        """Handle output type change"""
        # Hide all
        self.output_srt.setVisible(False)
        self.output_srt_label.setVisible(False)
        self.output_hls.setVisible(False)
        self.output_hls_label.setVisible(False)
        self.output_dash.setVisible(False)
        self.output_dash_label.setVisible(False)
        
        # Show relevant
        if text == OutputType.SRT.value:
            self.output_srt.setVisible(True)
            self.output_srt_label.setVisible(True)
        elif text == OutputType.HLS.value:
            self.output_hls.setVisible(True)
            self.output_hls_label.setVisible(True)
        elif text == OutputType.DASH.value:
            self.output_dash.setVisible(True)
            self.output_dash_label.setVisible(True)
        else:
            self.output_srt.setVisible(True)
            self.output_srt_label.setVisible(True)
    
    def _apply_config(self, config: StreamConfig):
        """Apply configuration to UI"""
        self.input_type.setCurrentText(config.input_type.value)
        self.input_url.setText(config.input_url)
        self.output_type.setCurrentText(config.output_type.value)
        self.output_srt.setText(config.output_srt)
        self.output_hls.setText(config.output_hls)
        self.output_dash.setText(config.output_dash)
        self.service_name.setText(config.service_name)
        self.provider_name.setText(config.provider_name)
        self.service_id.setValue(config.service_id)
        self.vpid.setValue(config.vpid)
        self.apid.setValue(config.apid)
        self.scte35_pid.setValue(config.scte35_pid)
        self.stream_id.setText(config.stream_id)
        self.latency.setValue(config.latency)
        self.enable_cors.setChecked(config.enable_cors)
        self.segment_duration.setValue(config.segment_duration)
        self.playlist_window.setValue(config.playlist_window)
        self.start_delay.setValue(config.start_delay)
        self.inject_count.setValue(config.inject_count)
        self.inject_interval.setValue(config.inject_interval)
        
        self._on_output_type_changed(config.output_type.value)
    
    def get_config(self) -> StreamConfig:
        """Get current configuration"""
        return StreamConfig(
            input_type=InputType(self.input_type.currentText()),
            input_url=self.input_url.text(),
            output_type=OutputType(self.output_type.currentText()),
            output_srt=self.output_srt.text(),
            output_hls=self.output_hls.text(),
            output_dash=self.output_dash.text(),
            service_name=self.service_name.text(),
            provider_name=self.provider_name.text(),
            service_id=self.service_id.value(),
            vpid=self.vpid.value(),
            apid=self.apid.value(),
            scte35_pid=self.scte35_pid.value(),
            stream_id=self.stream_id.text(),
            latency=self.latency.value(),
            enable_cors=self.enable_cors.isChecked(),
            segment_duration=self.segment_duration.value(),
            playlist_window=self.playlist_window.value(),
            start_delay=self.start_delay.value(),
            inject_count=self.inject_count.value(),
            inject_interval=self.inject_interval.value()
        )

