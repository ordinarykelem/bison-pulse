"""
Video streaming service for MJPEG and HLS streams
"""

import cv2
import numpy as np
import asyncio
import logging
import threading
from typing import Optional, AsyncGenerator
from datetime import datetime

from detection_service import detection_service
from config import Config

logger = logging.getLogger(__name__)

class VideoService:
    """Service for handling video streaming with detection overlays"""
    
    def __init__(self):
        self.cap: Optional[cv2.VideoCapture] = None
        self.stream_active = False
        self.frame_buffer = None
        self.buffer_lock = threading.Lock()
        
    def connect_stream(self) -> bool:
        """Connect to the video stream"""
        try:
            self.cap = cv2.VideoCapture(Config.RTSP_URL)
            self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
            
            if not self.cap.isOpened():
                logger.error("Failed to open video stream")
                return False
            
            self.stream_active = True
            logger.info("Video stream connected successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error connecting to video stream: {e}")
            self.stream_active = False
            return False
    
    def draw_detection_overlay(self, frame: np.ndarray) -> np.ndarray:
        """Draw detection information overlay on frame"""
        overlay_frame = frame.copy()
        
        # Get latest detection info
        latest_detection = detection_service.get_latest_detection()
        
        if latest_detection:
            # Draw detection info
            cv2.putText(overlay_frame, f"Bison Count: {latest_detection.bison_count}", 
                       (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            cv2.putText(overlay_frame, f"Movement: {latest_detection.movement.value}", 
                       (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            cv2.putText(overlay_frame, f"FPS: {latest_detection.fps}", 
                       (10, 110), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            
            # Draw timestamp
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cv2.putText(overlay_frame, timestamp, 
                       (10, overlay_frame.shape[0] - 20), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        # Draw connection status
        status_color = (0, 255, 0) if self.stream_active else (0, 0, 255)
        status_text = "LIVE" if self.stream_active else "OFFLINE"
        cv2.putText(overlay_frame, status_text, 
                   (overlay_frame.shape[1] - 100, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1, status_color, 2)
        
        return overlay_frame
    
    def create_placeholder_frame(self) -> np.ndarray:
        """Create a placeholder frame when stream is unavailable"""
        placeholder = np.zeros((Config.VIDEO_HEIGHT, Config.VIDEO_WIDTH, 3), dtype=np.uint8)
        
        # Add text overlay
        cv2.putText(placeholder, "Stream Unavailable", 
                   (150, Config.VIDEO_HEIGHT // 2 - 40), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1.5, (255, 255, 255), 2)
        
        cv2.putText(placeholder, "Connecting to RTSP...", 
                   (120, Config.VIDEO_HEIGHT // 2 + 20), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (200, 200, 200), 2)
        
        # Add timestamp
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cv2.putText(placeholder, timestamp, 
                   (10, Config.VIDEO_HEIGHT - 20), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        return placeholder
    
    async def generate_mjpeg_frames(self) -> AsyncGenerator[bytes, None]:
        """Generate MJPEG frames for streaming"""
        while True:
            try:
                if self.cap is None or not self.cap.isOpened():
                    # Try to reconnect
                    if not self.connect_stream():
                        # Send placeholder frame
                        placeholder = self.create_placeholder_frame()
                        _, buffer = cv2.imencode('.jpg', placeholder, 
                                               [cv2.IMWRITE_JPEG_QUALITY, Config.MJPEG_QUALITY])
                        frame_bytes = buffer.tobytes()
                        
                        yield (b'--frame\r\n'
                               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
                        await asyncio.sleep(1)  # Wait before retry
                        continue
                
                ret, frame = self.cap.read()
                if not ret:
                    logger.warning("Failed to read frame from video stream")
                    await asyncio.sleep(0.1)
                    continue
                
                # Resize frame if needed
                if frame.shape[:2] != (Config.VIDEO_HEIGHT, Config.VIDEO_WIDTH):
                    frame = cv2.resize(frame, (Config.VIDEO_WIDTH, Config.VIDEO_HEIGHT))
                
                # Draw detection overlay
                overlay_frame = self.draw_detection_overlay(frame)
                
                # Encode frame as JPEG
                _, buffer = cv2.imencode('.jpg', overlay_frame, 
                                       [cv2.IMWRITE_JPEG_QUALITY, Config.MJPEG_QUALITY])
                frame_bytes = buffer.tobytes()
                
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
                
                await asyncio.sleep(1.0 / Config.VIDEO_FPS)
                
            except Exception as e:
                logger.error(f"Error generating MJPEG frame: {e}")
                await asyncio.sleep(0.1)
    
    def generate_hls_playlist(self) -> str:
        """Generate HLS playlist content"""
        # This is a simplified HLS playlist
        # In a production environment, you would need proper HLS encoding
        playlist_content = f"""#EXTM3U
#EXT-X-VERSION:3
#EXT-X-TARGETDURATION:10
#EXT-X-MEDIA-SEQUENCE:0
#EXTINF:10.0,
stream.m3u8
#EXT-X-ENDLIST"""
        
        return playlist_content
    
    def cleanup(self):
        """Cleanup video resources"""
        if self.cap:
            self.cap.release()
        self.stream_active = False
        logger.info("Video service cleaned up")

# Global video service instance
video_service = VideoService()
