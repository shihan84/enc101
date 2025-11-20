"""
Modern Stat Card Widget
Beautiful, elegant stat card with glassmorphism and gradients
"""

from PyQt6.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout, QLabel
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPainter, QColor, QBrush, QPen
from typing import Optional


class ModernStatCard(QFrame):
    """Modern stat card with glassmorphism and gradient effects"""
    
    def __init__(self, title: str, value: str = "0", unit: str = "", 
                 color: str = "#6366f1", icon: str = ""):
        super().__init__()
        self.title = title
        self.value = value
        self.unit = unit
        self.color = color
        self.icon = icon
        self.setup_ui()
        self.setup_animation()
    
    def setup_ui(self):
        """Setup stat card UI"""
        self.setFixedHeight(140)
        self.setMinimumWidth(200)
        
        # Glassmorphism style
        self.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(30, 41, 59, 0.9),
                    stop:1 rgba(30, 41, 59, 0.7));
                border: 1px solid rgba(148, 163, 184, 0.2);
                border-radius: 16px;
            }}
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(8)
        
        # Icon and Title Row
        header_layout = QHBoxLayout()
        header_layout.setSpacing(10)
        
        if self.icon:
            icon_label = QLabel(self.icon)
            icon_label.setStyleSheet("font-size: 24px;")
            header_layout.addWidget(icon_label)
        
        title_label = QLabel(self.title)
        title_label.setStyleSheet("""
            color: #cbd5e1;
            font-size: 13px;
            font-weight: 500;
            letter-spacing: 0.5px;
        """)
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        
        layout.addLayout(header_layout)
        
        # Value Row
        value_layout = QHBoxLayout()
        value_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        
        self.value_label = QLabel(self.value)
        self.value_label.setObjectName("value_label")
        self.value_label.setStyleSheet(f"""
            color: {self.color};
            font-size: 36px;
            font-weight: 700;
            font-family: 'Segoe UI', 'Roboto', sans-serif;
        """)
        value_layout.addWidget(self.value_label)
        
        if self.unit:
            unit_label = QLabel(self.unit)
            unit_label.setStyleSheet("""
                color: #94a3b8;
                font-size: 18px;
                font-weight: 500;
                padding-top: 8px;
            """)
            value_layout.addWidget(unit_label)
        
        value_layout.addStretch()
        layout.addLayout(value_layout)
        
        # Accent line at bottom
        accent_line = QFrame()
        accent_line.setFixedHeight(3)
        accent_line.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {self.color},
                    stop:1 transparent);
                border-radius: 2px;
            }}
        """)
        layout.addWidget(accent_line)
    
    def setup_animation(self):
        """Setup hover animation"""
        pass  # Can add hover effects later
    
    def update_value(self, value: str):
        """Update stat value with smooth transition"""
        # Only update if value changed (performance optimization)
        if self.value == value:
            return
        
        value_label = self.findChild(QLabel, "value_label")
        if value_label:
            value_label.setText(value)
            self.value = value
            # Trigger minimal repaint
            self.update()
    
    def paintEvent(self, event):
        """Custom paint for glassmorphism effect - optimized"""
        # Use base paint first
        super().paintEvent(event)
        
        # Only draw glow if widget is visible and enabled
        if not self.isVisible() or not self.isEnabled():
            return
        
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        
        # Subtle glow effect (optimized - only draw if needed)
        glow_color = QColor(self.color)
        glow_color.setAlpha(20)
        pen = QPen(glow_color, 2)
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawRoundedRect(self.rect().adjusted(1, 1, -1, -1), 16, 16)
        
        painter.end()

