"""
Configuration settings for the Bison Detection API
"""

import os
from pathlib import Path
from typing import Optional

class Config:
    """Application configuration"""
    
    # API Settings
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8080
    API_TITLE: str = "Bison Detection API"
    API_VERSION: str = "1.0.0"
    
    # RTSP Settings
    RTSP_URL: str = "rtsps://cr-14.hostedcloudvideo.com:443/publish-cr/_definst_/G0W2EP7IKAXYETM1ANDVQ6DBRXNXCN7VK3MM7SP9/6b55ae911a8dbd2bd7d3a75ae4547acc976d0b9e?action=PLAY"
    RTSP_TIMEOUT: int = 30
    RTSP_RETRY_ATTEMPTS: int = 3
    RTSP_RETRY_DELAY: float = 5.0
    
    # YOLO Model Settings
    MODEL_PATH: str = "best.pt"
    FALLBACK_MODEL: str = "yolov8n.pt"
    BISON_CLASS_ID: int = 0  # Adjust based on your model
    CONFIDENCE_THRESHOLD: float = 0.25
    IOU_THRESHOLD: float = 0.45
    
    # Tracking Settings
    TRACK_THRESH: float = 0.5
    TRACK_BUFFER: int = 30
    MATCH_THRESH: float = 0.8
    MOVEMENT_THRESHOLD: int = 10  # pixels
    
    # Data Storage Settings
    HISTORY_SIZE: int = 1800  # 30 minutes at 1 FPS
    DETECTION_RETENTION_MINUTES: int = 30
    
    # Video Streaming Settings
    VIDEO_FPS: int = 30
    MJPEG_QUALITY: int = 85
    VIDEO_WIDTH: int = 640
    VIDEO_HEIGHT: int = 480
    
    # CORS Settings
    CORS_ORIGINS: list = [
        "http://localhost:3000",
        "http://localhost:5173",
        "https://*.onrender.com",
        "https://*.netlify.app"
    ]
    
    # Logging Settings
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # Performance Settings
    MAX_CONCURRENT_CONNECTIONS: int = 100
    SSE_HEARTBEAT_INTERVAL: float = 30.0
    FRAME_PROCESSING_TIMEOUT: float = 1.0
    
    @classmethod
    def get_model_path(cls) -> Path:
        """Get the path to the YOLO model file"""
        model_path = Path(cls.MODEL_PATH)
        if model_path.exists():
            return model_path
        return Path(cls.FALLBACK_MODEL)
    
    @classmethod
    def load_from_env(cls):
        """Load configuration from environment variables"""
        cls.API_HOST = os.getenv("API_HOST", cls.API_HOST)
        cls.API_PORT = int(os.getenv("API_PORT", cls.API_PORT))
        cls.RTSP_URL = os.getenv("RTSP_URL", cls.RTSP_URL)
        cls.MODEL_PATH = os.getenv("MODEL_PATH", cls.MODEL_PATH)
        cls.LOG_LEVEL = os.getenv("LOG_LEVEL", cls.LOG_LEVEL)
        
        # Parse CORS origins from environment
        cors_origins = os.getenv("CORS_ORIGINS")
        if cors_origins:
            cls.CORS_ORIGINS = [origin.strip() for origin in cors_origins.split(",")]

# Load configuration from environment
Config.load_from_env()
