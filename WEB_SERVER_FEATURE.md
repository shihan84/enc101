# Web Server Integration Feature

## Summary

A **Local Web Server** has been integrated directly into the IBE-100 UI, eliminating the need for external Python scripts or manual server management.

## Why This Was Needed

When generating HLS/DASH content for local testing, you need a web server to:
1. Serve the playlist files (.m3u8 for HLS, .mpd for DASH)
2. Serve video segments (.ts files)
3. Add CORS headers so web players can access the content
4. Allow browser-based testing

Without a web server, you'll get CORS errors when trying to play HLS/DASH content in a web browser.

## Features Added

### 1. Web Server Tab in Monitoring Panel
- Located in: **Monitoring → Web Server tab**
- One-click start/stop
- Real-time status display
- Port configuration (8000-9999)
- Custom directory selection

### 2. CORS Support
- Automatically adds CORS headers to all responses
- Allows access from any origin (for local testing)
- Required for web players (HLS.js, Video.js, etc.)

### 3. Embedded Server
- No external dependencies required
- Creates a temporary Python server script
- Automatically cleans up on stop
- Handles errors gracefully

## How to Use

### Step 1: Generate HLS/DASH Content
1. Configure your input stream
2. Select **Output Type**: "HLS" or "DASH"
3. Set **Output Directory**: e.g., `output/hls`
4. Enable **CORS Headers** checkbox
5. Start the encoder process

### Step 2: Start Local Web Server
1. Navigate to **Monitoring → Web Server** tab
2. Set **Port**: Default is 8000
3. Set **Serving Directory**: Match your output directory (e.g., `output/hls`)
4. Click **▶️ Start Web Server**
5. Status will show: "✅ Web Server: Running on http://localhost:8000"

### Step 3: Test in Browser
Open your browser and navigate to:
- **HLS**: `http://localhost:8000/stream.m3u8`
- **DASH**: `http://localhost:8000/stream.mpd`

Or use the included `test_player.html` file.

### Step 4: Stop Server
Click **⏹️ Stop Web Server** when done.

## Technical Implementation

### Embedded Server Code
The UI dynamically creates a Python HTTP server with CORS support:

```python
import http.server
import socketserver

class CORSRequestHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        super().end_headers()
```

### Process Management
- Uses `subprocess.Popen` to run server in background
- Automatic cleanup on stop
- Error handling and status reporting
- Port and directory validation

## Benefits

✅ **No External Tools**: Everything is integrated  
✅ **One-Click Operation**: Simple start/stop buttons  
✅ **Real-Time Status**: See server state at a glance  
✅ **Flexible Configuration**: Custom ports and directories  
✅ **CORS Included**: Automatic cross-origin support  
✅ **Clean Integration**: No manual Python scripts needed  

## Comparison

### Before
1. Generate HLS/DASH content
2. Manually run `python serve_hls.py 8000 output/hls`
3. Keep terminal window open
4. Manually stop server when done

### After
1. Generate HLS/DASH content
2. Click "Start Web Server" in UI
3. Test in browser
4. Click "Stop Web Server" when done

## User Experience

The web server UI provides:
- **Green Status**: Server running successfully
- **Red Status**: Error occurred
- **Gray Status**: Server stopped
- **URL Display**: Shows the access URL
- **Directory Display**: Shows what's being served

## Production Considerations

For production deployments:
1. **Remove CORS wildcard**: Use specific allowed origins
2. **Use dedicated server**: nginx, Apache instead of embedded Python server
3. **Enable HTTPS**: Use SSL/TLS certificates
4. **Authentication**: Add proper authentication
5. **CDN Integration**: Use content delivery network

## Troubleshooting

### Port Already in Use
- Change to a different port (e.g., 8001, 8002)
- Stop the conflicting application

### Directory Not Found
- Make sure output directory exists
- Check that encoder has generated content
- Verify path is correct

### CORS Errors Still Appearing
- Make sure "Enable CORS Headers" is checked in main config
- Restart web server
- Clear browser cache

## Future Enhancements

Potential improvements:
- Show active connections
- Display served files
- Logs viewer
- Auto-start on HLS/DASH generation
- Multiple server instances
- HTTPS support

---

**Version**: 2.0  
**Feature**: Integrated Web Server  
**Status**: ✅ Implemented

