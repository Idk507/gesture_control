"""
Camera capture module for gesture control library.

Handles webcam access, frame capture, and preprocessing for real-time hand gesture recognition.
"""

import cv2
import numpy as np
import time
from typing import Optional, Tuple
import logging

# Set up logging
logger = logging.getLogger(__name__)


class CameraCapture:
    """
    Handles camera capture and frame preprocessing for gesture recognition.

    Optimizes for real-time performance with configurable resolution and frame rate.
    """

    def __init__(self, camera_index: int = 0, width: int = 640, height: int = 480, fps: int = 30):
        """
        Initialize camera capture.

        Args:
            camera_index: Camera device index (0 for default webcam)
            width: Frame width in pixels
            height: Frame height in pixels
            fps: Target frames per second
        """
        self.camera_index = camera_index
        self.width = width
        self.height = height
        self.fps = fps
        self.cap = None
        self.is_running = False

        logger.info(f"CameraCapture initialized: {width}x{height} @ {fps} FPS")

    def start(self) -> bool:
        """
        Start camera capture.

        Returns:
            True if camera started successfully, False otherwise
        """
        try:
            self.cap = cv2.VideoCapture(self.camera_index)

            if not self.cap.isOpened():
                logger.error(f"Failed to open camera {self.camera_index}")
                return False

            # Configure camera settings
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
            self.cap.set(cv2.CAP_PROP_FPS, self.fps)

            # Additional optimizations
            self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)  # Minimize buffer lag

            self.is_running = True
            logger.info("Camera capture started successfully")
            return True

        except Exception as e:
            logger.error(f"Error starting camera: {e}")
            return False

    def read_frame(self) -> Optional[np.ndarray]:
        """
        Capture and preprocess a single frame.

        Returns:
            Preprocessed RGB frame as numpy array, or None if capture failed
        """
        if not self.is_running or self.cap is None:
            logger.warning("Camera not running")
            return None

        try:
            ret, frame = self.cap.read()

            if not ret or frame is None:
                logger.warning("Failed to read frame from camera")
                return None

            # Convert BGR to RGB for MediaPipe compatibility
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            return rgb_frame

        except Exception as e:
            logger.error(f"Error reading frame: {e}")
            return None

    def get_frame_dimensions(self) -> Tuple[int, int]:
        """
        Get the actual frame dimensions.

        Returns:
            Tuple of (width, height)
        """
        if self.cap is None:
            return (self.width, self.height)

        actual_width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        actual_height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

        return (actual_width, actual_height)

    def stop(self):
        """Stop camera capture and release resources."""
        self.is_running = False

        if self.cap is not None:
            self.cap.release()
            self.cap = None

        logger.info("Camera capture stopped")

    def __enter__(self):
        """Context manager entry."""
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.stop()
