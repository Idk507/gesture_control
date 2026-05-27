"""
Main control system for gesture control library.

Integrates all components into a cohesive gesture control system.
"""

import cv2
import numpy as np
import time
import threading
import logging
from typing import Optional, Dict, Any
from enum import Enum

# Set up logging
logger = logging.getLogger(__name__)

# Import all modules
from .core.capture import CameraCapture
from .core.detection import HandDetector
from .core.gestures import GestureRecognizer, GestureResult
from .core.actions import ActionExecutor, ActionResult


class SystemState(Enum):
    """System operational states."""

    STOPPED = "stopped"
    STARTING = "starting"
    RUNNING = "running"
    PAUSED = "paused"
    ERROR = "error"


class GestureControl:
    """
    Main gesture control system integrating all components.

    Provides the simple API: GestureControl().start()
    """

    def __init__(self,
                 camera_index: int = 0,
                 width: int = 640,
                 height: int = 480,
                 fps: int = 30,
                 show_preview: bool = True,
                 show_camera_overlay: bool = True,
                 use_mock_detection: bool = None,
                 enable_click: bool = False,
                 enable_cursor_tracking: bool = False):
        """
        Initialize the gesture control system.

        Args:
            camera_index: Camera device index
            width: Frame width
            height: Frame height
            fps: Target frames per second
            show_preview: Show live preview window
            show_camera_overlay: Show small camera preview in corner of window
            use_mock_detection: Force mock hand detection
            enable_click: Allow mouse click action from pinch gesture
            enable_cursor_tracking: Move cursor based on hand position (in addition to gestures)
        """
        self.camera_index = camera_index
        self.width = width
        self.height = height
        self.fps = fps
        self.show_preview = show_preview
        self.show_camera_overlay = show_camera_overlay
        self.enable_cursor_tracking = enable_cursor_tracking

        # System state
        self.state = SystemState.STOPPED
        self.running = False

        # Components
        self.camera = None
        self.detector = None
        self.recognizer = None
        self.executor = None

        # Statistics
        self.frame_count = 0
        self.hand_detection_count = 0
        self.gesture_count = 0
        self.action_count = 0
        self.start_time = None

        # Mock detection setting
        self.use_mock_detection = use_mock_detection
        self.enable_click = enable_click

        # Preview window
        self.window_name = "Gesture Control - Press 'q' to quit, 'p' to pause"

        logger.info("GestureControl initialized")

    def start(self) -> bool:
        """
        Start the gesture control system.

        This is the main API method as specified in the README.

        Returns:
            True if started successfully, False otherwise
        """
        if self.state != SystemState.STOPPED:
            logger.warning(f"System already {self.state.value}, cannot start")
            return False

        logger.info("Starting gesture control system...")
        self.state = SystemState.STARTING

        try:
            # Initialize components
            if not self._initialize_components():
                self.state = SystemState.ERROR
                return False

            self.state = SystemState.RUNNING
            self.running = True
            self.start_time = time.time()

            logger.info("✅ Gesture control system started successfully")
            logger.info("🎯 Perform hand gestures to control scrolling!")
            logger.info("   - Swipe down: Scroll down")
            logger.info("   - Swipe up: Scroll up")
            if self.enable_click:
                logger.info("   - Pinch: Click")
            if self.enable_cursor_tracking:
                logger.info("   - Open hand: Move cursor")
            logger.info("   - Press 'q' to quit, 'p' to pause")

            # Start main loop
            self._main_loop()

            return True

        except Exception as e:
            logger.error(f"Failed to start system: {e}")
            self.state = SystemState.ERROR
            return False

    def stop(self):
        """Stop the gesture control system."""
        logger.info("Stopping gesture control system...")

        self.running = False
        self.state = SystemState.STOPPED

        # Clean up components
        self._cleanup_components()

        # Close preview window
        if self.show_preview:
            cv2.destroyAllWindows()

        logger.info("✅ Gesture control system stopped")

    def pause(self):
        """Pause the system."""
        if self.state == SystemState.RUNNING:
            self.state = SystemState.PAUSED
            logger.info("System paused")
        elif self.state == SystemState.PAUSED:
            self.state = SystemState.RUNNING
            logger.info("System resumed")

    def _initialize_components(self) -> bool:
        """Initialize all system components."""
        try:
            # Camera
            self.camera = CameraCapture(
                camera_index=self.camera_index,
                width=self.width,
                height=self.height,
                fps=self.fps
            )

            if not self.camera.start():
                logger.error("Failed to initialize camera")
                return False

            # Hand detector
            self.detector = HandDetector(
                max_hands=1,  # Single hand for simplicity
                detection_confidence=0.7,
                use_mock=self.use_mock_detection
            )

            # Gesture recognizer
            self.recognizer = GestureRecognizer(
                swipe_threshold=0.08,
                pinch_threshold=0.04,
                smoothing_frames=5,
                min_confidence=0.6
            )

            # Action executor
            self.executor = ActionExecutor(
                scroll_amount=2,
                action_cooldown=0.3,
                enable_safety=True,
                enable_click=self.enable_click,
            )

            logger.info("✅ All components initialized")
            return True

        except Exception as e:
            logger.error(f"Component initialization failed: {e}")
            return False

    def _cleanup_components(self):
        """Clean up all components."""
        try:
            if self.camera:
                self.camera.stop()
            if self.detector:
                self.detector.close()
            # Other components don't need explicit cleanup

            logger.info("Components cleaned up")

        except Exception as e:
            logger.error(f"Error during cleanup: {e}")

    def _main_loop(self):
        """Main processing loop."""
        logger.info("Starting main processing loop...")

        try:
            while self.running:
                if self.state == SystemState.PAUSED:
                    time.sleep(0.1)
                    continue

                # Process one frame
                if not self._process_frame():
                    time.sleep(0.01)  # Small delay on errors
                    continue

                self.frame_count += 1

                # Show stats every 100 frames
                if self.frame_count % 100 == 0:
                    self._log_stats()

        except KeyboardInterrupt:
            logger.info("Received keyboard interrupt")
        except Exception as e:
            logger.error(f"Error in main loop: {e}")
            self.state = SystemState.ERROR
        finally:
            self.stop()

    def _process_frame(self) -> bool:
        """Process a single frame through the pipeline."""
        try:
            # 1. Capture frame
            frame = self.camera.read_frame()
            if frame is None:
                return False

            # 2. Detect hands
            hands = self.detector.detect_hands(frame)
            if hands:
                self.hand_detection_count += 1

            # 3. Process gestures
            gesture_result = None
            if hands:
                gesture_result = self.recognizer.recognize_gesture(hands[0])
                if gesture_result.gesture_type.name != "NONE":
                    self.gesture_count += 1

            # 4. Execute actions
            action_result = None
            if gesture_result:
                action_result = self.executor.execute_gesture(gesture_result)
                if action_result.success and action_result.action_type.name != "NONE":
                    self.action_count += 1

            # 5. Handle cursor tracking if enabled
            if self.enable_cursor_tracking and hands:
                self._update_cursor_position(hands[0], frame.shape)

            # 6. Update preview
            if self.show_preview:
                self._update_preview(frame, hands, gesture_result, action_result)

            return True

        except Exception as e:
            logger.error(f"Frame processing error: {e}")
            return False

    def _update_cursor_position(self, hand_data, frame_shape):
        """Update cursor position based on index finger tip for precise control."""
        try:
            import pyautogui
            
            # Get index finger tip position (landmark 8 in MediaPipe)
            if hasattr(hand_data, 'landmarks') and hand_data.landmarks:
                # Get index finger tip landmark (index 8)
                index_tip = hand_data.landmarks.get(8) if isinstance(hand_data.landmarks, dict) else hand_data.get_landmark(8)
                
                if index_tip:
                    # Handle both dict format (new API) and object format (old API)
                    if isinstance(index_tip, dict):
                        finger_x = index_tip['x']
                        finger_y = index_tip['y']
                    else:
                        finger_x = index_tip.x
                        finger_y = index_tip.y
                    
                    # Get screen size
                    screen_width, screen_height = pyautogui.size()
                    
                    # Map finger position to screen (with smoothing factor)
                    # Flip X axis for natural mirror-like control
                    screen_x = int((1.0 - finger_x) * screen_width)
                    screen_y = int(finger_y * screen_height)
                    
                    # Move cursor smoothly
                    pyautogui.moveTo(screen_x, screen_y, duration=0.05)
                
            elif isinstance(hand_data, dict) and 'landmarks' in hand_data:
                # Mock hand data structure
                landmarks = hand_data['landmarks']
                if len(landmarks) > 8:
                    finger = landmarks[8]  # Index finger tip
                    screen_width, screen_height = pyautogui.size()
                    screen_x = int((1.0 - finger[0]) * screen_width)
                    screen_y = int(finger[1] * screen_height)
                    pyautogui.moveTo(screen_x, screen_y, duration=0.05)
                    
        except Exception as e:
            logger.error(f"Cursor tracking error: {e}")

    def _update_preview(self, frame: np.ndarray, hands, gesture_result: Optional[GestureResult],
                       action_result: Optional[ActionResult]):
        """Update the preview window with overlays."""
        try:
            # Draw hand landmarks
            display_frame = self.detector.draw_landmarks(frame.copy(), hands)

            # Add camera overlay in corner if enabled
            if self.show_camera_overlay:
                self._add_camera_overlay(display_frame, frame)

            # Add status overlay
            self._add_status_overlay(display_frame, gesture_result, action_result)

            # Show frame
            cv2.imshow(self.window_name, display_frame)

            # Handle keyboard input
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                self.running = False
            elif key == ord('p'):
                self.pause()

        except Exception as e:
            logger.error(f"Preview update error: {e}")

    def _add_camera_overlay(self, display_frame: np.ndarray, original_frame: np.ndarray):
        """Add small camera preview in corner of window."""
        h, w = display_frame.shape[:2]
        
        # Size of the camera overlay (width, height)
        overlay_width = 160
        overlay_height = 120
        
        # Position in bottom-right corner with margin
        margin = 10
        x_pos = w - overlay_width - margin
        y_pos = h - overlay_height - margin
        
        # Resize original frame to overlay size
        overlay = cv2.resize(original_frame, (overlay_width, overlay_height))
        
        # Add border around overlay
        cv2.rectangle(display_frame, 
                     (x_pos - 2, y_pos - 2), 
                     (x_pos + overlay_width + 2, y_pos + overlay_height + 2),
                     (255, 255, 255), 2)
        
        # Place overlay on display frame
        display_frame[y_pos:y_pos+overlay_height, x_pos:x_pos+overlay_width] = overlay
        
        # Add label
        cv2.putText(display_frame, "Camera", (x_pos, y_pos - 5),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)

    def _add_status_overlay(self, frame: np.ndarray, gesture_result: Optional[GestureResult],
                           action_result: Optional[ActionResult]):
        """Add status information overlay to the frame."""
        h, w = frame.shape[:2]

        # Background rectangle
        cv2.rectangle(frame, (10, 10), (300, 120), (0, 0, 0), -1)
        cv2.rectangle(frame, (10, 10), (300, 120), (255, 255, 255), 1)

        # Status text
        y_offset = 30
        cv2.putText(frame, f"Status: {self.state.value.upper()}", (20, y_offset),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

        y_offset += 20
        fps = self.frame_count / (time.time() - self.start_time) if self.start_time else 0
        cv2.putText(frame, f"FPS: {fps:.1f}", (20, y_offset),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

        y_offset += 20
        gesture_text = gesture_result.gesture_type.value if gesture_result else "none"
        cv2.putText(frame, f"Gesture: {gesture_text}", (20, y_offset),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

        y_offset += 20
        action_text = action_result.action_type.value if action_result else "none"
        cv2.putText(frame, f"Action: {action_text}", (20, y_offset),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

        # Hands detected indicator
        hand_color = (0, 255, 0) if self.hand_detection_count > 0 else (0, 0, 255)
        cv2.circle(frame, (w-30, 30), 10, hand_color, -1)
        cv2.putText(frame, "Hand", (w-80, 35), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)

    def _log_stats(self):
        """Log current system statistics."""
        elapsed = time.time() - self.start_time if self.start_time else 0
        fps = self.frame_count / elapsed if elapsed > 0 else 0

        logger.info(f"Stats: Frames={self.frame_count}, FPS={fps:.1f}, "
                   f"Hands={self.hand_detection_count}, Gestures={self.gesture_count}, "
                   f"Actions={self.action_count}")

    def get_system_stats(self) -> Dict[str, Any]:
        """Get comprehensive system statistics."""
        elapsed = time.time() - self.start_time if self.start_time else 0

        return {
            'state': self.state.value,
            'running': self.running,
            'elapsed_time': elapsed,
            'frame_count': self.frame_count,
            'fps': self.frame_count / elapsed if elapsed > 0 else 0,
            'hand_detection_count': self.hand_detection_count,
            'gesture_count': self.gesture_count,
            'action_count': self.action_count,
            'components': {
                'camera': self.camera is not None,
                'detector': self.detector is not None,
                'recognizer': self.recognizer is not None,
                'executor': self.executor is not None,
            }
        }

    # Alias for backward compatibility with README
    def GestureScroll(self):
        """Alias for start() method to match README API."""
        return self.start()

    def __enter__(self):
        """Context manager entry."""
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.stop()
