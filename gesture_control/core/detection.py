"""
Hand detection module for gesture control library.

Detects hands in images using MediaPipe Hands with fallback to mock implementation.
"""

import cv2
import numpy as np
from typing import Optional, List, Dict, Any, Tuple
import logging
import time

# Set up logging
logger = logging.getLogger(__name__)

# Try to import MediaPipe
try:
    import mediapipe as mp
    MEDIAPIPE_AVAILABLE = True
    logger.info("MediaPipe imported successfully")
except ImportError:
    MEDIAPIPE_AVAILABLE = False
    logger.warning("MediaPipe not available. Using mock implementation.")
    logger.warning("For full functionality, install MediaPipe with: pip install mediapipe")
    logger.warning("Note: MediaPipe requires Python 3.11 or 3.12")


# Hand landmark constants
LANDMARK_NAMES = {
    0: "wrist",
    4: "thumb_tip",
    8: "index_tip",
    12: "middle_tip",
    16: "ring_tip",
    20: "pinky_tip",
    # Add more landmarks as needed
}


class HandLandmarks:
    """Represents hand landmark data."""

    def __init__(self, landmarks_data: Any, handedness: str = "Right"):
        """
        Initialize hand landmarks.

        Args:
            landmarks_data: Raw landmark data from MediaPipe
            handedness: "Left" or "Right" hand
        """
        self.handedness = handedness
        self.landmarks = {}
        self.raw_data = landmarks_data

        # Extract landmark coordinates
        if MEDIAPIPE_AVAILABLE and landmarks_data:
            for idx, landmark in enumerate(landmarks_data.landmark):
                self.landmarks[idx] = {
                    'x': landmark.x,
                    'y': landmark.y,
                    'z': landmark.z,
                    'visibility': getattr(landmark, 'visibility', 1.0)
                }
        else:
            # Mock data for development
            self._generate_mock_landmarks()

    def _generate_mock_landmarks(self):
        """Generate mock landmark data for development/testing."""
        np.random.seed(42)  # For reproducible mock data

        for i in range(21):
            self.landmarks[i] = {
                'x': np.random.uniform(0.3, 0.7),
                'y': np.random.uniform(0.3, 0.7),
                'z': np.random.uniform(-0.1, 0.1),
                'visibility': 0.9 + np.random.uniform(0, 0.1)
            }

    def get_landmark(self, index: int) -> Optional[Dict[str, float]]:
        """Get specific landmark by index."""
        return self.landmarks.get(index)

    def get_finger_tips(self) -> Dict[str, Dict[str, float]]:
        """Get coordinates of all finger tips."""
        tips = {}
        for idx, name in LANDMARK_NAMES.items():
            if '_tip' in name:
                landmark = self.get_landmark(idx)
                if landmark:
                    tips[name] = landmark
        return tips

    def get_wrist_position(self) -> Optional[Dict[str, float]]:
        """Get wrist position."""
        return self.get_landmark(0)

    def get_bounding_box(self) -> Tuple[float, float, float, float]:
        """Get bounding box (min_x, min_y, max_x, max_y)."""
        if not self.landmarks:
            return (0, 0, 0, 0)

        x_coords = [lm['x'] for lm in self.landmarks.values()]
        y_coords = [lm['y'] for lm in self.landmarks.values()]

        return (
            min(x_coords), min(y_coords),
            max(x_coords), max(y_coords)
        )

    def __str__(self):
        return f"HandLandmarks(handedness={self.handedness}, landmarks={len(self.landmarks)})"


