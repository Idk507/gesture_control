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
                 use_mock_detection: bool = None):
        """
        Initialize the gesture control system.

        Args:
            camera_index: Camera device index
            width: Frame width
            height: Frame height
            fps: Target frames per second
            show_preview: Show live preview window
            use_mock_detection: Force mock hand detection
        """
        self.camera_index = camera_index
        self.width = width
        self.height = height
        self.fps = fps
        self.show_preview = show_preview

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
            logger.info("   - Pinch: Click")
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
                enable_safety=True
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

            # 5. Update preview
            if self.show_preview:
                self._update_preview(frame, hands, gesture_result, action_result)

            return True

        except Exception as e:
            logger.error(f"Frame processing error: {e}")
            return False

    def _update_preview(self, frame: np.ndarray, hands, gesture_result: Optional[GestureResult],
                       action_result: Optional[ActionResult]):
        """Update the preview window with overlays."""
        try:
            # Draw hand landmarks
            display_frame = self.detector.draw_landmarks(frame.copy(), hands)

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
