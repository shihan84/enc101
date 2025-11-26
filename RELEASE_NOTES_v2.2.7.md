# Release Notes - IBE-210 Enterprise v2.2.7

## 🐛 Critical Bug Fixes

### SCTE-35 Marker Injection Fixes

**Issue**: SCTE-35 markers were not being injected into the stream, resulting in:
- SCTE-35 bitrate showing 0 b/s in monitoring
- Markers not being detected by downstream systems
- Event IDs not incrementing correctly

**Root Cause**: Multiple issues were identified:
1. TSDuck `--delete-files` option was deleting marker files before they could be injected
2. Marker files were being created in wrong directory (`scte35_final\` instead of `scte35_final\dynamic_markers\`)
3. File timing issues - markers not ready when TSDuck started polling
4. Multiple marker files causing confusion for TSDuck

**Fixes Applied**:

1. **Removed `--delete-files` from TSDuck Command** (`tsduck_service.py`):
   - TSDuck no longer deletes marker files automatically
   - Files now persist until the next marker is generated
   - Ensures TSDuck has time to inject markers before deletion

2. **Manual File Deletion** (`dynamic_marker_service.py`):
   - Implemented manual deletion of old `splice*.xml` files before creating new ones
   - Ensures only one marker file exists at a time
   - Prevents TSDuck from processing stale or duplicate files

3. **Simplified Directory Structure**:
   - Changed from `scte35_final\dynamic_markers\` to `scte35_final\` directly
   - Removed profile-based subdirectories (using general directory)
   - Simplified path resolution and reduced complexity

4. **Improved File Timing**:
   - First marker generated *before* TSDuck process starts
   - Added 1.0 second delay after marker generation to ensure file stability
   - Added `--min-stable-delay 500` to TSDuck command for file stability

5. **Enhanced File Writing**:
   - Added explicit file flushing (`f.flush()` and `os.fsync()`)
   - Added file verification after writing (checking existence and size)
   - Added comprehensive logging for debugging

6. **Event ID Incrementation**:
   - Event IDs now increment correctly: 10025 → 10026 → 10027...
   - Each marker gets a unique, sequential event ID
   - Proper tracking of marker generation count

## 📋 Changes Summary

### Modified Files:
- `src/services/dynamic_marker_service.py`: 
  - Simplified directory structure to use `scte35_final\` directly
  - Implemented manual file deletion before marker creation
  - Added robust file writing with flushing and verification
  - Enhanced logging for debugging
  - Fixed event ID incrementation
- `src/services/tsduck_service.py`:
  - Removed `--delete-files` from `spliceinject` command
  - Added `--min-stable-delay 500` for file stability
  - Updated logging to show absolute paths
- `src/services/stream_service.py`:
  - Generate first marker before starting TSDuck process
  - Added 1.0 second delay to ensure file stability
- `src/core/config.py`: Version updated to 2.2.7
- `main_enterprise.py`: Version comment updated to 2.2.7
- `version_info.txt`: FileVersion and ProductVersion updated to 2.2.7.0

## 🔍 Technical Details

### Marker File Management

**Before**:
- TSDuck deleted files immediately after injection
- Multiple files could exist simultaneously
- Files created in wrong directory
- Timing issues with file creation

**After**:
- Manual deletion of old files before creating new ones
- Only one marker file exists at a time
- Files created in correct directory (`scte35_final\`)
- Proper timing with file stability delays

### Directory Structure

**Before**:
```
scte35_final\
  └── dynamic_markers\
      └── splice_10024_*.xml
```

**After**:
```
scte35_final\
  └── splice_10024_*.xml
```

### TSDuck Command Changes

**Before**:
```bash
spliceinject --directory "C:\ENC210\scte35_final\dynamic_markers" --delete-files
```

**After**:
```bash
spliceinject --directory "C:\ENC210\scte35_final" --min-stable-delay 500
```

## ⚠️ Important Notes

### Verification Steps

After upgrading, verify:
- ✅ SCTE-35 bitrate > 0 b/s in monitoring (markers are being injected)
- ✅ Event IDs increment correctly (10025 → 10026 → 10027...)
- ✅ Marker files created in `scte35_final\` directory
- ✅ Only one marker file exists at a time
- ✅ Markers detected by downstream systems

### Monitoring Output

**Expected Monitoring Output**:
```
[SUCCESS] New marker generated: splice_10025_1764143937.xml
[TSDuck] | 0x01F4 SCTE 35 Splice Info .......................... C >0 b/s
```

**If you see 0 b/s**, check:
1. Marker files exist in `scte35_final\` directory
2. TSDuck process is running
3. File permissions are correct
4. No errors in logs

### No Breaking Changes

- All existing functionality remains the same
- No configuration changes required
- No migration needed
- Directory structure simplified (backward compatible)

## 🚀 Upgrade Instructions

1. Stop any running streams
2. Replace the executable with the new version (v2.2.7)
3. No additional configuration needed
4. Test marker injection and verify SCTE-35 bitrate > 0 b/s

## 📊 Testing Checklist

- [ ] Application starts without errors
- [ ] Stream starts successfully
- [ ] Marker files created in `scte35_final\` directory
- [ ] Only one marker file exists at a time
- [ ] Event IDs increment correctly
- [ ] SCTE-35 bitrate > 0 b/s in monitoring
- [ ] Markers detected by downstream systems

## 🔗 Related Issues

This release fixes:
- SCTE-35 bitrate showing 0 b/s
- Markers not being injected into stream
- Event IDs not incrementing
- Marker files in wrong directory
- File deletion timing issues

---

**Release Date**: 2025-01-27  
**Version**: 2.2.7  
**Build**: Enterprise Edition  
**Executable**: `IBE-210_Enterprise.exe` (88.42 MB)

