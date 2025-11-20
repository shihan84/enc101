"""
API Routes
Define REST API endpoints
"""

from typing import Dict, Any, Optional
from ..core.logger import get_logger


logger = get_logger("APIRoutes")


def setup_routes(api_server, app_framework):
    """Setup API routes"""
    
    # Get services
    stream_service = app_framework.get_service("stream")
    scte35_service = app_framework.get_service("scte35")
    profile_service = app_framework.get_service("profile")
    monitoring_service = app_framework.get_service("monitoring")
    
    # Comprehensive health check
    def health_check(query: Dict, body: Optional[Dict]) -> Dict[str, Any]:
        """Comprehensive health check endpoint"""
        health_status = {
            "status": "healthy",
            "version": app_framework.config.app_version,
            "timestamp": __import__('datetime').datetime.now().isoformat(),
            "services": {}
        }
        
        # Check Stream Service
        if stream_service:
            try:
                is_running = stream_service.is_running
                session = stream_service.get_current_session()
                health_status["services"]["stream"] = {
                    "status": "healthy" if stream_service else "unavailable",
                    "running": is_running,
                    "has_session": session is not None
                }
            except Exception as e:
                health_status["services"]["stream"] = {
                    "status": "unhealthy",
                    "error": str(e)
                }
                health_status["status"] = "degraded"
        else:
            health_status["services"]["stream"] = {"status": "unavailable"}
        
        # Check Monitoring Service
        if monitoring_service:
            try:
                metrics = monitoring_service.get_system_metrics()
                health_status["services"]["monitoring"] = {
                    "status": "healthy",
                    "metrics_available": metrics is not None
                }
            except Exception as e:
                health_status["services"]["monitoring"] = {
                    "status": "unhealthy",
                    "error": str(e)
                }
                health_status["status"] = "degraded"
        else:
            health_status["services"]["monitoring"] = {"status": "unavailable"}
        
        # Check Database
        try:
            from ..database.database import Database
            db = Database()
            # Simple query to check database connectivity
            with db.get_connection() as conn:
                conn.execute("SELECT 1")
            health_status["services"]["database"] = {"status": "healthy"}
        except Exception as e:
            health_status["services"]["database"] = {
                "status": "unhealthy",
                "error": str(e)
            }
            health_status["status"] = "degraded"
        
        # Check TSDuck (if available)
        try:
            tsduck_service = app_framework.get_service("tsduck")
            if tsduck_service:
                # Check if TSDuck is accessible
                import subprocess
                result = subprocess.run(
                    ["tsp", "--version"],
                    capture_output=True,
                    timeout=5
                )
                health_status["services"]["tsduck"] = {
                    "status": "healthy" if result.returncode == 0 else "unavailable",
                    "accessible": result.returncode == 0
                }
            else:
                health_status["services"]["tsduck"] = {"status": "unavailable"}
        except Exception as e:
            health_status["services"]["tsduck"] = {
                "status": "unhealthy",
                "error": str(e)
            }
            health_status["status"] = "degraded"
        
        # Check Telegram Service (if enabled)
        try:
            telegram_service = app_framework.get_service("telegram")
            if telegram_service:
                health_status["services"]["telegram"] = {
                    "status": "healthy" if telegram_service.enabled else "disabled",
                    "enabled": telegram_service.enabled
                }
            else:
                health_status["services"]["telegram"] = {"status": "unavailable"}
        except Exception as e:
            health_status["services"]["telegram"] = {
                "status": "unhealthy",
                "error": str(e)
            }
        
        return health_status
    
    # Simple health check (for load balancers)
    def simple_health(query: Dict, body: Optional[Dict]) -> Dict[str, Any]:
        return {"status": "ok"}
    
    api_server.add_route('GET', '/health', simple_health)  # Simple endpoint
    api_server.add_route('GET', '/api/health', health_check)  # Comprehensive endpoint
    
    # Stream status
    def stream_status(query: Dict, body: Optional[Dict]) -> Dict[str, Any]:
        session = stream_service.get_current_session() if stream_service else None
        if session:
            return {
                "running": stream_service.is_running,
                "session_id": session.session_id,
                "status": session.status
            }
        return {"running": False, "session_id": None, "status": "stopped"}
    
    api_server.add_route('GET', '/api/stream/status', stream_status)
    
    # System metrics
    def system_metrics(query: Dict, body: Optional[Dict]) -> Dict[str, Any]:
        metrics = monitoring_service.get_system_metrics()
        return metrics
    
    api_server.add_route('GET', '/api/metrics', system_metrics)
    
    # Profiles list
    def profiles_list(query: Dict, body: Optional[Dict]) -> Dict[str, Any]:
        profiles = profile_service.get_profile_names()
        return {"profiles": profiles}
    
    api_server.add_route('GET', '/api/profiles', profiles_list)
    
    # Prometheus metrics endpoint (returns text/plain, not JSON)
    def prometheus_metrics_handler(query: Dict, body: Optional[Dict]):
        """Prometheus metrics endpoint handler"""
        from ..api.prometheus_metrics import get_prometheus_metrics
        metrics_text = get_prometheus_metrics(app_framework)
        # Return as string for text/plain response
        return metrics_text
    
    # Store handler separately for special response handling
    api_server.add_route('GET', '/metrics', prometheus_metrics_handler)
    
    logger.info("API routes configured")

