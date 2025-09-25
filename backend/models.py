"""
Data models for the Bison Detection API
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum

class MovementDirection(str, Enum):
    """Enumeration of possible movement directions"""
    NORTH = "north"
    SOUTH = "south"
    EAST = "east"
    WEST = "west"
    STATIONARY = "stationary"

class DataSource(str, Enum):
    """Enumeration of possible data sources"""
    RTSP = "rtsp"
    SAMPLE = "sample"

class SystemStatusEnum(str, Enum):
    """Enumeration of system status values"""
    OPERATIONAL = "operational"
    INITIALIZING = "initializing"
    ERROR = "error"
    MAINTENANCE = "maintenance"

class BisonDetection(BaseModel):
    """Model for bison detection data"""
    timestamp: str = Field(..., description="ISO timestamp of the detection")
    bison_count: int = Field(..., ge=0, description="Number of bison detected")
    movement: MovementDirection = Field(..., description="Direction of bison movement")
    fps: float = Field(..., ge=0, description="Frames per second of the video stream")
    source: DataSource = Field(..., description="Source of the detection data")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class SystemStatus(BaseModel):
    """Model for system status information"""
    system_status: SystemStatusEnum = Field(..., description="Overall system status")
    stream_active: bool = Field(..., description="Whether the RTSP stream is active")
    model_loaded: bool = Field(..., description="Whether the YOLO model is loaded")
    last_detection: Optional[str] = Field(None, description="Timestamp of last detection")
    uptime_seconds: Optional[float] = Field(None, description="System uptime in seconds")
    memory_usage_mb: Optional[float] = Field(None, description="Memory usage in MB")
    cpu_usage_percent: Optional[float] = Field(None, description="CPU usage percentage")

class DetectionHistory(BaseModel):
    """Model for detection history response"""
    detections: List[BisonDetection] = Field(..., description="List of detections")
    total_count: int = Field(..., description="Total number of detections returned")
    time_range_minutes: int = Field(..., description="Time range in minutes")
    start_time: str = Field(..., description="Start time of the range")
    end_time: str = Field(..., description="End time of the range")

class TrackingInfo(BaseModel):
    """Model for tracking information"""
    track_id: int = Field(..., description="Unique track identifier")
    bbox: List[float] = Field(..., description="Bounding box [x1, y1, x2, y2]")
    confidence: float = Field(..., ge=0, le=1, description="Detection confidence")
    class_id: int = Field(..., description="Object class ID")
    class_name: str = Field(..., description="Object class name")
    center_x: float = Field(..., description="Center X coordinate")
    center_y: float = Field(..., description="Center Y coordinate")
    velocity_x: Optional[float] = Field(None, description="Velocity in X direction")
    velocity_y: Optional[float] = Field(None, description="Velocity in Y direction")

class DetailedDetection(BaseModel):
    """Model for detailed detection with tracking information"""
    timestamp: str = Field(..., description="ISO timestamp of the detection")
    bison_count: int = Field(..., ge=0, description="Number of bison detected")
    movement: MovementDirection = Field(..., description="Direction of bison movement")
    fps: float = Field(..., ge=0, description="Frames per second of the video stream")
    source: DataSource = Field(..., description="Source of the detection data")
    tracks: List[TrackingInfo] = Field(..., description="Detailed tracking information")
    frame_width: int = Field(..., description="Width of the video frame")
    frame_height: int = Field(..., description="Height of the video frame")

class APIResponse(BaseModel):
    """Generic API response model"""
    success: bool = Field(..., description="Whether the request was successful")
    message: str = Field(..., description="Response message")
    data: Optional[Any] = Field(None, description="Response data")
    timestamp: str = Field(..., description="Response timestamp")

class ErrorResponse(BaseModel):
    """Model for error responses"""
    error: str = Field(..., description="Error type")
    message: str = Field(..., description="Error message")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional error details")
    timestamp: str = Field(..., description="Error timestamp")

class StreamMetrics(BaseModel):
    """Model for stream performance metrics"""
    total_frames_processed: int = Field(..., description="Total frames processed")
    total_detections: int = Field(..., description="Total detections made")
    average_fps: float = Field(..., description="Average FPS over time window")
    stream_uptime_seconds: float = Field(..., description="Stream uptime in seconds")
    last_frame_time: Optional[str] = Field(None, description="Timestamp of last frame processed")
    connection_quality: str = Field(..., description="Connection quality assessment")
