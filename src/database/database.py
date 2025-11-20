"""
Database integration using SQLite
Stores session history, analytics, and audit logs
"""

import sqlite3
import json
from pathlib import Path
from datetime import datetime
from typing import List, Optional, Dict, Any
from contextlib import contextmanager

from ..core.logger import get_logger
from ..models.session import StreamSession
from ..models.stream_config import StreamConfig


class Database:
    """Database connection manager"""
    
    def __init__(self, db_path: Path = None):
        self.logger = get_logger("Database")
        self.db_path = db_path or Path("database/sessions.db")
        self.db_path.parent.mkdir(exist_ok=True)
        self._init_database()
        self.logger.info(f"Database initialized: {self.db_path}")
    
    def _init_database(self):
        """Initialize database schema"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Sessions table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS sessions (
                    session_id TEXT PRIMARY KEY,
                    config_json TEXT NOT NULL,
                    marker_json TEXT,
                    status TEXT NOT NULL,
                    start_time TEXT,
                    stop_time TEXT,
                    bytes_processed INTEGER DEFAULT 0,
                    packets_processed INTEGER DEFAULT 0,
                    errors_count INTEGER DEFAULT 0,
                    scte35_injected INTEGER DEFAULT 0,
                    created_at TEXT NOT NULL
                )
            """)
            
            # Analytics table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS analytics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT,
                    timestamp TEXT NOT NULL,
                    metric_name TEXT NOT NULL,
                    metric_value REAL,
                    metadata TEXT,
                    FOREIGN KEY (session_id) REFERENCES sessions(session_id)
                )
            """)
            
            # Audit log table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS audit_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    action TEXT NOT NULL,
                    user TEXT,
                    details TEXT
                )
            """)
            
            conn.commit()
            self.logger.info("Database schema initialized")
    
    @contextmanager
    def get_connection(self):
        """Get database connection context manager"""
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            self.logger.error(f"Database error: {e}", exc_info=True)
            raise
        finally:
            conn.close()
    
    def execute(self, query: str, params: tuple = ()) -> List[sqlite3.Row]:
        """Execute query and return results"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            return cursor.fetchall()
    
    def execute_one(self, query: str, params: tuple = ()) -> Optional[sqlite3.Row]:
        """Execute query and return single result"""
        results = self.execute(query, params)
        return results[0] if results else None


class SessionRepository:
    """Repository for stream session data"""
    
    def __init__(self, database: Database):
        self.db = database
        self.logger = get_logger("SessionRepository")
    
    def save_session(self, session: StreamSession) -> bool:
        """Save or update session"""
        try:
            config_json = json.dumps(session.config.to_dict(), ensure_ascii=False)
            marker_json = json.dumps(session.marker.to_dict(), ensure_ascii=False) if session.marker else None
            
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT OR REPLACE INTO sessions (
                        session_id, config_json, marker_json, status,
                        start_time, stop_time, bytes_processed,
                        packets_processed, errors_count, scte35_injected, created_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    session.session_id,
                    config_json,
                    marker_json,
                    session.status,
                    session.start_time.isoformat() if session.start_time else None,
                    session.stop_time.isoformat() if session.stop_time else None,
                    session.bytes_processed,
                    session.packets_processed,
                    session.errors_count,
                    session.scte35_injected,
                    session.created_at.isoformat()
                ))
                conn.commit()
            
            self.logger.debug(f"Saved session: {session.session_id}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to save session: {e}", exc_info=True)
            return False
    
    def get_session(self, session_id: str) -> Optional[StreamSession]:
        """Get session by ID"""
        try:
            row = self.db.execute_one(
                "SELECT * FROM sessions WHERE session_id = ?",
                (session_id,)
            )
            
            if not row:
                return None
            
            return self._row_to_session(row)
        except Exception as e:
            self.logger.error(f"Failed to get session: {e}", exc_info=True)
            return None
    
    def get_recent_sessions(self, limit: int = 10) -> List[StreamSession]:
        """Get recent sessions"""
        try:
            rows = self.db.execute(
                "SELECT * FROM sessions ORDER BY created_at DESC LIMIT ?",
                (limit,)
            )
            
            return [self._row_to_session(row) for row in rows]
        except Exception as e:
            self.logger.error(f"Failed to get recent sessions: {e}", exc_info=True)
            return []
    
    def _row_to_session(self, row: sqlite3.Row) -> StreamSession:
        """Convert database row to StreamSession"""
        config_data = json.loads(row['config_json'])
        config = StreamConfig.from_dict(config_data)
        
        marker = None
        if row['marker_json']:
            from ..models.scte35_marker import SCTE35Marker
            marker_data = json.loads(row['marker_json'])
            marker = SCTE35Marker.from_dict(marker_data)
        
        session = StreamSession(
            session_id=row['session_id'],
            config=config,
            marker=marker,
            status=row['status'],
            bytes_processed=row['bytes_processed'],
            packets_processed=row['packets_processed'],
            errors_count=row['errors_count'],
            scte35_injected=row['scte35_injected']
        )
        
        if row['start_time']:
            session.start_time = datetime.fromisoformat(row['start_time'])
        if row['stop_time']:
            session.stop_time = datetime.fromisoformat(row['stop_time'])
        if row['created_at']:
            session.created_at = datetime.fromisoformat(row['created_at'])
        
        return session
    
    def log_analytics(self, session_id: str, metric_name: str, metric_value: float, metadata: Dict = None):
        """Log analytics data"""
        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO analytics (session_id, timestamp, metric_name, metric_value, metadata)
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    session_id,
                    datetime.now().isoformat(),
                    metric_name,
                    metric_value,
                    json.dumps(metadata or {}, ensure_ascii=False)
                ))
                conn.commit()
        except Exception as e:
            self.logger.error(f"Failed to log analytics: {e}", exc_info=True)
    
    def log_audit(self, action: str, user: str = None, details: Dict = None):
        """Log audit event"""
        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO audit_log (timestamp, action, user, details)
                    VALUES (?, ?, ?, ?)
                """, (
                    datetime.now().isoformat(),
                    action,
                    user,
                    json.dumps(details or {}, ensure_ascii=False)
                ))
                conn.commit()
        except Exception as e:
            self.logger.error(f"Failed to log audit: {e}", exc_info=True)

