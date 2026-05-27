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
    from mediapipe.tasks import python
    from mediapipe.tasks.python import vision
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
            landmarks_data: Raw landmark data from MediaPipe (list of landmarks or NormalizedLandmarkList)
            handedness: "Left" or "Right" hand
        """
        self.handedness = handedness
        self.landmarks = {}
        self.raw_data = landmarks_data

        # Extract landmark coordinates
        if MEDIAPIPE_AVAILABLE and landmarks_data:
            # New MediaPipe API returns a list of NormalizedLandmark objects
            if isinstance(landmarks_data, list):
                for idx, landmark in enumerate(landmarks_data):
                    self.landmarks[idx] = {
                        'x': landmark.x,
                        'y': landmark.y,
                        'z': landmark.z,
                        'visibility': getattr(landmark, 'visibility', 1.0)
                    }
            # Old API compatibility (NormalizedLandmarkList)
            elif hasattr(landmarks_data, 'landmark'):
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
            self.hands = None
            self.mp_drawing = None
        else:
            logger.info("Using MediaPipe hand detection (tasks API)")
            try:
                # Create HandLandmarkerOptions for new API
                base_options = python.BaseOptions(
                    model_asset_path=self._get_model_path()
                )
                options = vision.HandLandmarkerOptions(
                    base_options=base_options,
                    running_mode=vision.RunningMode.IMAGE,
                    num_hands=max_hands,
                    min_hand_detection_confidence=detection_confidence,
                    min_hand_presence_confidence=tracking_confidence,
                    min_tracking_confidence=tracking_confidence
                )
                self.hands = vision.HandLandmarker.create_from_options(options)
                self.mp_drawing = None  # New API doesn't use mp.solutions.drawing_utils
                logger.info("MediaPipe HandLandmarker initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize MediaPipe: {e}")
                logger.warning("Falling back to mock implementation")
                self.use_mock = True
                self.hands = None
                self.mp_drawing = None

    def _get_model_path(self) -> str:
        """Get the path to the hand landmarker model file."""
        import os
        import urllib.request
        
        # Model will be stored in user's home directory
        model_dir = os.path.join(os.path.expanduser("~"), ".mediapipe", "models")
        os.makedirs(model_dir, exist_ok=True)
        
        model_path = os.path.join(model_dir, "hand_landmarker.task")
        
        # Download model if it doesn't exist
        if not os.path.exists(model_path):
            logger.info("Downloading hand landmarker model...")
            model_url = "https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task"
            try:
                urllib.request.urlretrieve(model_url, model_path)
                logger.info(f"Model downloaded to {model_path}")
            except Exception as e:
                logger.error(f"Failed to download model: {e}")
                raise
        
        return model_path

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
        """Real MediaPipe hand detection using new tasks API."""
        try:
            # Convert numpy array to MediaPipe Image
            mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame)
            
            # Detect hands
            detection_result = self.hands.detect(mp_image)

            detected_hands = []

            # Check if hands were detected
            if detection_result.hand_landmarks and detection_result.handedness:
                for hand_landmarks, handedness in zip(
                    detection_result.hand_landmarks,
                    detection_result.handedness
                ):
                    # Get handedness label (Left or Right)
                    hand_label = handedness[0].category_name

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
        # Draw landmarks for each detected hand
        for hand in hands:
            h, w = frame.shape[:2]
            
            # Draw bounding box
            min_x, min_y, max_x, max_y = hand.get_bounding_box()
            cv2.rectangle(frame,
                        (int(min_x * w), int(min_y * h)),
                        (int(max_x * w), int(max_y * h)),
                        (0, 255, 0), 2)

            # Draw hand label
            cv2.putText(frame, hand.handedness,
                      (int(min_x * w), int(min_y * h) - 10),
                      cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
            
            # Draw landmarks (circles for each point)
            for idx, landmark in hand.landmarks.items():
                x_px = int(landmark['x'] * w)
                y_px = int(landmark['y'] * h)
                
                # Draw landmark point
                cv2.circle(frame, (x_px, y_px), 3, (255, 0, 0), -1)
                
                # Draw finger tips larger
                if idx in [4, 8, 12, 16, 20]:  # Finger tips
                    cv2.circle(frame, (x_px, y_px), 5, (0, 255, 255), -1)
            
            # Draw connections between landmarks (simplified)
            connections = [
                # Thumb
                (0, 1), (1, 2), (2, 3), (3, 4),
                # Index
                (0, 5), (5, 6), (6, 7), (7, 8),
                # Middle
                (0, 9), (9, 10), (10, 11), (11, 12),
                # Ring
                (0, 13), (13, 14), (14, 15), (15, 16),
                # Pinky
                (0, 17), (17, 18), (18, 19), (19, 20),
                # Palm
                (5, 9), (9, 13), (13, 17)
            ]
            
            for start_idx, end_idx in connections:
                if start_idx in hand.landmarks and end_idx in hand.landmarks:
                    start = hand.landmarks[start_idx]
                    end = hand.landmarks[end_idx]
                    
                    start_point = (int(start['x'] * w), int(start['y'] * h))
                    end_point = (int(end['x'] * w), int(end['y'] * h))
                    
                    cv2.line(frame, start_point, end_point, (0, 255, 0), 2)

        return frame

    def close(self):
        """Clean up resources."""
        if not self.use_mock and self.hands:
            # New API uses close() method
            self.hands.close()
        logger.info("Hand detector closed")
