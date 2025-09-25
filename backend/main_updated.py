"""
Updated FastAPI Backend for Bison Detection Dashboard
Clean, modular implementation with proper separation of concerns
"""

import asyncio
import logging
from datetime import datetime
from typing import List, Optional

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
import uvicorn

from models import BisonDetection, SystemStatus, SystemStatusEnum, APIResponse, ErrorResponse
from detection_service import detection_service
from video_service import video_service
from config import Config

# Configure logging
logging.basicConfig(
    level=getattr(logging, Config.LOG_LEVEL),
    format=Config.LOG_FORMAT
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title=Config.API_TITLE,
    description="Real-time bison tracking and detection API",
    version=Config.API_VERSION,
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=Config.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    """Initialize the application"""
    logger.info("Starting Bison Detection API...")
    
    # Load YOLO model
    if detection_service.load_model():
        logger.info("YOLO model loaded successfully")
    else:
        logger.error("Failed to load YOLO model")
    
    # Start detection processing
    detection_service.start_processing()
    logger.info("Detection processing started")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("Shutting down Bison Detection API...")
    detection_service.stop_processing_service()
    video_service.cleanup()

@app.get("/", response_model=APIResponse)
async def root():
    """Root endpoint with API information"""
    return APIResponse(
        success=True,
        message="Bison Detection API is running",
        data={
            "version": Config.API_VERSION,
            "endpoints": {
                "latest": "/api/latest",
                "history": "/api/history?minutes=15",
                "status": "/api/status",
                "stream": "/stream",
                "video": "/video/stream.mjpeg",
                "hls": "/hls/index.m3u8"
            }
        },
        timestamp=datetime.utcnow().isoformat() + "Z"
    )

@app.get("/api/latest", response_model=BisonDetection)
async def get_latest():
    """Get the most recent bison detection data"""
    latest = detection_service.get_latest_detection()
    
    if latest is None:
        # Return mock data if no real detection yet
        return BisonDetection(
            timestamp=datetime.utcnow().isoformat() + "Z",
            bison_count=0,
            movement="stationary",
            fps=0.0,
            source="rtsp"
        )
    
    return latest

@app.get("/api/history", response_model=List[BisonDetection])
async def get_history(minutes: int = 15):
    """Get historical detection data for the specified time window"""
    if minutes < 1 or minutes > 60:
        raise HTTPException(
            status_code=400,
            detail="Minutes parameter must be between 1 and 60"
        )
    
    return detection_service.get_detection_history(minutes)

@app.get("/api/status", response_model=SystemStatus)
async def get_status():
    """Get system status information"""
    metrics = detection_service.get_system_metrics()
    
    return SystemStatus(
        system_status=SystemStatusEnum.OPERATIONAL if detection_service.model_loaded else SystemStatusEnum.ERROR,
        stream_active=detection_service.stream_active,
        model_loaded=detection_service.model_loaded,
        last_detection=detection_service.last_detection_time.isoformat() + "Z" if detection_service.last_detection_time else None,
        uptime_seconds=metrics["stream_uptime_seconds"],
        memory_usage_mb=None,  # Could be implemented with psutil
        cpu_usage_percent=None  # Could be implemented with psutil
    )

@app.get("/stream")
async def stream_detections():
    """Server-Sent Events endpoint for real-time detection updates"""
    async def event_generator():
        last_detection_time = None
        
        while True:
            try:
                latest = detection_service.get_latest_detection()
                
                if latest and latest.timestamp != last_detection_time:
                    yield f"data: {latest.json()}\n\n"
                    last_detection_time = latest.timestamp
                
                await asyncio.sleep(0.1)  # 10 FPS for SSE updates
                
            except Exception as e:
                logger.error(f"Error in SSE stream: {e}")
                await asyncio.sleep(1)
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "Cache-Control"
        }
    )

@app.get("/video/stream.mjpeg")
async def video_stream():
    """MJPEG video stream with detection overlays"""
    return StreamingResponse(
        video_service.generate_mjpeg_frames(),
        media_type="multipart/x-mixed-replace; boundary=frame",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive"
        }
    )

@app.get("/hls/index.m3u8")
async def hls_playlist():
    """HLS playlist endpoint"""
    playlist_content = video_service.generate_hls_playlist()
    
    return StreamingResponse(
        iter([playlist_content]),
        media_type="application/vnd.apple.mpegurl",
        headers={
            "Cache-Control": "no-cache"
        }
    )

@app.get("/api/metrics")
async def get_metrics():
    """Get system performance metrics"""
    return detection_service.get_system_metrics()

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "model_loaded": detection_service.model_loaded,
        "stream_active": detection_service.stream_active
    }

# Error handlers
@app.exception_handler(404)
async def not_found_handler(request, exc):
    return ErrorResponse(
        error="Not Found",
        message="The requested resource was not found",
        timestamp=datetime.utcnow().isoformat() + "Z"
    )

@app.exception_handler(500)
async def internal_error_handler(request, exc):
    return ErrorResponse(
        error="Internal Server Error",
        message="An internal server error occurred",
        timestamp=datetime.utcnow().isoformat() + "Z"
    )

if __name__ == "__main__":
    uvicorn.run(
        "main_updated:app",
        host=Config.API_HOST,
        port=Config.API_PORT,
        reload=True,
        log_level=Config.LOG_LEVEL.lower()
    )
