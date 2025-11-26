#!/usr/bin/env python3
"""
ITAssist Broadcast Encoder - 100 (IBE-100) v2.0
Clean, Minimal Implementation
"""

import sys
import os
import shutil
import psutil
from pathlib import Path
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QTabWidget
from PyQt6.QtWidgets import QPushButton, QLabel, QLineEdit, QSpinBox, QGroupBox, QScrollArea, QComboBox, QTimeEdit, QCheckBox
from PyQt6.QtCore import Qt, pyqtSignal, QTimer, QTime, QThread
from PyQt6.QtGui import QFont, QPixmap

# Import profile manager
try:
    from profile_manager import ProfileManager
except ImportError:
    # Fallback if profile_manager not found
    ProfileManager = None

# Set UTF-8 encoding for Windows console
os.system('chcp 65001 >nul 2>&1')

# Find TSDuck installation
def find_tsduck():
    """Find TSDuck installation"""
    # Check common installation paths
    paths = [
        "C:\\Program Files\\TSDuck\\bin\\tsp.exe",
        "C:\\TSDuck\\bin\\tsp.exe",
        "tsp.exe",  # Try PATH
        "tsp"  # Try PATH without extension
    ]
    
    for path in paths:
        if shutil.which(path) or os.path.exists(path):
            if os.path.exists(path):
                return path
            else:
                found = shutil.which(path)
                if found:
                    return found
    
    return "tsp"  # Fallback to tsp if not found

TSDUCK_PATH = find_tsduck()
print(f"[INFO] TSDuck found at: {TSDUCK_PATH}")

