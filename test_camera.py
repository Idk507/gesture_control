#!/usr/bin/env python
# coding: utf-8

# # Camera Capture Module
# 
# This notebook demonstrates the camera capture functionality for the gesture control library.
# It handles webcam access, frame capture, and preprocessing for real-time hand gesture recognition.
# 
# ## Requirements
# - OpenCV (cv2)
# - NumPy

# In[1]:


import cv2
import numpy as np
import time
from typing import Optional, Tuple
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ## Camera Capture Class
# 
# The CameraCapture class handles:
# - Webcam initialization and configuration
# - Frame capture with optimized settings
# - Image preprocessing (RGB conversion, resizing)
# - Resource management and cleanup

# In[2]:


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


# ## Testing Camera Capture
# 
# Let's test the camera capture functionality with a simple demo.

# In[3]:


# Test camera capture
def test_camera_capture():
    """Test the camera capture functionality."""

    print("Testing Camera Capture...")

    # Initialize camera
    camera = CameraCapture(width=640, height=480, fps=30)

    if not camera.start():
        print("❌ Failed to start camera")
        return

    print("✅ Camera started successfully")

    # Capture a few frames
    for i in range(5):
        frame = camera.read_frame()
        if frame is not None:
            print(f"✅ Frame {i+1}: Shape {frame.shape}, dtype {frame.dtype}")
        else:
            print(f"❌ Frame {i+1}: Failed to capture")

        time.sleep(0.1)  # Small delay between captures

    # Get frame dimensions
    width, height = camera.get_frame_dimensions()
    print(f"📐 Frame dimensions: {width}x{height}")

    # Stop camera
    camera.stop()
    print("✅ Camera stopped successfully")

# Run the test
test_camera_capture()


# ## Performance Testing
# 
# Let's measure the capture performance and frame rate.

# In[4]:


# Performance test
def performance_test():
    """Test camera capture performance."""

    print("Performance Testing...")

    camera = CameraCapture(width=640, height=480, fps=30)

    if not camera.start():
        print("❌ Failed to start camera")
        return

    # Capture frames for 3 seconds
    start_time = time.time()
    frame_count = 0

    while time.time() - start_time < 3.0:
        frame = camera.read_frame()
        if frame is not None:
            frame_count += 1

    end_time = time.time()

    # Calculate performance metrics
    duration = end_time - start_time
    fps_actual = frame_count / duration

    print(f"📊 Performance Results:")
    print(f"   Duration: {duration:.2f} seconds")
    print(f"   Frames captured: {frame_count}")
    print(f"   Actual FPS: {fps_actual:.2f}")
    print(f"   Target FPS: {camera.fps}")

    camera.stop()

# Run performance test
performance_test()


# ## Context Manager Usage
# 
# Demonstrate the context manager functionality for automatic resource management.

# In[5]:


# Context manager test
def test_context_manager():
    """Test using camera with context manager."""

    print("Testing Context Manager...")

    try:
        with CameraCapture(width=640, height=480) as camera:
            if camera.is_running:
                print("✅ Camera started with context manager")

                # Capture one frame
                frame = camera.read_frame()
                if frame is not None:
                    print(f"✅ Frame captured: {frame.shape}")
                else:
                    print("❌ Failed to capture frame")
            else:
                print("❌ Camera failed to start")

    except Exception as e:
        print(f"❌ Error: {e}")

    print("✅ Context manager test completed (camera should be stopped automatically)")

# Run context manager test
test_context_manager()


# ## Error Handling and Edge Cases
# 
# Test error handling for various scenarios.

# In[6]:


# Error handling test
def test_error_handling():
    """Test error handling scenarios."""

    print("Testing Error Handling...")

    # Test with invalid camera index
    print("1. Testing invalid camera index...")
    camera = CameraCapture(camera_index=999)
    success = camera.start()
    print(f"   Invalid camera index result: {'Success' if success else 'Failed (expected)'}")
    camera.stop()

    # Test reading frame when camera not started
    print("2. Testing read_frame when camera not started...")
    camera = CameraCapture()
    frame = camera.read_frame()
    print(f"   Read frame result: {'Got frame' if frame is not None else 'None (expected)'}")

    # Test double stop
    print("3. Testing double stop...")
    camera.stop()  # Should handle gracefully
    camera.stop()  # Should handle gracefully
    print("   Double stop completed without error")

    print("✅ Error handling tests completed")

# Run error handling test
test_error_handling()


# ## Summary
# 
# This notebook has implemented a robust camera capture module with:
# 
# - **Real-time frame capture** from webcam
# - **Optimized settings** for performance (resolution, FPS, buffer size)
# - **RGB conversion** for MediaPipe compatibility
# - **Resource management** with context manager support
# - **Error handling** for various failure scenarios
# - **Performance monitoring** capabilities
# 
# ### Next Steps
# - Integrate with MediaPipe for hand detection
# - Add gesture recognition logic
# - Implement OS-level action mapping
# 
# ### Performance Notes
# - 640x480 resolution provides good balance of quality and speed
# - Buffer size of 1 minimizes latency
# - RGB conversion adds small processing overhead but required for MediaPipe
