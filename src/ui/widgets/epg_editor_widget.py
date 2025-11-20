"""
EPG Editor Widget
Electronic Program Guide editor and management
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QTextEdit,
    QGroupBox, QLineEdit, QSpinBox, QFormLayout, QDateTimeEdit,
    QComboBox, QFileDialog, QMessageBox, QTabWidget, QSplitter,
    QCheckBox, QDoubleSpinBox, QListWidget, QDialog, QDialogButtonBox,
    QDateEdit
)
from PyQt6.QtCore import QTimer, Qt, pyqtSignal, QDateTime
from PyQt6.QtGui import QFont, QColor
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, List
from src.services.epg_service import EPGService, EPGEvent, EPGServiceInfo


class EPGEditorWidget(QWidget):
    """Widget for EPG/EIT editing and management - Enhanced Version"""
    
    epg_generated = pyqtSignal(object)  # Emits Path to EIT file
    
    def __init__(self, epg_service: Optional[EPGService] = None):
        super().__init__()
        self.epg_service = epg_service
        self.events: List[EPGEvent] = []
        self.filtered_events: List[EPGEvent] = []
        self.selected_events: List[EPGEvent] = []
        self._editing_event: Optional[EPGEvent] = None
        self.setup_ui()
    
    def setup_ui(self):
        """Setup user interface - redesigned to be less congested"""
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(5)
        main_layout.setContentsMargins(5, 5, 5, 5)
        
        # Top Control Bar - Compact
        control_bar = QHBoxLayout()
        
        # Service Info - Compact inline
        service_layout = QHBoxLayout()
        service_layout.addWidget(QLabel("Service ID:"))
        self.service_id = QSpinBox()
        self.service_id.setRange(1, 65535)
        self.service_id.setValue(1)
        self.service_id.setMaximumWidth(80)
        self.service_id.setStyleSheet("padding: 3px;")
        service_layout.addWidget(self.service_id)
        
        service_layout.addWidget(QLabel("Name:"))
        self.service_name = QLineEdit()
        self.service_name.setPlaceholderText("Service name")
        self.service_name.setMaximumWidth(150)
        self.service_name.setStyleSheet("padding: 3px;")
        service_layout.addWidget(self.service_name)
        
        service_layout.addWidget(QLabel("Provider:"))
        self.provider_name = QLineEdit()
        self.provider_name.setPlaceholderText("Provider")
        self.provider_name.setMaximumWidth(120)
        self.provider_name.setStyleSheet("padding: 3px;")
        service_layout.addWidget(self.provider_name)
        
        service_layout.addStretch()
        control_bar.addLayout(service_layout)
        
        # Action Buttons - Compact
        self.import_btn = QPushButton("📥 Import")
        self.import_btn.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                font-weight: bold;
                padding: 6px 12px;
                border-radius: 4px;
            }
            QPushButton:hover { background-color: #1976D2; }
        """)
        self.import_btn.clicked.connect(self._import_xmltv)
        control_bar.addWidget(self.import_btn)
        
        self.export_btn = QPushButton("📤 Export")
        self.export_btn.setStyleSheet("""
            QPushButton {
                background-color: #8b5cf6;
                color: white;
                font-weight: bold;
                padding: 6px 12px;
                border-radius: 4px;
            }
            QPushButton:hover { background-color: #7c3aed; }
        """)
        self.export_btn.clicked.connect(self._export_epg)
        control_bar.addWidget(self.export_btn)
        
        self.generate_btn = QPushButton("🎬 Generate EIT")
        self.generate_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                font-weight: bold;
                padding: 6px 12px;
                border-radius: 4px;
            }
            QPushButton:hover { background-color: #45a049; }
        """)
        self.generate_btn.clicked.connect(self._generate_eit)
        control_bar.addWidget(self.generate_btn)
        
        main_layout.addLayout(control_bar)
        
        # Use Splitter for better space management
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Left Panel - Event Editor (Collapsible)
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(5, 5, 5, 5)
        
        event_group = QGroupBox("📅 Event Editor")
        event_group.setStyleSheet("""
            QGroupBox {
                border: 2px solid rgba(148, 163, 184, 0.2);
                border-radius: 6px;
                margin-top: 8px;
                padding-top: 12px;
                font-weight: 600;
                font-size: 11px;
            }
        """)
        event_layout = QFormLayout()
        event_layout.setSpacing(6)
        
        # Compact form fields
        self.event_id = QSpinBox()
        self.event_id.setRange(1, 65535)
        self.event_id.setValue(1)
        self.event_id.setStyleSheet("padding: 4px;")
        event_layout.addRow("Event ID:", self.event_id)
        
        self.event_title = QLineEdit()
        self.event_title.setPlaceholderText("Event title")
        self.event_title.setStyleSheet("padding: 4px;")
        event_layout.addRow("Title:", self.event_title)
        
        self.event_description = QTextEdit()
        self.event_description.setPlaceholderText("Description (optional)")
        self.event_description.setMaximumHeight(50)
        self.event_description.setStyleSheet("padding: 4px; font-size: 10px;")
        event_layout.addRow("Description:", self.event_description)
        
        self.event_start = QDateTimeEdit()
        self.event_start.setDateTime(QDateTime.currentDateTime())
        self.event_start.setCalendarPopup(True)
        self.event_start.setStyleSheet("padding: 4px;")
        event_layout.addRow("Start:", self.event_start)
        
        duration_layout = QHBoxLayout()
        self.event_duration = QSpinBox()
        self.event_duration.setRange(1, 86400)
        self.event_duration.setValue(3600)
        self.event_duration.setStyleSheet("padding: 4px;")
        duration_layout.addWidget(self.event_duration)
        duration_layout.addWidget(QLabel("seconds"))
        duration_layout.addStretch()
        event_layout.addRow("Duration:", duration_layout)
        
        self.content_type = QComboBox()
        self.content_type.addItems([
            "0x10 - Movie/Drama", "0x20 - News", "0x30 - Show",
            "0x40 - Sports", "0x50 - Children", "0x60 - Music",
            "0x70 - Arts", "0x80 - Social", "0x90 - Education", "0xA0 - Leisure"
        ])
        self.content_type.setStyleSheet("padding: 4px; font-size: 10px;")
        event_layout.addRow("Type:", self.content_type)
        
        # Extended fields (collapsible)
        self.extended_group = QGroupBox("Extended Info (Optional)")
        self.extended_group.setCheckable(True)
        self.extended_group.setChecked(False)
        extended_layout = QFormLayout()
        extended_layout.setSpacing(4)
        
        self.director = QLineEdit()
        self.director.setPlaceholderText("Director name")
        extended_layout.addRow("Director:", self.director)
        
        self.actors_list = QListWidget()
        self.actors_list.setMaximumHeight(60)
        actors_btn_layout = QHBoxLayout()
        self.add_actor_btn = QPushButton("+")
        self.add_actor_btn.setMaximumWidth(30)
        self.add_actor_btn.clicked.connect(self._add_actor)
        actors_btn_layout.addWidget(self.add_actor_btn)
        self.remove_actor_btn = QPushButton("-")
        self.remove_actor_btn.setMaximumWidth(30)
        self.remove_actor_btn.clicked.connect(self._remove_actor)
        actors_btn_layout.addWidget(self.remove_actor_btn)
        actors_btn_layout.addStretch()
        extended_layout.addRow("Actors:", self.actors_list)
        extended_layout.addRow("", actors_btn_layout)
        
        self.year = QSpinBox()
        self.year.setRange(1900, 2100)
        self.year.setValue(0)
        extended_layout.addRow("Year:", self.year)
        
        self.star_rating = QDoubleSpinBox()
        self.star_rating.setRange(0.0, 10.0)
        self.star_rating.setSingleStep(0.1)
        extended_layout.addRow("Rating:", self.star_rating)
        
        self.parental_rating = QSpinBox()
        self.parental_rating.setRange(0, 18)
        extended_layout.addRow("Parental:", self.parental_rating)
        
        self.language = QLineEdit()
        self.language.setText("eng")
        extended_layout.addRow("Language:", self.language)
        
        self.category = QLineEdit()
        extended_layout.addRow("Category:", self.category)
        
        self.season = QSpinBox()
        self.season.setRange(0, 100)
        extended_layout.addRow("Season:", self.season)
        
        self.episode = QSpinBox()
        self.episode.setRange(0, 1000)
        extended_layout.addRow("Episode:", self.episode)
        
        self.episode_title = QLineEdit()
        extended_layout.addRow("Ep. Title:", self.episode_title)
        
        self.extended_group.setLayout(extended_layout)
        event_layout.addRow("", self.extended_group)
        
        btn_layout = QHBoxLayout()
        self.add_btn = QPushButton("➕ Add")
        self.add_btn.setStyleSheet("""
            QPushButton {
                background-color: #10b981;
                color: white;
                font-weight: bold;
                padding: 6px 15px;
                border-radius: 4px;
            }
            QPushButton:hover { background-color: #059669; }
        """)
        self.add_btn.clicked.connect(self._add_event)
        btn_layout.addWidget(self.add_btn)
        
        self.update_btn = QPushButton("✏️ Update")
        self.update_btn.setStyleSheet("""
            QPushButton {
                background-color: #f59e0b;
                color: white;
                font-weight: bold;
                padding: 6px 15px;
                border-radius: 4px;
            }
            QPushButton:hover { background-color: #d97706; }
        """)
        self.update_btn.setEnabled(False)
        self.update_btn.clicked.connect(self._update_event)
        btn_layout.addWidget(self.update_btn)
        
        self.recurring_btn = QPushButton("🔄 Recurring")
        self.recurring_btn.setStyleSheet("""
            QPushButton {
                background-color: #3b82f6;
                color: white;
                font-weight: bold;
                padding: 6px 15px;
                border-radius: 4px;
            }
            QPushButton:hover { background-color: #2563eb; }
        """)
        self.recurring_btn.clicked.connect(self._create_recurring)
        btn_layout.addWidget(self.recurring_btn)
        
        btn_layout.addStretch()
        event_layout.addRow("", btn_layout)
        
        event_group.setLayout(event_layout)
        left_layout.addWidget(event_group)
        left_layout.addStretch()
        
        splitter.addWidget(left_panel)
        splitter.setStretchFactor(0, 0)
        splitter.setSizes([300, 700])
        
        # Right Panel - Events Table with Search/Filter
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(5, 5, 5, 5)
        
        # Search and Filter Bar
        search_bar = QHBoxLayout()
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Search events...")
        self.search_input.textChanged.connect(self._on_search)
        search_bar.addWidget(self.search_input)
        
        self.filter_type = QComboBox()
        self.filter_type.addItems(["All Types", "Movie", "News", "Show", "Sports", "Children", "Music"])
        self.filter_type.currentTextChanged.connect(self._on_filter)
        search_bar.addWidget(self.filter_type)
        
        self.validate_btn = QPushButton("✓ Validate")
        self.validate_btn.setStyleSheet("background-color: #10b981; color: white; padding: 6px 12px; border-radius: 4px;")
        self.validate_btn.clicked.connect(self._validate_schedule)
        search_bar.addWidget(self.validate_btn)
        
        self.bulk_delete_btn = QPushButton("🗑️ Delete Selected")
        self.bulk_delete_btn.setStyleSheet("background-color: #ef4444; color: white; padding: 6px 12px; border-radius: 4px;")
        self.bulk_delete_btn.setEnabled(False)
        self.bulk_delete_btn.clicked.connect(self._bulk_delete)
        search_bar.addWidget(self.bulk_delete_btn)
        
        self.bulk_copy_btn = QPushButton("📋 Copy Selected")
        self.bulk_copy_btn.setStyleSheet("background-color: #3b82f6; color: white; padding: 6px 12px; border-radius: 4px;")
        self.bulk_copy_btn.setEnabled(False)
        self.bulk_copy_btn.clicked.connect(self._bulk_copy)
        search_bar.addWidget(self.bulk_copy_btn)
        
        right_layout.addLayout(search_bar)
        
        # Events Table
        events_group = QGroupBox("📋 EPG Events")
        events_group.setStyleSheet("""
            QGroupBox {
                border: 2px solid rgba(148, 163, 184, 0.2);
                border-radius: 6px;
                margin-top: 8px;
                padding-top: 12px;
                font-weight: 600;
                font-size: 11px;
            }
        """)
        events_layout = QVBoxLayout()
        
        self.events_table = QTableWidget()
        self.events_table.setColumnCount(8)
        self.events_table.setHorizontalHeaderLabels([
            "", "ID", "Title", "Start Time", "Duration", "Type", "Rating", "Actions"
        ])
        self.events_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.events_table.setSelectionMode(QTableWidget.SelectionMode.ExtendedSelection)
        self.events_table.itemSelectionChanged.connect(self._on_selection_changed)
        self.events_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.events_table.setAlternatingRowColors(True)
        self.events_table.setStyleSheet("""
            QTableWidget {
                background-color: #1e1e1e;
                color: #ffffff;
                gridline-color: #444;
                font-size: 10px;
            }
            QTableWidget::item {
                padding: 4px;
            }
            QHeaderView::section {
                background-color: #2a2a2a;
                color: #ffffff;
                padding: 6px;
                font-weight: bold;
                border: 1px solid #444;
                font-size: 10px;
            }
        """)
        events_layout.addWidget(self.events_table)
        events_group.setLayout(events_layout)
        right_layout.addWidget(events_group)
        
        # Status Log - Compact
        self.status_log = QTextEdit()
        self.status_log.setReadOnly(True)
        self.status_log.setFont(QFont("Courier", 8))
        self.status_log.setMaximumHeight(80)
        self.status_log.setStyleSheet("""
            QTextEdit {
                background-color: #1e1e1e;
                color: #00ff00;
                padding: 5px;
                border: 1px solid #444;
                font-size: 9px;
            }
        """)
        right_layout.addWidget(self.status_log)
        
        splitter.addWidget(right_panel)
        splitter.setStretchFactor(1, 1)
        
        main_layout.addWidget(splitter)
    
    def _add_actor(self):
        """Add actor to list"""
        actor, ok = QMessageBox.getText(self, "Add Actor", "Actor name:")
        if ok and actor:
            self.actors_list.addItem(actor)
    
    def _remove_actor(self):
        """Remove selected actor"""
        current = self.actors_list.currentItem()
        if current:
            self.actors_list.takeItem(self.actors_list.row(current))
    
    def _on_search(self, text):
        """Handle search"""
        if not text:
            self.filtered_events = self.events
        else:
            self.filtered_events = self.epg_service.search_events(self.events, text) if self.epg_service else []
        self._update_events_table()
    
    def _on_filter(self, text):
        """Handle filter"""
        content_type_map = {
            "Movie": "0x10", "News": "0x20", "Show": "0x30",
            "Sports": "0x40", "Children": "0x50", "Music": "0x60"
        }
        content_type = content_type_map.get(text)
        if content_type:
            self.filtered_events = self.epg_service.filter_events(
                self.events, content_type=content_type
            ) if self.epg_service else []
        else:
            self.filtered_events = self.events
        self._update_events_table()
    
    def _on_selection_changed(self):
        """Handle table selection"""
        selected = self.events_table.selectedItems()
        if selected:
            rows = set(item.row() for item in selected)
            self.selected_events = [self.filtered_events[row] for row in rows if row < len(self.filtered_events)]
            self.bulk_delete_btn.setEnabled(len(self.selected_events) > 0)
            self.bulk_copy_btn.setEnabled(len(self.selected_events) > 0)
        else:
            self.selected_events = []
            self.bulk_delete_btn.setEnabled(False)
            self.bulk_copy_btn.setEnabled(False)
    
    def _add_event(self):
        """Add event to EPG"""
        try:
            event = self._get_event_from_form()
            if not event:
                return
            
            # Validate
            if self.epg_service:
                valid, errors = self.epg_service.validate_event(event)
                if not valid:
                    QMessageBox.warning(self, "Validation Error", "\n".join(errors))
                    return
            
            self.events.append(event)
            self.filtered_events = self.events
            self._update_events_table()
            self._clear_form()
            self.status_log.append(f"[INFO] Added event: {event.title}")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to add event: {e}")
            self.status_log.append(f"[ERROR] Failed to add event: {e}")
    
    def _get_event_from_form(self) -> Optional[EPGEvent]:
        """Get event from form"""
        title = self.event_title.text().strip()
        if not title:
            QMessageBox.warning(self, "Warning", "Title is required")
            return None
        
        actors = [self.actors_list.item(i).text() for i in range(self.actors_list.count())]
        
        event = EPGEvent(
            event_id=self.event_id.value(),
            title=title,
            description=self.event_description.toPlainText(),
            start_time=self.event_start.dateTime().toPyDateTime(),
            duration=self.event_duration.value(),
            content_type=self.content_type.currentText().split(" - ")[0],
            director=self.director.text() if self.extended_group.isChecked() else "",
            actors=actors if self.extended_group.isChecked() else [],
            year=self.year.value() if self.extended_group.isChecked() and self.year.value() > 0 else 0,
            star_rating=self.star_rating.value() if self.extended_group.isChecked() else 0.0,
            parental_rating=self.parental_rating.value() if self.extended_group.isChecked() else 0,
            language=self.language.text() or "eng",
            category=self.category.text() if self.extended_group.isChecked() else "",
            season_number=self.season.value() if self.extended_group.isChecked() else 0,
            episode_number=self.episode.value() if self.extended_group.isChecked() else 0,
            episode_title=self.episode_title.text() if self.extended_group.isChecked() else ""
        )
        return event
    
    def _clear_form(self):
        """Clear form"""
        self.event_id.setValue(max([e.event_id for e in self.events], default=0) + 1)
        self.event_title.clear()
        self.event_description.clear()
        self.event_duration.setValue(3600)
        if self.extended_group.isChecked():
            self.director.clear()
            self.actors_list.clear()
            self.year.setValue(0)
            self.star_rating.setValue(0.0)
            self.parental_rating.setValue(0)
            self.category.clear()
            self.season.setValue(0)
            self.episode.setValue(0)
            self.episode_title.clear()
    
    def _update_event(self):
        """Update existing event"""
        if not self._editing_event:
            return
        
        event = self._get_event_from_form()
        if not event:
            return
        
        idx = self.events.index(self._editing_event)
        self.events[idx] = event
        self.filtered_events = self.events
        self._update_events_table()
        self._clear_form()
        self._editing_event = None
        self.update_btn.setEnabled(False)
        self.add_btn.setEnabled(True)
        self.status_log.append(f"[INFO] Updated event: {event.title}")
    
    def _edit_event(self, event: EPGEvent):
        """Edit event"""
        self._editing_event = event
        self.event_id.setValue(event.event_id)
        self.event_title.setText(event.title)
        self.event_description.setPlainText(event.description)
        if event.start_time:
            self.event_start.setDateTime(QDateTime.fromString(
                event.start_time.strftime("%Y-%m-%d %H:%M:%S"),
                "yyyy-MM-dd HH:mm:ss"
            ))
        self.event_duration.setValue(event.duration)
        
        for i in range(self.content_type.count()):
            if self.content_type.itemText(i).startswith(event.content_type):
                self.content_type.setCurrentIndex(i)
                break
        
        if event.director or event.actors or event.year > 0:
            self.extended_group.setChecked(True)
            self.director.setText(event.director)
            self.actors_list.clear()
            for actor in event.actors:
                self.actors_list.addItem(actor)
            self.year.setValue(event.year)
            self.star_rating.setValue(event.star_rating)
            self.parental_rating.setValue(event.parental_rating)
            self.language.setText(event.language)
            self.category.setText(event.category)
            self.season.setValue(event.season_number)
            self.episode.setValue(event.episode_number)
            self.episode_title.setText(event.episode_title)
        
        self.update_btn.setEnabled(True)
        self.add_btn.setEnabled(False)
    
    def _create_recurring(self):
        """Create recurring events"""
        base_event = self._get_event_from_form()
        if not base_event:
            QMessageBox.warning(self, "Warning", "Please fill in event details first")
            return
        
        dialog = self._create_recurring_dialog()
        if dialog.exec() == QDialog.DialogCode.Accepted:
            settings = dialog.get_settings()
            start_dt = datetime.combine(
                settings['start_date'],
                base_event.start_time.time() if base_event.start_time else datetime.now().time()
            )
            end_dt = datetime.combine(settings['end_date'], datetime.now().time())
            
            recurring = self.epg_service.create_recurring_events(
                base_event, start_dt, end_dt,
                settings['frequency'], settings['days_of_week']
            ) if self.epg_service else []
            
            self.events.extend(recurring)
            self.filtered_events = self.events
            self._update_events_table()
            self.status_log.append(f"[INFO] Created {len(recurring)} recurring events")
    
    def _create_recurring_dialog(self):
        """Create recurring event dialog"""
        dialog = QDialog(self)
        dialog.setWindowTitle("Create Recurring Events")
        dialog.setMinimumWidth(400)
        layout = QVBoxLayout(dialog)
        
        form = QFormLayout()
        
        frequency = QComboBox()
        frequency.addItems(["Daily", "Weekly", "Monthly"])
        form.addRow("Frequency:", frequency)
        
        start_date = QDateEdit()
        start_date.setDate(datetime.now().date())
        start_date.setCalendarPopup(True)
        form.addRow("Start Date:", start_date)
        
        end_date = QDateEdit()
        end_date.setDate(datetime.now().date() + timedelta(days=30))
        end_date.setCalendarPopup(True)
        form.addRow("End Date:", end_date)
        
        days_group = QGroupBox("Days of Week")
        days_layout = QVBoxLayout()
        day_checks = {}
        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        for i, day in enumerate(days):
            check = QCheckBox(day)
            check.setChecked(True)
            day_checks[i] = check
            days_layout.addWidget(check)
        days_group.setLayout(days_layout)
        form.addRow("", days_group)
        
        layout.addLayout(form)
        
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        
        def get_settings():
            days = [i for i, check in day_checks.items() if check.isChecked()]
            return {
                'frequency': frequency.currentText().lower(),
                'start_date': start_date.date().toPyDate(),
                'end_date': end_date.date().toPyDate(),
                'days_of_week': days
            }
        
        dialog.get_settings = get_settings
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)
        
        return dialog
    
    def _bulk_delete(self):
        """Delete selected events"""
        if not self.selected_events:
            return
        
        reply = QMessageBox.question(
            self, "Confirm Delete",
            f"Delete {len(self.selected_events)} event(s)?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            for event in self.selected_events:
                if event in self.events:
                    self.events.remove(event)
            self.filtered_events = self.events
            self._update_events_table()
            self.status_log.append(f"[INFO] Deleted {len(self.selected_events)} event(s)")
    
    def _bulk_copy(self):
        """Copy selected events"""
        if not self.selected_events:
            return
        
        copied = []
        for event in self.selected_events:
            new_id = max([e.event_id for e in self.events], default=0) + 1
            copied_event = EPGEvent(
                event_id=new_id,
                title=f"{event.title} (Copy)",
                description=event.description,
                start_time=event.start_time + timedelta(seconds=event.duration) if event.start_time else None,
                duration=event.duration,
                content_type=event.content_type,
                director=event.director,
                actors=event.actors.copy(),
                year=event.year,
                star_rating=event.star_rating,
                parental_rating=event.parental_rating,
                language=event.language,
                category=event.category,
                season_number=event.season_number,
                episode_number=event.episode_number,
                episode_title=event.episode_title,
                extended_info=event.extended_info.copy()
            )
            copied.append(copied_event)
        
        self.events.extend(copied)
        self.filtered_events = self.events
        self._update_events_table()
        self.status_log.append(f"[INFO] Copied {len(copied)} event(s)")
    
    def _validate_schedule(self):
        """Validate schedule"""
        if not self.epg_service:
            return
        
        valid, errors = self.epg_service.validate_schedule(self.events)
        if valid:
            QMessageBox.information(self, "Validation", "Schedule is valid!")
            self.status_log.append("[SUCCESS] Schedule validation passed")
        else:
            error_msg = "\n".join(errors)
            QMessageBox.warning(self, "Validation Errors", error_msg)
            self.status_log.append(f"[WARNING] Validation errors:\n{error_msg}")
    
    def _update_events_table(self):
        """Update events table"""
        self.events_table.setRowCount(0)
        
        display_events = self.filtered_events if self.filtered_events else self.events
        
        for event in display_events:
            row = self.events_table.rowCount()
            self.events_table.insertRow(row)
            
            # Checkbox for selection
            checkbox = QTableWidgetItem()
            checkbox.setCheckState(Qt.CheckState.Unchecked)
            self.events_table.setItem(row, 0, checkbox)
            
            # Event ID
            self.events_table.setItem(row, 1, QTableWidgetItem(str(event.event_id)))
            
            # Title
            title_item = QTableWidgetItem(event.title)
            title_item.setToolTip(event.description if event.description else event.title)
            self.events_table.setItem(row, 2, title_item)
            
            # Start Time
            start_str = event.start_time.strftime("%Y-%m-%d %H:%M") if event.start_time else "N/A"
            self.events_table.setItem(row, 3, QTableWidgetItem(start_str))
            
            # Duration
            duration_str = f"{event.duration // 3600}h {(event.duration % 3600) // 60}m"
            self.events_table.setItem(row, 4, QTableWidgetItem(duration_str))
            
            # Content Type
            self.events_table.setItem(row, 5, QTableWidgetItem(event.content_type))
            
            # Rating
            rating_str = f"{event.star_rating:.1f}" if event.star_rating > 0 else "-"
            self.events_table.setItem(row, 6, QTableWidgetItem(rating_str))
            
            # Actions - Edit, Copy, Delete
            actions_widget = QWidget()
            actions_layout = QHBoxLayout(actions_widget)
            actions_layout.setContentsMargins(2, 2, 2, 2)
            actions_layout.setSpacing(3)
            
            edit_btn = QPushButton("✏️")
            edit_btn.setToolTip("Edit")
            edit_btn.setStyleSheet("background-color: #f59e0b; color: white; padding: 4px 8px; border-radius: 3px; font-size: 10px;")
            edit_btn.clicked.connect(lambda checked, e=event: self._edit_event(e))
            actions_layout.addWidget(edit_btn)
            
            copy_btn = QPushButton("📋")
            copy_btn.setToolTip("Copy")
            copy_btn.setStyleSheet("background-color: #3b82f6; color: white; padding: 4px 8px; border-radius: 3px; font-size: 10px;")
            copy_btn.clicked.connect(lambda checked, e=event: self._copy_event(e))
            actions_layout.addWidget(copy_btn)
            
            delete_btn = QPushButton("🗑️")
            delete_btn.setToolTip("Delete")
            delete_btn.setStyleSheet("background-color: #ef4444; color: white; padding: 4px 8px; border-radius: 3px; font-size: 10px;")
            delete_btn.clicked.connect(lambda checked, e=event: self._delete_event(e))
            actions_layout.addWidget(delete_btn)
            
            actions_layout.addStretch()
            self.events_table.setCellWidget(row, 7, actions_widget)
    
    def _copy_event(self, event: EPGEvent):
        """Copy/duplicate event"""
        try:
            new_event_id = max([e.event_id for e in self.events], default=0) + 1
            
            copied_event = EPGEvent(
                event_id=new_event_id,
                title=f"{event.title} (Copy)",
                description=event.description,
                start_time=event.start_time + timedelta(seconds=event.duration) if event.start_time else None,
                duration=event.duration,
                content_type=event.content_type,
                content_nibble_level_2=event.content_nibble_level_2,
                director=event.director,
                actors=event.actors.copy(),
                year=event.year,
                star_rating=event.star_rating,
                parental_rating=event.parental_rating,
                language=event.language,
                category=event.category,
                season_number=event.season_number,
                episode_number=event.episode_number,
                episode_title=event.episode_title,
                extended_info=event.extended_info.copy()
            )
            
            self.events.append(copied_event)
            self.filtered_events = self.events
            self._update_events_table()
            self.status_log.append(f"[INFO] Copied: {event.title}")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to copy: {e}")
            self.status_log.append(f"[ERROR] Copy failed: {e}")
    
    def _delete_event(self, event: EPGEvent):
        """Delete event from EPG"""
        if event in self.events:
            self.events.remove(event)
            self._update_events_table()
            self.status_log.append(f"[INFO] Deleted event: {event.title}")
    
    def _import_xmltv(self):
        """Import EPG from XMLTV file"""
        if not self.epg_service:
            QMessageBox.warning(self, "Warning", "EPG service not available")
            return
        
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Import XMLTV File",
            "",
            "XMLTV Files (*.xml);;All Files (*)"
        )
        
        if not file_path:
            return
        
        try:
            events = self.epg_service.import_xmltv(Path(file_path))
            if events:
                self.events.extend(events)
                self._update_events_table()
                self.status_log.append(f"[SUCCESS] Imported {len(events)} events from XMLTV")
                QMessageBox.information(self, "Success", f"Imported {len(events)} events")
            else:
                QMessageBox.warning(self, "Warning", "No events found in XMLTV file")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to import XMLTV: {e}")
            self.status_log.append(f"[ERROR] Import failed: {e}")
    
    def _export_epg(self):
        """Export EPG to file"""
        if not self.epg_service:
            QMessageBox.warning(self, "Warning", "EPG service not available")
            return
        
        if not self.events:
            QMessageBox.warning(self, "Warning", "No events to export")
            return
        
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Export EPG",
            f"epg_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            "JSON Files (*.json);;XMLTV Files (*.xml);;All Files (*)"
        )
        
        if not file_path:
            return
        
        try:
            format = "json" if file_path.endswith(".json") else "xmltv"
            epg_data = self.epg_service.export_epg(self.events, format)
            Path(file_path).write_text(epg_data, encoding='utf-8')
            self.status_log.append(f"[SUCCESS] Exported EPG to {file_path}")
            QMessageBox.information(self, "Success", f"EPG exported to {file_path}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to export EPG: {e}")
            self.status_log.append(f"[ERROR] Export failed: {e}")
    
    def _generate_eit(self):
        """Generate EIT file"""
        if not self.epg_service:
            QMessageBox.warning(self, "Warning", "EPG service not available")
            return
        
        if not self.events:
            QMessageBox.warning(self, "Warning", "No events to generate EIT")
            return
        
        service_id = self.service_id.value()
        service_name = self.service_name.text().strip() or f"Service {service_id}"
        provider = self.provider_name.text().strip()
        
        try:
            eit_path = self.epg_service.generate_eit(
                service_id=service_id,
                service_name=service_name,
                events=self.events,
                provider=provider
            )
            
            self.status_log.append(f"[SUCCESS] Generated EIT file: {eit_path.name}")
            self.epg_generated.emit(eit_path)
            QMessageBox.information(
                self, "Success",
                f"EIT file generated successfully!\n\n{eit_path}\n\nReady for TSDuck injection."
            )
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to generate EIT: {e}")
            self.status_log.append(f"[ERROR] EIT generation failed: {e}")

