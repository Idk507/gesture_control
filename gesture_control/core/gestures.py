"""
Gesture recognition module for gesture control library.

Analyzes hand landmark movements to detect specific gestures like swipes, pinches, and hand states.
"""

import numpy as np
from typing import List, Dict, Optional, Tuple, Any
from enum import Enum
import time
import logging

# Set up logging
logger = logging.getLogger(__name__)


class GestureType(Enum):
    """Enumeration of supported gesture types."""

    NONE = "none"
    SWIPE_UP = "swipe_up"
    SWIPE_DOWN = "swipe_down"
    SWIPE_LEFT = "swipe_left"
    SWIPE_RIGHT = "swipe_right"
    PINCH = "pinch"
    HAND_OPEN = "hand_open"
    HAND_CLOSED = "hand_closed"

    def __str__(self):
        return self.value


class GestureAction(Enum):
    """Corresponding actions for each gesture."""

    NONE = "none"
    SCROLL_UP = "scroll_up"
    SCROLL_DOWN = "scroll_down"
    SCROLL_LEFT = "scroll_left"
    SCROLL_RIGHT = "scroll_right"
    CLICK = "click"
    HOVER = "hover"
    IDLE = "idle"


# Gesture to action mapping
GESTURE_ACTIONS = {
    GestureType.SWIPE_UP: GestureAction.SCROLL_UP,
    GestureType.SWIPE_DOWN: GestureAction.SCROLL_DOWN,
    GestureType.SWIPE_LEFT: GestureAction.SCROLL_LEFT,
    GestureType.SWIPE_RIGHT: GestureAction.SCROLL_RIGHT,
    GestureType.PINCH: GestureAction.CLICK,
    GestureType.HAND_OPEN: GestureAction.HOVER,
    GestureType.HAND_CLOSED: GestureAction.IDLE,
    GestureType.NONE: GestureAction.NONE,
}


class GestureResult:
    """Result of gesture recognition."""

    def __init__(self, gesture_type: GestureType, confidence: float, hand_data: Any = None):
        """
        Initialize gesture result.

        Args:
            gesture_type: Detected gesture type
            confidence: Confidence score (0.0-1.0)
            hand_data: Associated hand landmark data
        """
        self.gesture_type = gesture_type
        self.confidence = confidence
        self.action = GESTURE_ACTIONS.get(gesture_type, GestureAction.NONE)
        self.hand_data = hand_data
        self.timestamp = time.time()

    def __str__(self):
        return f"GestureResult(type={self.gesture_type.value}, confidence={self.confidence:.2f}, action={self.action.value})"


