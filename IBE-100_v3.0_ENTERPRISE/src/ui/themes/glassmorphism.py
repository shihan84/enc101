"""
Glassmorphism Widgets
Modern glass-like transparent effects
"""

from PyQt6.QtWidgets import QWidget, QFrame
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPainter, QColor, QBrush, QPen
from typing import Optional


class GlassmorphicWidget(QWidget):
    """Widget with glassmorphism effect"""
    
    def __init__(self, parent=None, blur_radius: int = 20, opacity: float = 0.7):
        super().__init__(parent)
        self.blur_radius = blur_radius
        self.opacity = opacity
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
    
    def paintEvent(self, event):
        """Paint glassmorphism effect"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Semi-transparent background
        bg_color = QColor(30, 41, 59, int(255 * self.opacity))
        painter.setBrush(QBrush(bg_color))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(self.rect(), 12, 12)
        
        # Border
        border_color = QColor(148, 163, 184, int(255 * 0.2))
        pen = QPen(border_color, 1)
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawRoundedRect(self.rect(), 12, 12)


class GlassmorphicCard(QFrame):
    """Card widget with glassmorphism effect"""
    
    def __init__(self, parent=None, opacity: float = 0.8):
        super().__init__(parent)
        self.opacity = opacity
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setStyleSheet("""
            QFrame {
                background-color: rgba(30, 41, 59, 0.8);
                border: 1px solid rgba(148, 163, 184, 0.2);
                border-radius: 16px;
            }
        """)
    
    def paintEvent(self, event):
        """Paint glassmorphism card"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Semi-transparent background with blur effect
        bg_color = QColor(30, 41, 59, int(255 * self.opacity))
        painter.setBrush(QBrush(bg_color))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(self.rect(), 16, 16)
        
        # Subtle border
        border_color = QColor(148, 163, 184, int(255 * 0.2))
        pen = QPen(border_color, 1)
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawRoundedRect(self.rect(), 16, 16)

