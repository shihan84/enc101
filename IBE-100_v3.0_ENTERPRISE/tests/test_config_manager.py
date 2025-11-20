"""
Unit tests for configuration manager
"""

import unittest
import sys
import json
from pathlib import Path
from tempfile import TemporaryDirectory

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from src.core.config import ConfigManager, Config


class TestConfigManager(unittest.TestCase):
    """Test configuration manager"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = TemporaryDirectory()
        self.config_path = Path(self.temp_dir.name) / "test_config.json"
        self.manager = ConfigManager(config_path=self.config_path)
    
    def tearDown(self):
        """Clean up"""
        self.temp_dir.cleanup()
    
    def test_load_default_config(self):
        """Test loading default configuration"""
        config = self.manager.load()
        self.assertIsNotNone(config)
        self.assertEqual(config.app_name, "IBE-100 Enterprise")
        self.assertEqual(config.app_version, "3.0.0")
    
    def test_save_and_load(self):
        """Test saving and loading configuration"""
        config = self.manager.load()
        config.log_level = "DEBUG"
        self.manager.save(config)
        
        # Load again
        loaded_config = self.manager.load()
        self.assertEqual(loaded_config.log_level, "DEBUG")
    
    def test_encryption(self):
        """Test configuration encryption"""
        config = self.manager.load()
        config.telegram_bot_token = "test_token_123"
        self.manager.save(config)
        
        # Verify encrypted
        config_data = json.loads(self.config_path.read_text())
        # Encrypted values should not be plain text
        self.assertNotEqual(config_data.get('telegram_bot_token'), "test_token_123")
        
        # Load and verify decryption
        loaded_config = self.manager.load()
        self.assertEqual(loaded_config.telegram_bot_token, "test_token_123")


if __name__ == '__main__':
    unittest.main()