class GestureRecognizer:
    """
    Recognizes hand gestures from landmark data.

    Uses movement analysis, thresholds, and smoothing to detect gestures reliably.
    """

    def __init__(self,
                 swipe_threshold: float = 0.1,
                 pinch_threshold: float = 0.05,
                 smoothing_frames: int = 5,
                 min_confidence: float = 0.7):
        """
        Initialize gesture recognizer.

        Args:
            swipe_threshold: Minimum displacement for swipe detection
            pinch_threshold: Maximum distance for pinch detection
            smoothing_frames: Number of frames for smoothing
            min_confidence: Minimum confidence for gesture recognition
        """
        self.swipe_threshold = swipe_threshold
        self.pinch_threshold = pinch_threshold
        self.smoothing_frames = smoothing_frames
        self.min_confidence = min_confidence

        # Movement history for smoothing
        self.position_history = []
        self.velocity_history = []

        # Gesture state
        self.last_gesture = GestureType.NONE
        self.gesture_start_time = None

        logger.info(f"GestureRecognizer initialized with thresholds: swipe={swipe_threshold}, pinch={pinch_threshold}")

    def recognize_gesture(self, hand: Any) -> GestureResult:
        """
        Analyze hand landmarks and recognize gesture.

        Args:
            hand: Hand landmark data

        Returns:
            GestureResult with detected gesture and confidence
        """
        if hand is None or not hasattr(hand, 'landmarks') or not hand.landmarks:
            return GestureResult(GestureType.NONE, 0.0)

        # Extract key positions
        index_tip = hand.get_landmark(8)  # Index finger tip
        thumb_tip = hand.get_landmark(4)  # Thumb tip
        wrist = hand.get_wrist_position()

        if not all([index_tip, thumb_tip, wrist]):
            return GestureResult(GestureType.NONE, 0.0)

        # Update movement history
        current_pos = np.array([index_tip['x'], index_tip['y']])
        self._update_history(current_pos)

        # Analyze different gesture types
        gestures = [
            self._detect_pinch(index_tip, thumb_tip),
            self._detect_hand_state(hand),
            self._detect_swipe(),
        ]

        # Find the best gesture (highest confidence)
        best_gesture = GestureResult(GestureType.NONE, 0.0, hand)

        for gesture_result in gestures:
            if gesture_result.confidence > best_gesture.confidence:
                best_gesture = gesture_result

        # Update gesture state
        if best_gesture.gesture_type != self.last_gesture:
            self.last_gesture = best_gesture.gesture_type
            self.gesture_start_time = time.time() if best_gesture.gesture_type != GestureType.NONE else None

        return best_gesture

    def _update_history(self, current_pos: np.ndarray):
        """Update position and velocity history for smoothing."""
        self.position_history.append(current_pos)

        # Keep only recent positions
        if len(self.position_history) > self.smoothing_frames:
            self.position_history.pop(0)

        # Calculate velocity if we have enough history
        if len(self.position_history) >= 2:
            velocity = self.position_history[-1] - self.position_history[-2]
            self.velocity_history.append(velocity)

            if len(self.velocity_history) > self.smoothing_frames:
                self.velocity_history.pop(0)

    def _detect_swipe(self) -> GestureResult:
        """Detect swipe gestures based on movement direction and distance."""
        if len(self.position_history) < self.smoothing_frames:
            return GestureResult(GestureType.NONE, 0.0)

        # Calculate smoothed displacement
        start_pos = np.mean(self.position_history[:3], axis=0)  # First 3 frames
        end_pos = np.mean(self.position_history[-3:], axis=0)  # Last 3 frames
        displacement = end_pos - start_pos

        # Calculate displacement magnitude
        distance = np.linalg.norm(displacement)

        if distance < self.swipe_threshold:
            return GestureResult(GestureType.NONE, 0.0)

        # Determine swipe direction
        dx, dy = displacement

        # Normalize direction
        if distance > 0:
            dx_norm, dy_norm = dx / distance, dy / distance
        else:
            return GestureResult(GestureType.NONE, 0.0)

        # Classify swipe direction
        confidence = min(distance / (self.swipe_threshold * 2), 1.0)  # Scale confidence

        if abs(dx_norm) > abs(dy_norm):
            # Horizontal swipe
            if dx_norm > 0.7:
                return GestureResult(GestureType.SWIPE_RIGHT, confidence)
            elif dx_norm < -0.7:
                return GestureResult(GestureType.SWIPE_LEFT, confidence)
        else:
            # Vertical swipe
            if dy_norm > 0.7:
                return GestureResult(GestureType.SWIPE_DOWN, confidence)
            elif dy_norm < -0.7:
                return GestureResult(GestureType.SWIPE_UP, confidence)

        return GestureResult(GestureType.NONE, 0.0)

    def _detect_pinch(self, index_tip: Dict, thumb_tip: Dict) -> GestureResult:
        """Detect pinch gesture based on distance between index finger and thumb."""
        # Calculate distance between finger tips
        index_pos = np.array([index_tip['x'], index_tip['y']])
        thumb_pos = np.array([thumb_tip['x'], thumb_tip['y']])

        distance = np.linalg.norm(index_pos - thumb_pos)

        # Pinch is detected when fingers are close together
        if distance < self.pinch_threshold:
            confidence = 1.0 - (distance / self.pinch_threshold)
            confidence = min(confidence, 1.0)
            return GestureResult(GestureType.PINCH, confidence)

        return GestureResult(GestureType.NONE, 0.0)

    def _detect_hand_state(self, hand: Any) -> GestureResult:
        """Detect overall hand state (open/closed) for hover/idle modes."""
        finger_tips = hand.get_finger_tips()
        wrist = hand.get_wrist_position()

        if not finger_tips or not wrist:
            return GestureResult(GestureType.NONE, 0.0)

        # Calculate distances from wrist to finger tips
        wrist_pos = np.array([wrist['x'], wrist['y']])

        distances = []
        for tip_name, tip_pos in finger_tips.items():
            tip_coords = np.array([tip_pos['x'], tip_pos['y']])
            distance = np.linalg.norm(tip_coords - wrist_pos)
            distances.append(distance)

        avg_distance = np.mean(distances)

        # Simple heuristic: hand is "open" if fingers are extended
        # This is a basic implementation - could be improved with more sophisticated analysis
        if avg_distance > 0.15:  # Threshold for "open" hand
            return GestureResult(GestureType.HAND_OPEN, 0.8)
        else:
            return GestureResult(GestureType.HAND_CLOSED, 0.8)

    def reset(self):
        """Reset gesture recognition state."""
        self.position_history.clear()
        self.velocity_history.clear()
        self.last_gesture = GestureType.NONE
        self.gesture_start_time = None
        logger.info("Gesture recognizer reset")

    def get_gesture_stats(self) -> Dict:
        """Get statistics about gesture recognition."""
        return {
            'current_gesture': self.last_gesture.value,
            'history_length': len(self.position_history),
            'gesture_duration': time.time() - self.gesture_start_time if self.gesture_start_time else 0,
            'thresholds': {
                'swipe': self.swipe_threshold,
                'pinch': self.pinch_threshold,
                'smoothing_frames': self.smoothing_frames,
            }
        }
