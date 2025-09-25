"""
Simplified FastAPI server for bison detection - runs without YOLO initially
"""

import asyncio
import json
import logging
import time
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from collections import deque
import cv2
import numpy as np
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import uvicorn
import threading
import random

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Data models
class BisonDetection(BaseModel):
    timestamp: str
    bison_count: int
    movement: str  # "north", "south", "east", "west", "stationary"
    fps: float
    source: str  # "rtsp"

class SystemStatus(BaseModel):
    system_status: str
    stream_active: bool
    model_loaded: bool
    last_detection: Optional[str]

# Global state
detection_history = deque(maxlen=1800)  # 30 minutes at 1 FPS
latest_detection = None
system_status = SystemStatus(
    system_status="operational",
    stream_active=True,
    model_loaded=False,  # Will be False initially
    last_detection=None
)

# RTSP Configuration
RTSP_URL = "rtsps://cr-14.hostedcloudvideo.com:443/publish-cr/_definst_/G0W2EP7IKAXYETM1ANDVQ6DBRXNXCN7VK3MM7SP9/6b55ae911a8dbd2bd7d3a75ae4547acc976d0b9e?action=PLAY"

# Video capture
cap = None
processing_thread = None
stop_processing = False

# Mock data generation
movement_options = ["north", "south", "east", "west", "stationary"]
last_mock_count = 0

app = FastAPI(
    title="Bison Detection API",
    description="Real-time bison tracking and detection API",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173",
        "https://*.onrender.com",
        "https://*.netlify.app"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def generate_mock_detection():
    """Generate mock detection data for testing"""
    global last_mock_count
    
    # Simulate realistic bison count changes
    if random.random() < 0.3:  # 30% chance to change count
        change = random.choice([-1, 0, 1])
        last_mock_count = max(0, min(10, last_mock_count + change))
    
    # Generate movement based on count
    if last_mock_count == 0:
        movement = "stationary"
    else:
        movement = random.choice(movement_options)
    
    return BisonDetection(
        timestamp=datetime.utcnow().isoformat() + "Z",
        bison_count=last_mock_count,
        movement=movement,
        fps=round(random.uniform(20, 30), 1),
        source="rtsp"
    )

def process_rtsp_stream():
    """Background thread for processing RTSP stream (with fallback to mock data)"""
    global cap, latest_detection, system_status, stop_processing
    
    try:
        # Try to connect to RTSP stream
        cap = cv2.VideoCapture(RTSP_URL)
        if not cap.isOpened():
            logger.warning("Failed to open RTSP stream, using mock data")
            system_status.stream_active = False
            cap = None
        else:
            system_status.stream_active = True
            logger.info("RTSP stream opened successfully")
        
        while not stop_processing:
            if cap is not None:
                ret, frame = cap.read()
                if not ret:
                    logger.warning("Failed to read frame from RTSP stream")
                    time.sleep(0.1)
                    continue
                
                # For now, just generate mock detection data
                # In the future, this is where YOLO inference would go
                detection = generate_mock_detection()
            else:
                # Use mock data when RTSP is not available
                detection = generate_mock_detection()
            
            # Update global state
            latest_detection = detection
            detection_history.append(detection)
            system_status.last_detection = detection.timestamp
            
            # Log detection
            if detection.bison_count > 0:
                logger.info(f"Detected {detection.bison_count} bison(s), movement: {detection.movement}, FPS: {detection.fps}")
            
            # Control frame rate
            time.sleep(1)  # 1 FPS for now
            
    except Exception as e:
        logger.error(f"Error in stream processing: {e}")
        system_status.stream_active = False
    finally:
        if cap:
            cap.release()

def start_rtsp_processing():
    """Start RTSP processing in background thread"""
    global processing_thread, stop_processing
    
    if processing_thread is None or not processing_thread.is_alive():
        stop_processing = False
        processing_thread = threading.Thread(target=process_rtsp_stream, daemon=True)
        processing_thread.start()
        logger.info("Started RTSP processing thread")

@app.on_event("startup")
async def startup_event():
    """Initialize the application"""
    logger.info("Starting Bison Detection API...")
    start_rtsp_processing()

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    global stop_processing, cap
    logger.info("Shutting down Bison Detection API...")
    stop_processing = True
    if cap:
        cap.release()

@app.get("/api/latest")
async def get_latest():
    """Get the most recent bison detection data"""
    if latest_detection is None:
        # Return mock data if no real detection yet
        return generate_mock_detection()
    return latest_detection

@app.get("/api/history")
async def get_history(minutes: int = 15):
    """Get historical detection data for the specified time window"""
    if not detection_history:
        return []
    
    cutoff_time = datetime.utcnow() - timedelta(minutes=minutes)
    cutoff_str = cutoff_time.isoformat() + "Z"
    
    # Filter detections within the time window
    filtered_detections = [
        detection for detection in detection_history
        if detection.timestamp >= cutoff_str
    ]
    
    return filtered_detections

@app.get("/api/status")
async def get_status():
    """Get system status information"""
    return system_status

@app.get("/stream")
async def stream_detections():
    """Server-Sent Events endpoint for real-time detection updates"""
    async def event_generator():
        last_detection_time = None
        
        while True:
            if latest_detection and latest_detection.timestamp != last_detection_time:
                yield f"data: {latest_detection.json()}\n\n"
                last_detection_time = latest_detection.timestamp
            
            await asyncio.sleep(0.1)  # 10 FPS for SSE updates
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        }
    )

