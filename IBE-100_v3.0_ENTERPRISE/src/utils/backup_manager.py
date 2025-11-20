"""
Automated backup manager for database and configuration
"""

import shutil
from pathlib import Path
from datetime import datetime
from typing import Optional
from ..core.logger import get_logger


class BackupManager:
    """Manages automated backups of database and configuration"""
    
    def __init__(self, backup_dir: Path = None, max_backups: int = 10):
        """
        Initialize backup manager
        
        Args:
            backup_dir: Directory to store backups
            max_backups: Maximum number of backups to keep
        """
        self.logger = get_logger("BackupManager")
        self.backup_dir = backup_dir or Path("backups")
        self.backup_dir.mkdir(exist_ok=True)
        self.max_backups = max_backups
    
    def backup_database(self, db_path: Path) -> Optional[Path]:
        """
        Backup database file
        
        Args:
            db_path: Path to database file
        
        Returns:
            Path to backup file, or None if backup failed
        """
        if not db_path or not db_path.exists():
            self.logger.warning(f"Database file not found: {db_path}")
            return None
        
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_filename = f"database_{timestamp}.db"
            backup_path = self.backup_dir / backup_filename
            
            shutil.copy2(db_path, backup_path)
            self.logger.info(f"Database backed up to: {backup_path}")
            
            # Cleanup old backups
            self._cleanup_old_backups("database_")
            
            return backup_path
        except Exception as e:
            self.logger.error(f"Failed to backup database: {e}")
            return None
    
    def backup_config(self, config_dir: Path) -> Optional[Path]:
        """
        Backup configuration directory
        
        Args:
            config_dir: Path to configuration directory
        
        Returns:
            Path to backup directory, or None if backup failed
        """
        if not config_dir or not config_dir.exists():
            self.logger.warning(f"Config directory not found: {config_dir}")
            return None
        
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_dirname = f"config_{timestamp}"
            backup_path = self.backup_dir / backup_dirname
            
            shutil.copytree(config_dir, backup_path, dirs_exist_ok=True)
            self.logger.info(f"Configuration backed up to: {backup_path}")
            
            # Cleanup old backups
            self._cleanup_old_backups("config_")
            
            return backup_path
        except Exception as e:
            self.logger.error(f"Failed to backup configuration: {e}")
            return None
    
    def backup_profiles(self, profiles_dir: Path) -> Optional[Path]:
        """
        Backup profiles directory
        
        Args:
            profiles_dir: Path to profiles directory
        
        Returns:
            Path to backup directory, or None if backup failed
        """
        if not profiles_dir or not profiles_dir.exists():
            self.logger.warning(f"Profiles directory not found: {profiles_dir}")
            return None
        
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_dirname = f"profiles_{timestamp}"
            backup_path = self.backup_dir / backup_dirname
            
            shutil.copytree(profiles_dir, backup_path, dirs_exist_ok=True)
            self.logger.info(f"Profiles backed up to: {backup_path}")
            
            # Cleanup old backups
            self._cleanup_old_backups("profiles_")
            
            return backup_path
        except Exception as e:
            self.logger.error(f"Failed to backup profiles: {e}")
            return None
    
    def create_full_backup(self, db_path: Path, config_dir: Path, profiles_dir: Path) -> Optional[Path]:
        """
        Create full backup of all data
        
        Args:
            db_path: Path to database file
            config_dir: Path to configuration directory
            profiles_dir: Path to profiles directory
        
        Returns:
            Path to backup directory, or None if backup failed
        """
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_dirname = f"full_backup_{timestamp}"
            backup_path = self.backup_dir / backup_dirname
            backup_path.mkdir(exist_ok=True)
            
            # Backup database
            if db_path and db_path.exists():
                shutil.copy2(db_path, backup_path / "database.db")
            
            # Backup config
            if config_dir and config_dir.exists():
                shutil.copytree(config_dir, backup_path / "config", dirs_exist_ok=True)
            
            # Backup profiles
            if profiles_dir and profiles_dir.exists():
                shutil.copytree(profiles_dir, backup_path / "profiles", dirs_exist_ok=True)
            
            self.logger.info(f"Full backup created at: {backup_path}")
            
            # Cleanup old backups
            self._cleanup_old_backups("full_backup_")
            
            return backup_path
        except Exception as e:
            self.logger.error(f"Failed to create full backup: {e}")
            return None
    
    def _cleanup_old_backups(self, prefix: str):
        """Remove old backups, keeping only the most recent ones"""
        try:
            backups = sorted(
                [p for p in self.backup_dir.iterdir() if p.name.startswith(prefix)],
                key=lambda p: p.stat().st_mtime,
                reverse=True
            )
            
            # Remove old backups
            for backup in backups[self.max_backups:]:
                try:
                    if backup.is_file():
                        backup.unlink()
                    else:
                        shutil.rmtree(backup)
                    self.logger.debug(f"Removed old backup: {backup}")
                except Exception as e:
                    self.logger.warning(f"Failed to remove old backup {backup}: {e}")
        except Exception as e:
            self.logger.error(f"Failed to cleanup old backups: {e}")
    
    def list_backups(self, backup_type: str = None) -> list:
        """
        List available backups
        
        Args:
            backup_type: Type of backup to list (database, config, profiles, full_backup)
        
        Returns:
            List of backup paths
        """
        try:
            if backup_type:
                prefix = f"{backup_type}_"
                backups = [p for p in self.backup_dir.iterdir() if p.name.startswith(prefix)]
            else:
                backups = list(self.backup_dir.iterdir())
            
            return sorted(backups, key=lambda p: p.stat().st_mtime, reverse=True)
        except Exception as e:
            self.logger.error(f"Failed to list backups: {e}")
            return []

