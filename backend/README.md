# Bison Detection FastAPI Backend

A production-ready FastAPI backend for real-time bison detection and tracking using YOLO and RTSP streams.

## Features

- **Real-time Detection**: YOLO-based bison detection with ByteTracker
- **RTSP Integration**: Live video stream processing
- **Movement Tracking**: Direction calculation (north/south/east/west/stationary)
- **REST API**: Clean REST endpoints for data access
- **Server-Sent Events**: Real-time streaming updates
- **Video Streaming**: MJPEG and HLS video streams with overlays
- **CORS Support**: Configured for frontend integration
- **Error Handling**: Graceful fallbacks and error recovery

## API Endpoints

### Core Endpoints
- `GET /` - API information and available endpoints
- `GET /api/latest` - Latest bison detection data
- `GET /api/history?minutes=15` - Historical detection data
- `GET /api/status` - System status information
- `GET /api/metrics` - Performance metrics
- `GET /health` - Health check

### Streaming Endpoints
- `GET /stream` - Server-Sent Events for real-time updates
- `GET /video/stream.mjpeg` - MJPEG video stream with overlays
- `GET /hls/index.m3u8` - HLS playlist (placeholder)

## Installation

1. **Install Python Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Download YOLO Model** (optional):
   - Place your trained `best.pt` model in the backend directory
   - If not available, the system will use the default YOLOv8n model

3. **Configure Environment** (optional):
   ```bash
   export API_HOST=0.0.0.0
   export API_PORT=8080
   export RTSP_URL="your_rtsp_url_here"
   export LOG_LEVEL=INFO
   ```

## Running the Server

### Option 1: Direct Python execution
```bash
cd backend
python run.py
```

### Option 2: Using uvicorn directly
```bash
cd backend
uvicorn main_updated:app --host 0.0.0.0 --port 8080 --reload
```

### Option 3: Production deployment
```bash
cd backend
uvicorn main_updated:app --host 0.0.0.0 --port 8080 --workers 4
```

## Configuration

The system uses the `config.py` file for configuration. Key settings:

- **RTSP_URL**: Your RTSP stream URL
- **MODEL_PATH**: Path to your YOLO model file
- **BISON_CLASS_ID**: Class ID for bison in your model (default: 0)
- **CONFIDENCE_THRESHOLD**: Detection confidence threshold (default: 0.25)
- **MOVEMENT_THRESHOLD**: Pixel threshold for movement detection (default: 10)

## Data Format

### Detection Response
```json
{
  "timestamp": "2025-01-25T10:30:00Z",
  "bison_count": 5,
  "movement": "north",
  "fps": 25.5,
  "source": "rtsp"
}
```

### System Status Response
```json
{
  "system_status": "operational",
  "stream_active": true,
  "model_loaded": true,
  "last_detection": "2025-01-25T10:30:00Z",
  "uptime_seconds": 3600.5,
  "memory_usage_mb": null,
  "cpu_usage_percent": null
}
```

## Architecture

The backend is organized into several modules:

- **`main_updated.py`**: FastAPI application and route handlers
- **`detection_service.py`**: YOLO inference and tracking logic
- **`video_service.py`**: Video streaming and overlay rendering
- **`models.py`**: Pydantic data models
- **`config.py`**: Configuration management

## Performance Considerations

- **Frame Rate**: Configurable FPS (default: 30)
- **Buffer Management**: Optimized for real-time processing
- **Memory Usage**: In-memory storage with configurable retention
- **Concurrent Connections**: Supports multiple SSE connections
- **Error Recovery**: Automatic reconnection to RTSP streams

## Troubleshooting

### Common Issues

1. **RTSP Connection Failed**:
   - Check RTSP URL validity
   - Verify network connectivity
   - Check firewall settings

2. **YOLO Model Not Loading**:
   - Ensure model file exists
   - Check file permissions
   - Verify model format compatibility

3. **High CPU Usage**:
   - Reduce video FPS in config
   - Lower confidence threshold
   - Use smaller model variant

4. **Memory Issues**:
   - Reduce history retention time
   - Lower video resolution
   - Restart service periodically

### Logs

The application logs to stdout with configurable levels:
- `DEBUG`: Detailed debugging information
- `INFO`: General information (default)
- `WARNING`: Warning messages
- `ERROR`: Error messages

## Development

### Adding New Features

1. **New Endpoints**: Add routes in `main_updated.py`
2. **Data Models**: Define in `models.py`
3. **Business Logic**: Implement in service modules
4. **Configuration**: Add settings to `config.py`

### Testing

Test the API endpoints:
```bash
# Health check
curl http://localhost:8080/health

# Latest detection
curl http://localhost:8080/api/latest

# System status
curl http://localhost:8080/api/status
```

## Production Deployment

For production deployment:

1. **Use a production ASGI server** (Gunicorn with Uvicorn workers)
2. **Set up reverse proxy** (Nginx)
3. **Configure SSL/TLS**
4. **Set up monitoring and logging**
5. **Use environment variables** for configuration
6. **Implement proper error handling and recovery**

## License

This project is part of the Bison Pulse monitoring system.