@app.get("/video/stream.mjpeg")
async def video_stream():
    """MJPEG video stream with detection overlays"""
    async def generate_frames():
        global cap
        
        if cap is None or not cap.isOpened():
            # Return a placeholder frame if stream is not available
            placeholder = np.zeros((480, 640, 3), dtype=np.uint8)
            cv2.putText(placeholder, "Stream Unavailable", (200, 240), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
            cv2.putText(placeholder, "Using Mock Data", (220, 280), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, (200, 200, 200), 2)
            
            _, buffer = cv2.imencode('.jpg', placeholder)
            frame_bytes = buffer.tobytes()
            
            while True:
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
                await asyncio.sleep(0.1)
            return
        
        while True:
            ret, frame = cap.read()
            if not ret:
                await asyncio.sleep(0.1)
                continue
            
            # Draw detection overlays if we have recent detections
            if latest_detection and latest_detection.bison_count > 0:
                cv2.putText(frame, f"Bison Count: {latest_detection.bison_count}", 
                           (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                cv2.putText(frame, f"Movement: {latest_detection.movement}", 
                           (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                cv2.putText(frame, f"FPS: {latest_detection.fps}", 
                           (10, 110), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            
            # Encode frame as JPEG
            _, buffer = cv2.imencode('.jpg', frame)
            frame_bytes = buffer.tobytes()
            
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
            
            await asyncio.sleep(0.033)  # ~30 FPS
    
    return StreamingResponse(
        generate_frames(),
        media_type="multipart/x-mixed-replace; boundary=frame"
    )

@app.get("/hls/index.m3u8")
async def hls_playlist():
    """HLS playlist endpoint (placeholder)"""
    playlist_content = """#EXTM3U
#EXT-X-VERSION:3
#EXT-X-TARGETDURATION:10
#EXT-X-MEDIA-SEQUENCE:0
#EXTINF:10.0,
stream.m3u8
#EXT-X-ENDLIST"""
    
    return StreamingResponse(
        iter([playlist_content]),
        media_type="application/vnd.apple.mpegurl"
    )

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Bison Detection API",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "latest": "/api/latest",
            "history": "/api/history?minutes=15",
            "status": "/api/status",
            "stream": "/stream",
            "video": "/video/stream.mjpeg",
            "hls": "/hls/index.m3u8"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "model_loaded": system_status.model_loaded,
        "stream_active": system_status.stream_active
    }

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(
        "simple_server:app",
        host="0.0.0.0",
        port=port,
        reload=False,  # Disable reload in production
        log_level="info"
    )