class HandDetector:
    """
    Detects hands in images using MediaPipe Hands.

    Provides both real MediaPipe implementation and mock version for development.
    """

    def __init__(self,
                 max_hands: int = 2,
                 detection_confidence: float = 0.7,
                 tracking_confidence: float = 0.5,
                 use_mock: bool = None):
        """
        Initialize hand detector.

        Args:
            max_hands: Maximum number of hands to detect
            detection_confidence: Minimum confidence for hand detection
            tracking_confidence: Minimum confidence for hand tracking
            use_mock: Force use of mock implementation (auto-detected if None)
        """
        self.max_hands = max_hands
        self.detection_confidence = detection_confidence
        self.tracking_confidence = tracking_confidence

        # Determine whether to use mock
        self.use_mock = use_mock if use_mock is not None else not MEDIAPIPE_AVAILABLE

        if self.use_mock:
            logger.info("Using mock hand detection implementation")
            self.mp_hands = None
            self.hands = None
            self.mp_drawing = None
        else:
            logger.info("Using MediaPipe hand detection")
            self.mp_hands = mp.solutions.hands
            self.hands = self.mp_hands.Hands(
                max_num_hands=max_hands,
                min_detection_confidence=detection_confidence,
                min_tracking_confidence=tracking_confidence
            )
            self.mp_drawing = mp.solutions.drawing_utils

    def detect_hands(self, frame: np.ndarray) -> List[HandLandmarks]:
        """
        Detect hands in the given frame.

        Args:
            frame: RGB image frame

        Returns:
            List of HandLandmarks objects for detected hands
        """
        if frame is None:
            return []

        if self.use_mock:
            return self._mock_detect_hands(frame)
        else:
            return self._real_detect_hands(frame)

    def _real_detect_hands(self, frame: np.ndarray) -> List[HandLandmarks]:
        """Real MediaPipe hand detection."""
        try:
            # Process the frame
            results = self.hands.process(frame)

            detected_hands = []

            if results.multi_hand_landmarks and results.multi_handedness:
                for hand_landmarks, handedness in zip(
                    results.multi_hand_landmarks,
                    results.multi_handedness
                ):
                    # Get handedness label
                    hand_label = handedness.classification[0].label

                    # Create HandLandmarks object
                    hand_obj = HandLandmarks(hand_landmarks, hand_label)
                    detected_hands.append(hand_obj)

            return detected_hands

        except Exception as e:
            logger.error(f"Error in hand detection: {e}")
            return []

    def _mock_detect_hands(self, frame: np.ndarray) -> List[HandLandmarks]:
        """Mock hand detection for development/testing."""
        # Simulate random hand detection (0-2 hands)
        num_hands = np.random.choice([0, 1, 2], p=[0.3, 0.5, 0.2])

        detected_hands = []
        for i in range(num_hands):
            # Alternate between left and right hands
            handedness = "Left" if i % 2 == 0 else "Right"

            # Create mock landmarks
            mock_landmarks = self._create_mock_landmark_data()
            hand_obj = HandLandmarks(mock_landmarks, handedness)
            detected_hands.append(hand_obj)

        return detected_hands

    def _create_mock_landmark_data(self):
        """Create mock landmark data object."""
        class MockLandmark:
            def __init__(self, x, y, z, visibility=1.0):
                self.x, self.y, self.z = x, y, z
                self.visibility = visibility

        class MockLandmarks:
            def __init__(self):
                np.random.seed(int(time.time()*1000) % 1000)  # Vary mock data
                self.landmark = []
                for i in range(21):
                    x = np.random.uniform(0.2, 0.8)
                    y = np.random.uniform(0.2, 0.8)
                    z = np.random.uniform(-0.2, 0.2)
                    visibility = 0.8 + np.random.uniform(0, 0.2)
                    self.landmark.append(MockLandmark(x, y, z, visibility))

        return MockLandmarks()

    def draw_landmarks(self, frame: np.ndarray, hands: List[HandLandmarks]) -> np.ndarray:
        """
        Draw hand landmarks on frame for visualization.

        Args:
            frame: RGB frame to draw on
            hands: List of detected hands

        Returns:
            Frame with landmarks drawn
        """
        if self.use_mock or not MEDIAPIPE_AVAILABLE:
            # Simple mock drawing
            for hand in hands:
                min_x, min_y, max_x, max_y = hand.get_bounding_box()
                h, w = frame.shape[:2]

                # Convert normalized to pixel coordinates
                cv2.rectangle(frame,
                            (int(min_x * w), int(min_y * h)),
                            (int(max_x * w), int(max_y * h)),
                            (0, 255, 0), 2)

                # Draw hand label
                cv2.putText(frame, hand.handedness,
                          (int(min_x * w), int(min_y * h) - 10),
                          cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
        else:
            # Real MediaPipe drawing
            frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

            # Convert back to RGB after drawing
            for hand in hands:
                if hand.raw_data:
                    self.mp_drawing.draw_landmarks(
                        frame_bgr, hand.raw_data, self.mp_hands.HAND_CONNECTIONS)

            frame = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)

        return frame

    def close(self):
        """Clean up resources."""
        if not self.use_mock and self.hands:
            self.hands.close()
        logger.info("Hand detector closed")
