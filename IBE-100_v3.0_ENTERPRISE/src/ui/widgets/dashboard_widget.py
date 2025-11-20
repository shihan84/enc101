"""
Enhanced Dashboard Widget
Comprehensive overview with real-time statistics, status indicators, and quick actions
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QGroupBox, QScrollArea, QGridLayout, QFrame
)
from PyQt6.QtCore import QTimer, Qt
from PyQt6.QtGui import QFont, QColor
from pathlib import Path
from typing import Optional
from datetime import datetime
import time

from ..themes.glassmorphism import GlassmorphicCard
from .modern_stat_card import ModernStatCard
from .modern_button import ModernButton


class StatCard(QFrame):
    """Stat card widget for displaying metrics"""
    
    def __init__(self, title: str, value: str = "N/A", unit: str = "", color: str = "#4CAF50"):
        super().__init__()
        self.color = color
        self.setup_ui(title, value, unit)
    
    def setup_ui(self, title: str, value: str, unit: str):
        """Setup stat card UI"""
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
        
        # Title
        title_label = QLabel(title)
        title_label.setStyleSheet("color: #888; font-size: 12px;")
        layout.addWidget(title_label)
        
        # Value
        value_layout = QHBoxLayout()
        value_label = QLabel(value)
        value_label.setStyleSheet(f"color: {self.color}; font-size: 28px; font-weight: bold;")
        value_layout.addWidget(value_label)
        
        if unit:
            unit_label = QLabel(unit)
            unit_label.setStyleSheet("color: #888; font-size: 14px;")
            value_layout.addWidget(unit_label)
        
        value_layout.addStretch()
        layout.addLayout(value_layout)
    
    def update_value(self, value: str):
        """Update stat value"""
        value_label = self.findChild(QLabel)
        if value_label:
            value_label.setText(value)


class DashboardWidget(QWidget):
    """Enhanced dashboard widget with comprehensive overview"""
    
    def __init__(self, app_framework=None):
        super().__init__()
        self.app = app_framework
        self.monitoring_service = None
        self.stream_service = None
        self.profile_service = None
        self.scte35_service = None
        self.session_repo = None
        
        # Performance optimization: Cache values to avoid unnecessary updates
        self._cached_values = {
            'cpu': None,
            'memory': None,
            'disk': None,
            'stream_status': None,
            'profiles_count': None,
            'markers_count': None,
            'sessions_count': None
        }
        
        if app_framework:
            self.monitoring_service = app_framework.get_service("monitoring")
            self.stream_service = app_framework.get_service("stream")
            self.profile_service = app_framework.get_service("profile")
            self.scte35_service = app_framework.get_service("scte35")
            self.session_repo = app_framework.get_service("session_repo")
        
        self.setup_ui()
        self.setup_timers()
    
    def setup_ui(self):
        """Setup user interface"""
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_widget = QWidget()
        layout = QVBoxLayout(scroll_widget)
        layout.setSpacing(15)
        
        # Title - Modern Styling
        title = QLabel("📊 Dashboard - System Overview")
        title.setStyleSheet("""
            font-size: 28px;
            font-weight: 700;
            color: #818cf8;
            padding: 15px 10px;
            font-family: 'Segoe UI', 'Roboto', sans-serif;
            letter-spacing: 0.5px;
        """)
        layout.addWidget(title)
        
        # Status Indicators Row - Modern Cards
        status_row = QHBoxLayout()
        status_row.setSpacing(15)
        
        # Stream Status Indicator
        self.stream_status_card = self._create_status_card("Stream Status", "Stopped", "#ef4444")
        status_row.addWidget(self.stream_status_card)
        
        # TSDuck Status
        self.tsduck_status_card = self._create_status_card("TSDuck", "Ready", "#10b981")
        status_row.addWidget(self.tsduck_status_card)
        
        # System Health
        self.health_card = self._create_status_card("System Health", "Good", "#10b981")
        status_row.addWidget(self.health_card)
        
        status_row.addStretch()
        layout.addLayout(status_row)
        
        # Statistics Cards Row 1 - Modern Cards
        stats_row1 = QHBoxLayout()
        stats_row1.setSpacing(15)
        
        self.cpu_card = ModernStatCard("CPU Usage", "0", "%", "#3b82f6", "⚡")
        stats_row1.addWidget(self.cpu_card)
        
        self.memory_card = ModernStatCard("Memory Usage", "0", "%", "#f59e0b", "💾")
        stats_row1.addWidget(self.memory_card)
        
        self.disk_card = ModernStatCard("Disk Usage", "0", "%", "#8b5cf6", "💿")
        stats_row1.addWidget(self.disk_card)
        
        stats_row1.addStretch()
        layout.addLayout(stats_row1)
        
        # Statistics Cards Row 2 - Modern Cards
        stats_row2 = QHBoxLayout()
        stats_row2.setSpacing(15)
        
        self.sessions_card = ModernStatCard("Total Sessions", "0", "", "#06b6d4", "📡")
        stats_row2.addWidget(self.sessions_card)
        
        self.profiles_card = ModernStatCard("Profiles", "0", "", "#ec4899", "📋")
        stats_row2.addWidget(self.profiles_card)
        
        self.markers_card = ModernStatCard("SCTE-35 Markers", "0", "", "#fbbf24", "🎬")
        stats_row2.addWidget(self.markers_card)
        
        stats_row2.addStretch()
        layout.addLayout(stats_row2)
        
        # Quick Actions - Modern Buttons
        actions_group = QGroupBox("🚀 Quick Actions")
        actions_group.setStyleSheet("""
            QGroupBox {
                border: 2px solid rgba(148, 163, 184, 0.2);
                border-radius: 12px;
                margin-top: 15px;
                padding-top: 20px;
                font-weight: 600;
                font-size: 14px;
                background-color: rgba(30, 41, 59, 0.5);
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 10px;
                background-color: #0f172a;
                color: #f1f5f9;
            }
        """)
        actions_layout = QHBoxLayout()
        actions_layout.setSpacing(15)
        
        self.quick_start_btn = ModernButton("Quick Start Stream", button_type="success", icon="▶️")
        actions_layout.addWidget(self.quick_start_btn)
        
        self.quick_marker_btn = ModernButton("Generate Marker", button_type="info", icon="🎬")
        actions_layout.addWidget(self.quick_marker_btn)
        
        self.view_logs_btn = ModernButton("View Logs", button_type="warning", icon="📋")
        actions_layout.addWidget(self.view_logs_btn)
        
        actions_layout.addStretch()
        actions_group.setLayout(actions_layout)
        layout.addWidget(actions_group)
        
        # Recent Activity - Glassmorphic Card
        activity_group = QGroupBox("📈 Recent Activity")
        activity_group.setStyleSheet("""
            QGroupBox {
                border: 2px solid rgba(148, 163, 184, 0.2);
                border-radius: 12px;
                margin-top: 15px;
                padding-top: 20px;
                font-weight: 600;
                font-size: 14px;
                background-color: rgba(30, 41, 59, 0.5);
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 10px;
                background-color: #0f172a;
                color: #f1f5f9;
            }
        """)
        activity_layout = QVBoxLayout()
        
        self.activity_label = QLabel("No recent activity")
        self.activity_label.setStyleSheet("""
            color: #cbd5e1;
            padding: 15px;
            font-size: 13px;
            background-color: rgba(15, 23, 42, 0.5);
            border-radius: 8px;
        """)
        self.activity_label.setWordWrap(True)
        activity_layout.addWidget(self.activity_label)
        
        activity_group.setLayout(activity_layout)
        layout.addWidget(activity_group)
        
        # System Information - Glassmorphic Card
        info_group = QGroupBox("ℹ️ System Information")
        info_group.setStyleSheet("""
            QGroupBox {
                border: 2px solid rgba(148, 163, 184, 0.2);
                border-radius: 12px;
                margin-top: 15px;
                padding-top: 20px;
                font-weight: 600;
                font-size: 14px;
                background-color: rgba(30, 41, 59, 0.5);
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 10px;
                background-color: #0f172a;
                color: #f1f5f9;
            }
        """)
        info_layout = QVBoxLayout()
        
        self.info_label = QLabel()
        self.info_label.setStyleSheet("""
            color: #cbd5e1;
            padding: 15px;
            font-family: 'Consolas', 'Courier New', monospace;
            font-size: 12px;
            background-color: rgba(15, 23, 42, 0.5);
            border-radius: 8px;
            line-height: 1.6;
        """)
        self.info_label.setWordWrap(True)
        info_layout.addWidget(self.info_label)
        
        info_group.setLayout(info_layout)
        layout.addWidget(info_group)
        
        layout.addStretch()
        scroll.setWidget(scroll_widget)
        
        main_layout = QVBoxLayout(self)
        main_layout.addWidget(scroll)
    
    def _create_status_card(self, title: str, status: str, color: str) -> QFrame:
        """Create modern status indicator card with glassmorphism"""
        card = GlassmorphicCard(opacity=0.8)
        card.setMinimumWidth(160)
        card.setFixedHeight(100)
        
        layout = QVBoxLayout(card)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(8)
        
        title_label = QLabel(title)
        title_label.setStyleSheet("""
            color: #cbd5e1;
            font-size: 11px;
            font-weight: 500;
            letter-spacing: 0.5px;
        """)
        layout.addWidget(title_label)
        
        status_label = QLabel(status)
        status_label.setStyleSheet(f"""
            color: {color};
            font-size: 20px;
            font-weight: 700;
            font-family: 'Segoe UI', sans-serif;
        """)
        status_label.setObjectName("status_label")
        layout.addWidget(status_label)
        
        layout.addStretch()
        
        return card
    
    def setup_timers(self):
        """Setup update timers with optimized intervals"""
        # Update timer - every 1.5 seconds for smoother updates
        self.update_timer = QTimer()
        self.update_timer.setSingleShot(False)
        self.update_timer.timeout.connect(self._update_dashboard)
        self.update_timer.start(1500)  # Update every 1.5 seconds
        
        # Initial update after a short delay
        QTimer.singleShot(100, self._update_dashboard)
    
    def _update_dashboard(self):
        """Update dashboard with latest data - optimized with caching"""
        try:
            # Update system metrics (only if changed)
            if self.monitoring_service:
                metrics = self.monitoring_service.get_system_metrics()
                if metrics:
                    cpu = metrics.get('cpu', {}).get('percent', 0)
                    memory = metrics.get('memory', {}).get('percent', 0)
                    disk = metrics.get('disk', {}).get('percent', 0)
                    
                    # Only update if value changed (performance optimization)
                    if self._cached_values['cpu'] != cpu and hasattr(self, 'cpu_card') and self.cpu_card:
                        self.cpu_card.update_value(f"{cpu:.1f}")
                        self._cached_values['cpu'] = cpu
                    
                    if self._cached_values['memory'] != memory and hasattr(self, 'memory_card') and self.memory_card:
                        self.memory_card.update_value(f"{memory:.1f}")
                        self._cached_values['memory'] = memory
                    
                    if self._cached_values['disk'] != disk and hasattr(self, 'disk_card') and self.disk_card:
                        self.disk_card.update_value(f"{disk:.1f}")
                        self._cached_values['disk'] = disk
                    
                    # Update health status
                    max_usage = max(cpu, memory, disk)
                    health_status = "Critical" if max_usage > 90 else "Warning" if max_usage > 70 else "Good"
                    health_color = "#f44336" if max_usage > 90 else "#FF9800" if max_usage > 70 else "#4CAF50"
                    self._update_status_card(self.health_card, health_status, health_color)
            
            # Update stream status (only if changed)
            if self.stream_service:
                is_running = self.stream_service.is_running
                session = self.stream_service.get_current_session()
                new_status = "Running" if (is_running and session) else "Stopped"
                new_color = "#4CAF50" if (is_running and session) else "#f44336"
                
                if self._cached_values['stream_status'] != new_status:
                    self._update_status_card(self.stream_status_card, new_status, new_color)
                    self._cached_values['stream_status'] = new_status
            
            # Update profiles count (cache to avoid repeated calls)
            if self.profile_service and hasattr(self, 'profiles_card') and self.profiles_card:
                try:
                    profiles = self.profile_service.get_profile_names()
                    count = len(profiles)
                    if self._cached_values['profiles_count'] != count:
                        self.profiles_card.update_value(str(count))
                        self._cached_values['profiles_count'] = count
                except:
                    pass
            
            # Update markers count (cache to avoid repeated file system calls)
            if self.scte35_service and hasattr(self, 'markers_card') and self.markers_card:
                try:
                    markers_dir = Path("scte35_final")
                    if markers_dir.exists():
                        markers = list(markers_dir.glob("*.xml"))
                        count = len(markers)
                        if self._cached_values['markers_count'] != count:
                            self.markers_card.update_value(str(count))
                            self._cached_values['markers_count'] = count
                except:
                    pass
            
            # Update sessions count (cache to avoid repeated DB queries)
            if self.session_repo and hasattr(self, 'sessions_card') and self.sessions_card:
                try:
                    recent_sessions = self.session_repo.get_recent_sessions(limit=100)
                    count = len(recent_sessions)
                    if self._cached_values['sessions_count'] != count:
                        self.sessions_card.update_value(str(count))
                        self._cached_values['sessions_count'] = count
                except:
                    pass
            
            # Update recent activity (less frequent - every 5 seconds)
            if not hasattr(self, '_last_activity_update'):
                self._last_activity_update = 0
            if time.time() - self._last_activity_update > 5:
                self._update_recent_activity()
                self._last_activity_update = time.time()
            
            # Update system info (less frequent - every 10 seconds)
            if not hasattr(self, '_last_info_update'):
                self._last_info_update = 0
            if time.time() - self._last_info_update > 10:
                self._update_system_info()
                self._last_info_update = time.time()
            
        except Exception as e:
            print(f"[ERROR] Dashboard update error: {e}")
    
    def _update_status_card(self, card: QFrame, status: str, color: str):
        """Update status card"""
        status_label = card.findChild(QLabel, "status_label")
        if status_label:
            status_label.setText(status)
            status_label.setStyleSheet(f"""
                color: {color};
                font-size: 20px;
                font-weight: 700;
                font-family: 'Segoe UI', sans-serif;
            """)
    
    def _update_recent_activity(self):
        """Update recent activity display"""
        activities = []
        
        # Check for recent sessions
        if self.session_repo:
            try:
                recent = self.session_repo.get_recent_sessions(limit=3)
                for session in recent:
                    status_icon = "▶️" if session.status == "running" else "⏹️"
                    activities.append(f"{status_icon} Session {session.session_id[:8]}... - {session.status}")
            except:
                pass
        
        # Check for recent markers
        markers_dir = Path("scte35_final")
        if markers_dir.exists():
            markers = sorted(markers_dir.glob("*.xml"), key=lambda p: p.stat().st_mtime, reverse=True)[:3]
            for marker in markers:
                mtime = datetime.fromtimestamp(marker.stat().st_mtime)
                activities.append(f"🎬 Marker: {marker.name} - {mtime.strftime('%H:%M:%S')}")
        
        if activities:
            self.activity_label.setText("\n".join(activities))
            self.activity_label.setStyleSheet("color: #4CAF50; padding: 10px;")
        else:
            self.activity_label.setText("No recent activity")
            self.activity_label.setStyleSheet("color: #888; padding: 10px;")
    
    def _update_system_info(self):
        """Update system information"""
        info_lines = []
        
        if self.app:
            config = self.app.config
            info_lines.append(f"Application: {config.app_name} v{config.app_version}")
            info_lines.append(f"TSDuck: {config.tsduck_path or 'Auto-detected'}")
            if config.api_enabled:
                info_lines.append(f"API: http://{config.api_host}:{config.api_port}")
            else:
                info_lines.append("API: Disabled")
        
        info_lines.append(f"Logs Directory: logs/")
        info_lines.append(f"Database: database/sessions.db")
        info_lines.append(f"Profiles: profiles/")
        info_lines.append(f"Markers: scte35_final/")
        
        self.info_label.setText("\n".join(info_lines))
    
    def set_quick_action_callbacks(self, start_callback, marker_callback, logs_callback):
        """Set callbacks for quick action buttons"""
        if start_callback:
            self.quick_start_btn.clicked.connect(start_callback)
        if marker_callback:
            self.quick_marker_btn.clicked.connect(marker_callback)
        if logs_callback:
            self.view_logs_btn.clicked.connect(logs_callback)
