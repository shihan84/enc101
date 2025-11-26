# Release Notes - IBE-210 Enterprise v2.2.6

## 🐛 Critical Bug Fixes

### Application Crash Fixes

**Issue**: Application was crashing when accessing dynamic marker directory paths, especially when:
- Directory path was not properly initialized
- Profile was changed after initialization
- Directory path resolution failed

**Root Cause**: The `get_dynamic_markers_dir()` and related methods were calling `resolve()` on potentially `None` or uninitialized directory paths without proper error handling.

**Fixes Applied**:

1. **Enhanced `get_dynamic_markers_dir()` Method** (`dynamic_marker_service.py`):
   - Added defensive None checks before calling `resolve()`
   - Added automatic reinitialization if directory is missing or invalid
   - Added try/except blocks to handle path resolution errors gracefully
   - Improved error logging for debugging

2. **Enhanced `set_profile()` Method** (`dynamic_marker_service.py`):
   - Added None checks before resolving directory paths
   - Added try/except blocks for safe path resolution
   - Added fallback reinitialization if path resolution fails

3. **Enhanced `get_profile_directory()` Method** (`dynamic_marker_service.py`):
   - Now calls `get_dynamic_markers_dir()` first to ensure directory is initialized
   - Prevents crashes when accessing `parent` attribute

## 📋 Changes Summary

### Modified Files:
- `src/services/dynamic_marker_service.py`: Added defensive programming and error handling
- `src/core/config.py`: Version updated to 2.2.6
- `main_enterprise.py`: Version comment updated to 2.2.6

## 🔍 Technical Details

### Defensive Programming Improvements

1. **None Checks**: All methods now check if `dynamic_markers_dir` is `None` before use
2. **Automatic Recovery**: If directory is missing, methods automatically reinitialize it
3. **Error Handling**: Try/except blocks catch and handle path resolution errors
4. **Logging**: Enhanced error logging helps identify issues during runtime

### Error Prevention

The application now handles these edge cases gracefully:
- Directory not initialized during service creation
- Profile change before directory is set
- Path resolution failures due to filesystem issues
- Missing parent directories

## ⚠️ Important Notes

### Stability Improvements

This release significantly improves application stability by:
- Preventing crashes from uninitialized directory paths
- Automatically recovering from path resolution errors
- Providing better error messages for debugging

### No Breaking Changes

- All existing functionality remains the same
- No configuration changes required
- No migration needed

## 🚀 Upgrade Instructions

1. Stop any running streams
2. Replace the executable with the new version
3. No additional configuration needed
4. Test the application to verify stability

## 📊 Verification

After upgrading, verify:
- ✅ Application starts without crashes
- ✅ Profile switching works correctly
- ✅ Dynamic marker generation works as expected
- ✅ No errors in logs related to directory paths

## 🔗 Related Issues

This release fixes crashes that occurred when:
- Starting streams with profiles
- Switching profiles during runtime
- Accessing dynamic marker directories before initialization

---

**Release Date**: 2025-01-27  
**Version**: 2.2.6  
**Build**: Enterprise Edition

