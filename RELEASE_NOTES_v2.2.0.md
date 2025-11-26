# 🚀 IBE-210 v2.2.0 Enterprise - Release Notes

**Release Date:** January 2025  
**Version:** 2.2.0 Enterprise  
**Status:** ✅ Production Ready

---

## 🎯 **Major Features**

### **1. Dynamic SCTE-35 Marker Generation for 24/7 Streaming** ⭐ NEW

**Problem Solved:**
- Event IDs were not incrementing on distributor side
- Continuous injection required manual file management
- Single marker file injected multiple times with same event ID

**Solution:**
- ✅ **Dynamic Marker Service**: Automatically generates markers with incrementing event IDs
- ✅ **Background Thread**: Generates markers continuously during streaming
- ✅ **Automatic Cleanup**: TSDuck deletes files after injection
- ✅ **Zero Configuration**: Works automatically when `inject_count > 1`

**Benefits:**
- ✅ Incrementing event IDs (10023, 10024, 10025, ...)
- ✅ Works for 24/7 continuous streaming
- ✅ No manual file management needed
- ✅ Resource efficient (only one file at a time)

---

### **2. Enhanced Injection Count Support** ⭐ NEW

**Improvements:**
- ✅ **Increased UI Limit**: From 1,000 to 100,000 injections
- ✅ **Long Stream Support**: Covers streams up to 69 days
- ✅ **Flexible Configuration**: Set any value up to 100,000 in UI
- ✅ **Config File Support**: Unlimited values via JSON config

**Use Cases:**
- 24-hour streams: 1,440 injections
- 7-day streams: 10,080 injections
- 30-day streams: 43,200 injections
- 69-day streams: 100,000 injections

---

### **3. TSDuck Directory Mode Support** ⭐ NEW

**Features:**
- ✅ **Automatic Detection**: Detects directory vs. single file mode
- ✅ **Wildcard Support**: Uses `splice*.xml` pattern for dynamic markers
- ✅ **File Polling**: Monitors directory for new markers
- ✅ **Auto Cleanup**: Deletes files after injection

**Technical:**
- Uses TSDuck's `--files` with wildcard pattern
- `--delete-files` flag for automatic cleanup
- `--poll-interval 500` for file monitoring
- `--inject-count 1` (each file injected once)

---

## 📊 **Improvements**

### **SCTE-35 Marker Injection**

1. **Event ID Incrementing**
   - ✅ Each marker now has unique, sequential event ID
   - ✅ Distributor can track and validate markers
   - ✅ No duplicate event IDs

2. **Continuous Injection**
   - ✅ Works for unlimited duration
   - ✅ No need to generate 1000 files upfront
   - ✅ Generates markers as needed

3. **Automatic Management**
   - ✅ Files generated automatically
   - ✅ Files deleted automatically
   - ✅ No manual intervention needed

### **User Interface**

1. **Injection Settings**
   - ✅ Increased `inject_count` limit to 100,000
   - ✅ Better validation and feedback
   - ✅ Clearer configuration options

2. **Stream Configuration**
   - ✅ Automatic dynamic generation detection
   - ✅ Seamless integration
   - ✅ No additional setup required

---

## 🔧 **Technical Changes**

### **New Files**

- `src/services/dynamic_marker_service.py` - Dynamic marker generation service
- `DYNAMIC_MARKER_IMPLEMENTATION.md` - Technical documentation
- `DYNAMIC_MARKER_USAGE_GUIDE.md` - User guide
- `EVENT_ID_NOT_INCREMENTING_EXPLANATION.md` - Problem explanation
- `TSDUCK_SPLICEINJECT_ANALYSIS.md` - TSDuck documentation analysis
- `CONTINUOUS_INJECTION_BEYOND_1000.md` - Injection count guide
- `SOLUTION_COMPARISON_GUIDE.md` - Solution comparison
- `OTHER_PROVIDERS_COMPARISON.md` - Industry comparison

### **Modified Files**

- `src/services/tsduck_service.py` - Added directory mode support
- `src/services/stream_service.py` - Integrated dynamic marker service
- `src/ui/widgets/stream_config_widget.py` - Increased inject_count limit
- `main.py` - Updated inject_count limit
- `main_enterprise.py` - Added DynamicMarkerService initialization
- `IBE-210_Enterprise.spec` - Added dynamic_marker_service to build

---

## 📚 **Documentation**

### **New Documentation**

1. **Dynamic Marker Generation**
   - Complete implementation guide
   - Usage instructions
   - Troubleshooting tips

