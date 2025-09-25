"""
Detection service for processing RTSP stream and running YOLO inference
"""

import cv2
import numpy as np
import time
import threading
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from collections import deque
from ultralytics import YOLO
from pathlib import Path

from models import BisonDetection, MovementDirection, DataSource, TrackingInfo, DetailedDetection
from config import Config

logger = logging.getLogger(__name__)

class DetectionService:
    """Service for handling bison detection and tracking"""
    
    def __init__(self):
        self.model: Optional[YOLO] = None
        self.cap: Optional[cv2.VideoCapture] = None
        self.processing_thread: Optional[threading.Thread] = None
        self.stop_processing = False
        
        # Detection storage
        self.detection_history = deque(maxlen=Config.HISTORY_SIZE)
        self.latest_detection: Optional[BisonDetection] = None
        
        # Tracking state
        self.previous_positions: Dict[int, Tuple[float, float]] = {}
        self.track_history: Dict[int, deque] = {}
        
        # Performance metrics
        self.fps_counter = 0
        self.start_time = time.time()
        self.total_frames_processed = 0
        self.total_detections = 0
        
        # Stream status
        self.stream_active = False
        self.model_loaded = False
        self.last_detection_time: Optional[datetime] = None
        
    def load_model(self) -> bool:
        """Load YOLO model"""
        try:
            model_path = Config.get_model_path()
            if model_path.exists():
                self.model = YOLO(str(model_path))
                logger.info(f"Loaded custom YOLO model from {model_path}")
            else:
                self.model = YOLO(Config.FALLBACK_MODEL)
                logger.info(f"Loaded default YOLO model: {Config.FALLBACK_MODEL}")
            
            self.model_loaded = True
            logger.info("YOLO model loaded successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to load YOLO model: {e}")
            self.model_loaded = False
            return False
    
    def connect_rtsp(self) -> bool:
        """Connect to RTSP stream"""
        try:
            self.cap = cv2.VideoCapture(Config.RTSP_URL)
            self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)  # Reduce buffer size for real-time processing
            
            if not self.cap.isOpened():
                logger.error("Failed to open RTSP stream")
                return False
            
            # Test read
            ret, frame = self.cap.read()
            if not ret:
                logger.error("Failed to read initial frame from RTSP stream")
                self.cap.release()
                return False
            
            self.stream_active = True
            logger.info("RTSP stream connected successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error connecting to RTSP stream: {e}")
            self.stream_active = False
            return False
    
    def calculate_movement(self, current_positions: Dict[int, Tuple[float, float]]) -> MovementDirection:
        """Calculate movement direction based on position changes"""
        if not self.previous_positions:
            return MovementDirection.STATIONARY
        
        total_dx = 0
        total_dy = 0
        valid_tracks = 0
        
        for track_id, current_pos in current_positions.items():
            if track_id in self.previous_positions:
                prev_pos = self.previous_positions[track_id]
                dx = current_pos[0] - prev_pos[0]
                dy = current_pos[1] - prev_pos[1]
                
                # Only consider significant movements
                if abs(dx) > Config.MOVEMENT_THRESHOLD or abs(dy) > Config.MOVEMENT_THRESHOLD:
                    total_dx += dx
                    total_dy += dy
                    valid_tracks += 1
        
        if valid_tracks == 0:
            return MovementDirection.STATIONARY
        
        avg_dx = total_dx / valid_tracks
        avg_dy = total_dy / valid_tracks
        
        # Determine primary direction
        if abs(avg_dx) > abs(avg_dy):
            return MovementDirection.EAST if avg_dx > 0 else MovementDirection.WEST
        else:
            return MovementDirection.SOUTH if avg_dy > 0 else MovementDirection.NORTH
    
    def extract_tracking_info(self, results) -> Tuple[List[TrackingInfo], Dict[int, Tuple[float, float]]]:
        """Extract tracking information from YOLO results"""
        tracks = []
        current_positions = {}
        
        for result in results:
            if result.boxes is not None and result.boxes.id is not None:
                boxes = result.boxes.xyxy.cpu().numpy()
                confidences = result.boxes.conf.cpu().numpy()
                class_ids = result.boxes.cls.cpu().numpy()
                track_ids = result.boxes.id.cpu().numpy()
                
                for i, (box, conf, class_id, track_id) in enumerate(zip(boxes, confidences, class_ids, track_ids)):
                    # Filter for bison class (adjust class ID as needed)
                    if int(class_id) == Config.BISON_CLASS_ID and conf >= Config.CONFIDENCE_THRESHOLD:
                        x1, y1, x2, y2 = box
                        center_x = (x1 + x2) / 2
                        center_y = (y1 + y2) / 2
                        
                        # Calculate velocity if we have previous position
                        velocity_x = velocity_y = None
                        if int(track_id) in self.previous_positions:
                            prev_x, prev_y = self.previous_positions[int(track_id)]
                            velocity_x = center_x - prev_x
                            velocity_y = center_y - prev_y
                        
                        track_info = TrackingInfo(
                            track_id=int(track_id),
                            bbox=[float(x1), float(y1), float(x2), float(y2)],
                            confidence=float(conf),
                            class_id=int(class_id),
                            class_name="bison",
                            center_x=float(center_x),
                            center_y=float(center_y),
                            velocity_x=velocity_x,
                            velocity_y=velocity_y
                        )
                        
                        tracks.append(track_info)
                        current_positions[int(track_id)] = (center_x, center_y)
        
        return tracks, current_positions
    
    def process_frame(self, frame: np.ndarray) -> Optional[BisonDetection]:
        """Process a single frame and return detection results"""
        if self.model is None:
            return None
        
        try:
            # Run YOLO inference with tracking
            results = self.model.track(
                frame, 
                persist=True, 
                verbose=False,
                conf=Config.CONFIDENCE_THRESHOLD,
                iou=Config.IOU_THRESHOLD
            )
            
            # Extract tracking information
            tracks, current_positions = self.extract_tracking_info(results)
            
            # Count bison detections
            bison_count = len(tracks)
            
            # Calculate movement
            movement = self.calculate_movement(current_positions)
            self.previous_positions = current_positions.copy()
            
            # Calculate FPS
            self.fps_counter += 1
            current_time = time.time()
            elapsed_time = current_time - self.start_time
            fps = self.fps_counter / elapsed_time if elapsed_time > 0 else 0
            
            # Update metrics
            self.total_frames_processed += 1
            if bison_count > 0:
                self.total_detections += 1
            
            # Create detection record
            detection = BisonDetection(
                timestamp=datetime.utcnow().isoformat() + "Z",
                bison_count=bison_count,
                movement=movement,
                fps=round(fps, 1),
                source=DataSource.RTSP
            )
            
            self.latest_detection = detection
            self.detection_history.append(detection)
            self.last_detection_time = datetime.utcnow()
            
            # Log detection
            if bison_count > 0:
                logger.info(f"Detected {bison_count} bison(s), movement: {movement.value}, FPS: {fps:.1f}")
            
            return detection
            
        except Exception as e:
            logger.error(f"Error processing frame: {e}")
            return None
    
    def process_stream(self):
        """Main processing loop for RTSP stream"""
        logger.info("Starting RTSP stream processing")
        
        while not self.stop_processing:
            try:
                if self.cap is None or not self.cap.isOpened():
                    logger.warning("RTSP stream not available, attempting to reconnect...")
                    if not self.connect_rtsp():
                        time.sleep(5)  # Wait before retry
                        continue
                
                ret, frame = self.cap.read()
                if not ret:
                    logger.warning("Failed to read frame from RTSP stream")
                    time.sleep(0.1)
                    continue
                
                # Process frame
                self.process_frame(frame)
                
                # Control frame rate
                time.sleep(1.0 / Config.VIDEO_FPS)
                
            except Exception as e:
                logger.error(f"Error in stream processing: {e}")
                self.stream_active = False
                time.sleep(1)
    
    def start_processing(self):
        """Start the detection processing in a background thread"""
        if self.processing_thread is None or not self.processing_thread.is_alive():
            self.stop_processing = False
            self.processing_thread = threading.Thread(target=self.process_stream, daemon=True)
            self.processing_thread.start()
            logger.info("Started detection processing thread")
    
    def stop_processing_service(self):
        """Stop the detection processing"""
        self.stop_processing = True
        if self.cap:
            self.cap.release()
        logger.info("Stopped detection processing")
    
    def get_latest_detection(self) -> Optional[BisonDetection]:
        """Get the latest detection"""
        return self.latest_detection
    
    def get_detection_history(self, minutes: int = 15) -> List[BisonDetection]:
        """Get detection history for the specified time window"""
        if not self.detection_history:
            return []
        
        cutoff_time = datetime.utcnow() - timedelta(minutes=minutes)
        cutoff_str = cutoff_time.isoformat() + "Z"
        
        return [
            detection for detection in self.detection_history
            if detection.timestamp >= cutoff_str
        ]
    
    def get_system_metrics(self) -> Dict[str, any]:
        """Get system performance metrics"""
        current_time = time.time()
        uptime = current_time - self.start_time
        
        return {
            "total_frames_processed": self.total_frames_processed,
            "total_detections": self.total_detections,
            "average_fps": self.fps_counter / uptime if uptime > 0 else 0,
            "stream_uptime_seconds": uptime,
            "last_detection_time": self.last_detection_time.isoformat() + "Z" if self.last_detection_time else None,
            "connection_quality": "good" if self.stream_active else "poor"
        }

# Global detection service instance
detection_service = DetectionService()
