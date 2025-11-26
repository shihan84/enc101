# Release Notes - IBE-210 Enterprise v2.2.5

## 🐛 Critical Fixes

### Profile-Specific Dynamic Marker Directory Path Resolution

**Issue**: TSDuck command was using incorrect directory path (`scte35_final/dynamic_markers/` instead of `scte35_final/{profile_name}/dynamic_markers/`), causing markers to be generated in the wrong location and not being injected into the stream.

**Root Cause**: The dynamic marker directory path was not being properly re-resolved after profile changes, and profile sync validation was insufficient.

**Fixes Applied**:

1. **Enhanced Profile Sync Validation** (`stream_service.py`):
   - Added aggressive profile sync checks before starting dynamic marker generation
   - Added detailed logging to track profile synchronization between SCTE35Service and DynamicMarkerService
   - Added critical error messages when profile directory path doesn't match expected profile name
   - Added clear instructions in error messages for users to load profile before starting stream

2. **Improved Directory Path Resolution** (`dynamic_marker_service.py`):
   - Enhanced `get_dynamic_markers_dir()` to re-resolve path on each call, ensuring latest path is always returned
   - Improved `set_profile()` with better logging and path verification
   - Added path validation to ensure profile name is present in directory path
   - Added error detection when profile name is missing from path

3. **Better Error Reporting**:
   - Added clear error messages with ✅/❌ indicators for easy identification
   - Added step-by-step instructions when profile path is incorrect
   - Enhanced logging to show profile sync status and directory paths

## 📋 Changes Summary

### Modified Files:
- `src/services/stream_service.py`: Enhanced profile sync and path validation
- `src/services/dynamic_marker_service.py`: Improved directory path resolution and validation
- `src/core/config.py`: Version updated to 2.2.5
- `main_enterprise.py`: Version comment updated to 2.2.5

## 🔍 Technical Details

### Profile Directory Structure
The application now correctly uses profile-specific directories:
- **Default Profile**: `scte35_final/dynamic_markers/`
- **Named Profile (e.g., "lokmanch")**: `scte35_final/lokmanch/dynamic_markers/`

### Path Resolution Flow
1. When profile is loaded in UI → `set_profile()` is called on both services
2. When stream starts → Profile sync is verified and corrected if needed
3. Directory path is re-resolved before building TSDuck command
4. Path is validated to ensure it contains the profile name

### Error Detection
The application now detects and reports:
- Profile mismatch between services
- Missing profile name in directory path
- Incorrect directory structure

## ⚠️ Important Notes

### User Action Required
**Before starting a stream with a profile:**
1. Go to **Configuration** tab
2. Select your profile from the dropdown
3. Click **Load Profile**
4. Wait for confirmation message
5. Then start the stream

If you see an error message about incorrect profile directory path, follow the instructions in the error message.

## 🚀 Upgrade Instructions

1. Stop any running streams
2. Replace the executable with the new version
3. Test with your profile:
   - Load your profile in Configuration tab
   - Start a stream with a marker
   - Verify the TSDuck command shows the correct profile directory path
   - Check that SCTE-35 bitrate > 0 in monitoring

## 📊 Verification

After upgrading, verify:
- ✅ Profile directory path in logs contains profile name
- ✅ TSDuck command uses correct directory: `scte35_final/{profile_name}/dynamic_markers/splice*.xml`
- ✅ SCTE-35 bitrate > 0 in monitoring output
- ✅ Markers are being generated in the correct directory

## 🔗 Related Issues

This release addresses the issue where:
- TSDuck command showed: `--files C:\ENC210\scte35_final\dynamic_markers\splice*.xml`
- Should show: `--files C:\ENC210\scte35_final\lokmanch\dynamic_markers\splice*.xml`
- SCTE-35 bitrate was 0 b/s because markers weren't being found

---

**Release Date**: 2025-01-27  
**Version**: 2.2.5  
**Build**: Enterprise Edition

