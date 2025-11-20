"""
Modern Theme with Elegant Styling
Professional, beautiful, and modern UI theme
"""

from PyQt6.QtWidgets import QApplication
from typing import Optional


class ModernTheme:
    """Modern theme with elegant styling"""
    
    # Color Palette - Modern Professional
    COLORS = {
        # Primary Colors
        'primary': '#6366f1',  # Indigo
        'primary_dark': '#4f46e5',
        'primary_light': '#818cf8',
        
        # Accent Colors
        'accent': '#10b981',  # Emerald
        'accent_dark': '#059669',
        'accent_light': '#34d399',
        
        # Status Colors
        'success': '#10b981',
        'warning': '#f59e0b',
        'error': '#ef4444',
        'info': '#3b82f6',
        
        # Background Colors
        'bg_primary': '#0f172a',  # Slate 900
        'bg_secondary': '#1e293b',  # Slate 800
        'bg_tertiary': '#334155',  # Slate 700
        'bg_card': '#1e293b',
        'bg_hover': '#334155',
        
        # Text Colors
        'text_primary': '#f1f5f9',  # Slate 100
        'text_secondary': '#cbd5e1',  # Slate 300
        'text_muted': '#94a3b8',  # Slate 400
        
        # Border Colors
        'border': '#334155',
        'border_light': '#475569',
        'border_dark': '#1e293b',
        
        # Glassmorphism
        'glass_bg': 'rgba(30, 41, 59, 0.7)',
        'glass_border': 'rgba(148, 163, 184, 0.2)',
    }
    
    @staticmethod
    def get_stylesheet() -> str:
        """Get complete modern stylesheet"""
        colors = ModernTheme.COLORS
        
        return f"""
        /* ============================================
           MODERN ENTERPRISE THEME - IBE-100 v3.0
           ============================================ */
        
        /* Main Window */
        QMainWindow {{
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 {colors['bg_primary']}, 
                stop:1 {colors['bg_secondary']});
            color: {colors['text_primary']};
        }}
        
        /* Widgets */
        QWidget {{
            background-color: transparent;
            color: {colors['text_primary']};
            font-family: 'Segoe UI', 'Roboto', 'Arial', sans-serif;
        }}
        
        /* Scroll Areas */
        QScrollArea {{
            background-color: transparent;
            border: none;
        }}
        
        QScrollBar:vertical {{
            background: {colors['bg_secondary']};
            width: 12px;
            border-radius: 6px;
            margin: 0;
        }}
        
        QScrollBar::handle:vertical {{
            background: {colors['bg_tertiary']};
            border-radius: 6px;
            min-height: 30px;
        }}
        
        QScrollBar::handle:vertical:hover {{
            background: {colors['border_light']};
        }}
        
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
            height: 0;
        }}
        
        /* Buttons - Modern Gradient */
        QPushButton {{
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 {colors['primary']}, 
                stop:1 {colors['primary_dark']});
            color: white;
            border: none;
            border-radius: 8px;
            padding: 12px 24px;
            font-size: 13px;
            font-weight: 600;
            min-height: 20px;
        }}
        
        QPushButton:hover {{
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 {colors['primary_light']}, 
                stop:1 {colors['primary']});
            transform: translateY(-1px);
        }}
        
        QPushButton:pressed {{
            background: {colors['primary_dark']};
        }}
        
        QPushButton:disabled {{
            background: {colors['bg_tertiary']};
            color: {colors['text_muted']};
        }}
        
        /* Success Button */
        QPushButton[class="success"] {{
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 {colors['success']}, 
                stop:1 {colors['accent_dark']});
        }}
        
        QPushButton[class="success"]:hover {{
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 {colors['accent_light']}, 
                stop:1 {colors['success']});
        }}
        
        /* Danger Button */
        QPushButton[class="danger"] {{
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 {colors['error']}, 
                stop:1 #dc2626);
        }}
        
        QPushButton[class="danger"]:hover {{
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #f87171, 
                stop:1 {colors['error']});
        }}
        
        /* Input Fields - Modern */
        QLineEdit, QSpinBox, QComboBox {{
            background-color: {colors['bg_secondary']};
            color: {colors['text_primary']};
            border: 2px solid {colors['border']};
            border-radius: 8px;
            padding: 10px 15px;
            font-size: 13px;
            selection-background-color: {colors['primary']};
            selection-color: white;
        }}
        
        QLineEdit:focus, QSpinBox:focus, QComboBox:focus {{
            border: 2px solid {colors['primary']};
            background-color: {colors['bg_tertiary']};
        }}
        
        QComboBox::drop-down {{
            border: none;
            width: 30px;
        }}
        
        QComboBox::down-arrow {{
            image: none;
            border-left: 5px solid transparent;
            border-right: 5px solid transparent;
            border-top: 5px solid {colors['text_secondary']};
            width: 0;
            height: 0;
        }}
        
        QComboBox QAbstractItemView {{
            background-color: {colors['bg_secondary']};
            border: 2px solid {colors['border']};
            border-radius: 8px;
            selection-background-color: {colors['primary']};
            selection-color: white;
            padding: 5px;
        }}
        
        /* Group Boxes - Elegant */
        QGroupBox {{
            border: 2px solid {colors['border']};
            border-radius: 12px;
            margin-top: 15px;
            padding-top: 20px;
            font-weight: 600;
            font-size: 14px;
            color: {colors['text_primary']};
            background-color: {colors['bg_card']};
        }}
        
        QGroupBox::title {{
            subcontrol-origin: margin;
            left: 15px;
            padding: 0 10px;
            background-color: {colors['bg_primary']};
            color: {colors['text_primary']};
        }}
        
        /* Labels */
        QLabel {{
            color: {colors['text_primary']};
            font-size: 13px;
        }}
        
        QLabel[class="title"] {{
            font-size: 24px;
            font-weight: 700;
            color: {colors['primary_light']};
        }}
        
        QLabel[class="subtitle"] {{
            font-size: 16px;
            font-weight: 600;
            color: {colors['text_secondary']};
        }}
        
        QLabel[class="muted"] {{
            color: {colors['text_muted']};
            font-size: 12px;
        }}
        
        /* Tabs - Modern */
        QTabWidget::pane {{
            border: 2px solid {colors['border']};
            border-radius: 12px;
            background-color: {colors['bg_secondary']};
            top: -1px;
        }}
        
        QTabBar::tab {{
            background-color: {colors['bg_tertiary']};
            color: {colors['text_secondary']};
            padding: 12px 24px;
            margin-right: 4px;
            border-top-left-radius: 8px;
            border-top-right-radius: 8px;
            font-weight: 500;
            font-size: 13px;
        }}
        
        QTabBar::tab:hover {{
            background-color: {colors['bg_hover']};
            color: {colors['text_primary']};
        }}
        
        QTabBar::tab:selected {{
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 {colors['primary']}, 
                stop:1 {colors['primary_dark']});
            color: white;
            font-weight: 600;
        }}
        
        /* Text Edit - Console Style */
        QTextEdit {{
            background-color: {colors['bg_primary']};
            color: {colors['accent_light']};
            border: 2px solid {colors['border']};
            border-radius: 8px;
            padding: 10px;
            font-family: 'Consolas', 'Courier New', monospace;
            font-size: 11px;
            selection-background-color: {colors['primary']};
        }}
        
        /* Checkboxes - Modern */
        QCheckBox {{
            color: {colors['text_primary']};
            font-size: 13px;
            spacing: 8px;
        }}
        
        QCheckBox::indicator {{
            width: 20px;
            height: 20px;
            border: 2px solid {colors['border']};
            border-radius: 4px;
            background-color: {colors['bg_secondary']};
        }}
        
        QCheckBox::indicator:hover {{
            border-color: {colors['primary']};
        }}
        
        QCheckBox::indicator:checked {{
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 {colors['primary']}, 
                stop:1 {colors['primary_dark']});
            border-color: {colors['primary']};
        }}
        
        QCheckBox::indicator:checked::after {{
            content: "✓";
            color: white;
        }}
        
        /* Time Edit */
        QTimeEdit {{
            background-color: {colors['bg_secondary']};
            color: {colors['text_primary']};
            border: 2px solid {colors['border']};
            border-radius: 8px;
            padding: 10px 15px;
            font-size: 13px;
        }}
        
        QTimeEdit:focus {{
            border: 2px solid {colors['primary']};
        }}
        
        /* Progress Bar - Modern */
        QProgressBar {{
            border: 2px solid {colors['border']};
            border-radius: 8px;
            text-align: center;
            background-color: {colors['bg_secondary']};
            color: {colors['text_primary']};
            height: 25px;
        }}
        
        QProgressBar::chunk {{
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 {colors['primary']}, 
                stop:1 {colors['accent']});
            border-radius: 6px;
        }}
        """


def apply_modern_theme(app: Optional[QApplication] = None):
    """Apply modern theme to application"""
    if app is None:
        app = QApplication.instance()
    
    if app:
        app.setStyleSheet(ModernTheme.get_stylesheet())
        return True
    return False

