#!/usr/bin/env python3
"""
Create GitHub Release for IBE-210 v2.1.0
"""

import requests
import json
import os
from pathlib import Path

# GitHub API configuration
# Note: Set GITHUB_TOKEN environment variable or replace with your token
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "YOUR_GITHUB_TOKEN_HERE")
REPO_OWNER = "shihan84"
REPO_NAME = "enc101"
TAG = "v2.2.0"
RELEASE_NAME = "IBE-210 v2.2.0 Enterprise"
RELEASE_BODY = """# IBE-210 v2.2.0 Enterprise Release

## 🎉 What's New

**IBE-210** is the next generation of the IBE broadcast encoder with **bundled TSDuck support**.

### ✨ Key Features

1. **Bundled TSDuck** 🎁
   - TSDuck binaries included in the application package
   - No separate TSDuck installation required
   - Works out of the box
   - Hybrid approach: Uses bundled TSDuck first, falls back to system TSDuck

2. **All Features from IBE-100 v3.0**
   - SCTE-35 marker injection and monitoring
   - Real-time stream analysis
   - EPG/EIT generation
   - Telegram notifications
   - Profile management
   - REST API
   - And more...

## 📦 Installation

### Download

Download `IBE-210_Enterprise.exe` from the assets below.

### Quick Start

1. **Launch IBE-210**
2. **Configure your stream** (Input/Output settings)
3. **Start streaming** - TSDuck is ready to use!

No need to install TSDuck separately!

## 📋 System Requirements

- **Windows 10/11** (64-bit)
- **TSDuck**: Included (bundled) or install separately

## 🔄 How Bundled TSDuck Works

IBE-210 uses a **hybrid approach**:

1. **First Priority**: Bundled TSDuck (included in package)
2. **Second Priority**: System TSDuck (if installed)
3. **Third Priority**: Custom path (user-specified)

This ensures maximum compatibility and flexibility.

## 📝 Version History

### v2.1.0 (IBE-210)
- ✨ Added bundled TSDuck support
- ✨ Hybrid TSDuck detection (bundled → system → custom)
- 🔧 Improved TSDuck environment setup
- 📦 Larger package size (~88 MB with TSDuck)

### v3.0.0 (IBE-100)
- All previous features
- Production-ready
- Comprehensive testing

## ⚖️ Licensing

**Important**: TSDuck is licensed under **GNU GPL v2**.

If you bundle TSDuck:
- Your application must be GPL (open-source), OR
- Purchase commercial license from TSDuck developers

## 🆘 Support

For issues, questions, or contributions:
- Check documentation in the repository
- Review troubleshooting guides

---

**IBE-210 Enterprise** - Professional Broadcast Encoding Made Easy 🚀
"""

def create_release():
    """Create GitHub release"""
    url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/releases"
    
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    data = {
        "tag_name": TAG,
        "name": RELEASE_NAME,
        "body": RELEASE_BODY,
        "draft": False,
        "prerelease": False
    }
    
    print(f"Creating release {TAG}...")
    print(f"Repository: {REPO_OWNER}/{REPO_NAME}")
    print()
    
    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        
        release_data = response.json()
        print("[SUCCESS] Release created successfully!")
        print()
        print(f"Release URL: {release_data['html_url']}")
        print(f"Tag: {release_data['tag_name']}")
        print()
        print("Next: Upload the executable as a release asset")
        
        return release_data
    except requests.exceptions.RequestException as e:
        print(f"[ERROR] Failed to create release: {e}")
        if hasattr(e.response, 'text'):
            print(f"Response: {e.response.text}")
        return None

if __name__ == "__main__":
    create_release()

