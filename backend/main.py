"""
FastAPI Backend for Bison Detection Dashboard
Integrates with RTSP stream and YOLO model for real-time bison tracking
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
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, FileResponse
from pydantic import BaseModel
import uvicorn
from ultralytics import YOLO
import threading
from pathlib import Path

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
    system_status="initializing",
    stream_active=False,
    model_loaded=False,
    last_detection=None
)

# RTSP Configuration
RTSP_URL = "rtsps://cr-14.hostedcloudvideo.com:443/publish-cr/_definst_/G0W2EP7IKAXYETM1ANDVQ6DBRXNXCN7VK3MM7SP9/6b55ae911a8dbd2bd7d3a75ae4547acc976d0b9e?action=PLAY"

# YOLO Model
model = None
cap = None
processing_thread = None
stop_processing = False

# Movement tracking
previous_positions = {}
movement_threshold = 10  # pixels

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

def load_yolo_model():
    """Load YOLO model"""
    global model, system_status
    try:
        # Try to load the model from best.pt, fallback to YOLOv8n if not found
        model_path = Path("best.pt")
        if model_path.exists():
            model = YOLO("best.pt")
            logger.info("Loaded custom YOLO model from best.pt")
        else:
            model = YOLO("yolov8n.pt")
            logger.info("Loaded default YOLOv8n model")
        
        system_status.model_loaded = True
        system_status.system_status = "operational"
        logger.info("YOLO model loaded successfully")
    except Exception as e:
        logger.error(f"Failed to load YOLO model: {e}")
        system_status.system_status = "error"
        system_status.model_loaded = False

def calculate_movement(current_positions: Dict, previous_positions: Dict) -> str:
    """Calculate movement direction based on position changes"""
    if not previous_positions:
        return "stationary"
    
    total_dx = 0
    total_dy = 0
    valid_tracks = 0
    
    for track_id, current_pos in current_positions.items():
        if track_id in previous_positions:
            prev_pos = previous_positions[track_id]
            dx = current_pos[0] - prev_pos[0]
            dy = current_pos[1] - prev_pos[1]
            
            # Only consider significant movements
            if abs(dx) > movement_threshold or abs(dy) > movement_threshold:
                total_dx += dx
                total_dy += dy
                valid_tracks += 1
    
    if valid_tracks == 0:
        return "stationary"
    
    avg_dx = total_dx / valid_tracks
    avg_dy = total_dy / valid_tracks
    
    # Determine primary direction
    if abs(avg_dx) > abs(avg_dy):
        return "east" if avg_dx > 0 else "west"
    else:
        return "south" if avg_dy > 0 else "north"

def process_rtsp_stream():
    """Background thread for processing RTSP stream"""
    global cap, latest_detection, system_status, stop_processing, previous_positions
    
    try:
        cap = cv2.VideoCapture(RTSP_URL)
        if not cap.isOpened():
            logger.error("Failed to open RTSP stream")
            system_status.stream_active = False
            return
        
        system_status.stream_active = True
        logger.info("RTSP stream opened successfully")
        
        fps_counter = 0
        start_time = time.time()
        
        while not stop_processing:
            ret, frame = cap.read()
            if not ret:
                logger.warning("Failed to read frame from RTSP stream")
                time.sleep(0.1)
                continue
            
            fps_counter += 1
            
            # Run YOLO inference
            if model is not None:
                results = model.track(frame, persist=True, verbose=False)
                
                # Extract bison detections (assuming class 0 is bison, adjust as needed)
                bison_count = 0
                current_positions = {}
                
                for result in results:
                    if result.boxes is not None:
                        for box, track_id in zip(result.boxes, result.boxes.id if result.boxes.id is not None else []):
                            # Assuming class 0 is bison - adjust based on your model
                            if int(box.cls) == 0:  # Adjust class ID as needed
                                bison_count += 1
                                # Get center position for movement tracking
                                x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                                center_x = (x1 + x2) / 2
                                center_y = (y1 + y2) / 2
                                current_positions[int(track_id)] = (center_x, center_y)
                
                # Calculate movement
                movement = calculate_movement(current_positions, previous_positions)
                previous_positions = current_positions.copy()
                
                # Calculate FPS
                current_time = time.time()
                elapsed_time = current_time - start_time
                fps = fps_counter / elapsed_time if elapsed_time > 0 else 0
                
                # Create detection record
                detection = BisonDetection(
                    timestamp=datetime.utcnow().isoformat() + "Z",
                    bison_count=bison_count,
                    movement=movement,
                    fps=round(fps, 1),
                    source="rtsp"
                )
                
                # Update global state
                latest_detection = detection
                detection_history.append(detection)
                system_status.last_detection = detection.timestamp
                
                # Log detection
                if bison_count > 0:
                    logger.info(f"Detected {bison_count} bison(s), movement: {movement}, FPS: {fps:.1f}")
            
            # Control frame rate
            time.sleep(0.033)  # ~30 FPS
            
    except Exception as e:
        logger.error(f"Error in RTSP processing: {e}")
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
    load_yolo_model()
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
        return BisonDetection(
            timestamp=datetime.utcnow().isoformat() + "Z",
            bison_count=0,
            movement="stationary",
            fps=0.0,
            source="rtsp"
        )
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
    # This would require additional HLS encoding setup
    # For now, return a simple playlist
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
        "endpoints": {
            "latest": "/api/latest",
            "history": "/api/history?minutes=15",
            "status": "/api/status",
            "stream": "/stream",
            "video": "/video/stream.mjpeg",
            "hls": "/hls/index.m3u8"
        }
    }

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8080,
        reload=True,
        log_level="info"
    )
