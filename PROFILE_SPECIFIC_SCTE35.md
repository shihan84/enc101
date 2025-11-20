# ✅ Profile-Specific SCTE-35 Marker Directories

## Problem
When running multiple instances of the application, all instances were using the same SCTE-35 marker directory, causing conflicts and confusion. Each instance should have its own marker directory based on the profile being used.

## Solution Implemented

### 1. Profile-Based Directory Structure
- ✅ **Profile-Specific Folders**: Each profile gets its own SCTE-35 marker directory
- ✅ **Directory Naming**: `scte35_final/{profile_name}/`
- ✅ **Safe Naming**: Profile names are sanitized for filesystem compatibility
- ✅ **Default Profile**: Uses `scte35_final/` for default profile

### 2. Profile-Specific Event ID State
- ✅ **Separate State Files**: Each profile has its own `.scte35_state.json`
- ✅ **Independent Event IDs**: Each profile tracks its own event ID sequence
- ✅ **No Conflicts**: Multiple instances can run without ID conflicts

### 3. Dynamic Profile Switching
- ✅ **Profile Change Detection**: Automatically switches when profile is loaded
- ✅ **Directory Update**: Service updates directory when profile changes
- ✅ **State Preservation**: Each profile maintains its own event ID state

## Directory Structure

```
scte35_final/
├── .scte35_state.json              # Default profile state
├── cue_out_10023_1234567890.xml
├── cue_in_10024_1234567891.xml
│
├── Distributor_SRT/                # Profile-specific folder
│   ├── .scte35_state.json         # Profile state
│   ├── cue_out_10023_1234567890.xml
│   └── cue_in_10024_1234567891.xml
│
├── HLS_Output/                     # Another profile
│   ├── .scte35_state.json
│   ├── cue_out_10023_1234567890.xml
│   └── cue_in_10024_1234567891.xml
│
└── Custom_Profile_Name/            # Custom profile
    ├── .scte35_state.json
    └── ...
```

## How It Works

### Scenario: Multiple Instances

**Instance 1 - Profile: "Distributor_SRT"**
- Markers saved to: `scte35_final/Distributor_SRT/`
- Event IDs: 10023, 10024, 10025...
- State file: `scte35_final/Distributor_SRT/.scte35_state.json`

**Instance 2 - Profile: "HLS_Output"**
- Markers saved to: `scte35_final/HLS_Output/`
- Event IDs: 10023, 10024, 10025... (independent sequence)
- State file: `scte35_final/HLS_Output/.scte35_state.json`

**Instance 3 - Profile: "default"**
- Markers saved to: `scte35_final/`
- Event IDs: 10023, 10024, 10025... (independent sequence)
- State file: `scte35_final/.scte35_state.json`

### Profile Switching

1. **User loads profile "Distributor_SRT"**
   - SCTE-35 service switches to: `scte35_final/Distributor_SRT/`
   - Loads event ID state from that profile's state file
   - UI updates to show current directory

2. **User loads profile "HLS_Output"**
   - SCTE-35 service switches to: `scte35_final/HLS_Output/`
   - Loads event ID state from that profile's state file
   - UI updates to show current directory

3. **Each profile maintains independent event ID sequence**

## Technical Implementation

### SCTE35Service Changes

```python
def __init__(self, markers_dir: Path = None, profile_name: str = None):
    self.profile_name = profile_name or "default"
    
    # Profile-specific directory
    if profile_name and profile_name != "default":
        safe_name = sanitize_profile_name(profile_name)
        self.markers_dir = Path("scte35_final") / safe_name
    else:
        self.markers_dir = Path("scte35_final")
    
    # Profile-specific state file
    self.state_file = self.markers_dir / ".scte35_state.json"

def set_profile(self, profile_name: str):
    """Switch to profile-specific directory"""
    # Update directory and state file
    # Load profile-specific event ID state
```

### UI Integration

```python
# StreamConfigWidget emits signal when profile loaded
profile_loaded = pyqtSignal(str)

# MainWindow connects signal
config_widget.profile_loaded.connect(self._on_profile_loaded)

# Update SCTE-35 service
scte35_service.set_profile(profile_name)
```

## Benefits

- ✅ **No Conflicts**: Multiple instances can run simultaneously
- ✅ **Organized**: Markers organized by profile
- ✅ **Independent**: Each profile has its own event ID sequence
- ✅ **Persistent**: Event IDs persist per profile
- ✅ **Automatic**: Switches automatically when profile is loaded
- ✅ **Safe**: Profile names sanitized for filesystem compatibility

## Usage

1. **Load Profile**: Select and load a profile in Configuration tab
2. **Automatic Switch**: SCTE-35 service automatically switches to profile directory
3. **Generate Markers**: Markers are saved to profile-specific folder
4. **Event IDs**: Each profile maintains its own incremental event ID sequence
5. **Multiple Instances**: Run multiple instances with different profiles - no conflicts!

## Example

**Instance 1:**
- Profile: "Distributor_SRT"
- Directory: `scte35_final/Distributor_SRT/`
- Generate CUE Pair → IDs: 10023, 10024

**Instance 2:**
- Profile: "HLS_Output"
- Directory: `scte35_final/HLS_Output/`
- Generate CUE Pair → IDs: 10023, 10024 (independent!)

**Both instances can run simultaneously without conflicts!**

---

**Status**: ✅ **IMPLEMENTED - Profile-Specific SCTE-35 Marker Directories**

