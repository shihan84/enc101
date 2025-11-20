"""
Prometheus metrics export for monitoring
"""

from typing import Dict, Any
from ..core.logger import get_logger


class PrometheusMetrics:
    """Prometheus metrics exporter"""
    
    def __init__(self):
        self.logger = get_logger("PrometheusMetrics")
    
    def format_metrics(self, metrics_data: Dict[str, Any]) -> str:
        """
        Format metrics data as Prometheus text format
        
        Args:
            metrics_data: Dictionary containing metrics
        
        Returns:
            Prometheus-formatted metrics string
        """
        lines = []
        
        # System metrics
        if 'cpu' in metrics_data:
            cpu = metrics_data['cpu']
            lines.append(f'# HELP system_cpu_usage CPU usage percentage')
            lines.append(f'# TYPE system_cpu_usage gauge')
            lines.append(f'system_cpu_usage {cpu.get("percent", 0)}')
        
        if 'memory' in metrics_data:
            memory = metrics_data['memory']
            lines.append(f'# HELP system_memory_usage Memory usage percentage')
            lines.append(f'# TYPE system_memory_usage gauge')
            lines.append(f'system_memory_usage {memory.get("percent", 0)}')
            lines.append(f'# HELP system_memory_used_bytes Memory used in bytes')
            lines.append(f'# TYPE system_memory_used_bytes gauge')
            lines.append(f'system_memory_used_bytes {memory.get("used_bytes", 0)}')
            lines.append(f'# HELP system_memory_total_bytes Memory total in bytes')
            lines.append(f'# TYPE system_memory_total_bytes gauge')
            lines.append(f'system_memory_total_bytes {memory.get("total_bytes", 0)}')
        
        if 'disk' in metrics_data:
            disk = metrics_data['disk']
            lines.append(f'# HELP system_disk_usage Disk usage percentage')
            lines.append(f'# TYPE system_disk_usage gauge')
            lines.append(f'system_disk_usage {disk.get("percent", 0)}')
            lines.append(f'# HELP system_disk_used_bytes Disk used in bytes')
            lines.append(f'# TYPE system_disk_used_bytes gauge')
            lines.append(f'system_disk_used_bytes {disk.get("used_bytes", 0)}')
            lines.append(f'# HELP system_disk_total_bytes Disk total in bytes')
            lines.append(f'# TYPE system_disk_total_bytes gauge')
            lines.append(f'system_disk_total_bytes {disk.get("total_bytes", 0)}')
        
        # Stream metrics
        if 'stream' in metrics_data:
            stream = metrics_data['stream']
            lines.append(f'# HELP stream_running Whether stream is running (1) or not (0)')
            lines.append(f'# TYPE stream_running gauge')
            lines.append(f'stream_running {1 if stream.get("running", False) else 0}')
            
            if 'packets_processed' in stream:
                lines.append(f'# HELP stream_packets_processed Total packets processed')
                lines.append(f'# TYPE stream_packets_processed counter')
                lines.append(f'stream_packets_processed {stream["packets_processed"]}')
            
            if 'errors_count' in stream:
                lines.append(f'# HELP stream_errors_count Total stream errors')
                lines.append(f'# TYPE stream_errors_count counter')
                lines.append(f'stream_errors_count {stream["errors_count"]}')
            
            if 'scte35_injected' in stream:
                lines.append(f'# HELP stream_scte35_injected Total SCTE-35 markers injected')
                lines.append(f'# TYPE stream_scte35_injected counter')
                lines.append(f'stream_scte35_injected {stream["scte35_injected"]}')
        
        return '\n'.join(lines) + '\n'


def get_prometheus_metrics(app_framework) -> str:
    """
    Get Prometheus-formatted metrics
    
    Args:
        app_framework: Application framework instance
    
    Returns:
        Prometheus metrics string
    """
    exporter = PrometheusMetrics()
    
    # Get system metrics
    monitoring_service = app_framework.get_service("monitoring")
    metrics_data = {}
    
    if monitoring_service:
        system_metrics = monitoring_service.get_system_metrics()
        if system_metrics:
            metrics_data.update(system_metrics)
    
    # Get stream metrics
    stream_service = app_framework.get_service("stream")
    if stream_service:
        session = stream_service.get_current_session()
        stream_metrics = {
            'running': stream_service.is_running,
            'packets_processed': session.packets_processed if session else 0,
            'errors_count': session.errors_count if session else 0,
            'scte35_injected': session.scte35_injected if session else 0
        }
        metrics_data['stream'] = stream_metrics
    
    return exporter.format_metrics(metrics_data)

