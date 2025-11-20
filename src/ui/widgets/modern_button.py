"""
Modern Button Widget
Elegant buttons with gradients, shadows, and hover effects
"""

from PyQt6.QtWidgets import QPushButton
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import QPainter, QColor, QBrush
from typing import Optional


class ModernButton(QPushButton):
    """Modern button with elegant styling"""
    
    def __init__(self, text: str = "", parent=None, 
                 button_type: str = "primary", icon: str = ""):
        super().__init__(text, parent)
        self.button_type = button_type
        self.icon_text = icon
        self.setup_style()
    
    def setup_style(self):
        """Setup button style based on type"""
        colors = {
            "primary": {
                "bg": "qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #6366f1, stop:1 #4f46e5)",
                "hover": "qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #818cf8, stop:1 #6366f1)",
                "text": "white"
            },
            "success": {
                "bg": "qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #10b981, stop:1 #059669)",
                "hover": "qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #34d399, stop:1 #10b981)",
                "text": "white"
            },
            "danger": {
                "bg": "qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #ef4444, stop:1 #dc2626)",
                "hover": "qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #f87171, stop:1 #ef4444)",
                "text": "white"
            },
            "warning": {
                "bg": "qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #f59e0b, stop:1 #d97706)",
                "hover": "qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #fbbf24, stop:1 #f59e0b)",
                "text": "white"
            },
            "info": {
                "bg": "qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #3b82f6, stop:1 #2563eb)",
                "hover": "qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #60a5fa, stop:1 #3b82f6)",
                "text": "white"
            }
        }
        
        style = colors.get(self.button_type, colors["primary"])
        
        if self.icon_text:
            self.setText(f"{self.icon_text} {self.text()}")
        
        self.setStyleSheet(f"""
            QPushButton {{
                background: {style['bg']};
                color: {style['text']};
                border: none;
                border-radius: 10px;
                padding: 12px 24px;
                font-size: 13px;
                font-weight: 600;
                min-height: 20px;
            }}
            QPushButton:hover {{
                background: {style['hover']};
            }}
            QPushButton:pressed {{
                background: {style['bg']};
            }}
            QPushButton:disabled {{
                background: #334155;
                color: #94a3b8;
            }}
        """)

