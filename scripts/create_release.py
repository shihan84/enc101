#!/usr/bin/env python3
"""
Create GitHub Release for IBE-210
Usage: python create_release.py <tag> [release_notes_file]
Example: python create_release.py v2.2.5 RELEASE_NOTES_v2.2.5.md
"""

import requests
import json
import os
import sys
from pathlib import Path

# GitHub API configuration
REPO_OWNER = "shihan84"
REPO_NAME = "enc101"

def read_release_notes(file_path: Path) -> str:
    """Read release notes from file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        print(f"[WARNING] Failed to read release notes file: {e}")
        return ""

def create_release(tag: str, release_notes_file: str = None, token: str = None):
    """Create GitHub release"""
    # Get GitHub token from multiple sources (priority order):
    # 1. Command-line argument
    # 2. Environment variable
    # 3. Config file (.github_token in script directory)
    GITHUB_TOKEN = None
    
    if token:
        GITHUB_TOKEN = token
    else:
        GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")
    
    # Try reading from config file if still not found
    if not GITHUB_TOKEN or GITHUB_TOKEN == "YOUR_GITHUB_TOKEN_HERE":
        script_dir = Path(__file__).parent
        token_file = script_dir / ".github_token"
        if token_file.exists():
            try:
                with open(token_file, 'r', encoding='utf-8') as f:
                    GITHUB_TOKEN = f.read().strip()
            except Exception as e:
                print(f"[WARNING] Failed to read token from file: {e}")
    
    if not GITHUB_TOKEN or GITHUB_TOKEN == "YOUR_GITHUB_TOKEN_HERE":
        print("[ERROR] GitHub token not found!")
        print()
        print("Please provide the token in one of these ways:")
        print()
        print("1. Command-line argument:")
        print("   python create_release.py v2.2.5 RELEASE_NOTES.md --token YOUR_TOKEN")
        print()
        print("2. Environment variable:")
        print("   Windows PowerShell: $env:GITHUB_TOKEN='your_token_here'")
        print("   Windows CMD: set GITHUB_TOKEN=your_token_here")
        print("   Linux/Mac: export GITHUB_TOKEN='your_token_here'")
        print()
        print("3. Config file:")
        print("   Create .github_token file in scripts/ directory with your token")
        print()
        print("To create a GitHub token:")
        print("1. Go to https://github.com/settings/tokens")
        print("2. Click 'Generate new token (classic)'")
        print("3. Select 'repo' scope")
        print("4. Copy the token")
        return None
    
    # Extract version from tag (e.g., v2.2.5 -> 2.2.5)
    version = tag.lstrip('v')
    release_name = f"IBE-210 v{version} Enterprise"
    
    # Read release notes if file provided
    release_body = ""
    if release_notes_file:
        notes_path = Path(release_notes_file)
        if not notes_path.is_absolute():
            # Try relative to script directory
            script_dir = Path(__file__).parent.parent
            notes_path = script_dir / release_notes_file
        
        if notes_path.exists():
            release_body = read_release_notes(notes_path)
        else:
            print(f"[WARNING] Release notes file not found: {notes_path}")
    
    # Default release body if no file provided
    if not release_body:
        release_body = f"""# IBE-210 v{version} Enterprise Release

## 🎉 Release {tag}

**IBE-210 Enterprise** - Professional Broadcast Encoding

## 📦 Installation

Download `IBE-210_Enterprise.exe` from the assets below.

## 📋 Changes

See the release notes for detailed changelog.

---

**IBE-210 Enterprise** - Professional Broadcast Encoding Made Easy 🚀
"""
    
    url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/releases"
    
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    data = {
        "tag_name": tag,
        "name": release_name,
        "body": release_body,
        "draft": False,
        "prerelease": False
    }
    
    print(f"Creating release {tag}...")
    print(f"Repository: {REPO_OWNER}/{REPO_NAME}")
    print(f"Release name: {release_name}")
    if release_notes_file:
        print(f"Release notes: {release_notes_file}")
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
        if hasattr(e, 'response') and e.response is not None:
            print(f"Response: {e.response.text}")
        return None

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python create_release.py <tag> [release_notes_file] [--token TOKEN]")
        print("Example: python create_release.py v2.2.5 RELEASE_NOTES_v2.2.5.md")
        print("Example: python create_release.py v2.2.5 RELEASE_NOTES_v2.2.5.md --token YOUR_TOKEN")
        sys.exit(1)
    
    tag = sys.argv[1]
    release_notes_file = None
    token = None
    
    # Parse arguments
    i = 2
    while i < len(sys.argv):
        if sys.argv[i] == "--token" and i + 1 < len(sys.argv):
            token = sys.argv[i + 1]
            i += 2
        else:
            if not release_notes_file:
                release_notes_file = sys.argv[i]
            i += 1
    
    create_release(tag, release_notes_file, token)

