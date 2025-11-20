# HLS/DASH Streaming Guide with CORS Support

## Overview

The IBE-100 application now supports multiple output formats including **HLS** (HTTP Live Streaming) and **DASH** (Dynamic Adaptive Streaming over HTTP) with automatic CORS (Cross-Origin Resource Sharing) support.

## Why CORS is Required

When serving HLS/DASH content from a local server to a web player, browsers enforce CORS policies. Without proper CORS headers, you'll see errors like:

```
Access to fetch at 'http://localhost:8000/stream.m3u8' from origin 'http://localhost' has been blocked by CORS policy
```

## Features Added

### 1. CORS Support Toggle
- ✅ **Enable CORS Headers** checkbox (enabled by default)
- Automatically adds `--cors *` to the TSDuck command for HLS/DASH/HTTP output
- Allows web players to access the stream from any origin

### 2. Segment Configuration
- **Segment Duration**: 2-30 seconds (default: 6 seconds)
- **Playlist Window**: 3-20 segments (default: 5 segments)

### 3. Output Format Selection
Choose from multiple output types:
- **SRT**: For streaming to remote servers
- **HLS**: For web playback
- **DASH**: For adaptive streaming
- **UDP**: For multicast
- **TCP**: For network streams
- **HTTP/HTTPS**: For HTTP-based streaming
- **File**: For local file storage

## Usage Instructions

### Step 1: Generate HLS/DASH Stream

1. Open IBE-100 application
2. Configure your input stream
3. **Select Output Type**: Choose "HLS" or "DASH"
4. **Set Output Directory**: e.g., `output/hls` or `output/dash`
5. **Enable CORS**: Check the "Enable CORS Headers" checkbox (default: enabled)
6. **Adjust Segment Duration**: Set 2-30 seconds (6 seconds recommended for HLS)
7. **Set Playlist Window**: 3-20 segments (5 recommended)
8. Click **Start Process**

### Step 2: Serve the Content

#### Option A: Use Built-in CORS (Recommended)
When you enable CORS in the application, TSDuck adds the necessary headers automatically.

#### Option B: Use the Provided Web Server

Run the included Python server script:

```bash
# For HLS output
python serve_hls.py 8000 output/hls

# For DASH output
python serve_hls.py 8000 output/dash
```

This starts a CORS-enabled HTTP server on `http://localhost:8000`

### Step 3: Test with the Test Player

1. Open `test_player.html` in your browser
2. Enter your stream URL:
   - HLS: `http://localhost:8000/output/hls/stream.m3u8`
   - DASH: `http://localhost:8000/output/dash/stream.mpd`
3. Select the stream type (HLS or DASH)
4. Click **Load Stream**
5. Click **Play** to start playback

## Troubleshooting

### CORS Error Still Appearing

**Solution 1**: Make sure "Enable CORS Headers" is checked in the application
**Solution 2**: Use the provided `serve_hls.py` server script
**Solution 3**: Configure your web server to allow CORS headers

For Apache (.htaccess):
```apache
Header set Access-Control-Allow-Origin "*"
Header set Access-Control-Allow-Methods "GET, OPTIONS"
```

For Nginx:
```nginx
add_header Access-Control-Allow-Origin *;
add_header Access-Control-Allow-Methods "GET, OPTIONS";
```

### Stream Not Loading

1. Check if segments are being generated in the output directory
2. Verify the playlist file (.m3u8 for HLS, .mpd for DASH) exists
3. Ensure server is running and accessible
4. Check browser console for errors

### Quality Issues

1. Adjust **Segment Duration**: Longer = larger files, better quality, more latency
2. Adjust **Playlist Window**: More segments = better buffering, more storage

## Technical Details

### TSDuck HLS Command (with CORS)
```bash
tsp -I hls https://input.m3u8 \
    -P spliceinject --files marker.xml \
    -O hls --live output/hls \
           --segment-duration 6 \
           --playlist-window 5 \
           --cors *
```

### TSDuck DASH Command (with CORS)
```bash
tsp -I hls https://input.m3u8 \
    -P spliceinject --files marker.xml \
    -O hls --live output/dash \
           --dash \
           --segment-duration 6 \
           --playlist-window 5 \
           --cors *
```

## Integration Examples

### Video.js Player
```html
<video id="player" class="video-js" controls preload="auto">
    <source src="http://localhost:8000/output/hls/stream.m3u8" type="application/x-mpegURL">
</video>
<script>
  var player = videojs('player');
</script>
```

### HLS.js Player
```html
<video id="video"></video>
<script src="https://cdn.jsdelivr.net/npm/hls.js@latest"></script>
<script>
  var video = document.getElementById('video');
  var videoSrc = 'http://localhost:8000/output/hls/stream.m3u8';
  if (Hls.isSupported()) {
    var hls = new Hls();
    hls.loadSource(videoSrc);
    hls.attachMedia(video);
  }
</script>
```

## Production Deployment

For production use:

1. **Remove `--cors *`** and implement specific allowed origins
2. Use a production web server (nginx, Apache) instead of Python's simple server
3. Configure proper authentication and security headers
4. Use HTTPS instead of HTTP
5. Set up a CDN for distribution

## Support

For issues or questions:
- Check TSDuck documentation: https://tsduck.io/
- Review SCTE-35 specifications
- Contact ITAssist support

---

**Version**: 2.0  
**Last Updated**: 2024

