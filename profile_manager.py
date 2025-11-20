"""
Profile Manager for IBE-100
Manages configuration profiles for different stream setups
"""

import json
from pathlib import Path
from datetime import datetime

class ProfileManager:
    """Manage stream configuration profiles"""
    
    def __init__(self):
        self.profiles_dir = Path("profiles")
        self.profiles_dir.mkdir(exist_ok=True)
        self.profiles_file = self.profiles_dir / "profiles.json"
        self.profiles = {}
        self.load_profiles()
    
    def load_profiles(self):
        """Load all profiles from disk"""
        if self.profiles_file.exists():
            try:
                with open(self.profiles_file, 'r', encoding='utf-8') as f:
                    self.profiles = json.load(f)
            except Exception as e:
                print(f"[ERROR] Failed to load profiles: {e}")
                self.profiles = {}
        else:
            # Create default profiles
            self.create_default_profiles()
    
    def save_profiles(self):
        """Save all profiles to disk"""
        try:
            with open(self.profiles_file, 'w', encoding='utf-8') as f:
                json.dump(self.profiles, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"[ERROR] Failed to save profiles: {e}")
            return False
    
    def create_default_profiles(self):
        """Create default profile templates"""
        defaults = {
            "Distributor_SRT": {
                "name": "Distributor SRT",
                "description": "Standard distributor SRT output",
                "created": datetime.now().isoformat(),
                "config": {
                    "input_type": "HLS (HTTP Live Streaming)",
                    "input_url": "https://cdn.example.com/stream/index.m3u8",
                    "output_type": "SRT",
                    "output_srt": "server.com:9045",
                    "stream_id": "",
                    "latency": 2000,
                    "service_id": 1,
                    "service_name": "SCTE-35 Stream",
                    "provider_name": "ITAssist",
                    "vpid": 256,
                    "apid": 257,
                    "scte35_pid": 500,
                    "start_delay": 2000,
                    "inject_count": 1,
                    "inject_interval": 1000
                }
            },
            "HLS_Output": {
                "name": "HLS Output",
                "description": "HLS streaming with CORS",
                "created": datetime.now().isoformat(),
                "config": {
                    "input_type": "SRT (Secure Reliable Transport)",
                    "input_url": "srt://source:8088",
                    "output_type": "HLS",
                    "output_hls": "output/hls",
                    "segment_duration": 6,
                    "playlist_window": 5,
                    "enable_cors": True,
                    "service_id": 1,
                    "service_name": "HLS Stream",
                    "provider_name": "ITAssist",
                    "vpid": 256,
                    "apid": 257,
                    "scte35_pid": 500
                }
            },
            "Trial_Stream": {
                "name": "Trial Stream",
                "description": "Basic trial configuration",
                "created": datetime.now().isoformat(),
                "config": {
                    "input_type": "HLS (HTTP Live Streaming)",
                    "input_url": "https://cdn.example.com/stream/index.m3u8",
                    "output_type": "SRT",
                    "output_srt": "trial.server.com:8888",
                    "stream_id": "",
                    "latency": 2000,
                    "service_id": 1,
                    "service_name": "Trial Stream",
                    "provider_name": "ITAssist",
                    "vpid": 256,
                    "apid": 257,
                    "scte35_pid": 500
                }
            }
        }
        
        self.profiles.update(defaults)
        self.save_profiles()
    
    def get_profile_names(self):
        """Get list of all profile names"""
        return list(self.profiles.keys())
    
    def get_profile(self, profile_name):
        """Get profile configuration by name"""
        if profile_name in self.profiles:
            return self.profiles[profile_name].get("config", {})
        return None
    
    def save_profile(self, profile_name, config, description=""):
        """Save a new profile or update existing"""
        self.profiles[profile_name] = {
            "name": profile_name,
            "description": description,
            "created": self.profiles.get(profile_name, {}).get("created", datetime.now().isoformat()),
            "modified": datetime.now().isoformat(),
            "config": config
        }
        return self.save_profiles()
    
    def delete_profile(self, profile_name):
        """Delete a profile"""
        if profile_name in self.profiles:
            del self.profiles[profile_name]
            return self.save_profiles()
        return False
    
    def rename_profile(self, old_name, new_name):
        """Rename a profile"""
        if old_name in self.profiles and new_name not in self.profiles:
            profile = self.profiles.pop(old_name)
            profile["name"] = new_name
            profile["modified"] = datetime.now().isoformat()
            self.profiles[new_name] = profile
            return self.save_profiles()
        return False
    
    def get_profile_info(self, profile_name):
        """Get profile metadata"""
        if profile_name in self.profiles:
            return {
                "name": self.profiles[profile_name].get("name"),
                "description": self.profiles[profile_name].get("description", ""),
                "created": self.profiles[profile_name].get("created"),
                "modified": self.profiles[profile_name].get("modified", "")
            }
        return None

