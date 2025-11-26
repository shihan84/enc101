# Code Signing Guide for IBE-210 Enterprise

## Overview

Windows shows "unidentified publisher" warnings for unsigned executables. This guide explains how to add version information and optionally code-sign your application.

## Current Status

✅ **Version Information Added**: The application now includes version info that shows:
- Company Name: ITAssist Broadcast Solutions
- Product Name: IBE-210 Enterprise
- File Version: 2.2.6.0
- Product Version: 2.2.6.0
- Copyright: Copyright (C) 2024 ITAssist Broadcast Solutions

This reduces the warning but doesn't eliminate it completely.

## Option 1: Version Information Only (Current Implementation)

**Status**: ✅ Implemented

The `version_info.txt` file has been created and added to the PyInstaller spec. This provides:
- File version information visible in Windows Properties
- Company and product information
- Better appearance in Windows Explorer

**Limitations**:
- Still shows "unidentified publisher" warning
- Windows SmartScreen may still block the application

## Option 2: Code Signing (Recommended for Distribution)

To completely eliminate the "unidentified publisher" warning, you need to **code-sign** the executable.

### Requirements

1. **Code Signing Certificate**:
   - Purchase from a Certificate Authority (CA) like:
     - DigiCert (~$200-400/year)
     - Sectigo (~$200-300/year)
     - GlobalSign (~$200-400/year)
   - Or use a self-signed certificate (not recommended for distribution)

2. **Signing Tools**:
   - `signtool.exe` (included with Windows SDK)
   - Or use `signtool` from Visual Studio

### Code Signing Process

#### Step 1: Obtain Certificate

**Option A: Purchase from CA (Recommended)**
1. Purchase a code signing certificate from a trusted CA
2. Install the certificate in Windows Certificate Store
3. Export as `.pfx` file if needed

**Option B: Self-Signed (Testing Only)**
```powershell
# Create self-signed certificate (for testing only)
New-SelfSignedCertificate -Type CodeSigningCert -Subject "CN=ITAssist Broadcast Solutions" -CertStoreLocation Cert:\CurrentUser\My
```

#### Step 2: Sign the Executable

**Using signtool.exe:**

```powershell
# Sign with certificate from store
signtool sign /f "certificate.pfx" /p "password" /t http://timestamp.digicert.com /d "IBE-210 Enterprise" /du "https://github.com/shihan84/enc101" "dist\IBE-210_Enterprise.exe"

# Or sign with certificate from Windows Certificate Store
signtool sign /a /t http://timestamp.digicert.com /d "IBE-210 Enterprise" /du "https://github.com/shihan84/enc101" "dist\IBE-210_Enterprise.exe"
```

**Using Python script:**

```python
import subprocess
import sys

def sign_executable(exe_path, cert_path, cert_password, timestamp_url="http://timestamp.digicert.com"):
    """Sign executable with code signing certificate"""
    cmd = [
        "signtool", "sign",
        "/f", cert_path,
        "/p", cert_password,
        "/t", timestamp_url,
        "/d", "IBE-210 Enterprise",
        "/du", "https://github.com/shihan84/enc101",
        exe_path
    ]
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print(f"✅ Successfully signed: {exe_path}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Signing failed: {e}")
        print(f"Output: {e.stdout}")
        print(f"Error: {e.stderr}")
        return False

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Usage: python sign_exe.py <exe_path> <cert_path> <cert_password>")
        sys.exit(1)
    
    sign_executable(sys.argv[1], sys.argv[2], sys.argv[3])
```

#### Step 3: Verify Signature

```powershell
# Verify signature
signtool verify /pa "dist\IBE-210_Enterprise.exe"
```

### Automated Signing Script

Create `scripts/sign_executable.py`:

```python
#!/usr/bin/env python3
"""
Code Signing Script for IBE-210 Enterprise
"""

import subprocess
import sys
from pathlib import Path

def sign_executable(
    exe_path: Path,
    cert_path: Path = None,
    cert_password: str = None,
    use_store: bool = True,
    timestamp_url: str = "http://timestamp.digicert.com"
):
    """Sign executable with code signing certificate"""
    
    if not exe_path.exists():
        print(f"❌ Executable not found: {exe_path}")
        return False
    
    if use_store:
        # Sign with certificate from Windows Certificate Store
        cmd = [
            "signtool", "sign",
            "/a",  # Automatically select certificate
            "/t", timestamp_url,
            "/d", "IBE-210 Enterprise",
            "/du", "https://github.com/shihan84/enc101",
            str(exe_path)
        ]
    else:
        # Sign with certificate file
        if not cert_path or not cert_password:
            print("❌ Certificate path and password required when not using certificate store")
            return False
        
        cmd = [
            "signtool", "sign",
            "/f", str(cert_path),
            "/p", cert_password,
            "/t", timestamp_url,
            "/d", "IBE-210 Enterprise",
            "/du", "https://github.com/shihan84/enc101",
            str(exe_path)
        ]
    
    try:
        print(f"🔐 Signing {exe_path}...")
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print(f"✅ Successfully signed: {exe_path}")
        print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Signing failed: {e}")
        if e.stdout:
            print(f"Output: {e.stdout}")
        if e.stderr:
            print(f"Error: {e.stderr}")
        return False
    except FileNotFoundError:
        print("❌ signtool.exe not found!")
        print("Please install Windows SDK or Visual Studio")
        return False

def verify_signature(exe_path: Path):
    """Verify executable signature"""
    cmd = ["signtool", "verify", "/pa", str(exe_path)]
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print(f"✅ Signature verified: {exe_path}")
        print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Signature verification failed: {e}")
        return False

if __name__ == "__main__":
    exe_path = Path("dist/IBE-210_Enterprise.exe")
    
    if len(sys.argv) > 1:
        exe_path = Path(sys.argv[1])
    
    # Try signing with certificate store first
    if sign_executable(exe_path, use_store=True):
        verify_signature(exe_path)
    else:
        print("\nTo sign with a certificate file:")
        print("python scripts/sign_executable.py <exe_path> <cert_path> <cert_password>")
```

## Option 3: Windows Defender SmartScreen

Even with code signing, Windows SmartScreen may still show warnings for:
- New applications (not enough reputation)
- Applications from unknown publishers

**Solutions**:
1. **Build Reputation**: Distribute through trusted channels
2. **Submit to Microsoft**: Submit your application to Microsoft for analysis
3. **User Education**: Inform users to click "More info" → "Run anyway"

## Current Implementation

✅ Version information is included in the build
- Shows proper company and product information
- Reduces but doesn't eliminate warnings

## Recommendations

1. **For Development/Testing**: Current implementation (version info only) is sufficient
2. **For Distribution**: Purchase a code signing certificate and sign the executable
3. **For Internal Use**: Self-signed certificate may be acceptable

## Next Steps

1. **Immediate**: Version info is already added - rebuild to see improvements
2. **Short-term**: Consider purchasing a code signing certificate if distributing publicly
3. **Long-term**: Build reputation with Microsoft SmartScreen

---

**Note**: Code signing certificates typically cost $200-400/year. For internal use or testing, the current version info implementation may be sufficient.

