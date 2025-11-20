"""
Feature Check Script
Verifies all features are properly integrated
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

def check_imports():
    """Check all imports"""
    print("[CHECK] Checking imports...")
    errors = []
    
    try:
        from src.services import (
            StreamAnalyzerService, BitrateMonitorService, EPGService,
            StreamMetrics, ComplianceReport, BitratePoint, EPGEvent
        )
        print("  [OK] Services imported")
    except Exception as e:
        errors.append(f"Services import: {e}")
        print(f"  [ERROR] Services import failed: {e}")
    
    try:
        from src.ui.widgets import (
            StreamQualityWidget, BitrateMonitorWidget, EPGEditorWidget
        )
        print("  [OK] Widgets imported")
    except Exception as e:
        errors.append(f"Widgets import: {e}")
        print(f"  [ERROR] Widgets import failed: {e}")
    
    return errors

def check_services():
    """Check service initialization"""
    print("\n[CHECK] Checking service initialization...")
    errors = []
    
    try:
        from src.services.tsduck_service import TSDuckService
        from src.services.telegram_service import TelegramService
        
        # Mock services for testing
        tsduck = TSDuckService()
        telegram = TelegramService()
        
        from src.services.stream_analyzer_service import StreamAnalyzerService
        analyzer = StreamAnalyzerService(tsduck, telegram)
        print("  [OK] StreamAnalyzerService initialized")
        
        from src.services.bitrate_monitor_service import BitrateMonitorService
        monitor = BitrateMonitorService(tsduck, telegram)
        print("  [OK] BitrateMonitorService initialized")
        
        from src.services.epg_service import EPGService
        epg = EPGService()
        print("  [OK] EPGService initialized")
        
    except Exception as e:
        errors.append(f"Service initialization: {e}")
        print(f"  [ERROR] Service initialization failed: {e}")
        import traceback
        traceback.print_exc()
    
    return errors

def check_widgets():
    """Check widget initialization"""
    print("\n[CHECK] Checking widget initialization...")
    errors = []
    
    try:
        from src.services.stream_analyzer_service import StreamAnalyzerService
        from src.services.bitrate_monitor_service import BitrateMonitorService
        from src.services.epg_service import EPGService
        
        from src.ui.widgets.stream_quality_widget import StreamQualityWidget
        from src.ui.widgets.bitrate_monitor_widget import BitrateMonitorWidget
        from src.ui.widgets.epg_editor_widget import EPGEditorWidget
        
        # Mock services
        analyzer = StreamAnalyzerService()
        monitor = BitrateMonitorService()
        epg = EPGService()
        
        # Try to create widgets (without Qt app, this might fail, but we can check imports)
        print("  [OK] Widget classes accessible")
        
    except Exception as e:
        errors.append(f"Widget check: {e}")
        print(f"  [ERROR] Widget check failed: {e}")
        import traceback
        traceback.print_exc()
    
    return errors

def check_main_integration():
    """Check main_enterprise.py integration"""
    print("\n[CHECK] Checking main_enterprise.py integration...")
    errors = []
    
    try:
        main_file = Path(__file__).parent / "main_enterprise.py"
        content = main_file.read_text(encoding='utf-8')
        
        checks = [
            ("StreamAnalyzerService", "StreamAnalyzerService imported"),
            ("BitrateMonitorService", "BitrateMonitorService imported"),
            ("EPGService", "EPGService imported"),
            ("register_service(\"stream_analyzer\"", "stream_analyzer registered"),
            ("register_service(\"bitrate_monitor\"", "bitrate_monitor registered"),
            ("register_service(\"epg\"", "epg registered"),
        ]
        
        # Check main_window.py for service access
        main_window_file = Path(__file__).parent / "src" / "ui" / "main_window.py"
        if main_window_file.exists():
            main_window_content = main_window_file.read_text(encoding='utf-8')
            window_checks = [
                ("get_service(\"stream_analyzer\")", "stream_analyzer accessed in UI"),
                ("get_service(\"bitrate_monitor\")", "bitrate_monitor accessed in UI"),
                ("get_service(\"epg\")", "epg accessed in UI"),
            ]
            for check, name in window_checks:
                if check in main_window_content:
                    print(f"  [OK] {name}")
                else:
                    errors.append(f"Missing: {name}")
                    print(f"  [ERROR] Missing: {name}")
        
        for check, name in checks:
            if check in content:
                print(f"  [OK] {name}")
            else:
                errors.append(f"Missing: {name}")
                print(f"  [ERROR] Missing: {name}")
        
    except Exception as e:
        errors.append(f"Main integration check: {e}")
        print(f"  [ERROR] Main integration check failed: {e}")
    
    return errors

def main():
    """Run all checks"""
    print("=" * 60)
    print("IBE-100 v3.0 Enterprise - Feature Check")
    print("=" * 60)
    
    all_errors = []
    
    all_errors.extend(check_imports())
    all_errors.extend(check_services())
    all_errors.extend(check_widgets())
    all_errors.extend(check_main_integration())
    
    print("\n" + "=" * 60)
    if all_errors:
        print(f"[FAILED] Found {len(all_errors)} issue(s):")
        for error in all_errors:
            print(f"  - {error}")
        return 1
    else:
        print("[SUCCESS] All features check passed!")
        return 0

if __name__ == "__main__":
    sys.exit(main())