2. **Event ID Issues**
   - Problem explanation
   - Root cause analysis
   - Solution details

3. **Injection Count**
   - Duration calculator
   - Configuration guide
   - Best practices

4. **Provider Comparison**
   - How other providers handle continuous injection
   - Industry standard approaches
   - Comparison with professional tools

---

## 🐛 **Bug Fixes**

1. **Event ID Not Incrementing**
   - ✅ Fixed: Now generates markers with incrementing event IDs
   - ✅ Root cause: Single file injected multiple times
   - ✅ Solution: Dynamic generation with multiple files

2. **Injection Count Limitation**
   - ✅ Fixed: Increased UI limit from 1,000 to 100,000
   - ✅ Added: Config file support for unlimited values
   - ✅ Added: Better validation and feedback

3. **Continuous Injection Issues**
   - ✅ Fixed: Markers now inject continuously for long streams
   - ✅ Added: Automatic dynamic generation
   - ✅ Improved: Resource efficiency

---

## ⚙️ **Configuration Changes**

### **Default Values**

- `inject_count`: Still defaults to 1 (for single injection)
- `inject_interval`: Still defaults to 1000ms
- `start_delay`: Still defaults to 2000ms

### **New Behavior**

- When `inject_count > 1`: Automatically uses dynamic generation
- Dynamic markers directory: `scte35_final/dynamic_markers/`
- File naming: `splice_XXXXX.xml` (zero-padded event ID)

---

## 🚀 **Migration Guide**

### **From v2.1.0 to v2.2.0**

**No Breaking Changes!**

1. **Existing Streams:**
   - Continue to work as before
   - Single file mode still supported
   - No configuration changes needed

2. **New Features:**
   - Set `inject_count > 1` to enable dynamic generation
   - System automatically detects and uses dynamic mode
   - No additional setup required

3. **Upgrade Steps:**
   - ✅ Install new version
   - ✅ Existing profiles work without changes
   - ✅ New features available immediately

---

## 📋 **System Requirements**

- **Python**: 3.9+ (for development)
- **OS**: Windows 10/11
- **TSDuck**: Included (bundled) or system installation
- **Memory**: 2GB+ RAM recommended
- **Disk**: 500MB+ free space

---

## ✅ **Testing**

### **Tested Scenarios**

1. ✅ Single marker injection (traditional mode)
2. ✅ Continuous injection with dynamic generation
3. ✅ Event ID incrementing (10023 → 10024 → 10025)
4. ✅ Long streams (24+ hours)
5. ✅ Multiple profiles with different settings
6. ✅ Stream start/stop with dynamic generation
7. ✅ File cleanup after injection
8. ✅ UI limit validation (up to 100,000)

---

## 🎯 **Known Limitations**

1. **Dynamic Generation:**
   - Requires `inject_count > 1` to activate
   - Generates one file at a time (resource efficient)
   - File must be stable for 500ms before TSDuck detects it

2. **Event ID Range:**
   - Valid range: 10000-99999
   - Wraps around after 99999
   - Managed automatically

---

## 🔮 **Future Enhancements**

1. **Scheduled Marker Generation**
   - Generate markers at specific times
   - Calendar-based scheduling
   - Event-based triggers

2. **Advanced Event ID Management**
   - Custom event ID ranges
   - Per-profile event ID pools
   - Event ID reservation system

3. **Performance Monitoring**
   - Marker generation metrics
   - Injection success tracking
   - Performance analytics

---

## 🙏 **Acknowledgments**

- TSDuck project for excellent SCTE-35 support
- SCTE-35 standard committee
- All contributors and testers

---

## 📞 **Support**

For issues, questions, or feature requests:
- Check documentation in project root
- Review troubleshooting guides
- Contact support team

---

## 📝 **Changelog Summary**

### **v2.2.0 (January 2025)**

**Added:**
- Dynamic SCTE-35 marker generation service
- Directory mode support in TSDuck service
- Increased inject_count limit to 100,000
- Comprehensive documentation

**Fixed:**
- Event ID not incrementing on distributor side
- Injection count limitation for long streams
- Continuous injection issues

**Improved:**
- Stream service integration
- User interface validation
- Resource efficiency
- Documentation coverage

---

**Download:** Available in `dist/IBE-210_Enterprise.exe`  
**Build Date:** January 2025  
**Status:** ✅ Production Ready

---

**Thank you for using IBE-210 Enterprise!** 🎉