def kill_all_tsduck_processes():
    """Force kill all TSDuck processes running in background"""
    import subprocess
    import platform
    
    killed_count = 0
    
    try:
        if platform.system() == "Windows":
            # Kill tsp.exe processes
            result = subprocess.run(
                ["taskkill", "/F", "/IM", "tsp.exe"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                creationflags=subprocess.CREATE_NO_WINDOW if hasattr(subprocess, 'CREATE_NO_WINDOW') else 0
            )
            
            # Count processes killed
            if "SUCCESS" in result.stdout or "terminated" in result.stdout.lower():
                # Parse output to count
                lines = result.stdout.split('\n')
                for line in lines:
                    if "terminated" in line.lower():
                        killed_count += 1
            
            # Also try PowerShell method as backup
            try:
                ps_result = subprocess.run(
                    ["powershell", "-Command", "Get-Process | Where-Object {$_.ProcessName -like '*tsp*'} | Stop-Process -Force"],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    timeout=5,
                    creationflags=subprocess.CREATE_NO_WINDOW if hasattr(subprocess, 'CREATE_NO_WINDOW') else 0
                )
            except:
                pass
        
        return killed_count
    except Exception as e:
        print(f"[WARNING] Error killing TSDuck processes: {e}")
        return 0

class StreamConfigWidget(QWidget):
    """Stream Configuration - Input/Output Settings"""
    
    def __init__(self):
        super().__init__()
        # Initialize profile manager
        if ProfileManager:
            self.profile_manager = ProfileManager()
        else:
            self.profile_manager = None
        self.setup_ui()
    
    def setup_ui(self):
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_widget = QWidget()
        layout = QVBoxLayout(scroll_widget)
        
        # Profile Management Section
        if self.profile_manager:
            profile_group = QGroupBox("Profile Management")
            profile_layout = QVBoxLayout()
            
            # Profile Selection
            profile_select_layout = QHBoxLayout()
            profile_select_layout.addWidget(QLabel("Profile:"))
            self.profile_combo = QComboBox()
            self.profile_combo.setEditable(True)  # Allow typing profile names
            self.profile_combo.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)  # Don't auto-add typed text
            self.profile_combo.lineEdit().setPlaceholderText("Type profile name or select existing...")
            self.refresh_profiles()
            profile_select_layout.addWidget(self.profile_combo, 1)
            
            # Load Profile Button
            self.load_profile_btn = QPushButton("Load Profile")
            self.load_profile_btn.clicked.connect(self.load_selected_profile)
            profile_select_layout.addWidget(self.load_profile_btn)
            
            # Save Profile Button
            self.save_profile_btn = QPushButton("Save as Profile")
            self.save_profile_btn.clicked.connect(self.save_current_profile)
            profile_select_layout.addWidget(self.save_profile_btn)
            
            # Delete Profile Button
            self.delete_profile_btn = QPushButton("Delete")
            self.delete_profile_btn.clicked.connect(self.delete_selected_profile)
            profile_select_layout.addWidget(self.delete_profile_btn)
            
            profile_layout.addLayout(profile_select_layout)
            profile_group.setLayout(profile_layout)
            layout.addWidget(profile_group)
        
        # Input Configuration
        input_group = QGroupBox("Input Stream")
        input_layout = QVBoxLayout()
        
        # Input Type Selection
        input_type_layout = QHBoxLayout()
        input_type_layout.addWidget(QLabel("Input Type:"))
        self.input_type = QComboBox()
        self.input_type.addItems(["HLS (HTTP Live Streaming)", "SRT (Secure Reliable Transport)", "UDP (User Datagram Protocol)", "TCP (Transmission Control Protocol)", "HTTP/HTTPS", "DVB", "ASI"])
        self.input_type.setCurrentText("HLS (HTTP Live Streaming)")
        input_type_layout.addWidget(self.input_type)
        input_layout.addLayout(input_type_layout)
        
        # Input URL/Address
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
        
        # Output Type Selection
        output_type_layout = QHBoxLayout()
        output_type_layout.addWidget(QLabel("Output Type:"))
        output_type_layout.addStretch()
        self.output_type = QComboBox()
        self.output_type.addItems(["SRT", "HLS", "DASH", "UDP", "TCP", "HTTP/HTTPS", "File"])
        self.output_type.setCurrentText("SRT")
        output_type_layout.addWidget(self.output_type)
        output_layout.addLayout(output_type_layout)
        
        # SRT Destination
        self.output_srt = QLineEdit()
        self.output_srt.setPlaceholderText("Enter SRT destination (e.g., cdn.example.com:8888)")
        self.output_srt.setText("cdn.itassist.one:8888")
        self.output_srt.setVisible(True)
        output_layout.addWidget(QLabel("SRT Destination:"))
        output_layout.addWidget(self.output_srt)
        
        # HLS Output
        self.output_hls_label = QLabel("HLS Output Directory:")
        self.output_hls = QLineEdit()
        self.output_hls.setPlaceholderText("Enter HLS output directory (e.g., /path/to/output)")
        self.output_hls.setText("output/hls")
        self.output_hls.setVisible(False)
        self.output_hls_label.setVisible(False)
        output_layout.addWidget(self.output_hls_label)
        output_layout.addWidget(self.output_hls)
        
        # DASH Output
        self.output_dash_label = QLabel("DASH Output Directory:")
        self.output_dash = QLineEdit()
        self.output_dash.setPlaceholderText("Enter DASH output directory (e.g., /path/to/output)")
        self.output_dash.setText("output/dash")
        self.output_dash.setVisible(False)
        self.output_dash_label.setVisible(False)
        output_layout.addWidget(self.output_dash_label)
        output_layout.addWidget(self.output_dash)
        
        # Show/Hide based on output type
        self.output_type.currentTextChanged.connect(self.on_output_type_changed)
        
        output_group.setLayout(output_layout)
        layout.addWidget(output_group)
        
        # Service Configuration
        service_group = QGroupBox("Service Configuration")
        service_layout = QVBoxLayout()
        
        # Service Name
        service_name_layout = QHBoxLayout()
        service_name_layout.addWidget(QLabel("Service Name:"))
        self.service_name = QLineEdit()
        self.service_name.setText("SCTE-35 Stream")
        service_name_layout.addWidget(self.service_name)
        service_layout.addLayout(service_name_layout)
        
        # Provider Name
        provider_layout = QHBoxLayout()
        provider_layout.addWidget(QLabel("Provider Name:"))
        self.provider_name = QLineEdit()
        self.provider_name.setText("ITAssist")
        provider_layout.addWidget(self.provider_name)
        service_layout.addLayout(provider_layout)
        
        # Service ID
        service_id_layout = QHBoxLayout()
        service_id_layout.addWidget(QLabel("Service ID:"))
        self.service_id = QSpinBox()
        self.service_id.setRange(1, 65535)
        self.service_id.setValue(1)
        service_id_layout.addWidget(self.service_id)
        service_layout.addLayout(service_id_layout)
        
        # Video PID
        vpid_layout = QHBoxLayout()
        vpid_layout.addWidget(QLabel("Video PID:"))
        self.vpid = QSpinBox()
        self.vpid.setRange(32, 8190)
        self.vpid.setValue(256)
        vpid_layout.addWidget(self.vpid)
        service_layout.addLayout(vpid_layout)
        
        # Audio PID
        apid_layout = QHBoxLayout()
        apid_layout.addWidget(QLabel("Audio PID:"))
        self.apid = QSpinBox()
        self.apid.setRange(32, 8190)
        self.apid.setValue(257)
        apid_layout.addWidget(self.apid)
        service_layout.addLayout(apid_layout)
        
        # SCTE-35 PID
        scte35_pid_layout = QHBoxLayout()
        scte35_pid_layout.addWidget(QLabel("SCTE-35 PID:"))
        self.scte35_pid = QSpinBox()
        self.scte35_pid.setRange(32, 8190)
        self.scte35_pid.setValue(500)
        scte35_pid_layout.addWidget(self.scte35_pid)
        service_layout.addLayout(scte35_pid_layout)
        
        service_group.setLayout(service_layout)
        layout.addWidget(service_group)
        
        # SRT Configuration
        srt_group = QGroupBox("SRT Configuration")
        srt_layout = QVBoxLayout()
        
        # Stream ID
        streamid_layout = QHBoxLayout()
        streamid_layout.addWidget(QLabel("Stream ID:"))
        self.stream_id = QLineEdit()
        self.stream_id.setText("#!::r=scte/scte,m=publish")
        self.stream_id.setPlaceholderText("Enter Stream ID for SRT (e.g., #!::r=scte/scte,m=publish)")
        streamid_layout.addWidget(self.stream_id)
        srt_layout.addLayout(streamid_layout)
        
        # Latency
        latency_layout = QHBoxLayout()
        latency_layout.addWidget(QLabel("Latency (ms):"))
        self.latency = QSpinBox()
        self.latency.setRange(100, 10000)
        self.latency.setValue(2000)
        self.latency.setSuffix(" ms")
        latency_layout.addWidget(self.latency)
        srt_layout.addLayout(latency_layout)
        
        srt_group.setLayout(srt_layout)
        layout.addWidget(srt_group)
        
        # HLS/DASH Output Settings
        hls_dash_group = QGroupBox("HLS/DASH Output Settings (For Local Server)")
        hls_dash_layout = QVBoxLayout()
        
        # CORS Enable
        cors_layout = QHBoxLayout()
        self.enable_cors = QCheckBox("Enable CORS Headers (Required for local web server)")
        self.enable_cors.setChecked(True)
        cors_layout.addWidget(self.enable_cors)
        hls_dash_layout.addLayout(cors_layout)
        
        # Segment Duration
        segment_duration_layout = QHBoxLayout()
        segment_duration_layout.addWidget(QLabel("Segment Duration (seconds):"))
        segment_duration_layout.addStretch()
        self.segment_duration = QSpinBox()
        self.segment_duration.setRange(2, 30)
        self.segment_duration.setValue(6)
        self.segment_duration.setSuffix(" seconds")
        segment_duration_layout.addWidget(self.segment_duration)
        hls_dash_layout.addLayout(segment_duration_layout)
        
        # Playlist Window Size
        playlist_window_layout = QHBoxLayout()
        playlist_window_layout.addWidget(QLabel("Playlist Window Size (segments):"))
        playlist_window_layout.addStretch()
        self.playlist_window = QSpinBox()
        self.playlist_window.setRange(3, 20)
        self.playlist_window.setValue(5)
        playlist_window_layout.addWidget(self.playlist_window)
        hls_dash_layout.addLayout(playlist_window_layout)
        
        hls_dash_group.setLayout(hls_dash_layout)
        layout.addWidget(hls_dash_group)
        
        # SCTE-35 Injection Settings
        injection_group = QGroupBox("SCTE-35 Injection Settings")
        injection_layout = QVBoxLayout()
        
        # Start Delay
        start_delay_layout = QHBoxLayout()
        start_delay_layout.addWidget(QLabel("Start Delay (ms):"))
        self.start_delay = QSpinBox()
        self.start_delay.setRange(0, 10000)
        self.start_delay.setValue(2000)
        self.start_delay.setSuffix(" ms")
        start_delay_layout.addWidget(self.start_delay)
        injection_layout.addLayout(start_delay_layout)
        
        # Inject Count
        inject_count_layout = QHBoxLayout()
        inject_count_layout.addWidget(QLabel("Inject Count:"))
        self.inject_count = QSpinBox()
        self.inject_count.setRange(1, 100000)  # Increased from 1000 to 100000 for long streams
        self.inject_count.setValue(1)
        inject_count_layout.addWidget(self.inject_count)
        injection_layout.addLayout(inject_count_layout)
        
        # Inject Interval
        inject_interval_layout = QHBoxLayout()
        inject_interval_layout.addWidget(QLabel("Inject Interval (ms):"))
        self.inject_interval = QSpinBox()
        self.inject_interval.setRange(100, 60000)
        self.inject_interval.setValue(1000)
        self.inject_interval.setSuffix(" ms")
        inject_interval_layout.addWidget(self.inject_interval)
        injection_layout.addLayout(inject_interval_layout)
        
        injection_group.setLayout(injection_layout)
        layout.addWidget(injection_group)
        
        layout.addStretch()
        scroll.setWidget(scroll_widget)
        
        main_layout = QVBoxLayout()
        main_layout.addWidget(scroll)
        self.setLayout(main_layout)
    
    def on_output_type_changed(self, text):
        """Show/hide output fields based on selected output type"""
        # Hide all output fields and labels
        self.output_srt.setVisible(False)
        self.output_hls.setVisible(False)
        self.output_hls_label.setVisible(False)
        self.output_dash.setVisible(False)
        self.output_dash_label.setVisible(False)
        
        # Show relevant field based on output type
        if text == "SRT":
            self.output_srt.setVisible(True)
        elif text == "HLS":
            self.output_hls_label.setVisible(True)
            self.output_hls.setVisible(True)
        elif text == "DASH":
            self.output_dash_label.setVisible(True)
            self.output_dash.setVisible(True)
        else:
            # For other types (UDP, TCP, HTTP, File), show SRT field as general output
            self.output_srt.setVisible(True)
            if text == "File":
                self.output_srt.setPlaceholderText("Enter output file path")
            elif text in ["UDP", "TCP"]:
                self.output_srt.setPlaceholderText("Enter destination (e.g., 224.1.1.1:9999 or tcp://server:port)")
            else:
                self.output_srt.setPlaceholderText("Enter SRT destination (e.g., cdn.example.com:8888)")
    
    def refresh_profiles(self):
        """Refresh profile list in combo box"""
        if not self.profile_manager:
            return
        
        self.profile_combo.clear()
        profiles = self.profile_manager.get_profile_names()
        if profiles:
            self.profile_combo.addItems(profiles)
    
    def load_selected_profile(self):
        """Load selected profile configuration"""
        if not self.profile_manager:
            return
        
        profile_name = self.profile_combo.currentText().strip()
        if not profile_name:
            return
        
        # Check if it's an existing profile
        if profile_name not in self.profile_manager.get_profile_names():
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.warning(
                self,
                "Profile Not Found",
                f"Profile '{profile_name}' does not exist.\n\nPlease select an existing profile or save a new one first."
            )
            return
        
        config = self.profile_manager.get_profile(profile_name)
        if config:
            self.apply_config(config)
            # Update output directories based on profile name
            self.update_output_paths_for_profile(profile_name)
            print(f"[INFO] Loaded profile: {profile_name}")
    
    def update_output_paths_for_profile(self, profile_name):
        """Update output directories to include profile name"""
        import re
        import os
        # Sanitize profile name for file system (remove invalid characters)
        safe_name = re.sub(r'[<>:"/\\|?*]', '_', profile_name)
        safe_name = safe_name.strip()
        
        # Update HLS output path
        current_hls = self.output_hls.text().strip()
        # Check if path already contains the profile name (avoid duplication)
        if safe_name.lower() in current_hls.lower():
            # Path already contains profile name, keep it
            pass
        elif current_hls.startswith("output/"):
            # Standard output/ path - add profile folder
            self.output_hls.setText(f"output/{safe_name}/hls")
        elif current_hls:
            # Custom path - add profile folder
            base = current_hls.rstrip("/")
            # Check if it ends with /hls or /dash and insert profile name before that
            if current_hls.endswith("/hls"):
                base = base[:-4]  # Remove /hls
                self.output_hls.setText(f"{base}/{safe_name}/hls")
            else:
                self.output_hls.setText(f"{base}/{safe_name}/hls")
        else:
            self.output_hls.setText(f"output/{safe_name}/hls")
        
        # Update DASH output path
        current_dash = self.output_dash.text().strip()
        # Check if path already contains the profile name (avoid duplication)
        if safe_name.lower() in current_dash.lower():
            # Path already contains profile name, keep it
            pass
        elif current_dash.startswith("output/"):
            # Standard output/ path - add profile folder
            self.output_dash.setText(f"output/{safe_name}/dash")
        elif current_dash:
            # Custom path - add profile folder
            base = current_dash.rstrip("/")
            # Check if it ends with /dash and insert profile name before that
            if current_dash.endswith("/dash"):
                base = base[:-5]  # Remove /dash
                self.output_dash.setText(f"{base}/{safe_name}/dash")
            else:
                self.output_dash.setText(f"{base}/{safe_name}/dash")
        else:
            self.output_dash.setText(f"output/{safe_name}/dash")
        
        print(f"[INFO] Updated output paths for profile: {profile_name} -> {safe_name}")
    
    def apply_config(self, config):
        """Apply configuration dictionary to UI fields"""
        # Input settings
        if "input_type" in config:
            index = self.input_type.findText(config["input_type"])
            if index >= 0:
                self.input_type.setCurrentIndex(index)
        
        if "input_url" in config:
            self.input_url.setText(config["input_url"])
        
        # Output settings
        if "output_type" in config:
            index = self.output_type.findText(config["output_type"])
            if index >= 0:
                self.output_type.setCurrentIndex(index)
        
        if "output_srt" in config:
            self.output_srt.setText(config["output_srt"])
        
        if "output_hls" in config:
            self.output_hls.setText(config["output_hls"])
        
        if "output_dash" in config:
            self.output_dash.setText(config["output_dash"])
        
        # Service settings
        if "service_name" in config:
            self.service_name.setText(config["service_name"])
        
        if "provider_name" in config:
            self.provider_name.setText(config["provider_name"])
        
        if "service_id" in config:
            self.service_id.setValue(config["service_id"])
        
        if "vpid" in config:
            self.vpid.setValue(config["vpid"])
        
        if "apid" in config:
            self.apid.setValue(config["apid"])
        
        if "scte35_pid" in config:
            self.scte35_pid.setValue(config["scte35_pid"])
        
        # SRT settings
        if "stream_id" in config:
            self.stream_id.setText(config["stream_id"])
        
        if "latency" in config:
            self.latency.setValue(config["latency"])
        
        # HLS/DASH settings
        if "enable_cors" in config:
            self.enable_cors.setChecked(config["enable_cors"])
        
        if "segment_duration" in config:
            self.segment_duration.setValue(config["segment_duration"])
        
        if "playlist_window" in config:
            self.playlist_window.setValue(config["playlist_window"])
        
        # Injection settings
        if "start_delay" in config:
            self.start_delay.setValue(config["start_delay"])
        
        if "inject_count" in config:
            self.inject_count.setValue(config["inject_count"])
        
        if "inject_interval" in config:
            self.inject_interval.setValue(config["inject_interval"])
        
        # Trigger output type change to show/hide fields
        self.on_output_type_changed(self.output_type.currentText())
    
    def save_current_profile(self):
        """Save current configuration as a profile"""
        if not self.profile_manager:
            return
        
        from PyQt6.QtWidgets import QInputDialog, QMessageBox
        
        # Get profile name from combo box or dialog
        current_text = self.profile_combo.currentText().strip()
        
        if current_text and current_text in self.profile_manager.get_profile_names():
            # Profile exists, ask for overwrite
            name = current_text
        elif current_text:
            # User typed a name in combo box, use it
            name = current_text
        else:
            # Show dialog to get profile name
            name, ok = QInputDialog.getText(
                self,
                "Save Profile",
                "Profile Name:",
                text=f"Profile_{len(self.profile_manager.get_profile_names()) + 1}"
            )
            
            if not ok or not name.strip():
                return
        
        # Get description
        desc, ok = QInputDialog.getText(
            self,
            "Save Profile",
            "Profile Description (optional):",
            text=""
        )
        
        if not ok:
            desc = ""
        
        # Check if profile exists
        if name in self.profile_manager.get_profile_names():
            reply = QMessageBox.question(
                self,
                "Profile Exists",
                f"Profile '{name}' already exists. Overwrite?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            
            if reply != QMessageBox.StandardButton.Yes:
                return
        
        # Update output paths to include profile name before saving
        self.update_output_paths_for_profile(name)
        
        # Get current config (with updated paths)
        config = self.get_config()
        
        # Save profile
        if self.profile_manager.save_profile(name, config, desc):
            self.refresh_profiles()
            # Select the saved profile
            index = self.profile_combo.findText(name)
            if index >= 0:
                self.profile_combo.setCurrentIndex(index)
            QMessageBox.information(self, "Success", f"Profile '{name}' saved successfully!")
        else:
            QMessageBox.warning(self, "Error", "Failed to save profile!")
    
    def delete_selected_profile(self):
        """Delete selected profile"""
        if not self.profile_manager:
            return
        
        profile_name = self.profile_combo.currentText()
        if not profile_name:
            return
        
        from PyQt6.QtWidgets import QMessageBox
        
        reply = QMessageBox.question(
            self,
            "Delete Profile",
            f"Are you sure you want to delete profile '{profile_name}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            if self.profile_manager.delete_profile(profile_name):
                self.refresh_profiles()
                QMessageBox.information(self, "Success", f"Profile '{profile_name}' deleted!")
            else:
                QMessageBox.warning(self, "Error", "Failed to delete profile!")
    
    def get_config(self):
        return {
            "input_type": self.input_type.currentText(),
            "input_url": self.input_url.text(),
            "output_type": self.output_type.currentText(),
            "output_srt": self.output_srt.text(),
            "output_hls": self.output_hls.text(),
            "output_dash": self.output_dash.text(),
            "enable_cors": self.enable_cors.isChecked(),
            "segment_duration": self.segment_duration.value(),
            "playlist_window": self.playlist_window.value(),
            "service_name": self.service_name.text(),
            "provider_name": self.provider_name.text(),
            "service_id": self.service_id.value(),
            "vpid": self.vpid.value(),
            "apid": self.apid.value(),
            "scte35_pid": self.scte35_pid.value(),
            "stream_id": self.stream_id.text(),
            "latency": self.latency.value(),
            "start_delay": self.start_delay.value(),
            "inject_count": self.inject_count.value(),
            "inject_interval": self.inject_interval.value()
        }


class SCTE35Widget(QWidget):
    """SCTE-35 Marker Generation Tool"""
    
    marker_generated = pyqtSignal(str, str)  # Emits XML file path
    
    def __init__(self):
        super().__init__()
        self.setup_ui()
    
    def setup_ui(self):
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_widget = QWidget()
        layout = QVBoxLayout(scroll_widget)
        
        # Title
        title = QLabel("🎬 Generate SCTE-35 Marker")
        title.setStyleSheet("font-size: 20px; font-weight: bold; color: #4CAF50; padding: 10px;")
        layout.addWidget(title)
        
        # Configuration Group
        config_group = QGroupBox("Marker Configuration")
        config_layout = QVBoxLayout()
        
        # Pre-roll Duration
        preroll_layout = QHBoxLayout()
        preroll_layout.addWidget(QLabel("Pre-roll Duration (seconds):"))
        preroll_layout.addStretch()
        self.preroll_duration = QSpinBox()
        self.preroll_duration.setRange(0, 10)
        self.preroll_duration.setValue(2)
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
        
        # Event ID
        event_id_layout = QHBoxLayout()
        event_id_layout.addWidget(QLabel("Event ID:"))
        event_id_layout.addStretch()
        self.event_id = QSpinBox()
        self.event_id.setRange(10000, 99999)
        self.event_id.setValue(10023)
        self.event_id.setMinimumWidth(150)
        event_id_layout.addWidget(self.event_id)
        config_layout.addLayout(event_id_layout)
        
        config_group.setLayout(config_layout)
        layout.addWidget(config_group)
        
        # Manual Cue Options
        cue_group = QGroupBox("Manual Cue Options")
        cue_layout = QVBoxLayout()
        
        # Cue Type
        cue_type_layout = QHBoxLayout()
        cue_type_layout.addWidget(QLabel("Cue Type:"))
        cue_type_layout.addStretch()
        self.cue_type = QComboBox()
        self.cue_type.addItems(["Pre-roll (Program Transition)", "CUE-OUT (Ad Break Start)", "CUE-IN (Ad Break End)", "Time Signal"])
        self.cue_type.setCurrentText("Pre-roll (Program Transition)")
        cue_type_layout.addWidget(self.cue_type)
        cue_layout.addLayout(cue_type_layout)
        
        # Schedule Time (optional)
        schedule_layout = QHBoxLayout()
        schedule_layout.addWidget(QLabel("Schedule Time (HH:MM:SS):"))
        schedule_layout.addStretch()
        from PyQt6.QtWidgets import QTimeEdit
        from PyQt6.QtCore import QTime
        self.schedule_time = QTimeEdit()
        self.schedule_time.setDisplayFormat("HH:mm:ss")
        self.schedule_time.setTime(QTime.currentTime())
        self.schedule_time.setMinimumWidth(150)
        schedule_layout.addWidget(self.schedule_time)
        cue_layout.addLayout(schedule_layout)
        
        # Enable immediate cue
        from PyQt6.QtWidgets import QCheckBox
        self.immediate_cue = QCheckBox("Trigger Cue Immediately (No Schedule)")
        self.immediate_cue.setChecked(True)
        cue_layout.addWidget(self.immediate_cue)
        
        cue_group.setLayout(cue_layout)
        layout.addWidget(cue_group)
        
        # Generate Button
        self.generate_btn = QPushButton("🎯 Generate SCTE-35 Marker")
        self.generate_btn.setStyleSheet("""
            QPushButton { 
                background-color: #4CAF50; 
                color: white; 
                font-weight: bold; 
                padding: 15px; 
                font-size: 16px;
                border-radius: 8px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        self.generate_btn.clicked.connect(self.generate_marker)
        layout.addWidget(self.generate_btn)
        
        layout.addStretch()
        scroll.setWidget(scroll_widget)
        
        main_layout = QVBoxLayout()
        main_layout.addWidget(scroll)
        self.setLayout(main_layout)
    
    def generate_marker(self):
        """Generate SCTE-35 marker XML file with manual cue support"""
        try:
            from datetime import datetime
            import json
            
            # Get parameters
            preroll = self.preroll_duration.value()
            ad_duration = self.ad_duration.value()
            event_id = self.event_id.value()
            cue_type = self.cue_type.currentText()
            schedule_time = self.schedule_time.time() if not self.immediate_cue.isChecked() else None
            immediate = self.immediate_cue.isChecked()
            
            # Create scte35_final directory if it doesn't exist
            markers_dir = Path("scte35_final")
            markers_dir.mkdir(exist_ok=True)
            
            # Generate timestamped filename based on cue type
            timestamp = int(datetime.now().timestamp())
            cue_prefix_map = {
                "Pre-roll (Program Transition)": "preroll",
                "CUE-OUT (Ad Break Start)": "cue_out",
                "CUE-IN (Ad Break End)": "cue_in",
                "Time Signal": "time_signal"
            }
            cue_prefix = cue_prefix_map.get(cue_type, "preroll")
            xml_filename = f"{cue_prefix}_{event_id}_{timestamp}.xml"
            json_filename = f"{cue_prefix}_{event_id}_{timestamp}.json"
            
            xml_path = markers_dir / xml_filename
            json_path = markers_dir / json_filename
            
            # Generate XML marker based on cue type
            # TSDuck requires <tsduck> root with <splice_information_table>
            if cue_type == "Pre-roll (Program Transition)":
                xml_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<tsduck>
    <splice_information_table protocol_version="0" pts_adjustment="0" tier="0xFFF">
        <splice_insert splice_event_id="{event_id}" 
                      splice_event_cancel="false" 
                      out_of_network="true" 
                      splice_immediate="false" 
                      pts_time="{preroll * 90000}" 
                      unique_program_id="1" 
                      avail_num="1" 
                      avails_expected="1">
            <break_duration auto_return="true" duration="{ad_duration * 90000}" />
        </splice_insert>
    </splice_information_table>
</tsduck>'''
            elif cue_type == "CUE-OUT (Ad Break Start)":
                xml_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<tsduck>
    <splice_information_table protocol_version="0" pts_adjustment="0" tier="0xFFF">
        <splice_insert splice_event_id="{event_id}" 
                      splice_event_cancel="false" 
                      out_of_network="true" 
                      splice_immediate="false" 
                      pts_time="0" 
                      unique_program_id="1" 
                      avail_num="1" 
                      avails_expected="1">
            <break_duration auto_return="false" duration="{ad_duration * 90000}" />
        </splice_insert>
    </splice_information_table>
</tsduck>'''
            elif cue_type == "CUE-IN (Ad Break End)":
                xml_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<tsduck>
    <splice_information_table protocol_version="0" pts_adjustment="0" tier="0xFFF">
        <splice_insert splice_event_id="{event_id}" 
                      splice_event_cancel="false" 
                      out_of_network="false" 
                      splice_immediate="true" 
                      pts_time="0" 
                      unique_program_id="1" 
                      avail_num="1" 
                      avails_expected="1">
            <break_duration auto_return="true" duration="0" />
        </splice_insert>
    </splice_information_table>
</tsduck>'''
            else:  # Time Signal
                xml_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<tsduck>
    <splice_information_table protocol_version="0" pts_adjustment="0" tier="0xFFF">
        <splice_time_signal splice_event_id="{event_id}" 
                           splice_event_cancel="false">
            <splice_time pts_time="0" />
        </splice_time_signal>
    </splice_information_table>
</tsduck>'''
            
            # Generate JSON metadata
            schedule_str = schedule_time.toString("HH:mm:ss") if schedule_time and not immediate else "Immediate"
            json_data = {
                "scte35_marker": {
                    "event_id": event_id,
                    "cue_type": cue_type,
                    "preroll_seconds": preroll,
                    "ad_duration_seconds": ad_duration,
                    "schedule_time": schedule_str,
                    "immediate": immediate,
                    "created_at": datetime.now().isoformat()
                }
            }
            
            # Write files
            xml_path.write_text(xml_content, encoding='utf-8')
            json_path.write_text(json.dumps(json_data, indent=2), encoding='utf-8')
            
            print(f"[SUCCESS] Generated SCTE-35 marker: {xml_filename}")
            
            # Emit signal
            self.marker_generated.emit(str(xml_path), str(json_path))
            
            return str(xml_path)
            
        except Exception as e:
            print(f"[ERROR] Failed to generate marker: {e}")
            return None


class MonitoringWidget(QWidget):
    """Monitoring and Console Output"""
    
    def __init__(self):
        super().__init__()
        # Initialize monitoring counters early
        self.scte35_markers_detected = 0
        self.last_scte35_detection = None
        self.setup_ui()
        self.setup_monitoring()
    
    def setup_ui(self):
        layout = QVBoxLayout()
        
        # Create tabs for different monitoring views
        self.monitor_tabs = QTabWidget()
        self.monitor_tabs.setStyleSheet("""
            QTabWidget::pane { border: 1px solid #444; background-color: #2a2a2a; }
            QTabBar::tab { background-color: #3a3a3a; color: white; padding: 8px 16px; }
            QTabBar::tab:selected { background-color: #2196F3; }
        """)
        
        # Console Tab
        from PyQt6.QtWidgets import QTextEdit
        self.console = QTextEdit()
        self.console.setReadOnly(True)
        self.console.setFont(QFont("Courier", 10))
        self.console.setStyleSheet("background-color: #1e1e1e; color: #00ff00; padding: 10px;")
        self.monitor_tabs.addTab(self.console, "📺 Console")
        
        # SCTE-35 Monitoring Tab
        self.scte35_monitor = QTextEdit()
        self.scte35_monitor.setReadOnly(True)
        self.scte35_monitor.setFont(QFont("Courier", 10))
        self.scte35_monitor.setStyleSheet("background-color: #1e1e1e; color: #4CAF50; padding: 10px;")
        self.monitor_tabs.addTab(self.scte35_monitor, "🎬 SCTE-35 Status")
        
        # System Metrics Tab
        from PyQt6.QtWidgets import QLabel
        self.system_metrics = QLabel()
        self.system_metrics.setFont(QFont("Courier", 10))
        self.system_metrics.setStyleSheet("background-color: #1e1e1e; color: #ffffff; padding: 10px;")
        self.monitor_tabs.addTab(self.system_metrics, "⚡ System Metrics")
        
        # Local Web Server Tab
        web_server_widget = QWidget()
        web_server_layout = QVBoxLayout()
        
        self.web_server_status = QLabel()
        self.web_server_status.setFont(QFont("Arial", 12))
        self.web_server_status.setStyleSheet("padding: 10px; border: 2px solid #444; border-radius: 4px;")
        self.web_server_status.setText("🌐 Web Server: Stopped")
        
        self.web_server_url = QLineEdit()
        self.web_server_url.setPlaceholderText("http://localhost:8000")
        self.web_server_url.setText("http://localhost:8000")
        
        self.web_server_port = QSpinBox()
        self.web_server_port.setRange(8000, 9999)
        self.web_server_port.setValue(8000)
        self.web_server_port.setSuffix(" - Port")
        
        self.web_server_path = QLineEdit()
        self.web_server_path.setPlaceholderText("output/hls")
        self.web_server_path.setText("output/hls")
        
        # HLS Link Display
        hls_link_layout = QHBoxLayout()
        hls_link_layout.addWidget(QLabel("📺 HLS Link:"))
        self.hls_link = QLineEdit()
        self.hls_link.setPlaceholderText("http://localhost:8000/stream.m3u8")
        self.hls_link.setReadOnly(True)
        self.hls_link.setStyleSheet("background-color: #3a3a3a; color: #4CAF50; padding: 5px; border: 1px solid #555; border-radius: 4px;")
        hls_copy_btn = QPushButton("📋 Copy")
        hls_copy_btn.setMaximumWidth(60)
        hls_copy_btn.clicked.connect(lambda: self.copy_to_clipboard(self.hls_link.text()))
        hls_link_layout.addWidget(self.hls_link, 1)
        hls_link_layout.addWidget(hls_copy_btn)
        
        # DASH Link Display
        dash_link_layout = QHBoxLayout()
        dash_link_layout.addWidget(QLabel("📡 DASH Link:"))
        self.dash_link = QLineEdit()
        self.dash_link.setPlaceholderText("http://localhost:8000/stream.mpd")
        self.dash_link.setReadOnly(True)
        self.dash_link.setStyleSheet("background-color: #3a3a3a; color: #2196F3; padding: 5px; border: 1px solid #555; border-radius: 4px;")
        dash_copy_btn = QPushButton("📋 Copy")
        dash_copy_btn.setMaximumWidth(60)
        dash_copy_btn.clicked.connect(lambda: self.copy_to_clipboard(self.dash_link.text()))
        dash_link_layout.addWidget(self.dash_link, 1)
        dash_link_layout.addWidget(dash_copy_btn)
        
        # QPushButton and QHBoxLayout already imported at top of file
        self.start_server_btn = QPushButton("▶️ Start Web Server")
        self.start_server_btn.setStyleSheet("background-color: #4CAF50; color: white; padding: 8px; border-radius: 4px;")
        self.stop_server_btn = QPushButton("⏹️ Stop Web Server")
        self.stop_server_btn.setEnabled(False)
        self.stop_server_btn.setStyleSheet("background-color: #f44336; color: white; padding: 8px; border-radius: 4px;")
        
        web_server_layout.addWidget(self.web_server_status)
        web_server_layout.addWidget(QLabel("Server URL:"))
        web_server_layout.addWidget(self.web_server_url)
        web_server_layout.addWidget(QLabel("Port:"))
        web_server_layout.addWidget(self.web_server_port)
        web_server_layout.addWidget(QLabel("Serving Directory:"))
        web_server_layout.addWidget(self.web_server_path)
        web_server_layout.addLayout(hls_link_layout)
        web_server_layout.addLayout(dash_link_layout)
        
        btn_layout = QHBoxLayout()
        btn_layout.addWidget(self.start_server_btn)
        btn_layout.addWidget(self.stop_server_btn)
        web_server_layout.addLayout(btn_layout)
        
        web_server_widget.setLayout(web_server_layout)
        self.monitor_tabs.addTab(web_server_widget, "🌐 Web Server")
        
        layout.addWidget(self.monitor_tabs)
        self.setLayout(layout)
        
        # Web server instance
        self.web_server_process = None
        self.web_server_thread = None
        
        # Reference to main window for accessing config
        self.main_window = None
    
    def setup_monitoring(self):
        """Setup real-time monitoring"""
        # Connect web server buttons
        self.start_server_btn.clicked.connect(self.start_web_server)
        self.stop_server_btn.clicked.connect(self.stop_web_server)
        
        # Connect web server URL changes to update links
        self.web_server_url.textChanged.connect(self.update_stream_links)
        self.web_server_port.valueChanged.connect(self.update_stream_links)
        self.web_server_path.textChanged.connect(self.update_stream_links)
        
        # Connect copy buttons - find buttons after they're added to layout
        # We'll connect them directly in setup_ui instead
        
        # Timer for system metrics updates
        self.metrics_timer = QTimer()
        self.metrics_timer.timeout.connect(self.update_metrics)
        self.metrics_timer.start(1000)  # Update every second
        
        # Initial link update
        self.update_stream_links()
    
    def copy_to_clipboard(self, text):
        """Copy text to clipboard"""
        from PyQt6.QtWidgets import QApplication
        clipboard = QApplication.clipboard()
        clipboard.setText(text)
        print(f"[INFO] Copied to clipboard: {text}")
    
    def update_stream_links(self):
        """Update HLS and DASH stream links based on server settings"""
        try:
            port = self.web_server_port.value()
            base_url = self.web_server_url.text().strip()
            if not base_url:
                base_url = f"http://localhost:{port}"
            elif ":" not in base_url.split("//")[-1]:
                # URL doesn't have port, extract it and use configured port
                if base_url.startswith("http://"):
                    base_url = f"http://localhost:{port}"
                elif base_url.startswith("https://"):
                    base_url = f"https://localhost:{port}"
                else:
                    base_url = f"http://localhost:{port}"
            
            # Always show links pointing to stream.m3u8 and stream.mpd
            # The actual filename will be stream.m3u8 or stream.mpd
            hls_url = f"{base_url}/stream.m3u8"
            dash_url = f"{base_url}/stream.mpd"
            
            self.hls_link.setText(hls_url)
            self.dash_link.setText(dash_url)
            
        except Exception as e:
            print(f"[WARNING] Error updating stream links: {e}")
    
    def start_web_server(self):
        """Start local web server for HLS/DASH content"""
        import subprocess
        import os
        
        port = self.web_server_port.value()
        path = self.web_server_path.text().strip()
        
        if not path:
            self.web_server_status.setText("❌ Error: Please specify serving directory")
            self.web_server_status.setStyleSheet("padding: 10px; border: 2px solid #f44336; border-radius: 4px; background-color: #3a3a3a;")
            return
        
        # Create directory if it doesn't exist
        if not os.path.exists(path):
            try:
                os.makedirs(path, exist_ok=True)
                print(f"[INFO] Created directory: {path}")
                self.web_server_status.setText(f"ℹ️ Directory '{path}' created. Starting server...")
            except Exception as e:
                self.web_server_status.setText(f"❌ Error: Cannot create directory '{path}': {str(e)}")
                self.web_server_status.setStyleSheet("padding: 10px; border: 2px solid #f44336; border-radius: 4px; background-color: #3a3a3a;")
                return
        
        # Start web server using embedded Python HTTP server
        # Use threading to run server in background
        try:
            import http.server
            import socketserver
            import threading
            
            # Check if port is already in use
            import socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            result = sock.connect_ex(('localhost', port))
            sock.close()
            
            if result == 0:
                self.web_server_status.setText(f"❌ Error: Port {port} is already in use")
                self.web_server_status.setStyleSheet("padding: 10px; border: 2px solid #f44336; border-radius: 4px; background-color: #3a3a3a;")
                return
            
            # Create CORS-enabled handler
            class CORSRequestHandler(http.server.SimpleHTTPRequestHandler):
                def end_headers(self):
                    self.send_header('Access-Control-Allow-Origin', '*')
                    self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
                    self.send_header('Access-Control-Allow-Headers', '*')
                    super().end_headers()
                
                def log_message(self, format, *args):
                    # Suppress log messages
                    pass
            
            # Create server in a thread
            def run_server():
                try:
                    os.chdir(path)
                    Handler = CORSRequestHandler
                    with socketserver.TCPServer(("", port), Handler) as httpd:
                        self.web_server_process = httpd
                        httpd.serve_forever()
                except Exception as e:
                    print(f"[ERROR] Web server error: {e}")
            
            # Start server thread
            server_thread = threading.Thread(target=run_server, daemon=True)
            server_thread.start()
            
            # Wait a moment to check if server started
            import time
            time.sleep(0.5)
            
            # Check if server is running
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            result = sock.connect_ex(('localhost', port))
            sock.close()
            
            if result == 0:
                self.web_server_status.setText(f"✅ Web Server: Running on http://localhost:{port}")
                self.web_server_status.setStyleSheet("padding: 10px; border: 2px solid #4CAF50; border-radius: 4px; background-color: #2a3a2a;")
                self.start_server_btn.setEnabled(False)
                self.stop_server_btn.setEnabled(True)
                self.web_server_url.setText(f"http://localhost:{port}")
                # Update stream links when server starts
                self.update_stream_links()
                print(f"[INFO] Web server started on port {port}, serving {path}")
            else:
                self.web_server_status.setText(f"❌ Error: Server failed to start on port {port}")
                self.web_server_status.setStyleSheet("padding: 10px; border: 2px solid #f44336; border-radius: 4px; background-color: #3a3a3a;")
            
        except Exception as e:
            import traceback
            error_msg = str(e)
            print(f"[ERROR] Web server startup error: {error_msg}")
            traceback.print_exc()
            self.web_server_status.setText(f"❌ Error: {error_msg}")
            self.web_server_status.setStyleSheet("padding: 10px; border: 2px solid #f44336; border-radius: 4px; background-color: #3a3a3a;")
    
    def stop_web_server(self):
        """Stop local web server"""
        if self.web_server_process:
            try:
                # If it's a TCPServer object, shutdown it
                if hasattr(self.web_server_process, 'shutdown'):
                    self.web_server_process.shutdown()
                elif hasattr(self.web_server_process, 'terminate'):
                    # If it's a subprocess
                    self.web_server_process.terminate()
                    self.web_server_process.wait(timeout=2)
                else:
                    # Try to kill if it's a process
                    try:
                        self.web_server_process.kill()
                    except:
                        pass
            except Exception as e:
                print(f"[WARNING] Error stopping web server: {e}")
            finally:
                self.web_server_process = None
        
        self.web_server_status.setText("🌐 Web Server: Stopped")
        self.web_server_status.setStyleSheet("padding: 10px; border: 2px solid #444; border-radius: 4px; background-color: #3a3a3a;")
        self.start_server_btn.setEnabled(True)
        self.stop_server_btn.setEnabled(False)
        print("[INFO] Web server stopped")
        
        # SCTE-35 monitoring - DISABLED for now to prevent crashes
        # TODO: Fix SCTE-35 status tab display issue
        self.scte35_timer = QTimer()
        self.scte35_timer.timeout.connect(self.update_scte35_status)
        self.scte35_timer.start(2000)  # Update every 2 seconds
    
    def update_metrics(self):
        """Update system metrics"""
        try:
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=0.1)
            
            # Memory usage
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            memory_used = memory.used / (1024**3)  # GB
            memory_total = memory.total / (1024**3)  # GB
            
            # Disk usage
            disk = psutil.disk_usage('/')
            disk_percent = disk.percent
            disk_used = disk.used / (1024**3)  # GB
            disk_total = disk.total / (1024**3)  # GB
            
            metrics_text = f"""
═══════════════════════════════════════════════════
           SYSTEM METRICS (Real-time)
═══════════════════════════════════════════════════

CPU Usage:      {cpu_percent}%

Memory Usage:   {memory_percent}%
                Used: {memory_used:.2f} GB / {memory_total:.2f} GB

Disk Usage:     {disk_percent}%
                Used: {disk_used:.2f} GB / {disk_total:.2f} GB

═══════════════════════════════════════════════════
"""
            self.system_metrics.setText(metrics_text)
        except Exception as e:
            self.system_metrics.setText(f"Error updating metrics: {e}")
    
    def update_scte35_status(self):
        """Update SCTE-35 monitoring status - TEMPORARILY DISABLED"""
        # Disabled to prevent crashes - will be fixed in future version
        return
        
        try:
            if not hasattr(self, 'scte35_monitor') or not self.scte35_monitor:
                return
                
            from pathlib import Path
            from datetime import datetime
            
            # Try multiple possible paths
            possible_paths = [
                Path("scte35_final"),
                Path("../scte35_final"),
                Path.cwd() / "scte35_final",
                Path.cwd().parent / "scte35_final"
            ]
            
            markers_dir = None
            for path in possible_paths:
                if path.exists():
                    markers_dir = path
                    print(f"[DEBUG] Found markers directory: {markers_dir}")
                    break
            
            if markers_dir is None:
                status = "[ERROR] No markers directory found. Checked: scte35_final, ../scte35_final, and parent directories."
                if self.scte35_monitor:
                    self.scte35_monitor.clear()
                    self.scte35_monitor.insertPlainText(status)
                print(f"[DEBUG] Markers directory not found in any location")
                return
            
            xml_files = list(markers_dir.glob("*.xml"))
            print(f"[DEBUG] Found {len(xml_files)} XML marker files")
            print(f"[DEBUG] Widget exists: {self.scte35_monitor is not None}")
            print(f"[DEBUG] About to set content to widget")
            
            if not xml_files:
                status = f"""[WARNING] No SCTE-35 markers found. Generate markers from the SCTE-35 tab.

Marker Directory: {markers_dir}
Available Paths: {list(markers_dir.glob('*'))}
"""
                self.scte35_monitor.clear()
                self.scte35_monitor.insertPlainText(status)
                print(f"[DEBUG] No XML files found in {markers_dir}")
                print(f"[DEBUG] Directory contents: {list(markers_dir.glob('*'))}")
                return
            
            # Get latest marker
            latest_file = max(xml_files, key=lambda f: f.stat().st_mtime)
            latest_time = datetime.fromtimestamp(latest_file.stat().st_mtime)
            print(f"[DEBUG] Latest marker: {latest_file.name}")
            
            # Show both file-based and stream-based markers
            stream_detected = self.scte35_markers_detected if hasattr(self, 'scte35_markers_detected') else 0
            stream_info = ""
            if stream_detected > 0:
                stream_info = f"""
Markers Detected in Stream: {stream_detected}
Last Detection: {self.last_scte35_detection if hasattr(self, 'last_scte35_detection') and self.last_scte35_detection else 'None'}
"""
            
            status = f"""
═══════════════════════════════════════════════════
          SCTE-35 MARKER STATUS (Real-time)
═══════════════════════════════════════════════════

FILE-BASED MARKERS:
Total Markers:      {len(xml_files)}
Latest Marker:      {latest_file.name}
Last Modified:      {latest_time.strftime('%Y-%m-%d %H:%M:%S')}
Marker Directory:   {markers_dir.absolute()}

───────────────────────────────────────────────────
STREAM MONITORING:{stream_info}
───────────────────────────────────────────────────

[INFO] SCTE-35 monitoring active...
[INFO] Ready to inject markers into stream

═══════════════════════════════════════════════════
"""
            print(f"[DEBUG] Setting content to widget, length: {len(status)} chars")
            print(f"[DEBUG] Content preview: {status[:200]}...")
            self.scte35_monitor.clear()
            self.scte35_monitor.insertPlainText(status)
            print(f"[DEBUG] Content set successfully")
            
            # Force refresh the widget
            self.scte35_monitor.repaint()
            self.scte35_monitor.update()
            
        except Exception as e:
            import traceback
            error_msg = f"""[ERROR] SCTE-35 monitoring error: {e}

Working Directory: {os.getcwd()}
Error Type: {type(e).__name__}
"""
            self.scte35_monitor.setPlainText(error_msg)
            print(f"[ERROR] SCTE-35 Status Error: {e}")
            traceback.print_exc()
            print(f"[DEBUG] Current working directory: {os.getcwd()}")
    
    def append(self, text):
        self.console.append(text)


class UpdateChecker(QThread):
    """Background thread for checking updates"""
    update_available = pyqtSignal(str, str, str)  # version, url, notes
    check_complete = pyqtSignal(bool)  # update available
    
    def __init__(self, current_version):
        super().__init__()
        self.current_version = current_version
        self.api_url = "https://api.github.com/repos/shihan84/Encoder-100/releases/latest"
        self.latest_version = None
        self.download_url = None
        self.release_notes = ""
    
    def run(self):
        """Check for available updates"""
        try:
            import urllib.request
            import json
            
            req = urllib.request.Request(self.api_url)
            req.add_header('User-Agent', 'IBE-100/2.0.4')
            
            with urllib.request.urlopen(req, timeout=10) as response:
                data = json.loads(response.read())
                self.latest_version = data.get('tag_name', '')
                self.download_url = data.get('html_url', '')
                self.release_notes = data.get('body', 'No release notes available.')
                
                # Compare versions (simple string comparison for now)
                if self.latest_version > self.current_version:
                    self.update_available.emit(self.latest_version, self.download_url, self.release_notes)
                    self.check_complete.emit(True)
                else:
                    self.check_complete.emit(False)
                    
        except Exception as e:
            print(f"[INFO] Could not check for updates: {e}")
            self.check_complete.emit(False)


class MainWindow(QMainWindow):
    """Main Application Window"""
    
    def __init__(self):
        super().__init__()
        self.processor = None
        self.latest_marker = None
        self.update_checker = None
        self.streaming_active = False
        self.retry_count = 0
        self.setup_ui()
        self.setup_connections()
        
        # Check for updates 5 seconds after startup
        QTimer.singleShot(5000, self.check_for_updates)
    
    def setup_ui(self):
        self.setWindowTitle("ITAssist Broadcast Encoder - 100 (IBE-100) v2.0.4")
        self.setMinimumSize(800, 600)
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QVBoxLayout()
        
        # Header with Logo
        header_layout = QHBoxLayout()
        
        # Logo
        logo_label = QLabel()
        logo_path = Path("logo.png")
        if logo_path.exists():
            pixmap = QPixmap(str(logo_path))
            scaled_pixmap = pixmap.scaled(50, 50, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            logo_label.setPixmap(scaled_pixmap)
        else:
            logo_label.setText("🏠")
            logo_label.setStyleSheet("font-size: 40px;")
        
        # Title
        title_label = QLabel("ITAssist Broadcast Encoder - 100")
        title_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #4CAF50;")
        
        header_layout.addWidget(logo_label)
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        
        main_layout.addLayout(header_layout)
        
        # Tab widget
        self.tab_widget = QTabWidget()
        self.tab_widget.setStyleSheet("""
            QTabWidget::pane { border: 1px solid #444; background-color: #2a2a2a; }
            QTabBar::tab { background-color: #3a3a3a; color: white; padding: 10px 20px; }
            QTabBar::tab:selected { background-color: #4CAF50; }
        """)
        
        # Stream Configuration Tab
        self.config_widget = StreamConfigWidget()
        self.tab_widget.addTab(self.config_widget, "⚙️ Configuration")
        
        # SCTE-35 Tab
        self.scte35_widget = SCTE35Widget()
        self.tab_widget.addTab(self.scte35_widget, "🎬 SCTE-35")
        
        # Monitoring Tab
        self.monitoring_widget = MonitoringWidget()
        # Set reference to main window so monitoring widget can access config
        self.monitoring_widget.main_window = self
        self.tab_widget.addTab(self.monitoring_widget, "📊 Monitoring")
        
        main_layout.addWidget(self.tab_widget)
        
        # Control Buttons
        control_layout = QHBoxLayout()
        
        self.start_btn = QPushButton("▶️ Start Processing")
        self.start_btn.setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold; padding: 10px;")
        control_layout.addWidget(self.start_btn)
        
        self.stop_btn = QPushButton("⏹️ Stop")
        self.stop_btn.setStyleSheet("background-color: #f44336; color: white; font-weight: bold; padding: 10px;")
        self.stop_btn.setEnabled(False)
        control_layout.addWidget(self.stop_btn)
        
        self.preview_btn = QPushButton("🔍 Preview Command")
        self.preview_btn.setStyleSheet("background-color: #FF9800; color: white; font-weight: bold; padding: 10px;")
        control_layout.addWidget(self.preview_btn)
        
        self.save_btn = QPushButton("💾 Save Config")
        self.save_btn.setStyleSheet("background-color: #2196F3; color: white; font-weight: bold; padding: 10px;")
        control_layout.addWidget(self.save_btn)
        
        self.load_btn = QPushButton("📁 Load Config")
        self.load_btn.setStyleSheet("background-color: #9C27B0; color: white; font-weight: bold; padding: 10px;")
        control_layout.addWidget(self.load_btn)
        
        control_layout.addStretch()
        main_layout.addLayout(control_layout)
        
        # Footer
        footer_layout = QHBoxLayout()
        footer_layout.setContentsMargins(10, 5, 10, 5)
        
        # Left side - Company info
        company_label = QLabel("© 2024 ITAssist Broadcast Solutions | Dubai • Mumbai • Gurugram")
        company_label.setStyleSheet("color: #888; font-size: 10px;")
        footer_layout.addWidget(company_label)
        
        # Right side - Version
        version_label = QLabel("IBE-100 v2.0.4")
        version_label.setStyleSheet("color: #4CAF50; font-size: 11px; font-weight: bold;")
        version_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        footer_layout.addWidget(version_label)
        
        footer_widget = QWidget()
        footer_widget.setLayout(footer_layout)
        footer_widget.setStyleSheet("background-color: #1a1a1a; border-top: 1px solid #444;")
        main_layout.addWidget(footer_widget)
        
        central_widget.setLayout(main_layout)
        self.setStyleSheet("""
            QMainWindow {
                background-color: #1a1a1a;
            }
            QWidget {
                color: #ffffff;
                background-color: #2a2a2a;
            }
            QLineEdit {
                color: #000000;
                background-color: #ffffff;
                border: 2px solid #555;
                border-radius: 4px;
                padding: 5px;
                font-size: 13px;
            }
            QLineEdit:focus {
                border: 2px solid #4CAF50;
            }
            QSpinBox {
                color: #000000;
                background-color: #ffffff;
                border: 2px solid #555;
                border-radius: 4px;
                padding: 5px;
                font-size: 13px;
            }
            QGroupBox {
                border: 2px solid #444;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
                font-weight: bold;
                font-size: 14px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
            QLabel {
                color: #ffffff;
                font-size: 13px;
            }
        """)
    
    def setup_connections(self):
        self.start_btn.clicked.connect(self.start_processing)
        self.stop_btn.clicked.connect(self.stop_processing)
        self.preview_btn.clicked.connect(self.preview_command)
        self.scte35_widget.marker_generated.connect(self.on_marker_generated)
    
    def kill_all_tsduck_bg_processes(self):
        """Force kill all background TSDuck processes - utility method"""
        self.monitoring_widget.append("[INFO] Force killing all background TSDuck processes...")
        killed = kill_all_tsduck_processes()
        if killed > 0:
            self.monitoring_widget.append(f"[INFO] Successfully terminated {killed} TSDuck process(es)")
        else:
            self.monitoring_widget.append("[INFO] No TSDuck processes found")
        return killed
    
    def check_for_updates(self):
        """Check for available updates"""
        if self.update_checker is None:
            self.update_checker = UpdateChecker("2.0.4")
            self.update_checker.update_available.connect(self.show_update_dialog)
            self.update_checker.check_complete.connect(self.on_update_check_complete)
        
        if not self.update_checker.isRunning():
            self.update_checker.start()
    
    def on_update_check_complete(self, update_available):
        """Handle update check completion"""
        if not update_available:
            print("[INFO] Application is up to date")
    
    def show_update_dialog(self, version, url, notes):
        """Show update available dialog"""
        from PyQt6.QtWidgets import QMessageBox, QTextEdit, QPushButton
        
        msg = QMessageBox(self)
        msg.setWindowTitle("🔄 Update Available")
        msg.setIcon(QMessageBox.Icon.Information)
        msg.setText(f"<b>IBE-100 Version {version} is Available!</b>")
        msg.setInformativeText(f"Current version: 2.0.4<br>Latest version: {version}")
        
        # Add release notes
        details = QTextEdit()
        details.setPlainText(notes[:500] if len(notes) > 500 else notes)
        details.setReadOnly(True)
        details.setMaximumHeight(150)
        details.setMaximumWidth(500)
        
        # Custom layout for details
        msg.layout().addWidget(details, 1, 0, 1, msg.layout().columnCount())
        
        # Buttons
        download_btn = msg.addButton("Download Update", QMessageBox.ButtonRole.AcceptRole)
        later_btn = msg.addButton("Later", QMessageBox.ButtonRole.RejectRole)
        msg.setDefaultButton(later_btn)
        
        # Show dialog
        result = msg.exec()
        
        if msg.clickedButton() == download_btn:
            import webbrowser
            webbrowser.open(url)
            print(f"[INFO] Opened download page for version {version}")
    
    def on_marker_generated(self, xml_file: str, json_file: str):
        """Handle marker generation"""
        self.latest_marker = xml_file
        self.monitoring_widget.append(f"[INFO] Marker generated: {xml_file}")
        print(f"[INFO] Latest marker set to: {xml_file}")
    
    def get_latest_marker(self) -> str:
        """Get the latest SCTE-35 marker file - DYNAMIC, NO hardcoded fallback"""
        from pathlib import Path
        from datetime import datetime
        
        # Look for scte35_final directory
        markers_dir = Path("scte35_final")
        
        if not markers_dir.exists():
            return "ERROR: No markers directory found. Generate a marker first."
        
        # Find all XML marker files
        xml_files = list(markers_dir.glob("*.xml"))
        
        if not xml_files:
            return "ERROR: No marker files found. Generate a marker first."
        
        # Get the latest file by modification time
        latest_file = max(xml_files, key=lambda f: f.stat().st_mtime)
        print(f"[INFO] Selected marker: {latest_file.name}")
        
        # Return relative path for TSDuck
        return str(latest_file)
    
    def build_command(self):
        """Build complete TSDuck command with all distributor requirements"""
        config = self.config_widget.get_config()
        marker = self.get_latest_marker()
        
        # Get values from config
        input_type = config.get("input_type", "HLS (HTTP Live Streaming)")
        input_url = config.get("input_url", "https://cdn.example.com/stream/index.m3u8")
        output_type = config.get("output_type", "SRT")
        output_srt = config.get("output_srt", "cdn.example.com:8888")
        output_hls = config.get("output_hls", "output/hls")
        output_dash = config.get("output_dash", "output/dash")
        enable_cors = config.get("enable_cors", True)
        segment_duration = config.get("segment_duration", 6)
        playlist_window = config.get("playlist_window", 5)
        service_id = config.get("service_id", 1)
        service_name = config.get("service_name", "SCTE-35 Stream")
        provider_name = config.get("provider_name", "ITAssist")
        vpid = config.get("vpid", 256)
        apid = config.get("apid", 257)
        scte35_pid = config.get("scte35_pid", 500)
        stream_id = config.get("stream_id", "#!::r=scte/scte,m=publish")
        latency = config.get("latency", 2000)
        start_delay = config.get("start_delay", 2000)
        inject_count = config.get("inject_count", 1)
        inject_interval = config.get("inject_interval", 1000)
        
        # Determine input plugin based on input type
        input_plugin_map = {
            "HLS (HTTP Live Streaming)": "hls",
            "SRT (Secure Reliable Transport)": "srt",
            "UDP (User Datagram Protocol)": "ip",
            "TCP (Transmission Control Protocol)": "tcp",
            "HTTP/HTTPS": "http",
            "DVB": "dvb",
            "ASI": "asi"
        }
        
        input_plugin = input_plugin_map.get(input_type, "hls")
        
        # Start building command
        command = [TSDUCK_PATH]
        
        # For SRT input, we need to parse the URL to extract host, port, and streamid
        if input_type == "SRT (Secure Reliable Transport)":
            # Parse SRT URL: srt://host:port?streamid=...
            # Based on working implementation from old app (enc100.py)
            try:
                # Remove srt:// prefix to get host:port?streamid=...
                clean_url = input_url.replace("srt://", "").replace("srt:", "")
                
                # Split into host:port and streamid
                if "?" in clean_url:
                    host_port = clean_url.split("?")[0]
                    query_part = clean_url.split("?")[1]
                    
                    # Extract streamid if present
                    streamid_param = None
                    if "streamid=" in query_part:
                        streamid_param = query_part.split("streamid=")[1]
                    
                    # Build SRT command like old app: -I srt host:port --transtype live --messageapi --latency 2000
                    command.extend(["-I", "srt", host_port, 
                                   "--transtype", "live",
                                   "--messageapi",
                                   "--latency", "2000"])
                    
                    # Add streamid if present
                    if streamid_param:
                        command.extend(["--streamid", streamid_param])
                else:
                    # No streamid, just host:port
                    command.extend(["-I", "srt", clean_url,
                                   "--transtype", "live",
                                   "--messageapi",
                                   "--latency", "2000"])
            except Exception as e:
                # Fallback - use input as-is with SRT parameters
                clean_url = input_url.replace("srt://", "").replace("srt:", "")
                command.extend(["-I", "srt", clean_url,
                               "--transtype", "live",
                               "--messageapi",
                               "--latency", "2000"])
        else:
            command.extend(["-I", input_plugin, input_url])
        
        # SDT Plugin - Service Description Table
        command.extend(["-P", "sdt",
            "--service", str(service_id),
            "--name", service_name,
            "--provider", provider_name])
        
        # Smart PID Remapping - only remap if needed to avoid conflicts
        # For SRT input, PIDs may already be correct, so check first
        # Skip remapping for SRT input to avoid PID conflict errors
        if input_type != "SRT (Secure Reliable Transport)":
            # Only remap for HLS and other input types that typically use PIDs 211/221
            command.extend(["-P", "remap", f"211={vpid}", f"221={apid}"])
        
        # PMT Plugin - Program Map Table
        command.extend(["-P", "pmt",
            "--service", str(service_id),
            "--add-pid", f"{vpid}/0x1b",  # Video PID
            "--add-pid", f"{apid}/0x0f",  # Audio PID
            "--add-pid", f"{scte35_pid}/0x86"])  # SCTE-35 PID
        
        # SpliceInject Plugin
        command.extend(["-P", "spliceinject",
            "--pid", str(scte35_pid),
            "--pts-pid", str(vpid),
            "--files", marker,
            "--inject-count", str(inject_count),
            "--inject-interval", str(inject_interval),
            "--start-delay", str(start_delay)])
        
        # Add output based on selected output type
        if output_type == "SRT":
            # Build SRT output command
            output_args = ["-O", "srt", "--caller", output_srt, "--latency", str(latency)]
            
            # Only add --streamid if it's not empty
            if stream_id and stream_id.strip():
                output_args.extend(["--streamid", stream_id.strip()])
        elif output_type == "HLS":
            output_args = ["-O", "hls", "--live", output_hls, "--segment-duration", str(segment_duration), "--playlist-window", str(playlist_window)]
            if enable_cors:
                output_args.extend(["--cors", "*"])
        elif output_type == "DASH":
            output_args = ["-O", "hls", "--live", output_dash, "--dash", "--segment-duration", str(segment_duration), "--playlist-window", str(playlist_window)]
            if enable_cors:
                output_args.extend(["--cors", "*"])
        elif output_type == "UDP":
            output_args = ["-O", "ip", output_srt]
        elif output_type == "TCP":
            output_args = ["-O", "tcp", output_srt]
        elif output_type == "HTTP/HTTPS":
            output_args = ["-O", "http", output_srt]
            if enable_cors:
                output_args.extend(["--cors", "*"])
        else:  # File
            output_args = ["-O", "file", output_srt]
        
        command.extend(output_args)
        
        return command
    
    def preview_command(self):
        """Preview the TSDuck command"""
        from PyQt6.QtWidgets import QDialog, QVBoxLayout, QTextEdit, QPushButton
        
        dialog = QDialog(self)
        dialog.setWindowTitle("TSDuck Command Preview")
        dialog.setMinimumSize(600, 400)
        
        layout = QVBoxLayout()
        
        marker = self.get_latest_marker()
        info = QLabel(f"📌 Marker: {marker}\n\nTSDuck Command:")
        info.setStyleSheet("font-weight: bold; color: #4CAF50;")
        layout.addWidget(info)
        
        cmd_text = QTextEdit()
        cmd_text.setReadOnly(True)
        cmd_text.setFont(QFont("Courier", 9))
        cmd_text.setStyleSheet("background-color: #1e1e1e; color: #ffffff; padding: 10px;")
        
        command = self.build_command()
        cmd_text.setText(" ".join(command))
        layout.addWidget(cmd_text)
        
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(dialog.close)
        layout.addWidget(close_btn)
        
        dialog.setLayout(layout)
        dialog.exec()
    
    def start_processing(self):
        """Start processing with TSDuck"""
        import subprocess
        import threading
        
        config = self.config_widget.get_config()
        marker = self.get_latest_marker()
        
        if "ERROR" in marker:
            self.monitoring_widget.append(f"[ERROR] {marker}")
            return
        
        # Kill any existing TSDuck processes before starting
        self.monitoring_widget.append("[INFO] Checking for existing TSDuck processes...")
        killed = kill_all_tsduck_processes()
        if killed > 0:
            self.monitoring_widget.append(f"[INFO] Terminated {killed} existing TSDuck process(es)")
        else:
            self.monitoring_widget.append("[INFO] No existing TSDuck processes found")
        
        self.monitoring_widget.append(f"[INFO] Starting processing...")
        self.monitoring_widget.append(f"[INFO] Using marker: {marker}")
        
        # Create output directories if needed (for HLS/DASH)
        config = self.config_widget.get_config()
        output_type = config.get("output_type", "SRT")
        
        if output_type == "HLS":
            output_path = config.get("output_hls", "output/hls")
            if output_path:
                try:
                    import os
                    os.makedirs(output_path, exist_ok=True)
                    self.monitoring_widget.append(f"[INFO] Created/verified output directory: {output_path}")
                except Exception as e:
                    self.monitoring_widget.append(f"[WARNING] Could not create directory {output_path}: {e}")
        
        elif output_type == "DASH":
            output_path = config.get("output_dash", "output/dash")
            if output_path:
                try:
                    import os
                    os.makedirs(output_path, exist_ok=True)
                    self.monitoring_widget.append(f"[INFO] Created/verified output directory: {output_path}")
                except Exception as e:
                    self.monitoring_widget.append(f"[WARNING] Could not create directory {output_path}: {e}")
        
        command = self.build_command()
        cmd_str = ' '.join(command)
        self.monitoring_widget.append(f"[INFO] TSDuck Command: {cmd_str}")
        
        # Set streaming active flag
        self.streaming_active = True
        self.retry_count = 0
        
        # Start TSDuck process in background thread with auto-reconnect
        def run_tsp_continuous():
            import time
            max_retries = 999  # Effectively unlimited retries
            
            while self.streaming_active and self.retry_count < max_retries:
                try:
                    process = subprocess.Popen(
                        command,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.STDOUT,
                        text=True,
                        bufsize=1,
                        universal_newlines=True,
                        creationflags=subprocess.CREATE_NO_WINDOW if hasattr(subprocess, 'CREATE_NO_WINDOW') else 0
                    )
                    
                    self.processor = process
                    
                    if self.retry_count > 0:
                        self.monitoring_widget.append(f"[INFO] Reconnected - Retry attempt {self.retry_count}")
                        self.retry_count = 0  # Reset counter on successful connection
                    
                    # Read output line by line
                    for line in process.stdout:
                        if not self.streaming_active:
                            break
                            
                        line_text = line.strip()
                        self.monitoring_widget.append(f"[TSDuck] {line_text}")
                        
                        # Detect SCTE-35 markers in stream
                        if any(keyword in line_text.lower() for keyword in ['splice', 'scte', 'cue', 'break', 'ad break']):
                            self.monitoring_widget.scte35_markers_detected += 1
                            self.monitoring_widget.last_scte35_detection = line_text
                            self.monitoring_widget.update_scte35_status()

                    # Process finished
                    process.wait()
                    exit_code = process.returncode
                    self.processor = None
                    
                    if not self.streaming_active:
                        # User stopped manually
                        self.monitoring_widget.append("[INFO] Stream stopped by user")
                        break
                    
                    # Stream stopped unexpectedly - reconnect
                    self.retry_count += 1
                    
                    if exit_code == 0:
                        self.monitoring_widget.append(f"[WARNING] Stream disconnected (exit code: {exit_code}). Reconnecting in 5 seconds...")
                    else:
                        self.monitoring_widget.append(f"[WARNING] Stream error (exit code: {exit_code}). Reconnecting in 5 seconds...")
                    
                    # Wait before reconnecting (with exponential backoff, max 30 seconds)
                    wait_time = min(5 * min(self.retry_count, 6), 30)
                    for i in range(wait_time):
                        if not self.streaming_active:
                            break
                        time.sleep(1)
                    
                except Exception as e:
                    self.monitoring_widget.append(f"[ERROR] Stream error: {e}")
                    if not self.streaming_active:
                        break
                    
                    # Wait before retry
                    self.retry_count += 1
                    wait_time = min(5 * min(self.retry_count, 6), 30)
                    self.monitoring_widget.append(f"[INFO] Retrying in {wait_time} seconds...")
                    for i in range(wait_time):
                        if not self.streaming_active:
                            break
                        time.sleep(1)
        
        # Run in background thread
        thread = threading.Thread(target=run_tsp_continuous, daemon=True)
        thread.start()
        
        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
    
    def stop_processing(self):
        """Stop TSDuck processing"""
        # Set flag to stop continuous streaming
        self.streaming_active = False
        
        if self.processor:
            self.monitoring_widget.append("[INFO] Stopping TSDuck process...")
            try:
                self.processor.terminate()
                self.processor.wait(timeout=5)
            except:
                try:
                    self.processor.kill()
                except:
                    pass
            finally:
                self.processor = None
        
        # Kill all TSDuck processes to ensure clean shutdown
        self.monitoring_widget.append("[INFO] Force killing all TSDuck processes...")
        killed = kill_all_tsduck_processes()
        if killed > 0:
            self.monitoring_widget.append(f"[INFO] Terminated {killed} TSDuck process(es)")
        
        # Reset retry count
        self.retry_count = 0
        self.monitoring_widget.append("[INFO] Processing stopped.")
        
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
